"""Execute the Gold Spark SQL files and validate their basic outputs."""

from pathlib import Path
from typing import Dict, List

from pyspark.sql import SparkSession
from pyspark.sql import functions as F


SQL_FILES: List[str] = [
    "01_sales_by_product.sql",
    "02_revenue_by_customer.sql",
    "03_daily_weekly_trends.sql",
    "04_customer_segmentation.sql",
]
GOLD_TABLES: List[str] = [
    "gold.sales_by_product",
    "gold.revenue_by_customer",
    "gold.daily_sales_trends",
    "gold.weekly_sales_trends",
    "gold.customer_segmentation",
]


def sql_directory() -> Path:
    """Locate SQL files when run as a script or from a Databricks workspace."""
    if "__file__" in globals():
        return Path(__file__).resolve().parent

    current_directory = Path.cwd()
    repository_directory = current_directory / "src" / "gold"
    return (
        repository_directory
        if repository_directory.exists()
        else current_directory
    )


def execute_sql_file(spark: SparkSession, sql_path: Path) -> None:
    """Execute each semicolon-delimited statement in one SQL file."""
    sql_text = sql_path.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]
    for statement in statements:
        spark.sql(statement)
    print(f"Executed {sql_path.name}")


def validate_gold_tables(spark: SparkSession) -> Dict[str, int]:
    """Check expected tables and reconcile retained product/customer rows."""
    table_counts = {
        table_name: spark.table(table_name).count()
        for table_name in GOLD_TABLES
    }

    valid_product_count = spark.table("silver.products").where(
        F.col("quality_check_result") == "PASS"
    ).count()
    if table_counts["gold.sales_by_product"] != valid_product_count:
        raise RuntimeError(
            "sales_by_product does not contain every accepted product"
        )

    valid_customer_count = spark.table("silver.customers").where(
        F.col("quality_check_result") == "PASS"
    ).count()
    if table_counts["gold.revenue_by_customer"] != valid_customer_count:
        raise RuntimeError(
            "revenue_by_customer does not contain every accepted customer"
        )

    segmented_customer_count = (
        spark.table("gold.customer_segmentation")
        .agg(F.coalesce(F.sum("customer_count"), F.lit(0)).alias("count"))
        .first()["count"]
    )
    if segmented_customer_count != valid_customer_count:
        raise RuntimeError(
            "customer_segmentation does not classify every accepted customer"
        )

    return table_counts


def main() -> None:
    """Create all Gold tables in dependency order."""
    spark = SparkSession.builder.appName("ecommerce-gold-tables").getOrCreate()
    spark.sql("CREATE SCHEMA IF NOT EXISTS gold")

    directory = sql_directory()
    for sql_file in SQL_FILES:
        execute_sql_file(spark, directory / sql_file)

    for table_name, row_count in validate_gold_tables(spark).items():
        print(f"Validated {table_name}: rows={row_count}")


if __name__ == "__main__":
    main()
