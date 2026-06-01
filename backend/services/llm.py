from __future__ import annotations

import json
import os
import re
from collections import OrderedDict
from pathlib import Path
from typing import Any

import httpx

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")


def deepseek_status() -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    return {
        "configured": bool(api_key),
        "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        "has_env_file": Path(".env").exists(),
    }


def analyze_financial_document(company_name: str, extracted_text: str) -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if api_key:
        try:
            response = _call_deepseek(company_name, extracted_text, api_key)
            parsed = _parse_json_response(response)
            return _normalize_analysis(company_name, parsed)
        except Exception:
            pass

    return _fallback_analysis(company_name, extracted_text)


def test_deepseek_return_three() -> dict[str, Any]:
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        return {"configured": False, "result": None, "error": "DEEPSEEK_API_KEY is not set"}

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "Return only the single digit 3 and nothing else."},
            {"role": "user", "content": "Return 3."},
        ],
        "temperature": 0,
        "max_tokens": 8,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    with httpx.Client(timeout=30) as client:
        response = client.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    content = data["choices"][0]["message"]["content"].strip()
    return {"configured": True, "result": content}


def _call_deepseek(company_name: str, extracted_text: str, api_key: str) -> str:
    prompt = f"""
You are extracting structured financial research notes from a company document.

Return valid JSON only and use null when a value is not available.
Never invent values.

Schema:
{{
  "company_overview": string|null,
  "key_highlights": [string],
  "revenue": [{{"period": string, "value": number|null}}],
  "ebitda": [{{"period": string, "value": number|null}}],
  "pat": [{{"period": string, "value": number|null}}],
  "financial_metrics": object,
  "outlook": string|null,
  "risks": [string],
  "recommendation": "BUY" | "HOLD" | "SELL" | null
}}

Rules:
- Return valid JSON only.
- Never invent values.
- Use null when data is unavailable.
- recommendation must be one of: "BUY", "HOLD", "SELL", or null. Do not use other values.

Company: {company_name}

Document:
{extracted_text}
""".strip()

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {"role": "system", "content": "You extract structured financial data from documents."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.1,
        "max_tokens": 2000,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=90) as client:
        response = client.post(DEEPSEEK_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

    return data["choices"][0]["message"]["content"]


def _parse_json_response(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM response did not contain JSON")
    return json.loads(text[start : end + 1])


def _normalize_analysis(company_name: str, data: dict[str, Any]) -> dict[str, Any]:
    recommendation = data.get("recommendation")
    if isinstance(recommendation, str):
        recommendation = recommendation.strip().upper()
        if recommendation not in {"BUY", "HOLD", "SELL"}:
            recommendation = "Not Rated"
    else:
        recommendation = "Not Rated"

    return {
        "company_name": company_name,
        "company_overview": data.get("company_overview") or "",
        "key_highlights": _to_string_list(data.get("key_highlights")),
        "revenue": _normalize_metric_series(data.get("revenue")),
        "gross_order_value": _normalize_metric_series(data.get("gross_order_value")),
        "ebitda": _normalize_metric_series(data.get("ebitda")),
        "pat": _normalize_metric_series(data.get("pat")),
        "price_performance": _normalize_metric_series(data.get("price_performance")),
        "financial_metrics": data.get("financial_metrics") or {},
        "outlook": data.get("outlook") or "",
        "risks": _to_string_list(data.get("risks")),
        "recommendation": recommendation,
        "section_blocks": data.get("section_blocks") or {},
    }


def _fallback_analysis(company_name: str, extracted_text: str) -> dict[str, Any]:
    sentences = re.split(r"(?<=[.!?])\s+", extracted_text)
    overview = " ".join(sentences[:3]).strip() if sentences else extracted_text[:400]
    overview = overview or f"Limited text was extracted for {company_name}."

    highlights = _first_unique_lines(extracted_text, patterns=[r"growth", r"margin", r"revenue", r"ebitda", r"pat", r"outlook"], limit=5)
    risks = _first_unique_lines(extracted_text, patterns=[r"risk", r"debt", r"volatility", r"slowdown", r"competition"], limit=4)

    revenue = _extract_series_from_text(extracted_text, ["revenue", "sales"])
    gross_order_value = _extract_series_from_text(extracted_text, ["gross order value", "gov", "nov"])
    ebitda = _extract_series_from_text(extracted_text, ["ebitda"])
    pat = _extract_series_from_text(extracted_text, ["pat", "profit after tax", "net profit"])
    price_performance = _extract_series_from_text(extracted_text, ["price performance", "absolute return", "sensex"])

    financial_metrics = _extract_metric_dictionary(extracted_text)
    outlook = _extract_sentence_after_keyword(extracted_text, ["outlook", "guidance", "valuation", "target price"]) or "Document reviewed. Additional analyst interpretation is required for a firm view."

    section_blocks = {
        "company_data": _extract_section_block(extracted_text, "Company Data", ["Shareholding", "Price Performance", "Outlook & Valuation"]),
        "shareholding": _extract_section_block(extracted_text, "Shareholding", ["Price Performance", "Outlook & Valuation", "Key highlights"]),
        "price_performance": _extract_section_block(extracted_text, "Price Performance", ["Outlook & Valuation", "Key highlights", "Revenue"]),
        "key_highlights": _extract_section_block(extracted_text, "Key highlights", ["Revenue", "Gross Order Value", "Consolidated Financials"]),
        "change_in_estimates": _extract_section_block(extracted_text, "Change in Estimates", ["Consolidated Financials", "Recommendation Summary"]),
        "consolidated_financials": _extract_section_block(extracted_text, "Consolidated Financials", ["Recommendation Summary", "DISCLAIMER & DISCLOSURES"]),
        "recommendation_summary": _extract_section_block(extracted_text, "Recommendation Summary", ["Investment Rating Criteria", "DISCLAIMER & DISCLOSURES"]),
        "investment_rating_criteria": _extract_section_block(extracted_text, "Investment Rating Criteria", ["Symbols definition", "DISCLAIMER & DISCLOSURES"]),
        "symbols_definition": _extract_section_block(extracted_text, "Symbols definition", ["DISCLAIMER & DISCLOSURES"]),
        "disclaimer": _extract_section_block(extracted_text, "DISCLAIMER & DISCLOSURES", []),
    }

    return {
        "company_name": company_name,
        "company_overview": overview,
        "key_highlights": highlights or ["Document extracted successfully.", "DeepSeek fallback mode used."],
        "revenue": revenue,
        "gross_order_value": gross_order_value,
        "ebitda": ebitda,
        "pat": pat,
        "price_performance": price_performance,
        "financial_metrics": financial_metrics,
        "outlook": outlook,
        "risks": risks or ["No explicit risks extracted from the provided document."],
        "recommendation": "Not Rated",
        "section_blocks": section_blocks,
    }


def _normalize_metric_series(series: Any) -> list[dict[str, Any]]:
    if not isinstance(series, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in series:
        if isinstance(item, dict):
            period = str(item.get("period") or item.get("year") or item.get("label") or "")
            value = item.get("value")
        else:
            period = ""
            value = item
        if period or value is not None:
            normalized.append({"period": period, "value": _to_number(value)})
    return normalized


def _to_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        if item is None:
            continue
        text = str(item).strip()
        if text:
            output.append(text)
    return output


def _to_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    if not text or text.lower() in {"na", "n/a", "null", "none"}:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def _first_unique_lines(extracted_text: str, patterns: list[str], limit: int) -> list[str]:
    seen: OrderedDict[str, None] = OrderedDict()
    for raw_line in extracted_text.splitlines():
        line = raw_line.strip()
        if not line or len(line) < 25:
            continue
        lower = line.lower()
        if any(re.search(pattern, lower) for pattern in patterns):
            seen.setdefault(line, None)
        if len(seen) >= limit:
            break
    return list(seen.keys())[:limit]


def _extract_series_from_text(extracted_text: str, keywords: list[str]) -> list[dict[str, Any]]:
    series: list[dict[str, Any]] = []
    for line in extracted_text.splitlines():
        lower = line.lower()
        if not any(keyword in lower for keyword in keywords):
            continue
        years = re.findall(r"FY\d{2}|20\d{2}", line, flags=re.IGNORECASE)
        numbers = re.findall(r"-?\d+(?:,\d{3})*(?:\.\d+)?", line)
        if not numbers:
            continue
        period = years[0] if years else f"Point {len(series) + 1}"
        series.append({"period": period, "value": _to_number(numbers[-1])})
        if len(series) >= 4:
            break
    return series


def _extract_metric_dictionary(extracted_text: str) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    for line in extracted_text.splitlines():
        lower = line.lower()
        if any(term in lower for term in ["margin", "growth", "ratio", "cagr", "ebitda", "pat", "revenue"]):
            cleaned = line.strip()
            if cleaned and len(cleaned) < 140:
                key = cleaned.split(":", 1)[0].strip()
                metrics.setdefault(key, cleaned)
        if len(metrics) >= 8:
            break
    if not metrics:
        metrics["Source characters"] = len(extracted_text)
    return metrics


def _extract_sentence_after_keyword(extracted_text: str, keywords: list[str]) -> str:
    for keyword in keywords:
        match = re.search(rf"([^\n.]*{re.escape(keyword)}[^\n.]*(?:[.][^\n.]*)?)", extracted_text, flags=re.IGNORECASE)
        if match:
            sentence = match.group(1).strip()
            if sentence:
                return sentence[:300]
    return ""


def _extract_section_block(extracted_text: str, start_marker: str, stop_markers: list[str]) -> str:
    lines = [line.rstrip() for line in extracted_text.splitlines()]
    start_index = None
    for index, line in enumerate(lines):
        if start_marker.lower() in line.lower():
            start_index = index + 1
            break
    if start_index is None:
        return ""

    stop_index = len(lines)
    for index in range(start_index, len(lines)):
        lower_line = lines[index].lower().strip()
        if any(marker.lower() in lower_line for marker in stop_markers):
            stop_index = index
            break

    block_lines = [line.strip() for line in lines[start_index:stop_index] if line.strip()]
    return "\n".join(block_lines[:200])
