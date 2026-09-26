# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Bronze Ingestion
# MAGIC
# MAGIC Loads the **raw** sales orders "as-is" into the bronze table and adds an ingestion timestamp.
# MAGIC The source data is built-in (no external storage needed on Databricks Free Edition).

# COMMAND ----------

import os
import sys

sys.path.append(os.getcwd())

from pyspark.sql import functions as F
from transformations import get_raw_orders, table_name

# COMMAND ----------

dbutils.widgets.text("catalog", "qa_catalog")
dbutils.widgets.text("schema", "sales")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
bronze_table = table_name(catalog, schema, "bronze_orders")

# COMMAND ----------

bronze_df = get_raw_orders(spark).withColumn("ingestion_ts", F.current_timestamp())

# Overwrite keeps the demo re-runnable (idempotent) on every deployment.
(
    bronze_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(bronze_table)
)

print(f"Wrote {spark.table(bronze_table).count()} rows to {bronze_table}")
