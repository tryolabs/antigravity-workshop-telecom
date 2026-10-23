"""Pydantic domain models for 3GPP RAN Telemetry, TAP3 CDRs, B2B Contracts, and TMF622 Orders."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RanCellTelemetry(BaseModel):
    cell_id: str
    gnodeb_id: str
    tac: str
    region_name: str
    plmn_id: str
    s_nssai_sst: int = Field(..., description="3GPP Slice/Service Type: 1=eMBB, 2=URLLC, 3=mIoT")
    s_nssai_sd: str
    qos_5qi: int
    prb_utilization_pct: float
    rsrp_dbm: float
    sinr_db: float
    pdcp_latency_ms: float
    packet_loss_rate: float
    rrc_conn_failures: int
    availability_pct: float
    active_ue_count: int
    max_bandwidth_mbps: int
    available_bandwidth_mbps: int
    status: str
    neighbor_cell_id: str


class B2BContract(BaseModel):
    contract_id: str
    enterprise_name: str
    account_tier: str
    sales_rep_id: str
    primary_tac: str
    s_nssai_sst: int
    s_nssai_sd: str
    annual_contract_value_usd: float
    committed_latency_ms: float
    committed_availability_pct: float
    sla_penalty_per_hour_usd: float
    included_data_tb: float
    overage_rate_per_gb_usd: float
    roaming_markup_pct: float
    status: str
    breach_hours_mtd: float


class CdrRecord(BaseModel):
    cdr_id: str
    contract_id: str
    imsi: str
    msisdn: str
    imei_tac: str
    charging_id: int
    cell_id: str
    tac: str
    apn_dnn: str
    rat_type: str
    s_nssai_sst: int
    qos_5qi: int
    uplink_bytes: int
    downlink_bytes: int
    duration_sec: int
    roaming_plmn: str
    base_rate_per_gb_usd: float
    roaming_markup_pct: float
    billed_amount_usd: float
    expected_amount_usd: float
    rating_status: str
    timestamp_utc: str


class Tmf622Order(BaseModel):
    order_id: str
    contract_id: str
    enterprise_name: str
    account_tier: str
    target_tac: str
    requested_slice_sst: int
    requested_slice_sd: str
    requested_qos_5qi: int
    requested_bandwidth_mbps: int
    max_latency_ms: float
    estimated_mrr_usd: float
    sales_stage: str
    order_status: str
    notes: str
    created_at: str


class FeasibilityCheckRequest(BaseModel):
    order_id: str


class SliceRemediateRequest(BaseModel):
    order_id: str
    steering_mode: str = Field(
        default="NEIGHBOR_OFFLOAD_AND_PRB_REALLOC",
        description="Traffic steering or dynamic PRB slice reallocation strategy",
    )
