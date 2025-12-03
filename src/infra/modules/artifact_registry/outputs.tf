output "repository_name" {
  description = "Artifact Registry repository name"
  value       = google_artifact_registry_repository.docker_repo.name
}

output "repository_id" {
  description = "Artifact Registry repository ID"
  value       = google_artifact_registry_repository.docker_repo.repository_id
}
