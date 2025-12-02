variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "cluster_name" {
  description = "Dataproc cluster name"
  type        = string
}

variable "staging_bucket" {
  description = "Staging bucket for Dataproc"
  type        = string
}

variable "master_machine_type" {
  description = "Master node machine type"
  type        = string
  default     = "n1-standard-2"
}

variable "worker_machine_type" {
  description = "Worker node machine type"
  type        = string
  default     = "n1-standard-2"
}

variable "num_workers" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}
