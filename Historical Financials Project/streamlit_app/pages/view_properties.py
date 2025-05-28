import streamlit as st
import pandas as pd
from utils_api import get_properties, get_expenses, get_units

CATEGORY_KEYS = [
    'payroll','marketing','admin','maintenance',
    'turnover','utilities','taxes','insurance','management_fees'
]

def app():
    st.header("View & Filter Properties and Expenses")

    # ── Fetch data ────────────────────────────────────────────────────────────
    props = pd.DataFrame(get_properties()).rename(columns={'name':'property_name'})
    exp   = pd.DataFrame(get_expenses()).rename(columns={'property':'property_id'})
    if props.empty:
        st.info("No properties found. Add one on the Add Property page.")
        return
    if exp.empty:
        st.info("No expenses found. Add some properties with expenses first.")
        return

    # ── Compute average sqft per property ────────────────────────────────────
    units = pd.DataFrame(get_units()).rename(columns={'property':'property_id'})
    if not units.empty:
        avg_sqft = units.groupby('property_id')['square_footage'].mean().rename('avg_sqft')
        props = props.merge(avg_sqft, left_on='id', right_index=True, how='left')
    else:
        props['avg_sqft'] = None

    # ── Sidebar filters ───────────────────────────────────────────────────────
    st.sidebar.subheader("Property Filters")
    types = st.sidebar.multiselect(
        "Property Type",
        options=props['property_type'].unique(),
        default=props['property_type'].unique()
    )
    locs = st.sidebar.multiselect(
        "Location",
        options=props['location'].unique(),
        default=props['location'].unique()
    )
    min_u, max_u = int(props['units'].min()), int(props['units'].max())
    if min_u == max_u:
        st.sidebar.write(f"Units: {min_u}")
        units_range = (min_u, max_u)
    else:
        units_range = st.sidebar.slider("Units range", min_u, max_u, (min_u, max_u))
    per_unit = st.sidebar.checkbox("Show expenses per unit")

    # ── Filter properties ────────────────────────────────────────────────────
    filtered = props[
        props['property_type'].isin(types) &
        props['location'].isin(locs) &
        props['units'].between(*units_range)
    ]
    if filtered.empty:
        st.warning("No properties match filters.")
        return

    # ── Prepare expenses ───────────────────────────────────────────────────────
    exp['period'] = pd.to_datetime(dict(year=exp['year'], month=exp['month'], day=1))
    merged = exp.merge(filtered, left_on='property_id', right_on='id', how='inner')

    # ── View mode ─────────────────────────────────────────────────────────────
    mode = st.sidebar.radio("View Mode", ["T12", "T3", "Monthly"])

    if mode in ("T12", "T3"):
        n = 12 if mode=="T12" else 3
        summaries = []
        for _, p in filtered.iterrows():
            pe = (merged[merged['property_id']==p['id']]
                  .sort_values('period')
                  .tail(n))
            sums = pe[CATEGORY_KEYS].sum()
            row = {
                'property_name': p['property_name'],
                'units':         p['units'],
                'property_type': p['property_type'],
                'location':      p['location'],
                'avg_sqft':      p.get('avg_sqft', None),
                **sums.to_dict()
            }
            if per_unit:
                for k in CATEGORY_KEYS:
                    row[k] = row[k] / p['units']
            summaries.append(row)

        df_summary = pd.DataFrame(summaries)
        # Format currency & avg_sqft
        df_summary['avg_sqft'] = df_summary['avg_sqft'].map(lambda x: f"{x:,.1f}" if pd.notna(x) else "N/A")
        for k in CATEGORY_KEYS:
            df_summary[k] = df_summary[k].map(lambda x: f"${x:,.0f}")

        st.subheader(f"{mode} Expenses Summary (Last {n} Months){' per unit' if per_unit else ''}")
        st.dataframe(df_summary, use_container_width=True)

    else:
        dfm = merged[['property_name','units','property_type','location','year','month'] + CATEGORY_KEYS].copy()
        dfm = dfm.merge(filtered[['id','avg_sqft']], left_on='property_id', right_on='id', how='left')
        dfm.drop(columns=['id_y'], inplace=True)
        dfm.rename(columns={'id_x':'id'}, inplace=True)

        if per_unit:
            for k in CATEGORY_KEYS:
                dfm[k] = dfm[k] / dfm['units']
        dfm['avg_sqft'] = dfm['avg_sqft'].map(lambda x: f"{x:,.1f}" if pd.notna(x) else "N/A")
        for k in CATEGORY_KEYS:
            dfm[k] = dfm[k].map(lambda x: f"${x:,.0f}")

        st.subheader(f"Monthly Expenses{' per unit' if per_unit else ''}")
        st.dataframe(dfm, use_container_width=True)
