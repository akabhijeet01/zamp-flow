"""
PDF Generator for Realistic AP Invoices using ReportLab.
Generates genuine, professional PDF files for the Happy Path and all Edge Cases.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

SCENARIOS_META = {
    "happy_path": {
        "id": "happy_path",
        "name": "Scenario 1: Clean 2-Way Match (Happy Path)",
        "badge": "Happy Path",
        "badge_color": "emerald",
        "vendor": "Apex Data Systems",
        "invoice_no": "INV-2026-8041",
        "po_no": "PO-9042",
        "total": 7500.00,
        "description": "Standard SaaS & Support contract. Invoice line items, quantities, and pricing exactly match PO-9042.",
        "expected_result": "AUTO-APPROVED",
        "pdf_filename": "sample_invoices/01_happy_path_INV-2026-8041.pdf"
    },
    "edge_price_variance": {
        "id": "edge_price_variance",
        "name": "Scenario 2: Price Variance Exceeds 3% Tolerance",
        "badge": "Edge Case · Variance",
        "badge_color": "amber",
        "vendor": "Meridian Logistics Global",
        "invoice_no": "INV-ML-5521",
        "po_no": "PO-8810",
        "total": 4700.00,
        "description": "Freight rate billed at $1,450/unit instead of contract price $1,200/unit (+20.8% variance). Exceeds 3.0% company tolerance threshold.",
        "expected_result": "FLAGGED FOR REVIEW",
        "pdf_filename": "sample_invoices/02_edge_price_variance_INV-ML-5521.pdf"
    },
    "edge_split_billing": {
        "id": "edge_split_billing",
        "name": "Scenario 3: Split PO Drawdown / Milestone Billing",
        "badge": "Edge Case · Partial PO",
        "badge_color": "blue",
        "vendor": "CloudScale Infrastructure Inc.",
        "invoice_no": "INV-CS-3022",
        "po_no": "PO-7020",
        "total": 6000.00,
        "description": "Milestone 2 partial billing against $25k master PO. System verifies remaining $10k balance, approves drawdown, and updates remaining balance to $4,000.",
        "expected_result": "APPROVED (PARTIAL DRAWDOWN)",
        "pdf_filename": "sample_invoices/03_edge_split_billing_INV-CS-3022.pdf"
    },
    "edge_duplicate_fraud": {
        "id": "edge_duplicate_fraud",
        "name": "Scenario 4: Duplicate Invoice / Double Billing",
        "badge": "Edge Case · Duplicate",
        "badge_color": "red",
        "vendor": "CyberShield Security Corp",
        "invoice_no": "INV-CS-9941",
        "po_no": "PO-6640",
        "total": 8800.00,
        "description": "Vendor resubmits an invoice that was already processed and paid last week. Caught by duplicate hash detection.",
        "expected_result": "REJECTED (DUPLICATE DETECTED)",
        "pdf_filename": "sample_invoices/04_edge_duplicate_fraud_INV-CS-9941.pdf"
    },
    "edge_unapproved_vendor": {
        "id": "edge_unapproved_vendor",
        "name": "Scenario 5: Unapproved Vendor & Banking Tampering",
        "badge": "Edge Case · Fraud Risk",
        "badge_color": "purple",
        "vendor": "Phantom Supplies LLC",
        "invoice_no": "INV-PH-1090",
        "po_no": "PO-9042",
        "total": 3800.00,
        "description": "Unregistered vendor attempts to claim PO-9042 with unrecognized bank routing info. Quarantined as compliance violation.",
        "expected_result": "REJECTED (SECURITY / VENDOR MASTER)",
        "pdf_filename": "sample_invoices/05_edge_unapproved_vendor_INV-PH-1090.pdf"
    }
}

def generate_invoice_pdf(scenario_id: str, output_path: str):
    """Generate a clean, professional, uncompressed PDF invoice."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # We use canvas directly with pageCompression=0 so text is crystal clear and parseable
    c = canvas.Canvas(output_path, pagesize=letter, pageCompression=0)
    width, height = letter # 612 x 792

    if scenario_id == "happy_path":
        vendor_name = "Apex Data Systems"
        address1 = "100 Innovation Way, Suite 400"
        address2 = "Austin, TX 78701 · Tax ID: US-84-9210442"
        inv_no = "INV-2026-8041"
        date_str = "2026-11-08"
        due_str = "2026-12-08"
        po_str = "PO-9042"
        routing = "121000358"
        account = "XXXX4892"
        items = [
            ("1", "DATA-ENG-PRO", "Enterprise Data Analytics License (Annual)", "1", "$5,000.00", "$5,000.00"),
            ("2", "DATA-SUP-PREM", "24/7 Dedicated Infrastructure Support Tier", "1", "$2,500.00", "$2,500.00")
        ]
        subtotal = "$7,500.00"
        tax = "$0.00"
        total = "$7,500.00"
        note = "Thank you for your business. Payment terms Net 30. Direct ACH wire details below."

    elif scenario_id == "edge_price_variance":
        vendor_name = "Meridian Logistics Global"
        address1 = "450 Industrial Parkway, Dock 12"
        address2 = "Chicago, IL 60607 · Tax ID: US-13-8829104"
        inv_no = "INV-ML-5521"
        date_str = "2026-11-09"
        due_str = "2026-11-24"
        po_str = "PO-8810"
        routing = "026009593"
        account = "XXXX9912"
        items = [
            ("1", "FREIGHT-EXP-01", "Cross-Country Pallet Freight Handling", "2", "$1,450.00", "$2,900.00"),
            ("2", "STORAGE-TEMP-04", "Temperature Controlled Warehousing (Mo.)", "1", "$1,800.00", "$1,800.00")
        ]
        subtotal = "$4,700.00"
        tax = "$0.00"
        total = "$4,700.00"
        note = "Notice: Spot fuel surcharges applied to freight lines. Total differs from base PO contract."

    elif scenario_id == "edge_split_billing":
        vendor_name = "CloudScale Infrastructure Inc."
        address1 = "500 Cloud Valley Blvd"
        address2 = "Seattle, WA 98101 · Tax ID: US-94-1182390"
        inv_no = "INV-CS-3022"
        date_str = "2026-11-10"
        due_str = "2026-12-10"
        po_str = "PO-7020"
        routing = "322271627"
        account = "XXXX3341"
        items = [
            ("1", "CLOUD-RES-COMPUTE", "High Performance Reserved GPU Cluster - Milestone 2 of 3", "1", "$6,000.00", "$6,000.00")
        ]
        subtotal = "$6,000.00"
        tax = "$0.00"
        total = "$6,000.00"
        note = "Progress billing against master agreement PO-7020 ($25,000.00 total). Milestone 2 of 3."

    elif scenario_id == "edge_duplicate_fraud":
        vendor_name = "CyberShield Security Corp"
        address1 = "22 Security Circle, Floor 9"
        address2 = "San Francisco, CA 94105 · Tax ID: US-55-9012431"
        inv_no = "INV-CS-9941"
        date_str = "2026-11-11"
        due_str = "2026-12-11"
        po_str = "PO-6640"
        routing = "071000288"
        account = "XXXX7710"
        items = [
            ("1", "SOC2-AUDIT-PREP", "SOC2 Type II Continuous Audit & Evidence Collector", "1", "$8,800.00", "$8,800.00")
        ]
        subtotal = "$8,800.00"
        tax = "$0.00"
        total = "$8,800.00"
        note = "Reminder Statement: Invoiced services for continuous SOC2 compliance automation."

    else: # edge_unapproved_vendor
        vendor_name = "Phantom Supplies LLC"
        address1 = "PO Box 9912 Unknown St"
        address2 = "Grand Cayman, KY · Tax ID: UNKNOWN-990"
        inv_no = "INV-PH-1090"
        date_str = "2026-11-11"
        due_str = "2026-11-12"
        po_str = "PO-9042"
        routing = "999999999"
        account = "XXXX0001"
        items = [
            ("1", "OFFICE-EQUIP-X", "Expedited Server Replacement Components", "1", "$3,800.00", "$3,800.00")
        ]
        subtotal = "$3,800.00"
        tax = "$0.00"
        total = "$3,800.00"
        note = "URGENT PAYMENT REQUIRED. Please wire directly to offshore routing 999999999."

    # Draw header banner
    c.setFillColor(colors.HexColor("#0f172a")) # Slate 900
    c.rect(0, 720, 612, 72, fill=1, stroke=0)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, 750, "COMMERCIAL INVOICE")
    
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#94a3b8")) # Slate 400
    c.drawString(40, 734, "AUTOMATED ACCOUNTS PAYABLE RECONCILIATION DOCUMENT")

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.white)
    c.drawRightString(572, 750, f"INVOICE: {inv_no}")
    c.setFont("Helvetica", 10)
    c.drawRightString(572, 734, f"PO REF: {po_str}")

    # Vendor Block & Bill-To Block
    c.setFillColor(colors.HexColor("#0f172a"))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, 680, vendor_name)
    
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(40, 665, address1)
    c.drawString(40, 652, address2)

    # Bill-To (Customer)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(340, 680, "BILLED TO:")
    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawString(340, 665, "Zamp Global Enterprises Inc.")
    c.drawString(340, 652, "Attn: Accounts Payable Department")
    c.drawString(340, 639, "500 Technology Square, San Francisco, CA 94107")

    # Metadata Grid
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.roundRect(40, 580, 532, 45, 4, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(55, 608, "INVOICE DATE")
    c.drawString(175, 608, "PAYMENT DUE")
    c.drawString(295, 608, "PURCHASE ORDER")
    c.drawString(435, 608, "PAYMENT METHOD")

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(55, 592, date_str)
    c.drawString(175, 592, due_str)
    c.drawString(295, 592, po_str)
    c.drawString(435, 592, "ACH / Direct Wire")

    # Table Header
    c.setFillColor(colors.HexColor("#1e293b")) # Slate 800
    c.rect(40, 535, 532, 24, fill=1, stroke=0)
    
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(50, 542, "ITEM")
    c.drawString(90, 542, "SKU")
    c.drawString(180, 542, "DESCRIPTION")
    c.drawRightString(400, 542, "QTY")
    c.drawRightString(470, 542, "UNIT PRICE")
    c.drawRightString(560, 542, "AMOUNT")

    # Table Rows
    y = 515
    for item in items:
        item_no, sku, desc, qty, unit_p, amt = item
        c.setFillColor(colors.HexColor("#0f172a"))
        c.setFont("Helvetica", 9)
        c.drawString(50, y, item_no)
        c.setFont("Helvetica-Bold", 8)
        c.setFillColor(colors.HexColor("#475569"))
        c.drawString(90, y, sku)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#0f172a"))
        c.drawString(180, y, desc[:35])
        c.drawRightString(400, y, qty)
        c.drawRightString(470, y, unit_p)
        c.setFont("Helvetica-Bold", 9)
        c.drawRightString(560, y, amt)
        
        # Row divider line
        c.setStrokeColor(colors.HexColor("#f1f5f9"))
        c.line(40, y - 6, 572, y - 6)
        y -= 26

    # Totals Section
    totals_y = y - 15
    c.setFillColor(colors.HexColor("#f8fafc"))
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.roundRect(330, totals_y - 65, 242, 70, 4, fill=1, stroke=1)

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(345, totals_y - 12, "Subtotal:")
    c.drawRightString(560, totals_y - 12, subtotal)

    c.drawString(345, totals_y - 28, "Tax (Sales / VAT):")
    c.drawRightString(560, totals_y - 28, tax)

    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.line(345, totals_y - 35, 560, totals_y - 35)

    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.HexColor("#0f172a"))
    c.drawString(345, totals_y - 54, "TOTAL DUE:")
    c.drawRightString(560, totals_y - 54, total)

    # Remittance Bank Info Box
    bank_y = totals_y - 130
    c.setFillColor(colors.HexColor("#eff6ff")) # Light blue
    c.setStrokeColor(colors.HexColor("#bfdbfe"))
    c.roundRect(40, bank_y, 270, 60, 4, fill=1, stroke=1)

    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#1d4ed8"))
    c.drawString(50, bank_y + 44, "REMITTANCE & ACH PAYMENT DETAILS")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#1e293b"))
    c.drawString(50, bank_y + 28, f"Bank Routing (ABA): {routing}")
    c.drawString(50, bank_y + 14, f"Account Number: {account}")

    # Notes & Footer
    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor("#64748b"))
    c.drawString(40, 70, f"Notes: {note}")
    c.setStrokeColor(colors.HexColor("#e2e8f0"))
    c.line(40, 55, 572, 55)
    c.setFont("Helvetica", 7)
    c.setFillColor(colors.HexColor("#94a3b8"))
    c.drawString(40, 40, f"Generated for Zamp AI Solutions Analyst Case Study · Enterprise AP Pipeline · {inv_no}")
    c.drawRightString(572, 40, "Confidential Financial Document · Page 1 of 1")

    c.save()
    return output_path

def generate_all_sample_pdfs():
    """Generates all 5 scenario PDFs to disk."""
    created = []
    for s_id, meta in SCENARIOS_META.items():
        path = meta["pdf_filename"]
        generate_invoice_pdf(s_id, path)
        created.append(path)
    return created

if __name__ == "__main__":
    files = generate_all_sample_pdfs()
    print(f"Generated {len(files)} sample invoice PDFs:")
    for f in files:
        print(" -", f)
