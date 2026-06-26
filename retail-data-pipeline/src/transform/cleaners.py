"""Pure cleaning and type-casting functions for validated datasets."""

import pandas as pd

from src.config import CUSTOMER_ID_COLUMN, ORDER_ID_COLUMN, PRODUCT_ID_COLUMN


def _strip_text(value: object) -> str:
    return str(value).strip()


def transform_customers(df: pd.DataFrame) -> pd.DataFrame:
    """Cast types and normalize customer text fields."""
    cleaned = df.copy()
    cleaned[CUSTOMER_ID_COLUMN] = cleaned[CUSTOMER_ID_COLUMN].astype(int)
    cleaned["name"] = cleaned["name"].map(_strip_text)
    cleaned["email"] = cleaned["email"].map(lambda v: _strip_text(v).lower())
    cleaned["city"] = cleaned["city"].map(lambda v: _strip_text(v).title())
    cleaned = cleaned.drop_duplicates(subset=[CUSTOMER_ID_COLUMN], keep="first")
    return cleaned.reset_index(drop=True)


def transform_products(df: pd.DataFrame) -> pd.DataFrame:
    """Cast types and normalize product fields."""
    cleaned = df.copy()
    cleaned[PRODUCT_ID_COLUMN] = cleaned[PRODUCT_ID_COLUMN].astype(int)
    cleaned["product_name"] = cleaned["product_name"].map(_strip_text)
    cleaned["category"] = cleaned["category"].map(lambda v: _strip_text(v).title())
    cleaned["price"] = cleaned["price"].astype(float)
    cleaned = cleaned.drop_duplicates(subset=[PRODUCT_ID_COLUMN], keep="first")
    return cleaned.reset_index(drop=True)


def transform_orders(df: pd.DataFrame, products: pd.DataFrame) -> pd.DataFrame:
    """
    Cast order types, parse dates, and derive unit_price and total_order_value.

    unit_price comes from the cleaned products table; total_order_value = quantity * unit_price.
    """
    cleaned = df.copy()
    cleaned[ORDER_ID_COLUMN] = cleaned[ORDER_ID_COLUMN].astype(int)
    cleaned[CUSTOMER_ID_COLUMN] = cleaned[CUSTOMER_ID_COLUMN].astype(int)
    cleaned[PRODUCT_ID_COLUMN] = cleaned[PRODUCT_ID_COLUMN].astype(int)
    cleaned["quantity"] = cleaned["quantity"].astype(int)
    cleaned["order_date"] = pd.to_datetime(cleaned["order_date"], format="%Y-%m-%d").dt.date
    cleaned = cleaned.drop_duplicates(subset=[ORDER_ID_COLUMN], keep="first")

    price_lookup = products.set_index(PRODUCT_ID_COLUMN)["price"]
    cleaned["unit_price"] = cleaned[PRODUCT_ID_COLUMN].map(price_lookup).astype(float)
    cleaned["total_order_value"] = cleaned["quantity"] * cleaned["unit_price"]

    return cleaned.reset_index(drop=True)
