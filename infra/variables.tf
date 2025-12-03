variable "project_id" {
  description = "GCP Project ID"
  type        = string
  default     = "secure-cipher-475203-k2"
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "bucket_name" {
  description = "GCS Bucket name for medallion architecture"
  type        = string
  default     = "iowa-liquor-medallion-ml"
}

variable "repository_id" {
  description = "Artifact Registry repository ID"
  type        = string
  default     = "iowa-liquor-ml"
}

variable "job_name" {
  description = "Cloud Run job name"
  type        = string
  default     = "bronze-extract-job"
}

variable "cluster_name" {
  description = "Dataproc cluster name"
  type        = string
}

variable "master_machine_type" {
  description = "Master node machine type"
  type        = string
}

variable "worker_machine_type" {
  description = "Worker node machine type"
  type        = string
}

variable "num_workers" {
  description = "Number of worker nodes"
  type        = number
}

