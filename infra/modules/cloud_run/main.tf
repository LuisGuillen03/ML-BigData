resource "google_cloud_run_v2_job" "bronze_extract" {
  name     = var.job_name
  location = var.region
  project  = var.project_id

  template {
    template {
      containers {
        image = var.image_url
        
        resources {
          limits = {
            memory = "8Gi"
            cpu    = "4"
          }
        }
        
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        
        env {
          name  = "BUCKET_NAME"
          value = var.bucket_name
        }
      }
      
      timeout = "3600s"
    }
  }
}
