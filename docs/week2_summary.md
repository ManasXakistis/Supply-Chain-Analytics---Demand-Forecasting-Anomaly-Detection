# Week 2 Summary — Anomaly Detection

## Objective

Identify unusual patterns in sales, inventory, and warehouse dispatch behavior using three complementary statistical and machine-learning techniques, and combine them into a single high-confidence consensus flag.

## Activities Completed

### 1. Data Loading
- Loaded the gap-free daily series produced in Week 1 (`data/processed/supply_chain_daily.csv`).
- Verified data types and category coverage before modeling.

### 2. Deseasonalizing
- Decomposed each category's `units_sold` (additive, weekly period) and kept the **residual** — demand with trend and weekly seasonality removed — so normal seasonal peaks aren't mistaken for anomalies.

### 3. Feature Selection
Selected the key variables for anomaly detection:
- Units Sold
- Inventory Level
- Unit Price
- Warehouse Dispatch Rate

### 4. Anomaly Detection — Three Methods
- **Z-Score**: flags residual days beyond 3 standard deviations. Simple statistical baseline.
- **IQR (Tukey fences)**: flags values outside 1.5×IQR of the residual. More robust to extreme values, doesn't assume normality.
- **Isolation Forest**: multivariate, looks at all four numeric features together (contamination = 2%), so it catches unusual *combinations* of values that the univariate methods miss.
- **Consensus**: a day is flagged with high confidence when at least 2 of the 3 methods agree — 193 consensus anomaly-days across all 11 categories.

### 5. Visualization & Review
- Plotted each method's flags against the raw demand series per category to sanity-check the results visually before exporting.

## Outcome

By the end of Week 2, every category had anomaly flags from three independent methods plus a consensus flag, exported to `data/processed/anomalies.csv`. This gives Operations Analysts a ranked, cross-validated list of days worth investigating, and sets up Week 3's forecasting work on the same cleaned daily series.
