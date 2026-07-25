"""Week 4 — Supply Chain Analytics Dashboard.

Run locally with:
    streamlit run app.py

Reads everything from data/processed/, which is produced by running
notebooks 01-05 in order. See docs/week4_deployment_guide.docx for setup
and deployment instructions.
"""
import plotly.graph_objects as go
import streamlit as st

from src.data_loader import (
    data_is_available,
    load_anomalies,
    load_arima_forecast,
    load_baseline_forecast,
    load_daily,
    load_model_comparison,
)
from src.metrics import confidence_band, mape, rmse

st.set_page_config(
    page_title="Supply Chain Analytics",
    page_icon="📦",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Guard: make sure the notebook pipeline has actually been run
# ---------------------------------------------------------------------------
if not data_is_available():
    st.error(
        "Processed data not found. Run notebooks `01_data_preprocessing.ipynb` "
        "through `05_model_evaluation.ipynb` (in order) before launching the "
        "dashboard — they generate everything under `data/processed/`."
    )
    st.stop()

daily = load_daily()
anomalies = load_anomalies()
baseline_fc = load_baseline_forecast()
arima_fc = load_arima_forecast()
comparison = load_model_comparison()

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
st.sidebar.title("📦 Controls")

categories = sorted(daily["product_category"].unique())
category = st.sidebar.selectbox("Product category", categories)

model_choice = st.sidebar.radio(
    "Forecast model", ["ARIMA", "Moving-average baseline", "Both"], index=0
)

confidence_level = st.sidebar.select_slider(
    "Confidence interval", options=[80, 85, 90, 95, 99], value=95,
    help="Width of the shaded band around the forecast, sized from that "
         "model's own backtest error for this category.",
)

show_anomalies = st.sidebar.checkbox("Highlight anomalies on history", value=True)
anomaly_method = st.sidebar.selectbox(
    "Anomaly method",
    ["Consensus (2 of 3 methods)", "Z-Score", "IQR", "Isolation Forest"],
    disabled=not show_anomalies,
)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Data source: `data/processed/` — regenerate by re-running notebooks "
    "01 → 05 after new data lands in `data/raw/`."
)

# ---------------------------------------------------------------------------
# Filter to the selected category
# ---------------------------------------------------------------------------
cat_daily = daily[daily["product_category"] == category].sort_values("date")
cat_anom = anomalies[anomalies["product_category"] == category]
cat_baseline = baseline_fc[baseline_fc["product_category"] == category].sort_values("date")
cat_arima = arima_fc[arima_fc["product_category"] == category].sort_values("date")
cat_compare = comparison[comparison["product_category"] == category]

method_col = {
    "Consensus (2 of 3 methods)": "anomaly_consensus",
    "Z-Score": "anomaly_z",
    "IQR": "anomaly_iqr",
    "Isolation Forest": "anomaly_if",
}[anomaly_method]
cat_anom_selected = cat_anom[cat_anom[method_col]]

# ---------------------------------------------------------------------------
# Header + KPI summary
# ---------------------------------------------------------------------------
st.title("Supply Chain Analytics Dashboard")
st.caption(f"Category: **{category}**  ·  {len(cat_daily)} days of history")

