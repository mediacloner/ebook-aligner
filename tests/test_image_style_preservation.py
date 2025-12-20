import unittest
import sys
import os

# Add parent directory to path to import align_book
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import EnglishParser, generate_chapter_html

class TestImageStylePreservation(unittest.TestCase):
    def test_image_inherits_parent_classes(self):
        html = '<p class="wdh1 custom-style"><img src="image.jpg" alt="test" /></p>'
        config = {'en': {'header_tags': ['h1'], 'image_tags': ['img']}}
        parser = EnglishParser(config)
        parser.feed(html)
        parser.finish_chunk()
        
        chunks = parser.chunks
        # Find image chunk
        img_chunk = next((c for c in chunks if c.get('type') == 'image'), None)
        
        self.assertIsNotNone(img_chunk)
        self.assertIn('wdh1', img_chunk['classes'])
        self.assertIn('custom-style', img_chunk['classes'])

    def test_html_generation_applies_classes(self):
        # Simulate aligned item with classes
        aligned_item = {
            'tag': 'img',
            'type': 'image',
            'src': 'pic.jpg',
            'alt': 'Pic', 
            'en': '', 'es': '',
            'classes': ['wdh1', 'center-me']
        }
        
        html = generate_chapter_html([aligned_item], "Test Chapter")
        
        # Verify output structure
        self.assertIn('<div class="image-container wdh1 center-me">', html)
        self.assertIn('<img src="pic.jpg"', html)

if __name__ == '__main__':
    unittest.main()
