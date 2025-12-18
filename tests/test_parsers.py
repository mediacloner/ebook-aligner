import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import BaseParser, EnglishParser, clean_text

class TestParsers(unittest.TestCase):
    def test_base_parser_splitting_br(self):
        # We need a parser that uses BaseParser logic
        # EnglishParser inherits from it
        config = {'en': {'header_tags': ['h1'], 'caption_tag': 'figcaption'}}
        parser = EnglishParser(config)
        
        # Input HTML with BR
        html_content = "<p>Line 1.<br/>Line 2.</p>"
        parser.feed(html_content)
        parser.finish_chunk()
        
        # We expect 2 chunks if <br> splits
        # Line 1. should be one chunk (p)
        # Line 2. should be another chunk (p)
        # Note: BaseParser logic with finish_chunk pushes current_chunk to chunks list
        
        chunks = parser.chunks
        
        # Let's inspect what we got
        # Current logic: handle_starttag('br') -> calls finish_chunk()
        # So "Line 1." -> finish_chunk -> stored.
        # Then "Line 2." -> handle_data -> stored in new current_chunk?
        # WAIT. finish_chunk sets current_chunk = None.
        # handle_data checks if self.current_chunk:
        # If processing <p>, we are inside a chunk.
        # <br> closes it.
        # Then "Line 2." arrives. handle_data checks current_chunk. It is NONE!
        # Result: "Line 2." might be dropped if we don't re-open a chunk?
        # We need to verify this behavior.
        
        self.assertEqual(len(chunks), 2, f"Expected 2 chunks, got {len(chunks)}")
        self.assertEqual(chunks[0]['text'].strip(), "Line 1.")
        self.assertEqual(chunks[1]['text'].strip(), "Line 2.")

if __name__ == '__main__':
    unittest.main()
