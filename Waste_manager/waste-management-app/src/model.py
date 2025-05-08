from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
import cv2

class GarbageClassifier:
    def __init__(self, input_shape=(128, 128, 3), num_classes=4):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self.build_model()

    def build_model(self):
        model = Sequential()
        model.add(Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Conv2D(128, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Flatten())
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.num_classes, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def train(self, X, y, batch_size=32, epochs=10, validation_split=0.2):
        datagen = ImageDataGenerator(rotation_range=20, width_shift_range=0.2,
                                     height_shift_range=0.2, shear_range=0.2,
                                     zoom_range=0.2, horizontal_flip=True,
                                     fill_mode='nearest')
        datagen.fit(X)
        self.model.fit(datagen.flow(X, y, batch_size=batch_size),
                       steps_per_epoch=len(X) // batch_size,
                       epochs=epochs,
                       validation_split=validation_split)

    def save_model(self, filepath):
        self.model.save(filepath)

    def load_data(self, data_dir):
        images = []
        labels = []
        for category in os.listdir(data_dir):
            category_path = os.path.join(data_dir, category)
            for img_file in os.listdir(category_path):
                img_path = os.path.join(category_path, img_file)
                img = cv2.imread(img_path)
                img = cv2.resize(img, self.input_shape[:2])
                images.append(img)
                labels.append(category)
        images = np.array(images) / 255.0
        lb = LabelBinarizer()
        labels = lb.fit_transform(labels)
        return images, labels

    def prepare_data(self, data_dir):
        X, y = self.load_data(data_dir)
        return train_test_split(X, y, test_size=0.2, random_state=42)