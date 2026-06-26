import pandas as pd

from src.validation.validator import validate_customers, validate_orders, validate_products


def test_validate_customers(sample_customers: pd.DataFrame) -> None:
    valid, rejected = validate_customers(sample_customers)

    assert len(valid) == 2
    assert set(valid["customer_id"]) == {"1", "3"}
    assert len(rejected) == 2
    assert "invalid_email_format" in rejected.iloc[0]["rejection_reason"]
    assert "duplicate_customer_id" in rejected.iloc[1]["rejection_reason"]


def test_validate_products(sample_products: pd.DataFrame) -> None:
    valid, rejected = validate_products(sample_products)

    assert len(valid) == 1
    assert valid.iloc[0]["product_id"] == "1"
    assert len(rejected) == 2


def test_validate_orders_rejects_invalid_foreign_keys(sample_orders: pd.DataFrame) -> None:
    valid, rejected = validate_orders(sample_orders, {"1"}, {"1"})

    assert len(valid) == 1
    assert valid.iloc[0]["order_id"] == "1"
    assert len(rejected) == 2
    rejected_reasons = " ".join(rejected["rejection_reason"])
    assert "invalid_foreign_key:customer_id" in rejected_reasons
    assert "non_positive_integer:quantity" in rejected_reasons or "invalid_date:order_date" in rejected_reasons
