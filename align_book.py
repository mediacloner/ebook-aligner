import argparse
import sys
print(f"DEBUG: Loading align_book.py v2024.12.28.1019 from {__file__}")
import os
import time
import re
import html
import difflib
import concurrent.futures
import multiprocessing
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import zipfile
import shutil
import uuid
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter
import json
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

try:
    from neural_aligner import NeuralAligner
except ImportError:
    NeuralAligner = None

from splitter import Splitter

CACHED_ALIGNER = None



# ----------------------------------------------------------------------------- 
# Configuration
# -----------------------------------------------------------------------------
SPLIT_TRIGGER_CHARS = 240  # Characters
SPLIT_TOLERANCE = 0.20     # 20% +/- deviation allowed

# Default configuration for "Artificial Intelligence" book
# Configuration Profiles
PROFILES = {
    'generic': {
        'filter_captions': False, # KEEP CAPTIONS (User requested generic-only, so enabled globally)
        'en': {
            'header_tags': ['h1', 'h2', 'h3'],
            'header_classes': ['CN', 'CN-Only', 'CT'], 
            'caption_start_tags': ['figcaption'],
            'caption_classes': ['caption'],
            'ignore_tags': [],
            'ignore_classes': [],
            'SPLIT_TRIGGER_CHARS': 240,
            'image_tag': 'img',
            'merge_headers': True,
            'header_merge_targets': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        },
        'es': {
            'header_tags': ['h1', 'h2', 'h3', 'p', 'div'],
            'header_indicators': [
                'Capitulos_Capitulo_Numero', 
                'Capitulos_Capitulo_1_Linea', 
                'Subcapitulos_subcapitulo', 
                'Subcapitulos_Subcapitulo'
            ],
            'caption_classes': ['Basico_pie_foto', 'Basico_pie_foto_centrado', 'caption'],
            'ignore_tags': [],
            'ignore_classes': ['_idFootnotes', 'centradoespacioantes', 'capitulo', 'Notas-Pie_Notas_Pie', '_idFootnote'],
            'ignore_div_classes': ['_idFootnotes'],
            'merge_headers': True,
            'header_merge_trigger': 'Capitulos_Capitulo_1_Linea',
            'header_merge_targets': ['Capitulos_Capitulo_Numero', 'Capitulos_Capitulo_1_Linea', 'capitulo']
        }
    }
}

def detect_profile(file_path):
    """Detects likely profile based on content signatures."""
    # Always default to generic as requested by user
    print(f"Auto-detection: Using 'generic' profile for {os.path.basename(file_path)}")
    return 'generic'

