# Instructor Demo Guide: Telecom Nexus — Antigravity Workshop

<p align="center">
  <img src="src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

**Platform**: Telecom Nexus — 5G Network Slice SLA, CDR Revenue Assurance & B2B Contract Intelligence Platform  
**Presented by**: Tryolabs — Telecom OSS/BSS AI Practice  
**Total Duration**: 120–150 Minutes (Modular 4-Lab Format)  
**Languages**: English (`INSTRUCTOR_DEMO_GUIDE.md`) | [Español](INSTRUCTOR_DEMO_GUIDE.es.md)

---

## 1. Executive Narrative & Workshop Positioning

When delivering this workshop to Telecom CTOs, VPs of Network Engineering, Revenue Assurance Directors, and Principal Architects, frame the challenge around the **OSS/BSS Chasm**:

1. **Technical OSS Teams** live in **3GPP TS 28.552** 5G Radio Access Network (RAN) KPIs (`DL_PRB_UTIL_PCT`, `RAN_LATENCY_MS`, `PACKET_LOSS_PCT`), JSONL cell alarms, and **3GPP TS 32.298 / GSMA TAP3.12** Call Detail Records (CDRs).
2. **Commercial BSS Teams** live in **TM Forum TMF622** B2B Enterprise Sales Orders, **URLLC / eMBB / mMTC** SLA penalty structures, and Commercial Tariff Plans.
3. **Why Generic AI Coding Assistants Fail in Telecom**: Out-of-the-box coding assistants don't know your proprietary roaming tariffs, cannot query live 5G RAN telemetry databases safely, and lack the compliance hooks required by **SOX Section 404** and **FCC CPNI**.

In this workshop, participants transform **Google Antigravity** from a general-purpose coding assistant into a **Telecom-Grade OSS/BSS Autonomous Engineering Platform** across four progressive labs.

---

## 2. Pre-Flight Checklist (15 Minutes Before Session)

Run these commands in `/Users/hcorrea/Workspace/agy_agy_workshop/antigravity-workshop-telecom` before participants join:

