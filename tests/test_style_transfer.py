import sys
import os
import re

# Add parent directory to path to import align_book
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import generate_chapter_html

def test_style_transfer():
    # Mock aligned pairs
    aligned_pairs = [
        # Case 1: Simple Italics (Whole sentence)
        {
            'tag': 'p',
            'classes': [],
            'en': 'It was a dark night.', # Just text representation
            'raw_html': '<i>It was a dark night.</i>',
            'es': 'Era una noche oscura.',
            'type': 'std'
        },
        # Case 2: Dialogue Pattern (Small + Italic)
        {
            'tag': 'p',
            'classes': ['DIA'],
            'en': 'MOM: The problem...',
            'raw_html': '<small>MOM:</small> <i>The problem with people is...</i>',
            'es': 'mi madre: El problema con la gente es...',
            'type': 'std'
        },
        # Case 3: Partial Italic (Should NOT transfer globally, or requires advanced logic)
        # For now, we might skip this or see if we can handle it.
        # User said "if affect a complete sentence".
        {
            'tag': 'p',
            'classes': [],
            'en': 'He said hello back.',
            'raw_html': 'He said <i>hello</i> back.',
            'es': 'Él dijo hola de vuelta.',
            'type': 'std'
        }
    ]

    html = generate_chapter_html(aligned_pairs, title="Test Style Transfer")
    
    print("Generated HTML Snippet:")
    print(html)
    
    # Assertions
    
    # 1. Whole Italic
    # English
    if '<i>It was a dark night.</i>' in html:
        print("PASS: En 1 preserved")
    # Spanish - Expecting transfer
    if '<span class="es-trans"><i>Era una noche oscura.</i></span>' in html or '<i><span class="es-trans">Era una noche oscura.</span></i>' in html:
        print("PASS: Es 1 style transferred")
    else:
        print("FAIL: Es 1 style NOT transferred")

    # 2. Dialogue
    # English
    if '<small>MOM:</small> <i>The problem with people is...</i>' in html:
        print("PASS: En 2 preserved")
    # Spanish - Expecting smart transfer logic
    # Maybe: <small>mi madre:</small> <i>El problema con la gente es...</i>
    # Or at least finding the colon and splitting?
    expected_es_2_sub = 'mi madre:'
    expected_es_2_main = 'El problema con la gente es...'
    
    if '<small>mi madre:</small>' in html and '<i>El problema con la gente es...</i>' in html:
         print("PASS: Es 2 Dialogue style transferred")
    else:
         print("FAIL: Es 2 Dialogue style NOT transferred")

if __name__ == "__main__":
    test_style_transfer()
