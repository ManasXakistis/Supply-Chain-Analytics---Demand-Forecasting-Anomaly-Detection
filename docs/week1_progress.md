# Week 1 Summary – Data Preprocessing & Time-Series Decomposition

## Objective

Establish a reliable foundation for the demand forecasting pipeline by cleaning and structuring the raw supply chain export into a gap-free daily time series, ready for anomaly detection and forecasting.

## Activities Completed

### 1. Dataset Assessment
- Loaded the raw export and profiled it for quality issues before touching anything.
- Found: inconsistent column naming, 106 distinct spellings/casings of 11 product categories, three mixed date formats, 8 different encodings of the promotion flag, `999999` sentinel error codes and negative values in every numeric column, and ~1.5% exact duplicate rows.

### 2. Cleaning
- Normalized category names (typos, whitespace, casing) down to 11 canonical categories.
- Parsed all three date formats into a single `datetime` column.
- Normalized the promotion flag to boolean.
- Nulled out sentinel (`999999`) and negative values in the numeric columns — left in, these silently break any model fit downstream.
- Removed exact duplicate rows.

### 3. Building a Continuous Daily Series
- Averaged away duplicate (category, date) rows.
- Reindexed each category onto a full daily calendar and linearly interpolated the remaining gaps. `Clothing` has the sparsest raw coverage of any category, so its interpolated share is the highest — its downstream anomaly and forecast results should be read with that in mind.

### 4. Decomposition
- Applied additive seasonal decomposition (weekly period) to sanity-check that trend, seasonality, and residual look reasonable before building on top of the data.

## Deliverables
- `data/processed/supply_chain_cleaned_data.csv` — clean, typed, deduplicated records
- `data/processed/supply_chain_daily.csv` — gap-free daily series per category
- Trend / seasonality / residual decomposition visualization

## Outcome

The dataset went from ~11,165 messy raw rows to a clean, continuous daily series across 11 product categories, ready for anomaly detection and forecasting in the following weeks.

**✅ Week 1 Completed**
