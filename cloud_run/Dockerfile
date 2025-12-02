FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir google-cloud-bigquery google-cloud-storage pandas pyarrow db-dtypes

COPY bronze_extract.py .

CMD ["python", "bronze_extract.py"]
