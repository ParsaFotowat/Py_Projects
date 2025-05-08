# Data Structure and Preprocessing Documentation

This directory contains the data used for the garbage classification application. The data is organized into two main subdirectories: `raw` and `processed`.

## Directory Structure

- **data/raw**: This directory contains the raw garbage classification dataset files downloaded from Kaggle. These files have not been altered and are in their original format.

- **data/processed**: This directory holds the processed data files that are ready for model training. The preprocessing steps include data cleaning, normalization, and any necessary transformations to prepare the data for input into the machine learning model.

## Data Sources

The dataset used for this project is sourced from Kaggle's garbage classification datasets. It includes images categorized into four classes: organic, plastic, metal/glass, and paper.

## Preprocessing Steps

1. **Data Cleaning**: Remove any corrupted or irrelevant images from the dataset.
2. **Normalization**: Scale pixel values to a range suitable for model training.
3. **Augmentation**: Apply techniques such as rotation, flipping, and zooming to increase the diversity of the training dataset.
4. **Splitting**: Divide the dataset into training, validation, and test sets to evaluate model performance effectively.

This documentation will be updated as the project progresses and additional preprocessing steps are implemented.