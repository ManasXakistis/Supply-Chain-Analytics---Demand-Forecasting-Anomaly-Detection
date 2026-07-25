# Week 3 Progress — Supply Chain Analytics

**Phase:** Demand Forecasting · **Status:** Completed

- Split each category's demand into a training period and a held-out 30-day test window (per category).
- Built a moving-average baseline (mean of the last 7 training days, held flat) as the benchmark to beat.
- Evaluated the baseline with reusable `mape()` and `rmse()` functions, overall and per category.
- Fitted an ARIMA(1,1,1) model per category with a moving-average fallback for any category that fails to converge.
- Compared baseline vs ARIMA on identical test windows, picked a winner per category and overall by RMSE.
- Exported the merged forecasts to `data/processed/forecasts.csv` and the scoreboard to `data/processed/model_scores.csv`.

**Deliverables:** `notebooks/forecasting.ipynb`, `notebooks/forecast_evaluation.ipynb`, `notebooks/arima_forecast.ipynb`, `notebooks/model_comparison.ipynb`, `data/processed/forecasts.csv`, `data/processed/model_scores.csv`
