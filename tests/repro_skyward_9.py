
import sys
import os
sys.path.append(os.getcwd())
import align_book
from align_book import align_chunks

def test_skyward_desync_9():
    # Case: Massive 1-to-N Split (Ratio >> 1.8)
    # English text seems to condense or omit the dialogue, or structure is wildly different.
    # EN: 2 Paragraphs.
    # ES: 8 Paragraphs (Dialogue chain).
    
    english_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Instead, I approached a student at the back of the room—a lanky boy with red hair. He’d immediately opened a book to read once the lecture was done.'},
        {'type': 'std', 'tag': 'p', 'text': '“Rodge,” I said. “Rigmarole!”'},
        # Assuming the next match is "—Yo no lo veo..." equivalent?
        # The user provided snippet ends with Spanish text "-Yo no lo veo...".
        # Let's assume the next English paragraph is something that matches that.
        # "I don't see it clearly." (Taking a guess to create an Anchor).
        {'type': 'std', 'tag': 'p', 'text': '“I don’t see it that clearly.” Rodge glanced at his textbook.'}
    ]
    
    spanish_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Me acerqué a un alumno que estaba al fondo del aula, un chico pelirrojo y larguirucho. Había abierto un libro para ponerse a leer en el mismo instante en que terminó la charla.'},
        {'type': 'std', 'tag': 'p', 'text': '—Rodge —lo llamé—. ¡Galimatías!'},
        {'type': 'std', 'tag': 'p', 'text': 'Su apodo, el identificador que le habíamos elegido para cuando se convirtiera en piloto, hizo que levantara la mirada.'},
        {'type': 'std', 'tag': 'p', 'text': '—¡Spensa! ¿Cuándo has llegado?'},
        {'type': 'std', 'tag': 'p', 'text': '—A mitad de la charla. ¿No me has visto entrar?'},
        {'type': 'std', 'tag': 'p', 'text': '—Estaba repasando de memoria las listas de diagramas de vuelo. Tirda, nos queda solo un día. ¿Tú no estás nerviosa?'},
        {'type': 'std', 'tag': 'p', 'text': '—Pues claro que no. ¿Por qué tendría que estar nerviosa? Lo tengo controlado.'},
        {'type': 'std', 'tag': 'p', 'text': '—Yo no lo veo tan claro. —Rodge echó una mirada fugaz a su libro de texto.'}
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
    test_skyward_desync_9()
