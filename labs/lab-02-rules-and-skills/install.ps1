$ErrorActionPreference = "Stop"
$LabDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RootDir = Resolve-Path (Join-Path $LabDir "..\..")
Set-Location $RootDir

Write-Host "[Lab 02 Setup] Ensuring Lab 01 prerequisites and solutions are applied..."
& "$RootDir\labs\lab-01-revenue-sla-triage\install.ps1"
Copy-Item "$RootDir\labs\lab-01-revenue-sla-triage\solution\cdr_rating.py" "$RootDir\src\services\cdr_rating.py" -Force
Copy-Item "$RootDir\labs\lab-01-revenue-sla-triage\solution\sla_monitor.py" "$RootDir\src\services\sla_monitor.py" -Force
Write-Host "[Lab 02 Ready] Ready to author GEMINI.md, .agents/rules/telecom-standards.md, and .agents/skills/sla-revenue-audit/SKILL.md."
