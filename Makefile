PROJECT_ID = secure-cipher-475203-k2
REGION = us-central1
BUCKET = iowa-liquor-medallion-ml
REPO_ID = iowa-liquor-ml
CLUSTER1 = iowa-cluster-n1-std-3w
CLUSTER2 = iowa-cluster-n2-hm-4w

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make help                    - Show this help message"
	@echo ""
	@echo "Infrastructure:"
	@echo "  make infra-init              - Initialize Terraform"
	@echo "  make infra-plan-c1           - Plan cluster1 (1m+3w n1-standard-2)"
	@echo "  make infra-plan-c2           - Plan cluster2 (1m+4w n2-highmem)"
	@echo "  make infra-apply-c1          - Apply cluster1 configuration"
	@echo "  make infra-apply-c2          - Apply cluster2 configuration"
	@echo "  make infra-destroy           - Destroy infrastructure"
	@echo ""
	@echo "Bronze Layer:"
	@echo "  make build-bronze-container  - Build and push bronze Docker image"
	@echo "  make run-bronze-extraction   - Execute bronze extraction job"
	@echo ""
	@echo "Gold Layer - Cluster 1:"
	@echo "  make upload-gold-script      - Upload gold transform script to GCS"
	@echo "  make run-gold-c1             - Run gold transform on cluster1"
	@echo "  make cluster1-start          - Start cluster1"
	@echo "  make cluster1-stop           - Stop cluster1"
	@echo "  make cluster1-ssh            - SSH into cluster1"
	@echo ""
	@echo "Gold Layer - Cluster 2:"
	@echo "  make run-gold-c2             - Run gold transform on cluster2"
	@echo "  make cluster2-start          - Start cluster2"
	@echo "  make cluster2-stop           - Stop cluster2"
	@echo "  make cluster2-ssh            - SSH into cluster2"

.PHONY: infra-init
infra-init:
	cd infra && terraform init

.PHONY: infra-plan-c1
infra-plan-c1:
	cd infra && terraform plan -var-file=cluster1.tfvars

.PHONY: infra-plan-c2
infra-plan-c2:
	cd infra && terraform plan -var-file=cluster2.tfvars

.PHONY: infra-apply-c1
infra-apply-c1:
	cd infra && terraform apply -var-file=cluster1.tfvars

.PHONY: infra-apply-c2
infra-apply-c2:
	cd infra && terraform apply -var-file=cluster2.tfvars

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

.PHONY: run-gold-c1
run-gold-c1:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/gold_transform.py \
	  --cluster=$(CLUSTER1) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID) \
	  --id=gold-c1-$$(date +%Y%m%d-%H%M%S) \
	  -- $(CLUSTER1)

.PHONY: run-gold-c2
run-gold-c2:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/gold_transform.py \
	  --cluster=$(CLUSTER2) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID) \
	  --id=gold-c2-$$(date +%Y%m%d-%H%M%S) \
	  -- $(CLUSTER2)

.PHONY: cluster1-start
cluster1-start:
	gcloud dataproc clusters start $(CLUSTER1) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster1-stop
cluster1-stop:
	gcloud dataproc clusters stop $(CLUSTER1) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster1-ssh
cluster1-ssh:
	gcloud compute ssh $(CLUSTER1)-m --zone=$(REGION)-a --project=$(PROJECT_ID)

.PHONY: cluster2-start
cluster2-start:
	gcloud dataproc clusters start $(CLUSTER2) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster2-stop
cluster2-stop:
	gcloud dataproc clusters stop $(CLUSTER2) --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: cluster2-ssh
cluster2-ssh:
	gcloud compute ssh $(CLUSTER2)-m --zone=$(REGION)-a --project=$(PROJECT_ID)
