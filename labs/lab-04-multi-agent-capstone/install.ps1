$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $LabDir "..\..")
Set-Location $RootDir

Write-Host "[Lab 04 Setup] Ensuring Labs 01, 02 & 03 prerequisites and solutions are applied..."
& "$RootDir\labs\lab-03-mcp-and-hooks\install.ps1"
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\telecom_mcp.py" "$RootDir\mcp_server\telecom_mcp.py" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\mcp_config.json" "$RootDir\.agents\mcp_config.json" -Force
Copy-Item "$RootDir\labs\lab-03-mcp-and-hooks\solution\hooks.json" "$RootDir\.agents\hooks.json" -Force
Copy-Item "$LabDir\starter\order_feasibility.py" "$RootDir\src\services\order_feasibility.py" -Force
Copy-Item "$LabDir\starter\adk_a2a_orchestrator.py" "$RootDir\src\agents\adk_a2a_orchestrator.py" -Force
Write-Host "[Lab 04 Ready] Ready to build the Multi-Agent Capstone in src/services/order_feasibility.py and src/agents/adk_a2a_orchestrator.py."
