import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Set page config
st.set_page_config(
    page_title="Netflix User Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("Dim_User.xlsx")

df = load_data()

# Data preprocessing
df['AgeGroup'] = pd.cut(df['Age'], bins=[0, 18, 25, 35, 50, 100],
                       labels=['<18', '18–25', '26–35', '36–50', '50+'])

# Sidebar filters
st.sidebar.header("Filters")
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=df['Country'].unique(),
    default=df['Country'].value_counts().head(3).index.tolist()
)

selected_genders = st.sidebar.multiselect(
    "Select Genders",
    options=df['Gender'].unique(),
    default=df['Gender'].unique()
)

age_range = st.sidebar.slider(
    "Select Age Range",
    min_value=int(df['Age'].min()),
    max_value=int(df['Age'].max()),
    value=(int(df['Age'].min()), int(df['Age'].max()))
)

# Filter data based on selections
filtered_df = df[
    (df['Country'].isin(selected_countries) if selected_countries else df['Country'].notnull()) &
    (df['Gender'].isin(selected_genders) if selected_genders else df['Gender'].notnull()) &
    (df['Age'] >= age_range[0]) &
    (df['Age'] <= age_range[1])
]

# Main app
st.title("📊 Netflix User Analytics Dashboard")
st.markdown("""
Explore user demographics, preferences, and viewing habits.
""")

# Key metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Users", len(filtered_df))
col2.metric("Average Age", f"{filtered_df['Age'].mean():.1f} years")
col3.metric("Avg Weekly Watch Time", f"{filtered_df['TimeConsumingPerWeek'].mean():.1f} hours")
col4.metric("Top Genre", filtered_df['Genre'].mode()[0])

# Visualization tabs
tab1, tab2, tab3, tab4 = st.tabs(["Demographics", "Genre Preferences", "Age Analysis", "Interactive"])

with tab1:
    st.subheader("User Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top Countries**")
        top_countries = filtered_df['Country'].value_counts().head(10)
        fig, ax = plt.subplots(figsize=(7,6))
        sns.barplot(x=top_countries.values, y=top_countries.index, palette='Set2', ax=ax)
        plt.title("Top 10 Countries by User Count")
        plt.xlabel("No. of Users")
        plt.ylabel("Country")
        st.pyplot(fig)
    
    with col2:
        st.markdown("**Gender Distribution**")
        gender_counts = filtered_df['Gender'].value_counts()
        fig, ax = plt.subplots(figsize=(5,2))
        ax.pie(gender_counts, labels=gender_counts.index, 
               autopct='%1.1f%%', startangle=90, 
               colors=sns.color_palette('pastel'))
        plt.title("Gender Distribution")
        st.pyplot(fig)

with tab2:
    st.subheader("Genre Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Most Preferred Genres**")
        fig, ax = plt.subplots(figsize=(8,6.5))
        sns.countplot(data=filtered_df, y='Genre', 
                     order=filtered_df['Genre'].value_counts().index, 
                     palette='husl', ax=ax)
        plt.title("Most Preferred Genres")
        plt.xlabel("User Count")
        plt.ylabel("Genre")
        st.pyplot(fig)
    
    with col2:
        st.markdown("**Genre Preference by Gender**")
        heatmap_data = pd.crosstab(filtered_df['Genre'], filtered_df['Gender'])
        fig, ax = plt.subplots(figsize=(8,6))
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlGnBu', ax=ax)
        plt.title("Genre Preference by Gender")
        plt.ylabel("Genre")
        plt.xlabel("Gender")
        st.pyplot(fig)

with tab3:
    st.subheader("Age Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Age Group Distribution**")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.countplot(x='AgeGroup', data=filtered_df, palette='Purples', ax=ax)
        plt.title("User Distribution by Age Group")
        plt.xlabel("Age Group")
        plt.ylabel("No. of Users")
        st.pyplot(fig)
    
    with col2:
        st.markdown("**Watch Time vs Age**")
        fig, ax = plt.subplots(figsize=(8,5))
        sns.scatterplot(x='Age', y='TimeConsumingPerWeek', hue='Gender', 
                        data=filtered_df, palette='Set1', s=100, 
                        edgecolor='black', ax=ax)
        plt.title("Watch Time vs Age by Gender")
        plt.xlabel("Age")
        plt.ylabel("Time Spent on Netflix per Week")
        plt.grid(True)
        st.pyplot(fig)

with tab4:
    st.subheader("Interactive Visualizations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Interactive Age Distribution**")
        fig = px.histogram(filtered_df, x='Age', nbins=20, 
                          color='Gender', barmode='overlay',
                          title="Age Distribution by Gender")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("**Country Distribution**")
        country_counts = filtered_df['Country'].value_counts().reset_index()
        country_counts.columns = ['Country', 'Users']
        fig = px.choropleth(country_counts, 
                           locations='Country',
                           locationmode='country names',
                           color='Users',
                           hover_name='Country',
                           color_continuous_scale='Viridis',
                           title="User Distribution by Country")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("**Age vs Watch Time Interactive**")
    fig = px.scatter(filtered_df, x='Age', y='TimeConsumingPerWeek',
                    color='Gender', size='TimeConsumingPerWeek',
                    hover_data=['Country', 'Genre'],
                    title="Interactive Age vs Watch Time Analysis")
    st.plotly_chart(fig, use_container_width=True)

# Raw data view
st.subheader("Raw Data")
if st.checkbox("Show raw data"):
    st.dataframe(filtered_df)

# Download button
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(filtered_df)
st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name='filtered_netflix_users.csv',
    mime='text/csv'
)