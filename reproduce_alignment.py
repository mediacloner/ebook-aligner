import sys
import os

# Add local dir to path to find align_book
sys.path.append(os.getcwd())

from align_book import BaseParser, SpanishParser, EnglishParser, align_chunks, PROFILES

def reproduce():
    # Load content
    with open('temp_debug_toc/en/ch06.html', 'r') as f:
        en_html = f.read()
    with open('temp_debug_toc/es/ch06.html', 'r') as f:
        es_html = f.read()
        
    # Use generic profile
    config = PROFILES['generic']
    
    print("Parsing EN...")
    en_parser = EnglishParser(config, raw_source=en_html)
    en_parser.feed(en_html)
    en_parser.finish_chunk()
    en_chunks = en_parser.chunks
    
    print("Parsing ES...")
    # Use generic config for ES
    es_parser = SpanishParser(config, raw_source=es_html)
    es_parser.feed(es_html)
    es_parser.finish_chunk()
    es_chunks = es_parser.chunks
    
    print(f"EN Chunks: {len(en_chunks)}")
    print(f"ES Chunks: {len(es_chunks)}")
    
    # Print first few chunks to verify text
    print("\n--- EN HEAD ---")
    for c in en_chunks[:5]:
        print(f"[{c['type']}] {c['text'][:50]}...")
        
    print("\n--- ES HEAD ---")
    for c in es_chunks[:5]:
        print(f"[{c['type']}] {c['text'][:50]}...")

    # Attempt Alignment
    print("\nAligning...")
    
    # DEBUG: Manual Fingerprint Check for relevant chunks
    import re
    def get_fingerprint(txt, shared_anchors):
        # Mini version of align_book fingerprint logic for debug
        tokens = re.findall(r'\b[A-Z][a-z]{3,}\b', txt)
        allowed = [t for t in tokens if t in shared_anchors]
        anchors = sorted(list(set(allowed)))
        
        is_dialog = False
        s = txt.strip()
        if s:
             if s.startswith('“') or s.startswith('"'): is_dialog = True
             elif s.startswith('—') or s.startswith('-') or s.startswith('–'): is_dialog = True
             
        anchor_sig = "|".join(anchors)
        dialog_sig = "DIALOG" if is_dialog else "NARRATION"
        return f"{dialog_sig}:{anchor_sig}"

    # Find chunks
    en_idx = -1
    es_idx = -1
    for i, c in enumerate(en_chunks):
        if "Quintus" in c['text']: en_idx = i; break
    for i, c in enumerate(es_chunks):
        if "Quintus" in c['text']: es_idx = i; break
        
    if en_idx != -1 and es_idx != -1:
        print(f"\n--- FINGERPRINT DEBUG ---")
        # Get shared anchors for this window
        window_en = [c['text'] for c in en_chunks[en_idx:en_idx+5]]
        window_es = [c['text'] for c in es_chunks[es_idx:es_idx+5]]
        
        en_toks = set()
        for t in window_en: en_toks.update(re.findall(r'\b[A-Z][a-z]{3,}\b', t))
        es_toks = set()
        for t in window_es: es_toks.update(re.findall(r'\b[A-Z][a-z]{3,}\b', t))
        shared = en_toks & es_toks
        print(f"Shared Anchors in window: {shared}")
        
        for k in range(5):
            print(f"EN[{en_idx+k}]: {get_fingerprint(en_chunks[en_idx+k]['text'], shared)}")
            print(f"ES[{es_idx+k}]: {get_fingerprint(es_chunks[es_idx+k]['text'], shared)}")
            print("-" * 20)

    aligned = align_chunks(en_chunks, es_chunks)
    
    print("\n--- RESULTS HEAD ---")
    for item in aligned[:15]:
         en_txt = item['en'][:30].replace('\n', ' ') if item['en'] else "---"
         es_txt = item['es'][:30].replace('\n', ' ') if item['es'] else "---"
         print(f"EN: {en_txt:<35} | ES: {es_txt}")


if __name__ == "__main__":
    reproduce()
