
import os
import zipfile
import re
import sys
from bs4 import BeautifulSoup

def normalize(text):
    # Aggressive normalization matching align_book.py
    # Remove all non-digits, or just strip punctuation?
    # align_book uses: r'^(?:Figure|Figura|...)\s*([\d\.\-]+)' and rstrip('.:,;- ')
    m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Fig\.?)\s*([\d\.\-]+)', text.strip(), re.IGNORECASE)
    if m:
        return m.group(1).rstrip('.:,;- ')
    return None

def verify_epub(epub_path):
    print(f"Verifying: {epub_path}")
    
    if not os.path.exists(epub_path):
        print(f"Error: File not found: {epub_path}")
        return False

    failures = []
    total_checked = 0
    passed = 0

    with zipfile.ZipFile(epub_path, 'r') as z:
        # Find all xhtml/html files
        html_files = [f for f in z.namelist() if f.endswith('.xhtml') or f.endswith('.html')]
        html_files.sort()
        
        for fname in html_files:
            soup = BeautifulSoup(z.read(fname), 'xml') # Use XML parser for XHTML
            
            # Find all potential English Figures
            # They might be in <p>, <div>, <figcaption>, etc.
            # We look for text matching "Figure \d" that does NOT have class "es-translation"
            
            # Iterate all text nodes? No, elements.
            # We iterate elements linear order to check siblings.
            
            elements = soup.find_all(['p', 'div', 'figcaption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            
            for i, el in enumerate(elements):
                text = el.get_text().strip()
                # Skip if empty or inside span.es-translation (wait, find_all finds containers)
                
                # Check if this element IS the Spanish translation?
                # The structure is specific:
                # <tag>English Text</tag>
                # <tag><span class="es-translation">Spanish Text</span></tag>
                
                # If this element contains .es-translation span, it IS the translation node.
                if el.find('span', class_='es-translation'):
                    continue
                    
                # So this is a potential English node.
                # Check if it matches Figure pattern
                en_num = normalize(text)
                if not en_num:
                    continue
                
                # It's a Figure!
                total_checked += 1
                
                # Look for Translation Sibling
                # The helper injects it as immediate sibling (next_sibling)
                # But typically find_all returns flat list, so we can check elements[i+1]
                # BUT, bs4 'next_sibling' is safer for DOM structure.
                
                sib = el.find_next_sibling()
                
                if not sib:
                    failures.append(f"[{fname}] Missing Translation Sibling for 'Figure {en_num}': '{text[:30]}...'")
                    continue
                    
                es_span = sib.find('span', class_='es-translation')
                if not es_span:
                    # Maybe it's not the immediate sibling? (e.g. whitespace node)
                    # Check next sibling again?
                    sib = sib.find_next_sibling()
                    if sib: es_span = sib.find('span', class_='es-translation')
                
                if not es_span:
                    failures.append(f"[{fname}] Sibling contains no translation for 'Figure {en_num}'")
                    continue
                    
                es_text = es_span.get_text().strip()
                es_num = normalize(es_text)
                
                if es_num == en_num:
                    passed += 1
                    # print(f"MATCH: {en_num}")
                else:
                    failures.append(f"[{fname}] MISMATCH: EN='{text}' ({en_num}) vs ES='{es_text}' ({es_num})")

    print("\n--- RESULTS ---")
    print(f"Total Figures Potential: {total_checked}")
    print(f"Passed: {passed}")
    print(f"Failed: {len(failures)}")
    
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f)
        return False
    
    return True

if __name__ == "__main__":
    epub = "books/output/Artificial Intelligence (bilingual).epub"
    if len(sys.argv) > 1: epub = sys.argv[1]
    success = verify_epub(epub)
    sys.exit(0 if success else 1)
