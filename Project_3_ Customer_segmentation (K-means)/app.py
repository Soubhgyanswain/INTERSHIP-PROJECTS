import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import silhouette_score
import io
import datetime
import logging

# ----------------------------------------------------------
# CONFIG + LOGGING
# ----------------------------------------------------------

st.set_page_config(page_title="Customer Segmentation", layout="wide", page_icon="📊")

# Logging
logging.basicConfig(
    filename='app_logs.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

# ----------------------------------------------------------
# SPLASH SCREEN
# ----------------------------------------------------------

splash_html = """
<style>
#splash-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  animation: fadeOut 3s forwards;
  animation-delay: 2s;
}

#splash-screen h1 {
  color: #ffffff;
  font-size: 4em;
  text-align: center;
  font-family: sans-serif;
  letter-spacing: 2px;
}

@keyframes fadeOut {
  to {
    opacity: 0;
    visibility: hidden;
  }
}
</style>

<div id="splash-screen">
  <h1>✨ Customer Segmentation ✨</h1>
</div>
"""
st.markdown(splash_html, unsafe_allow_html=True)

# ----------------------------------------------------------
# APP TITLE
# ----------------------------------------------------------

st.title("📊 Customer Segmentation Streamlit App")

# ----------------------------------------------------------
# FILE UPLOAD
# ----------------------------------------------------------

st.sidebar.header("Upload Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel (.xlsx) or CSV (.csv) file:",
    type=["csv", "xlsx"],
    accept_multiple_files=False
)

if uploaded_file is not None:

    # ------------------------------------------------------
    # READ UPLOADED FILE
    # ------------------------------------------------------

    with st.spinner("Reading your uploaded file..."):
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            logging.info(f"Uploaded file shape: {df.shape}")
        except Exception as e:
            logging.error(f"Error reading uploaded file: {e}")
            st.error(f"❌ Failed to read uploaded file: {e}")
            st.stop()

    # ------------------------------------------------------
    # CLEANING
    # ------------------------------------------------------

    with st.spinner("Cleaning data..."):

        try:
            if 'Customer ID' not in df.columns:
                st.error("The file does not contain a 'Customer ID' column.")
                st.stop()

            df = df.dropna(subset=['Customer ID'])
            df.drop_duplicates(inplace=True)

            # Fill numeric nulls with 0 for simplicity
            num_cols = df.select_dtypes(include=np.number).columns.tolist()
            df[num_cols] = df[num_cols].fillna(0)

            if 'TotalPrice' not in df.columns:
                if 'Quantity' in df.columns and 'Price' in df.columns:
                    df['TotalPrice'] = df['Quantity'] * df['Price']
                else:
                    df['TotalPrice'] = 0

            logging.info("Data cleaned successfully.")
        except Exception as e:
            logging.error(f"Data cleaning error: {e}")
            st.error(f"Error cleaning data: {e}")
            st.stop()

    # ------------------------------------------------------
    # DATA PREVIEW
    # ------------------------------------------------------

    st.subheader("🔎 Data Preview")
    st.dataframe(df.head(10))

    # ------------------------------------------------------
    # TOP COUNTRIES
    # ------------------------------------------------------

    st.subheader("🌍 Top 10 Countries by Unique Customers")

    try:
        if 'Country' in df.columns:
            country_data = df.groupby("Country")["Customer ID"].nunique().sort_values(ascending=False).head(10)
            fig_country = px.bar(
                country_data,
                x=country_data.index,
                y=country_data.values,
                title="Top 10 Countries by Unique Customers",
                labels={"y": "Unique Customers", "x": "Country"}
            )
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.info("No 'Country' column found in the data.")
    except Exception as e:
        st.error(f"Error plotting country data: {e}")

    # ------------------------------------------------------
    # TOP PRODUCTS
    # ------------------------------------------------------

    st.subheader("🛒 Top 10 Selling Products")

    try:
        if 'Description' in df.columns:
            top_products = df['Description'].value_counts().head(10)
            fig_products = px.bar(
                top_products,
                x=top_products.index,
                y=top_products.values,
                title="Top 10 Selling Products",
                labels={"y": "Units Sold", "x": "Product"}
            )
            st.plotly_chart(fig_products, use_container_width=True)
        else:
            st.info("No 'Description' column found in the data.")
    except Exception as e:
        st.error(f"Error plotting product data: {e}")

    # ------------------------------------------------------
    # CUSTOMER FEATURES CLUSTERING
    # ------------------------------------------------------

    st.subheader("🧑‍💼 Customer Feature Clustering")

    try:
        if all(col in df.columns for col in ['Invoice', 'Quantity', 'TotalPrice', 'Price']):
            customer_features = df.groupby('Customer ID').agg({
                'Invoice': 'nunique',
                'Quantity': 'sum',
                'TotalPrice': 'sum',
                'Price': 'mean'
            }).reset_index()

            customer_features.columns = ['CustomerID', 'NumInvoices', 'TotalQuantity', 'TotalSpent', 'AvgPrice']

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(customer_features[['NumInvoices', 'TotalQuantity', 'TotalSpent', 'AvgPrice']])

            k_val = st.slider("Select number of clusters for customer features:", 2, 8, 4)

            model = KMeans(n_clusters=k_val, random_state=42, n_init=10)
            customer_features['Cluster'] = model.fit_predict(X_scaled)

            fig_pair = px.scatter_matrix(
                customer_features,
                dimensions=['NumInvoices', 'TotalQuantity', 'TotalSpent', 'AvgPrice'],
                color='Cluster',
                title="Customer Clusters (Feature Space)",
                height=700
            )
            st.plotly_chart(fig_pair, use_container_width=True)
        else:
            st.info("Some required columns are missing for customer feature clustering.")
    except Exception as e:
        st.error(f"Error during customer feature clustering: {e}")
        logging.error(f"Customer feature clustering error: {e}")

    # ------------------------------------------------------
    # RFM ANALYSIS
    # ------------------------------------------------------

    st.subheader("📊 RFM Analysis")

    try:
        if 'InvoiceDate' in df.columns:
            snapshot_date = df['InvoiceDate'].max() + pd.Timedelta(days=1)

            rfm = df.groupby('Customer ID').agg({
                'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
                'Invoice': 'nunique',
                'TotalPrice': 'sum'
            })
            rfm.columns = ['Recency', 'Frequency', 'Monetary']

            fig_r = px.histogram(rfm, x='Recency', nbins=30, title='Recency Distribution')
            fig_f = px.histogram(rfm, x='Frequency', nbins=30, title='Frequency Distribution')
            fig_m = px.histogram(rfm, x='Monetary', nbins=30, title='Monetary Distribution')

            st.plotly_chart(fig_r, use_container_width=True)
            st.plotly_chart(fig_f, use_container_width=True)
            st.plotly_chart(fig_m, use_container_width=True)

            # RFM heatmap
            rfm['R_score'] = pd.qcut(rfm['Recency'], 4, labels=[4,3,2,1])
            rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 4, labels=[1,2,3,4])
            rfm['M_score'] = pd.qcut(rfm['Monetary'], 4, labels=[1,2,3,4])

            rfm['RFM_Score'] = rfm[['R_score', 'F_score', 'M_score']].astype(int).sum(axis=1)

            heat_data = rfm.groupby(['R_score', 'F_score']).size().reset_index(name='Count')
            heatmap_fig = px.density_heatmap(
                heat_data,
                x='F_score',
                y='R_score',
                z='Count',
                color_continuous_scale='Viridis',
                title="RFM Heatmap"
            )
            st.plotly_chart(heatmap_fig, use_container_width=True)

            # Segment customers
            rfm['Segment'] = pd.cut(
                rfm['RFM_Score'],
                bins=[0,4,6,8,10,12],
                labels=['At Risk', 'Need Attention', 'Potential Loyalist', 'Loyal', 'Champion']
            )

            seg_counts = rfm['Segment'].value_counts().reindex(
                ['Champion','Loyal','Potential Loyalist','Need Attention','At Risk']
            )

            seg_fig = px.bar(
                seg_counts,
                x=seg_counts.index,
                y=seg_counts.values,
                title="Customer Segments Based on RFM Score",
                labels={"x":"Segment", "y":"Number of Customers"}
            )
            st.plotly_chart(seg_fig, use_container_width=True)

        else:
            st.info("No 'InvoiceDate' column found for RFM analysis.")
    except Exception as e:
        st.error(f"Error during RFM analysis: {e}")
        logging.error(f"RFM analysis error: {e}")

    # ------------------------------------------------------
    # CLUSTER EVALUATION
    # ------------------------------------------------------

    st.subheader("📐 Evaluate Clustering")

    try:
        if 'InvoiceDate' in df.columns:
            X_rfm = rfm[['Recency', 'Frequency', 'Monetary']].values

            wcss = []
            sil_scores = []

            for k in range(2, 9):
                kmeans = KMeans(n_clusters=k, random_state=42)
                kmeans.fit(X_rfm)
                wcss.append(kmeans.inertia_)
                sil = silhouette_score(X_rfm, kmeans.labels_)
                sil_scores.append(sil)

            fig_elbow = px.line(
                x=list(range(2,9)),
                y=wcss,
                markers=True,
                title="Elbow Method (WCSS)",
                labels={"x":"Number of Clusters", "y":"WCSS"}
            )
            st.plotly_chart(fig_elbow, use_container_width=True)

            fig_sil = px.line(
                x=list(range(2,9)),
                y=sil_scores,
                markers=True,
                title="Silhouette Scores",
                labels={"x":"Number of Clusters", "y":"Silhouette Score"}
            )
            st.plotly_chart(fig_sil, use_container_width=True)

    except Exception as e:
        st.error(f"Error during clustering evaluation: {e}")
        logging.error(f"Clustering evaluation error: {e}")

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    st.subheader("⬇ Download RFM Data")

    try:
        csv_data = rfm.reset_index().to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download RFM Data as CSV",
            csv_data,
            file_name="rfm_data.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error preparing download: {e}")
        logging.error(f"Download error: {e}")

else:
    st.info("Please upload an Excel (.xlsx) or CSV (.csv) file to start the analysis.")