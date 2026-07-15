# Week 1 Progress — Supply Chain Analytics

**Phase:** Time-Series Preprocessing & Decomposition · **Status:** Completed

- Set up Python 3.12 venv and pinned dependencies in `requirements.txt`.
- Finalized dataset: 11,000 records, 11 categories, 2020-01-01 → 2023-04-01.
- Cleaned data: resolved 629 duplicates, built a gap-free daily series (13,057 rows).
- Resampled demand to weekly and monthly frequencies.
- Ran additive seasonal decomposition (trend/seasonal/residual) with seasonal-strength scoring across all categories.

**Deliverables:** `requirements.txt`, `data/supply_chain_cleaned_data.csv`, `data/processed/supply_chain_daily.csv`, `notebooks/decomposition.ipynb`
