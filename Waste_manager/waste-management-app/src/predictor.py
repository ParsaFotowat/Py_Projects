class Predictor:
    def __init__(self, model_path):
        import joblib
        self.model = joblib.load(model_path)

    def predict(self, image):
        import numpy as np
        from PIL import Image
        from torchvision import transforms

        # Define the image transformations
        preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        # Preprocess the image
        image = preprocess(image)
        image = image.unsqueeze(0)  # Add batch dimension

        # Make prediction
        with torch.no_grad():
            output = self.model(image)
            _, predicted = torch.max(output, 1)

        return predicted.item()

    def predict_from_path(self, image_path):
        image = Image.open(image_path)
        return self.predict(image)