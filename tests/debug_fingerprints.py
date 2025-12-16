
import sys
import os
import re
sys.path.append(os.getcwd())
from align_book import fingerprint

def debug_fp():
    en_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'I stepped up to the hole and looked out on Igneous. My home cavern and the largest of the underground cities that made up the Defiant League. My perch was high, providing me with a stunning view of a large cave filled with boxy apartments built like cubes splitting off one another.'},
        {'type': 'std', 'tag': 'p', 'text': 'My father’s dream had come true. In defeating the Krell that day over nine years ago, those fledgling starfighter pilots had inspired a nation. Dozens of once-nomadic clans had congregated, colonizing Igneous and the caverns around it. Each clan had its own name still, traced back to the ship or section of the ship they’d worked on. My clan was the Motorskaps—from the old words for engine crew.'},
        {'type': 'std', 'tag': 'p', 'text': 'Together, we called ourselves Defiants. A name taken from our original flagship.'}
    ]
    
    es_chunks = [
        {'type': 'std', 'tag': 'p', 'text': 'Me acerqué al hueco y contemplé Ígnea. Era mi caverna natal y la mayor de las ciudades subterráneas que componían la Liga Desafiante. Desde mi posición elevada, tenía una vista impresionante de la inmensa caverna, llena de apartamentos rectangulares construidos como cubos que salían unos de otros.'},
        {'type': 'std', 'tag': 'p', 'text': 'El sueño de mi padre se había hecho realidad. Al derrotar a los krells aquel día, más de nueve años antes, aquellos pilotos novatos de caza estelar habían inspirado una nación. Decenas de clanes que una vez habían sido nómadas se habían congregado para colonizar Ígnea y las cavernas que la rodeaban. Cada clan conservaba todavía su propio nombre, procedente de la nave o la sección de la nave en la que había trabajado. Mi clan era el de los Makinkaps, que procedía de las antiguas palabras para designar a los técnicos de motores.'},
        {'type': 'std', 'tag': 'p', 'text': 'Todos juntos, nos hacíamos llamar los Desafiantes, por el nombre de nuestra nave insignia original.'}
    ]
    
    print("English Fingerprints:")
    for i, c in enumerate(en_chunks):
        fp = fingerprint(c, 'en')
        print(f"{i}: {fp}")
        
    print("\nSpanish Fingerprints:")
    for i, c in enumerate(es_chunks):
        fp = fingerprint(c, 'es')
        print(f"{i}: {fp}")

if __name__ == "__main__":
    debug_fp()
