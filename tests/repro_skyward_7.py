
import sys
import os
sys.path.append(os.getcwd())
import align_book
from align_book import align_chunks

def test_skyward_desync_7():
    # Case: 1-to-N Mixed Content Split
    # EN has Narration + Dialogue in one P.
    # ES splits them into separate Ps.
    
    english_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'I stood up, wiping my hands on a rag. I knew how Beowulf would face monsters and dragons . . . but how would he face his mother on a day when he was supposed to be in school? I settled on a noncommittal shrug.'},
        {'type': 'std', 'tag': 'p', 'text': 'Mother eyed me. “He died, you know,” she said. “Beowulf died fighting that dragon.”'}
        # Assuming next paragraph exists to check alignment flow
    ]
    
    spanish_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Me levanté y me limpié las manos con un trapo. Sabía cómo se enfrentó Beowulf a monstruos y dragones, pero ¿cómo se enfrentaría a su madre en un día en el que debería estar en la escuela? Me conformé con un vago encogimiento de hombros.'},
        {'type': 'std', 'tag': 'p', 'text': 'Mi madre me miró.'},
        {'type': 'std', 'tag': 'p', 'text': '—Murió, ¿sabes? —dijo—.'},
        {'type': 'std', 'tag': 'p', 'text': '—Beowulf murió luchando contra ese dragón.'} # Assuming continuation
    ]
    
    print("Running align_chunks...")
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print(f"\nResulting Alignment ({len(aligned)} items):")
    for i, item in enumerate(aligned):
        en_txt = item.get('en', '')
        es_txt = item.get('es', '')
        ratio = len(es_txt)/len(en_txt) if en_txt else 0
        print(f"{i}: Ratio={ratio:.2f}")
        print(f"    EN: '{en_txt[:40]}...{en_txt[-40:] if len(en_txt)>40 else ''}'")
        print(f"    ES: '{es_txt[:40]}...{es_txt[-40:] if len(es_txt)>40 else ''}'")

if __name__ == "__main__":
    test_skyward_desync_7()
