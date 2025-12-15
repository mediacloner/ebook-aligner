import os
import sys
# Ensure we can import from local dir
sys.path.append(os.getcwd())

from align_book import parse_toc, align_tocs, find_toc_file, EnglishParser, SpanishParser, align_chunks, PROFILES, detect_profile, collect_split_files

def debug_chapter1():
    uploads_dir = 'uploads'
    if not os.path.exists(uploads_dir): return
    jobs = [os.path.join(uploads_dir, d) for d in os.listdir(uploads_dir) if os.path.isdir(os.path.join(uploads_dir, d))]
    jobs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    if not jobs: return
    latest_job = jobs[0]
    print(f"Job: {latest_job}")

    def find_opf_root(d):
        for root, _, files in os.walk(d):
            for f in files:
                if f.endswith('.opf'): return root
        return None

    en_base = find_opf_root(os.path.join(latest_job, 'en_extract'))
    es_base = find_opf_root(os.path.join(latest_job, 'es_extract'))
             
    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
    en_toc = parse_toc(en_toc_path)
    es_toc = parse_toc(es_toc_path)
    
    pairs = align_tocs(en_toc, es_toc)
    
    # Find pair corresponding to Chapter 1
    target_pair = None
    target_en_src = ""
    target_es_src = ""
    
    for p in pairs:
        if not isinstance(p, tuple) and not isinstance(p, list): continue
        if len(p) != 2: continue
        en_src, es_src = p
        
        if en_src and "chapter001" in en_src.lower():
             target_pair = p
        elif es_src and "6.html" in es_src:
             target_pair = p
             
        if target_pair:
             target_en_src = en_src
             target_es_src = es_src
             break
            
    if not target_pair:
        print("Could not find Chapter 1 pair in aligned TOCs.")
        return

    print(f"Found Pair: {target_en_src} <-> {target_es_src}")
    
    en_dir = os.path.dirname(en_toc_path)
    es_dir = os.path.dirname(es_toc_path)
    
    # Parse EN using split helper
    en_files = collect_split_files(target_en_src, en_dir)
    print(f"Collected EN files: {en_files}")
    
    if not en_files:
        print("No EN files found.")
        return

    with open(en_files[0], 'r', encoding='utf-8') as f:
         first_c = f.read()
    
    profile_name = detect_profile(first_c)
    print(f"Detected profile: {profile_name}")
    config = PROFILES[profile_name]
        
    en_chunks = []
    for fpath in en_files:
        print(f"Parsing EN: {os.path.basename(fpath)}")
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                c = f.read()
            p = EnglishParser(config)
            p.feed(c)
            # p.finish_chunk() # Assuming finish_chunk needed? align_book doesn't seem to expose it generally but parse_file uses it.
            # parse_file does: p.feed(c); p.finish_chunk(); return p.chunks
            # I should call it.
            if hasattr(p, 'finish_chunk'): p.finish_chunk()
            en_chunks.extend(p.chunks)
        except Exception as e:
            print(f"Error parsing {fpath}: {e}")

    # Parse ES using split helper
    es_files = collect_split_files(target_es_src, es_dir)
    print(f"Collected ES files: {es_files}")
    es_chunks = []
    for fpath in es_files:
        print(f"Parsing ES: {os.path.basename(fpath)}")
        try:
            with open(fpath, 'r', encoding='utf-8') as f:
                c = f.read()
            p = SpanishParser(config)
            p.feed(c)
            if hasattr(p, 'finish_chunk'): p.finish_chunk()
            es_chunks.extend(p.chunks)
        except Exception as e:
            print(f"Error parsing {fpath}: {e}")
    
    print(f"EN chunks: {len(en_chunks)}")
    print(f"ES chunks: {len(es_chunks)}")

    en_headers = [c for c in en_chunks if c['type'] == 'header']
    es_headers = [c for c in es_chunks if c['type'] == 'header']
    print(f"EN headers: {len(en_headers)}")
    print(f"ES headers: {len(es_headers)}")
    if len(en_headers) > 0: print(f"Sample EN header: {en_headers[0]}")
    if len(es_headers) > 0: print(f"Sample ES header: {es_headers[0]}")
    
    # Debug Search in RAW chunks
    print("--- Searching for '1273' in RAW chunks ---")
    found_en = [i for i, c in enumerate(en_chunks) if '1273' in c['text']]
    found_es = [i for i, c in enumerate(es_chunks) if '1273' in c['text']]
    print(f"Found '1273' in EN chunks at indices: {found_en}")
    for i in found_en:
        print(f"  EN[{i}]: {en_chunks[i]['text'][:60]}...")
        
    print(f"Found '1273' in ES chunks at indices: {found_es}")
    for i in found_es:
        print(f"  ES[{i}]: {es_chunks[i]['text'][:60]}...")

    # Align
    aligned = align_chunks(en_chunks, es_chunks)
    # DEBUG: Print aligned pairs around the problematic area
    # We look for "Helena" or "Light" in the pairs
    print(f"Aligned pairs: {len(aligned)}") 
    
    # Iterate through ALL pairs
    for i, item in enumerate(aligned): 
        en_txt = str(item['en']).strip().replace('\n', ' ')
        es_txt = str(item['es']).strip().replace('\n', ' ')
        
        relevant = False
        # Always print early indices where the problem is
        if i < 150:
            relevant = True
            
        if "awake" in en_txt.lower() or "despierta" in es_txt.lower(): relevant = True
        
        if relevant:
             print(f"Pair {i}:")
             print(f"  EN: {en_txt[:80]}")
             print(f"  ES: {es_txt[:80]}")
             print("-" * 40)
    # The original code had an `else` block here, but the instruction implies replacing the search logic.
    # If the intent was to add this debug print *before* the search, the instruction was ambiguous.
    # Assuming the instruction meant to replace the search logic with this debug print.
    # The `else` block for "Search text not found" is now orphaned if the search logic is removed.
    # Given the instruction "Update the print loop to iterate `pairs`", and the provided code block
    # which is a complete loop, it seems to replace the previous search loop.
    # The `else` at the end of the provided snippet is syntactically incorrect without an `if`.
    # I will assume the user wants to replace the search block with the new debug print,
    # and the `else` at the end of the provided snippet was a copy-paste error or intended to be removed.
    # I will remove the `else` block that was originally tied to the `if found_idx != -1`.

if __name__ == "__main__":
    debug_chapter1()
