"""Load cleaned datasets into the SQL database."""

import pandas as pd
from sqlalchemy.engine import Engine

from src.load.database import get_engine
from src.load.models import Base, Customer, Order, Product

# Load parent tables before child tables to satisfy foreign keys.
LOAD_ORDER = [
    ("customers", Customer.__tablename__),
    ("products", Product.__tablename__),
    ("orders", Order.__tablename__),
]


def _load_table(engine: Engine, table_name: str, df: pd.DataFrame) -> int:
    """Replace a single table's contents with the given DataFrame."""
    row_count = len(df)
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    return row_count


def run_load(
    cleaned: dict[str, pd.DataFrame],
    database_url: str | None = None,
) -> dict[str, int]:
    """
    Create tables (if needed) and load cleaned data into the database.

    Args:
        cleaned: Output from run_transformation(), keyed by entity name.
        database_url: Optional override; defaults to config / DATABASE_URL env var.

    Returns:
        Dict mapping table name to number of rows loaded.
    """
    # TODO: wrap with logger once logging module is added
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)

    loaded: dict[str, int] = {}
    for dataset_key, table_name in LOAD_ORDER:
        df = cleaned[dataset_key]
        loaded[table_name] = _load_table(engine, table_name, df)

    return loaded
