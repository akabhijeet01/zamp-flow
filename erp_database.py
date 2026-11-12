"""
Simulated ERP & Procurement Master Database.
Includes:
- Approved Vendor Master (tax IDs, banking details, terms)
- Purchase Orders (line item contracts, historical draw-downs, remaining balances)
- Past Invoice Fingerprint Registry (for duplicate fraud detection)
"""
import copy
from typing import Dict, Any, Optional, List

# Initial reference data
DEFAULT_VENDORS = {
    "VEND-001": {
        "vendor_id": "VEND-001",
        "name": "Apex Data Systems",
        "tax_id": "US-84-9210442",
        "status": "APPROVED",
        "payment_terms": "Net 30",
        "approved_bank_routing": "121000358",
        "approved_bank_account_last4": "4892",
        "category": "Software & Cloud Services",
    },
    "VEND-002": {
        "vendor_id": "VEND-002",
        "name": "Meridian Logistics Global",
        "tax_id": "US-13-8829104",
        "status": "APPROVED",
        "payment_terms": "Net 15",
        "approved_bank_routing": "026009593",
        "approved_bank_account_last4": "9912",
        "category": "Freight & Warehousing",
    },
    "VEND-003": {
        "vendor_id": "VEND-003",
        "name": "CloudScale Infrastructure Inc.",
        "tax_id": "US-94-1182390",
        "status": "APPROVED",
        "payment_terms": "Net 30",
        "approved_bank_routing": "322271627",
        "approved_bank_account_last4": "3341",
        "category": "Cloud Hosting & Compute",
    },
    "VEND-004": {
        "vendor_id": "VEND-004",
        "name": "CyberShield Security Corp",
        "tax_id": "US-55-9012431",
        "status": "APPROVED",
        "payment_terms": "Net 30",
        "approved_bank_routing": "071000288",
        "approved_bank_account_last4": "7710",
        "category": "Cybersecurity & Compliance",
    }
}

DEFAULT_PURCHASE_ORDERS = {
    "PO-9042": {
        "po_number": "PO-9042",
        "vendor_id": "VEND-001",
        "vendor_name": "Apex Data Systems",
        "total_amount": 7500.00,
        "already_invoiced": 0.00,
        "remaining_balance": 7500.00,
        "status": "OPEN",
        "created_date": "2026-10-15",
        "buyer": "DevOps Engineering",
        "line_items": [
            {
                "line_no": 1,
                "sku": "DATA-ENG-PRO",
                "description": "Enterprise Data Analytics License (Annual)",
                "quantity": 1,
                "unit_price": 5000.00,
                "total": 5000.00
            },
            {
                "line_no": 2,
                "sku": "DATA-SUP-PREM",
                "description": "24/7 Dedicated Infrastructure Support Tier",
                "quantity": 1,
                "unit_price": 2500.00,
                "total": 2500.00
            }
        ]
    },
    "PO-8810": {
        "po_number": "PO-8810",
        "vendor_id": "VEND-002",
        "vendor_name": "Meridian Logistics Global",
        "total_amount": 4200.00,
        "already_invoiced": 0.00,
        "remaining_balance": 4200.00,
        "status": "OPEN",
        "created_date": "2026-10-20",
        "buyer": "Supply Chain Ops",
        "line_items": [
            {
                "line_no": 1,
                "sku": "FREIGHT-EXP-01",
                "description": "Cross-Country Pallet Freight Handling",
                "quantity": 2,
                "unit_price": 1200.00,
                "total": 2400.00
            },
            {
                "line_no": 2,
                "sku": "STORAGE-TEMP-04",
                "description": "Temperature Controlled Warehousing (Mo.)",
                "quantity": 1,
                "unit_price": 1800.00,
                "total": 1800.00
            }
        ]
    },
    "PO-7020": {
        "po_number": "PO-7020",
        "vendor_id": "VEND-003",
        "vendor_name": "CloudScale Infrastructure Inc.",
        "total_amount": 25000.00,
        "already_invoiced": 15000.00,  # Prior milestone 1 already drawn
        "remaining_balance": 10000.00,  # Remaining budget for Milestone 2 & 3
        "status": "OPEN_PARTIALLY_INVOICED",
        "created_date": "2026-09-01",
        "buyer": "Platform Ops",
        "line_items": [
            {
                "line_no": 1,
                "sku": "CLOUD-RES-COMPUTE",
                "description": "High Performance Reserved GPU Cluster - Q4",
                "quantity": 1,
                "unit_price": 25000.00,
                "total": 25000.00
            }
        ]
    },
    "PO-6640": {
        "po_number": "PO-6640",
        "vendor_id": "VEND-004",
        "vendor_name": "CyberShield Security Corp",
        "total_amount": 8800.00,
        "already_invoiced": 0.00,
        "remaining_balance": 8800.00,
        "status": "OPEN",
        "created_date": "2026-10-28",
        "buyer": "Security & Risk",
        "line_items": [
            {
                "line_no": 1,
                "sku": "SOC2-AUDIT-PREP",
                "description": "SOC2 Type II Continuous Audit & Evidence Collector",
                "quantity": 1,
                "unit_price": 8800.00,
                "total": 8800.00
            }
        ]
    }
}

