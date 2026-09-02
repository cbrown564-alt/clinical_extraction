"""Grouped-column figures for the Gan results section.

Reads sealed comparison.json aggregates only. Does not open row files.
"""

from __future__ import annotations

import json
import textwrap
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.cells import normalize_repair_mode
from clinical_extraction.paper.roster import living_models

ROOT = discover_repo_root(start=Path(__file__))
FIVE_CELL_TEST450 = (
    ROOT / "paper_experiments/gan/five_cell_grid/gemini37flash/test450/comparison.json"
)
GAN_RULES_OWNER = ROOT / "paper_experiments/gan/gan_rules.json"
GEMINI_DEV750_RUNGS = ROOT / "paper_experiments/gan/rungs/gemini37flash/dev750/comparison.json"
CELL5_DEV750 = (
    ROOT
    / "experiments/paper/gan_llm_select_from_extract/gemini37flash"
    / "gan_llm_extract/dev750/comparison.json"
)
RUNGS_ROOT = ROOT / "paper_experiments/gan/rungs"
CELL_BARBELL_LABELS = ("Rules only", "LLM and rules", "LLM only")
BARBELL_Y_LABEL_WRAP = 10
BARBELL_CONNECTOR_MIN_ABS_DELTA = 0.012
BARBELL_DELTA_LABEL_MIN_ABS_DELTA = 0.05
SPLIT_COLORS = {
    "Development": "#7C8B9E",
    "Test": "#15324F",
}
FIGURE_DIR = ROOT / "paper/draft"
STAGE_ORDER = ("Find", "Encode", "Select")
# Each stop scores the answer submitted so far, not the stage in isolation.
# The paper reports two stops (extract, decide); the encode stop stays
# available for repository figures.
STAGE_LEGEND_LABELS = {
    "Find": "Provisional answer (after extract)",
    "Encode": "After encode",
    "Select": "Final answer (after decide)",
}
PAPER_STAGES = ("Find", "Select")
STAGE_COLORS = {
    "Find": "#8C9BAE",
    "Encode": "#12968F",
    "Select": "#15324F",
}
AXIS_GREY = "#CBD5E1"
GRID_GREY = "#E2E8F0"
LABEL_BLACK = "#1E293B"
LATIN_MODERN_NAME = "Latin Modern Roman"
LATIN_MODERN_CANDIDATES = (
    Path("/Library/TeX/Root/texmf-dist/fonts/opentype/public/lm/lmroman10-regular.otf"),
)
MODEL_LABELS = {
    "gemini37flash": "Gemini 3.7 Flash",
    "grok46": "Grok 4.6",
    "gpt56luna": "GPT-5.6 Luna",
    "deepseek_v4_flash": "DeepSeek V4 Flash",
    "qwen38_27b": "Qwen 3.8 27B",
    "gemma4_26b": "Gemma 4 26B",
}

AA_HEALTHCARE_INDEX = {
    "grok46": 45.0,
    "gemini37flash": 39.0,
    "deepseek_v4_flash": 38.0,
    "gpt56luna": 35.0,
    "qwen38_27b": 35.0,
    "gemma4_26b": 15.0,
}

PURIST_CATEGORY_ORDER = (
    "seizure_freq_1ormore_daily",
    "seizure_freq_more1week_less1day",
    "seizure_freq_1_per_week",
    "seizure_freq_more1mon_less1week",
    "seizure_freq_1_per_mon",
    "seizure_freq_more1per6mon_less1mon",
    "seizure_freq_1_per_6mon",
    "seizure_freq_1_per_yr",
    "seizure_freq_unknown",
    "currently_no_seizure",
)

PURIST_DISPLAY_LABELS = {
    "seizure_freq_1ormore_daily": "Daily",
    "seizure_freq_more1week_less1day": "More than weekly, less than daily",
    "seizure_freq_1_per_week": "Once a week",
    "seizure_freq_more1mon_less1week": "More than monthly, less than weekly",
    "seizure_freq_1_per_mon": "Once a month",
    "seizure_freq_more1per6mon_less1mon": "More than 6 months, less than monthly",
    "seizure_freq_1_per_6mon": "Once every 6 months",
    "seizure_freq_1_per_yr": "Less than once every 6 months",
    "seizure_freq_unknown": "Unknown",
    "currently_no_seizure": "Seizure free",
}

PRAGMATIC_CATEGORY_ORDER = (
    "seizure_frequent",
    "seizure_infrequent",
    "seizure_freq_unknown",
    "currently_no_seizure",
)

