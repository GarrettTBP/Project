import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Set page configuration
st.set_page_config(page_title="Visualize Data", layout="wide")

# Load data
@st.cache_data
def load_data():
    # Replace with your actual data loading logic
    df = pd.read_csv("data/financials.csv", parse_dates=["Date"])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("Filters")

# Property Type Filter
property_types = df["Property Type"].dropna().unique()
selected_property_types = st.sidebar.multiselect("Property Type", options=property_types, default=property_types)

# Location Filter
locations = df["Location"].dropna().unique()
selected_locations = st.sidebar.multiselect("Location", options=locations, default=locations)

# Per Unit Toggle
per_unit = st.sidebar.checkbox("Per Unit", value=False)

# Time Frame Selection
st.sidebar.header("Time Frame")
time_frame = st.sidebar.radio("Select Time Frame", options=["T3", "T12", "Monthly"], index=1)

# Expense Category Selection
expense_categories = df["Expense Category"].dropna().unique()
selected_category = st.sidebar.selectbox("Expense Category", options=expense_categories)

# Filter Data Based on Selections
filtered_df = df[
    (df["Property Type"].isin(selected_property_types)) &
    (df["Location"].isin(selected_locations)) &
    (df["Expense Category"] == selected_category)
].copy()

# Apply Time Frame Filtering
latest_date = filtered_df["Date"].max()
if time_frame == "T3":
    start_date = latest_date - pd.DateOffset(months=3)
    filtered_df = filtered_df[filtered_df["Date"] >= start_date]
elif time_frame == "T12":
    start_date = latest_date - pd.DateOffset(months=12)
    filtered_df = filtered_df[filtered_df["Date"] >= start_date]
# For "Monthly", we assume the data is already in monthly granularity

# Apply Per Unit Calculation if Toggle is On
if per_unit:
    filtered_df["Expense Per Unit"] = filtered_df["Expense Amount"] / filtered_df["Unit Count"]
    value_column = "Expense Per Unit"
else:
    value_column = "Expense Amount"

# Box and Whisker Chart
st.subheader("Distribution of Selected Expenses Across Properties")
box_fig = px.box(
    filtered_df,
    x="Property Name",
    y=value_column,
    title=f"Box and Whisker Plot of {selected_category}",
    labels={value_column: "Expense"}
)
st.plotly_chart(box_fig, use_container_width=True)

# Weighted Average Calculation
st.subheader("Weighted Average Expense Per Unit")
if per_unit:
    weighted_avg = np.average(
        filtered_df["Expense Per Unit"],
        weights=filtered_df["Unit Count"]
    )
else:
    weighted_avg = np.average(
        filtered_df["Expense Amount"],
        weights=filtered_df["Unit Count"]
    )
st.metric(label="Weighted Average", value=f"${weighted_avg:,.2f}")

# Historical Weighted Average Graph
st.subheader("Historical Trends in Weighted Average Expenses Per Unit")
# Group by Date to calculate monthly weighted average
historical_df = filtered_df.copy()
historical_df["Month"] = historical_df["Date"].dt.to_period("M").dt.to_timestamp()
grouped = historical_df.groupby("Month").apply(
    lambda x: np.average(
        x["Expense Per Unit"] if per_unit else x["Expense Amount"],
        weights=x["Unit Count"]
    )
).reset_index(name="Weighted Average")

line_fig = px.line(
    grouped,
    x="Month",
    y="Weighted Average",
    title=f"Historical Weighted Average of {selected_category}",
    labels={"Weighted Average": "Expense", "Month": "Date"}
)
st.plotly_chart(line_fig, use_container_width=True)
