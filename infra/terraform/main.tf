locals {
  required_apis = [
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "aiplatform.googleapis.com",
    "cloudaicompanion.googleapis.com",
    "discoveryengine.googleapis.com",
    "logging.googleapis.com",
  ]
  resolved_image = (
    var.container_image != ""
    ? var.container_image
    : "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.telecom_repo.repository_id}/${var.service_name}:latest"
  )
}

resource "google_project_service" "telecom_apis" {
  for_each           = toset(local.required_apis)
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

resource "google_artifact_registry_repository" "telecom_repo" {
  location      = var.region
  repository_id = "${var.service_name}-repo"
  description   = "Artifact Registry Docker repository for Telecom Nexus OSS/BSS ADK & A2A Service"
  format        = "DOCKER"
  depends_on    = [google_project_service.telecom_apis]
}

resource "google_service_account" "telecom_runtime_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Telecom Nexus ADK & A2A Runtime Service Account"
  description  = "Least-privilege IAM identity for Telecom Nexus Cloud Run, Vertex AI, and Gemini Enterprise"
}

resource "google_project_iam_member" "vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.telecom_runtime_sa.email}"
}

resource "google_project_iam_member" "discovery_engine_viewer" {
  project = var.project_id
  role    = "roles/discoveryengine.viewer"
  member  = "serviceAccount:${google_service_account.telecom_runtime_sa.email}"
}

resource "google_project_iam_member" "log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.telecom_runtime_sa.email}"
}

resource "google_cloud_run_v2_service" "telecom_nexus" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.telecom_runtime_sa.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = local.resolved_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GOOGLE_GENAI_USE_VERTEXAI"
        value = "TRUE"
      }

      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }

      env {
        name  = "GOOGLE_CLOUD_LOCATION"
        value = var.region
      }

      env {
        name  = "GEMINI_ENTERPRISE_APP_ID"
        value = var.gemini_enterprise_app_id
      }

      resources {
        limits = {
          cpu    = "2"
          memory = "1Gi"
        }
      }
    }
  }

  depends_on = [
    google_project_service.telecom_apis,
    google_artifact_registry_repository.telecom_repo,
  ]
}

resource "google_cloud_run_v2_service_iam_member" "public_invoker" {
  count    = var.allow_unauthenticated ? 1 : 0
  project  = google_cloud_run_v2_service.telecom_nexus.project
  location = google_cloud_run_v2_service.telecom_nexus.location
  name     = google_cloud_run_v2_service.telecom_nexus.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
