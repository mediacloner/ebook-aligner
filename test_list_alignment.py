
from align_book import BilingualAligner, BilingualConfig
from unittest.mock import MagicMock
import re

def test_numbered_vs_unnumbered_list():
    """
    Test alignment when EN has explicit numbers but ES does not.
    """
    en_texts = [
        "1. Whatever goes upon two legs is an enemy.",
        "2. Whatever goes upon four legs, or has wings, is a friend.",
        "3. No animal shall wear clothes."
    ]
    
    # ES texts WITHOUT numbers (as reported in latest user paste)
    es_texts = [
        "Todo lo que camina sobre dos pies es un enemigo.",
        "Todo lo que camina sobre cuatro patas, o tenga alas, es un amigo.",
        "Ningún animal usará ropa."
    ]
    
    print("\n--- Testing Numbered (EN) vs Unnumbered (ES) ---")
    
    # Mock chunks
    en_chunks = [{'text': t, 'type': 'p', 'tag': 'p'} for t in en_texts]
    es_chunks = [{'text': t, 'type': 'p', 'tag': 'p'} for t in es_texts]
    
    # Current Logic Simulation
    constraints = []
    en_nums = {}
    
    # 1. Map English Numbers
    for i, c in enumerate(en_chunks):
        txt = c['text'].strip()
        m_list = re.match(r'^(\d+)\.\s+[A-Z]', txt)
        if m_list:
            num = "L" + m_list.group(1)
            en_nums[num] = [i]
            print(f"EN Found: {num} -> '{txt[:20]}...'")
            
    # 2. Find ES matches (Simulating current regex)
    for j, c in enumerate(es_chunks):
        txt = c['text'].strip()
        
        # Current logic looks for number
        found_num = None
        m_list = re.match(r'^(\d+)\.\s+[A-Z]', txt)
        if m_list:
            found_num = "L" + m_list.group(1)
            
        if found_num and found_num in en_nums:
            print(f"ES Match (Current): {found_num} -> '{txt[:20]}...'")
            constraints.append((en_nums[found_num][0], j))
        else:
            print(f"ES No Match (Current) for: '{txt[:20]}...'")
            
    if not constraints:
        print("FAIL: No constraints generated for unnumbered Spanish list.")
    else:
        print(f"SUCCESS: Generated {len(constraints)} constraints.")

if __name__ == "__main__":
    test_numbered_vs_unnumbered_list()
