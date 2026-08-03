"""Render DeepSeek V4-Flash-0731 matched-comparison charts as pure SVG.

Reads experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json.
Does not open sealed holdout row JSONL. No matplotlib dependency.
"""

from __future__ import annotations

import json
import xml.sax.saxutils as xml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "experiments/deepseek_v4_flash_0731_matched_comparison_20260803.json"
OUTPUT = ROOT / "docs/research/assets/deepseek_v4_flash_0731_comparison_2026-08-03"

BG = "#FBFCFD"
INK = "#25313C"
MUTED = "#66727D"
GRID = "#DDE3E8"
BLUE = "#2563A6"
TEAL = "#167C80"
ORANGE = "#D97706"
GOLD = "#B8871B"
FONT = "DejaVu Sans, Arial, sans-serif"


def _esc(text: str) -> str:
    return xml.escape(text, {'"': "&quot;"})


def _write(path: Path, body: str, *, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
            f'height="{height}" viewBox="0 0 {width} {height}">\n'
            f'<rect width="100%" height="100%" fill="{BG}"/>\n'
            f"{body}\n</svg>\n"
        ),
        encoding="utf-8",
    )


def _header(title: str, subtitle: str, x: int = 36) -> str:
    return (
        f'<text x="{x}" y="36" fill="{INK}" font-family="{FONT}" '
        f'font-size="20" font-weight="700">{_esc(title)}</text>\n'
        f'<text x="{x}" y="58" fill="{MUTED}" font-family="{FONT}" '
        f'font-size="12">{_esc(subtitle)}</text>'
    )


def _barbell_chart(
    filename: str,
    title: str,
    subtitle: str,
    rows: list[tuple[str, float, float]],
    *,
    xlabel: str,
) -> None:
    width, height = 980, 420
    left, right = 280, 920
    top, row_h = 100, 52
    values = [v for _, a, b in rows for v in (a, b)]
    xmin = max(0.0, min(values) - 0.04)
    xmax = min(1.0, max(values) + 0.04)
    span = xmax - xmin or 1.0

    def x_of(v: float) -> float:
        return left + (v - xmin) / span * (right - left)

    parts = [_header(title, subtitle)]
    for i in range(5):
        tick = xmin + span * i / 4
        x = x_of(tick)
        y2 = top + row_h * len(rows) - 8
        parts.append(
            f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" '
            f'y2="{y2}" stroke="{GRID}" stroke-width="1"/>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{top + row_h * len(rows) + 18}" '
            f'fill="{MUTED}" font-family="{FONT}" font-size="11" '
            f'text-anchor="middle">{tick:.2f}</text>'
        )
    for i, (label, prior, update) in enumerate(rows):
        y = top + i * row_h + 18
        x0, x1 = x_of(prior), x_of(update)
        parts.append(
            f'<text x="24" y="{y + 4}" fill="{INK}" '
            f'font-family="{FONT}" font-size="13">{_esc(label)}</text>'
        )
        parts.append(
            f'<line x1="{x0:.1f}" y1="{y}" x2="{x1:.1f}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="4" stroke-linecap="round"/>'
        )
        parts.append(
            f'<circle cx="{x0:.1f}" cy="{y}" r="7" fill="{BG}" '
            f'stroke="{BLUE}" stroke-width="2.4"/>'
        )
        parts.append(
            f'<circle cx="{x1:.1f}" cy="{y}" r="7" '
            f'fill="{TEAL}" stroke="{TEAL}"/>'
        )
        prior_right = prior >= update
        parts.append(
            f'<text x="{(x0 + 10) if prior_right else (x0 - 10):.1f}" '
            f'y="{y + 4}" fill="{INK}" font-family="{FONT}" '
            f'font-size="11" '
            f'text-anchor="{"start" if prior_right else "end"}">'
            f"{prior:.3f}</text>"
        )
        parts.append(
            f'<text x="{(x1 - 10) if prior_right else (x1 + 10):.1f}" '
            f'y="{y + 4}" fill="{INK}" font-family="{FONT}" '
            f'font-size="11" '
            f'text-anchor="{"end" if prior_right else "start"}">'
            f"{update:.3f}</text>"
        )
    legend_y = height - 34
    parts.append(
        f'<circle cx="280" cy="{legend_y}" r="6" fill="{BG}" '
        f'stroke="{BLUE}" stroke-width="2.2"/>'
        f'<text x="294" y="{legend_y + 4}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="12">'
        f"Prior (ruleset-matched)</text>"
        f'<circle cx="500" cy="{legend_y}" r="6" fill="{TEAL}"/>'
        f'<text x="514" y="{legend_y + 4}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="12">0731 live</text>'
        f'<text x="680" y="{legend_y + 4}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="12">{_esc(xlabel)}</text>'
    )
    _write(OUTPUT / filename, "\n".join(parts), width=width, height=height)


