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
GEMINI_DEV750_RUNGS = ROOT / "paper_experiments/gan/rungs/gemini37flash/dev750/comparison.json"
CELL5_DEV750 = (
    ROOT
    / "experiments/paper/gan_llm_select_from_extract/gemini37flash"
    / "gan_llm_extract/dev750/comparison.json"
)
RUNGS_ROOT = ROOT / "paper_experiments/gan/rungs"
CELL_BARBELL_LABELS = ("Rules only", "LLM + rules", "LLM only")
SPLIT_COLORS = {
    "Development": "#9AA3AB",
    "Test": "#15324F",
}
FIGURE_DIR = ROOT / "paper/draft"
STAGE_ORDER = ("Recognise", "Encode", "Select")
STAGE_COLORS = {
    "Recognise": "#C5CDD4",
    "Encode": "#12968F",
    "Select": "#15324F",
}
AXIS_GREY = "#D2D5DA"
LABEL_BLACK = "#000000"
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


def gemini_cells_1_3_5(payload: Mapping[str, Any]) -> GroupedColumns:
    """Return Gemini cells 1 / 3 / 5 at recognise, encode, and select."""

    n = int(payload["n"])
    cells = payload["cells"]
    rows = (
        ("Rules", cells["rules"]),
        ("Both", cells["llm_extract_then_rules"]),
        ("LLM", cells["llm"]),
    )
    recognise: list[float] = []
    encode: list[float] = []
    select: list[float] = []
    categories: list[str] = []
    for name, cell in rows:
        ablation = cell["ablation"]
        categories.append(name)
        recognise.append(int(ablation["extract"]) / n)
        encode.append(int(ablation["encode"]) / n)
        select.append(int(cell["select"]) / n)
    return GroupedColumns(
        categories=categories,
        series={
            "Recognise": recognise,
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
            "Recognise": [extract / n for _, _, extract, _, _, n in rows],
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
    _require_codebook_cell3(rungs, "gemini37flash")
    cell5 = json.loads(CELL5_DEV750.read_text(encoding="utf-8"))
    if cell5.get("method") != "gan_llm_select_from_extract":
        raise ValueError("cell 5 development is not gan_llm_select_from_extract")
    cells = test["cells"]
    return gemini_cells_1_3_5_barbell(
        development={
            "n": int(rungs["row_count"]),
            "select": {
                "rules": int(rungs["rungs"]["rules_only"]["purist_correct"]),
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


def _style_axis(
    axis: Any,
    *,
    title: str,
    xlim: tuple[float, float] = (0.65, 0.95),
    xticks: tuple[float, ...] = (0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95),
) -> None:
    axis.set_title(title, pad=10, fontsize=12, color=LABEL_BLACK)
    axis.set_xlabel("")
    axis.set_xlim(*xlim)
    axis.set_xticks(list(xticks))
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
        labelsize=10,
    )
    axis.xaxis.label.set_color(LABEL_BLACK)
    axis.yaxis.label.set_color(LABEL_BLACK)


def render_grouped_columns(
    chart: GroupedColumns,
    path: Path,
    *,
    title: str,
) -> Path:
    """Write one grouped-column chart as PDF and PNG."""

    import matplotlib.pyplot as plt

    _prepare_figure_fonts()
    n_groups = len(chart.categories)
    n_series = len(STAGE_ORDER)
    width = 0.2
    xs = list(range(n_groups))
    wrap_width = 10 if n_groups >= 5 else 16
    fig_height = 3.9 if n_groups >= 5 else 3.4
    fig, axis = plt.subplots(figsize=(7.16, fig_height), dpi=200)
    for index, stage in enumerate(STAGE_ORDER):
        offset = (index - (n_series - 1) / 2) * (width + 0.02)
        values = chart.series[stage]
        bars = axis.bar(
            [x + offset for x in xs],
            values,
            width=width,
            label=stage,
            color=STAGE_COLORS[stage],
            linewidth=0,
        )
        axis.bar_label(
            bars,
            labels=[f"{value:.2f}" for value in values],
            padding=2,
            fontsize=8,
            color=LABEL_BLACK,
        )
    axis.set_title(title, pad=10, fontsize=12, color=LABEL_BLACK)
    axis.set_xticks(xs)
    axis.set_xticklabels([])
    axis.set_xlabel("")
    for x, name in zip(xs, chart.categories, strict=True):
        axis.text(
            x,
            -0.03,
            wrap_category_label(name, width=wrap_width),
            transform=axis.get_xaxis_transform(),
            ha="center",
            va="top",
            fontsize=10,
            color=LABEL_BLACK,
            linespacing=1.1,
            clip_on=False,
        )
    axis.set_ylabel(chart.ylabel)
    axis.set_ylim(0.0, 1.0)
    axis.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
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
        labelsize=10,
    )
    axis.tick_params(axis="x", pad=3.5)
    axis.yaxis.label.set_color(LABEL_BLACK)
    axis.yaxis.label.set_fontsize(10)
    axis.legend(
        frameon=False,
        ncol=3,
        loc="upper right",
        prop={"family": LATIN_MODERN_NAME, "size": 10},
        labelcolor=LABEL_BLACK,
    )
    if n_groups >= 5:
        fig.subplots_adjust(left=0.10, right=0.99, top=0.84, bottom=0.14)
    else:
        fig.tight_layout(pad=0.8)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.06)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.06, dpi=300)
    plt.close(fig)
    return pdf


def render_barbell(
    chart: BarbellPairs,
    path: Path,
    *,
    title: str,
) -> Path:
    """Write one horizontal barbell chart as PDF and PNG."""

    import matplotlib.pyplot as plt

    _prepare_figure_fonts()
    ys = list(range(len(chart.categories) - 1, -1, -1))
    fig, axis = plt.subplots(figsize=(7.16, 3.15), dpi=200)
    for y, left, right in zip(ys, chart.development, chart.holdout, strict=True):
        axis.plot(
            [left, right],
            [y, y],
            color=AXIS_GREY,
            linewidth=1.6,
            solid_capstyle="round",
            zorder=1,
        )
    axis.scatter(
        chart.development,
        ys,
        s=56,
        color=SPLIT_COLORS["Development"],
        zorder=2,
        label="Development",
    )
    axis.scatter(
        chart.holdout,
        ys,
        s=56,
        color=SPLIT_COLORS["Test"],
        zorder=2,
        label="Test",
    )
    for y, left, right in zip(ys, chart.development, chart.holdout, strict=True):
        axis.text(
            left,
            y + 0.16,
            f"{left:.2f}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=LABEL_BLACK,
        )
        axis.text(
            right,
            y - 0.16,
            f"{right:.2f}",
            ha="center",
            va="top",
            fontsize=8,
            color=LABEL_BLACK,
        )
    axis.set_yticks(ys)
    axis.set_yticklabels(chart.categories)
    axis.set_ylabel("")
    _style_axis(axis, title=title)
    axis.set_xlabel(chart.ylabel)
    axis.xaxis.label.set_fontsize(10)
    axis.set_ylim(-0.55, len(chart.categories) - 0.45)
    axis.legend(
        frameon=False,
        loc="lower right",
        prop={"family": LATIN_MODERN_NAME, "size": 10},
        labelcolor=LABEL_BLACK,
        handlelength=0.8,
        handletextpad=0.35,
        borderaxespad=0.2,
        labelspacing=0.35,
    )
    fig.tight_layout(pad=0.6)
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = path.with_suffix(".pdf")
    png = path.with_suffix(".png")
    fig.savefig(pdf, bbox_inches="tight", pad_inches=0.06)
    fig.savefig(png, bbox_inches="tight", pad_inches=0.06, dpi=300)
    plt.close(fig)
    return pdf


def render_living_figures(out_dir: Path | None = None) -> dict[str, str]:
    """Render the living Gan results figures next to the draft."""

    dest = out_dir or FIGURE_DIR
    models = render_grouped_columns(
        load_living_six_model_cell3(),
        dest / "fig3",
        title=(
            "Every model benefits from the encode and select stage,\n"
            "but it helps weaker models the most"
        ),
    )
    barbell = render_barbell(
        load_living_gemini_dev_vs_test(),
        dest / "fig4",
        title=(
            "Rules perform best on development,\n"
            "but generalise very poorly to test"
        ),
    )
    return {
        "six_model": models.as_posix(),
        "dev_vs_test": barbell.as_posix(),
    }
