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
uvicorn src.main:app --reload --port 8000
```

Open `http://127.0.0.1:8000` in your browser and verify:
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
6. **Browser Allowlist**: Restricts the `/browser` agent to approved internal OSS/BSS portals (`127.0.0.1:8000`).
7. **Deterministic Workspace Hooks (`.agents/hooks.json`)**: Pre-execution (`PreRunCommand`) and post-edit (`PostEditFile`) hooks that enforce SOX 404 & FCC CPNI audit trails (built live in **Lab 03**).

---

## 4. Minute-by-Minute Live Demo Walkthrough

### Module 1: Lab 01 — 5G Revenue Assurance & Network Slice SLA Triage (30 Mins)

#### Scene Setting (5 Mins)
Show the live dashboard at `http://127.0.0.1:8000`. Point out two anomalies reported by the NOC and Finance:
1. **Finance Alert**: Roaming partners submitted 250 TAP3.12 CDRs with 5G Ultra-Reliable Low-Latency (`5G_URLLC_ROAM`) overages, yet the dashboard shows **`$0.00` Unbilled Leakage**.
2. **Legal/B2B Alert**: The dashboard shows **`$259,500.00`** in SLA penalty exposure, including `$35,000` for **Apex Logistics (`CTR-B2B-1007`)**, whose contract status is **`SUSPENDED`**.

#### Live Demo Steps (15 Mins)
1. Run pytest in the terminal to show the failing tests:
   ```bash
   ./.venv/bin/pytest tests/test_lab01_triage.py -v
   ```
2. Open Antigravity and paste **Prompt 1** from `labs/lab-01-revenue-sla-triage/PROMPTS.md`.
3. Watch Antigravity inspect `src/services/cdr_rating.py` (finding the `overage_gb * 0.0` bug) and `src/services/sla_monitor.py` (finding the missing `c.status != 'ACTIVE'` check).
4. Paste **Prompt 2** to apply the fixes and run the tests.
5. Refresh `http://127.0.0.1:8000` (or use `/browser`) to show:
   - **Unbilled CDR Leakage**: **`~$55,392.45`** across **125 unbilled roaming CDRs**
   - **Active SLA Penalty Exposure**: **`$224,500.00`** across **5 breached ACTIVE contracts** (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`).

#### Instructor Fallback Command
```bash
./labs/lab-01-revenue-sla-triage/apply_solution.sh
./labs/lab-01-revenue-sla-triage/verify.sh
```

---

### Module 2: Lab 02 — Telecom Domain Rules, Skills & Workflows (30 Mins)

#### Scene Setting (5 Mins)
Ask the audience: *"How do we make sure every engineer's agent automatically follows 3GPP TS 28.552 thresholds, masks IMSI/MSISDN identifiers per FCC CPNI, and calculates SLA penalties identically?"*

#### Live Demo Steps (15 Mins)
1. Prepare the Lab 02 state:
   ```bash
   ./labs/lab-02-rules-and-skills/install.sh
   ```
2. Walk through the starter templates in `.agents/rules/telecom-3gpp-governance.md`, `.agents/skills/telecom-sla-auditor/SKILL.md`, and `.agents/workflows/slice-sla-triage.md`.
3. Use the prompts in `labs/lab-02-rules-and-skills/PROMPTS.md` to complete the rule, skill, and workflow, then execute `/slice-sla-triage` to generate `data/exports/sla_audit_report.json`.
4. Open `data/exports/sla_audit_report.json` and highlight:
   - `"total_penalty_exposure_usd": 224500.0`
   - Every breached contract (`CTR-B2B-1001`, `1002`, `1004`, `1006`, `1009`) mapped to its root-cause `RRC_CONGESTION_ALERT` alarm.

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
2. Show `mcp_server/telecom_mcp.py` and the 4 OSS/BSS tools (`query_ran_slice_health`, `inspect_cdr_leakage_by_tariff`, `evaluate_b2b_contract_sla`, `check_tmf622_order_feasibility`).
3. Use `labs/lab-03-mcp-and-hooks/PROMPTS.md` to implement `check_tmf622_order_feasibility`, configure `.mcp.json`, and wire `.agents/hooks.json` to `scripts/audit_hook.py`.
4. Live-test the compliance hook in the terminal to prove it blocks destructive SQL:
   ```bash
   echo '{"command": "sqlite3 data/telecom_nexus.db \"DROP TABLE cdrs;\""}' | python3 scripts/audit_hook.py --event PreRunCommand
   echo "Exit code: $?" # Returns Exit code: 2 (BLOCKED!)
   ```
5. Show `data/logs/hook_audit.log` containing the JSON audit trail.

#### Instructor Fallback Command
```bash
./labs/lab-03-mcp-and-hooks/apply_solution.sh
./labs/lab-03-mcp-and-hooks/verify.sh
```

---

### Module 4: Lab 04 — Multi-Agent OSS/BSS Capstone: TMF622 Order Feasibility & Executive Advisory (30 Mins)

#### Scene Setting (5 Mins)
Bring the Technical OSS and Business BSS worlds together. The Enterprise Sales Desk has **8 pending TMF622 B2B 5G Slice Orders** worth millions in annual contract value. Which orders can the 5G RAN safely accept right now, and which ones must be held for RAN capacity expansion?

#### Live Demo Steps (15 Mins)
1. Prepare the Lab 04 state:
   ```bash
   ./labs/lab-04-multi-agent-capstone/install.sh
   ```
2. Show the two specialized subagents in `.agents/agents/`:
   - `ran-oss-investigator.md` (3GPP TS 28.552 RAN capacity & alarm investigator)
   - `bss-revenue-auditor.md` (TMF622 order feasibility, TAP3.12 CDR leakage & SLA risk auditor)
3. Run the multi-agent orchestration prompt (or `/teamwork` / `/plan`) from `labs/lab-04-multi-agent-capstone/PROMPTS.md` to produce `data/exports/executive_oss_bss_advisory.md`.
4. Review the generated Executive Advisory report with the audience:
   - **3 Feasible Orders (`APPROVE_IMMEDIATELY`)**: `ORD-TMF622-9003`, `ORD-TMF622-9005`, `ORD-TMF622-9008`
   - **5 Contended Orders (`HOLD_REQUIRES_RAN_EXPANSION`)**: `ORD-TMF622-9001`, `ORD-TMF622-9002`, `ORD-TMF622-9004`, `ORD-TMF622-9006`, `ORD-TMF622-9007`

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
rm -f data/exports/sla_audit_report.json data/exports/executive_oss_bss_advisory.md data/logs/hook_audit.log
```
