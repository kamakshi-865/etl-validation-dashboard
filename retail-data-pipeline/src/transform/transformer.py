"""Orchestrate cleaning and transformation of validated datasets."""

import pandas as pd

from src.transform.cleaners import (
    transform_customers,
    transform_orders,
    transform_products,
)
from src.utils.io import write_cleaned_outputs


def run_transformation(
    validated: dict[str, dict[str, pd.DataFrame]],
) -> dict[str, pd.DataFrame]:
    """
    Transform validated datasets: type casting, normalization, deduplication,
    and derived columns (e.g. total_order_value on orders).

    Args:
        validated: Output from run_validation(), keyed by entity with "valid"/"rejected".

    Returns:
        Dict of cleaned DataFrames keyed by entity name.
    """
    # TODO: wrap with logger once logging module is added
    customers = transform_customers(validated["customers"]["valid"])
    products = transform_products(validated["products"]["valid"])
    orders = transform_orders(validated["orders"]["valid"], products)

    cleaned = {
        "customers": customers,
        "products": products,
        "orders": orders,
    }

    write_cleaned_outputs(cleaned)
    return cleaned
