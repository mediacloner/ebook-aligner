import argparse
import sys
import os
import re
import html
import difflib
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import zipfile
import shutil
import uuid
from datetime import datetime

# ----------------------------------------------------------------------------- 
# Configuration
# -----------------------------------------------------------------------------
SPLIT_TRIGGER_CHARS = 240  # Characters
SPLIT_TOLERANCE = 0.20     # 20% +/- deviation allowed

# Default configuration for "Artificial Intelligence" book
# Configuration Profiles
PROFILES = {
    'melanie': {
        'en': {
            'header_tags': ['h1', 'h2'],
            'header_classes': ['CN', 'CN-Only', 'CT'], 
            'caption_start_tags': ['figcaption'],
            'caption_classes': [],
            'ignore_tags': [],
            'ignore_classes': [],
            'SPLIT_TRIGGER_CHARS': 240
        },
        'es': {
            'header_tags': ['p', 'div'],
            'header_indicators': [
                'Capitulos_Capitulo_Numero', 
                'Capitulos_Capitulo_1_Linea', 
                'Subcapitulos_subcapitulo', 
                'Subcapitulos_Subcapitulo'
            ],
            'caption_classes': ['Basico_pie_foto', 'Basico_pie_foto_centrado'],
            'ignore_tags': ['h1'], # Ignore original H1s as typically book title in header
            'ignore_classes': ['_idFootnotes', 'centradoespacioantes', 'capitulo'],

            'merge_headers': True, # Merge logic for split titles
            'header_merge_trigger': 'Capitulos_Capitulo_1_Linea',
            'header_merge_targets': ['Capitulos_Capitulo_Numero', 'Capitulos_Capitulo_1_Linea', 'capitulo']
        }
    },
    'generic': {
        'en': {
            'header_tags': ['h1', 'h2', 'h3'],
            'header_classes': [], # Any allowed tag is header if no classes specified
            'caption_start_tags': ['figcaption'],
            'caption_classes': ['caption'],
            'ignore_tags': [],
            'ignore_classes': [],
            'SPLIT_TRIGGER_CHARS': 300
        },
        'es': {
            'header_tags': ['h1', 'h2', 'h3'],
            'header_indicators': [],
            'caption_classes': ['caption'],
            'ignore_tags': [],
            'ignore_classes': [],
            'merge_headers': False
        }
    }
}

