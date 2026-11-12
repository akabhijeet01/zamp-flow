"""
Data models for the Autonomous AP Invoice Processing & PO Matching Engine.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class LineItem:
    description: str
    quantity: float
    unit_price: float
    total_price: float
    sku: Optional[str] = None
    po_line_match: Optional[str] = None
    price_variance_pct: Optional[float] = None
    qty_variance: Optional[float] = None
    status: str = "MATCHED"  # MATCHED, VARIANCE, UNMATCHED

@dataclass
class ExtractedInvoice:
    invoice_number: str
    vendor_name: str
    vendor_address: Optional[str] = None
    vendor_tax_id: Optional[str] = None
    invoice_date: str = ""
    due_date: str = ""
    po_number: Optional[str] = None
    line_items: List[LineItem] = field(default_factory=list)
    subtotal: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    currency: str = "USD"
    bank_account_number: Optional[str] = None
    bank_routing_number: Optional[str] = None
    raw_text: str = ""

@dataclass
class StageResult:
    stage_id: int
    stage_name: str
    status: str  # SUCCESS, WARNING, FAILED
    duration_ms: float
    details: Dict[str, Any]
    message: str

@dataclass
class FinalDecision:
    decision: str  # APPROVED, FLAGGED_EXCEPTION, REJECTED
    confidence_score: float  # e.g. 0.99
    risk_level: str  # LOW, MEDIUM, HIGH
    summary_headline: str
    reasoning_points: List[str]
    suggested_action: str
    tolerance_applied: Dict[str, Any]
    erp_action_payload: Optional[Dict[str, Any]] = None

@dataclass
class RunRecord:
    run_id: str
    timestamp: str
    scenario_id: Optional[str]
    filename: str
    vendor_name: str
    invoice_number: str
    po_number: Optional[str]
    total_amount: float
    decision: str
    confidence_score: float
    risk_level: str
    summary_headline: str
    stages: List[Dict[str, Any]]
    extracted_invoice: Dict[str, Any]
    reasoning_points: List[str]
    human_override: Optional[Dict[str, Any]] = None
    processing_time_ms: float = 0.0
