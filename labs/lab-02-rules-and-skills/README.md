<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 02: Encoding Telecom Domain Standards with Rules & Custom Skills

**Delivered by**: **Tryolabs** (Powered by Google Antigravity & Gemini Enterprise)  
**Antigravity Capabilities Practiced**: Workspace Rules (`GEMINI.md`, `.agents/rules/*.md`), Progressive-Disclosure Skills (`.agents/skills/<name>/SKILL.md`), `@` Mentions, `/plan`, `/learn`, and `/grill-me`.

> **Language / Idioma:** [English](./README.md) | [Español](./README.es.md) • **Prompt Playbook:** [PROMPTS.md](./PROMPTS.md) | [PROMPTS.es.md](./PROMPTS.es.md) • **PDF:** [EN (Dark)](./LAB_02_INSTRUCTIONS_EN.pdf) | [EN (Light)](./LAB_02_INSTRUCTIONS_EN_LIGHT.pdf) | [ES (Dark)](./LAB_02_INSTRUCTIONS_ES.pdf) | [ES (Light)](./LAB_02_INSTRUCTIONS_ES_LIGHT.pdf)

---

## 1. Scenario & Architectural Goal

In Lab 01, you fixed two costly OSS/BSS bugs manually with Antigravity. How do you ensure that **every developer and every AI agent session** across your Telecom engineering organization automatically enforces:
- **3GPP TS 28.552** (5G RAN PRB `< 80%` and PDCP latency SLA rules)
- **3GPP TS 32.298 & GSMA TAP3.12** (`Decimal(1024 ** 3)` GiB volume conversion & `NR_5G` visiting PLMN roaming markup)
- **TMF622** (Product Ordering status lifecycle)
- **CPNI Subscriber Privacy** (Masking IMSI and MSISDN in diagnostic outputs)

In **Google Antigravity**, you achieve this using two complementary customization primitives:
1. **Rules (`GEMINI.md` and `.agents/rules/telecom-standards.md`)**: Hierarchical guardrails loaded automatically to enforce coding styles, domain math (`Decimal`), and 3GPP/TMF compliance.
2. **Skills (`.agents/skills/sla-revenue-audit/SKILL.md`)**: On-demand runbooks using **Progressive Disclosure** (only the YAML `name` and `description` are loaded into context initially; the full runbook and helper script `scripts/run_sla_audit.py` are loaded only when the user or agent invokes the skill).

---

## 2. Lab Setup

Run the Lab 02 installer (which automatically ensures Lab 01 solutions are applied first):

```bash
./labs/lab-02-rules-and-skills/install.sh
```

---

## 3. Step-by-Step Instructions

### Step 3.1: Author `GEMINI.md` at the Repository Root
Use Antigravity (see [PROMPTS.md](./PROMPTS.md)) to create `GEMINI.md` at the root of the project. Ensure it specifies:
- The OSS (`ran_telemetry`, `ran_alarms.jsonl`) and BSS (`b2b_contracts`, `cdr_records`, `tmf622_sales_orders`) architecture.
- Mandatory Python `Decimal` (`ROUND_HALF_UP` to `0.01`) for all currency calculations.
- Binary GiB conversion (`1024 ** 3`) and `3GPP` slice types (`s_nssai_sst` 1, 2, 3).

### Step 3.2: Create `.agents/rules/telecom-standards.md`
Create `.agents/rules/telecom-standards.md` documenting:
- `3GPP` TS 28.552 and TS 32.298 standards
- `TAP3` roaming markup rules across `NR_5G` and `EUTRAN_4G`
- `TMF622` order feasibility classifications (`READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION`, `REJECTED`)
- `Decimal` financial precision and CPNI IMSI/MSISDN privacy safeguards

### Step 3.3: Create `.agents/skills/sla-revenue-audit/SKILL.md`
Create `.agents/skills/sla-revenue-audit/SKILL.md` starting with YAML frontmatter:

```markdown
---
name: sla-revenue-audit
description: >-
  Executes a combined 5G Network Slice SLA compliance and GSMA TAP3 CDR revenue assurance
  audit across OSS and BSS, generating an executive risk matrix in JSON and Markdown formats.
---
```

In the body of `SKILL.md`, instruct the agent to run `./.venv/bin/python scripts/run_sla_audit.py` and inspect `data/exports/sla_revenue_audit_report.json` and `data/exports/sla_revenue_audit_report.md`.

---

## 4. Verification

Run the Lab 02 verification script:

```bash
./labs/lab-02-rules-and-skills/verify.sh
```

> **Need the Reference Solution?** Run `./labs/lab-02-rules-and-skills/apply_solution.sh`.
