import unittest
import os
import shutil
import tempfile
from align_book import collect_split_files

class TestCollectSplitFiles(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        shutil.rmtree(self.test_dir)
        
    def create_dummy_file(self, filename):
        path = os.path.join(self.test_dir, filename)
        with open(path, 'w') as f:
            f.write("content")
        return path

    def test_generic_index_prefix(self):
        # Create simulated Calibre files
        self.create_dummy_file("index_split_000.html")
        self.create_dummy_file("index_split_001.html")
        target = "index_split_001.html"
        
        # Should only return the target file, NOT both
        result = collect_split_files(target, self.test_dir)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].endswith("index_split_001.html"))
        
    def test_valid_split_prefix(self):
        # Create valid split chapter
        self.create_dummy_file("ch01_split_00.html")
        self.create_dummy_file("ch01_split_01.html")
        target = "ch01_split_00.html"
        
        # Should return both
        result = collect_split_files(target, self.test_dir)
        self.assertEqual(len(result), 2)
        
    def test_excessive_split_safeguard(self):
        # Create 60 split files
        prefix = "overflow"
        for i in range(60):
            self.create_dummy_file(f"{prefix}_split_{i:03d}.html")
            
        target = f"{prefix}_split_000.html"
        # Should trigger safeguard and return only one
        result = collect_split_files(target, self.test_dir)
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].endswith(target))

if __name__ == '__main__':
    unittest.main()
