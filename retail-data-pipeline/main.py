"""Entry point for the retail ETL pipeline."""

from src.insights.reporter import run_insights
from src.load.loader import run_load
from src.transform.transformer import run_transformation
from src.validation.validator import run_validation


def main() -> None:
    validation_results = run_validation()

    for entity, datasets in validation_results.items():
        valid_count = len(datasets["valid"])
        rejected_count = len(datasets["rejected"])
        print(f"{entity}: {valid_count} valid, {rejected_count} rejected")

    cleaned = run_transformation(validation_results)

    for entity, df in cleaned.items():
        print(f"{entity}: {len(df)} cleaned rows written to data/cleaned/")

    loaded = run_load(cleaned)

    for table, count in loaded.items():
        print(f"{table}: {count} rows loaded into database")

    reports = run_insights()

    print("\n--- Business Insights ---")
    print("\nTop-selling products:")
    print(reports["top_selling_products"].to_string(index=False))

    print("\nRevenue trends:")
    print(reports["revenue_trends"].to_string(index=False))

    print("\nCustomer purchase stats:")
    print(reports["customer_purchase_stats"].to_string(index=False))

    print(f"\nReports written to data/insights/")


if __name__ == "__main__":
    main()
