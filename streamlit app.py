# app.py
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import date

engine = create_engine('sqlite:///healthcare.db')

st.title("Healthcare Capstone Dashboard")

# Filters
with engine.connect() as conn:
    depts = [r[0] for r in conn.execute("SELECT DISTINCT dept FROM visits").fetchall()]

dept_choice = st.sidebar.multiselect("Department", options=depts, default=depts)
date_range = st.sidebar.date_input("Date range", [date(2023,1,1), date(2025,8,31)])

start = date_range[0].isoformat()
end = date_range[1].isoformat()

query = f"""
SELECT strftime('%Y-%m', visit_date) AS month, COUNT(*) AS visits
FROM visits
WHERE dept IN ({','.join(['?']*len(dept_choice))})
  AND visit_date BETWEEN ? AND ?
GROUP BY month
ORDER BY month
"""
params = dept_choice + [start, end]
df_month = pd.read_sql_query(query, engine, params=params)

fig = px.line(df_month, x='month', y='visits', title='Monthly Visits')
st.plotly_chart(fig, use_container_width=True)

# show top diagnoses table
diagnosis_q = f"""
SELECT diag_desc, COUNT(*) AS cnt
FROM visits
WHERE dept IN ({','.join(['?']*len(dept_choice))})
  AND visit_date BETWEEN ? AND ?
GROUP BY diag_desc
ORDER BY cnt DESC
LIMIT 10
"""
df_diag = pd.read_sql_query(diagnosis_q, engine, params=params)
st.table(df_diag)