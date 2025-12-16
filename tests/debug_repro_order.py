
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import EnglishParser, SpanishParser, PROFILES, align_chunks

# Config
config = PROFILES['melanie']

# Files
en_file = 'temp_bilingual/en_full/OEBPS/xhtml/chapter1.xhtml'
es_file = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'

# Parse EN
p_en = EnglishParser(config)
with open(en_file, 'r', encoding='utf-8') as f:
    p_en.feed(f.read())
p_en.finish_chunk()

# Parse ES
p_es = SpanishParser(config)
with open(es_file, 'r', encoding='utf-8') as f:
    p_es.feed(f.read())
p_es.finish_chunk()

# Align
aligned = align_chunks(p_en.chunks, p_es.chunks)

# Expose internal fingerprint logic (copy-paste from align_book.py for testing)
import re
from align_book import split_sentences

def fingerprint(c, lang='en', shared_anchors=None):
    txt = c['text']
    nums = re.findall(r'\d+', txt)
    anchors_list = sorted(list(set(nums)))
    if shared_anchors is not None:
         tokens = re.findall(r'\b[A-Z][a-z]{3,}\b', txt)
         allowed_tokens = [t for t in tokens if t in shared_anchors]
         anchors_list.extend(allowed_tokens)
         anchors_list = sorted(list(set(anchors_list)))
    
    anchor_sig = ""
    if anchors_list: anchor_sig = "ANCHOR:" + "|".join(anchors_list)
    
    sent_count = len(split_sentences(txt))
    if sent_count <= 1: sc_sig = "SC1"
    elif sent_count <= 3: sc_sig = "SC2-3"
    elif sent_count <= 5: sc_sig = "SC4-5"
    else: sc_sig = "SC6+"
    
    return f"{c.get('tag','p')}|{sc_sig}|{anchor_sig}"

# Align (We want to inspect the fingerprints used inside align_chunks -> align_section)
# Simulating the prep done inside align_chunks for the first section
print("\n--- DEBUGGING FINGERPRINTS ---")
en_chunks = p_en.chunks
es_chunks = p_es.chunks

# Headers are roughly at indices 0-3 (En: 0,2; Es: 0,2 from previous output)
# "Two Months" is header at En[2] (index 6, based on previous run output saying index 1 of aligned list was header?)
# Wait, let's just find the chunks corresponding to the text
en_start_chunk = next(c for c in en_chunks if "The dream of creating" in c['text'])
es_start_chunk = next(c for c in es_chunks if "El sueño de crear" in c['text'])

print(f"EN Chunk: {en_start_chunk['text'][:30]}...")
print(f"ES Chunk: {es_start_chunk['text'][:30]}...")

# Calculate Shared Anchors for context
section_en = [en_start_chunk] # Simplified context
section_es = [es_start_chunk]
en_tokens = set()
for c in section_en: en_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
es_tokens = set()
for c in section_es: es_tokens.update(re.findall(r'\b[A-Z][a-z]{3,}\b', c['text']))
shared = en_tokens & es_tokens
print(f"Shared Anchors: {shared}")

fp_en = fingerprint(en_start_chunk, 'en', shared)
fp_es = fingerprint(es_start_chunk, 'es', shared)

print(f"FP EN: {fp_en}")
print(f"FP ES: {fp_es}")
