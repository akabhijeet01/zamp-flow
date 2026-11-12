# Zamp Flow · Autonomous AP Invoice Processing & PO Matching Engine

> **AI Solutions Analyst Case Study Submission · Zamp (2026)**  
> **Problem Statement Selected:** **PS-1 · Finance / AP — Invoice Processing — from PDF to Decision**  
> **Author:** Candidate Submission  
> **Live runnable application:** `http://localhost:8000` (or deployed URL)  

---

## 🎯 Executive Summary & Problem Framing

In mid-market enterprises, Accounts Payable (AP) teams handle hundreds of vendor invoices each month—all arriving as unstructured PDF attachments over email. 

Today, human AP specialists manually open each PDF, locate matching Purchase Orders (POs) in an ERP spreadsheet or database, compare line item descriptions and unit prices, check sales tax, and check remittance bank routing numbers. When fatigue sets in—especially on a Friday afternoon—costly mistakes happen:
1. **Unchecked Price Drift:** Vendors slip in unapproved 10–25% price hikes or emergency surcharges above contracted rates.
2. **Duplicate Invoice Payments:** Resubmitted reminder invoices get processed twice across billing cycles.
3. **Budget Exhaustion & Multi-Part Split Billing:** Master contracts are overdrawn without real-time PO balance tracking.
4. **Remittance Fraud:** Attackers spoof vendor identities or alter bank routing numbers on PDFs.

**Zamp Flow** is an autonomous, transparent 6-stage AP reconciliation engine that takes unstructured PDF invoices as input, executes multi-point validation against ERP and policy rules, and produces a definitive, reasoned decision (`APPROVED`, `FLAGGED_EXCEPTION`, or `REJECTED`) with straight-through GL posting or human-in-the-loop exception handling.

---

## 🏗️ System Architecture & The 6-Stage Pipeline

```
[ Unstructured Invoice PDF ]
          │
          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 1: Document Ingestion & Optical Parsing         │
│ • PDF byte stream tokenizer & text extraction          │
│ • Cryptographic SHA-256 fingerprinting                 │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 2: Entity & Key-Value AI Extraction              │
│ • Vendor, Invoice #, PO Ref, Dates, Bank Routing       │
│ • Tabular line item extraction & arithmetic integrity  │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 3: ERP Vendor Master & Compliance Verification   │
│ • Checks against approved vendor registry              │
│ • Verifies tax IDs, payment terms, and ACH routing     │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 4: 2-Way Line-by-Line PO Matching Engine         │
│ • SKU / description semantic alignment                 │
│ • Line-level quantity & unit price comparison          │
│ • Progress / milestone billing detection               │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 5: Fraud, Duplication & Tolerance Policy Rules   │
│ • 90-day duplicate invoice detection                   │
│ • Company tolerance check (Max 3.0% price variance)    │
│ • PO remaining budget consumption check                │
└─────────────────────────┬──────────────────────────────┘
                          │
                          ▼
┌────────────────────────────────────────────────────────┐
│ STAGE 6: Final Decision & Reasoned Explanation Engine   │
│ • APPROVED: Auto-queues NetSuite/SAP ACH payment       │
│ • FLAGGED: Surfaces exact line variance for review     │
│ • REJECTED: Blocks duplicate or compliance violation   │
└────────────────────────────────────────────────────────┘
```

---

## 🧪 Scenarios & Edge Cases Built & Tested

We designed and built 5 distinct scenarios representing realistic commercial workflows:

| Scenario | Vendor | Invoiced Amt | PO Number | Operational Condition | Automated Decision | Key Reason |
|---|---|---|---|---|---|---|
| **1. Happy Path** | Apex Data Systems | $7,500.00 | PO-9042 | Clean 2-way match, 0.0% variance, bank verified | `APPROVED` | Auto-posted to ERP under Net 30 terms |
| **2. Edge Case A** | Meridian Logistics | $4,700.00 | PO-8810 | Freight billed at $1,450 vs $1,200 (+20.8% variance) | `FLAGGED_EXCEPTION` | Exceeds 3.0% company price tolerance threshold |
| **3. Edge Case B** | CloudScale Infra | $6,000.00 | PO-7020 | Milestone 2 drawdown against $25k master agreement | `APPROVED` | Verified within $10k balance; decrements to $4,000 |
| **4. Edge Case C** | CyberShield Security | $8,800.00 | PO-6640 | Resubmission of invoice already paid last week | `REJECTED` | Duplicate invoice fingerprint blocked |
| **5. Edge Case D** | Phantom Supplies | $3,800.00 | PO-9042 | Unregistered vendor & unverified offshore bank routing | `REJECTED` | Vendor Master & compliance quarantine |

---

## 🚀 Quickstart: Running the Application

### 1. Requirements
- Python 3.10+ (Standard libraries + `starlette`, `uvicorn`, `reportlab` already configured).

