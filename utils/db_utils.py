import streamlit as st
import pymongo
import pandas as pd

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(
        "mongodb+srv://DanielSilva:danielsilva@garminfakedata.qppxh.mongodb.net/?retryWrites=true&w=majority&appName=GarminFakeData"
    )

@st.cache_data
def get_data():
    client = init_connection()
    db = client.garmin_data
    items = db.activities.find()
    items = list(items)
    return pd.DataFrame(items)