
import sys
import os
sys.path.append(os.getcwd())
import align_book
from align_book import align_chunks

def test_skyward_desync_10():
    # Case: Massive N-to-1 Merge (Issue 9)
    # English has standard paragraph breaks for dialogue.
    # Spanish condenses ALL of it into one paragraph.
    
    english_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Instead, I approached a student at the back of the room—a lanky boy with red hair. He’d immediately opened a book to read once the lecture was done.'},
        {'type': 'std', 'tag': 'p', 'text': '“Rodge,” I said. “Rigmarole!”'},
        {'type': 'std', 'tag': 'p', 'text': 'His nickname—the callsign we’d chosen for him to take once he became a pilot—made him look up. “Spensa! When did you get here?”'},
        {'type': 'std', 'tag': 'p', 'text': '“Middle of the lecture. You didn’t see me come in?”'},
        {'type': 'std', 'tag': 'p', 'text': '“I was going through flight schematics lists in my head. Scud. Only one day left. Aren’t you nervous?”'},
        {'type': 'std', 'tag': 'p', 'text': '“Of course I’m not nervous. Why would I be nervous? I’ve got this down.”'},
        {'type': 'std', 'tag': 'p', 'text': '“Not sure I do.” Rodge glanced back at his textbook.'},
        # Adding next one to check continuity
        {'type': 'std', 'tag': 'p', 'text': '“Are you kidding? You know basically everything. Rig.”'}
    ]
    
    spanish_chunks = [
        # Matches EN[0]
        {'type': 'std', 'tag': 'p', 'text': 'Me acerqué a un alumno que estaba al fondo del aula, un chico pelirrojo y larguirucho. Había abierto un libro para ponerse a leer en el mismo instante en que terminó la charla.'},
        # Matches EN[1]...EN[6] !!
        {'type': 'std', 'tag': 'p', 'text': '—Rodge —lo llamé—. ¡Galimatías! Su apodo, el identificador que le habíamos elegido para cuando se convirtiera en piloto, hizo que levantara la mirada. —¡Spensa! ¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar? —Estaba repasando de memoria las listas de diagramas de vuelo. Tirda, nos queda solo un día. ¿Tú no estás nerviosa? —Pues claro que no. ¿Por qué tendría que estar nerviosa? Lo tengo controlado. —Yo no lo veo tan claro. —Rodge echó una mirada fugaz a su libro de texto.'},
        # Matches EN[7]
        {'type': 'std', 'tag': 'p', 'text': '—¿Estás de broma? Pero si te lo sabes todo, Gali.'}
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
    test_skyward_desync_10()
