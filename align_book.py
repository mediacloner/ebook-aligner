import argparse
import sys
import os
import re
import html
import difflib
import concurrent.futures
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import zipfile
import shutil
import uuid
from datetime import datetime
from difflib import SequenceMatcher
from collections import Counter
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
    """
    Aligns chapters using a hybrid 'Anchor and Fill' strategy.
    1. Identify high-confidence matches (Anchors) using Structure/String matching.
    2. Fill gaps between anchors using positional alignment (linear zip).
    This ensures 'all book' is processed even if names don't match (e.g. Prologue vs Prólogo if typo/mismatch).
    """
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
    # We iterate through the anchors and fill the space before/between/after.
    
    last_en_idx = -1
    last_es_idx = -1
    
    # Add a sentinel anchor at the end to handle trailing items
    sentinel_en = {'idx': len(en_items)}
    sentinel_es = {'idx': len(es_items)}
    anchors.append((sentinel_en, sentinel_es))
    
    for anchor_en, anchor_es in anchors:
        current_en_idx = anchor_en['idx']
        current_es_idx = anchor_es['idx']
        
        # Identification of Gap Items
        # Items strictly BETWEEN last_en_idx and current_en_idx
        gap_en = [x for x in en_items if last_en_idx < x['idx'] < current_en_idx and x['idx'] not in en_matched]
        gap_es = [x for x in es_items if last_es_idx < x['idx'] < current_es_idx and x['idx'] not in es_matched]
        
        # Linear Alignment of Gap (Zip)
        # We pair 1st unmatched EN with 1st unmatched ES in this region.
        # Any excess on either side is unfortunately dropped (or could be appended as unmatched, but we need pairs)
        # "Translate all book" -> We prioritize pairing over precision here.
        limit = min(len(gap_en), len(gap_es))
        for k in range(limit):
            final_pairs.append((gap_en[k]['item']['src'], gap_es[k]['item']['src']))
            
        # Add the Anchor itself (if not sentinel)
        if current_en_idx < len(en_items) and current_es_idx < len(es_items):
             final_pairs.append((anchor_en['item']['src'], anchor_es['item']['src']))
             
        last_en_idx = current_en_idx
        last_es_idx = current_es_idx
        
    return final_pairs

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip()

def split_sentences(text):
    """
    Deprecated: No longer splits sentences. Returns text as single item.
    """
    if not text:
        return []
    return [text.strip()]


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
    """Deprecated: Returns original text paired."""
    return [en_text], [es_text]

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
                    local_res.append({'tag': use_tag, 'classes': use_classes, 'en': t_en, 'es': t_es})
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
        
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == 'equal':
                for k in range(i2 - i1):
                    en_item = en_sec[i1+k]
                    es_item = es_sec[j1+k]
                    en_text = en_item['text']
                    es_text = es_item['text']
                    
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

    # Handle any remaining chunks after the last header (or if no headers)
    if len(en_anchors) > limit:
        en_section = en_chunks[en_anchors[limit-1]+1 : en_anchors[limit]]
        section_aligned = align_section(en_section, [])
        final_aligned.extend(section_aligned)
    
    if len(es_anchors) > limit:
        es_section = es_chunks[es_anchors[limit-1]+1 : es_anchors[limit]]
        section_aligned = align_section([], es_section)
        final_aligned.extend(section_aligned)

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
            
            if ratio_curr < 1.05 and ratio_combined <= 1.8:
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
                         'text': nxt.get('text', '')
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
    pass_2_aligned = [x for x in pass_2_aligned if x['en'].strip() or x['es'].strip()]
        
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
    pass_2_aligned = [x for x in pass_2_aligned if x['en'].strip() or x['es'].strip()]
    
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
                
                if sim > 0.1: # Loose threshold?
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
                     if curr['en'].strip() or curr['es'].strip():
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
                           
                           if curr['en'].strip() or curr['es'].strip():
                               final_pass.append(curr)
                           continue

        if curr['en'].strip() or curr['es'].strip():
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
                   # Next Item (Old Match) loses English key -> Becomes Orphan
                   nxt['en'] = ""
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
    final_pass = [x for x in final_pass if x['en'].strip() or x['es'].strip()]





    
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
            # Removed CSS line-clamping
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

