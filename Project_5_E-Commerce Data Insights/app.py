import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.colors as colors
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="🛍️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("Sample - Superstore.csv", encoding='latin-1')

data = load_data()

# Data preprocessing
data['Order Date'] = pd.to_datetime(data['Order Date'])
data['Ship Date'] = pd.to_datetime(data['Ship Date'])
data['Order Month'] = data['Order Date'].dt.month
data['Order Year'] = data['Order Date'].dt.year
data['Order Day of Week'] = data['Order Date'].dt.dayofweek

# Sidebar filters
st.sidebar.header("Filters")
selected_years = st.sidebar.multiselect(
    "Select Years",
    options=sorted(data['Order Year'].unique()),
    default=sorted(data['Order Year'].unique())
)

selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=data['Category'].unique(),
    default=data['Category'].unique()
)

selected_segments = st.sidebar.multiselect(
    "Select Customer Segments",
    options=data['Segment'].unique(),
    default=data['Segment'].unique()
)

# Apply filters
filtered_data = data[
    (data['Order Year'].isin(selected_years)) &
    (data['Category'].isin(selected_categories)) &
    (data['Segment'].isin(selected_segments))
]

# Main dashboard
st.title("🛍️ E-Commerce Performance Dashboard")
st.markdown("""
    Analyze sales, profit, and customer segment performance across different product categories.
""")

# KPI cards
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Sales", f"${filtered_data['Sales'].sum():,.2f}")
with col2:
    st.metric("Total Profit", f"${filtered_data['Profit'].sum():,.2f}")
with col3:
    st.metric("Profit Margin", 
              f"{(filtered_data['Profit'].sum() / filtered_data['Sales'].sum()) * 100:.2f}%")

# Tabs for different analyses
tab1, tab2, tab3, tab4 = st.tabs(["Sales Analysis", "Profit Analysis", "Segment Analysis", "Geospatial View"])

with tab1:
    st.subheader("Sales Performance")
    
    col1, col2 = st.columns(2)
    with col1:
        # Monthly sales trend
        sales_by_month = filtered_data.groupby('Order Month')['Sales'].sum().reset_index()
        fig = px.line(sales_by_month, x='Order Month', y='Sales', 
                     title='Monthly Sales Trend',
                     labels={'Order Month': 'Month', 'Sales': 'Total Sales ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Sales by category
        sales_by_category = filtered_data.groupby('Category')['Sales'].sum().reset_index()
        fig = px.pie(sales_by_category, values='Sales', names='Category',
                    title='Sales Distribution by Category',
                    hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales by sub-category
    sales_by_subcategory = filtered_data.groupby('Sub-Category')['Sales'].sum().reset_index()
    fig = px.bar(sales_by_subcategory.sort_values('Sales', ascending=False), 
                x='Sub-Category', y='Sales',
                title='Sales by Sub-Category (Top Performers)',
                color='Sales',
                color_continuous_scale='Blues')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Profit Analysis")
    
    col1, col2 = st.columns(2)
    with col1:
        # Monthly profit trend
        profit_by_month = filtered_data.groupby('Order Month')['Profit'].sum().reset_index()
        fig = px.line(profit_by_month, x='Order Month', y='Profit',
                     title='Monthly Profit Trend',
                     labels={'Order Month': 'Month', 'Profit': 'Total Profit ($)'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Profit by category
        profit_by_category = filtered_data.groupby('Category')['Profit'].sum().reset_index()
        fig = px.pie(profit_by_category, values='Profit', names='Category',
                    title='Profit Distribution by Category',
                    hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    # Profit by sub-category
    profit_by_subcategory = filtered_data.groupby('Sub-Category')['Profit'].sum().reset_index()
    fig = px.bar(profit_by_subcategory.sort_values('Profit', ascending=False), 
                x='Sub-Category', y='Profit',
                title='Profit by Sub-Category',
                color='Profit',
                color_continuous_scale='Greens')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Customer Segment Analysis")
    
    # Sales and profit by segment
    sales_profit_by_segment = filtered_data.groupby('Segment').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=sales_profit_by_segment['Segment'],
        y=sales_profit_by_segment['Sales'],
        name='Sales',
        marker_color=colors.qualitative.Pastel[0]
    ))
    fig.add_trace(go.Bar(
        x=sales_profit_by_segment['Segment'],
        y=sales_profit_by_segment['Profit'],
        name='Profit',
        marker_color=colors.qualitative.Pastel[1]
    ))
    fig.update_layout(
        title='Sales and Profit by Customer Segment',
        barmode='group'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Sales to profit ratio
    sales_profit_by_segment['Sales_to_Profit_Ratio'] = sales_profit_by_segment['Sales'] / sales_profit_by_segment['Profit']
    fig = px.bar(sales_profit_by_segment, 
                x='Segment', y='Sales_to_Profit_Ratio',
                title='Sales to Profit Ratio by Segment',
                labels={'Sales_to_Profit_Ratio': 'Sales/Profit Ratio'})
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Geospatial Analysis")
    
    # Sales by state/region
    sales_by_region = filtered_data.groupby('State')['Sales'].sum().reset_index()
    
    fig = px.choropleth(sales_by_region,
                       locations='State',
                       locationmode='USA-states',
                       color='Sales',
                       scope="usa",
                       color_continuous_scale='Blues',
                       title='Sales by State')
    st.plotly_chart(fig, use_container_width=True)

# Additional features
st.sidebar.header("Additional Options")
show_raw_data = st.sidebar.checkbox("Show raw data")
if show_raw_data:
    st.subheader("Raw Data")
    st.dataframe(data)

# Download button for filtered data
@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')

csv = convert_df(filtered_data)
st.sidebar.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='filtered_ecommerce_data.csv',
    mime='text/csv'
)

# Date range selector
date_range = st.sidebar.date_input(
    "Select Date Range",
    value=[data['Order Date'].min(), data['Order Date'].max()],
    min_value=data['Order Date'].min(),
    max_value=data['Order Date'].max()
)

if len(date_range) == 2:
    filtered_data = filtered_data[
        (filtered_data['Order Date'] >= pd.to_datetime(date_range[0])) &
        (filtered_data['Order Date'] <= pd.to_datetime(date_range[1]))
    ]

# About section
st.sidebar.header("About")
st.sidebar.info(
    """
    This dashboard analyzes Superstore sales data to identify trends and opportunities.
    Use the filters to explore different dimensions of the data.
    """
)