def _family_delta_chart(
    filename: str,
    title: str,
    subtitle: str,
    families: dict[str, dict],
) -> None:
    width, height = 900, 360
    left, bar_max = 220, 520
    top, row_h = 100, 48
    order = ["SeizureFrequency", "Diagnosis", "Investigations", "Prescription"]
    deltas = [families[name]["delta"] for name in order]
    abs_max = max(abs(v) for v in deltas) * 1.25 or 0.1
    zero = left + bar_max / 2

    parts = [_header(title, subtitle)]
    y2 = top + row_h * len(order) - 10
    parts.append(
        f'<line x1="{zero:.1f}" y1="{top - 8}" x2="{zero:.1f}" '
        f'y2="{y2}" stroke="{GRID}" stroke-width="1.5"/>'
    )
    for i, name in enumerate(order):
        delta = families[name]["delta"]
        y = top + i * row_h
        w = abs(delta) / abs_max * (bar_max / 2)
        color = TEAL if delta >= 0 else ORANGE
        x = zero if delta >= 0 else zero - w
        parts.append(
            f'<text x="24" y="{y + 22}" fill="{INK}" '
            f'font-family="{FONT}" font-size="13">{_esc(name)}</text>'
        )
        parts.append(
            f'<rect x="{x:.1f}" y="{y + 8}" width="{max(w, 1):.1f}" '
            f'height="24" fill="{color}" rx="3"/>'
        )
        parts.append(
            f'<text x="{(x + w + 8) if delta >= 0 else (x - 8):.1f}" '
            f'y="{y + 25}" fill="{INK}" font-family="{FONT}" '
            f'font-size="12" '
            f'text-anchor="{"start" if delta >= 0 else "end"}">'
            f"{delta:+.4f}</text>"
        )
    parts.append(
        f'<text x="{left}" y="{height - 28}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="12">'
        f"Δ clinical fact F1 on ExECT dev140 "
        f"(ruleset-matched)</text>"
    )
    _write(OUTPUT / filename, "\n".join(parts), width=width, height=height)


def _gan_ladder_chart(filename: str, title: str, subtitle: str, cell: dict) -> None:
    width, height = 900, 340
    left, right = 260, 820
    top = 110
    frozen = cell["frozen_panel"]
    prior = cell["prior_ruleset_matched"]
    update = cell["update_0731"]
    steps = [
        (
            "Frozen matched panel",
            frozen["purist_accuracy"],
            frozen["purist_correct"],
            BLUE,
        ),
        (
            "Final-ruleset replay",
            prior["purist_accuracy"],
            prior["purist_correct"],
            GOLD,
        ),
        (
            "0731 live",
            update["purist_accuracy"],
            update["purist_correct"],
            TEAL,
        ),
    ]
    values = [v for _, v, _, _ in steps]
    xmin, xmax = min(values) - 0.03, max(values) + 0.03
    span = xmax - xmin

    def x_of(v: float) -> float:
        return left + (v - xmin) / span * (right - left)

    parts = [_header(title, subtitle)]
    y = top + 40
    for i in range(len(steps) - 1):
        x0, x1 = x_of(steps[i][1]), x_of(steps[i + 1][1])
        parts.append(
            f'<line x1="{x0:.1f}" y1="{y}" x2="{x1:.1f}" y2="{y}" '
            f'stroke="{GRID}" stroke-width="5" stroke-linecap="round"/>'
        )
    for label, value, correct, color in steps:
        x = x_of(value)
        parts.append(f'<circle cx="{x:.1f}" cy="{y}" r="10" fill="{color}"/>')
        parts.append(
            f'<text x="{x:.1f}" y="{y - 22}" fill="{INK}" '
            f'font-family="{FONT}" font-size="12" text-anchor="middle" '
            f'font-weight="700">{value:.3f}</text>'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y + 34}" fill="{MUTED}" '
            f'font-family="{FONT}" font-size="12" text-anchor="middle">'
            f"{_esc(label)}</text>"
        )
        parts.append(
            f'<text x="{x:.1f}" y="{y + 52}" fill="{MUTED}" '
            f'font-family="{FONT}" font-size="11" text-anchor="middle">'
            f"{correct}/450 Purist</text>"
        )
    parts.append(
        f'<text x="36" y="{height - 28}" fill="{MUTED}" '
        f'font-family="{FONT}" font-size="12">'
        f"Ruleset-matched compare uses final-ruleset replay (348), "
        f"not frozen 344 alone.</text>"
    )
    _write(OUTPUT / filename, "\n".join(parts), width=width, height=height)


