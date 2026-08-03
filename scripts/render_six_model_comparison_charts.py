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
AA_SNAPSHOT = ROOT / "experiments/six_model_external_capability_cost_snapshot_20260731.json"
OUTPUT = ROOT / "docs/research/assets/six_model_comparison_2026-07-18"

MODELS = [
    ("openai/gpt-4.1-mini", "GPT-4.1-mini"),
    ("openai/gpt-5.6-luna", "GPT-5.6 Luna"),
    ("openai/gpt-5.6-sol", "GPT-5.6 Sol"),
    ("deepseek/deepseek-v4-flash", "DeepSeek V4 Flash"),
    ("ollama_chat/qwen3.6:35b", "Qwen 3.6:35B"),
    ("ollama_chat/gemma4:26b", "Gemma 4 26B"),
]

SHORT = {
    "openai/gpt-4.1-mini": "mini",
    "openai/gpt-5.6-luna": "Luna",
    "openai/gpt-5.6-sol": "Sol",
    "deepseek/deepseek-v4-flash": "DeepSeek",
    "ollama_chat/qwen3.6:35b": "Qwen",
    "ollama_chat/gemma4:26b": "Gemma",
}

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


def _save(fig: plt.Figure, filename: str) -> None:
    fig.savefig(OUTPUT / filename, format="svg")
    fig.savefig(OUTPUT / filename.replace(".svg", ".png"), dpi=160)
    plt.close(fig)


def _finish_x(ax: plt.Axes, xlabel: str) -> None:
    ax.set_xlabel(xlabel, labelpad=10)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))


def _finish_y(ax: plt.Axes, ylabel: str) -> None:
    ax.set_ylabel(ylabel, labelpad=10)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)


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
    _finish_x(ax, xlabel)
    _save(fig, filename)


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
    _finish_x(ax, xlabel)
    _save(fig, filename)


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
    _save(fig, filename)


def _gap_bars(
    filename: str,
    title: str,
    subtitle: str,
    llm_gap: dict[str, float],
    rules_gap: dict[str, float],
    *,
    sort_on: dict[str, float],
    xlabel: str,
) -> None:
    ordered = sorted(MODELS, key=lambda item: sort_on[item[0]])
    keys = [key for key, _ in ordered]
    labels = [label for _, label in ordered]
    y = np.arange(len(labels))
    height = 0.32
    fig, ax = plt.subplots(figsize=(10.8, 6.5))
    fig.subplots_adjust(left=0.22, right=0.97, top=0.84, bottom=0.20)
    ax.axvline(0, color=GRID, linewidth=1.2, zorder=0)
    ax.barh(
        y - height / 2,
        [llm_gap[k] for k in keys],
        height,
        label="LLM only",
        color=NEUTRAL,
        edgecolor="none",
    )
    ax.barh(
        y + height / 2,
        [rules_gap[k] for k in keys],
        height,
        label="LLM with rules",
        color=ORANGE,
        edgecolor="none",
    )
    for offset, values in ((-height / 2, llm_gap), (height / 2, rules_gap)):
        for row, key in enumerate(keys):
            value = values[key]
            ax.text(
                value + (0.004 if value >= 0 else -0.004),
                row + offset,
                f"{value:+.2f}",
                va="center",
                ha="left" if value >= 0 else "right",
                color=INK,
                fontsize=9,
            )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    span = max(abs(v) for v in [*llm_gap.values(), *rules_gap.values()]) + 0.02
    ax.set_xlim(-span, span)
    ax.legend(
        frameon=False,
        ncols=2,
        loc="upper right",
        bbox_to_anchor=(1, -0.10),
        borderaxespad=0,
    )
    _header(ax, title, subtitle)
    _finish_x(ax, xlabel)
    _save(fig, filename)


def _rules_lift_bars(
    filename: str,
    title: str,
    subtitle: str,
    lift_dev: dict[str, float],
    lift_test: dict[str, float],
    *,
    sort_on: dict[str, float],
    xlabel: str,
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
        [lift_dev[k] for k in keys],
        height,
        label="Development",
        color=TEAL_LIGHT,
        edgecolor="none",
    )
    ax.barh(
        y + height / 2,
        [lift_test[k] for k in keys],
        height,
        label="Locked holdout",
        color=TEAL,
        edgecolor="none",
    )
    for offset, values in ((-height / 2, lift_dev), (height / 2, lift_test)):
        for row, key in enumerate(keys):
            ax.text(
                values[key] + 0.003,
                row + offset,
                f"{values[key]:+.2f}",
                va="center",
                color=INK,
                fontsize=9,
            )
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, max(lift_dev.values()) + 0.03)
    ax.legend(
        frameon=False,
        ncols=2,
        loc="upper right",
        bbox_to_anchor=(1, -0.10),
        borderaxespad=0,
    )
    _header(ax, title, subtitle)
    _finish_x(ax, xlabel)
    _save(fig, filename)


