import csv
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def read_csv(filename):
    with open(DATA_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_customer_row_count():
    customers = read_csv("customers.csv")
    assert len(customers) == 10_000


def test_product_row_count():
    products = read_csv("products.csv")
    assert len(products) == 500


def test_order_row_count():
    orders = read_csv("orders.csv")
    assert len(orders) == 100_000


def test_customer_quality_issues_exist():
    customers = read_csv("customers.csv")

    null_emails = sum(row["email"] == "" for row in customers)
    customer_ids = [row["customer_id"] for row in customers]

    duplicate_ids = len(customer_ids) - len(set(customer_ids))

    assert null_emails == 50
    assert duplicate_ids == 10


def test_order_quality_issues_exist():
    orders = read_csv("orders.csv")

    null_customer_ids = sum(row["customer_id"] == "" for row in orders)
    null_product_ids = sum(row["product_id"] == "" for row in orders)

    order_ids = [row["order_id"] for row in orders]
    duplicate_order_ids = len(order_ids) - len(set(order_ids))

    assert null_customer_ids == 100
    assert null_product_ids == 200
    assert duplicate_order_ids == 20
