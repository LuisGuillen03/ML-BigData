"""
Gold Layer Transformation - Feature Engineering for ML
Target: Predict sale_dollars (regression)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    year,
    month,
    dayofweek,
    quarter,
    when,
    avg,
    count,
    datediff,
    lit,
    min as spark_min,
)
from pyspark.sql.window import Window
import time

start_time = time.time()
print(f"[METRIC] Job started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

spark = SparkSession.builder.appName("Iowa-Gold-Cluster1").getOrCreate()

SILVER_PATH = "gs://iowa-liquor-medallion-ml/silver/iowa_sales"
GOLD_PATH = "gs://iowa-liquor-medallion-ml/gold/iowa_sales"

print(f"[METRIC] Spark initialized at: {time.time() - start_time:.2f}s")
read_start = time.time()
df = spark.read.parquet(SILVER_PATH)
print(f"[METRIC] Read {df.count()} records in {time.time() - read_start:.2f}s")
feat_start = time.time()
df_gold = (
    df.withColumn("year", year(col("date")))
    .withColumn("month", month(col("date")))
    .withColumn("day_of_week", dayofweek(col("date")))
    .withColumn("quarter", quarter(col("date")))
    .withColumn("is_weekend", when(col("day_of_week").isin([1, 7]), 1).otherwise(0))
)

min_date = df.select(spark_min("date")).first()[0]
df_gold = df_gold.withColumn("days_since_start", datediff(col("date"), lit(min_date)))
print(f"[METRIC] Temporal features created in {time.time() - feat_start:.2f}s")
agg_start = time.time()
store_window = Window.partitionBy("store_number")
df_gold = df_gold.withColumn(
    "avg_sales_by_store", avg("sale_dollars").over(store_window)
)
category_window = Window.partitionBy("category")
df_gold = df_gold.withColumn(
    "avg_sales_by_category", avg("sale_dollars").over(category_window)
)
city_window = Window.partitionBy("city")
df_gold = df_gold.withColumn("avg_sales_by_city", avg("sale_dollars").over(city_window))

print(f"[METRIC] Aggregations created in {time.time() - agg_start:.2f}s")

prod_start = time.time()
df_gold = df_gold.withColumn(
    "price_per_bottle",
    when(col("bottles_sold") > 0, col("sale_dollars") / col("bottles_sold")).otherwise(
        0
    ),
)

df_gold = df_gold.withColumn(
    "volume_per_bottle",
    when(
        col("bottles_sold") > 0, col("volume_sold_liters") / col("bottles_sold")
    ).otherwise(0),
)

print(f"[METRIC] Product features created in {time.time() - prod_start:.2f}s")

enc_start = time.time()
top_categories = (
    df_gold.groupBy("category")
    .agg(count("*").alias("cnt"))
    .orderBy(col("cnt").desc())
    .limit(50)
    .select("category")
    .rdd.flatMap(lambda x: x)
    .collect()
)

df_gold = df_gold.withColumn(
    "category_encoded",
    when(col("category").isin(top_categories), col("category")).otherwise("OTHER"),
)

print(f"[METRIC] Encoding completed in {time.time() - enc_start:.2f}s")

select_start = time.time()
df_final = df_gold.select(
    "sale_dollars",
    "year",
    "month",
    "day_of_week",
    "quarter",
    "is_weekend",
    "days_since_start",
    "avg_sales_by_store",
    "avg_sales_by_category",
    "avg_sales_by_city",
    "price_per_bottle",
    "volume_per_bottle",
    "bottles_sold",
    "volume_sold_liters",
    "category_encoded",
    "store_number",
    "city",
    "date",
)

final_count = df_final.count()
print(
    f"[METRIC] Final dataset prepared: {final_count} records in {time.time() - select_start:.2f}s"
)

write_start = time.time()
df_final.write.mode("overwrite").partitionBy("year", "month").parquet(GOLD_PATH)

print(f"[METRIC] Write completed in {time.time() - write_start:.2f}s")

total_time = time.time() - start_time
print(f"[METRIC] Total job time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
print(f"[METRIC] Job completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

spark.stop()
