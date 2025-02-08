import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Detailed Activity Metrics Analysis",
    page_icon="📊",
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
        .stDateInput {
            width: 100%;
            position: relative;
        }
        .stDateInput > div[data-baseweb="input"] {
            width: 100%;
        }
        .stDateInput input {
            max-width: 100%;
            padding-right: 10px;
        }
        .stDateInput > div[data-baseweb="calendar"] {
            max-width: 100%;
            width: fit-content !important;
            position: absolute;
            z-index: 1000;
            background: white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
            overflow: visible;
        }
    </style>
""", unsafe_allow_html=True)

# Import database utilities
from utils.db_utils import init_connection, get_data

# Initialize connection and get data
client = init_connection()
df = get_data()

st.title("Detailed Activity Metrics Analysis")

# Convert date string to datetime if needed
df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

# Sidebar filters
st.sidebar.header("Filters")

# Date range filter
date_range = st.sidebar.date_input(
    "Select Date Range",
    [df['startTimeLocal'].min(), df['startTimeLocal'].max()]
)

# Ensure we have both start and end dates
start_date = date_range[0] if isinstance(date_range, (list, tuple)) else date_range
end_date = date_range[1] if isinstance(date_range, (list, tuple)) and len(date_range) > 1 else start_date

# Activity type filter
activity_types = df['activityName'].unique()
selected_activity = st.sidebar.selectbox(
    "Select Activity Type",
    activity_types
)

# Filter data
mask = (
    (df['startTimeLocal'].dt.date >= start_date) &
    (df['startTimeLocal'].dt.date <= end_date) &
    (df['activityName'] == selected_activity)
)
filtered_df = df[mask]

# Process splits data
def process_splits_data(activity_row):
    splits_data = activity_row['splits']
    if not splits_data:
        return pd.DataFrame()
    
    # Calculate metrics per km
    total_steps = activity_row['steps']
    total_distance = sum(split['distance'] for split in splits_data)
    steps_per_meter = total_steps / total_distance if total_distance > 0 else 0
    
    splits_metrics = []
    for split in splits_data:
        if split['distance'] == 1000:  # Only process 1km splits
            split_steps = int(split['distance'] * steps_per_meter)
            split_metrics = {
                'kilometer': len(splits_metrics) + 1,
                'steps': split_steps,
                'time': split['time'],  # Time in seconds
                'speed': (split['distance'] / split['time']) * 3.6,  # Convert to km/h
                'activity_date': activity_row['startTimeLocal'],
                'avg_heart_rate': activity_row['averageHeartRate'],
                'max_heart_rate': activity_row['maxHeartRate']
            }
            splits_metrics.append(split_metrics)
    
    return pd.DataFrame(splits_metrics)

# Process all activities
all_splits = []
for _, activity in filtered_df.iterrows():
    splits_df = process_splits_data(activity)
    if not splits_df.empty:
        all_splits.append(splits_df)

if all_splits:
    combined_splits = pd.concat(all_splits)
    
    # Create visualizations
    # Steps per kilometer
    # Calculate y-axis range for steps graph
    min_steps = combined_splits['steps'].min()
    max_steps = combined_splits['steps'].max()
    steps_padding = (max_steps - min_steps) * 0.1  # Add 10% padding
    
    fig_steps = px.line(
        combined_splits,
        x='kilometer',
        y='steps',
        color='activity_date',
        title='Steps per Kilometer'
    )
    fig_steps.update_layout(
        yaxis=dict(
            range=[max(0, min_steps - steps_padding), max_steps + steps_padding]
        )
    )
    st.plotly_chart(fig_steps, use_container_width=True)
    
    # Speed per kilometer
    fig_speed = px.line(
        combined_splits,
        x='kilometer',
        y='speed',
        color='activity_date',
        title='Speed per Kilometer (km/h)'
    )
    st.plotly_chart(fig_speed, use_container_width=True)
    
    # Heart Rate per kilometer
    # Calculate y-axis range for heart rate graph
    min_hr = min(combined_splits['avg_heart_rate'].min(), combined_splits['max_heart_rate'].min())
    max_hr = max(combined_splits['avg_heart_rate'].max(), combined_splits['max_heart_rate'].max())
    hr_padding = (max_hr - min_hr) * 0.1  # Add 10% padding
    
    fig_hr = px.line(
        combined_splits,
        x='kilometer',
        y=['avg_heart_rate', 'max_heart_rate'],
        color='activity_date',
        title='Heart Rate per Kilometer'
    )
    fig_hr.update_layout(
        yaxis=dict(
            range=[max(0, min_hr - hr_padding), max_hr + hr_padding]
        )
    )
    st.plotly_chart(fig_hr, use_container_width=True)
    
    # Statistics table
    st.subheader("Kilometer Split Statistics")

    stats_df = combined_splits.groupby('kilometer').agg({
        'steps': ['mean', 'min', 'max'],
        'speed': ['mean', 'min', 'max'],
        'avg_heart_rate': ['mean', 'min', 'max'],
        'max_heart_rate': ['mean', 'min', 'max']
    }).round(2)
    
    # Rename columns to be more descriptive and ensure uniqueness
    stats_df.columns = [
        'Avg Steps', 'Min Steps', 'Max Steps',
        'Avg Speed', 'Min Speed', 'Max Speed',
        'Avg HR (Avg)', 'Min HR (Avg)', 'Max HR (Avg)',
        'Avg HR (Max)', 'Min HR (Max)', 'Max HR (Max)'
    ]
    st.dataframe(stats_df, use_container_width=True)
else:
    st.info("No kilometer splits data available for the selected filters.")