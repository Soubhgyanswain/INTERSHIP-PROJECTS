import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.cluster import DBSCAN
from sklearn.ensemble import IsolationForest
from prophet import Prophet
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time
import warnings
warnings.filterwarnings('ignore')

# Configure the app
st.set_page_config(
    page_title="🚦 India Traffic Analysis Dashboard",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stAlert {
        border-radius: 10px;
    }
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        border-left: 4px solid #4CAF50;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card h3 {
        font-size: 1rem;
        margin: 0;
        color: #666;
    }
    .metric-card h2 {
        font-size: 1.8rem;
        margin: 5px 0 0 0;
        color: #2e7d32;
    }
    .st-bb {
        background-color: transparent;
    }
    .st-at {
        background-color: #e8f5e9;
    }
    .st-ax {
        background-color: #4CAF50;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    .header-style {
        background-color: rgba(232, 245, 233, 0.9);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #2e7d32;
    }
    .header-title {
        color: #2e7d32;
        margin-bottom: 0;
    }
    .header-subtitle {
        color: #2e7d32;
        margin-bottom: 0;
    }
    @media (prefers-color-scheme: dark) {
        .header-style {
            background-color: rgba(30, 50, 30, 0.9);
            border-color: #4CAF50;
        }
        .header-title, .header-subtitle {
            color: #e8f5e9;
        }
    }
    .search-box {
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# App title and description
st.markdown("""
<div class="header-style">
    <h1 class="header-title">🚦 India Traffic Pattern Analysis</h1>
    <p class="header-subtitle">Interactive Traffic Monitoring Dashboard for Indian Cities</p>
    <p class="header-subtitle">Analyze live traffic patterns, detect anomalies, and predict future congestion</p>
</div>
""", unsafe_allow_html=True)

# ====================== DATA GENERATION ======================
@st.cache_data(ttl=300)  # Cache for 5 minutes
def generate_india_traffic_data(num_points=10000, days_history=7, city="Delhi"):
    """Generate realistic traffic data for Indian cities"""
    try:
        # Get city coordinates with error handling
        geolocator = Nominatim(user_agent="india_traffic_app")
        try:
            location = geolocator.geocode(city + ", India", timeout=10)
            if not location:
                st.warning(f"Could not geocode {city}, using Delhi as default")
                location = geolocator.geocode("Delhi, India")
        except GeocoderTimedOut:
            st.warning("Geocoding timed out, using Delhi coordinates")
            location = geolocator.geocode("Delhi, India")
            
        if not location:
            raise ValueError("Could not geocode location")
            
        base_lat, base_lon = location.latitude, location.longitude
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_history)
        
        np.random.seed(42)
        timestamps = pd.date_range(start_date, end_date, periods=num_points)
        
        # Indian vehicle distribution (adjusted for India)
        vehicle_types = ['car', 'motorcycle', 'truck', 'bus', 'auto']
        vehicle_probs = [0.5, 0.3, 0.1, 0.05, 0.05]
        
        data = pd.DataFrame({
            'timestamp': timestamps,
            'latitude': base_lat + np.random.normal(0, 0.02, num_points),
            'longitude': base_lon + np.random.normal(0, 0.02, num_points),
            'speed': np.random.uniform(5, 60, num_points),  # km/h
            'vehicle_type': np.random.choice(vehicle_types, num_points, p=vehicle_probs)
        })
        
        # Indian traffic patterns (longer rush hours)
        for day in range(days_history):
            day_date = start_date + timedelta(days=day)
            day_mask = (timestamps >= day_date) & (timestamps < day_date + timedelta(days=1))
            
            # Weekday vs weekend patterns
            if day_date.weekday() < 5:  # Weekday
                morning_rush = ((timestamps.hour >= 7) & (timestamps.hour <= 11))  # 7-11am
                evening_rush = ((timestamps.hour >= 16) & (timestamps.hour <= 21))  # 4-9pm
                data.loc[day_mask & (morning_rush | evening_rush), 'speed'] *= np.random.uniform(0.2, 0.4)
            else:  # Weekend
                afternoon_slow = ((timestamps.hour >= 12) & (timestamps.hour <= 19))
                data.loc[day_mask & afternoon_slow, 'speed'] *= np.random.uniform(0.5, 0.7)
        
        # Add random incidents (higher probability during rush hours)
        incident_prob = 0.002 * (1 + np.sin(timestamps.hour * np.pi / 12))
        incidents = np.random.random(len(data)) < incident_prob
        data.loc[incidents, 'speed'] *= np.random.uniform(0.1, 0.3)
        
        return data, base_lat, base_lon
    
    except Exception as e:
        st.error(f"Error generating data: {str(e)}")
        # Return default Delhi data if error occurs
        base_lat, base_lon = 28.6139, 77.2090
        data = pd.DataFrame({
            'timestamp': pd.date_range(end_date - timedelta(days=days_history), end_date, periods=num_points),
            'latitude': base_lat + np.random.normal(0, 0.02, num_points),
            'longitude': base_lon + np.random.normal(0, 0.02, num_points),
            'speed': np.random.uniform(5, 60, num_points),
            'vehicle_type': np.random.choice(vehicle_types, num_points, p=vehicle_probs)
        })
        return data, base_lat, base_lon

