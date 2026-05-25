import argparse
import sys
print(f"DEBUG: Loading align_book.py v2024.12.28.1019 from {__file__}")
import os
import time
import re
import html
import difflib
from urllib.parse import unquote
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
import numpy as np
from scipy.spatial.distance import cdist
from bs4 import BeautifulSoup, NavigableString, Comment, Tag
import warnings
from sentence_transformers import SentenceTransformer, util
import torch
import semantic_toc  # [NEW] Import our semantic aligner modulening
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Stanza NLP for sentence tokenization (lazy loaded)
import stanza
_STANZA_PIPELINES = {}

def _get_stanza_pipeline(lang='en'):
    """Lazy-load Stanza pipeline for the given language."""
    global _STANZA_PIPELINES
    if lang not in _STANZA_PIPELINES:
        try:
            # Try to load existing model
            _STANZA_PIPELINES[lang] = stanza.Pipeline(lang, processors='tokenize', verbose=False, download_method=None)
        except Exception:
            # Download if not available
            stanza.download(lang, processors='tokenize', verbose=False)
            _STANZA_PIPELINES[lang] = stanza.Pipeline(lang, processors='tokenize', verbose=False)
    return _STANZA_PIPELINES[lang]

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
            'header_classes': ['CN', 'CN-Only', 'CT', 'fmh', 'bibh', 'bib_center2', 'bib_jus', 'bib_jus1', 'bib_center'], 
            'caption_start_tags': ['figcaption'],
            'caption_classes': ['caption'],
            'ignore_tags': [],
            'ignore_classes': [],
            'SPLIT_TRIGGER_CHARS': 240,
            'image_tag': 'img',
            'merge_headers': False,
            'header_merge_targets': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        },
        'es': {
            'SPLIT_TRIGGER_CHARS': 200,
            'header_tags': ['h1', 'h2', 'h3', 'p', 'div'],
            'header_indicators': [
                'CAPITULOLO', 'LADILLOS',
                'Capitulos_Capitulo_Numero', 
                'Capitulos_Capitulo_1_Linea', 
                'Subcapitulos_subcapitulo', 
                'Subcapitulos_Subcapitulo',
                'tith', 'title', 'titulo', 'tit',
                'fmh', 'centern', 'bibh', 'notes1', 'notesb'
            ],
            'caption_classes': ['Basico_pie_foto', 'Basico_pie_foto_centrado', 'caption'],
            'ignore_tags': [],
            'ignore_classes': ['_idFootnotes', 'centradoespacioantes', 'capitulo', 'Notas-Pie_Notas_Pie', '_idFootnote', 'credit'],
            'ignore_div_classes': ['_idFootnotes'],
            'merge_headers': False,
            'header_merge_trigger': 'Capitulos_Capitulo_1_Linea',
            'header_merge_targets': ['Capitulos_Capitulo_Numero', 'Capitulos_Capitulo_1_Linea', 'capitulo', 'tith', 'title', 'titulo', 'tit']
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

def parse_toc(toc_path):
    """Parses the NCX (or OPF) file and returns a list of (label, src) tuples."""
    if toc_path.lower().endswith('.opf'):
        return parse_opf_as_toc(toc_path)
        
    tree = ET.parse(toc_path)
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
        content = unquote(content_node.get('src')) if content_node is not None else ""
        
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

    base_dir = os.path.dirname(toc_path)
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

def enrich_toc_from_content(toc, base_dir):
    """
    Scans the source files for each TOC item to find subtitles (dates)
    that might be missing from the NCX label.
    """
    for item in toc:
        if not item['src']: continue
        
        # Resolve path
        rel_path = item['src'].split('#')[0]
        full_path = os.path.join(base_dir, rel_path)
        
        if not os.path.exists(full_path):
            continue
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                # Read first 3KB - subtitles are usually at top
                content = f.read(3000)
            
            # print(f"Scanned {rel_path}: {len(content)} bytes") # excessive
            
            # Regex for subtitles
            # Match elements with "subtitulo" or "subtitle" in class
            matches = re.findall(r'<(h[2-3]|p)[^>]*class="[^"]*subtitul[^"]*"[^>]*>(.*?)</\1>', content, re.IGNORECASE | re.DOTALL)
            
            if matches:
                pass # print(f"Found subtitle matches in {rel_path}: {matches}")
            
            extracted_subs = []
            for tag, text in matches:
                clean = re.sub(r'<[^>]+>', '', text).strip()
                if clean and len(clean) < 50:
                    extracted_subs.append(clean)
            
            # If nothing found via class, look for loose dates in ANY h2/h3
            if not extracted_subs:
                headers = re.findall(r'<(h[2-3])[^>]*>(.*?)</\1>', content, re.IGNORECASE | re.DOTALL)
                for tag, text in headers:
                     clean = re.sub(r'<[^>]+>', '', text).strip()
                     # Check if looks like date
                     if re.search(r'\d{4}', clean) and len(clean) < 50:
                         extracted_subs.append(clean)

            if extracted_subs:
                # Append to label
                # Avoid dupes
                existing = item['label'].lower()
                to_add = [s for s in extracted_subs if s.lower() not in existing]
                if to_add:
                    item['label'] = f"{item['label']} ({', '.join(to_add)})"
                    # print(f"Enriched TOC: {item['label']}")

        except Exception as e:
            # print(f"Error enriching {rel_path}: {e}")
            pass


def extract_figure_number(text):
    """Extract figure number from caption text."""
    m = re.match(r'^(?:Figure|Figura|Table|Tabla|Fig\.?)\s*(\d+)', text.strip(), re.IGNORECASE)
    if m:
        return m.group(1)
    return None


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
    if 'bibliograph' in label or 'bibliograf' in label: return 'bibliography'
    
    # Specific Author's Note Check (Before generic note check)
    if ('note' in label and 'author' in label) or ('nota' in label and ('autora' in label or 'autor' in label)):
        return 'authors_note_specific'
        
    if 'note' in label or 'nota' in label: return 'notes'
    
    # Reading Group Guide
    if 'reading group' in label or 'lectura de grupo' in label: return 'reading_group_guide'
    if 'questions' in label and ('discussion' in label or 'discusión' in label): return 'reading_group_guide'
    
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

# Common abbreviations that should NOT trigger sentence splits
# English: Mr., Mrs., Ms., Dr., Prof., Sr., Jr., St., vs., No., Fig., etc.
# Spanish: Sr., Sra., Srta., Dr., Dra., Prof., Lic., Ing., Arq., etc.
ABBREVIATIONS = [
    'Mr', 'Mrs', 'Ms', 'Dr', 'Prof', 'Sr', 'Jr', 'St', 'vs', 'No', 'Fig',
    'Sra', 'Srta', 'Dra', 'Lic', 'Ing', 'Arq', 'Gral', 'Col', 'Cap',
    'Rev', 'Gov', 'Gen', 'Lt', 'Sgt', 'Pvt', 'Cpl', 'Corp',
    'Inc', 'Ltd', 'Co', 'Bros', 'Ave', 'Blvd', 'Rd', 'Mt',
    'Vol', 'Ch', 'Pt', 'Ed', 'Ph', 'etc', 'al'
]

def _protect_abbreviations(text):
    """Replace abbreviation periods with placeholder to prevent incorrect sentence splits."""
    protected = text
    for abbr in ABBREVIATIONS:
        # Match abbreviation followed by period and space (case insensitive)
        # e.g., "Mr. Jones" -> "Mr⌐ABBR⌐ Jones"
        pattern = r'\b(' + re.escape(abbr) + r')\. '
        protected = re.sub(pattern, r'\1⌐ABBR⌐ ', protected, flags=re.IGNORECASE)
    return protected

def _restore_abbreviations(text):
    """Restore abbreviation periods from placeholder."""
    return text.replace('⌐ABBR⌐', '.')

def _split_sentences_regex(text):
    """
    Splits text into sentences using simple regex (Legacy method).
    Handles common abbreviations via protection.
    """
    if not text:
        return []
    
    # Protect abbreviations before splitting
    protected_text = _protect_abbreviations(text)
    
    # Pattern: End punctuation + optional quotes + whitespace + Next is Upper/Start/Dash
    # Added em-dash (—) and en-dash (–) to lookahead for Spanish dialogue
    pattern = r'([.!?…]+(?:["\"\'\)\]»]*)\s+(?=[A-Z¿¡\"\'\-—–]))'
    parts = re.split(pattern, protected_text)
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
    
    # Restore abbreviations in each sentence
    return [_restore_abbreviations(s) for s in sentences]


def split_sentences_helper(text, language='en'):
    """
    Splits text into sentences using Stanza NLP.
    
    Stanza is a Stanford NLP library that uses neural models trained on 
    Universal Dependencies for accurate sentence boundary detection. It 
    correctly handles abbreviations like Mr., Dr., Sr., Sra., Dra., etc.
    
    Args:
        text: The text to split into sentences
        language: Language code ('en' for English, 'es' for Spanish)
    
    Returns:
        List of sentence strings
    """
    if not text or not text.strip():
        return []
    
    try:
        # Use Stanza for sentence segmentation
        nlp = _get_stanza_pipeline(language)
        doc = nlp(text)
        sentences = [sent.text.strip() for sent in doc.sentences if sent.text.strip()]
        
        # Post-process: Stanza may still split on rare abbreviations (e.g., "Prof. Williams")
        # Apply abbreviation protection as a safety net
        merged_sentences = []
        i = 0
        while i < len(sentences):
            curr = sentences[i]
            # Check if current sentence ends with an abbreviation
            ends_with_abbr = False
            for abbr in ABBREVIATIONS:
                if curr.rstrip().endswith(abbr + '.'):
                    ends_with_abbr = True
                    break
            
            if ends_with_abbr and i + 1 < len(sentences):
                # Merge with next sentence
                merged_sentences.append(curr + ' ' + sentences[i + 1])
                i += 2
            else:
                merged_sentences.append(curr)
                i += 1
        
                i += 1
        
        # HYBRID CHECK: If Stanza returns only 1 sentence, but Regex would find multiple
        # substantial sentences (e.g., "Boxer... D. Trazaba..."), trust Regex.
        # This handles cases where Stanza is too conservative about initials vs letters.
        if len(merged_sentences) == 1:
            try:
                regex_sents = _split_sentences_regex(text)
                # If regex found at least 2 sentences that are reasonably long (>8 chars),
                # it's likely a valid split that Stanza missed.
                substantial_count = sum(1 for s in regex_sents if len(s.strip()) > 8)
                if substantial_count > 1:
                    print(f"DEBUG: Stanza returned 1 sentence, Regex found {len(regex_sents)} (substantial). Using Regex.")
                    return regex_sents
            except Exception:
                pass

        return merged_sentences if merged_sentences else sentences
        
    except Exception as e:
        # Fallback to regex-based splitting if Stanza fails
        print(f"Stanza failed, using regex fallback: {e}")
        return _split_sentences_regex(text)



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



# --- METADATA/FRONTMATTER DETECTION ---
# These sections will never align correctly between different editions
METADATA_PATTERNS = [
    # Copyright/Legal
    r'copyright\s*©?', r'\bisbn\b', r'first\s*(avon\s*)?(printing|edition)',
    r'trademark', r'library\s*of\s*congress', r'published\s*by',
    r'marca\s*registrada', r'all\s*rights?\s*reserved', r'derechos?\s*reservados?',
    # Publisher/Web
    r'www\.', r'\.org\b', r'\.com\b', r'maquetación', r'edición\s*digital',
    # Credits/Index/TOC
    r'\bcréditos\b', r'\bcredits\b', r'\bíndice\b', r'\bindex\b',
    r'\btable\s*of\s*contents\b', r'\bcontents\b', r'nota\s*del\s*(autor|editor)',
    r"author'?s?\s*note", r"editor'?s?\s*note",
    # Frontmatter
    r'\bportada\b', r'\bcover\b', r'\btitle\s*page\b', r'\bdedication\b',
    r'\bdedicatoria\b', r'\bepígrafe\b', r'\bepigraph\b',
    # Navigation markers (TOC entries)
    r'primera\s*parte', r'segunda\s*parte', r'tercera\s*parte',
    r'part\s*one', r'part\s*two', r'part\s*three',
    # Map/illustration references
    r'\bsite\s*of\s*levee\b', r'\bpop\.\s*\d', r'alabama\s*\n.*pop\.',
]

def is_metadata_content(text):
    """
    Detect if text is metadata/frontmatter that shouldn't be flagged.
    
    Metadata from different editions will never align correctly
    (different publishers, dates, ISBNs, etc.)
    """
    if not text or len(text) > 500:  # Metadata is usually short
        return False
    
    text_lower = text.lower()
    match_count = sum(1 for p in METADATA_PATTERNS if re.search(p, text_lower))
    
    # Require at least 1 strong match for short text, 2 for longer
    return match_count >= 1 if len(text) < 150 else match_count >= 2

# --- SCENE BREAK DETECTION (Pattern 3: Paragraph Bleeding Fix) ---
SCENE_BREAK_PATTERNS = [
    r'^[\s]*⁂[\s]*$',           # Asterism
    r'^[\s]*\*\s*\*\s*\*[\s]*$', # Three asterisks
    r'^[\s]*\*{3,}[\s]*$',       # Three or more asterisks
    r'^[\s]*§[\s]*$',            # Section sign
    r'^[\s]*[-–—]{3,}[\s]*$',    # Three or more dashes
    r'^[\s]*[_]{3,}[\s]*$',      # Three or more underscores
]




def align_tocs(en_toc, es_toc, en_toc_dir=None, es_toc_dir=None, aligner=None, model=None):
    """
    Aligns the Table of Contents from both books.
    Returns a list of tuples: (Label, en_src, es_src, level)
    
    Args:
        model: Optional SentenceTransformer model (LaBSE). If provided, enables Semantic Alignment strategy.
    """

    en_items = []
    for i, item in enumerate(en_toc):
        norm = normalize_label(item['label'])
        raw = item['label'].lower().strip()
        en_items.append({'idx': i, 'item': item, 'norm': norm, 'raw':  raw})

    es_items = []
    for i, item in enumerate(es_toc):
        norm = normalize_label(item['label'])
        raw = item['label'].lower().strip()
        if raw in ['tabla de contenido', 'contenido', 'página de título', 'cubierta', 'derechos de autor']: continue
        es_items.append({'idx': i, 'item': item, 'norm': norm, 'raw': raw})
    
    # Pre-compute semantic similarity matrix
    semantic_sim_matrix = None
    if aligner and en_items and es_items:
        print("Using Neural Aligner for TOC matching...")
        try:
            en_texts = [x['item']['label'] or "Chapter" for x in en_items]
            es_texts = [x['item']['label'] or "Capitulo" for x in es_items]
            
            en_embs = aligner.embed_chunks([{'text': t} for t in en_texts])
            es_embs = aligner.embed_chunks([{'text': t} for t in es_texts])
            
            dists = cdist(en_embs, es_embs, metric='cosine')
            semantic_sim_matrix = 1 - dists
        except Exception as e:
            print(f"Neural TOC alignment preparation failed: {e}")
            semantic_sim_matrix = None

    # --- SCORE CALCULATION ---
    all_candidates = [] # (score, en_idx, es_idx)
    
    for i, en in enumerate(en_items):
        en_label = en['item']['label']
        en_norm = normalize_label(en_label)
        en_level = en['item'].get('level', 1)
        
        for j, es in enumerate(es_items):
             es_label = es['item']['label']
             es_norm = normalize_label(es_label)
             es_level = es['item'].get('level', 1)
             
             score = 0.0
             
             if not en['raw'] and not es['raw']:
                 # Empty labels: Position Match
                 en_pos = i / len(en_items) if len(en_items) > 0 else 0
                 es_pos = j / len(es_items) if len(es_items) > 0 else 0
                 pos_diff = abs(en_pos - es_pos)
                 if pos_diff < 0.05: score = 0.95
                 elif pos_diff < 0.15: score = 0.8
                 else: score = max(0.3, 0.8 - (pos_diff * 2))
             elif en_norm and en_norm == es_norm:
                 score = 1.0
             else:
                 sim = difflib.SequenceMatcher(None, en_label.lower(), es_label.lower()).ratio()
                 score = sim
                 
                 # Neural Boost
                 if semantic_sim_matrix is not None:
                     sem_score = semantic_sim_matrix[i, j]
                     if sem_score > score:
                         if sem_score > 0.8: score = sem_score
                         else: score = (score + sem_score) / 2
            
             # --- HARD CONSTRAINT: DATE MISMATCH ---
             if isinstance(en_norm, tuple) and isinstance(es_norm, tuple):
                 # Check if they are both date chapters
                 if en_norm[0] == 'date-chapter' and es_norm[0] == 'date-chapter':
                     if en_norm != es_norm:
                         score = 0.0 # Force mismatch for different dates
            
             # Level Penalty
             if abs(en_level - es_level) > 0:
                 if score < 0.9: score = 0 
             
             # Relative Position Penalty (Keep diagonal)
             en_pos = i / len(en_items) if en_items else 0
             es_pos = j / len(es_items) if es_items else 0
             pos_diff = abs(en_pos - es_pos)
             if pos_diff > 0.4: score -= 0.3
                 
             if score > 0.1:
                all_candidates.append({'score': score, 'en': i, 'es': j})

    # --- STAGE 1: HIGH CONFIDENCE ANCHORS ---
    candidates_sorted = sorted(all_candidates, key=lambda x: x['score'], reverse=True)
    
    en_assigned = set()
    es_assigned = set()
    matches_map = {} # en_idx -> es_idx
    
    # High Threshold for initial anchoring
    HIGH_THRESHOLD = 0.85
    
    for cand in candidates_sorted:
        if cand['score'] < HIGH_THRESHOLD: break
        
        i, j = cand['en'], cand['es']
        if i in en_assigned or j in es_assigned: continue
        
        # Monotonicity Check (LIS-lite): 
        # Only accept if consistent with existing strong anchors?
        # Actually, let's just take highest scores first.
        # But we MUST filter by LIS later.
        
        matches_map[i] = j
        en_assigned.add(i)
        es_assigned.add(j)
        
    # --- RECURSIVE BEST-FIRST ALIGNMENT ---
    # Strictly enforces monotonicity while maximizing score sum.
    final_pairs_map = {} 

    def recursive_align(en_start, en_end, es_start, es_end):
        if en_start >= en_end or es_start >= es_end:
            return

        # Find best candidate strictly within this block
        best_cand = None
        best_score = -1
        
        for cand in all_candidates:
            if (en_start <= cand['en'] < en_end and es_start <= cand['es'] < es_end):
                if cand['score'] > best_score:
                    best_score = cand['score']
                    best_cand = cand
        
        if best_score < 0.4: return

        final_pairs_map[best_cand['en']] = best_cand['es']
        recursive_align(en_start, best_cand['en'], es_start, best_cand['es'])
        recursive_align(best_cand['en'] + 1, en_end, best_cand['es'] + 1, es_end)

    recursive_align(0, len(en_items), 0, len(es_items))
    
    # --- GAP FILLING / SEMANTIC RESCUE ---
    assigned_en_count = len(final_pairs_map)
    
    # Trigger if:
    # 1. Sparse ES TOC (Original Animal Farm case)
    # 2. OR Very Bad Alignment (< 20% matched) AND we have a Model (Blackwater case)
    is_sparse = len(es_items) < len(en_items) * 0.5
    is_poor_match = assigned_en_count < len(en_items) * 0.5
    
    if en_items and (is_sparse or (is_poor_match and model)):
        print(f"Triggering Semantic Rescue: Sparse={is_sparse}, PoorMatch={is_poor_match} ({assigned_en_count}/{len(en_items)})")
        
        if en_toc_dir and es_toc_dir:
            try:
                # 0. Discovery (Same as before)
                found_es_files = []
                try:
                    for f in os.listdir(es_toc_dir):
                        if f.lower().endswith('.xhtml') or f.lower().endswith('.html'):
                             # Filter out explicit ignores if any?
                             found_es_files.append(os.path.join(es_toc_dir, f))
                    
                    # Sort numerically if possible to respect reading order
                    import re
                    def mixed_sort_key(x):
                        fname = os.path.basename(x)
                        nums = re.findall(r'\d+', fname)
                        if nums:
                            return int(nums[0])
                        return 99999
                    
                    found_es_files.sort(key=mixed_sort_key)
                    print(f"DEBUG: Found {len(found_es_files)} total ES files: {[os.path.basename(f) for f in found_es_files]}")
                except Exception as e:
                    print(f"DEBUG: Error scanning ES dir: {e}")
                    found_es_files = []

                # Use discovered files if more comprehensive
                candidate_es_items = [{'path': f} for f in found_es_files] if len(found_es_files) > len(es_items) else es_items

                # ---------------------------------------------------------
                # STRATEGY A: SEMANTIC MATCHING (If Model Available)
                # ---------------------------------------------------------
                if model:
                    print(">>> Using SEMANTIC TOC ALIGNMENT (Neural) <<<")
                    semantic_pairs = semantic_toc.align_tocs_semantically(
                        en_items, candidate_es_items, en_toc_dir, es_toc_dir, model
                    )
                    if semantic_pairs:
                        print(f"Semantic Alignment returned {len(semantic_pairs)} pairs. Using them.")
                        return semantic_pairs
                    else:
                        print("Semantic Alignment returned no results. Falling back to Proportional.")
                else:
                    print("Neural Model not provided to align_tocs. Skipping Semantic Alignment.")

                # STRATEGY B: PROPORTIONAL (Fallback)
                # 1. Calculate Sizes (Restored)
                en_sizes = []
                for i, en_item in enumerate(en_items):
                    src_full = en_item['item']['src'].split('#')[0]
                    path = os.path.join(en_toc_dir, src_full)
                    size = os.path.getsize(path) if os.path.exists(path) else 1000
                    en_sizes.append(size)

                # If discovery found more files than TOC, use the discovered list
                # This fixes 'Animal Farm' where TOC has 52, 53 but content is 50, 51, 52, 53
                if len(found_es_files) > len(es_items):
                     print("Using DISCOVERED file list for assignment instead of sparse TOC.")
                     # Rebuild es_files list from hard drive
                     es_files = []
                     es_file_map = {}
                     total_es_size = 0
                     for i, path in enumerate(found_es_files):
                         size = os.path.getsize(path)
                         # Ignore tiny files (wrappers, covers) < 500 bytes?
                         # Be careful, some text might be small. 
                         # But 50.xhtml might be title.
                         es_file_map[path] = i
                         # Use relative path for src
                         rel_src = os.path.basename(path) # Assuming flat structure or simplistic
                         es_files.append({'idx': i, 'size': size, 'path': path, 'src': rel_src, 'cum_start': total_es_size})
                         total_es_size += size
                else:
                    # Fallback to TOC items
                    es_files = [] # (index, size, path)
                    es_file_map = {} # path -> index
                    total_es_size = 0
                    
                    # Get unique ES files in order 
                    # (TOC might point to same file multiple times, but here usually they are distinct or missing)
                    for i, es in enumerate(es_items):
                        path = os.path.join(es_toc_dir, es['item']['src'].split('#')[0])
                        if path not in es_file_map:
                             size = os.path.getsize(path) if os.path.exists(path) else 1000
                             es_file_map[path] = i
                             es_files.append({'idx': i, 'size': size, 'path': path, 'src': es['item']['src'], 'cum_start': total_es_size})
                             total_es_size += size
                
                # Update es_files with cum_end
                current_cum = 0
                for f in es_files:
                    f['cum_start'] = current_cum
                    current_cum += f['size']
                    f['cum_end'] = current_cum
                
                # 2. Assign EN chapters to ES files based on cumulative position
                cum_en = 0
                final_pairs = [] # Rebuild final pairs
                
                for i, en_item in enumerate(en_items):
                    label = en_item['item']['label']
                    en_src = en_item['item']['src']
                    level = en_item['item'].get('level', 0)
                    size = en_sizes[i]
                    
                    # Calculate position: use center of chapter
                    # to distribute evenly.
                    check_pos = cum_en + (size * 0.5)
                    check_ratio = check_pos / max(1, total_en_size)
                    
                    # Find corresponding ES file
                    target_es_pos = check_ratio * total_es_size
                    
                    matched_es_file = None
                    for f in es_files:
                        if target_es_pos >= f['cum_start'] and target_es_pos < f['cum_end']:
                            matched_es_file = f
                            break
                    
                    # Edge case: if last chapter, map to last file
                    if not matched_es_file and es_files:
                        matched_es_file = es_files[-1]
                        
                    if matched_es_file:
                        # es_item might not exist in original es_items if we used discovered list
                        # So we construct the src directly
                        final_pairs.append((label, en_src, matched_es_file['src'], level))
                    else:
                         final_pairs.append((label, en_src, None, level))
                         
                    cum_en += size
                    
                print(f"Proportional assignment completed. Generated {len(final_pairs)} pairs.")
                return final_pairs

            except Exception as e:
                print(f"Proportional TOC assignment failed: {e}")
                # Fall through to original return

    final_pairs = []
    for i, en_item in enumerate(en_items):
        label = en_item['item']['label']
        en_src = en_item['item']['src']
        level = en_item['item'].get('level', 0)
        
        if i in final_pairs_map:
            es_idx = final_pairs_map[i]
            es_item = es_items[es_idx]
            es_src = es_item['item']['src']
            final_pairs.append((label, en_src, es_src, level))
        else:
            final_pairs.append((label, en_src, None, level))
    
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
    return split_sentences_helper(text, language='en')


def split_sentences_aggressive(text):
    """
    Aggressive splitting using Regex (ignores Stanza).
    Used for recovery when Stanza under-splits.
    """
    return _split_sentences_regex(text)

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
            self.ignore_section = True
            self.ignore_depth = 1
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

                if any(c in classes for c in caption_classes) or any('pie_foto' in c.lower() for c in classes):
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
        # Type upgrade is now handled in process_chapter_pair using extract_figure_number
        pass
                 
        super().finish_chunk()

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def clean_text(t):
    return re.sub(r'\s+', ' ', t).strip()



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
        # Detect captions via CSS class (figure/figura)
        elif any(c in ['figure', 'figura', 'figura1', 'caption'] for c in classes):
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



def distribute_chunks(en_chunks, es_chunks, tolerance=0.25):
    """
    Recursively group chunks based on character length ratios.
    Used to resolve structural mismatches (e.g. 2 EN paragraphs vs 1 ES paragraph).
    Returns a list of tuples: [ ( [en_sub], [es_sub] ), ... ]
    """
    # Base cases
    if not en_chunks and not es_chunks:
        return []
    if not en_chunks or not es_chunks:
        return [(en_chunks, es_chunks)]

    total_en = sum(len(c.get('text', '')) for c in en_chunks)
    total_es = sum(len(c.get('text', '')) for c in es_chunks)
    
    if total_es == 0:
        return [(en_chunks, es_chunks)]
        
    target_ratio = total_en / total_es
    
    # We want to find the first split (i, j) that approximates the target ratio
    # Prefer smaller splits to keep granularity
    for i in range(1, len(en_chunks) + 1):
        for j in range(1, len(es_chunks) + 1):
            # Skip the full-block case until the end (it's the fallback)
            if i == len(en_chunks) and j == len(es_chunks):
                continue
                
            sub_en_len = sum(len(c.get('text', '')) for c in en_chunks[:i])
            sub_es_len = sum(len(c.get('text', '')) for c in es_chunks[:j])
            
            if sub_es_len == 0: continue
            
            ratio = sub_en_len / sub_es_len
            
            # Check if ratio is within tolerance (using log difference for symmetry)
            # log(1.25) ~ 0.22. tolerance=0.25 allows ~28% deviation.
            import math
            try:
                error = abs(math.log(ratio / target_ratio))
            except ValueError:
                error = float('inf')
            
            if error < tolerance:
                # Found a good split! Recurse on the remainder
                remainder = distribute_chunks(en_chunks[i:], es_chunks[j:], tolerance)
                return [(en_chunks[:i], es_chunks[:j])] + remainder

    # Fallback: If no good internal split found, return the whole block as one pair
    return [(en_chunks, es_chunks)]




def find_toc_file(base_dir):
    # Try standard name first
    std = os.path.join(base_dir, 'toc.ncx')
    if os.path.exists(std): return std
    # Search recursively
    # Search recursively for NCX
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.ncx'):
                return os.path.join(root, f)
                
    # Fallback: Search for OPF to use as pseudo-TOC
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            if f.endswith('.opf'):
                return os.path.join(root, f)
                
    return None
    
def parse_opf_as_toc(opf_path):
    """
    Parses an OPF file and constructs a flat TOC from the spine.
    Used as fallback when no NCX exists (e.g. Blackwater ES).
    """
    print(f"Parsing OPF as fallback TOC: {opf_path}")
    tree = ET.parse(opf_path)
    root = tree.getroot()
    # Namespace handling
    ns = {'opf': 'http://www.idpf.org/2007/opf'}
    # If no namespace found, try without or check root tag
    if not root.tag.startswith('{http://www.idpf.org/2007/opf}'):
        ns = {} # Or handle differently
        
    # Map manifest IDs to hrefs
    manifest = {}
    for item in root.findall('.//opf:item', ns) or root.findall('.//item'):
        if item.get('id') and item.get('href'):
            manifest[item.get('id')] = item.get('href')
            
    # Read Spine
    toc_items = []
    spine = root.find('.//opf:spine', ns) or root.find('.//spine')
    if spine:
        for itemref in spine.findall('.//opf:itemref', ns) or spine.findall('.//itemref'):
            idref = itemref.get('idref')
            if idref in manifest:
                href = unquote(manifest[idref])
                # Use basename as label since we don't have real titles
                label = os.path.splitext(os.path.basename(href))[0]
                toc_items.append({'label': label, 'src': href, 'level': 0})
                
    return toc_items

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




def process_chapter_pair(args):
    """Thin wrapper around the new footnote-mode aligner pipeline."""
    from aligner.bridge import run_chapter_pair
    return run_chapter_pair(args)


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
    
    # Normalize paths to avoid mismatches
    en_base = os.path.abspath(en_base)
    es_base = os.path.abspath(es_base)
    staging_dir = os.path.abspath(staging_dir)
    
    # 1. Copy Entire Structure
    print(f"--- Starting Fresh Execution for {os.path.basename(output_epub_path)} ---")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)
        
    print(f"Copying original structure from {en_base} to {staging_dir}...")
    shutil.copytree(en_base, staging_dir)

    staging_dir_fixed = None
    verify_mode = config.get('verify_mode')
    if not verify_mode and config.get('verify_llm'):
        verify_mode = 'validate_fix'

    if config and verify_mode == 'validate_fix':
        staging_dir_fixed = staging_dir + "_fixed"
        if os.path.exists(staging_dir_fixed):
            shutil.rmtree(staging_dir_fixed)
        print(f"Copying structure for fixed version to {staging_dir_fixed}...")
        shutil.copytree(en_base, staging_dir_fixed)
    
    staging_info = (staging_dir, staging_dir_fixed, en_base)
    
    # 2. Identify TOC and Pairs
    # We still need to align the structure to know what to inject where.
    # Paths in 'pairs' are relative to the *root* of the unpacked dir (en_base).
    
    en_toc_path = find_toc_file(en_base)
    es_toc_path = find_toc_file(es_base)
    
    if not en_toc_path or not es_toc_path:
        raise FileNotFoundError("TOC file not found in one of the EPUBs.")

    en_toc = parse_toc(en_toc_path)
    es_toc = parse_toc(es_toc_path)
    
    # Enrichment: improve matching by finding subtitles/dates in content
    enrich_toc_from_content(en_toc, os.path.dirname(en_toc_path))
    enrich_toc_from_content(es_toc, os.path.dirname(es_toc_path))
    
    # 2b. Load Neural Model EARLY (if configured)
    # We load it here to pass to Semantic TOC alignment
    model = None
    if config.get('use_neural', True):
        try:
             import logging
             # Reduce SentenceTransformer verbosity
             logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
             
             print("Loading Neural Model (LaBSE) for Alignment...")
             # Use the same device logic as process_chapter_pair
             device_name = 'cpu'
             if torch.backends.mps.is_available(): device_name = 'mps'
             elif torch.cuda.is_available(): device_name = 'cuda'
             
             model = SentenceTransformer('sentence-transformers/LaBSE', device=device_name)
             print(f"Model loaded on {device_name}")
        except Exception as e:
             print(f"Warning: Failed to load neural model early: {e}")
             model = None

    # Use CACHED_ALIGNER if available to improve TOC alignment
    pairs = align_tocs(en_toc, es_toc, 
                       en_toc_dir=os.path.dirname(en_toc_path), 
                       es_toc_dir=os.path.dirname(es_toc_path), 
                       aligner=CACHED_ALIGNER,
                       model=model) # [NEW] Pass model
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
            
            # Append arguments (including model)
            args_list.append( (idx, en_abs, es_abs, es_opf_dir, config, label, chunk_range, model, staging_info) )
            
            # --- DEBUG LIMIT REMOVED ---
            # if len(args_list) >= 6:
            #     print("DEBUG: Limiting to first 6 chapters for verification.")
            #     break
            
        # Replaces the original loop below
        
    except Exception as e:
        print(f"CRITICAL ERROR in Spine Expansion: {e}. Fallback to TOC only.")
        import traceback
        traceback.print_exc()
        # args_list will be empty, triggering fallback below
        args_list = []

    if not args_list: 
         # Fallback loop if args_list wasn't populated (e.g. error above handled silently?)
         
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
            
            args_list.append( (idx, en_abs, es_abs, es_opf_dir, config, label, None, model, staging_info) )

    # 4. Process Chapters (In-Place)
    
    # We already built args_list.
    # Just need to skip the original loop declaration.
    
    # ...
    
    # 5. Process Chapters (ProcessPool -> ThreadPool)
    # Using ThreadPoolExecutor allows efficient sharing of the 'model' object (LaBSE)
    # which is large and unpicklable (or slow to pickle) for Multiprocessing.
    # Since PyTorch releases GIL for heavy ops, threading is efficient here.
    
    print(f"Executing {len(args_list)} content tasks...")
    import concurrent.futures

    # Parallel Processing
    max_workers = 1 if config and config.get('use_neural') else 4
    
    # We don't need to collect results for manifest/spine/images here,
    # as we are modifying in place and the original EPUB structure is preserved.
    # However, process_chapter_pair still returns images, which might be useful for manifest updates.
    all_collected_images = set()
    all_flagged_pairs = []
    all_collected_images = set()
    all_flagged_pairs = []
    total_stats = {'count': 0, 'en_chars': 0, 'es_chars': 0}
    
    try:
        count_done = 0
        total = len(args_list)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(process_chapter_pair, args): i for i, args in enumerate(args_list)}
            
            for future in concurrent.futures.as_completed(future_to_idx):
                i = future_to_idx[future]
                try:
                    res_idx, res_filename, res_label, res_images, res_flagged, res_stats = future.result()
                    if res_images:
                        all_collected_images.update(res_images)
                    if res_flagged:
                        all_flagged_pairs.extend(res_flagged)
                    
                    if isinstance(res_stats, dict):
                        total_stats['count'] += res_stats.get('count', 0)
                        total_stats['en_chars'] += res_stats.get('en_chars', 0)
                        total_stats['es_chars'] += res_stats.get('es_chars', 0)
                    else:
                        total_stats['count'] += res_stats
                except Exception as exc:
                    print(f"Task {i} failed: {exc}")
                    import traceback; traceback.print_exc()
                
                count_done += 1
                if progress_callback: 
                    progress_callback(count_done, total, f"Processed {count_done}/{total}")
                
                if cancel_check and cancel_check():
                    print("Cancellation requested.")
                    break
            
            time.sleep(0.1)
            
            # Wait for all futures to complete (handled by context manager exit)
            pass
        
    except Exception as e:
        print(f"Error during parallel processing: {e}")
        # executor shuts down automatically
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
    
    # Pack fixed version if it exists
    if staging_dir_fixed and os.path.exists(staging_dir_fixed):
        fixed_out_path = output_epub_path.replace('.epub', '_fixed.epub')
        print(f"Packing fixed version to {fixed_out_path}...")
        
        # Ensure mimetype and meta-inf exist in fixed staging
        # We can just copy them from main staging if missing, or generate.
        # But since we copied structure initially, they should be there (or generated by same logic if we duplicated it).
        # To be safe, let's copy mimetype and container from staging_dir logic
        # OR just assume they are there because we copied entire en_base which usually has them,
        # AND we ran logic on them? 
        # Actually logic only runs on staging_dir.
        # So we should copy mimetype and META-INF from staging_dir to staging_dir_fixed to be sure.
        shutil.copy(os.path.join(staging_dir, 'mimetype'), os.path.join(staging_dir_fixed, 'mimetype'))
        if os.path.exists(os.path.join(staging_dir, 'META-INF')):
             if os.path.exists(os.path.join(staging_dir_fixed, 'META-INF')): shutil.rmtree(os.path.join(staging_dir_fixed, 'META-INF'))
             shutil.copytree(os.path.join(staging_dir, 'META-INF'), os.path.join(staging_dir_fixed, 'META-INF'))

        with zipfile.ZipFile(fixed_out_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(os.path.join(staging_dir_fixed, 'mimetype'), 'mimetype', compress_type=zipfile.ZIP_STORED)
            for root, dirs, files in os.walk(staging_dir_fixed):
                for file in files:
                    if file == 'mimetype': continue
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, staging_dir_fixed)
                    zipf.write(file_path, arc_name)
        
        print(f"Fixed EPUB created at: {fixed_out_path}")
        # Clean up fixed staging
        shutil.rmtree(staging_dir_fixed)

    return {'title': new_title, 'language': 'bilingual', 'flagged_pairs': all_flagged_pairs, 'total_pairs': total_stats['count'], 'stats': total_stats}
    
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
    parser.add_argument('--translation-color', type=str, default='grey',
                       help='Color for Spanish translation (e.g., #555555 or grey)')
    parser.add_argument('--preset', type=str, default=None,
                        choices=['default', 'side_by_side', 'color_coded', 'spanish_first', 'spanish_only', 'learner_mode'],
                        help='Use a preset configuration (overrides individual settings)')
    
    # LLM verification options
    parser.add_argument('--verify', action='store_true',
                        help='Use local LLM (Ollama) to verify and fix alignment errors')
    parser.add_argument('--verify-model', type=str, default='mistral-nemo',
                        help='Ollama model for verification (default: mistral-nemo)')
    
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
            style_mode=StyleMode(args.style_mode.lower()),
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
        'verify_llm': args.verify,
        'verify_mode': 'validate_fix' if args.verify else 'none',
        'verify_model': args.verify_model,
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
