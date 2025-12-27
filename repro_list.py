
from align_book import BilingualAligner, BilingualConfig, BaseParser
from unittest.mock import MagicMock

def test_interleaved_list_alignment():
    # Simulate the Animal Farm case
    # EN: List 1-3, then Comment A, Comment B
    en_texts = [
        "1. Whatever goes upon two legs is an enemy.",
        "2. Whatever goes upon four legs, or has wings, is a friend.",
        "3. No animal shall wear clothes.",
        "It was very neatly written.",  # Comment A
        "All the animals nodded."       # Comment B
    ]
    
    # ES: List 1, Comment A, List 2, Comment B, List 3
    es_texts = [
        "1. Whatever goes upon two legs is an enemy.",
        "Estaba escrito muy claramente.", # Comment A (Interleaved)
        "2. Whatever goes upon four legs, or has wings, is a friend.",
        "Todos los animales asintieron.", # Comment B (Interleaved)
        "3. No animal shall wear clothes."
    ]
    
    # Wrap in chunks
    en_chunks = [{'text': t, 'type': 'p', 'tag': 'p', 'node': MagicMock()} for t in en_texts]
    es_chunks = [{'text': t, 'type': 'p', 'tag': 'p'} for t in es_texts]
    
    # Run Alignment
    config = BilingualConfig()
    aligner = BilingualAligner(config)
    
    # Create simple aligner mock
    aligner.aligner = MagicMock()
    # Mock DTW to mimic monotonic behavior (simplified)
    # If we force 1-1, 2-2, 3-3, the interleaved text gets squashed
    
    # We want to see what constraints are generated
    constraints = []
    
    # Extract logic from process_chapter_pair (manually equivalent)
    # 1. Map Numbers
    import re
    en_nums = {}
    for i, c in enumerate(en_chunks):
        m = re.match(r'^(\d+)\.', c['text'])
        if m:
            en_nums[m.group(1)] = [i]
            
    print(f"EN Nums: {en_nums}")
            
    # 2. Find ES matches
    for j, c in enumerate(es_chunks):
        m = re.match(r'^(\d+)\.', c['text'])
        if m:
            num = m.group(1)
            if num in en_nums:
                print(f"Match found: {num} -> EN:{en_nums[num][0]} ES:{j}")
                constraints.append((en_nums[num][0], j))
                
    print(f"Constraints: {constraints}")
    
    # Expected: (0,0), (1,2), (2,4)
    # This forces "Estaba escrito" (index 1) to align with EN index 0 or 1?
    # EN[0]="1.", EN[1]="2."
    # ES[0]="1.", ES[1]="Comment", ES[2]="2."
    
    # If we constrain 0->0 and 1->2...
    # The gap EN(0..1) is empty. The gap ES(0..2) is "Comment".
    # DTW must assign ES "Comment" to either EN "1." or EN "2.".
    
    print("Test finished")

if __name__ == "__main__":
    test_interleaved_list_alignment()
