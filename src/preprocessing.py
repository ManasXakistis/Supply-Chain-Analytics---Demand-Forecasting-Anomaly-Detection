"""
Week 1 - Day 2: Supply chain demand data cleaning pipeline.

Reads the messy raw file, cleans it, and writes an analysis-ready continuous
daily time series to data/processed/supply_chain_daily_clean.csv.

Run from the project root:  python src/preprocessing.py
"""

import numpy as np
import pandas as pd
from pathlib import Path

# Resolve paths relative to the project root (parent of this src/ folder).
ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / 'data' / 'raw' / 'supply_chain_raw.csv'
OUT_PATH = ROOT / 'data' / 'processed' / 'supply_chain_daily_clean.csv'

CANONICAL = ['Electronics', 'Furniture', 'Clothing', 'Groceries', 'Toys']
NUM_COLS = ['units_sold', 'inventory_on_hand', 'unit_price']
MISSING_TOKENS = {'', ' ', 'n/a', 'na', 'null', '?'}
TYPO_MAP = {
    'electroncs': 'Electronics',
    'furnitature': 'Furniture',
    'cloting': 'Clothing',
    'grocery': 'Groceries',
    'toyz': 'Toys',
}
_CATEGORY_LOOKUP = {c.lower(): c for c in CANONICAL}


def to_nan(series):
    # Convert disguised missing tokens (N/A, null, ?, blanks) to real NaN.
    stripped = series.str.strip()
    mask = stripped.str.lower().isin(MISSING_TOKENS)
    return stripped.mask(mask, np.nan)


def clean_category(value):
    # Standardize a category label to one of the 5 canonical values (or NaN).
    if pd.isna(value):
        return np.nan
    key = str(value).strip().lower()
    if key in TYPO_MAP:
        return TYPO_MAP[key]
    return _CATEGORY_LOOKUP.get(key, np.nan)


def parse_dates(s):
    # Route each date format to the correct parser (US slash vs European dash).
    out = pd.Series(pd.NaT, index=s.index, dtype='datetime64[ns]')
    dash = s.str.match(r'^\d{2}-\d{2}-\d{4}$', na=False)    # DD-MM-YYYY (European)
    slash = s.str.match(r'^\d{2}/\d{2}/\d{4}$', na=False)   # MM/DD/YYYY (US)
    rest = s.notna() & ~(dash | slash)                      # named-month / ISO etc.
    out[dash] = pd.to_datetime(s[dash], format='%d-%m-%Y', errors='coerce')
    out[slash] = pd.to_datetime(s[slash], format='%m/%d/%Y', errors='coerce')
    out[rest] = pd.to_datetime(s[rest], format='mixed', errors='coerce')
    return out


def clean_count(value):
    # Parse an integer-like count that may use ',' as a thousands separator.
    if pd.isna(value):
        return np.nan
    s = str(value).strip().replace(',', '')
    return pd.to_numeric(s, errors='coerce')


def clean_price(value):
    # Parse a price string with $, thousands ',' and/or European decimal ','.
    if pd.isna(value):
        return np.nan
    s = str(value).strip().replace('$', '').replace(' ', '')
    if ',' in s and '.' in s:
        s = s.replace(',', '')                     # comma = thousands separator
    elif ',' in s:
        parts = s.split(',')
        if len(parts) == 2 and len(parts[1]) == 2:
            s = parts[0] + '.' + parts[1]          # comma = decimal (e.g. 249,77)
        else:
            s = s.replace(',', '')                 # comma = thousands
    return pd.to_numeric(s, errors='coerce')