# ====================== SIDEBAR CONTROLS ======================
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # City search
    st.subheader("City Selection")
    city_search = st.text_input("Search any city in India", "Bhubaneswar", 
                              help="Enter any Indian city name")
    
    # Data controls
    days_history = st.slider("Days of history to analyze", 1, 30, 7)
    refresh_data = st.button("🔄 Refresh Data", help="Generate fresh traffic data")
    
    # Analysis parameters
    st.subheader("Analysis Settings")
    speed_threshold = st.slider("Congestion threshold (km/h)", 5, 30, 20, help="Speed below which traffic is considered congested")
    anomaly_sensitivity = st.slider("Anomaly sensitivity", 1, 10, 3, help="Higher values detect more anomalies")
    
    # Map options
    st.subheader("Map Display")
    show_heatmap = st.checkbox("Show heatmap", True)
    show_clusters = st.checkbox("Show clusters", True)
    map_style = st.selectbox("Map style", ["OpenStreetMap", "CartoDB positron", "Stamen Terrain"])
    
    # About section
    st.markdown("---")
    st.markdown("""
    **About this dashboard:**
    - Simulates realistic traffic patterns for Indian cities
    - Updates predictions in real-time
    - Detects congestion and anomalies
    - Works with any Indian city
    """)

# Load or refresh data
if refresh_data or 'traffic_df' not in st.session_state or 'city_search' not in st.session_state or st.session_state.city_search != city_search:
    with st.spinner(f"Generating traffic data for {city_search}..."):
        traffic_df, base_lat, base_lon = generate_india_traffic_data(days_history=days_history, city=city_search)
        st.session_state.traffic_df = traffic_df
        st.session_state.base_lat = base_lat
        st.session_state.base_lon = base_lon
        st.session_state.city_search = city_search
        st.session_state.last_updated = datetime.now()
        st.success(f"Data for {city_search} loaded successfully!")

traffic_df = st.session_state.traffic_df
base_lat = st.session_state.base_lat
base_lon = st.session_state.base_lon

