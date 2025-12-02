"""Bronze layer extraction - Cloud Run Job
Exports data partitioned by year/month folders
"""

import os
from google.cloud import bigquery

PROJECT_ID = os.environ.get("PROJECT_ID", "secure-cipher-475203-k2")
BUCKET_NAME = os.environ.get("BUCKET_NAME", "iowa-liquor-medallion-ml")


def extract_and_upload():
    bq_client = bigquery.Client(project=PROJECT_ID)

    query = """
    SELECT DISTINCT 
        EXTRACT(YEAR FROM date) as year,
        EXTRACT(MONTH FROM date) as month
    FROM `bigquery-public-data.iowa_liquor_sales.sales`
    ORDER BY year, month
    """

    months = list(bq_client.query(query).result())
    print(f"Found {len(months)} months to export")

    for row in months:
        year, month = int(row.year), int(row.month)
        destination_uri = f"gs://{BUCKET_NAME}/bronze/iowa_sales/year={year}/month={month:02d}/*.parquet"

        month_query = f"""
        SELECT *
        FROM `bigquery-public-data.iowa_liquor_sales.sales`
        WHERE EXTRACT(YEAR FROM date) = {year}
          AND EXTRACT(MONTH FROM date) = {month}
        """

        job_config = bigquery.QueryJobConfig(
            destination=f"{PROJECT_ID}.ml_work.temp_export_{year}_{month:02d}",
            write_disposition="WRITE_TRUNCATE",
        )

        query_job = bq_client.query(month_query, job_config=job_config)
        query_job.result()

        extract_config = bigquery.ExtractJobConfig(
            destination_format=bigquery.DestinationFormat.PARQUET
        )

        extract_job = bq_client.extract_table(
            f"{PROJECT_ID}.ml_work.temp_export_{year}_{month:02d}",
            destination_uri,
            location="US",
            job_config=extract_config,
        )
        extract_job.result()

        bq_client.delete_table(f"{PROJECT_ID}.ml_work.temp_export_{year}_{month:02d}")
        print(f"✓ Exported {year}-{month:02d}")

    print(f"✓ All {len(months)} months exported")


if __name__ == "__main__":
    extract_and_upload()
