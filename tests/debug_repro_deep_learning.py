import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import EnglishParser, SpanishParser, PROFILES, align_chunks, split_sentences

def fingerprint(c, lang='en', shared_anchors=None, shared_nums=None):
    txt = c['text']
    nums = re.findall(r'\d+', txt)
    
    if shared_nums is not None:
         nums = [n for n in nums if n in shared_nums]
    
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

# Config
config = PROFILES['melanie']

# Files
en_file = 'temp_bilingual/en_full/OEBPS/xhtml/chapter1.xhtml'
es_file = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'

# Parse
p_en = EnglishParser(config)
with open(en_file, 'r', encoding='utf-8') as f:
    p_en.feed(f.read())
p_en.finish_chunk()

p_es = SpanishParser(config)
with open(es_file, 'r', encoding='utf-8') as f:
    p_es.feed(f.read())
p_es.finish_chunk()

# Find the relevant chunks
en_chunk = next(c for c in p_en.chunks if "But since the 2010s" in c['text'])
es_chunk = next(c for c in p_es.chunks if "Sin embargo, desde la pasada década" in c['text'])

print(f"EN Chunk Length: {len(en_chunk['text'])}")
print(f"ES Chunk Length: {len(es_chunk['text'])}")

# Check splitting
print("\n--- SENTENCE SPLITTING ---")
en_sents = split_sentences(en_chunk['text'])
es_sents = split_sentences(es_chunk['text'])

print(f"EN Sentences ({len(en_sents)}):")
for i, s in enumerate(en_sents):
    print(f"[{i}] {s[:60]}... (ends with: {s[-10:]})")

print(f"\nES Sentences ({len(es_sents)}):")
for i, s in enumerate(es_sents):
    print(f"[{i}] {s[:60]}... (ends with: {s[-10:]})")

# Check Alignment if we were to align just this section
print("\n--- ALIGNMENT SIMULATION ---")
aligned = align_chunks([en_chunk], [es_chunk])
for item in aligned:
    print(f"[{item['tag']}] EN: {item['en'][:30]}... | ES: {item['es'][:30]}...")

# Check fingerprints for the first sentences of the chunks
print("\n--- FINGERPRINT DEBUG ---")

# We need to compute shared anchors and NUMS first
en_tokens = set(re.findall(r'\b[A-Z][a-z]{3,}\b', en_chunk['text']))
en_nums = set(re.findall(r'\d+', en_chunk['text']))

es_tokens = set(re.findall(r'\b[A-Z][a-z]{3,}\b', es_chunk['text']))
es_nums = set(re.findall(r'\d+', es_chunk['text']))

shared = en_tokens & es_tokens
shared_nums = en_nums & es_nums
print(f"Shared Anchors: {shared}")
print(f"Shared Nums: {shared_nums}")

c_en_0 = {'text': en_sents[0], 'tag': 'p'}
c_es_0 = {'text': es_sents[0], 'tag': 'p'}

# Now we can pass shared_nums
fp_en_0 = fingerprint(c_en_0, 'en', shared, shared_nums)
fp_es_0 = fingerprint(c_es_0, 'es', shared, shared_nums)
print(f"EN[0]: {en_sents[0][:30]}...")
print(f"EN[0] FP: {fp_en_0}")

print(f"ES[0]: {es_sents[0][:30]}...")
print(f"ES[0] FP: {fp_es_0}")
