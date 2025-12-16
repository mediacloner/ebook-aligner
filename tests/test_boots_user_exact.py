#!/usr/bin/env python3
"""Test exact user input for Boots/Worms issue"""

import sys
sys.path.insert(0, '/Volumes/ExternalHD/Users/alex.sanchez/Documents/repos/AI/ebooks')

import align_book
from dictionary_loader import DictionaryLoader

# Initialize dictionary
if not align_book.DICT_LOADER:
    align_book.DICT_LOADER = DictionaryLoader(check_download=True)

# Exact user input
en_text = """I'd taken off my boots so they wouldn't squeak. I'd removed my socks so I wouldn't slip. The rock under my feet was comfortably cool as I took another silent step forward."""

es_text = """Me había quitado las botas para que no chirriaran. Me había sacado los calcetines para no resbalar. La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante. A tanta profundidad, la única luz procedía del tenue resplandor de los gusanos del techo, que se alimentaban de la humedad que se colaba por las grietas. Había que quedarse parada unos minutos en la oscuridad para que los ojos se adaptaran a una iluminación tan débil."""

print("Testing User's Exact Input...")
print(f"\nEN ({len(en_text)} chars): {en_text[:50]}...")
print(f"ES ({len(es_text)} chars): {es_text[:50]}...\n")

# Create chunks
en_chunks = [{'tag': 'p', 'type': 'std', 'text': en_text, 'classes': []}]
es_chunks = [{'tag': 'p', 'type': 'std', 'text': es_text, 'classes': []}]

# Align
aligned = align_book.align_chunks(en_chunks, es_chunks)

print(f"Aligned count: {len(aligned)}\n")
for i, pair in enumerate(aligned):
    en_preview = pair['en'][:50] + '...' if len(pair['en']) > 50 else pair['en']
    es_preview = pair['es'][:50] + '...' if len(pair['es']) > 50 else pair['es']
    print(f"Pair {i}:")
    print(f"  EN: {en_preview} (len={len(pair['en'])})")
    print(f"  ES: {es_preview} (len={len(pair['es'])})")
    print()

# Check if "A tanta profundidad" is separate
last_pair = aligned[-1] if aligned else None
if last_pair and last_pair['en'] == '' and 'A tanta profundidad' in last_pair['es']:
    print("✓ SUCCESS: 'A tanta profundidad' is correctly separated as orphan")
elif any('A tanta profundidad' in pair['es'] and 'rock' in pair['en'].lower() for pair in aligned):
    print("✗ FAILURE: 'A tanta profundidad' incorrectly merged with 'rock' paragraph")
else:
    print("? UNCLEAR: Need to check output manually")
