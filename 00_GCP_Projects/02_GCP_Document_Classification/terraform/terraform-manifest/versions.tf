# Terraform Block: Settings
terraform {
  required_version = "~> 1.9.6"
  required_providers {
    google = {
      source = "hashicorp/google"
      version = "~> 6.6.0"
    }
  }
}
# Terraform Block: Provider
provider "google" {
  credentials = file("${path.module}/../../secrets/key_access_sql.json")
  project     = var.project_id
  region      = var.region
}
