import sys
import os
import shutil
import zipfile
import tempfile
sys.path.append(os.getcwd())
from align_book import parse_toc, align_tocs, normalize_label, enrich_toc_from_content
from neural_aligner import NeuralAligner

def unzip_epub(epub_path, extract_to):
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def find_ncx(root_dir):
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            if f.lower().endswith('.ncx'):
                return os.path.join(root, f)
    return None

def run_debug():
    en_path = "books/Normal People - Sally Rooney EN.epub"
    es_path = "books/Normal People - Sally Rooney ES.epub"
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        en_dir = os.path.join(tmp_dir, "en")
        es_dir = os.path.join(tmp_dir, "es")
        os.makedirs(en_dir)
        os.makedirs(es_dir)
        
        print(f"Unzipping {en_path}...")
        unzip_epub(en_path, en_dir)
        print(f"Unzipping {es_path}...")
        unzip_epub(es_path, es_dir)
        
        print("Finding NCX files...")
        en_ncx = find_ncx(en_dir)
        es_ncx = find_ncx(es_dir)
        
        if not en_ncx or not es_ncx:
            print(f"Error: Could not find NCX. EN: {en_ncx}, ES: {es_ncx}")
            return

        print("Parsing TOCs...")
        en_toc = parse_toc(en_ncx)
        es_toc = parse_toc(es_ncx)
        
        print(f"\n--- Extracted EN TOC ({len(en_toc)} items) ---")
        enrich_toc_from_content(en_toc, os.path.dirname(en_ncx))
        for item in en_toc:
            print(f"Label: '{item['label']}', Src: {item['src']}")
            
        print(f"\n--- Extracted ES TOC ({len(es_toc)} items) ---")
        enrich_toc_from_content(es_toc, os.path.dirname(es_ncx))
        for item in es_toc:
            print(f"Label: '{item['label']}', Src: {item['src']}")
            
        print("\n--- Running Alignment ---")
        aligner = NeuralAligner()
        pairs = align_tocs(en_toc, es_toc, aligner=aligner)
        
        print(f"\n--- Alignment Results ({len(pairs)} pairs) ---")
        for p in pairs:
            # p is (label, en_src, es_src, level)
            print(f"'{p[0]}' -> {p[1]} <-> {p[2]}")
            
            # Inspect content if it matches Section0002 or similar
            if p[2] and 'Section000' in p[2]:
                full_path = os.path.join(es_dir, p[2])
                if os.path.exists(full_path):
                    with open(full_path, 'r', encoding='utf-8') as f:
                        snippet = f.read(800).replace('\n', ' ')
                        print(f"   [CONTENT SNIPPET]: {snippet}...")
            
if __name__ == "__main__":
    run_debug()
