
import sys
import os
import unittest
import shutil
import tempfile
from sentence_transformers import SentenceTransformer

sys.path.append(os.getcwd())
from align_book import align_tocs

class TestSemanticTOC(unittest.TestCase):
    def setUp(self):
        # Create temp dirs
        self.test_dir = tempfile.mkdtemp()
        self.en_dir = os.path.join(self.test_dir, 'en')
        self.es_dir = os.path.join(self.test_dir, 'es')
        os.makedirs(self.en_dir)
        os.makedirs(self.es_dir)
        
        # Load Model (Global or per test? Loading is slow)
        # We assume clean environment so load it here.
        # To save time, we might check if 'model' is already in sys modules? No.
        print("Loading Model...")
        self.model = SentenceTransformer('sentence-transformers/LaBSE')
        
        # Create Dummy Content
        # Case 1: Mismatched TOC Labels, but Matching Content
        
        self.en_files = {
            'ch1.xhtml': "The quick brown fox jumps over the lazy dog.",
            'ch2.xhtml': "Artificial Intelligence is the future of humanity.",
            'ch3.xhtml': "George Orwell wrote Animal Farm in 1945."
        }
        
        self.es_files = {
            # es1 matches ch1 semantically
            'es_start.xhtml': "El zorro marrón rápido salta sobre el perro perezoso.", 
            # es2 matches ch2
            'es_mid.xhtml': "La Inteligencia Artificial es el futuro de la humanidad.",
            # es3 matches ch3
            'es_end.xhtml': "George Orwell escribió Rebelión en la granja en 1945."
        }
        
        for name, content in self.en_files.items():
            with open(os.path.join(self.en_dir, name), 'w') as f:
                f.write(f"<html><body><p>{content}</p></body></html>")

        for name, content in self.es_files.items():
            with open(os.path.join(self.es_dir, name), 'w') as f:
                f.write(f"<html><body><p>{content}</p></body></html>")
                
        # Define TOCs (Sparse or Mismatched to trigger Semantic logic)
        # We need to trigger the "Gap Filling" condition: 
        # assigned_en_count < len(en_items) * 0.4
        # So we simply provide NO matching TOC labels.
        
        self.en_toc = [
            {'label': 'Chapter One', 'src': 'ch1.xhtml'},
            {'label': 'Chapter Two', 'src': 'ch2.xhtml'},
            {'label': 'Chapter Three', 'src': 'ch3.xhtml'}
        ]
        
        self.es_toc = [
             # Only 1 item to trigger "Sparse" logic?
             # Or Mismatched names.
             # align_tocs logic: 
             # if en_items and es_items and assigned_en_count < len(en_items) * 0.4 ...
             # So we need 'initial alignment' to fail.
             
            {'label': 'Inicio', 'src': 'es_start.xhtml'}, # 'Inicio' != 'Chapter One'
            # Missing others (Sparse)
        ]

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_semantic_alignment(self):
        print("\nRunning Semantic Alignment Test...")
        
        # We pass 'model' to enable Strategy A
        pairs = align_tocs(self.en_toc, self.es_toc, 
                           en_toc_dir=self.en_dir, 
                           es_toc_dir=self.es_dir, 
                           model=self.model)
        
        print("\nResulting Pairs:")
        for p in pairs:
            print(p)
            
        # Verify Mappings
        # label, en_src, es_src, level
        
        # Chapter One (ch1) -> es_start
        self.assertEqual(pairs[0][1], 'ch1.xhtml')
        self.assertEqual(pairs[0][2], 'es_start.xhtml') # Should match via LaBSE
        
        # Chapter Two (ch2) -> es_mid (Discovered!)
        # Wait, align_tocs only scans ONLY if TOC is sparse.
        # My es_toc has only 1 item. EN has 3. 1 < 1.5. So Sparse check PASSES.
        # Discovery should find es_mid and es_end.
        # Then Semantic Align should match them.
        
        self.assertEqual(pairs[1][1], 'ch2.xhtml')
        self.assertEqual(pairs[1][2], 'es_mid.xhtml')
        
        # Chapter Three (ch3) -> es_end
        self.assertEqual(pairs[2][1], 'ch3.xhtml')
        self.assertEqual(pairs[2][2], 'es_end.xhtml')

if __name__ == "__main__":
    unittest.main()
