resource "google_storage_bucket" "medallion_bucket" {
  name          = var.bucket_name
  location      = "US"
  force_destroy = true

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 90
    }
    action {
      type = "Delete"
    }
  }
}
