import numpy as np
from sentence_transformers import SentenceTransformer
from scipy.spatial.distance import cdist
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NeuralAligner:
    def __init__(self, model_name='sentence-transformers/LaBSE', device=None):
        """
        Initialize the NeuralAligner with a specific SentenceTransformer model.
        LaBSE is recommended for bitext alignment.
        """
        logger.info(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        
        # Log the actual device being used
        device_used = self.model.device
        logger.info(f"Model loaded successfully on device: {device_used}")


    def embed_chunks(self, chunks):
        """
        lines is a list of strings (text content of chunks).
        Returns a numpy array of embeddings.
        """
        texts = [c['text'] for c in chunks]
        return self.model.encode(texts, show_progress_bar=False)

    def compute_similarity_matrix(self, embs1, embs2):
        """
        Compute cosine distance matrix.
        Note: cdist calculates distance. Similarity = 1 - distance.
        We want distance for DTW (minimize cost).
        """
        # cosine distance = 1 - cosine similarity
        return cdist(embs1, embs2, metric='cosine')

    def align_dtw(self, en_chunks, es_chunks, constraints=None):
        """
        Aligns chunks using Dynamic Time Warping on their embeddings.
        Returns a list of matched pairs/groups.
        constraints: optional list of (en_idx, es_idx) tuples that MUST match.
        """
        if not en_chunks or not es_chunks:
            return []

        logger.info(f"embedding {len(en_chunks)} EN chunks...")
        en_embs = self.embed_chunks(en_chunks)
        
        logger.info(f"embedding {len(es_chunks)} ES chunks...")
        es_embs = self.embed_chunks(es_chunks)

        logger.info("Computing distance matrix...")
        # distance matrix
        D = cdist(en_embs, es_embs, metric='cosine')
        
        # Apply Hard Constraints
        if constraints:
            logger.info(f"Applying {len(constraints)} hard constraints...")
            # We enforce constraints by making the cost of violating them infinite
            # and the cost of the constrained match 0 (or very low neg).
            # Strategy: For each (i, j) in constraints:
            # 1. Set D[i, j] = 0
            # 2. Set entire row i to infinity (except j)
            # 3. Set entire col j to infinity (except i)
            
            # Use a large number for infinity
            INF_COST = 1e6
            
            for item in constraints:
                # Support (i, j), (i, j, options)
                if len(item) == 2:
                    i, j = item
                    options = {}
                else:
                    i, j, options = item
                
                if i >= D.shape[0] or j >= D.shape[1]: continue
                
                # Check for 'soft' option
                is_soft = options.get('soft', False)
                allow_col_merge = options.get('allow_col_merge', False)
                
                if is_soft:
                    # SOFT CONSTRAINT (Gravity Well)
                    # Make this match extremely attractive, but don't forbid others.
                    # This allows the path to flow through here if plausible, but skip/merge if necessary.
                    # We subtract a large value to ensure it's the preferred path locally.
                    D[i, j] -= 100.0 
                    continue

                # HARD CONSTRAINT
                # Mask out row (Force En[i] to match Es[j])
                D[i, :] = INF_COST
                
                # Mask out col (Force Es[j] to match En[i])
                if not allow_col_merge:
                    D[:, j] = INF_COST
                
                D[i, j] = 0.0

        # Simple DTW implementation
        # Accumulate cost matrix
        n, m = D.shape
        acc = np.zeros((n, m))
        
        # Initialize
        acc[0, 0] = D[0, 0]
        for i in range(1, n):
            acc[i, 0] = acc[i-1, 0] + D[i, 0]
        for j in range(1, m):
            acc[0, j] = acc[0, j-1] + D[0, j]
            
        # Fill
        # We allow steps: (1,1) match, (1,0) skip es (merge en), (0,1) skip en (merge es)
        # But for alignment, we usually want to step through both.
        # This is a basic asymmetric implementation. 
        # For text alignment, we often want to allow [1,1], [1,0], [0,1]
        
        path_matrix = np.zeros((n, m), dtype=int) # 0: diag, 1: up, 2: left
        
        for i in range(1, n):
            for j in range(1, m):
                # Option 0: Match (Diagonal)
                match_cost = acc[i-1, j-1]
                
                # Option 1: Vertical (En advances, Es stays / Merge En)
                vert_cost = acc[i-1, j]
                
                # Option 2: Horizontal (Es advances, En stays / Merge Es)
                # This implies En[i] maps to Es[j-1] AND Es[j].
                # We want to PENALIZE this if Es[j] is a pre-split chunk (should be 1:1).
                horiz_cost = acc[i, j-1]
                if es_chunks[j].get('is_pre_split', False):
                    # Add significant penalty to discourage merging pre-split Spanish chunks
                    # D values are usually < 1.0, so 5.0 is a strong deterrent
                    horiz_cost += 5.0
                
                choices = [match_cost, vert_cost, horiz_cost]
                best_idx = np.argmin(choices)
                acc[i, j] = D[i, j] + choices[best_idx]
                path_matrix[i, j] = best_idx

        # Backtrack
        i, j = n-1, m-1
        alignment_path = []
        
        while i > 0 or j > 0:
            alignment_path.append((i, j))
            if i == 0:
                j -= 1
            elif j == 0:
                i -= 1
            else:
                step = path_matrix[i, j]
                if step == 0:
                    i -= 1
                    j -= 1
                elif step == 1:
                    i -= 1
                else:
                    j -= 1
        
        alignment_path.append((0, 0))
        alignment_path.reverse()
        
        # Group alignments
        # DTW gives a path of indices. We need to group them.
        # e.g. (0,0), (1,0), (2,1) -> En[0]~Es[0], En[1]~Es[0] ... wait
        # (1,0) means En advanced but Es didn't -> En[1] maps to Es[0] too?
        # Standard DTW aligns every point.
        # We need to turn the path into blocks.
        
        aligned_groups = []
        current_en = []
        current_es = []
        
        last_i = -1
        last_j = -1
        
        # This simple interpreting of DTW path might be noisy.
        # Let's just collect the raw path first.
        # We can refine the grouping:
        # If we have (i, j) then (i+1, j), it means En[i+1] is also matched to Es[j].
        # So Es[j] corresponds to {En[i], En[i+1]}.
        
        # Let's iterate and build map
        # en_map = { i: [list of j] }
        # es_map = { j: [list of i] }
        
        en_to_es = {x: set() for x in range(n)}
        es_to_en = {x: set() for x in range(m)}
        
        for (i, j) in alignment_path:
            en_to_es[i].add(j)
            es_to_en[j].add(i)
            
        # Convert to list of objects
        # To make it linear, we can iterate through En 0..N
        
        processed_en = set()
        processed_es = set()
        
        # Pre-process: Identify hard constraint pairs that should be isolated (1:1 blocks)
        # Create a set of (en_idx, es_idx) tuples that MUST stay isolated
        hard_pairs = set()
        if constraints:
            for item in constraints:
                if len(item) == 2:
                    i, j = item
                    options = {}
                else:
                    i, j, options = item
                if not options.get('soft', False):
                    hard_pairs.add((i, j))
        
        final_alignment = []
        
        # FIRST: Emit ALL hard constraint pairs as isolated 1:1 blocks
        # This must happen BEFORE the main loop to prevent them from being absorbed
        for (hi, hj) in sorted(hard_pairs):  # Sort by en index for consistent ordering
            if hi not in processed_en and hj not in processed_es:
                if hi < n and hj < m:  # Bounds check
                    final_alignment.append({
                        'en_indices': [hi],
                        'es_indices': [hj], 
                        'en_chunks': [en_chunks[hi]],
                        'es_chunks': [es_chunks[hj]]
                    })
                    processed_en.add(hi)
                    processed_es.add(hj)
        
        for i in range(n):
            if i in processed_en:
                continue
            
            # Check if this En index is part of a hard constraint pair
            # If so, emit it as an isolated 1:1 block (bypass expansion)
            hard_partner = None
            for (hi, hj) in hard_pairs:
                if hi == i:
                    hard_partner = hj
                    break
            
            if hard_partner is not None and hard_partner not in processed_es:
                # Emit isolated 1:1 block for hard constraint
                final_alignment.append({
                    'en_indices': [i],
                    'es_indices': [hard_partner], 
                    'en_chunks': [en_chunks[i]],
                    'es_chunks': [es_chunks[hard_partner]]
                })
                processed_en.add(i)
                processed_es.add(hard_partner)
                continue
                
            # Who does i map to?
            related_es = en_to_es[i]
            
            # Who do those es map to? (Closure)
            # This is a connected components problem on the bipartite graph defined by the path.
            # But the path is continuous, so we just march forward.
            
            # Simple greedy block builder
            block_en = {i}
            block_es = set(related_es)
            
            # CHECK: If this chunk is pre-split, do NOT expand the block
            # Pre-split chunks should maintain 1:1 alignment with their translations
            is_presplit_en = en_chunks[i].get('is_pre_split', False)
            is_presplit_es = any(es_chunks[j].get('is_pre_split', False) for j in related_es if j < m)
            
            # Only expand if NOT pre-split
            if not is_presplit_en and not is_presplit_es:
                # Expand block until stable
                while True:
                    initial_size = len(block_en) + len(block_es)
                    
                    # Add all En that map to any in block_es (excluding already processed)
                    for es_idx in list(block_es):
                        for en_idx in es_to_en[es_idx]:
                            if en_idx not in processed_en:
                                block_en.add(en_idx)
                        
                    # Add all Es that map to any in block_en (excluding already processed)
                    for en_idx in list(block_en):
                        for es_idx in en_to_es[en_idx]:
                            if es_idx not in processed_es:
                                block_es.add(es_idx)
                        
                    if len(block_en) + len(block_es) == initial_size:
                        break
            
            # Sort and store (filter out any processed indices that slipped in)
            sorted_en = sorted([x for x in block_en if x not in processed_en])
            sorted_es = sorted([x for x in block_es if x not in processed_es])
            
            # Skip empty blocks
            if not sorted_en:
                continue
            
            final_alignment.append({
                'en_indices': sorted_en,
                'es_indices': sorted_es, 
                'en_chunks': [en_chunks[x] for x in sorted_en],
                'es_chunks': [es_chunks[x] for x in sorted_es]
            })
            
            processed_en.update(block_en)
            processed_es.update(block_es)
            
        logger.info(f"Aligned into {len(final_alignment)} blocks.")
        return final_alignment

if __name__ == "__main__":
    # Test stub
    aligner = NeuralAligner()
    en = [{'text': "Hello world"}, {'text': "This is a test"}, {'text': "End"}]
    es = [{'text': "Hola mundo"}, {'text': "Esto es una prueba"}, {'text': "Fin"}]
    res = aligner.align_dtw(en, es)
    for r in res:
        print(r['en_indices'], "->", r['es_indices'])