def _delta_summary_chart(
    filename: str,
    title: str,
    subtitle: str,
    rows: list[tuple[str, float, str]],
) -> None:
    width, height = 900, 380
    left, max_w = 320, 420
    top, row_h = 100, 48
    max_abs = max(abs(d) for _, d, _ in rows) * 1.15 or 0.05
    parts = [_header(title, subtitle)]
    for i, (label, delta, unit) in enumerate(rows):
        y = top + i * row_h
        w = abs(delta) / max_abs * max_w
        parts.append(
            f'<text x="24" y="{y + 22}" fill="{INK}" '
            f'font-family="{FONT}" font-size="13">{_esc(label)}</text>'
        )
        parts.append(
            f'<rect x="{left}" y="{y + 8}" width="{max(w, 2):.1f}" '
            f'height="24" fill="{TEAL}" rx="3"/>'
        )
        parts.append(
            f'<text x="{left + w + 10:.1f}" y="{y + 25}" fill="{INK}" '
            f'font-family="{FONT}" font-size="12">'
            f"{delta:+.4f} {_esc(unit)}</text>"
        )
    _write(OUTPUT / filename, "\n".join(parts), width=width, height=height)


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    cells = data["cells"]

    def _pair(cell_key: str) -> tuple[float, float]:
        cell = cells[cell_key]
        return cell["prior"]["value"], cell["update_0731"]["value"]

    _barbell_chart(
        "exect_prior_vs_0731.svg",
        "ExECT DeepSeek: prior vs 0731",
        "Ruleset-matched on dev140; test60 uses retained prior "
        "panel vs live 0731",
        [
            ("dev140 · llm only", *_pair("exectv2_dev140_llm_only")),
            ("dev140 · llm + rules", *_pair("exectv2_dev140_llm_with_rules")),
            ("test60 · llm only", *_pair("exectv2_test60_llm_only")),
            ("test60 · llm + rules", *_pair("exectv2_test60_llm_with_rules")),
        ],
        xlabel="Clinical fact F1",
    )

    _family_delta_chart(
        "exect_dev140_family_deltas.svg",
        "ExECT dev140 family deltas",
        "0731 live minus ruleset-matched prior (clinical_headline)",
        cells["exectv2_dev140_llm_with_rules"]["family_clinical_headline"],
    )

    gan = cells["gan2026_test450_llm_with_rules"]
    _gan_ladder_chart(
        "gan_test450_ladder.svg",
        "Gan test450 llm + rules ladder",
        "Frozen panel → final-ruleset replay of prior raws → 0731 live",
        gan,
    )

    _delta_summary_chart(
        "cross_task_delta_summary.svg",
        "Ruleset-matched provider-update deltas",
        "DeepSeek V4 Flash prior panel cell → 0731 live; "
        "tasks use native metrics",
        [
            (
                "ExECT dev140 llm + rules",
                cells["exectv2_dev140_llm_with_rules"]["delta"],
                "F1",
            ),
            (
                "ExECT dev140 llm only",
                cells["exectv2_dev140_llm_only"]["delta"],
                "F1",
            ),
            (
                "ExECT test60 llm + rules",
                cells["exectv2_test60_llm_with_rules"]["delta"],
                "F1",
            ),
            (
                "ExECT test60 llm only",
                cells["exectv2_test60_llm_only"]["delta"],
                "F1",
            ),
            (
                "Gan test450 llm + rules",
                gan["delta_vs_ruleset_matched_purist"],
                "Purist",
            ),
        ],
    )
    print(f"Wrote charts to {OUTPUT}")


if __name__ == "__main__":
    main()
