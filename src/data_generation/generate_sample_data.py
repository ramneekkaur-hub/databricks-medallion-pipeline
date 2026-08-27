"""Generate reproducible synthetic CSV source data for the learning pipeline.

The script uses only Python's standard library. A dedicated Random instance
with a fixed seed makes the generated values and injected quality issues
reproducible on every run. Empty strings are written as empty CSV fields and
are intentionally interpreted as NULL during Bronze and Silver processing.
"""

import csv
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Sequence


RANDOM_SEED = 20260827
CUSTOMER_COUNT = 10_000
PRODUCT_COUNT = 500
ORDER_COUNT = 100_000

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"

CUSTOMER_FIELDS = [
    "customer_id",
    "customer_name",
    "email",
    "country",
    "signup_date",
    "customer_segment",
    "lifetime_value",
]
PRODUCT_FIELDS = [
    "product_id",
    "product_name",
    "category",
    "price",
    "cost",
    "stock_quantity",
    "reorder_level",
]
ORDER_FIELDS = [
    "order_id",
    "customer_id",
    "order_date",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "order_status",
    "payment_date",
]


def random_date(rng: random.Random, start: date, end: date) -> date:
    """Return a deterministic random date within the inclusive date range."""
    return start + timedelta(days=rng.randint(0, (end - start).days))


def money_from_cents(cents: int) -> str:
    """Format integer cents as a two-decimal CSV value."""
    return str((Decimal(cents) / Decimal("100")).quantize(Decimal("0.01")))


def generate_customers(rng: random.Random) -> List[Dict[str, Any]]:
    """Generate customers, then inject documented customer quality issues."""
    countries = ["Australia", "Canada", "Germany", "India", "Singapore", "UK", "USA"]
    segments = ["Premium", "Standard", "Basic"]
    customers: List[Dict[str, Any]] = []

    # The final ten rows reuse IDs 1-10, producing exactly ten duplicate records.
    customer_ids = list(range(1, CUSTOMER_COUNT - 10 + 1)) + list(range(1, 11))
    for row_number, customer_id in enumerate(customer_ids, start=1):
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": f"Synthetic Customer {row_number:05d}",
                # example.invalid is reserved for examples and cannot be a real domain.
                "email": f"customer{row_number:05d}@example.invalid",
                "country": rng.choice(countries),
                "signup_date": random_date(
                    rng, date(2020, 1, 1), date(2025, 12, 31)
                ).isoformat(),
                "customer_segment": rng.choice(segments),
                "lifetime_value": money_from_cents(rng.randint(0, 2_000_000)),
            }
        )

    # Disjoint samples make each injected issue count easy to verify. An empty
    # email is written as an empty CSV field and represents a source NULL.
    issue_rows = rng.sample(range(CUSTOMER_COUNT), 80)
    for index in issue_rows[:50]:
        customers[index]["email"] = ""
    for index in issue_rows[50:60]:
        customers[index]["signup_date"] = "invalid-date"
    for index in issue_rows[60:70]:
        customers[index]["lifetime_value"] = "invalid-decimal"
    for index in issue_rows[70:80]:
        customers[index]["lifetime_value"] = "-100.00"

    return customers


def generate_products(rng: random.Random) -> List[Dict[str, Any]]:
    """Generate products, including type errors, failures, and warning cases."""
    categories = ["Accessories", "Electronics", "Home", "Office", "Sports"]
    products: List[Dict[str, Any]] = []

    for product_id in range(1, PRODUCT_COUNT + 1):
        price_cents = rng.randint(500, 200_000)
        cost_cents = rng.randint(100, price_cents)
        products.append(
            {
                "product_id": product_id,
                "product_name": f"Synthetic Product {product_id:04d}",
                "category": rng.choice(categories),
                "price": money_from_cents(price_cents),
                "cost": money_from_cents(cost_cents),
                "stock_quantity": rng.randint(0, 1_000),
                "reorder_level": rng.randint(5, 100),
            }
        )

    issue_rows = rng.sample(range(PRODUCT_COUNT), 30)
    for index in issue_rows[:10]:
        products[index]["price"] = "invalid-decimal"
    for index in issue_rows[10:20]:
        products[index]["stock_quantity"] = "invalid-integer"
    for index in issue_rows[20:25]:
        products[index]["stock_quantity"] = -1
    for index in issue_rows[25:30]:
        # Cost above price is intentionally a warning, not a failing rule.
        price = Decimal(products[index]["price"])
        products[index]["cost"] = str(price + Decimal("10.00"))

    return products