def process_chapter_pair(args):
    """
    Worker function to process a single chapter pair.
    Args structured as tuple to easier map with executor:
    (idx, en_rel, es_rel, en_opf_dir, es_opf_dir, staging_dir, config)
    """
    idx, en_rel, es_rel, en_opf_dir, es_opf_dir, staging_dir, config = args
    
    # Standard processing without dictionary semantic guard
    try:
        # English: collect potentially split files (RELATIVE TO OPF DIR!)
        en_files = collect_split_files(en_rel, en_opf_dir)
        en_chunks = []
        for fpath in en_files:
             try:
                 chunks = parse_file(fpath, EnglishParser, config)
                 en_chunks.extend(chunks)
             except Exception as e:
                 print(f"Error parsing EN file {fpath}: {e}")

        # Spanish: collect potentially split files (RELATIVE TO OPF DIR!)
        es_files = collect_split_files(es_rel, es_opf_dir)
        es_chunks = []
        for fpath in es_files:
             try:
                 chunks = parse_file(fpath, SpanishParser, config)
                 es_chunks.extend(chunks)
             except Exception as e:
                 print(f"Error parsing ES file {fpath}: {e}")
        
        # print(f"Processing Pair {idx+1}: {en_rel} <-> {es_rel}")
        
        # Align
        if config.get('use_neural') and NeuralAligner:
            try:
                global CACHED_ALIGNER
                if CACHED_ALIGNER is None:
                    print(f"Process {os.getpid()}: Loading Neural Model...")
                    CACHED_ALIGNER = NeuralAligner()
                aligner = CACHED_ALIGNER
                
                # Helper to explode paragraphs into sentences
                def flatten_to_sentences(chunks):
                    flat = []
                    for c in chunks:
                        if c['type'] == 'header' or c['tag'] == 'figcaption':
                            flat.append(c) # Keep headers/captions as is
                        else:
                            # Split paragraph text
                            sents = split_sentences(c['text'])
                            # Debug log for large splits
                            # if len(sents) > 5:
                            #    print(f"Split paragraph into {len(sents)} sentences.")
                            
                            for s in sents:
                                if s.strip():
                                    flat.append({
                                        'type': c['type'],
                                        'tag': c['tag'],
                                        'classes': c.get('classes', []),
                                        'text': s
                                    })
                    return flat

                # Flatten both sides
                en_sents = flatten_to_sentences(en_chunks)
                es_sents = flatten_to_sentences(es_chunks)
                
                print(f"Aligning {len(en_sents)} EN vs {len(es_sents)} ES sentences...")
                aligned_groups = aligner.align_dtw(en_sents, es_sents)
                
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Critical Neural Alignment Error in pair {idx}: {e}")
                # Fallback to heuristic
                print("Falling back to heuristic alignment for this chapter.")
                aligned = align_chunks(en_chunks, es_chunks)
            else:
                # Convert neural groups to the format expected by generate_chapter_html
                aligned = []
                for group in aligned_groups:
                    ens = group['en_chunks']
                    ess = group['es_chunks']
                    
                    merged_en_text = ""
                    merged_es_text = ""
                    tag = 'p'
                    classes = []
                    
                    if ens:
                        merged_en_text = " ".join([c.get('text', '') for c in ens])
                        tag = ens[0].get('tag', 'p')
                        classes = ens[0].get('classes', [])
                    
                    if ess:
                        merged_es_text = " ".join([c.get('text', '') for c in ess])
                        if not ens:
                            tag = ess[0].get('tag', 'p')
                            classes = ess[0].get('classes', [])
                            
                    aligned.append({
                        'tag': tag,
                        'classes': classes,
                        'en': merged_en_text,
                        'es': merged_es_text
                    })

                    
        else:
            aligned = align_chunks(en_chunks, es_chunks)
        
        # -------------------------------------------------------------------------
        # Phase 5: Splitter Service (Post-Alignment Refinement)
        # -------------------------------------------------------------------------
        if Splitter and aligned:
             # Ensure we have an aligner if possible (might be None for heuristic path, that's fine)
             aligner_instance = CACHED_ALIGNER if config.get('use_neural') else None
             t_len = config.get('split_length', 280)
             splitter_svc = Splitter(aligner=aligner_instance, trigger_length=t_len)
             aligned = splitter_svc.process_all(aligned)

        # Generate HTML
        out_filename = f"chapter_{idx:02d}.xhtml"
        chapter_content = generate_chapter_html(aligned, title=f"Chapter {idx}")
        
        out_path = os.path.join(staging_dir, 'OEBPS', out_filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chapter_content)
            
        return (idx, out_filename, en_rel)
        
    except Exception as e:
        print(f"Error processing {en_rel}: {e}")
        return (idx, None, str(e))

