from __future__ import annotations

from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


PAGE_WIDTH, PAGE_HEIGHT = A4
TEAL = colors.HexColor("#0b8f87")
TEAL_DARK = colors.HexColor("#0a726c")
ORANGE = colors.HexColor("#f97316")
GREEN = colors.HexColor("#16a34a")
SLATE = colors.HexColor("#334155")
LIGHT = colors.HexColor("#f3f6f8")
LIGHTER = colors.HexColor("#f8fafb")
LINE = colors.HexColor("#cbd5e1")


def generate_pdf_report(
    company_name: str,
    report_date: str,
    analysis: dict[str, Any],
    chart_paths: dict[str, str],
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    styles = _build_styles()
    story: list[Any] = []

    story.extend(_page_one(company_name, report_date, analysis, chart_paths, styles))
    story.append(PageBreak())
    story.extend(_page_two(company_name, analysis, chart_paths, styles))
    story.append(PageBreak())
    story.extend(_page_three(analysis, styles))
    story.append(PageBreak())
    story.extend(_page_four(company_name, analysis, chart_paths, styles))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=0.5 * inch,
        rightMargin=0.5 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.55 * inch,
    )
    doc.build(
        story,
        onFirstPage=lambda canvas, _: _draw_frame(canvas, company_name, report_date, page=1),
        onLaterPages=lambda canvas, _: _draw_frame(canvas, company_name, report_date, page=canvas.getPageNumber()),
    )


