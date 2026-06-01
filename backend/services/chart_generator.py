from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


TEAL = "#0ea5a4"
TEAL_DARK = "#0f766e"
ORANGE = "#f97316"
SLATE = "#334155"
GRID = "#dbe3ea"


def create_report_charts(analysis: dict[str, Any], company_name: str, generated_dir: Path) -> dict[str, str]:
    generated_dir.mkdir(parents=True, exist_ok=True)
    slug = company_name.lower().replace(" ", "_")

    revenue_path = generated_dir / f"{slug}_revenue_chart.png"
    gross_order_value_path = generated_dir / f"{slug}_gross_order_value_chart.png"
    ebitda_path = generated_dir / f"{slug}_ebitda_chart.png"
    pat_path = generated_dir / f"{slug}_pat_chart.png"
    price_performance_path = generated_dir / f"{slug}_price_performance_chart.png"

    revenue_series = _series_points(analysis.get("revenue"))
    gov_series = _series_points(analysis.get("gross_order_value"))
    ebitda_series = _series_points(analysis.get("ebitda"))
    pat_series = _series_points(analysis.get("pat"))
    price_series = _series_points(analysis.get("price_performance"))

    _render_price_chart(
        primary=price_series,
        secondary=None,
        title="Price Performance",
        output_path=price_performance_path,
        primary_label=company_name,
        secondary_label="Benchmark",
    )
    _render_combo_chart(
        primary=revenue_series,
        secondary=_growth_series(revenue_series),
        title="Revenue",
        output_path=revenue_path,
        primary_label="Revenue (Rs.cr)",
        secondary_label="Growth (YoY)",
    )
    _render_combo_chart(
        primary=gov_series,
        secondary=_growth_series(gov_series),
        title="Gross Order Value",
        output_path=gross_order_value_path,
        primary_label="GOV (Rs.cr)",
        secondary_label="Growth (YoY)",
    )
    _render_combo_chart(
        primary=ebitda_series,
        secondary=_margin_series(ebitda_series, revenue_series),
        title="EBITDA",
        output_path=ebitda_path,
        primary_label="EBITDA (Rs.cr)",
        secondary_label="Margin",
    )
    _render_combo_chart(
        primary=pat_series,
        secondary=_margin_series(pat_series, revenue_series),
        title="PAT",
        output_path=pat_path,
        primary_label="PAT (Rs.cr)",
        secondary_label="Margin",
    )

    return {
        "price_performance_chart": str(price_performance_path),
        "revenue_chart": str(revenue_path),
        "gross_order_value_chart": str(gross_order_value_path),
        "ebitda_chart": str(ebitda_path),
        "pat_chart": str(pat_path),
    }


def _series_points(series: Any) -> list[tuple[str, float]]:
    if not isinstance(series, list):
        return []

    points: list[tuple[str, float]] = []
    for index, item in enumerate(series):
        if isinstance(item, dict):
            label = str(item.get("period") or item.get("year") or item.get("label") or f"P{index + 1}")
            value = item.get("value") if item.get("value") is not None else item.get("amount")
        else:
            label = f"P{index + 1}"
            value = item
        numeric = _to_float(value)
        if numeric is not None:
            points.append((label, numeric))
    return points


def _growth_series(series: list[tuple[str, float]]) -> list[float]:
    if not series:
        return []
    values = [value for _, value in series]
    growth: list[float] = [0.0]
    for current, previous in zip(values[1:], values[:-1]):
        if previous == 0:
            growth.append(0.0)
        else:
            growth.append((current - previous) / abs(previous) * 100.0)
    return growth


def _margin_series(series: list[tuple[str, float]], denominator_series: list[tuple[str, float]]) -> list[float]:
    if not series:
        return []
    if not denominator_series:
        return _growth_series(series)

    numerator = [value for _, value in series]
    denominator = [value for _, value in denominator_series]
    margins: list[float] = []
    for index, value in enumerate(numerator):
        base = denominator[index] if index < len(denominator) else None
        if not base:
            margins.append(0.0)
            continue
        margins.append(value / base * 100.0)
    return margins


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    try:
        return float(text)
    except ValueError:
        return None


