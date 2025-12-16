import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import align_chunks

def test_issue_13():
    print("Testing Issue 13: Dialogue Merge Split (No Anchors/Few Cognates)")
    
    # English: Item 1 and 2 are separate paragraphs.
    english_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“At the very least,” Mother said, “they fight for irony.” She glanced again at the rats. “Thanks. But get going. Don’t you have the pilot test tomorrow?”', 'es': '', 'text': '“At the very least,” Mother said, “they fight for irony.” She glanced again at the rats. “Thanks. But get going. Don’t you have the pilot test tomorrow?”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“I’m ready for the test,” I said. “Today is just learning things I don’t need to know.”', 'es': '', 'text': '“I’m ready for the test,” I said. “Today is just learning things I don’t need to know.”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Mother gave me an unyielding stare. Every great warrior knew when they were bested, so I gave Gran-Gran a hug and whispered, “Thank you.”', 'es': '', 'text': 'Mother gave me an unyielding stare. Every great warrior knew when they were bested, so I gave Gran-Gran a hug and whispered, “Thank you.”'}
    ]

    # Spanish: Item 1 contains matches for BOTH EN[0] and EN[1].
    spanish_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—Como mínimo, luchan por la ironía —dijo mi madre. Volvió a mirar las ratas—. Gracias. Pero andando, venga. ¿No tienes el examen de piloto mañana? —Estoy preparada para el examen —respondí—. Hoy solo van a aprender cosas que no necesito saber.', 'text': '—Como mínimo, luchan por la ironía —dijo mi madre. Volvió a mirar las ratas—. Gracias. Pero andando, venga. ¿No tienes el examen de piloto mañana? —Estoy preparada para el examen —respondí—. Hoy solo van a aprender cosas que no necesito saber.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Mi madre me siguió mirando, inflexible. Todos los grandes guerreros sabían cuándo estaban derrotados, así que di un abrazo a la yaya y le susurré: —Gracias.', 'text': 'Mi madre me siguió mirando, inflexible. Todos los grandes guerreros sabían cuándo estaban derrotados, así que di un abrazo a la yaya y le susurré: —Gracias.'}
    ]
    
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print("\nResulting Alignment:")
    for idx, item in enumerate(aligned):
        en_snip = item.get('en', '').replace('\n', ' ')
        es_snip = item.get('es', '').replace('\n', ' ')
        print(f"{idx}: EN: '{en_snip}'")
        print(f"    ES: '{es_snip}'")

if __name__ == "__main__":
    test_issue_13()
