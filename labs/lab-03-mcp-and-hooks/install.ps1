$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $LabDir "..\..")
Set-Location $RootDir

Write-Host "[Lab 03 Setup] Ensuring Labs 01 & 02 prerequisites and solutions are applied..."
& "$RootDir\labs\lab-02-rules-and-skills\install.ps1"
New-Item -ItemType Directory -Force -Path "$RootDir\.agents\rules" | Out-Null
New-Item -ItemType Directory -Force -Path "$RootDir\.agents\skills\sla-revenue-audit" | Out-Null
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\GEMINI.md" "$RootDir\GEMINI.md" -Force
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\telecom-standards.md" "$RootDir\.agents\rules\telecom-standards.md" -Force
Copy-Item "$RootDir\labs\lab-02-rules-and-skills\solution\SKILL.md" "$RootDir\.agents\skills\sla-revenue-audit\SKILL.md" -Force
Write-Host "[Lab 03 Ready] Ready to complete mcp_server/telecom_mcp.py, .agents/mcp_config.json, and .agents/hooks.json."
