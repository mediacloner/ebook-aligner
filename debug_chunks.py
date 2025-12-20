import sys
import os

sys.path.append(os.getcwd())
from align_book import PROFILES, SpanishParser

def inspect_chunks():
    with open('temp_debug_toc/es/ch06.html', 'r') as f:
        es_html = f.read()
        
    config = PROFILES['generic']
    parser = SpanishParser(config, raw_source=es_html)
    parser.feed(es_html)
    parser.finish_chunk()
    chunks = parser.chunks
    
    # Search for "Quintus" and dump surrounding
    found_idx = -1
    for i, c in enumerate(chunks):
        if "Quintus" in c['text']:
            found_idx = i
            break
            
    if found_idx != -1:
        start = max(0, found_idx - 1)
        end = min(len(chunks), found_idx + 5)
        print(f"--- Surrounding Chunks (Index {found_idx}) ---")
        for k in range(start, end):
            print(f"[{k}] Type: {chunks[k]['type']} | Tag: {chunks[k]['tag']}")
            print(f"    Text: {chunks[k]['text'][:100]}")
            print(f"    Classes: {chunks[k].get('classes')}")
            print("-" * 40)
    else:
        print("Could not find 'Quintus' in chunks.")

if __name__ == "__main__":
    inspect_chunks()
