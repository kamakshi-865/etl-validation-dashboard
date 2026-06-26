"""Generate and persist business insight reports from the database."""

import pandas as pd

import src.config as config
from src.insights.queries import (
    fetch_customer_purchase_stats,
    fetch_revenue_trends,
    fetch_top_selling_products,
)
from src.load.database import get_engine
from src.utils.io import write_dataset


def _write_insights(reports: dict[str, pd.DataFrame]) -> None:
    config.INSIGHTS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, df in reports.items():
        write_dataset(df, config.INSIGHTS_DATA_DIR / f"{name}.csv")


def run_insights(database_url: str | None = None) -> dict[str, pd.DataFrame]:
    """
    Query the database and produce insight reports.

    Returns a dict of report DataFrames keyed by report name, and writes each
    report to data/insights/ as CSV.
    """
    # TODO: wrap with logger once logging module is added
    engine = get_engine(database_url)

    reports = {
        "top_selling_products": fetch_top_selling_products(engine),
        "revenue_trends": fetch_revenue_trends(engine),
        "customer_purchase_stats": fetch_customer_purchase_stats(engine),
    }

    _write_insights(reports)
    return reports
