output "cluster_name" {
  description = "Dataproc cluster name"
  value       = google_dataproc_cluster.silver_cluster.name
}

output "cluster_id" {
  description = "Dataproc cluster ID"
  value       = google_dataproc_cluster.silver_cluster.id
}
