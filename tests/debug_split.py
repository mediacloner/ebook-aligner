import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import smart_pair_split, SPLIT_TRIGGER_CHARS

# Snippet with trailing quote - PADDED to force split
filler = "Padding text to make it long enough. " * 10
en_text = filler + 'In fact, the ideas that led to the first programmable computers came out of mathematicians’ attempts to understand human thought—particularly logic—as a mechanical process of “symbol manipulation.” Digital computers are essentially symbol manipulators, pushing around combinations of the symbols 0 and 1.'

# Spanish has quote BEFORE dot
es_text = filler + 'En realidad, las ideas que dieron lugar a los primeros ordenadores programables surgieron de los intentos de los matemáticos de interpretar el pensamiento humano, en especial la lógica, como un proceso mecánico de «manipulación de símbolos». Los ordenadores digitales son esencialmente unos manipuladores de símbolos que juguetean con combinaciones de los símbolos 0 y 1.'

# Force split by setting a low trigger for testing, or just rely on length if it's long enough.
# The text above is short (~300 chars). 'melanie' profile has trigger 240.
# Let's see if it splits.

print(f"EN Len: {len(en_text)}")
print(f"ES Len: {len(es_text)}")

en_chunks, es_chunks = smart_pair_split(en_text, es_text)

print("\n--- SPLIT RESULTS ---")
for i, c in enumerate(en_chunks):
    print(f"EN[{i}]: '{c}'")
for i, c in enumerate(es_chunks):
    print(f"ES[{i}]: '{c}'")
