import pandas as pd

from src.transform.cleaners import transform_customers, transform_orders, transform_products


def test_transform_customers_normalizes_text_and_types() -> None:
    df = pd.DataFrame(
        [{"customer_id": "1", "name": "  John  ", "email": "JOHN@Gmail.COM", "city": "new delhi"}]
    )
    cleaned = transform_customers(df)

    assert cleaned.iloc[0]["customer_id"] == 1
    assert cleaned.iloc[0]["name"] == "John"
    assert cleaned.iloc[0]["email"] == "john@gmail.com"
    assert cleaned.iloc[0]["city"] == "New Delhi"


def test_transform_products_casts_price() -> None:
    df = pd.DataFrame(
        [{"product_id": "1", "product_name": "Laptop", "category": "electronics", "price": "999.5"}]
    )
    cleaned = transform_products(df)

    assert cleaned.iloc[0]["price"] == 999.5
    assert cleaned.iloc[0]["category"] == "Electronics"


def test_transform_orders_derives_total_order_value() -> None:
    orders = pd.DataFrame(
        [
            {
                "order_id": "1",
                "customer_id": "1",
                "product_id": "1",
                "quantity": "3",
                "order_date": "2024-01-15",
            }
        ]
    )
    products = pd.DataFrame(
        [{"product_id": 1, "product_name": "Laptop", "category": "Electronics", "price": 1000.0}]
    )

    cleaned = transform_orders(orders, products)

    assert cleaned.iloc[0]["unit_price"] == 1000.0
    assert cleaned.iloc[0]["total_order_value"] == 3000.0
    assert str(cleaned.iloc[0]["order_date"]) == "2024-01-15"