def extract_title_from_html(file_path):
    """Fallback: peeks into HTML file to find a likely chapter title."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read(6000) 

            
            # 1. Standard Headers
            # Use findall to check all headers, ignoring empty ones (e.g. image-only)
            h_matches = re.findall(r'<(h[123])[^>]*>(.*?)</\1>', content, re.IGNORECASE | re.DOTALL)
            for tag, raw in h_matches:
                text = re.sub(r'<[^>]+>', '', raw).strip() 
                if text:
                    return html.unescape(text)
                
            # 2. Paragraphs
            p_matches = re.findall(r'<p(?:\s+[^>]*)?>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
            
            count = 0
            for p_text in p_matches:
                clean = re.sub(r'<[^>]+>', '', p_text).strip()
                clean = html.unescape(clean).strip()
                if not clean: continue


                
                count += 1
                if count > 20: break 
                
                if len(clean) > 80: continue
                
                norm = clean.lower().replace('í', 'i').replace('á', 'a').replace('é', 'e').replace('ó', 'o').replace('ú', 'u')
                
                if 'capitulo' in norm or 'parte' in norm or 'prologo' in norm or 'epilogo' in norm or 'chapter' in norm:
                     return clean
                
                if any(c.isdigit() for c in clean) and len(clean) < 30:
                     return clean
            
            
            # 3. Check for specific Dedication/About patterns in first few paragraphs
            # Only if we haven't found a strong title yet.
            if count < 15: # Checked up to 15 non-empty paragraphs
                lower = clean.lower()
                if lower.startswith('para ') or lower.startswith('a ') or lower.startswith('to ') or lower.startswith('for ') or 'dedicada' in lower:
                     return "Dedication"

                if 'sobre el autor' in lower or 'about the author' in lower:
                     return "About the Author"



    except Exception as e:
        pass # Error sniffing title from {file_path}: {e}
    return ""

def parse_toc(ncx_path):
    """Parses the NCX file and returns a list of (label, src) tuples."""
    tree = ET.parse(ncx_path)
    root = tree.getroot()\
    
    # Handle namespaces which can be finicky
    # Try with namespace first
    ns = {'ncx': 'http://www.daisy.org/z3986/2005/ncx/'}
    
    # Robust finder
    def find_text(node, xpath):
        found = node.find(xpath, ns)
        if found is not None and found.text:
            return found.text
        return ""

    # Find all navPoints recursively but preserve hierarchy via level
    # We'll use a recursive helper
    def parse_navpoint(node, level, ns):
        items = []
        # Current node details
        label = find_text(node, './ncx:navLabel/ncx:text')
        content_node = node.find('./ncx:content', ns)
        content = content_node.get('src') if content_node is not None else ""
        
        # Cleanup content
        if '#' in content:
            content = content.split('#')[0]
            
        # Add self
        # Note: We append self BEFORE children
        items.append({'label': label.strip(), 'src': content, 'level': level})
        
        # Process children
        for child in node.findall('./ncx:navPoint', ns):
            items.extend(parse_navpoint(child, level + 1, ns))
            
        return items

    base_dir = os.path.dirname(ncx_path)
    nav_points = []
    
    # Iterate top-level navPoints
    for nav_point in root.findall('./ncx:navMap/ncx:navPoint', ns):
         nav_points.extend(parse_navpoint(nav_point, 0, ns))
         
    # Fallback sniffing logic (same as before but iterated over flat list)
    for item in nav_points:
        if not item['label'] and item['src']:
             # Construct absolute path to sniff
            content = item['src']
            try:
                # Remove anchor for file path
                file_part = content.split('#')[0]
                full_path = os.path.join(base_dir, file_part)
                if os.path.exists(full_path):
                    label = extract_title_from_html(full_path)
                    item['label'] = label
            except Exception as e:
                pass # Failed to sniff {content}: {e}

    return nav_points

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

def parse_written_number(text):
    """Parses English or Spanish written numbers (e.g. 'twenty-one', 'veintiuno') to int."""
    text = text.lower().strip().replace('-', ' ')
    
    # 1. Simple En/Es map for base numbers
    num_map = {
        'one': 1, 'uno': 1, 'un': 1, 'una': 1, 'first': 1, 'primero': 1,
        'two': 2, 'dos': 2, 'second': 2, 'segundo': 2,
        'three': 3, 'tres': 3, 'third': 3, 'tercero': 3,
        'four': 4, 'cuatro': 4, 'fourth': 4, 'cuarto': 4,
        'five': 5, 'cinco': 5, 'fifth': 5, 'quinto': 5,
        'six': 6, 'seis': 6, 'sixth': 6, 'sexto': 6,
        'seven': 7, 'siete': 7, 'seventh': 7, 'séptimo': 7,
        'eight': 8, 'ocho': 8, 'eighth': 8, 'octavo': 8,
        'nine': 9, 'nueve': 9, 'ninth': 9, 'noveno': 9,
        'ten': 10, 'diez': 10, 'tenth': 10, 'décimo': 10,
        'eleven': 11, 'once': 11,
        'twelve': 12, 'doce': 12,
        'thirteen': 13, 'trece': 13,
        'fourteen': 14, 'catorce': 14,
        'fifteen': 15, 'quince': 15,
        'sixteen': 16, 'dieciséis': 16, 'dieciseis': 16,
        'seventeen': 17, 'diecisiete': 17,
        'eighteen': 18, 'dieciocho': 18,
        'nineteen': 19, 'diecinueve': 19,
        'twenty': 20, 'veinte': 20,
        'thirty': 30, 'treinta': 30,
        'forty': 40, 'cuarenta': 40,
        'fifty': 50, 'cincuenta': 50,
        'sixty': 60, 'sesenta': 60,
        'seventy': 70, 'setenta': 70,
        'eighty': 80, 'ochenta': 80,
        'ninety': 90, 'noventa': 90,
        'hundred': 100, 'cien': 100, 'ciento': 100
    }
    
    if text in num_map:
        return num_map[text]
        
    # compound check
    words = text.split()
    total = 0
    current = 0
    
    for w in words:
        if w in num_map:
            val = num_map[w]
            if val == 100:
                current = (current if current else 1) * val
            else:
                current += val
        elif w in ['and', 'y']:
            continue
        elif 'veinti' in w: # Spanish 21-29 agglutinated (veintiuno, veintidos...)
            # veinti = 20
            suffix = w.replace('veinti', '')
            if suffix in num_map:
                current += 20 + num_map[suffix]
        else:
             # Unknown word, abort
             return None
             
    total += current
    return total if total > 0 else None

def normalize_label(label):
    label = label.lower().strip()
    
    if 'prologue' in label or 'prólogo' in label or 'prologo' in label: return 'prologue'
    if 'epilogue' in label or 'epílogo' in label or 'epilogo' in label: return 'epilogue'
    if 'index' in label or 'índice' in label or 'indice' in label: return 'index'
    if 'intro' in label: return 'introduction'
    if 'preface' in label or 'prefacio' in label: return 'preface'
    if 'bibliograph' in label or 'bibliograf' in label: return 'bibliography'
    if 'note' in label or 'nota' in label: return 'notes'
    
    # Enhanced mappings
    if 'dedication' in label or 'dedicación' in label or 'dedicatoria' in label: return 'dedication'
    if 'acknowledg' in label or 'agradecimiento' in label or 'gratitud' in label: return 'acknowledgments'
    if 'about' in label and 'author' in label: return 'about_author'
    if 'acerca' in label and 'autor' in label: return 'about_author'
    if 'sobre' in label and 'autor' in label: return 'about_author'
    
    part_match = re.search(r'\b(?:part|parte|libro|book)\s+(.+)', label)
    if part_match:

        num_str = part_match.group(1).strip().upper()
        if num_str.isdigit(): 
            num = int(num_str)
        elif all(c in 'IVXLCDM' for c in num_str):
             num = roman_to_int(num_str)
        else:
             # Try parse written
             num = parse_written_number(num_str)
             if not num: 
                 return label # Fail to parse number
                 
        return ('part', num)


    clean_label = re.sub(r'^(chapter|capitulo|capítulo)\s*', '', label)
    
    # Check for digit or roman
    num_match = re.match(r'^(\d+|[ivxlcdm]+)(?:[\.\:\s]|$)', clean_label)
    if num_match:
        num_str = num_match.group(1).upper()
        is_digit = num_str.isdigit()
        is_roman = not is_digit and all(c in 'IVXLCDM' for c in num_str)
        
        if is_digit:
            return ('chapter', int(num_str))
        elif is_roman:
            return ('chapter', roman_to_int(num_str))
            
    # Check for written number
    parsed_num = parse_written_number(clean_label)
    if parsed_num:
        return ('chapter', parsed_num)
    
    # --- TIME-BASED CHAPTER LABELS ---
    # For books like "Normal People" with labels like:
    # EN: "Six Weeks Later (September 2012)" or "January 2011"
    # ES: "Seis semanas más tarde" or "Enero de 2011"
    
    # Month mapping (EN and ES to month number)
    month_map = {
        # English
        'january': 1, 'february': 2, 'march': 3, 'april': 4,
        'may': 5, 'june': 6, 'july': 7, 'august': 8,
        'september': 9, 'october': 10, 'november': 11, 'december': 12,
        # Spanish
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
    }
    
    # Try to extract "(MONTH YEAR)" pattern from label
    date_in_parens = re.search(r'\(([^)]+)\)', label)
    if date_in_parens:
        date_str = date_in_parens.group(1).lower().strip()
        # Try "MONTH (DE)? YEAR" pattern
        date_match = re.search(r'(\w+)(?:\s+de)?\s+(\d{4})', date_str)
        if date_match:
            month_word = date_match.group(1)
            year = int(date_match.group(2))
            if month_word in month_map:
                return ('date-chapter', month_map[month_word], year)
    
    # Try "MONTH (DE)? YEAR" pattern directly (e.g., "January 2011", "Enero de 2011")
    date_match = re.search(r'^(\w+)(?:\s+de)?\s+(\d{4})$', label.strip())
    if date_match:
        month_word = date_match.group(1)
        year = int(date_match.group(2))
        if month_word in month_map:
            return ('date-chapter', month_map[month_word], year)
            
    return label

def split_sentences_helper(text):
    """
    Splits text into sentences using simple regex.
    """
    if not text:
        return []
    # Pattern: End punctuation + optional quotes + whitespace + Next is Upper/Start/Dash
    # Added em-dash (—) and en-dash (–) to lookahead for Spanish dialogue
    pattern = r'([.!?…]+(?:[”"’\'\)\]»]*)\s+(?=[A-Z¿¡"\'\-\—\–]))'
    parts = re.split(pattern, text)
    sentences = []
    current_sent = ""
    for i, part in enumerate(parts):
        if i % 2 == 0:
            current_sent += part
        else:
            current_sent += part
            sentences.append(current_sent.strip())
            current_sent = ""
    if current_sent and current_sent.strip():
        sentences.append(current_sent.strip())
    return sentences

def distribute_spanish(aligner, en_chunks, es_text):
    """
    Distributes Spanish text across multiple English chunks using semantic similarity.
    Returns a list of strings (one per en_chunk).
    """
    import numpy as np
    from scipy.spatial.distance import cosine
    
    # 0. Pre-checks
    if not es_text.strip():
        return [""] * len(en_chunks)
    if len(en_chunks) == 1:
        return [es_text]
        
    en_texts = [c['text'] for c in en_chunks]
    es_sents = split_sentences_helper(es_text)
    
    if not es_sents:
        return [""] * len(en_chunks)
        
    # 1. Embeddings
    en_embs = aligner.embed_chunks([{'text': t} for t in en_texts])
    es_embs = aligner.embed_chunks([{'text': t} for t in es_sents])
    
    results = []
    es_idx = 0
    
    # 2. Greedy Distribution
    for i, en_text in enumerate(en_texts):
        # Last chunk gets remainder
        if i == len(en_texts) - 1:
            remainder = " ".join(es_sents[es_idx:])
            results.append(remainder)
            break
            
        if es_idx >= len(es_sents):
            results.append("")
            continue
            
        en_vec = en_embs[i]
        en_len = len(en_text)
        
        best_cut = es_idx + 1
        best_score = float('inf')
        
        current_es_str = ""
        max_lookahead = min(len(es_sents) - es_idx, 20)
        
        # Look ahead to find best accumulation matching the current english chunk
        for k in range(max_lookahead):
            idx = es_idx + k
            sent = es_sents[idx]
            current_es_str += (" " + sent) if current_es_str else sent
            
            # Length Ratio Guard (looser than Splitter)
            ratio = len(current_es_str) / (en_len + 1)
            # If ratio is too small, keep adding. If too big, stop?
            # English might be 50 chars ("Figure 35") and Spanish 200 chars ("La Figura 35 muestra...")
            # So ratio can be high.
            # But "The idea is..." (short) vs "Se trata..." (short).
            # Let's rely mainly on cosine.
            
            # Vector Aggregation
            relevant_vecs = es_embs[es_idx : idx+1]
            if not isinstance(relevant_vecs, np.ndarray):
                relevant_vecs = np.vstack(relevant_vecs)
            cand_vec = np.mean(relevant_vecs, axis=0)
            
            dist = cosine(en_vec, cand_vec)
            
            # Bias slightly towards ratio ~ 1.0 - 1.5?
            # Add penalty for extreme ratios
            length_penalty = 0
            if ratio < 0.2: length_penalty = 0.5
            if ratio > 3.0: length_penalty = 0.5
            
            final_score = dist + length_penalty
            
            if final_score < best_score:
                best_score = final_score
                best_cut = idx + 1
                
        # Commit best cut
        part = " ".join(es_sents[es_idx:best_cut])
        results.append(part)
        es_idx = best_cut
        
    return results

def save_cleaned_opf(soup, path):
    """
    Saves the OPF soup to path, stripping 'opf:' prefixes from metadata tags
    to ensure compatibility with readers expecting standard namespaces.
    """
    content = str(soup)
    
    # Strip opf: prefix from metadata and meta tags
    # We do simple string replacement as regex might overlap if not careful, 
    # but exact tags are predictable from BS4 xml output.
    
    # Replace open tags
    content = content.replace('<opf:metadata', '<metadata')
    content = content.replace('<opf:meta', '<meta')
    
    # Replace close tags
    content = content.replace('</opf:metadata>', '</metadata>')
    content = content.replace('</opf:meta>', '</meta>')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def merge_bleeding_blocks(aligner, blocks):
    """
    Detects if the end of block N bleeds into the start of block N+1.
    If similarity(en_chunks[-1].last_sentence, es_chunks[0].first_sentence) is high,
    merge the blocks and flag for forced redistribution.
    """
    if not blocks: return []
    
    merged = []
    skip_next = False
    
    import numpy as np
    from scipy.spatial.distance import cosine
    
    for i in range(len(blocks)):
        if skip_next:
            skip_next = False
            continue
            
        current_block = blocks[i]
        
        # Determine if we can check next block
        if i + 1 >= len(blocks):
            merged.append(current_block)
            continue
            
        next_block = blocks[i+1]
        
        # Check candidates
        if not current_block['en_chunks'] or not next_block['es_chunks']:
            merged.append(current_block)
            continue
            
        last_en_chunk = current_block['en_chunks'][-1]
        first_es_chunk = next_block['es_chunks'][0]
        
        # Extract "sentences" (simplistic split for check)
        en_text = last_en_chunk['text'].strip()
        es_text = first_es_chunk['text'].strip()
        
        # Heuristic: verify short snippets match
        en_sents = re.split(r'[.?!]\s+', en_text)
        es_sents = re.split(r'[.?!]\s+', es_text)
        
        candidate_en = en_sents[-1] if en_sents else en_text
        candidate_es = es_sents[0] if es_sents else es_text
        
        # Compute Sim
        try:
            emb_en = aligner.embed_chunks([{'text': candidate_en}])[0]
            emb_es = aligner.embed_chunks([{'text': candidate_es}])[0]
            sim = 1 - cosine(emb_en, emb_es)
            
            # Threshold from investigation: 0.6148
            if sim > 0.6:
                print(f"Merge Triggered: '{candidate_en[:20]}...' vs '{candidate_es[:20]}...' (Sim: {sim:.4f})")
                
                # Merge
                new_block = {
                    'en_chunks': current_block['en_chunks'] + next_block['en_chunks'],
                    'es_chunks': current_block['es_chunks'] + next_block['es_chunks'],
                    'force_distribution': True
                }
                merged.append(new_block)
                skip_next = True
            else:
                merged.append(current_block)
                
        except Exception as e:
            print(f"Merge check failed: {e}")
            merged.append(current_block)
            
    return merged 

def align_tocs(en_toc, es_toc):
    """
    Aligns chapters using a hybrid 'Anchor and Fill' strategy.
    Returns list of (label, en_src, es_src).
    Includes unmatched items from both sides (paired with None) to ensure no content is lost.
    """
    en_items = []
    for i, item in enumerate(en_toc):
        norm = normalize_label(item['label'])
        raw = item['label'].lower().strip()
        # Don't skip empty labels - we'll use filename matching for them
        en_items.append({'idx': i, 'item': item, 'norm': norm, 'raw':  raw})

    es_items = []
    for i, item in enumerate(es_toc):
        norm = normalize_label(item['label'])
        raw = item['label'].lower().strip()
        # Filter Ignored Items (but not empty labels)
        if raw in ['tabla de contenido', 'contenido', 'página de título', 'cubierta', 'derechos de autor']: continue
        es_items.append({'idx': i, 'item': item, 'norm': norm, 'raw': raw})
    
    anchors = []
    en_matched = set()
    es_matched = set()
    
    # GLOBAL BEST MATCH STRATEGY (Stable Marriage Approx)
    
    candidates = [] # (score, en_idx, es_idx)
    
    for i, en in enumerate(en_items):
        en_label = en['item']['label']
        en_norm = normalize_label(en_label)
        en_level = en['item'].get('level', 1)
        
        for j, es in enumerate(es_items):
             es_label = es['item']['label']
             es_norm = normalize_label(es_label)
             es_level = es['item'].get('level', 1)
             
             score = 0
             
             # 1. Filename-based matching for empty labels
             if not en['raw'] and not es['raw']:
                 # Both labels are empty - use position-based matching primarily
                 # This handles cases where filename numbers have inconsistent offsets
                 # (e.g., content0011 -> Sec0009, content0012 -> Sec0010)
                 
                 # Position matching: chapters at same relative position should match
                 en_pos = i / len(en_items) if len(en_items) > 0 else 0
                 es_pos = j / len(es_items) if len(es_items) > 0 else 0
                 pos_diff = abs(en_pos - es_pos)
                 
                 # High score for items at same position
                 if pos_diff < 0.05:  # Within 5% position
                     score = 0.95
                 elif pos_diff < 0.15:  # Within 15% position  
                     score = 0.8
                 else:
                     score = max(0.3, 0.8 - (pos_diff * 2))  # Decay with distance
                     
             # 2. Exact Normalized Match (Highest Priority for non-empty labels)
             elif en_norm and en_norm == es_norm:
                 score = 1.0
             else:
                 # 3. Fuzzy Match
                 import difflib
                 sim = difflib.SequenceMatcher(None, en_label.lower(), es_label.lower()).ratio()
                 score = sim
                 
             # PENALTIES
             # Level Mismatch Penalty
             if abs(en_level - es_level) > 0:
                 # Strict rejection for mismatch
                 if score < 0.9: score = 0 
             
             # Relative Position Penalty (Keep diagonal)
             en_pos = i / len(en_items) if en_items else 0
             es_pos = j / len(es_items) if es_items else 0
             pos_diff = abs(en_pos - es_pos)
             if pos_diff > 0.3:
                 score -= 0.2
                 
             if score > 0.3: # Min Threshold
                candidates.append((score, i, j))
                
    # Sort by Score Descending
    candidates.sort(key=lambda x: x[0], reverse=True)
    
    # Assign
    en_assigned = set()
    es_assigned = set()
    matches_map = {} # en_idx -> es_idx
    
    for score, i, j in candidates:
        if i in en_assigned or j in es_assigned:
            continue
            
        matches_map[i] = j
        en_assigned.add(i)
        es_assigned.add(j)
        
    anchors = []
    
    for i, en_item_data in enumerate(en_items):
        if i in matches_map:
            es_idx = matches_map[i]
            anchors.append((en_item_data, es_items[es_idx]))
        else:
            # Unmatched EN - Logic requires us to return only matched/anchors? 
            # Original function returned list of (en, es).
            # If not matched, we skip it here.
            pass
    
    # Sort by English index to keep order
    anchors.sort(key=lambda x: x[0]['idx'])
    
    # --- FILTER ANCHORS FOR MONOTONICITY (LIS) ---
    # We need to find the Longest Increasing Subsequence of Spanish indices.
    # Anchors that violate the sequence are likely mismatches (e.g. Front Note <-> Back Note).
    
    if anchors:
        es_indices = [x[1]['idx'] for x in anchors]
        
        # Standard LIS algorithm O(N log N) or O(N^2) - N is small here
        # We need to retrieve the actual items, not just length.
        
        # Simple O(N^2) approach for reconstruction
        n = len(es_indices)
        # dp[i] = (length, predecessor_index)
        dp = [(1, -1)] * n
        
        for i in range(1, n):
            for j in range(i):
                if es_indices[j] < es_indices[i]:
                    if dp[j][0] + 1 > dp[i][0]:
                        dp[i] = (dp[j][0] + 1, j)
                        
        # Find max length
        max_len_idx = -1
        max_len = 0
        for i in range(n):
            if dp[i][0] > max_len:
                max_len = dp[i][0]
                max_len_idx = i
                
        # Reconstruct path
        lis_indices = []
        curr = max_len_idx
        while curr != -1:
            lis_indices.append(curr)
            curr = dp[curr][1]
            
        lis_indices.reverse()
        
        # Filter anchors
        valid_anchors = [anchors[i] for i in lis_indices]
        
        if len(valid_anchors) < len(anchors):
            print(f"Refined Anchors via LIS: {len(anchors)} -> {len(valid_anchors)} (Removed outliers)")
            
        anchors = valid_anchors

    final_pairs = []
    
    # 2. Fill Gaps
    last_en_idx = -1
    # Add a sentinel anchor at the end to handle trailing items
    # CAUTION: If we used N-to-1 mapping, we can't assume 1-to-1 gaps.
    # But the gap fill logic simply zips what's between anchors.
    # If consecutive anchors map [En1->Es1, En2->Es1], the gap between En1 and En2 is empty.    
    # --- Phase 2: Fill Gaps Between Anchors ---
    # Gaps are unmatched EN/ES items between consecutive anchors.
    # We pair them linearly (zip-like) BUT with strict duplicate prevention.
    final_pairs = []
    last_en_idx = -1
    last_es_idx = -1
    
    # CRITICAL: Track ALL used ES sources to prevent duplication
    used_es_sources = set()
    
    # Pre-populate with anchor ES sources
    for anchor_en, anchor_es in anchors:
        # Only add if it's a real item, not a sentinel
        if 'src' in anchor_es['item']:
            used_es_sources.add(anchor_es['item']['src'])
    
    sentinel_en = {'idx': len(en_items), 'item': {'label': 'SENTINEL_EN', 'src': None, 'level': 0}}
    sentinel_es = {'idx': len(es_items), 'item': {'label': 'SENTINEL_ES', 'src': None, 'level': 0}}
    anchors.append((sentinel_en, sentinel_es))

    for anchor_en, anchor_es in anchors:
        current_en_idx = anchor_en['idx']
        current_es_idx = anchor_es['idx']
        
        gap_en = [x for x in en_items if last_en_idx < x['idx'] < current_en_idx and x['idx'] not in en_assigned]
        gap_es = [x for x in es_items if last_es_idx < x['idx'] < current_es_idx and x['idx'] not in es_assigned]
        
        # STRICT PAIRING: Only pair if we have BOTH EN and ES, and ES is NOT already used
        for k in range(min(len(gap_en), len(gap_es))):
            en_item = gap_en[k]
            es_item = gap_es[k]
            
            en_src = en_item['item']['src']
            es_src = es_item['item']['src']
            
            # DUPLICATE CHECK
            if es_src in used_es_sources:
                # This ES source was already used (by an anchor or earlier gap item)
                # Leave EN unmatched rather than duplicate
                final_pairs.append((en_item['item']['label'], en_src, None, en_item['item'].get('level', 0)))
                continue
            
            # Valid 1-to-1 pairing
            used_es_sources.add(es_src)
            label = en_item['item']['label']
            level = en_item['item'].get('level', 0)
            final_pairs.append((label, en_src, es_src, level))
        
        # Handle EXCESS English chapters (more EN than ES in gap)
        for k in range(min(len(gap_en), len(gap_es)), len(gap_en)):
            en_item = gap_en[k]
            final_pairs.append((en_item['item']['label'], en_item['item']['src'], None, en_item['item'].get('level', 0)))
        
        # Handle EXCESS Spanish chapters (more ES than EN in gap)
        # These are orphaned Spanish content - we can't align them
        for k in range(min(len(gap_en), len(gap_es)), len(gap_es)):
            es_item = gap_es[k]
            es_src = es_item['item']['src']
            if es_src not in used_es_sources:
                used_es_sources.add(es_src)
                final_pairs.append((es_item['item']['label'], None, es_src, es_item['item'].get('level', 0)))
             
        # Add the Anchor itself (if not sentinel)
        if current_en_idx < len(en_items) and current_es_idx < len(es_items):
             level = anchor_en['item'].get('level', 0)
             final_pairs.append((anchor_en['item']['label'], anchor_en['item']['src'], anchor_es['item']['src'], level))
             
        last_en_idx = current_en_idx
        last_es_idx = current_es_idx
        
    return final_pairs

def align_by_spine(en_base, es_base, en_toc_path, es_toc_path):
    """
    Fallback alignment using OPF spine order when TOC matching fails.
    Filters out front/back matter and pairs content chapters by position.
    Returns list of (label, en_src, es_src, level).
    """
    print("Attempting spine-based alignment...")
    
    # Find OPF files
    en_opf = find_opf_file(en_base)
    es_opf = find_opf_file(es_base)
    
    if not en_opf or not es_opf:
        print("WARNING: Could not find OPF files for spine-based alignment")
        return []
    
    def get_spine_items(opf_path):
        """Extract spine items from OPF file."""
        try:
            with open(opf_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'xml')
            
            # Build manifest id -> href map
            manifest = {}
            for item in soup.find_all('item'):
                item_id = item.get('id')
                href = item.get('href')
                if item_id and href:
                    manifest[item_id] = href
            
            # Get spine order
            spine = []
            for itemref in soup.find_all('itemref'):
                idref = itemref.get('idref')
                if idref and idref in manifest:
                    spine.append(manifest[idref])
            
            return spine
        except Exception as e:
            print(f"Error reading OPF spine: {e}")
            return []
    
    def is_excluded_page(filename):
        """Heuristic to detect pages that should NOT be aligned (true front/back matter)."""
        lower = filename.lower()
        # Strict exclusion patterns - only truly non-alignable pages
        excluded = [
            'cover', 'cubierta', 'cvi_',  # Cover pages
            'copyright', 'creditos', 'derechos', 'cop_',  # Copyright
            'toc_', 'nav', '_toc', 'indice', 'content.xhtml',  # Navigation
            'promo', 'sinopsis', 'about', 'bio', 'autor', 'adc_',  # Back matter
            'acknowledgment', 'agradecimiento', 'ack_',  # Acknowledgments (usually at end)
            'notes', 'notas', 'bibliography', 'bibliografia',  # References
        ]
        for p in excluded:
            if p in lower:
                return True
        return False
    
    en_spine = get_spine_items(en_opf)
    es_spine = get_spine_items(es_opf)
    
    print(f"EN spine items: {len(en_spine)}")
    print(f"ES spine items: {len(es_spine)}")
    
    # Filter to alignable content (everything except strict exclusions)
    en_content = [f for f in en_spine if not is_excluded_page(f)]
    es_content = [f for f in es_spine if not is_excluded_page(f)]
    
    print(f"EN content chapters: {len(en_content)}")
    print(f"ES content chapters: {len(es_content)}")
    
    # Pair by position
    pairs = []
    min_len = min(len(en_content), len(es_content))
    
    for i in range(min_len):
        en_src = en_content[i]
        es_src = es_content[i]
        # Use EN filename as label, or extract from path
        label = os.path.splitext(os.path.basename(en_src))[0]
        pairs.append((label, en_src, es_src, 0))
    
    # Handle remaining EN chapters (no ES translation)
    for i in range(min_len, len(en_content)):
        en_src = en_content[i]
        label = os.path.splitext(os.path.basename(en_src))[0]
        pairs.append((label, en_src, None, 0))
    
    # Handle remaining ES chapters (extra Spanish content)
    for i in range(min_len, len(es_content)):
        es_src = es_content[i]
        label = os.path.splitext(os.path.basename(es_src))[0]
        pairs.append((label, None, es_src, 0))
    
    print(f"Spine-based alignment: {len(pairs)} chapter pairs")
    return pairs

def extract_chapter_number(filename):
    """
    Extracts the first significant number from a filename.
    Useful for aligning 'chapter001.xhtml' with '1.html'.
    Returns int or None.
    """
    if not filename: return None
    base = os.path.basename(filename)
    # Look for patterns like 'chapter001', 'part01', or just '1.html'
    # Priority: numbers embedded in text
    
    # 1. Look for 'chapter' followed by digits
    m = re.search(r'chapter[-_]?(\d+)', base, re.IGNORECASE)
    if m: return int(m.group(1))

    # 2. Look for just leading digits (e.g. '1.html')
    m = re.match(r'^(\d+)', base)
    if m: return int(m.group(1))
    
    # 3. Look for ANY digits? Dangerous ('part2_chapter1')
    # Let's try to be smart. 'split_000' is secondary.
    # What about 'chapter001_split_000'? 'chapter(\d+)' catches it.
    
    # What if it is just 'name.html'? None.
    return None

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def split_sentences(text):
    """
    Splits text into sentences using the helper regex function.
    Restored for Heuristic Alignment drill-down.
    """
    return split_sentences_helper(text)


def split_sentences_aggressive(text):
    """Deprecated: No longer splits."""
    return split_sentences(text)

def find_opf_file(base_dir):
    """Recursively searches for the first .opf file in the directory."""
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.opf'):
                return os.path.join(root, f)
    return None

def read_opf_data(opf_path):
    """
    Extracts comprehensive data from an OPF file:
    - Metadata elements (list of dicts with tag, text, attribs)
    - Manifest mapping (id -> href)
    - Cover ID (if found in meta name="cover")
    - Textual metadata (Title, Language, Creator) for convenience
    - UUID data
    - Namespaces defined in the package
    """
    data = {
        'title': "Bilingual Edition",
        'language': "en",
        'creator': "Unknown",
        'uid': "urn:uuid:12345",
        'uid_scheme': "BookId",
        'cover_id': None,
        'metadata_items': [], # List of objects to reconstruct strings
        'manifest': {},
        'namespaces': {}
    }

    if not opf_path or not os.path.exists(opf_path):
        return data

    try:
        # 0. Extract Namespaces using iterparse
        # We need to re-open the file for iterparse to catch start-ns events at the top
        for event, (prefix, uri) in ET.iterparse(opf_path, events=['start-ns']):
            if prefix: # Skip default namespace if empty, or handle it
                data['namespaces'][prefix] = uri
        
        # 1. Parse Tree
        tree = ET.parse(opf_path)
        root = tree.getroot()
        
        # Register namespaces to prevent "ns0" prefixes if possible, though strict valid XML output needs careful handling
        for prefix, uri in data['namespaces'].items():
            ET.register_namespace(prefix, uri)

        # Standard Namespaces for finding things
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # Update our lookup ns with found ones
        ns.update(data['namespaces'])
        
        # 1. Metadata
        # We look for the metadata tag using the standard namespace or wildcard
        metadata_node = root.find('opf:metadata', ns)
        if metadata_node is None:
             # Fallback: try finding it by tag name ignoring namespace
             for child in root:
                 if child.tag.endswith('}metadata'):
                     metadata_node = child
                     break

        if metadata_node is not None:
            # Capture ALL children
            for child in metadata_node:
                # Store the full tag, text, and attributes
                # We will attempt to reconstruct the tag with the correct prefix later
                
                # Check for specific fields for convenience
                # We use the tag without namespace for checking
                clean_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                text = child.text
                
                if 'title' == clean_tag: data['title'] = text
                elif 'language' == clean_tag: data['language'] = text
                elif 'creator' == clean_tag: data['creator'] = text
                
                # Check for cover meta
                if 'meta' == clean_tag and child.get('name') == 'cover':
                    data['cover_id'] = child.get('content')

                # Store for reproduction
                # We save the raw element info
                item = {'tag': child.tag, 'text': text, 'attrib': child.attrib}
                data['metadata_items'].append(item)

            # Resolve Identifier
            package_uid_ref = root.get('unique-identifier')
            if package_uid_ref:
                data['uid_scheme'] = package_uid_ref
                # Try to find the specific identifier
                for child in metadata_node:
                    if child.tag.endswith('}identifier') and child.get('id') == package_uid_ref:
                        data['uid'] = child.text
                        break

        # 2. Manifest
        manifest_node = root.find('opf:manifest', ns)
        if manifest_node is None:
             for child in root:
                 if child.tag.endswith('}manifest'):
                     manifest_node = child
                     break

        if manifest_node is not None:
            for item in manifest_node: # Iterate children directly
                if item.tag.endswith('}item'):
                    i_id = item.get('id')
                    i_href = item.get('href')
                    i_media = item.get('media-type')
                    if i_id and i_href:
                        data['manifest'][i_id] = {'href': i_href, 'media-type': i_media}

    except Exception as e:
        print(f"Error reading OPF data: {e}")
        
    return data


class BaseParser(HTMLParser):
    def __init__(self, config, raw_source=""):
        super().__init__()
        self.config = config
        self.image_tag = config.get('image_tag', 'img') # Deprecated single
        self.image_tags = config.get('image_tags', ['img', 'image', 'svg:image'])
        # Merge single into list if present
        if self.image_tag not in self.image_tags:
            self.image_tags.append(self.image_tag)
        self.chunks = [] 
        self.current_chunk = None
        self.capture_text = False
        self.raw_source = raw_source
        self.line_offsets = []
        
        # List State Tracking
        self.list_stack = [] # Stack of {'tag': 'ol'|'ul', 'count': 0}
        
        if raw_source:
             self._calculate_offsets()
             
    def _calculate_offsets(self):
        offset = 0
        for line in self.raw_source.splitlines(keepends=True):
            self.line_offsets.append(offset)
            offset += len(line)
            
    def get_offset(self, line, col):
        if not self.line_offsets or line - 1 >= len(self.line_offsets):
            return 0
        return self.line_offsets[line - 1] + col

    def finish_chunk(self):
        if self.current_chunk:
            self.current_chunk['text'] = clean_text(self.current_chunk['text'])
            
            # Extract Raw HTML if valid
            if self.raw_source and 'start_pos' in self.current_chunk and 'end_pos' in self.current_chunk:
                s = self.current_chunk['start_pos']
                e = self.current_chunk['end_pos']
                # Try to capture the inner content
                # The positions from getpos() are at the START of the tag. 
                # Ideally we want the inner HTML, but capturing the whole element is easier then stripping outer tag.
                # ACTUALLY: handle_starttag pos is at '<', handle_endtag pos is at '<'.
                # So we need to find where the start tag ends to get inner HTML? 
                # Or just store the full outer HTML and we decide how to render?
                
                # Let's try to grab the Inner HTML if possible.
                # But typically regex/parsing re-construction is safer if we just grab outer and strip.
                # However, for 'p', we might just want to grab the content.
                
                # Simple approach for now: grab EVERYTHING from End of Start Tag to Start of End Tag?
                # We don't easily know length of start tag from handle_starttag without parsing attrs again.
                # Let's grab the raw slice from (start_line, start_col) to (end_line, end_col).
                pass

            if self.current_chunk['text'] or self.current_chunk['type'] == 'header' or self.current_chunk['type'] == 'image':
                 self.chunks.append(self.current_chunk)
            self.current_chunk = None
            self.capture_text = False

    def handle_data(self, data):
        if self.capture_text and self.current_chunk:
            self.current_chunk['text'] += data




class EnglishParser(BaseParser):
    def __init__(self, config, raw_source=""):
        super().__init__(config, raw_source)
        self.in_caption = False
        self.rules = self.config['en']

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        
        # Handle BR for English
        if tag == 'br':
            if self.current_chunk:
                self.current_chunk['text'] += " "
            self.finish_chunk()
            self.current_chunk = {
                'tag': 'p',
                'classes': [],
                'text': '',
                'type': 'std'
            }
            self.capture_text = True
            return

        header_tags = self.rules.get('header_tags', [])
        
        if tag in header_tags:
            # Check for Merge: h1.CT merging into preceding h1.CN
            if tag == 'h1' and 'CT' in classes:
                if self.chunks:
                    prev = self.chunks[-1]
                    if prev['tag'] == 'h1' and 'CN' in prev['classes']:
                        self.finish_chunk() # Ensure any pending text is flushed (unlikely if strictly structural)
                        # Actually finish_chunk pushes current_chunk. 
                        # We want to re-open the *previous* completed chunk.
                        self.current_chunk = self.chunks.pop()
                        self.current_chunk['text'] += " "
                        self.capture_text = True
                        return

            self.finish_chunk()
            
            chunk_type = 'std'
            # Strict header detection
            if tag == 'h1':
                valid_classes = self.rules.get('header_classes', [])
                if any(c in classes for c in valid_classes):
                    chunk_type = 'header'
                else:
                    chunk_type = 'std'
            elif tag.startswith('h'): 
                chunk_type = 'header'
            
            self.current_chunk = {
                'tag': tag,
                'classes': classes,
                'text': '',
                'type': chunk_type,
                'raw_start_offset': self.get_offset(*self.getpos())
            }
            self.capture_text = True
            
        elif tag in self.image_tags:
            # Capture current context before finishing chunk
            parent_tag = self.current_chunk['tag'] if self.current_chunk else 'p'
            parent_classes = self.current_chunk['classes'] if self.current_chunk else []
            
            self.finish_chunk()
            
            src = attr_dict.get('src') or attr_dict.get('xlink:href') # Support xlink for svg:image
            alt = attr_dict.get('alt', '')
            width = attr_dict.get('width')
            height = attr_dict.get('height')
            style = attr_dict.get('style')
            # Extract classes specifically on the img tag. 
            # Note: 'classes' key stores PARENT classes (from p/div), so we use 'img_classes'
            img_classes = attr_dict.get('class', '').split()
            
            if src:
                self.chunks.append({
                    'type': 'image',
                    'tag': 'img', # Normalize to img for internal use
                    'src': src,
                    'alt': alt,
                    'width': width,
                    'height': height,
                    'img_style': style,
                    'img_classes': img_classes,
                    'text': '',
                    'classes': parent_classes, # Inherit parent classes
                    'wrapper_tag': parent_tag, # Preserve original wrapper (figure, etc)
                    'as_en': True # Assume EN by default, alignment will fix
                })
            
            # Start a new chunk for subsequent text, inheriting the current container tag
            self.current_chunk = {
                'type': 'std',
                'tag': parent_tag,
                'text': '',
                'classes': [],
                'raw_html': None
            }
            self.capture_text = True
            return

        if tag in ['br', 'hr']:
            if self.current_chunk:
                self.current_chunk['text'] += " "
            self.finish_chunk()
            return

        elif tag in self.rules.get('caption_start_tags', []):
            self.finish_chunk()
            self.current_chunk = {
                'tag': tag,
                'classes': classes,
                'text': '',
                'type': 'caption',
                'raw_start_offset': self.get_offset(*self.getpos())
            }
            self.capture_text = True
            self.in_caption = True
            
        elif tag == 'p':
            if self.in_caption and self.rules.get('ignore_p_in_caption'): return
            self.finish_chunk()
            self.current_chunk = {
                'tag': tag,
                'classes': classes,
                'text': '',
                'type': 'caption' if self.in_caption else 'std',
                'raw_start_offset': self.get_offset(*self.getpos())
            }
            self.capture_text = True


    def handle_endtag(self, tag):
        # Capture raw html end pos
        if self.current_chunk and self.capture_text:
             # This is called at the start of the end tag </p>
             # To capture raw inner html, we need the end of the previous data?
             # Or we define that raw_html is everything accumulated?
             
             # BETTER STRATEGY: 
             # We rely on capturing the raw span from the source string.
             # start_offset was set in handle_starttag?
             
             # Calculate current offset
             end_offset = self.get_offset(*self.getpos())
             
             if 'raw_start_offset' in self.current_chunk:
                  # This slice includes the start tag but excludes the end tag (because getpos is at < of </p>)
                  # BUT: We don't know the length of the start tag '<p class="foo">'
                  # So we can't easily isolate just the inner text without parsing the start tag string.
                  
                  # ALTERNATIVE: Use the Accumulated Data + Re-tagging?
                  # No, the user wants <i> and <small> and <span class="foo"> preserved.
                  # Standard HTMLParser strips those unless we reconstruct them.
                  
                  # NEW APPROACH:
                  # We extract the full content from start_offset to end_offset.
                  # This includes the Open Tag '<p class="x">'.
                  # Then we strip the open tag regex-style?
                  
                  full_slice = self.raw_source[self.current_chunk['raw_start_offset']:end_offset]
                  
                  # Remove the first tag (start tag)
                  # Be careful with nested tags passed as data (rare in valid XHTML but possible)
                  # A regex to match the first <[^>]+>
                  match = re.match(r'<[^>]+>', full_slice)
                  if match:
                      inner_html = full_slice[match.end():]
                      self.current_chunk['raw_html'] = inner_html.strip()
                  else:
                      self.current_chunk['raw_html'] = full_slice # Fallback
             
        header_tags = self.rules.get('header_tags', [])
        if tag in header_tags:
             self.finish_chunk()
        elif tag == 'img':
             pass # Void tag, already finished
        elif tag in self.rules.get('caption_start_tags', []):
             self.finish_chunk()
             self.in_caption = False
        elif tag == 'p':
            if self.in_caption and self.rules.get('ignore_p_in_caption'): return
            self.finish_chunk()

class SpanishParser(BaseParser):
    def __init__(self, config, raw_source=""):
        super().__init__(config, raw_source)
        self.ignore_section = False
        self.ignore_depth = 0
        self.rules = self.config['es']

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        
        # Ignore sections
        ignore_divs = self.rules.get('ignore_div_classes', [])
        if tag == 'div' and any(c in classes for c in ignore_divs):
            self.ignore_section = True
            self.ignore_depth = 1
            return
        
        if self.ignore_section:
            self.ignore_depth += 1
            return
            
        ignore_classes = self.rules.get('ignore_classes', [])
        if any(c in classes for c in ignore_classes):
            return

        # Handle BR for Spanish
        if tag == 'br':
            if self.current_chunk:
                self.current_chunk['text'] += " "
            self.finish_chunk()
            self.current_chunk = {
                'tag': 'p',
                'classes': [],
                'text': '',
                'type': 'std'
            }
            self.capture_text = True
            return

        # Image Handling (Ported from EnglishParser)
        if tag in self.image_tags:
            # Capture current context before finishing chunk
            parent_tag = self.current_chunk['tag'] if self.current_chunk else 'p'
            
            self.finish_chunk()
            
            src = attr_dict.get('src') or attr_dict.get('xlink:href')
            alt = attr_dict.get('alt', '')
            
            if src:
                # Synthesize raw_html so it carries through alignment
                raw_img = f'<img src="{src}" alt="{alt}" />'
                if classes:
                     cls_str = " ".join(classes)
                     raw_img = f'<img src="{src}" class="{cls_str}" alt="{alt}" />'
                     
                self.chunks.append({
                    'type': 'image',
                    'tag': 'img', 
                    'src': src,
                    'alt': alt,
                    'text': '',
                    'classes': classes,
                    'raw_html': raw_img,
                    'as_en': False 
                })
            
            # Start a new chunk for subsequent text
            self.current_chunk = {
                'type': 'std',
                'tag': parent_tag,
                'text': '',
                'classes': [],
                'raw_html': None
            }
            self.capture_text = True
            return

    # Block-level tags that should initiate a chunk
        block_tags = ['p', 'div', 'li'] + [f'h{i}' for i in range(1, 7)]
        target_tags = set(block_tags + self.rules.get('header_tags', []))

        if tag in target_tags:
            # Check for Header Merge (Melanie Profile specific)
            merge_trigger = self.rules.get('header_merge_trigger')
            if merge_trigger and merge_trigger in classes:
                if self.chunks:
                    prev_type = self.chunks[-1].get('special_type')
                    merge_targets = self.rules.get('header_merge_targets', [])
                    if prev_type in merge_targets:
                        self.current_chunk = self.chunks.pop()
                        self.current_chunk['text'] += " "
                        self.capture_text = True
                        return

            self.finish_chunk() 
            
            chunk_type = 'std'
            special_type = None
            is_header = False
            
            # 1. Native Header Tags
            if tag.startswith('h'): 
                is_header = True
            
            # 2. Configured Indicators
            header_indicators = self.rules.get('header_indicators', [])
            for ind in header_indicators:
                 if ind in classes or any(ind in c for c in classes):
                     is_header = True
                     special_type = ind
                     break
            
            if is_header:
                chunk_type = 'header'
            else:
                # Check for captions
                caption_classes = self.rules.get('caption_classes', [])
                citation_sub = self.rules.get('citation_substring', 'Citas')

                if any(c in classes for c in caption_classes):
                    chunk_type = 'caption'
                elif any(citation_sub in c for c in classes):
                    chunk_type = 'std'
            
            self.current_chunk = {
                'tag': tag,
                'classes': classes,
                'text': '',
                'type': chunk_type,
                'special_type': special_type,
                'raw_start_offset': self.get_offset(*self.getpos())
            }
            
            # Special Handling for <ol> lists:
            # If we are inside an <ol>, we should inject the number into the text
            # so that it aligns with explicit numbered lists in the other language.
            # (Note: self.list_stack should track 'ol'/'ul' state)
            # But BaseParser doesn't track list stack well yet. Let's add simple check.
            # OR: just check if parent tag was ol? No, handle_starttag usage prevents easy parent access without stack.
            # Assuming 'li' is block tag now.
            
            if tag == 'li':
                 # Hack: Check if we are in an Ordered List. 
                 # We need to maintain a counter.
                 # Let's add self.in_ordered_list and self.list_counter to __init__?
                 # Too invasive.
                 pass
            

            if tag in ['ol', 'ul']:
                self.list_stack.append({'tag': tag, 'count': 0})
            
            if tag == 'li' and self.list_stack:
                parent = self.list_stack[-1]
                if parent['tag'] == 'ol':
                     parent['count'] += 1
                     # Inject Number: "1. "
                     self.current_chunk['text'] = f"{parent['count']}. "
            
            self.capture_text = True

    def handle_endtag(self, tag):
        if tag in ['ol', 'ul'] and self.list_stack:
             self.list_stack.pop()

        if self.ignore_section:
            self.ignore_depth -= 1
            if self.ignore_depth == 0:
                self.ignore_section = False
            return

        # Capture raw html logic (Same as English)
        if self.current_chunk and self.capture_text and tag in ['p', 'div'] + [f'h{i}' for i in range(1, 7)]:
             end_offset = self.get_offset(*self.getpos())
             if 'raw_start_offset' in self.current_chunk:
                  full_slice = self.raw_source[self.current_chunk['raw_start_offset']:end_offset]
                  match = re.match(r'<[^>]+>', full_slice)
                  if match:
                      inner_html = full_slice[match.end():]
                      self.current_chunk['raw_html'] = inner_html.strip()
                  else:
                      self.current_chunk['raw_html'] = full_slice

            
        if tag == 'p':
             self.finish_chunk()

    def handle_data(self, data):
        if self.ignore_section:
            return
        super().handle_data(data)

    def finish_chunk(self):
        # Override to perform text-based classification before finalizing
        if self.current_chunk and self.current_chunk['type'] == 'std':
             text = self.current_chunk['text'].strip()
             # Check for "Figura X" pattern
             # We match "Figura" followed by a number
             if re.match(r'^Figura\s+\d+', text, re.IGNORECASE):
                 self.current_chunk['type'] = 'caption'
                 
        super().finish_chunk()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def clean_text(t):
    return re.sub(r'\s+', ' ', t).strip()

def find_nearest_sentence_end(text, target_idx):
    if target_idx >= len(text): return len(text)
    fwd_dot = text.find('.', target_idx)
    bwd_dot = text.rfind('.', 0, target_idx)
    candidates = []
    if fwd_dot != -1: candidates.append(fwd_dot)
    if bwd_dot != -1: candidates.append(bwd_dot)
    if not candidates: return -1 
    closest = min(candidates, key=lambda x: abs(x - target_idx))
    return closest + 1

def smart_pair_split(en_text, es_text):
    """Deprecated: Returns original text paired."""
    return [en_text], [es_text]

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------

def parse_file(path, parser_cls, config):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        parser = parser_cls(config, raw_source=content)
        parser.feed(content)
        parser.finish_chunk() # Flush
        return parser.chunks
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        return []
def get_header_indices(chunks):
    return [i for i, c in enumerate(chunks) if c['type'] == 'header']

def extract_nodes(soup):
    """
    DOM Extraction for Experimental Method.
    Traverses the soup and extracts text chunks with their DOM node references.
    Returns: list of dicts {'text': ..., 'node': ..., 'type': ...}
    """
    chunks = []
    
    # Target meaningful content elements
    # Added li, blockquote, div to be safe, but main content usually in p/h tags
    target_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'div', 'figcaption']
    
    # We use find_all to get them in document order
    # Note: This might get nested elements (div containing p). 
    # We should filter out elements that contain other target elements to avoid duplication?
    # Or rely on text content check.
    
    elements = soup.find_all(target_tags)
    
    for el in elements:
        # Check if this element contains other target elements (e.g. div wrapper)
        # EXCEPTION: figcaption often contains <p> but we want to extract figcaption itself
        if el.name != 'figcaption' and el.find(target_tags):
            continue
        # Skip elements whose parent is a figcaption (we already extract figcaption itself)
        if el.parent and el.parent.name == 'figcaption':
            continue
        # If it's figcaption, extract it (don't skip)
        if el.name == 'figcaption':
            pass # Proceed to extract
            
        text = el.get_text().strip()
        if not text:
            # Check for images?
            if el.find('img'):
                 chunks.append({
                    'text': '',
                    'node': el,
                    'tag': el.name,
                    'classes': el.get('class', []),
                    'type': 'image',
                    'raw_html': str(el)
                })
            continue
            
        # Determine specific type/classes
        classes = el.get('class', [])
        tag = el.name
        
        chunk_type = 'std'
        if tag.startswith('h'):
            chunk_type = 'header'
        # Detect captions via CSS class (figure/figura) OR text patterns
        elif any(c in ['figure', 'figura', 'figura1', 'caption'] for c in classes):
            chunk_type = 'caption'
        elif re.match(r'^(?:Figure|Figura|Table|Tabla|Box|Map|Mapa|Fig\.?)\s*\d+\s*[:\.\s]', text, re.IGNORECASE):
            chunk_type = 'caption'
        # Numbered captions starting with just "N." (e.g. "3. A speculative reconstruction...")
        elif re.match(r'^\d+\.\s+\S', text) and len(text) < 500:
            chunk_type = 'caption'
            
        chunks.append({
            'text': text,
            'node': el,
            'tag': tag,
            'classes': classes,
            'type': chunk_type,
            'raw_html': str(el) 
        })
        
    return chunks

def merge_consecutive_headers(chunks):
    """
    Merges consecutive header chunks into the first one, removing the subsequent nodes from the DOM.
    Useful when source splits 'Number' and 'Title' into separate H tags.
    """
    if not chunks: return []
    merged = []
    
    current_header = None
    
    for c in chunks:
        is_header = c.get('type') == 'header'
        # Treat images as standard or special? 
        # If image comes between headers, it breaks the merge? Yes.
        
        if is_header:
            if current_header:
                 # Merge with previous
                 # Join text
                 sep = " " 
                 current_header['text'] += sep + c['text']
                 # We assume the user wants 1 visible header.
                 # We must remove the second node from DOM to avoid duplication.
                 if c.get('node'):
                     # Decompose removes it from the tree entirely.
                     c['node'].decompose() 
                     # Set node to None in chunk just in case
                     c['node'] = None
            else:
                current_header = c
        else:
            if current_header:
                merged.append(current_header)
                current_header = None
            merged.append(c)
            
    if current_header:
        merged.append(current_header)
        
    return merged

def is_standalone_numeric_header(text):
    """
    Detects if a header contains only a number or minimal chapter marker.
    Examples that return True: "4", "Chapter 4", "4.", "IV", "CHAPTER 4"
    Examples that return False: "4: The Beginning", "Chapter 4: Introduction"
    """
    if not text:
        return False
    
    text = text.strip()
    
    # Pattern 1: Just a number (arabic or roman)
    # "4", "42", "IV", "XII"
    if text.isdigit():
        return True
    
    # Quick Win #2: Roman numerals
    # CAUTION: Spanish headers often are JUST "IX". We shouldn't filter them if they are likely headers.
    # We only filter if they look like minor structure (e.g. small part) AND aren't matching a chapter pattern.
    # But detecting that here is hard.
    # checking strict strict roman numeral (I, V, X, L, C, D, M)
    # If it's just a Roman numeral, it CAN be a header.
    # Let's REMOVE this aggressive filter for now to let Roman Numeral Constraints handle it.
    # if re.match(r'^[IVX]+\.?$', text):
    #     return True
     
    # Quick Win #2: All-caps short text (likely headers)
    # Refined: Only if very short and common words, or completely isolated.
    # "CHAPTER ONE" -> Keep it (don't return True to skip). We WANT to align headers.
    # The original intent of this function was to skip "Standalone Numeric Headers" that don't have translations.
    # But "Chapter One" usually HAS a translation "Capítulo Uno".
    # "3" might not.
    
    # Reverting aggressive filtering for textual headers to prevent data loss.
    # Only filter pure digits or symbols.
    
    # Scene break separators
    if re.match(r'^[*#\-—═]{3,}$', text):
        return True
    
    # Check for roman numerals
    if all(c in 'IVXLCDM' for c in text.upper()) and len(text) <= 10:
        return True
    
    # Pattern 2: Optional "Chapter/Part/Section" + number + optional punctuation
    # "Chapter 4", "CHAPTER 4", "Part IV", "4."
    pattern = r'^(?:chapter|part|section|ch\.?|pt\.?)\s*(?:\d+|[ivxlcdm]+)[\.:\s]*$'
    if re.match(pattern, text, re.IGNORECASE):
        return True
    
    # Pattern 3: Just number with punctuation
    # "4.", "4:", "42."
    pattern = r'^\d+[\.:\s]*$'
    if re.match(pattern, text):
        return True
    
    return False


def inject_translation(en_node, es_text, config, soup, en_text=None):
    if not en_node or not es_text:
        return
    
    # Check if using new layout mode system
    bilingual_config = config.get('bilingual')
    use_layout_modes = bilingual_config is not None
    # print(f"DEBUG: inject_translation called. Text len: {len(es_text) if es_text else 0}. LayoutMode: {use_layout_modes}")

    
    # 0. Pre-check: Extract Images from English Node?
    # User Request: Order should be EN -> ES -> IMG
    # Currently it is EN(with img) -> ES.
    # We detected if en_node has images, extract them, and append them AFTER the translation.
    
    extracted_images = []
    images = en_node.find_all(['img', 'svg'])
    if images:
        for img in images:
            extracted_images.append(img.extract()) # Remove from EN
    
    # Update English text if provided (e.g. from header merge)
    # This must happen AFTER image extraction but BEFORE translation injection
    if en_text:
        en_node.string = en_text

    # --- INLINE HEADER HANDLING ---
    # For headers (h1-h6), render both languages on the same line:
    # "5 The Best Way to Start a New Habit        5 La mejor manera de comenzar un nuevo hábito"
    is_header = en_node.name.lower() in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
    
    if is_header:
        # Inline mode: Append Spanish to the same header element
        # Separator: Use <br> for new line (User request)
        separator = soup.new_tag("br")
        
        from layout_helpers import apply_styling
        
        # Create span for Spanish styling
        span = soup.new_tag("span")
        # Apply unified styling logic
        apply_styling(span, config, is_translation=True)
        
        # Parse es_text as HTML to preserve formatting tags
        inner_content = BeautifulSoup(es_text, 'html.parser')
        if inner_content:
            span.append(inner_content)
        else:
            span.string = es_text
        
        # Append separator and Spanish span to the existing header
        en_node.append(separator)
        en_node.append(span)
        
        # Re-append extracted images if any
        if extracted_images:
            for img in extracted_images:
                en_node.append(img)
        
        return en_node  # Return the modified node
            
    # --- LAYOUT MODE SYSTEM (for paragraphs and other elements) ---
    if use_layout_modes:
        from layout_helpers import inject_layout_mode
        
        result_node = inject_layout_mode(soup, en_node, es_text, config)
        
        # Handle extracted images
        if extracted_images:
            # Create image container
            img_container = soup.new_tag(en_node.name)
            img_container.attrs = en_node.attrs.copy()
            if 'id' in img_container.attrs:
                del img_container.attrs['id']
            
            # Reset margins for image container
            img_style = img_container.get('style', '')
            if img_style and not img_style.endswith(';'):
                img_style += ';'
            img_container['style'] = img_style + " margin-top: 1em;"
            
            for img in extracted_images:
                img_container.append(img)
            
            # Insert after the result node
            if result_node:
                result_node.insert_after(img_container)
            else:
                en_node.insert_after(img_container)
        
        return result_node
    
    # --- LEGACY BLOCK MODE (backward compatibility) ---
    # 1. Exact Clone of the Wrapper (p, div, h1, etc.)
    # We create a new tag with the same name
    new_tag = soup.new_tag(en_node.name)
    # Copy all attributes exactly (classes, styles, data-attributes)
    new_tag.attrs = en_node.attrs.copy()
    
    # Remove ID to avoid invalid HTML (duplicate IDs)
    if 'id' in new_tag.attrs:
        del new_tag.attrs['id']
        
    # 2. Check for Internal Wrapper (e.g. <p class="CAP"> inside figcaption)
    # If the English node has a single child that is a structural tag, we should clone it.
    inner_wrapper = None
    
    # Simple check: direct children
    # We ignore nav strings
    children = [c for c in en_node.children if c.name]
    if len(children) == 1 and children[0].name in ['p', 'div', 'span']:
        # Clone the wrapper
        inner_wrapper = soup.new_tag(children[0].name)
        inner_wrapper.attrs = children[0].attrs.copy()
        if 'id' in inner_wrapper.attrs: del inner_wrapper.attrs['id']
        new_tag.append(inner_wrapper)
    
    # 3. Add Span for Styling
    # User Request: "add a span to put grey color in text"
    # Check config for classes if needed
    span_class = "es-translation"
    
    span = soup.new_tag("span")
    span['class'] = span_class
    span['style'] = "color: grey !important;" # Explicit as requested
    
    # Parse es_text as HTML to preserve tags like <b>, <i>, etc.
    # We use the same parser as the main soup
    inner_content = BeautifulSoup(es_text, 'html.parser')
    # Append content directly (BeautifulSoup will handle the move)
    if inner_content:
        span.append(inner_content)
    else:
        span.string = es_text
    
    if inner_wrapper:
        inner_wrapper.append(span)
    else:
        new_tag.append(span)
    
    # 2.5 Style Overrides for Spacing
    # Prevent double margins (En bottom + Es top) causing huge gaps.
    # Strategy: 
    # - Remove bottom margin from English node
    # - Add small top margin to Spanish node
    # - Spanish node keeps original bottom margin (spacing to next pair)
    
    # Update English Node styles
    en_style = en_node.get('style', '')
    if en_style: en_style += ";"
    en_node['style'] = en_style + " margin-bottom: 0 !important;"
    
    # Update Spanish Node styles
    new_tag_style = new_tag.get('style', '')
    if new_tag_style: new_tag_style += ";"
    new_tag['style'] = new_tag_style + " margin-top: 0 !important;"

    # 3. Insert after original
    en_node.insert_after(new_tag)
    
    # 4. Append Extracted Images (if any)
    if extracted_images:
        # We wrap them in a similar container to preserve layout (e.g. centering)
        # But we strip text-specific styles potentially?
        # Safe bet: Clone the wrapper again.
        img_container = soup.new_tag(en_node.name)
        img_container.attrs = en_node.attrs.copy()
        
        # Remove ID
        if 'id' in img_container.attrs: del img_container.attrs['id']
        
        # Reset margins for image container?
        # It should probably have top margin (spacing from ES) and original bottom margin.
        img_style = img_container.get('style', '')
        if img_style: img_style += ";"
        img_container['style'] = img_style + " margin-top: 1em !important;"
        
        for img in extracted_images:
            img_container.append(img)
            
        # Insert AFTER the Spanish node
        new_tag.insert_after(img_container)
    
    return new_tag


def perform_injection(aligned_pairs, config, soup):
    from collections import defaultdict
    
    print(f"DEBUG: perform_injection called with {len(aligned_pairs)} pairs")
    
    def get_node_id(p): return id(p.get('node'))
    
    # CRITICAL FIX: Pre-group ALL pairs by node_id instead of using groupby.
    # groupby only groups CONSECUTIVE items, but split chunks can become
    # non-consecutive after alignment, causing later pairs to overwrite earlier ones.
    node_groups = defaultdict(list)
    seen_order = []  # Preserve first-occurrence order for stable processing
    for p in aligned_pairs:
        nid = get_node_id(p)
        if nid not in node_groups:
            seen_order.append(nid)
        node_groups[nid].append(p)
    
    for node_id in seen_order:
        group = node_groups[node_id]
        if not group: continue
        
        original_node = group[0].get('node')
        if not original_node: continue
        
        # Optimization: Single pair (Normal case)
        if len(group) == 1:
            p = group[0]
            # Skip injection for chunks marked to skip alignment (e.g. standalone numeric headers)
            if p.get('skip_alignment'):
                continue
            # Pass English text to update if needed (merged headers)
            inject_translation(original_node, p['es'], config, soup, en_text=p['en'])
            continue
            
        # Split Case: Multiple pairs for same source node
        # We need to turn 1 Node into N Nodes (alternating En/Es)
        
        # Skip if marked to skip alignment
        if any(p.get('skip_alignment') for p in group):
            continue
        
        last_node = original_node
        
        for i, p in enumerate(group):
            en_text = p['en']
            es_text = p['es']
            
            if i == 0:
                # Reuse the original node for the first chunk
                # Explicitly set text too
                original_node.string = en_text
                es_node = inject_translation(original_node, es_text, config, soup)
                
                # If this is a split group, and there is a next part:
                if len(group) > 1 and es_node:
                    # Reduce bottom margin of this Spanish block to show it continues
                    s = es_node.get('style', '')
                    es_node['style'] = s + "; margin-bottom: 0 !important;"

                last_node = original_node.find_next_sibling()
                # Fallback if no sibling was added (e.g., empty es_text)
                if last_node is None:
                    last_node = original_node
            else:
                # Create NEW English node clone
                import copy
                new_en_node = copy.copy(original_node)
                new_en_node.string = en_text
                if new_en_node.has_attr('id'): del new_en_node['id']
                
                # Split Continuation Style: 
                # Remove Top Margin from English part to pull it up to previous Span
                s = new_en_node.get('style', '')
                new_en_node['style'] = s + "; margin-top: 0 !important;"
                
                # Safety: If last_node is None, fall back to original_node
                if last_node is None:
                    last_node = original_node
                    
                last_node.insert_after(new_en_node)
                # Pass None for en_text since we just set it
                es_node = inject_translation(new_en_node, es_text, config, soup)
                
                # If not the last part, tight bottom margin too
                if i < len(group) - 1 and es_node:
                     s = es_node.get('style', '')
                     es_node['style'] = s + "; margin-bottom: 0 !important;"

                next_sib = new_en_node.find_next_sibling()
                last_node = next_sib if next_sib else new_en_node

def align_chunks(en_chunks, es_chunks):
    aligned = []

    
    en_headers = get_header_indices(en_chunks)
    es_headers = get_header_indices(es_chunks)
    
    # Fix for structure mismatch: If header counts differ, fall back to flat alignment
    # This handles cases where one language uses <h1> and the other uses <p class="title">
    if len(en_headers) != len(es_headers):

        en_headers = []
        es_headers = []
    
    # We assume headers map 1-to-1. If not, this heuristic fails, but it's better than nothing.
    
    def fingerprint(c, lang='en', shared_anchors=None, shared_nums=None):
        """Generates a fingerprint for alignment matching."""
        txt = c['text']
        
        # Anchors: Numbers (Only if Shared)
        # We previously used all numbers, but "2010s" vs "DECADA" causes mismatches.
        nums = re.findall(r'\d+', txt)
        if shared_nums is not None:
             nums = [n for n in nums if n in shared_nums]
        
        anchors_list = sorted(list(set(nums)))
        
        # Anchors: Capitalized Tokens (Only if Shared in current scope)
        if shared_anchors is not None:
             tokens = re.findall(r'\b[A-Z][a-z]{3,}\b', txt)
             allowed_tokens = [t for t in tokens if t in shared_anchors]
             anchors_list.extend(allowed_tokens)
             anchors_list = sorted(list(set(anchors_list))) # Re-sort with tokens       
        
        # Dialogue Anchor: Check for start chars
        is_dialog = False
        s = txt.strip()
        if s:
             if s.startswith('“') or s.startswith('"'): is_dialog = True
             elif s.startswith('—') or s.startswith('-') or s.startswith('–'): is_dialog = True
        
        anchor_sig = ""
        if anchors_list: anchor_sig = "ANCHOR:" + "|".join(anchors_list)
        
        # Image Handling
        if c.get('type') == 'image':
             # Use basename of src as unique identifier
             src = c.get('src', '')
             fname = os.path.basename(src)
             return f"IMG:{fname}"
        
        # Structural signal
        dialog_sig = "DIALOG" if is_dialog else "NARRATION"
        
        # Granularity signal: Sentence Count
        # This prevents aligning a single sentence paragraph with a 5-sentence paragraph
        # pushing them into a 'replace' block for finer alignment.
        sent_count = len(split_sentences(txt))
        # Bucketing to allow some flexibility
        if sent_count <= 1: sc_sig = "SC1"
        elif sent_count <= 3: sc_sig = "SC2-3"
        else: sc_sig = "SC4+"
        
        fp = f"{c['type']}:{dialog_sig}:{anchor_sig}:{sc_sig}"
        return fp





    def align_section(en_sec, es_sec, depth=0):
        # Filter out chunks marked to skip alignment (e.g. standalone numeric headers)
        en_sec = [c for c in en_sec if not c.get('skip_alignment')]
        
        if not en_sec and not es_sec: return []
        
        if depth > 1:
             local_res = []
             max_len = max(len(en_sec), len(es_sec))
             for k in range(max_len):
                    itm_en = en_sec[k] if k < len(en_sec) else None
                    itm_es = es_sec[k] if k < len(es_sec) else None
                    t_en = itm_en['text'] if itm_en else ""
                    t_es = itm_es['text'] if itm_es else ""
                    use_tag = itm_en['tag'] if itm_en else 'p'
                    use_classes = itm_en.get('classes', []) if itm_en else []
                    use_raw = itm_en.get('raw_html') if itm_en else None
                    
                    local_res.append({
                        'tag': use_tag, 
                        'classes': use_classes, 
                        'en': t_en, 
                        'es': t_es,
                        'raw_html': use_raw,
                        'es_raw_html': itm_es.get('raw_html') if itm_es else None,
                        'node': itm_en['node'] if itm_en else None
                    })
             return local_res

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
        
        fp_en = [fingerprint(c, 'en', shared, shared_nums) for c in en_sec]
        fp_es = [fingerprint(c, 'es', shared, shared_nums) for c in es_sec]
        
        # Use SequenceMatcher to find the optimal global alignment based on type+length profile
        # autojunk=False is CRITICAL for preventing anchors from being discarded if they appear commonly (which they might in repetitive text)
        sm = difflib.SequenceMatcher(None, fp_en, fp_es, autojunk=False)
        local_res = []
        
        if not sm.get_opcodes(): return []
        
        # DEBUG LOGGING
        import logging
        debug_log = logging.getLogger('align_debug')
        if not debug_log.handlers:
            fh = logging.FileHandler('/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/debug_align.log')
            fh.setLevel(logging.DEBUG)
            debug_log.addHandler(fh)
            debug_log.setLevel(logging.DEBUG)
        
        debug_log.debug(f"=== align_section called depth={depth} ===")
        debug_log.debug(f"EN chunks: {len(en_sec)}, ES chunks: {len(es_sec)}")
        for idx, c in enumerate(en_sec[:5]):
            debug_log.debug(f"  EN[{idx}]: {c['text'][:50]}...")
        for idx, c in enumerate(es_sec[:5]):
            debug_log.debug(f"  ES[{idx}]: {c['text'][:50]}...")
        
        # Post-process opcodes to handle N:M mismatches (e.g. 1 long ES para vs 2 short EN paras)
        raw_opcodes = sm.get_opcodes()
        debug_log.debug(f"Raw opcodes: {raw_opcodes}")
        opcodes = []
        
        # We process manually to allow merging multiple blocks
        i = 0
        while i < len(raw_opcodes):
            tag, i1, i2, j1, j2 = raw_opcodes[i]
            
            merged = False
            
            # 1. Forward Merge: EQUAL + DELETE
            # Check if this EQUAL block should absorb the NEXT DELETE block
            if tag == 'equal' and i + 1 < len(raw_opcodes):
                n_tag, n_i1, n_i2, n_j1, n_j2 = raw_opcodes[i+1]
                if n_tag == 'delete':
                     en_len = sum(len(c['text']) for c in en_sec[i1:i2])
                     es_len = sum(len(c['text']) for c in es_sec[j1:j2])
                     del_en_len = sum(len(c['text']) for c in en_sec[n_i1:n_i2])
                     debug_log.debug(f"FWD check: ES={es_len} vs EN={en_len}+DEL={del_en_len}")
                     
                     if es_len > en_len * 1.2 and es_len > (en_len + del_en_len) * 0.8:
                         debug_log.debug("  -> FWD MERGE!")
                         opcodes.append(('replace', i1, n_i2, j1, j2))
                         i += 2 # Skip next
                         continue

            # 2. Backward Merge: DELETE + EQUAL
            # Check if this DELETE block should be absorbed by the NEXT EQUAL block
            if tag == 'delete' and i + 1 < len(raw_opcodes):
                n_tag, n_i1, n_i2, n_j1, n_j2 = raw_opcodes[i+1]
                if n_tag == 'equal':
                     en_len = sum(len(c['text']) for c in en_sec[n_i1:n_i2]) # Next EN (Equal)
                     es_len = sum(len(c['text']) for c in es_sec[n_j1:n_j2]) # Next ES (Equal)
                     del_en_len = sum(len(c['text']) for c in en_sec[i1:i2]) # Current EN (Deleted)
                     debug_log.debug(f"BWD check: ES={es_len} vs EN={en_len}+DEL={del_en_len}")
                     
                     if es_len > en_len * 1.2 and es_len > (en_len + del_en_len) * 0.8:
                         debug_log.debug("  -> BWD MERGE!")
                         opcodes.append(('replace', i1, n_i2, n_j1, n_j2))
                         i += 2 # Skip next
                         continue

                # 3. Delete + Insert => Replace
                # If we delete EN and immediately insert ES, treat as REPLACE to try sentence alignment
                if n_tag == 'insert':
                     en_len = sum(len(c['text']) for c in en_sec[i1:i2])
                     es_len = sum(len(c['text']) for c in es_sec[n_j1:n_j2])
                     debug_log.debug(f"DEL+INS check: EN={en_len}, ES={es_len}")
                     
                     # Loose heuristic: match if lengths are broadly compatible
                     if es_len > 0 and en_len > 0:
                         ratio = es_len / en_len
                         debug_log.debug(f"  ratio={ratio}")
                         if 0.5 < ratio < 2.0:
                             debug_log.debug("  -> DEL+INS MERGE!")
                             opcodes.append(('replace', i1, i2, n_j1, n_j2))
                             i += 2
                             continue
            
            opcodes.append(raw_opcodes[i])
            i += 1

        debug_log.debug(f"Final opcodes: {opcodes}")


        for tag, i1, i2, j1, j2 in opcodes:
            if tag == 'equal':
                for k in range(i2 - i1):
                    en_item = en_sec[i1+k]
                    es_item = es_sec[j1+k]
                    en_text = en_item['text']
                    es_text = es_item['text']
                    
                    item_data = en_item.copy()
                    item_data.update({
                        'en': en_text,
                        'es': es_text,
                        'raw_html': en_item.get('raw_html'), # Preserve raw
                        'es_raw_html': es_item.get('raw_html'), # Preserve ES raw
                        'node': en_item['node']
                    })
                    # Remove 'text' key to avoid confusion? Or keep it?
                    # Keep everything else (src, alt, etc)
                    local_res.append(item_data)
            elif tag == 'replace':
                # Block mismatch. Drill down by splitting text into sentences.
                sub_en = en_sec[i1:i2]
                sub_es = es_sec[j1:j2]
                
                # Expand paragraphs into sentence chunks
                v_en_chunks = []
                for c in sub_en:
                    if c['type'] == 'std' and c['text']:
                        sents = split_sentences(c['text'])
                        if len(sents) <= 1:
                             # Preserve raw/dict if no split
                             v_en_chunks.append(c)
                        else:
                            for s in sents: v_en_chunks.append({'tag': c['tag'], 'type': 'std', 'text': s, 'classes': c.get('classes', []), 'raw_html': None, 'node': c['node']})
                    else:
                        v_en_chunks.append(c)

                v_es_chunks = []
                for c in sub_es:
                    if c['type'] == 'std' and c['text']:
                        sents = split_sentences(c['text'])
                        for s in sents: v_es_chunks.append({'tag': c.get('tag','p'), 'type': 'std', 'text': s, 'classes': c.get('classes', [])})
                    else:
                        v_es_chunks.append(c)
                
                # RECOVERY: If granularity mismatch (One side has significantly more sentences), try aggressive splitting on the OTHER side.
                if len(v_en_chunks) > len(v_es_chunks): 
                     v_es_chunks_agg = []
                     for c in sub_es:
                        if c['type'] == 'std' and c['text']:
                            sents = split_sentences_aggressive(c['text'])
                            for s in sents: v_es_chunks_agg.append({'tag': c.get('tag','p'), 'type': 'std', 'text': s, 'classes': c.get('classes', [])})
                        else:
                            v_es_chunks_agg.append(c)
                     
                     # Only use aggressive if it actually created more chunks
                     if len(v_es_chunks_agg) > len(v_es_chunks):
                        v_es_chunks = v_es_chunks_agg
                
                # Recursive align with increased depth
                sub_aligned = align_section(v_en_chunks, v_es_chunks, depth + 1)
                local_res.extend(sub_aligned)

            elif tag == 'delete':
                # EN Content, No ES
                for k in range(i1, i2):
                    item_data = en_sec[k].copy()
                    item_data.update({
                        'en': en_sec[k]['text'],
                        'es': "",
                        'node': en_sec[k]['node']
                    })
                    local_res.append(item_data)
            elif tag == 'insert':
                # ES Content, No EN
                    for k in range(j1, j2):
                        item_data = es_sec[k].copy()
                        item_data.update({
                            'en': "", 
                            'es': es_sec[k]['text'],
                            'raw_html': None,
                            'es_raw_html': es_sec[k].get('raw_html'),
                            'node': None # Explicitly set None to avoid KeyError
                        })
                        local_res.append(item_data)
                    
        return local_res    # Add implicit start (0) and end (len) sentinels
    en_anchors = [-1] + en_headers + [len(en_chunks)]
    es_anchors = [-1] + es_headers + [len(es_chunks)]
    
    # Process each section between headers
    # Process each section between headers
    limit = min(len(en_anchors), len(es_anchors))
    
    final_aligned = []
    for i in range(limit - 1):
        en_start = en_anchors[i] + 1
        en_end = en_anchors[i+1]
        es_start = es_anchors[i] + 1
        es_end = es_anchors[i+1]
        
        en_section = en_chunks[en_start:en_end]
        es_section = es_chunks[es_start:es_end]
        
        section_aligned = align_section(en_section, es_section)
        final_aligned.extend(section_aligned)
        
        # Explicitly align the headers themselves if they are not sentinels
        idx_en_h = en_anchors[i+1]
        idx_es_h = es_anchors[i+1]
        
        is_en_real = idx_en_h < len(en_chunks)
        is_es_real = idx_es_h < len(es_chunks)
        
        if is_en_real and is_es_real:
             # Matched Header Pair
             h_en = en_chunks[idx_en_h]
             h_es = es_chunks[idx_es_h]
             final_aligned.append({
                 'tag': h_en['tag'],
                 'classes': h_en.get('classes', []),
                 'en': h_en['text'],
                 'es': h_es['text'],
                 'type': 'header',
                 'node': h_en['node']
             })
             
    # Handle any remaining chunks after the last header
    # If len > limit, it means we have Headers remaining (orphans) or content after the last matched/sentinel anchor.
    # The last processed anchor was at index `limit-1`. 
    # If that anchor was a real header (and not a sentinel), it was paired with a Sentinel in the loop check (and skipped).
    # So we must include it now.
    
    if len(en_anchors) > limit:
        # Start from the anchor itself if it's real
        last_anchor_idx = en_anchors[limit-1]
        start_idx = last_anchor_idx if last_anchor_idx != -1 else 0
        
        # NOTE: If we start at last_anchor_idx, we include the header.
        # But wait, if `limit-1` was 0 (start), last_anchor was -1. Start=0. Correct.
        # If `limit-1` was 1, last_anchor was H1_index. Start=H1_index. Correct (include H1).
        
        en_section = en_chunks[start_idx : en_anchors[limit]]
        section_aligned = align_section(en_section, [])
        final_aligned.extend(section_aligned)
        
    if len(es_anchors) > limit:
        last_anchor_idx = es_anchors[limit-1]
        start_idx = last_anchor_idx if last_anchor_idx != -1 else 0
        
        es_section = es_chunks[start_idx : es_anchors[limit]]
        section_aligned = align_section([], es_section)
        final_aligned.extend(section_aligned)
        
    # Post-Process: Fix Merged Spanish Captions
    # Scenario: En Caption is orphan (Delete). Es Chunk has Caption + Body (merged).
    # Since Es Chunk matches En Body, it aligns with En Body.
    # Result: En Caption (empty ES). En Body (Es Caption + Es Body).
    
    final_aligned = fix_split_headers(final_aligned)
    final_aligned = fix_merged_captions(final_aligned)
        
    return final_aligned

def fix_split_headers(aligned_items):
    """
    Detects cases where English headers are split (e.g. Number, then Title) 
    but Spanish header is single (Number + Title).
    Splits the Spanish text to align with both English parts.
    """
    import re
    # Safely iterate with modification? We are modifying in place, but not adding/removing items from list.
    for i in range(len(aligned_items) - 1):
        item_a = aligned_items[i]
        item_b = aligned_items[i+1]
        
        # Check pattern: 
        # A: Header with ES content (likely merged match)
        # B: Header (EN only) with NO ES content (orphan)
        # Verify A is not empty EN
        if item_a.get('type') == 'header' and item_a.get('es') and item_a.get('en') and \
           item_b.get('type') == 'header' and not item_b.get('es') and item_b.get('en'):
               
            en_a = item_a.get('en', '').strip()
            es_text = item_a.get('es', '').strip()
            
            # Heuristic: Exact Number Match at Start
            # Only if En_a is short (likely a number or prefix)
            if len(en_a) < 10 or en_a.lower().startswith('chapter') or en_a.lower().startswith('part'):
                try:
                    pattern = r'^(' + re.escape(en_a) + r')([\.\:\s]+)(.*)$'
                    match = re.search(pattern, es_text, re.IGNORECASE)
                    
                    if match:
                         part1 = match.group(1) # "5"
                         # part2 is remainder
                         part2 = match.group(3).strip() 
                         
                         if part2:
                             # Assign
                             item_a['es'] = part1 
                             item_b['es'] = part2
                             print(f"Fixed Split Header: '{es_text}' -> '{part1}' | '{part2}'")
                except Exception:
                    pass
                 
    return aligned_items

def fix_merged_captions(aligned_items):
    """
    Detects and fixes cases where a Spanish caption is merged with the following paragraph,
    causing it to look like the English Body text's translation.
    """
    unmatched_captions = []
    
    for idx, item in enumerate(aligned_items):
        en_val = item.get('en', '')
        es_val = item.get('es', '')
        
        # if "30" in es_val:
        #     print(f"DEBUG: GLOBAL TRACE 30 at {idx}: ENtype={item.get('type')} EN='{en_val[:15]}...' ES='{es_val[:30]}...'")
        
        # 1. Identify Orphan English Caption
        if en_val and not es_val:
             txt = en_val.strip()
             is_caption = item.get('type') == 'caption' or re.match(r'^FIGURE\s+\d+|Figure\s+\d+', txt, re.IGNORECASE)
             if is_caption:
                 # print(f"DEBUG: Found Orphan EN Caption at {idx}: '{txt[:30]}...'")
                 unmatched_captions.append((idx, item))
                 
        # 2. Identify Suspicious Merged Spanish Chunk
        elif en_val and es_val:
             es_txt = es_val.strip()
             
             # if "Figura" in es_txt:
             #     print(f"DEBUG: TRACE FIGURA at {idx}: ENtype={item.get('type')} EN='{en_val[:15]}...' ES='{es_txt[:30]}...'")

             if re.match(r'^Figura\s+\d+', es_txt, re.IGNORECASE):
                 # print(f"DEBUG: Found Potential Merged ES Caption at {idx}: '{es_txt[:30]}...'")
                 
                 if unmatched_captions:
                     cand_idx, cand_item = unmatched_captions[-1]
                     # Only consider if candidate is reasonably close (e.g. within last 10 items? Or just last one?)
                     # If it's too far, maybe irrelevant.
                     # But for now, just take last.
                     
                     en_body = en_val
                     es_full = es_val
                     
                     
                     s = difflib.SequenceMatcher(None, en_body, es_full, autojunk=False)
                     match_block = s.find_longest_match(0, len(en_body), 0, len(es_full))
                     
                     # print(f"DEBUG: Match Analysis at {idx}: EN('{en_body[:20]}') ES('{es_full[:20]}') -> MatchStart={match_block.b} Len={match_block.size}")
                     
                     if match_block.b > 0:
                         prefix = es_full[:match_block.b].strip()
                         if re.match(r'^Figura\s+\d+', prefix, re.IGNORECASE):
                             # print(f"Refining Alignment: Extracted Spanish Caption '{prefix[:30]}...' from merged paragraph.")
                             
                             cand_item['es'] = prefix
                             cand_item['classes'] =  item.get('classes', []) + ['es-trans']
                             
                             remainder = es_full[match_block.b:].strip()
                             item['es'] = remainder
                             
                             unmatched_captions.pop()
                     else:
                         pass
                         
        # 3. Identify Orphan Spanish Caption (Displaced)
        elif not en_val and es_val:
             es_txt = es_val.strip()
             if re.match(r'^Figura\s+\d+', es_txt, re.IGNORECASE):
                 # print(f"DEBUG: Found Orphan ES Caption at {idx}: '{es_txt[:30]}...'")
                 
                 if unmatched_captions:
                     # Check the list of candidates for a match
                     # We might need to search backwards or check all?
                     # Simple heuristic: Check the LAST one first.
                     
                     cand_idx, cand_item = unmatched_captions[-1]
                     en_txt = cand_item['en'].strip()
                     
                     # Extract numbers
                     en_nums = re.findall(r'\d+', en_txt)
                     es_nums = re.findall(r'\d+', es_txt)
                     
                     if en_nums and es_nums and en_nums[0] == es_nums[0]:
                         # print(f"Refining Alignment: Paired Displaced Spanish Caption '{es_txt[:30]}...' with English Caption '{en_txt[:30]}...'")
                         
                         cand_item['es'] = es_txt
                         cand_item['classes'] = cand_item.get('classes', []) + item.get('classes', []) + ['es-trans']
                         
                         # Clear the current orphan ES item
                         item['es'] = ""
                         item['en'] = "" # Should be empty already
                         
                         unmatched_captions.pop()
                     # else:
                        # print(f"DEBUG: Mismatch or No Num: EN={en_nums} ES={es_nums}")
                             
    return aligned_items
    # -------------------------------------------------------------------------
    # Post-processing 1: Merge short English attribution lines into previous
    # This handles cases like:
    # EN: "Hello," she said.
    # ES: "Hola," dijo.
    #
    # EN: "How are you?"
    # ES: "¿Cómo estás?"
    #
    # EN: she asked.
    # ES:
    #
    # We want to merge "she asked." into the previous English chunk.
    # -------------------------------------------------------------------------
    
    # We need a new list to build the result
    pass_1_aligned = []
    for item in final_aligned:
        if not pass_1_aligned:
            pass_1_aligned.append(item)
            continue
            
        prev = pass_1_aligned[-1]
        
        # Candidate for merge:
        # 1. Current has EN but no ES
        # 2. Previous has EN and ES (or just EN, but usually we want to attach to a dialogue pair)
        # 3. Current EN is short and looks like attribution
        
        do_merge = False
        en_text = item['en'].strip()
        es_text = item['es'].strip()
        
        if en_text and not es_text and len(en_text) < 50:
             # Attribution keywords
             lower_en = en_text.lower()
             attr_starts = ["i ", "he ", "she ", "they ", "we ", "rig "] # "Rig" specific to Skyward
             attr_words = ["asked", "said", "replied", "answered", "whispered", "shouted", "muttered"]
             
             is_attribution = False
             if any(lower_en.startswith(s) for s in attr_starts): is_attribution = True
             if any(w in lower_en for w in attr_words): is_attribution = True
             
             # Check previous ending
             prev_en = prev['en'].strip()
             prev_ends_quote = prev_en.endswith('”') or prev_en.endswith('"') or prev_en.endswith('?') or prev_en.endswith('!')
             
             if is_attribution and prev_ends_quote:
                 do_merge = True
        
        if do_merge:
            # Merge
            prev['en'] += " " + item['en']
            # Merge raw_html if present
            if prev.get('raw_html') is not None:
                to_append = item.get('raw_html') or item['en']
                prev['raw_html'] += " " + to_append
                
            # Update pass_1_aligned[-1] in place
        else:
            pass_1_aligned.append(item)

    final_aligned = pass_1_aligned
    
    # -------------------------------------------------------------------------
    # Post-processing 2: Merge Split Spanish Paragraphs (1-to-N)
    # Detects when one English par corresponds to ES[i] + ES[i+1].
    # Heuristic:
    #   Current alignment seems wrong or ES[i+1] is a "delete" (orphaned Spanish? No, here it's aligned to next English).
    #   We actually typically see:
    #     EN[i] <-> ES[i] (partial match)
    #     EN[i+1] <-> ES[i+1] (MISMATCH, ES[i+1] actually belongs to EN[i])
    # -------------------------------------------------------------------------
    
    # We need a new pass on 'final_aligned'.
    # Because we modify the list structure (merge two items' Spanish, delete one item),
    # we can't easily use a simple loop.
    
    pass_2_aligned = []
    i = 0
    from difflib import SequenceMatcher
    
    # print("DEBUG Phase 1 Dump:")
    # for idx, x in enumerate(final_aligned):
    #      print(f"  {idx}: EN='{x['en'][:20]}...' ES='{x['es'][:20]}...'")
    
    while i < len(final_aligned):
        curr = final_aligned[i]
        orphans_to_append = []
        
        # Inner loop: keep merging next item if it qualifies
        while i + 1 < len(final_aligned):
            nxt = final_aligned[i+1]
            
            # Extract texts
            if nxt.get('tag') == 'img' or nxt.get('type') == 'image':
                 break
            
            en1 = curr['en'].strip()
            es1 = curr['es'].strip()
            es2 = nxt['es'].strip()
            
            # Conditions:
            # 1. Next has NO English (pure orphan) - Essential for N-to-1 merge
            # REVISION: We MUST allow merging even if Next has English, if the Spanish chunks belong together.
            # This creates an Orphaned EN at i+1, which Phase 3 will fix.
            # if nxt['en'].strip():
            #    break # Stop merging
                
            # if nxt['en'].strip():
            #    break # Stop merging
                
            if not en1 or (not es1 and not es2):
                 # If EN is empty, we can't judge ratio.
                 # If BOTH ES are empty, nothing to merge.
                 # But if ES1 is empty and ES2 is not, we MIGHT merge (Pull Up).
                 if not en1: break
                 if not es1 and not es2: break
                 # Continue
                
            len_en = len(en1)
            len_es1 = len(es1)
            len_es2 = len(es2)
            len_combined = len_es1 + len_es2
            combined_es = es1 + " " + es2 
            
            ratio_curr = len_es1 / len_en if len_en > 0 else 0
            ratio_combined = len_combined / len_en if len_en > 0 else 0
            
            should_merge = False
            
            # SAFETY CHECK: If next item has English, be very conservative about merging.
            # Only merge if current is VERY short (implying it's just a fragment).
            # Standard Spanish/English expansion is ~1.2.
            # 0.8 is short but plausible. 0.5 is definitely a fragment.
            
            has_next_en = bool(nxt['en'].strip())
            thresh_curr = 0.6 if has_next_en else 1.05
            
            if ratio_curr < thresh_curr and ratio_combined <= 1.8:
                 should_merge = True
                 
            if should_merge:
                curr['es'] = combined_es
                
                # Check if we are consuming an English chunk (making it a true orphan)
                if nxt['en'].strip():
                     # We must preserve this English chunk as an orphan!
                     # We can't insert it into 'final_aligned' because we are iterating it.
                     # We should add it to a temporary buffer to append AFTER the current merged item?
                     # But we might merge multiple items.
                     # Let's attach it to 'curr' as 'orphans_created' list? No, structure change.
                     # Better: Add it to 'pass_2_aligned' immediately? 
                     # No, 'curr' is still being built.
                     
                     # Solution: We need a side-list of orphans for THIS 'curr'.
                     # But wait, if we merge ES[i+1] into ES[i], EN[i+1] becomes standalone with ES="".
                     # We should append {en: EN[i+1], es: ""} to the Output List, 
                     # BUT it must come AFTER 'curr'.
                     # Since 'curr' is not yet appended (looping), we can keep a list of orphans to append after curr.
                     orphans_to_append.append({
                         'tag': nxt['tag'], 
                         'classes': nxt.get('classes', []), 
                         'type': nxt.get('type', 'p'),
                         'en': nxt['en'], 
                         'es': '',
                         'text': nxt.get('text', ''),
                         'raw_html': nxt.get('raw_html')
                     })
                
                # Consume i+1
                i += 1
            else:
                break
        
        pass_2_aligned.append(curr)
        if orphans_to_append:
             pass_2_aligned.extend(orphans_to_append)
             
        i += 1
        
    # Filter out completely empty items to prevent gaps from blocking Phase 3


        
    # Filter out completely empty items to prevent gaps from blocking Phase 3
    pass_2_aligned = [x for x in pass_2_aligned if x['en'].strip() or x['es'].strip() or x.get('type') == 'image' or x.get('tag') == 'img']
        
    # Phase 3: Fix the gaps created by Phase 2 (The Ripple Effect)

    # Now we might have:
    # [i]   {en: EN1, es: ES1+ES2}
    # [i+1] {en: EN2, es: ""}   <-- Orphaned EN
    # [i+2] {en: EN3, es: ES3}  <-- Mismatch? If the original error was a shift, then ES3 likely belongs to EN2.
    
    # We need a "Gap Closer" pass.
    # Logic:
    # If Item K has {en: EN_K, es: ""} 
    # And Item K+1 has {en: EN_K+1, es: ES_K+1}
    # Check if ES_K+1 belongs to EN_K.
    
    # Filter out completely empty items to prevent gaps from blocking Phase 3
    pass_2_aligned = [x for x in pass_2_aligned if x['en'].strip() or x['es'].strip() or x.get('type') == 'image' or x.get('tag') == 'img']
    
    final_pass = []



    skip_next = False
    for i in range(len(pass_2_aligned)):
        if skip_next:
            skip_next = False
            continue
            
        curr = pass_2_aligned[i]
        
        if i + 1 < len(pass_2_aligned):


            nxt = pass_2_aligned[i+1]
            
            # Gap detection (Pull Up)
            if curr['en'] and not curr['es'] and nxt['es']:
                # Potential Pull-Up
                en = curr['en']
                es = nxt['es']
                
                # Verify match
                sim = SequenceMatcher(None, en, es).ratio()
                
                if sim > 0.35: # INCREASED THRESHOLD (was 0.1)
                    # Pull Up!
                    curr['es'] = es
                    nxt['es'] = "" # Steal it
                    
                    # We continue, effectively moving the empty bubble down
                    # The next iteration will see 'nxt' is now empty, and try to steal from i+2
                    if curr['en'].strip() or curr['es'].strip():
                        final_pass.append(curr)
                    continue


            
            # Gap detection (Pull Down)
            # Case: {en: "", es: ES} followed by {en: EN, es: ""}
            # This happens when difflib emits Insert then Delete
            if not curr['en'] and curr['es'] and nxt['en'] and not nxt['es']:
                 en = nxt['en']
                 es = curr['es']
                 
                 sim = SequenceMatcher(None, en, es).ratio()
                 print(f"DEBUG Phase 3 Pull Down: '{en[:20]}' vs '{es[:20]}' Sim={sim:.3f}")
                 
                 if sim > 0.1:

                     # Pull Down (Push ES to next)
                     nxt['es'] = es
                     curr['es'] = ""
                     
                     # We append curr (now empty)
                     if curr['en'].strip() or curr['es'].strip() or curr.get('tag') == 'img':
                        final_pass.append(curr)
                     # Loop continues to process nxt (now full) in next iteration
                     continue

                     continue
            
            # Orphan Prepend (Issue 7 Fix)
            # Case: {en: "", es: Orphan} followed by {en: EN, es: Match}
            # Happens when difflib anchors to the END of a paragraph.
            if not curr['en'] and curr['es'] and nxt['en'] and nxt['es']:
                 en = nxt['en']
                 es_current = nxt['es']
                 es_orphan = curr['es']
                 
                 sim_curr = SequenceMatcher(None, en, es_current).ratio()
                 sim_with_orphan = SequenceMatcher(None, en, es_orphan + " " + es_current).ratio()
                 
                 # Logic: Does prepending the orphan IMPROVE the match?
                 # Or at least make it "Complete"?
                 # Since Phase 1 matched EN to ES_current, sim_curr is likely decent.
                 # But if sim_with_orphan is ALSO good (or better), and Length Ratio suggests we need more Spanish...
                 
                 len_en = len(en)
                 len_es_curr = len(es_current)
                 len_es_combined = len(es_orphan) + len_es_curr
                 
                 ratio_curr = len_es_curr / len_en

                 ratio_combined = len_es_combined / len_en
                 
                 # If current is short (< 1.0) and combined is better (<= 1.8)
                 # AND sim doesn't tank.
                 
                 if ratio_curr < 1.05 and ratio_combined <= 1.8:
                      if sim_with_orphan >= sim_curr - 0.1: # Allow slight drop if length is much better
                           # Prepend!
                           nxt['es'] = es_orphan + " " + es_current
                           curr['es'] = ""
                           
                           if curr['en'].strip() or curr['es'].strip() or curr.get('tag') == 'img':
                               final_pass.append(curr)
                           continue

        if curr['en'].strip() or curr['es'].strip() or curr.get('tag') == 'img':
            final_pass.append(curr)

    # Phase 3b: Zipper Merge (Fix Fragmentation)
    # Merges adjacent [En, ""] and ["", Es] items.
    zipped_pass = []
    i = 0
    while i < len(final_pass):
        curr = final_pass[i]
        if i + 1 < len(final_pass):
             nxt = final_pass[i+1]
             if curr['en'].strip() and not curr['es'].strip() and \
                not nxt['en'].strip() and nxt['es'].strip():
                # Merge
                curr['es'] = nxt['es']
                i += 1 # Skip nxt
        zipped_pass.append(curr)
        i += 1
    
    final_pass = zipped_pass

    # Phase 3c: Orphan Prepend (Reverse Pass)
    # Recursively merge orphans into the *following* match if applicable.
    # Iterating backwards allows handling chains (Orphan1, Orphan2, Match).
    # Logic: Merge Orphan2 -> Match. Then Orphan1 -> Match(Modified).
    
    # We edit final_pass in place? List insertions are messy.
    # We can iterate backwards and modify. 
    # Since we only merge i into i+1, we can just clear i and update i+1.
    # Then filter empty items later.
    
    for i in range(len(final_pass) - 2, -1, -1):
        curr = final_pass[i]
        
        # Find next valid Match (look ahead)
        nxt = None
        for k in range(i + 1, len(final_pass)):
             if final_pass[k]['en'].strip():
                nxt = final_pass[k]
                break
        
        if not nxt:
             continue
        
        # Phase 3c: Reverse Orphan Prepend (Merged into loop)
        # Check if Current is Orphan (No EN, Yes ES)
        # And Next is Match (Yes EN, Yes ES)
        if not curr['en'].strip() and curr['es'].strip() and \
           nxt['en'].strip() and nxt['es'].strip():
             
             en = nxt['en']
             es_match = nxt['es']
             es_orphan = curr['es']
             
             # Similarity Check
             # Check if prepending orphan makes sense.
             sim_curr = SequenceMatcher(None, en, es_match).ratio()
             combined_es = es_orphan + " " + es_match
             sim_combined = SequenceMatcher(None, en, combined_es).ratio()
             
             len_en = len(en)
             len_es_curr = len(es_match)
             len_es_comb = len(combined_es)
             
             ratio_curr = len_es_curr / len_en if len_en > 0 else 0
             ratio_comb = len_es_comb / len_en if len_en > 0 else 0
             
             should_prepend = False
             
             # Standard Prepend Heuristic (Phase 3c)
             if ratio_comb <= 1.9:
                  if sim_combined >= sim_curr - 0.15: # Allow 15% drop
                       should_prepend = True
                  elif len_es_curr < len_en * 0.5: # If current match is TINY, we definitely need the orphan
                       should_prepend = True
             
             if should_prepend:
                  nxt['es'] = combined_es
                  curr['es'] = "" 
                  continue
             
             # Phase 3d: Orphan Swap (Issue 8 Fix)
             # If Prepend didn't trigger, check if the Orphan ITSELF is a better match than the Current Match.
             # This handles case where "Rodge" anchored to the WRONG "Rodge".
             
             sim_orphan = SequenceMatcher(None, en, es_orphan).ratio()
             ratio_orphan = len(es_orphan) / len_en if len_en > 0 else 0
             
             # Criteria for Swap:
             # 1. Orphan is decent match (sim > 0.2)

             # 2. Orphan is BETTER than Current Match (sim_orphan > sim_curr)?
             # 3. Or Length Ratio is SIGNIFICANTLY better.
             
             should_swap = False
             if sim_orphan > 0.2 and sim_orphan > sim_curr - 0.1:
                  # If Length Ratio of Match is BAD (> 2.0) and Orphan is GOOD (< 1.8)
                  if ratio_curr > 2.0 and ratio_orphan < 1.8 and ratio_orphan > 0.5:
                        should_swap = True
                  
                  # Special Case: "Rodge" vs "Rodge"
                  # If text is short (< 50 chars), sim is volatile.
                  if len_en < 50:
                       # If Orphan ratio is near 1.0 (e.g. 1.2) and Match is 2.8
                       if abs(ratio_orphan - 1.2) < abs(ratio_curr - 1.2) - 0.5:
                            should_swap = True
                            
                  # Similarity Win (Issue 8 Fix for Short Text)
                  # If Orphan is SIGNIFICANTLY better match (> 0.15 better), Swap regardless of Ratio (if Ratio is sane)
                  if sim_orphan > sim_curr + 0.15 and ratio_orphan < 2.5:
                       should_swap = True

             if should_swap:
                   # Swap!
                   # Current Orphan takes the English key.
                   curr['en'] = en
                   curr['raw_html'] = nxt.get('raw_html')
                   
                   # Next Item (Old Match) loses English key -> Becomes Orphan
                   nxt['en'] = ""
                   nxt['raw_html'] = None
                   
                   # Note: We don't move Spanish texts. We move the English KEY "up".
                   continue
        
    # Phase 3e: Linear Gap Fill (Massive 1-to-N)
    # If we have [Match A] ... [Orphans] ... [Match B]
    # And English for Match A is MISSING the dialogue corresponding to Orphans.
    # We must attach Orphans to A (Forward Fill) or B (Backward Fill).
    # Dialogue usually flows A -> A' -> A''. So attach to A.
    
    # We iterate Forward.
    last_match_idx = -1
    for i in range(len(final_pass)):
         curr = final_pass[i]
         if curr['en'].strip():
              last_match_idx = i
         elif curr['es'].strip():
              # Orphan.
              # If we have a preceding match, try to merge?
              if last_match_idx != -1:
                   # Only if ratio permits? Or Aggressive?
                   # Issue 8: Ratio is 13.0. We MUST merge regardless of ratio if we assume 1-to-N.
                   # But we need a boundary check.
                   # If we merge everything, we might eat the next paragraph's start?
                   # But Phase 1 anchored the Next Paragraph (Match B).
                   # So Orphans strictly strictly BETWEEN A and B should belong to A (or B).
                   
                   # We assume A.
                   anchor = final_pass[last_match_idx]
                   # Append
                   anchor['es'] += " " + curr['es']
                   curr['es'] = ""
                   # Continue

    # Filter empty
    final_pass = [x for x in final_pass if x['en'].strip() or x['es'].strip() or x.get('type') == 'image' or x.get('tag') == 'img']





    
    # Phase 3f: Orphan Steal (Issue 9 Shift Fix)
    # If Orphan[i] is followed by Fat[i+1], and Fat[i+1] starts with Orphan[i]'s text.
    # We steal the Head.
    
    for i in range(len(final_pass) - 1):
        curr = final_pass[i]
        nxt = final_pass[i+1]
        
        # Condition: Current is Orphan (or emptyish)
        # Next is Fat
        
        # Check if current is orphan-like OR Bad Match
        is_orphan = False
        if not curr['es'].strip() and curr['en'].strip():
             is_orphan = True
        
        sim_curr = 0
        if curr['es'].strip() and curr['en'].strip():
             sim_curr = SequenceMatcher(None, curr['en'], curr['es']).ratio()
             if sim_curr < 0.35: # Treat bad match as orphan for stealing purposes
                  is_orphan = True
                  
        len_nxt_en = len(nxt['en'])
        len_nxt_es = len(nxt['es'])
        ratio_nxt = len_nxt_es / len_nxt_en if len_nxt_en > 0 else 0
        
        print(f"DEBUG Phase 3f Check: i={i} IsOrphan={is_orphan} RatioNxt={ratio_nxt:.2f}")

        if not is_orphan:
             # If it has text, print it for debugging
             if i == 2:
                  print(f"DEBUG Item 2 Content: '{curr['es'][:50]}'")
             # continue # Don't continue, let it flow through phase 4 checks?
             # No, Phase 3f is separate from Phase 4
             # Phase 3f logic block
        
        pass # End of trace block logic
        
        if not nxt['es'].strip():
             continue
             
        # Check if next is Fat
        if ratio_nxt > 1.8:
             # Try to split Next
             parts = split_sentences(nxt['es'])
             
             # Debug parts
             print(f"DEBUG Phase 3f Parts Check: i={i} NxtES='{nxt['es'][:20]}...' NumParts={len(parts)}")
             
             best_cut_idx = -1

             best_score = -1
             best_head = ""
             best_tail = ""
             for k in range(1, len(parts)):
                  head = " ".join(parts[:k])
                  tail = " ".join(parts[k:])
                  
                  # Check sim of Head vs Orphan(Curr)
                  sim_steal = SequenceMatcher(None, curr['en'], head).ratio()
                  sim_tail = SequenceMatcher(None, nxt['en'], tail).ratio()
                  sim_head_vs_next = SequenceMatcher(None, nxt['en'], head).ratio()
                  
                  # Debug
                  print(f"DEBUG Phase 3f Scan: k={k} Steal={sim_steal:.3f} Tail={sim_tail:.3f}")

                  # Length Heuristics
                  len_en_curr = len(curr['en'])
                  len_en_nxt = len(nxt['en'])
                  
                  ratio_steal = len(head) / len_en_curr if len_en_curr > 0 else 0
                  ratio_keep = len(tail) / len_en_nxt if len_en_nxt > 0 else 0
                  
                  is_candidate = False
                  
                  # 1. Strong Similarity Signal
                  if sim_tail > 0.3 and sim_tail > sim_head_vs_next:
                       is_candidate = True
                  
                  # 2. Strong Length Signal (if Sim is weak but non-zeroish)
                  if not is_candidate and sim_tail > 0.05:
                       # We only verify that the HEAD looks correct for the Orphan.
                       # The Tail is likely huge (Fat), so ratio_keep will be bad.
                       if 0.5 < ratio_steal < 2.5:
                            is_candidate = True
                  
                  if is_candidate:
                       # Score: Sim + Ratio Match?
                       dist_steal = abs(ratio_steal - 1.5)
                       # ratio_penalty = dist_steal + dist_keep
                       
                       score = sim_tail - (dist_steal * 0.1) 
                       
                       if score > best_score:
                            best_score = score
                            best_cut_idx = k
                            best_head = head
                            best_tail = tail
                            
             if best_cut_idx != -1:
                  print(f"DEBUG Phase 3f Steal: i={i} Score={best_score:.2f} Head='{best_head[:20]}'")
                  curr['es'] = best_head
                  nxt['es'] = best_tail

                  # Continue to next (which is nxt, but nxt is now modified)

    # -------------------------------------------------------------------------
    # Phase 4: Greedy Spanish Split & Ripple Shift

    # Handles cases where S[i] consumed content for E[i+1], causing a mismatched chain shift.
    
    phase_4_aligned = []
    carry_es = None
    
    for i in range(len(final_pass)):
        item = final_pass[i]
        
        # 1. Handle Incoming Ripple
        if carry_es:
            # We have a displaced Spanish chunk. Does it belong here?
            # Compare sim(EN, Carry) vs sim(EN, ES)
            en_txt = item['en']
            cur_es = item['es']
            
            sim_carry = SequenceMatcher(None, en_txt, carry_es).ratio() if en_txt else 0
            sim_curr = SequenceMatcher(None, en_txt, cur_es).ratio() if en_txt and cur_es else 0
            
            # Bias towards carry if it's a decent match, because ripple implies correction
            if sim_carry > 0.3 and sim_carry >= sim_curr - 0.1:
                # Swap!
                item['es'] = carry_es
                carry_es = cur_es # Displace current
            else:

                # Carry doesn't match here. 
                # Could be that Carry belongs to a Missing English chunk (Insert)?
                # Or we logic error.
                # For now, let's assume if we started a ripple, we persist it unless explicitly blocked?
                # Actually, if sim_carry is bad, maybe we should insert carry as a separate item?
                # But we are 1-to-1 aligning.
                # Let's simple swap for now as per algorithm.
                item['es'] = carry_es
                carry_es = cur_es
        
        # 2. Check for Greedy Split (Initiate Ripple)
        # Only if we aren't currently carrying (or even if we are? No, if we just swapped, we look at NEW es)
        # But if we swapped, item['es'] is the Carry (the proper match). It shouldn't be split.
        # So only check if NOT ripple?
        # Actually, check if item['es'] is "Fat" and matches NEXT EN.
        
        if i + 1 < len(final_pass):
            nxt_en = final_pass[i+1]['en']
            cur_es = item['es']
            
            if nxt_en and cur_es:
                # Heuristic: Check if Tail of Cur_ES matches Nxt_EN
                # Split cur_es into sentences. Try ALL cuts.
                parts = split_sentences(cur_es)
                
                best_cut_idx = -1
                best_tail = ""
                best_head = ""
                
                # Helper for token-based similarity (Proper Nouns & Numbers)
                def get_token_sim(t1, t2):
                    if not t1 or not t2: return 0.0
                    
                    # Extract features
                    # 1. Numbers
                    nums1 = set(re.findall(r'\d+', t1))
                    nums2 = set(re.findall(r'\d+', t2))
                    
                    # 2. Proper Nouns (Capitalized words > 3 chars)
                    # Exclude start of sentence? Hard to detect in fragments.
                    # Just verify if it appears in both.
                    props1 = set(re.findall(r'\b[A-Z][a-z]{3,}\b', t1))
                    props2 = set(re.findall(r'\b[A-Z][a-z]{3,}\b', t2))
                    
                    set1 = nums1 | props1
                    set2 = nums2 | props2
                    
                    if not set1 or not set2:
                         return 0.0 # No anchors to compare
                         
                    isect = set1 & set2
                    if not isect:
                         return 0.0
                    
                    # Dice Coefficient / Ratio
                    return 2.0 * len(isect) / (len(set1) + len(set2))

                # Baseline: Don't split.
                current_score = get_token_sim(item['en'], item['es'])
                best_score = current_score + 0.05 
                
                sim_existing = 0
                if i + 1 < len(final_pass):
                     nxt_es_check = final_pass[i+1]['es']
                     sim_existing = get_token_sim(nxt_en, nxt_es_check)
                
                # We iterate cuts.
                # k is number of sentences to KEEP.
                for k in range(1, len(parts)):
                    head = " ".join(parts[:k])
                    tail = " ".join(parts[k:])
                    
                    sim_keep = get_token_sim(item['en'], head)
                    sim_give = get_token_sim(nxt_en, tail)
                    
                    # Debug loop
                    # print(f"DEBUG Cut k={k}: Keep={sim_keep:.3f} Give={sim_give:.3f} Existing={sim_existing:.3f}")

                    # Bad Match Override Check
                    # If Give is WORSE than Existing (and existing is real), don't do it.
                    if sim_existing > 0.4 and sim_give < sim_existing + 0.1:
                         continue
                         
                    score = sim_keep + sim_give
                    if score > best_score:
                         best_score = score
                         best_cut_idx = k

                         best_tail = tail
                         best_head = head
                         
                if best_cut_idx != -1:
                     # Thresholds
                     # If score is reasonable?
                     # print(f"DEBUG Phase 4 Split Found: i={i} Score={best_score:.2f} HeadLen={len(best_head)} TailLen={len(best_tail)}")
                     
                     item['es'] = best_head
                     if carry_es:
                         carry_es = best_tail + " " + carry_es
                     else:
                         carry_es = best_tail
                         
                     # Also update nxt['es'] immediately for the next iteration?
                     # No, we use 'carry_es' to pass it.
                     # Wait. The original code updated nxt['es']?
                     # My previous edit (Step 949) removed 'nxt['es'] = best_tail'.
                     # Instead it used 'carry_es'.
                     # Correct. 'carry_es' flows to 'i+1' in next loop iteration.
                     pass

        phase_4_aligned.append(item)

        
    # Handle leftover carry
    if carry_es:
         phase_4_aligned.append({'tag': 'p', 'classes': [], 'en': '', 'es': carry_es})
         
    # -------------------------------------------------------------------------

    # Remove Legacy Phase 3 Post-processing block
    
    # -------------------------------------------------------------------------
    # Phase 5: Splitter Service (Post-Alignment Refinement)
    # -------------------------------------------------------------------------
    if Splitter:
        splitter = Splitter(aligner=CACHED_ALIGNER)
        phase_4_aligned = splitter.process_all(phase_4_aligned)

    return phase_4_aligned


def generate_html(aligned_pairs):
    html = """<html><head><style>
    body { font-family: serif; line-height: 1.5; max-width: 800px; margin: 0 auto; padding: 20px; }
    p, h1, h2, h3, div { margin-bottom: 10px; }
    p, h1, h2, h3, div { margin-bottom: 10px; }
    .es-trans { color: grey; margin-bottom: 1em; display: block; }
    .no-bottom-margin { margin-bottom: 0 !important; }
    figcaption { font-weight: bold; margin-top: 10px; }
    .image-subtitle { font-style: italic; color: #555; margin: 10px 0; text-align: center; }
    </style></head><body>"""
    
    for item in aligned_pairs:
        tag = item['tag']
        en_text = item['en']
        es_text = item['es']
        
        if not en_text and not es_text and tag != 'img': continue

        # English Block
        if tag.startswith('h') or tag == 'figcaption':
            html += f"<{tag}>{en_text}</{tag}>"
        elif tag == 'img':
             src = item.get('src', '')
             alt = item.get('alt', '')
             html += f'<img src="{src}" alt="{alt}" />'
        else:
            html += f"<p>{en_text}</p>"
        
        # Spanish Block (Mirroring Tag)
        # For images, we usually don't want to duplicate, unless we want to show the Spanish one too?
        # User request: "take pictures from the original book".
        # So usually we ignore Spanish image chunk if aligned.
        # But if we have text in Spanish side? Images have empty text.
        
        if es_text:
            if tag.startswith('h') or tag == 'figcaption':
                 html += f"<{tag} class='es-trans'>{es_text}</{tag}>"
            else:
                 html += f"<p class='es-trans'>{es_text}</p>"
            
    html += "</body></html>"
    return html

def reconstruct_aligned_items(aligned_groups):
    """
    Reconstructs a flat list of aligned items from Neural Alignment groups.
    Handles splitting of groups containing images or special blocks that shouldn't be merged.
    """
    aligned = []
    
    # Helper to merge a subset of chunks (local to this function context if simple, or defined here)
    def create_merged_item(sub_ens, sub_ess):
        m_en = ""
        m_es = ""
        t_tag = 'p'
        t_classes = []
        
        if sub_ens:
                m_en = " ".join([c.get('text', '') for c in sub_ens])
                t_tag = sub_ens[0].get('tag', 'p')
                t_classes = sub_ens[0].get('classes', [])
        
        if sub_ess:
                m_es = " ".join([c.get('text', '') for c in sub_ess])
                if not sub_ens:
                    t_tag = sub_ess[0].get('tag', 'p')
                    t_classes = sub_ess[0].get('classes', [])

        raw = None
        if sub_ens and len(sub_ens) == 1:
            raw = sub_ens[0].get('raw_html')
        
        # Base copy to preserve attrs (src, alt)
        b_item = {}
        if sub_ens:
            b_item = sub_ens[0].copy()
        elif sub_ess:
            b_item = sub_ess[0].copy()
            b_item['en'] = ""
        else:
            # Should not happen if passed valid stuff
            return None
        
        b_item.update({
            'tag': t_tag,
            'classes': t_classes,
            'en': m_en,
            'es': m_es,
            'raw_html': raw
        })
        return b_item

    for group in aligned_groups:
        ens = group['en_chunks']
        ess = group['es_chunks']

        # Check for images in ens
        has_image = any(c.get('type') == 'image' or c.get('tag') == 'img' for c in ens)
        
        if not has_image:
            # Standard Merge
            aligned.append(create_merged_item(ens, ess))
        else:
            # Split Logic: Flush text buffers around images
            cur_buf = []
            es_consumed = False
            
            for c in ens:
                if c.get('type') == 'image' or c.get('tag') == 'img':
                    # Flush buffer
                    if cur_buf:
                        # Assign ES to first block?
                        use_es = ess if not es_consumed else []
                        aligned.append(create_merged_item(cur_buf, use_es))
                        if use_es: es_consumed = True
                        cur_buf = []
                    
                    # Emit Image
                    aligned.append(create_merged_item([c], []))
                else:
                    cur_buf.append(c)
            
            # Flush final
            if cur_buf:
                    use_es = ess if not es_consumed else []
                    aligned.append(create_merged_item(cur_buf, use_es))
                    
    return aligned

def extract_body_content(file_path):
    """Extracts the raw inner HTML of the body tag."""
    if not file_path or not os.path.exists(file_path): return ""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Simple regex to find body
            m = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL | re.IGNORECASE)
            if m:
                return m.group(1).strip()
            else:
                 # Fallback: return everything? No, might include Head.
                 # Just return generic placeholder if failed?
                 return ""
    except Exception as e:
        print(f"Error extracting body from {file_path}: {e}")
        return ""

def generate_passthrough_chapter(en_src, es_src, title, staging_dir=None):
    """Generates a combined chapter without alignment, preserving raw structure and images."""
    
    def process_content(source_path, staging_dir):
        if not source_path: return ""
        content = extract_body_content(source_path)
        if not content or not staging_dir: return content
        
        # Regex to find src attributes (img, audio, video)
        # Matches src="...", src='...'
        # We also need to handle xlink:href for svg images if present, but standard img src is main target
        
        base_dir = os.path.dirname(source_path)
        img_dest_dir = os.path.join(staging_dir, 'OEBPS', 'images')
        if not os.path.exists(img_dest_dir): os.makedirs(img_dest_dir, exist_ok=True)
        
        def replace_src(match):
            attr_name = match.group(1)
            original_src = match.group(3)
            # Ignore external links or data URIs
            if original_src.startswith('http') or original_src.startswith('data:') or original_src.startswith('mailto:'):
                return match.group(0)
                
            # Ignore non-image extensions (prevent rewriting links to other chapters)
            # We allow jpg, png, gif, svg, jpeg, webp, etc.
            # We explicitly block html-like types
            lower_src = original_src.lower()
            if any(lower_src.endswith(ext) for ext in ['.xhtml', '.html', '.htm', '.ncx', '.css', '#']):
                 return match.group(0)
            
            # Resolve absolute path
            # Handle encoded URL chars in filename if any
            import urllib.parse
            dec_src = urllib.parse.unquote(original_src)
            
            # If path starts with ../ resolve it
            full_src_path = os.path.normpath(os.path.join(base_dir, dec_src))
            
            if os.path.exists(full_src_path):
                fname = os.path.basename(full_src_path)
                dest_path = os.path.join(img_dest_dir, fname)
                shutil.copy2(full_src_path, dest_path)
                print(f"Passthrough Copy: {fname}")
                return f'{match.group(1)}="images/{fname}"'
            else:
                print(f"Warning: Passthrough image missing: {full_src_path}")
                return match.group(0)

        # Pattern: (src|href)=["'](.*?)["']
        # We focus on src attribute primarily. 
        # Use re.sub with callback to robustly handle replacements
        processed = re.sub(r'(src|href)=([\'"])(.*?)\2', replace_src, content)
        
        return processed

    en_body = process_content(en_src, staging_dir)
    es_body = process_content(es_src, staging_dir)
    
    # Check if this page should be centered (Title Page, Cover)
    is_centered = False
    if title and any(x in title.lower() for x in ['title page', 'cover']):
        is_centered = True
        
    center_class = " centered-content" if is_centered else ""
    
    html_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
  <style>
     .passthrough-container {{ margin-bottom: 2em; padding-bottom: 1em; border-bottom: 1px solid #ccc; }}
     .passthrough-container.centered-content {{ text-align: center; }}
     .passthrough-container.centered-content img {{ margin: 0 auto; display: block; }}
     .es-original {{ color: #444; margin-top: 2em; }}
  </style>
</head>
<body>
    <!-- English Content -->
    <div class="en-original passthrough-container{center_class}">
       {en_body}
    </div>
    
    <!-- Spanish Content -->
    <div class="es-original passthrough-container{center_class}">
       {es_body}
    </div>
</body>
</html>
"""
    return html_content

def apply_common_styles(en_html, es_text):
    """
    Attempts to transfer common formatting styles from English HTML to Spanish text.
    Handles:
    1. Full wrapping tags (i, b, strong, em, small)
    2. Dialogue patterns (specific <small>LABEL:</small> <i>Text</i>)
    """
    if not en_html or not es_text:
        return es_text

    # 1. Check for Full Wrapping Tags
    # Matches <tag>content</tag> with no other tags at top level
    # Updated to allow attributes, whitespace, and trailing punctuation (e.g., <i>text</i>.)
    # Matches: <tag attr>content</tag>trailing
    full_wrap_pattern = re.compile(r'^\s*<(i|b|strong|em|small)(?:\s+[^>]*)?>(.+?)</\1>(\s*[.!?;:,]*)?\s*$', re.DOTALL | re.IGNORECASE)
    match = full_wrap_pattern.match(en_html)
    if match:
        tag = match.group(1).lower() # Normalize tag name
        trailing = match.group(3) or ""  # Capture trailing punctuation
        # We wrap the entire Spanish text in the CLEAN tag (no attributes)
        # This preserves the style (italics/bold) but strips specific classes/colors
        # Only add trailing punctuation if Spanish doesn't already end with similar punctuation
        es_stripped = es_text.rstrip()
        if trailing.strip() and es_stripped and es_stripped[-1] in '.!?;:,':
            # Spanish already ends with punctuation, don't duplicate
            trailing = ""
        return f"<{tag}>{es_text}</{tag}>{trailing}"

    # 2. Check for Dialogue Pattern
    # Pattern: <small>SPEAKER:</small> <i>Dialogue</i>
    # We are lenient with whitespace
    dia_pattern = re.compile(r'^<small>([^<]+):</small>\s*<i>(.*?)</i>$', re.DOTALL)
    dia_match = dia_pattern.match(en_html)
    
    if dia_match:
        # Check if Spanish has a similar structure (finding the first colon)
        # We look for "Speaker: Dialogue"
        if ':' in es_text:
            parts = es_text.split(':', 1)
            speaker = parts[0].strip()
            dialogue = parts[1].strip()
            
            # Reconstruct with transferred styles
            return f"<small>{speaker}:</small> <i>{dialogue}</i>"

    # 3. Check for Figure/Table Caption Pattern (Robust BS4)
    # Pattern: <p class="..."><small>FIGURE X:</small> Description</p> or just <small>FIGURE X:</small> Description
    # We parse the HTML structure explicitly to handle wrappers like <figcaption>.
    
    try:
        soup = BeautifulSoup(en_html, 'html.parser')
        
        # Look for the <small> tag defining the figure label
        small = soup.find('small')
        if small:
             small_text = small.get_text()
             # Check if it looks like a figure label
             if re.match(r'^(FIGURE|FIGURA|TABLE|TABLA|FIG\.)', small_text, re.IGNORECASE):
                 # Found English Label
                 en_label = small_text.strip()
                 
                 # Check if Spanish text starts with a similar label pattern
                 es_fig_pattern = re.compile(r'^((?:Figura|Tabla|Figure|Table|Cuadro|Grafico|Fig\.)\s*\d+[\.\:]?)\s*(.*)', re.DOTALL | re.IGNORECASE)
                 es_fig_match = es_fig_pattern.match(es_text.strip())
                 
                 if es_fig_match:
                     es_label = es_fig_match.group(1).strip()
                     es_description = es_fig_match.group(2).strip()
                     
                     # Reconstruct content with small tag
                     es_content = f"<small>{es_label}</small> {es_description}"
                     
                     # Check if there is a wrapping <p> tag with classes we should inherit
                     # We favor the innermost <p> that wraps the <small> tag
                     # But in <figcaption><p class="CAP">..., the <p> is a parent of <small>
                     p_tag = small.find_parent('p')
                     if p_tag and p_tag.get('class'):
                         classes = " ".join(p_tag.get('class'))
                         return f'<p class="{classes}">{es_content}</p>'
                     
                     # If no p tag, or no classes, just return the content using the inferred tag?
                     # If the original was just <p> without class, we might want to preserve <p>?
                     if p_tag:
                         return f'<p>{es_content}</p>'
                         
                     return es_content

    except Exception as e:
        print(f"Warning: BS4 parsing failed in apply_common_styles: {e}")
        pass

    return es_text

def generate_chapter_html(aligned_pairs, title="", css_files=None):
    """Generates XHTML for a single chapter."""
    css_links = ""
    if css_files:
        for css in css_files:
            css_links += f'  <link rel="stylesheet" type="text/css" href="{css}"/>\n'
    
    # Always include our custom styles last to override colors
    css_links += '  <link rel="stylesheet" type="text/css" href="styles.css"/>\n'

    html_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{html.escape(title)}</title>
  {css_links}
</head>
<body>
"""
    
    
    for i in range(len(aligned_pairs)):
        item = aligned_pairs[i]
        tag = item['tag']
        en_text = item['en']
        es_text = item['es']

        if not en_text and not es_text and not item.get('raw_html') and not item.get('es_raw_html') and tag != 'img': 
             continue
        



        
        # Format attributes
        tag_classes = item.get('classes', [])
        cls_str = " ".join(tag_classes)
        en_attrs = f' class="{cls_str}"' if cls_str else ""
        
        # Check for split continuation (end with asterism)
        is_split_continuation = en_text.strip().endswith("⁂")
        
        # For Spanish, we apply structural classes to the container,
        # but stylistic 'es-trans' to the inner content (via span) to avoid overrides.
        es_container_classes = list(tag_classes)
        if is_split_continuation:
            es_container_classes.append('no-bottom-margin')
            
        # Ensure Spanish container has es-trans class for CSS targeting
        if 'es-trans' not in es_container_classes:
            es_container_classes.append('es-trans')
            
        es_cls_str = " ".join(es_container_classes)
        es_attrs = f' class="{es_cls_str}"' if es_cls_str else ""
        
        
        # Calculate English Attributes with optional margin logic
        limit_margin = False
        has_spanish_local = (es_text or item.get('es_raw_html'))
        
        # Logic: We want to trigger margin removal IF:
        # 1. We have local Spanish (Standard Case)
        # 2. OR We are the LAST English header in a group immediately followed by a Spanish block (Split Header Case)
        
        is_last_english_before_spanish = False
        
        
        
        # Check subsequent items to see what is next
        for k in range(i + 1, len(aligned_pairs)):
            check_item = aligned_pairs[k]
            
            # Check content presence
            c_en = check_item.get('en', '')
            c_raw = check_item.get('raw_html')
            has_en_content = (c_en and c_en.strip()) or c_raw
            
            c_es = check_item.get('es', '')
            c_es_raw = check_item.get('es_raw_html')
            has_es_content = (c_es and c_es.strip()) or c_es_raw
            
            if has_en_content:

                # We found another English item before finding a Spanish one.
                # So we are NOT the last English item in this group.
                is_last_english_before_spanish = False
                break
            
            if has_es_content:
                # We found a Spanish item, and haven't seen English yet.
                # So we ARE the last English item connecting to this Spanish block.
                is_last_english_before_spanish = True
                break
        
        if (has_spanish_local or is_last_english_before_spanish) and (tag.startswith('h') or item.get('type') == 'caption'):
             limit_margin = True
         
        final_en_attrs = en_attrs
        if limit_margin:
             # Inject class
             if 'class="' in en_attrs:
                 final_en_attrs = en_attrs.replace('class="', 'class="no-bottom-margin ')
             else:
                 final_en_attrs = ' class="no-bottom-margin"'

        # En
        # Only render English block if there is content (or raw_html)
        # Simplify check:
        c_en = en_text.strip()
        c_raw = item.get('raw_html')
        
        if c_en or c_raw:
            if c_raw:
                # Use raw extracted HTML to preserve styles (<i>, <small>, <span>, etc.)
                final_raw = c_raw
                
                # SPECIAL HANDLING: If raw_html contains block-level tags (like merged headers),
                # we must inject the margin class into the LAST block element within it.
                # Otherwise, the wrapper's class only affects the first element (due to browser HTML parsing).
                if limit_margin:
                    # Find all block start tags: <h1...>, <p...>, <div...>
                    # We look for <(h1-6|p|div) ... >
                    # Using a regex that captures: 1=TagStart(<h1), 2=Attributes, 3=TagEnd(>)
                    pattern = r'(<(?:h[1-6]|p|div|figcaption)\b)([^>]*?)(/?>)'
                    matches = list(re.finditer(pattern, final_raw, re.IGNORECASE))
                    if matches:
                        last_m = matches[-1]
                        g1, g2, g3 = last_m.group(1), last_m.group(2), last_m.group(3)
                        
                        # Inject class
                        if 'class="' in g2 or "class='" in g2:
                             new_attrs = re.sub(r'class=(["\'])', r'class=\1no-bottom-margin ', g2)
                        else:
                             new_attrs = g2 + ' class="no-bottom-margin"'
                        
                        # Reconstruct string
                        replacement = f"{g1}{new_attrs}{g3}"
                        final_raw = final_raw[:last_m.start()] + replacement + final_raw[last_m.end():]

                if tag.startswith('h') or tag == 'figcaption':
                     html_content += f"<{tag}{final_en_attrs}>{final_raw}</{tag}>\n"
                else:
                     html_content += f"<p{final_en_attrs}>{final_raw}</p>\n"
            else:
                 if tag.startswith('h') or tag == 'figcaption':

                    html_content += f"<{tag}{final_en_attrs}>{en_text}</{tag}>\n"
                 else:
                    html_content += f"<p{final_en_attrs}>{en_text}</p>\n"
        
        # Es
        # First, try to apply style transfer if we have raw English HTML
        final_es_content = None
        
        # Use English Raw HTML map if available, else plain text (less useful for transfer)
        en_source_for_transfer = item.get('raw_html') or en_text
        
        if es_text and not item.get('es_raw_html'):
             # Try transfer
             final_es_content = apply_common_styles(en_source_for_transfer, es_text)
        elif item.get('es_raw_html'):
             final_es_content = item.get('es_raw_html')
        else:
             final_es_content = es_text # Fallback

        if final_es_content:
            content = final_es_content
            
            # Check if content already contains block-level elements (from apply_common_styles)
            # If so, don't wrap in span - just use directly
            has_block_element = re.search(r'<(?:p|div|h[1-6])\s', content, re.IGNORECASE)
            
            if has_block_element:
                # Content already has proper structure, output directly
                # For figcaption, we still need the outer figcaption tag
                if tag == 'figcaption':
                    html_content += f"<{tag}{es_attrs}>{content}</{tag}>\n"
                else:
                    # For other tags, content is self-contained
                    html_content += f"{content}\n"
            else:
                # Wrap in generic span for styling isolation
                wrapped_content = f'<span class="es-trans">{content}</span>'
                
                if tag.startswith('h') or tag == 'figcaption':
                     html_content += f"<{tag}{es_attrs}>{wrapped_content}</{tag}>\n"
                else:
                     html_content += f"<p{es_attrs}>{wrapped_content}</p>\n"
                 
        # Image (English Only usually)
        # Image (English Only usually)
        if tag == 'img':
             # Logic: If item has src, print it.
             # We put it OUTSIDE the p/h blocks.
             src = item.get('src', '')
             alt = item.get('alt', '')
             width = item.get('width')
             height = item.get('height')
             style = item.get('img_style')
             direct_classes = item.get('img_classes', [])
             
             # We should wrap it in a div or figure for containment?
             # Simple img for now.
             if src:
                 # Add derived classes to container from PARENT
                 parent_classes = item.get('classes', [])
                 container_class = "image-container"
                 if parent_classes:
                     container_class += " " + " ".join(parent_classes)
                 
                 # Construct img tag attributes
                 img_attrs_list = [f'src="{src}"', f'alt="{alt}"']
                 if width: img_attrs_list.append(f'width="{width}"')
                 if height: img_attrs_list.append(f'height="{height}"')
                 if style: img_attrs_list.append(f'style="{style}"')
                 
                 # Add direct img classes
                 if direct_classes:
                     img_attrs_list.append(f'class="{" ".join(direct_classes)}"')
                     
                 img_tag = f'<img {" ".join(img_attrs_list)} />'
                 
                 # Use preserved wrapper tag (e.g., figure) or default to div
                 wrapper = item.get('wrapper_tag', 'div')
                 html_content += f'<{wrapper} class="{container_class}">{img_tag}</{wrapper}>\n'
            
    html_content += "</body></html>"
    return html_content

def find_toc_file(base_dir):
    # Try standard name first
    std = os.path.join(base_dir, 'toc.ncx')
    if os.path.exists(std): return std
    # Search recursively
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.ncx'):
                return os.path.join(root, f)
    return None

def collect_split_files(base_src, base_dir):
    """
    If base_src is 'chapter001_split_000.xhtml', find all siblings like 'chapter001_split_*.xhtml'.
    Returns list of absolute paths.
    """
    if not base_src:
        return []
    
    full_path = os.path.join(base_dir, base_src)
    if not os.path.exists(full_path):
        return []
        
    filename = os.path.basename(base_src)
    dirname = os.path.dirname(full_path)
    
    # Regex for split pattern: prefix_split_NUM.ext
    # Matches e.g. chapter001_split_000.xhtml
    match = re.match(r'^(.*)_split_(\d+)(\.[^.]+)$', filename)
    if not match:
        return [full_path]
        
    prefix = match.group(1)
    suffix = match.group(3)
    
    # SAFEGUARD 1: Generic Prefix "index"
    # Calibre often names ALL files index_split_xxx. merging them connects the whole book.
    if prefix.lower() == 'index':
        return [full_path]

    # Search dir
    siblings = []
    try:
        if os.path.exists(dirname):
            for f in os.listdir(dirname):
                # strict match to avoid mixing chapter001 vs chapter0010
                m = re.match(r'^(.*)_split_(\d+)(\.[^.]+)$', f)
                if m and m.group(1) == prefix and m.group(3) == suffix:
                    siblings.append(os.path.join(dirname, f))
    except Exception as e:
        print(f"Error collecting split files: {e}")
        return [full_path]
        
    if not siblings: return [full_path]
    
    # SAFEGUARD 2: Excessive Splitting
    # If we matched > 50 files, it's likely a mis-identification of a split sequence
    # unless it's a huge dictionary. But for normal chapters, 50 parts is suspicious.
    if len(siblings) > 50:
        print(f"Warning: Found {len(siblings)} split parts for {base_src}. Assuming false positive and using single file.")
        return [full_path]

    siblings.sort() # Ensure textual sort matches numeric order
    return siblings

def unzip_epub(epub_path, extract_to):
    """Unzips an EPUB file to a destination directory."""
    if os.path.isdir(epub_path):
        print(f"Input {epub_path} is a directory. Using as-is.")
        # If it's already a dir, we assume it's the unzipped content.
        # However, create_bilingual_epub might expect it to be IN extract_to.
        # Simpler to just return absolute path.
        return os.path.abspath(epub_path)
        
    if not os.path.exists(epub_path):
        raise FileNotFoundError(f"EPUB file not found: {epub_path}")
    
    # The rest of the unzip_epub function would go here if it were fully provided.
    # For now, we'll assume it's just the directory check.
    # Placeholder for actual unzip logic if needed later:
    # with zipfile.ZipFile(epub_path, 'r') as zip_ref:
    #     zip_ref.extractall(extract_to)
    # return extract_to


def is_navigation_page(soup, threshold=0.5):
    """
    Detect if a page is primarily a navigation/index page (TOC, list of chapters, etc.).
    Returns True if the ratio of navigation links to text content is high.
    
    Args:
        soup: BeautifulSoup parsed HTML
        threshold: Ratio threshold - if link-heavy paragraphs / total paragraphs > threshold, it's navigation
    """
    # Count elements with links that point to internal content
    links = soup.find_all('a', href=True)
    internal_links = [a for a in links if not a.get('href', '').startswith(('http://', 'https://', 'mailto:'))]
    
    # Count text paragraphs (non-link content)
    paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    
    # If there are many internal links, check if it's a navigation page
    if len(internal_links) > 20:  # Arbitrary threshold - TOC has many links
        # Check if most paragraphs just contain links
        link_heavy_paras = 0
        for p in paragraphs:
            p_text = p.get_text(strip=True)
            links_in_p = p.find_all('a')
            if links_in_p and len(p_text) < 100:  # Short text with links = likely TOC entry
                link_heavy_paras += 1
        
        if paragraphs and link_heavy_paras / len(paragraphs) > threshold:
            return True
    
    return False


def is_part_title_page(en_chunks):
    """
    Detect if page contains only headers (part/chapter title pages).
    These pages should not receive full chapter translations.
    
    Returns True if page has <= 5 chunks and all are headers (not std paragraphs).
    """
    if len(en_chunks) > 5:  # More than 5 chunks = not a title page
        return False
    
    if len(en_chunks) == 0:
        return False
    
    for chunk in en_chunks:
        # If ANY chunk is regular text paragraph, it's not a title page
        chunk_type = chunk.get('type', 'std')
        chunk_tag = chunk.get('tag', 'p')
        
        # Headers have type='header' or tag in h1-h6
        is_header = chunk_type == 'header' or chunk_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        if not is_header:
            return False
    
    return True


def filter_to_matching_headers(en_chunks, es_chunks):
    """
    Filter ES chunks to only header-type chunks matching EN structure.
    Used for part title pages to prevent content bleeding.
    
    Returns: List of ES chunks containing only headers, matched to EN count.
    """
    # Spanish title classes that indicate headers
    title_classes = ['titulo', 'titulo1', 'titulo2', 'capitulo', 'chapter-title', 'part-title']
    
    # Only keep ES chunks that are headers
    es_headers = []
    for c in es_chunks:
        chunk_type = c.get('type', 'std')
        chunk_tag = c.get('tag', 'p')
        chunk_classes = c.get('classes', [])
        
        # Check if it's a header by type, tag, or CSS class
        is_header = chunk_type == 'header' or chunk_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        # Also check for Spanish title classes
        if not is_header and chunk_classes:
            for cls in chunk_classes:
                if any(tc in cls.lower() for tc in title_classes):
                    is_header = True
                    break
        
        if is_header:
            es_headers.append(c)
    
    # Return up to same count as EN chunks (one header per EN header)
    return es_headers[:len(en_chunks)]


def process_chapter_pair(args):
    # Unpack args
    if len(args) == 7:
        idx, en_path, es_path, es_opf_dir, config, label, chunk_range = args
    else:
        # Backward compatibility
        idx, en_path, es_path, es_opf_dir, config, label = args
        chunk_range = None
    """
    Worker function to process a single chapter pair IN-PLACE.
    args: (idx, target_path, es_rel, es_opf_dir, config, label)
    """
    # The original line `idx, target_path, es_rel, es_opf_dir, config, label = args` is replaced by the if/else block above.
    # Now, map the new variable names to the old ones for the rest of the function's logic.
    target_path = en_path
    es_rel = es_path

    print(f"DEBUG: Entering process_chapter_pair for {label}")
    print(f"DEBUG: MAPPING: {os.path.basename(target_path)} <-> {os.path.basename(es_rel) if es_rel else 'None'}")
    
    # Check bypass
    if config.get('bypass_alignment'):
         return (idx, None, "Bypassed", None)

    try:
        # 1. Parse Existing English File (DOM)
        if not os.path.exists(target_path):
             return (idx, None, f"Target file not found: {target_path}", None)

        with open(target_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'lxml')

        # 2. Extract Nodes for Alignment
        en_chunks = extract_nodes(soup)
        print(f"DEBUG: {label} - Extracted {len(en_chunks)} EN chunks")

        # Check if this is a navigation page (TOC, index, etc.) - skip alignment
        if is_navigation_page(soup):
            print(f"DEBUG: {label} - Detected as navigation page, skipping alignment")
            return (idx, target_path, label, [])
            
        # --- PRE-PROCESS: Merge Consecutive Headers (Fixed for Atomic Habits) ---
        # Atomic Habits splits Chapter Num and Title into separate h2 tags.
        # But Spanish has them in one p tag.
        # Merging English headers simplifies alignment and layout.
        en_conf = config.get('en', {})
        if en_conf.get('merge_headers'):
             en_chunks = merge_consecutive_headers(en_chunks)
             print(f"DEBUG: {label} - Merged headers, count is now {len(en_chunks)}")
        
        # --- PRE-PROCESS: Skip Alignment for Standalone Numeric Headers ---
        # Dungeon Crawler Carl and similar books have decorative numeric headers (e.g. "<h1>4</h1>")
        # while Spanish uses images. These shouldn't force Spanish content alignment.
        for i, chunk in enumerate(en_chunks):
            if chunk.get('type') == 'header' and is_standalone_numeric_header(chunk.get('text', '')):
                # Mark for skipping - Spanish version uses images for chapter headers
                chunk['skip_alignment'] = True
                print(f"DEBUG: {label} - Marking standalone header '{chunk['text']}' to skip alignment")



        # --- PRE-PROCESS: Split Massive English Chunks ---
        # Same rationale as Spanish: Granularity mismatch causes alignment drifts/merges.
        temp_splitter_en = Splitter()
        new_en_chunks = []
        for c in en_chunks:
            txt = c['text']
            # Only split standard text, preserve headers/captions structure if small enough
            # But here we just use length check. 
            if len(txt) > 600 and c['type'] == 'std':
                parts = temp_splitter_en.split_sentences(txt)
                for part in parts:
                     if not part.strip(): continue
                     new_c = c.copy()
                     new_c['text'] = part
                     new_en_chunks.append(new_c)
            else:
                new_en_chunks.append(c)
        en_chunks = new_en_chunks
        print(f"DEBUG: {label} - Split EN chunks to {len(en_chunks)}")
        
        # 3. Parse Spanish Content
        if not es_rel or not os.path.exists(es_rel):
            # No Spanish chapter to align with.
            # We just leave the English file as-is.
            return (idx, target_path, label, [])
            
        es_files = [es_rel] 
        # Verify config has 'es' key before parsing
        if 'es' not in config:
             # Fallback if config incorrectly merged
             print(f"Warning: Config missing 'es' profile. Using generic defaults.")
             # Retrieve PROFILES['generic']['es'] manually if possible, or mocked
             # Ideally this should be fixed upstream in _process_epub_generation
             # But for robustness:
             config['es'] =  {
                'header_tags': ['h1', 'h2', 'h3', 'class:chapter-title', 'class:title'],
                'ignore_classes': [],
             }
             
        es_chunks = parse_file(es_rel, SpanishParser, config)
        print(f"DEBUG: {label} - Parsed {len(es_chunks)} ES chunks")
        
        # CRITICAL: Apply chunk range if this is a shared Spanish file
        if chunk_range:
            # Check if it's semantic (direct indices) or proportional
            if isinstance(chunk_range[0], int) and isinstance(chunk_range[1], int):
                # Semantic: direct (start, end) indices
                start_idx, end_idx = chunk_range
                total_chunks = len(es_chunks)
                print(f"DEBUG: {label} - Shared file detected (semantic), using chunks {start_idx}-{end_idx}")
                es_chunks = es_chunks[start_idx:end_idx]
                print(f"DEBUG: {label} - After semantic splitting: {len(es_chunks)} ES chunks for this chapter")
            else:
                # Proportional fallback: (position, proportions)
                position, proportions = chunk_range
                total_chunks = len(es_chunks)
                
                # Calculate cumulative boundaries using proportions
                cumulative = 0
                for i in range(position):
                    cumulative += proportions[i]
                start_idx = int(cumulative * total_chunks)
                
                cumulative += proportions[position]
                end_idx = int(cumulative * total_chunks) if position < len(proportions) - 1 else total_chunks
                
                print(f"DEBUG: {label} - Shared file detected (proportional), using chunks {start_idx}-{end_idx} ({proportions[position]*100:.1f}% of {total_chunks})")
                es_chunks = es_chunks[start_idx:end_idx]
                print(f"DEBUG: {label} - After proportional splitting: {len(es_chunks)} ES chunks for this chapter")
        
        # --- PART TITLE PAGE DETECTION ---
        # If EN page has only headers (part/chapter title page), filter ES to matching headers only.
        # This prevents full chapter content from bleeding into title pages.
        if is_part_title_page(en_chunks):
            print(f"DEBUG: {label} - Detected as PART TITLE PAGE, filtering ES to headers only")
            es_chunks = filter_to_matching_headers(en_chunks, es_chunks)
            print(f"DEBUG: {label} - Filtered ES to {len(es_chunks)} header chunks")
        
        # --- PRE-PROCESS: Split Massive Spanish Chunks ---
        # If a Spanish chunk is huge (e.g. > 600 chars), it likely contains merged paragraphs/headers.
        # We split it to give the aligner better granularity.
        
        # Instantiate Splitter for this pre-pass (Splitter is imported class)
        temp_splitter = Splitter() 
        
        new_es_chunks = []
        for c in es_chunks:
            txt = c['text']
            if len(txt) > 600:
                # Split into sentences
                parts = temp_splitter.split_sentences(txt)
                for part in parts:
                    if not part.strip(): continue
                    # Clone the chunk metadata but update text
                    new_c = c.copy()
                    new_c['text'] = part
                    new_es_chunks.append(new_c)
            else:
                new_es_chunks.append(c)
        es_chunks = new_es_chunks
        print(f"DEBUG: {label} - Split ES chunks to {len(es_chunks)}")
        
        print(f"DEBUG: {label} - use_neural={config.get('use_neural')}")
             
        if config.get('use_neural'):
             try:
                 global CACHED_ALIGNER
                 if CACHED_ALIGNER is None:
                     # Local import to prevent startup overhead if not used
                     from neural_aligner import NeuralAligner
                     # Use 'cpu' device if MPS is unstable? 
                     # For now, let it use default (likely MPS on Mac) but CACHE it.
                     CACHED_ALIGNER = NeuralAligner()
                 
                 aligner = CACHED_ALIGNER
                 
                 # --- CAPTION FILTERING ---
                 # Filter out captions from the alignment input to prevent strict monotonic constraint failures 
                 # when captions float (e.g. Figure X appears before text in EN vs after in ES).
                 
                 should_filter = config.get('filter_captions', False) # Default to False to include captions
                 print(f"DEBUG: {label} - Initial should_filter={should_filter}")
                 if not should_filter:
                      print("DEBUG: Caption filtering DISABLED by config.")
                 
                 en_filtered = []
                 for c in en_chunks:
                     if c['type'] == 'image': continue # Images always filtered from text alignment
                     
                     txt = c['text'].strip()
                     if should_filter:
                         if c['type'] == 'caption': continue
                         # Regex Check
                         if re.match(r'^(Figura|Figure|Tabla|Table|Cuadro|Grafico)\s*\d+', txt, re.IGNORECASE):
                             continue
                             
                     # Separator Check (Prevent Desync)
                     # Filter out scene breaks like * * * or ----- to prevent alignment shifts
                     if len(txt) < 20 and re.match(r'^[\s\*\-\u2013\u2014_]{3,}$', txt):
                         continue

                     en_filtered.append(c)
                 
                 # Post-process ES chunks to detect text-based captions (redundant safety)
                 es_filtered = []
                 for c in es_chunks:
                     if c['type'] == 'image': continue
                     
                     txt = c['text'].strip()
                     
                     if should_filter:
                         if c['type'] == 'caption': continue
                         
                         if re.match(r'^(Figura|Figure|Tabla|Table|Cuadro|Grafico)\s*\d+', txt, re.IGNORECASE):
                             continue
                             
                     # Separator Check (Prevent Desync)
                     if len(txt) < 20 and re.match(r'^[\s\*\-\u2013\u2014_]{3,}$', txt):
                         continue

                     es_filtered.append(c)
                     
                 should_filter = False # Force it to run
                 print(f"DEBUG: Processing Ch Pair. should_filter={should_filter}")
                 
                 # --- PRE-PROCESSING: MERGE SENTENCE FRAGMENTS ---
                 # Fix: "where Mrs. ⁂" + "Jones was..." → "where Mrs. ⁂ Jones was..."
                 from fragment_merger import merge_sentence_fragments
                 
                 print(f"DEBUG: {label} - Before merge: EN={len(en_filtered)}, ES={len(es_filtered)}")
                 en_filtered = merge_sentence_fragments(en_filtered)
                 es_filtered = merge_sentence_fragments(es_filtered)
                 print(f"DEBUG: {label} - After merge: EN={len(en_filtered)}, ES={len(es_filtered)}")
                 
                 # --- HEURISTIC: PRE-CALCULATE CONSTRAINTS ---
                 # If captions are present, we want to force-align them based on explicit numbering.
                 constraints = []
                 if not should_filter:
                     # 1. Map English Numbers -> Indices
                     en_nums = {} # Num -> [list of indices]
                     for i, c in enumerate(en_filtered):
                         txt = c['text'].strip()
                         # Safety: Captions shouldn't be huge paragraphs, unless explicit caption type
                         if len(txt) > 300 and c.get('type') != 'caption': continue 

                         m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)[\s:]*([0-9]+)', txt, re.IGNORECASE)
                         if m:
                             num = m.group(1).rstrip('.:,;- ') # Aggr. Normalize
                             if num not in en_nums: en_nums[num] = []
                             en_nums[num].append(i)
                         # Also match numbered captions like "3. A speculative reconstruction..."
                         # when chunk is already classified as 'caption' (from class="figure")
                         elif c.get('type') == 'caption':
                             m2 = re.match(r'^(\d+)\.?\s+\S', txt)
                             if m2:
                                 num = m2.group(1)
                                 if num not in en_nums: en_nums[num] = []
                                 en_nums[num].append(i)
                         
                         # Quick Win #3: Numbered List anchors ("1. ", "2. ")
                         # Helps align list structures even if interleaved with text
                         elif re.match(r'^(\d+)\.\s+[A-Z]', txt):
                             m_list = re.match(r'^(\d+)\.', txt)
                             if m_list:
                                 num = m_list.group(1) # Assign num here
                                 if num not in en_nums: en_nums[num] = []
                                 en_nums[num].append(i)
                                 
                         # Quick Win #4: Roman Numeral Anchors
                         # "Chapter IV" <-> "Capitulo IV" or "IV"
                         m_rom = re.search(r'\b([IVXLCDM]+)\b\.?', txt.upper())
                         if m_rom and len(txt) < 40:
                             # Simple Roman Check
                             try:
                                 # Convert to int to normalize (IX == 9, VIIII? no)
                                 # We just use string for matching if robust
                                 # Actually, convert to int is safer
                                 from roman_helper import roman_to_int
                                 r_val = roman_to_int(m_rom.group(1))
                                 r_key = f"ROM_{r_val}"
                                 if r_key not in en_nums: en_nums[r_key] = []
                                 en_nums[r_key].append(i)
                             except:
                                 pass
                              
                     print(f"DEBUG: {label} - EN figure numbers: {en_nums}")
                     
                     # 2. Find Matches in Spanish (Monotonic)
                     last_en_idx = -1
                      
                     # --- PRIMARY ANCHORS (Starts with Figure X) ---
                     for j, c in enumerate(es_filtered):
                         es_loop_txt = c['text'].strip()
                         # Safety:
                         if len(es_loop_txt) > 300 and c.get('type') != 'caption': continue
                         
                         # Check for Numbered List match ("1. ", "2. ")
                         found_num = None
                         m_list = re.match(r'^(\d+)\.\s+[A-Z]', es_loop_txt)
                         if m_list:
                             potential_num = "L" + m_list.group(1)
                             if potential_num in en_nums:
                                 found_num = potential_num
                                 
                         # Check for Roman Match
                         if not found_num and len(es_loop_txt) < 40:
                             m_rom = re.search(r'\b([IVXLCDM]+)\b\.?', es_loop_txt.upper())
                             if m_rom:
                                 try:
                                     from roman_helper import roman_to_int
                                     r_val = roman_to_int(m_rom.group(1))
                                     r_key = f"ROM_{r_val}"
                                     if r_key in en_nums:
                                         found_num = r_key
                                 except:
                                     pass
                         
                         # Check for Figure match
                         if not found_num:
                             m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)\s*([\d\.\-]+)', es_loop_txt, re.IGNORECASE)
                             if m:
                                 found_num = m.group(1).rstrip('.:,;- ')
                         
                         if found_num:
                             num = found_num
                             if num in en_nums:
                                 # Find first valid English match that preserves monotonicity
                                 candidates = en_nums[num]
                                 best_match = -1
                                 
                                 # --- HARD CONSTRAINTS ---
                                 for candidate in candidates:
                                     # Enforce strict Type matching for Captions to avoid Body<->Caption misalignment
                                     en_type = en_filtered[candidate].get('type')
                                     es_type = c.get('type')
                                     # Assuming 'caption' type is reliable. If not, maybe relax.
                                     # But En Parser sets 'caption' for figcaption matches.
                                     if es_type == 'caption' and en_type != 'caption': continue
                                     if es_type != 'caption' and en_type == 'caption': continue

                                     if candidate > last_en_idx:
                                         best_match = candidate
                                         break
                                 if best_match != -1:
                                     constraints.append((best_match, j, {'soft': False}))

                                     last_en_idx = best_match

                     # --- SECONDARY ANCHORS (References in Text) ---
                     # "as seen in Figure 22" <-> "como en la figura 22"
                     # This anchors the body text surrounding captions without numbers.
                     en_refs = {}
                     for i, c in enumerate(en_filtered):
                         # Skip Definition Chunks (Anchors)
                         if re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)\s*\d+', c['text'].strip(), re.IGNORECASE):
                             print(f"DEBUG: Skipping EN Ref Source (Definition): {c['text'][:30]}...")
                             continue
                         refs = re.findall(r'(?:figure|figura|map|mapa|fig\.?)\s*(\d+)', c['text'], re.IGNORECASE)
                         for r in refs:
                             if r not in en_refs: en_refs[r] = []
                             en_refs[r].append(i)
                              
                     es_refs = {}
                     for j, c in enumerate(es_filtered):
                         # Skip Definition Chunks (Anchors)
                         if re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)\s*\d+', c['text'].strip(), re.IGNORECASE):
                             print(f"DEBUG: Skipping ES Ref Source (Definition): {c['text'][:30]}...")
                             continue
                         refs = re.findall(r'(?:figure|figura|map|mapa|fig\.?)\s*(\d+)', c['text'], re.IGNORECASE)
                         for r in refs:
                             if r not in es_refs: es_refs[r] = []
                             es_refs[r].append(j)
                              
                     # Intersect References
                     common_refs = set(en_refs.keys()) & set(es_refs.keys())
                      
                     # Filter for Monotonicity? Reference constraints are looser.
                     # We can just add them all as soft constraints. DTW will ignore outliers.
                     # To avoid noise, ensure they are relatively unique?
                     # If "Figure 1" is mentioned 50 times, constraints will be messy.
                     # We restrict to cases where the reference count is low (e.g. <= 3).
                      
                     for num in common_refs:
                         e_idxs = en_refs[num]
                         s_idxs = es_refs[num]
                          
                         if len(e_idxs) <= 3 and len(s_idxs) <= 3:
                             # Cartesian product of likely matches
                             # (Usually 1 ref in En matches 1 ref in Es)
                             for e_i in e_idxs:
                                 for s_i in s_idxs:
                                      # Make constraint HARD when reference is unique (1:1 match)
                                      # This prevents DTW from misaligning paragraphs that discuss same figure
                                       is_unique = len(e_idxs) == 1 and len(s_idxs) == 1
                                       constraints.append((e_i, s_i, {'soft': not is_unique, 'allow_col_merge': True}))
                      
                     # --- HEADER-TO-HEADER CONSTRAINTS ---
                     # Prevent headers from being misaligned to content paragraphs
                     en_headers = [(i, c) for i, c in enumerate(en_filtered) if c.get('type') == 'header']
                     es_headers = [(i, c) for i, c in enumerate(es_filtered) if c.get('type') == 'header']
                      
                     if en_headers and es_headers:
                         # Embed headers for semantic matching
                         try:
                             en_hdr_texts = [{'text': c['text']} for _, c in en_headers]
                             es_hdr_texts = [{'text': c['text']} for _, c in es_headers]
                             en_hdr_embs = aligner.embed_chunks(en_hdr_texts)
                             es_hdr_embs = aligner.embed_chunks(es_hdr_texts)
                             
                             from scipy.spatial.distance import cosine
                             
                             # For each EN header, find best matching ES header
                             last_es_idx = -1
                             for en_pos, (en_idx, en_hdr) in enumerate(en_headers):
                                 best_es_idx = -1
                                 best_sim = 0.5  # Threshold for header match (lowered for cross-lingual)
                                 
                                 for es_pos, (es_idx, es_hdr) in enumerate(es_headers):
                                     if es_idx <= last_es_idx:  # Maintain monotonicity
                                         continue
                                     sim = 1 - cosine(en_hdr_embs[en_pos], es_hdr_embs[es_pos])
                                     if sim > best_sim:
                                         best_sim = sim
                                         best_es_idx = es_idx
                                 
                                 if best_es_idx >= 0:
                                     constraints.append((en_idx, best_es_idx, {'soft': False}))
                                     last_es_idx = best_es_idx
                                     print(f"  Header constraint: '{en_hdr['text'][:25]}...' -> ES idx {best_es_idx} (sim={best_sim:.2f})")
                         except Exception as e:
                             print(f"Header constraint generation failed: {e}")
                      
                     with open("/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks/constraints.log", "a") as f:
                         f.write(f"DEBUG: Ch Pair generated {len(constraints)} constraints (Start + Refs + Headers)\n")
                         for c in constraints: f.write(f"  {c}\n")

                 # Run Alignment on Filtered Sequences
                 # boost_constraints=True? No, manual weight modification in align_dtw.
                 # Wait, align_dtw logic processes 'soft'.
                 # I need to ensure align_dtw uses the weight.
                 # Let's verify neural_aligner.py handles 'soft' weight?
                 # It used fixed -2.0. I should verify/edit neural_aligner.py or just trust it.
                 # Actually I should viewing neural_aligner.py first.
                 
                 # --- POSITIONAL ALIGNMENT OPTIMIZATION ---
                 # When EN and ES have EQUAL chunk counts, use positional (1:1) alignment
                 # instead of DTW. This prevents misalignment in technical text where
                 # multiple paragraphs share similar vocabulary (e.g. "figure 38", "encoder").
                 use_positional = False
                 if len(en_filtered) == len(es_filtered) and len(en_filtered) > 0:
                     # Additional check: verify structural similarity using type fingerprints
                     # to ensure we're not falsely applying positional to mismatched structures
                     type_match = True
                     for i in range(len(en_filtered)):
                         en_type = en_filtered[i].get('type', 'std')
                         es_type = es_filtered[i].get('type', 'std')
                         # Allow std<->std and caption<->caption
                         if en_type != es_type:
                             type_match = False
                             break
                     if type_match:
                         use_positional = True
                         print(f"DEBUG: {label} - Using POSITIONAL alignment (equal counts: {len(en_filtered)})")
                 
                 if use_positional:
                     # Build blocks positionally: each en[i] matches es[i]
                     blocks = []
                     for i in range(len(en_filtered)):
                         blocks.append({
                             'en_indices': [i],
                             'es_indices': [i],
                             'en_chunks': [en_filtered[i]],
                             'es_chunks': [es_filtered[i]]
                         })
                 else:
                     blocks = aligner.align_dtw(en_filtered, es_filtered, constraints=constraints)
                 
                 # --- MERGE PASS ---
                 blocks = merge_bleeding_blocks(aligner, blocks)
                 
                 # Adapter: Convert Neural Blocks to Flat Pairs with DOM Nodes
                 aligned_pairs = []
                 for b in blocks:
                     ens = b['en_chunks']
                     ess = b['es_chunks']
                     
                     if not ens: continue # No anchor to inject into
                     
                     # 1:1 Mapping
                     if len(ens) == len(ess) and not b.get('force_distribution'):
                         for k in range(len(ens)):
                             if not ess[k]['text'].strip(): continue
                             aligned_pairs.append({
                                 'node': ens[k]['node'],
                                 'es': ess[k]['text'],
                                 'en': ens[k]['text'],
                                 'tag': ens[k]['tag'],
                                 'raw_html': ens[k].get('raw_html'),
                                 'classes': ens[k].get('classes', [])
                             })
                         continue
                     
                     # N:1 or N:M (where N > M) - Distribute Logic
                     if len(ens) >= len(ess):
                         joined_es = " ".join([c['text'] for c in ess])
                         
                         # Use our new distribution helper
                         distributed_es = distribute_spanish(aligner, ens, joined_es)
                         
                         for k, es_part in enumerate(distributed_es):
                             if not es_part.strip() and not ens[k]['text'].strip(): continue
                             aligned_pairs.append({
                                 'node': ens[k]['node'],
                                 'es': es_part,
                                 'en': ens[k]['text'],
                                 'tag': ens[k]['tag']
                             })
                         continue

                     # M > N Case: More Spanish chunks than English
                     # Instead of lumping, use semantic distribution to properly pair them
                     joined_es = " ".join([c['text'] for c in ess])
                     if not joined_es.strip(): continue
                     
                     # Use distribute_spanish to semantically match ES text to EN nodes
                     distributed_es = distribute_spanish(aligner, ens, joined_es)
                     
                     for k, es_part in enumerate(distributed_es):
                         if not es_part.strip() and not ens[k]['text'].strip(): continue
                         aligned_pairs.append({
                             'node': ens[k]['node'],
                             'es': es_part,
                             'en': ens[k]['text'],
                             'tag': ens[k]['tag'],
                             'raw_html': ens[k].get('raw_html'),
                             'classes': ens[k].get('classes', [])
                         })
             except Exception as e:
                 print(f"Neural alignment failed: {e}. Fallback to heuristic.")
                 aligned_pairs = align_chunks(en_chunks, es_chunks)
                 
             # --- RESCUE PASS: Handle Reordered Paragraphs ---
             # Detect English paragraphs with empty/missing translations and
             # search for semantic matches in unused Spanish chunks
             try:
                 # Collect used Spanish text (already assigned)
                 used_es_text = set()
                 orphaned_pairs = []
                 
                 for pair in aligned_pairs:
                     if pair.get('es') and pair['es'].strip():
                         used_es_text.add(pair['es'].strip()[:50])  # Use prefix as key
                     elif pair.get('en') and len(pair['en'].strip()) > 30:
                         # This EN paragraph has no translation - mark as orphaned
                         orphaned_pairs.append(pair)
                 
                 if orphaned_pairs and len(orphaned_pairs) <= 20:  # Don't rescue too many
                     print(f"DEBUG: {label} - Rescue pass: {len(orphaned_pairs)} orphaned EN paragraphs")
                     
                     # Build list of unused Spanish chunks
                     unused_es = []
                     for c in es_filtered:
                         txt = c.get('text', '').strip()
                         if txt and txt[:50] not in used_es_text and len(txt) > 30:
                             unused_es.append(c)
                     
                     if unused_es:
                         print(f"DEBUG: {label} - {len(unused_es)} unused ES chunks available for rescue")
                         
                         # Embed orphaned EN and unused ES
                         orphan_texts = [{'text': p['en']} for p in orphaned_pairs]
                         orphan_embs = aligner.embed_chunks(orphan_texts)
                         unused_embs = aligner.embed_chunks(unused_es)
                         
                         from scipy.spatial.distance import cosine
                         import numpy as np
                         
                         used_unused_indices = set()
                         
                         for i, pair in enumerate(orphaned_pairs):
                             best_j = -1
                             best_sim = 0.65  # Threshold for rescue match
                             
                             for j, es_chunk in enumerate(unused_es):
                                 if j in used_unused_indices:
                                     continue
                                 sim = 1 - cosine(orphan_embs[i], unused_embs[j])
                                 if sim > best_sim:
                                     best_sim = sim
                                     best_j = j
                             
                             if best_j >= 0:
                                 # Found a match - update the pair
                                 pair['es'] = unused_es[best_j]['text']
                                 used_unused_indices.add(best_j)
                                 print(f"  Rescued: '{pair['en'][:30]}...' -> '{pair['es'][:30]}...' (sim={best_sim:.2f})")
                         
                         print(f"DEBUG: {label} - Rescued {len(used_unused_indices)} orphaned paragraphs")
                         
             except Exception as e:
                 print(f"Rescue pass failed: {e}")
              
             # --- REDISTRIBUTION PASS: Handle Merged Paragraphs ---
             # When one ES paragraph contains translations for multiple EN paragraphs,
             # split ES into sentences and redistribute to consecutive orphaned EN paragraphs
             try:
                 # Find pairs where ES is abnormally long compared to EN
                 redistribution_needed = False
                 for i, pair in enumerate(aligned_pairs):
                     en_len = len(pair.get('en', '').strip())
                     es_len = len(pair.get('es', '').strip())
                     
                     # ES is 3x+ longer than EN suggests merged content
                     if en_len > 30 and es_len > en_len * 3:
                         # Check if next pairs are orphaned (no ES translation)
                         orphan_count = 0
                         for j in range(i + 1, min(i + 10, len(aligned_pairs))):
                             if not aligned_pairs[j].get('es', '').strip():
                                 orphan_count += 1
                             else:
                                 break
                         
                         if orphan_count >= 2:  # At least 2 consecutive orphans
                             redistribution_needed = True
                             print(f"DEBUG: {label} - Redistribution candidate at index {i}: ES ({es_len}) is {es_len/en_len:.1f}x longer than EN ({en_len}), {orphan_count} orphans follow")
                             
                             # Split ES into sentences
                             es_text = pair['es']
                             es_sentences = re.split(r'(?<=[.!?])\s+', es_text)
                             es_sentences = [s.strip() for s in es_sentences if s.strip()]
                             
                             if len(es_sentences) >= orphan_count + 1:
                                 # Collect EN paragraphs to redistribute to
                                 en_targets = [pair]  # Include current pair
                                 for j in range(i + 1, min(i + orphan_count + 1, len(aligned_pairs))):
                                     en_targets.append(aligned_pairs[j])
                                 
                                 # Embed EN paragraphs and ES sentences
                                 en_texts = [{'text': t.get('en', '')} for t in en_targets]
                                 es_sent_dicts = [{'text': s} for s in es_sentences]
                                 
                                 en_embs = aligner.embed_chunks(en_texts)
                                 es_embs = aligner.embed_chunks(es_sent_dicts)
                                 
                                 from scipy.spatial.distance import cosine
                                 
                                 # Greedy assignment: for each EN, find best matching consecutive ES sentences
                                 # Use monotonic matching to preserve order
                                 es_pointer = 0
                                 for k, target in enumerate(en_targets):
                                     if es_pointer >= len(es_sentences):
                                         break
                                     
                                     # Find how many ES sentences belong to this EN
                                     best_end = es_pointer + 1
                                     best_sim = 0
                                     
                                     for end in range(es_pointer + 1, min(es_pointer + 4, len(es_sentences) + 1)):
                                         combined = ' '.join(es_sentences[es_pointer:end])
                                         combined_emb = aligner.embed_chunks([{'text': combined}])[0]
                                         sim = 1 - cosine(en_embs[k], combined_emb)
                                         
                                         if sim > best_sim:
                                             best_sim = sim
                                             best_end = end
                                     
                                     # Assign to target
                                     assigned_text = ' '.join(es_sentences[es_pointer:best_end])
                                     target['es'] = assigned_text
                                     print(f"  Redistributed: '{target['en'][:25]}...' <- '{assigned_text[:25]}...' (sim={best_sim:.2f})")
                                     es_pointer = best_end
                             
                 if redistribution_needed:
                     print(f"DEBUG: {label} - Redistribution pass completed")
                     
             except Exception as e:
                 print(f"Redistribution pass failed: {e}")
                
             # --- SPLITTING LOGIC ---
             try:
                 # Local import removed to prevent UnboundLocalError
                 # Use global aligner for semantic splitting if available
                 splitter = Splitter(aligner=CACHED_ALIGNER, trigger_length=config.get('SPLIT_TRIGGER_CHARS', 240))
                 aligned_pairs = splitter.process_all(aligned_pairs)
             except Exception as e:
                 print(f"Splitting failed: {e}")

             # --- INJECTION ---
             # Group by node to handle splits (1 Node -> Multiple Pairs)
             perform_injection(aligned_pairs, config, soup)
             
        else:
             aligned_pairs = align_chunks(en_chunks, es_chunks)
             # --- INJECTION ---
             # Group by node to handle splits (1 Node -> Multiple Pairs)
             from itertools import groupby
             
             # We must preserve order, so we just iterate and group consecutive same-nodes?
             # No, aligned_pairs is ordered. Consecutive pairs with SAME node object = Split Node.
             
             def get_node_id(p): return id(p.get('node'))
             
             for node_id, group_iter in groupby(aligned_pairs, get_node_id):
                 group = list(group_iter)
                 if not group: continue
            
                 # Helper to get node safely
                 original_node = None
                 if 'node' in group[0]:
                     original_node = group[0]['node']
                
                 # If no node (e.g. from an 'insert' operation in alignment),
                 # we need to attach this to the PREVIOUS node if possible.
                 if original_node is None:
                     # We can't inject into nothing.
                     # Logic: append this text to the previous node's injection?
                     # For now, print warning and skip to avoid crash, OR try to find context.
                     # Better: In a sequential flow, if we have orphaned ES text, 
                     # we technically should append it to the previous pair's ES node.
                     # But 'group' is isolated.
                     # Let's Skip for safety but log it
                     # print(f"Warning: Orphaned Spanish text without anchor: {group[0].get('es', '')[:30]}...")
                     continue
                 
                 if not original_node: continue
                 
                 # Optimization: Single pair (Normal case)
                 if len(group) == 1:
                     p = group[0]
                     # Fallback implementation for injection
                     inject_translation(original_node, p['es'], config, soup)
                     # Update English text if changed (e.g. by splitter adding ⁂)
                     # Note: inner text replacement required
                     if p['en'] != original_node.get_text().strip():
                         original_node.string = p['en']
                     continue
                     
                 # Split Case: Multiple pairs for same source node
                 # We need to turn 1 Node into N Nodes (alternating En/Es)
                 last_node = original_node
                 
                 for i, p in enumerate(group):
                     en_text = p['en']
                     es_text = p['es']
                     
                     if i == 0:
                         # Reuse the original node for the first chunk
                         original_node.string = en_text
                         inject_translation(original_node, es_text, config, soup)
                         # inject_translation appends the Spanish node AFTER original_node.
                         # We need to find that injected node to update 'last_node'
                         # inject_translation returns nothing, but we know it inserts after.
                         # Let's inspect next sibling.
                         last_node = original_node.find_next_sibling() # This should be the span/p we just added
                     else:
                         # Create NEW English node clone
                         import copy
                         new_en_node = copy.copy(original_node) # Shallow copy might be enough tag structure
                         new_en_node.string = en_text
                         # Clear attributes that shouldn't be duplicated? IDs?
                         if new_en_node.has_attr('id'): del new_en_node['id']
                         
                         last_node.insert_after(new_en_node)
                         
                         inject_translation(new_en_node, es_text, config, soup)
                         last_node = new_en_node.find_next_sibling()
        
        

        
        with open(target_path, 'w', encoding='utf-8') as f:
             f.write(str(soup))

        
        # Collect images if any (extract from soup check?)
        # For now, we don't need to return images as we are preserving original structure
        # But if we did find new images (rare in this mode), we'd track them.
        return (idx, target_path, label, [])
        
    except Exception as e:
        print(f"Error processing chapter {label}: {e}")
        import traceback
        traceback.print_exc()
        return (idx, None, str(e), [])
                             
def create_bilingual_epub(en_base, es_base, output_epub_path, config=None, progress_callback=None, cancel_check=None):
    # Use a staging directory relative to the output path (job-specific)
    # staging dir = output_dir / bilingual_epub_staging
    out_dir = os.path.dirname(os.path.abspath(output_epub_path))
    staging_dir = os.path.join(out_dir, 'bilingual_epub_staging')
    
    try:
        return _process_epub_generation(en_base, es_base, output_epub_path, staging_dir, config, progress_callback, cancel_check)
    except Exception as e:
        print(f"Error during EPUB generation: {e}")
        raise
    finally:
        if os.path.exists(staging_dir):
            print(f"Cleaning up staging directory: {staging_dir}")
            shutil.rmtree(staging_dir)

def _process_epub_generation(en_base, es_base, output_epub_path, staging_dir, config=None, progress_callback=None, cancel_check=None):
    """
    Refactored Logic: EXACT COPY Strategy.
    1. Copy entire En directory to staging.
    2. Modify metadata in place (Title).
    3. Modify chapters in place (Inject translation).
    """
    
    # 1. Copy Entire Structure
    print(f"--- Starting Fresh Execution for {os.path.basename(output_epub_path)} ---")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
        
    print(f"Copying original structure from {en_base} to {staging_dir}...")
    shutil.copytree(en_base, staging_dir)
    
    # 2. Identify TOC and Pairs
    # We still need to align the structure to know what to inject where.
    # Paths in 'pairs' are relative to the *root* of the unpacked dir (en_base).
    
    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
    if not en_toc_path or not es_toc_path:
        raise FileNotFoundError("TOC file not found in one of the EPUBs.")

    en_toc = parse_toc(en_toc_path)
    es_toc = parse_toc(es_toc_path)
    pairs = align_tocs(en_toc, es_toc)
    print(f"Identified {len(pairs)} chapters to align.")
    
    # Fallback: Detect if TOC alignment failed (most EN chapters have no ES match)
    if pairs:
        unmatched_count = sum(1 for item in pairs if len(item) >= 3 and item[1] and not item[2])
        total_en = sum(1 for item in pairs if len(item) >= 2 and item[1])
        
        if total_en > 0 and (unmatched_count / total_en) > 0.7:
            print(f"WARNING: TOC alignment poor ({unmatched_count}/{total_en} unmatched, {100*unmatched_count/total_en:.0f}%). Falling back to spine-based alignment.")
            pairs = align_by_spine(en_base, es_base, en_toc_path, es_toc_path)
            print(f"Spine-based fallback found {len(pairs)} chapter pairs.")

    if not pairs:
        raise ValueError("No aligned chapters found.")

    # 1b. Load Profile / Config
    # We default to 'generic' which has standard settings for 'en' and 'es'
    # Use output filename for detection since input path might be temp
    detected_profile = detect_profile(output_epub_path)
    print(f"Using profile: {detected_profile}")
    
    defaults = PROFILES.get(detected_profile, PROFILES['generic'])
    if config is None: config = {}
    
    # Merge defaults into config (preserving existing keys like 'use_neural')
    for k, v in defaults.items():
        if k not in config:
            config[k] = v
        elif isinstance(v, dict) and isinstance(config[k], dict):
             for sk, sv in v.items():
                 if sk not in config[k]:
                     config[k][sk] = sv

    # 3. Update Metadata (Title) in Staging OPF
    # We need to find the OPF in the staging directory
    staging_opf_path = find_opf_file(staging_dir)
    if not staging_opf_path:
        # Should exist since we copied it
        raise FileNotFoundError("OPF file missing in staging directory.")
        
    # Simple modification of the OPF to append "(bilingual)" to title
    new_title = "Unknown" # Default in case of error
    try:
        with open(staging_opf_path, 'r', encoding='utf-8') as f:
            opf_content = f.read()
            
        opf_soup = BeautifulSoup(opf_content, 'xml')
        # Standard OPF namespaces
        dc_title = opf_soup.find('dc:title') or opf_soup.find('title')
        if dc_title:
            original_title = dc_title.get_text()
            new_title = f"{original_title} (bilingual)"
            dc_title.string = new_title
            
            save_cleaned_opf(opf_soup, staging_opf_path)
            print(f"Updated metadata title: {new_title}")
    except Exception as e:
        print(f"Warning: Could not update OPF metadata: {e}")

    # 4. Process Chapters (In-Place)
    # Prepare arguments. 
    # en_rel is relative to en_base. We need absolute path in staging.
    
    # Define required path variables at the top of the block
    en_toc_dir = os.path.dirname(en_toc_path)
    es_toc_dir = os.path.dirname(es_toc_path)
    es_opf_dir = None # Unused in new logic but required for args tuple
    
    # =========================================================================
    # REFACTOR: SPINE EXPANSION for Split Chapters
    # =========================================================================
    # Problem: TOC only points to 'chapter001_split_000.xhtml'. 
    # Actual text is often in 'chapter001_split_001.xhtml' etc.
    # Logic: 
    # 1. Read the English OPF (from staging) to get the Spine order.
    # 2. Iterate the Spine. 
    # 3. If a spine item is in 'pairs' (from TOC), lock "current_spanish_src".
    # 4. If a spine item is NOT in 'pairs' but "follows" the matched chapter (same prefix?), use "current_spanish_src".
    
    # helper to normalize paths for comparison
    def norm_p(p): return os.path.normpath(str(p))
    
    # 1. Parse Spine from Staging OPF
    # staging_opf_path is already known
    try:
        epub_root = os.path.dirname(staging_opf_path) # Absolute path to OPS/OEBPS
        
        with open(staging_opf_path, 'r', encoding='utf-8') as f:
             # Use a robust parser for OPF
             soup_opf = BeautifulSoup(f.read(), 'xml')
             
        # Map Manifest ID -> Href
        manifest = {}
        for item in soup_opf.find_all('item'):
            manifest[item.get('id')] = item.get('href')
            
        # Get Spine Order (list of hrefs)
        spine_refs = []
        for itemref in soup_opf.find_all('itemref'):
            idref = itemref.get('idref')
            if idref in manifest:
                href = manifest[idref]
                # Resolve href to absolute path within staging
                # Manifest hrefs are relative to OPF file
                abs_path = os.path.normpath(os.path.join(epub_root, href))
                spine_refs.append(abs_path)
                
        print(f"Parsed {len(spine_refs)} items in Spine for expansion.")
        
        # 2. Build Lookup from TOC Pairs
        # Map: AbsPath -> (label, es_src, level)
        toc_lookup = {}
        
        # We need to resolve 'en_rel' from pairs to absolute paths too
        en_toc_dir = os.path.dirname(en_toc_path) # Original EN TOC dir
        # Be careful: 'en_rel' in pairs comes from 'en_toc' which is from 'en_base'.
        # We need to map it to 'staging_dir'.
        # Structure of staging = structure of en_base.
        
        # Calculate 'staging_toc_dir' 
        rel_toc_from_base = os.path.relpath(en_toc_dir, en_base)
        staging_toc_dir = os.path.join(staging_dir, rel_toc_from_base)
        
        processed_pairs = []
        
        for idx, (label, en_rel, es_rel, level) in enumerate(pairs):
             if not en_rel: continue
             # Resolve en_rel against STAGING TOC DIR
             if not os.path.isabs(en_rel):
                 s_abs = os.path.normpath(os.path.join(staging_toc_dir, en_rel))
             else:
                 s_abs = en_rel # Should not happen given logic, but safety
                 
             toc_lookup[s_abs] = (label, es_rel, level, idx)
             
        # 3. Propagate Matches via Spine
        final_processing_list = []
        current_es_match = None
        current_label = None
        
        for spine_abs in spine_refs:
            # Is this spine item in our TOC pairs?
            if spine_abs in toc_lookup:
                # Yes! Switch to this new chapter.
                label, es_rel, level, idx = toc_lookup[spine_abs]
                current_es_match = es_rel
                current_label = label
                
                # Add it
                final_processing_list.append( (idx, label, spine_abs, es_rel, level) )
                # print(f"DEBUG: Spine Matched TOC: {os.path.basename(spine_abs)} -> {es_rel}")
            
            elif current_es_match:
                # It's a follower file (e.g. split_001).
                # Heuristic: verify filename prefix similarity to avoid carrying over to unrelated files (like 'copyright')?
                # Actually, Spine is ordered. If 'copyright' is next, it usually has its own TOC entry.
                # If it DOESN'T have a TOC entry, maybe it belongs to the previous chapter?
                # Let's rely on the user's report: Prologue had splits and worked.
                # Let's assume Spine propagation is safe until we hit next TOC item.
                # Wait, 'copyright.xhtml' might NOT be in TOC but shouldn't inherit 'Chapter 78'.
                # Strict check: Filename must look like a split? 
                # e.g. 'chapter001_split_000' -> 'chapter001_split_001'.
                # Or simply: assume standard flow.
                
                # SKIP ATTRIBUTION/METADATA PAGES
                # These have almost no real content and shouldn't steal Spanish translations
                fname = os.path.basename(spine_abs).lower()
                skip_patterns = ['w2e', 'writer2epub', 'copyright', 'colophon', 'aboutthebook', 
                                'abouttheauthor', 'dedication', 'frontmatter', 'backmatter']
                is_skip_page = any(pat in fname for pat in skip_patterns)
                
                if is_skip_page:
                    print(f"DEBUG: Skipping attribution/metadata page: {fname}")
                    continue  # Don't create (cont.) for these
                
                # Let's use it.
                # Use '-1' for index to indicate it's an extension
                final_processing_list.append( (9999, f"{current_label} (cont.)", spine_abs, current_es_match, 0) )
                # print(f"DEBUG: Spine Expanded: {os.path.basename(spine_abs)} -> {current_es_match}")
                
        print(f"Expanded processing list from {len(pairs)} to {len(final_processing_list)} terms.")
        
        # Override args_list preparation loop
        args_list = []
        
        # We need es_toc_dir to resolve es_rel
        es_toc_dir = os.path.dirname(es_toc_path)
        
        # CRITICAL: Detect Shared Spanish Files and calculate PROPORTIONAL splits
        # Build mapping: es_abs -> [(idx, en_abs, label), ...]
        print(f"DEBUG: Building ES file usage map from {len(final_processing_list)} items")
        es_file_usage = {}
        for idx, label, en_abs, es_rel, level in final_processing_list:
            if not es_rel: continue
            
            if not os.path.isabs(es_rel):
                es_abs = os.path.normpath(os.path.join(es_toc_dir, es_rel))
            else:
                es_abs = es_rel
            
            if es_abs not in es_file_usage:
                es_file_usage[es_abs] = []
            es_file_usage[es_abs].append((idx, en_abs, label))
        
        print(f"DEBUG: Found {len(es_file_usage)} unique ES files")
        for es_path, en_refs in es_file_usage.items():
            print(f"DEBUG:   {os.path.basename(es_path)}: {len(en_refs)} EN references")
        
        # Filter to only multi-reference files
        shared_es_files = {k: v for k, v in es_file_usage.items() if len(v) > 1}
        print(f"DEBUG: After filtering, {len(shared_es_files)} are shared (multiple references)")
        
        if shared_es_files:
            print(f"Detected {len(shared_es_files)} shared Spanish files used by multiple English chapters")
            
            # For each shared file, find SEMANTIC split points
            for es_abs, en_list in shared_es_files.items():
                labels = [label for _, _, label in en_list]
                print(f"  {os.path.basename(es_abs)} -> {labels}")
                
                # Parse Spanish file ONCE to get all chunks
                try:
                    print(f"    Attempting to parse shared ES file: {es_abs}")
                    es_chunks_all = parse_file(es_abs, SpanishParser, config)
                    print(f"    Successfully parsed {len(es_chunks_all)} total ES chunks in shared file")
                except Exception as e:
                    print(f"    ERROR parsing shared file {os.path.basename(es_abs)}: {e}")
                    import traceback
                    traceback.print_exc()
                    print(f"    Falling back to equal split")
                    # Fallback to equal proportions
                    total_refs = len(en_list)
                    proportions = [1.0 / total_refs] * total_refs
                    shared_es_files[es_abs] = (en_list, proportions, None)
                    continue
                
                # Find split points by matching first paragraphs
                split_indices = [0]  # First chapter starts at index 0
                
                for i in range(1, len(en_list)):
                    idx_en, en_abs, label_en = en_list[i]
                    
                    # Extract first paragraph from this English chapter
                    try:
                        with open(en_abs, 'r', encoding='utf-8') as f:
                            soup = BeautifulSoup(f.read(), 'lxml')
                        en_chunks_temp = extract_nodes(soup)
                        
                        if not en_chunks_temp:
                            print(f"    {label_en}: No EN chunks found, using proportional fallback")
                            split_indices.append(int(i * len(es_chunks_all) / len(en_list)))
                            continue
                        
                        # FIX: If this English file is tiny (e.g., Part title page),
                        # don't let it steal content from the previous chapter.
                        # Skip adding a split point - the part title detection logic
                        # in process_chapter_pair will handle filtering it to headers only.
                        en_chunk_count = len([c for c in en_chunks_temp if c.get('type') != 'image'])
                        if en_chunk_count <= 5:
                            # Tiny file - give it the last chunk only (for fallback)
                            # The Part Title detection in process_chapter_pair will filter properly
                            split_idx = len(es_chunks_all)  # Point to end, giving it nothing
                            split_indices.append(split_idx)
                            print(f"    {label_en}: Tiny file ({en_chunk_count} chunks), skipping (split at end: {split_idx})")
                            continue
                        
                        # Get first meaningful paragraph (skip headers)
                        first_para = None
                        for chunk in en_chunks_temp[:5]:  # Check first 5 chunks
                            if chunk.get('type') == 'std' and len(chunk.get('text', '').strip()) > 20:
                                first_para = chunk['text'].strip()
                                break
                        
                        if not first_para:
                            print(f"    {label_en}: No meaningful first paragraph, using proportional fallback")
                            split_indices.append(int(i * len(es_chunks_all) / len(en_list)))
                            continue
                        
                        # Find best matching Spanish chunk using simple text matching
                        # (Semantic embeddings would be better but this is faster and simpler)
                        best_match_idx = 0
                        best_score = 0
                        
                        # Search starting from previous split point
                        search_start = split_indices[-1]
                        for j in range(search_start, min(search_start + 200, len(es_chunks_all))):
                            es_text = es_chunks_all[j].get('text', '').strip()
                            if len(es_text) < 20:
                                continue
                            
                            # Simple similarity: check if first words match
                            en_words = first_para.lower().split()[:10]
                            es_words = es_text.lower().split()[:10]
                            
                            # Count matching words (simple heuristic)
                            matches = sum(1 for w in en_words if w in es_words)
                            score = matches / len(en_words) if en_words else 0
                            
                            if score > best_score:
                                best_score = score
                                best_match_idx = j
                        
                        
                        # Check if semantic matching succeeded
                        # If match score is too low, fall back to proportional distribution
                        SCORE_THRESHOLD = 0.1  # Require at least 10% word overlap
                        
                        if best_score >= SCORE_THRESHOLD and best_match_idx > split_indices[-1]:
                            # Good semantic match found, use it
                            split_indices.append(best_match_idx)
                            print(f"    {label_en}: Split point at chunk {best_match_idx} (semantic, score: {best_score:.2f})")
                        else:
                            # Poor match or non-monotonic, fall back to proportional
                            proportional_idx = int(i * len(es_chunks_all) / len(en_list))
                            # Ensure monotonic increase
                            proportional_idx = max(proportional_idx, split_indices[-1] + 1)
                            split_indices.append(proportional_idx)
                            print(f"    {label_en}: Split point at chunk {proportional_idx} (proportional, semantic score was {best_score:.2f})")
                        
                        
                    except Exception as e:
                        print(f"    {label_en}: Error finding split point: {e}, using proportional fallback")
                        split_indices.append(int(i * len(es_chunks_all) / len(en_list)))
                
                # Convert split indices to chunk ranges
                chunk_ranges_list = []
                for i in range(len(en_list)):
                    start = split_indices[i]
                    end = split_indices[i+1] if i+1 < len(split_indices) else len(es_chunks_all)
                    chunk_ranges_list.append((start, end))
                    print(f"    {en_list[i][2]}: chunks {start}-{end} ({end-start} chunks)")
                
                # Store ranges for this shared file
                shared_es_files[es_abs] = (en_list, None, chunk_ranges_list)
        
        # Build args_list with semantic chunk range info
        for idx, label, en_abs, es_rel, level in final_processing_list:
            if not es_rel: continue
            
            if not os.path.isabs(es_rel):
                es_abs = os.path.normpath(os.path.join(es_toc_dir, es_rel))
            else:
                es_abs = es_rel
            
            # Check if this ES file is shared (has semantic split points)
            chunk_range = None
            if es_abs in shared_es_files:
                en_list, proportions_unused, chunk_ranges_list = shared_es_files[es_abs]
                
                if chunk_ranges_list:  # Semantic splitting worked
                    # Find this entry's position in the list
                    position = next(i for i, (_, e, _) in enumerate(en_list) if e == en_abs)
                    start, end = chunk_ranges_list[position]
                    chunk_range = (start, end)
                    print(f"  {label}: Will use chunks {start}-{end} of shared file {os.path.basename(es_abs)}")
                elif proportions_unused:  # Fallback to proportions
                    position = next(i for i, (_, e, _) in enumerate(en_list) if e == en_abs)
                    chunk_range = (position, proportions_unused)
                    print(f"  {label}: Will use {proportions_unused[position]*100:.1f}% of shared file {os.path.basename(es_abs)}")
            
            args_list.append( (idx, en_abs, es_abs, es_opf_dir, config, label, chunk_range) )
            
        # Replaces the original loop below
        
    except Exception as e:
        print(f"CRITICAL ERROR in Spine Expansion: {e}. Fallback to TOC only.")
        import traceback
        traceback.print_exc()
        # args_list will be empty, triggering fallback below
        args_list = []

    if not args_list: 
         # Fallback loop if args_list wasn't populated (e.g. error above handled silently?)
         # Or if spine was empty.
         # Re-implement basic loop here or structure code to allow fallback?
         # Simplest: check "src" loop
         
         en_toc_dir = os.path.dirname(en_toc_path)
         args_list = []
         for idx, (label, en_rel, es_rel, level) in enumerate(pairs):
            if not en_rel: continue
            if not os.path.isabs(en_rel):
                en_abs = os.path.normpath(os.path.join(en_toc_dir, en_rel))
            else:
                en_abs = en_rel
                
            if not es_rel: continue
            es_abs = os.path.normpath(os.path.join(es_toc_dir, es_rel))
            
            args_list.append( (idx, en_abs, es_abs, es_opf_dir, config, label) )

    # 4. Process Chapters (In-Place)
    
    # We already built args_list.
    # Just need to skip the original loop declaration.
    
    # ...
    
    # 5. Process Chapters (ProcessPool)
    # args_list is now ready from Spine Expansion
    
    print(f"Executing {len(args_list)} content tasks...")

    # Parallel Processing
    max_workers = 1 if config and config.get('use_neural') else None
    pool = multiprocessing.Pool(processes=max_workers)
    
    # We don't need to collect results for manifest/spine/images here,
    # as we are modifying in place and the original EPUB structure is preserved.
    # However, process_chapter_pair still returns images, which might be useful for manifest updates.
    all_collected_images = set()
    
    try:
        count_done = 0
        total = len(args_list)
        
        async_results = [pool.apply_async(process_chapter_pair, (args,)) for args in args_list]

        completed_indices = set()
        while len(completed_indices) < len(async_results):
            if cancel_check and cancel_check():
                pool.terminate()
                raise InterruptedError("Cancelled")
                
            for i, res in enumerate(async_results):
                if i not in completed_indices and res.ready():
                    try:
                        res_idx, res_filename, res_label, res_images = res.get() # Get results to collect images
                        if res_images:
                            all_collected_images.update(res_images)
                    except Exception as exc:
                        print(f"Task {i} failed: {exc}")
                    completed_indices.add(i)
                    count_done += 1
                    
                    if progress_callback:
                        progress_callback(count_done, total, f"Processed {count_done}/{total}")
            
            time.sleep(0.1)
            
        pool.close()
        pool.join()
        
    except Exception as e:
        pool.terminate()
        raise e
        
    print("Alignment/Injection Complete.")
    
    # 5. Update OPF Manifest with new images
    # This step is crucial because new images might have been copied to OEBPS/images
    # and need to be declared in the manifest.
    try:
        with open(staging_opf_path, 'r', encoding='utf-8') as f:
            opf_content = f.read()
        opf_soup = BeautifulSoup(opf_content, 'xml')
        manifest = opf_soup.find('manifest')
        if manifest:
            for img_fname, img_mime in all_collected_images:
                item_id = f"img-{img_fname.replace('.', '-')}"
                # Check if item already exists to avoid duplicates
                if not opf_soup.find('item', id=item_id):
                    new_item = opf_soup.new_tag('item', id=item_id, href=f"images/{img_fname}", media_type=img_mime)
                    manifest.append(new_item)
            
            save_cleaned_opf(opf_soup, staging_opf_path)
            print(f"Updated OPF manifest with {len(all_collected_images)} new image entries.")
    except Exception as e:
        print(f"Warning: Could not update OPF manifest with new images: {e}")

    # Return metadata for filename generation
    # The original metadata extraction is gone, so we return a simplified dict.
    # We could re-parse the OPF for more complete metadata if needed.
    
    # 9. Zip it
    print(f"Success! Bilingual EPUB created at: {output_epub_path}")
    
    # Ensure directory exists for output
    out_dir = os.path.dirname(output_epub_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    # Ensure mimetype exists
    mimetype_path = os.path.join(staging_dir, 'mimetype')
    if not os.path.exists(mimetype_path):
        with open(mimetype_path, 'w', encoding='utf-8') as f:
            f.write("application/epub+zip")

    # Ensure META-INF/container.xml exists
    meta_inf_dir = os.path.join(staging_dir, 'META-INF')
    os.makedirs(meta_inf_dir, exist_ok=True)
    container_xml_path = os.path.join(meta_inf_dir, 'container.xml')
    
    if not os.path.exists(container_xml_path):
        # Calculate relative path to OPF
        opf_rel_path = os.path.relpath(staging_opf_path, staging_dir).replace('\\', '/')
        
        container_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="{opf_rel_path}" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        
        with open(container_xml_path, 'w', encoding='utf-8') as f:
            f.write(container_content)
        print(f"Generated missing META-INF/container.xml pointing to {opf_rel_path}")
    
    # Debug: List staging contents to ensure assets are present
    total_files = 0
    assets_found = 0
    for root, dirs, files in os.walk(staging_dir):
        total_files += len(files)
        for f in files:
            if f.lower().endswith(('.jpg', '.jpeg', '.png', '.otf', '.ttf', '.css')):
                assets_found += 1
    print(f"Zipping {total_files} files (including {assets_found} assets/styles) from staging...")

    with zipfile.ZipFile(output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(mimetype_path, 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                if file == 'mimetype': continue
                file_path = os.path.join(root, file)
                # Archive name must be relative to staging_dir to be at root of EPUB
                arc_name = os.path.relpath(file_path, staging_dir)
                zipf.write(file_path, arc_name)
    
    print("Alignment/Generation Complete.")
    
    return {'title': new_title, 'language': 'bilingual'}
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a bilingual EPUB from extracted English and Spanish EPUB OEBPS directories.")
    parser.add_argument("--en", required=False, default='temp_bilingual/en_full/OEBPS', help="Path to English OEBPS directory")
    parser.add_argument("--es", required=False, default='temp_bilingual/es_full/OEBPS', help="Path to Spanish OEBPS directory")
    parser.add_argument("--output", required=False, default='bilingual_book.epub', help="Output EPUB filename")
    parser.add_argument("--local-ai", action='store_true', help="Use local neural alignment (LaBSE)")
    
    parser.add_argument('--split-length', type=int, default=280, help='Character threshold to trigger paragraph splitting (default: 280)')
    
    # Bilingual layout and styling options
    parser.add_argument('--layout-mode', type=str, default='below',
                       choices=['below', 'above', 'side', 'only'],
                       help='Translation layout mode: below (default), above, side (side-by-side), only (Spanish only)')
    parser.add_argument('--style-mode', type=str, default='class',
                       choices=['class', 'inline', 'hybrid'],
                       help='Styling approach: class (CSS classes), inline (inline styles), hybrid (both)')
    parser.add_argument('--column-gap', type=int, default=10,
                       help='Column gap percentage for side-by-side layout (5-30, default: 10)')
    parser.add_argument('--left-column', type=str, default='english',
                       choices=['english', 'spanish'],
                       help='Language for left column in side-by-side mode (default: english)')
    parser.add_argument('--original-color', type=str, default=None,
                       help='Color for original English text (e.g., #000000 or black)')
    parser.add_argument('--translation-color', type=str, default=None,
                       help='Color for Spanish translation (e.g., #555555 or grey)')
    parser.add_argument('--preset', type=str, default=None,
                       choices=['default', 'side_by_side', 'color_coded', 'spanish_first', 'spanish_only', 'learner_mode'],
                       help='Use a preset configuration (overrides individual settings)')
    
    args = parser.parse_args()

    # Import bilingual configuration
    from bilingual_config import BilingualConfig, LayoutMode, StyleMode, get_preset
    
    # Create bilingual config from args or preset
    if args.preset:
        bilingual_config = get_preset(args.preset)
        print(f"Using preset: {args.preset}")
    else:
        bilingual_config = BilingualConfig(
            layout_mode=LayoutMode.from_string(args.layout_mode),
            column_gap_percentage=args.column_gap,
            left_column_language=args.left_column,
            style_mode=StyleMode[args.style_mode.upper()],
            original_color=args.original_color,
            translation_color=args.translation_color,
        )
    
    # Validate configuration
    try:
        bilingual_config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Pass config
    config = {
        'use_neural': args.local_ai,
        'split_length': args.split_length,
        'bilingual': bilingual_config,
    }
    
    if args.local_ai:
        print("Using Local Neural Alignment (LaBSE)...")
    
    print(f"\nLayout configuration:")
    print(f"  Mode: {bilingual_config.layout_mode.value}")
    if bilingual_config.layout_mode == LayoutMode.SIDE_BY_SIDE:
        print(f"  Side-by-side: {bilingual_config.left_column_language} on left, {bilingual_config.column_gap_percentage}% gap")
    print(f"  Style: {bilingual_config.style_mode.value}")
    if bilingual_config.original_color:
        print(f"  English color: {bilingual_config.original_color}")
    if bilingual_config.translation_color:
        print(f"  Spanish color: {bilingual_config.translation_color}")
    
    create_bilingual_epub(args.en, args.es, args.output, config)
