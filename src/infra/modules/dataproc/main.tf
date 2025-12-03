resource "google_dataproc_cluster" "silver_cluster" {
  name   = var.cluster_name
  region = var.region

  cluster_config {
    staging_bucket = var.staging_bucket

    endpoint_config {
      enable_http_port_access = true
    }

    master_config {
      num_instances = 1
      machine_type  = var.master_machine_type
      disk_config {
        boot_disk_size_gb = 100
      }
    }

    worker_config {
      num_instances = var.num_workers
      machine_type  = var.worker_machine_type
      disk_config {
        boot_disk_size_gb = 100
      }
    }

    software_config {
      image_version = "2.2-debian12"
      optional_components = ["JUPYTER"]
    }

    gce_cluster_config {
      metadata = {
        "enable-oslogin" = "true"
      }
    }
  }
}
