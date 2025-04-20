import matplotlib
matplotlib.use("Agg")  # Use the Agg backend for non-interactive environments

import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from ydata_profiling import ProfileReport
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

# VISION: A dynamic, zero-config, plug-and-play data analysis suite
st.set_page_config(page_title="Data Analysis Suite", layout="wide")

# Session state to track user data
if "df" not in st.session_state:
    st.session_state.df = None

@st.cache_data
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".xlsx"):
        return pd.read_excel(uploaded_file, engine="openpyxl")
    elif uploaded_file.name.endswith(".xls"):
        return pd.read_excel(uploaded_file, engine="xlrd")
    elif uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)

@st.cache_data
def generate_profile_report(data):
    return ProfileReport(data, title="Profiling Report", explorative=True)

# 1) Drag-and-Drop File Upload
st.sidebar.header("Upload Your File")
uploaded_files = st.sidebar.file_uploader(
    "Upload CSV/XLSX/XLS files", type=["csv", "xlsx", "xls"], accept_multiple_files=True
)

if uploaded_files:
    dfs = [load_file(file) for file in uploaded_files]
    st.session_state.df = pd.concat(dfs, ignore_index=True)

if st.session_state.df is not None:
    df = st.session_state.df
    if len(df) > 10000:
        st.warning("The uploaded file is large. Processing may take some time.")
    sampled_data = df.sample(n=min(1000, len(df)), random_state=42)  # Limit to 1,000 rows

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
        sns.heatmap(sampled_data.isnull(), cbar=False, cmap="viridis", ax=ax)
        st.pyplot(fig)

        # Generate and display a profiling report
        st.write("Data Profiling Report")
        profile = generate_profile_report(df)
        st.download_button(
            label="Download Profiling Report (HTML)",
            data=profile.to_html(),
            file_name="profiling_report.html",
            mime="text/html",
        )
        st.components.v1.html(profile.to_html(), height=1000, scrolling=True)

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
        numeric_data = df.select_dtypes(include=["number"]).dropna()

        if len(numeric_data) > 1000:  # Limit to 1,000 rows for clustering
            numeric_data = numeric_data.sample(n=1000, random_state=42)

        if len(numeric_data) < num_clusters:
            st.warning(f"Number of samples ({len(numeric_data)}) is less than the number of clusters ({num_clusters}). Reduce the number of clusters.")
        else:
            kmeans = KMeans(n_clusters=num_clusters)
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
        st.download_button("Download Clustered Dataset", df.to_csv(index=False), "clustered_data.csv", "text/csv")

    profile = generate_profile_report(st.session_state.df)
    st.download_button(
        label="Download Profiling Report (HTML)",
        data=profile.to_html(),
        file_name="profiling_report.html",
        mime="text/html",
    )
    st.components.v1.html(profile.to_html(), height=1000, scrolling=True)