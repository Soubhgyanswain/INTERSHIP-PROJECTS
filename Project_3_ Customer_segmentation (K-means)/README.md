## 📊 Customer Segmentation Analysis using K-Means

This project showcases an end-to-end **Customer Segmentation Analysis** developed during my **Tamizhan Skills Rise Internship**. It combines detailed data exploration, machine learning clustering, and a fully interactive Streamlit web application for business stakeholders to analyze customer behavior, identify valuable segments, and optimize marketing strategies.

---

## 📝 Project Overview

The primary objective of this project is to:

- Perform exploratory data analysis (EDA) to understand customer behavior patterns.
- Identify key customer segments using RFM (Recency, Frequency, Monetary) analysis and K-Means clustering.
- Visualize insights using interactive charts.
- Build an intuitive web dashboard for business users to upload their own data and explore segmentation insights without writing code.

The project involves two key components:

- **Jupyter Notebook**: Performs data cleaning, analysis, clustering, and in-depth data visualizations.
- **Streamlit App**: Provides an interactive user interface for real-time analysis, cluster evaluation, and results export.

This project is particularly beneficial for retail businesses looking to understand customer loyalty, improve retention strategies, and target high-value customers effectively.

---

## 🔧 Tools & Libraries

- Python
- Pandas
- NumPy
- Scikit-learn
- Matplotlib
- Seaborn
- Plotly
- Streamlit

---

## Key Features & Functionalities

### Data Cleaning & Preparation

- Handles missing values and duplicates.
- Calculates `TotalPrice` for each transaction when not provided in the data.
- Generates aggregated customer-level features for further analysis.

### Exploratory Data Analysis (EDA)

- Displays dataset structure, null-value analysis, and basic statistical descriptions.
- Visualizes:
  - Top 10 countries by unique customers.
  - Top-selling products in the dataset.

### RFM Analysis

- Calculates Recency, Frequency, and Monetary values for each customer.
- Generates distributions for Recency, Frequency, and Monetary scores.
- Assigns RFM scores and segments customers into:
  - Champion
  - Loyal
  - Potential Loyalist
  - Need Attention
  - At Risk
- Visualizes customer segments using bar plots and heatmaps to show segment distributions.

### K-Means Clustering

- Performs clustering on aggregated customer features such as:
  - Number of invoices
  - Total quantity purchased
  - Total spending
  - Average price per purchase
- Evaluates clustering performance through:
  - Elbow method (WCSS plot)
  - Silhouette score analysis
- Allows users to experiment with different numbers of clusters.

### Streamlit Interactive Dashboard

- Uploads custom retail data (CSV or Excel).
- Displays top countries and products dynamically.
- Runs live customer feature clustering and RFM analysis.
- Allows:
  - Interactive cluster visualization via scatter matrix.
  - Selection of cluster counts via sliders.
- Provides interactive evaluation of cluster quality using:
  - Elbow plots
  - Silhouette score charts
- Enables downloading RFM segment data for further use.

### Error Handling & User Experience

- Provides user-friendly error messages for missing columns or incompatible file uploads.
- Implements a custom splash screen in the Streamlit app for branding and enhanced UX.
- Includes a logging mechanism to track errors and processes during user interactions.

---

## How to Run

### Running Jupyter Notebook

1. Open the `.ipynb` file in Jupyter Notebook or JupyterLab.
2. Ensure the required packages are installed:
    ```bash
    pip install pandas numpy scikit-learn matplotlib seaborn
    ```
3. Run all cells to perform:
    - Data cleaning
    - EDA
    - RFM analysis
    - Customer segmentation
    - Visualizations of clusters

> **Note:** Ensure your data file (`online_retail_II.xlsx`) is placed in the same directory as the notebook.

---

### Running the Streamlit App

1. Clone this repository.

2. Install necessary dependencies:

    ```bash
    pip install streamlit pandas numpy scikit-learn plotly openpyxl
    ```

3. Run the app:

    ```bash
    streamlit run app.py
    ```

4. Open the URL provided in your terminal (usually `http://localhost:8501`).

5. Upload a retail dataset in `.xlsx` or `.csv` format to begin analysis.

---

## Insights Gained

- Identified customer segments with high monetary value and frequent purchases.
- Discovered a significant proportion of customers contributing a majority of revenue, revealing the potential for targeted marketing.
- Visualized purchasing trends and product popularity across regions and customer groups.
- Provided actionable business insights that can drive marketing strategies and customer retention efforts.

---

## Author

Developed by **Soubhagya**  
RISE Internship | Tamizhan Skills
