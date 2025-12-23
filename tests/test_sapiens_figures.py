
import unittest
from bs4 import BeautifulSoup
import re

# Mocking the logic found in align_book.py to test it in isolation

def mock_extract_nodes(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    chunks = []
    
    # Target meaningful content elements
    target_tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'blockquote', 'div', 'figcaption']
    
    elements = soup.find_all(target_tags)
    
    for el in elements:
        # Check if this element contains other target elements (simplified for test)
        if el.name != 'figcaption' and el.find(target_tags):
            continue
        
        text = el.get_text().strip()
        if not text:
             continue
            
        # Determine specific type/classes
        classes = el.get('class', [])
        tag = el.name
        
        chunk_type = 'std'
        if tag.startswith('h'):
            chunk_type = 'header'
        
        # --- LOGIC UNDER TEST (Updated from align_book.py) ---
        # Detect captions via CSS class (figure/figura) OR text patterns
        elif any(c in ['figure', 'figura', 'figura1', 'caption'] for c in classes):
            chunk_type = 'caption'
        elif re.match(r'^(?:Figure|Figura|Table|Tabla|Box|Map|Mapa|Fig\.?)\s*\d+\s*[:\.\s]', text, re.IGNORECASE):
            chunk_type = 'caption'
        # Numbered captions starting with just "N." (e.g. "3. A speculative reconstruction...")
        elif re.match(r'^\d+\.\s+\S', text) and len(text) < 500:
            chunk_type = 'caption'
        # -----------------------------------------------------

        chunks.append({
            'text': text,
            'node': el,
            'tag': tag,
            'classes': classes,
            'type': chunk_type
        })
        
    return chunks

def mock_generate_constraints(en_chunks, es_chunks):
    en_filtered = en_chunks
    es_filtered = es_chunks
    constraints = []
    
    # --- LOGIC UNDER TEST (Updated from align_book.py) ---
    
    # 1. Map English Numbers -> Indices
    en_nums = {} # Num -> [list of indices]
    for i, c in enumerate(en_filtered):
        txt = c['text'].strip()
        # Safety: Captions shouldn't be huge paragraphs, unless explicit caption type
        if len(txt) > 300 and c.get('type') != 'caption': continue 

        # Extended pattern: Match "Figure X", "Map X", or just "X." (for numbered captions)
        m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)\s*([\d\.\-]+)', txt, re.IGNORECASE)
        if m:
            num = m.group(1).rstrip('.:,;- ') # Aggr. Normalize
            if num not in en_nums: en_nums[num] = []
            en_nums[num].append(i)
        # Also match numbered captions like "3. A speculative reconstruction..."
        # when chunk is already classified as 'caption' (from class="figure")
        elif c.get('type') == 'caption':
            m2 = re.match(r'^(\d+)\.\s+\S', txt)
            if m2:
                num = m2.group(1)
                if num not in en_nums: en_nums[num] = []
                en_nums[num].append(i)
        
    # 2. Find Matches in Spanish (Monotonic)
    last_en_idx = -1
    
    # --- PRIMARY ANCHORS (Starts with Figure X) ---
    for j, c in enumerate(es_filtered):
        es_loop_txt = c['text'].strip()
        # Safety:
        if len(es_loop_txt) > 300 and c.get('type') != 'caption': continue
        
        # Extended pattern to match FIGURA/MAPA patterns used in Spanish Sapiens
        m = re.match(r'^(?:Figure|Figura|Table|Tabla|Cuadro|Grafico|Map|Mapa|Fig\.?)\s*([\d\.\-]+)', es_loop_txt, re.IGNORECASE)
        
        if m:
            num = m.group(1).rstrip('.:,;- ')
            if num in en_nums:
                # Find first valid English match that preserves monotonicity
                candidates = en_nums[num]
                best_match = -1
                for candidate in candidates:
                    # Enforce strict Type matching for Captions to avoid Body<->Caption misalignment
                    en_type = en_filtered[candidate].get('type')
                    es_type = c.get('type')
                    
                    # Assuming 'caption' type is reliable. If not, maybe relax.
                    if es_type == 'caption' and en_type != 'caption': continue
                    if es_type != 'caption' and en_type == 'caption': continue

                    if candidate > last_en_idx:
                        best_match = candidate
                        break
                if best_match != -1:
                    constraints.append((best_match, j, {'soft': False}))

                    last_en_idx = best_match
    # -----------------------------------------------------
    
    return constraints, en_nums

