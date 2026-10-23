output "cloud_run_service_url" {
  description = "Base URL of the deployed Telecom Nexus Cloud Run service"
  value       = google_cloud_run_v2_service.telecom_nexus.uri
}

output "a2a_agent_card_url" {
  description = "A2A Protocol Agent Discovery Card URL (/.well-known/agent.json)"
  value       = "${google_cloud_run_v2_service.telecom_nexus.uri}/.well-known/agent.json"
}

output "a2a_jsonrpc_endpoint" {
  description = "A2A Protocol JSON-RPC 2.0 Task endpoint (/api/v1/a2a)"
  value       = "${google_cloud_run_v2_service.telecom_nexus.uri}/api/v1/a2a"
}

output "gemini_enterprise_agent_registration_command" {
  description = "Command to register the deployed Cloud Run A2A Agent into Gemini Enterprise"
  value       = "./deploy/register_gemini_enterprise_agent.sh --project ${var.project_id} --app-id ${var.gemini_enterprise_app_id} --location ${var.gemini_enterprise_location} --agent-url ${google_cloud_run_v2_service.telecom_nexus.uri}"
}
