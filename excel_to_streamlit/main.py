import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("Upload your Excel file")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Preview:", df.head())
    st.line_chart(df.select_dtypes(include=['number']))
