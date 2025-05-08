class DataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir

    def load_images(self, category):
        import os
        from PIL import Image
        import numpy as np

        category_path = os.path.join(self.data_dir, category)
        images = []
        labels = []

        for filename in os.listdir(category_path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                img_path = os.path.join(category_path, filename)
                image = Image.open(img_path)
                image = image.resize((224, 224))  # Resize to fit model input
                images.append(np.array(image))
                labels.append(category)

        return np.array(images), np.array(labels)

    def load_data(self):
        categories = ['organic', 'plastic', 'metal_glass', 'paper']
        all_images = []
        all_labels = []

        for category in categories:
            images, labels = self.load_images(category)
            all_images.extend(images)
            all_labels.extend(labels)

        return np.array(all_images), np.array(all_labels)