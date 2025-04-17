import streamlit as st
import pandas as pd

uploaded_file = st.file_uploader("Upload your Excel or CSV file")
if uploaded_file:
    try:
        # Check the file extension
        if uploaded_file.name.endswith('.xlsx'):
            # Read Excel file
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.name.endswith('.csv'):
            # Read CSV file
            df = pd.read_csv(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a .xlsx or .csv file.")
            st.stop()

        if st.checkbox("Clean Data"):
            if st.checkbox("Drop Missing Values"):
                df = df.dropna()
            if st.checkbox("Drop Duplicates"):
                df = df.drop_duplicates()

        # Display the data and a chart
        st.write("Preview:", df.head())
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
        pivot_table = df.pivot_table(index=index, values=values, aggfunc='sum')
        st.write(pivot_table)

        @st.cache
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
        st.error("The uploaded file is not valid. Please upload a valid .xlsx or .csv file.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