def generate_orders(rng: random.Random, products: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Generate orders, then inject referential, type, and business-rule issues."""
    statuses = ["Pending", "Completed", "Cancelled"]
    valid_customer_count = CUSTOMER_COUNT - 10
    product_prices = {
        int(product["product_id"]): product["price"]
        for product in products
        if product["price"] != "invalid-decimal"
    }
    valid_product_ids = list(product_prices)
    orders: List[Dict[str, Any]] = []

    # The final twenty rows reuse IDs 1-20, producing exactly twenty duplicates.
    order_ids = list(range(1, ORDER_COUNT - 20 + 1)) + list(range(1, 21))
    for order_id in order_ids:
        order_date = random_date(rng, date(2023, 1, 1), date(2025, 12, 31))
        product_id = rng.choice(valid_product_ids)
        quantity = rng.randint(1, 10)
        unit_price = str(product_prices[product_id])
        total_amount = (Decimal(unit_price) * quantity).quantize(Decimal("0.01"))
        status = rng.choice(statuses)
        payment_date = (
            (order_date + timedelta(days=rng.randint(0, 3))).isoformat()
            if status == "Completed"
            else ""
        )

        orders.append(
            {
                "order_id": order_id,
                "customer_id": rng.randint(1, valid_customer_count),
                "order_date": order_date.isoformat(),
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_amount": str(total_amount),
                "order_status": status,
                "payment_date": payment_date,
            }
        )

    # Empty ID strings become empty CSV fields (source NULLs). Disjoint rows
    # provide exact completeness and referential issue counts.
    reference_issue_rows = rng.sample(range(ORDER_COUNT), 380)
    for index in reference_issue_rows[:100]:
        orders[index]["customer_id"] = ""
    for index in reference_issue_rows[100:300]:
        orders[index]["product_id"] = ""
    for offset, index in enumerate(reference_issue_rows[300:350], start=1):
        orders[index]["customer_id"] = valid_customer_count + 10_000 + offset
    for offset, index in enumerate(reference_issue_rows[350:380], start=1):
        orders[index]["product_id"] = PRODUCT_COUNT + 10_000 + offset

    # Additional disjoint rows demonstrate Silver type and business validation.
    validation_issue_rows = rng.sample(
        sorted(set(range(ORDER_COUNT)) - set(reference_issue_rows)), 175
    )
    for index in validation_issue_rows[:25]:
        orders[index]["order_date"] = "invalid-date"
    for index in validation_issue_rows[25:50]:
        orders[index]["quantity"] = "invalid-integer"
    for index in validation_issue_rows[50:75]:
        orders[index]["unit_price"] = "invalid-decimal"
    for index in validation_issue_rows[75:100]:
        orders[index]["quantity"] = 0
        # Keep the amount mathematically consistent so this row demonstrates
        # only the non-positive quantity rule.
        orders[index]["total_amount"] = "0.00"
    for index in validation_issue_rows[100:125]:
        orders[index]["total_amount"] = str(
            Decimal(orders[index]["total_amount"]) + Decimal("1.00")
        )
    for index in validation_issue_rows[125:150]:
        orders[index]["order_status"] = "Unknown"
    for index in validation_issue_rows[150:175]:
        order_date = date.fromisoformat(orders[index]["order_date"])
        orders[index]["payment_date"] = (order_date - timedelta(days=1)).isoformat()

    return orders


def write_csv(path: Path, fieldnames: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    """Write rows with a stable column order and a header."""
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def validate_row_counts(
    customers: Sequence[Dict[str, Any]],
    products: Sequence[Dict[str, Any]],
    orders: Sequence[Dict[str, Any]],
) -> None:
    """Fail immediately if generation does not produce the required row counts."""
    assert len(customers) == CUSTOMER_COUNT, "Unexpected customer row count"
    assert len(products) == PRODUCT_COUNT, "Unexpected product row count"
    assert len(orders) == ORDER_COUNT, "Unexpected order row count"


def print_summary() -> None:
    """Print the intentional issues that the Silver layer should detect."""
    print("Generated customers.csv: 10,000 rows")
    print("  - 50 NULL emails")
    print("  - 10 duplicate customer_id records")
    print("  - 10 invalid signup_date values")
    print("  - 10 invalid lifetime_value values")
    print("  - 10 negative lifetime_value values")
    print("Generated products.csv: 500 rows")
    print("  - 10 invalid price values")
    print("  - 10 invalid stock_quantity values")
    print("  - 5 negative stock_quantity values")
    print("  - 5 cost-greater-than-price warnings")
    print("Generated orders.csv: 100,000 rows")
    print("  - 100 NULL customer_id values")
    print("  - 200 NULL product_id values")
    print("  - 50 non-existent customer_id values")
    print("  - 30 non-existent product_id values")
    print("  - 20 duplicate order_id records")
    print("  - 25 invalid order_date values")
    print("  - 25 invalid quantity values")
    print("  - 25 invalid unit_price values")
    print("  - 25 zero quantity values")
    print("  - 25 incorrect total_amount values")
    print("  - 25 invalid order_status values")
    print("  - 25 payment dates before order dates")


def main() -> None:
    """Generate, validate, and write all source files."""
    rng = random.Random(RANDOM_SEED)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(rng)
    products = generate_products(rng)
    orders = generate_orders(rng, products)
    validate_row_counts(customers, products, orders)

    write_csv(DATA_DIR / "customers.csv", CUSTOMER_FIELDS, customers)
    write_csv(DATA_DIR / "products.csv", PRODUCT_FIELDS, products)
    write_csv(DATA_DIR / "orders.csv", ORDER_FIELDS, orders)

    print(f"Synthetic data written to: {DATA_DIR}")
    print(f"Random seed: {RANDOM_SEED}")
    print_summary()


if __name__ == "__main__":
    main()
