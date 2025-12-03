PROJECT_ID = secure-cipher-475203-k2
REGION = us-central1
BUCKET = iowa-liquor-medallion-ml
CLUSTER = iowa-cluster1
REPO_ID = iowa-liquor-ml

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make help                    - Show this help message"
	@echo "  make infra-init              - Initialize Terraform"
	@echo "  make infra-plan              - Plan infrastructure changes"
	@echo "  make infra-apply             - Apply infrastructure changes"
	@echo "  make infra-destroy           - Destroy infrastructure"
	@echo "  make build-bronze-container  - Build and push bronze Docker image"
	@echo "  make run-bronze-extraction   - Execute bronze extraction job (monthly partitions)"
	@echo "  make upload-gold-script      - Upload gold transform script to GCS"
	@echo "  make run-gold-transform      - Submit gold transform PySpark job"
	@echo "  make cluster-start           - Start Dataproc cluster"
	@echo "  make cluster-stop            - Stop Dataproc cluster"
	@echo "  make cluster-ssh             - SSH into cluster master node"

.PHONY: infra-init
infra-init:
	cd infra && terraform init

.PHONY: infra-plan
infra-plan:
	cd infra && terraform plan

.PHONY: infra-apply
infra-apply:
	cd infra && terraform apply

.PHONY: infra-destroy
infra-destroy:
	cd infra && terraform destroy

.PHONY: build-bronze-container
build-bronze-container:
	cd cloud_run && gcloud builds submit --tag $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_ID)/bronze-extract:latest --project=$(PROJECT_ID) --quiet

.PHONY: run-bronze-extraction
run-bronze-extraction:
	@echo "Running bronze extraction with timing..."
	gcloud run jobs execute bronze-extract-job --region=$(REGION) --project=$(PROJECT_ID)
	@echo "Waiting for timing file..."
	@sleep 10
	@gsutil cat gs://$(BUCKET)/job_timing_bronze.json 2>/dev/null || echo "Timing file not yet available"

.PHONY: upload-gold-script
upload-gold-script:
	gsutil cp dataproc/gold_transform.py gs://$(BUCKET)/scripts/

.PHONY: run-gold-transform
run-gold-transform:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/gold_transform.py \
	  --cluster=$(CLUSTER) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID)

.PHONY: cluster-start
cluster-start:
	gcloud dataproc clusters start $(CLUSTER) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster-stop
cluster-stop:
	gcloud dataproc clusters stop $(CLUSTER) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster-ssh
cluster-ssh:
	gcloud compute ssh $(CLUSTER)-m --zone=$(REGION)-a --project=$(PROJECT_ID)
