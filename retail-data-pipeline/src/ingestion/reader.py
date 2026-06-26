"""Read raw CSV files into DataFrames."""

from pathlib import Path

import pandas as pd

import src.config as config


def read_csv(path: Path) -> pd.DataFrame:
    """Load a single CSV file. All values are read as strings to preserve raw input."""
    # TODO: wrap with logger once logging module is added
    if not path.exists():
        raise FileNotFoundError(f"Raw data file not found: {path}")
    return pd.read_csv(path, dtype=str, keep_default_na=False)


def load_customers() -> pd.DataFrame:
    return read_csv(config.RAW_FILES["customers"])


def load_products() -> pd.DataFrame:
    return read_csv(config.RAW_FILES["products"])


def load_orders() -> pd.DataFrame:
    return read_csv(config.RAW_FILES["orders"])


def load_all_raw() -> dict[str, pd.DataFrame]:
    """Load all three raw datasets. Keys: customers, products, orders."""
    return {
        "customers": load_customers(),
        "products": load_products(),
        "orders": load_orders(),
    }
