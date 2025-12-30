
import sys
import os
import unittest
sys.path.append(os.getcwd())
from align_book import align_tocs
from neural_aligner import NeuralAligner

class TestSemanticTOC(unittest.TestCase):
    def setUp(self):
        # Difficult semantic pairs that fuzzy match usually fails on
        self.en_toc = [
            {'label': 'The Start', 'src': 'ch1.html', 'level': 1},
            {'label': 'Middle Part', 'src': 'ch2.html', 'level': 1},
            {'label': 'Conclusion', 'src': 'ch3.html', 'level': 1}
        ]
        
        self.es_toc = [
            {'label': 'El Comienzo', 'src': 'es1.html', 'level': 1},     # "The Start"
            {'label': 'Parte Central', 'src': 'es2.html', 'level': 1},    # "Middle Part"
            {'label': 'Conclusión', 'src': 'es3.html', 'level': 1}       # "Conclusion"
        ]

    def test_without_aligner(self):
        """Standard fuzzy matching should likely fail or rely purely on position for these."""
        print("\nRunning without aligner...")
        try:
            pairs = align_tocs(self.en_toc, self.es_toc, aligner=None)
            
            # Check p[1] (en_src) and p[2] (es_src)
            matched_start = any(p[1] == 'ch1.html' and p[2] == 'es1.html' for p in pairs if len(p) >= 3)
            print(f"Match 'The Start' <-> 'El Comienzo' (No Model): {matched_start}")
            
        except Exception as e:
             print(f"ERROR: Exception during align_tocs: {e}")
             import traceback
             traceback.print_exc()
        
    def test_with_aligner(self):
        """With aligner, these should match with high confidence."""
        print("\nRunning WITH aligner...")
        try:
            aligner = NeuralAligner()
            pairs = align_tocs(self.en_toc, self.es_toc, aligner=aligner)
            
            matched_start = any(p[1] == 'ch1.html' and p[2] == 'es1.html' for p in pairs if len(p) >= 3)
            matched_middle = any(p[1] == 'ch2.html' and p[2] == 'es2.html' for p in pairs if len(p) >= 3)
            
            print(f"Match 'The Start' <-> 'El Comienzo' (With Model): {matched_start}")
            print(f"Match 'Middle Part' <-> 'Parte Central' (With Model): {matched_middle}")
            
            self.assertTrue(matched_start, "Should match semantically")
            self.assertTrue(matched_middle, "Should match semantically")
            
        except TypeError as e:
            print(f"ERROR: TypeError during align_tocs: {e}")
            import traceback
            traceback.print_exc()
        except Exception as e:
             print(f"ERROR: Exception during align_tocs: {e}")
             import traceback
             traceback.print_exc()

if __name__ == "__main__":
    unittest.main()
