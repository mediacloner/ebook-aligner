import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import align_chunks

def test_issue_12():
    print("Testing Issue 12: Gran-Gran Split (Missing Anchor Split)")
    
    # English: "But she was still..." is a separate paragraph.
    english_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Gran-Gran looked up, hearing me. Her name was Becca Nightshade—I shared her last name—but even those who barely knew her called her Gran-Gran. She had lost nearly all her sight a few years ago, her eyes having gone a milky white. She was hunched over and worked with sticklike arms.', 'es': '', 'text': 'Gran-Gran looked up, hearing me. Her name was Becca Nightshade—I shared her last name—but even those who barely knew her called her Gran-Gran. She had lost nearly all her sight a few years ago, her eyes having gone a milky white. She was hunched over and worked with sticklike arms.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'But she was still the strongest person I knew.', 'es': '', 'text': 'But she was still the strongest person I knew.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“Oooh,” she said. “That sounds like Spensa! How many did you get today?”', 'es': '', 'text': '“Oooh,” she said. “That sounds like Spensa! How many did you get today?”'}
    ]

    # Spanish: Merged the two English paragraphs into one big one.
    spanish_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'La yaya alzó la mirada al oírme. Se llamaba Becca Nightshade —yo tenía el mismo apellido—, pero incluso quienes apenas la conocían la llamaban yaya. Había perdido la visión casi por completo hacía unos años y sus ojos se habían puesto de un blanco lechoso. Estaba encorvada y trabajaba con unos brazos flacos como palos, pero aun así era la persona más fuerte que conocía.', 'text': 'La yaya alzó la mirada al oírme. Se llamaba Becca Nightshade —yo tenía el mismo apellido—, pero incluso quienes apenas la conocían la llamaban yaya. Había perdido la visión casi por completo hacía unos años y sus ojos se habían puesto de un blanco lechoso. Estaba encorvada y trabajaba con unos brazos flacos como palos, pero aun así era la persona más fuerte que conocía.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—¡Anda! —exclamó—.', 'text': '—¡Anda! —exclamó—.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '¡Pero si suena a que llega Spensa! ¿Cuántas has cazado hoy?', 'text': '¡Pero si suena a que llega Spensa! ¿Cuántas has cazado hoy?'}
    ]
    
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print("\nResulting Alignment:")
    for idx, item in enumerate(aligned):
        en_snip = item.get('en', '').replace('\n', ' ')
        es_snip = item.get('es', '').replace('\n', ' ')
        print(f"{idx}: EN: '{en_snip}'")
        print(f"    ES: '{es_snip}'")

if __name__ == "__main__":
    test_issue_12()
