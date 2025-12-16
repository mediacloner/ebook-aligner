
import sys
import os

path = 'temp_bilingual/es_full/OEBPS/inteligencia_artificial-5.xhtml'
target = "Dos meses y diez hombres"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find(target)
if idx == -1:
    print("TARGET NOT FOUND")
else:
    print(f"FOUND AT {idx}")
    print(content[idx:idx+2000])
