# 🚦 India Traffic Pattern Analysis Dashboard

This project presents an interactive **India Traffic Pattern Analysis Dashboard** developed during my **Tamizhan Skills Rise Internship**. The dashboard simulates real-time traffic data for Indian cities, helping analyze traffic congestion, detect anomalies, and forecast future trends.

---

## 📝 Project Overview

The objective of this project is to:

- Visualize traffic patterns in Indian cities.
- Identify congestion zones and potential incidents.
- Predict future traffic loads for better urban planning.

The dashboard is built using **Streamlit**, with advanced mapping via **Folium**, time-series modeling using **Prophet**, and interactive charts powered by **Plotly**.

---

## 🔧 Tools & Libraries

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- Folium
- Scikit-learn
- Prophet
- Geopy

---

## Key Features & Visualizations

- Simulates realistic traffic data for any Indian city based on geolocation.
- Allows user customization:
  - City selection
  - Historical data window
  - Congestion thresholds
  - Anomaly sensitivity
  - Map styling
- Live interactive map with:
  - Traffic heatmaps indicating congestion levels
  - Cluster markers for congestion incidents
- Traffic trends analysis:
  - Hourly speed trends across days of the week
  - Vehicle type distribution and speed variations
- Alerts & anomalies:
  - Detects unusual traffic behavior using Isolation Forest
  - Maps recent anomalies and displays incident details
- Forecasting module:
  - Predicts traffic volume for the next 48 hours using Prophet time-series forecasting
  - Displays forecast trends and seasonal patterns

---

## How to Run

1. Clone this repository.

2. Install required Python libraries:

    ```bash
    pip install streamlit pandas numpy plotly folium scikit-learn prophet geopy streamlit-folium
    ```

3. Run the Streamlit app:

    ```bash
    streamlit run app.py
    ```

4. Open your browser and navigate to the displayed local URL (usually `http://localhost:8501`).

> **Note:** All data is simulated and generated dynamically within the app.

---

## Insights Gained

- Provides valuable insights into urban traffic behavior, congestion hotspots, and potential incident zones.
- Enables proactive planning for traffic management based on forecasts.
- Demonstrates how AI models like Isolation Forest and Prophet can enhance traffic analysis for smart cities.

---

## Author

Developed by **Soubhagya**  
RISE Internship | Tamizhan Skills
