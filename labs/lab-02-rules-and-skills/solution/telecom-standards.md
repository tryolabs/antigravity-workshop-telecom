# Telecom 3GPP, GSMA TAP3 & TMF Open API Governance Rules

## 1. 3GPP & GSMA Standards Compliance
- **3GPP TS 28.552 (5G Performance Measurements)**:
  - Physical Resource Block (PRB) utilization (`prb_utilization_pct`) must remain `< 80.0%` for new TMF622 B2B slice admission.
  - PDCP SDU latency (`pdcp_latency_ms`) must be `<= committed_latency_ms` (or `max_latency_ms` on TMF622 orders).
  - Standard S-NSSAI Slice/Service Types (`s_nssai_sst`):
    - `SST = 1`: eMBB (`5QI = 7`)
    - `SST = 2`: URLLC (`5QI = 82`)
    - `SST = 3`: mIoT (`5QI = 9`)
- **3GPP TS 32.298 & GSMA TAP3.12 (Charging & Roaming Settlement)**:
  - Exact binary Gigabyte scaling (`1 GiB = 1024**3 bytes = 1,073,741,824 bytes`) is mandatory.
  - Home PLMN ID is `310-410`. All non-home PLMNs (`234-15`, `262-01`, `440-10`, etc.) must apply the contract's `roaming_markup_pct` regardless of whether `rat_type` is `NR_5G` or `EUTRAN_4G`.
- **TMF622 (Product Ordering Management API)**:
  - Every B2B order feasibility evaluation must classify the order into one of:
    - `READY_TO_ACTIVATE`
    - `REQUIRES_SLICE_REMEDIATION`
    - `REJECTED`

## 2. Financial & Privacy Safeguards
- **Decimal Monetary Arithmetic**:
  - Use `from decimal import Decimal, ROUND_HALF_UP` for all currency calculations (`billed_amount_usd`, `expected_amount_usd`, `penalty_exposure_usd`, `estimated_mrr_usd`).
- **CPNI / Subscriber Privacy (IMSI & MSISDN Protection)**:
  - Never expose raw subscriber credentials or perform destructive SQL operations (`DROP TABLE`, `TRUNCATE`, `DELETE FROM b2b_contracts`) in diagnostic scripts or hooks.
