# Lab 01: 5G Slice SLA & CDR Revenue Assurance Triage

**Duration**: 45 minutes  
**Antigravity Capabilities Practiced**: `@` Context Mentions, `/plan` Mode, Inline Command (`Cmd+I` / `Ctrl+I`), Antigravity Tab (Supercomplete), Visual Diff Overlays, Terminal Test Execution, `/browser`, and `/learn`.

> 📄 **Quick Prompts File**: See [PROMPTS.md](./PROMPTS.md) ([Español](./PROMPTS.es.md)) for copy-paste prompts.

---

## 1. Scenario & Business Context

You are a Senior Principal Telecom OSS/BSS Engineer on call for **Telecom Nexus**. Two critical alarms just fired in `data/logs/ran_alarms.jsonl`:
1. **`ALM-BSS-8006` (Revenue Assurance Anomaly)**: Enterprise B2B data sessions are being severely underbilled.
   - In [src/services/cdr_rating.py](../../src/services/cdr_rating.py), `BYTES_DIVISOR` was mistakenly set to `Decimal(1024 ** 4)` (Terabytes!) instead of `Decimal(1024 ** 3)` (Gigabytes / GiB per **3GPP TS 32.298**).
   - Additionally, visiting PLMN roaming markup (`roaming_plmn != "310-410"`) is only applied when `rat_type == "EUTRAN_4G"`, silently dropping roaming charges on all **5G Standalone (`NR_5G`)** roaming CDRs!
2. **`ALM-3GPP-8001` .. `ALM-3GPP-8005` (5G Network Slice SLA Breaches)**:
   - In [src/services/sla_monitor.py](../../src/services/sla_monitor.py), `evaluate_contract_sla_compliance()` fails to filter `WHERE status = 'ACTIVE'` (accidentally penalizing `TERMINATED` contract `CTR-B2B-1011` and `DRAFT` contract `CTR-B2B-1012`).
   - Worse, the latency breach condition is inverted (`worst_latency < committed_latency` instead of `worst_latency > committed_latency`), marking healthy low-latency slices as breached while ignoring congested cells!

---

## 2. Lab Setup

Run the Lab 01 installer from the repository root to ensure a clean starting state:

```bash
./labs/lab-01-revenue-sla-triage/install.sh
```

Confirm that the starter bug causes the Lab 01 test suite to fail:

```bash
./.venv/bin/pytest tests/test_lab01_triage.py
```

---

## 3. Step-by-Step Instructions with Google Antigravity

### Step 3.1: Diagnose Root Causes with `@` Mentions
Open Antigravity and paste the **Discovery Prompt** from [PROMPTS.md](./PROMPTS.md):

```text
@data/logs/ran_alarms.jsonl @src/services/cdr_rating.py @src/services/sla_monitor.py @tests/test_lab01_triage.py
We have two critical OSS/BSS incidents reported in our 3GPP alarm stream (`ALM-BSS-8006` and `ALM-3GPP-8001`..`8005`):
1. Our GSMA TAP3 / 3GPP CDR rating engine is underbilling enterprise data sessions and missing 5G Standalone (`NR_5G`) roaming markups.
2. Our B2B 5G Network Slice SLA monitor is misreporting breached contracts and including non-active contracts.

Run `./.venv/bin/pytest tests/test_lab01_triage.py` to reproduce the failures, then explain the exact root causes in `cdr_rating.py` and `sla_monitor.py`.
```

### Step 3.2: Generate & Review a Plan with `/plan`
Ask Antigravity to plan the fix before editing files:

```text
/plan Create a step-by-step remediation plan to fix `src/services/cdr_rating.py` and `src/services/sla_monitor.py` so that all tests in `tests/test_lab01_triage.py` pass.
```

### Step 3.3: Fix `src/services/cdr_rating.py` and `src/services/sla_monitor.py`
Either approve the `/plan` in Chat Canvas or use `Cmd+I` / `Ctrl+I` inline in the editor:
1. In `src/services/cdr_rating.py`:
   - Change `BYTES_DIVISOR = Decimal(1024 ** 4)` to `BYTES_PER_GB = Decimal(1024 ** 3)`.
   - Change `if roaming_plmn != HOME_PLMN and rat_type == "EUTRAN_4G":` to `if roaming_plmn != HOME_PLMN:`.
2. In `src/services/sla_monitor.py`:
   - Filter contracts by `WHERE status = 'ACTIVE'`.
   - Change `latency_breach = worst_latency < committed_latency` to `latency_breach = worst_latency > committed_latency`.

---

## 4. Verification

Run the Lab 01 verification script:

```bash
./labs/lab-01-revenue-sla-triage/verify.sh
```

> **Need the Reference Solution?** Run `./labs/lab-01-revenue-sla-triage/apply_solution.sh` at any time.
