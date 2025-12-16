import sys
import os
# Add parent dir to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import align_book
from dictionary_loader import DictionaryLoader

def test_seam_bucket():
    print("Testing Seam/Bucket N-to-1 Merge...")
    
    if not align_book.DICT_LOADER:
        align_book.DICT_LOADER = DictionaryLoader(check_download=True)
    
    # English Paragraph 1
    en_1 = "A seam dripped water into a bucket I’d left, and it was half full, so I took a long drink. Cool and refreshing, with a tinge of something metallic."
    
    # English Paragraph 2 (Approximated from Spanish provided by user scenario)
    en_2 = "We didn't know much about the people who had built all that machinery. Like the debris belt, it was already there when our flotilla fell on the planet. They had been human, given that the writing present in places like the ceiling and the floor of that intersection was in human languages."
    
    # English Paragraph 3 (Context)
    en_3 = "And appear..." 
    
    # Merged Spanish
    es_combined = "De una juntura caían gotas de agua a un cubo que había dejado yo allí, y lo encontré medio lleno, así que di un largo sorbo. Estaba fresca y tenía un leve matiz a algo metálico. No sabíamos gran cosa de la gente que había construido toda aquella maquinaria. Al igual que el cinturón de cascotes, ya estaba allí cuando nuestra flotilla cayó en el planeta. Habían sido humanos, dado que la escritura presente en lugares como el techo y el suelo de esa intersección estaba en idiomas humanos."
    
    en_chunks = [
        {'type': 'std', 'text': en_1, 'tag': 'p'},
        {'type': 'std', 'text': en_2, 'tag': 'p'},
         # {'type': 'std', 'text': en_3, 'tag': 'p'} # Keeping it simple 2-to-1 first
    ]
    
    es_chunks = [
        {'type': 'std', 'text': es_combined, 'tag': 'p'}
    ]
    
    print(f"\nEN 1: {en_1[:30]}...")
    print(f"EN 2: {en_2[:30]}...")
    print(f"ES Combined: {es_combined[:50]}...")
    
    aligned = align_book.align_chunks(en_chunks, es_chunks)
    
    print(f"\nAligned count: {len(aligned)}")
    for i, a in enumerate(aligned):
        print(f"Pair {i}:")
        print(f"  EN: {a['en'][:40]}...")
        print(f"  ES: {a['es'][:40]}...")
        
    # Validating the specific target: "No sabíamos" should align with "We didn't know" (which is the last EN chunk).
    found_sabios = False
    for a in aligned:
        if "No sabíamos" in a['es'] and "We didn't know" in a['en']:
            found_sabios = True
            
    if found_sabios:
         print("\nSUCCESS: Split correctly (Found 'No sabíamos' <-> 'We didn't know').")
    else:
         print("\nFAILURE: Did not split correctly.")

if __name__ == "__main__":
    test_seam_bucket()
