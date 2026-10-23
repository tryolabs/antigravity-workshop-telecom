---
marp: true
theme: default
paginate: true
backgroundColor: #0d1117
color: #f0f6fc
---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### TRYOLABS EXECUTIVE WORKSHOP • 4 HOURS (10% THEORY / 90% HANDS-ON LABS)
# Agentic Engineering with Google Antigravity — Telecom Edition: Building 'Telecom Nexus'
**5G Network Slice SLA, CDR Revenue Assurance & B2B Contract Intelligence (Delivered by Tryolabs)**

![Architecture Diagram](../assets/telecom_domain_en.png)

### Workshop Mission & Industry Architecture
- OSS Technical Data: 20 5G NR cells (gNodeB, TAC, S-NSSAI SST 1/2/3, PRB%, PDCP latency)
- TAP3 / 3GPP CDRs: 250 call/data records (IMSI, MSISDN, NR_5G roaming PLMN, GiB volume)
- BSS Business Data: 12 Enterprise B2B SLA contracts ($180K–$2.4M ACV, $/hr SLA penalties)
- TMF622 Sales Pipeline: 15 pending B2B slice orders + JSONL RAN alarm telemetry
- Tangible Impact: Recover $54,672.22 in unbilled CDRs & protect $224,500 in active SLA exposure

> **Delivered by Tryolabs • 100% Local Laptop Execution + Terraform Cloud Run & Gemini Enterprise Ready**

<!-- Speaker Notes: Welcome attendees on behalf of Tryolabs. Highlight the 10% theory / 90% hands-on format and how we combine technical telemetry with commercial business data (contracts, sales, revenue/margins). -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### AGENDA & PROGRESSION • 24M THEORY / 216M HANDS-ON LABS
# 4-Hour Hands-On Roadmap: From Triage to Multi-Agent ADK & A2A
**Four 6-minute micro-theory briefings paired with four progressive 52–55 minute hands-on labs**

![Architecture Diagram](../assets/roadmap_en.png)

### Minute-by-Minute Workshop Schedule
- Hour 1 (00:00–00:58): [6m Theory] Internal Architecture & Surfaces → [52m Lab 1] Triage & Revenue/Margin Recovery
- Hour 2 (00:58–01:58): [6m Theory] Rules & Progressive Skills → [54m Lab 2] Domain Standards & Executive Risk Skill
- Hour 3 (01:58–02:59): [6m Theory] MCP, Hooks & Cloud Governance → [55m Lab 3] Local FastMCP Server & Compliance Hooks
- Hour 4 (02:59–04:00): [6m Theory] Subagents, ADK, A2A & Terraform → [55m Lab 4] Multi-Agent Capstone, ADK Dev UI & Cloud Deploy
- Self-Healing Checkpoints: Running ./labs/lab-0X/install.sh automatically applies prior lab solutions!

> **Every lab includes README.md, PROMPTS.md (optimized Antigravity prompts), install.sh, and verify.sh.**

<!-- Speaker Notes: Walk through the 4-hour progression. Emphasize that attendees use Antigravity itself to solve every lab using the curated prompts in PROMPTS.md. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### THEORY MODULE 1A (3 MINUTES) • UNDER THE HOOD
# How Google Antigravity Works Internally
**Inside the closed-loop cognitive planner, context assembler, policy gate, and sandboxed runtime**

![Architecture Diagram](../assets/arch_internal_en.png)

### The 5-Stage Internal Execution Loop
- 1. Context & Progressive Loader: Walks directory tree for GEMINI.md & .agents/rules, indexes SKILL.md YAML frontmatter, resolves @mentions, and manages transcript.jsonl
- 2. Gemini Enterprise Planner: Generates interleaved chain-of-thought (thinking), synthesizes plans (/plan), and dispatches parallel tool or subagent calls
- 3. Deterministic Security Gate: Evaluates PreToolUse hooks (exit code 2 blocks execution), tool policies, file/network ACLs, and OS sandbox rules
- 4. Tool Runtime & MCP Bridge: Executes AST-aware file diffs, sandboxed pytest commands, and stdio/SSE FastMCP calls
- 5. Verification & Reactive Loop: Runs PostToolUse hooks, reads compiler/test outputs, and self-corrects until green

> **Key Insight: Antigravity is not just chat—it is a stateful, verifiable closed-loop engineering runtime.**