PRAGMATIC_DISPLAY_LABELS = {
    "seizure_frequent": "Frequent",
    "seizure_infrequent": "Infrequent",
    "seizure_freq_unknown": "Unknown",
    "currently_no_seizure": "Seizure free",
}


@dataclass(frozen=True)
class GroupedColumns:
    """One grouped-column chart: categories on x, stages as series."""

    categories: list[str]
    series: dict[str, list[float]]
    n: int
    ylabel: str = "Purist micro-F1"


@dataclass(frozen=True)
class BarbellPairs:
    """One barbell chart: categories on y, two splits as paired points."""

    categories: list[str]
    development: list[float]
    holdout: list[float]
    n_development: int
    n_holdout: int
    ylabel: str = "Purist micro-F1"


@dataclass(frozen=True)
class ConfusionMatrixData:
    """Confusion matrix data for multi-class classification."""

    categories: list[str]
    labels: list[str]
    matrix: list[list[int]]
    n: int
    title: str = "Purist Classification Confusion Matrix"


@dataclass(frozen=True)
class ScatterPlotData:
    """Scatter plot data for external capability vs task performance."""

    points: list[tuple[str, float, float]]
    xlabel: str = "Artificial Analysis Healthcare & Medical Index"
    ylabel: str = "Purist micro-F1"
    title: str = ""


def gemini_cells_1_3_5(payload: Mapping[str, Any]) -> GroupedColumns:
    """Return Gemini cells 1 / 3 / 5 at find, encode, and select."""

    n = int(payload["n"])
    cells = payload["cells"]
    rows = (
        ("Rules", cells["rules"]),
        ("Both", cells["llm_extract_then_rules"]),
        ("LLM", cells["llm"]),
    )
    find_vals: list[float] = []
    encode: list[float] = []
    select: list[float] = []
    categories: list[str] = []
    for name, cell in rows:
        ablation = cell["ablation"]
        categories.append(name)
        find_vals.append(int(ablation["extract"]) / n)
        encode.append(int(ablation["encode"]) / n)
        select.append(int(cell["select"]) / n)
    return GroupedColumns(
        categories=categories,
        series={
            "Find": find_vals,
            "Encode": encode,
            "Select": select,
        },
        n=n,
    )


def gemini_cells_1_3_5_barbell(
    development: Mapping[str, Any],
    holdout: Mapping[str, Any],
) -> BarbellPairs:
    """Return Gemini cells 1 / 3 / 5 select stops on development and holdout."""

    n_dev = int(development["n"])
    n_holdout = int(holdout["n"])
    dev_select = development["select"]
    holdout_select = holdout["select"]
    keys = ("rules", "hybrid", "llm")
    return BarbellPairs(
        categories=list(CELL_BARBELL_LABELS),
        development=[int(dev_select[key]) / n_dev for key in keys],
        holdout=[int(holdout_select[key]) / n_holdout for key in keys],
        n_development=n_dev,
        n_holdout=n_holdout,
    )


def _require_codebook_cell3(payload: Mapping[str, Any], slug: str) -> None:
    check = payload.get("format_only_check") or {}
    if normalize_repair_mode(str(check.get("repair_mode") or "")) != "gan_rules_encode":
        raise ValueError(f"{slug} encode is not gan_rules_encode")
    if check.get("select_repair_mode") != "llm_select_after_codebook":
        raise ValueError(f"{slug} select is not llm_select_after_codebook")


def six_model_cell3(rungs_by_slug: Mapping[str, Mapping[str, Any]]) -> GroupedColumns:
    """Return cell-3 codebook rungs, models ordered by select stop."""

    rows: list[tuple[int, str, int, int, int, int]] = []
    n = None
    for slug, payload in rungs_by_slug.items():
        _require_codebook_cell3(payload, slug)
        row_n = int(payload["row_count"])
        if n is None:
            n = row_n
        elif row_n != n:
            raise ValueError("rung row_count mismatch")
        rungs = payload["rungs"]
        extract = int(rungs["llm_extract"]["purist_correct"])
        encode = int(rungs["llm_encode"]["purist_correct"])
        select = int(rungs["llm_select"]["purist_correct"])
        rows.append((select, slug, extract, encode, select, row_n))
    if n is None:
        raise ValueError("no rung payloads")
    rows.sort(key=lambda item: (-item[0], item[1]))
    categories = [MODEL_LABELS[slug] for _, slug, _, _, _, _ in rows]
    return GroupedColumns(
        categories=categories,
        series={
            "Find": [extract / n for _, _, extract, _, _, n in rows],
            "Encode": [encode / n for _, _, _, encode, _, n in rows],
            "Select": [select / n for _, _, _, _, select, n in rows],
        },
        n=n,
    )


