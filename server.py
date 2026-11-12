"""
Starlette ASGI Server for Zamp Flow AP Reconciliation Engine.
Runs with built-in Uvicorn.
"""
import os
import io
import time
import json
from typing import Optional, Dict, Any, List
from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, FileResponse
from starlette.routing import Route
from starlette.requests import Request
from starlette.exceptions import HTTPException

from pipeline import pipeline
from erp_database import db, COMPANY_POLICY
from pdf_generator import SCENARIOS_META, generate_all_sample_pdfs, generate_invoice_pdf

# Ensure sample PDFs are pre-generated
generate_all_sample_pdfs()

async def get_scenarios(request: Request):
    return JSONResponse(list(SCENARIOS_META.values()))

async def get_purchase_orders(request: Request):
    return JSONResponse(list(db.purchase_orders.values()))

async def get_vendors(request: Request):
    return JSONResponse(list(db.vendors.values()))

async def get_runs(request: Request):
    history = db.run_history
    total = len(history)
    approved = sum(1 for r in history if r["decision"].startswith("APPROVED"))
    flagged = sum(1 for r in history if r["decision"] == "FLAGGED_EXCEPTION")
    rejected = sum(1 for r in history if "REJECT" in r["decision"])
    avg_time = round(sum(r["processing_time_ms"] for r in history) / total, 2) if total > 0 else 0.0

    return JSONResponse({
        "metrics": {
            "total_runs": total,
            "approved": approved,
            "flagged": flagged,
            "rejected": rejected,
            "approval_rate_pct": round((approved / total * 100), 1) if total > 0 else 0.0,
            "avg_time_ms": avg_time,
            "time_saved_hours": round(total * 0.25, 2)
        },
        "runs": history
    })

async def get_run_detail(request: Request):
    run_id = request.path_params["run_id"]
    for r in db.run_history:
        if r["run_id"] == run_id:
            return JSONResponse(r)
    return JSONResponse({"detail": "Run not found"}, status_code=404)

async def human_override(request: Request):
    run_id = request.path_params["run_id"]
    try:
        body = await request.json()
    except Exception:
        body = {}
    action = body.get("action", "OVERRIDE_APPROVE")
    notes = body.get("notes", "")
    reviewer = body.get("reviewer", "AP Lead Reviewer")

    for r in db.run_history:
        if r["run_id"] == run_id:
            r["human_override"] = {
                "action": action,
                "notes": notes,
                "reviewer": reviewer,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            if action == "OVERRIDE_APPROVE":
                r["decision"] = "APPROVED_WITH_OVERRIDE"
                r["risk_level"] = "LOW"
                r["summary_headline"] = f"Approved by Human Override ({reviewer})"
                db.record_approved_invoice(
                    r["invoice_number"],
                    r["vendor_name"],
                    r["po_number"],
                    r["total_amount"]
                )
            elif action == "CONFIRM_REJECT":
                r["decision"] = "CONFIRMED_REJECTED"
                r["summary_headline"] = f"Rejected & Confirmed by {reviewer}"
            return JSONResponse(r)
    return JSONResponse({"detail": "Run not found"}, status_code=404)

async def reset_erp(request: Request):
    db.reset()
    generate_all_sample_pdfs()
    return JSONResponse({"status": "success", "message": "ERP Master, balances, and invoice run history reset to pristine state."})

async def download_sample_pdf(request: Request):
    scenario_id = request.path_params["scenario_id"]
    if scenario_id not in SCENARIOS_META:
        return JSONResponse({"detail": "Scenario not found"}, status_code=404)
    filepath = SCENARIOS_META[scenario_id]["pdf_filename"]
    if not os.path.exists(filepath):
        generate_invoice_pdf(scenario_id, filepath)
    return FileResponse(filepath, media_type="application/pdf", filename=os.path.basename(filepath))

async def process_invoice(request: Request):
    form = await request.form()
    scenario_id = form.get("scenario_id")
    file = form.get("file")

    if scenario_id and scenario_id in SCENARIOS_META:
        meta = SCENARIOS_META[scenario_id]
        filepath = meta["pdf_filename"]
        if not os.path.exists(filepath):
            generate_invoice_pdf(scenario_id, filepath)
        with open(filepath, "rb") as f:
            pdf_bytes = f.read()
        filename = os.path.basename(filepath)
    elif file and hasattr(file, "read"):
        pdf_bytes = await file.read()
        filename = getattr(file, "filename", "uploaded_invoice.pdf")
        scenario_id = None
    else:
        return JSONResponse({"detail": "Must provide either scenario_id or uploaded file."}, status_code=400)

    run_record = pipeline.run(filename, pdf_bytes, scenario_id=scenario_id)
    from dataclasses import asdict
    return JSONResponse(asdict(run_record))

async def index_page(request: Request):
    with open("templates/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content)

routes = [
    Route("/", endpoint=index_page, methods=["GET"]),
    Route("/api/scenarios", endpoint=get_scenarios, methods=["GET"]),
    Route("/api/erp/pos", endpoint=get_purchase_orders, methods=["GET"]),
    Route("/api/erp/vendors", endpoint=get_vendors, methods=["GET"]),
    Route("/api/runs", endpoint=get_runs, methods=["GET"]),
    Route("/api/runs/{run_id}", endpoint=get_run_detail, methods=["GET"]),
    Route("/api/runs/{run_id}/override", endpoint=human_override, methods=["POST"]),
    Route("/api/reset-erp", endpoint=reset_erp, methods=["POST"]),
    Route("/api/download-sample/{scenario_id}", endpoint=download_sample_pdf, methods=["GET"]),
    Route("/api/process", endpoint=process_invoice, methods=["POST"]),
]

app = Starlette(debug=True, routes=routes)

if __name__ == "__main__":
    import uvicorn
    print("Starting Zamp Flow AP Engine on http://localhost:8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
