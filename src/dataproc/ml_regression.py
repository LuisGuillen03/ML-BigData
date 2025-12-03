"""ML Regression Model - PySpark
Trains Linear Regression model on Gold layer to predict sale_dollars
"""

import sys
import time
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

CLUSTER_NAME = sys.argv[1] if len(sys.argv) > 1 else "iowa-cluster-n1-std-3w"
BUCKET = "iowa-liquor-medallion-ml"
GOLD_PATH = f"gs://{BUCKET}/gold_{CLUSTER_NAME}/iowa_sales"

job_start = time.time()
timings = {}

# Initialize Spark
stage_start = time.time()
spark = SparkSession.builder.appName(f"MLRegression-{CLUSTER_NAME}").getOrCreate()
timings["spark_initialization"] = f"{time.time() - stage_start:.2f}s"

# Read Gold layer
stage_start = time.time()
df = spark.read.parquet(GOLD_PATH)
records_read = df.count()
timings["read_gold_data"] = f"{time.time() - stage_start:.2f}s"
print(f"Gold records: {records_read}")

# Prepare features
stage_start = time.time()
feature_cols = [
    "bottles_sold",
    "volume_sold_liters",
    "day_of_week",
    "quarter",
    "is_weekend",
    "price_per_bottle",
    "volume_per_bottle"
]

# Assemble features
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
df_features = assembler.transform(df).select("features", "sale_dollars")

# Split data (80/20)
train_df, test_df = df_features.randomSplit([0.8, 0.2], seed=42)
train_count = train_df.count()
test_count = test_df.count()
timings["feature_preparation"] = f"{time.time() - stage_start:.2f}s"
print(f"Train: {train_count}, Test: {test_count}")

# Train model
stage_start = time.time()
lr = LinearRegression(featuresCol="features", labelCol="sale_dollars", maxIter=10)
model = lr.fit(train_df)
timings["model_training"] = f"{time.time() - stage_start:.2f}s"
print(f"Model trained")

# Evaluate model
stage_start = time.time()
predictions = model.transform(test_df)

evaluator_r2 = RegressionEvaluator(labelCol="sale_dollars", predictionCol="prediction", metricName="r2")
evaluator_rmse = RegressionEvaluator(labelCol="sale_dollars", predictionCol="prediction", metricName="rmse")
evaluator_mae = RegressionEvaluator(labelCol="sale_dollars", predictionCol="prediction", metricName="mae")

r2 = evaluator_r2.evaluate(predictions)
rmse = evaluator_rmse.evaluate(predictions)
mae = evaluator_mae.evaluate(predictions)

timings["model_evaluation"] = f"{time.time() - stage_start:.2f}s"
print(f"R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

# Save results
total_time = time.time() - job_start
timing_data = {
    "ml_phase": {
        "cluster_name": CLUSTER_NAME,
        "stages": timings,
        "metadata": {
            "job_completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_time": f"{total_time:.2f}s",
            "total_minutes": f"{total_time/60:.2f}",
            "records_read": records_read,
            "train_records": train_count,
            "test_records": test_count,
            "features_used": feature_cols
        },
        "model_metrics": {
            "r2_score": float(r2),
            "rmse": float(rmse),
            "mae": float(mae),
            "model_type": "Linear Regression",
            "max_iterations": 10
        }
    }
}

# Save timing to GCS
timing_json = json.dumps(timing_data, indent=2)
spark.sparkContext.parallelize([timing_json]).coalesce(1).saveAsTextFile(
    f"gs://{BUCKET}/job_timing_ml_{CLUSTER_NAME}_temp"
)

from subprocess import call
call([
    "gsutil", "cp",
    f"gs://{BUCKET}/job_timing_ml_{CLUSTER_NAME}_temp/part-00000",
    f"gs://{BUCKET}/job_timing_ml_{CLUSTER_NAME}.json"
])
call(["gsutil", "rm", "-r", f"gs://{BUCKET}/job_timing_ml_{CLUSTER_NAME}_temp"])

print(f"✓ Model metrics saved to gs://{BUCKET}/job_timing_ml_{CLUSTER_NAME}.json")
spark.stop()