def load_living_gemini_cells() -> GroupedColumns:
    """Load the sealed Gemini five-cell grid for cells 1 / 3 / 5."""

    return gemini_cells_1_3_5(json.loads(FIVE_CELL_TEST450.read_text(encoding="utf-8")))


def load_living_gemini_dev_vs_test() -> BarbellPairs:
    """Load Gemini cells 1 / 3 / 5 select stops on both Gan splits."""

    test = json.loads(FIVE_CELL_TEST450.read_text(encoding="utf-8"))
    rungs = json.loads(GEMINI_DEV750_RUNGS.read_text(encoding="utf-8"))
    rules = json.loads(GAN_RULES_OWNER.read_text(encoding="utf-8"))
    _require_codebook_cell3(rungs, "gemini37flash")
    cell5 = json.loads(CELL5_DEV750.read_text(encoding="utf-8"))
    if cell5.get("method") != "gan_llm_select_from_extract":
        raise ValueError("cell 5 development is not gan_llm_select_from_extract")
    cells = test["cells"]
    return gemini_cells_1_3_5_barbell(
        development={
            "n": int(rules["dev750"]["row_count"]),
            "select": {
                "rules": int(rules["dev750"]["select_purist_correct"]),
                "hybrid": int(rungs["rungs"]["llm_select"]["purist_correct"]),
                "llm": int(cell5["summary"]["purist_correct"]),
            },
        },
        holdout={
            "n": int(test["n"]),
            "select": {
                "rules": int(cells["rules"]["select"]),
                "hybrid": int(cells["llm_extract_then_rules"]["select"]),
                "llm": int(cells["llm"]["select"]),
            },
        },
    )


def load_living_six_model_cell3() -> GroupedColumns:
    """Load sealed codebook rungs for the living roster."""

    payloads: dict[str, dict[str, Any]] = {}
    for model in living_models():
        slug = str(model["slug"])
        path = RUNGS_ROOT / slug / "test450" / "comparison.json"
        payloads[slug] = json.loads(path.read_text(encoding="utf-8"))
    return six_model_cell3(payloads)


def load_living_purist_confusion_matrix(
    slug: str = "gemini37flash",
    split: str = "test450",
) -> ConfusionMatrixData:
    """Load gold and predicted purist categories for the specified model and split."""

    from clinical_extraction.paper.gan_cell_replay import gan_living_extract_rows_path
    from clinical_extraction.paper.methods import gan_machine_split
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
        load_records_for_split,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
        StructuredRepairConfig,
        parse_structured_json_with_trace,
    )

    machine_split = gan_machine_split(split)
    records = {r.source_row_index: r for r in load_records_for_split(machine_split)}
    rows_path = gan_living_extract_rows_path(slug, split)
    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    config = StructuredRepairConfig.for_mode("llm_select_after_codebook")
    cat_to_idx = {cat: i for i, cat in enumerate(PURIST_CATEGORY_ORDER)}
    n_cats = len(PURIST_CATEGORY_ORDER)
    mat = [[0] * n_cats for _ in range(n_cats)]

    for row in rows:
        idx = row["source_row_index"]
        rec = records[idx]
        gold_cat = str(map_purist(rec.gold_monthly_frequency))
        extraction, _, _, _ = parse_structured_json_with_trace(
            row["raw_output"],
            note_text=rec.note_text,
            repair_config=config,
        )
        label = None if extraction is None else extraction.selection.final_label
        parsed = label_to_frequency_record(label) if label else None
        pred_cat = (
            str(map_purist(parsed.monthly_frequency))
            if parsed
            else "seizure_freq_unknown"
        )

        g_idx = cat_to_idx.get(gold_cat, cat_to_idx["seizure_freq_unknown"])
        p_idx = cat_to_idx.get(pred_cat, cat_to_idx["seizure_freq_unknown"])
        mat[g_idx][p_idx] += 1

    display_labels = [PURIST_DISPLAY_LABELS[c] for c in PURIST_CATEGORY_ORDER]
    return ConfusionMatrixData(
        categories=list(PURIST_CATEGORY_ORDER),
        labels=display_labels,
        matrix=mat,
        n=len(rows),
        title=f"Purist Categorisation Confusion Matrix ({MODEL_LABELS.get(slug, slug)}, {split})",
    )


