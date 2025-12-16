import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import align_chunks, split_sentences, smart_pair_split, SPLIT_TRIGGER_CHARS

# From English Source (chapter1.xhtml, around page 19)
# Based on grep output earlier, these are separate paragraphs in English.
en_chunks = [
    {'tag': 'p', 'type': 'std', 'text': "Obstacles soon arose that would be familiar to anyone organizing a scientific workshop today. The Rockefeller Foundation came through with only half the requested amount of funding."},
    {'tag': 'p', 'type': 'std', 'text': "And it turned out to be harder than McCarthy had thought to persuade the participants to actually come and then stay, not to mention agree on anything. There were lots of interesting discussions but not a lot of coherence."},
    {'tag': 'p', 'type': 'std', 'text': "As usual in such meetings, “Everyone had a different idea, a hearty ego, and much enthusiasm for their own plan.”"}
]

# From Spanish Source (inteligencia_artificial-5.xhtml)
# Based on find_text.py output, it looks like a continuous flow, likely one p tag or multiple spans inside a p.
# Assuming it is one p tag for the reproduction.
es_chunks = [
    {'tag': 'p', 'type': 'std', 'text': "Pronto surgieron obstáculos que hoy le resultarían familiares a cualquiera que quiera organizar un taller científico. La Fundación Rockefeller solo aportó la mitad del dinero solicitado, y a McCarthy le costó más de lo que creía convencer a los participantes de que acudieran y se quedaran, por no hablar de conseguir que se pusieran de acuerdo en algo. Hubo muchos debates interesantes, pero no mucha coherencia. Como suele suceder en este tipo de reuniones, «todos tenían una idea diferente, un ego importante y mucho entusiasmo por su propio plan»."}
]

print("--- DEBUG MISMATCH ---")
print(f"EN chunks: {len(en_chunks)}")
print(f"ES chunks: {len(es_chunks)}")

aligned = align_chunks(en_chunks, es_chunks)

print(f"\nAligned Pairs: {len(aligned)}")
for i, p in enumerate(aligned):
    print(f"[{i}] {p['tag']}")
    print(f"   EN: {p['en'][:100]}...")
    print(f"   ES: {p['es'][:100]}...")
    print("-" * 20)
