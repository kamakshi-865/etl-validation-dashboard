"""SQL queries for business insight reports."""

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

TOP_SELLING_PRODUCTS_SQL = text(
    """
    SELECT
        p.product_id,
        p.product_name,
        p.category,
        SUM(o.quantity) AS total_quantity_sold,
        SUM(o.total_order_value) AS total_revenue
    FROM orders o
    JOIN products p ON o.product_id = p.product_id
    GROUP BY p.product_id, p.product_name, p.category
    ORDER BY total_revenue DESC, total_quantity_sold DESC
    """
)

REVENUE_TRENDS_SQL = text(
    """
    SELECT
        order_date,
        COUNT(order_id) AS order_count,
        SUM(total_order_value) AS daily_revenue
    FROM orders
    GROUP BY order_date
    ORDER BY order_date
    """
)

CUSTOMER_PURCHASE_STATS_SQL = text(
    """
    SELECT
        c.customer_id,
        c.name,
        c.email,
        c.city,
        COUNT(o.order_id) AS order_frequency,
        SUM(o.total_order_value) AS total_spend,
        AVG(o.total_order_value) AS average_order_value
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name, c.email, c.city
    ORDER BY total_spend DESC
    """
)


def fetch_top_selling_products(engine: Engine) -> pd.DataFrame:
    """Return products ranked by revenue and quantity sold."""
    with engine.connect() as conn:
        return pd.read_sql(TOP_SELLING_PRODUCTS_SQL, conn)


def fetch_revenue_trends(engine: Engine) -> pd.DataFrame:
    """Return daily order count and revenue over time."""
    with engine.connect() as conn:
        return pd.read_sql(REVENUE_TRENDS_SQL, conn)


def fetch_customer_purchase_stats(engine: Engine) -> pd.DataFrame:
    """Return per-customer order frequency, total spend, and AOV."""
    with engine.connect() as conn:
        return pd.read_sql(CUSTOMER_PURCHASE_STATS_SQL, conn)
