# Week 2 Roadmap — Anomaly Detection & Business Insights

## Objective

Identify unusual patterns and anomalies within the supply chain dataset by detecting irregularities in sales, inventory levels, and warehouse dispatch operations, using statistical and machine-learning techniques. These insights support demand forecasting, operational efficiency, and data-driven decisions.

## Step 1 — Data Loading and Preparation
- Load the cleaned supply chain dataset.
- Convert the date column to datetime for time-series analysis.
- Check for missing values and verify data types.

## Step 2 — Feature Selection
Key variables monitored for unusual behavior:
- Units Sold
- Inventory Level
- Warehouse Dispatch Rate

Each variable is analyzed individually before multivariate anomaly detection.

## Step 3 — Anomaly Detection
Three techniques are implemented and compared:

**1. Z-Score** — measures how far a point deviates from the mean in standard deviations. Good for identifying extreme values in roughly normal data; a simple statistical baseline.

**2. IQR (Interquartile Range)** — flags points outside the spread of the middle 50% of the data. Doesn't assume a normal distribution and is more robust to extreme values.

**3. Isolation Forest (recommended)** — an unsupervised ML method for multivariate anomaly detection.
- Handles large, skewed datasets efficiently
- Detects unusual *combinations* of features, not just single-variable extremes
- Catches subtle anomalies the statistical methods can miss

## Step 4 — Business Interpretation

Detecting an anomaly is only the first step — each one should be checked against business context:
- **Promotion campaigns** may explain a sudden sales spike rather than an operational issue.
- **Inventory shortages** may explain an unexpected sales decline (stockouts).
- **Warehouse dispatch delays** may signal transportation, congestion, or supplier issues.

## Step 5 — Dashboard Development (Streamlit)

An interactive dashboard to visualize anomaly results for business users, with:
- Product category selector
- Historical demand trend with anomalies highlighted
- Anomaly summary table with business interpretation
- Demand forecast section (next 90 days)

## Expected Deliverables
- Cleaned and preprocessed dataset
- Anomaly detection via Z-Score, IQR, and Isolation Forest
- Comparison of the three methods' results
- Time-series visualizations with anomalies highlighted
- Business interpretation linking anomalies to real-world events
- Initial Streamlit dashboard incorporating anomaly results

## Report Structure
1. **Objective** — detect abnormal patterns to improve monitoring, efficiency, and forecast accuracy
2. **Dataset used** — date, units sold, inventory level, warehouse dispatch rate, promotion flag
3. **Methods implemented** — Z-Score, IQR, Isolation Forest
4. **Results** — anomaly counts per method, comparative analysis, visualizations, strengths/limitations
5. **Business interpretation** — link anomalies to promotions, shortages, supplier delays, dispatch disruptions, and demand fluctuations; close with actionable recommendations for inventory management and forecasting.
