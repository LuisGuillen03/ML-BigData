"""Test BigQuery connection and dataset access with credentials.json"""

import os
import pathlib
from google.cloud import bigquery

# Set credentials path
creds_path = pathlib.Path(__file__).parent / "credentials.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(creds_path.resolve())

try:
    # Initialize client
    client = bigquery.Client(project="secure-cipher-475203-k2")
    print(f"✓ Connected to project: {client.project}")
    
    # Test dataset access
    dataset_id = "ml_work"
    dataset = client.get_dataset(dataset_id)
    print(f"✓ Dataset '{dataset_id}' accessible")
    
    # Test table query
    query = "SELECT COUNT(*) as count FROM `secure-cipher-475203-k2.ml_work.iowa_sales` LIMIT 1"
    result = client.query(query).result()
    row = next(result)
    print(f"✓ Table query successful: {row.count} rows in iowa_sales")
    
    print("\n✓ All tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    exit(1)
