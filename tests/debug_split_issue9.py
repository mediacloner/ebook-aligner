
import re

def split_sentences(text):
    # Regex from align_book.py (approximate)
    # r'(?<=[.!?])\s+'
    return re.split(r'(?<=[.!?])\s+', text)

def test_split():
    text = "¿Cuándo has llegado? —A mitad de la charla. ¿No me has visto entrar? —Estaba repasando de memoria las listas de diagramas de vuelo. Tirda, nos queda solo un día. ¿Tú no estás nerviosa? —Pues claro que no. ¿Por qué tendría que estar nerviosa? Lo tengo controlado. —Yo no lo veo tan claro. —Rodge echó una mirada fugaz a su libro de texto."
    
    parts = split_sentences(text)
    print(f"Text Length: {len(text)}")
    print(f"Num Parts: {len(parts)}")
    for i, p in enumerate(parts):
        print(f"{i}: '{p}'")

if __name__ == "__main__":
    test_split()
