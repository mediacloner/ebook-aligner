
import sys
import os
import difflib
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import EnglishParser, SpanishParser, PROFILES, align_chunks

# Config
config = PROFILES['melanie']

# Files
en_file = 'temp_bilingual/en_full/OEBPS/xhtml/chapter1.xhtml'
es_file = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'

# Parse
print("--- PARSING EN ---")
p_en = EnglishParser(config)
with open(en_file, 'r', encoding='utf-8') as f:
    p_en.feed(f.read())
p_en.finish_chunk()

# Check parser output for specific headers
found_h1 = False
found_h2 = False
print(f"Total chunks: {len(p_en.chunks)}")
for c in p_en.chunks[:10]: # Check first 10
    if "The Roots of Artificial Intelligence" in c['text']:
        print(f"EN Header 1 Found: Tag={c['tag']}, Classes={c.get('classes')}")
        found_h1 = True
    if "Two Months and Ten Men" in c['text']:
        print(f"EN Header 2 Found: Tag={c['tag']}, Classes={c.get('classes')}")
        found_h2 = True

print(f"Found H1: {found_h1}, H2: {found_h2}")

# Parse ES
print("\n--- PARSING ES ---")
p_es = SpanishParser(config)
with open(es_file, 'r', encoding='utf-8') as f:
    p_es.feed(f.read())
p_es.finish_chunk()

# Align
print("\n--- ALIGNING ---")
aligned = align_chunks(p_en.chunks, p_es.chunks)

# Check alignment result
print(f"Aligned pairs: {len(aligned)}")
for item in aligned:
    en_txt = item['en']
    if "The Roots of Artificial Intelligence" in en_txt:
        print(f"ALIGN RESULT H1: Tag={item['tag']}, Classes={item.get('classes')}")
    if "Two Months and Ten Men" in en_txt:
        print(f"ALIGN RESULT H2: Tag={item['tag']}, Classes={item.get('classes')}")

