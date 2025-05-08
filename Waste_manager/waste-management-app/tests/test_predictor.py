import unittest
from src.predictor import Predictor

class TestPredictor(unittest.TestCase):
    def setUp(self):
        self.predictor = Predictor(model_path='models/trained_model.pkl')

    def test_predict_organic(self):
        result = self.predictor.predict('path/to/organic_image.jpg')
        self.assertEqual(result, 'organic')

    def test_predict_plastic(self):
        result = self.predictor.predict('path/to/plastic_image.jpg')
        self.assertEqual(result, 'plastic')

    def test_predict_metal_glass(self):
        result = self.predictor.predict('path/to/metal_glass_image.jpg')
        self.assertEqual(result, 'metal/glass')

    def test_predict_paper(self):
        result = self.predictor.predict('path/to/paper_image.jpg')
        self.assertEqual(result, 'paper')

    def test_invalid_image(self):
        with self.assertRaises(ValueError):
            self.predictor.predict('path/to/invalid_image.txt')

if __name__ == '__main__':
    unittest.main()