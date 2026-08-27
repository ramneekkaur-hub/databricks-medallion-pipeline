"""Ingest the raw e-commerce CSV files into Bronze Delta tables.

Bronze deliberately reads every source column as a string so invalid source
values remain available for validation in Silver.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F


DATA_DIRECTORY = Path(__file__).resolve().parents[2] / "data"
DATASETS: Dict[str, str] = {
    "customers": f"file:{DATA_DIRECTORY / 'customers.csv'}",
    "products": f"file:{DATA_DIRECTORY / 'products.csv'}",
    "orders": f"file:{DATA_DIRECTORY / 'orders.csv'}",
}
BRONZE_SCHEMA = "bronze"


def read_source_csv(spark: SparkSession, source_path: str) -> DataFrame:
    """Read a CSV without inferring types or filtering invalid records."""
    return (
        spark.read.option("header", "true")
        .option("inferSchema", "false")
        .option("mode", "PERMISSIVE")
        .csv(source_path)
    )


def add_ingestion_metadata(source_df: DataFrame, batch_id: str) -> DataFrame:
    """Add audit metadata while leaving all source columns unchanged."""
    return (
        source_df.withColumn("ingestion_timestamp", F.current_timestamp())
        # _metadata.file_name works with Unity Catalog and serverless compute;
        # input_file_name() is deprecated and unavailable on newer runtimes.
        .withColumn("source_file_name", F.col("_metadata.file_name"))
        .withColumn("batch_id", F.lit(batch_id))
    )


def ingest_dataset(
    spark: SparkSession, dataset_name: str, source_path: str, batch_id: str
) -> None:
    """Overwrite one Bronze table and confirm that no source rows were lost."""
    source_df = read_source_csv(spark, source_path)
    source_count = source_df.count()
    bronze_df = add_ingestion_metadata(source_df, batch_id)
    table_name = f"{BRONZE_SCHEMA}.{dataset_name}"

    (
        bronze_df.write.format("delta")
        .mode("overwrite")
        .option("overwriteSchema", "true")
        .saveAsTable(table_name)
    )

    bronze_count = spark.table(table_name).count()
    if bronze_count != source_count:
        raise RuntimeError(
            f"Row-count validation failed for {dataset_name}: "
            f"source={source_count}, bronze={bronze_count}"
        )

    print(
        f"Loaded {dataset_name}: source={source_count}, "
        f"bronze={bronze_count}, table={table_name}"
    )


def main() -> None:
    """Create the Bronze schema and ingest all source datasets."""
    spark = SparkSession.builder.appName("ecommerce-bronze-ingestion").getOrCreate()
    spark.sql(f"CREATE SCHEMA IF NOT EXISTS {BRONZE_SCHEMA}")

    batch_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    for dataset_name, source_path in DATASETS.items():
        ingest_dataset(spark, dataset_name, source_path, batch_id)


if __name__ == "__main__":
    main()
