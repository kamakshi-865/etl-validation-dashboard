"""Shared fixtures for pipeline tests."""

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def sample_customers() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"customer_id": "1", "name": "John Doe", "email": "john@gmail.com", "city": "delhi"},
            {"customer_id": "2", "name": "", "email": "bad-email", "city": "Mumbai"},
            {"customer_id": "3", "name": "Bob", "email": "bob@gmail.com", "city": "Pune"},
            {"customer_id": "3", "name": "Bob Duplicate", "email": "bob@gmail.com", "city": "Pune"},
        ]
    )


@pytest.fixture
def sample_products() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"product_id": "1", "product_name": "Laptop", "category": "electronics", "price": "1000"},
            {"product_id": "2", "product_name": "Phone", "category": "electronics", "price": "0"},
            {"product_id": "1", "product_name": "Laptop Dup", "category": "electronics", "price": "500"},
        ]
    )


@pytest.fixture
def sample_orders() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "order_id": "1",
                "customer_id": "1",
                "product_id": "1",
                "quantity": "2",
                "order_date": "2024-01-15",
            },
            {
                "order_id": "2",
                "customer_id": "99",
                "product_id": "1",
                "quantity": "1",
                "order_date": "2024-02-01",
            },
            {
                "order_id": "3",
                "customer_id": "1",
                "product_id": "1",
                "quantity": "0",
                "order_date": "bad-date",
            },
        ]
    )


@pytest.fixture
def cleaned_pipeline_data() -> dict[str, pd.DataFrame]:
    products = pd.DataFrame(
        [
            {"product_id": 1, "product_name": "Laptop", "category": "Electronics", "price": 1000.0},
            {"product_id": 2, "product_name": "Phone", "category": "Electronics", "price": 500.0},
        ]
    )
    customers = pd.DataFrame(
        [
            {"customer_id": 1, "name": "John Doe", "email": "john@gmail.com", "city": "Delhi"},
            {"customer_id": 2, "name": "Alice", "email": "alice@gmail.com", "city": "Mumbai"},
        ]
    )
    orders = pd.DataFrame(
        [
            {
                "order_id": 1,
                "customer_id": 1,
                "product_id": 1,
                "quantity": 2,
                "order_date": pd.Timestamp("2024-01-15").date(),
                "unit_price": 1000.0,
                "total_order_value": 2000.0,
            },
            {
                "order_id": 2,
                "customer_id": 2,
                "product_id": 2,
                "quantity": 1,
                "order_date": pd.Timestamp("2024-02-20").date(),
                "unit_price": 500.0,
                "total_order_value": 500.0,
            },
        ]
    )
    return {"customers": customers, "products": products, "orders": orders}


@pytest.fixture
def isolated_data_dirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Point all data paths at a temporary directory for integration tests."""
    raw_dir = tmp_path / "raw"
    valid_dir = tmp_path / "valid"
    rejected_dir = tmp_path / "rejected"
    cleaned_dir = tmp_path / "cleaned"
    insights_dir = tmp_path / "insights"
    db_path = tmp_path / "test.db"

    for directory in (raw_dir, valid_dir, rejected_dir, cleaned_dir, insights_dir):
        directory.mkdir()

    raw_dir.joinpath("customers.csv").write_text(
        "customer_id,name,email,city\n"
        "1,John Doe,john@gmail.com,Delhi\n"
        "2,Alice Smith,alice@gmail.com,Mumbai\n",
        encoding="utf-8",
    )
    raw_dir.joinpath("products.csv").write_text(
        "product_id,product_name,category,price\n"
        "1,Laptop,Electronics,1000\n"
        "2,Phone,Electronics,500\n",
        encoding="utf-8",
    )
    raw_dir.joinpath("orders.csv").write_text(
        "order_id,customer_id,product_id,quantity,order_date\n"
        "1,1,1,2,2024-01-15\n"
        "2,2,2,1,2024-02-20\n",
        encoding="utf-8",
    )

    import src.config as config

    monkeypatch.setattr(config, "RAW_DATA_DIR", raw_dir)
    monkeypatch.setattr(config, "VALID_DATA_DIR", valid_dir)
    monkeypatch.setattr(config, "REJECTED_DATA_DIR", rejected_dir)
    monkeypatch.setattr(config, "CLEANED_DATA_DIR", cleaned_dir)
    monkeypatch.setattr(config, "INSIGHTS_DATA_DIR", insights_dir)
    monkeypatch.setattr(config, "DATABASE_PATH", db_path)
    monkeypatch.setattr(config, "DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setattr(
        config,
        "RAW_FILES",
        {
            "customers": raw_dir / "customers.csv",
            "products": raw_dir / "products.csv",
            "orders": raw_dir / "orders.csv",
        },
    )

    return tmp_path
