"""Gold layer transformation - PySpark
Reads bronze (year=/month= partitions), cleans, engineers features, writes gold
"""

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window

BUCKET = "iowa-liquor-medallion-ml"
BRONZE_PATH = f"gs://{BUCKET}/bronze/iowa_sales"
GOLD_PATH = f"gs://{BUCKET}/gold/iowa_sales"

spark = SparkSession.builder.appName("GoldTransform").getOrCreate()

# Read bronze with partition pruning
df = spark.read.parquet(BRONZE_PATH)

print(f"Bronze records: {df.count()}")

# Data cleaning
df_clean = df.filter(
    (F.col("sale_dollars").isNotNull()) &
    (F.col("sale_dollars") > 0) &
    (F.col("bottles_sold").isNotNull()) &
    (F.col("bottles_sold") > 0) &
    (F.col("volume_sold_liters").isNotNull()) &
    (F.col("volume_sold_liters") > 0)
).dropDuplicates()

print(f"After cleaning: {df_clean.count()}")

# Feature engineering
df_features = df_clean.withColumn("year", F.year("date")) \
    .withColumn("month", F.month("date")) \
    .withColumn("day_of_week", F.dayofweek("date")) \
    .withColumn("quarter", F.quarter("date")) \
    .withColumn("is_weekend", F.when(F.dayofweek("date").isin([1, 7]), 1).otherwise(0)) \
    .withColumn("price_per_bottle", F.col("sale_dollars") / F.col("bottles_sold")) \
    .withColumn("volume_per_bottle", F.col("volume_sold_liters") / F.col("bottles_sold"))

# Aggregations by store
store_window = Window.partitionBy("store_number")
df_features = df_features.withColumn("avg_sale_by_store", F.avg("sale_dollars").over(store_window))

# Aggregations by category
category_window = Window.partitionBy("category_name")
df_features = df_features.withColumn("avg_sale_by_category", F.avg("sale_dollars").over(category_window))

# Aggregations by city
city_window = Window.partitionBy("city")
df_features = df_features.withColumn("avg_sale_by_city", F.avg("sale_dollars").over(city_window))

print(f"Features engineered: {df_features.count()}")

# Write gold with year/month partitioning
df_features.write.mode("overwrite").partitionBy("year", "month").parquet(GOLD_PATH)

print(f"✓ Gold layer written to {GOLD_PATH}")
spark.stop()
