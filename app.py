# app.py
# Vantage: Financial Forecast Accuracy Suite - Streamlit Frontend

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ====================== PAGE CONFIG ======================
st.set_page_config(
    page_title="Vantage: Financial Forecast Accuracy Suite",
    page_icon="📈",
    layout="wide",
)

# Corporate theme
st.markdown(
    """
    <style>
        .stApp { background-color: #0a192f; color: #e0f2ff; }
        h1, h2, h3 { color: #1e88e5 !important; }
        .stMetric-label { color: #64b5f6; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 Vantage: Financial Forecast Accuracy Suite")
st.markdown("**Accurate Prophet-powered forecasting**")

tab1, tab2 = st.tabs(["🔮 Predictive Forecast", "📊 Executive Insights (Power BI)"])

# ====================== TAB 1: PREDICTIVE FORECAST ======================
with tab1:
    st.subheader("What-If Growth Scenario Analysis")

    @st.cache_data
    def load_forecast():
        return pd.read_csv("forecast_results.csv")

    forecast_df = load_forecast()
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    # Split historical vs future
    historical_df = forecast_df[forecast_df["y"].notna()].copy()
    future_df = forecast_df[forecast_df["ds"] > historical_df["ds"].max()].copy()

    # Growth slider
    growth_adjust = st.slider(
        "Growth Adjustment (%)",
        min_value=-50,
        max_value=50,
        value=0,
        step=1,
        help="Applies only to the future forecast",
    )
    factor = 1 + (growth_adjust / 100.0)

    # Apply adjustment
    future_df = future_df.copy()
    future_df["adjusted_yhat"] = future_df["yhat"] * factor
    future_df["adjusted_yhat_lower"] = future_df["yhat_lower"] * factor
    future_df["adjusted_yhat_upper"] = future_df["yhat_upper"] * factor

    # KPIs
    total_pred = future_df["adjusted_yhat"].sum()
    ci_range = future_df["adjusted_yhat_upper"].sum() - future_df["adjusted_yhat_lower"].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Predicted 12M Revenue", f"${total_pred:,.0f}", f"{growth_adjust:+.0f}% vs baseline")
    with col2:
        st.metric("Confidence Interval Range", f"${ci_range:,.0f}")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=historical_df["ds"], y=historical_df["y"],
                             mode="lines", name="Historical Sales",
                             line=dict(color="#1e88e5", width=4)))
    fig.add_trace(go.Scatter(x=future_df["ds"], y=future_df["adjusted_yhat"],
                             mode="lines", name=f"Adjusted Forecast ({growth_adjust:+.0f}%)",
                             line=dict(color="#ff9800", width=4, dash="dash")))
    fig.add_trace(go.Scatter(x=future_df["ds"], y=future_df["adjusted_yhat_upper"],
                             mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=future_df["ds"], y=future_df["adjusted_yhat_lower"],
                             mode="lines", fill="tonexty",
                             fillcolor="rgba(255, 152, 0, 0.25)",
                             name="95% Confidence Interval"))

    fig.update_layout(
        title="Monthly Sales – Historical vs. Adjusted 12-Month Forecast",
        xaxis_title="Date",
        yaxis_title="Revenue ($)",
        template="plotly_dark",
        height=550,
        legend=dict(orientation="h", y=1.02, x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

# ====================== TAB 2: POWER BI ======================
@st.cache_data
def load_exec_data():
    df = pd.read_csv("forecast_results.csv")
    df["ds"] = pd.to_datetime(df["ds"])
    df["YearMonth"] = df["ds"].dt.to_period("M").astype(str)
    return df

exec_df = load_exec_data()

# Create monthly aggregated dataset
monthly = exec_df.groupby("YearMonth").agg({
    "y": "sum",
    "yhat": "sum"
}).reset_index()

monthly.columns = ["YearMonth", "Sales", "Forecast"]

# Accuracy metrics
monthly["Error"] = monthly["Sales"] - monthly["Forecast"]
MAPE = (abs(monthly["Error"] / monthly["Sales"]).replace([np.inf, -np.inf], 0).fillna(0)).mean() * 100
accuracy = 100 - MAPE

# Dummy category data (since not in your dataset)
filtered_df = exec_df.copy()
filtered_df["Category"] = np.random.choice(["A", "B", "C"], len(filtered_df))
with tab2:

    st.subheader("📊 Financial Forecast Dashboard")

    # KPI Section
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Sales", f"{monthly['Sales'].sum():,.0f}")
    col2.metric("Forecast Sales", f"{monthly['Forecast'].sum():,.0f}")
    col3.metric("MAPE (%)", f"{MAPE:.2f}")
    col4.metric("Accuracy (%)", f"{accuracy:.2f}")

    # Line Chart
    st.subheader("📈 Actual vs Forecast")

    fig = px.line(monthly, x='YearMonth', y=['Sales', 'Forecast'], markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Error Chart
    st.subheader("📊 Error by Category")

    cat = filtered_df.groupby('Category').agg({
    'y': 'sum',
    'yhat': 'sum'
}).reset_index()

    cat.columns = ['Category', 'Sales', 'Forecast']
    cat['Error'] = cat['Sales'] - cat['Forecast']
    fig2 = px.bar(cat, x='Category', y='Error', color='Error')
    st.plotly_chart(fig2, use_container_width=True)

    # Scatter Plot
    st.subheader("🔍 Forecast vs Actual")

    fig3 = px.scatter(monthly, x='Forecast', y='Sales', size='Sales')
    st.plotly_chart(fig3, use_container_width=True)

    # Insights
    st.subheader("🧠 Insights")

    if accuracy > 90:
        st.success("Forecast is highly accurate.")
    elif accuracy > 75:
        st.warning("Forecast is moderately accurate.")
    else:
        st.error("Forecast accuracy is low.")

st.caption("Built as a two-file system • Run pipeline first → then this dashboard")
