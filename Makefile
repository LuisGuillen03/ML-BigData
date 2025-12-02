PROJECT_ID = secure-cipher-475203-k2
REGION = us-central1
BUCKET = iowa-liquor-medallion-ml
CLUSTER = iowa-cluster1
REPO_ID = iowa-liquor-ml

.PHONY: help
help:
	@echo "Available commands:"
	@echo "  make infra-init      - Initialize Terraform"
	@echo "  make infra-plan      - Plan infrastructure changes"
	@echo "  make infra-apply     - Apply infrastructure changes"
	@echo "  make infra-destroy   - Destroy infrastructure"
	@echo "  make docker-build    - Build bronze extract Docker image"
	@echo "  make docker-push     - Push Docker image to Artifact Registry"
	@echo "  make run-bronze      - Execute bronze extraction job"
	@echo "  make upload-silver   - Upload silver transform script to GCS"
	@echo "  make run-silver      - Submit silver transform PySpark job"
	@echo "  make upload-gold     - Upload gold transform script to GCS"
	@echo "  make run-gold        - Submit gold transform PySpark job"
	@echo "  make cluster-ssh     - SSH into cluster master node"

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

.PHONY: docker-build
docker-build:
	cd cloud_run && docker build -t $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_ID)/bronze-extract:latest .

.PHONY: docker-push
docker-push:
	docker push $(REGION)-docker.pkg.dev/$(PROJECT_ID)/$(REPO_ID)/bronze-extract:latest

.PHONY: run-bronze
run-bronze:
	gcloud run jobs execute bronze-extract-job --region=$(REGION) --project=$(PROJECT_ID)

.PHONY: upload-silver
upload-silver:
	gsutil cp dataproc/silver_transform.py gs://$(BUCKET)/scripts/

.PHONY: run-silver
run-silver:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/silver_transform.py \
	  --cluster=$(CLUSTER) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID)

.PHONY: upload-gold
upload-gold:
	gsutil cp dataproc/gold_transform.py gs://$(BUCKET)/scripts/

.PHONY: run-gold
run-gold:
	gcloud dataproc jobs submit pyspark \
	  gs://$(BUCKET)/scripts/gold_transform.py \
	  --cluster=$(CLUSTER) \
	  --region=$(REGION) \
	  --project=$(PROJECT_ID)

.PHONY: cluster-ssh
cluster-ssh:
	gcloud compute ssh $(CLUSTER)-m --zone=$(REGION)-a --project=$(PROJECT_ID)