# Policy Configuration
COMPANY_POLICY = {
    "price_tolerance_pct": 3.0,      # Max 3% price variance allowed without manager override
    "price_tolerance_usd": 50.00,    # Max $50 absolute dollar variance
    "require_po_above_usd": 500.00,  # Any invoice above $500 requires a matching PO
    "duplicate_lookback_days": 90,
    "require_bank_account_match": True,
}

class ERPDatabase:
    def __init__(self):
        self.vendors = copy.deepcopy(DEFAULT_VENDORS)
        self.purchase_orders = copy.deepcopy(DEFAULT_PURCHASE_ORDERS)
        # Register an already paid invoice to demonstrate duplicate detection
        self.processed_invoices_registry = {
            "INV-CS-9941": {
                "vendor_name": "CyberShield Security Corp",
                "invoice_number": "INV-CS-9941",
                "po_number": "PO-6640",
                "total_amount": 8800.00,
                "processed_date": "2026-11-04",
                "status": "PAID"
            }
        }
        self.run_history: List[Dict[str, Any]] = []

    def reset(self):
        self.vendors = copy.deepcopy(DEFAULT_VENDORS)
        self.purchase_orders = copy.deepcopy(DEFAULT_PURCHASE_ORDERS)
        self.processed_invoices_registry = {
            "INV-CS-9941": {
                "vendor_name": "CyberShield Security Corp",
                "invoice_number": "INV-CS-9941",
                "po_number": "PO-6640",
                "total_amount": 8800.00,
                "processed_date": "2026-11-04",
                "status": "PAID"
            }
        }
        self.run_history = []

    def find_vendor_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        clean_name = name.lower().strip()
        for v in self.vendors.values():
            if v["name"].lower() in clean_name or clean_name in v["name"].lower():
                return v
        return None

    def get_po(self, po_number: str) -> Optional[Dict[str, Any]]:
        clean_po = po_number.strip().upper()
        return self.purchase_orders.get(clean_po)

    def find_active_pos_for_vendor(self, vendor_name: str) -> List[Dict[str, Any]]:
        clean_name = vendor_name.lower().strip()
        matches = []
        for po in self.purchase_orders.values():
            if (clean_name in po["vendor_name"].lower() or po["vendor_name"].lower() in clean_name) and po["remaining_balance"] > 0:
                matches.append(po)
        return matches

    def record_run(self, run_dict: Dict[str, Any]):
        self.run_history.insert(0, run_dict)

    def record_approved_invoice(self, invoice_number: str, vendor_name: str, po_number: Optional[str], amount: float):
        self.processed_invoices_registry[invoice_number.upper()] = {
            "vendor_name": vendor_name,
            "invoice_number": invoice_number,
            "po_number": po_number,
            "total_amount": amount,
            "processed_date": "2026-11-11",
            "status": "APPROVED"
        }
        # Decrement PO balance if PO exists
        if po_number and po_number.upper() in self.purchase_orders:
            po = self.purchase_orders[po_number.upper()]
            po["already_invoiced"] += amount
            po["remaining_balance"] = max(0.0, po["total_amount"] - po["already_invoiced"])
            if po["remaining_balance"] == 0:
                po["status"] = "FULLY_CONSUMED"
            else:
                po["status"] = "OPEN_PARTIALLY_INVOICED"

# Global singleton
db = ERPDatabase()
