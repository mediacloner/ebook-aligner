import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import align_book
from dictionary_loader import DictionaryLoader

def test_n_to_1():
    print("Testing N-to-1 Merge (2 EN -> 1 ES) ...")
    
    if not align_book.DICT_LOADER:
        align_book.DICT_LOADER = DictionaryLoader(check_download=True)
        
    en_text_1 = "I'd taken off my boots so they wouldn't squeak. I'd removed my socks so I wouldn't slip. The rock under my feet was comfortably cool as I took another silent step forward."
    en_text_2 = "This deep, the only light came from the faint glow of the worms on the ceiling, feeding off the moisture seeping through cracks. You had to sit for minutes in the darkness for your eyes to adjust to that faint light."
    
    es_combined = "Me había quitado las botas para que no chirriaran. Me había sacado los calcetines para no resbalar. La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante. A tanta profundidad, la única luz procedía del tenue resplandor de los gusanos del techo, que se alimentaban de la humedad que se colaba por las grietas. Había que quedarse parada unos minutos en la oscuridad para que los ojos se adaptaran a una iluminación tan débil."
    
    es_extra = "Otro estremecimiento en las sombras. Allí, cerca de aquellos bultos oscuros que debían de ser las fortificaciones enemigas."
    
    en_chunks = [
        {'type': 'std', 'text': en_text_1, 'tag': 'p'},
        {'type': 'std', 'text': en_text_2, 'tag': 'p'}
    ]
    
    es_chunks = [
        {'type': 'std', 'text': es_combined, 'tag': 'p'},
        {'type': 'std', 'text': es_extra, 'tag': 'p'}
    ]
    
    print(f"\nEN 1: {en_text_1[:30]}...")
    print(f"EN 2: {en_text_2[:30]}...")
    print(f"ES 1 (Combined): {es_combined[:50]}...")
    print(f"ES 2 (Extra): {es_extra[:30]}...")
    
    aligned = align_book.align_chunks(en_chunks, es_chunks)
    
    print(f"\nAligned count: {len(aligned)}")
    for i, a in enumerate(aligned):
        print(f"Pair {i}:")
        print(f"  EN: {a['en'][:50]}...")
        print(f"  ES: {a['es'][:50]}...")
        
    # Validation: 
    # We expect 2 pairs (or 3/4 if splitting sentences).
    # Pair 0 should correspond to EN1
    # Pair 1 should correspond to EN2.
    # ES2 should be left over or marked as extra? Or maybe 3 pairs if it's there.
    # If Pair 0 matches EN1 to ES_Combined, and Pair 1 matches EN2 to ES2, THAT IS WRONG.
    
    # Check Pair 0
    # Ideally EN1 matches first half of ES1.
    
if __name__ == "__main__":
    test_n_to_1()
