import unittest
import sys
import os

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from neural_aligner import NeuralAligner

class TestNeuralAligner(unittest.TestCase):
    def setUp(self):
        # Use a smaller model for testing if possible, but we only installed one main one implicitly via cache
        # LaBSE is the default in the class
        self.aligner = NeuralAligner()

    def test_simple_alignment(self):
        en_chunks = [
            {'text': 'The cat sat on the mat.', 'id': 1},
            {'text': 'It was a sunny day.', 'id': 2},
            {'text': 'Programming is fun.', 'id': 3}
        ]
        
        es_chunks = [
            {'text': 'El gato se sentó en la alfombra.', 'id': 1},
            {'text': 'Era un día soleado.', 'id': 2},
            {'text': 'Programar es divertido.', 'id': 3}
        ]
        
        alignment = self.aligner.align_dtw(en_chunks, es_chunks)
        
        self.assertEqual(len(alignment), 3)
        self.assertEqual(alignment[0]['en_indices'], [0])
        self.assertEqual(alignment[0]['es_indices'], [0])
        self.assertEqual(alignment[2]['en_indices'], [2])
        self.assertEqual(alignment[2]['es_indices'], [2])

    def test_merge_alignment(self):
        # 2 English sentences split -> 1 Spanish sentence
        en_chunks = [
            {'text': 'Hello world.', 'id': 1},
            {'text': 'My name is AI.', 'id': 2}
        ]
        es_chunks = [
            {'text': 'Hola mundo, mi nombre es IA.', 'id': 1}
        ]
        
        alignment = self.aligner.align_dtw(en_chunks, es_chunks)
        
        # Depending on DTW path, it should group them
        # path might be (0,0) -> (1,0)
        self.assertEqual(len(alignment), 1)
        self.assertEqual(sorted(alignment[0]['en_indices']), [0, 1])
        self.assertEqual(sorted(alignment[0]['es_indices']), [0])

if __name__ == '__main__':
    unittest.main()
