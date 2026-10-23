# Lab 04: Multi-Agent Capstone — TMF622 Order Feasibility & 5G Slice QoS Remediation

**Duration**: 60 minutes  
**Delivered by**: **Tryolabs** (Powered by Google Antigravity & Gemini Enterprise)  
**Antigravity Capabilities Practiced**: Multi-Agent Orchestration (`/teamwork`, Subagents), Deep Strategic Thinking (`/boost`), Autonomous Goal Execution (`/goal`), Browser Automation (`/browser`), and Auxiliary Pane Inspection (Subagents, Background Tasks, Artifacts, Files Changed).

> 📄 **Quick Prompts File**: See [PROMPTS.md](./PROMPTS.md) ([Español](./PROMPTS.es.md)) for copy-paste prompts.

---

## 1. Capstone Scenario

Fifteen high-value **TMF622 Enterprise B2B Sales Orders** (`ORD-TMF622-9001` .. `9015`) are waiting in the provisioning queue.
- Some orders target healthy 5G RAN Tracking Area Codes (`TAC-LAX-004`, `TAC-CHI-002` SST=3) and can be activated immediately (`READY_TO_ACTIVATE`).
- Several strategic orders (such as `ORD-TMF622-9001` for **Goldman Sachs Low-Latency Trading Backup** in `TAC-NY-001` `SST=2`, worth **$42,000/mo MRR / $504,000 ARR**) are blocked because primary sector `CELL-NY-001-B` is congested (`88.2%` PRB, `14.8ms` PDCP latency vs `5.0ms` max latency), even though neighbor sector `CELL-NY-001-C` in the same TAC and URLLC slice is healthy (`44.0%` PRB, `3.4ms` latency, `448 Mbps` free)!
- Two orders (`ORD-TMF622-9011` requesting `950 Mbps @ 1.2ms` and `ORD-TMF622-9014` requesting `750 Mbps @ 2.0ms`) exceed physical 5G air-interface capacity across all cells in their target TAC and must be classified as `REJECTED`.

Your mission in Lab 04 is to use **Antigravity's Multi-Agent capabilities** (`/teamwork` or `/boost`) to implement `evaluate_order_feasibility()` and `remediate_slice_for_order()` in [src/services/order_feasibility.py](../../src/services/order_feasibility.py), powering the FastAPI endpoints:
- `POST /api/v1/orders/feasibility-check`
- `POST /api/v1/slices/remediate`

---

## 2. Lab Setup

Run the Lab 04 installer (which automatically applies Labs 01, 02, and 03 solutions first):

```bash
./labs/lab-04-multi-agent-capstone/install.sh
```

---

## 3. Step-by-Step Instructions

### Step 3.1: Launch a Multi-Agent Workflow (`/teamwork` or `/boost`)
Copy the `/teamwork` or `/boost` prompt from [PROMPTS.md](./PROMPTS.md) into Antigravity. Watch the **HTML Auxiliary Pane** in Antigravity 2.0 as subagents inspect the OSS/BSS schema, implement `src/services/order_feasibility.py`, and run verification tests!

### Step 3.2: Verify Business & Technical Rules Implemented
1. **`evaluate_order_feasibility(order_id, db_path)`**:
   - Queries `ran_telemetry` for `tac = target_tac` and `s_nssai_sst = requested_slice_sst`.
   - Checks `prb_utilization_pct < 80.0`, `pdcp_latency_ms <= max_latency_ms`, and `available_bandwidth_mbps >= requested_bandwidth_mbps`.
   - Classifies order as `READY_TO_ACTIVATE`, `REQUIRES_SLICE_REMEDIATION`, or `REJECTED` and updates `tmf622_sales_orders.order_status`.
2. **`remediate_slice_for_order(order_id, steering_mode, db_path)`**:
   - Raises `ValueError` if the order is `REJECTED` (which `src/main.py` maps to HTTP `400`).
   - Steers slice load and rebalances PRB on the congested cell (`prb_utilization_pct = 64.0`, `pdcp_latency_ms = round(max_latency_ms * 0.75, 2)`, `availability_pct = 99.995`, `status = 'HEALTHY'`).
   - Updates `tmf622_sales_orders` to `order_status = 'READY_TO_ACTIVATE'` and `sales_stage = 'PROVISIONED'`.
   - Computes `protected_annual_revenue_usd`, `avoided_sla_penalty_usd`, and `total_commercial_value_preserved_usd` using `Decimal`.

---

## 4. Full Workshop Verification

Run the Lab 04 verification script (which runs the entire test suite across Labs 01, 02, 03, and 04):

```bash
./labs/lab-04-multi-agent-capstone/verify.sh
```

> **Need the Reference Solution?** Run `./labs/lab-04-multi-agent-capstone/apply_solution.sh`.
