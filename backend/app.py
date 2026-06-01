from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from services.chart_generator import create_report_charts
from services.llm import analyze_financial_document, deepseek_status, test_deepseek_return_three
from services.parser import extract_text_from_file, save_upload_file
from services.pdf_generator import generate_pdf_report


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_DIR = BASE_DIR / "generated"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


app = FastAPI(title="Financial Research MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/generated", StaticFiles(directory=GENERATED_DIR), name="generated")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/deepseek-status")
def deepseek_configuration() -> dict[str, object]:
    return deepseek_status()


@app.get("/deepseek-test-3")
def deepseek_test_three() -> dict[str, object]:
    return test_deepseek_return_three()


@app.post("/generate-report")
async def generate_report(
    company_name: str = Form(...),
    uploaded_file: UploadFile = File(...),
) -> dict[str, str]:
    if not company_name.strip():
        raise HTTPException(status_code=400, detail="company_name is required")

    saved_file_path = await asyncio.to_thread(save_upload_file, uploaded_file, UPLOAD_DIR)
    extracted_text = await asyncio.to_thread(extract_text_from_file, saved_file_path)

    analysis = await asyncio.to_thread(
        analyze_financial_document,
        company_name.strip(),
        extracted_text,
    )

    chart_paths = await asyncio.to_thread(
        create_report_charts,
        analysis,
        company_name.strip(),
        GENERATED_DIR,
    )

    report_date = datetime.now().strftime("%d %b %Y")
    pdf_filename = f"{company_name.strip().lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf_path = GENERATED_DIR / pdf_filename

    await asyncio.to_thread(
        generate_pdf_report,
        company_name.strip(),
        report_date,
        analysis,
        chart_paths,
        pdf_path,
    )

    return {"pdf_url": f"/download/{pdf_filename}"}


@app.get("/download/{filename}")
def download_report(filename: str) -> FileResponse:
    safe_name = Path(filename).name
    pdf_path = GENERATED_DIR / safe_name
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=safe_name,
    )