kpi_cols = st.columns(5)
kpi_cols[0].metric("Avg. daily demand", f"{cat_daily['units_sold'].mean():,.0f} units")
kpi_cols[1].metric("Avg. inventory level", f"{cat_daily['inventory_level'].mean():,.0f}")
kpi_cols[2].metric(
    "Consensus anomalies",
    int(cat_anom["anomaly_consensus"].sum()) if len(cat_anom) else 0,
    help="Days flagged by at least 2 of the 3 anomaly-detection methods.",
)
if not cat_compare.empty:
    row = cat_compare.iloc[0]
    kpi_cols[3].metric("ARIMA MAPE (backtest)", f"{row['MAPE_arima']:.1f}%")
    kpi_cols[4].metric(
        "Baseline MAPE (backtest)",
        f"{row['MAPE_baseline']:.1f}%",
        delta=f"{row['MAPE_baseline'] - row['MAPE_arima']:+.1f} pp vs ARIMA",
        delta_color="normal" if row["arima_wins_mape"] else "inverse",
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Historical demand chart with anomalies
# ---------------------------------------------------------------------------
st.subheader("Historical demand")

fig_hist = go.Figure()
fig_hist.add_trace(go.Scatter(
    x=cat_daily["date"], y=cat_daily["units_sold"],
    mode="lines", name="units sold", line=dict(color="#4C78A8", width=1.5),
))
if show_anomalies and len(cat_anom_selected):
    fig_hist.add_trace(go.Scatter(
        x=cat_anom_selected["date"], y=cat_anom_selected["units_sold"],
        mode="markers", name=f"{anomaly_method} anomaly",
        marker=dict(color="#E45756", size=9, symbol="circle-open", line=dict(width=2)),
    ))
fig_hist.update_layout(
    height=420, margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="date", yaxis_title="units sold",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig_hist, use_container_width=True)

if show_anomalies:
    with st.expander(f"Anomaly detail — {anomaly_method} ({len(cat_anom_selected)} days)"):
        st.dataframe(
            cat_anom_selected[["date", "units_sold", "residual", "anomaly_votes"]]
            .sort_values("date"),
            use_container_width=True, hide_index=True,
        )

st.markdown("---")

# ---------------------------------------------------------------------------
# Forecast backtest chart
# ---------------------------------------------------------------------------
st.subheader("Forecast backtest (held-out 30-day test window)")

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(
    x=cat_arima["date"], y=cat_arima["units_sold"],
    mode="lines+markers", name="actual", line=dict(color="black", width=2),
))

if model_choice in ("ARIMA", "Both") and len(cat_arima):
    lower, upper = confidence_band(cat_arima["forecast_arima"], cat_arima["units_sold"], confidence_level)
    fig_fc.add_trace(go.Scatter(
        x=list(cat_arima["date"]) + list(cat_arima["date"])[::-1],
        y=list(upper) + list(lower)[::-1],
        fill="toself", fillcolor="rgba(228,87,86,0.15)", line=dict(width=0),
        name=f"ARIMA {confidence_level}% CI", showlegend=True, hoverinfo="skip",
    ))
    fig_fc.add_trace(go.Scatter(
        x=cat_arima["date"], y=cat_arima["forecast_arima"],
        mode="lines", name="ARIMA forecast", line=dict(color="#E45756", width=2, dash="dash"),
    ))

if model_choice in ("Moving-average baseline", "Both") and len(cat_baseline):
    lower, upper = confidence_band(cat_baseline["forecast_ma"], cat_baseline["units_sold"], confidence_level)
    fig_fc.add_trace(go.Scatter(
        x=list(cat_baseline["date"]) + list(cat_baseline["date"])[::-1],
        y=list(upper) + list(lower)[::-1],
        fill="toself", fillcolor="rgba(76,120,168,0.15)", line=dict(width=0),
        name=f"Baseline {confidence_level}% CI", showlegend=True, hoverinfo="skip",
    ))
    fig_fc.add_trace(go.Scatter(
        x=cat_baseline["date"], y=cat_baseline["forecast_ma"],
        mode="lines", name="Baseline forecast", line=dict(color="#4C78A8", width=2, dash="dash"),
    ))

fig_fc.update_layout(
    height=420, margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="date", yaxis_title="units sold",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig_fc, use_container_width=True)

# ---------------------------------------------------------------------------
# Model comparison across all categories
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Model comparison — all categories")
st.dataframe(
    comparison.sort_values("MAPE_arima").style.format({
        "MAPE_baseline": "{:.2f}%", "MAPE_arima": "{:.2f}%",
        "RMSE_baseline": "{:.2f}", "RMSE_arima": "{:.2f}",
    }),
    use_container_width=True, hide_index=True,
)
st.caption(
    "MAPE / RMSE computed on each category's held-out 30-day test window "
    "(see `notebooks/05_model_evaluation.ipynb`)."
)
