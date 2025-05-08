import unittest
from src.data_loader import DataLoader

class TestDataLoader(unittest.TestCase):

    def setUp(self):
        self.data_loader = DataLoader(data_dir='data/raw')

    def test_load_images(self):
        images, labels = self.data_loader.load_images()
        self.assertIsInstance(images, list)
        self.assertIsInstance(labels, list)
        self.assertGreater(len(images), 0)
        self.assertEqual(len(images), len(labels))

    def test_preprocess_image(self):
        sample_image = self.data_loader.load_image('data/raw/sample_image.jpg')
        processed_image = self.data_loader.preprocess_image(sample_image)
        self.assertEqual(processed_image.shape, (224, 224, 3))  # Assuming the model expects 224x224 RGB images

    def test_get_class_labels(self):
        class_labels = self.data_loader.get_class_labels()
        expected_labels = ['organic', 'plastic', 'metal/glass', 'paper']
        self.assertListEqual(class_labels, expected_labels)

if __name__ == '__main__':
    unittest.main()