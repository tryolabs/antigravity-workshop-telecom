variable "project_id" {
  description = "Google Cloud Project ID for Telecom Nexus OSS/BSS Platform"
  type        = string
}

variable "region" {
  description = "Google Cloud region for Cloud Run and Artifact Registry"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Cloud Run service name for Telecom Nexus API, ADK & A2A Orchestrator"
  type        = string
  default     = "telecom-nexus-oss-bss"
}

variable "container_image" {
  description = "Full container image URI in Artifact Registry"
  type        = string
  default     = ""
}

variable "gemini_enterprise_app_id" {
  description = "Gemini Enterprise (Discovery Engine) App/Engine ID for A2A Agent registration"
  type        = string
  default     = "telecom-nexus-enterprise-app"
}

variable "gemini_enterprise_location" {
  description = "Gemini Enterprise location (global, us, eu)"
  type        = string
  default     = "global"
}

variable "allow_unauthenticated" {
  description = "Whether to allow public unauthenticated access for workshop demo purposes"
  type        = bool
  default     = false
}
