# ML Model Implementation Instructions

## Overview
The ML regression model is **REQUIRED** and worth **35/100 points** in the project rubric.

## What's Already Done
✅ ML script template created: `src/dataproc/ml_regression.py`  
✅ Makefile targets added for running the model  
✅ Gold layer data ready with engineered features

## Your Task

### 1. Review the Script
The script at `src/dataproc/ml_regression.py` implements:
- Linear Regression to predict `sale_dollars`
- Features: bottles_sold, volume_sold_liters, day_of_week, quarter, is_weekend, price_per_bottle, volume_per_bottle
- 80/20 train/test split
- Metrics: R², RMSE, MAE

### 2. Run the Model

**Option A: Run on Cluster 1 (if recreated)**
```bash
make infra-apply-c1          # Create cluster 1
make upload-ml-script        # Upload script to GCS
make run-ml-c1              # Run model on cluster 1
```

**Option B: Run on Cluster 2 (if recreated)**
```bash
make infra-apply-c2          # Create cluster 2
make upload-ml-script        # Upload script to GCS
make run-ml-c2              # Run model on cluster 2
```

### 3. Collect Results

After the job completes, download the metrics:
```bash
gsutil cat gs://iowa-liquor-medallion-ml/job_timing_ml_iowa-cluster-n1-std-3w.json
# or
gsutil cat gs://iowa-liquor-medallion-ml/job_timing_ml_iowa-cluster-n2-hm-4w.json
```

### 4. Expected Output

The model will generate:
```json
{
  "ml_phase": {
    "cluster_name": "iowa-cluster-n1-std-3w",
    "model_metrics": {
      "r2_score": 0.xxxx,
      "rmse": xxx.xx,
      "mae": xxx.xx,
      "model_type": "Linear Regression"
    },
    "metadata": {
      "train_records": xxxxxxx,
      "test_records": xxxxxxx,
      "features_used": [...]
    }
  }
}
```

### 5. For the Report

Include in the final PDF:
- **Model description**: Linear Regression to predict sale_dollars
- **Features used**: List the 7 features
- **Metrics**: R², RMSE, MAE values
- **Interpretation**: 
  - R² close to 1.0 = good fit
  - Lower RMSE/MAE = better predictions
- **Cluster comparison**: Did the model train faster on cluster 2?

## Optional Improvements

If you have time:
1. Try different features
2. Add feature importance analysis
3. Compare with Logistic Regression (for classification)
4. Add cross-validation

## Questions?

The script is ready to run as-is. Just:
1. Create a cluster
2. Upload the script
3. Run the job
4. Collect the metrics

Good luck! 🚀
