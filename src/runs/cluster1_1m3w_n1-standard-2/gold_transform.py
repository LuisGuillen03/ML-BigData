"""Gold layer transformation - PySpark
Reads bronze, cleans, engineers features, writes with year/month partitions
"""

import time
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

BUCKET = "iowa-liquor-medallion-ml"
BRONZE_PATH = f"gs://{BUCKET}/bronze/iowa_sales"
GOLD_PATH = f"gs://{BUCKET}/gold/iowa_sales"

job_start = time.time()
timings = {}

stage_start = time.time()
spark = SparkSession.builder.appName("GoldTransform").getOrCreate()
timings["spark_initialization"] = f"{time.time() - stage_start:.2f}s"

stage_start = time.time()
df = spark.read.parquet(BRONZE_PATH)
records_read = df.count()
timings["read_bronze_data"] = f"{time.time() - stage_start:.2f}s"
print(f"Bronze records: {records_read}")

stage_start = time.time()
df_clean = df.filter(
    (F.col("sale_dollars").isNotNull())
    & (F.col("sale_dollars") > 0)
    & (F.col("bottles_sold").isNotNull())
    & (F.col("bottles_sold") > 0)
    & (F.col("volume_sold_liters").isNotNull())
    & (F.col("volume_sold_liters") > 0)
).dropDuplicates()

records_cleaned = df_clean.count()
timings["data_cleaning"] = f"{time.time() - stage_start:.2f}s"
print(f"After cleaning: {records_cleaned}")

stage_start = time.time()
df_features = (
    df_clean.withColumn("day_of_week", F.dayofweek("date"))
    .withColumn("quarter", F.quarter("date"))
    .withColumn("is_weekend", F.when(F.dayofweek("date").isin([1, 7]), 1).otherwise(0))
    .withColumn("price_per_bottle", F.col("sale_dollars") / F.col("bottles_sold"))
    .withColumn(
        "volume_per_bottle", F.col("volume_sold_liters") / F.col("bottles_sold")
    )
)

records_final = df_features.count()
timings["feature_engineering"] = f"{time.time() - stage_start:.2f}s"
print(f"Features engineered: {records_final}")

stage_start = time.time()
df_features.write.mode("overwrite").partitionBy("year", "month").parquet(GOLD_PATH)
timings["write_to_gold_partitioned"] = f"{time.time() - stage_start:.2f}s"
print(f"✓ Gold layer written to {GOLD_PATH}")

total_time = time.time() - job_start
timing_data = {
    "gold_phase": {
        "stages": timings,
        "metadata": {
            "job_completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": f"{total_time:.2f}s",
            "total_minutes": f"{total_time/60:.2f}",
            "records_read": records_read,
            "records_cleaned": records_cleaned,
            "records_removed": records_read - records_cleaned,
            "removal_percentage": f"{((records_read - records_cleaned) / records_read * 100):.2f}%",
            "features_added": [
                "day_of_week",
                "quarter",
                "is_weekend",
                "price_per_bottle",
                "volume_per_bottle",
            ],
        },
    }
}

timing_json = json.dumps(timing_data, indent=2)
spark.sparkContext.parallelize([timing_json]).coalesce(1).saveAsTextFile(
    f"gs://{BUCKET}/job_timing_gold_temp"
)
from subprocess import call

call(
    [
        "gsutil",
        "cp",
        f"gs://{BUCKET}/job_timing_gold_temp/part-00000",
        f"gs://{BUCKET}/job_timing_gold.json",
    ]
)
call(["gsutil", "rm", "-r", f"gs://{BUCKET}/job_timing_gold_temp"])

print(f"✓ Timing saved to gs://{BUCKET}/job_timing_gold.json")
spark.stop()