def detect_profile(file_path):
    """Detects likely profile based on content signatures."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(10000) # Read first 10KB
            
        # Signatures for Melanie Mitchell book
        if 'class="CN"' in sample or 'class="Capitulos_Capitulo' in sample or 'class="block_21"' in sample:
             # Added block_21 as slight heuristic for that specific es file if needed, 
             # but sticking to strict class names is safer.
             if 'class="CN"' in sample or 'Capitulos_' in sample:
                 print(f"Auto-detection: Matched 'melanie' profile for {os.path.basename(file_path)}")
                 return 'melanie'
        
        print(f"Auto-detection: Using 'generic' profile for {os.path.basename(file_path)}")
        return 'generic'
    except Exception as e:
        print(f"Auto-detection failed ({e}), defaulting to generic.")
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
                clean = html.unescape(clean)
                if not clean: continue
                
                count += 1
                if count > 10: break 
                
                if len(clean) > 80: continue
                
                norm = clean.lower().replace('í', 'i').replace('á', 'a').replace('é', 'e').replace('ó', 'o').replace('ú', 'u')
                
                if 'capitulo' in norm or 'parte' in norm or 'prologo' in norm or 'epilogo' in norm or 'chapter' in norm:
                     return clean
                
                if any(c.isdigit() for c in clean) and len(clean) < 30:
                     return clean

    except Exception as e:
        print(f"Error sniffing title from {file_path}: {e}")
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

    base_dir = os.path.dirname(ncx_path)
    nav_points = []
    
    # Find all navPoints recursively (flattened)
    for nav_point in root.findall('.//ncx:navPoint', ns):
        label = find_text(nav_point, './ncx:navLabel/ncx:text')
        content_node = nav_point.find('./ncx:content', ns)
        content = content_node.get('src') if content_node is not None else ""
        
        # Fallback: Sniff content if label is empty
        if not label and content:
            # Construct absolute path to sniff
            # content might be relative to ncx
            # e.g. src="Text/ch01.html"
            try:
                # Remove anchor for file path
                file_part = content.split('#')[0]
                full_path = os.path.join(base_dir, file_part)
                if os.path.exists(full_path):
                    label = extract_title_from_html(full_path)
                    print(f"Sniffed label for {content}: '{label}'")
            except Exception as e:
                print(f"Failed to sniff {content}: {e}")

        # Final cleanup
        if '#' in content:
            content = content.split('#')[0]
            
        nav_points.append({'label': label.strip(), 'src': content})
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

def normalize_label(label):
    label = label.lower().strip()
    
    if 'prologue' in label or 'pólogo' in label or 'prologo' in label: return 'prologue'
    if 'epilogue' in label or 'epílogo' in label or 'epilogo' in label: return 'epilogue'
    
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
    """Aligns chapters based on normalized labels (Structure Matching)."""
    pairs = []
    
    # Pre-process lists
    en_list = [{'idx': i, 'item': item, 'norm': normalize_label(item['label'])} for i, item in enumerate(en_toc)]
    es_list = [{'idx': i, 'item': item, 'norm': normalize_label(item['label'])} for i, item in enumerate(es_toc)]
    
    es_used = set()
    
    for en_row in en_list:
        match_found = None
        
        # 1. Structural Match
        if isinstance(en_row['norm'], tuple):
            for es_row in es_list:
                if es_row['idx'] in es_used: continue
                if es_row['norm'] == en_row['norm']:
                    match_found = es_row
                    break
                    
        # 2. String Match 
        if not match_found and isinstance(en_row['norm'], str):
             for es_row in es_list:
                if es_row['idx'] in es_used: continue
                if es_row['norm'] == en_row['norm']: 
                    match_found = es_row
                    break

        if match_found:
            pairs.append((en_row['item']['src'], match_found['item']['src']))
            es_used.add(match_found['idx'])
            
    return pairs

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def split_sentences(text):
    """Splits text into sentences using simple heuristics to avoid granularity mismatch."""
    # Lookbehind for punctuation [.!?], spaces, lookahead for Capital letter or Inverted Punctuation.
    # Also include quotes/dashes as potential sentence starters.
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z¿¡"\'\-])', text)
    return [p.strip() for p in parts if p.strip()]

def split_sentences_aggressive(text):
    """Splits text more aggressively for alignment mismatches (e.g. compound sentences)."""
    # Standard split first
    base_parts = split_sentences(text)
    final_parts = []
    for p in base_parts:
        # Split on semicolons or ", y " (common Spanish compound connector)
        # Regex: Lookbehind for ; or , space, Lookahead for y space or start of sentence or pero/sin embargo
        # Simplified: Split on '; ' and ', y '
        sub = re.split(r'(?:;|(?<=,)\s+(?=[yY]\s))', p)
        final_parts.extend([s.strip() for s in sub if s.strip()])
    return final_parts

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
    """
    data = {
        'title': "Bilingual Edition",
        'language': "en",
        'creator': "Unknown",
        'uid': "urn:uuid:12345",
        'uid_scheme': "BookId",
        'cover_id': None,
        'metadata_items': [], # List of objects to reconstruct strings
        'manifest': {}
    }

    if not opf_path or not os.path.exists(opf_path):
        return data

    try:
        tree = ET.parse(opf_path)
        root = tree.getroot()
        
        # Namespaces
        ns = {
            'opf': 'http://www.idpf.org/2007/opf',
            'dc': 'http://purl.org/dc/elements/1.1/'
        }
        
        # 1. Metadata
        metadata_node = root.find('opf:metadata', ns)
        if metadata_node is not None:
            # Capture all dc:* children
            for child in metadata_node:
                # Naive namespace check
                tag = child.tag
                # Remove namespace uri from tag for cleaner handling if needed, or keep it
                # We will store the full tag and attributes to reconstruct
                
                # Check for specific fields for convenience
                clean_tag = tag.split('}')[-1] if '}' in tag else tag
                text = child.text
                
                if 'title' in clean_tag: data['title'] = text
                elif 'language' in clean_tag: data['language'] = text
                elif 'creator' in clean_tag: data['creator'] = text
                
                # Check for cover meta
                if 'meta' in clean_tag and child.get('name') == 'cover':
                    data['cover_id'] = child.get('content')

                # Store for reproduction (excluding unique-identifier which we handle separately)
                # We save the raw element info
                full_tag = tag # keeps {uri}tag
                
                # We want to output standard tags without expanding namespaces manually if possible, 
                # but ET expands them. We will reconstruct them carefully.
                # Simplified: Store tag and attributes.
                item = {'tag': tag, 'text': text, 'attrib': child.attrib}
                data['metadata_items'].append(item)

            # Resolve Identifier
            package_uid_ref = root.get('unique-identifier')
            if package_uid_ref:
                data['uid_scheme'] = package_uid_ref
                for ident in metadata_node.findall('dc:identifier', ns):
                    if ident.get('id') == package_uid_ref:
                        data['uid'] = ident.text
                        break

        # 2. Manifest
        manifest_node = root.find('opf:manifest', ns)
        if manifest_node is not None:
            for item in manifest_node.findall('opf:item', ns):
                i_id = item.get('id')
                i_href = item.get('href')
                i_media = item.get('media-type')
                if i_id and i_href:
                    data['manifest'][i_id] = {'href': i_href, 'media-type': i_media}

    except Exception as e:
        print(f"Error reading OPF data: {e}")
        
    return data


