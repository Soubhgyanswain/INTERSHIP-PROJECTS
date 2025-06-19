# app.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set Streamlit page configuration
st.set_page_config(page_title="COVID-19 Analysis", layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("country_wise_latest.csv")
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]
    return df

df = load_data()

# Title
st.title("🌍 COVID-19 Country-wise Data Analysis")
st.markdown("This dashboard visualizes the latest global COVID-19 data using various charts and insights.")

# Show data on checkbox
if st.checkbox("Show Raw Data"):
    st.dataframe(df)

# Summary stats
st.subheader("🔹 Global Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Confirmed", int(df['Confirmed'].sum()))
col2.metric("Total Deaths", int(df['Deaths'].sum()))
col3.metric("Total Recovered", int(df['Recovered'].sum()))
col4.metric("Total Active", int(df['Active'].sum()))

# Bar chart - Top 10 Countries by Confirmed Cases
st.subheader("🔸 Top 10 Countries by Confirmed Cases")
top10 = df.sort_values(by='Confirmed', ascending=False).head(10)

fig1, ax1 = plt.subplots(figsize=(10, 5))
sns.barplot(x='Confirmed', y='Country/Region', data=top10, palette='Reds_r', ax=ax1)
ax1.set_title("Top 10 Countries with Highest Confirmed Cases")
st.pyplot(fig1)

# Pie chart - Top 5 Deaths Share
st.subheader("🔸 Death Share of Top 5 Countries")
top5_deaths = df.sort_values(by='Deaths', ascending=False).head(5)

fig2, ax2 = plt.subplots(figsize=(6, 6))
ax2.pie(top5_deaths['Deaths'], labels=top5_deaths['Country/Region'], autopct='%1.1f%%',
        startangle=90, colors=sns.color_palette('pastel'))
ax2.set_title("Top 5 Countries by Deaths")
st.pyplot(fig2)

# Scatterplot - Active vs Recovered
st.subheader("🔸 Recovered vs Active Cases by WHO Region")
fig3, ax3 = plt.subplots(figsize=(10, 6))
sns.scatterplot(x='Recovered', y='Active', data=df, hue='WHO_Region', s=150, edgecolor='black', ax=ax3)
ax3.set_title("Recovered vs Active")
st.pyplot(fig3)

# Heatmap - Correlation
st.subheader("🔸 Correlation Between Confirmed, Deaths, Recovered, Active")
fig4, ax4 = plt.subplots(figsize=(6, 4))
numeric = df[['Confirmed', 'Deaths', 'Recovered', 'Active']]
sns.heatmap(numeric.corr(), annot=True, cmap='coolwarm', fmt='.2f', ax=ax4)
st.pyplot(fig4)

# Region-wise Confirmed Chart
st.subheader("🔸 WHO Region-wise Total Confirmed Cases")
region_total = df.groupby('WHO_Region')['Confirmed'].sum().sort_values(ascending=False)

fig5, ax5 = plt.subplots(figsize=(8, 4))
sns.barplot(x=region_total.index, y=region_total.values, palette='Set3', ax=ax5)
ax5.set_title("Confirmed Cases by WHO Region")
ax5.set_xlabel("WHO Region")
ax5.set_ylabel("Confirmed")
plt.xticks(rotation=45)
st.pyplot(fig5)

# Footer
st.markdown("---")
st.markdown("📊 Created by Soubhagya | Covid-19 Analysis | Tamizhan Skills")
