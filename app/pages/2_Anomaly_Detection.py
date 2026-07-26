"""Anomaly Detection page — demand anomalies per category, by method."""
import plotly.graph_objects as go
import streamlit as st

from lib.data_loader import ANOMALIES_FILE, DAILY_FILE, load_anomalies, load_daily, missing_files

st.set_page_config(page_title="Anomaly Detection", page_icon="🚨", layout="wide")
st.sidebar.info("Select a product category and anomaly method to inspect historical demand flags.")

st.title("Anomaly Detection")
st.caption("Demand anomalies flagged by Z-Score, IQR, Isolation Forest, or their consensus.")

missing = missing_files([DAILY_FILE, ANOMALIES_FILE])
if missing:
    st.warning(
        "Data files not found: "
        + ", ".join(f"`{m}`" for m in missing)
        + ". Run `notebooks/anomaly_detection.ipynb` first to generate them."
    )
    st.stop()

daily = load_daily()
anomalies = load_anomalies()

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
categories = sorted(daily["product_category"].unique())
category = st.sidebar.selectbox("Product category", categories)
anomaly_method = st.sidebar.selectbox(
    "Anomaly method",
    ["Consensus (2 of 3 methods)", "Z-Score", "IQR", "Isolation Forest"],
)
method_col = {
    "Consensus (2 of 3 methods)": "anomaly_consensus",
    "Z-Score": "anomaly_z",
    "IQR": "anomaly_iqr",
    "Isolation Forest": "anomaly_if",
}[anomaly_method]

flagged = anomalies[anomalies[method_col]]
cat_flags = flagged[flagged["product_category"] == category].sort_values("date")
category_days = int((daily["product_category"] == category).sum())
category_flag_rate = 100 * len(cat_flags) / max(category_days, 1)

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
c1.metric(f"{anomaly_method} — all categories", f"{len(flagged):,}")
c2.metric("In this category", int(len(cat_flags)))
c3.metric("Category flag rate", f"{category_flag_rate:.1f}%")

st.markdown("---")

# ---------------------------------------------------------------------------
# Demand chart with anomalies
# ---------------------------------------------------------------------------
series = daily[daily["product_category"] == category].sort_values("date")

st.subheader(f"{category}: demand with {anomaly_method} anomalies")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=series["date"], y=series["units_sold"],
    mode="lines", name="units sold", line=dict(color="#4C78A8", width=1.5),
))
if len(cat_flags):
    fig.add_trace(go.Scatter(
        x=cat_flags["date"], y=cat_flags["units_sold"],
        mode="markers", name="anomaly",
        marker=dict(color="#E45756", size=9, symbol="circle-open", line=dict(width=2)),
    ))
fig.update_layout(
    height=440, margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="date", yaxis_title="units sold",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Flagged rows
# ---------------------------------------------------------------------------
st.subheader(f"Flagged rows for {category}")
show_cols = [
    c for c in ["date", "units_sold", "residual", "z", "anomaly_votes", "promotion_flag"]
    if c in cat_flags.columns
]
st.dataframe(cat_flags[show_cols].reset_index(drop=True), use_container_width=True, hide_index=True)
