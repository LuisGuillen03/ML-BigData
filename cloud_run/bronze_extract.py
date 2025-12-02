"""Bronze layer extraction - Cloud Run Job"""

import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get("PROJECT_ID", "secure-cipher-475203-k2")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "iowa-liquor-medallion-ml")


def extract_and_upload():
    bq_client = bigquery.Client(project=PROJECT_ID)

    temp_table = f"{PROJECT_ID}.ml_work.iowa_sales_temp"

    print("Creating temp table...")
    query = f"""
    CREATE OR REPLACE TABLE `{temp_table}`
    AS
    SELECT *
    FROM `bigquery-public-data.iowa_liquor_sales.sales`
    """

    job = bq_client.query(query)
    job.result()
    print(f"✓ Temp table created: {temp_table}")

    destination_uri = f"gs://{BUCKET_NAME}/bronze/iowa_sales/*.parquet"

    print(f"Exporting to {destination_uri}...")

    job_config = bigquery.ExtractJobConfig()
    job_config.destination_format = bigquery.DestinationFormat.PARQUET

    extract_job = bq_client.extract_table(
        temp_table, destination_uri, location="US", job_config=job_config
    )

    extract_job.result()
    print(f"✓ Export complete to gs://{BUCKET_NAME}/bronze/iowa_sales/")

    bq_client.delete_table(temp_table)
    print("✓ Temp table deleted")


if __name__ == "__main__":
    extract_and_upload()
