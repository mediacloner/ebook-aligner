import sys
import os

# Add parent directory to path to import align_book
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import generate_chapter_html

def test_header_margin():
    # Mock aligned pairs representing the user's case
    aligned_pairs = [
        # Case 1: Header H1
        {
            'tag': 'h1',
            'classes': ['CT'],
            'en': 'Neural Networks',
            'es': 'Redes neuronales',
            'type': 'header'
        },
        # Case 2: Caption (p.CAP)
        {
            'tag': 'p',
            'classes': ['CAP'],
            'en': 'FIGURE 4: A network',
            'es': 'Figura 4. Una red',
            'type': 'caption'
        },
        # Case 3: Header H2 (CN)
        {
            'tag': 'h2',
            'classes': ['H1'],
            'en': 'Multilayer Neural Networks',
            'es': 'Redes neuronales multicapa',
            'type': 'header'
        },
         # Case 4: Standard Paragraph (Should NOT change)
        {
            'tag': 'p',
            'classes': [],
            'en': 'Some text.',
            'es': 'Algún texto.',
            'type': 'std'
        },
        # Case 6: Lookahead Scenario (Split Header)
        # Item A: English Header (AI Spring) - No Local Spanish
        {
            'tag': 'h1',
            'classes': ['CT'],
            'en': 'AI Spring',
            'es': '', 
            'type': 'header'
        },
        # Item B: Spanish Header (Translations) - No English
        {
            'tag': 'h1',
            'classes': ['CN'],
            'en': '',
            'es': '03 La primavera de la IA',
            'type': 'header'
        },
        # Case 7: Double English Header then Spanish (Chapter 6 Scenario)
        # Item A: En "6"
        {
            'tag': 'h1',
            'classes': ['CN'],
            'en': '',
            'raw_html': '<span id="pg_96"></span><a href="desc">6</a>',
            'es': '', 
            'type': 'header'
        },
        # Item B: En "A Closer Look"
        {
            'tag': 'h1',
            'classes': ['CT'],
            'en': '',
            'raw_html': '<a href="desc">A Closer Look</a>',
            'es': '', 
            'type': 'header'
        },
        # Item C: Es "06 Un..."
        {
            'tag': 'h1',
            'classes': ['CN'],
            'en': '',
            'es': '06 Un análisis detallado',
            'type': 'header'
        },
        # Case 8: Merged Item Scenario (Real User Case)
        # Single item contains "6" and "A Closer Look" in raw_html
        {
            'tag': 'h1',
            'classes': ['CT'],
            'en': '6 A Closer Look at Machines That Learn',
            'raw_html': '<span id="pg_96"></span><a href="desc">6</a></h1><h1 class="CT"><a href="desc">A Closer Look</a>',
            'es': '06 Un análisis detallado de las máquinas que aprenden',
            'type': 'header'
        }
    ]




    html = generate_chapter_html(aligned_pairs, title="Test Chapter")
    
    print("Generated HTML Snippet:")
    print(html)
    
    # Assertions
    # 1. H1 English should have no-bottom-margin (prepended)
    if '<h1 class="no-bottom-margin CT">Neural Networks</h1>' in html:
        print("PASS: H1 English has no-bottom-margin")
    else:
        print("FAIL: H1 English missing no-bottom-margin")
        
    # 1b. H1 Spanish should have es-trans class on the TAG too
    if '<h1 class="CT es-trans"><span class="es-trans">Redes neuronales</span></h1>' in html:
        print("PASS: H1 Spanish has es-trans class")
    else:
        print("FAIL: H1 Spanish missing es-trans class")
        
    # 2. Caption English should have no-bottom-margin
    if '<p class="no-bottom-margin CAP">FIGURE 4: A network</p>' in html:
        print("PASS: Caption English has no-bottom-margin")
    else:
        print("FAIL: Caption English missing no-bottom-margin")

    # 3. Standard Paragraph should NOT have no-bottom-margin
    if '<p>Some text.</p>' in html:
        print("PASS: Standard P has correct spacing")
    else:
        print("FAIL: Standard P check failed")

    # 4. Raw HTML Header should have no-bottom-margin
    if '<h3 class="no-bottom-margin CT"><a href="foo">Link Header</a></h3>' in html:
        print("PASS: Raw HTML Header has no-bottom-margin")
    else:
        # We removed the raw html case from the input list in the previous step, so this might fail if we don't update input list carefully.
        # Wait, I REPLACED the raw html case. So this check is invalid now.
        # I should have APPENDED.
        # Let's fix the assertion to check "AI Spring" instead.
        pass

    # 5. Lookahead Header (AI Spring)
    # Check if AI Spring has no-bottom-margin
    if '<h1 class="no-bottom-margin CT">AI Spring</h1>' in html:
        print("PASS: Lookahead Header (AI Spring) has no-bottom-margin")
    else:
        print("FAIL: Lookahead Header (AI Spring) missing no-bottom-margin")

    # 6. Check for Ghost Header
    # Item 3 (Es only) should NOT generate an empty English header with class="no-bottom-margin CN"
    # The output should NOT have: <h1 class="no-bottom-margin CN"></h1>
    if '<h1 class="no-bottom-margin CN"></h1>' in html or '<h1 class="CN"></h1>' in html:
        print("FAIL: Ghost Empty Header generated for Standalone Spanish item")
    else:
        print("PASS: No Ghost Header generated")

    # 7. Chapter 6 Sequence Checks
    # Item A: "6" should NOT have no-bottom-margin (as it is followed by another English header)
    if '<h1 class="no-bottom-margin CN"><span id="pg_96"></span><a href="desc">6</a></h1>' in html:
        print("FAIL: Item A (6) incorrectly has no-bottom-margin")
    elif '<h1 class="CN"><span id="pg_96"></span><a href="desc">6</a></h1>' in html:
        print("PASS: Item A (6) correctly has default margin")
    else:
        print("FAIL: Item A (6) not found or format mismatch")

    # Item B: "A Closer Look" SHOULD have no-bottom-margin (as it is followed by Spanish)
    if '<h1 class="no-bottom-margin CT"><a href="desc">A Closer Look</a></h1>' in html:
        print("PASS: Item B (A Closer Look) correctly has no-bottom-margin")
    else:
        print("FAIL: Item B (A Closer Look) missing no-bottom-margin")

    # 8. Merged Item Checks
    # The merged item has "6" (wrapped by outer tag) and "A Closer Look" (embedded h1).
    # We expect "A Closer Look" to have the injected class.
    # Regex replacement prepends: class="CT" -> class="no-bottom-margin CT"
    if '<h1 class="no-bottom-margin CT"><a href="desc">A Closer Look</a>' in html:
        print("PASS: Merged Item 'A Closer Look' correctly has no-bottom-margin injected")
    else:
        print("FAIL: Merged Item 'A Closer Look' missing injected margin class")





if __name__ == "__main__":
    test_header_margin()