def load_living_pragmatic_confusion_matrix(
    slug: str = "gemini37flash",
    split: str = "test450",
) -> ConfusionMatrixData:
    """Load gold and predicted pragmatic categories for the specified model and split."""

    from clinical_extraction.paper.gan_cell_replay import gan_living_extract_rows_path
    from clinical_extraction.paper.methods import gan_machine_split
    from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
        label_to_frequency_record,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
        load_records_for_split,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
        StructuredRepairConfig,
        parse_structured_json_with_trace,
    )

    machine_split = gan_machine_split(split)
    records = {r.source_row_index: r for r in load_records_for_split(machine_split)}
    rows_path = gan_living_extract_rows_path(slug, split)
    rows = [
        json.loads(line)
        for line in rows_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    config = StructuredRepairConfig.for_mode("llm_select_after_codebook")
    cat_to_idx = {cat: i for i, cat in enumerate(PRAGMATIC_CATEGORY_ORDER)}
    n_cats = len(PRAGMATIC_CATEGORY_ORDER)
    mat = [[0] * n_cats for _ in range(n_cats)]

    for row in rows:
        idx = row["source_row_index"]
        rec = records[idx]
        gold_cat = str(map_pragmatic(rec.gold_monthly_frequency))
        extraction, _, _, _ = parse_structured_json_with_trace(
            row["raw_output"],
            note_text=rec.note_text,
            repair_config=config,
        )
        label = None if extraction is None else extraction.selection.final_label
        parsed = label_to_frequency_record(label) if label else None
        pred_cat = (
            str(map_pragmatic(parsed.monthly_frequency))
            if parsed
            else "seizure_freq_unknown"
        )

        g_idx = cat_to_idx.get(gold_cat, cat_to_idx["seizure_freq_unknown"])
        p_idx = cat_to_idx.get(pred_cat, cat_to_idx["seizure_freq_unknown"])
        mat[g_idx][p_idx] += 1

    display_labels = [PRAGMATIC_DISPLAY_LABELS[c] for c in PRAGMATIC_CATEGORY_ORDER]
    return ConfusionMatrixData(
        categories=list(PRAGMATIC_CATEGORY_ORDER),
        labels=display_labels,
        matrix=mat,
        n=len(rows),
        title=(
            f"Pragmatic Categorisation Confusion Matrix "
            f"({MODEL_LABELS.get(slug, slug)}, {split})"
        ),
    )


def latin_modern_regular() -> Path:
    """Return the installed Latin Modern Roman 10 Regular face."""

    texlive = Path("/usr/local/texlive")
    discovered = sorted(
        texlive.glob("*/texmf-dist/fonts/opentype/public/lm/lmroman10-regular.otf")
    )
    for path in (*reversed(discovered), *LATIN_MODERN_CANDIDATES):
        if path.is_file():
            return path
    raise FileNotFoundError("Latin Modern Roman (lmroman10-regular.otf) is not installed")


def wrap_category_label(label: str, *, width: int) -> str:
    """Wrap a category tick onto two short lines without breaking tokens."""

    parts = textwrap.wrap(
        label,
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    )
    return "\n".join(parts) if parts else label


def _prepare_figure_fonts() -> None:
    from matplotlib import font_manager, rcParams

    font_manager.fontManager.addfont(str(latin_modern_regular()))
    rcParams["font.family"] = LATIN_MODERN_NAME
    rcParams["mathtext.fontset"] = "cm"
    rcParams["axes.formatter.use_mathtext"] = True
    rcParams["font.size"] = 10
    rcParams["axes.linewidth"] = 0.6
    rcParams["pdf.fonttype"] = 42


def render_grouped_columns(
    chart: GroupedColumns,
    path: Path,
    *,
    title: str = "",
    ylim: tuple[float, float] = (0.0, 1.0),
    yticks: tuple[float, ...] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
    stages: tuple[str, ...] = STAGE_ORDER,
) -> Path:
    """Write one grouped-column chart as PDF and PNG with refined styling."""

    import matplotlib.pyplot as plt

    _prepare_figure_fonts()
    n_groups = len(chart.categories)
    n_series = len(stages)
    width = 0.22 if n_series > 2 else 0.3
    xs = list(range(n_groups))
    wrap_width = 10 if n_groups >= 5 else 16
    fig_height = 3.5 if n_groups >= 5 else 3.2
    fig, axis = plt.subplots(figsize=(7.16, fig_height), dpi=300)

    axis.grid(axis="y", linestyle="--", linewidth=0.5, color=GRID_GREY, zorder=0)

    for index, stage in enumerate(stages):
        offset = (index - (n_series - 1) / 2) * (width + 0.02)
        values = chart.series[stage]
        axis.bar(
            [x + offset for x in xs],
            values,
            width=width,
            label=STAGE_LEGEND_LABELS[stage],
            color=STAGE_COLORS[stage],
            linewidth=0,
            zorder=3,
        )

    if "GPT-5.6 Luna" in chart.categories:
        luna_idx = chart.categories.index("GPT-5.6 Luna")
        half_span = ((n_series - 1) / 2) * (width + 0.02)
        x_rec = luna_idx - half_span
        y_rec = chart.series["Find"][luna_idx] + 0.025
        x_sel = luna_idx + half_span
        y_sel = chart.series["Select"][luna_idx] + 0.025
        rec_val = round(chart.series["Find"][luna_idx], 2)
        sel_val = round(chart.series["Select"][luna_idx], 2)
        delta = sel_val - rec_val

        axis.annotate(
            "",
            xy=(x_sel, y_sel),
            xytext=(x_rec, y_rec),
            arrowprops={
                "arrowstyle": "->,head_width=0.25,head_length=0.35",
                "color": "#1E293B",
                "lw": 1.1,
                "connectionstyle": "arc3,rad=-0.38",
            },
            zorder=5,
        )
        axis.text(
            luna_idx - 0.07,
            max(y_rec, y_sel) + 0.008,
            f"$\\Delta$ +{delta:.2f}",
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=LABEL_BLACK,
            zorder=5,
        )

    if title:
        axis.set_title(title, pad=12, fontsize=11, color=LABEL_BLACK)

    axis.set_xticks(xs)
    axis.set_xticklabels(
        [wrap_category_label(name, width=wrap_width) for name in chart.categories],
        fontsize=9.5,
        color=LABEL_BLACK,
        linespacing=1.05,
    )
    axis.set_xlabel("")
    axis.set_ylabel(chart.ylabel, fontsize=10, color=LABEL_BLACK)
    axis.set_ylim(*ylim)
    axis.set_yticks(list(yticks))

    for spine in axis.spines.values():
        spine.set_color(AXIS_GREY)
        spine.set_linewidth(0.6)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(
        color=AXIS_GREY,
        labelcolor=LABEL_BLACK,
        width=0.5,
        length=3,
        labelsize=9.5,
    )
    axis.legend(
        frameon=False,
        ncol=n_series,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.14),
        prop={"family": LATIN_MODERN_NAME, "size": 9.5},
        labelcolor=LABEL_BLACK,
        handlelength=1.2,
        handletextpad=0.4,
        columnspacing=1.5,
    )

    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.18)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


