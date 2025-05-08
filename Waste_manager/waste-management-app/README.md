# Waste Management App

This project is a machine learning application designed for garbage sorting, classifying waste into four categories: organic, plastic, metal/glass, and paper. The application utilizes Kaggle's garbage classification datasets to train a model that can accurately identify and sort different types of waste.

## Project Structure

- **data/**: Contains raw and processed data.
  - **raw/**: Raw garbage classification dataset files downloaded from Kaggle.
  - **processed/**: Processed data files ready for model training.
  - **README.md**: Documentation on the data structure, sources, and preprocessing steps.

- **models/**: Stores the trained machine learning model.
  - **trained_model.pkl**: The trained model for garbage classification.
  - **README.md**: Documentation on model architecture, training process, and usage.

- **notebooks/**: Jupyter notebooks for data processing and model training.
  - **data_preprocessing.ipynb**: Code for data cleaning and preprocessing.
  - **model_training.ipynb**: Code for training the machine learning model.
  - **evaluation.ipynb**: Code for evaluating model performance and visualizing results.

- **src/**: Source code for the application.
  - **app.py**: Main entry point of the application, setting up the web server and API endpoints.
  - **data_loader.py**: Functions for loading and preprocessing images.
  - **model.py**: Defines the machine learning model architecture and training methods.
  - **predictor.py**: Functions for loading the trained model and making predictions.
  - **utils.py**: Utility functions for image transformations and metrics calculations.

- **tests/**: Unit tests for the application.
  - **test_data_loader.py**: Tests for data loading and preprocessing functions.
  - **test_model.py**: Tests for model training and evaluation functions.
  - **test_predictor.py**: Tests for prediction functionality.

- **requirements.txt**: Lists Python dependencies required for the project.

- **Dockerfile**: Defines the Docker image for the application.

- **.gitignore**: Specifies files and directories to be ignored by Git.

- **LICENSE**: Licensing information for the project.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd waste-management-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Prepare the dataset by placing the raw files in the `data/raw` directory.

## Usage

To run the application, execute the following command:
```
python src/app.py
```

The application will start a web server that allows users to upload images for classification.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.