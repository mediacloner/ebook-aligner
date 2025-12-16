
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import EnglishParser, SpanishParser, PROFILES

en_path = 'temp_bilingual/en_full/OEBPS/xhtml/chapter1.xhtml'
# Assuming 'melanie' profile is now selected or enforced.
config = PROFILES['melanie']

with open(en_path, 'r', encoding='utf-8') as f:
    content = f.read()

p_en = EnglishParser({'en': config['en']})
p_en.feed(content)
p_en.finish_chunk()

headers = [c for c in p_en.chunks if c['type'] == 'header']
print(f"Total Chunks: {len(p_en.chunks)}")
print(f"Total Headers: {len(headers)}")

print("\n--- DETECTED HEADERS ---")
for h in headers:
    print(f"Tag: {h['tag']}, Classes: {h['classes']}, Text: {h['text'][:50]}...")
