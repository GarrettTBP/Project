import streamlit as st
import pandas as pd
import io
from utils_api import get_properties, get_expenses, get_units, add_unit

CATEGORY_KEYS = [
    'payroll','marketing','admin','maintenance',
    'turnover','utilities','taxes','insurance','management_fees'
]

def app():
    st.header("Property List")

    # ── Load properties ───────────────────────────────────────────────────────
    props = pd.DataFrame(get_properties()).rename(columns={'name':'property_name'})
    if props.empty:
        st.info("No properties found. Add one first.")
        return

    # ── Property selector ────────────────────────────────────────────────────
    if 'selected_property' not in st.session_state:
        st.session_state.selected_property = None

    st.subheader("Select a property")
    cols = st.columns(3)
    for idx, name in enumerate(props['property_name']):
        if cols[idx % 3].button(name, key=f"prop_{idx}"):
            st.session_state.selected_property = name

    sel = st.session_state.selected_property
    if not sel:
        return

    p = props[props['property_name'] == sel].iloc[0]
    st.markdown(f"**{sel}** — Units: {p.units} — Type: {p.property_type} — Location: {p.location}")

    # ── Expense view options ──────────────────────────────────────────────────
    mode = st.radio("View Mode", ["T12", "T3", "Monthly"], horizontal=True)
    per_unit = st.checkbox("Show expenses per unit")

    exp = pd.DataFrame(get_expenses()).rename(columns={'property':'property_id'})
    exp['period'] = pd.to_datetime(dict(year=exp.year, month=exp.month, day=1))
    e = exp[exp['property_id'] == p['id']]

    if not e.empty:
        if mode in ("T12", "T3"):
            n = 12 if mode=="T12" else 3
            tail = e.sort_values('period').tail(n)
            sums = tail[CATEGORY_KEYS].sum()
            summary = {
                'property_name': sel,
                'units': p.units,
                'property_type': p.property_type,
                'location': p.location,
                **{k: sums[k] for k in CATEGORY_KEYS}
            }
            if per_unit:
                for k in CATEGORY_KEYS:
                    summary[k] = summary[k] / p.units
            df_sum = pd.DataFrame([summary])
            for k in CATEGORY_KEYS:
                df_sum[k] = df_sum[k].map(lambda x: f"${x:,.0f}")
            st.subheader(f"{mode} Summary{' per unit' if per_unit else ''}")
            st.dataframe(df_sum, use_container_width=True)
        else:
            dfm = e[['year','month'] + CATEGORY_KEYS].copy()
            dfm.insert(0, 'location', p.location)
            dfm.insert(0, 'property_type', p.property_type)
            dfm.insert(0, 'units', p.units)
            dfm.insert(0, 'property_name', sel)
            if per_unit:
                for k in CATEGORY_KEYS:
                    dfm[k] = dfm[k] / p.units
            for k in CATEGORY_KEYS:
                dfm[k] = dfm[k].map(lambda x: f"${x:,.0f}")
            st.subheader(f"Monthly Expenses{' per unit' if per_unit else ''}")
            st.dataframe(dfm, use_container_width=True)
    else:
        st.warning("No expenses for this property.")

    st.markdown("---")

    # ── Unit SqFt: download template, upload, view & save ────────────────────
    st.subheader("Unit Square Footage")

    # Template for download
    tmpl = pd.DataFrame({
        'property_name': [sel]*p.units,
        'unit_number': list(range(1, p.units+1)),
        'square_footage': ['']*p.units
    })
    buf = io.BytesIO()
    tmpl.to_excel(buf, index=False, sheet_name='Units')
    buf.seek(0)
    st.download_button(
        "Download Unit SqFt Template",
        data=buf,
        file_name=f"{sel}_unit_sqft_template.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # Upload filled template
    uploaded = st.file_uploader(
        "Upload filled Unit SqFt template",
        type=['xlsx','csv'],
        key='sqft_up'
    )
    if not uploaded:
        return

    try:
        if uploaded.name.lower().endswith('.csv'):
            df_units = pd.read_csv(uploaded)
        else:
            df_units = pd.read_excel(uploaded, sheet_name='Units')
    except Exception:
        st.error("Unable to read file. Please use the provided template.")
        return

    required = {'property_name','unit_number','square_footage'}
    if not required.issubset(df_units.columns):
        st.error("Template columns mismatch.")
        return

    df_units = df_units[df_units['property_name'] == sel].copy()
    df_units['square_footage'] = pd.to_numeric(df_units['square_footage'], errors='coerce')
    if df_units.empty:
        st.warning("No unit data for this property.")
        return

    # Display average SqFt
    avg_sqft = df_units['square_footage'].mean()
    st.metric("Average SqFt per Unit", f"{avg_sqft:,.2f}")

    # Expander for individual units
    with st.expander("Show all units"):
        st.dataframe(
            df_units[['unit_number','square_footage']].set_index('unit_number'),
            use_container_width=True
        )

    # Save to API
    if st.button("Save Unit Data"):
        failed = []
        existing = set()
        try:
            existing = {int(u['unit_number']) for u in get_units(property_id=int(p['id']))}
        except Exception:
            # if get_units fails, we'll just attempt all
            existing = set()

        for _, row in df_units.iterrows():
            unit_no = int(row['unit_number'])
            if unit_no in existing:
                st.info(f"Unit {unit_no} already exists; skipping.")
                continue

            try:
                payload = {
                    'property':       int(p['id']),
                    'unit_number':    unit_no,
                    'square_footage': float(row['square_footage'])
                }
                st.write(f"Sending payload for unit {unit_no}: {payload}")
                add_unit(payload)
                st.success(f"Unit {unit_no} saved.")
            except Exception as e:
                failed.append(unit_no)
                # try to extract DRF error text
                msg = e.response.text if hasattr(e, 'response') else str(e)
                st.error(f"Error saving unit {unit_no}: {msg}")

        if not failed:
            st.success("All units saved successfully.")
        else:
            st.error(f"Failed to save these units: {failed}")
