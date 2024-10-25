resource "google_project" "my_project" {
  name            = var.project_name
  project_id      = var.project_id
  org_id          = var.organization_id
  billing_account = var.billing_account
  folder_id       = var.folder_id
}
