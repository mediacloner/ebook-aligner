import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import align_book
from dictionary_loader import DictionaryLoader

def test_boots_overlap():
    print("Testing Boots/Worms Overlap Issue...")
    
    if not align_book.DICT_LOADER:
        align_book.DICT_LOADER = DictionaryLoader(check_download=True)
        
    # Scenario: 1 EN Chunk vs 1 ES Chunk (which contains EN content + extra content)
    # The 'extra content' corresponds to a 2nd English paragraph that is MISSING here or just merged.
    # If the aligner forces a 1-to-1 match, it's BAD because we lose the granularity.
    # It SHOULD split ES.
    
    en_text = "I'd taken off my boots so they wouldn't squeak. I'd removed my socks so I wouldn't slip. The rock under my feet was comfortably cool as I took another silent step forward."
    
    es_text = "Me había quitado las botas para que no chirriaran. Me había sacado los calcetines para no resbalar. La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante. A tanta profundidad, la única luz procedía del tenue resplandor de los gusanos del techo, que se alimentaban de la humedad que se colaba por las grietas. Había que quedarse parada unos minutos en la oscuridad para que los ojos se adaptaran a una iluminación tan débil."
    
    en_chunks = [{'type': 'std', 'text': en_text, 'tag': 'p'}]
    es_chunks = [{'type': 'std', 'text': es_text, 'tag': 'p'}]
    
    print("\n--- Input ---")
    print(f"EN ({len(en_text)} chars): {en_text[:50]}...")
    print(f"ES ({len(es_text)} chars): {es_text[:50]}...")
    
    aligned = align_book.align_chunks(en_chunks, es_chunks)
    
    print(f"\nAligned count: {len(aligned)}")
    for i, a in enumerate(aligned):
        print(f"Pair {i}:")
        print(f"  EN: {a['en']}")
        print(f"  ES: {a['es'][:50]}... (len={len(a['es'])})")
        
    last_pair_es = aligned[-1]['es']
    if "A tanta profundidad" in last_pair_es:
         print("\nFAILURE: Extra Spanish content ('A tanta profundidad') was incorrectly merged into the last English sentence.")
    else:
         print("\nSUCCESS: Extra content was correctly separated.")

if __name__ == "__main__":
    test_boots_overlap()
