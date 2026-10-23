<p align="center">
  <img src="../../../src/static/tryolabs-logo.png" alt="Tryolabs Logo" width="180" />
</p>

# Telecom Nexus — Workspace Engineering Constitution (`GEMINI.md`)

## 1. Domain Architecture & Mission
You are operating inside **Telecom Nexus**, an integrated **5G Network Slice SLA (OSS)** and **Commercial Revenue Assurance & B2B Contract Intelligence (BSS)** platform.

### Core Domain Layers
- **OSS / 3GPP Network Layer (`ran_telemetry`, `data/logs/ran_alarms.jsonl`)**:
  - 5G Standalone (SA) RAN cell telemetry identified by `cell_id`, `gnodeb_id`, `tac` (Tracking Area Code), `plmn_id` (`310-410`), and 3GPP Single Network Slice Selection Assistance Information (`s_nssai_sst`, `s_nssai_sd`, `qos_5qi`).
  - Slice/Service Types (`s_nssai_sst`): `1` = eMBB (Enhanced Mobile Broadband), `2` = URLLC (Ultra-Reliable Low-Latency Communications), `3` = mIoT (Massive IoT).
- **BSS / Commercial Layer (`b2b_contracts`, `cdr_records`, `tmf622_sales_orders`, `tariff_plans`)**:
  - Enterprise B2B SLA Contracts (`CTR-B2B-*`) with committed latency (`committed_latency_ms`), availability (`committed_availability_pct`), hourly SLA penalty rates (`sla_penalty_per_hour_usd`), and roaming markups (`roaming_markup_pct`).
  - 3GPP TS 32.298 / GSMA TAP3.12 Charging Data Records (`cdr_records`).
  - TMF622 Product Ordering pipeline (`tmf622_sales_orders`).

## 2. Mandatory Coding & Telecom Standards
1. **Financial & Rating Precision (`Decimal` Only)**:
   - Never use binary `float` arithmetic for CDR rating, roaming markups, SLA penalty calculations, or MRR/ARR aggregations.
   - Always use Python `decimal.Decimal` with `ROUND_HALF_UP` quantized to `Decimal("0.01")`.
2. **Data Volume Conversion (3GPP TS 32.298 / GSMA TAP3)**:
   - Convert byte counters (`uplink_bytes + downlink_bytes`) to Gigabytes (GiB) using `Decimal(1024 ** 3)` (`1,073,741,824` bytes per GB).
   - Apply visiting PLMN (`roaming_plmn != '310-410'`) roaming markup across ALL radio access technologies (`NR_5G` and `EUTRAN_4G`).
3. **B2B SLA Compliance & Feasibility Rules (3GPP TS 28.552 / TMF622)**:
   - Only `ACTIVE` contracts (`status == 'ACTIVE'`) are eligible for SLA breach and penalty exposure calculations.
   - A 5G RAN cell is congested if `prb_utilization_pct >= 80.0` and breaches latency SLA when `pdcp_latency_ms > committed_latency_ms`.
4. **Verification Command**:
   - Always run `.venv/bin/pytest` after modifying any service or API endpoint.
