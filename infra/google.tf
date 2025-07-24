locals {
  gcp_region = "us-central1"
}

variable "google_project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "mcp-tutorial-1371337"
}

# Google Cloud Provider Configuration
provider "google" {
  project     = var.google_project_id
  credentials = file("../gcp-service-creds.json")
  region      = local.gcp_region
  zone        = "${local.gcp_region}-a"
}

# Reserve a public IP address
resource "google_compute_address" "public" {
  name         = "public-ip"
  network_tier = "STANDARD"
  address_type = "EXTERNAL"
}

resource "google_service_account" "mcp_server" {
  account_id   = "gcr-pull-sa"
  display_name = "Service Account for pulling images from GCR"
}

resource "google_project_iam_member" "registry_access" {
  project = var.google_project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.mcp_server.email}"
}

# Create a GCE instance with cloud-init on COS
resource "google_compute_instance" "mcp_server" {
  name         = "mcp-server"
  machine_type = "e2-micro"
  depends_on   = [time_sleep.dns_propagation]

  boot_disk {
    initialize_params {
      image = "cos-cloud/cos-stable"
    }
  }

  metadata = {
    google-logging-enabled    = "true"
    google-monitoring-enabled = "true"
    user-data                = templatefile("${path.module}/cloud-init.yml", {
      google_project_id = var.google_project_id
    })
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip                 = google_compute_address.public.address
      network_tier           = "STANDARD"
      public_ptr_domain_name = local.mcp_domain
    }
  }

  service_account {
    email  = google_service_account.mcp_server.email
    scopes = ["cloud-platform"]
  }
  tags = ["mcp-server"]
}

resource "google_compute_firewall" "mcp_server_https" {
  name    = "mcp-server-https"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  direction     = "INGRESS"
  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["mcp-server"]
  description   = "Allow HTTPS traffic to MCP server on port 443"
}
