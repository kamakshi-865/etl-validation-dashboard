# Retail ETL Pipeline

![Tests](https://github.com/kamakshi-865/etl-validation-dashboard/actions/workflows/tests.yml/badge.svg)

An automated retail ETL pipeline that ingests CSV data, validates and quarantines bad
records, cleans and transforms valid data, loads it into SQL, and generates business
insight reports — with a Streamlit dashboard on top for uploading new data and viewing
results visually.



## Architecture

```
 data/raw/*.csv
        │
        ▼
 ┌─────────────┐     valid rows      ┌──────────────┐     ┌────────────┐     ┌────────────┐
 │  Validation │ ──────────────────▶ │ Transformation│ ──▶ │    Load    │ ──▶ │  Insights  │
 └─────────────┘                     └──────────────┘     │ (SQLite /  │     │ (reports)  │
        │                                                  │ Postgres)  │     └────────────┘
        ▼ rejected rows                                    └────────────┘
 data/rejected/*.csv
 (+ rejection_reason)
```

Each stage is a separate module (`src/validation`, `src/transform`, `src/load`,
`src/insights`), orchestrated by `main.py`. Bad rows never reach the database — they're
quarantined with a reason code instead of silently breaking the pipeline downstream.

## Features

- **Ingestion** — reads customer, product, and order CSVs from `data/raw/`
- **Validation** — detects missing values, duplicate IDs, invalid types, bad emails/dates, and broken referential integrity
- **Quarantine** — splits records into `data/valid/` and `data/rejected/` (with a `rejection_reason` column)
- **Transformation** — type casting, text normalization, deduplication, and derived columns (`unit_price`, `total_order_value`)
- **Load** — writes cleaned data to SQLite via SQLAlchemy (Postgres-ready, no code changes)
- **Insights** — top-selling products, revenue trends, and customer purchase statistics
- **Dashboard** — upload new data, run the pipeline, and view results as interactive charts
- **CI** — GitHub Actions runs the full test suite on every push

## Project structure

```
retail-data-pipeline/
├── main.py                     # Pipeline entry point
├── dashboard.py                 # Streamlit dashboard
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Dev/test dependencies
├── .github/workflows/tests.yml # CI: runs pytest on every push
├── data/
│   ├── raw/                    # Input CSVs
│   ├── valid/                  # Validated rows
│   ├── rejected/               # Quarantined rows + rejection_reason
│   ├── cleaned/                # Transformed rows
│   ├── insights/               # Generated report CSVs
│   ├── run_history.csv         # Per-run data-quality log (created by dashboard)
│   └── retail.db               # SQLite database (created on run)
└── src/
    ├── config.py               # Paths, schemas, database URL
    ├── ingestion/               # CSV readers
    ├── validation/              # Validation checks and orchestration
    ├── transform/               # Cleaning and transformation
    ├── load/                    # SQLAlchemy models and loader
    ├── insights/                # SQL-based reporting
    └── utils/                   # Shared I/O helpers
```

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

For development and tests:

```powershell
pip install -r requirements-dev.txt
```

## Run the pipeline

```powershell
python main.py
```

Expected flow:

1. Validate raw CSVs → write `data/valid/` and `data/rejected/`
2. Transform valid data → write `data/cleaned/`
3. Load cleaned data → `data/retail.db`
4. Generate insights → `data/insights/` + console summary

## Dashboard

A Streamlit dashboard lets you upload new raw CSVs, trigger the pipeline, and view
validation results and business insights as charts — without touching the command line.

```powershell
streamlit run dashboard.py
```

What it does:

- Upload `customers.csv` / `products.csv` / `orders.csv` from the sidebar (each upload
  replaces the matching file in `data/raw/`).
- Click **Run ETL Pipeline** to run validate → transform → load → insights end to end.
- View valid/rejected counts per entity, with an expandable view of rejected rows and
  their `rejection_reason`.
- View generated charts: top-selling products, revenue trend over time, and a
  spend-vs-order-frequency scatter for customers.
- A **Run History** table (`data/run_history.csv`) tracks valid/rejected counts and rows
  loaded across every run, so you can see data-quality trends over time.

## Run tests

```powershell
pytest
```

Run with verbose output:

```powershell
pytest -v
```

Tests run automatically on every push via GitHub Actions (`.github/workflows/tests.yml`)
— see the **Actions** tab on GitHub for results.

## Validation rules

| Check | Customers | Products | Orders |
|-------|-----------|----------|--------|
| Missing required fields | ✓ | ✓ | ✓ |
| Duplicate primary key (keep first) | ✓ | ✓ | ✓ |
| Integer ID fields | ✓ | ✓ | ✓ |
| Email format (`@` required) | ✓ | | |
| Positive price | | ✓ | |
| Positive quantity | | | ✓ |
| Date format (`YYYY-MM-DD`) | | | ✓ |
| Foreign keys (customer, product) | | | ✓ |

## Switching to Postgres

Set `DATABASE_URL` before running. No code changes required:

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://user:pass@localhost:5432/retail"
python main.py
```

Install a Postgres driver when you make the switch, e.g. `psycopg2-binary`.

## Sample raw data

The included CSVs contain deliberate bad rows for testing validation:

- **customers** — invalid email, missing name, duplicate ID
- **products** — missing name, invalid price, duplicate ID, negative price
- **orders** — invalid FKs, zero quantity, missing quantity, bad date, duplicate ID

## Future phases (not implemented)

- Structured logging module
- Scheduling / automation
- PySpark support for large-volume processing
- Deployment of the dashboard (Streamlit Community Cloud)

TODO hooks are left in the codebase where those integrations will attach.

## Tech stack

- Python 3.10+
- pandas
- SQLAlchemy 2.x
- Streamlit + Plotly (dashboard)
- pytest (tests)
- GitHub Actions (CI)

## License

MIT — feel free to use this as a reference for your own ETL projects.
