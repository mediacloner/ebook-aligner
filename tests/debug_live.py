import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import parse_toc, align_tocs, find_toc_file, normalize_label

def debug_live():
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir):
        print("Uploads dir not found.")
        return

    # Find latest jobdir
    jobs = [os.path.join(uploads_dir, d) for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
    jobs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    if not jobs:
        print("No jobs found.")
        return
        
    latest_job = jobs[0]
    print(f"Inspecting Latest Job: {latest_job}")
    
    en_extract = os.path.join(latest_job, 'en_extract')
    es_extract = os.path.join(latest_job, 'es_extract')
    
    print(f"Finding OEBPS/Content...")
    
    def find_opf_root(d):
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.opf'): return root
        return None
        
    en_base = find_opf_root(en_extract)
    es_base = find_opf_root(es_extract)
    
    print(f"EN Base: {en_base}")
    print(f"ES Base: {es_base}")
    
    if not en_base or not es_base:
        print("FAILED to find base dirs.")
        return

    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
    print(f"EN TOC: {en_toc_path}")
    print(f"ES TOC: {es_toc_path}")
    
    if not en_toc_path or not es_toc_path:
        print("Missing TOC file.")
        return
        
    en_toc_items = parse_toc(en_toc_path)
    es_toc_items = parse_toc(es_toc_path)
    
    print(f"EN Items: {len(en_toc_items)}")
    print(f"ES Items: {len(es_toc_items)}")
    
    print("\n--- SAMPLE LABELS & NORMALIZATION ---")
    for i in range(min(5, len(en_toc_items))):
        lbl = en_toc_items[i]['label']
        norm = normalize_label(lbl)
        print(f"EN[{i}]: '{lbl}' -> {norm}")

    print("")
    for i in range(min(5, len(es_toc_items))):
        lbl = es_toc_items[i]['label']
        norm = normalize_label(lbl)
        print(f"ES[{i}]: '{lbl}' -> {norm}")
        
    pairs = align_tocs(en_toc_items, es_toc_items)
    print(f"\nPairs Found: {len(pairs)}")
    
    if not pairs:
        print("DEBUG: Dumping more items to see why match failed.")
        print("EN[5:15]:")
        for i in range(5, min(15, len(en_toc_items))):
            lbl = en_toc_items[i]['label']
            print(f"  '{lbl}' -> {normalize_label(lbl)}")
            
        print("ES[5:15]:")
        for i in range(5, min(15, len(es_toc_items))):
            lbl = es_toc_items[i]['label']
            print(f"  '{lbl}' -> {normalize_label(lbl)}")

if __name__ == "__main__":
    debug_live()
