from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pdfplumber
from fastapi import UploadFile


SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv"}


def save_upload_file(upload_file: UploadFile, upload_dir: Path) -> Path:
    upload_dir.mkdir(parents=True, exist_ok=True)
    original_name = Path(upload_file.filename or "document").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError("Only PDF, TXT, and CSV files are supported")

    safe_stem = Path(original_name).stem.replace(" ", "_")
    target_path = upload_dir / f"{safe_stem}{suffix}"

    with target_path.open("wb") as target_file:
        shutil.copyfileobj(upload_file.file, target_file)

    return target_path


def extract_text_from_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf_text(file_path)
    if suffix == ".csv":
        return _extract_csv_text(file_path)
    if suffix == ".txt":
        return _extract_txt_text(file_path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf_text(file_path: Path) -> str:
    chunks: list[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                chunks.append(page_text)
    return _normalize_text("\n".join(chunks))


def _extract_csv_text(file_path: Path) -> str:
    dataframe = pd.read_csv(file_path)
    return _normalize_text(dataframe.fillna("").to_string(index=False))


def _extract_txt_text(file_path: Path) -> str:
    return _normalize_text(file_path.read_text(encoding="utf-8", errors="ignore"))


def _normalize_text(text: str, limit: int = 30000) -> str:
    compact = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return compact[:limit]
