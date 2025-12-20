import sys
import os
import re
import difflib

sys.path.append(os.getcwd())
from align_book import PROFILES, SpanishParser, EnglishParser

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def split_sentences(text):
    if not text: return []
    return [text.strip()]

def fingerprint(c, lang='en', shared_anchors=None, shared_nums=None):
    txt = c['text']
    
    # Anchors: Numbers
    nums = re.findall(r'\d+', txt)
    if shared_nums is not None:
         nums = [n for n in nums if n in shared_nums]
    anchors_list = sorted(list(set(nums)))
    
    # Anchors: Capitalized Tokens
    if shared_anchors is not None:
         # Simplified regex from align_book
         tokens = re.findall(r'\b[A-Z][a-z]{3,}\b', txt)
         allowed_tokens = [t for t in tokens if t in shared_anchors]
         anchors_list.extend(allowed_tokens)
         anchors_list = sorted(list(set(anchors_list)))     
    
    is_dialog = False
    s = txt.strip()
    if s:
         if s.startswith('“') or s.startswith('"'): is_dialog = True
         elif s.startswith('—') or s.startswith('-') or s.startswith('–'): is_dialog = True
    
    anchor_sig = ""
    if anchors_list: anchor_sig = "ANCHOR:" + "|".join(anchors_list)
    
    if c.get('type') == 'image':
         src = c.get('src', '')
         fname = os.path.basename(src)
         return f"IMG:{fname}"
    
    dialog_sig = "DIALOG" if is_dialog else "NARRATION"
    
    sent_count = len(split_sentences(txt))
    if sent_count <= 1: sc_sig = "SC1"
    elif sent_count <= 3: sc_sig = "SC2-3"
    else: sc_sig = "SC4+"
    
    fp = f"{c['type']}:{dialog_sig}:{anchor_sig}:{sc_sig}"
    return fp

def debug_alignment():
    # Load content
    with open('temp_debug_toc/en/ch06.html', 'r') as f: en_html = f.read()
    with open('temp_debug_toc/es/ch06.html', 'r') as f: es_html = f.read()
        
    config = PROFILES['generic']
    
    en_parser = EnglishParser(config, raw_source=en_html)
    en_parser.feed(en_html)
    en_parser.finish_chunk()
    en_chunks = en_parser.chunks
    
    es_parser = SpanishParser(config, raw_source=es_html)
    es_parser.feed(es_html)
    es_parser.finish_chunk()
    es_chunks = es_parser.chunks
    
    # Focus on first 20 chunks
    en_sec = en_chunks[:20]
    es_sec = es_chunks[:20]
    
    print(f"Analyzing {len(en_sec)} EN chunks vs {len(es_sec)} ES chunks")
    
    # Compute Shared Anchors
    en_tokens = set()
    en_nums = set()
    for c in en_sec: 
        en_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
        en_nums.update(re.findall(r'\d+', c['text']))
        
    es_tokens = set()
    es_nums = set()
    for c in es_sec: 
        es_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
        es_nums.update(re.findall(r'\d+', c['text']))
        
    shared = en_tokens & es_tokens
    shared_nums = en_nums & es_nums
    
    print(f"Shared Anchors: {sorted(list(shared))}")
    print(f"Shared Nums: {sorted(list(shared_nums))}")
    
    fp_en = [fingerprint(c, 'en', shared, shared_nums) for c in en_sec]
    fp_es = [fingerprint(c, 'es', shared, shared_nums) for c in es_sec]
    
    print("\n--- FINGERPRINTS ---")
    limit = max(len(fp_en), len(fp_es))
    for i in range(limit):
        f_en = fp_en[i] if i < len(fp_en) else "-"
        f_es = fp_es[i] if i < len(fp_es) else "-"
        txt_en = en_sec[i]['text'][:20] if i < len(fp_en) else ""
        txt_es = es_sec[i]['text'][:20] if i < len(fp_es) else ""
        
        print(f"{i:02d} | EN: {f_en:<40} ({txt_en}) | ES: {f_es:<40} ({txt_es})")

    # Sequence Matcher
    sm = difflib.SequenceMatcher(None, fp_en, fp_es, autojunk=False)
    
    print("\n--- OPCODES ---")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        print(f"{tag.upper()} EN[{i1}:{i2}] ES[{j1}:{j2}]")
        if tag == 'replace':
             print(f"  > EN: {fp_en[i1:i2]}")
             print(f"  > ES: {fp_es[j1:j2]}")

if __name__ == "__main__":
    debug_alignment()
