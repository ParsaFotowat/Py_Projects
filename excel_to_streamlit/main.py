import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("Upload your Excel (.xls, .xlsx) or CSV file")
if uploaded_file:
    try:
        @st.cache_data
        def load_file(uploaded_file):
            if uploaded_file.name.endswith('.xlsx'):
                return pd.read_excel(uploaded_file, engine='openpyxl')
            elif uploaded_file.name.endswith('.xls'):
                return pd.read_excel(uploaded_file, engine='xlrd')
            elif uploaded_file.name.endswith('.csv'):
                return pd.read_csv(uploaded_file)

        df = load_file(uploaded_file)

        if st.checkbox("Clean Data"):
            if st.checkbox("Drop The Missing Values"):
                df = df.dropna()
            if st.checkbox("Drop Duplicates"):
                df = df.drop_duplicates()

        # Display the data and a chart
        st.write("Preview:", df.head(100))  # Limit to 100 rows
        st.write("Data Summary:")
        st.write(df.describe())
        st.write("Missing Values:")
        st.write(df.isnull().sum())
        st.line_chart(df.select_dtypes(include=['number']))

        st.write("Visualize Data:")
        chart_type = st.selectbox("Select Chart Type", ["Line Chart", "Bar Chart", "Area Chart"])
        numeric_columns = df.select_dtypes(include=['number']).columns
        selected_column = st.selectbox("Select Column to Visualize", numeric_columns)

        if chart_type == "Line Chart":
            st.line_chart(df[selected_column])
        elif chart_type == "Bar Chart":
            st.bar_chart(df[selected_column])
        elif chart_type == "Area Chart":
            st.area_chart(df[selected_column])

        st.write("Create a Pivot Table:")
        index = st.selectbox("Select Index", df.columns)
        values = st.selectbox("Select Values", df.select_dtypes(include=['number']).columns)

        @st.cache_data
        def create_pivot_table(df, index, values):
            return df.pivot_table(index=index, values=values, aggfunc='sum')

        pivot_table = create_pivot_table(df, index, values)
        st.write(pivot_table)

        @st.cache_data
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df_to_csv(df)
        st.download_button(
            label="Download Processed Data as CSV",
            data=csv,
            file_name='processed_data.csv',
            mime='text/csv',
        )
    except ValueError as e:
        st.error("The uploaded file is not valid. Please upload a valid .xls, .xlsx, or .csv file.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
