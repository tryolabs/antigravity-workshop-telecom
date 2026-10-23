# Lab 02 — Optimized Antigravity Prompts Cheat Sheet (English)

> **Goal**: Use **Google Antigravity** (associated with your **Gemini Enterprise** license and delivered by **Tryolabs**) to encode Telecom 3GPP/GSMA/TMF domain governance into:
> 1. Root Workspace Constitution (`GEMINI.md`)
> 2. Modular Rule (`.agents/rules/telecom-standards.md`)
> 3. Progressive-Disclosure On-Demand Skill (`.agents/skills/sla-revenue-audit/SKILL.md`)

---

## 1. Discovery & Architecture Survey Prompt (`@` Mentions)

```text
@src/services/contract_auditor.py @scripts/run_sla_audit.py @tests/test_lab02_rules_skills.py
Inspect how Telecom Nexus combines 3GPP 5G RAN telemetry (`ran_telemetry`), GSMA TAP3 CDR revenue assurance (`cdr_records`), and Enterprise B2B SLA contracts (`b2b_contracts`) to generate executive risk reports. Also inspect what `tests/test_lab02_rules_skills.py` requires for `GEMINI.md`, `.agents/rules/telecom-standards.md`, and `.agents/skills/sla-revenue-audit/SKILL.md`.
```

---

## 2. Planning Prompt (`/plan`)

```text
/plan Design the three Antigravity Customization files required for Lab 02:
1. `GEMINI.md` at the repository root defining the OSS/BSS domain architecture, mandatory Python `Decimal` arithmetic (`ROUND_HALF_UP`), `1024 ** 3` GiB scaling, and `ACTIVE` contract SLA filtering.
2. `.agents/rules/telecom-standards.md` enforcing 3GPP TS 28.552 (5G RAN PRB < 80%, PDCP latency), 3GPP TS 32.298 / GSMA TAP3.12, TMF622 order statuses, `Decimal` billing precision, and CPNI IMSI/MSISDN privacy protection.
3. `.agents/skills/sla-revenue-audit/SKILL.md` with valid YAML frontmatter (`name: sla-revenue-audit`, `description: ...`) instructing Antigravity how to execute `scripts/run_sla_audit.py` and validate `data/exports/sla_revenue_audit_report.json` and `.md`.
```

---

## 3. Instructive Inline Edit Prompt (`Cmd+I` / `Ctrl+I`)

Open `.agents/skills/sla-revenue-audit/SKILL.md` in Antigravity IDE and press `Cmd+I` / `Ctrl+I`:

```text
Generate a complete Antigravity SKILL.md with YAML frontmatter (`name: sla-revenue-audit` and a third-person `description` explaining when to activate the skill) followed by a 4-step runbook that runs `./.venv/bin/pytest tests/test_lab01_triage.py`, executes `./.venv/bin/python scripts/run_sla_audit.py`, and verifies `data/exports/sla_revenue_audit_report.json` and `data/exports/sla_revenue_audit_report.md`.
```

---

## 4. Implementation & Skill Invocation Prompt

First, ask Antigravity to create the three files:

```text
Create `GEMINI.md`, `.agents/rules/telecom-standards.md`, and `.agents/skills/sla-revenue-audit/SKILL.md` according to our plan, then run `./labs/lab-02-rules-and-skills/verify.sh`.
```

Next, test invoking your newly created **Skill** in natural language:

```text
Use the `sla-revenue-audit` skill to run a full 5G Slice SLA & GSMA TAP3 CDR revenue assurance audit and summarize the top 3 highest-risk B2B enterprise contracts from the generated executive report.
```

---

## 5. Power-User & Stretch Prompts (`/grill-me`, `/learn`, `/compact`)

### Governance & Rule Design Interview (`/grill-me`)
```text
/grill-me Interview me to refine our `.agents/rules/telecom-standards.md` so it covers 3GPP Release 18 Network Data Analytics Function (NWDAF), CPNI subscriber privacy masking, and TMF622/TMF641 service order decomposition.
```

### Persist Rule Corrections (`/learn`)
```text
/learn Whenever generating executive B2B SLA reports in Telecom Nexus, always sort contracts by `total_commercial_risk_usd` descending and highlight both `degraded_cell_id` and `primary_tac`.
```
