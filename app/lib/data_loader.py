"""Cached data-loading helpers for the Streamlit dashboard.

Everything here reads the already-processed CSVs produced by the notebooks in
``notebooks/`` (written to ``data/processed/``). The dashboard never recomputes
cleaning, forecasting, or anomaly detection itself — it just displays exactly
what the notebooks generated, which keeps it fast and reproducible.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

# app/lib/data_loader.py -> app/lib -> app -> project root
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "processed"

DAILY_FILE = "supply_chain_daily.csv"
ANOMALIES_FILE = "anomalies.csv"
FORECASTS_FILE = "forecasts.csv"
SCORES_FILE = "model_scores.csv"

REQUIRED_FILES = [DAILY_FILE, ANOMALIES_FILE, FORECASTS_FILE, SCORES_FILE]


@st.cache_data
def load_daily() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / DAILY_FILE, parse_dates=["date"])
    return df.sort_values(["product_category", "date"]).reset_index(drop=True)


@st.cache_data
def load_anomalies() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / ANOMALIES_FILE, parse_dates=["date"])
    return df.sort_values(["product_category", "date"]).reset_index(drop=True)


@st.cache_data
def load_forecasts() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / FORECASTS_FILE, parse_dates=["date"])
    return df.sort_values(["product_category", "date"]).reset_index(drop=True)


@st.cache_data
def load_scores() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / SCORES_FILE)


def missing_files(names) -> list:
    """Return the subset of ``names`` that don't exist in ``data/processed/``."""
    return [name for name in names if not (DATA_DIR / name).exists()]


def data_is_available() -> bool:
    """Return True if the full processed dataset required by the app exists."""
    return all((DATA_DIR / name).exists() for name in REQUIRED_FILES)
