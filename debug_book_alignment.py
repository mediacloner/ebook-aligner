from align_book import parse_toc, align_tocs, detect_profile, PROFILES, EnglishParser, SpanishParser, smart_pair_split
import os

def debug_alignment():
    # Paths we extracted earlier
    en_base = 'temp_analysis/en'
    es_base = 'temp_analysis/es'
    
    en_toc_path = os.path.join(en_base, 'toc.ncx')
    es_toc_path = os.path.join(es_base, 'toc.ncx')

    print(f"Loading TOCs:\n EN: {en_toc_path}\n ES: {es_toc_path}")
    
    en_toc = parse_toc(en_toc_path)
    es_toc = parse_toc(es_toc_path)
    
    print(f"EN Chapters: {len(en_toc)}")
    # for t in en_toc[:5]: print(f"  EN: {t}")
    
    pairs = align_tocs(en_toc, es_toc)
    print(f"Pairs Found: {len(pairs)}")
    
    print("\n--- TOC LABEL COMPARISON ---")
    limit = max(len(en_toc), len(es_toc))
    for i in range(limit):
        en_row = en_toc[i] if i < len(en_toc) else ("MISSING", "")
        es_row = es_toc[i] if i < len(es_toc) else ("MISSING", "")
        
        if isinstance(en_row, dict):
            en_lbl = en_row.get('label', '').strip().replace('\n', ' ')[:40]
        else:
            en_lbl = "MISSING"

        if isinstance(es_row, dict):
            es_lbl = es_row.get('label', '').strip().replace('\n', ' ')[:40]
        else:
            es_lbl = "MISSING"
        
        match_status = "   "
        # Check if this exact index was matched
        for p_idx, (p_en, p_es) in enumerate(pairs):
             # To verify match, we'd need to check src, but we just want to see labels here
             pass

        print(f"{i:02d} | EN: {en_lbl:<40} | ES: {es_lbl:<40}")

    if not pairs:
        print("CRITICAL: No pairs found. Alignment logic failing.")
        
        # Dump comparison
        print("\nTop 5 EN Labels vs ES Labels:")
        for i in range(min(5, len(en_toc), len(es_toc))):
            print(f" {i}: '{en_toc[i][0]}' vs '{es_toc[i][0]}'")
            
        return

    # If pairs succeed, check content
    first_pair = pairs[0] 
    print(f"\nChecking First Pair: {first_pair}")
    
    en_file = os.path.join(en_base, str(first_pair[0]))
    es_file = os.path.join(es_base, str(first_pair[1])) 
    # Note: parse_toc returns paths usually relative to OEBPS or similar, 
    # but `extract` put them in specific places.
    # EN structure: temp_analysis/en/e978.../xhtml/ch01.xhtml
    # ES structure: temp_analysis/es/index_split_007.html
    # We might need to adjust paths for this debug script if they aren't standard.
    
    # Try finding the actual files
    # The TOC parser extracts 'src' attribute.
    print(f"Raw Paths from TOC: {first_pair}")
    
    # Auto-Detect
    # We need a real file path to detecting.
    # Searching for the file
    def find_file(base, partial):
        for root, dirs, files in os.walk(base):
            if partial in files:
                return os.path.join(root, partial)
            # Handle if partial contains directory
            if os.path.exists(os.path.join(root, partial)):
                 return os.path.join(root, partial)
        return None

    # The paths in TOCs are usually relative to the OPF file location.
    # For this debug, I'll assume standard naming but if not I'll just skip detection if file missing.
    
    # Let's inspect the first detected pair's content processing
    # Assuming we can find the files...
    
if __name__ == "__main__":
    debug_alignment()
