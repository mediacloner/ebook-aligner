import unittest
import sys
import os

# Add parent directory to path to import align_book
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from align_book import generate_passthrough_chapter

class TestPassthroughAlignment(unittest.TestCase):
    def test_title_page_centering(self):
        # Mock inputs
        en_src = None
        es_src = None
        title = "Title Page"
        
        # Capture stdout to avoid printing to test output
        from io import StringIO
        saved_stdout = sys.stdout
        sys.stdout = StringIO()
        
        try:
            # Generate HTML
            # generate_passthrough_chapter(en_src, es_src, title, staging_dir=None)
            # Since process_content requires file I/O, we can't easily mock it without writing files.
            # However, looking at the function, if src is None, it returns empty string for body.
            # We are verifying the CONTAINER wrapper logic which depends on title.
            
            html = generate_passthrough_chapter(None, None, title, staging_dir=None)
            
            # Check for class injection
            self.assertIn('class="en-original passthrough-container centered-content"', html)
            self.assertIn('.passthrough-container.centered-content { text-align: center; }', html)
            
        finally:
            sys.stdout = saved_stdout

    def test_cover_centering(self):
        title = "Cover"
        html = generate_passthrough_chapter(None, None, title, staging_dir=None)
        self.assertIn('class="en-original passthrough-container centered-content"', html)

    def test_other_passthrough_not_centered(self):
        title = "Copyright"
        html = generate_passthrough_chapter(None, None, title, staging_dir=None)
        # Check that the specific class combination is NOT present in the DIV check
        self.assertNotIn('class="en-original passthrough-container centered-content"', html)
        self.assertIn('class="en-original passthrough-container"', html)

if __name__ == '__main__':
    unittest.main()
