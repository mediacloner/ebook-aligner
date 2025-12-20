
import sys
import unittest
from align_book import EnglishParser, PROFILES

class TestCaptionParsing(unittest.TestCase):
    def setUp(self):
        # Use the REAL generic profile
        self.config = PROFILES['generic']

    def test_caption_is_detected(self):
        # HTML structure similar to the book
        html_input = """
        <figcaption><p class="CAP">Figure 30: A chart.</p></figcaption>
        <p class="TX">This is normal text following the figure.</p>
        """
        
        parser = EnglishParser(self.config, html_input)
        parser.feed(html_input)
        parser.close()
        
        # Filter out empty text chunks
        chunks = [c for c in parser.chunks if c['text'].strip()]
        
        # Expectation: 
        # Chunk 0 should be 'caption' -> "Figure 30: A chart."
        # Chunk 1 should be 'std' -> "This is normal text following the figure."
        
        if not chunks:
            self.fail("No chunks parsed")
            
        print("\nParsed Chunks:")
        for i, c in enumerate(chunks):
            print(f"{i}: Type={c['type']}, Tag={c['tag']}, Text='{c['text'][:30]}...'")

        self.assertEqual(chunks[0]['type'], 'caption', f"First chunk should be caption, got {chunks[0]['type']}")
        self.assertEqual(chunks[1]['type'], 'std', "Second chunk should be std")

if __name__ == '__main__':
    unittest.main()