def render_barbell(
    chart: BarbellPairs,
    path: Path,
    *,
    title: str = "",
    xlim: tuple[float, float] = (0.65, 0.95),
    xticks: tuple[float, ...] = (0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95),
) -> Path:
    """Write one horizontal barbell chart as PDF and PNG with collision handling."""

    import matplotlib.pyplot as plt

    _prepare_figure_fonts()
    ys = list(range(len(chart.categories) - 1, -1, -1))
    fig, axis = plt.subplots(figsize=(7.16, 2.4), dpi=300)

    axis.grid(axis="x", linestyle="--", linewidth=0.5, color=GRID_GREY, zorder=0)

    for y, left, right in zip(ys, chart.development, chart.holdout, strict=True):
        delta = right - left
        if abs(delta) >= BARBELL_CONNECTOR_MIN_ABS_DELTA:
            axis.plot(
                [left, right],
                [y, y],
                color=AXIS_GREY,
                linewidth=2.2,
                solid_capstyle="round",
                zorder=2,
            )
            if abs(delta) >= BARBELL_DELTA_LABEL_MIN_ABS_DELTA:
                mid_x = (left + right) / 2
                sign = "+" if delta > 0 else "−"
                axis.text(
                    mid_x,
                    y + 0.26,
                    f"$\\Delta$ {sign}{abs(delta):.2f} generalisation gap",
                    ha="center",
                    va="bottom",
                    fontsize=8,
                    color="#475569",
                    zorder=5,
                )
                axis.annotate(
                    "",
                    xy=(mid_x, y + 0.06),
                    xytext=(mid_x, y + 0.24),
                    arrowprops={
                        "arrowstyle": "->,head_width=0.12,head_length=0.16",
                        "color": "#1E293B",
                        "lw": 0.7,
                        "connectionstyle": "arc3,rad=0.22",
                        "shrinkA": 0,
                        "shrinkB": 0,
                    },
                    zorder=5,
                )

    for y, left, right in zip(ys, chart.development, chart.holdout, strict=True):
        if abs(left - right) < BARBELL_CONNECTOR_MIN_ABS_DELTA:
            axis.scatter(
                [left],
                [y],
                s=100,
                color=SPLIT_COLORS["Development"],
                edgecolors=SPLIT_COLORS["Test"],
                linewidth=2.5,
                zorder=4,
            )
            axis.text(
                left,
                y + 0.20,
                f"{left:.2f} (Dev & Test)",
                ha="center",
                va="bottom",
                fontsize=8,
                color=LABEL_BLACK,
            )
        else:
            axis.scatter(
                [left],
                [y],
                s=64,
                color=SPLIT_COLORS["Development"],
                zorder=4,
            )
            axis.scatter(
                [right],
                [y],
                s=64,
                color=SPLIT_COLORS["Test"],
                zorder=4,
            )
            axis.text(
                left,
                y + 0.18,
                f"{left:.2f}",
                ha="center",
                va="bottom",
                fontsize=8,
                color=LABEL_BLACK,
            )
            axis.text(
                right,
                y - 0.20,
                f"{right:.2f}",
                ha="center",
                va="top",
                fontsize=8,
                color=LABEL_BLACK,
            )

    axis.scatter([], [], s=50, color=SPLIT_COLORS["Development"], label="Development")
    axis.scatter([], [], s=50, color=SPLIT_COLORS["Test"], label="Test")

    axis.set_yticks(ys)
    axis.set_yticklabels(
        [wrap_category_label(name, width=BARBELL_Y_LABEL_WRAP) for name in chart.categories],
        fontsize=9.5,
        color=LABEL_BLACK,
        linespacing=1.05,
    )
    axis.set_ylabel("")
    axis.set_xlabel(chart.ylabel, fontsize=10, color=LABEL_BLACK)
    axis.set_xlim(*xlim)
    axis.set_xticks(list(xticks))
    axis.set_ylim(-0.5, len(chart.categories) - 0.25)

    if title:
        axis.set_title(title, pad=10, fontsize=11, color=LABEL_BLACK)

    for spine in axis.spines.values():
        spine.set_color(AXIS_GREY)
        spine.set_linewidth(0.6)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(
        color=AXIS_GREY,
        labelcolor=LABEL_BLACK,
        width=0.5,
        length=3,
        labelsize=9.5,
    )
    axis.legend(
        frameon=False,
        loc="lower right",
        prop={"family": LATIN_MODERN_NAME, "size": 9},
        labelcolor=LABEL_BLACK,
        handlelength=1.0,
        handletextpad=0.4,
        borderaxespad=0.4,
        labelspacing=0.3,
    )

    fig.tight_layout(pad=0.5)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


