import sys
import os
sys.path.append(os.getcwd())
from align_book import align_tocs

# Mock TOC data matching the issue
en_toc = [
    {'label': 'Dedication', 'src': 'Dedication.xhtml'},
    {'label': 'Catenan Rankings', 'src': 'Rankings.xhtml'},
    {'label': 'Part I: Imperium Sine Fine', 'src': 'Part1.xhtml'},
    {'label': 'Chapter I', 'src': 'Chapter1.xhtml'}
]

es_toc = [
    {'label': 'Tabla de contenido', 'src': 'index_split_000.html'},
    {'label': 'Página de título', 'src': 'index_split_001.html'},
    {'label': 'Dedicación', 'src': 'index_split_002.html'},
    {'label': 'Clasificaciones de Catenan', 'src': 'index_split_003.html'},
    {'label': 'Parte I: Imperium Sine Fine', 'src': 'index_split_004.html'},
    {'label': 'Capítulo I', 'src': 'index_split_005.html'}
]

def test_toc_alignment():
    print("Aligning TOCs...")
    pairs = align_tocs(en_toc, es_toc)
    
    print("\n--- Alignment Results ---")
    for label, en_src, es_src in pairs:
        print(f"Label: {label:<30} | EN: {str(en_src):<30} <-> ES: {str(es_src)}")

if __name__ == "__main__":
    test_toc_alignment()
