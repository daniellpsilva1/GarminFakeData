import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="General Metrics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': 'Garmin Activity Dashboard - Track your fitness progress'
    }
)

# Hide the default menu and footer
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Import database utilities
from utils.db_utils import init_connection, get_data

# Initialize connection and get data
client = init_connection()

st.title("Garmin Activity Dashboard")

# Load data
try:
    df = get_data()
    
    # Convert date string to datetime
    df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        [df['startTimeLocal'].min(), df['startTimeLocal'].max()]
    )
    
    # Activity type filter
    activity_types = df['activityName'].unique()
    selected_activities = st.sidebar.multiselect(
        "Select Activity Types",
        activity_types,
        default=activity_types
    )
    
    # Ensure we have both start and end dates
    start_date = date_range[0] if isinstance(date_range, (list, tuple)) else date_range
    end_date = date_range[1] if isinstance(date_range, (list, tuple)) and len(date_range) > 1 else start_date

    # Filter data
    mask = (
        (df['startTimeLocal'].dt.date >= start_date) &
        (df['startTimeLocal'].dt.date <= end_date) &
        (df['activityName'].isin(selected_activities))
    )
    filtered_df = df[mask]
    
    # Main dashboard
    col1, col2 = st.columns(2)
    
    # Activity Distance Over Time
    with col1:
        fig_distance = px.line(
            filtered_df,
            x='startTimeLocal',
            y='distance',
            title='Activity Distance Over Time'
        )
        st.plotly_chart(fig_distance, use_container_width=True)
    
    # Heart Rate Distribution
    with col2:
        fig_hr = px.scatter(
            filtered_df,
            x='averageHeartRate',
            y='maxHeartRate',
            color='activityName',
            title='Heart Rate Distribution by Activity Type'
        )
        st.plotly_chart(fig_hr, use_container_width=True)
    
    # Activity Statistics
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric(
            "Total Activities",
            len(filtered_df)
        )
    
    with col4:
        st.metric(
            "Average Distance (km)",
            f"{filtered_df['distance'].mean() / 1000:.2f}"
        )
    
    with col5:
        st.metric(
            "Average VO2 Max",
            f"{filtered_df['vo2Max'].mean():.1f}"
        )
    
    # Recent Activities Table
    st.subheader("Recent Activities")
    recent_activities = filtered_df[[
        'startTimeLocal', 'activityName', 'distance',
        'duration', 'averageHeartRate', 'calories'
    ]].sort_values('startTimeLocal', ascending=False).head(10)
    
    # Format the table
    recent_activities['distance'] = recent_activities['distance'].apply(lambda x: f"{x/1000:.2f} km")
    recent_activities['duration'] = recent_activities['duration'].apply(lambda x: f"{x//60}:{x%60:02d}")
    recent_activities['startTimeLocal'] = recent_activities['startTimeLocal'].dt.strftime('%Y-%m-%d %H:%M')
    
    st.dataframe(recent_activities, use_container_width=True)

except Exception as e:
    st.error(f"Error connecting to MongoDB: {str(e)}")
    st.info("Please ensure you have the correct MongoDB connection string and credentials.")