<!-- Speaker Notes: Explain how Antigravity works under the hood: Context Loader -> Interleaved Thinking Planner -> Deterministic Policy/Hook Gate -> Tool/MCP Runtime -> Closed-Loop Self-Verification. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### THEORY MODULE 1B (3 MINUTES) • UNIFIED SURFACES & MODALITIES
# Antigravity 2.0, IDE & CLI (`agy`) — Core Modalities
**Choosing the right modality and slash command for every engineering task**

![Architecture Diagram](../assets/surfaces_en.png)

### Features You Will Explore Today
- Passive Modality (IDE Tab): Context-aware Supercomplete, Tab-to-Jump across files, and Tab-to-Auto-Import
- Instructive Modality (Cmd/Ctrl+I & Code Lenses): Highlight a function for surgical inline refactoring or click 'Write Tests'
- Collaborative Modality (Chat Canvas & CLI `agy`): Multi-file reasoning with @file, @folder, @terminal, and screenshot drag-and-drop
- High-Leverage Slash Commands: /plan (step-by-step architecture), /grill-me (design interview), /boost, /teamwork, /learn & /compact
- HTML Auxiliary Pane: Real-time inspection of Subagents, Background Tasks, Artifacts, and File Diffs

> **Pro Tip: Start complex tasks with /plan and @file mentions; use Cmd+I for localized formula fixes.**

<!-- Speaker Notes: Demonstrate the three surfaces (Antigravity 2.0, IDE, CLI) and show how @ mentions, /plan, and Cmd+I work together. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### HANDS-ON LAB 1 (52 MINUTES) • TRIAGE & RECOVERY
# Lab 1: Root-Cause Triage & Revenue/Margin Leakage Recovery
**Use Antigravity (/plan, @mentions, Cmd+I, pytest) to diagnose and fix two high-impact bugs**

![Architecture Diagram](../assets/telecom_domain_en.png)

### Lab 1 Walkthrough & Optimized Prompts
- Setup: Run ./labs/lab-01-revenue-sla-triage/install.sh & open http://localhost:8001
- Bug #1 (BSS Revenue Leakage): src/services/cdr_rating.py uses 1000^3 instead of 1024^3 GiB and drops the 1.50x NR_5G roaming multiplier ($54,672.22 leaked)
- Bug #2 (OSS/BSS SLA Risk): src/services/sla_monitor.py inverts latency (< vs >) and includes SUSPENDED contract CTR-B2B-1007 ($35K false alert)
- Prompt 1 (/plan): '/plan Analyze @src/services/cdr_rating.py, @src/services/sla_monitor.py and @tests/test_lab01_triage.py to diagnose the revenue and SLA bugs'
- Prompt 2 (Cmd+I & Fix): Use Inline Cmd+I to fix Decimal math, then run ./labs/lab-01-revenue-sla-triage/verify.sh

> **Open PROMPTS.md inside labs/lab-01-* for copy-pasteable prompts across Discovery, /plan, Cmd+I & Verification.**

<!-- Speaker Notes: Launch Lab 1! Have attendees run install.sh, inspect the broken KPIs on the live Web Dashboard, and use the optimized prompts in PROMPTS.md to fix both bugs. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### THEORY MODULE 2 (6 MINUTES) • CUSTOMIZATION ARCHITECTURE
# How Rules & Progressive Disclosure Skills Work Internally
**Specializing Antigravity for your industry without overflowing the context window**

![Architecture Diagram](../assets/customizations_en.png)

