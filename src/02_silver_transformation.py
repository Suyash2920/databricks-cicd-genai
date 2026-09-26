# Databricks notebook source
# MAGIC %md
# MAGIC # 02 - Silver Transformation
# MAGIC
# MAGIC Cleans the bronze data:
# MAGIC - removes rows with missing keys, negative quantity or price
# MAGIC - removes duplicate orders
# MAGIC - standardizes text and calculates `amount = quantity * unit_price`

# COMMAND ----------

import os
import sys

sys.path.append(os.getcwd())

from transformations import clean_orders, table_name

# COMMAND ----------

dbutils.widgets.text("catalog", "qa_catalog")
dbutils.widgets.text("schema", "sales")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
bronze_table = table_name(catalog, schema, "bronze_orders")
silver_table = table_name(catalog, schema, "silver_orders")

# COMMAND ----------

silver_df = clean_orders(spark.table(bronze_table))

(
    silver_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(silver_table)
)

print(f"Wrote {spark.table(silver_table).count()} clean rows to {silver_table}")