def render_purist_confusion_matrix(
    data: ConfusionMatrixData,
    path: Path,
    *,
    title: str = "",
) -> Path:
    """Render a publication-ready confusion matrix for the Purist evaluation."""

    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import numpy as np

    _prepare_figure_fonts()

    mat = np.array(data.matrix, dtype=int)
    n_classes = len(data.labels)

    fig, axis = plt.subplots(figsize=(7.6, 5.4), dpi=300)

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "PuristHeatmap",
        ["#FFFFFF", "#E0F2F1", "#4DB6AC", "#12968F", "#15324F"],
        N=256,
    )

    row_sums = mat.sum(axis=1, keepdims=True)
    norm_mat = np.divide(mat, row_sums, out=np.zeros_like(mat, dtype=float), where=row_sums != 0)

    im = axis.imshow(norm_mat, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")

    axis.set_xticks(range(n_classes))
    axis.set_yticks(range(n_classes))
    axis.set_xticklabels(data.labels, rotation=45, ha="right", fontsize=8, color=LABEL_BLACK)
    axis.set_yticklabels(data.labels, fontsize=8, color=LABEL_BLACK)

    axis.set_xlabel(
        "Predicted",
        fontsize=10,
        labelpad=8,
        color=LABEL_BLACK,
    )
    axis.set_ylabel(
        "True",
        fontsize=10,
        labelpad=8,
        color=LABEL_BLACK,
    )

    if title:
        axis.set_title(title, pad=12, fontsize=11, color=LABEL_BLACK)

    threshold = 0.55
    for i in range(n_classes):
        for j in range(n_classes):
            val = mat[i, j]
            prop = norm_mat[i, j]
            if val > 0:
                text_color = "white" if prop > threshold else LABEL_BLACK
                if val >= 10:
                    label = f"{val}\n({prop:.0%})"
                else:
                    label = f"{val}"
                axis.text(
                    j,
                    i,
                    label,
                    ha="center",
                    va="center",
                    fontsize=7.2,
                    color=text_color,
                    linespacing=1.35,
                )

    for spine in axis.spines.values():
        spine.set_color(AXIS_GREY)
        spine.set_linewidth(0.6)

    axis.tick_params(color=AXIS_GREY, width=0.5, length=2.5)

    cbar = fig.colorbar(im, ax=axis, fraction=0.046, pad=0.04)
    cbar.outline.set_linewidth(0.6)
    cbar.outline.set_color(AXIS_GREY)
    cbar.ax.tick_params(labelsize=8, color=AXIS_GREY, labelcolor=LABEL_BLACK)
    cbar.set_label("Row Recall", fontsize=9, color=LABEL_BLACK)

    fig.tight_layout(pad=0.6)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


def render_pragmatic_confusion_matrix(
    data: ConfusionMatrixData,
    path: Path,
    *,
    title: str = "",
) -> Path:
    """Render a publication-ready confusion matrix for the Pragmatic evaluation."""

    import matplotlib.colors as mcolors
    import matplotlib.pyplot as plt
    import numpy as np

    _prepare_figure_fonts()

    mat = np.array(data.matrix, dtype=int)
    n_classes = len(data.labels)

    fig, axis = plt.subplots(figsize=(5.4, 4.3), dpi=300)

    cmap = mcolors.LinearSegmentedColormap.from_list(
        "PragmaticHeatmap",
        ["#FFFFFF", "#E0F2F1", "#4DB6AC", "#12968F", "#15324F"],
        N=256,
    )

    row_sums = mat.sum(axis=1, keepdims=True)
    norm_mat = np.divide(mat, row_sums, out=np.zeros_like(mat, dtype=float), where=row_sums != 0)

    im = axis.imshow(norm_mat, cmap=cmap, vmin=0.0, vmax=1.0, aspect="auto")

    axis.set_xticks(range(n_classes))
    axis.set_yticks(range(n_classes))
    axis.set_xticklabels(data.labels, rotation=25, ha="right", fontsize=9, color=LABEL_BLACK)
    axis.set_yticklabels(data.labels, fontsize=9, color=LABEL_BLACK)

    axis.set_xlabel(
        "Predicted",
        fontsize=9.5,
        labelpad=8,
        color=LABEL_BLACK,
    )
    axis.set_ylabel(
        "True",
        fontsize=9.5,
        labelpad=8,
        color=LABEL_BLACK,
    )

    if title:
        axis.set_title(title, pad=12, fontsize=11, color=LABEL_BLACK)

    threshold = 0.55
    for i in range(n_classes):
        for j in range(n_classes):
            val = mat[i, j]
            prop = norm_mat[i, j]
            if val > 0:
                text_color = "white" if prop > threshold else LABEL_BLACK
                if val >= 5:
                    label = f"{val}\n({prop:.0%})"
                else:
                    label = f"{val}"
                axis.text(
                    j,
                    i,
                    label,
                    ha="center",
                    va="center",
                    fontsize=8.5,
                    color=text_color,
                    linespacing=1.35,
                )

    for spine in axis.spines.values():
        spine.set_color(AXIS_GREY)
        spine.set_linewidth(0.6)

    axis.tick_params(color=AXIS_GREY, width=0.5, length=2.5)

    cbar = fig.colorbar(im, ax=axis, fraction=0.046, pad=0.04)
    cbar.outline.set_linewidth(0.6)
    cbar.outline.set_color(AXIS_GREY)
    cbar.ax.tick_params(labelsize=8, color=AXIS_GREY, labelcolor=LABEL_BLACK)
    cbar.set_label("Row Recall", fontsize=9, color=LABEL_BLACK)

    fig.tight_layout(pad=0.6)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


def load_living_aa_healthcare_vs_purist() -> ScatterPlotData:
    """Load living six models' AA Healthcare Index and test450 Purist micro-F1."""

    points: list[tuple[str, float, float]] = []
    for model in living_models():
        slug = str(model["slug"])
        label = MODEL_LABELS.get(slug, str(model.get("label", slug)))
        aa_score = AA_HEALTHCARE_INDEX.get(slug)
        if aa_score is None:
            raise KeyError(f"Missing AA Healthcare Index score for model: {slug}")
        path = RUNGS_ROOT / slug / "test450" / "comparison.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        _require_codebook_cell3(payload, slug)
        n = int(payload["row_count"])
        select_correct = int(payload["rungs"]["llm_select"]["purist_correct"])
        purist_f1 = select_correct / n
        points.append((label, aa_score, purist_f1))
    return ScatterPlotData(
        points=points,
        xlabel="Artificial Analysis Healthcare & Medical Index",
        ylabel="Purist micro-F1",
        title="",
    )


def render_healthcare_vs_purist_scatter(
    data: ScatterPlotData,
    path: Path,
    *,
    title: str = "",
    xlim: tuple[float, float] = (10.0, 56.0),
    ylim: tuple[float, float] = (0.68, 0.88),
) -> Path:
    """Render a publication-ready scatter plot of Purist F1 vs AA Healthcare Index."""

    import matplotlib.pyplot as plt
    import numpy as np

    _prepare_figure_fonts()
    fig, axis = plt.subplots(figsize=(5.4, 4.0), dpi=300)

    axis.grid(True, linestyle="--", linewidth=0.5, color=GRID_GREY, zorder=0)

    xs = [p[1] for p in data.points]
    ys = [p[2] for p in data.points]

    x_arr = np.array(xs)
    y_arr = np.array(ys)
    m, b = np.polyfit(x_arr, y_arr, 1)
    x_line = np.linspace(xlim[0] + 2, xlim[1] - 2, 100)
    corr = np.corrcoef(x_arr, y_arr)[0, 1]
    axis.plot(
        x_line,
        m * x_line + b,
        linestyle="--",
        color="#8C9BAE",
        linewidth=0.8,
        zorder=2,
        label=f"Linear trend ($r = {corr:.2f}$)",
    )

    axis.scatter(
        xs,
        ys,
        s=55,
        color="#15324F",
        linewidth=0,
        zorder=4,
    )

    offsets: dict[str, tuple[float, float, str, str]] = {
        "Grok 4.6": (0.8, -0.006, "left", "top"),
        "Gemini 3.7 Flash": (-0.8, 0.006, "right", "bottom"),
        "DeepSeek V4 Flash": (0.8, 0.006, "left", "bottom"),
        "GPT-5.6 Luna": (-0.8, 0.006, "right", "bottom"),
        "Qwen 3.8 27B": (0.8, -0.006, "left", "top"),
        "Gemma 4 26B": (0.8, -0.006, "left", "top"),
    }

    for label, x, y in data.points:
        dx, dy, ha, va = offsets.get(label, (0.8, 0.006, "left", "bottom"))
        axis.annotate(
            label,
            xy=(x, y),
            xytext=(x + dx, y + dy),
            fontsize=8.5,
            color=LABEL_BLACK,
            ha=ha,
            va=va,
            zorder=5,
        )

    if title:
        axis.set_title(title, pad=12, fontsize=11, color=LABEL_BLACK)

    from matplotlib.ticker import FormatStrFormatter

    axis.set_xlabel(data.xlabel, fontsize=10, color=LABEL_BLACK, labelpad=6)
    axis.set_ylabel(data.ylabel, fontsize=10, color=LABEL_BLACK, labelpad=6)
    axis.set_xlim(*xlim)
    axis.set_ylim(*ylim)
    axis.set_yticks([0.70, 0.75, 0.80, 0.85])
    axis.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))

    for spine in axis.spines.values():
        spine.set_color(AXIS_GREY)
        spine.set_linewidth(0.6)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.tick_params(
        color=AXIS_GREY,
        labelcolor=LABEL_BLACK,
        width=0.5,
        length=3,
        labelsize=9.5,
    )

    axis.legend(
        frameon=False,
        loc="upper left",
        prop={"family": LATIN_MODERN_NAME, "size": 9},
        labelcolor=LABEL_BLACK,
    )

    fig.tight_layout(pad=0.6)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.04)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.04, dpi=300)
    plt.close(fig)
    return pdf


