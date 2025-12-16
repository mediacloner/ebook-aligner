
import sys
import os
sys.path.append(os.getcwd())
import align_book
from align_book import align_chunks

def test_skyward_desync_2():
    # Case: 1-to-N where English P has narration + quote, Spanish splits them.
    # EN: "I'm offering..."
    # ES: "Lo que te ofrezco..."
    # ES: "Necesito un nuevo..."
    
    english_chunks = [
        {'type': 'std', 'tag': 'p', 'text': '“I’m offering you a job. I need a new assistant, and you’re the only one I can trust.”'},
        {'type': 'std', 'tag': 'p', 'text': '“She doesn’t approve,” I whispered.'}
    ]
    
    spanish_chunks = [
        {'type': 'std', 'tag': 'p', 'text': '—Lo que te ofrezco es un trabajo.'}, # Split 1
        {'type': 'std', 'tag': 'p', 'text': 'Necesito un nuevo ayudante, y eres la única en quien puedo confiar.'}, # Split 2
        {'type': 'std', 'tag': 'p', 'text': '—No lo aprueba —susurré.'}
    ]
    
    print("Running align_chunks...")
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print(f"\nResulting Alignment ({len(aligned)} items):")
    for i, item in enumerate(aligned):
        en_txt = item.get('en', '')
        es_txt = item.get('es', '')
        print(f"{i}: Ratio={len(es_txt)/len(en_txt) if en_txt else 0:.2f}")
        print(f"    EN: '{en_txt[:40]}...{en_txt[-40:] if len(en_txt)>40 else ''}'")
        print(f"    ES: '{es_txt[:40]}...{es_txt[-40:] if len(es_txt)>40 else ''}'")

if __name__ == "__main__":
    test_skyward_desync_2()