def create_bilingual_epub(en_base, es_base, output_epub_path, config=None, progress_callback=None):
    staging_dir = 'bilingual_epub_staging'
    try:
        return _process_epub_generation(en_base, es_base, output_epub_path, staging_dir, config, progress_callback)
    except Exception as e:
        print(f"Error during EPUB generation: {e}")
        raise
    finally:
        if os.path.exists(staging_dir):
            print(f"Cleaning up staging directory: {staging_dir}")
            shutil.rmtree(staging_dir)

def _process_epub_generation(en_base, es_base, output_epub_path, staging_dir, config=None, progress_callback=None):
    """Orchestrates the creation of the full bilingual EPUB."""
    
    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
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
    m_namespaces = opf_data['namespaces']
    
    # Ensure Calibre namespace is present if likely used
    if 'calibre' not in m_namespaces and any('calibre:' in item['tag'] for item in opf_data['metadata_items']):
         m_namespaces['calibre'] = "http://calibre.kovidgoyal.net/2009/metadata"

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


    # 1b. Auto-Detect Profile if not provided or partial
    # We might pass {'use_neural': True}, so check for content keys
    if config is None or 'en' not in config:
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
        
        # Load profile settings
        profile_config = PROFILES.get(detected_profile, PROFILES['generic'])
        
        # Merge if we had some partial config (e.g. flags)
        if config:
            profile_config.update(config)
            
        config = profile_config
        


    # 2. Setup Staging Directory
    # staging_dir passed as argument
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
    p.es-trans, div.es-trans, span.es-trans { color: #666; font-family: serif; font-size: 0.95em; margin-bottom: 0.5em; margin-top: 0; }
    h1.es-trans, h2.es-trans, h3.es-trans, h4.es-trans { color: #666; opacity: 0.8; }
    /* Remove spacing between English header and Spanish header */
    h1 + h1.es-trans, h2 + h2.es-trans, h3 + h3.es-trans, h4 + h4.es-trans { margin-top: 0; padding-top: 0; }
    /* Optional: tighten bottom of English header too if needed */
    h1:has(+ h1.es-trans), h2:has(+ h2.es-trans), h3:has(+ h3.es-trans), h4:has(+ h4.es-trans) { margin-bottom: 0.1em; } 
    figcaption { font-weight: bold; margin-top: 10px; }
    .clamp-text {
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    """
    with open(os.path.join(staging_dir, 'OEBPS', 'styles.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)

    # 6. Process Chapters
    spine_refs = []
    
    en_opf_dir = os.path.dirname(en_opf_path) if en_opf_path else en_base
    es_opf_dir = os.path.dirname(find_opf_file(es_base)) if find_opf_file(es_base) else es_base

    args_list = []
    print(f"Preparing {len(pairs)} tasks for parallel processing (Multithread CPU)...")
    
    # Prepare arguments for each task
    for idx, (en_rel, es_rel) in enumerate(pairs):
        # We pass everything needed to process one pair
        args = (idx, en_rel, es_rel, en_opf_dir, es_opf_dir, staging_dir, config)
        args_list.append(args)

    # Dictionary to collect results: idx -> filename
    # We need to maintain order of spine_refs
    results_map = {}
    
    # Use ProcessPoolExecutor for CPU-bound parallelism
    # max_workers=None defaults to num_cpus
    # We use 'spawn' start method context implicitly on Mac/Windows, but we handled global DICT_LOADER in worker
    
    # If using neural alignment (heavy memory usage per process), limit workers
    max_workers = 1 if config.get('use_neural') else None
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_idx = {executor.submit(process_chapter_pair, args): args[0] for args in args_list}
        
        count_done = 0
        total = len(args_list)
        
        for future in concurrent.futures.as_completed(future_to_idx):
            f_idx = future_to_idx[future]
            try:
                res_idx, res_filename, res_name = future.result()
                if res_filename:
                    results_map[res_idx] = res_filename
                else:
                    print(f"Task {f_idx} returned no filename (Error: {res_name})")
            except Exception as exc:
                print(f"Task {f_idx} generated an exception: {exc}")
                
            count_done += 1
            if progress_callback:
                progress_callback(count_done, total, f"Processed {count_done}/{total} chapters")
            else:
                 # Print progress every 10%
                 if total > 10 and count_done % (total // 10) == 0:
                      print(f"Progress: {count_done}/{total}...")

    # Reconstruct spine_refs in correct order
    for idx in range(len(pairs)):
        if idx in results_map:
            spine_refs.append(results_map[idx])
        else:
            print(f"Warning: Chapter {idx} failed or missing from results.")

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
    
    metadata_lines = []
    
    # Helper to resolve namespace prefix
    # Inverted map: URI -> Prefix
    uri_to_prefix = {v: k for k, v in m_namespaces.items()}
    # Add standard checks
    if 'http://purl.org/dc/elements/1.1/' not in uri_to_prefix: uri_to_prefix['http://purl.org/dc/elements/1.1/'] = 'dc'
    if 'http://www.idpf.org/2007/opf' not in uri_to_prefix: uri_to_prefix['http://www.idpf.org/2007/opf'] = 'opf'
    
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
        clean_tag = tag
        if '}' in tag:
             uri, local_name = tag.split('}')
             uri = uri[1:] # remove {
             prefix = uri_to_prefix.get(uri)
             if prefix:
                 clean_tag = f"{prefix}:{local_name}"
             else:
                 # Fallback, just use local name or look harder?
                 # ideally we registered it.
                 clean_tag = local_name
        
        attr_list = []
        for k, v in attribs.items():
            ck = k
            if '}' in k:
                 uri, local = k.split('}')
                 uri = uri[1:]
                 prefix = uri_to_prefix.get(uri)
                 if prefix:
                     ck = f"{prefix}:{local}"
                 else:
                     ck = local
            attr_list.append(f'{ck}="{html.escape(str(v))}"')
            
        attr_str = " " + " ".join(attr_list) if attr_list else ""
        
        if text:
             metadata_lines.append(f'        <{clean_tag}{attr_str}>{html.escape(str(text))}</{clean_tag}>')
        else:
             metadata_lines.append(f'        <{clean_tag}{attr_str}/>')

    joined_metadata = "\n".join(metadata_lines)

    # Construct xmlns attributes
    xmlns_attrs = []
    for prefix, uri in m_namespaces.items():
         if prefix: # Skip default if handled by package
              xmlns_attrs.append(f'xmlns:{prefix}="{uri}"')
    
    if 'xmlns:dc' not in xmlns_attrs and 'dc' not in m_namespaces:
         xmlns_attrs.append('xmlns:dc="http://purl.org/dc/elements/1.1/"')
    if 'xmlns:opf' not in xmlns_attrs and 'opf' not in m_namespaces:
         xmlns_attrs.append('xmlns:opf="http://www.idpf.org/2007/opf"')
         
    xmlns_str = " ".join(xmlns_attrs)

    opf_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="{m_uid_scheme}" version="3.0" {xmlns_str}>
    <metadata {xmlns_str}>
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
    print(f"Success! Bilingual EPUB created at: {output_epub_path}")
    
    with zipfile.ZipFile(output_epub_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(os.path.join(staging_dir, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
        for root, dirs, files in os.walk(staging_dir):
            for file in files:
                if file == 'mimetype': continue
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, staging_dir)
                zipf.write(file_path, arc_name)
    
    print("Alignment/Generation Complete.")
    
    return {'title': final_title, 'author': m_creator}
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a bilingual EPUB from extracted English and Spanish EPUB OEBPS directories.")
    parser.add_argument("--en", required=False, default='temp_bilingual/en_full/OEBPS', help="Path to English OEBPS directory")
    parser.add_argument("--es", required=False, default='temp_bilingual/es_full/OEBPS', help="Path to Spanish OEBPS directory")
    parser.add_argument("--output", required=False, default='bilingual_book.epub', help="Output EPUB filename")
    parser.add_argument("--local-ai", action='store_true', help="Use local neural alignment (LaBSE)")
    
    parser.add_argument('--split-length', type=int, default=280, help='Character threshold to trigger paragraph splitting (default: 280)')
    
    args = parser.parse_args()

    # Pass config
    config = {
        'use_neural': args.local_ai,
        'split_length': args.split_length
    }
    
    if args.local_ai:
        print("Using Local Neural Alignment (LaBSE)...")
    
    create_bilingual_epub(args.en, args.es, args.output, config)