def render_living_figures(out_dir: Path | None = None) -> dict[str, str]:
    """Render the living Gan results figures next to the draft."""

    dest = out_dir or FIGURE_DIR
    models = render_grouped_columns(
        load_living_six_model_cell3(),
        dest / "six_model_stage_performance",
        stages=PAPER_STAGES,
    )
    barbell = render_barbell(
        load_living_gemini_dev_vs_test(),
        dest / "development_vs_test_generalization",
    )
    matrix = render_purist_confusion_matrix(
        load_living_purist_confusion_matrix("gemini37flash", "test450"),
        dest / "confusion_matrix_purist",
    )
    render_purist_confusion_matrix(
        load_living_purist_confusion_matrix("gemini37flash", "test450"),
        dest / "confusion_matrix",
    )
    pragmatic = render_pragmatic_confusion_matrix(
        load_living_pragmatic_confusion_matrix("gemini37flash", "test450"),
        dest / "confusion_matrix_pragmatic",
    )
    scatter = render_healthcare_vs_purist_scatter(
        load_living_aa_healthcare_vs_purist(),
        dest / "healthcare_index_vs_purist_f1",
    )
    return {
        "six_model": models.as_posix(),
        "dev_vs_test": barbell.as_posix(),
        "confusion_matrix_purist": matrix.as_posix(),
        "confusion_matrix": matrix.as_posix(),
        "confusion_matrix_pragmatic": pragmatic.as_posix(),
        "aa_healthcare_vs_purist": scatter.as_posix(),
    }

