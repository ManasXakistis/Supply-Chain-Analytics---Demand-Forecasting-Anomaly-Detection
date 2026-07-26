# Supply Chain Analytics – Demand Forecasting & Anomaly Detection

## Project Overview

Supply chain efficiency plays a critical role in reducing operational costs and improving customer satisfaction. Incorrect demand estimation can result in excess inventory, increased storage costs, product spoilage, or stock shortages leading to lost sales.

This project builds an end-to-end analytics pipeline that cleans messy raw supply chain data, forecasts future demand, and detects unusual patterns in historical sales, inventory, and dispatch behavior — combining statistical analysis, machine learning, and (in Week 4) an interactive dashboard.

---

## Business Problem

Organizations need accurate demand forecasting to optimize inventory levels and procurement planning. At the same time, unexpected anomalies — sudden demand spikes, supplier delays, stockouts, or operational disruptions — should be identified early to minimize business impact.

This project provides:

- Demand forecasting for future inventory planning
- Automated anomaly detection across three complementary methods
- Time-series decomposition (trend / seasonality / residual)
- A foundation for an interactive business dashboard (Week 4)

---

## Key Performance Indicators (KPIs)

- Mean Absolute Percentage Error (MAPE)
- Root Mean Square Error (RMSE)
- Number of detected anomalies (per method and consensus)
- Forecast accuracy vs. baseline

---

## User Personas

### Supply Chain Manager
**Needs:** accurate procurement planning, future demand estimation
**Uses:** reviews forecasted demand, plans purchasing, optimizes warehouse capacity

### Operations Analyst
**Needs:** early anomaly detection, operational monitoring
**Uses:** investigates unusual inventory movements, flags stock shortages, detects unexpected sales spikes

---

## Pipeline & Findings

### Week 1 — Preprocessing (`notebooks/01_data_preprocessing.ipynb`)
The raw export (`data/raw/supply_chain_raw_data.csv`) is genuinely messy:
- Category names with mixed case, whitespace/tabs, underscores, and typos (`Furnture`, `Beuaty`, `Electronis`, `Appearl`, ...) → normalized to 11 canonical categories
- Three mixed date formats (`DD-MM-YYYY`, `MM-DD-YYYY`, `DD-Mon-YY`) → parsed into one datetime column
- `promotion_flag` in 8 different encodings (`0/1`, `TRUE/FALSE`, `Yes/No`, `Y/N`) → normalized to boolean
- **`999999` sentinel error codes and negative values** in every numeric column → treated as missing (this one matters: leaving them in makes any model fit on the data diverge wildly)
- ~1.5% exact duplicate rows → removed
- Per-category date gaps → reindexed to a full daily calendar and linearly interpolated (`Clothing` has the sparsest raw coverage, so treat its downstream results with extra caution)

Outputs: `data/processed/supply_chain_cleaned_data.csv` (clean but still irregular) and `data/processed/supply_chain_daily.csv` (gap-free daily series used by everything downstream).

### Week 2 — Anomaly Detection (`notebooks/02_anomaly_detection.ipynb`)
Three methods, run on the trend/seasonality-adjusted residual (or all four numeric features, for Isolation Forest):
- **Z-Score** (|z| > 3)
- **IQR** (Tukey fences, 1.5×IQR)
- **Isolation Forest** (multivariate, contamination = 2%)
- **Consensus flag**: at least 2 of 3 methods agree — 193 high-confidence anomaly-days across all categories

Output: `data/processed/anomalies.csv`.

### Week 3 — Forecasting (`notebooks/03`–`05`)
- **Baseline**: flat 7-day moving average, held out the last 30 days per category as the test window
- **ARIMA(1,1,1)**: fit per category with a moving-average fallback if a category fails to converge
- **Evaluation**: MAPE and RMSE, per category, baseline vs. ARIMA — ARIMA wins on MAPE in about half the categories (notably `Furniture`, `Sporting Goods`, `Clothing`), while the simple baseline holds its own on the calmer, low-variance categories (`Automotive Parts`, `Groceries`). See `data/processed/model_comparison.csv` for the full table.

### Week 4 — Interactive Dashboard (`app.py`)
A Streamlit app built on top of everything above — no recomputation happens in the app itself, it only reads `data/processed/`:
- Product category selector
- Historical demand chart with anomalies highlighted (choice of Z-Score / IQR / Isolation Forest / consensus)
- Forecast backtest chart (ARIMA vs. baseline vs. actual) with an adjustable confidence-interval band, sized from that model's own backtest error for the selected category
- KPI summary (avg. demand, avg. inventory, anomaly count, MAPE for both models)
- Full model-comparison table across all 11 categories

Run it with `streamlit run app.py` after the notebooks have been executed at least once. See `docs/Week4_Deployment_Guide.docx` for local setup and Streamlit Community Cloud deployment steps, and `docs/Project_Report.docx` for the full write-up.

---

## Project Structure

```
supply-chain-analytics/
├── README.md
├── requirements.txt
├── app.py                             # Week 4 Streamlit dashboard
├── data/
│   ├── raw/                          # original, uncleaned export
│   ├── processed/                    # cleaned + daily + model outputs
│   └── reference/                    # labeled demand data (ground-truth anomaly flags), for validation
├── notebooks/
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_anomaly_detection.ipynb
│   ├── 03_forecasting_baseline.ipynb
│   ├── 04_arima_forecast.ipynb
│   └── 05_model_evaluation.ipynb
├── src/
│   ├── data_loader.py                 # cached readers for data/processed/*.csv
│   └── metrics.py                     # MAPE / RMSE / confidence-band helpers
├── docs/
│   ├── week1_progress.md
│   ├── week2_summary.md
│   ├── week2_roadmap.md
│   ├── Project_Report.docx
│   └── Week4_Deployment_Guide.docx
└── assets/
```

---

## Technology Stack

Python · Pandas · NumPy · Matplotlib · Statsmodels · Scikit-learn · Streamlit (Week 4)

---

## Installation

```bash
git clone <this-repo>
cd supply-chain-analytics
pip install -r requirements.txt
jupyter notebook notebooks/01_data_preprocessing.ipynb
```

Run the notebooks in order (01 → 05); each one reads the previous step's output from `data/processed/`. Then launch the dashboard:

```bash
streamlit run app.py
```

Full deployment instructions (local + Streamlit Community Cloud): `docs/Week4_Deployment_Guide.docx`.

---

## Roadmap

| Week | Focus | Status |
|---|---|---|
| 1 | Preprocessing, decomposition | ✅ Complete |
| 2 | Anomaly detection (Z-score, IQR, Isolation Forest, consensus) | ✅ Complete |
| 3 | Baseline + ARIMA forecasting, evaluation | ✅ Complete |
| 4 | Streamlit dashboard, business interpretation, GitHub docs | ✅ Complete |

Future improvements: LSTM / XGBoost forecasting, multi-product joint models, real-time ingestion, automated alerts, cloud deployment.

---

## Author

Developed as part of a Data Analytics Internship Project focusing on Supply Chain Analytics, Demand Forecasting, and Statistical Anomaly Detection.

## License

This project is intended for educational and portfolio purposes.