def clean(raw):
    """Run the full cleaning pipeline on the raw dataframe and return the daily series."""
    df = raw.copy()

    # 1. Remove exact duplicate rows.
    df = df.drop_duplicates().copy()

    # 2. Convert disguised missing tokens to real NaN across all columns.
    for col in ['order_date', 'category', 'units_sold', 'inventory_on_hand', 'unit_price']:
        df[col] = to_nan(df[col])

    # 3. Standardize category labels (20+ variants -> 5 canonical) and drop unmapped.
    df['category'] = df['category'].map(clean_category)
    df = df.dropna(subset=['category'])

    # 4. Parse mixed date formats into datetimes and drop anything unparseable.
    df['order_date'] = parse_dates(df['order_date'])
    df = df.dropna(subset=['order_date'])

    # 5. Clean numeric columns (strip $, thousands ',', European decimal ',').
    df['units_sold'] = df['units_sold'].map(clean_count)
    df['inventory_on_hand'] = df['inventory_on_hand'].map(clean_count)
    df['unit_price'] = df['unit_price'].map(clean_price)

    # 6. Treat impossible negative counts as missing so they get interpolated.
    for col in ['units_sold', 'inventory_on_hand']:
        df.loc[df[col] < 0, col] = np.nan

    # 7. Collapse to one row per (date, category); carry the hidden anomaly label.
    df['order_date'] = df['order_date'].dt.normalize()
    agg = (df.groupby(['order_date', 'category'], as_index=False)
             .agg(units_sold=('units_sold', 'mean'),
                  inventory_on_hand=('inventory_on_hand', 'mean'),
                  unit_price=('unit_price', 'mean'),
                  injected_anomaly=('_injected_anomaly', 'max')))

    # 8a. Trim to the reliably-covered window (7-day rolling coverage >= 70% of median).
    raw_range = pd.date_range(agg['order_date'].min(), agg['order_date'].max(), freq='D')
    daily_obs = agg.groupby('order_date').size().reindex(raw_range, fill_value=0)
    rolling_cov = daily_obs.rolling(7, center=True, min_periods=1).sum()
    keep = rolling_cov[rolling_cov >= 0.70 * rolling_cov.median()].index
    start, end = keep.min(), keep.max()
    agg = agg[agg['order_date'].between(start, end)].copy()

    # 8b. Reindex every category onto the full daily calendar and interpolate gaps.
    full_range = pd.date_range(start, end, freq='D')
    frames = []
    for cat in CANONICAL:
        sub = (agg[agg['category'] == cat]
               .set_index('order_date')
               .sort_index()
               .reindex(full_range))
        sub.index.name = 'order_date'
        sub['category'] = cat
        sub[NUM_COLS] = sub[NUM_COLS].interpolate(method='linear', limit_direction='both')
        sub['injected_anomaly'] = sub['injected_anomaly'].fillna('')  # reindexed rows are not anomalies
        frames.append(sub.reset_index())
    clean_daily = pd.concat(frames, ignore_index=True)

    # 9. Round to sensible types and order the columns.
    clean_daily['units_sold'] = clean_daily['units_sold'].round().astype('int64')
    clean_daily['inventory_on_hand'] = clean_daily['inventory_on_hand'].round().astype('int64')
    clean_daily['unit_price'] = clean_daily['unit_price'].round(2)
    clean_daily = clean_daily[['order_date', 'category', 'units_sold',
                               'inventory_on_hand', 'unit_price', 'injected_anomaly']]
    clean_daily = clean_daily.sort_values(['category', 'order_date']).reset_index(drop=True)

    # 10. Validate the result before trusting it downstream.
    expected_rows = len(full_range) * len(CANONICAL)
    assert clean_daily[NUM_COLS].isna().sum().sum() == 0, 'Missing values remain!'
    assert clean_daily.duplicated(['order_date', 'category']).sum() == 0, 'Duplicate keys!'
    assert set(clean_daily['category'].unique()) == set(CANONICAL), 'Unexpected categories!'
    assert len(clean_daily) == expected_rows, 'Series is not fully continuous!'
    assert (clean_daily['units_sold'] >= 0).all(), 'Negative units remain!'

    return clean_daily


def main():
    # Load everything as text so pandas does not silently coerce the messy values.
    raw = pd.read_csv(RAW_PATH, dtype=str, keep_default_na=False)
    clean_daily = clean(raw)

    # Save the cleaned continuous daily series.
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_daily.to_csv(OUT_PATH, index=False)
    print(f'Saved {len(clean_daily)} rows -> {OUT_PATH}')
    print(f"Date range: {clean_daily['order_date'].min()} -> {clean_daily['order_date'].max()}")


if __name__ == '__main__':
    main()
