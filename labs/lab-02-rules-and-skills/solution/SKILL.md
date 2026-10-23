---
name: sla-revenue-audit
description: >-
  Executes a combined 5G Network Slice SLA compliance and GSMA TAP3 CDR revenue assurance
  audit across OSS (3GPP RAN telemetry and alarms) and BSS (Enterprise B2B contracts),
  generating an executive risk matrix in JSON and Markdown formats. Use this skill when the
  user asks to audit SLA breaches, quantify CDR revenue leakage, or generate an executive
  telecom risk report.
---

# 5G SLA & CDR Revenue Assurance Executive Audit Skill

Use this skill to perform an end-to-end technical (3GPP RAN) and commercial (BSS B2B SLA + TAP3 CDR) risk audit.

## Step-by-Step Procedure

1. **Verify Core Rating & SLA Engines**:
   Ensure the unit tests for CDR rating (`src/services/cdr_rating.py`) and SLA compliance (`src/services/sla_monitor.py`) pass:
   ```bash
   ./.venv/bin/pytest tests/test_lab01_triage.py
   ```

2. **Execute the Combined Audit Helper Script**:
   Run the CLI audit generator [run_sla_audit.py](../../../scripts/run_sla_audit.py):
   ```bash
   ./.venv/bin/python scripts/run_sla_audit.py
   ```

3. **Inspect Generated Artifacts**:
   Read the generated executive reports in `data/exports/`:
   - JSON payload: `data/exports/sla_revenue_audit_report.json`
   - Executive Markdown brief: `data/exports/sla_revenue_audit_report.md`

4. **Validate Output Contract**:
   Confirm that the report includes:
   - `total_cdr_leakage_usd` (`Decimal`-rounded currency)
   - `total_sla_penalty_exposure_usd` (across `ACTIVE` B2B contracts only)
   - `total_combined_commercial_risk_usd`
   - `contract_risk_matrix` sorted by highest commercial risk first, linking each breached contract to its degraded 5G RAN `cell_id` and `primary_tac`.
