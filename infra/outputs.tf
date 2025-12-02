output "bucket_name" {
  description = "GCS bucket name"
  value       = module.storage.bucket_name
}

output "bucket_url" {
  description = "GCS bucket URL"
  value       = module.storage.bucket_url
}

output "repository_name" {
  description = "Artifact Registry repository name"
  value       = module.artifact_registry.repository_name
}

output "cloud_run_job_name" {
  description = "Cloud Run job name"
  value       = module.cloud_run.job_name
}

output "dataproc_cluster1_name" {
  description = "Dataproc Cluster 1 name"
  value       = module.dataproc_cluster1.cluster_name
}
