import unittest
import sys
import os

# Add parent directory to path to import align_book
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import align_chunks, generate_chapter_html, EnglishParser, SpanishParser

class TestImageAlignment(unittest.TestCase):
    def test_parser_img_tag(self):
        html = '<p>Text</p><img src="image.jpg" alt="An image" /><p>More text</p>'
        parser = EnglishParser({'en': {'image_tag': 'img'}}, raw_source=html)
        parser.feed(html)
        parser.finish_chunk()
        
        chunks = parser.chunks
        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[0]['tag'], 'p')
        self.assertEqual(chunks[1]['tag'], 'img')
        self.assertEqual(chunks[1]['src'], 'image.jpg')
        self.assertEqual(chunks[1]['alt'], 'An image')
        self.assertEqual(chunks[1]['type'], 'image')
        self.assertEqual(chunks[2]['tag'], 'p')

    def test_alignment_preserves_image(self):
        en_chunks = [
            {'tag': 'p', 'type': 'std', 'text': 'Paragraph 1', 'classes': []},
            {'tag': 'img', 'type': 'image', 'src': 'img1.jpg', 'alt': 'Img1', 'text': '', 'classes': []},
            {'tag': 'p', 'type': 'std', 'text': 'Paragraph 2', 'classes': []}
        ]
        
        es_chunks = [
            {'tag': 'p', 'type': 'std', 'text': 'Parrafo 1', 'classes': []},
            # Spanish might lack the image or have it
            {'tag': 'p', 'type': 'std', 'text': 'Parrafo 2', 'classes': []}
        ]
        
        aligned = align_chunks(en_chunks, es_chunks)
        
        # Expect: P1-P1, Img-Empty, P2-P2 (or similar)
        # Verify img is in result
        
        img_found = False
        for item in aligned:
            print(f"DEBUG ITEM: Tag={item.get('tag')} Type={item.get('type')} EN='{item.get('en')}'")
            if item['tag'] == 'img':
                img_found = True
                self.assertEqual(item['src'], 'img1.jpg')
                self.assertEqual(item['as_en'], True) if 'as_en' in item else None
        self.assertTrue(img_found, "Image chunk should be preserved in alignment")

    def test_html_generation(self):
        aligned = [
            {'tag': 'p', 'en': 'Hello', 'es': 'Hola', 'classes': []},
            {'tag': 'img', 'en': '', 'es': '', 'src': 'pic.jpg', 'alt': 'Pic', 'classes': []}
        ]
        
        html = generate_chapter_html(aligned, "Test Chapter")
        
        self.assertIn('<p>Hello</p>', html)
        self.assertIn('<p class="es-trans">Hola</p>', html)
        self.assertIn('<img src="pic.jpg" alt="Pic" />', html)

if __name__ == '__main__':
    unittest.main()
