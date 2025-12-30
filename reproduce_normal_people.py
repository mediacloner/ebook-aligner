import sys
import os
sys.path.append(os.getcwd())
from align_book import normalize_label, align_tocs
from neural_aligner import NeuralAligner

# Simulation of Normal People Headers
en_headers = [
    "Six Weeks Later (July 2011)",
    "Four Months Later (November 2011)",
    "Six Months Later (April 2012)",
    "Three Months Later (July 2013)",
    "Five Minutes Later" # Hypothetical
]

es_headers = [
    "Seis semanas después (Julio de 2011)",
    "Cuatro meses después (Noviembre de 2011)",
    "Seis meses más tarde (Abril de 2012)",
    "Tres meses después (Julio de 2013)",
    "Cinco minutos después"
]

print("--- 1. Normalization Check ---")
for en, es in zip(en_headers, es_headers):
    norm_en = normalize_label(en)
    norm_es = normalize_label(es)
    print(f"EN: '{en}' -> {norm_en}")
    print(f"ES: '{es}' -> {norm_es}")
    print(f"Match: {norm_en == norm_es}")
    print("-" * 20)

print("\n--- 2. Alignment Check (No Model) ---")
en_toc = [{'label': l, 'src': f'en_{i}.html'} for i, l in enumerate(en_headers)]
es_toc = [{'label': l, 'src': f'es_{i}.html'} for i, l in enumerate(es_headers)]

pairs = align_tocs(en_toc, es_toc, aligner=None)
for p in pairs:
    print(f"{p[0]} -> {p[1]} <-> {p[2]}")
    
print("\n--- 3. Alignment Check (With Model) ---")
try:
    import numpy as np
    from scipy.spatial.distance import cdist
    
    # Manually compute and print similarity matrix for demonstration
    aligner = NeuralAligner()
    
    print("\n--- 4. Raw Similarity Scores (Probabilistic) ---")
    en_texts = [x['label'] for x in en_toc]
    es_texts = [x['label'] for x in es_toc]
    
    en_embs = aligner.embed_chunks([{'text': t} for t in en_texts])
    es_embs = aligner.embed_chunks([{'text': t} for t in es_texts])
    
    dists = cdist(en_embs, es_embs, metric='cosine')
    sims = 1 - dists
    
    # Print Matrix
    print(f"{'':<40} | " + " | ".join([f"ES_{j}" for j in range(len(es_toc))]))
    for i, en_label in enumerate(en_texts):
        row_str = " | ".join([f"{sims[i,j]:.4f}" for j in range(len(es_texts))])
        print(f"{en_label[:40]:<40} | {row_str}")

    print("\n--- 5. Automated Alignment Results ---")
    pairs = align_tocs(en_toc, es_toc, aligner=aligner)
    for p in pairs:
        print(f"{p[0]} -> {p[1]} <-> {p[2]}")
except Exception as e:
    print(e)
