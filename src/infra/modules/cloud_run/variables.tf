variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "job_name" {
  description = "Cloud Run job name"
  type        = string
}

variable "image_url" {
  description = "Docker image URL"
  type        = string
}

variable "bucket_name" {
  description = "GCS bucket name"
  type        = string
}
