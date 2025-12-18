import unittest
import sys
import os
from unittest.mock import MagicMock
import numpy as np

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from splitter import Splitter

class TestSplitter(unittest.TestCase):
    def setUp(self):
        self.splitter = Splitter(trigger_length=50) # Low trigger for testing

    def test_sentence_splitting_basic(self):
        text = "Hello world. This is a test."
        sents = self.splitter.split_sentences(text)
        self.assertEqual(len(sents), 2)
        self.assertEqual(sents[0], "Hello world.")
        self.assertEqual(sents[1], "This is a test.")

    def test_sentence_splitting_quotes(self):
        text = '"Hello," she said. "Hi," he replied.'
        sents = self.splitter.split_sentences(text)
        self.assertEqual(len(sents), 2)
        self.assertEqual(sents[0], '"Hello," she said.')
        self.assertEqual(sents[1], '"Hi," he replied.')

    def test_no_trigger_short_text(self):
        en = "Short text."
        es = "Texto corto."
        results = self.splitter.process_pair(en, es)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['en'], en)
        self.assertEqual(results[0]['es'], es)

    def test_trigger_ratio_split(self):
        # Create a long EN text
        # We need the first chunk to be > 50 chars due to hardcoded check in splitter.py
        en_s1 = "This is the first long sentence which is definitely longer than fifty characters now."
        en_s2 = "This is the second long sentence which is also quite long indeed."
        en = f"{en_s1} {en_s2}"
        
        es_s1 = "Esta es la primera frase larga que definitivamente es mas larga que cincuenta caracteres."
        es_s2 = "Esta es la segunda frase larga que tambien es bastante larga."
        es = f"{es_s1} {es_s2}"
        
        # Without aligner, it should use ratio.
        # Ratio EN: 1.0 (approx split check)
        # It should try to split into 2 chunks if chunks > 50 chars.
        
        results = self.splitter.process_pair(en, es)
        
        # Expecting at least 2 chunks because total len > 50 and sentences facilitate split
        self.assertTrue(len(results) >= 2, f"Expected split, got {len(results)}")
        
        # Verify content reconstruction
        reconstructed_en = " ".join([r['en'] for r in results]).replace(" ⁂", "")
        # Note: Splitter adds asterisms ' ⁂'. We should strip them to compare text.
        
        self.assertTrue(en_s1 in reconstructed_en)
        self.assertTrue(en_s2 in reconstructed_en)

    def test_trigger_neural_mock(self):
        # Mock Aligner
        aligner = MagicMock()
        # Mock embed_chunks to return dummy vectors
        # 2 EN chunks -> return 2 vectors
        # 2 ES sents -> return 2 vectors
        # If vectors are identical for index 0 and index 1 respectively, it should map 1-to-1
        
        def mock_embed(chunks):
            # chunks is list of dict {'text': ...}
            # return numpy array of shape (len(chunks), 10)
            return np.random.rand(len(chunks), 10)
            
        aligner.embed_chunks.side_effect = mock_embed
        
        splitter = Splitter(aligner=aligner, trigger_length=50)
        
        en = "Sentence one. Sentence two."
        es = "Frase uno. Frase dos."
        
        # This is probabilistic with random vectors, but we just check it runs without crashing
        # and returns chunks
        results = splitter.process_pair(en, es)
        self.assertTrue(len(results) >= 1)

if __name__ == '__main__':
    unittest.main()
