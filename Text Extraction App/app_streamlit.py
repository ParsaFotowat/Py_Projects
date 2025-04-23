import os
import cv2
import numpy as np
import random
import string
import pytesseract
from PIL import Image
import streamlit as st

# Configure Tesseract path (update this path based on your local installation)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Streamlit app setup
st.title("Text Extraction from Images")
st.text("Upload an image to extract text using Tesseract OCR.")

# File uploader
uploaded_file = st.file_uploader("Choose an image file", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Load the uploaded image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Convert image to array
    image_arr = np.array(image.convert('RGB'))

    # Convert to grayscale
    gray_img_arr = cv2.cvtColor(image_arr, cv2.COLOR_BGR2GRAY)

    # Display the grayscale image
    st.image(gray_img_arr, caption="Grayscale Image", use_column_width=True, channels="GRAY")

    # Extract text using Tesseract
    custom_config = r'-l eng --oem 3 --psm 6'
    extracted_text = pytesseract.image_to_string(gray_img_arr, config=custom_config)

    # Remove unwanted characters
    characters_to_remove = "!()@—*“>+-/,'|£#%$&^_~"
    cleaned_text = extracted_text
    for character in characters_to_remove:
        cleaned_text = cleaned_text.replace(character, "")

    # Display extracted text
    st.subheader("Extracted Text")
    if cleaned_text.strip():
        st.text_area("Text Output", cleaned_text, height=200)
    else:
        st.warning("No text detected in the image.")

    # Option to download the extracted text
    st.download_button(
        label="Download Extracted Text",
        data=cleaned_text,
        file_name="extracted_text.txt",
        mime="text/plain"
    )