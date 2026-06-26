"""Orchestrate validation across customers, products, and orders."""

import pandas as pd

from src.config import (
    CUSTOMER_ID_COLUMN,
    CUSTOMER_REQUIRED,
    ORDER_ID_COLUMN,
    ORDER_REQUIRED,
    PRODUCT_ID_COLUMN,
    PRODUCT_REQUIRED,
    REJECTION_REASON_COLUMN,
)
from src.ingestion.reader import load_all_raw
from src.utils.io import write_validation_outputs
from src.validation.checks import (
    check_date_format,
    check_duplicate_ids,
    check_email_format,
    check_foreign_key,
    check_integer_column,
    check_missing_values,
    check_positive_float_column,
    check_positive_integer_column,
    combine_reasons,
    split_by_reasons,
)


def _valid_id_set(df: pd.DataFrame, id_column: str) -> set[str]:
    if df.empty or id_column not in df.columns:
        return set()
    return {str(value).strip() for value in df[id_column]}


def validate_customers(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    reasons = combine_reasons(
        check_missing_values(df, CUSTOMER_REQUIRED),
        check_duplicate_ids(df, CUSTOMER_ID_COLUMN),
        check_integer_column(df, CUSTOMER_ID_COLUMN),
        check_email_format(df),
    )
    return split_by_reasons(df, reasons, REJECTION_REASON_COLUMN)


def validate_products(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    reasons = combine_reasons(
        check_missing_values(df, PRODUCT_REQUIRED),
        check_duplicate_ids(df, PRODUCT_ID_COLUMN),
        check_integer_column(df, PRODUCT_ID_COLUMN),
        check_positive_float_column(df, "price"),
    )
    return split_by_reasons(df, reasons, REJECTION_REASON_COLUMN)


def validate_orders(
    df: pd.DataFrame,
    valid_customer_ids: set[str],
    valid_product_ids: set[str],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    reasons = combine_reasons(
        check_missing_values(df, ORDER_REQUIRED),
        check_duplicate_ids(df, ORDER_ID_COLUMN),
        check_integer_column(df, ORDER_ID_COLUMN),
        check_integer_column(df, CUSTOMER_ID_COLUMN),
        check_integer_column(df, PRODUCT_ID_COLUMN),
        check_positive_integer_column(df, "quantity"),
        check_date_format(df, "order_date"),
        check_foreign_key(df, CUSTOMER_ID_COLUMN, valid_customer_ids),
        check_foreign_key(df, PRODUCT_ID_COLUMN, valid_product_ids),
    )
    return split_by_reasons(df, reasons, REJECTION_REASON_COLUMN)


def run_validation() -> dict[str, dict[str, pd.DataFrame]]:
    """
    Load raw data, validate all tables, and write valid/rejected CSV outputs.

    Returns a nested dict: {entity: {"valid": df, "rejected": df}}.
    """
    # TODO: wrap with logger once logging module is added
    raw = load_all_raw()

    valid_customers, rejected_customers = validate_customers(raw["customers"])
    valid_products, rejected_products = validate_products(raw["products"])

    valid_customer_ids = _valid_id_set(valid_customers, CUSTOMER_ID_COLUMN)
    valid_product_ids = _valid_id_set(valid_products, PRODUCT_ID_COLUMN)
    valid_orders, rejected_orders = validate_orders(
        raw["orders"], valid_customer_ids, valid_product_ids
    )

    results = {
        "customers": {"valid": valid_customers, "rejected": rejected_customers},
        "products": {"valid": valid_products, "rejected": rejected_products},
        "orders": {"valid": valid_orders, "rejected": rejected_orders},
    }

    write_validation_outputs(
        valid={name: data["valid"] for name, data in results.items()},
        rejected={name: data["rejected"] for name, data in results.items()},
    )

    return results
