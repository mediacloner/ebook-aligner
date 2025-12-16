import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import align_chunks

def test_issue_11():
    print("Testing Issue 11: Scrambled Split (Mrs. Vmeer)")
    
    # Based on user report
    english_chunks = [
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Vmeer drew her lips to a line and didn’t answer.', 'es': '', 'text': 'Vmeer drew her lips to a line and didn’t answer.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“Is it all lies, then?” I asked. “The talk of equality and of only skill mattering? Of finding your right place and serving there?”', 'es': '', 'text': '“Is it all lies, then?” I asked. “The talk of equality and of only skill mattering? Of finding your right place and serving there?”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“It’s complicated,” Mrs. Vmeer said. She lowered her voice. “Look, why don’t you skip the test tomorrow to save everyone the embarrassment? Come to me, and we’ll talk about what might work for you. If not sanitation, perhaps ground troops?”', 'es': '', 'text': '“It’s complicated,” Mrs. Vmeer said. She lowered her voice. “Look, why don’t you skip the test tomorrow to save everyone the embarrassment? Come to me, and we’ll talk about what might work for you. If not sanitation, perhaps ground troops?”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '“So I can stand all day on guard duty?” I said, my voice growing louder. “I need to fly. I need to prove myself!”', 'es': '', 'text': '“So I can stand all day on guard duty?” I said, my voice growing louder. “I need to fly. I need to prove myself!”'},
        # Triggering the issue: "Mrs." split from "Vmeer"
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Mrs.', 'es': '', 'text': 'Mrs.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Vmeer sighed, then shook her head. “I’m sorry, Spensa. I wish one of your teachers had been brave enough to disabuse you of the notion when you were younger.”', 'es': '', 'text': 'Vmeer sighed, then shook her head. “I’m sorry, Spensa. I wish one of your teachers had been brave enough to disabuse you of the notion when you were younger.”'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'In that moment, everything came crashing down around me. A daydreamed future. A carefully imagined escape from my life of ridicule.', 'es': '', 'text': 'In that moment, everything came crashing down around me. A daydreamed future. A carefully imagined escape from my life of ridicule.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Lies. Lies that a part of me had suspected. Of course they weren’t going to let me pass the test. Of course I was too much of an embarrassment to let fly.', 'es': '', 'text': 'Lies. Lies that a part of me had suspected. Of course they weren’t going to let me pass the test. Of course I was too much of an embarrassment to let fly.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'I wanted to rage. I wanted to hit someone, break something, scream until my lungs bled.', 'es': '', 'text': 'I wanted to rage. I wanted to hit someone, break something, scream until my lungs bled.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': 'Instead I strode from the room, away from the laughing eyes of the other students.', 'es': '', 'text': 'Instead I strode from the room, away from the laughing eyes of the other students.'}
    ]

    spanish_chunks = [
        # Assuming typical translation structure
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Vmeer apretó los labios hasta formar una fina línea y no respondió.', 'text': 'Vmeer apretó los labios hasta formar una fina línea y no respondió.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—¿Son todo mentiras, entonces? —pregunté—. ¿Todo eso que dicen de la igualdad y de que lo único importante es la destreza? ¿De encontrar el puesto adecuado para ti y servir en él?', 'text': '—¿Son todo mentiras, entonces? —pregunté—. ¿Todo eso que dicen de la igualdad y de que lo único importante es la destreza? ¿De encontrar el puesto adecuado para ti y servir en él?'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—Es complicado —dijo la señora Vmeer. Bajó la voz—. Mira, ¿por qué no te saltas el examen mañana para ahorrarnos a todos el mal trago? Ven a verme y hablaremos de lo que podría irte bien. Si no te gusta saneamiento, ¿quizá en las tropas terrestres?', 'text': '—Es complicado —dijo la señora Vmeer. Bajó la voz—. Mira, ¿por qué no te saltas el examen mañana para ahorrarnos a todos el mal trago? Ven a verme y hablaremos de lo que podría irte bien. Si no te gusta saneamiento, ¿quizá en las tropas terrestres?'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': '—¿Para pasarme el día entero montando guardia? —repliqué, en voz cada vez más alta—. Necesito volar. ¡Necesito demostrar que valgo!', 'text': '—¿Para pasarme el día entero montando guardia? —repliqué, en voz cada vez más alta—. Necesito volar. ¡Necesito demostrar que valgo!'},
        # Shifted structure to test realignment capability
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'La señora Vmeer suspiró y negó con la cabeza. —Lo siento, Spensa, pero esto era imposible desde el principio.', 'text': 'La señora Vmeer suspiró y negó con la cabeza. —Lo siento, Spensa, pero esto era imposible desde el principio.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Ojalá algún profesor tuyo hubiera tenido la valentía de quitarte la idea de la cabeza cuando eras más pequeña.', 'text': 'Ojalá algún profesor tuyo hubiera tenido la valentía de quitarte la idea de la cabeza cuando eras más pequeña.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'En ese momento, todo se derrumbó a mi alrededor. Un futuro ensoñado. Una huida meticulosamente imaginada de mi vida de escarnio.', 'text': 'En ese momento, todo se derrumbó a mi alrededor. Un futuro ensoñado. Una huida meticulosamente imaginada de mi vida de escarnio.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Mentiras. Mentiras que una parte de mí ya sospechaba. Pues claro que no iban a dejarme aprobar el examen. Pues claro que sería demasiado bochornoso permitirme volar.', 'text': 'Mentiras. Mentiras que una parte de mí ya sospechaba. Pues claro que no iban a dejarme aprobar el examen. Pues claro que sería demasiado bochornoso permitirme volar.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Quería montar en cólera. Quería pegar a alguien, romper algo, chillar hasta que me sangraran los pulmones.', 'text': 'Quería montar en cólera. Quería pegar a alguien, romper algo, chillar hasta que me sangraran los pulmones.'},
        {'tag': 'p', 'type': 'p', 'classes': [], 'en': '', 'es': 'Pero lo que hice fue salir del aula, alejarme de los ojos burlones de los otros alumnos.', 'text': 'Pero lo que hice fue salir del aula, alejarme de los ojos burlones de los otros alumnos.'}
    ]
    
    aligned = align_chunks(english_chunks, spanish_chunks)
    
    print("\nResulting Alignment:")
    for idx, item in enumerate(aligned):
        en_snip = item.get('en', '').replace('\n', ' ')
        es_snip = item.get('es', '').replace('\n', ' ')
        print(f"{idx}: EN: '{en_snip}'")
        print(f"    ES: '{es_snip}'")

if __name__ == "__main__":
    test_issue_11()
