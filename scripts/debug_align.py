
import os
import sys
import argparse
from bs4 import BeautifulSoup
import html

# Mock config
PROFILES = {
    'generic': {
        'en': {
            'header_tags': ['h1', 'h2', 'h3'],
            'header_classes': ['CN', 'CN-Only', 'CT'], 
            'caption_start_tags': ['figcaption'],
            'caption_classes': ['caption'],
            'ignore_tags': [],
            'ignore_classes': [],
            'SPLIT_TRIGGER_CHARS': 240,
            'image_tag': 'img'
        },
        'es': {
            'header_tags': ['h1', 'h2', 'h3', 'p', 'div'],
            'header_indicators': [
                'Capitulos_Capitulo_Numero', 
                'Capitulos_Capitulo_1_Linea', 
                'Subcapitulos_subcapitulo', 
                'Subcapitulos_Subcapitulo'
            ],
            'caption_classes': ['Basico_pie_foto', 'Basico_pie_foto_centrado', 'caption'],
            'ignore_tags': [],
            'ignore_classes': ['_idFootnotes', 'centradoespacioantes', 'capitulo'],
            'merge_headers': True,
            'header_merge_trigger': 'Capitulos_Capitulo_1_Linea',
            'header_merge_targets': ['Capitulos_Capitulo_Numero', 'Capitulos_Capitulo_1_Linea', 'capitulo']
        }
    }
}

# Import local modules
sys.path.append(os.getcwd())
from align_book import extract_nodes, parse_file, SpanishParser
from neural_aligner import NeuralAligner

def debug_alignment(en_path, es_path):
    print(f"--- Debugging Alignment ---")
    print(f"En: {en_path}")
    print(f"Es: {es_path}")
    
    # 1. English Extraction
    print("\n[English Extraction]")
    with open(en_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    en_chunks = extract_nodes(soup)
    print(f"Extracted {len(en_chunks)} English chunks.")
    # Print first 5
    for i, c in enumerate(en_chunks[:5]):
        print(f"  {i}: [{c['tag']}] {c['text'][:50]}...")

    # 2. Spanish Parsing
    print("\n[Spanish Parsing]")
    config = PROFILES['generic']['es']
    # Add generic 'es' config needed for parser
    full_config = {'es': config, 'use_neural': True} 
    
    es_chunks = parse_file(es_path, SpanishParser, full_config)
    print(f"Extracted {len(es_chunks)} Spanish chunks.")
    # Print first 5
    for i, c in enumerate(es_chunks[:5]):
        print(f"  {i}: [{c['tag']}] {c['text'][:50]}...")

    # 3. Neural Alignment
    print("\n[Neural Alignment]")
    aligner = NeuralAligner()
    pairs = aligner.align_dtw(en_chunks, es_chunks)
    
    print(f"\nAligned {len(pairs)} pairs.")
    print("-" * 60)
    print(f"{'IDX':<5} | {'EN (start)':<30} | {'ES (start)':<30} | {'SCORE'}")
    print("-" * 60)
    
    for i, p in enumerate(pairs[:20]):
        ens = p.get('en_chunks', [])
        ess = p.get('es_chunks', [])
        
        en_txt = " | ".join([c['text'][:20] for c in ens]).replace('\n', ' ')
        es_txt = " | ".join([c['text'][:20] for c in ess]).replace('\n', ' ')
        
        print(f"{i:<5} | {en_txt:<40} | {es_txt:<40}")
        
        # Check for obvious mismatches
        # e.g. short vs long, or non-matching starts
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--en', required=True)
    parser.add_argument('--es', required=True)
    args = parser.parse_args()
    
    debug_alignment(args.en, args.es)
