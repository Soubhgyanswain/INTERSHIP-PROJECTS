# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Netflix Analysis", layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_excel("Dim_User.xlsx")  # replace if dataset is named differently
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    return df

df = load_data()

# Clean data types
df["Age"] = pd.to_numeric(df["Age"], errors='coerce')
df["TimeConsumingPerWeek"] = pd.to_numeric(df["TimeConsumingPerWeek"], errors='coerce')
df["Satisfaction"] = pd.to_numeric(df["Satisfaction"], errors='coerce')

df.dropna(subset=["Age", "TimeConsumingPerWeek", "Satisfaction", "Genre"], inplace=True)

# 📊 Data Preview
st.title("📺 Netflix User Behavior – Simple Visuals")
st.dataframe(df.head())

# 🎬 Plot 1: Genre Count
st.header("🎬 Genre Distribution")
fig1 = px.histogram(df, y="Genre", color="Gender", barmode="group")
st.plotly_chart(fig1, use_container_width=True)

# ⏱️ Plot 2: Watch Time vs Age
st.header("⏱️ Watch Time vs Age")
fig2 = px.scatter(df, x="Age", y="TimeConsumingPerWeek", color="Gender", size="Satisfaction")
st.plotly_chart(fig2, use_container_width=True)

# 🌟 Plot 3: Satisfaction by Genre
st.header("🌟 Average Satisfaction by Genre")
genre_avg = df.groupby("Genre")["Satisfaction"].mean().reset_index().sort_values(by="Satisfaction", ascending=False)
fig3 = px.bar(genre_avg, x="Satisfaction", y="Genre", orientation="h", color="Satisfaction")
st.plotly_chart(fig3, use_container_width=True)

# 🔝 Plot 4: Top 10 Watchers
st.header("🔥 Top 10 Binge Watchers")
top_users = df.sort_values(by="TimeConsumingPerWeek", ascending=False).head(10)
st.dataframe(top_users[["User_ID", "Age", "Country", "TimeConsumingPerWeek"]])

# 📊 Plot 5: Satisfaction by Device (Matplotlib)
st.header("📱 Satisfaction by Device (Boxplot)")
fig4, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=df, x="Device", y="Satisfaction", ax=ax)
st.pyplot(fig4)

# 📊 Plot 6: Age Group Pie Chart
st.header("👥 Age Group Pie Chart")
df["AgeGroup"] = pd.cut(df["Age"], bins=[0, 18, 25, 35, 50, 100], labels=["<18", "18–25", "26–35", "36–50", "50+"])
fig5 = px.pie(df, names="AgeGroup", title="User Age Group Distribution", hole=0.4)
st.plotly_chart(fig5, use_container_width=True)

# Done
st.markdown("---")
st.markdown("📊 Built from uploaded notebook – Soubhagya | RISE Internship Project 6")