def _render_price_chart(
    primary: list[tuple[str, float]],
    secondary: list[tuple[str, float]] | None,
    title: str,
    output_path: Path,
    primary_label: str,
    secondary_label: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 3.0), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#ffffff")

    if primary:
        x_values = list(range(len(primary)))
        labels = [label for label, _ in primary]
        values = [value for _, value in primary]
        ax.plot(x_values, values, color=TEAL_DARK, linewidth=2.0, marker="o", markersize=3.5, label=primary_label)
        if secondary:
            secondary_values = [value for _, value in secondary[: len(values)]]
            if secondary_values:
                ax.plot(x_values[: len(secondary_values)], secondary_values, color="#94a3b8", linewidth=1.8, label=secondary_label)
        ax.set_xticks(x_values)
        ax.set_xticklabels(labels, fontsize=8, color=SLATE)
        ax.tick_params(axis="y", labelsize=8, colors=SLATE)
        ax.grid(axis="y", linestyle="--", alpha=0.25, color=GRID)
        ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.25), ncol=2, frameon=False, fontsize=8)
    else:
        _render_empty_chart(ax, title, "No price performance data was extracted")

    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", color=TEAL_DARK, pad=10)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _render_combo_chart(
    primary: list[tuple[str, float]],
    secondary: list[float],
    title: str,
    output_path: Path,
    primary_label: str,
    secondary_label: str,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.2, 3.2), dpi=180)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("#ffffff")

    if primary:
        x_values = list(range(len(primary)))
        labels = [label for label, _ in primary]
        values = [value for _, value in primary]

        ax.bar(x_values, values, color=TEAL, width=0.42, label=primary_label)
        ax.set_xticks(x_values)
        ax.set_xticklabels(labels, fontsize=8, color=SLATE)
        ax.tick_params(axis="y", labelsize=8, colors=SLATE)
        ax.grid(axis="y", linestyle="--", alpha=0.22, color=GRID)

        line_ax = ax.twinx()
        if secondary:
            line_ax.plot(x_values[: len(secondary)], secondary, color=ORANGE, linewidth=1.8, marker="o", markersize=3, label=secondary_label)
            for index, value in enumerate(secondary):
                line_ax.annotate(
                    _format_percent(value),
                    (x_values[index], value),
                    textcoords="offset points",
                    xytext=(0, 6),
                    ha="center",
                    fontsize=7,
                    color="#6b7280",
                )
        line_ax.tick_params(axis="y", labelsize=8, colors=SLATE)
        line_ax.spines["right"].set_color("#d1d5db")
        line_ax.spines["top"].set_visible(False)
        line_ax.spines["left"].set_visible(False)
        line_ax.grid(False)

        handles_left, labels_left = ax.get_legend_handles_labels()
        handles_right, labels_right = line_ax.get_legend_handles_labels()
        ax.legend(
            handles_left + handles_right,
            labels_left + labels_right,
            loc="lower center",
            bbox_to_anchor=(0.5, -0.28),
            ncol=2,
            frameon=False,
            fontsize=8,
        )
    else:
        _render_empty_chart(ax, title, "No chart data available")

    ax.set_title(title, loc="left", fontsize=12.5, fontweight="bold", color=TEAL_DARK, pad=10)
    _style_axes(ax)
    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def _render_empty_chart(ax, title: str, message: str) -> None:
    ax.text(0.5, 0.52, message, ha="center", va="center", fontsize=10, color="#64748b", transform=ax.transAxes)
    ax.set_xticks([])
    ax.set_yticks([])


def _style_axes(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cbd5e1")
    ax.spines["bottom"].set_color("#cbd5e1")


def _format_percent(value: float) -> str:
    if value is None:
        return ""
    if abs(value) < 10:
        return f"{value:.1f}%"
    return f"{value:.0f}%"
