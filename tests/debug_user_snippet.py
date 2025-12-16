import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import align_book
from dictionary_loader import DictionaryLoader

def test_user_snippet():
    print("Testing User Snippet Alignment...")
    
    # Initialize Loader
    if not align_book.DICT_LOADER:
        align_book.DICT_LOADER = DictionaryLoader(check_download=True)
        
    en_chunks = [
        {'type': 'std', 'text': 'I stalked my enemy carefully through the cavern.', 'tag': 'p'},
        {'type': 'std', 'text': "I'd taken off my boots so they wouldn't squeak. I'd removed my socks so I wouldn't slip. The rock under my feet was comfortably cool as I took another silent step forward.", 'tag': 'p'},
        {'type': 'std', 'text': 'This deep, the only light came from the faint glow of the worms on the ceiling, feeding off the moisture seeping through cracks. You had to sit for minutes in the darkness for your eyes to adjust to that faint light.', 'tag': 'p'}
    ]
    
    # Case 1: Perfectly separated
    es_chunks = [
        {'type': 'std', 'text': 'Aceché a mi enemigo con sigilo por la caverna.', 'tag': 'p'},
        {'type': 'std', 'text': 'Me había quitado las botas para que no chirriaran. Me había sacado los calcetines para no resbalar. La roca bajo mis pies me transmitió un cómodo frescor al dar otro silencioso paso adelante.', 'tag': 'p'},
        {'type': 'std', 'text': 'A tanta profundidad, la única luz procedía del tenue resplandor de los gusanos del techo, que se alimentaban de la humedad que se colaba por las grietas. Había que quedarse parada unos minutos en la oscuridad para que los ojos se adaptaran a una iluminación tan débil.', 'tag': 'p'}
    ]
    
    print("\n--- Test Case 1: 1-to-1 Alignment ---")
    aligned = align_book.align_chunks(en_chunks, es_chunks)
    for a in aligned:
        print(f"EN: {a['en'][:30]}... | ES: {a['es'][:30]}...")

    # Case 2: ES Merged (Simulating 1-to-N or N-to-1 complexity, forcing 'replace' block analysis)
    # If ES is merged, Phase 4 (Greedy Split) or Phase 1 replacements should handle it.
    print("\n--- Test Case 2: ES Merged (Boots + Worms) ---")
    es_merged = [
        es_chunks[0],
        {'type': 'std', 'text': es_chunks[1]['text'] + " " + es_chunks[2]['text'], 'tag': 'p'}
    ]
    
    aligned_merged = align_book.align_chunks(en_chunks, es_merged)
    for a in aligned_merged:
        print(f"EN: {a['en'][:30]}... | ES: {a['es'][:30]}...")

if __name__ == "__main__":
    test_user_snippet()
