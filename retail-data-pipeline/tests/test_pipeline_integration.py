from pathlib import Path

import pandas as pd

from src.insights.reporter import run_insights
from src.load.loader import run_load
from src.transform.transformer import run_transformation
from src.validation.validator import run_validation


def test_full_pipeline_on_isolated_data(isolated_data_dirs: Path) -> None:
    validation_results = run_validation()

    assert len(validation_results["customers"]["valid"]) == 2
    assert len(validation_results["orders"]["valid"]) == 2
    assert (isolated_data_dirs / "valid" / "customers.csv").exists()

    cleaned = run_transformation(validation_results)
    assert cleaned["orders"].iloc[0]["total_order_value"] == 2000.0

    loaded = run_load(cleaned)
    assert loaded["orders"] == 2

    reports = run_insights()
    assert not reports["top_selling_products"].empty
    assert (isolated_data_dirs / "insights" / "revenue_trends.csv").exists()

    revenue = pd.read_csv(isolated_data_dirs / "insights" / "revenue_trends.csv")
    assert revenue["daily_revenue"].sum() == 2500.0
