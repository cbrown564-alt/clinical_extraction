"""Render six-model comparison report charts from the clean final panel."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FormatStrFormatter

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "experiments/six_model_final_panel_20260803/panel_aggregate.json"
OUTPUT = ROOT / "docs/research/assets/six_model_comparison_2026-07-18"

MODELS = [
    ("openai/gpt-4.1-mini", "GPT-4.1-mini"),
    ("openai/gpt-5.6-luna", "GPT-5.6 Luna"),
    ("openai/gpt-5.6-sol", "GPT-5.6 Sol"),
    ("deepseek/deepseek-v4-flash", "DeepSeek V4 Flash"),
    ("ollama_chat/qwen3.6:35b", "Qwen 3.6:35B"),
    ("ollama_chat/gemma4:26b", "Gemma 4 26B"),
]

TEAL = "#167C80"
TEAL_LIGHT = "#B7DDD8"
ORANGE = "#D97706"
NEUTRAL = "#D9DEE3"
INK = "#25313C"
MUTED = "#66727D"
GRID = "#DDE3E8"
BG = "#FBFCFD"


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelcolor": MUTED,
            "axes.edgecolor": GRID,
            "xtick.color": MUTED,
            "ytick.color": INK,
            "figure.facecolor": BG,
            "axes.facecolor": BG,
            "savefig.facecolor": BG,
        }
    )


def _header(ax: plt.Axes, title: str, subtitle: str) -> None:
    ax.set_title(title, loc="left", color=INK, pad=30)
    ax.text(0, 1.03, subtitle, transform=ax.transAxes, color=MUTED, fontsize=9, va="bottom")


def _finish(ax: plt.Axes, xlabel: str) -> None:
    ax.set_xlabel(xlabel, labelpad=10)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))


def _grouped_bar(
    filename: str,
    title: str,
    subtitle: str,
    first_label: str,
    second_label: str,
    first: dict[str, float],
    second: dict[str, float],
    *,
    sort_on: dict[str, float],
    xlabel: str,
    colors: tuple[str, str],
) -> None:
    ordered = sorted(MODELS, key=lambda item: sort_on[item[0]], reverse=True)
    keys = [key for key, _ in ordered]
    labels = [label for _, label in ordered]
    y = np.arange(len(labels))
    height = 0.32
    fig, ax = plt.subplots(figsize=(10.8, 6.5))
    fig.subplots_adjust(left=0.22, right=0.97, top=0.84, bottom=0.20)
    ax.barh(
        y - height / 2,
        [first[k] for k in keys],
        height,
        label=first_label,
        color=colors[0],
        edgecolor="none",
    )
    ax.barh(
        y + height / 2,
        [second[k] for k in keys],
        height,
        label=second_label,
        color=colors[1],
        edgecolor="none",
    )
    for offset, values in ((-height / 2, first), (height / 2, second)):
        for row, key in enumerate(keys):
            ax.text(
                values[key] + 0.008,
                row + offset,
                f"{values[key]:.2f}",
                va="center",
                color=INK,
                fontsize=9,
            )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 1.02)
    ax.legend(
        frameon=False,
        ncols=2,
        loc="upper right",
        bbox_to_anchor=(1, -0.10),
        borderaxespad=0,
    )
    _header(ax, title, subtitle)
    _finish(ax, xlabel)
    fig.savefig(OUTPUT / filename, format="svg")
    fig.savefig(OUTPUT / filename.replace(".svg", ".png"), dpi=160)
    plt.close(fig)


def _barbell(
    filename: str,
    title: str,
    subtitle: str,
    first_label: str,
    second_label: str,
    first: dict[str, float],
    second: dict[str, float],
    *,
    sort_on: dict[str, float],
    xlabel: str,
    colors: tuple[str, str],
) -> None:
    ordered = sorted(MODELS, key=lambda item: sort_on[item[0]], reverse=True)
    keys = [key for key, _ in ordered]
    labels = [label for _, label in ordered]
    y = np.arange(len(labels))
    values = [value for key in keys for value in (first[key], second[key])]
    padding = 0.035
    xmin = max(0.0, min(values) - padding)
    xmax = min(1.0, max(values) + padding)

    fig, ax = plt.subplots(figsize=(10.8, 6.5))
    fig.subplots_adjust(left=0.22, right=0.95, top=0.84, bottom=0.20)
    for row, key in enumerate(keys):
        ax.plot(
            [first[key], second[key]],
            [row, row],
            color=GRID,
            linewidth=3,
            solid_capstyle="round",
            zorder=1,
        )
    ax.scatter(
        [first[key] for key in keys],
        y,
        s=90,
        facecolor=BG,
        edgecolor=colors[0],
        linewidth=2.2,
        label=first_label,
        zorder=3,
    )
    ax.scatter(
        [second[key] for key in keys],
        y,
        s=90,
        facecolor=colors[1],
        edgecolor=colors[1],
        linewidth=1.5,
        label=second_label,
        zorder=3,
    )
    label_offset = (xmax - xmin) * 0.012
    for row, key in enumerate(keys):
        first_is_right = first[key] >= second[key]
        ax.text(
            first[key] + (label_offset if first_is_right else -label_offset),
            row,
            f"{first[key]:.2f}",
            ha="left" if first_is_right else "right",
            va="center",
            color=INK,
            fontsize=9,
        )
        ax.text(
            second[key] + (-label_offset if first_is_right else label_offset),
            row,
            f"{second[key]:.2f}",
            ha="right" if first_is_right else "left",
            va="center",
            color=INK,
            fontsize=9,
        )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(xmin, xmax)
    ax.legend(
        frameon=False,
        ncols=2,
        loc="upper right",
        bbox_to_anchor=(1, -0.10),
        borderaxespad=0,
    )
    _header(ax, title, subtitle)
    _finish(ax, xlabel)
    fig.savefig(OUTPUT / filename, format="svg")
    fig.savefig(OUTPUT / filename.replace(".svg", ".png"), dpi=160)
    plt.close(fig)


def _heatmap(
    filename: str,
    title: str,
    subtitle: str,
    columns: list[str],
    values: dict[str, dict[str, float]],
) -> None:
    ordered = sorted(
        MODELS, key=lambda item: np.mean([values[item[0]][c] for c in columns]), reverse=True
    )
    matrix = np.array([[values[key][column] for column in columns] for key, _ in ordered])
    labels = [label for _, label in ordered]
    cmap = LinearSegmentedColormap.from_list(
        "research_red_blue",
        ["#A94442", "#F5F2ED", "#2563A6"],
    )
    fig, ax = plt.subplots(figsize=(10.8, 6.2), constrained_layout=True)
    image = ax.imshow(matrix, cmap=cmap, vmin=0.45, vmax=0.95, aspect="auto")
    ax.set_xticks(np.arange(len(columns)), columns)
    ax.set_yticks(np.arange(len(labels)), labels)
    ax.tick_params(length=0)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix[row, column]
            ax.text(
                column,
                row,
                f"{value:.2f}",
                ha="center",
                va="center",
                color="white" if value <= 0.58 or value >= 0.87 else INK,
                fontsize=9,
            )
    colorbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.025)
    colorbar.set_label("Score", color=MUTED)
    colorbar.ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    colorbar.outline.set_visible(False)
    _header(ax, title, subtitle)
    ax.spines[:].set_visible(False)
    fig.savefig(OUTPUT / filename, format="svg")
    fig.savefig(OUTPUT / filename.replace(".svg", ".png"), dpi=160)
    plt.close(fig)


def main() -> None:
    _style()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    panel = _read(PANEL)
    by_model = {row["model"]: row for row in panel["conditions"]}

    exect_dev = {
        model: float(by_model[model]["exectv2"]["dev140"]["llm_with_rules_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_test = {
        model: float(by_model[model]["exectv2"]["test60"]["llm_with_rules_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_llm = {
        model: float(by_model[model]["exectv2"]["test60"]["llm_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_family = {
        model: {
            family: float(score)
            for family, score in by_model[model]["exectv2"]["test60"][
                "llm_with_rules_by_family"
            ].items()
        }
        for model, _ in MODELS
    }
    gan_dev = {
        model: float(by_model[model]["gan2026"]["dev750"]["llm_with_rules_purist_accuracy"])
        for model, _ in MODELS
    }
    gan_test = {
        model: float(by_model[model]["gan2026"]["test450"]["llm_with_rules_purist_accuracy"])
        for model, _ in MODELS
    }
    gan_llm = {
        model: float(by_model[model]["gan2026"]["test450"]["llm_purist_accuracy"])
        for model, _ in MODELS
    }

    shared_split_subtitle = (
        "Final LLM-with-rules results; primary readout is aggregate-only locked holdout"
    )
    shared_method_subtitle = "Final results on aggregate-only locked holdout"

    _barbell(
        "exect_dev_test.svg",
        "ExECT clinical fact F1: locked holdout versus development",
        shared_split_subtitle,
        "dev140",
        "test60",
        exect_dev,
        exect_test,
        sort_on=exect_test,
        xlabel="Clinical fact F1 (0–1)",
        colors=(TEAL_LIGHT, TEAL),
    )
    _grouped_bar(
        "exect_llm_rules.svg",
        "ExECT clinical fact F1: LLM only and LLM with rules",
        shared_method_subtitle,
        "LLM only",
        "LLM with rules",
        exect_llm,
        exect_test,
        sort_on=exect_test,
        xlabel="Clinical fact F1 (0–1)",
        colors=(NEUTRAL, ORANGE),
    )
    _heatmap(
        "exect_family_heatmap.svg",
        "ExECT locked-holdout F1 by letter part",
        "Final LLM-with-rules clinical fact F1 on aggregate-only test60",
        ["Diagnosis", "SeizureFrequency", "Prescription", "Investigations"],
        exect_family,
    )
    _barbell(
        "gan_dev_test.svg",
        "Gan Purist accuracy: locked holdout versus development",
        shared_split_subtitle,
        "dev750",
        "test450",
        gan_dev,
        gan_test,
        sort_on=gan_test,
        xlabel="Purist accuracy (0–1)",
        colors=(TEAL_LIGHT, TEAL),
    )
    _grouped_bar(
        "gan_llm_rules.svg",
        "Gan Purist accuracy: LLM only and LLM with rules",
        shared_method_subtitle,
        "LLM only",
        "LLM with rules",
        gan_llm,
        gan_test,
        sort_on=gan_test,
        xlabel="Purist accuracy (0–1)",
        colors=(NEUTRAL, ORANGE),
    )


if __name__ == "__main__":
    main()
