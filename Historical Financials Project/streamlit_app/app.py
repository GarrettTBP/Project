import streamlit as st
from pages import add_property, view_properties, visualize_data, property_list

st.set_page_config(page_title="Historical Financials", layout="wide")
st.title("Historical Financials (API)")

page = st.sidebar.radio("Go to", [
    "Add Property",
    "View Properties",
    "Visualize Data",
    "Property List"
])

if page == "Add Property":
    add_property.app()
elif page == "View Properties":
    view_properties.app()
elif page == "Visualize Data":
    visualize_data.app()
else:  # Property List
    property_list.app()
