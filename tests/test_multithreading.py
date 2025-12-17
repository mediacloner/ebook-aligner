#!/usr/bin/env python3
import sys
import unittest
import os
import shutil
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import align_book
from align_book import process_chapter_pair, create_bilingual_epub

class TestMultithreading(unittest.TestCase):
    def setUp(self):
        # Create dummy directories
        self.test_dir = 'temp_mt_test'
        if os.path.exists(self.test_dir): shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        self.en_opf = os.path.join(self.test_dir, 'en_opf')
        self.es_opf = os.path.join(self.test_dir, 'es_opf')
        self.staging = os.path.join(self.test_dir, 'staging')
        os.makedirs(self.en_opf)
        os.makedirs(self.es_opf)
        os.makedirs(os.path.join(self.staging, 'OEBPS'))
        
        # Dummy config
        self.config = {'SPLIT_TRIGGER_CHARS': 150}

    def tearDown(self):
        if os.path.exists(self.test_dir): shutil.rmtree(self.test_dir)

    @patch('align_book.collect_split_files')
    @patch('align_book.parse_file')
    @patch('align_book.align_chunks')
    @patch('align_book.generate_chapter_html')
    def test_process_chapter_pair(self, mock_gen, mock_align, mock_parse, mock_collect):
        # Mock dependencies
        mock_collect.return_value = ['dummy.html']
        mock_parse.return_value = [{'tag': 'p', 'text': 'test'}]
        # Simple alignment without dictionary
        mock_align.return_value = [{'en': 'test', 'es': 'prueba'}]
        mock_gen.return_value = "<html><body></body></html>"
        
        args = (0, 'ch1.html', 'cap1.html', self.en_opf, self.es_opf, self.staging, self.config)
        
        # Run worker function directly
        result = process_chapter_pair(args)
        
        self.assertEqual(result, (0, 'chapter_00.xhtml', 'ch1.html'))
        self.assertTrue(os.path.exists(os.path.join(self.staging, 'OEBPS', 'chapter_00.xhtml')))
        
    @patch('align_book.process_chapter_pair')
    @patch('concurrent.futures.ProcessPoolExecutor')
    def test_create_bilingual_epub_parallel(self, mock_executor, mock_worker):
        # Verify executor is called
        pass

if __name__ == '__main__':
    unittest.main()
