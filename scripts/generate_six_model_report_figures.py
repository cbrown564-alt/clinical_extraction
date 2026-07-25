"""Generate the two main empirical figures for the six-model comparison report.

The values are copied from the retained reports cited in
docs/research/six_model_comparison_report_2026-07-18.md. This script does not
read locked row-level data or call a model.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "docs"
    / "research"
    / "assets"
    / "six_model_comparison_2026-07-18"
)

MODELS = [
    "GPT-4.1-mini",
    "GPT-5.6 Luna",
    "GPT-5.6 Sol",
    "DeepSeek V4 Flash",
    "Qwen 3.6:35B",
    "Gemma 4 26B",
]

INK = "#18212B"
MUTED = "#5D6B78"
GRID = "#DCE3E8"
BLUE = "#2878B5"
TEAL = "#2A9D8F"
ORANGE = "#E07A3F"
LIGHT_BLUE = "#DCECF7"


def _save(fig: plt.Figure, stem: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_DIR / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUTPUT_DIR / f"{stem}.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def error_location() -> None:
    """Pair Gan first-failure ownership with ExECT family F1."""

    failure_labels = [
        "Clinical selection",
        "Evidence selection",
        "Format or schema",
        "Deterministic processing",
        "Model transport",
    ]
    failure_counts = [1449, 616, 84, 40, 12]

    family_labels = [
        "Diagnosis",
        "Seizure\nFrequency",
        "Prescription",
        "Investigations",
    ]
    family_scores = np.array(
        [
            [0.85, 0.69, 0.87, 0.85],
            [0.89, 0.79, 0.93, 0.92],
            [0.89, 0.80, 0.94, 0.94],
            [0.88, 0.76, 0.93, 0.94],
            [0.87, 0.71, 0.92, 0.91],
            [0.84, 0.62, 0.90, 0.80],
        ]
    )

    fig, (left, right) = plt.subplots(
        1,
        2,
        figsize=(13.5, 5.8),
        gridspec_kw={"width_ratios": [0.9, 1.25], "wspace": 0.42},
    )
    fig.patch.set_facecolor("white")

    positions = np.arange(len(failure_labels))
    colors = [ORANGE, ORANGE, LIGHT_BLUE, LIGHT_BLUE, LIGHT_BLUE]
    left.barh(positions, failure_counts, color=colors, height=0.62)
    left.set_yticks(positions, failure_labels)
    left.invert_yaxis()
    left.set_xlabel("Rows assigned to first failure owner", color=MUTED)
    left.set_title(
        "Gan dev750: clinical and evidence selection\ndominate recorded first failures",
        loc="left",
        color=INK,
        fontweight="bold",
    )
    left.xaxis.grid(True, color=GRID, linewidth=0.8)
    left.set_axisbelow(True)
    for index, value in enumerate(failure_counts):
        left.text(value + 24, index, f"{value:,}", va="center", color=INK, fontsize=9)
    left.spines[["top", "right", "left"]].set_visible(False)
    left.tick_params(axis="y", length=0, colors=INK)
    left.tick_params(axis="x", colors=MUTED)

    image = right.imshow(family_scores, cmap="YlGnBu", vmin=0.60, vmax=0.95, aspect="auto")
    right.set_xticks(np.arange(len(family_labels)), family_labels)
    right.set_yticks(np.arange(len(MODELS)), MODELS)
    right.set_title(
        "ExECT dev140: Seizure Frequency is\nthe weakest family for every model",
        loc="left",
        color=INK,
        fontweight="bold",
    )
    for row in range(family_scores.shape[0]):
        for column in range(family_scores.shape[1]):
            value = family_scores[row, column]
            text_color = "white" if value >= 0.85 else INK
            right.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                color=text_color,
                fontsize=9,
                fontweight="bold",
            )
    right.tick_params(axis="both", length=0, colors=INK)
    right.spines[:].set_visible(False)
    colorbar = fig.colorbar(image, ax=right, fraction=0.035, pad=0.03)
    colorbar.set_label("F1", color=MUTED)
    colorbar.ax.tick_params(colors=MUTED)

    fig.suptitle(
        "The remaining errors are mainly clinical, not structural",
        x=0.02,
        y=1.02,
        ha="left",
        color=INK,
        fontsize=16,
        fontweight="bold",
    )
    _save(fig, "clinical_error_location")


def component_transitions() -> None:
    """Show pipeline-stage and method transitions without pooling tasks."""

    exect_rescues = np.array([13, 4, 3, 9, 13, 12])
    exect_regressions = np.array([0, 0, 1, 0, 0, 0])
    gan_rescues = np.array([110, 120, 96, 115, 125, 168])
    gan_regressions = np.array([34, 32, 31, 31, 23, 34])

    fig, (left, right) = plt.subplots(
        1,
        2,
        figsize=(13.5, 6.2),
        gridspec_kw={"wspace": 0.38},
    )
    fig.patch.set_facecolor("white")
    positions = np.arange(len(MODELS))
    height = 0.34

    for axis, rescues, regressions, title, xlabel in [
        (
            left,
            exect_rescues,
            exect_regressions,
            "ExECT dev140 Seizure Frequency states",
            "State transitions per model run",
        ),
        (
            right,
            gan_rescues,
            gan_regressions,
            "Gan dev750 matched method changes",
            "Final-answer transitions per model",
        ),
    ]:
        axis.barh(
            positions - height / 2,
            rescues,
            height=height,
            color=TEAL,
            label="Wrong → correct",
        )
        axis.barh(
            positions + height / 2,
            regressions,
            height=height,
            color=ORANGE,
            label="Correct → wrong",
        )
        axis.set_yticks(positions, MODELS)
        axis.invert_yaxis()
        axis.set_xlabel(xlabel, color=MUTED)
        axis.set_title(title, loc="left", color=INK, fontweight="bold")
        axis.xaxis.grid(True, color=GRID, linewidth=0.8)
        axis.set_axisbelow(True)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.tick_params(axis="y", length=0, colors=INK)
        axis.tick_params(axis="x", colors=MUTED)

    handles, labels = left.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.95),
        ncol=2,
        frameon=False,
    )
    fig.suptitle(
        "Pipeline changes rescue errors and can introduce new ones",
        x=0.02,
        y=1.02,
        ha="left",
        color=INK,
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.02,
        0.01,
        "Panels use different tasks, units, and denominators; counts must not be pooled. "
        "ExECT repeats the same 140 letters across six model runs.",
        color=MUTED,
        fontsize=9,
    )
    _save(fig, "component_transitions")


if __name__ == "__main__":
    error_location()
    component_transitions()
