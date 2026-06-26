"""File I/O helpers for writing validated output datasets."""

from pathlib import Path

import pandas as pd

import src.config as config


def ensure_output_dirs() -> None:
    """Create data/valid/, data/rejected/, and data/cleaned/ if they do not exist."""
    config.VALID_DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.REJECTED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.CLEANED_DATA_DIR.mkdir(parents=True, exist_ok=True)


def write_dataset(df: pd.DataFrame, path: Path) -> None:
    """Write a DataFrame to CSV."""
    # TODO: wrap with logger once logging module is added
    df.to_csv(path, index=False)


def write_validation_outputs(
    valid: dict[str, pd.DataFrame],
    rejected: dict[str, pd.DataFrame],
) -> None:
    """Write all valid and rejected datasets to their respective folders."""
    ensure_output_dirs()
    for name, df in valid.items():
        write_dataset(df, config.VALID_DATA_DIR / f"{name}.csv")
    for name, df in rejected.items():
        write_dataset(df, config.REJECTED_DATA_DIR / f"{name}.csv")


def write_cleaned_outputs(cleaned: dict[str, pd.DataFrame]) -> None:
    """Write all cleaned datasets to data/cleaned/."""
    ensure_output_dirs()
    for name, df in cleaned.items():
        write_dataset(df, config.CLEANED_DATA_DIR / f"{name}.csv")
