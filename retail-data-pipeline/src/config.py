"""Central configuration: paths, schemas, and validation rules."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
VALID_DATA_DIR = PROJECT_ROOT / "data" / "valid"
REJECTED_DATA_DIR = PROJECT_ROOT / "data" / "rejected"
CLEANED_DATA_DIR = PROJECT_ROOT / "data" / "cleaned"
INSIGHTS_DATA_DIR = PROJECT_ROOT / "data" / "insights"

REJECTION_REASON_COLUMN = "rejection_reason"

# Column definitions per entity
CUSTOMER_COLUMNS = ["customer_id", "name", "email", "city"]
PRODUCT_COLUMNS = ["product_id", "product_name", "category", "price"]
ORDER_COLUMNS = ["order_id", "customer_id", "product_id", "quantity", "order_date"]
CLEANED_ORDER_COLUMNS = ORDER_COLUMNS + ["unit_price", "total_order_value"]

CUSTOMER_REQUIRED = ["customer_id", "name", "email", "city"]
PRODUCT_REQUIRED = ["product_id", "product_name", "category", "price"]
ORDER_REQUIRED = ["order_id", "customer_id", "product_id", "quantity", "order_date"]

CUSTOMER_ID_COLUMN = "customer_id"
PRODUCT_ID_COLUMN = "product_id"
ORDER_ID_COLUMN = "order_id"

RAW_FILES = {
    "customers": RAW_DATA_DIR / "customers.csv",
    "products": RAW_DATA_DIR / "products.csv",
    "orders": RAW_DATA_DIR / "orders.csv",
}

DATABASE_PATH = PROJECT_ROOT / "data" / "retail.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"
