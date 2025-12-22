
import sys
import os
import re

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import PROFILES, EnglishParser, parse_file

def debug_en_parse(file_path, target_num):
    print(f"--- Parsing {file_path} ---")
    config = PROFILES['generic']
    chunks = parse_file(file_path, EnglishParser, config)
    
    print(f"Extracted {len(chunks)} chunks.")
    
    for i, c in enumerate(chunks):
        txt = c['text'].strip()
        if f"figure {target_num}" in txt.lower():
            print(f"\n[CHUNK {i}] Type: {c.get('type')} Tag: {c.get('tag')} Len: {len(txt)}")
            print(f"Text: '{txt[:100]}...'")
            
            # Test Regex
            m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Fig\.?)\s*([\d\.\-]+)', txt, re.IGNORECASE)
            if m:
                print(f"MATCH: '{m.group(0)}' Num: '{m.group(1)}'")
            else:
                print("NO MATCH")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        debug_en_parse(sys.argv[1], sys.argv[2])
