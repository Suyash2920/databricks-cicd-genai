"""
Reusable transformation logic for the Sales ETL pipeline.

The logic lives in a plain Python module (not inside notebooks) so that it can be
unit-tested in GitHub Actions with a local Spark session. The notebooks import it.
"""
import re

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType

# Only letters, digits and "_" are allowed in catalog/schema/table names.
# This protects the SQL statements in the notebooks from SQL injection.
_IDENTIFIER_PATTERN = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,254}")

RAW_ORDERS_SCHEMA = StructType([
    StructField("order_id", StringType(), True),
    StructField("order_date", StringType(), True),
    StructField("customer_id", StringType(), True),
    StructField("region", StringType(), True),
    StructField("product", StringType(), True),
    StructField("quantity", IntegerType(), True),
    StructField("unit_price", DoubleType(), True),
])

# Small built-in dataset (Free Edition friendly: no external storage needed).
# It intentionally contains bad records to demonstrate data cleaning.
SAMPLE_ORDERS = [
    ("O1001", "2025-01-05", "C001", "North", "Laptop", 1, 850.0),
    ("O1002", "2025-01-05", "C002", "South", "Mouse", 3, 15.5),
    ("O1003", "2025-01-06", "C003", "East", "Keyboard", 2, 45.0),
    ("O1004", "2025-01-06", "C001", "North", "Mouse", 1, 15.5),
    ("O1005", "2025-01-07", "C004", "West", "Laptop", 2, 820.0),
    ("O1006", "2025-01-07", "C005", "South", "Monitor", 1, 199.99),
    ("O1007", "2025-01-08", "C002", "East", "Laptop", 1, 860.0),
    ("O1008", "2025-01-08", "C006", "West", "Keyboard", 4, 42.0),
    ("O1011", "2025-01-10", "C008", " north ", "Laptop", 1, 870.0),  # messy region text
    ("O1002", "2025-01-05", "C002", "South", "Mouse", 3, 15.5),      # duplicate order
    ("O1009", "2025-01-09", None, "North", "Monitor", 1, 205.0),     # missing customer
    ("O1010", "2025-01-09", "C007", "East", "Mouse", -2, 15.5),      # negative quantity
]


def validate_identifier(name: str) -> str:
    """Return the name if it is a safe SQL identifier, otherwise raise ValueError."""
    if not isinstance(name, str) or not _IDENTIFIER_PATTERN.fullmatch(name):
        raise ValueError(f"Invalid identifier: {name!r}. Use only letters, digits and '_'.")
    return name


def table_name(catalog: str, schema: str, table: str) -> str:
    """Build a fully qualified, quoted table name: `catalog`.`schema`.`table`."""
    return ".".join(f"`{validate_identifier(part)}`" for part in (catalog, schema, table))


def get_raw_orders(spark: SparkSession) -> DataFrame:
    """Bronze source data."""
    return spark.createDataFrame(SAMPLE_ORDERS, schema=RAW_ORDERS_SCHEMA)


def clean_orders(raw_df: DataFrame) -> DataFrame:
    """Silver layer: remove bad/duplicate rows, standardize text, add amount column."""
    return (
        raw_df
        .dropna(subset=["order_id", "customer_id", "quantity", "unit_price"])
        .filter((F.col("quantity") > 0) & (F.col("unit_price") > 0))
        .dropDuplicates(["order_id"])
        .select(
            F.col("order_id"),
            F.to_date(F.col("order_date"), "yyyy-MM-dd").alias("order_date"),
            F.col("customer_id"),
            F.initcap(F.trim(F.col("region"))).alias("region"),
            F.trim(F.col("product")).alias("product"),
            F.col("quantity"),
            F.col("unit_price"),
            F.round(F.col("quantity") * F.col("unit_price"), 2).alias("amount"),
        )
    )


def aggregate_sales(silver_df: DataFrame) -> DataFrame:
    """Gold layer: revenue summary per region and product."""
    return (
        silver_df
        .groupBy("region", "product")
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.sum("quantity").alias("total_quantity"),
            F.round(F.sum("amount"), 2).alias("total_revenue"),
        )
        .orderBy("region", "product")
    )


def find_quality_issues(silver_df: DataFrame) -> list:
    """Return a list of data quality problems (empty list = data is good)."""
    issues = []

    null_ids = silver_df.filter(F.col("order_id").isNull()).count()
    if null_ids:
        issues.append(f"{null_ids} row(s) have a null order_id")

    non_positive = silver_df.filter(F.col("amount") <= 0).count()
    if non_positive:
        issues.append(f"{non_positive} row(s) have amount <= 0")

    duplicates = silver_df.count() - silver_df.dropDuplicates(["order_id"]).count()
    if duplicates:
        issues.append(f"{duplicates} duplicate order_id value(s)")

    return issues
