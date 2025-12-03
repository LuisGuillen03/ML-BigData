"""Bronze layer extraction - Cloud Run Job
Single export with year/month columns for Spark partitioning
"""

import os
import json
import time
from datetime import datetime
from google.cloud import bigquery, storage

PROJECT_ID = os.environ.get("PROJECT_ID", "secure-cipher-475203-k2")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "iowa-liquor-medallion-ml")


def extract_and_upload():
    timings = {}
    job_start = time.time()

    bq_client = bigquery.Client(project=PROJECT_ID)

    stage_start = time.time()
    query = f"""
    SELECT 
        *,
        EXTRACT(YEAR FROM date) as year,
        EXTRACT(MONTH FROM date) as month
    FROM `bigquery-public-data.iowa_liquor_sales.sales`
    """

    temp_table = f"{PROJECT_ID}.ml_work.bronze_temp"
    job_config = bigquery.QueryJobConfig(
        destination=temp_table, write_disposition="WRITE_TRUNCATE"
    )

    print("Creating temp table with year/month columns...")
    query_job = bq_client.query(query, job_config=job_config)
    query_job.result()
    timings["bigquery_temp_table"] = f"{time.time() - stage_start:.2f}s"
    print(f"✓ Temp table created: {temp_table}")

    stage_start = time.time()
    destination_uri = f"gs://{BUCKET_NAME}/bronze/iowa_sales/*.parquet"
    print(f"Exporting to {destination_uri}...")

    extract_config = bigquery.ExtractJobConfig(
        destination_format=bigquery.DestinationFormat.PARQUET
    )

    extract_job = bq_client.extract_table(
        temp_table, destination_uri, location="US", job_config=extract_config
    )

    extract_job.result()
    timings["bigquery_export"] = f"{time.time() - stage_start:.2f}s"
    print(f"✓ Export complete to gs://{BUCKET_NAME}/bronze/iowa_sales/")

    stage_start = time.time()
    bq_client.delete_table(temp_table)
    timings["cleanup"] = f"{time.time() - stage_start:.2f}s"
    print("✓ Temp table deleted")

    total_time = time.time() - job_start
    timing_data = {
        "bronze_phase": {
            "stages": timings,
            "metadata": {
                "job_completed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_time": f"{total_time:.2f}s",
                "total_minutes": f"{total_time/60:.2f}",
            },
        }
    }

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob("job_timing_bronze.json")
    blob.upload_from_string(json.dumps(timing_data, indent=2))
    print(f"✓ Timing saved to gs://{BUCKET_NAME}/job_timing_bronze.json")


if __name__ == "__main__":
    extract_and_upload()
