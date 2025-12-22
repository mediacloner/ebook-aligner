
import sys
import os
import re
# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neural_aligner import NeuralAligner
from align_book import align_chunks, distribute_spanish

# Simulation of what happens in align_book.py around line 3350
def simulate_alignment(en_text_list, es_text_list):
    print("--- Simulating Alignment ---")
    
    # 1. Parsing (Mock)
    en_chunks = [{'text': t, 'type': 'p', 'tag': 'p', 'node': 'node'} for t in en_text_list]
    es_chunks = [{'text': t, 'type': 'p', 'tag': 'p', 'node': 'node'} for t in es_text_list]
    
    # 2. Filtering (The Logic we suspect is problematic)
    # Copied from align_book.py
    en_filtered = []
    for c in en_chunks:
        # Check explicit type
        if c.get('type') == 'caption': continue
        
        # Check Regex
        txt = c['text'].strip()
        if re.match(r'^(Figura|Figure|Tabla|Table|Cuadro|Grafico)\s*\d+', txt, re.IGNORECASE):
            print(f"DROPPED EN: {txt}")
            continue
        en_filtered.append(c)
        
    es_filtered = []
    for c in es_chunks:
        if c.get('type') == 'caption': continue
        
        txt = c['text'].strip()
        if re.match(r'^(Figura|Figure|Tabla|Table|Cuadro|Grafico)\s*\d+', txt, re.IGNORECASE):
            print(f"DROPPED ES: {txt}")
            continue
        es_filtered.append(c)
        
    print(f"En Filtered: {len(en_filtered)} / {len(en_chunks)}")
    print(f"Es Filtered: {len(es_filtered)} / {len(es_chunks)}")
    
    # 3. Simulate Result
    # We expect these filtered items to be missing from the final output/alignment.
    # The actual Neural Aligner would process the filtered lists.
    
    return en_filtered, es_filtered

if __name__ == "__main__":
    en_data = [
        "Artificial Intelligence is a broad field.",
        "Figure 1.1: A neural network.",
        "It encompasses machine learning and deep learning."
    ]
    
    es_data = [
        "La inteligencia artificial es un campo amplio.",
        "Figura 1.1: Una red neuronal.",
        "Abarca el aprendizaje automático y el aprendizaje profundo."
    ]
    
    simulate_alignment(en_data, es_data)
