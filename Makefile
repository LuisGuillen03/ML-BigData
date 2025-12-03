
.PHONY: upload-ml-script
upload-ml-script:
	gsutil cp src/dataproc/ml_regression.py gs://$(BUCKET)/scripts/

.PHONY: run-ml-c1
run-ml-c1:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/ml_regression.py \
	  --cluster=$(CLUSTER1) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID) \
	  --id=ml-c1-$$(date +%Y%m%d-%H%M%S) \
	  -- $(CLUSTER1)

.PHONY: run-ml-c2
run-ml-c2:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/ml_regression.py \
	  --cluster=$(CLUSTER2) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID) \
	  --id=ml-c2-$$(date +%Y%m%d-%H%M%S) \
	  -- $(CLUSTER2)
