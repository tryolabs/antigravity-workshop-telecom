param(
    [switch]$DryRun = $false,
    [string]$ProjectId = "your-telecom-gcp-project-id",
    [string]$Region = "us-central1",
    [string]$ServiceName = "telecom-nexus-oss-bss",
    [string]$GeminiAppId = "telecom-nexus-enterprise-app"
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) "..")
Set-Location $RootDir

$RequiredFiles = @(
    "Dockerfile",
    "infra/terraform/versions.tf",
    "infra/terraform/variables.tf",
    "infra/terraform/main.tf",
    "infra/terraform/outputs.tf",
    "deploy/register_gemini_enterprise_agent.sh"
)

foreach ($f in $RequiredFiles) {
    if (-not (Test-Path (Join-Path $RootDir $f))) {
        throw "Missing required deployment file: $f"
    }
}

if ($DryRun) {
    Write-Host "[PASS] Telecom Nexus GCP + Terraform + Gemini Enterprise Dry-Run validated."
    exit 0
}

$ImageUri = "$Region-docker.pkg.dev/$ProjectId/$ServiceName-repo/${ServiceName}:latest"
gcloud builds submit $RootDir --project $ProjectId --tag $ImageUri
Set-Location (Join-Path $RootDir "infra/terraform")
terraform init
terraform apply -auto-approve `
    -var="project_id=$ProjectId" `
    -var="region=$Region" `
    -var="service_name=$ServiceName" `
    -var="container_image=$ImageUri" `
    -var="gemini_enterprise_app_id=$GeminiAppId"
