"""Render and validate the human view of the shared reliability scorecard."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from clinical_extraction.core.shared_reliability_schema import SIX_MODELS


def _format_float(value: float) -> str:
    return f"{value:.4f}"


def _task_cell(scorecard: Mapping[str, Any], task: str, criterion_id: str) -> Mapping[str, Any]:
    return next(
        cell
        for cell in scorecard["task_criteria"]
        if cell["task"] == task and cell["criterion_id"] == criterion_id
    )


def _measurement_by_id(scorecard: Mapping[str, Any], measurement_id: str) -> Mapping[str, Any]:
    return next(
        item for item in scorecard["measurements"] if item["measurement_id"] == measurement_id
    )


def render_report(scorecard: Mapping[str, Any]) -> str:
    """Render the human scorecard from the machine scorecard."""

    criteria = {criterion["id"]: criterion for criterion in scorecard["criteria"]}
    gan_purist = _measurement_by_id(
        scorecard,
        "gan2026_six_model_test450_purist_accuracy",
    )["value"]
    gan_pragmatic = _measurement_by_id(
        scorecard,
        "gan2026_six_model_test450_pragmatic_accuracy",
    )["value"]
    exect_dev = _measurement_by_id(
        scorecard,
        "exectv2_six_model_dev140_clinical_headline_f1",
    )["value"]
    exect_test = _measurement_by_id(
        scorecard,
        "exectv2_six_model_test60_clinical_headline_f1",
    )["value"]
    transitions = _measurement_by_id(
        scorecard,
        "exectv2_six_model_sf_correction_transitions",
    )["value"]

    model_labels = {
        "openai/gpt-4.1-mini": "GPT-4.1-mini",
        "openai/gpt-5.6-luna": "GPT-5.6 Luna",
        "openai/gpt-5.6-sol": "GPT-5.6 Sol",
        "deepseek/deepseek-v4-flash": "DeepSeek V4 Flash",
        "ollama_chat/qwen3.6:35b": "Qwen 3.6:35B",
        "ollama_chat/gemma4:26b": "Gemma 4 26B",
    }

    lines = [
        "# Shared reliability scorecard",
        "",
        "Date: 2026-07-18  ",
        "Evidence mode: retained no-call replay and synthesis",
        "",
        "Gan 2026 and ExECTv2 are assessed with the same eight reliability questions.",
        "Each task keeps its own measurement object, denominator, scorer, output stage,",
        "and claim boundary. No composite reliability score or pooled task ranking is",
        "calculated.",
        "",
        "This report is generated from",
        (
            "[`shared_reliability_scorecard_20260718.json`]"
            "(../../experiments/shared_reliability_scorecard_20260718.json)."
        ),
        "The exact selected sources and hashes are owned by the",
        "[retained evidence index](../experiments/retained_evidence_manifest.md).",
        "",
        "## Gan 2026 task scorecard",
        "",
        "| Criterion | State | Strongest evidence | Result and limit |",
        "| --- | --- | --- | --- |",
    ]
    for criterion in scorecard["criteria"]:
        cell = _task_cell(scorecard, "gan2026", criterion["id"])
        lines.append(
            f"| {criterion['name']} | `{cell['result_state']}` / `{cell['completion_status']}` "
            f"| `{cell['strongest_evidence_state']}` | {cell['summary']} |"
        )

    lines.extend(
        [
            "",
            "### Gan matched six-model test450 panel",
            "",
            "| Model | Purist | Pragmatic |",
            "| --- | ---: | ---: |",
        ]
    )
    for model in SIX_MODELS:
        lines.append(
            f"| {model_labels[model]} | {gan_purist[model]['correct']}/450 "
            f"| {gan_pragmatic[model]['correct']}/450 |"
        )
    lines.extend(
        [
            "",
            "The panel is aggregate-only evidence on a previously used locked holdout.",
            "Provider routes and temperatures differ, and the result is not a pristine",
            "one-shot or general model-superiority comparison.",
            "",
            "## ExECTv2 task scorecard",
            "",
            "| Criterion | State | Strongest evidence | Result and limit |",
            "| --- | --- | --- | --- |",
        ]
    )
    for criterion in scorecard["criteria"]:
        cell = _task_cell(scorecard, "exectv2", criterion["id"])
        lines.append(
            f"| {criterion['name']} | `{cell['result_state']}` / `{cell['completion_status']}` "
            f"| `{cell['strongest_evidence_state']}` | {cell['summary']} |"
        )

    lines.extend(
        [
            "",
            "### ExECT fixed six-model panel",
            "",
            "| Model | dev140 F1 | test60 F1 | Change |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for model in SIX_MODELS:
        change = round(exect_test[model] - exect_dev[model], 4)
        lines.append(
            f"| {model_labels[model]} | {_format_float(exect_dev[model])} "
            f"| {_format_float(exect_test[model])} | {change:+.4f} |"
        )
    lines.extend(
        [
            "",
            "The test60 values are aggregate-only internal-score results over 59 loadable",
            "letters. `clinical_headline` is not the published ExECT benchmark, and these",
            "results are not clinical validation. Hosted and local runtime routes remain",
            "separate conditions.",
            "",
            "The six-model SF component replay records",
            f"{transitions['wrong_to_correct']} wrong-to-correct and",
            f"{transitions['correct_to_wrong']} correct-to-wrong transitions. The 840",
            "model-letter rows repeat the same 140 letters and are descriptive, not 840",
            "independent clinical samples. The predeclared unknown-only denominator is zero;",
            "empty-gold letters were not relabelled as unknown.",
            "",
            "## Cross-task criterion matrix",
            "",
            "| Criterion | Comparability | Numerical delta | Reason |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for comparison in scorecard["cross_task_matrix"]:
        lines.append(
            f"| {comparison['criterion']} | `{comparison['comparability']}` | — | "
            f"{comparison['reason']} |"
        )

    lines.extend(
        [
            "",
            "## Evidence-state and comparability matrix",
            "",
            "| Criterion | Gan evidence | ExECT evidence | Comparability |",
            "| --- | --- | --- | --- |",
        ]
    )
    for item in scorecard["evidence_state_matrix"]:
        lines.append(
            f"| {criteria[item['criterion_id']]['name']} | `{item['gan2026']}` | "
            f"`{item['exectv2']}` | `{item['comparability']}` |"
        )

    lines.extend(
        [
            "",
            "## Unresolved dependencies",
            "",
        ]
    )
    for gap in scorecard["gaps"]:
        lines.extend(
            [
                f"- `{gap['id']}` ({gap['class']}): {gap['decision']} "
                f"Unblock when {gap['unblock_condition']} {gap['claim_effect']}",
                "",
            ]
        )

    lines.extend(
        [
            "## Claim boundary",
            "",
            str(scorecard["claim_boundary"]),
            "",
            "Exact source presence is not semantic support. Internal review is not",
            "independent clinical validation. Construct-only and not-comparable cells do not",
            "produce cross-task numerical differences. No composite score is reported.",
            "",
            "<!-- MACHINE SYNCHRONIZATION MARKERS; generated, do not edit -->",
        ]
    )
    for measurement in scorecard["measurements"]:
        canonical = json.dumps(
            {
                "denominator": measurement["denominator"],
                "result_state": measurement["result_state"],
                "value": measurement["value"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(canonical.encode()).hexdigest()
        lines.append(f"<!-- measurement:{measurement['measurement_id']}:{digest} -->")
    lines.append("")
    return "\n".join(lines)


def validate_report(scorecard: Mapping[str, Any], report: str) -> None:
    """Require the report to be the exact generated view of the scorecard."""

    expected = render_report(scorecard)
    if report != expected:
        raise ValueError("human reliability report does not reproduce the machine scorecard")
