terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project     = var.project_id
  region      = var.region
  credentials = file("../credentials.json")
}

module "storage" {
  source      = "./modules/storage"
  project_id  = var.project_id
  bucket_name = var.bucket_name
}

module "artifact_registry" {
  source       = "./modules/artifact_registry"
  project_id   = var.project_id
  region       = var.region
  repository_id = var.repository_id
}

module "cloud_run" {
  source         = "./modules/cloud_run"
  project_id     = var.project_id
  region         = var.region
  job_name       = var.job_name
  image_url      = "${var.region}-docker.pkg.dev/${var.project_id}/${var.repository_id}/bronze-extract:latest"
  bucket_name    = module.storage.bucket_name
  
  depends_on = [module.artifact_registry]
}

module "dataproc" {
  source              = "./modules/dataproc"
  project_id          = var.project_id
  region              = var.region
  cluster_name        = var.cluster_name
  staging_bucket      = module.storage.bucket_name
  master_machine_type = var.master_machine_type
  worker_machine_type = var.worker_machine_type
  num_workers         = var.num_workers
}