```bash
# 1. Provision Python virtual environment and seed deterministic OSS/BSS data
./install.sh

# 2. Ensure the repository is in the Lab 1 Starter state (with the intentional bugs)
./labs/lab-01-revenue-sla-triage/install.sh

# 3. Start the FastAPI OSS/BSS Web Dashboard in a dedicated terminal tab
source .venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

Open `http://127.0.0.1:8001` in your browser and verify:
- The **Tryolabs** logo renders in the top-left header.
- **Unbilled CDR Leakage** initially reads **`$0.00`** (Bug #1 active).
- **Active SLA Penalty Exposure** initially reads **`$259,500.00`** (Bug #2 active — includes suspended contract `CTR-B2B-1007`).

---

## 3. Enterprise Security & Governance Deep-Dive (15 Minutes)

> **Instructor Tip**: Telecom CISO and Cloud Governance stakeholders will ask how Antigravity is governed in regulated environments. Present this two-layer architecture before diving into Lab 1.

### Layer 1: Google Cloud & Gemini Enterprise Governance
When Antigravity is deployed with **Gemini Enterprise on Google Cloud**:
1. **Cloud IAM Access Control**: Developer access is governed via Google Cloud IAM (`roles/cloudaicompanion.user`) managed through corporate identity providers (Okta, Microsoft Entra ID, Google Workspace SSO).
2. **Cloud Audit Logs**: Every administrative action and API request to `cloudaicompanion.googleapis.com` can be logged via Google Cloud Audit Logs and exported to **BigQuery** or **Chronicle SIEM** for telecom security operations.
3. **Zero Data Training Guarantee**: Customer source code, prompts, 3GPP telemetry, and BSS contracts are **never** used to train Google foundation models.
4. **Network & IP Protection**: Supports **VPC Service Controls (VPC-SC)** perimeters, Private Google Access, and full **Google Cloud Generative AI Intellectual Property Indemnification**.

### Layer 2: Antigravity Client & Workspace Security Controls
On the engineer's workstation and inside the repository, Antigravity enforces granular runtime policies:
1. **Tool Execution Policy (`Turbo` / `Auto` / `Ask`)**: Controls whether terminal commands execute automatically or require explicit human approval.
2. **Terminal Sandbox (macOS Seatbelt / Linux Bubblewrap)**: Restricts OS-level file and network operations performed by shell sub-processes.
3. **Non-Workspace File Access Toggle**: Blocks the agent from reading files outside the workspace directory (`/Users/hcorrea/Workspace/agy_agy_workshop/antigravity-workshop-telecom`).
4. **Internet Access Policy (`enabled` / `allowlist` / `disabled`)**: Prevents outbound connections to unauthorized external endpoints.
5. **Command Allowlist & Denylist**: Explicitly blocks destructive shell commands (`rm -rf`, `DROP TABLE`, raw production credentials).
6. **Browser Allowlist**: Restricts the `/browser` agent to approved internal OSS/BSS portals (`127.0.0.1:8001`).
7. **Deterministic Workspace Hooks (`.agents/hooks.json`)**: Pre-execution (`PreToolUse` / `PreRunCommand`) and post-edit (`PostToolUse` / `PostEditFile`) hooks that enforce SOX 404 & FCC CPNI audit trails (built live in **Lab 03**).

---

## 4. Minute-by-Minute Live Demo Walkthrough

### Module 1: Lab 01 — 5G Revenue Assurance & Network Slice SLA Triage (30 Mins)

#### Scene Setting (5 Mins)
Show the live dashboard at `http://127.0.0.1:8001`. Point out two anomalies reported by the NOC and Finance:
1. **Finance Alert**: Roaming partners submitted 250 TAP3.12 CDRs with 5G Ultra-Reliable Low-Latency (`5G_URLLC_ROAM`) overages, yet the dashboard shows **`$0.00` Unbilled Leakage**.
2. **Legal/B2B Alert**: The dashboard shows **`$259,500.00`** in SLA penalty exposure, including `$35,000` for **Apex Logistics (`CTR-B2B-1007`)**, whose contract status is **`SUSPENDED`**.

#### Live Demo Steps (15 Mins)
1. Run pytest in the terminal to show the failing tests:
   ```bash
   ./.venv/bin/pytest tests/test_lab01_triage.py -v
   ```
2. Open Antigravity and paste **Prompt 1** from `labs/lab-01-revenue-sla-triage/PROMPTS.md`.
3. Watch Antigravity inspect `src/services/cdr_rating.py` (finding the `overage_gb * 0.0` bug) and `src/services/sla_monitor.py` (finding the missing `c.status != 'ACTIVE'` check).
4. Paste **Prompt 2** to apply the fixes and run the tests (`4/4` passing).
5. Refresh `http://127.0.0.1:8001` (or use `/browser`) to show:
   - **Unbilled CDR Leakage**: **`$54,672.22`** across **125 unbilled roaming CDRs**
   - **Active SLA Penalty Exposure**: **`$224,500.00`** across **5 breached ACTIVE contracts** (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`)
   - **Combined Commercial Risk Exposure**: **`$279,172.22`**

#### Instructor Fallback Command
```bash
./labs/lab-01-revenue-sla-triage/apply_solution.sh
./labs/lab-01-revenue-sla-triage/verify.sh
```

---

### Module 2: Lab 02 — Telecom Domain Rules, Skills & Executive Audit (30 Mins)

#### Scene Setting (5 Mins)
Ask the audience: *"How do we make sure every engineer's agent automatically follows 3GPP TS 28.552 thresholds, masks IMSI/MSISDN identifiers per FCC CPNI, and calculates SLA penalties identically?"*

#### Live Demo Steps (15 Mins)
1. Prepare the Lab 02 state:
   ```bash
   ./labs/lab-02-rules-and-skills/install.sh
   ```
2. Walk through the three customization tiers:
   - Workspace Memory (`GEMINI.md`)
   - Domain Guardrails (`.agents/rules/telecom-standards.md`)
   - Progressive Disclosure Skill (`.agents/skills/sla-revenue-audit/SKILL.md` + `scripts/run_sla_audit.py`)
3. Use the prompts in `labs/lab-02-rules-and-skills/PROMPTS.md` (or `/learn`) to create the customization files and run `scripts/run_sla_audit.py` to generate `data/exports/sla_revenue_audit_report.json` and `data/exports/sla_revenue_audit_report.md`.
4. Open `data/exports/sla_revenue_audit_report.json` and highlight:
   - `"total_penalty_exposure_usd": 224500.0`
   - `"total_unbilled_cdr_leakage_usd": 54672.22`
   - `"total_commercial_risk_usd": 279172.22`
   - Every breached contract (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`) mapped to its root-cause `RRC_CONGESTION_ALERT` alarm (`8/8` cumulative tests passing).

#### Instructor Fallback Command
```bash
./labs/lab-02-rules-and-skills/apply_solution.sh
./labs/lab-02-rules-and-skills/verify.sh
```

---

### Module 3: Lab 03 — Live OSS/BSS MCP Server & SOX/CPNI Compliance Hooks (30 Mins)

#### Scene Setting (5 Mins)
Explain that static files aren't enough—agents need **live, read-only tool access** to OSS/BSS databases via the **Model Context Protocol (MCP)**, paired with **deterministic compliance hooks** that block destructive SQL (`DROP TABLE`, `DELETE FROM cdrs`) before execution.

#### Live Demo Steps (15 Mins)
1. Prepare the Lab 03 state:
   ```bash
   ./labs/lab-03-mcp-and-hooks/install.sh
   ```
2. Show `mcp_server/telecom_mcp.py` and the 4 OSS/BSS tools (`query_ran_cell_health`, `calculate_contract_penalty_exposure`, `inspect_unbilled_cdrs`, `evaluate_slice_capacity`).
3. Use `labs/lab-03-mcp-and-hooks/PROMPTS.md` to implement `inspect_unbilled_cdrs` and `evaluate_slice_capacity`, configure `.agents/mcp_config.json`, and wire `.agents/hooks.json` to `scripts/audit_hook.py`.
4. Live-test the compliance hook in the terminal to prove it blocks destructive SQL:
   ```bash
   echo '{"toolCall":{"name":"run_command","args":{"CommandLine":"sqlite3 data/telecom_nexus.db \"DROP TABLE b2b_contracts;\""}}}' | ./.venv/bin/python scripts/audit_hook.py --event PreToolUse
   ```
   Show the deterministic JSON deny response (`{"decision": "deny", "reason": "Blocked by Telecom Compliance Hook (SOX 404 / FCC CPNI)..."}`).
5. Show `data/logs/hook_audit.log` containing the immutable JSON audit trail (`11/11` cumulative tests passing).

#### Instructor Fallback Command
```bash
./labs/lab-03-mcp-and-hooks/apply_solution.sh
./labs/lab-03-mcp-and-hooks/verify.sh
```

---

### Module 4: Lab 04 — Multi-Agent OSS/BSS Capstone: Google ADK, A2A Protocol, `adk web` & Gemini Enterprise (30 Mins)

#### Scene Setting (5 Mins)
Bring the Technical OSS and Business BSS worlds together. The Enterprise Sales Desk has **15 pending TMF622 B2B 5G Slice Orders** worth millions in annual contract value. How do we build a production **Google ADK (Agent Development Kit)** multi-agent system, expose it via the **A2A (Agent2Agent) Protocol**, test it interactively in the **ADK Dev UI (`adk web`)**, and register it into **Google Gemini Enterprise** via **Terraform**?

#### Live Demo Steps (15 Mins)
1. Prepare the Lab 04 state:
   ```bash
   ./labs/lab-04-multi-agent-capstone/install.sh
   ```
2. Use `labs/lab-04-multi-agent-capstone/PROMPTS.md` to implement `src/services/order_feasibility.py` (`evaluate_order_feasibility`, `batch_evaluate_pending_orders`) and `src/agents/adk_a2a_orchestrator.py` (`RANSliceCapacityAgent`, `BSSCommercialSLAAgent`, `TelecomNexusOrchestratorAgent`, `get_a2a_agent_card`, and `handle_a2a_jsonrpc`), passing all **21/21 cumulative tests**.
3. Launch the **Google ADK Development UI (`adk web`)** locally:
   ```bash
   ./scripts/run_adk_web.sh --check
   ./scripts/run_adk_web.sh --port 8080
   ```
   Open `http://127.0.0.1:8080`, select `telecom_nexus`, and show the live multi-agent trace graph and A2A JSON-RPC handoff for `ORD-TMF622-9001` (`FEASIBLE_READY`) and `ORD-TMF622-9002` (`DEFERRED_CONGESTION`).
4. Validate the Cloud Run + Artifact Registry **Terraform (`infra/terraform/`)** infrastructure and **Gemini Enterprise Discovery Engine A2A Registration** (`deploy/register_gemini_enterprise_agent.sh`):
   ```bash
   ./labs/lab-04-multi-agent-capstone/deploy_gcp.sh --dry-run
   ```

#### Instructor Fallback Command
```bash
./labs/lab-04-multi-agent-capstone/apply_solution.sh
./labs/lab-04-multi-agent-capstone/verify.sh
```

---

## 5. Resetting the Repository After the Demo

To reset the repository back to the clean Lab 01 starter state for the next workshop cohort:

```bash
./labs/lab-01-revenue-sla-triage/install.sh
rm -f data/exports/sla_revenue_audit_report.json data/exports/sla_revenue_audit_report.md data/logs/hook_audit.log
```