class BaseParser(HTMLParser):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.chunks = [] 
        self.current_chunk = None
        self.capture_text = False

    def finish_chunk(self):
        if self.current_chunk:
            self.current_chunk['text'] = clean_text(self.current_chunk['text'])
            if self.current_chunk['text'] or self.current_chunk['type'] == 'header':
                # Keep headers even if empty-ish to preserve structure
                if self.current_chunk['text'] or self.current_chunk['type'] == 'header':
                    if self.current_chunk['text'] or self.current_chunk['type'] == 'header':
                         self.chunks.append(self.current_chunk)
            self.current_chunk = None
            self.capture_text = False

    def handle_data(self, data):
        if self.capture_text and self.current_chunk:
            self.current_chunk['text'] += data

class EnglishParser(BaseParser):
    def __init__(self, config):
        super().__init__(config)
        self.in_caption = False
        self.rules = self.config['en']

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        classes = attr_dict.get('class', '').split()
        
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
                'type': chunk_type
            }
            self.capture_text = True

        elif tag == self.rules.get('caption_tag'):
            self.finish_chunk()
            self.current_chunk = {
                'tag': tag,
                'classes': classes,
                'text': '',
                'type': 'caption'
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
                'type': 'std'
            }
            self.capture_text = True

    def handle_endtag(self, tag):
        header_tags = self.rules.get('header_tags', [])
        if tag in header_tags:
             self.finish_chunk()
        elif tag == self.rules.get('caption_tag'):
            self.finish_chunk()
            self.in_caption = False
        elif tag == 'p':
            if self.in_caption and self.rules.get('ignore_p_in_caption'): return
            self.finish_chunk()

