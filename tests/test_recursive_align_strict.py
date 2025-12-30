import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from align_book import align_tocs

class MockAligner:
    """Mocks the NeuralAligner to provide deterministic similarity matrices."""
    def __init__(self, matrix_dict):
        # matrix_dict: {(en_idx, es_idx): score}
        self.matrix_dict = matrix_dict

    def embed_chunks(self, chunks):
        # Dummy behavior, not used because we mock the matrix lookup implicitly
        # strictly speaking align_tocs calculates matrix via cdist using embeddings
        # So we need to mock the logic inside align_tocs or patch the matrix.
        return [] 

# Since align_tocs calculates the matrix internally using cdist, 
# it's harder to inject scores directly without patching cdist or the embeddings.
# HOWEVER, we can control `embed_chunks` to return specific distinct vectors.
# But easier is to rely on the fact that align_tocs allows 'aligner' to be None 
# OR use a mock that we can patch "semantic_sim_matrix" into if we modify align_tocs slightly?
# No, align_tocs computes it locally.

# Strategy: We will monkeypatch `align_book.cdist` or use known text inputs 
# and a real aligner? No, user complained tests don't work.
# We will use the fact that `align_tocs` calculates `score` using fuzzy matching 
# AND model. We can force fuzzy matching to be low (using distinct strings) 
# and rely on the mocked matrix if we could inject it.

# Actually, the best way to verify the ALGORITHM (Recursive/Monotonic) 
# is to rely on position logic or fuzzy matches that we construct carefully,
# OR we simply define a MockAligner that behaves predictably.

# Let's try to verify the DATE constraint first. It relies on `normalize_label`.
# We don't need a model for that if the strings align.

class TestRecursiveAlignmentSafe(unittest.TestCase):
    
    def test_date_constraint_mismatch(self):
        """Test that differing dates are rejected (Score 0), preventing alignment."""
        en_toc = [{'label': 'Two Days Later (April 2011)', 'src': 'en1'}]
        es_toc = [{'label': 'Dos dias despues (Agosto 2011)', 'src': 'es1'}]
        
        # Even with no aligner, Fuzzy score would be > 0.
        # But Constraint should kill it.
        pairs = align_tocs(en_toc, es_toc, aligner=None)
        
        # Should be unmatched or matched to None
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][1], 'en1')
        self.assertIsNone(pairs[0][2], "Dates mismatch (April vs August) should NOT align")

    def test_date_constraint_match(self):
        """Test that matching dates align correctly."""
        en_toc = [{'label': 'Two Days Later (April 2011)', 'src': 'en1'}]
        es_toc = [{'label': 'Dos dias despues (Abril 2011)', 'src': 'es1'}]
        
        pairs = align_tocs(en_toc, es_toc, aligner=None)
        
        self.assertEqual(pairs[0][2], 'es1', "Matching dates should align")

    def test_monotonicity_crossing(self):
        """
        Verify recursive logic prevents crossing.
        Setup:
        En1 matches Es2 (Strong)
        En2 matches Es1 (Weak)
        
        If monotonic, picking En1-Es2 forbids En2-Es1.
        """
        en_toc = [
            {'label': 'Chapter One', 'src': 'en1'},
            {'label': 'Chapter Two', 'src': 'en2'}
        ]
        es_toc = [
            {'label': 'Capitulo Dos', 'src': 'es1'}, # Deliberately confusing text
            {'label': 'Capitulo Uno', 'src': 'es2'} 
        ]
        
        # Without model, "Chapter One" ~ "Capitulo Uno" (es2)
        # "Chapter Two" ~ "Capitulo Dos" (es1)
        # If we were greedy/non-monotonic, we might pick One->Uno (en1->es2) AND Two->Dos (en2->es1).
        # This would be CROSSING. En1->Es2, En2->Es1. 
        # Indices: (0->1), (1->0). THIS IS A CROSS.
        
        # Recursive Algorithm should pick the BEST pair first. 
        # Let's say One->Uno is score 0.9. Two->Dos is score 0.9.
        # If it picks One->Uno (0, 1) first:
        #   Left Gap: En[], Es[0] (Unused Es1). 
        #   Right Gap: En[1] (En2), Es[] (Empty).
        # result: En1->Es2. En2->None. Es1 Unused.
        
        pairs = align_tocs(en_toc, es_toc, aligner=None)
        
        # Let's inspect pairs.
        print("\nMonotonicity Test Pairs:", pairs)
        
        es_indices = [p[2] for p in pairs if p[2]]
        # If monotonic, indices must be increasing.
        # es2 is index 1. es1 is index 0.
        # If we have both, it would be [es2, es1] -> [1, 0] -> NOT MONOTONIC.
        # So we should strictly NOT see both if they cross.
        
        mapping = {p[1]: p[2] for p in pairs}
        
        # Expectation: Only one pair survives, or they do not cross.
        # Likely 'Chapter One' ('en1') matches 'Capitulo Uno' ('es2') because 'One'/'Uno' is stronger match?
        # Actually difflib might be close. 
        # Let's just assert that IF both are matched, index(en1_match) < index(en2_match).
        
        if mapping['en1'] and mapping['en2']:
             srcs = [x['src'] for x in es_toc]
             idx1 = srcs.index(mapping['en1'])
             idx2 = srcs.index(mapping['en2'])
             self.assertLess(idx1, idx2, "Resulting alignment crossed! Monotonicity failed.")
        else:
             print("Good: One of the conflicting pairs was dropped to preserve order.")

if __name__ == '__main__':
    unittest.main()
