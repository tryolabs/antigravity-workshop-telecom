<p align="center">
  <img src="../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Lab 01 — Optimized Antigravity Prompts Cheat Sheet (English)

> **Goal**: Use **Google Antigravity** (Antigravity 2.0 Desktop App, Antigravity IDE, or `agy` CLI) to diagnose and repair two critical production incidents in **Telecom Nexus**:
> 1. **CDR Revenue Leakage ($54,000+ unbilled)** in `src/services/cdr_rating.py` (3GPP TS 32.298 / GSMA TAP3.12).
> 2. **Inverted 5G Slice SLA Latency & Contract Status Filter Bug** in `src/services/sla_monitor.py` (3GPP TS 28.552).

---

## 1. Discovery & Root-Cause Triage Prompt (Use `@` Mentions)

Copy and paste this into the **Antigravity Chat Canvas / Sidebar Chat**:

```text
@data/logs/ran_alarms.jsonl @src/services/cdr_rating.py @src/services/sla_monitor.py @tests/test_lab01_triage.py
We have two critical OSS/BSS incidents reported in our 3GPP alarm stream (`ALM-BSS-8006` and `ALM-3GPP-8001`..`8005`):
1. Our GSMA TAP3 / 3GPP CDR rating engine is underbilling enterprise data sessions and missing 5G Standalone (`NR_5G`) roaming markups.
2. Our B2B 5G Network Slice SLA monitor is misreporting breached contracts and including non-active contracts.

Run `./.venv/bin/pytest tests/test_lab01_triage.py` to reproduce the failures, then explain the exact root causes in `cdr_rating.py` and `sla_monitor.py`.
```

---

## 2. Planning Mode Prompt (`/plan`)

Use `/plan` to review Antigravity's step-by-step remediation strategy before any code is modified:

```text
/plan Create a step-by-step remediation plan to fix `src/services/cdr_rating.py` and `src/services/sla_monitor.py` so that:
1. `cdr_rating.py` converts `uplink_bytes + downlink_bytes` to binary Gigabytes (`Decimal(1024 ** 3)`) instead of Terabytes (`1024 ** 4`) and applies `roaming_markup_pct` whenever `roaming_plmn != "310-410"` across all `rat_type` values (`NR_5G` and `EUTRAN_4G`), rounding with `Decimal` `ROUND_HALF_UP` to `0.01`.
2. `sla_monitor.py` queries only `status = 'ACTIVE'` contracts from `b2b_contracts` and flags `latency_breach = worst_latency > committed_latency`.
3. Verify the fix by running `./labs/lab-01-revenue-sla-triage/verify.sh`.
```

---

## 3. Instructive Inline Edit Prompts (`Cmd+I` / `Ctrl+I` in Antigravity IDE)

If you want to fix each bug using **Inline Command** directly inside the editor:

### A. Inside `src/services/cdr_rating.py` (Highlight lines 19-48 and press `Cmd+I` / `Ctrl+I`)
```text
Fix BYTES_DIVISOR to use binary Gigabytes `Decimal(1024 ** 3)` per 3GPP TS 32.298, and apply the roaming markup multiplier whenever `roaming_plmn != HOME_PLMN` regardless of `rat_type` (including `NR_5G`). Keep all arithmetic in `Decimal` rounded via `round_money()`.
```

### B. Inside `src/services/sla_monitor.py` (Highlight lines 29-65 and press `Cmd+I` / `Ctrl+I`)
```text
Filter `b2b_contracts` so only rows with `status = 'ACTIVE'` are queried, and fix `latency_breach` so a breach occurs when `worst_latency > committed_latency`.
```

---

## 4. Full Autonomous Implementation & Verification Prompt

```text
Apply the fixes to @src/services/cdr_rating.py and @src/services/sla_monitor.py, then run `./labs/lab-01-revenue-sla-triage/verify.sh` and print a summary table showing:
1. Total CDRs audited, underbilled CDR count, and total recovered revenue leakage ($ USD).
2. The 5 breached ACTIVE B2B contracts, their degraded 5G RAN cell IDs, observed PDCP latency vs committed SLA latency, and exact SLA penalty exposure ($224,500.00 total).
```

---

## 5. Power-User & Stretch Prompts (`/grill-me`, `/browser`, `/learn`)

### Interactive Design Interview (`/grill-me`)
```text
/grill-me Interview me on how we should evolve our 5G Standalone CHF rating engine to support tiered overage buckets, mid-session QoS 5QI downgrades, and bilateral GSMA BCE (Billing and Charging Evolution) settlement with visiting PLMNs 234-15 and 262-01.
```

### Live NOC Dashboard Inspection (`/browser`)
```text
/browser Start the FastAPI server (`./.venv/bin/uvicorn src.main:app --port 8001`), open `http://localhost:8001`, and verify that the KPI cards display the recovered CDR Revenue Leakage and $224,500.00 Active B2B SLA Penalty Exposure.
```

### Persist Domain Knowledge (`/learn`)
```text
/learn Remember that in Telecom Nexus, byte-to-GiB conversion must always use `Decimal(1024 ** 3)`, roaming markup applies to all visiting PLMNs (`!= '310-410'`) across both `NR_5G` and `EUTRAN_4G`, and SLA penalty exposure only applies to `ACTIVE` B2B contracts.
```
