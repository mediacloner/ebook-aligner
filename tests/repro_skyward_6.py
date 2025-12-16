
import sys
import os
sys.path.append(os.getcwd())
import align_book
from align_book import align_chunks

def test_skyward_desync_6():
    # Case: Real N-to-1 Merge
    # ES combines two EN paragraphs into one.
    
    english_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'I hiked down to the normal entrance into the cavern. Two soldiers from the ground troops—which barely ever did any real fighting—guarded the way in. Though I knew them both by their first names, they still made me stand to the side as they pretended to call for authorization for me to enter.'},
        {'type': 'std', 'tag': 'p', 'text': 'Really, they just liked making me wait.'},
        {'type': 'std', 'tag': 'p', 'text': 'Every day. Every scudding day.'},
        {'type': 'std', 'tag': 'p', 'text': 'Eventually, Aluko stepped over and began looking through my sack with a suspicious eye.'},
        #{'type': 'std', 'tag': 'p', 'text': '“What kind of contraband...'}
    ]
    
    spanish_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Fui hasta la entrada normal de la caverna. Había dos soldados del ejército de tierra, que apenas entraba jamás en combate, vigilando la entrada. Aunque los conocía a los dos por su nombre de pila, me hicieron quedarme a un lado mientras fingían solicitar autorización para abrirme el paso. En realidad, era solo que les gustaba hacerme esperar.'},
        {'type': 'std', 'tag': 'p', 'text': 'Todos los días. Todos los tirdosos días.'},
        {'type': 'std', 'tag': 'p', 'text': 'Al final, Aluko vino hacia mí y empezó a registrar mi saco con mirada sospechosa.'}
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
    test_skyward_desync_6()