class SpanishParser(BaseParser):
    def __init__(self, config):
        super().__init__(config)
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

        # Block-level tags that should initiate a chunk
        block_tags = ['p', 'div'] + [f'h{i}' for i in range(1, 7)]
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
                'special_type': special_type
            }
            self.capture_text = True

    def handle_endtag(self, tag):
        if self.ignore_section:
            self.ignore_depth -= 1
            if self.ignore_depth == 0:
                self.ignore_section = False
            return
            
        if tag == 'p':
             self.finish_chunk()

    def handle_data(self, data):
        if self.ignore_section:
            return
        super().handle_data(data)

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
    en_split_indices = []
    current_idx = 0
    # Loop to find split points. 
    # Conditions:
    # 1. Remaining text > trigger
    while len(en_text) - current_idx > SPLIT_TRIGGER_CHARS:
        search_start = current_idx + SPLIT_TRIGGER_CHARS
        dot_idx = en_text.find('.', search_start)
        
        # If no dot found, stop splitting (keep remainder as one chunk)
        if dot_idx == -1: 
            break
            
        split_point = dot_idx + 1
        
        # Check for closing punctuation (quotes, brackets) immediately following the dot
        # Example: manipulation." -> split after "
        trailing = en_text[split_point:]
        match = re.match(r'^[”"’\'\)\]»]+', trailing)
        if match:
             split_point += len(match.group(0))
        
        # If split point is the very end, break loop to handle as last chunk
        if split_point >= len(en_text):
            break
            
        en_split_indices.append(split_point)
        current_idx = split_point
        
    if not en_split_indices:
        return [en_text], [es_text]

    es_split_indices = []
    if es_text:
        total_en_len = len(en_text)
        total_es_len = len(es_text)
        for en_idx in en_split_indices:
            ratio = en_idx / total_en_len
            target_es_idx = int(ratio * total_es_len)
            best_es_idx = find_nearest_sentence_end(es_text, target_es_idx)
            
            # Avoid splitting at 0 or end if close
            if best_es_idx <= 0: best_es_idx = target_es_idx
            if best_es_idx >= len(es_text): best_es_idx = len(es_text) # Will be handled by loop
            
            # Safety: don't add duplicate split point if it matches previous or is end
            if not es_split_indices or best_es_idx > es_split_indices[-1]:
                 if best_es_idx < len(es_text): # Only add if it's NOT the end
                    es_split_indices.append(best_es_idx)

    # Correction: effectively we want to align the splits.
    # If ES has fewer splits, we might run out.
    while len(es_split_indices) < len(en_split_indices):
        es_split_indices.append(len(es_text))

    en_chunks = []
    start = 0
    for end in en_split_indices:
        chunk = en_text[start:end]
        # REMOVED: if start != 0: chunk = "[...] " + chunk
        chunk = chunk + " [...]"
        en_chunks.append(chunk)
        start = end
    
    # Last EN chunk
    last_en = en_text[start:]
    if last_en.strip(): # Only add if real content
        # REMOVED: if start != 0: last_en = "[...] " + last_en
        en_chunks.append(last_en)
    
    es_chunks = []
    if not es_text:
        es_chunks = [""] * len(en_chunks)
    else:
        start = 0
        for i in range(len(en_split_indices)): 
            # Use corresponding ES index if available, else End
            end = es_split_indices[i] if i < len(es_split_indices) else len(es_text)
            
            chunk = es_text[start:end]
            # REMOVED: if start != 0: chunk = "[...] " + chunk
            chunk = chunk + " [...]"
            es_chunks.append(chunk)
            start = end
            
        # Last ES chunk
        last_es = es_text[start:]
        if len(es_chunks) < len(en_chunks):
            # REMOVED: if start != 0 and last_es.strip(): last_es = "[...] " + last_es
            es_chunks.append(last_es)
            
    return en_chunks, es_chunks

# -----------------------------------------------------------------------------
# Main Logic
# -----------------------------------------------------------------------------

def parse_file(path, parser_cls, config):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    p = parser_cls(config)
    p.feed(content)
    p.finish_chunk()
    return p.chunks

def get_header_indices(chunks):
    return [i for i, c in enumerate(chunks) if c['type'] == 'header']

