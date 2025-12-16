
import sys
import os
import re
from difflib import SequenceMatcher

def split_sentences(text):
    """Splits text into sentences using simple heuristics."""
    pattern = r'([.!?]+(?:[”"’\'\)\]»]*)\s+(?=[A-Z¿¡"\'\-]))'
    parts = re.split(pattern, text)
    sentences = []
    current_sent = ""
    for i, p in enumerate(parts):
        if i % 2 == 0:
            current_sent += p
        else:
            current_sent += p
            sentences.append(current_sent.strip())
            current_sent = ""
    if current_sent and current_sent.strip():
        sentences.append(current_sent.strip())
    return sentences


def fingerprint(c, lang='en', shared_anchors=None, shared_nums=None):
    """Generates a fingerprint for alignment matching."""
    txt = c.get('text', '')
    
    # Anchors: Numbers
    nums = re.findall(r'\d+', txt)
    if shared_nums is not None:
         nums = [n for n in nums if n in shared_nums]
    
    anchors_list = sorted(list(set(nums)))
    
    # Anchors: Capitalized Tokens
    if shared_anchors is not None:
         tokens = re.findall(r'\b[A-Z][a-z]{3,}\b', txt)
         allowed_tokens = [t for t in tokens if t in shared_anchors]
         anchors_list.extend(allowed_tokens)
         anchors_list = sorted(list(set(anchors_list)))       
    
    # Dialogue Anchor
    is_dialog = False
    s = txt.strip()
    if s:
         if s.startswith('“') or s.startswith('"'): is_dialog = True
         elif s.startswith('—') or s.startswith('-') or s.startswith('–'): is_dialog = True
    
    anchor_sig = ""
    if anchors_list: anchor_sig = "ANCHOR:" + "|".join(anchors_list)
    
    dialog_sig = "DIALOG" if is_dialog else "NARRATION"
    
    # Sentence Count
    sents = split_sentences(txt)
    sc = len(sents)
    sc_sig = f"{sc}"
    
    return f"{c['type']}:{dialog_sig}:{anchor_sig}:{sc_sig}"

def debug_fp_v2():
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
    en_fps = []
    for i, c in enumerate(en_chunks):
        fp = fingerprint(c, 'en')
        en_fps.append(fp)
        print(f"{i}: {fp}")
        
    print("\nSpanish Fingerprints:")
    es_fps = []
    for i, c in enumerate(es_chunks):
        fp = fingerprint(c, 'es')
        es_fps.append(fp)
        print(f"{i}: {fp}")
        
    # Check alignment using DiffLib with these FPs
    print("\nDiffLib Match:")
    matcher = SequenceMatcher(None, en_fps, es_fps)
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        print(f"{tag} EN[{i1}:{i2}] ES[{j1}:{j2}]")

if __name__ == "__main__":
    debug_fp_v2()
