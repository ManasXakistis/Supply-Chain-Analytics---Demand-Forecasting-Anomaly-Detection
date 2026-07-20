# Week 2 Progress — Supply Chain Analytics

**Phase:** Statistical Anomaly Detection · **Status:** Completed

- Detected anomalies on the deseasonalized residual (demand minus trend and weekly seasonality) per category.
- Z-Score method (|z| > 3): 275 anomalies.
- IQR method (Tukey 1.5× fences): 1,183 anomalies.
- Isolation Forest (multivariate, contamination 2%): 264 anomalies.
- Combined the three methods with a consensus vote (≥2 of 3 agree): 302 high-confidence anomalies.
- Exported all flagged days with per-method flags and consensus to `data/processed/anomalies.csv` (1,352 rows).

**Deliverables:** `notebooks/anomaly_detection.ipynb`, `data/processed/anomalies.csv`