### Rules vs. Skills vs. /learn
- Hierarchical Rules (GEMINI.md & .agents/rules/*.md): Always-on or model-decided domain invariants loaded from workspace root down to target directories (deduplicated automatically)
- Progressive Disclosure Skills (.agents/skills/<name>/SKILL.md): Only lightweight YAML frontmatter (name, description) sits in system prompt; full markdown runbook & scripts/ load ONLY when triggered!
- Self-Improving Memory (/learn): Ask Antigravity to codify a newly discovered debugging pattern or architectural standard into a reusable workspace customization
- Precedence Hierarchy: Workspace (.agents/) > Declared JSON (skills.json) > Global (~/.gemini/config/) > Built-in

> **Rule of Thumb: Put permanent guardrails in GEMINI.md/rules; put multi-step workflows & scripts in SKILL.md.**

<!-- Speaker Notes: Explain progressive disclosure: why 50 skills don't bloat the prompt because only YAML frontmatter is loaded until the agent activates a specific skill. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### HANDS-ON LAB 2 (54 MINUTES) • DOMAIN BRAIN
# Lab 2: Encoding Industry Rules & Executive Audit Skills
**Teach Antigravity your industry standards and build an automated Technical + Commercial Risk Auditor**

![Architecture Diagram](../assets/customizations_en.png)

### Lab 2 Walkthrough & Optimized Prompts
- Setup: Run ./labs/lab-02-rules-and-skills/install.sh (auto-applies Lab 1 solution)
- Task 1 (Workspace Rules): Create GEMINI.md & .agents/rules/telecom-standards.md enforcing Decimal(0.01) billing math, 3GPP S-NSSAI SST {1,2,3}, and TMF622 schemas
- Task 2 (Progressive Skill): Create .agents/skills/sla-revenue-audit/SKILL.md with YAML frontmatter and executive audit runbook
- Optimized Prompt: 'Create @GEMINI.md, @.agents/rules/telecom-standards.md and @.agents/skills/sla-revenue-audit/SKILL.md, then run @scripts/run_sla_audit.py'
- Verify: Run ./labs/lab-02-rules-and-skills/verify.sh & try /learn to persist a new rule!

> **Open labs/lab-02-rules-and-skills/PROMPTS.md for step-by-step prompts to generate and verify your Rules & Skill.**

<!-- Speaker Notes: Guide attendees through Lab 2. Show how Antigravity automatically respects GEMINI.md and invokes their custom SKILL.md. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### THEORY MODULE 3 (6 MINUTES) • MCP, HOOKS & ENTERPRISE GOVERNANCE
# Live MCP Bridge, Deterministic Hooks & Gemini Enterprise Governance
**Connecting live databases safely while proving end-to-end enterprise security in Google Cloud**

![Architecture Diagram](../assets/governance_en.png)

### 2-Layer Enterprise Security & Governance
- Layer 1 — Google Cloud & Gemini Enterprise (Instructor Live Demo): Cloud IAM (roles/cloudaicompanion.user), Cloud Audit Logs (cloudaicompanion.googleapis.com), VPC-SC perimeters, Zero Data Retention / No Training on customer code
- Layer 2 — Antigravity Client Security: Tool Execution Policy (strict / request-review / proceed-in-sandbox), OS Terminal Sandbox, Non-Workspace File Access (deny), Command & Browser Allow/Denylists
- Live Context via FastMCP (.agents/mcp_config.json): Exposes strongly-typed Python tools querying live SQLite & telemetry over stdio/SSE
- Deterministic Lifecycle Hooks (.agents/hooks.json): PreToolUse script inspects tool JSON on stdin; exit code 2 hard-blocks policy violations and writes an immutable audit log!

> **Instructor Demo: Show Cloud Audit Logs in GCP Console + trigger a deterministic PreToolUse Hook block locally!**

<!-- Speaker Notes: This is a critical module for enterprise architects and CISOs. Show how Google Cloud governs Gemini Enterprise licenses & audit logs in Layer 1, while Antigravity enforces sandboxing and deterministic PreToolUse hooks in Layer 2. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### HANDS-ON LAB 3 (55 MINUTES) • LIVE MCP & COMPLIANCE HOOKS
# Lab 3: Building a Local FastMCP Server & Compliance Guardrails
**Give Antigravity live database/telemetry tools and deterministic PreToolUse protection**

![Architecture Diagram](../assets/governance_en.png)

### Lab 3 Walkthrough & Optimized Prompts
- Setup: Run ./labs/lab-03-mcp-and-hooks/install.sh
- Task 1 (FastMCP Server): Implement live tools in @mcp_server/telecom_mcp.py (query_ran_cell_health, calculate_contract_penalty_exposure, inspect_unbilled_cdrs, evaluate_slice_capacity)
- Task 2 (MCP & Deterministic Hook): Wire .agents/mcp_config.json and .agents/hooks.json (runs @scripts/audit_hook.py to block destructive SQL with exit code 2 & log SOX/CPNI audits)
- Optimized Prompt: 'Complete @mcp_server/telecom_mcp.py, register @.agents/mcp_config.json and @.agents/hooks.json, then query live B2B SLA exposure via MCP'
- Verify: Run ./labs/lab-03-mcp-and-hooks/verify.sh & inspect data/logs/hook_audit.log

> **Open labs/lab-03-mcp-and-hooks/PROMPTS.md for copy-pasteable prompts to build and test your MCP server & Hooks.**

<!-- Speaker Notes: Have attendees build the FastMCP tools, wire mcp_config.json and hooks.json, and deliberately test a blocked command to see exit code 2 and the audit log in action. -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### THEORY MODULE 4 (6 MINUTES) • SUBAGENTS, GOOGLE ADK, A2A & TERRAFORM
# Multi-Agent Systems with Google ADK, A2A Protocol & Terraform
**Designing multi-agent architectures locally with `adk web` and deploying to Cloud Run & Gemini Enterprise**

![Architecture Diagram](../assets/adk_a2a_cloud_en.png)

### End-to-End Multi-Agent Architecture
- Antigravity Subagents (/teamwork, /boost, /grill-me): Delegate parallel coding & research tasks inside Antigravity to build your application faster
- Google ADK (Agent Development Kit): Build domain multi-agent hierarchies (`root_agent` orchestrating Technical & Commercial specialist `LlmAgent`s with typed Python tools)
- Local Testing via ADK Dev UI (`adk web`): Launch `./scripts/run_adk_web.sh` (http://localhost:8080) to interactively inspect multi-agent event traces, tool calls, and session state!
- A2A (Agent2Agent) Protocol: Publish `GET /.well-known/agent.json` (Agent Card) and `POST /api/v1/a2a` (JSON-RPC 2.0 `tasks/send`) for cross-agent interoperability
- Terraform + Gemini Enterprise: Provision Cloud Run v2 & IAM via `infra/terraform/` (`deploy_gcp.sh`) and register your A2A agent into Gemini Enterprise (`register_gemini_enterprise_agent.sh`)

> **Develop & test 100% locally with `adk web` + `pytest`, then deploy to Google Cloud & Gemini Enterprise with Terraform!**

<!-- Speaker Notes: Explain the synergy between Antigravity subagents (which help you write the code) and Google ADK + A2A (the runtime multi-agent system you build, test locally in `adk web`, deploy with Terraform, and register in Gemini Enterprise). -->

---

![Tryolabs Logo](../assets/tryolabs-logo-dark-bg.png)
##### HANDS-ON LAB 4 CAPSTONE (55 MINUTES) • ADK, A2A & CLOUD DEPLOYMENT
# Lab 4 Capstone: Ship the Multi-Agent ADK + A2A System
**Use Antigravity (/grill-me, /boost, Subagents) to build, test in `adk web`, and validate Terraform deployment**

![Architecture Diagram](../assets/adk_a2a_cloud_en.png)

### Lab 4 Walkthrough & Optimized Prompts
- Setup: Run ./labs/lab-04-multi-agent-capstone/install.sh
- Task 1 (Google ADK Hierarchy): Implement @src/agents/adk_a2a_orchestrator.py & @adk_agents/telecom_nexus/agent.py (RANSliceCapacityAgent + BSSCommercialSLAAgent -> TelecomNexusOrchestratorAgent)
- Task 2 (A2A Protocol): Expose GET /.well-known/agent.json & POST /api/v1/a2a (JSON-RPC 2.0 tasks/send) + TMF622 feasibility & slice remediation routes
- Task 3 (Local ADK Dev UI): Run ./scripts/run_adk_web.sh to test interactively in `adk web` (http://localhost:8080) & run ./labs/lab-04-multi-agent-capstone/verify.sh
- Task 4 (Terraform & Gemini Enterprise): Validate with ./deploy/deploy_gcp.sh --dry-run, deploy to Cloud Run via Terraform, and connect via ./deploy/register_gemini_enterprise_agent.sh!

> **Congratulations! Run ./labs/lab-04-multi-agent-capstone/verify.sh to see your full test suite pass 100%!**

<!-- Speaker Notes: Guide attendees through the Capstone! Have them test their multi-agent hierarchy in both the FastAPI dashboard, the ADK Development UI (`./scripts/run_adk_web.sh` at localhost:8080), and `./deploy/deploy_gcp.sh --dry-run` (or live GCP deploy!). -->