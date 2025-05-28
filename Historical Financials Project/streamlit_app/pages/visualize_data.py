import streamlit as st
import pandas as pd
import altair as alt

from utils_api import get_properties, get_expenses

CATEGORY_KEYS = [
    'payroll','marketing','admin','maintenance',
    'turnover','utilities','taxes','insurance','management_fees'
]

def app():
    st.header("Visualize Expenses")
    props=get_properties()
    exps=get_expenses()
    if not props or not exps:
        st.info('Not enough data.')
        return
    dfp=pd.DataFrame(props)
    dfe=pd.DataFrame(exps)
    merged=dfe.merge(dfp,left_on='property',right_on='id')
    merged['period']=pd.to_datetime(dict(year=merged.year,month=merged.month,day=1))
    st.sidebar.subheader('Unit Info (CSV)')
    uf=st.sidebar.file_uploader("Upload CSV with 'property_name','average_sqft'",type=['csv'])
    if uf:
        ui=pd.read_csv(uf)
        merged=merged.merge(ui,on='property_name',how='left')
        for k in CATEGORY_KEYS: merged[f"{k}_per_sqft"]=merged[k]/merged['average_sqft']
    st.subheader('Box-and-Whiskers Plot')
    cat=st.selectbox('Expense Category',CATEGORY_KEYS)
    per_sqft=uf and st.checkbox('Plot per sqft')
    field=f"{cat}_per_sqft" if per_sqft else cat
    ylabel=f"{cat.replace('_',' ').title()}{' per sqft' if per_sqft else ''}"
    chart=alt.Chart(merged).mark_boxplot(extent=1.5).encode(
        x=alt.X('property_name:N',title='Property'),
        y=alt.Y(f'{field}:Q',title=ylabel)
    ).properties(width=600,height=400)
    st.altair_chart(chart,use_container_width=True)
