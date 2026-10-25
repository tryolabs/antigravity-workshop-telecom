<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 03 — Optimized Antigravity Prompts Cheat Sheet (English)

> **Language / Idioma:** [English](./PROMPTS.md) | [Español](./PROMPTS.es.md) • **Lab Guide:** [README.md](./README.md) | [README.es.md](./README.es.md) • **PDF:** [EN](./LAB_03_INSTRUCTIONS_EN.pdf) | [ES](./LAB_03_INSTRUCTIONS_ES.pdf)

> **Goal**: Connect **Google Antigravity** (governed by **Gemini Enterprise** and delivered by **Tryolabs**) to live Telecom OSS/BSS databases via **Model Context Protocol (FastMCP)** and enforce deterministic CPNI/database security via **Lifecycle Hooks (`hooks.json`)**.

---

## 1. Discovery Prompt (`@` Mentions)

```text
@mcp_server/telecom_mcp.py @scripts/audit_hook.py @tests/test_lab03_mcp_hooks.py
Inspect the starter FastMCP server in `mcp_server/telecom_mcp.py`, the compliance hook validator in `scripts/audit_hook.py`, and the test expectations in `tests/test_lab03_mcp_hooks.py`. List the 3 unimplemented MCP tools in `telecom_mcp.py` and the exact schemas required for `.agents/mcp_config.json` and `.agents/hooks.json`.
```

---

## 2. Planning Prompt (`/plan`)

```text
/plan Create an implementation plan for Lab 03 to:
1. Complete `mcp_server/telecom_mcp.py` by implementing:
   - `calculate_contract_penalty_exposure(contract_id: str | None = None)` using `evaluate_contract_sla_compliance()` and `Decimal`.
   - `inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False)` using `rate_cdr_record()` and masking `imsi` (`masked_imsi`) and `msisdn` (`masked_msisdn`) with `***` for CPNI compliance.
   - `evaluate_slice_capacity(target_tac: str, requested_slice_sst: int, requested_bandwidth_mbps: int, max_latency_ms: float)` returning `READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION`, or `REJECTED`.
2. Create `.agents/mcp_config.json` registering `telecom-nexus-mcp` over Stdio (`./.venv/bin/python mcp_server/telecom_mcp.py`).
3. Create `.agents/hooks.json` wiring `PreToolUse` (`matcher: "run_command"`) and `PostToolUse` (`matcher: "run_command|edit_file|write_file"`) to `scripts/audit_hook.py`.
```

---

## 3. Instructive Inline Edit Prompt (`Cmd+I` / `Ctrl+I`)

Open `mcp_server/telecom_mcp.py`, highlight the three stubbed `@mcp.tool()` functions, and press `Cmd+I` / `Ctrl+I`:

```text
Implement `calculate_contract_penalty_exposure`, `inspect_unbilled_cdrs` (masking IMSI and MSISDN with `***` in `masked_imsi` and `masked_msisdn`), and `evaluate_slice_capacity` using `src.services.sla_monitor`, `src.services.cdr_rating`, and `src.database.fetch_all` so all assertions in `tests/test_lab03_mcp_hooks.py` pass.
```

---

## 4. Autonomous Implementation & Verification Prompt

```text
Implement the 3 remaining MCP tools in @mcp_server/telecom_mcp.py, create `.agents/mcp_config.json` and `.agents/hooks.json`, and run `./labs/lab-03-mcp-and-hooks/verify.sh`.
```

---

## 5. Testing Live MCP Tools & Security Hooks Prompt

After `verify.sh` passes, test the MCP tools and the `PreToolUse` safety hook directly from Antigravity Chat:

```text
1. Use our Telecom MCP tools (or call the functions in `mcp_server/telecom_mcp.py`) to inspect `TAC-NY-001` slice `SST=2`, calculate penalty exposure for `CTR-B2B-1002`, and inspect unbilled roaming CDRs with CPNI-masked IMSIs.
2. Test our `PreToolUse` lifecycle hook by simulating a call to `scripts/audit_hook.py --event PreToolUse` with a destructive SQL payload (`DROP TABLE b2b_contracts;`) and show how the hook returns `"decision": "deny"` and logs the event in `data/logs/hook_audit.log`.
```

---

## 6. Power-User & Security Governance Prompts (`/boost`, `/grill-me`, `/schedule`)

### Deep Security Architecture Review (`/boost`)
```text
/boost Perform a comprehensive Telecom OSS/BSS threat-modeling review combining our local Antigravity `.agents/hooks.json` guardrails, Terminal Sandbox settings, and Google Cloud Gemini Enterprise governance (`roles/cloudaicompanion.user`, Cloud Audit Logs for `cloudaicompanion.googleapis.com`, and VPC Service Controls).
```

### Continuous SLA & Hook Audit Monitoring (`/schedule`)
```text
/schedule Every 10 minutes, run `query_ran_cell_health` across all 5 TACs and check `data/logs/hook_audit.log` for any denied tool executions.
```
