<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 03: Live OSS/BSS Telemetry via FastMCP, Lifecycle Hooks & Gemini Enterprise Security

**Duration**: 50 minutes  
**Delivered by**: **Tryolabs** (Powered by Google Antigravity & Gemini Enterprise)  
**Antigravity Capabilities Practiced**: Model Context Protocol (`mcp_config.json` + FastMCP), Lifecycle Hooks (`hooks.json` `PreToolUse` & `PostToolUse`), Antigravity Client Security Settings (Sandbox, Tool Execution Policy, Allowlists/Denylists), and Google Cloud **Gemini Enterprise** Governance.

> **Language / Idioma:** [English](./README.md) | [Español](./README.es.md) • **Prompt Playbook:** [PROMPTS.md](./PROMPTS.md) | [PROMPTS.es.md](./PROMPTS.es.md) • **PDF:** [EN](./LAB_03_INSTRUCTIONS_EN.pdf) | [ES](./LAB_03_INSTRUCTIONS_ES.pdf)

---

## 1. Scenario & Enterprise Security Architecture

Telecom operators manage highly sensitive infrastructure (3GPP 5G RAN gNodeBs, Core Charging Functions) and regulated Customer Proprietary Network Information (**CPNI**: `IMSI`, `MSISDN`, `IMEI`). Connecting AI agents to Telecom OSS/BSS databases requires two layers of enterprise governance:

### Layer 1: Google Cloud & Gemini Enterprise Governance (Cloud Plane)
When attendees authenticate Antigravity with their corporate **Gemini Enterprise** license:
1. **IAM & Seat Governance**: Access is governed via Google Cloud IAM (`roles/cloudaicompanion.user`) federated with corporate SSO (Workspace / Cloud Identity / Okta / Entra ID).
2. **Cloud Audit Logs (`cloudaicompanion.googleapis.com`)**: Platform administrators monitor `Admin Activity` and `Data Access` audit logs in **Google Cloud Logging** for compliance and license utilization—without logging proprietary source code or subscriber payloads.
3. **Zero Training & Perimeter Security**: Customer code, prompts, and 3GPP/BSS telemetry are **never** used to train foundation models, are covered by Google Cloud IP indemnification, and can be perimeter-restricted with **VPC Service Controls (VPC-SC)**.

### Layer 2: Antigravity Client & Workspace Guardrails (Local Plane)
Inside **Antigravity 2.0** and **Antigravity IDE** (`Settings` -> `Global` & `Project-Level Settings`):
1. **Tool Execution Policy**: Choose between `strict`, `request-review`, `proceed-in-sandbox`, or `always-proceed`.
2. **Terminal Sandbox**: Isolates shell commands executed by the agent inside an OS-level sandbox.
3. **File & Internet Access Policies**: Restrict `Non-Workspace File Access` (`deny`/`ask`) and `Internet Access Policy` (`deny`/`ask`), plus configure `Command Allowlist / Denylist` and `Browser Allowlist`.
4. **Deterministic Lifecycle Hooks (`.agents/hooks.json`)**: Intercept every tool call (`PreToolUse` / `PostToolUse`) via `scripts/audit_hook.py` to block destructive SQL (`DROP TABLE`, `TRUNCATE`, `DELETE FROM b2b_contracts`) before execution!

---

## 2. Lab Setup

Run the Lab 03 installer (which automatically applies Labs 01 and 02 solutions first):

```bash
./labs/lab-03-mcp-and-hooks/install.sh
```

---

## 3. Step-by-Step Instructions

### Step 3.1: Complete the 4 FastMCP Tools in `mcp_server/telecom_mcp.py`
Open [mcp_server/telecom_mcp.py](../../mcp_server/telecom_mcp.py). `query_ran_cell_health` is already implemented. Use Antigravity (see [PROMPTS.md](./PROMPTS.md)) to implement the remaining three `@mcp.tool()` functions:
1. `calculate_contract_penalty_exposure(contract_id: str | None = None)`
2. `inspect_unbilled_cdrs(contract_id: str | None = None, roaming_only: bool = False)` — **Important**: Mask `imsi` and `msisdn` as `masked_imsi` and `masked_msisdn` (e.g., `3104***0001`) so raw CPNI is never exposed!
3. `evaluate_slice_capacity(target_tac: str, requested_slice_sst: int, requested_bandwidth_mbps: int, max_latency_ms: float)`

### Step 3.2: Register the MCP Server in `.agents/mcp_config.json`
Create `.agents/mcp_config.json`:

```json
{
  "mcpServers": {
    "telecom-nexus-mcp": {
      "command": "./.venv/bin/python",
      "args": ["mcp_server/telecom_mcp.py"],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Step 3.3: Configure `PreToolUse` & `PostToolUse` Hooks in `.agents/hooks.json`
Inspect [scripts/audit_hook.py](../../scripts/audit_hook.py) and create `.agents/hooks.json` so every `run_command` step is validated by `audit_hook.py` before execution and logged to `data/logs/hook_audit.log` afterward.

---

## 4. Verification

Run the Lab 03 verification script:

```bash
./labs/lab-03-mcp-and-hooks/verify.sh
```

> **Need the Reference Solution?** Run `./labs/lab-03-mcp-and-hooks/apply_solution.sh`.
