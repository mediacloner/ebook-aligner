import sys
import os
sys.path.append(os.getcwd())
from align_book import align_tocs, normalize_label

# Mock TOC data for "Artificial Intelligence" (simulated from file list)
en_toc = [
    {'label': 'Cover', 'src': 'cover.xhtml'},
    {'label': 'Title Page', 'src': 'title.xhtml'},
    {'label': 'Dedication', 'src': 'dedication.xhtml'},
    {'label': 'Chapter 1', 'src': 'chapter1.xhtml'},
    {'label': 'Chapter 2', 'src': 'chapter2.xhtml'}
]

# Simulate typical Spanish structure if it has title page
es_toc = [
    {'label': 'Portada', 'src': 'cover.html'},
    {'label': 'Página de título', 'src': 'title.html'}, # Should be filtered now
    {'label': 'Dedicatoria', 'src': 'dedication.html'}, # Should match Dedication
    {'label': 'Capítulo 1', 'src': 'ch1.html'},
    {'label': 'Capítulo 2', 'src': 'ch2.html'}
]

def test_regression_toc():
    print("Aligning TOCs (Regression Test)...")
    pairs = align_tocs(en_toc, es_toc)
    
    print("\n--- Alignment Results ---")
    for label, en_src, es_src in pairs:
        print(f"LBL: {label:<20} | EN: {str(en_src):<20} <-> ES: {str(es_src)}")

if __name__ == "__main__":
    test_regression_toc()
