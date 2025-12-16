import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import align_chunks

def test_issue_14():
    print("Testing Issue 14: Scrambled Dialogue (Rodge/Rigmarole)")
    
    # English chunks
    english_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Instead, I approached a student at the back of the room—a lanky boy with red hair. He’d immediately opened a book to read once the lecture was done.', 'es': '', 'text': 'Instead...'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“Rodge,” I said. “Rigmarole!”', 'es': '', 'text': '“Rodge,” I said. “Rigmarole!”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'His nickname—the callsign we’d chosen for him to take once he became a pilot—made him look up. “Spensa!', 'es': '', 'text': 'His nickname... “Spensa!'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'When did you get here?”', 'es': '', 'text': 'When did you get here?”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“Middle of the lecture. You didn’t see me come in?”', 'es': '', 'text': '“Middle of the lecture. You didn’t see me come in?”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“I was going through flight schematics lists in my head.', 'es': '', 'text': '“I was going through flight schematics lists in my head.'}
    ]

    # Spanish chunks (Simulating the scrambling described)
    spanish_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Me acerqué a un alumno que estaba al fondo del aula, un chico pelirrojo y larguirucho. Había abierto un libro para ponerse a leer en el mismo instante en que terminó la charla.', 'text': 'Me acerqué a un alumno que estaba al fondo del aula, un chico pelirrojo y larguirucho. Había abierto un libro para ponerse a leer en el mismo instante en que terminó la charla.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—Rodge —lo llamé—.', 'text': '—Rodge —lo llamé—.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '¡Galimatías! Su apodo, el identificador que le habíamos elegido para cuando se convirtiera en piloto, hizo que levantara la mirada.', 'text': '¡Galimatías! Su apodo, el identificador que le habíamos elegido para cuando se convirtiera en piloto, hizo que levantara la mirada.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—¡Spensa!', 'text': '—¡Spensa!'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar?', 'text': '¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar?'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—Estaba repasando de memoria las listas de diagramas de vuelo.', 'text': '—Estaba repasando de memoria las listas de diagramas de vuelo.'}
    ]
    
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print("\nResulting Alignment:")
    for idx, item in enumerate(aligned):
        en_snip = item.get('en', '').replace('\n', ' ')
        es_snip = item.get('es', '').replace('\n', ' ')
        print(f"{idx}: EN: '{en_snip}'")
        print(f"    ES: '{es_snip}'")

if __name__ == "__main__":
    test_issue_14()
