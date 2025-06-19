import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Survey Data Dashboard", layout="wide")
st.title("📊 Survey Data Visualization")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("survey_data_cleaned.csv")  # Make sure this CSV is in same folder

df = load_data()

# Show raw data
if st.checkbox("Show Raw Data"):
    st.write("### Raw Survey Data")
    st.dataframe(df)

# Sidebar filters
st.sidebar.header("🔍 Filter Options")

# Gender filter
if "Gender" in df.columns:
    genders = st.sidebar.multiselect("Select Gender:", df["Gender"].dropna().unique(), default=df["Gender"].dropna().unique())
    df = df[df["Gender"].isin(genders)]

# Age filter (if Age column exists)
if "Age" in df.columns:
    min_age, max_age = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.sidebar.slider("Select Age Range:", min_value=min_age, max_value=max_age, value=(min_age, max_age))
    df = df[(df["Age"] >= age_range[0]) & (df["Age"] <= age_range[1])]

# Preferred platform distribution
st.subheader("📱 Preferred Platform")
if "preferred_platform" in df.columns:
    fig1, ax1 = plt.subplots()
    sns.countplot(data=df, x="preferred_platform", palette="cool", ax=ax1)
    ax1.set_title("Distribution of Preferred Platforms")
    st.pyplot(fig1)
else:
    st.warning("Column 'preferred_platform' not found in the dataset.")

# Age distribution histogram
st.subheader("🎂 Age Distribution")
if "Age" in df.columns:
    fig2, ax2 = plt.subplots()
    sns.histplot(df["Age"], kde=True, bins=20, color="skyblue", ax=ax2)
    ax2.set_title("Age Distribution of Survey Participants")
    st.pyplot(fig2)

# Gender-wise platform preference
st.subheader("📊 Gender vs Platform")
if "Gender" in df.columns and "preferred_platform" in df.columns:
    fig3, ax3 = plt.subplots()
    sns.countplot(data=df, x="preferred_platform", hue="Gender", ax=ax3)
    ax3.set_title("Platform Preference by Gender")
    st.pyplot(fig3)

# Correlation heatmap if numerical columns exist
st.subheader("📈 Correlation Heatmap")
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns
if len(numerical_cols) >= 2:
    fig4, ax4 = plt.subplots()
    sns.heatmap(df[numerical_cols].corr(), annot=True, cmap="coolwarm", ax=ax4)
    st.pyplot(fig4)
else:
    st.warning("Not enough numerical columns for correlation heatmap.")

# Footer
st.markdown("---")
st.markdown("Developed by **Soubhagya | RISE Internship | Tamizhan Skills**")

