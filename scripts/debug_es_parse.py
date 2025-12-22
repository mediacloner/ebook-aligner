
import sys
import os
import re

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import PROFILES, SpanishParser, parse_file

def debug_es_parse(file_path, target_str):
    print(f"--- Parsing {file_path} ---")
    config = PROFILES['generic']
    # Ensure ES config is present
    config['es'] = {
        'caption_classes': ['Basico_pie_foto', 'Basico_pie_foto_centrado', 'caption'],
         'header_tags': ['h1', 'h2', 'h3', 'class:chapter-title', 'class:title'],
         'ignore_classes': [],
         'ignore_div_classes': []
    }
    
    chunks = parse_file(file_path, SpanishParser, config)
    
    print(f"Extracted {len(chunks)} chunks.")
    
    for i, c in enumerate(chunks):
        txt = c['text'].strip()
        if target_str.lower() in txt.lower():
            print(f"\n[CHUNK {i}] Type: {c.get('type')} Tag: {c.get('tag')} Class: {c.get('classes')}")
            print(f"CONTENT: '{txt[:200]}...'")
            
            # Test Regex
            m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Fig\.?)\s*([\d\.\-]+)', txt, re.IGNORECASE)
            if m:
                print(f"REGEX MATCH: '{m.group(0)}' Num: '{m.group(1)}'")
            else:
                print("REGEX FAIL")
            
            if i > 0:
                prev_c = chunks[i-1]
                print(f"PREV CHUNK [{i-1}] ({len(prev_c['text'])} chars): ...{prev_c['text'][-100:]}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        debug_es_parse(sys.argv[1], sys.argv[2])
    else:
        print("Usage: python debug_es_parse.py <file> <term>")
