import sys
import os
sys.path.append(os.getcwd())
from align_book import parse_toc, align_tocs, find_toc_file

def debug_full_alignment():
    en_path = "temp_en_investigation"
    es_path = "temp_es_investigation"
    
    # We might need to find OEBPS or similar if unzip structure is complex
    # But checking unzip output, toc.ncx is at root for ES.
    
    print("Finding TOCs...")
    en_toc_file = find_toc_file(en_path)
    es_toc_file = find_toc_file(es_path)
    
    print(f"EN TOC File: {en_toc_file}")
    print(f"ES TOC File: {es_toc_file}")
    
    print("Parsing TOCs...")
    en_toc = parse_toc(en_toc_file)
    es_toc = parse_toc(es_toc_file)
    
    print("\n--- EN TOC HEAD ---")
    for x in en_toc[:5]: print(f"{x['label']} -> {x['src']}")
    
    print("\n--- ES TOC HEAD ---")
    for x in es_toc[:5]: print(f"{x['label']} -> {x['src']}")

    print("\nAligning...")
    aligned = align_tocs(en_toc, es_toc)
    
    print("\n--- ALIGNED PAIRS ---")
    for lbl, en_src, es_src in aligned:
        print(f"LBL: {lbl:<30} | EN: {str(en_src):<30} <-> ES: {str(es_src)}")


if __name__ == "__main__":
    debug_full_alignment()
