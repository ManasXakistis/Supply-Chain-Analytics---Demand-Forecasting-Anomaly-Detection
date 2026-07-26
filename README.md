# Supply Chain Analytics – Demand Forecasting & Anomaly Detection

## Project Overview

Supply chain efficiency plays a critical role in reducing operational costs and improving customer satisfaction. Incorrect demand estimation can result in excess inventory, increased storage costs, product spoilage, or stock shortages leading to lost sales.

This project focuses on building an end-to-end analytics pipeline that forecasts future product demand while detecting unusual patterns in historical supply chain data. The solution combines statistical analysis, machine learning, and interactive visualization to help businesses make informed inventory decisions.

---

## Business Problem

Organizations require accurate demand forecasting to optimize inventory levels and improve procurement planning. At the same time, unexpected anomalies such as sudden demand spikes, supplier delays, stockouts, or operational disruptions should be identified early to minimize business impact.

This project provides:

- Demand Forecasting for future inventory planning
- Automated Anomaly Detection
- Time Series Analysis
- Interactive dashboard for business users

---

## Business Objectives

- Improve inventory planning
- Reduce overstock and stockout situations
- Forecast demand for the next 90 days
- Automatically identify abnormal sales or inventory behavior
- Support data-driven procurement decisions

---

## Key Performance Indicators (KPIs)

- Mean Absolute Percentage Error (MAPE)
- Root Mean Square Error (RMSE)
- Forecast Accuracy
- Number of Detected Anomalies
- Precision of Anomaly Detection

---

## User Personas

### Supply Chain Manager

**Needs**

- Accurate procurement planning
- Future demand estimation

**Uses**

- Reviews forecasted demand
- Plans inventory purchasing
- Optimizes warehouse capacity

---

### Operations Analyst

**Needs**

- Early anomaly detection
- Operational monitoring

**Uses**

- Investigates unusual inventory movements
- Identifies stock shortages
- Detects unexpected sales spikes

---

# Features

## Time Series Preprocessing

- Date parsing
- Datetime indexing
- Missing value handling
- Weekly and monthly aggregation
- Interpolation
- Time series decomposition
  - Trend
  - Seasonality
  - Residual

---

## Anomaly Detection

Implemented techniques include:

- Z-Score Analysis
- Interquartile Range (IQR)
- Isolation Forest (optional)

The system highlights abnormal inventory or sales behavior for further investigation.

---

## Demand Forecasting

Forecasting models include:

- Moving Average (Baseline)
- ARIMA
- Prophet (Optional)

The application predicts demand for the next 90 days.

---

## Interactive Dashboard

Built using **Streamlit**

Features include:

- Product selection dropdown
- Historical demand visualization
- Forecast chart
- Anomaly visualization
- Confidence interval adjustment
- KPI summary

---

# Technology Stack

- Python
- Pandas
- NumPy
- Matplotlib
- Plotly
- Statsmodels
- Scikit-learn
- Prophet (Optional)
- Streamlit

---

# Project Structure

```
Supply-Chain-Analytics/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│
├── src/
│   ├── preprocessing.py
│   ├── anomaly_detection.py
│   ├── forecasting.py
│   ├── visualization.py
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
└── assets/
```

---

# Engineering Roadmap

## Week 1

### Time Series Preprocessing

- Load dataset
- Datetime conversion
- Handle missing dates
- Resampling
- Time series decomposition

---

## Week 2

### Statistical Anomaly Detection

- Z-Score
- IQR
- Isolation Forest
- Visualize anomalies
- Analyze anomaly causes

---

## Week 3

### Demand Forecasting

- Train/Test split
- Moving Average
- ARIMA
- Prophet
- Model evaluation
- Forecast next 90 days

---

## Week 4

### Streamlit Deployment

- Interactive dashboard
- Product filtering
- Confidence interval slider
- Forecast visualization
- GitHub documentation

---

# Installation

Clone the repository:

```bash
git clone https://github.com/ManasXakistis/Supply-Chain-Analytics---Demand-Forecasting-Anomaly-Detection.git
```

Navigate into the project:

```bash
cd "c:\Users\hemangi\Desktop\Supply Chain Analytics - Demand Forecasting"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the notebook pipeline to generate processed data:

```bash
# Run these in order from the project root
jupyter notebook notebooks/01_data_preprocessing.ipynb
jupyter notebook notebooks/02_anomaly_detection.ipynb
jupyter notebook notebooks/03_forecasting_baseline.ipynb
jupyter notebook notebooks/04_arima_forecast.ipynb
jupyter notebook notebooks/05_model_evaluation.ipynb
```

Launch the multi-page Streamlit dashboard:

```bash
streamlit run app/app.py
```
> The app uses Streamlit's multipage feature: the root page is `app/app.py` and the detailed pages are located in `app/pages/`.> If Streamlit prompts for an onboarding email on first run, press `Enter` to skip.

---

# Future Improvements

- LSTM Forecasting
- XGBoost Forecasting
- Multi-product forecasting
- Real-time data ingestion
- Power BI integration
- Automated email alerts
- Cloud deployment

---

# Author

Developed as part of a Data Analytics Internship Project focusing on Supply Chain Analytics, Demand Forecasting, and Statistical Anomaly Detection.

---

# License

This project is intended for educational and portfolio purposes.
