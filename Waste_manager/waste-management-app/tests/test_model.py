import unittest
from src.model import Model

class TestModel(unittest.TestCase):

    def setUp(self):
        self.model = Model()

    def test_model_training(self):
        # Assuming we have a method to train the model and return the accuracy
        accuracy = self.model.train()
        self.assertGreaterEqual(accuracy, 0.7, "Model accuracy should be at least 70%")

    def test_model_evaluation(self):
        # Assuming we have a method to evaluate the model
        evaluation_metrics = self.model.evaluate()
        self.assertIn('accuracy', evaluation_metrics, "Evaluation metrics should include accuracy")
        self.assertIn('f1_score', evaluation_metrics, "Evaluation metrics should include f1_score")

    def test_model_save_load(self):
        # Test saving and loading the model
        self.model.train()
        self.model.save('models/trained_model.pkl')
        loaded_model = Model.load('models/trained_model.pkl')
        self.assertIsNotNone(loaded_model, "Loaded model should not be None")

if __name__ == '__main__':
    unittest.main()