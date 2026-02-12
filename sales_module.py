import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils import ensure_datetime, ensure_numeric

def render_sales_dashboard(df: pd.DataFrame) -> None:
    st.success("✅ Detected: Sales Dataset")

    # --- Cleaning ---
    df = df.copy()
    df = ensure_datetime(df, "order_date", dayfirst=True)
    df = ensure_datetime(df, "ship_date", dayfirst=True)

    # Sales must be numeric (fixes your 'str / int' error)
    df = ensure_numeric(df, "sales")

    # Optional cleanups
    if "postal_code" in df.columns:
        df["postal_code"] = df["postal_code"].fillna(0)

    if "row_id" in df.columns:
        df = df.drop(columns=["row_id"])

    df = df.drop_duplicates()
    df = df.dropna(subset=["order_date", "sales"])  # must have date + sales

    # --- Sidebar Filters ---
    st.sidebar.header("Sales Filters")

    selected_regions = None
    if "region" in df.columns:
        regions = sorted(df["region"].dropna().unique())
        selected_regions = st.sidebar.multiselect("Select Region", regions, default=regions)

    selected_categories = None
    if "category" in df.columns:
        categories = sorted(df["category"].dropna().unique())
        selected_categories = st.sidebar.multiselect("Select Category", categories, default=categories)

    min_date = df["order_date"].min().date()
    max_date = df["order_date"].max().date()

    date_range = st.sidebar.date_input("Select Date Range", value=(min_date, max_date))
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # --- Apply Filters ---
    df_filtered = df.copy()

    if selected_regions is not None:
        df_filtered = df_filtered[df_filtered["region"].isin(selected_regions)]

    if selected_categories is not None:
        df_filtered = df_filtered[df_filtered["category"].isin(selected_categories)]

    df_filtered = df_filtered[
        (df_filtered["order_date"] >= pd.to_datetime(start_date)) &
        (df_filtered["order_date"] <= pd.to_datetime(end_date))
    ]

    # --- KPIs ---
    total_revenue = float(df_filtered["sales"].sum())  # ensure it's numeric
    if "order_id" in df_filtered.columns:
        total_orders = int(df_filtered["order_id"].nunique())
    else:
        total_orders = int(len(df_filtered))

    avg_order_value = (total_revenue / total_orders) if total_orders > 0 else 0

    st.subheader("✅ Key Metrics (Sales)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Revenue", f"{total_revenue:,.2f}")
    c2.metric("Total Orders", f"{total_orders}")
    c3.metric("Avg Order Value", f"{avg_order_value:,.2f}")

    # --- Monthly Revenue + Best Month Insight ---
    df_filtered = df_filtered.copy()
    df_filtered["month"] = df_filtered["order_date"].dt.to_period("M").astype(str)
    monthly_revenue = df_filtered.groupby("month")["sales"].sum()

    if not monthly_revenue.empty:
        best_month = monthly_revenue.idxmax()
        best_month_value = monthly_revenue.max()
        st.info(f"🏆 Best Month: {best_month} | Sales: {best_month_value:,.2f}")

    # --- Charts ---
    st.subheader("📈 Charts (Sales)")
    colA, colB = st.columns(2)

    with colA:
        st.write("Monthly Revenue Trend")
        fig1 = plt.figure()
        monthly_revenue.plot()
        plt.xticks(rotation=45)
        plt.xlabel("Month")
        plt.ylabel("Sales")
        plt.tight_layout()
        st.pyplot(fig1)

    with colB:
        if "category" in df_filtered.columns:
            st.write("Sales by Category")
            category_sales = df_filtered.groupby("category")["sales"].sum().sort_values(ascending=False)
            fig2 = plt.figure()
            category_sales.plot(kind="bar")
            plt.xlabel("Category")
            plt.ylabel("Sales")
            plt.tight_layout()
            st.pyplot(fig2)

    if "region" in df_filtered.columns:
        st.write("Revenue by Region")
        region_sales = df_filtered.groupby("region")["sales"].sum().sort_values(ascending=False)
        fig3 = plt.figure()
        region_sales.plot(kind="bar")
        plt.xlabel("Region")
        plt.ylabel("Sales")
        plt.tight_layout()
        st.pyplot(fig3)

    # --- Top Products ---
    product_col = "product_name" if "product_name" in df_filtered.columns else None
    if product_col:
        st.subheader("🏷️ Top 10 Products")
        top_products = df_filtered.groupby(product_col)["sales"].sum().sort_values(ascending=False).head(10)
        st.dataframe(top_products.reset_index().rename(columns={"sales": "product_sales"}))

    # --- Downloads ---
    st.subheader("⬇️ Download Reports (Sales)")
    kpi_report = pd.DataFrame({
        "metric": ["total_revenue", "total_orders", "average_order_value"],
        "value": [total_revenue, total_orders, avg_order_value]
    })

    st.download_button(
        "Download KPI Report (CSV)",
        data=kpi_report.to_csv(index=False).encode("utf-8"),
        file_name="sales_kpi_report.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download Cleaned & Filtered Data (CSV)",
        data=df_filtered.to_csv(index=False).encode("utf-8"),
        file_name="sales_cleaned_filtered.csv",
        mime="text/csv"
    )
