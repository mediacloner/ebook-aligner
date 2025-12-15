from align_book import EnglishParser, SpanishParser, BOOK_CONFIG
import os
import sys

def debug_headers():
    en_path = 'temp_bilingual/en_full/OEBPS/xhtml/chapter1.xhtml'
    es_path = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'
    
    print(f"Checking EN: {en_path}")
    with open(en_path, 'r', encoding='utf-8') as f:
        content_en = f.read()
    
    p_en = EnglishParser(BOOK_CONFIG)
    p_en.feed(content_en)
    p_en.finish_chunk()
    
    en_headers = [c for c in p_en.chunks if c['type'] == 'header']
    print(f"EN Headers ({len(en_headers)}):")
    for h in en_headers:
        print(f"  [{h['tag']}] {h['classes']} : {h['text'][:50]}...")

    print(f"\nChecking ES: {es_path}")
    with open(es_path, 'r', encoding='utf-8') as f:
        content_es = f.read()
    
    p_es = SpanishParser(BOOK_CONFIG)
    p_es.feed(content_es)
    p_es.finish_chunk()
    
    es_headers = [c for c in p_es.chunks if c['type'] == 'header']
    print(f"ES Headers ({len(es_headers)}):")
    for h in es_headers:
        print(f"  [{h['tag']}] {h['classes']} : {h['text'][:50]}...")

if __name__ == "__main__":
    debug_headers()
