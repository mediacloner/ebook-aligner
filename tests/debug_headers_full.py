
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import EnglishParser, SpanishParser, PROFILES

es_path = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'
config = PROFILES['melanie']

print(f"Parsing {es_path}...")

with open(es_path, 'r', encoding='utf-8') as f:
    content = f.read()

p_es = SpanishParser({'es': config['es']})
p_es.feed(content)
p_es.finish_chunk()

headers = [c for c in p_es.chunks if c['type'] == 'header']
print(f"Total Chunks: {len(p_es.chunks)}")
print(f"Total Headers: {len(headers)}")

print("\n--- DETECTED HEADERS ---")
for h in headers:
    print(f"Tag: {h['tag']}, Classes: {h['classes']}, Text: {h['text'][:50]}...")

print("\n--- CHECKING MISSED CANDIDATES ---")
# Manually check for classes that LOOK like headers but weren't caught
for c in p_es.chunks:
    if c['type'] != 'header':
        cls_str = " ".join(c['classes'])
        if 'capitulo' in cls_str.lower():
            print(f"MISSED candidate? [{c['tag']}] class={c['classes']} Text={c['text'][:50]}...")
