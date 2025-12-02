output "job_name" {
  description = "Cloud Run job name"
  value       = google_cloud_run_v2_job.bronze_extract.name
}

output "job_id" {
  description = "Cloud Run job ID"
  value       = google_cloud_run_v2_job.bronze_extract.id
}
