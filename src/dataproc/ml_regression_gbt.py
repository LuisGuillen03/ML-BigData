"""ML Regression Model - PySpark with Gradient Boosted Trees
Trains GBT model on Gold layer to predict sale_dollars
More complex model for performance comparison
"""

import sys
import time
import json
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.ml.evaluation import RegressionEvaluator

CLUSTER_NAME = sys.argv[1] if len(sys.argv) > 1 else "iowa-cluster-n1-std-3w"
BUCKET = "iowa-liquor-medallion-ml"
GOLD_PATH = f"gs://{BUCKET}/gold_{CLUSTER_NAME}/iowa_sales"

job_start = time.time()
timings = {}

# Initialize Spark with memory optimizations
stage_start = time.time()
spark = (
    SparkSession.builder.appName(f"MLRegression-GBT-{CLUSTER_NAME}")
    .config("spark.sql.shuffle.partitions", "60")
    .config("spark.sql.autoBroadcastJoinThreshold", "-1")
    .getOrCreate()
)
timings["spark_initialization"] = f"{time.time() - stage_start:.2f}s"

# Read Gold layer with year filter (2022+) - GBT is more expensive
stage_start = time.time()
# Read Gold layer - Filter based on DATA_MODE
DATA_MODE = sys.argv[2] if len(sys.argv) > 2 else "subset"

stage_start = time.time()
df = spark.read.parquet(GOLD_PATH)

if DATA_MODE == "subset":
    # 30% of data (approx based on year)
    df = df.filter(F.col("year") >= 2022)
    print("Running in SUBSET mode: Filtering for year >= 2022 (~30% data)")
else:
    # Full dataset
    print("Running in FULL mode: Using 100% of data")

# Coalesce based on size estimate
partitions = 50 if DATA_MODE == "subset" else 200
df = df.coalesce(partitions)
df = df.coalesce(50)
timings["read_gold_data"] = f"{time.time() - stage_start:.2f}s"
print(f"Data loaded with year >= 2022 filter, coalesced to 50 partitions")

# Prepare features - same as simple version
stage_start = time.time()
feature_cols = [
    "bottles_sold",
    "volume_sold_liters",
    "day_of_week",
    "quarter",
    "is_weekend",
    "price_per_bottle",
    "volume_per_bottle",
]

# Assemble features
assembler = VectorAssembler(
    inputCols=feature_cols, outputCol="features", handleInvalid="skip"
)
df_features = assembler.transform(df).select("features", "sale_dollars")

# Split data (80/20)
train_df, test_df = df_features.randomSplit([0.8, 0.2], seed=42)
timings["feature_preparation"] = f"{time.time() - stage_start:.2f}s"
print(f"Train/test split completed (80/20)")

# Train Gradient Boosted Trees model
stage_start = time.time()
print("Starting Gradient Boosted Trees training...")
gbt = GBTRegressor(
    featuresCol="features",
    labelCol="sale_dollars",
    maxIter=20,  # Number of trees
    maxDepth=5,  # Tree depth
    stepSize=0.1,  # Learning rate
    subsamplingRate=0.8,  # Sample 80% for each tree
    seed=42,
)
model = gbt.fit(train_df)
timings["model_training"] = f"{time.time() - stage_start:.2f}s"
print(f"GBT model trained in {timings['model_training']}")

# Evaluate model
stage_start = time.time()
print("Generating predictions...")
predictions = model.transform(test_df)

evaluator_r2 = RegressionEvaluator(
    labelCol="sale_dollars", predictionCol="prediction", metricName="r2"
)
evaluator_rmse = RegressionEvaluator(
    labelCol="sale_dollars", predictionCol="prediction", metricName="rmse"
)
evaluator_mae = RegressionEvaluator(
    labelCol="sale_dollars", predictionCol="prediction", metricName="mae"
)

r2 = evaluator_r2.evaluate(predictions)
rmse = evaluator_rmse.evaluate(predictions)
mae = evaluator_mae.evaluate(predictions)

timings["model_evaluation"] = f"{time.time() - stage_start:.2f}s"
print(f"Model Metrics - R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

# Get counts AFTER training
train_count = train_df.count()
test_count = test_df.count()
print(f"Train records: {train_count}, Test records: {test_count}")

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
            "train_records": train_count,
            "test_records": test_count,
            "features_used": feature_cols,
            "year_filter": "year >= 2022" if DATA_MODE == "subset" else "none",
            "data_percentage": "~30%" if DATA_MODE == "subset" else "100%",
        },
        "model_metrics": {
            "r2_score": float(r2),
            "rmse": float(rmse),
            "mae": float(mae),
            "model_type": "Gradient Boosted Trees",
            "max_iterations": 20,
            "max_depth": 5,
            "step_size": 0.1,
            "subsampling_rate": 0.8,
        },
    }
}

# Save timing to GCS
timing_json = json.dumps(timing_data, indent=2)
output_path = f"gs://{BUCKET}/job_timing_ml_gbt_{CLUSTER_NAME}_{DATA_MODE}.json"
temp_path = f"gs://{BUCKET}/job_timing_ml_gbt_{CLUSTER_NAME}_{DATA_MODE}_temp"

spark.sparkContext.parallelize([timing_json]).coalesce(1).saveAsTextFile(temp_path)

from subprocess import call

call(["gsutil", "cp", f"{temp_path}/part-00000", output_path])
call(["gsutil", "rm", "-r", temp_path])

print(f"✓ GBT model metrics saved to {output_path}")
spark.stop()
