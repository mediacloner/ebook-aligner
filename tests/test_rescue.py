import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import align_book
from dictionary_loader import DictionaryLoader
from dictionary_loader import DictionaryLoader

def test_rescue_logic():
    print("Testing Dictionary Rescue Logic...")
    
    # Initialize Loader
    if not align_book.DICT_LOADER:
        align_book.DICT_LOADER = DictionaryLoader(check_download=True)
        
    # Mock Chunks
    # Case 1: Mismatched by Anchor (so difflib sees them as different) but semantically identical
    en_chunks = [{'type': 'std', 'text': 'The computer is fast.', 'tag': 'p'}]
    es_chunks = [{'type': 'std', 'text': 'La computadora es rápida.', 'tag': 'p'}]
    
    print("\n--- Test Case 1: Simple Semantic Match ---")
    # Config to force split trigger high so it doesn't try to split sentences
    config = {'SPLIT_TRIGGER_CHARS': 1000} 
    
    # We expect align_chunks to align them despite structural differences?
    # Actually, for 1 item vs 1 item, difflib usually aligns them if they are the only ones.
    # We need a context where difflib prefers to REPLACE.
    # Let's add noise.
    
    en_chunks = [
        {'type': 'std', 'text': 'Intro.', 'tag': 'p'},
        {'type': 'std', 'text': 'The house is big 123.', 'tag': 'p'}, # Has number
        {'type': 'std', 'text': 'End.', 'tag': 'p'}
    ]
    es_chunks = [
        {'type': 'std', 'text': 'Intro.', 'tag': 'p'},
        {'type': 'std', 'text': 'La casa es grande.', 'tag': 'p'}, # No number
        {'type': 'std', 'text': 'End.', 'tag': 'p'}
    ]
    
    aligned = align_book.align_chunks(en_chunks, es_chunks, config)
    
    print(f"Aligned count: {len(aligned)}")
    for a in aligned:
        print(f"EN: {a['en']} | ES: {a['es']}")
        
    # Verification: Middle chunk should be aligned
    middle = aligned[1]
    match = middle['en'] == 'The house is big 123.' and middle['es'] == 'La casa es grande.'
    if match:
        print("SUCCESS: Dictionary rescued the mismatched chunk!")
    else:
        print("FAILURE: Dictionary did not rescue.")
        # Check if it was treated as replace
        # If replace wasn't rescued, align_section would likely split them or return them as unmatched?
        # In align_section, non-rescued replace blocks define:
        # local_res.extend(sub_aligned) -> which calls align_section recursively.
        # If sentences also don't match, it might map them oddly or leave them.

if __name__ == "__main__":
    test_rescue_logic()
