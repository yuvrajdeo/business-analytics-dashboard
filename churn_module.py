import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from utils import ensure_numeric

def render_churn_dashboard(df: pd.DataFrame) -> None:
    st.success("Detected: Customer Churn Dataset")

    df = df.copy()

    # Normalize churn values (Yes/No or 0/1)
    if df["churn"].dtype == "object":
        df["churn"] = (
            df["churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0})
        )

    df = ensure_numeric(df, "churn")
    df["churn"] = df["churn"].fillna(0).astype(int)

    # Optional numeric columns
    for col in ["monthlycharges", "totalcharges", "tenure", "monthly_charges", "total_charges"]:
        if col in df.columns:
            df = ensure_numeric(df, col)

    st.sidebar.header("Churn Filters")
    if "contract" in df.columns:
        contracts = sorted(df["contract"].dropna().unique())
        selected_contracts = st.sidebar.multiselect("Select Contract", contracts, default=contracts)
        df = df[df["contract"].isin(selected_contracts)]

    # KPIs
    total_customers = len(df)
    churned = int(df["churn"].sum())
    churn_rate = (churned / total_customers) * 100 if total_customers else 0

    st.subheader("✅ Key Metrics (Churn)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Customers", f"{total_customers}")
    c2.metric("Churned Customers", f"{churned}")
    c3.metric("Churn Rate", f"{churn_rate:.2f}%")

    st.subheader("📈 Charts (Churn)")

    churn_counts = df["churn"].value_counts().sort_index()
    churn_counts.index = ["Not Churned", "Churned"] if len(churn_counts.index) == 2 else churn_counts.index

    fig1 = plt.figure()
    churn_counts.plot(kind="bar")
    plt.xlabel("Customer Status")
    plt.ylabel("Count")
    plt.tight_layout()
    st.pyplot(fig1)

    if "contract" in df.columns:
        st.write("Churn Rate by Contract")
        churn_by_contract = df.groupby("contract")["churn"].mean().sort_values(ascending=False) * 100
        fig2 = plt.figure()
        churn_by_contract.plot(kind="bar")
        plt.xlabel("Contract")
        plt.ylabel("Churn Rate (%)")
        plt.tight_layout()
        st.pyplot(fig2)

    # Downloads
    st.subheader("⬇️ Download Reports (Churn)")
    churn_report = pd.DataFrame({
        "metric": ["total_customers", "churned_customers", "churn_rate_percent"],
        "value": [total_customers, churned, round(churn_rate, 2)]
    })

    st.download_button(
        "Download Churn KPI Report (CSV)",
        data=churn_report.to_csv(index=False).encode("utf-8"),
        file_name="churn_kpi_report.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download Cleaned Data (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="churn_cleaned.csv",
        mime="text/csv"
    )
