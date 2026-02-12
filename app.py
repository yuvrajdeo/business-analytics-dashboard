import pandas as pd
import streamlit as st

from utils import standardize_columns, detect_dataset_type
from sales_module import render_sales_dashboard
from churn_module import render_churn_dashboard

st.set_page_config(page_title="Business Analytics Dashboard", layout="wide")

st.title("📊 Business Analytics Dashboard")
st.write("Upload a dataset (CSV). The app will auto-detect and show the right dashboard.")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a CSV file to continue.")
    st.stop()

df = pd.read_csv(uploaded_file)
df = standardize_columns(df)

st.subheader("Preview of Data (Standardized Columns)")
st.dataframe(df.head(10))

dataset_type = detect_dataset_type(df)

if dataset_type == "sales":
    render_sales_dashboard(df)
elif dataset_type == "churn":
    render_churn_dashboard(df)
else:
    st.error("Unknown dataset format.")
    st.write("Sales needs at least: **order_date, sales**")
    st.write("Churn needs at least: **churn**")
    st.write("Your columns are:")
    st.code(", ".join(df.columns))
