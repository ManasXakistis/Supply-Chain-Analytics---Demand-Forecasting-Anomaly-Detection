"""
Supply Chain Data Cleaning Script
----------------------------------
Cleans supply_chain_raw_data.csv, fixing:
  - inconsistent/ambiguous date formats
  - messy product_category text (case, whitespace, typos, plurals)
  - non-boolean promotion_flag values
  - currency-prefixed / placeholder unit_price values
  - '-' / 'NA' placeholders in numeric columns
  - impossible negative values in units_sold / inventory_level
  - sentinel/outlier values in warehouse_dispatch_rate
  - duplicate rows and a stray empty column
Outputs a cleaned CSV plus a short console report.
"""

import re
import numpy as np
import pandas as pd

INPUT_PATH = "/mnt/user-data/uploads/supply_chain_raw_data.csv"
OUTPUT_PATH = "/mnt/user-data/outputs/supply_chain_cleaned_data.csv"

# --------------------------------------------------------------------------
# 1. LOAD
# --------------------------------------------------------------------------
df = pd.read_csv(INPUT_PATH)
raw_rows = len(df)

# Drop fully-empty stray column(s), e.g. 'Unnamed: 7'
df = df.loc[:, ~df.columns.str.contains(r"^Unnamed")]

# --------------------------------------------------------------------------
# 2. DATE COLUMN — handles 3 mixed formats: 'DD-Mon-YY', 'DD-MM-YYYY', 'MM-DD-YYYY'
# --------------------------------------------------------------------------
def parse_date(value):
    if pd.isna(value):
        return pd.NaT
    value = str(value).strip()

    # Format: 20-Sep-22
    try:
        return pd.to_datetime(value, format="%d-%b-%y")
    except ValueError:
        pass

    parts = value.split("-")
    if len(parts) == 3 and all(p.isdigit() for p in parts):
        a, b, year = parts
        a, b = int(a), int(b)
        # Disambiguate day/month: whichever number > 12 must be the day
        if a > 12 and b <= 12:
            day, month = a, b
        elif b > 12 and a <= 12:
            month, day = a, b
        else:
            # Ambiguous (both <=12): default to day-first convention
            day, month = a, b
        try:
            return pd.Timestamp(year=int(year), month=month, day=day)
        except ValueError:
            return pd.NaT
    return pd.NaT


df["date"] = df["date"].apply(parse_date)

# --------------------------------------------------------------------------
# 3. PRODUCT CATEGORY — normalize case/whitespace/typos into a canonical set
# --------------------------------------------------------------------------
CATEGORY_MAP = {
    "apparel": "Apparel", "appearl": "Apparel",
    "auto parts": "Automotive Parts", "automotive parts": "Automotive Parts",
    "automotive-parts": "Automotive Parts", "automotiveparts": "Automotive Parts",
    "beauty": "Beauty", "beuaty": "Beauty",
    "clothing": "Clothing",
    "electronics": "Electronics", "electronic": "Electronics", "electronis": "Electronics",
    "furniture": "Furniture", "furnture": "Furniture",
    "groceries": "Groceries", "grocery": "Groceries", "grocerys": "Groceries",
    "office supplies": "Office Supplies", "officesupplies": "Office Supplies",
    "pet supplies": "Pet Supplies", "petsupplies": "Pet Supplies",
    "sporting goods": "Sporting Goods", "sport goods": "Sporting Goods",
    "sporting_goods": "Sporting Goods",
    "toys": "Toys", "toy": "Toys",
}


def clean_category(value):
    if pd.isna(value):
        return np.nan
    v = str(value).strip().lower()
    v = v.replace("\t", " ")
    v = re.sub(r"[-_]", " ", v)          # unify separators
    v = re.sub(r"\s+", " ", v).strip()   # collapse whitespace
    return CATEGORY_MAP.get(v, v.title())  # fall back to Title Case if unseen


df["product_category"] = df["product_category"].apply(clean_category)

# --------------------------------------------------------------------------
# 4. PROMOTION FLAG — normalize to real booleans
# --------------------------------------------------------------------------
BOOL_MAP = {
    "0": False, "false": False, "no": False, "n": False,
    "1": True, "true": True, "yes": True, "y": True,
}
df["promotion_flag"] = (
    df["promotion_flag"].astype(str).str.strip().str.lower().map(BOOL_MAP)
)

# --------------------------------------------------------------------------
# 5. NUMERIC COLUMNS — strip currency symbols / placeholders, coerce to float
# --------------------------------------------------------------------------
PLACEHOLDER_TOKENS = {"-", "missing", "na", "n/a", "?", ""}


def to_numeric(value):
    if pd.isna(value):
        return np.nan
    v = str(value).strip()
    if v.lower() in PLACEHOLDER_TOKENS:
        return np.nan
    v = re.sub(r"[^\d.\-]", "", v)   # drop currency symbols like $, Rs.
    try:
        return float(v)
    except ValueError:
        return np.nan


for col in ["units_sold", "inventory_level", "unit_price", "warehouse_dispatch_rate"]:
    df[col] = df[col].apply(to_numeric)

# units_sold / inventory_level cannot legitimately be negative -> sign error, take magnitude
df["units_sold"] = df["units_sold"].abs()
df["inventory_level"] = df["inventory_level"].abs()

# warehouse_dispatch_rate: 999999 is a sentinel error code -> treat as missing
df.loc[df["warehouse_dispatch_rate"] >= 999999, "warehouse_dispatch_rate"] = np.nan

# --------------------------------------------------------------------------
# 6. OUTLIER CAPPING (IQR method) for remaining continuous numeric columns
# --------------------------------------------------------------------------
def cap_outliers_iqr(series, k=1.5):
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    return series.clip(lower=lower, upper=upper)


for col in ["units_sold", "inventory_level", "unit_price", "warehouse_dispatch_rate"]:
    df[col] = cap_outliers_iqr(df[col])

# --------------------------------------------------------------------------
# 7. IMPUTE remaining missing numeric values with the per-category median
# --------------------------------------------------------------------------
for col in ["units_sold", "inventory_level", "unit_price", "warehouse_dispatch_rate"]:
    df[col] = df.groupby("product_category")[col].transform(
        lambda s: s.fillna(s.median())
    )
    df[col] = df[col].fillna(df[col].median())  # catch-all safety net
    df[col] = df[col].round(2)

# --------------------------------------------------------------------------
# 8. DROP rows with an unparseable date (essential key) & duplicates
# --------------------------------------------------------------------------
df = df.dropna(subset=["date"])
before_dedup = len(df)
df = df.drop_duplicates()

df = df.sort_values("date").reset_index(drop=True)

# --------------------------------------------------------------------------
# 9. SAVE + REPORT
# --------------------------------------------------------------------------
df.to_csv(OUTPUT_PATH, index=False)

print("=" * 60)
print("CLEANING REPORT")
print("=" * 60)
print(f"Raw rows read           : {raw_rows}")
print(f"Rows after date fix     : {before_dedup}  (dropped {before_dedup - raw_rows if before_dedup>raw_rows else raw_rows - before_dedup} unparseable dates)")
print(f"Duplicate rows removed  : {before_dedup - len(df)}")
print(f"Final row count         : {len(df)}")
print(f"Final column count      : {df.shape[1]}")
print(f"Distinct categories now : {df['product_category'].nunique()} -> {sorted(df['product_category'].unique())}")
print(f"Remaining NaNs per col  :\n{df.isna().sum()}")
print(f"\nCleaned file saved to: {OUTPUT_PATH}")
