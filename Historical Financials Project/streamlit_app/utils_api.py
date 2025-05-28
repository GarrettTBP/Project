import os
import requests
import pandas as pd
import streamlit as st

# Base URL for your Django API
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000/api")

# Helper to handle API responses and errors
def _handle_response(resp):
    try:
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"API error: {e} - {resp.text}")
        return None

# Property endpoints
def get_properties():
    resp = requests.get(f"{API_BASE}/properties/")
    return _handle_response(resp) or []

def add_property(data):
    resp = requests.post(f"{API_BASE}/properties/", json=data)
    return _handle_response(resp)

# Expense endpoints
def get_expenses():
    resp = requests.get(f"{API_BASE}/expenses/")
    return _handle_response(resp) or []

def add_expense(data):
    resp = requests.post(f"{API_BASE}/expenses/", json=data)
    return _handle_response(resp)
def get_units(property_id=None):
    url = f"{API_BASE}/units/"
    if property_id is not None:
        url += f"?property={property_id}"
    resp = requests.get(url)
    resp.raise_for_status()
    return pd.DataFrame(resp.json())

def add_unit(unit):
    """
    unit = {
      'property': <property_id>,
      'unit_number': <int>,
      'square_footage': <float>
    }
    """
    resp = requests.post(f"{API_BASE}/units/", json=unit)
    resp.raise_for_status()
    return resp.json()