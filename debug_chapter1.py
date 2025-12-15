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
    print(f"Aligned pairs: {len(aligned)}")
    
    # Search for specific text
    search_en = "Helena tried to speak"
    search_es = "Helena intentó hablar"
    
    found_idx = -1
    for i, item in enumerate(aligned):
        if search_en.lower() in (item['en'] or "").lower() or search_es.lower() in (item['es'] or "").lower():
            found_idx = i
            break
            
    if found_idx != -1:
        print(f"Found match at index {found_idx}")
        start = max(0, found_idx - 3)
        end = min(len(aligned), found_idx + 5)
        for i in range(start, end):
             en_txt = aligned[i]['en']
             es_txt = aligned[i]['es']
             print(f"[{i}] EN: {en_txt}")
             print(f"    ES: {es_txt}")
             print("-" * 40)
    else:
        print("Search text not found in alignment.")

if __name__ == "__main__":
    debug_chapter1()
