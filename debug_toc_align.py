import sys
import os
import xml.etree.ElementTree as ET
import re

# -----------------------------------------------------------------------------
# Copied from align_book.py
# -----------------------------------------------------------------------------

def roman_to_int(s):
    if not s: return 0
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val.get(s[i], 0) > rom_val.get(s[i - 1], 0):
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val.get(s[i], 0)
    return int_val

def normalize_label(label):
    label = label.lower().strip()
    
    if 'prologue' in label or 'prólogo' in label or 'prologo' in label: return 'prologue'
    if 'epilogue' in label or 'epílogo' in label or 'epilogo' in label: return 'epilogue'
    if 'index' in label or 'índice' in label or 'indice' in label: return 'index'
    if 'intro' in label: return 'introduction'
    if 'preface' in label or 'prefacio' in label: return 'preface'
    if 'bibliograph' in label or 'bibliograf' in label: return 'bibliography'
    if 'note' in label or 'nota' in label: return 'notes'
    
    part_match = re.search(r'(?:part|parte)\s*(\d+|[ivxlcdm]+)', label)
    if part_match:
        num_str = part_match.group(1).upper()
        if num_str.isdigit(): num = int(num_str)
        else: num = roman_to_int(num_str)
        return ('part', num)

    clean_label = re.sub(r'^(chapter|capitulo|capítulo)\s*', '', label)
    num_match = re.match(r'^(\d+|[ivxlcdm]+)(?:[\.\:\s]|$)', clean_label)
    if num_match:
        num_str = num_match.group(1).upper()
        # Simple heuristic: if it looks Roman (all matches in IVXLCDM) and not digit
        is_digit = num_str.isdigit()
        is_roman = not is_digit and all(c in 'IVXLCDM' for c in num_str)
        
        if is_digit:
            return ('chapter', int(num_str))
        elif is_roman:
            return ('chapter', roman_to_int(num_str))
            
    return label 

def align_tocs(en_toc, es_toc):
    en_items = [{'idx': i, 'item': item, 'norm': normalize_label(item['label'])} for i, item in enumerate(en_toc)]
    es_items = [{'idx': i, 'item': item, 'norm': normalize_label(item['label'])} for i, item in enumerate(es_toc)]
    
    anchors = []
    en_matched = set()
    es_matched = set()
    
    # 1. Find Anchors (Greedy Best Match)
    for en in en_items:
        match = None
        # Structural Match
        if isinstance(en['norm'], tuple):
            for es in es_items:
                if es['idx'] in es_matched: continue
                if es['norm'] == en['norm']:
                    match = es
                    break
        # String Match
        if not match and isinstance(en['norm'], str):
             for es in es_items:
                if es['idx'] in es_matched: continue
                if es['norm'] == en['norm']: 
                    match = es
                    break
                    
        if match:
            anchors.append((en, match))
            en_matched.add(en['idx'])
            es_matched.add(match['idx'])
            
    # Sort anchors by English index to establish a skeleton
    anchors.sort(key=lambda x: x[0]['idx'])
    
    final_pairs = []
    
    # 2. Fill Gaps
    last_en_idx = -1
    last_es_idx = -1
    
    sentinel_en = {'idx': len(en_items)}
    sentinel_es = {'idx': len(es_items)}
    anchors.append((sentinel_en, sentinel_es))
    
    for anchor_en, anchor_es in anchors:
        current_en_idx = anchor_en['idx']
        current_es_idx = anchor_es['idx']
        
        # Identification of Gap Items
        gap_en = [x for x in en_items if last_en_idx < x['idx'] < current_en_idx and x['idx'] not in en_matched]
        gap_es = [x for x in es_items if last_es_idx < x['idx'] < current_es_idx and x['idx'] not in es_matched]
        
        # Linear Alignment of Gap (Zip Longest)
        limit = max(len(gap_en), len(gap_es))
        for k in range(limit):
            en_src = gap_en[k]['item']['src'] if k < len(gap_en) else None
            en_lbl = gap_en[k]['item']['label'] if k < len(gap_en) else None
            es_src = gap_es[k]['item']['src'] if k < len(gap_es) else None
            
            label = en_lbl if en_lbl else (gap_es[k]['item']['label'] if k < len(gap_es) else "Unknown")
            final_pairs.append((label, en_src, es_src))
            
        if current_en_idx < len(en_items) and current_es_idx < len(es_items):
             final_pairs.append((anchor_en['item']['label'], anchor_en['item']['src'], anchor_es['item']['src']))
             
        last_en_idx = current_en_idx
        last_es_idx = current_es_idx
        
    return final_pairs

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def parse_toc(ncx_path):
    print(f"Parsing: {ncx_path}")
    tree = ET.parse(ncx_path)
    root = tree.getroot()
    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    def find_text(node, xpath):
        found = node.find(xpath, ns)
        if found is not None and found.text:
            return found.text
        return ""

    nav_points = []
    for nav_point in root.findall('.//ncx:navPoint', ns):
        label = find_text(nav_point, './ncx:navLabel/ncx:text')
        content_node = nav_point.find('./ncx:content', ns)
        content = content_node.get('src') if content_node is not None else ""
        nav_points.append({'label': label.strip(), 'src': content})
    return nav_points

def main():
    en_toc = parse_toc('temp_debug_toc/en/toc.ncx')
    es_toc = parse_toc('temp_debug_toc/es/toc.ncx')
    
    print(f"EN Items: {len(en_toc)}")
    print(f"ES Items: {len(es_toc)}")
    
    aligned = align_tocs(en_toc, es_toc)
    
    print("\n--- ALIGNMENT RESULT ---")
    for label, en, es in aligned:
        status = "MATCH" if en and es else "ORPHAN"
        print(f"[{status}] {label} |\n    EN: {en}\n    ES: {es}")

if __name__ == "__main__":
    main()
