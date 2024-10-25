# Input Variables
variable "project_name" {
  description = "The name of the project."
  type        = string
}

variable "project_id" {
  description = "The unique ID of the project."
  type        = string
}

variable "organization_id" {
  description = "The ID of the organization."
  type        = string
}

variable "billing_account" {
  description = "The billing account ID."
  type        = string
}

variable "folder_id" {
  description = "Folder ID under which the project will be created."
  type        = string
  default     = null # Optional
}

variable "region" {
  description = "The region for GCP resources."
  type        = string
  default     = "us-central1"
}