def _scatter(
    filename: str,
    title: str,
    subtitle: str,
    xs: dict[str, float],
    ys: dict[str, float],
    *,
    xlabel: str,
    ylabel: str,
    x_fmt: str = "%.2f",
    y_fmt: str = "%.2f",
    annotate_short: bool = True,
) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    fig.subplots_adjust(left=0.12, right=0.96, top=0.84, bottom=0.12)
    x_vals = [xs[model] for model, _ in MODELS]
    y_vals = [ys[model] for model, _ in MODELS]
    ax.scatter(x_vals, y_vals, s=90, color=TEAL, edgecolor=INK, linewidth=0.6, zorder=3)
    for model, _ in MODELS:
        label = SHORT[model] if annotate_short else dict(MODELS)[model]
        ax.annotate(
            label,
            (xs[model], ys[model]),
            textcoords="offset points",
            xytext=(7, 5),
            color=INK,
            fontsize=9,
        )
    lo_x, hi_x = min(x_vals), max(x_vals)
    lo_y, hi_y = min(y_vals), max(y_vals)
    pad_x = max(0.02, (hi_x - lo_x) * 0.12)
    pad_y = max(0.01, (hi_y - lo_y) * 0.18)
    ax.set_xlim(lo_x - pad_x, hi_x + pad_x)
    ax.set_ylim(lo_y - pad_y, hi_y + pad_y)
    ax.xaxis.set_major_formatter(FormatStrFormatter(x_fmt))
    ax.yaxis.set_major_formatter(FormatStrFormatter(y_fmt))
    _header(ax, title, subtitle)
    _finish_y(ax, ylabel)
    ax.set_xlabel(xlabel, labelpad=10)
    ax.grid(True, color=GRID, linewidth=0.8)
    _save(fig, filename)


def _cost_frontier(
    filename: str,
    title: str,
    subtitle: str,
    costs: dict[str, float],
    scores: dict[str, float],
    *,
    xlabel: str,
    ylabel: str,
) -> None:
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
    fig.subplots_adjust(left=0.12, right=0.96, top=0.84, bottom=0.12)
    x_vals = [costs[model] for model, _ in MODELS]
    y_vals = [scores[model] for model, _ in MODELS]
    ax.scatter(x_vals, y_vals, s=90, color=ORANGE, edgecolor=INK, linewidth=0.6, zorder=3)
    for model, _ in MODELS:
        ax.annotate(
            SHORT[model],
            (costs[model], scores[model]),
            textcoords="offset points",
            xytext=(7, 5),
            color=INK,
            fontsize=9,
        )
    ax.set_xscale("log")
    ax.set_xlim(min(x_vals) * 0.6, max(x_vals) * 1.8)
    lo_y, hi_y = min(y_vals), max(y_vals)
    ax.set_ylim(lo_y - 0.02, hi_y + 0.03)
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
    _header(ax, title, subtitle)
    _finish_y(ax, ylabel)
    ax.set_xlabel(xlabel, labelpad=10)
    ax.grid(True, which="both", color=GRID, linewidth=0.8)
    _save(fig, filename)


