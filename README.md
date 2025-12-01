# Iowa liquor sales EDA

Contenido:
- `eda_iowa.py`: script CLI que consulta `secure-cipher-475203-k2.ml_work.iowa_sales` y devuelve métricas básicas.
- `eda_iowa.ipynb`: notebook interactivo con las mismas consultas.

Requisitos:
- Python 3.10+.
- Paquetes: `google-cloud-bigquery`, `pandas`, `pyarrow`, `db-dtypes`.
  ```
  pip install google-cloud-bigquery pandas pyarrow db-dtypes
  ```

Credenciales:
- Coloca un `credentials.json` en la raíz del repo o exporta `GOOGLE_APPLICATION_CREDENTIALS` a tu propia ruta. El archivo está ignorado en `.gitignore`.

Uso rápido:
- Script:
  ```
  python eda_iowa.py
  ```
- Notebook:
  Abrir `eda_iowa.ipynb` en Jupyter/VS Code, ejecutar celdas. Ajusta la ruta de credenciales si no usas la ubicación por defecto.
