"""Demand Forecasting page — baseline vs ARIMA on the held-out test window."""
import plotly.graph_objects as go
import streamlit as st

from lib.data_loader import FORECASTS_FILE, SCORES_FILE, load_forecasts, load_scores, missing_files
from lib.metrics import confidence_band

st.set_page_config(page_title="Demand Forecasting", page_icon="📈", layout="wide")

st.title("Demand Forecasting")
st.caption("Moving-average baseline vs ARIMA on the last 30 held-out days per category.")

missing = missing_files([FORECASTS_FILE, SCORES_FILE])
if missing:
    st.warning(
        "Forecast files not found: "
        + ", ".join(f"`{m}`" for m in missing)
        + ". Run `notebooks/model_comparison.ipynb` first to generate them."
    )
    st.stop()

forecasts = load_forecasts()
scores = load_scores()

# ---------------------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------------------
categories = sorted(forecasts["product_category"].unique())
category = st.sidebar.selectbox("Product category", categories)
model_choice = st.sidebar.radio(
    "Forecast model", ["Both", "ARIMA", "Moving-average baseline"], index=0
)
confidence_level = st.sidebar.select_slider(
    "Confidence interval", options=[80, 85, 90, 95, 99], value=95,
    help="Width of the shaded band around each forecast, sized from that "
         "model's own backtest error for this category.",
)

one = forecasts[forecasts["product_category"] == category].sort_values("date")

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
row = scores[scores["product_category"] == category]
if not row.empty:
    row = row.iloc[0]
    c1, c2, c3 = st.columns(3)
    c1.metric("Baseline RMSE", f"{row['RMSE_baseline']:.2f}")
    c2.metric(
        "ARIMA RMSE", f"{row['RMSE_arima']:.2f}",
        delta=f"{row['RMSE_baseline'] - row['RMSE_arima']:+.2f} vs baseline",
        delta_color="normal",
    )
    c3.metric("Winner", str(row["winner"]))

st.markdown("---")

# ---------------------------------------------------------------------------
# Forecast chart with confidence bands
# ---------------------------------------------------------------------------
st.subheader(f"{category}: actual vs forecasts (held-out 30-day window)")

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=one["date"], y=one["units_sold"],
    mode="lines+markers", name="actual", line=dict(color="black", width=2),
))

if model_choice in ("ARIMA", "Both"):
    lower, upper = confidence_band(one["forecast_arima"], one["units_sold"], confidence_level)
    fig.add_trace(go.Scatter(
        x=list(one["date"]) + list(one["date"])[::-1],
        y=list(upper) + list(lower)[::-1],
        fill="toself", fillcolor="rgba(228,87,86,0.15)", line=dict(width=0),
        name=f"ARIMA {confidence_level}% CI", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=one["date"], y=one["forecast_arima"],
        mode="lines", name="ARIMA forecast", line=dict(color="#E45756", width=2, dash="dash"),
    ))

if model_choice in ("Moving-average baseline", "Both"):
    lower, upper = confidence_band(one["forecast_ma"], one["units_sold"], confidence_level)
    fig.add_trace(go.Scatter(
        x=list(one["date"]) + list(one["date"])[::-1],
        y=list(upper) + list(lower)[::-1],
        fill="toself", fillcolor="rgba(76,120,168,0.15)", line=dict(width=0),
        name=f"Baseline {confidence_level}% CI", hoverinfo="skip",
    ))
    fig.add_trace(go.Scatter(
        x=one["date"], y=one["forecast_ma"],
        mode="lines", name="Baseline forecast", line=dict(color="#4C78A8", width=2, dash="dash"),
    ))

fig.update_layout(
    height=440, margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title="date", yaxis_title="units sold",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------------------------
# Scoreboard
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Model scoreboard (all categories)")
st.dataframe(
    scores.sort_values("RMSE_arima").style.format({
        "MAPE_baseline": "{:.2f}%", "MAPE_arima": "{:.2f}%",
        "RMSE_baseline": "{:.2f}", "RMSE_arima": "{:.2f}",
    }),
    use_container_width=True, hide_index=True,
)
st.caption(
    "MAPE / RMSE computed on each category's held-out 30-day test window "
    "(see `notebooks/model_comparison.ipynb`)."
)