# ====================== METRICS DASHBOARD ======================
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🚗 Total Vehicles</h3>
        <h2>{:,}</h2>
    </div>
    """.format(len(traffic_df)), unsafe_allow_html=True)

with col2:
    avg_speed = traffic_df['speed'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <h3>📊 Avg Speed</h3>
        <h2>{avg_speed:.1f} km/h</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    congestion_pct = (len(traffic_df[traffic_df['speed'] < speed_threshold]) / len(traffic_df)) * 100
    st.markdown(f"""
    <div class="metric-card">
        <h3>⚠️ Congestion</h3>
        <h2>{congestion_pct:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h3>🕒 Last Updated</h3>
        <h2>{st.session_state.last_updated.strftime('%H:%M:%S')}</h2>
    </div>
    """, unsafe_allow_html=True)

# ====================== MAIN TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["🌍 Live Map", "📈 Trends", "⚠️ Alerts", "🔮 Forecast"])

with tab1:
    st.header(f"🌍 Real-Time Traffic Map - {city_search}")
    
    # Time window filter
    time_window = st.select_slider("Time window", 
                                 options=["Last hour", "Last 6 hours", "Last 24 hours", "All data"],
                                 value="Last 24 hours")
    
    # Apply time filter
    time_map = {
        "Last hour": 1,
        "Last 6 hours": 6,
        "Last 24 hours": 24,
        "All data": 24 * days_history
    }
    filtered_df = traffic_df[traffic_df['timestamp'] >= datetime.now() - timedelta(hours=time_map[time_window])]
    
    # Create the map
    m = folium.Map(location=[base_lat, base_lon], 
                  zoom_start=12, 
                  tiles=map_style,
                  control_scale=True)
    
    # Add heatmap if enabled
    if show_heatmap and len(filtered_df) > 0:
        HeatMap(filtered_df[['latitude', 'longitude', 'speed']].values,
               radius=10,
               gradient={0.2: 'blue', 0.4: 'lime', 0.6: 'orange', 1: 'red'},
               blur=15).add_to(m)
    
    # Add clusters if enabled
    if show_clusters and len(filtered_df) > 0:
        # Detect congestion clusters
        slow_traffic = filtered_df[filtered_df['speed'] < speed_threshold]
        if len(slow_traffic) > 0:
            coords = slow_traffic[['latitude', 'longitude']].values
            db = DBSCAN(eps=0.02, min_samples=20).fit(coords)
            slow_traffic['cluster'] = db.labels_
            
            for _, row in slow_traffic.iterrows():
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=5,
                    color='red' if row['cluster'] == -1 else 'blue',
                    fill=True,
                    fill_opacity=0.7,
                    popup=f"Speed: {row['speed']:.1f} km/h\nType: {row['vehicle_type']}\nTime: {row['timestamp']}"
                ).add_to(m)
    
    # Display the map
    st_folium(m, width=1200, height=600, returned_objects=[])

with tab2:
    st.header(f"📈 Traffic Trends Analysis - {city_search}")
    
    # Add temporal aggregations
    traffic_df['hour'] = traffic_df['timestamp'].dt.hour
    traffic_df['day_of_week'] = traffic_df['timestamp'].dt.day_name()
    traffic_df['date'] = traffic_df['timestamp'].dt.date
    
    # Plot hourly patterns
    st.subheader("Hourly Speed Patterns")
    fig1 = px.line(traffic_df.groupby(['day_of_week', 'hour'])['speed'].mean().reset_index(),
                 x='hour', y='speed', color='day_of_week',
                 title='Average Speed by Hour and Day of Week',
                 labels={'hour': 'Hour of Day', 'speed': 'Speed (km/h)'})
    fig1.add_hline(y=speed_threshold, line_dash="dash", line_color="red", 
                  annotation_text="Congestion Threshold", 
                  annotation_position="bottom right")
    st.plotly_chart(fig1, use_container_width=True)
    
    # Vehicle type analysis
    st.subheader("Vehicle Type Distribution")
    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.pie(traffic_df, names='vehicle_type', 
                     title='Vehicle Type Distribution')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        fig3 = px.box(traffic_df, x='vehicle_type', y='speed',
                     title='Speed Distribution by Vehicle Type')
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.header(f"⚠️ Traffic Alerts & Anomalies - {city_search}")
    
    # Anomaly detection
    with st.spinner("Detecting anomalies..."):
        traffic_df['day_of_week_num'] = traffic_df['timestamp'].dt.dayofweek
        traffic_df['is_weekend'] = traffic_df['day_of_week_num'].isin([5,6]).astype(int)
        traffic_df['time_of_day'] = traffic_df['timestamp'].dt.hour + traffic_df['timestamp'].dt.minute/60
        
        features = traffic_df[['hour', 'latitude', 'longitude', 'speed', 'day_of_week_num', 'is_weekend', 'time_of_day']]
        model = IsolationForest(contamination=0.01 * anomaly_sensitivity/10, 
                              random_state=42)
        traffic_df['anomaly'] = model.fit_predict(features)
        anomalies = traffic_df[traffic_df['anomaly'] == -1]
        recent_anomalies = anomalies[anomalies['timestamp'] >= datetime.now() - timedelta(hours=24)]
    
    st.success(f"Detected {len(recent_anomalies)} potential incidents in last 24 hours")
    
    if len(recent_anomalies) > 0:
        # Show recent anomalies
        st.subheader("Recent Incidents")
        st.dataframe(recent_anomalies.sort_values('timestamp', ascending=False).head(10)[
            ['timestamp', 'latitude', 'longitude', 'speed', 'vehicle_type']
        ], height=300)
        
        # Anomaly map
        st.subheader("Incident Locations")
        m_anomalies = folium.Map(location=[base_lat, base_lon], zoom_start=12)
        
        for _, row in recent_anomalies.iterrows():
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                color='red',
                fill=True,
                popup=f"Time: {row['timestamp']}\nSpeed: {row['speed']:.1f} km/h"
            ).add_to(m_anomalies)
        
        st_folium(m_anomalies, width=1200, height=400)
    else:
        st.info("No anomalies detected with current settings")

with tab4:
    st.header(f"🔮 Traffic Forecast - {city_search}")
    
    with st.spinner("Generating forecast..."):
        # Prepare data
        hourly_counts = traffic_df.resample('H', on='timestamp').size().reset_index()
        hourly_counts.columns = ['ds', 'y']
        
        # Train model
        model = Prophet(seasonality_mode='multiplicative',
                       yearly_seasonality=False,
                       weekly_seasonality=True,
                       daily_seasonality=True,
                       changepoint_prior_scale=0.05)
        model.fit(hourly_counts)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=48, freq='H')
        forecast = model.predict(future)
        
        # Plot forecast
        st.subheader("48-Hour Traffic Forecast")
        fig1 = model.plot(forecast)
        current_time = datetime.now()
        plt.axvline(x=current_time, color='r', linestyle='--', label='Current Time')
        plt.title('Predicted Traffic Volume')
        plt.legend()
        st.pyplot(fig1)
        
        # Show components
        st.subheader("Forecast Components")
        fig2 = model.plot_components(forecast)
        st.pyplot(fig2)
        
        # Calculate forecast change
        forecast_change = forecast['yhat'][-48:].mean()/hourly_counts['y'].mean()*100-100
        st.metric("Forecast Change", f"{forecast_change:.1f}%")

# ====================== FOOTER ======================
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;font-size:0.9em">
    <p>India Traffic Analysis Dashboard • Last update: {}</p>
    <p>Data simulated for demonstration purposes • Works with any Indian city</p>
</div>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)