def main() -> None:
    _style()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    panel = _read(PANEL)
    aa = _read(AA_SNAPSHOT)
    by_model = {row["model"]: row for row in panel["conditions"]}
    aa_by_name = {row["roster_display_name"]: row for row in aa["models"]}
    budget = aa["illustrative_extraction_token_budget"]
    in_tok = int(budget["input_tokens_per_note"])
    out_tok = int(budget["output_tokens_per_note"])

    exect_dev_rules = {
        model: float(by_model[model]["exectv2"]["dev140"]["llm_with_rules_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_test_rules = {
        model: float(by_model[model]["exectv2"]["test60"]["llm_with_rules_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_dev_llm = {
        model: float(by_model[model]["exectv2"]["dev140"]["llm_clinical_fact_f1"])
        for model, _ in MODELS
    }
    exect_test_llm = {
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
    gan_dev_rules = {
        model: float(by_model[model]["gan2026"]["dev750"]["llm_with_rules_purist_accuracy"])
        for model, _ in MODELS
    }
    gan_test_rules = {
        model: float(by_model[model]["gan2026"]["test450"]["llm_with_rules_purist_accuracy"])
        for model, _ in MODELS
    }
    gan_dev_llm = {
        model: float(by_model[model]["gan2026"]["dev750"]["llm_purist_accuracy"])
        for model, _ in MODELS
    }
    gan_test_llm = {
        model: float(by_model[model]["gan2026"]["test450"]["llm_purist_accuracy"])
        for model, _ in MODELS
    }

    exect_gap_llm = {m: exect_test_llm[m] - exect_dev_llm[m] for m, _ in MODELS}
    exect_gap_rules = {m: exect_test_rules[m] - exect_dev_rules[m] for m, _ in MODELS}
    gan_gap_llm = {m: gan_test_llm[m] - gan_dev_llm[m] for m, _ in MODELS}
    gan_gap_rules = {m: gan_test_rules[m] - gan_dev_rules[m] for m, _ in MODELS}
    exect_lift_dev = {m: exect_dev_rules[m] - exect_dev_llm[m] for m, _ in MODELS}
    exect_lift_test = {m: exect_test_rules[m] - exect_test_llm[m] for m, _ in MODELS}
    gan_lift_dev = {m: gan_dev_rules[m] - gan_dev_llm[m] for m, _ in MODELS}
    gan_lift_test = {m: gan_test_rules[m] - gan_test_llm[m] for m, _ in MODELS}

    healthcare = {}
    cost_per_1k = {}
    for model, label in MODELS:
        row = aa_by_name[label]
        healthcare[model] = float(row["healthcare_index"])
        price = row["list_price_usd_per_million_tokens"]
        cost_per_1k[model] = (
            float(price["input"]) * in_tok + float(price["output"]) * out_tok
        ) / 1000.0

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
        exect_dev_rules,
        exect_test_rules,
        sort_on=exect_test_rules,
        xlabel="Clinical fact F1 (0–1)",
        colors=(TEAL_LIGHT, TEAL),
    )
    _grouped_bar(
        "exect_llm_rules.svg",
        "ExECT clinical fact F1: LLM only and LLM with rules",
        shared_method_subtitle,
        "LLM only",
        "LLM with rules",
        exect_test_llm,
        exect_test_rules,
        sort_on=exect_test_rules,
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
        gan_dev_rules,
        gan_test_rules,
        sort_on=gan_test_rules,
        xlabel="Purist accuracy (0–1)",
        colors=(TEAL_LIGHT, TEAL),
    )
    _grouped_bar(
        "gan_llm_rules.svg",
        "Gan Purist accuracy: LLM only and LLM with rules",
        shared_method_subtitle,
        "LLM only",
        "LLM with rules",
        gan_test_llm,
        gan_test_rules,
        sort_on=gan_test_rules,
        xlabel="Purist accuracy (0–1)",
        colors=(NEUTRAL, ORANGE),
    )

    _gap_bars(
        "exect_generalization_gap.svg",
        "ExECT generalization gap by method",
        "test60 − dev140 clinical fact F1; negative means holdout is lower",
        exect_gap_llm,
        exect_gap_rules,
        sort_on=exect_gap_rules,
        xlabel="Holdout minus development (clinical fact F1)",
    )
    _gap_bars(
        "gan_generalization_gap.svg",
        "Gan generalization gap by method",
        (
            "test450 − dev750 Purist; DeepSeek llm_only mixes pre-0731 development "
            "with 0731 holdout"
        ),
        gan_gap_llm,
        gan_gap_rules,
        sort_on=gan_gap_rules,
        xlabel="Holdout minus development (Purist accuracy)",
    )
    _rules_lift_bars(
        "exect_rules_lift_by_split.svg",
        "ExECT rules lift is larger on development",
        "LLM-with-rules minus LLM-only clinical fact F1 on each split",
        exect_lift_dev,
        exect_lift_test,
        sort_on=exect_lift_dev,
        xlabel="Rules lift (clinical fact F1)",
    )
    _rules_lift_bars(
        "gan_rules_lift_by_split.svg",
        "Gan rules lift by split",
        (
            "LLM-with-rules minus LLM-only Purist; methods differ (v0.8 llm_only vs "
            "current-floors llm_with_rules)"
        ),
        gan_lift_dev,
        gan_lift_test,
        sort_on=gan_lift_dev,
        xlabel="Rules lift (Purist accuracy)",
    )
    _scatter(
        "cross_task_holdout_scatter.svg",
        "Cross-task holdout scores under LLM with rules",
        "Aggregate-only locked holdout; metrics are not interchangeable",
        gan_test_rules,
        exect_test_rules,
        xlabel="Gan test450 Purist accuracy",
        ylabel="ExECT test60 clinical fact F1",
    )
    _scatter(
        "aa_healthcare_vs_exect.svg",
        "AA Healthcare Index versus ExECT holdout",
        "External AA context on x; task score on y (not the same units)",
        healthcare,
        exect_test_rules,
        xlabel="Artificial Analysis Healthcare & Medical Index",
        ylabel="ExECT test60 clinical fact F1",
        x_fmt="%.0f",
    )
    _scatter(
        "aa_healthcare_vs_gan.svg",
        "AA Healthcare Index versus Gan holdout",
        "External AA context on x; task score on y (not the same units)",
        healthcare,
        gan_test_rules,
        xlabel="Artificial Analysis Healthcare & Medical Index",
        ylabel="Gan test450 Purist accuracy",
        x_fmt="%.0f",
    )
    _cost_frontier(
        "cost_quality_frontier.svg",
        "Illustrative list-price cost versus ExECT holdout",
        (
            f"External AA list prices; {in_tok:,} in + {out_tok:,} out tokens/note; "
            "no thinking surplus"
        ),
        cost_per_1k,
        exect_test_rules,
        xlabel="Illustrative USD per 1,000 notes (log scale)",
        ylabel="ExECT test60 clinical fact F1",
    )


if __name__ == "__main__":
    main()
