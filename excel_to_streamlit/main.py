import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pandas_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# VISION: A dynamic, zero-config, plug-and-play data analysis suite
st.set_page_config(page_title="Data Analysis Suite", layout="wide")

# Session state to track user data
if "df" not in st.session_state:
    st.session_state.df = None

# 1) Drag-and-Drop File Upload
st.sidebar.header("Upload Your File")
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV/XLSX/XLS files", type=["csv", "xlsx", "xls"], accept_multiple_files=True
)

if uploaded_files:
    dfs = []
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".xlsx"):
            dfs.append(pd.read_excel(uploaded_file, engine="openpyxl"))
        elif uploaded_file.name.endswith(".xls"):
            dfs.append(pd.read_excel(uploaded_file, engine="xlrd"))
        elif uploaded_file.name.endswith(".csv"):
            dfs.append(pd.read_csv(uploaded_file))
    st.session_state.df = pd.concat(dfs, ignore_index=True)

if st.session_state.df is not None:
    df = st.session_state.df

    # Tabs for UX segmentation
    tabs = st.tabs(["Raw View", "Clean & Transform", "Visualize", "Insights"])

    # Tab 1: Raw View
    with tabs[0]:
        st.header("Raw Data Preview")
        st.write("Preview of raw data (first 100 rows):")
        st.dataframe(df.head(100))

        st.write("Data Summary Dashboard")
        st.write(f"**Rows:** {df.shape[0]} | **Columns:** {df.shape[1]}")
        st.write("Column Data Types:")
        st.write(df.dtypes)

        st.write("Missing Value Heatmap:")
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis", ax=ax)
        st.pyplot(fig)

    # Tab 2: Clean & Transform
    with tabs[1]:
        st.header("Data Cleaning & Transformation")
        st.write("Interactive Filtering + Sorting")
        for col in df.columns:
            if df[col].dtype == "object":
                selected_values = st.multiselect(f"Filter {col}", df[col].unique())
                if selected_values:
                    df = df[df[col].isin(selected_values)]
            elif np.issubdtype(df[col].dtype, np.number):
                min_val, max_val = st.slider(
                    f"Filter {col}", float(df[col].min()), float(df[col].max()), (float(df[col].min()), float(df[col].max()))
                )
                df = df[(df[col] >= min_val) & (df[col] <= max_val)]

        st.write("Missing Value Imputation Tools")
        imputation_method = st.selectbox("Select Imputation Method", ["None", "Drop Rows", "Fill with Mean", "Fill with Median", "Fill with Mode"])
        if imputation_method == "Drop Rows":
            df = df.dropna()
        elif imputation_method == "Fill with Mean":
            df = df.fillna(df.mean())
        elif imputation_method == "Fill with Median":
            df = df.fillna(df.median())
        elif imputation_method == "Fill with Mode":
            df = df.fillna(df.mode().iloc[0])

        st.write("Data Transformation Studio")
        rename_columns = st.text_input("Rename Columns (comma-separated, e.g., old1:new1,old2:new2)")
        if rename_columns:
            rename_dict = dict(item.split(":") for item in rename_columns.split(","))
            df = df.rename(columns=rename_dict)

        st.write("Cleaned Data Preview:")
        st.dataframe(df.head(100))

    # Tab 3: Visualize
    with tabs[2]:
        st.header("Data Visualization")
        st.write("Column-wise Bar Charts, Histograms, Pie Charts")
        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object"]).columns

        chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Histogram", "Pie Chart", "Scatter Plot"])
        if chart_type == "Bar Chart":
            x_col = st.selectbox("X-axis", categorical_columns)
            y_col = st.selectbox("Y-axis", numeric_columns)
            bar_data = df.groupby(x_col)[y_col].sum().reset_index()
            st.bar_chart(bar_data.set_index(x_col))
        elif chart_type == "Histogram":
            hist_col = st.selectbox("Select Column", numeric_columns)
            st.histogram(df[hist_col])
        elif chart_type == "Pie Chart":
            pie_col = st.selectbox("Select Column", categorical_columns)
            pie_data = df[pie_col].value_counts()
            st.write(pie_data.plot.pie(autopct="%1.1f%%"))
            st.pyplot()
        elif chart_type == "Scatter Plot":
            x_col = st.selectbox("X-axis", numeric_columns)
            y_col = st.selectbox("Y-axis", numeric_columns)
            st.scatter_chart(df[[x_col, y_col]])

    # Tab 4: Insights
    with tabs[3]:
        st.header("Insights & ML-Powered Analysis")
        st.write("Auto Clustering (KMeans Preview)")
        num_clusters = st.slider("Number of Clusters", 2, 10, 3)
        kmeans = KMeans(n_clusters=num_clusters)
        numeric_data = df.select_dtypes(include=["number"]).dropna()
        kmeans.fit(numeric_data)
        df["Cluster"] = kmeans.labels_
        st.write("Clustered Data Preview:")
        st.dataframe(df.head(100))

        st.write("Regression Target Prediction (Light AutoML)")
        target_col = st.selectbox("Select Target Column (Regression)", numeric_columns)
        if target_col:
            features = numeric_data.drop(columns=[target_col])
            target = numeric_data[target_col]
            model = LinearRegression()
            model.fit(features, target)
            st.write(f"Model Coefficients: {model.coef_}")
            st.write(f"Model Intercept: {model.intercept_}")

        st.write("Download Results")
        st.download_button("Download Cleaned Dataset", df.to_csv(index=False), "cleaned_data.csv", "text/csv")
