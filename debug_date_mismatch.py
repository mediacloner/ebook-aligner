import sys
import os
sys.path.append(os.getcwd())
import numpy as np
from scipy.spatial.distance import cdist
from neural_aligner import NeuralAligner
from align_book import normalize_label, align_tocs

# Pairs from user report (Mismatches)
pairs = [
    ("Two Days Later (April 2011)", "Cuatro meses más tarde (Agosto de 2011)"),
    ("Six Weeks Later (September 2012)", "Cuatro meses más tarde (Enero de 2013)"),
    ("Four Months Later (January 2013)", "Seis meses más tarde (Julio de 2013)")
]

print("--- 1. Normalization & Date Extraction ---")
for en, es in pairs:
    norm_en = normalize_label(en)
    norm_es = normalize_label(es)
    print(f"EN: {en} -> {norm_en}")
    print(f"ES: {es} -> {norm_es}")
    if norm_en[0] == 'date-chapter' and norm_es[0] == 'date-chapter':
        if norm_en != norm_es:
            print("❌ DATE MISMATCH DETECTED")
        else:
            print("✅ Dates Match")
    print("-" * 20)

print("\n--- 2. Neural Similarity Scores ---")
aligner = NeuralAligner()

en_texts = [p[0] for p in pairs]
es_texts = [p[1] for p in pairs]

en_embs = aligner.embed_chunks([{'text': t} for t in en_texts])
es_embs = aligner.embed_chunks([{'text': t} for t in es_texts])

# We only care about the diagonal (direct pair comparison) for this test
for i in range(len(pairs)):
    sim = 1 - cdist([en_embs[i]], [es_embs[i]], metric='cosine')[0][0]
    print(f"Pair: {en_texts[i]} <-> {es_texts[i]}")
    print(f"Score: {sim:.4f}")
    if sim > 0.4:
         print("⚠️  Would Pass Gap Filling (>0.4)")
    if sim > 0.85:
         print("⚠️  Would be HIGH CONF ANCHOR (>0.85)")
    print("-" * 10)

print("\n--- 3. Running align_tocs with Constraint ---")
# Construct mini-TOC
en_toc = [{'label': p[0], 'src': f'en_{i}.html'} for i, p in enumerate(pairs)]
es_toc = [{'label': p[1], 'src': f'es_{i}.html'} for i, p in enumerate(pairs)]

aligner = NeuralAligner()
final_pairs = align_tocs(en_toc, es_toc, aligner=aligner)

print("Alignment Results:")
for p in final_pairs:
    en_lbl = p[0]
    es_src = p[2]
    print(f"EN: '{en_lbl}' -> ES: {es_src}")

matched_count = sum(1 for p in final_pairs if p[2] is not None)
if matched_count == 0:
    print("\n✅ SUCCESS: No mismatches aligned (Constraint working)")
else:
    print(f"\n❌ FAILURE: {matched_count} pairs aligned incorrectly")
