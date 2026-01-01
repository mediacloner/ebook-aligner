
import os
import bs4
from bs4 import BeautifulSoup
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

def extract_text_sample(file_path, max_chars=1000):
    """
    Reads the first 'max_chars' of text from an XHTML file.
    Does a quick parse to ignore tags.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text(separator=' ', strip=True)
            return text[:max_chars]
    except Exception as e:
        # logging.warning(f"Failed to extract text sample from {file_path}: {e}")
        return ""

def align_tocs_semantically(en_items, es_items, en_toc_dir, es_toc_dir, model):
    """
    Aligns EN TOC items to ES files using semantic similarity of their content.
    
    Args:
        en_items: List of EN TOC items (dicts with 'item'->'src').
        es_items: List of ES TOC items OR just file paths (dicts). 
                  If 'item' key exists, uses src. Else assumes dict has 'path'.
        en_toc_dir: Base dir for EN files.
        es_toc_dir: Base dir for ES files.
        model: Loaded SentenceTransformer model (LaBSE).
        
    Returns:
        List of tuples: (label, en_src, es_src, level)
    """
    print(f"Starting Semantic TOC Alignment with {len(en_items)} EN items and {len(es_items)} ES candidates.")
    
    # 1. Extract Samples
    en_samples = []
    en_valid_indices = []
    
    for i, item in enumerate(en_items):
        src = item['item']['src'].split('#')[0]
        full_path = os.path.join(en_toc_dir, src)
        text = extract_text_sample(full_path)
        if text:
            en_samples.append(text)
            en_valid_indices.append(i)
        else:
            print(f"  Warning: No text found for EN item {src} at {full_path}")

    es_samples = []
    es_paths = [] # Store relative paths to return
    
    for item in es_items:
        # Determine path
        if 'item' in item:
            src = item['item']['src'].split('#')[0]
            rel_path = item['item']['src']
        elif 'path' in item:
            # candidate item (dict with path)
            full_path = item['path'] # Absolute path
            rel_path = os.path.basename(full_path)
            # wait, logic below re-joins? 
            # item['path'] is absolute if from discovery.
            src = None 
        else:
            continue
            
        if src:
            full_path = os.path.join(es_toc_dir, src)
            
        # Debug
        # print(f"  Reading ES sample: {full_path}")
            
        text = extract_text_sample(full_path)
        if text:
            es_samples.append(text)
            es_paths.append(rel_path)
        else:
             print(f"  Warning: No text found for ES item {rel_path} at {full_path}")
    if not en_samples or not es_samples:
        print("  Semantic Align Failed: Not enough text samples.")
        return []

    # 2. Encode
    print(f"  Encoding content samples ({len(en_samples)} EN, {len(es_samples)} ES)...")
    en_embeddings = model.encode(en_samples)
    es_embeddings = model.encode(es_samples)
    
    # Ensure 2D arrays (Handle single sample case)
    if len(en_embeddings.shape) == 1:
        en_embeddings = en_embeddings.reshape(1, -1)
    if len(es_embeddings.shape) == 1:
        es_embeddings = es_embeddings.reshape(1, -1)
    
    # 3. Compute Similarity Matrix
    # Shape: (n_en, n_es)
    sim_matrix = cosine_similarity(en_embeddings, es_embeddings)
    
    # 4. Assign
    # Simple strategy: Max similarity for each EN item
    # But we want to preserve order constraint if possible?
    # For now, just Greedy Max is huge improvement over nothing.
    # Optionally, we can add a diagonal penalty if verify it works.
    
    final_pairs = []
    
    # Map valid EN indices to their matches
    en_matches = {} # en_idx -> es_idx
    
    for i in range(len(en_samples)):
        scores = sim_matrix[i]
        best_es_idx = np.argmax(scores)
        best_score = scores[best_es_idx]
        
        real_en_idx = en_valid_indices[i]
        
        # Threshold?
        if best_score > 0.4: # Loose threshold, context matching can be noisy
             en_matches[real_en_idx] = {'es_idx': best_es_idx, 'score': best_score}
        else:
             print(f"  Low confidence match for EN '{en_items[real_en_idx]['item']['label']}': {best_score:.3f}")

    # Reconstruct Full Pairs List in Order
    current_es_src = None
    
    for i, en_item in enumerate(en_items):
        label = en_item['item']['label']
        en_src = en_item['item']['src']
        level = en_item['item'].get('level', 0)
        
        match = en_matches.get(i)
        if match:
             es_idx = match['es_idx']
             es_src = es_paths[es_idx]
             current_es_src = es_src
             print(f"  Matched '{label}' -> {es_src} (Score: {match['score']:.3f})")
             final_pairs.append((label, en_src, es_src, level))
        else:
            # Fallback: Use last known good ES source? Or None?
            # If we missed a match, it's safer to skip or map to None than to guess wrong
            print(f"  No match for '{label}'")
            final_pairs.append((label, en_src, None, level))
            
    return final_pairs
