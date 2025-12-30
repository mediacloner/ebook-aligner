import sys
import os
import unittest

# Add parent directory to path to import align_book
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from align_book import extract_figure_number

class TestFigureTyping(unittest.TestCase):
    """
    Test that extract_figure_number correctly detects figure numbers.
    This function is used in process_chapter_pair to upgrade chunk types to 'caption'.
    """
    
    def test_english_figure_detection(self):
        """Test that English figure captions are detected"""
        test_cases = [
            ("FIGURE 23: A hypothetical first episode of reinforcement learning.", "23"),
            ("Figure 23. A hypothetical first episode.", "23"),
            ("Fig. 23 - Some caption", "23"),
            ("Table 5: Results", "5"),
            ("Normal paragraph about Figure 23", None),  # Reference, not caption
        ]
        
        for text, expected in test_cases:
            result = extract_figure_number(text)
            self.assertEqual(result, expected, f"Failed for: {text}")
            print(f"✓ '{text[:40]}...' -> {result}")
    
    def test_spanish_figure_detection(self):
        """Test that Spanish figure captions are detected"""
        test_cases = [
            ("Figura 23. Un hipotético primer episodio de aprendizaje por refuerzo.", "23"),
            ("Figura 23: Un hipotético primer episodio.", "23"),
            ("Tabla 5. Resultados", "5"),
            ("Un párrafo normal sobre la figura 23", None),  # Reference, not caption
        ]
        
        for text, expected in test_cases:
            result = extract_figure_number(text)
            self.assertEqual(result, expected, f"Failed for: {text}")
            print(f"✓ '{text[:40]}...' -> {result}")
    
    def test_type_upgrade_simulation(self):
        """Simulate the type upgrade logic from process_chapter_pair"""
        chunks = [
            {'text': 'Normal paragraph', 'type': 'std'},
            {'text': 'Figura 23. Un hipotético primer episodio de aprendizaje por refuerzo.', 'type': 'std'},
            {'text': 'Another paragraph', 'type': 'std'},
        ]
        
        # Simulate the type upgrade logic
        for c in chunks:
            if c.get('type') == 'std':
                fig_num = extract_figure_number(c['text'])
                if fig_num:
                    c['type'] = 'caption'
                    print(f"✓ Upgraded to caption: '{c['text'][:40]}...'")
        
        # Verify Figure 23 was upgraded
        fig_chunk = next((c for c in chunks if "Figura 23" in c['text']), None)
        self.assertIsNotNone(fig_chunk)
        self.assertEqual(fig_chunk['type'], 'caption')

if __name__ == '__main__':
    unittest.main()