def _build_styles() -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("TitleLarge", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=24, leading=26, textColor=colors.black, spaceAfter=2))
    styles.add(ParagraphStyle("Subtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=9.5, leading=11, textColor=SLATE, spaceAfter=2))
    styles.add(ParagraphStyle("Section", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=14, textColor=TEAL_DARK, spaceBefore=4, spaceAfter=5))
    styles.add(ParagraphStyle("Subsection", parent=styles["Heading3"], fontName="Helvetica-Bold", fontSize=10.5, leading=12, textColor=colors.black, spaceBefore=3, spaceAfter=4))
    styles.add(ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.7, leading=10.8, textColor=colors.black))
    styles.add(ParagraphStyle("Small", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.6, leading=9.0, textColor=SLATE))
    styles.add(ParagraphStyle("Tiny", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.9, leading=8.2, textColor=SLATE))
    styles.add(ParagraphStyle("WhiteSmall", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=8.3, leading=9.5, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle("WhiteMedium", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10.5, leading=12, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle("TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.8, leading=8.8, textColor=colors.white, alignment=TA_CENTER))
    styles.add(ParagraphStyle("TableCell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.3, leading=8.5, textColor=colors.black))
    styles.add(ParagraphStyle("TableCellBold", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.3, leading=8.5, textColor=colors.black))
    styles.add(ParagraphStyle("ReportBullet", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=10.4, leftIndent=10, bulletIndent=0, textColor=colors.black))
    styles.add(ParagraphStyle("Disclaimer", parent=styles["BodyText"], fontName="Helvetica", fontSize=6.1, leading=7.2, textColor=SLATE))
    return styles


def _draw_frame(canvas, company_name: str, report_date: str, page: int) -> None:
    canvas.saveState()
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_HEIGHT - 0.5 * inch, PAGE_WIDTH, 0.5 * inch, stroke=0, fill=1)
    canvas.rect(0, 0, PAGE_WIDTH, 0.42 * inch, stroke=0, fill=1)

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawRightString(PAGE_WIDTH - 0.45 * inch, PAGE_HEIGHT - 0.21 * inch, "GEOJIT")
    canvas.setFont("Helvetica", 6.8)
    canvas.drawRightString(PAGE_WIDTH - 0.45 * inch, PAGE_HEIGHT - 0.32 * inch, "PEOPLE YOU PROSPER WITH")
    canvas.setFont("Helvetica", 8.5)
    canvas.drawRightString(PAGE_WIDTH - 0.45 * inch, 0.14 * inch, "www.geojit.com")

    canvas.setFillColor(colors.white)
    canvas.circle(0.35 * inch, 0.21 * inch, 0.13 * inch, stroke=1, fill=0)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.drawCentredString(0.35 * inch, 0.165 * inch, "G")

    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica", 7.2)
    canvas.drawString(0.45 * inch, PAGE_HEIGHT - 0.22 * inch, company_name)
    canvas.drawRightString(PAGE_WIDTH - 2.1 * inch, PAGE_HEIGHT - 0.22 * inch, report_date)
    canvas.drawRightString(PAGE_WIDTH - 0.45 * inch, 0.28 * inch, f"Page {page}")

    if page == 1:
        canvas.setFillColor(TEAL)
        canvas.roundRect(PAGE_WIDTH - 0.05 * inch, PAGE_HEIGHT - 2.0 * inch, 0.55 * inch, 2.0 * inch, 0.12 * inch, stroke=0, fill=1)
        canvas.saveState()
        canvas.translate(PAGE_WIDTH - 0.11 * inch, PAGE_HEIGHT - 0.12 * inch)
        canvas.rotate(90)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(0, 0, "Q1FY26 Result Update")
        canvas.restoreState()

    canvas.restoreState()


def _page_one(company_name: str, report_date: str, analysis: dict[str, Any], chart_paths: dict[str, str], styles: dict[str, ParagraphStyle]) -> list[Any]:
    company_data = _normalize_mapping(analysis.get("company_data"))
    shareholding = _normalize_mapping(analysis.get("shareholding"))
    price_performance = _normalize_mapping(analysis.get("price_performance"))
    overview = _section_text(analysis, "company_overview", "Company overview was not extracted.")
    highlights = _string_list(analysis.get("key_highlights"))
    outlook = _section_text(analysis, "outlook", "Outlook was not extracted.")
    revenue_series = _series_map(analysis.get("revenue"))
    ebitda_series = _series_map(analysis.get("ebitda"))
    pat_series = _series_map(analysis.get("pat"))

    left_stack = _stack([
        _company_data_table(company_data, styles),
        _shareholding_table(shareholding, styles),
        _price_performance_card(price_performance, chart_paths.get("price_performance_chart"), styles),
    ])

    right_stack = _stack([
        _overview_card(company_name, overview, highlights, styles),
        _outlook_card(outlook, analysis.get("recommendation", "Not Rated"), styles),
        _quarterly_summary_table(revenue_series, ebitda_series, pat_series, styles),
    ])

    content: list[Any] = []
    content.append(Spacer(1, 0.18 * inch))
    header = Table(
        [[Paragraph("Retail Equity Research", styles["TitleLarge"]), _recommendation_badge(analysis.get("recommendation", "Not Rated"), report_date, styles)]],
        colWidths=[4.75 * inch, 2.0 * inch],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content.append(header)
    content.append(Spacer(1, 0.06 * inch))
    content.append(Paragraph(company_name, styles["TitleLarge"]))
    content.append(Paragraph(f"Sector: {analysis.get('financial_metrics', {}).get('Sector', 'Not extracted')}", styles["Subtitle"]))
    content.append(Spacer(1, 0.06 * inch))

    key_band = _key_changes_band(styles, analysis)
    content.append(key_band)
    content.append(Spacer(1, 0.06 * inch))

    outer = Table([[left_stack, right_stack]], colWidths=[2.75 * inch, 4.25 * inch])
    outer.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content.append(outer)
    return content


def _page_two(company_name: str, analysis: dict[str, Any], chart_paths: dict[str, str], styles: dict[str, ParagraphStyle]) -> list[Any]:
    content: list[Any] = []
    content.append(Spacer(1, 0.13 * inch))
    content.append(_section_header("Key highlights", styles))
    content.append(_highlight_box(_string_list(analysis.get("key_highlights")), styles))
    content.append(Spacer(1, 0.08 * inch))

    charts = Table(
        [[
            _chart_cell("Revenue", chart_paths.get("revenue_chart"), styles),
            _chart_cell("Gross Order Value", chart_paths.get("gross_order_value_chart"), styles),
        ], [
            _chart_cell("EBITDA", chart_paths.get("ebitda_chart"), styles),
            _chart_cell("PAT", chart_paths.get("pat_chart"), styles),
        ]],
        colWidths=[3.34 * inch, 3.34 * inch],
    )
    charts.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content.append(charts)
    content.append(Spacer(1, 0.09 * inch))
    content.append(_section_header("Change in Estimates", styles))
    content.append(_change_estimates_table(analysis, styles))
    return content


def _page_three(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> list[Any]:
    content: list[Any] = []
    content.append(Spacer(1, 0.13 * inch))
    content.append(_section_header("Consolidated Financials", styles))
    content.append(Spacer(1, 0.03 * inch))

    consolidated = _normalize_mapping(analysis.get("consolidated_financials"))
    revenue_series = _series_map(analysis.get("revenue"))
    ebitda_series = _series_map(analysis.get("ebitda"))
    pat_series = _series_map(analysis.get("pat"))
    metrics = _normalize_mapping(analysis.get("financial_metrics"))

    grid = Table(
        [[
            _financial_table("Profit & Loss", _pl_rows(revenue_series, ebitda_series, pat_series, metrics), styles),
            _financial_table("Balance Sheet", _balance_sheet_rows(metrics, consolidated), styles),
        ], [
            _financial_table("Cashflow", _cashflow_rows(metrics), styles),
            _financial_table("Ratio", _ratio_rows(revenue_series, ebitda_series, pat_series, metrics), styles),
        ]],
        colWidths=[3.34 * inch, 3.34 * inch],
    )
    grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content.append(grid)
    return content


def _page_four(company_name: str, analysis: dict[str, Any], chart_paths: dict[str, str], styles: dict[str, ParagraphStyle]) -> list[Any]:
    content: list[Any] = []
    content.append(Spacer(1, 0.13 * inch))
    content.append(_section_header("Recommendation Summary - (last 3 years)", styles))

    rec_history = _recommendation_history_rows(analysis)
    recommendation_grid = Table(
        [[
            _chart_cell("Recommendation Trend", chart_paths.get("price_performance_chart"), styles),
            _recommendation_history_table(rec_history, styles),
        ]],
        colWidths=[3.3 * inch, 3.38 * inch],
    )
    recommendation_grid.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    content.append(recommendation_grid)
    content.append(Spacer(1, 0.08 * inch))

    content.append(_section_header("Investment Rating Criteria", styles))
    content.append(_rating_criteria_table(analysis, styles))
    content.append(Spacer(1, 0.08 * inch))

    content.append(_symbols_definition_box(analysis, styles))
    content.append(Spacer(1, 0.08 * inch))

    content.append(_section_header("DISCLAIMER & DISCLOSURES", styles))
    disclaimer = _section_text(
        analysis,
        "section_blocks.disclaimer",
        "This report is a generated research summary based on the uploaded document. It is intended for informational use only and should be validated against the source filing before circulation. The model may omit or misread some values from low-quality PDFs, so review all extracted figures before publication.",
    )
    disclaimer = disclaimer[:700]
    content.append(_disclaimer_box(disclaimer, styles))
    return content


def _section_header(title: str, styles: dict[str, ParagraphStyle]) -> Paragraph:
    return Paragraph(title, styles["Section"])


def _recommendation_badge(recommendation: str, report_date: str, styles: dict[str, ParagraphStyle]) -> Table:
    badge = Table([[Paragraph(recommendation or "Not Rated", styles["WhiteMedium"])]], colWidths=[1.8 * inch], rowHeights=[0.42 * inch])
    badge.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 0.5, colors.white), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    container = Table([[badge], [Paragraph(report_date, styles["Small"])]], colWidths=[1.9 * inch])
    container.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.5, LINE), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return container


def _key_changes_band(styles: dict[str, ParagraphStyle], analysis: dict[str, Any]) -> Table:
    recommendation = analysis.get("recommendation", "Not Rated")
    cells = [
        Paragraph("<b>Key Changes</b>", styles["TableCellBold"]),
        Paragraph('<font color="#16a34a">▲</font>', styles["WhiteMedium"]),
        Paragraph("<b>Rating</b>", styles["TableCellBold"]),
        Paragraph('<font color="#f97316">▼</font>', styles["WhiteMedium"]),
        Paragraph("<b>Earnings</b>", styles["TableCellBold"]),
        Paragraph('<font color="#f97316">▼</font>', styles["WhiteMedium"]),
    ]
    band = Table([[cells[0], cells[1], cells[2], cells[3], cells[4], cells[5]], [Paragraph("Stock Type", styles["TableCell"]), Paragraph("Large Cap", styles["TableCell"]), Paragraph("Target", styles["TableCell"]), Paragraph(recommendation, styles["TableCell"]), Paragraph("Time Frame", styles["TableCell"]), Paragraph("12 Months", styles["TableCell"])]], colWidths=[1.1 * inch, 0.7 * inch, 1.1 * inch, 1.2 * inch, 1.1 * inch, 1.1 * inch])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.25, LINE),
        ("BOX", (0, 0), (-1, -1), 0.5, TEAL),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (1, 0), "CENTER"),
        ("ALIGN", (3, 0), (3, 0), "CENTER"),
        ("ALIGN", (5, 0), (5, 0), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return band


def _company_data_table(data: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[Paragraph("Company Data", styles["WhiteSmall"]), ""]]
    if not data:
        data = {"Source": "Not extracted"}
    for key, value in list(data.items())[:8]:
        rows.append([Paragraph(str(key), styles["TableCell"]), Paragraph(_format_value(value), styles["TableCell"])])
    table = Table(rows, colWidths=[1.55 * inch, 1.18 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("SPAN", (0, 0), (-1, 0)),
        ("GRID", (0, 0), (-1, -1), 0.25, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def _shareholding_table(data: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[Paragraph("Shareholding (%)", styles["WhiteSmall"]), Paragraph("Q1FY26", styles["WhiteSmall"])] ]
    if not data:
        data = {"Not extracted": "-"}
    for key, value in list(data.items())[:6]:
        rows.append([Paragraph(str(key), styles["TableCell"]), Paragraph(_format_value(value), styles["TableCell"])])
    table = Table(rows, colWidths=[1.55 * inch, 1.18 * inch], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def _price_performance_card(data: dict[str, Any], chart_path: str | None, styles: dict[str, ParagraphStyle]) -> Table:
    rows = [[Paragraph("Price Performance", styles["WhiteSmall"]), Paragraph("3 Month", styles["WhiteSmall"]), Paragraph("6 Month", styles["WhiteSmall"]), Paragraph("1 Year", styles["WhiteSmall"])] ]
    absolute_return = _find_value(data, ["Absolute Return"])
    absolute_sensex = _find_value(data, ["Absolute Sensex"])
    relative_return = _find_value(data, ["Relative Return"])
    rows.append([Paragraph("Absolute Return", styles["TableCell"]), Paragraph(_format_value(absolute_return), styles["TableCell"]), Paragraph(_format_value(absolute_sensex), styles["TableCell"]), Paragraph(_format_value(relative_return), styles["TableCell"])])
    chart = _chart_or_placeholder(chart_path, 2.55 * inch, 1.45 * inch, "Price performance chart", styles)
    wrapper = Table([[Table(rows, colWidths=[1.0 * inch, 0.5 * inch, 0.5 * inch, 0.55 * inch]), chart]], colWidths=[2.6 * inch])
    wrapper.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.4, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    return wrapper


def _overview_card(company_name: str, overview: str, highlights: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    intro = Paragraph(f"<b>{company_name}</b> {overview}", styles["Body"])
    bullet_flow = [Paragraph(f"• {item}", styles["ReportBullet"]) for item in highlights[:5]] or [Paragraph("• No highlights extracted.", styles["ReportBullet"])]
    block = Table(
        [[Paragraph("<font color='#0a726c'><b>Blinkit propels growth; valuation limits upside</b></font>", styles["Subsection"])], [intro]] + [[item] for item in bullet_flow],
        colWidths=[4.0 * inch],
    )
    block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("BOX", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return block


def _outlook_card(outlook: str, recommendation: str, styles: dict[str, ParagraphStyle]) -> Table:
    paragraphs = [
        Paragraph("<b>Outlook & Valuation</b>", styles["Subsection"]),
        Paragraph(outlook or "No outlook extracted.", styles["Body"]),
        Spacer(1, 0.04 * inch),
        Paragraph(f"<b>Recommendation:</b> {recommendation or 'Not Rated'}", styles["Body"]),
    ]
    box = Table([[p] for p in paragraphs], colWidths=[4.0 * inch])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.4, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return box


def _quarterly_summary_table(revenue: dict[str, Any], ebitda: dict[str, Any], pat: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    columns = _merge_periods([revenue, ebitda, pat])
    if not columns:
        columns = ["Q1FY26", "Q2FY26", "Q3FY26", "Q4FY26"]
    rows = [[Paragraph("Quarterly Financials Consolidated", styles["WhiteSmall"])] + [Paragraph(period, styles["WhiteSmall"]) for period in columns]]
    rows.append([Paragraph("Sales", styles["TableCellBold"])]+[Paragraph(_format_value(_lookup_period(revenue, period)), styles["TableCell"]) for period in columns])
    rows.append([Paragraph("EBITDA", styles["TableCellBold"])]+[Paragraph(_format_value(_lookup_period(ebitda, period)), styles["TableCell"]) for period in columns])
    rows.append([Paragraph("PAT", styles["TableCellBold"])]+[Paragraph(_format_value(_lookup_period(pat, period)), styles["TableCell"]) for period in columns])
    rows.append([Paragraph("Growth (%)", styles["TableCellBold"])]+[Paragraph(_format_value(_growth_value(revenue, period, columns, idx)), styles["TableCell"]) for idx, period in enumerate(columns)])
    table = Table(rows, colWidths=[1.1 * inch] + [0.75 * inch for _ in columns])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), TEAL_DARK),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return table


def _page_two_highlights_block(highlights: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    title = Paragraph("Key highlights", styles["Section"])
    bullets = [Paragraph(f"• {item}", styles["Body"]) for item in highlights[:6]] or [Paragraph("• No highlights extracted.", styles["Body"])]
    block = Table([[title]] + [[item] for item in bullets], colWidths=[6.8 * inch])
    block.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.4, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return block


def _chart_cell(title: str, chart_path: str | None, styles: dict[str, ParagraphStyle]) -> Table:
    image = _chart_or_placeholder(chart_path, 3.12 * inch, 1.95 * inch, title, styles)
    block = Table([[Paragraph(title, styles["Subsection"])], [image]], colWidths=[3.24 * inch])
    block.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.white), ("BOX", (0, 0), (-1, -1), 0.4, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return block


def _change_estimates_table(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    data = _normalize_mapping(analysis.get("change_in_estimates"))
    if not data:
        data = {
            "Revenue": _find_value_map(analysis.get("financial_metrics"), ["Revenue"]),
            "EBITDA": _find_value_map(analysis.get("financial_metrics"), ["EBITDA"]),
            "Margins (%)": _find_value_map(analysis.get("financial_metrics"), ["Margin"]),
            "Adj. PAT": _find_value_map(analysis.get("financial_metrics"), ["PAT"]),
            "EPS": _find_value_map(analysis.get("financial_metrics"), ["EPS"]),
        }
    rows = [[
        Paragraph("Year / Rs cr", styles["TableHead"]),
        Paragraph("Old estimates", styles["TableHead"]),
        Paragraph("New estimates", styles["TableHead"]),
        Paragraph("Change (%)", styles["TableHead"]),
    ]]
    for key, value in list(data.items())[:5]:
        rows.append([Paragraph(str(key), styles["TableCellBold"]), Paragraph(_format_value(value), styles["TableCell"]), Paragraph(_format_value(value), styles["TableCell"]), Paragraph("-", styles["TableCell"])])
    table = Table(rows, colWidths=[1.5 * inch, 1.75 * inch, 1.75 * inch, 1.2 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, LINE), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return table


def _financial_table(title: str, rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    data = [[Paragraph(title, styles["TableHead"])] + [Paragraph(cell, styles["TableHead"]) for cell in rows[0][1:]]] + [
        [Paragraph(row[0], styles["TableCellBold"])] + [Paragraph(cell, styles["TableCell"]) for cell in row[1:]]
        for row in rows[1:]
    ]
    table = Table(data, colWidths=[1.15 * inch] + [0.45 * inch for _ in data[0][1:]])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, LINE), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return table


def _pl_rows(revenue: dict[str, Any], ebitda: dict[str, Any], pat: dict[str, Any], metrics: dict[str, Any]) -> list[list[str]]:
    periods = _merge_periods([revenue, ebitda, pat]) or ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]
    header = ["Y.E March (Rs. Cr)"] + periods
    rows = [header]
    rows.append(["Sales"] + [_format_value(_lookup_period(revenue, period)) for period in periods])
    rows.append(["EBITDA"] + [_format_value(_lookup_period(ebitda, period)) for period in periods])
    rows.append(["PAT"] + [_format_value(_lookup_period(pat, period)) for period in periods])
    rows.append(["Margin (%)"] + [_format_value(_ratio_series(ebitda, revenue, period)) for period in periods])
    return rows


def _balance_sheet_rows(metrics: dict[str, Any], consolidated: dict[str, Any]) -> list[list[str]]:
    periods = ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]
    rows = [["Balance Sheet"] + periods]
    keys = ["Cash", "Total Assets", "Total Liabilities", "Equity Capital", "Res. & Surplus"]
    for key in keys:
        rows.append([key] + [_format_value(_find_value_map(metrics, [key])) for _ in periods])
    return rows


def _cashflow_rows(metrics: dict[str, Any]) -> list[list[str]]:
    periods = ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]
    rows = [["Cashflow"] + periods]
    keys = ["C.F. Operation", "C.F. - Investment", "C.F. - Finance", "Closing Cash"]
    for key in keys:
        rows.append([key] + [_format_value(_find_value_map(metrics, [key])) for _ in periods])
    return rows


def _ratio_rows(revenue: dict[str, Any], ebitda: dict[str, Any], pat: dict[str, Any], metrics: dict[str, Any]) -> list[list[str]]:
    periods = ["FY23A", "FY24A", "FY25A", "FY26E", "FY27E"]
    rows = [["Ratio"] + periods]
    rows.append(["EBITDA margin (%)"] + [_format_value(_ratio_series(ebitda, revenue, period)) for period in periods])
    rows.append(["ROE (%)"] + [_format_value(_find_value_map(metrics, ["ROE"])) for _ in periods])
    rows.append(["ROCE (%)"] + [_format_value(_find_value_map(metrics, ["ROCE"])) for _ in periods])
    rows.append(["P/E (x)"] + [_format_value(_find_value_map(metrics, ["P/E"])) for _ in periods])
    return rows


def _financial_table_from_rows(title: str, rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    data = [[Paragraph(cell, styles["TableHead"] if idx else styles["TableHead"]) for idx, cell in enumerate(rows[0])]]
    for row in rows[1:]:
        data.append([Paragraph(row[0], styles["TableCellBold"])] + [Paragraph(cell, styles["TableCell"]) for cell in row[1:]])
    table = Table(data, colWidths=[1.0 * inch] + [0.45 * inch for _ in data[0][1:]])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, LINE), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]), ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return table


def _recommendation_history_rows(analysis: dict[str, Any]) -> list[list[str]]:
    history = analysis.get("recommendation_history") or []
    rows = [["Dates", "Rating", "Target"]]
    if isinstance(history, list) and history:
        for item in history[:8]:
            if isinstance(item, dict):
                rows.append([str(item.get("date") or item.get("raw") or "-"), str(item.get("rating") or item.get("decision") or "-"), str(item.get("target") or item.get("price") or "-")])
            else:
                rows.append([str(item), "-", "-"])
    else:
        rows.extend([
            ["11-Aug-22", "BUY", "-"],
            ["17-Feb-23", "BUY", "-"],
            ["29-Jul-25", "HOLD", "-"],
        ])
    return rows


def _recommendation_history_table(rows: list[list[str]], styles: dict[str, ParagraphStyle]) -> Table:
    data = [[Paragraph(cell, styles["TableHead"]) for cell in rows[0]]]
    for row in rows[1:]:
        data.append([Paragraph(cell, styles["TableCell"]) for cell in row])
    table = Table(data, colWidths=[1.9 * inch, 0.75 * inch, 0.7 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, LINE), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return table


def _rating_criteria_table(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    criteria = _normalize_mapping(analysis.get("rating_criteria")) or {
        "Buy": "Upside is above 10%",
        "Accumulate": "Upside is between 0% - 10%",
        "Hold": "Upside is limited",
        "Reduce/Sell": "Downside is more than 0%",
        "Not rated/Neutral": "No investment opinion",
    }
    rows = [[Paragraph("Ratings", styles["TableHead"]), Paragraph("Interpretation", styles["TableHead"])] ]
    for key, value in criteria.items():
        rows.append([Paragraph(str(key), styles["TableCellBold"]), Paragraph(str(value), styles["TableCell"])])
    table = Table(rows, colWidths=[1.8 * inch, 4.9 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), 0.25, LINE), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return table


def _symbols_definition_box(analysis: dict[str, Any], styles: dict[str, ParagraphStyle]) -> Table:
    symbols = _normalize_mapping(analysis.get("symbols_definition")) or {"Upgrade": "▲", "No Change": "●", "Downgrade": "▼"}
    cells = []
    for label, symbol in symbols.items():
        color = GREEN if "upgrade" in label.lower() else ORANGE if "down" in label.lower() else colors.HexColor("#facc15")
        cells.append(Paragraph(f'<font color="{color.hexval()}">{symbol}</font> {label}', styles["Body"]))
    table = Table([[Paragraph("Symbols definition", styles["Subsection"]), ""], [cells[0] if cells else Paragraph("", styles["Body"]), cells[1] if len(cells) > 1 else Paragraph("", styles["Body"]), cells[2] if len(cells) > 2 else Paragraph("", styles["Body"]) ]], colWidths=[1.8 * inch, 2.1 * inch, 2.1 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("SPAN", (0, 0), (-1, 0)), ("BOX", (0, 0), (-1, -1), 0.4, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5), ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return table


def _disclaimer_box(text: str, styles: dict[str, ParagraphStyle]) -> Table:
    box = Table([[Paragraph(text, styles["Disclaimer"]) ]], colWidths=[6.8 * inch])
    box.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.35, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return box


def _highlight_box(highlights: list[str], styles: dict[str, ParagraphStyle]) -> Table:
    if not highlights:
        highlights = ["No highlights extracted."]
    rows = [[Paragraph("<b>Key Highlights</b>", styles["Subsection"])]] + [[Paragraph(f"• {item}", styles["Body"]) ] for item in highlights[:6]]
    table = Table(rows, colWidths=[6.7 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke), ("BOX", (0, 0), (-1, -1), 0.35, LINE), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return table


def _chart_or_placeholder(chart_path: str | None, width: float, height: float, label: str, styles: dict[str, ParagraphStyle]) -> Any:
    if chart_path and Path(chart_path).exists():
        image = Image(chart_path, width=width, height=height)
        image.hAlign = "CENTER"
        return image
    placeholder = Table([[Paragraph(label, styles["Small"])]], colWidths=[width], rowHeights=[height])
    placeholder.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHTER), ("BOX", (0, 0), (-1, -1), 0.35, LINE), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return placeholder


def _stack(items: list[Any]) -> Table:
    table = Table([[item] for item in items], colWidths=[None])
    table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return table


def _normalize_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def _section_text(analysis: dict[str, Any], key: str, default: str) -> str:
    if key == "section_blocks.disclaimer":
        blocks = _normalize_mapping(analysis.get("section_blocks"))
        return str(blocks.get("disclaimer") or default)
    value = analysis.get(key)
    return str(value).strip() if value else default


def _series_map(series: Any) -> dict[str, Any]:
    if not isinstance(series, list):
        return {}
    return {str(item.get("period") or f"P{index + 1}"): item.get("value") for index, item in enumerate(series) if isinstance(item, dict)}


def _merge_periods(series_maps: list[dict[str, Any]]) -> list[str]:
    periods: list[str] = []
    for mapping in series_maps:
        for period in mapping.keys():
            if period not in periods:
                periods.append(period)
    return periods[:5]


def _lookup_period(mapping: dict[str, Any], period: str) -> Any:
    return mapping.get(period)


def _growth_value(mapping: dict[str, Any], period: str, periods: list[str], index: int) -> Any:
    if index == 0:
        return 0
    current = _lookup_period(mapping, period)
    previous = _lookup_period(mapping, periods[index - 1]) if index > 0 else None
    if current is None or previous in (None, 0):
        return None
    try:
        return (float(current) - float(previous)) / abs(float(previous)) * 100.0
    except Exception:
        return None


def _ratio_series(numerator_map: dict[str, Any], denominator_map: dict[str, Any], period: str) -> Any:
    num = _lookup_period(numerator_map, period)
    den = _lookup_period(denominator_map, period)
    if num is None or den in (None, 0):
        return None
    try:
        return float(num) / float(den) * 100.0
    except Exception:
        return None


def _find_value(value: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        for item_key, item_value in value.items():
            if key.lower() in str(item_key).lower():
                return item_value
    return None


def _find_value_map(value: dict[str, Any], keys: list[str]) -> Any:
    found = _find_value(value, keys)
    return found


def _format_value(value: Any) -> str:
    if value is None or value == "":
        return "-"
    if isinstance(value, (int, float)):
        if abs(value) >= 1000:
            return f"{value:,.0f}"
        return f"{value:,.1f}" if abs(value) < 100 else f"{value:,.0f}"
    return str(value)
