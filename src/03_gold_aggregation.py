# Databricks notebook source
# MAGIC %md
# MAGIC # 03 - Gold Aggregation
# MAGIC
# MAGIC Builds the business-ready table `gold_sales_summary`: orders, quantity and revenue
# MAGIC per region and product.

# COMMAND ----------

import os
import sys

sys.path.append(os.getcwd())

from transformations import aggregate_sales, table_name

# COMMAND ----------

dbutils.widgets.text("catalog", "qa_catalog")
dbutils.widgets.text("schema", "sales")

catalog = dbutils.widgets.get("catalog")
schema = dbutils.widgets.get("schema")
silver_table = table_name(catalog, schema, "silver_orders")
gold_table = table_name(catalog, schema, "gold_sales_summary")

# COMMAND ----------

gold_df = aggregate_sales(spark.table(silver_table))

(
    gold_df.write
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable(gold_table)
)

print(f"Wrote {spark.table(gold_table).count()} summary rows to {gold_table}")
display(spark.table(gold_table))
