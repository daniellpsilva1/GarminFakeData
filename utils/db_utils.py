import streamlit as st
import pymongo
import pandas as pd
import os
from dotenv import load_dotenv

# Load environment variables from .env file if running locally
if not hasattr(st, 'secrets'):
    load_dotenv()

@st.cache_resource
def init_connection():
    # Use st.secrets if running in cloud, otherwise use environment variables
    if hasattr(st, 'secrets'):
        username = st.secrets.mongo.username
        password = st.secrets.mongo.password
        cluster = st.secrets.mongo.cluster
    else:
        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        cluster = os.getenv('MONGO_CLUSTER')
    
    return pymongo.MongoClient(
        f"mongodb+srv://{username}:{password}@{cluster}/?retryWrites=true&w=majority&appName=GarminFakeData"
    )

@st.cache_data
def get_data():
    client = init_connection()
    db = client.garmin_data
    items = db.activities.find()
    items = list(items)
    return pd.DataFrame(items)