import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Title
st.set_page_config(page_title="Student Performance Analysis", layout="wide")
st.title("📊 Student Performance Analysis Dashboard")

# Upload File
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    # Load data
    df = pd.read_excel(uploaded_file)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Show raw data
    with st.expander("🔍 View Raw Data"):
        st.dataframe(df)

    # Drop missing values in score columns
    df.dropna(subset=["Math Score", "Reading Score", "Writing Score"], inplace=True)

    # Add a new column: Average Score
    df["Average Score"] = df[["Math Score", "Reading Score", "Writing Score"]].mean(axis=1)

    # Sidebar filters
    st.sidebar.header("🔧 Filter Students")
    gender_filter = st.sidebar.multiselect("Select Gender", options=df["Gender"].unique(), default=df["Gender"].unique())
    ethnicity_filter = st.sidebar.multiselect("Select Ethnicity", options=df["Ethnicity"].unique(), default=df["Ethnicity"].unique())
    prep_filter = st.sidebar.multiselect("Test Preparation", options=df["Test Preparation"].unique(), default=df["Test Preparation"].unique())

    # Apply filters
    filtered_df = df[
        (df["Gender"].isin(gender_filter)) &
        (df["Ethnicity"].isin(ethnicity_filter)) &
        (df["Test Preparation"].isin(prep_filter))
    ]

    # Show filtered data
    st.subheader("📄 Filtered Student Data")
    st.dataframe(filtered_df)

    # Statistics
    st.subheader("📈 Summary Statistics")
    st.write(filtered_df.describe())

    # Visualization Section
    st.subheader("📊 Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Average Score by Gender")
        gender_avg = filtered_df.groupby("Gender")["Average Score"].mean().sort_values()
        st.bar_chart(gender_avg)

    with col2:
        st.markdown("### Average Score by Test Preparation")
        prep_avg = filtered_df.groupby("Test Preparation")["Average Score"].mean().sort_values()
        st.bar_chart(prep_avg)

    st.markdown("### Correlation Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(filtered_df[["Math Score", "Reading Score", "Writing Score", "Average Score"]].corr(), annot=True, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

else:
    st.info("📥 Please upload an Excel file to get started.")

