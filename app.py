"""Supply Chain Analytics — Streamlit dashboard (home page).

Run from the project root with:
    streamlit run app/app.py
"""
import plotly.graph_objects as go
import streamlit as st

from lib.data_loader import (
    ANOMALIES_FILE,
    DAILY_FILE,
    FORECASTS_FILE,
    SCORES_FILE,
    load_anomalies,
    load_daily,
    load_scores,
    missing_files,
)

st.set_page_config(page_title="Supply Chain Analytics", page_icon="📦", layout="wide")
st.sidebar.info(
    "Use the sidebar to open the Forecasting and Anomaly Detection pages for deeper analysis."
)

st.title("Supply Chain Analytics — Demand Forecasting & Anomaly Detection")
st.markdown(
    """
    An end-to-end analytics pipeline that **forecasts product demand** and
    **flags unusual patterns** in historical supply chain data.

    Use the pages in the sidebar or the quick navigation links to explore:
    - **Forecasting** — compare the moving-average baseline against ARIMA,
      with confidence-interval bands.
    - **Anomaly Detection** — review demand spikes and dips flagged by Z-Score,
      IQR, Isolation Forest, or their consensus.
    """
)

missing = missing_files([DAILY_FILE, ANOMALIES_FILE, FORECASTS_FILE, SCORES_FILE])
if missing:
    st.warning(
        "Missing processed data: " + ", ".join(f"`{name}`" for name in missing)
        + ". Run the notebooks in `notebooks/` first to generate them."
    )
    st.stop()

daily = load_daily()
anomalies = load_anomalies()
scores = load_scores()

arima_wins = int((scores["winner"] == "ARIMA").sum())
mean_mape_baseline = scores["MAPE_baseline"].mean()
mean_mape_arima = scores["MAPE_arima"].mean()
avg_daily_demand = daily["units_sold"].mean()
avg_inventory = daily["inventory_level"].mean()
consensus_flags = len(anomalies[anomalies["anomaly_consensus"]])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Product categories", daily["product_category"].nunique())
c2.metric("Avg. daily demand", f"{avg_daily_demand:,.1f} units")
c3.metric("Avg. inventory level", f"{avg_inventory:,.0f}")
c4.metric("ARIMA wins", f"{arima_wins}/{len(scores)}")

st.markdown("---")

st.subheader("Demand & forecasting overview")
sub1, sub2 = st.columns(2)

fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=daily.groupby("date")["units_sold"].sum().reset_index()["date"],
    y=daily.groupby("date")["units_sold"].sum().reset_index()["units_sold"],
    mode="lines", name="Total units sold", line=dict(color="#4C78A8", width=1.5),
))
fig_ts.update_layout(
    height=360, margin=dict(l=10, r=10, t=30, b=30),
    xaxis_title="date", yaxis_title="units sold",
)
sub1.plotly_chart(fig_ts, use_container_width=True)

score_chart = go.Figure()
score_chart.add_trace(go.Bar(
    x=scores.sort_values("MAPE_arima")["product_category"],
    y=scores.sort_values("MAPE_arima")["MAPE_baseline"],
    name="Baseline",
    marker_color="#4C78A8",
))
score_chart.add_trace(go.Bar(
    x=scores.sort_values("MAPE_arima")["product_category"],
    y=scores.sort_values("MAPE_arima")["MAPE_arima"],
    name="ARIMA",
    marker_color="#E45756",
))
score_chart.update_layout(
    height=360,
    margin=dict(l=10, r=10, t=30, b=120),
    xaxis_title="product category",
    yaxis_title="MAPE (%)",
    barmode="group",
)
sub2.plotly_chart(score_chart, use_container_width=True)

st.markdown("---")

st.subheader("Category-level demand and anomaly rate")

by_cat = (
    daily.groupby("product_category")["units_sold"].sum().sort_values(ascending=False)
    .reset_index()
)
fig_cat = go.Figure(go.Bar(
    x=by_cat["product_category"], y=by_cat["units_sold"], marker_color="#4C78A8",
))
fig_cat.update_layout(
    height=360, margin=dict(l=10, r=10, t=30, b=120),
    xaxis_title="product category", yaxis_title="total units sold",
)

anomaly_rate = (
    anomalies[anomalies["anomaly_consensus"]]
    .groupby("product_category")["anomaly_consensus"].count()
    .rename("count")
    .reset_index()
)
category_days = daily.groupby("product_category")["date"].count().rename("days").reset_index()
anomaly_rate = anomaly_rate.merge(category_days, on="product_category", how="left")
anomaly_rate["rate"] = anomaly_rate["count"] / anomaly_rate["days"] * 100
fig_anom_rate = go.Figure(go.Bar(
    x=anomaly_rate.sort_values("rate", ascending=False)["product_category"],
    y=anomaly_rate.sort_values("rate", ascending=False)["rate"],
    marker_color="#E45756",
))
fig_anom_rate.update_layout(
    height=360, margin=dict(l=10, r=10, t=30, b=120),
    xaxis_title="product category", yaxis_title="consensus anomaly rate (%)",
)

st.plotly_chart(fig_cat, use_container_width=True)
st.plotly_chart(fig_anom_rate, use_container_width=True)

st.markdown("---")

st.subheader("Top category insights")
top_improvement = (
    scores.assign(improvement=scores["MAPE_baseline"] - scores["MAPE_arima"])
    .sort_values("improvement", ascending=False)
    .head(5)
    [["product_category", "MAPE_baseline", "MAPE_arima", "improvement"]]
)
top_anomaly_rate = anomaly_rate.sort_values("rate", ascending=False).head(5)

col5, col6 = st.columns(2)
col5.dataframe(
    top_improvement.style.format({
        "MAPE_baseline": "{:.2f}%",
        "MAPE_arima": "{:.2f}%",
        "improvement": "{:.2f} pp",
    }),
    use_container_width=True,
)
col5.caption("Top 5 categories where ARIMA improves most over the baseline.")
col6.dataframe(
    top_anomaly_rate.style.format({"rate": "{:.2f}%"}),
    use_container_width=True,
)
col6.caption("Top 5 categories by consensus anomaly rate.")
st.markdown("---")

st.subheader("Dashboard summary")
summary_cols = st.columns(3)
summary_cols[0].metric("Consensus anomaly flags", f"{consensus_flags:,}")
summary_cols[1].metric("Average ARIMA MAPE", f"{mean_mape_arima:.1f}%")
summary_cols[2].metric("Average baseline MAPE", f"{mean_mape_baseline:.1f}%")

st.markdown(
    """
    The sidebar contains the detailed per-category Forecasting and Anomaly
    Detection pages. Use those pages for deeper analysis of model performance
    and flagged demand anomalies.
    """
)
