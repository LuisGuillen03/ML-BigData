"""
Silver Layer Transformation - Data Cleaning and Partitioning
Cluster 1: 1 master (n1-standard-2) + 2 workers (n1-standard-2)
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, year, month, dayofmonth
import time

start_time = time.time()
print(f"[METRIC] Job started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

spark = SparkSession.builder.appName("Iowa-Silver-Cluster1").getOrCreate()

BRONZE_PATH = "gs://iowa-liquor-medallion-ml/bronze/iowa_sales/*.parquet"
SILVER_PATH = "gs://iowa-liquor-medallion-ml/silver/iowa_sales"

print(f"[METRIC] Spark initialized at: {time.time() - start_time:.2f}s")

read_start = time.time()
df = spark.read.parquet(BRONZE_PATH)
initial_count = df.count()
print(f"[METRIC] Read {initial_count} records in {time.time() - read_start:.2f}s")

clean_start = time.time()
df_clean = df.filter(
    col("date").isNotNull()
    & col("store_number").isNotNull()
    & col("sale_dollars").isNotNull()
)
df_clean = df_clean.filter(col("sale_dollars") >= 0)
df_clean = df_clean.dropDuplicates()

final_count = df_clean.count()
print(
    f"[METRIC] Cleaned data: {initial_count} -> {final_count} records in {time.time() - clean_start:.2f}s"
)
print(
    f"[METRIC] Removed {initial_count - final_count} records ({((initial_count - final_count) / initial_count * 100):.2f}%)"
)

write_start = time.time()
df_clean.write.mode("overwrite").partitionBy("date").parquet(SILVER_PATH)

print(f"[METRIC] Write completed in {time.time() - write_start:.2f}s")

total_time = time.time() - start_time
print(f"[METRIC] Total job time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
print(f"[METRIC] Job completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

spark.stop()