def align_chunks(en_chunks, es_chunks):
    aligned = []
    print(f"Aligning: EN {len(en_chunks)} chunks (Headers: {len(get_header_indices(en_chunks))}) vs ES {len(es_chunks)} chunks (Headers: {len(get_header_indices(es_chunks))})")
    
    en_headers = get_header_indices(en_chunks)
    es_headers = get_header_indices(es_chunks)
    
    # Fix for structure mismatch: If header counts differ, fall back to flat alignment
    # This handles cases where one language uses <h1> and the other uses <p class="title">
    if len(en_headers) != len(es_headers):
        print(f"  -> Header mismatch ({len(en_headers)} vs {len(es_headers)}). Falling back to flat alignment.")
        en_headers = []
        es_headers = []
    
    # We assume headers map 1-to-1. If not, this heuristic fails, but it's better than nothing.
    
    def fingerprint(c, lang='en', shared_anchors=None):
        """Generates a fingerprint for alignment matching."""
        txt = c['text']
        
        # Anchors: Numbers (Always valid)
        nums = re.findall(r'\d+', txt)
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
        
        return f"{c['type']}:{dialog_sig}:{anchor_sig}:{sc_sig}"

    def align_section(en_sec, es_sec, depth=0):
        if not en_sec and not es_sec: return []
        
        # Base case: if drill-down depth > 1, fall back to linear pairing
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
                    local_res.append({'tag': use_tag, 'classes': use_classes, 'en': t_en, 'es': t_es})
             return local_res

        # Compute Shared Anchors (Intersection Strategy)
        # Only use proper nouns that appear in BOTH texts to avoid translation artifacts (Gods vs Dios)
        en_tokens = set()
        for c in en_sec: en_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
        es_tokens = set()
        for c in es_sec: es_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
        shared = en_tokens & es_tokens
        
        fp_en = [fingerprint(c, 'en', shared) for c in en_sec]
        fp_es = [fingerprint(c, 'es', shared) for c in es_sec]
        
        # Use SequenceMatcher to find the optimal global alignment based on type+length profile
        # autojunk=False is CRITICAL for preventing anchors from being discarded if they appear commonly (which they might in repetitive text)
        sm = difflib.SequenceMatcher(None, fp_en, fp_es, autojunk=False)
        local_res = []
        
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    en_item = en_sec[i1+k]
                    es_item = es_sec[j1+k]
                    en_text = en_item['text']
                    es_text = es_item['text']
                    
                    # Restore Split Feature for Long Paragraphs
                    if len(en_text) > SPLIT_TRIGGER_CHARS:
                         en_subs, es_subs = smart_pair_split(en_text, es_text)
                         # Ensure pairing
                         max_subs = max(len(en_subs), len(es_subs))
                         for x in range(max_subs):
                             sub_en = en_subs[x] if x < len(en_subs) else ""
                             sub_es = es_subs[x] if x < len(es_subs) else ""
                             local_res.append({
                                 'tag': en_item['tag'],
                                 'classes': en_item.get('classes', []),
                                 'en': sub_en,
                                 'es': sub_es
                             })
                    else:
                        local_res.append({
                            'tag': en_item['tag'],
                            'classes': en_item.get('classes', []),
                            'en': en_text,
                            'es': es_text
                        })
            elif tag == 'replace':
                # Block mismatch. Drill down by splitting text into sentences.
                sub_en = en_sec[i1:i2]
                sub_es = es_sec[j1:j2]
                
                # Expand paragraphs into sentence chunks
                v_en_chunks = []
                for c in sub_en:
                    if c['type'] == 'std' and c['text']:
                        sents = split_sentences(c['text'])
                        for s in sents: v_en_chunks.append({'tag': c['tag'], 'type': 'std', 'text': s, 'classes': c.get('classes', [])})
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
                    local_res.append({'tag': en_sec[k]['tag'], 'classes': en_sec[k].get('classes', []), 'en': en_sec[k]['text'], 'es': ""})
            elif tag == 'insert':
                # ES Content, No EN
                for k in range(j1, j2):
                    # Use ES classes if available? Or default?
                    # Probably default or grab from ES if we want to preserve ES styling
                    local_res.append({'tag': 'p', 'classes': es_sec[k].get('classes', []), 'en': "", 'es': es_sec[k]['text']})
                    
        return local_res    # Add implicit start (0) and end (len) sentinels
    en_anchors = [-1] + en_headers + [len(en_chunks)]
    es_anchors = [-1] + es_headers + [len(es_chunks)]
    
    # Process each section between headers
    limit = min(len(en_anchors), len(es_anchors))
    
    for k in range(limit - 1):
        en_start = en_anchors[k] + 1
        en_end = en_anchors[k+1]
        
        es_start = es_anchors[k] + 1
        es_end = es_anchors[k+1]
        
        if k > 0:
            h_en = en_chunks[en_anchors[k]]
            h_es = es_chunks[es_anchors[k]]
            aligned.append({'tag': h_en['tag'], 'en': h_en['text'], 'es': h_es['text']})
            
        # 2. Process content chunks in this section using Length Profiling
        section_en = en_chunks[en_start:en_end]
        section_es = es_chunks[es_start:es_end]
        
        aligned_sec = align_section(section_en, section_es)
        aligned.extend(aligned_sec)

    return aligned

def generate_html(aligned_pairs):
    html = """<html><head><style>
    body { font-family: serif; line-height: 1.5; max-width: 800px; margin: 0 auto; padding: 20px; }
    p, h1, h2, h3, div { margin-bottom: 10px; }
    .es-trans { color: grey; margin-bottom: 20px; display: block; }
    figcaption { font-weight: bold; margin-top: 10px; }
    </style></head><body>"""
    
    for item in aligned_pairs:
        tag = item['tag']
        en_text = item['en']
        es_text = item['es']
        
        if not en_text and not es_text: continue

        # English Block
        if tag.startswith('h') or tag == 'figcaption':
            html += f"<{tag}>{en_text}</{tag}>"
        else:
            html += f"<p>{en_text}</p>"
        
        # Spanish Block (Mirroring Tag)
        if es_text:
            if tag.startswith('h') or tag == 'figcaption':
                 html += f"<{tag} class='es-trans'>{es_text}</{tag}>"
            else:
                 html += f"<p class='es-trans'>{es_text}</p>"
            
    html += "</body></html>"
    return html

