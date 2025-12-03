"""
EDA rapido sobre secure-cipher-475203-k2.ml_work.iowa_sales
Requisitos: pip install google-cloud-bigquery pandas pyarrow db-dtypes
Coloca credentials.json en el directorio actual (se ignora en git) o apunta la
variable GOOGLE_APPLICATION_CREDENTIALS a tu ruta de credenciales.
"""

import os
import pathlib

import pandas as pd
from google.cloud import bigquery

# Usa credenciales locales por defecto (ruta relativa)
default_creds = pathlib.Path(__file__).parent / "credentials.json"
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", str(default_creds.resolve()))

client = bigquery.Client(project="secure-cipher-475203-k2")
table = "`secure-cipher-475203-k2.ml_work.iowa_sales`"

# 1) Conteo y rango de fechas
q_meta = f"""
SELECT
  COUNT(*) AS row_count,
  MIN(date) AS min_date,
  MAX(date) AS max_date
FROM {table}
"""
meta = client.query(q_meta).to_dataframe()
print("\nMeta:")
print(meta)

# 2) Cardinalidades clave
q_card = f"""
SELECT
  COUNT(DISTINCT store_number) AS stores,
  COUNT(DISTINCT city) AS cities,
  COUNT(DISTINCT item_number) AS items,
  COUNT(DISTINCT category) AS categories
FROM {table}
"""
card = client.query(q_card).to_dataframe()
print("\nCardinalidades:")
print(card)

# 3) Cuantiles de sale_dollars (p50, p90, p99) y nulos básicos
q_quants = f"""
SELECT
  APPROX_QUANTILES(sale_dollars, 100)[OFFSET(50)] AS p50,
  APPROX_QUANTILES(sale_dollars, 100)[OFFSET(90)] AS p90,
  APPROX_QUANTILES(sale_dollars, 100)[OFFSET(99)] AS p99,
  SUM(IF(sale_dollars IS NULL,1,0)) AS sale_nulls,
  SUM(IF(category IS NULL,1,0)) AS cat_nulls,
  SUM(IF(city IS NULL,1,0)) AS city_nulls
FROM {table}
"""
quants = client.query(q_quants).to_dataframe()
print("\nCuantiles / nulos:")
print(quants)

# 4) Top categorías por venta
q_top_cat = f"""
SELECT
  category,
  SUM(sale_dollars) AS sales,
  COUNT(*) AS tx
FROM {table}
GROUP BY category
ORDER BY sales DESC
LIMIT 10
"""
top_cat = client.query(q_top_cat).to_dataframe()
print("\nTop 10 categorías por venta:")
print(top_cat)

# 5) Sample de filas para inspección
sample = client.query(
    f"SELECT date, store_number, city, category, item_number, sale_dollars, bottles_sold "
    f"FROM {table} TABLESAMPLE SYSTEM (0.001) LIMIT 5"
).to_dataframe()
print("\nMuestra de filas:")
print(sample)
