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

    def align_dtw(self, en_chunks, es_chunks):
        """
        Aligns chunks using Dynamic Time Warping on their embeddings.
        Returns a list of matched pairs/groups.
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
                choices = [
                    acc[i-1, j-1], # Match
                    acc[i-1, j],   # En advances, Es stays (merge En)
                    acc[i, j-1]    # Es advances, En stays (merge Es)
                ]
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
        
        final_alignment = []
        
        for i in range(n):
            if i in processed_en:
                continue
                
            # Who does i map to?
            related_es = en_to_es[i]
            
            # Who do those es map to? (Closure)
            # This is a connected components problem on the bipartite graph defined by the path.
            # But the path is continuous, so we just march forward.
            
            # Simple greedy block builder
            block_en = {i}
            block_es = set(related_es)
            
            # Expand block until stable
            while True:
                initial_size = len(block_en) + len(block_es)
                
                # Add all En that map to any in block_es
                for es_idx in list(block_es):
                    block_en.update(es_to_en[es_idx])
                    
                # Add all Es that map to any in block_en
                for en_idx in list(block_en):
                    block_es.update(en_to_es[en_idx])
                    
                if len(block_en) + len(block_es) == initial_size:
                    break
            
            # Sort and store
            sorted_en = sorted(list(block_en))
            sorted_es = sorted(list(block_es))
            
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