class TestSapiensAlignment(unittest.TestCase):
    
    def test_caption_detection_and_matching(self):
        # Sample English HTML (Sapiens style)
        en_html = """
        <html><body>
        <p>Some text before.</p>
        <p class="figure"><strong>2.</strong> Some description.</p>
        <p>Text between.</p>
        <p class="figure"><strong>3.</strong> A speculative reconstruction of a Neanderthal child.</p>
        <p class="figure"><strong>Map 2.</strong> Locations of agricultural revolutions.</p>
        </body></html>
        """
        
        # Sample Spanish HTML (Sapiens style)
        es_html = """
        <html><body>
        <p>Texto antes.</p>
        <p class="figura">FIGURA 2. Alguna descripción.</p>
        <p>Texto entre.</p>
        <p class="figura">FIGURA 3. Una reconstrucción especulativa de un niño neandertal.</p>
        <p class="figura">MAPA 2. Ubicaciones de revoluciones.</p>
        </body></html>
        """
        
        en_chunks = mock_extract_nodes(en_html)
        es_chunks = mock_extract_nodes(es_html)
        
        print("\n--- English Chunks ---")
        for i, c in enumerate(en_chunks):
            print(f"{i}: [{c['type']}] {c['text'][:50]}")
            
        print("\n--- Spanish Chunks ---")
        for i, c in enumerate(es_chunks):
            print(f"{i}: [{c['type']}] {c['text'][:50]}")
            
        # Verify Capture Types
        self.assertEqual(en_chunks[1]['type'], 'caption', "English '2.' should be detected as caption")
        self.assertEqual(en_chunks[3]['type'], 'caption', "English '3.' should be detected as caption")
        self.assertEqual(en_chunks[4]['type'], 'caption', "English 'Map 2.' should be detected as caption")
        
        self.assertEqual(es_chunks[1]['type'], 'caption', "Spanish 'FIGURA 2' should be detected as caption")
        self.assertEqual(es_chunks[3]['type'], 'caption', "Spanish 'FIGURA 3' should be detected as caption")
        self.assertEqual(es_chunks[4]['type'], 'caption', "Spanish 'MAPA 2' should be detected as caption")
        
        # Verify Matching Logic
        constraints, en_nums = mock_generate_constraints(en_chunks, es_chunks)
        
        print(f"\nExtracted En Nums: {en_nums.keys()}")
        print(f"Generated Constraints: {constraints}")
        
        # We expect:
        # 2 -> 2
        # 3 -> 3
        # Map 2 (extracted as 2?) -> 2?
        # WAIT: Map 2 might extract as '2'. 
        # If '2' is already in en_nums (from Figure 2), we have conflict?
        # en_nums is dict: num -> list of indices.
        
        # Let's see what numbers were extracted
        self.assertIn('2', en_nums)
        self.assertIn('3', en_nums)
        
        # Check if Map 2 was extracted as '2'
        # The logic: m = re.match(r'^(?:...|Map|Mapa|...)\s*([\d\.\-]+)')
        # It extracts the number group. So "Map 2" -> "2".
        # So '2' should map to indices [1, 4] (Figure 2 and Map 2)
        
        self.assertEqual(len(en_nums['2']), 2, "Should have two occurrences of '2' (Fig 2 and Map 2)")
        
        # Check constraints
        # We want strict monotonic matching.
        # chunks:
        # EN: 0(p), 1(fig2), 2(p), 3(fig3), 4(map2)
        # ES: 0(p), 1(fig2), 2(p), 3(fig3), 4(map2)
        
        # Constraints should be:
        # (1, 1) -> Fig 2 matches Fig 2
        # (3, 3) -> Fig 3 matches Fig 3
        # (4, 4) -> Map 2 matches Map 2
        
        matched_pairs = [(c[0], c[1]) for c in constraints]
        self.assertIn((1, 1), matched_pairs)
        self.assertIn((3, 3), matched_pairs)
        self.assertIn((4, 4), matched_pairs)

        # Additional Test: Complex Cases from Sapiens
        en_html_2 = """
        <html><body>
        <p class="figure"><strong>Map 3.</strong> The world in 1450.</p>
        <p class="figure"><strong>15.</strong> A modern calf in an industrial meat farm.</p>
        <p class="figure"><strong>Table 4.</strong> Population changes.</p>
        </body></html>
        """
        
        es_html_2 = """
        <html><body>
        <p class="figura">MAPA 3. El mundo en 1450.</p>
        <p class="figura">FIGURA 15. Un ternero moderno.</p>
        <p class="tabla">TABLA 4. Cambios de población.</p>
        </body></html>
        """
        
        en_chunks_2 = mock_extract_nodes(en_html_2)
        es_chunks_2 = mock_extract_nodes(es_html_2)
        
        constraints_2, en_nums_2 = mock_generate_constraints(en_chunks_2, es_chunks_2)
        
        print("\n--- Complex Test Output ---")
        print(f"Extracted Numbers: {en_nums_2.keys()}")
        print(f"Constraints: {constraints_2}")

        self.assertIn('3', en_nums_2, "Map 3 should extract '3'")
        self.assertIn('15', en_nums_2, "Figure 15 should extract '15'")
        self.assertIn('4', en_nums_2, "Table 4 should extract '4'")
        
        self.assertEqual(len(constraints_2), 3, "Should match all 3 items")

if __name__ == '__main__':
    unittest.main()