def generate_chapter_html(aligned_pairs, title=""):
    """Generates XHTML for a single chapter."""
    html_content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
"""
    
    for item in aligned_pairs:
        tag = item['tag']
        en_text = item['en']
        es_text = item['es']
        
        if not en_text and not es_text: continue

        # Format attributes
        tag_classes = item.get('classes', [])
        cls_str = " ".join(tag_classes)
        en_attrs = f' class="{cls_str}"' if cls_str else ""
        
        # For Spanish, we append 'es-trans' to inherited classes
        es_cls_list = tag_classes + ['es-trans']
        es_cls_str = " ".join(es_cls_list)
        es_attrs = f' class="{es_cls_str}"'
        
        # En
        if tag.startswith('h') or tag == 'figcaption':
            html_content += f"<{tag}{en_attrs}>{en_text}</{tag}>\n"
        else:
            html_content += f"<p{en_attrs}>{en_text}</p>\n"
        
        # Es
        if es_text:
            if tag.startswith('h') or tag == 'figcaption':
                 html_content += f"<{tag}{es_attrs}>{es_text}</{tag}>\n"
            else:
                 html_content += f"<p{es_attrs}>{es_text}</p>\n"
            
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
    siblings.sort() # Ensure textual sort matches numeric order
    return siblings

def create_bilingual_epub(en_base, es_base, output_epub_path, config=None, progress_callback=None):
    """Orchestrates the creation of the full bilingual EPUB."""
    
    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
    # 1. Map Chapters
    if not en_toc_path:
        raise FileNotFoundError(f"English TOC (.ncx) not found in {en_base}")
    if not es_toc_path:
        raise FileNotFoundError(f"Spanish TOC (.ncx) not found in {es_base}")

    en_toc = parse_toc(en_toc_path)
    es_toc = parse_toc(es_toc_path)
    pairs = align_tocs(en_toc, es_toc)
    print(f"Identified {len(pairs)} chapters to align.")
    
    if not pairs:
        raise ValueError("No aligned chapters found. The structures of the two books may be too different.")

    # 1a. Extract Metadata from English Source
    en_opf_path = find_opf_file(en_base)
    if not en_opf_path:
        parent = os.path.dirname(en_base.rstrip('/'))
        en_opf_path = find_opf_file(parent)
        
    # Read comprehensive data
    opf_data = read_opf_data(en_opf_path)
    
    # Metadata variables for convenience
    m_title = opf_data['title']
    m_lang = opf_data['language']
    m_creator = opf_data['creator']
    m_ident = opf_data['uid']
    m_uid_scheme = opf_data['uid_scheme']
    
    # Modify Title
    final_title = f"{m_title} (bilingual)"
    print(f"Metadata extracted: Title='{final_title}', Language='{m_lang}'")
    
    # Cover Handling
    cover_item_to_copy = None # (src_abs_path, filename_in_dest)
    cover_id_in_manifest = opf_data['cover_id']
    
    if cover_id_in_manifest and cover_id_in_manifest in opf_data['manifest']:
        c_item = opf_data['manifest'][cover_id_in_manifest]
        c_href = c_item['href']
        
        # Resolve path
        # opf_path directory is the base for relative hrefs
        if en_opf_path:
            opf_dir = os.path.dirname(en_opf_path)
            # URL unquote might be needed if href has %20, but usually simple file paths
            # Handle potential URL encoding just in case
            import urllib.parse
            c_path_dec = urllib.parse.unquote(c_href)
            src_full = os.path.join(opf_dir, c_path_dec)
            
            if os.path.exists(src_full):
                # We will copy this file
                fname = os.path.basename(c_path_dec)
                cover_item_to_copy = (src_full, fname, c_item['media-type'])
                print(f"Found cover image: {src_full}")
            else:
                print(f"Warning: Cover extracted from OPF ({c_href}) not found at {src_full}")


    # 1b. Auto-Detect Profile if not provided
    if config is None:
        detected_profile = 'generic'
        # Check first content file (English)
        if pairs:
            first_content = os.path.join(en_base, pairs[0][0])
            if os.path.exists(first_content):
                 detected_profile = detect_profile(first_content)
        
        # If still generic, check Spanish files (often have distinctive classes)
        if detected_profile == 'generic' and pairs:
             for _, sp in pairs: # Check first available Spanish file
                 full_es = os.path.join(es_base, sp)
                 if os.path.exists(full_es):
                     detected_profile = detect_profile(full_es)
                     if detected_profile != 'generic':
                         break
                         
        print(f"selected profile: {detected_profile}")
        config = PROFILES.get(detected_profile, PROFILES['generic'])

    # 2. Setup Staging Directory
    staging_dir = 'bilingual_epub_staging'
    if os.path.exists(staging_dir): shutil.rmtree(staging_dir)
    os.makedirs(os.path.join(staging_dir, 'META-INF'))
    os.makedirs(os.path.join(staging_dir, 'OEBPS'))
    
    # 3. Write Mimetype (must be first, no newline)
    with open(os.path.join(staging_dir, 'mimetype'), 'w', encoding='utf-8') as f:
        f.write('application/epub+zip')
        
    # 4. Write container.xml
    container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
   <rootfiles>
      <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
   </rootfiles>
</container>"""
    with open(os.path.join(staging_dir, 'META-INF', 'container.xml'), 'w', encoding='utf-8') as f:
        f.write(container_xml)
        
    # 5a. Copy Cover Image if found
    if cover_item_to_copy:
        src, dest_name, c_media = cover_item_to_copy
        # We'll put it in OEBPS root for simplicity (or images/ if we wanted)
        shutil.copy2(src, os.path.join(staging_dir, 'OEBPS', dest_name))


    css_content = """
    body { font-family: serif; line-height: 1.5; margin: 0 auto; padding: 20px; }
    p { margin-top: 0; margin-bottom: 0; text-indent: 0; } 
    h1, h2, h3, h4 { margin-top: 1.5em; margin-bottom: 0.5em; font-weight: bold; }
    .es-trans { color: #666; font-family: serif; font-size: 0.95em; margin-bottom: 1em; margin-top: 0; }
    figcaption { font-weight: bold; margin-top: 10px; }
    """
    with open(os.path.join(staging_dir, 'OEBPS', 'styles.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

    # 6. Process Chapters
    spine_refs = []
    
    for idx, (en_rel, es_rel) in enumerate(pairs):
        if progress_callback:
            progress_callback(idx, len(pairs), f"Processing {en_rel}")

        # English: collect potentially split files
        en_files = collect_split_files(en_rel, en_base)
        en_chunks = []
        for fpath in en_files:
             try:
                 chunks = parse_file(fpath, EnglishParser, config)
                 en_chunks.extend(chunks)
             except Exception as e:
                 print(f"Error parsing EN file {fpath}: {e}")

        # Spanish: collect potentially split files
        es_files = collect_split_files(es_rel, es_base)
        es_chunks = []
        for fpath in es_files:
             try:
                 chunks = parse_file(fpath, SpanishParser, config)
                 es_chunks.extend(chunks)
             except Exception as e:
                 print(f"Error parsing ES file {fpath}: {e}")
        
        print(f"Processing Pair {idx+1}/{len(pairs)}: {en_rel} <-> {es_rel}")
        
        try:
            # Align (Function handles headers internally)
            aligned = align_chunks(en_chunks, es_chunks)
            
            # Generate HTML
            out_filename = f"chapter_{idx:02d}.xhtml"
            # Use English parser results or similar for title if needed, here just generic
            chapter_content = generate_chapter_html(aligned, title=f"Chapter {idx}")
            
            with open(os.path.join(staging_dir, 'OEBPS', out_filename), 'w', encoding='utf-8') as f:
                f.write(chapter_content)
                
            spine_refs.append(out_filename)
        except Exception as e:
            print(f"Error processing {en_rel}: {e}")
            raise e

    # 7. Create content.opf
    manifest_items = ""
    spine_items = ""
    
    # CSS
    manifest_items += f'<item id="css" href="styles.css" media-type="text/css"/>\n'
    
    # Cover
    if cover_item_to_copy:
        _, dest_name, c_media = cover_item_to_copy
        # Re-use original cover ID if possible, or 'cover-image'
        cover_id = opf_data['cover_id'] or 'cover-image'
        manifest_items += f'<item id="{cover_id}" href="{dest_name}" media-type="{c_media}"/>\n'
    
    # Chapters
    for idx, filename in enumerate(spine_refs):
        item_id = f"item_{idx}"
        manifest_items += f'<item id="{item_id}" href="{filename}" media-type="application/xhtml+xml"/>\n'
        spine_items += f'<itemref idref="{item_id}"/>\n'
        
    # Reconstruct Metadata Block
    # We want to preserve everything but override title and identifier if needed so they match the package attributes
    # Actually we just dump what we found, checking for existing title/ident to update.
    
    metadata_lines = []
    
    # We use a set to avoid duplicates if we re-inject mapped items (though extraction was linear)
    # Strategy: Filter out the ID that matches unique-identifier (we write it manually)
    # Filter out title (we write manual title)
    # Write others as is.
    
    for item in opf_data['metadata_items']:
        tag = item['tag']
        text = item['text']
        attribs = item['attrib']
        
        # Skip if it is the unique identifier (we handled it in package attrib + manual entry)
        if tag.endswith('identifier') and attribs.get('id') == m_uid_scheme:
             continue
             
        # Skip title (we use final_title)
        if tag.endswith('title'):
             continue

        # Reconstruct XML string
        # Handle Namespace: tag is likely {http://purl.org/dc/elements/1.1/}title
        # We simply replace known namespaces with prefixes for clean output
        clean_tag = tag.replace('{http://purl.org/dc/elements/1.1/}', 'dc:') \
                       .replace('{http://www.idpf.org/2007/opf}', 'opf:')
                       
        # Fallback if unknown namespace
        if clean_tag.startswith('{'): 
            # Strip it
            clean_tag = clean_tag.split('}')[-1]
            
        attr_list = []
        for k, v in attribs.items():
            # Clean attribute key namespaces
            # Commonly opf:role, opf:file-as, opf:scheme
            ck = k.replace('{http://www.idpf.org/2007/opf}', 'opf:')
            if ck.startswith('{'): ck = ck.split('}')[-1] # Fallback
            attr_list.append(f'{ck}="{v}"')
            
        attr_str = " " + " ".join(attr_list) if attr_list else ""
        
        if text:
             metadata_lines.append(f'        <{clean_tag}{attr_str}>{html.escape(text)}</{clean_tag}>')
        else:
             metadata_lines.append(f'        <{clean_tag}{attr_str}/>')

    joined_metadata = "\n".join(metadata_lines)

    opf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="{m_uid_scheme}" version="3.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{final_title}</dc:title>
        <dc:identifier id="{m_uid_scheme}">{m_ident}</dc:identifier>
{joined_metadata}
    </metadata>
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        {manifest_items}
    </manifest>
    <spine toc="ncx">
        {spine_items}
    </spine>
</package>"""
    
    with open(os.path.join(staging_dir, 'OEBPS', 'content.opf'), 'w', encoding='utf-8') as f:
        f.write(opf_content)

    # 8. Create Simple TOC (NCX)
    nav_points = ""
    for idx, filename in enumerate(spine_refs):
        nav_points += f"""<navPoint id="navPoint-{idx+1}" playOrder="{idx+1}">
      <navLabel><text>Section {idx+1}</text></navLabel>
      <content src="{filename}"/>
    </navPoint>\n"""
    
    ncx_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:12345"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{final_title}</text></docTitle>
  <navMap>
    {nav_points}
  </navMap>
</ncx>"""
    
    with open(os.path.join(staging_dir, 'OEBPS', 'toc.ncx'), 'w', encoding='utf-8') as f:
        f.write(ncx_content)
        
    # 9. Zip it
    print(f"Creating EPUB: {output_epub_path}")
    with zipfile.ZipFile(output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(staging_dir, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                if file == 'mimetype': continue
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, staging_dir)
                zipf.write(file_path, arc_name)
    
    print("Alignment/Generation Complete.")
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a bilingual EPUB from extracted English and Spanish EPUB OEBPS directories.")
    parser.add_argument("--en", required=False, default='temp_bilingual/en_full/OEBPS', help="Path to English OEBPS directory")
    parser.add_argument("--es", required=False, default='temp_bilingual/es_full/OEBPS', help="Path to Spanish OEBPS directory")
    parser.add_argument("--output", required=False, default='bilingual_book.epub', help="Output EPUB filename")
    
    args = parser.parse_args()
    
    # In a real generalized version, one might load config from a JSON file here.
    # config = load_config(args.config) 
    config = BOOK_CONFIG
    
    create_bilingual_epub(args.en, args.es, args.output, config)
