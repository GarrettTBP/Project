import streamlit as st
import pandas as pd
import io
import datetime
from utils_api import add_property, add_expense


CATEGORY_KEYS = [
    'payroll','marketing','admin','maintenance',
    'turnover','utilities','taxes','insurance','management_fees'
]
MONTHS = [
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
]

def app():
    st.header("Add Property & Expenses")
    st.markdown("---")

    # --- Excel template for 12 months ---
    template_df = pd.DataFrame([
        {**{'property_name':'','units':'','property_type':'','location':''},
         **{k:'' for k in CATEGORY_KEYS},
         'month': m, 'year': datetime.datetime.now().year}
        for m in range(1, 13)
    ])
    towrite = io.BytesIO()
    template_df.to_excel(towrite, index=False, sheet_name='Expenses')
    towrite.seek(0)
    st.download_button(
        "Download Excel Template",
        data=towrite,
        file_name='property_expenses_template.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    st.markdown("---")

    # --- Upload filled template ---
    uploaded = st.file_uploader("Upload filled Excel template", type=['xlsx'])
    if uploaded:
        try:
            df = pd.read_excel(uploaded, sheet_name='Expenses')
        except Exception:
            st.error("Unable to read 'Expenses' sheet. Please use the provided template.")
            return
        expected = ['property_name','units','property_type','location','month','year'] + CATEGORY_KEYS
        if not all(c in df.columns for c in expected):
            st.error("Template columns mismatch. Do not rename headers.")
            return

        # Handle multiple distinct properties
        props = df[['property_name','units','property_type','location']].drop_duplicates()
        for _, p in props.iterrows():
            # Create the property
            prop_data = {
                'name': p['property_name'],
                'units': int(p['units']),
                'property_type': p['property_type'],
                'location': p['location']
            }
            prop = add_property(prop_data)
            if not prop:
                st.error(f"Failed to create property {p['property_name']}")
                continue

            # Filter expenses for this property
            mask = (
                (df.property_name == p['property_name']) &
                (df.units == p['units']) &
                (df.property_type == p['property_type']) &
                (df.location == p['location'])
            )
            this_rows = df[mask]

            # Add expense entries
            count = 0
            for _, row in this_rows.iterrows():
                exp_payload = {
                    'property': prop['id'],
                    'month': int(row['month']),
                    'year': int(row['year']),
                    **{k: float(row[k]) for k in CATEGORY_KEYS}
                }
                res = add_expense(exp_payload)
                if res:
                    count += 1

            st.success(
                f"Added property '{prop['name']}' with {count} expense entries."
            )
        return

    # --- Manual entry form ---
    st.info("Or fill manually below:")
    with st.form('manual_form', clear_on_submit=True):
        name = st.text_input('Property Name')
        units = st.number_input('Units', min_value=1, step=1)
        ptype = st.selectbox('Property Type', ['Garden','High Rise','Mid Rise','Townhouse','Other'])
        location = st.text_input('Location')

        entries = []
        year_now = datetime.datetime.now().year
        for i in range(1, 13):
            st.markdown(f"**Entry {i}**")
            mon = st.selectbox(f"Month (Entry {i})", MONTHS, key=f"month_{i}")
            month = MONTHS.index(mon) + 1
            year = st.number_input(
                f"Year (Entry {i})", 2000, 2100, year_now, key=f"year_{i}"
            )
            vals = {
                k: st.number_input(
                    k.replace('_',' ').title(), min_value=0.0, format='%.2f',
                    key=f"{k}_{i}"
                ) for k in CATEGORY_KEYS
            }
            entries.append({'month': month, 'year': year, **vals})

        if st.form_submit_button('Add Property & Expenses'):
            prop = add_property({
                'name': name,
                'units': units,
                'property_type': ptype,
                'location': location
            })
            if prop:
                for e in entries:
                    add_expense({ 'property': prop['id'], **e })
                st.success(f"Property '{name}' and manual entries added.")

