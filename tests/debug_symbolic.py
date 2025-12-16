
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from align_book import EnglishParser, SpanishParser, PROFILES

# Exact snippets from grep
en_html = """
<h2 class="H1">Symbolic AI</h2>
<p class="TNI">First let’s look at <i>symbolic AI</i>.</p>
"""

es_html = """
<p class="Subcapitulos_Subcapitulo_1_Salto" lang="es" xml:lang="es"><span lang="es" xml:lang="es">IA simbólica</span></p>
<p class="Basico_Basico_0" lang="es" xml:lang="es"><span lang="es" xml:lang="es">En primer lugar, veamos la IA simbólica.</span></p>
"""

config = PROFILES['melanie']

print("--- DEBUG HEADER DETECTION ---")

# EN
p_en = EnglishParser({'en': config['en']})
p_en.feed(en_html)
p_en.finish_chunk()
print(f"EN Chunks: {len(p_en.chunks)}")
for c in p_en.chunks:
    print(f"  [{c['type']}] {c['tag']} class={c['classes']} Text='{c['text']}'")

print("-" * 20)

# ES
p_es = SpanishParser({'es': config['es']})
p_es.feed(es_html)
p_es.finish_chunk()
print(f"ES Chunks: {len(p_es.chunks)}")
for c in p_es.chunks:
    print(f"  [{c['type']}] {c['tag']} class={c['classes']} Text='{c['text']}'")
