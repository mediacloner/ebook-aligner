import re
import sys
import os

def split_sentences(text):
    # Copy from align_book.py
    pattern = r'([.!?]+(?:[”"’\'\)\]»]*)\s*(?=[A-Z¿¡"\'\-—–]))'
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

def test_split():
    text = "—Rodge —lo llamé—. ¡Galimatías! Su apodo, el identificador que le habíamos elegido para cuando se convirtiera en piloto, hizo que levantara la mirada. —¡Spensa! ¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar? —Estaba repasando de memoria las listas de diagramas de vuelo. Tirda, nos queda solo un día. ¿Tú no estás nerviosa? —Pues claro que no. ¿Por qué tendría que estar nerviosa? Lo tengo controlado. —Yo no lo veo tan claro. —Rodge echó una mirada fugaz a su libro de texto."
    
    print(f"Original Length: {len(text)}")
    sents = split_sentences(text)
    print(f"Split Count: {len(sents)}")
    
    reconstructed = " ".join(sents)
    print(f"Reconstructed Length: {len(reconstructed)}")
    
    for i, s in enumerate(sents):
        print(f"{i}: {s}")

if __name__ == "__main__":
    test_split()
