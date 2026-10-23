#!/usr/bin/env python3
"""
Deterministic Telecom Data Generator for the Google Antigravity Telecom Workshop.
Generates:
1. SQLite database (`data/telecom_nexus.db`) with OSS (5G RAN Telemetry, 3GPP/TAP3 CDRs)
   and BSS (Enterprise B2B SLA Contracts, TMF622 B2B Sales Orders, Commercial Tariff Plans).
2. CSV snapshots in `data/exports/` (`b2b_contracts.csv`, `sample_cdrs.csv`, `sales_orders.csv`).
3. Realistic 3GPP/ITU-T X.733 RAN & Core alarm logs in `data/logs/ran_alarms.jsonl`.
"""

from __future__ import annotations

import csv
import json
import random
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "telecom_nexus.db"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"

BYTES_PER_GB = Decimal(1024 ** 3)


def round_currency(val: Decimal) -> float:
    return float(val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def get_tariff_plans() -> list[dict]:
    return [
        {
            "plan_id": "PLAN-5G-EMBB-ENT",
            "plan_name": "Enterprise 5G eMBB High-Throughput",
            "s_nssai_sst": 1,
            "slice_type": "eMBB",
            "default_qos_5qi": 7,
            "base_rate_per_gb_usd": 4.50,
            "roaming_5g_zone_a_markup_pct": 35.0,
            "roaming_4g_zone_a_markup_pct": 20.0,
            "min_committed_acv_usd": 200000.0,
        },
        {
            "plan_id": "PLAN-5G-URLLC-MISSION",
            "plan_name": "Mission-Critical 5G URLLC Ultra-Low Latency",
            "s_nssai_sst": 2,
            "slice_type": "URLLC",
            "default_qos_5qi": 82,
            "base_rate_per_gb_usd": 12.00,
            "roaming_5g_zone_a_markup_pct": 50.0,
            "roaming_4g_zone_a_markup_pct": 30.0,
            "min_committed_acv_usd": 500000.0,
        },
        {
            "plan_id": "PLAN-5G-MIOT-GRID",
            "plan_name": "Industrial 5G mIoT Massive Telemetry",
            "s_nssai_sst": 3,
            "slice_type": "mIoT",
            "default_qos_5qi": 9,
            "base_rate_per_gb_usd": 2.25,
            "roaming_5g_zone_a_markup_pct": 25.0,
            "roaming_4g_zone_a_markup_pct": 15.0,
            "min_committed_acv_usd": 150000.0,
        },
    ]


def get_b2b_contracts() -> list[dict]:
    return [
        {
            "contract_id": "CTR-B2B-1001",
            "enterprise_name": "Mayo Clinic Connected Ambulance URLLC",
            "account_tier": "STRATEGIC_GLOBAL",
            "sales_rep_id": "REP-US-204",
            "primary_tac": "TAC-CHI-002",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A102",
            "annual_contract_value_usd": 1850000.0,
            "committed_latency_ms": 6.0,
            "committed_availability_pct": 99.99,
            "sla_penalty_per_hour_usd": 9500.0,
            "included_data_tb": 80.0,
            "overage_rate_per_gb_usd": 12.00,
            "roaming_markup_pct": 50.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 6.5,
        },
        {
            "contract_id": "CTR-B2B-1002",
            "enterprise_name": "Goldman Sachs Low-Latency Trading Backup",
            "account_tier": "STRATEGIC_GLOBAL",
            "sales_rep_id": "REP-US-101",
            "primary_tac": "TAC-NY-001",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A101",
            "annual_contract_value_usd": 2400000.0,
            "committed_latency_ms": 5.0,
            "committed_availability_pct": 99.995,
            "sla_penalty_per_hour_usd": 12000.0,
            "included_data_tb": 120.0,
            "overage_rate_per_gb_usd": 14.00,
            "roaming_markup_pct": 55.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 8.0,
        },
        {
            "contract_id": "CTR-B2B-1003",
            "enterprise_name": "Maersk Smart Port Autonomous Cranes",
            "account_tier": "PLATINUM",
            "sales_rep_id": "REP-US-409",
            "primary_tac": "TAC-LAX-004",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00B204",
            "annual_contract_value_usd": 1350000.0,
            "committed_latency_ms": 8.0,
            "committed_availability_pct": 99.99,
            "sla_penalty_per_hour_usd": 7500.0,
            "included_data_tb": 95.0,
            "overage_rate_per_gb_usd": 11.50,
            "roaming_markup_pct": 45.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 0.0,
        },
        {
            "contract_id": "CTR-B2B-1004",
            "enterprise_name": "Delta Air Lines Tarmac Operations eMBB",
            "account_tier": "PLATINUM",
            "sales_rep_id": "REP-US-305",
            "primary_tac": "TAC-DAL-003",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E301",
            "annual_contract_value_usd": 980000.0,
            "committed_latency_ms": 20.0,
            "committed_availability_pct": 99.95,
            "sla_penalty_per_hour_usd": 5200.0,
            "included_data_tb": 250.0,
            "overage_rate_per_gb_usd": 4.50,
            "roaming_markup_pct": 35.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 5.0,
        },
        {
            "contract_id": "CTR-B2B-1005",
            "enterprise_name": "Ford Global Connected Fleet Telemetry",
            "account_tier": "PLATINUM",
            "sales_rep_id": "REP-US-204",
            "primary_tac": "TAC-CHI-002",
            "s_nssai_sst": 3,
            "s_nssai_sd": "0x00C302",
            "annual_contract_value_usd": 840000.0,
            "committed_latency_ms": 45.0,
            "committed_availability_pct": 99.90,
            "sla_penalty_per_hour_usd": 3800.0,
            "included_data_tb": 400.0,
            "overage_rate_per_gb_usd": 2.25,
            "roaming_markup_pct": 30.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 0.0,
        },
        {
            "contract_id": "CTR-B2B-1006",
            "enterprise_name": "NBCUniversal Live 8K Broadcast Uplink",
            "account_tier": "GOLD",
            "sales_rep_id": "REP-US-101",
            "primary_tac": "TAC-NY-001",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E101",
            "annual_contract_value_usd": 720000.0,
            "committed_latency_ms": 18.0,
            "committed_availability_pct": 99.95,
            "sla_penalty_per_hour_usd": 4500.0,
            "included_data_tb": 320.0,
            "overage_rate_per_gb_usd": 4.75,
            "roaming_markup_pct": 40.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 4.0,
        },
        {
            "contract_id": "CTR-B2B-1007",
            "enterprise_name": "Walmart Cold-Chain Logistics mIoT",
            "account_tier": "GOLD",
            "sales_rep_id": "REP-US-305",
            "primary_tac": "TAC-DAL-003",
            "s_nssai_sst": 3,
            "s_nssai_sd": "0x00C303",
            "annual_contract_value_usd": 610000.0,
            "committed_latency_ms": 50.0,
            "committed_availability_pct": 99.90,
            "sla_penalty_per_hour_usd": 2800.0,
            "included_data_tb": 500.0,
            "overage_rate_per_gb_usd": 2.10,
            "roaming_markup_pct": 25.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 0.0,
        },
        {
            "contract_id": "CTR-B2B-1008",
            "enterprise_name": "Royal Caribbean Smart Cruise Port Network",
            "account_tier": "GOLD",
            "sales_rep_id": "REP-US-512",
            "primary_tac": "TAC-MIA-005",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E505",
            "annual_contract_value_usd": 540000.0,
            "committed_latency_ms": 22.0,
            "committed_availability_pct": 99.95,
            "sla_penalty_per_hour_usd": 3200.0,
            "included_data_tb": 210.0,
            "overage_rate_per_gb_usd": 4.25,
            "roaming_markup_pct": 35.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 0.0,
        },
        {
            "contract_id": "CTR-B2B-1009",
            "enterprise_name": "Siemens Smart Grid Automated Substation",
            "account_tier": "PLATINUM",
            "sales_rep_id": "REP-US-512",
            "primary_tac": "TAC-MIA-005",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A505",
            "annual_contract_value_usd": 1120000.0,
            "committed_latency_ms": 7.0,
            "committed_availability_pct": 99.99,
            "sla_penalty_per_hour_usd": 6500.0,
            "included_data_tb": 90.0,
            "overage_rate_per_gb_usd": 11.00,
            "roaming_markup_pct": 45.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 3.5,
        },
        {
            "contract_id": "CTR-B2B-1010",
            "enterprise_name": "DHL Autonomous Warehouse Robotics",
            "account_tier": "SILVER",
            "sales_rep_id": "REP-US-409",
            "primary_tac": "TAC-LAX-004",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E404",
            "annual_contract_value_usd": 390000.0,
            "committed_latency_ms": 25.0,
            "committed_availability_pct": 99.90,
            "sla_penalty_per_hour_usd": 2000.0,
            "included_data_tb": 140.0,
            "overage_rate_per_gb_usd": 4.50,
            "roaming_markup_pct": 30.0,
            "status": "ACTIVE",
            "breach_hours_mtd": 0.0,
        },
        {
            "contract_id": "CTR-B2B-1011",
            "enterprise_name": "Legacy Retail POS Backhaul Corp (Decommissioned)",
            "account_tier": "SILVER",
            "sales_rep_id": "REP-US-101",
            "primary_tac": "TAC-NY-001",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A101",
            "annual_contract_value_usd": 250000.0,
            "committed_latency_ms": 5.0,
            "committed_availability_pct": 99.99,
            "sla_penalty_per_hour_usd": 8000.0,
            "included_data_tb": 40.0,
            "overage_rate_per_gb_usd": 9.00,
            "roaming_markup_pct": 20.0,
            "status": "TERMINATED",
            "breach_hours_mtd": 12.0,
        },
        {
            "contract_id": "CTR-B2B-1012",
            "enterprise_name": "Apex Autonomous Mining Sandbox (Pre-Commercial)",
            "account_tier": "GOLD",
            "sales_rep_id": "REP-US-204",
            "primary_tac": "TAC-CHI-002",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A102",
            "annual_contract_value_usd": 680000.0,
            "committed_latency_ms": 6.0,
            "committed_availability_pct": 99.99,
            "sla_penalty_per_hour_usd": 6000.0,
            "included_data_tb": 60.0,
            "overage_rate_per_gb_usd": 10.50,
            "roaming_markup_pct": 35.0,
            "status": "DRAFT",
            "breach_hours_mtd": 9.0,
        },
    ]


def get_ran_cells() -> list[dict]:
    """
    Returns 20 5G NR RAN cells across 5 Tracking Area Codes (TACs).
    Notice which TAC+Slice combinations have SLA breaches on active contracts:
    - TAC-NY-001, SST=2 (CTR-B2B-1002 Goldman Sachs, committed 5.0ms): CELL-NY-001-B has pdcp_latency_ms=14.8ms, availability=99.91% -> BREACH
    - TAC-NY-001, SST=1 (CTR-B2B-1006 NBCUniversal, committed 18.0ms): CELL-NY-001-A has pdcp_latency_ms=26.4ms, prb=91.5% -> BREACH
    - TAC-CHI-002, SST=2 (CTR-B2B-1001 Mayo Clinic, committed 6.0ms): CELL-CHI-002-B has pdcp_latency_ms=16.2ms, availability=99.88% -> BREACH
    - TAC-DAL-003, SST=1 (CTR-B2B-1004 Delta Air Lines, committed 20.0ms): CELL-DAL-003-A has pdcp_latency_ms=29.5ms, prb=89.0% -> BREACH
    - TAC-MIA-005, SST=2 (CTR-B2B-1009 Siemens Smart Grid, committed 7.0ms): CELL-MIA-005-B has pdcp_latency_ms=13.5ms, availability=99.92% -> BREACH
    While the other 5 ACTIVE contracts (CTR-B2B-1003, 1005, 1007, 1008, 1010) are 100% COMPLIANT!
    """
    return [
        # TAC-NY-001 (New York Metro)
        {
            "cell_id": "CELL-NY-001-A",
            "gnodeb_id": "gNB-US-NY-101",
            "tac": "TAC-NY-001",
            "region_name": "New York Financial District",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E101",
            "qos_5qi": 7,
            "prb_utilization_pct": 91.5,
            "rsrp_dbm": -98.4,
            "sinr_db": 6.2,
            "pdcp_latency_ms": 26.4,
            "packet_loss_rate": 0.018,
            "rrc_conn_failures": 42,
            "availability_pct": 99.92,
            "active_ue_count": 840,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 85,
            "status": "CONGESTED",
            "neighbor_cell_id": "CELL-NY-001-D",
        },
        {
            "cell_id": "CELL-NY-001-B",
            "gnodeb_id": "gNB-US-NY-101",
            "tac": "TAC-NY-001",
            "region_name": "New York Financial District",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A101",
            "qos_5qi": 82,
            "prb_utilization_pct": 88.2,
            "rsrp_dbm": -95.0,
            "sinr_db": 8.5,
            "pdcp_latency_ms": 14.8,
            "packet_loss_rate": 0.012,
            "rrc_conn_failures": 31,
            "availability_pct": 99.91,
            "active_ue_count": 310,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 95,
            "status": "DEGRADED",
            "neighbor_cell_id": "CELL-NY-001-C",
        },
        {
            "cell_id": "CELL-NY-001-C",
            "gnodeb_id": "gNB-US-NY-102",
            "tac": "TAC-NY-001",
            "region_name": "New York Midtown Core",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A101",
            "qos_5qi": 82,
            "prb_utilization_pct": 44.0,
            "rsrp_dbm": -76.5,
            "sinr_db": 22.4,
            "pdcp_latency_ms": 3.4,
            "packet_loss_rate": 0.0002,
            "rrc_conn_failures": 1,
            "availability_pct": 99.998,
            "active_ue_count": 120,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 448,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-NY-001-B",
        },
        {
            "cell_id": "CELL-NY-001-D",
            "gnodeb_id": "gNB-US-NY-102",
            "tac": "TAC-NY-001",
            "region_name": "New York Midtown Core",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E101",
            "qos_5qi": 7,
            "prb_utilization_pct": 51.0,
            "rsrp_dbm": -79.0,
            "sinr_db": 19.8,
            "pdcp_latency_ms": 11.2,
            "packet_loss_rate": 0.0008,
            "rrc_conn_failures": 3,
            "availability_pct": 99.98,
            "active_ue_count": 390,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 490,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-NY-001-A",
        },
        # TAC-CHI-002 (Chicago Metro)
        {
            "cell_id": "CELL-CHI-002-A",
            "gnodeb_id": "gNB-US-CHI-201",
            "tac": "TAC-CHI-002",
            "region_name": "Chicago Medical District",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A102",
            "qos_5qi": 82,
            "prb_utilization_pct": 48.5,
            "rsrp_dbm": -78.2,
            "sinr_db": 21.0,
            "pdcp_latency_ms": 4.1,
            "packet_loss_rate": 0.0003,
            "rrc_conn_failures": 2,
            "availability_pct": 99.995,
            "active_ue_count": 145,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 412,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-CHI-002-B",
        },
        {
            "cell_id": "CELL-CHI-002-B",
            "gnodeb_id": "gNB-US-CHI-202",
            "tac": "TAC-CHI-002",
            "region_name": "Chicago Loop Corridor",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A102",
            "qos_5qi": 82,
            "prb_utilization_pct": 93.4,
            "rsrp_dbm": -101.2,
            "sinr_db": 4.8,
            "pdcp_latency_ms": 16.2,
            "packet_loss_rate": 0.024,
            "rrc_conn_failures": 58,
            "availability_pct": 99.88,
            "active_ue_count": 360,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 52,
            "status": "CONGESTED",
            "neighbor_cell_id": "CELL-CHI-002-A",
        },
        {
            "cell_id": "CELL-CHI-002-C",
            "gnodeb_id": "gNB-US-CHI-203",
            "tac": "TAC-CHI-002",
            "region_name": "Chicago Industrial Hub",
            "plmn_id": "310-410",
            "s_nssai_sst": 3,
            "s_nssai_sd": "0x00C302",
            "qos_5qi": 9,
            "prb_utilization_pct": 62.0,
            "rsrp_dbm": -84.0,
            "sinr_db": 15.6,
            "pdcp_latency_ms": 28.5,
            "packet_loss_rate": 0.0015,
            "rrc_conn_failures": 5,
            "availability_pct": 99.96,
            "active_ue_count": 4200,
            "max_bandwidth_mbps": 500,
            "available_bandwidth_mbps": 190,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-CHI-002-D",
        },
        {
            "cell_id": "CELL-CHI-002-D",
            "gnodeb_id": "gNB-US-CHI-203",
            "tac": "TAC-CHI-002",
            "region_name": "Chicago O'Hare Freight Zone",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E202",
            "qos_5qi": 7,
            "prb_utilization_pct": 55.2,
            "rsrp_dbm": -81.4,
            "sinr_db": 18.2,
            "pdcp_latency_ms": 14.0,
            "packet_loss_rate": 0.001,
            "rrc_conn_failures": 4,
            "availability_pct": 99.97,
            "active_ue_count": 410,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 448,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-CHI-002-C",
        },
        # TAC-DAL-003 (Dallas-Fort Worth)
        {
            "cell_id": "CELL-DAL-003-A",
            "gnodeb_id": "gNB-US-DAL-301",
            "tac": "TAC-DAL-003",
            "region_name": "DFW Airport Tarmac East",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E301",
            "qos_5qi": 7,
            "prb_utilization_pct": 89.0,
            "rsrp_dbm": -96.5,
            "sinr_db": 7.4,
            "pdcp_latency_ms": 29.5,
            "packet_loss_rate": 0.015,
            "rrc_conn_failures": 37,
            "availability_pct": 99.91,
            "active_ue_count": 780,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 110,
            "status": "CONGESTED",
            "neighbor_cell_id": "CELL-DAL-003-B",
        },
        {
            "cell_id": "CELL-DAL-003-B",
            "gnodeb_id": "gNB-US-DAL-301",
            "tac": "TAC-DAL-003",
            "region_name": "DFW Airport Tarmac West",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E301",
            "qos_5qi": 7,
            "prb_utilization_pct": 49.0,
            "rsrp_dbm": -79.8,
            "sinr_db": 20.1,
            "pdcp_latency_ms": 12.6,
            "packet_loss_rate": 0.0007,
            "rrc_conn_failures": 2,
            "availability_pct": 99.98,
            "active_ue_count": 370,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 510,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-DAL-003-A",
        },
        {
            "cell_id": "CELL-DAL-003-C",
            "gnodeb_id": "gNB-US-DAL-302",
            "tac": "TAC-DAL-003",
            "region_name": "Dallas Logistics Hub South",
            "plmn_id": "310-410",
            "s_nssai_sst": 3,
            "s_nssai_sd": "0x00C303",
            "qos_5qi": 9,
            "prb_utilization_pct": 58.0,
            "rsrp_dbm": -83.1,
            "sinr_db": 16.5,
            "pdcp_latency_ms": 31.0,
            "packet_loss_rate": 0.0012,
            "rrc_conn_failures": 4,
            "availability_pct": 99.95,
            "active_ue_count": 5100,
            "max_bandwidth_mbps": 500,
            "available_bandwidth_mbps": 210,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-DAL-003-D",
        },
        {
            "cell_id": "CELL-DAL-003-D",
            "gnodeb_id": "gNB-US-DAL-302",
            "tac": "TAC-DAL-003",
            "region_name": "Dallas Telecom Corridor",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A303",
            "qos_5qi": 82,
            "prb_utilization_pct": 41.0,
            "rsrp_dbm": -75.0,
            "sinr_db": 23.5,
            "pdcp_latency_ms": 3.9,
            "packet_loss_rate": 0.0002,
            "rrc_conn_failures": 1,
            "availability_pct": 99.996,
            "active_ue_count": 95,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 472,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-DAL-003-C",
        },
        # TAC-LAX-004 (Los Angeles / Port of LA)
        {
            "cell_id": "CELL-LAX-004-A",
            "gnodeb_id": "gNB-US-LAX-401",
            "tac": "TAC-LAX-004",
            "region_name": "Port of Los Angeles Container Terminal",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00B204",
            "qos_5qi": 82,
            "prb_utilization_pct": 64.5,
            "rsrp_dbm": -80.2,
            "sinr_db": 19.4,
            "pdcp_latency_ms": 4.8,
            "packet_loss_rate": 0.0004,
            "rrc_conn_failures": 2,
            "availability_pct": 99.995,
            "active_ue_count": 210,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 284,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-LAX-004-B",
        },
        {
            "cell_id": "CELL-LAX-004-B",
            "gnodeb_id": "gNB-US-LAX-401",
            "tac": "TAC-LAX-004",
            "region_name": "Port of Long Beach Pier T",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00B204",
            "qos_5qi": 82,
            "prb_utilization_pct": 52.0,
            "rsrp_dbm": -77.9,
            "sinr_db": 21.2,
            "pdcp_latency_ms": 4.2,
            "packet_loss_rate": 0.0003,
            "rrc_conn_failures": 1,
            "availability_pct": 99.997,
            "active_ue_count": 165,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 384,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-LAX-004-A",
        },
        {
            "cell_id": "CELL-LAX-004-C",
            "gnodeb_id": "gNB-US-LAX-402",
            "tac": "TAC-LAX-004",
            "region_name": "LAX Inland Warehouse District",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E404",
            "qos_5qi": 7,
            "prb_utilization_pct": 61.0,
            "rsrp_dbm": -82.0,
            "sinr_db": 17.8,
            "pdcp_latency_ms": 15.4,
            "packet_loss_rate": 0.0009,
            "rrc_conn_failures": 3,
            "availability_pct": 99.96,
            "active_ue_count": 480,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 390,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-LAX-004-D",
        },
        {
            "cell_id": "CELL-LAX-004-D",
            "gnodeb_id": "gNB-US-LAX-402",
            "tac": "TAC-LAX-004",
            "region_name": "LAX Silicon Beach Hub",
            "plmn_id": "310-410",
            "s_nssai_sst": 3,
            "s_nssai_sd": "0x00C404",
            "qos_5qi": 9,
            "prb_utilization_pct": 47.0,
            "rsrp_dbm": -79.5,
            "sinr_db": 18.9,
            "pdcp_latency_ms": 24.0,
            "packet_loss_rate": 0.0008,
            "rrc_conn_failures": 2,
            "availability_pct": 99.98,
            "active_ue_count": 3100,
            "max_bandwidth_mbps": 500,
            "available_bandwidth_mbps": 265,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-LAX-004-C",
        },
        # TAC-MIA-005 (Miami Port & Grid)
        {
            "cell_id": "CELL-MIA-005-A",
            "gnodeb_id": "gNB-US-MIA-501",
            "tac": "TAC-MIA-005",
            "region_name": "PortMiami Cruise Terminal",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E505",
            "qos_5qi": 7,
            "prb_utilization_pct": 66.0,
            "rsrp_dbm": -81.0,
            "sinr_db": 18.0,
            "pdcp_latency_ms": 16.5,
            "packet_loss_rate": 0.001,
            "rrc_conn_failures": 4,
            "availability_pct": 99.97,
            "active_ue_count": 520,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 340,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-MIA-005-C",
        },
        {
            "cell_id": "CELL-MIA-005-B",
            "gnodeb_id": "gNB-US-MIA-501",
            "tac": "TAC-MIA-005",
            "region_name": "Miami Energy Substation Grid",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A505",
            "qos_5qi": 82,
            "prb_utilization_pct": 86.5,
            "rsrp_dbm": -94.0,
            "sinr_db": 8.9,
            "pdcp_latency_ms": 13.5,
            "packet_loss_rate": 0.011,
            "rrc_conn_failures": 27,
            "availability_pct": 99.92,
            "active_ue_count": 290,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 108,
            "status": "DEGRADED",
            "neighbor_cell_id": "CELL-MIA-005-D",
        },
        {
            "cell_id": "CELL-MIA-005-C",
            "gnodeb_id": "gNB-US-MIA-502",
            "tac": "TAC-MIA-005",
            "region_name": "Miami Brickell Financial",
            "plmn_id": "310-410",
            "s_nssai_sst": 1,
            "s_nssai_sd": "0x00E505",
            "qos_5qi": 7,
            "prb_utilization_pct": 46.0,
            "rsrp_dbm": -77.5,
            "sinr_db": 21.0,
            "pdcp_latency_ms": 11.8,
            "packet_loss_rate": 0.0005,
            "rrc_conn_failures": 2,
            "availability_pct": 99.99,
            "active_ue_count": 340,
            "max_bandwidth_mbps": 1000,
            "available_bandwidth_mbps": 540,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-MIA-005-A",
        },
        {
            "cell_id": "CELL-MIA-005-D",
            "gnodeb_id": "gNB-US-MIA-502",
            "tac": "TAC-MIA-005",
            "region_name": "Miami Substation Redundant Sector",
            "plmn_id": "310-410",
            "s_nssai_sst": 2,
            "s_nssai_sd": "0x00A505",
            "qos_5qi": 82,
            "prb_utilization_pct": 39.0,
            "rsrp_dbm": -74.5,
            "sinr_db": 24.0,
            "pdcp_latency_ms": 3.6,
            "packet_loss_rate": 0.0002,
            "rrc_conn_failures": 1,
            "availability_pct": 99.997,
            "active_ue_count": 110,
            "max_bandwidth_mbps": 800,
            "available_bandwidth_mbps": 488,
            "status": "HEALTHY",
            "neighbor_cell_id": "CELL-MIA-005-B",
        },
    ]


def generate_cdrs(contracts: list[dict], cells: list[dict]) -> list[dict]:
    """
    Deterministically generates 250 3GPP / GSMA TAP3 CDR records.
    Some records are properly billed (`BILLED_OK`), while a subset of high-volume
    and 5G NR roaming records were rated by the legacy buggy rating script
    (producing ~$56,000+ in revenue leakage).
    """
    rng = random.Random(202605)
    active_contracts = [c for c in contracts if c["status"] == "ACTIVE"]
    apn_by_sst = {
        1: "corp.embb.5g.net",
        2: "enterprise.urllc.5g",
        3: "iot.fleet.mnc410",
    }
    qos_by_sst = {1: 7, 2: 82, 3: 9}
    roaming_partners = ["234-15", "262-01", "440-10"]  # Vodafone UK, Telekom DE, SoftBank JP

    cdrs: list[dict] = []
    for idx in range(1, 251):
        contract = active_contracts[(idx - 1) % len(active_contracts)]
        sst = contract["s_nssai_sst"]
        matching_cells = [
            c for c in cells
            if c["tac"] == contract["primary_tac"] and c["s_nssai_sst"] == sst
        ]
        cell = matching_cells[0] if matching_cells else cells[idx % len(cells)]

        # 30% of CDRs are roaming
        is_roaming = (idx % 10) in (0, 3, 7)
        roaming_plmn = roaming_partners[idx % len(roaming_partners)] if is_roaming else "310-410"
        rat_type = "NR_5G" if (idx % 5 != 0) else "EUTRAN_4G"

        # Data volumes between 25 GB and 185 GB per aggregated enterprise session CDR
        gb_volume = Decimal(str(rng.randint(25, 185))) + Decimal(str(rng.choice([0, 25, 50, 75]))) / Decimal("100")
        total_bytes = int(gb_volume * BYTES_PER_GB)
        uplink_bytes = int(total_bytes * 0.28)
        downlink_bytes = total_bytes - uplink_bytes

        base_rate = Decimal(str(contract["overage_rate_per_gb_usd"]))
        markup_pct = Decimal(str(contract["roaming_markup_pct"]))

        # True expected rating formula:
        # data_gb = Decimal(uplink_bytes + downlink_bytes) / Decimal(1024 ** 3)
        # multiplier = 1 + (markup_pct / 100) if roaming_plmn != "310-410" else 1
        data_gb_exact = Decimal(uplink_bytes + downlink_bytes) / BYTES_PER_GB
        multiplier = (
            Decimal("1.0") + (markup_pct / Decimal("100.0"))
            if roaming_plmn != "310-410"
            else Decimal("1.0")
        )
        expected_dec = (data_gb_exact * base_rate * multiplier).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        expected_amount = float(expected_dec)

        # Simulate historical billing anomalies on a deterministic subset of CDRs:
        # 1) All NR_5G roaming sessions missed the roaming markup in historical billing
        # 2) Every 4th session was rated using Terabytes (1024**4) instead of Gigabytes (1024**3)
        if is_roaming and rat_type == "NR_5G":
            billed_dec = (data_gb_exact * base_rate).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            rating_status = "UNDERBILLED_LEAKAGE"
        elif idx % 4 == 0:
            buggy_gb = Decimal(uplink_bytes + downlink_bytes) / Decimal(1024 ** 4)
            billed_dec = (buggy_gb * base_rate * multiplier).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            rating_status = "UNDERBILLED_LEAKAGE"
        else:
            billed_dec = expected_dec
            rating_status = "BILLED_OK"

        billed_amount = float(billed_dec)

        day = (idx % 28) + 1
        hour = idx % 24
        cdrs.append(
            {
                "cdr_id": f"CDR-202605-{idx:04d}",
                "contract_id": contract["contract_id"],
                "imsi": f"3104109900{idx:05d}",
                "msisdn": f"+1212555{idx:04d}",
                "imei_tac": f"35982110{idx % 90 + 10:02d}",
                "charging_id": 880000 + idx,
                "cell_id": cell["cell_id"],
                "tac": cell["tac"],
                "apn_dnn": apn_by_sst[sst],
                "rat_type": rat_type,
                "s_nssai_sst": sst,
                "qos_5qi": qos_by_sst[sst],
                "uplink_bytes": uplink_bytes,
                "downlink_bytes": downlink_bytes,
                "duration_sec": rng.randint(600, 14400),
                "roaming_plmn": roaming_plmn,
                "base_rate_per_gb_usd": float(base_rate),
                "roaming_markup_pct": float(markup_pct),
                "billed_amount_usd": billed_amount,
                "expected_amount_usd": expected_amount,
                "rating_status": rating_status,
                "timestamp_utc": f"2026-05-{day:02d}T{hour:02d}:15:00Z",
            }
        )
    return cdrs


def get_sales_orders() -> list[dict]:
    """
    Returns 15 TMF622 B2B Product Orders across the 5 TACs.
    Includes orders that:
    - Target healthy cells with plenty of bandwidth -> READY_TO_ACTIVATE
    - Target congested/degraded cells where a healthy neighbor cell in the same TAC+SST exists -> REQUIRES_SLICE_REMEDIATION
    - Target impossible bandwidth/latency constraints -> REJECTED / UNFEASIBLE
    """
    return [
        {
            "order_id": "ORD-TMF622-9001",
            "contract_id": "CTR-B2B-1002",
            "enterprise_name": "Goldman Sachs Low-Latency Trading Backup",
            "account_tier": "STRATEGIC_GLOBAL",
            "target_tac": "TAC-NY-001",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A101",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 150,
            "max_latency_ms": 5.0,
            "estimated_mrr_usd": 42000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Primary sector CELL-NY-001-B degraded (14.8ms); neighbor CELL-NY-001-C has 3.4ms & 448 Mbps free.",
            "created_at": "2026-05-18T09:00:00Z",
        },
        {
            "order_id": "ORD-TMF622-9002",
            "contract_id": "CTR-B2B-1001",
            "enterprise_name": "Mayo Clinic Connected Ambulance URLLC",
            "account_tier": "STRATEGIC_GLOBAL",
            "target_tac": "TAC-CHI-002",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A102",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 120,
            "max_latency_ms": 6.0,
            "estimated_mrr_usd": 36500.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Primary sector CELL-CHI-002-B congested (93.4% PRB); steer to CELL-CHI-002-A (48.5% PRB, 4.1ms).",
            "created_at": "2026-05-18T09:30:00Z",
        },
        {
            "order_id": "ORD-TMF622-9003",
            "contract_id": "CTR-B2B-1003",
            "enterprise_name": "Maersk Smart Port Autonomous Cranes",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-LAX-004",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00B204",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 180,
            "max_latency_ms": 8.0,
            "estimated_mrr_usd": 29000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Both LAX SST=2 cells are healthy and under 65% PRB utilization.",
            "created_at": "2026-05-18T10:15:00Z",
        },
        {
            "order_id": "ORD-TMF622-9004",
            "contract_id": "CTR-B2B-1004",
            "enterprise_name": "Delta Air Lines Tarmac Operations eMBB",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-DAL-003",
            "requested_slice_sst": 1,
            "requested_slice_sd": "0x00E301",
            "requested_qos_5qi": 7,
            "requested_bandwidth_mbps": 220,
            "max_latency_ms": 20.0,
            "estimated_mrr_usd": 24500.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-DAL-003-A congested (89% PRB, 29.5ms); neighbor CELL-DAL-003-B healthy (49% PRB, 12.6ms).",
            "created_at": "2026-05-18T11:00:00Z",
        },
        {
            "order_id": "ORD-TMF622-9005",
            "contract_id": "CTR-B2B-1009",
            "enterprise_name": "Siemens Smart Grid Automated Substation",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-MIA-005",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A505",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 140,
            "max_latency_ms": 7.0,
            "estimated_mrr_usd": 27500.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-MIA-005-B degraded (86.5% PRB, 13.5ms); neighbor CELL-MIA-005-D healthy (39% PRB, 3.6ms).",
            "created_at": "2026-05-18T11:45:00Z",
        },
        {
            "order_id": "ORD-TMF622-9006",
            "contract_id": "CTR-B2B-1006",
            "enterprise_name": "NBCUniversal Live 8K Broadcast Uplink",
            "account_tier": "GOLD",
            "target_tac": "TAC-NY-001",
            "requested_slice_sst": 1,
            "requested_slice_sd": "0x00E101",
            "requested_qos_5qi": 7,
            "requested_bandwidth_mbps": 250,
            "max_latency_ms": 18.0,
            "estimated_mrr_usd": 21000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-NY-001-A congested (91.5% PRB, 26.4ms); neighbor CELL-NY-001-D healthy (51% PRB, 11.2ms).",
            "created_at": "2026-05-18T12:20:00Z",
        },
        {
            "order_id": "ORD-TMF622-9007",
            "contract_id": "CTR-B2B-1005",
            "enterprise_name": "Ford Global Connected Fleet Telemetry",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-CHI-002",
            "requested_slice_sst": 3,
            "requested_slice_sd": "0x00C302",
            "requested_qos_5qi": 9,
            "requested_bandwidth_mbps": 90,
            "max_latency_ms": 45.0,
            "estimated_mrr_usd": 18500.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-CHI-002-C healthy with 190 Mbps available capacity.",
            "created_at": "2026-05-18T13:10:00Z",
        },
        {
            "order_id": "ORD-TMF622-9008",
            "contract_id": "CTR-B2B-1007",
            "enterprise_name": "Walmart Cold-Chain Logistics mIoT",
            "account_tier": "GOLD",
            "target_tac": "TAC-DAL-003",
            "requested_slice_sst": 3,
            "requested_slice_sd": "0x00C303",
            "requested_qos_5qi": 9,
            "requested_bandwidth_mbps": 110,
            "max_latency_ms": 50.0,
            "estimated_mrr_usd": 16200.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-DAL-003-C healthy (58% PRB, 31.0ms latency).",
            "created_at": "2026-05-18T14:00:00Z",
        },
        {
            "order_id": "ORD-TMF622-9009",
            "contract_id": "CTR-B2B-1008",
            "enterprise_name": "Royal Caribbean Smart Cruise Port Network",
            "account_tier": "GOLD",
            "target_tac": "TAC-MIA-005",
            "requested_slice_sst": 1,
            "requested_slice_sd": "0x00E505",
            "requested_qos_5qi": 7,
            "requested_bandwidth_mbps": 200,
            "max_latency_ms": 22.0,
            "estimated_mrr_usd": 19500.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Both MIA SST=1 cells are healthy and meet 22ms SLA.",
            "created_at": "2026-05-18T14:30:00Z",
        },
        {
            "order_id": "ORD-TMF622-9010",
            "contract_id": "CTR-B2B-1010",
            "enterprise_name": "DHL Autonomous Warehouse Robotics",
            "account_tier": "SILVER",
            "target_tac": "TAC-LAX-004",
            "requested_slice_sst": 1,
            "requested_slice_sd": "0x00E404",
            "requested_qos_5qi": 7,
            "requested_bandwidth_mbps": 160,
            "max_latency_ms": 25.0,
            "estimated_mrr_usd": 14000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-LAX-004-C healthy with 390 Mbps free.",
            "created_at": "2026-05-18T15:00:00Z",
        },
        {
            "order_id": "ORD-TMF622-9011",
            "contract_id": "CTR-B2B-1002",
            "enterprise_name": "Goldman Sachs Ultra-HFT Sub-Millisecond Link",
            "account_tier": "STRATEGIC_GLOBAL",
            "target_tac": "TAC-NY-001",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A101",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 950,
            "max_latency_ms": 1.2,
            "estimated_mrr_usd": 55000.0,
            "sales_stage": "TECHNICAL_FEASIBILITY",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Exceeds 5G NR air-interface physical latency & bandwidth capacity on all NY cells.",
            "created_at": "2026-05-18T15:45:00Z",
        },
        {
            "order_id": "ORD-TMF622-9012",
            "contract_id": "CTR-B2B-1004",
            "enterprise_name": "Delta Air Lines Cargo Drone Telemetry",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-DAL-003",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A303",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 130,
            "max_latency_ms": 6.0,
            "estimated_mrr_usd": 22000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-DAL-003-D healthy (41% PRB, 3.9ms latency).",
            "created_at": "2026-05-18T16:15:00Z",
        },
        {
            "order_id": "ORD-TMF622-9013",
            "contract_id": "CTR-B2B-1003",
            "enterprise_name": "Maersk Smart Port IoT Reefer Containers",
            "account_tier": "PLATINUM",
            "target_tac": "TAC-LAX-004",
            "requested_slice_sst": 3,
            "requested_slice_sd": "0x00C404",
            "requested_qos_5qi": 9,
            "requested_bandwidth_mbps": 85,
            "max_latency_ms": 40.0,
            "estimated_mrr_usd": 15800.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-LAX-004-D healthy (47% PRB, 24.0ms latency).",
            "created_at": "2026-05-18T16:45:00Z",
        },
        {
            "order_id": "ORD-TMF622-9014",
            "contract_id": "CTR-B2B-1001",
            "enterprise_name": "Mayo Clinic Remote Robotic Surgery Trial",
            "account_tier": "STRATEGIC_GLOBAL",
            "target_tac": "TAC-CHI-002",
            "requested_slice_sst": 2,
            "requested_slice_sd": "0x00A102",
            "requested_qos_5qi": 82,
            "requested_bandwidth_mbps": 750,
            "max_latency_ms": 2.0,
            "estimated_mrr_usd": 48000.0,
            "sales_stage": "TECHNICAL_FEASIBILITY",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "Requires 750 Mbps @ 2.0ms; exceeds available bandwidth on all CHI SST=2 sectors.",
            "created_at": "2026-05-18T17:10:00Z",
        },
        {
            "order_id": "ORD-TMF622-9015",
            "contract_id": "CTR-B2B-1006",
            "enterprise_name": "NBCUniversal Stadium Fan AR Experience",
            "account_tier": "GOLD",
            "target_tac": "TAC-CHI-002",
            "requested_slice_sst": 1,
            "requested_slice_sd": "0x00E202",
            "requested_qos_5qi": 7,
            "requested_bandwidth_mbps": 200,
            "max_latency_ms": 20.0,
            "estimated_mrr_usd": 19000.0,
            "sales_stage": "CLOSED_WON_PENDING_PROV",
            "order_status": "PENDING_FEASIBILITY",
            "notes": "CELL-CHI-002-D healthy (55.2% PRB, 14.0ms latency).",
            "created_at": "2026-05-18T17:40:00Z",
        },
    ]


def get_ran_alarms() -> list[dict]:
    return [
        {
            "alarm_id": "ALM-3GPP-8001",
            "timestamp_utc": "2026-05-18T08:12:04Z",
            "severity": "CRITICAL",
            "alarm_type": "QOS_SLA_LATENCY_VIOLATION",
            "standard_ref": "3GPP TS 28.532 / TS 28.552",
            "gnodeb_id": "gNB-US-NY-101",
            "cell_id": "CELL-NY-001-B",
            "tac": "TAC-NY-001",
            "s_nssai": "SST:2 / SD:0x00A101",
            "metric_name": "pdcp_latency_ms",
            "metric_value": 14.8,
            "threshold_value": 5.0,
            "affected_contract_id": "CTR-B2B-1002",
            "probable_cause": "UL/DL PRB contention (88.2%) and microwave backhaul jitter in NY Financial District",
            "recommended_action": "Steer URLLC slice SST=2 traffic to neighbor CELL-NY-001-C (3.4ms PDCP latency)",
        },
        {
            "alarm_id": "ALM-3GPP-8002",
            "timestamp_utc": "2026-05-18T08:19:41Z",
            "severity": "CRITICAL",
            "alarm_type": "PRB_CONGESTION_AND_SLA_BREACH",
            "standard_ref": "3GPP TS 28.552",
            "gnodeb_id": "gNB-US-CHI-202",
            "cell_id": "CELL-CHI-002-B",
            "tac": "TAC-CHI-002",
            "s_nssai": "SST:2 / SD:0x00A102",
            "metric_name": "prb_utilization_pct",
            "metric_value": 93.4,
            "threshold_value": 80.0,
            "affected_contract_id": "CTR-B2B-1001",
            "probable_cause": "High RRC connection surge and PRB exhaustion on Chicago Loop URLLC slice",
            "recommended_action": "Trigger RAN slice PRB reallocation and offload to CELL-CHI-002-A",
        },
        {
            "alarm_id": "ALM-3GPP-8003",
            "timestamp_utc": "2026-05-18T08:45:10Z",
            "severity": "MAJOR",
            "alarm_type": "PRB_UTILIZATION_THRESHOLD_EXCEEDED",
            "standard_ref": "3GPP TS 28.552",
            "gnodeb_id": "gNB-US-NY-101",
            "cell_id": "CELL-NY-001-A",
            "tac": "TAC-NY-001",
            "s_nssai": "SST:1 / SD:0x00E101",
            "metric_name": "pdcp_latency_ms",
            "metric_value": 26.4,
            "threshold_value": 18.0,
            "affected_contract_id": "CTR-B2B-1006",
            "probable_cause": "Live 8K uplink burst saturating eMBB PRB pool (91.5%)",
            "recommended_action": "Rebalance eMBB slice load to neighbor CELL-NY-001-D",
        },
        {
            "alarm_id": "ALM-3GPP-8004",
            "timestamp_utc": "2026-05-18T09:05:22Z",
            "severity": "MAJOR",
            "alarm_type": "QOS_SLA_LATENCY_VIOLATION",
            "standard_ref": "3GPP TS 28.532",
            "gnodeb_id": "gNB-US-DAL-301",
            "cell_id": "CELL-DAL-003-A",
            "tac": "TAC-DAL-003",
            "s_nssai": "SST:1 / SD:0x00E301",
            "metric_name": "pdcp_latency_ms",
            "metric_value": 29.5,
            "threshold_value": 20.0,
            "affected_contract_id": "CTR-B2B-1004",
            "probable_cause": "Tarmac East sector congestion (89.0% PRB) during aircraft turnarounds",
            "recommended_action": "Handover enterprise eMBB bearers to CELL-DAL-003-B",
        },
        {
            "alarm_id": "ALM-3GPP-8005",
            "timestamp_utc": "2026-05-18T09:33:50Z",
            "severity": "MAJOR",
            "alarm_type": "QOS_SLA_LATENCY_VIOLATION",
            "standard_ref": "3GPP TS 28.532",
            "gnodeb_id": "gNB-US-MIA-501",
            "cell_id": "CELL-MIA-005-B",
            "tac": "TAC-MIA-005",
            "s_nssai": "SST:2 / SD:0x00A505",
            "metric_name": "pdcp_latency_ms",
            "metric_value": 13.5,
            "threshold_value": 7.0,
            "affected_contract_id": "CTR-B2B-1009",
            "probable_cause": "Substation telemetry interference (SINR 8.9 dB) & 86.5% PRB load",
            "recommended_action": "Steer URLLC substation slice to CELL-MIA-005-D (3.6ms latency)",
        },
        {
            "alarm_id": "ALM-BSS-8006",
            "timestamp_utc": "2026-05-18T10:02:15Z",
            "severity": "CRITICAL",
            "alarm_type": "TAP3_CDR_REVENUE_ASSURANCE_ANOMALY",
            "standard_ref": "GSMA TAP3.12 / 3GPP TS 32.298",
            "gnodeb_id": "CHF-CORE-US-01",
            "cell_id": "GLOBAL-CHF",
            "tac": "MULTI-TAC",
            "s_nssai": "ALL",
            "metric_name": "unbilled_roaming_and_unit_scaling_gap_pct",
            "metric_value": 34.8,
            "threshold_value": 1.0,
            "affected_contract_id": "MULTIPLE",
            "probable_cause": "CHF rating engine unit conversion scaling error and skipped NR_5G roaming markup",
            "recommended_action": "Audit src/services/cdr_rating.py against 3GPP TS 32.298 & GSMA TAP3 rules",
        },
    ]


def seed_all(db_path: Path = DB_PATH) -> dict:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE tariff_plans (
            plan_id TEXT PRIMARY KEY,
            plan_name TEXT NOT NULL,
            s_nssai_sst INTEGER NOT NULL,
            slice_type TEXT NOT NULL,
            default_qos_5qi INTEGER NOT NULL,
            base_rate_per_gb_usd REAL NOT NULL,
            roaming_5g_zone_a_markup_pct REAL NOT NULL,
            roaming_4g_zone_a_markup_pct REAL NOT NULL,
            min_committed_acv_usd REAL NOT NULL
        );

        CREATE TABLE b2b_contracts (
            contract_id TEXT PRIMARY KEY,
            enterprise_name TEXT NOT NULL,
            account_tier TEXT NOT NULL,
            sales_rep_id TEXT NOT NULL,
            primary_tac TEXT NOT NULL,
            s_nssai_sst INTEGER NOT NULL,
            s_nssai_sd TEXT NOT NULL,
            annual_contract_value_usd REAL NOT NULL,
            committed_latency_ms REAL NOT NULL,
            committed_availability_pct REAL NOT NULL,
            sla_penalty_per_hour_usd REAL NOT NULL,
            included_data_tb REAL NOT NULL,
            overage_rate_per_gb_usd REAL NOT NULL,
            roaming_markup_pct REAL NOT NULL,
            status TEXT NOT NULL,
            breach_hours_mtd REAL NOT NULL
        );

        CREATE TABLE ran_telemetry (
            cell_id TEXT PRIMARY KEY,
            gnodeb_id TEXT NOT NULL,
            tac TEXT NOT NULL,
            region_name TEXT NOT NULL,
            plmn_id TEXT NOT NULL,
            s_nssai_sst INTEGER NOT NULL,
            s_nssai_sd TEXT NOT NULL,
            qos_5qi INTEGER NOT NULL,
            prb_utilization_pct REAL NOT NULL,
            rsrp_dbm REAL NOT NULL,
            sinr_db REAL NOT NULL,
            pdcp_latency_ms REAL NOT NULL,
            packet_loss_rate REAL NOT NULL,
            rrc_conn_failures INTEGER NOT NULL,
            availability_pct REAL NOT NULL,
            active_ue_count INTEGER NOT NULL,
            max_bandwidth_mbps INTEGER NOT NULL,
            available_bandwidth_mbps INTEGER NOT NULL,
            status TEXT NOT NULL,
            neighbor_cell_id TEXT NOT NULL
        );

        CREATE TABLE cdr_records (
            cdr_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            imsi TEXT NOT NULL,
            msisdn TEXT NOT NULL,
            imei_tac TEXT NOT NULL,
            charging_id INTEGER NOT NULL,
            cell_id TEXT NOT NULL,
            tac TEXT NOT NULL,
            apn_dnn TEXT NOT NULL,
            rat_type TEXT NOT NULL,
            s_nssai_sst INTEGER NOT NULL,
            qos_5qi INTEGER NOT NULL,
            uplink_bytes INTEGER NOT NULL,
            downlink_bytes INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            roaming_plmn TEXT NOT NULL,
            base_rate_per_gb_usd REAL NOT NULL,
            roaming_markup_pct REAL NOT NULL,
            billed_amount_usd REAL NOT NULL,
            expected_amount_usd REAL NOT NULL,
            rating_status TEXT NOT NULL,
            timestamp_utc TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES b2b_contracts(contract_id),
            FOREIGN KEY (cell_id) REFERENCES ran_telemetry(cell_id)
        );

        CREATE TABLE tmf622_sales_orders (
            order_id TEXT PRIMARY KEY,
            contract_id TEXT NOT NULL,
            enterprise_name TEXT NOT NULL,
            account_tier TEXT NOT NULL,
            target_tac TEXT NOT NULL,
            requested_slice_sst INTEGER NOT NULL,
            requested_slice_sd TEXT NOT NULL,
            requested_qos_5qi INTEGER NOT NULL,
            requested_bandwidth_mbps INTEGER NOT NULL,
            max_latency_ms REAL NOT NULL,
            estimated_mrr_usd REAL NOT NULL,
            sales_stage TEXT NOT NULL,
            order_status TEXT NOT NULL,
            notes TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (contract_id) REFERENCES b2b_contracts(contract_id)
        );
        """
    )

    tariffs = get_tariff_plans()
    contracts = get_b2b_contracts()
    cells = get_ran_cells()
    cdrs = generate_cdrs(contracts, cells)
    orders = get_sales_orders()
    alarms = get_ran_alarms()

    cur.executemany(
        """
        INSERT INTO tariff_plans VALUES (
            :plan_id, :plan_name, :s_nssai_sst, :slice_type, :default_qos_5qi,
            :base_rate_per_gb_usd, :roaming_5g_zone_a_markup_pct,
            :roaming_4g_zone_a_markup_pct, :min_committed_acv_usd
        )
        """,
        tariffs,
    )

    cur.executemany(
        """
        INSERT INTO b2b_contracts VALUES (
            :contract_id, :enterprise_name, :account_tier, :sales_rep_id,
            :primary_tac, :s_nssai_sst, :s_nssai_sd, :annual_contract_value_usd,
            :committed_latency_ms, :committed_availability_pct,
            :sla_penalty_per_hour_usd, :included_data_tb, :overage_rate_per_gb_usd,
            :roaming_markup_pct, :status, :breach_hours_mtd
        )
        """,
        contracts,
    )

    cur.executemany(
        """
        INSERT INTO ran_telemetry VALUES (
            :cell_id, :gnodeb_id, :tac, :region_name, :plmn_id, :s_nssai_sst,
            :s_nssai_sd, :qos_5qi, :prb_utilization_pct, :rsrp_dbm, :sinr_db,
            :pdcp_latency_ms, :packet_loss_rate, :rrc_conn_failures,
            :availability_pct, :active_ue_count, :max_bandwidth_mbps,
            :available_bandwidth_mbps, :status, :neighbor_cell_id
        )
        """,
        cells,
    )

    cur.executemany(
        """
        INSERT INTO cdr_records VALUES (
            :cdr_id, :contract_id, :imsi, :msisdn, :imei_tac, :charging_id,
            :cell_id, :tac, :apn_dnn, :rat_type, :s_nssai_sst, :qos_5qi,
            :uplink_bytes, :downlink_bytes, :duration_sec, :roaming_plmn,
            :base_rate_per_gb_usd, :roaming_markup_pct, :billed_amount_usd,
            :expected_amount_usd, :rating_status, :timestamp_utc
        )
        """,
        cdrs,
    )

    cur.executemany(
        """
        INSERT INTO tmf622_sales_orders VALUES (
            :order_id, :contract_id, :enterprise_name, :account_tier,
            :target_tac, :requested_slice_sst, :requested_slice_sd,
            :requested_qos_5qi, :requested_bandwidth_mbps, :max_latency_ms,
            :estimated_mrr_usd, :sales_stage, :order_status, :notes, :created_at
        )
        """,
        orders,
    )

    conn.commit()
    conn.close()

    # Export CSV snapshots
    def write_csv(filename: str, rows: list[dict]) -> None:
        if not rows:
            return
        out_file = EXPORTS_DIR / filename
        with out_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    write_csv("b2b_contracts.csv", contracts)
    write_csv("sample_cdrs.csv", cdrs[:50])
    write_csv("sales_orders.csv", orders)

    # Write JSONL RAN & BSS alarms
    alarms_file = LOGS_DIR / "ran_alarms.jsonl"
    with alarms_file.open("w", encoding="utf-8") as f:
        for alarm in alarms:
            f.write(json.dumps(alarm) + "\n")

    total_expected = sum(Decimal(str(c["expected_amount_usd"])) for c in cdrs)
    total_billed = sum(Decimal(str(c["billed_amount_usd"])) for c in cdrs)
    leakage = total_expected - total_billed

    summary = {
        "db_path": str(db_path),
        "contracts_count": len(contracts),
        "ran_cells_count": len(cells),
        "cdr_records_count": len(cdrs),
        "sales_orders_count": len(orders),
        "alarms_count": len(alarms),
        "total_expected_usd": float(total_expected),
        "total_billed_usd": float(total_billed),
        "revenue_leakage_usd": float(leakage),
    }
    return summary


if __name__ == "__main__":
    stats = seed_all()
    print(
        f"[Telecom Nexus Seed] Seeded {stats['contracts_count']} B2B contracts, "
        f"{stats['ran_cells_count']} 5G RAN cells, {stats['cdr_records_count']} CDRs "
        f"(Unbilled Leakage: ${stats['revenue_leakage_usd']:,.2f}), and "
        f"{stats['sales_orders_count']} TMF622 sales orders into {stats['db_path']}."
    )
