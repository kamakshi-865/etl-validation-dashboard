from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from src.insights.reporter import run_insights
from src.load.loader import run_load


def test_run_load_writes_tables(cleaned_pipeline_data: dict[str, pd.DataFrame], tmp_path: Path) -> None:
    db_path = tmp_path / "load_test.db"
    database_url = f"sqlite:///{db_path.as_posix()}"

    loaded = run_load(cleaned_pipeline_data, database_url=database_url)

    assert loaded == {"customers": 2, "products": 2, "orders": 2}

    engine = create_engine(database_url)
    with engine.connect() as conn:
        order_count = conn.execute(text("SELECT COUNT(*) FROM orders")).scalar_one()
        assert order_count == 2


def test_run_insights_produces_expected_reports(
    cleaned_pipeline_data: dict[str, pd.DataFrame],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    db_path = tmp_path / "insights_test.db"
    insights_dir = tmp_path / "insights"
    insights_dir.mkdir()
    database_url = f"sqlite:///{db_path.as_posix()}"

    import src.config as config

    monkeypatch.setattr(config, "INSIGHTS_DATA_DIR", insights_dir)
    monkeypatch.setattr(config, "DATABASE_URL", database_url)
    monkeypatch.setattr(config, "DATABASE_PATH", db_path)

    run_load(cleaned_pipeline_data, database_url=database_url)
    reports = run_insights(database_url=database_url)

    assert list(reports.keys()) == [
        "top_selling_products",
        "revenue_trends",
        "customer_purchase_stats",
    ]
    assert reports["top_selling_products"].iloc[0]["product_name"] == "Laptop"
    assert reports["revenue_trends"]["daily_revenue"].sum() == 2500.0
    assert reports["customer_purchase_stats"].iloc[0]["total_spend"] == 2000.0
    assert (insights_dir / "top_selling_products.csv").exists()
