$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $LabDir "..\..")
Set-Location $RootDir

if (-not (Test-Path ".venv")) {
    & "$RootDir\install.ps1"
}

Write-Host "[Lab 01 Setup] Resetting Telecom Nexus to Lab 01 Starter State..."
Copy-Item "$LabDir\starter\cdr_rating.py" "$RootDir\src\services\cdr_rating.py" -Force
Copy-Item "$LabDir\starter\sla_monitor.py" "$RootDir\src\services\sla_monitor.py" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\starter\telecom_mcp.py" "$RootDir\mcp_server\telecom_mcp.py" -Force
Copy-Item "$RootDir\labs\lab-04-multi-agent-capstone\starter\order_feasibility.py" "$RootDir\src\services\order_feasibility.py" -Force
Copy-Item "$RootDir\labs\lab-04-multi-agent-capstone\starter\adk_a2a_orchestrator.py" "$RootDir\src\agents\adk_a2a_orchestrator.py" -Force

Remove-Item "$RootDir\GEMINI.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\rules\telecom-standards.md" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\skills\sla-revenue-audit" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\mcp_config.json" -ErrorAction SilentlyContinue
Remove-Item "$RootDir\.agents\hooks.json" -ErrorAction SilentlyContinue

.\.venv\Scripts\python data/seed_telecom_data.py
Write-Host "[Lab 01 Ready] Starter bugs active in src/services/cdr_rating.py and src/services/sla_monitor.py."
