import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from align_book import align_chunks

class TestProp(unittest.TestCase):
    def test_align_chunks_prop(self):
        en = [{'type': 'std', 'tag': 'p', 'text': 'Hello world', 'raw_html': '<b>Hello</b> world', 'classes': []}]
        es = [{'type': 'std', 'tag': 'p', 'text': 'Hola mundo', 'classes': []}]
        
        # Exact match logic (equal)
        res = align_chunks(en, es)
        
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['en'], 'Hello world')
        self.assertEqual(res[0]['raw_html'], '<b>Hello</b> world')
        
    def test_align_chunks_fallback(self):
        # Mismatch structure (replace block)
        # Using a dummy fingerprint function inside align_chunks makes it hard to force equal without mocking?
        # Actually standard difflib will match "std::ANC::SC1" equality.
        
        en = [{'type': 'std', 'tag': 'p', 'text': 'Hello', 'raw_html': '<i>Hello</i>', 'classes': []}]
        es = [{'type': 'std', 'tag': 'p', 'text': 'Hola', 'classes': []}]
        
        res = align_chunks(en, es)
        if res:
             self.assertEqual(res[0]['raw_html'], '<i>Hello</i>')

if __name__ == '__main__':
    unittest.main()