### 2. Run Locally
```bash
./run.sh
```
Or directly with Python:
```bash
python3 server.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

### 3. Run Automated Tests
```bash
python3 -m unittest tests/test_pipeline.py
```
*(Runs 7 unit and integration tests verifying all 5 scenarios and human-in-the-loop overrides in <0.05 seconds).*

---

## 💻 User Interface Features

1. **Interactive Scenario Launcher:** 1-click execution of Happy Path and all 4 edge cases with pre-generated genuine ReportLab PDF invoices.
2. **Drag-and-Drop PDF Uploader:** Upload any custom PDF invoice to parse and reconcile live.
3. **Real-Time Stage Stepper:** Animated progression through each of the 6 stages with individual millisecond latency counters and status badges.
4. **Side-by-Side Dual View:** Real PDF viewer on the left; structured reasoning and line-by-line reconciliation table on the right.
5. **Human-in-the-Loop Override:** AP managers can review flagged exceptions, input an operational justification note, and approve/reject with a complete audit trail.
6. **Live ERP PO Registry & Vendor Master:** View real-time PO budget drawdowns and active vendor records.
7. **Audit History & Analytics Dashboard:** Real-time KPI metrics on touchless approval rate %, exceptions flagged, and hours saved.

---

## 🎥 5-Minute Demo Video Recording Script (Loom Walkthrough)

*Note: For the 5-minute video submission, record your screen with your own voice (no AI voice, no slides needed).*

### Minute 0:00 – 1:00: Problem Context & Architecture
> *"Hi everyone, I'm presenting my submission for the Zamp AI Solutions Analyst case study on Problem Statement 1: Invoice Processing from PDF to Decision.*  
>  
> *In accounts payable, teams spend hundreds of hours manually verifying vendor invoice PDFs against purchase orders. Fatigue leads to overpaying inflated unit prices, paying duplicate reminder invoices, or missing payment fraud.*  
>  
> *I built **Zamp Flow**—a transparent, 6-stage autonomous AP engine that extracts unstructured invoice PDFs, verifies ERP vendor compliance, reconciles line items against purchase orders, enforces tolerance policies, detects duplicate fraud, and produces a reasoned, audit-ready decision."*

### Minute 1:00 – 2:15: Happy Path (Straight-Through Processing)
> *(Action: Click **"Scenario 1: Happy Path"**)*  
>  
> *"Let's run our Happy Path. Here we ingest a real PDF invoice from Apex Data Systems for \$7,500 referencing PO-9042.*  
> *Notice the 6 stages executing in real time:*  
> *1. Stage 1 extracts the PDF byte stream and computes a cryptographic SHA-256 fingerprint.*  
> *2. Stage 2 extracts the metadata, bank details, and line items, verifying arithmetic balance.*  
> *3. Stage 3 validates that Apex Data Systems is an approved vendor in our ERP Vendor Master and confirms the bank routing number matches.*  
> *4. Stage 4 executes a 2-way match against PO-9042: both line items match contracted prices exactly with 0.0% variance.*  
> *5. Stage 5 confirms no duplicate invoices and verifies budget availability.*  
> *6. Stage 6 produces an **AUTO-APPROVED** decision, generating the ERP payment payload for scheduled Net 30 ACH release."*

### Minute 2:15 – 3:30: Edge Case 1 (Line-Item Price Variance Exceeds Tolerance)
> *(Action: Click **"Scenario 2: Price Variance"**)*  
>  
> *"Now let's examine a critical edge case: price variance. Meridian Logistics submitted invoice INV-ML-5521 against PO-8810.*  
> *The vendor is approved and the PO exists, but in Stage 4, line-item reconciliation flags that freight handling was billed at \$1,450 per unit instead of the contracted \$1,200 rate—a **+20.8% price variance**.*  
>  
> *Our company policy specifies a maximum 3.0% tolerance threshold. Because 20.8% exceeds our threshold, Stage 5 triggers a policy violation and Stage 6 immediately sets the decision to **FLAGGED EXCEPTION**.*  
> *Instead of blindly paying or dropping the invoice, the system highlights the exact line variance and gives the AP Lead a human-in-the-loop review button to record an operational justification."*

### Minute 3:30 – 4:30: Edge Cases 2 & 3 (Milestone Split Billing & Duplicate Fraud)
> *(Action: Click **"Scenario 4: Duplicate Fraud"**, then **"Scenario 3: Split Billing"**)*  
>  
> *"In Scenario 4, CyberShield Security resubmitted an \$8,800 invoice that was already processed and paid last week. Our fingerprinting engine in Stage 5 catches the duplicate invoice number and immediately rejects it with 99.8% confidence, preventing duplicate payment.*  
>  
> *In Scenario 3, for vendors billing milestones against large master contracts, the engine verifies that this \$6,000 milestone invoice is within the \$10,000 remaining PO budget, approves it, and updates the ERP balance to \$4,000."*

### Minute 4:30 – 5:00: History Dashboard & Conclusion
> *(Action: Click to the **"Past Runs & History"** tab)*  
>  
> *"Finally, all runs are tracked in this real-time audit dashboard, providing AP leadership with instant visibility into straight-through processing rates, exception breakdown, and hours saved.*  
> *Thank you, and I look forward to walking through the live demo with the Zamp team!"*

---

## 📧 Hiring Coordinator Email Submission Template

**Subject:** `ASA Case Study — [Your Name] — PS-1`

```text
Hi [Hiring Coordinator Name],

I have completed the AI Solutions Analyst Case Study. I selected Problem Statement 1 (Finance / AP: Invoice processing — from PDF to decision) as it aligns directly with Zamp's core operational domain.

Here are the two deliverables for my submission:

1. Working Process Link (Live & Runnable):
   [Insert your deployed link or github repository link]
   (Instructions to run locally: Clone repo and run ./run.sh -> accessible on http://localhost:8000)

2. 5-Minute Demo Video Link (Loom):
   [Insert your Loom recording link]

The process runs live end-to-end with real PDF inputs, an animated 6-stage execution view, a complete audit history dashboard, and 4 realistic commercial edge cases (price variance exceeding tolerance, milestone split billing, duplicate billing prevention, and unapproved vendor quarantine).

Looking forward to demonstrating the build live in the follow-up interview!

Best regards,
[Your Name]
```
