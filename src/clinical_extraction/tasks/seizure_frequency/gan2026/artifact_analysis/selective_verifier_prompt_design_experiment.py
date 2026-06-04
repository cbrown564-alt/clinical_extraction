"""Run plain-language selective verifier prompt designs over predeclared rows."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

from . import selective_verifier_experiment as base_experiment
from . import selective_verifier_predeclaration as predecl

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_verifier_prompt_designs_live_gpt41mini_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_verifier_prompt_designs_live_gpt41mini_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_selective_verifier_prompt_designs_live_gpt41mini_2026-06-04.md"
)
DEFAULT_PREDECLARATION_JSONL_PATH = predecl.DEFAULT_JSONL_PATH
DEFAULT_SOURCE_DATA_PATH = Path("data/Gan (2026)/synthetic_data_subset_1500.json")
TASK_DESIGNS = tuple(predecl.PROMPT_DESIGN_ORDER)
FULL_LETTER_TASK_DESIGN = "support_parts_full_letter"
BINARY_TASK_DESIGN = "binary_quote_highest_answer_selector"
ACTION_VALUES = {"use_proposed_answer", "use_unknown", "needs_review"}
SUPPORT_PARTS_FULL_LETTER_SYSTEM_PROMPT = (
    "Check whether the proposed seizure-frequency answer is supported by the "
    "clinical text. A supported answer has a seizure or event type, a count, a "
    "timeframe, and enough context to show it applies to the current highest "
    "seizure frequency. The evidence snippet is the passage that originally "
    "suggested the answer, but use the full clinical text when dates, currentness, "
    "seizure types, or other context matters. Do not fill in missing parts from "
    "assumptions. Return only JSON matching the requested fields."
)
BINARY_SYSTEM_PROMPT = (
    "Check a selected seizure-frequency quote and label using the full clinical "
    "letter. Answer the first three questions with only true or false. First, "
    "does the selected quote support the selected label? Second, is the selected "
    "label the highest current seizure frequency described anywhere in the "
    "letter? Third, are you certain? Then choose exactly one answer from the "
    "provided answer choices. Do not create a new answer. If none of the answer "
    "choices is clearly right, choose human_review. For the highest-frequency "
    "question, compare across all current or recent seizure/event types in the "
    "letter, not only the seizure type named in the selected quote. Set "
    "selected_label_is_highest_frequency to false if any other current or recent "
    "seizure type is more frequent, if another active seizure type continues but "
    "has no clear count, or if the selected label is about seizure freedom for "
    "only one seizure type while another type still occurs. Do not mark a "
    "zero-seizure label as highest when any current seizure-like events continue. "
    "Only answer true when the selected label is at least as frequent as every "
    "other current seizure/event frequency in the full letter. Return only JSON "
    "matching the requested fields."
)


class VetoFirstOutput(BaseModel):
    decision: str
    blocking_issue: str = ""
    supporting_quotes: list[str] = Field(default_factory=list)
    reason: str = ""
    confidence: str = ""


class SupportPartsOutput(BaseModel):
    seizure_or_event_type_supported: bool
    count_supported: bool
    timeframe_supported: bool
    current_highest_frequency_supported: bool
    all_required_parts_supported: bool
    recommended_action: str
    missing_or_conflicting_parts: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    reason: str = ""


class SupportPartsFullLetterOutput(BaseModel):
    seizure_or_event_type_supported: bool
    count_supported: bool
    timeframe_supported: bool
    current_highest_frequency_supported: bool
    all_answer_parts_supported: bool
    recommended_action: str
    missing_or_conflicting_parts: list[str] = Field(default_factory=list)
    quotes: list[str] = Field(default_factory=list)
    reason: str = ""


class BinaryQuoteHighestOutput(BaseModel):
    quote_supports_label: bool
    selected_label_is_highest_frequency: bool
    certain: bool
    selected_answer: str
    supporting_quotes: list[str] = Field(default_factory=list)
    reason: str = ""


ParsedOutput = (
    VetoFirstOutput
    | SupportPartsOutput
    | SupportPartsFullLetterOutput
    | BinaryQuoteHighestOutput
)


def run_experiment(
    predeclared_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
    task_designs: Sequence[str] = TASK_DESIGNS,
    source_text_by_row: Mapping[int, str] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    source_text_by_row = source_text_by_row or {}
    rows = [
        _run_row(
            predeclared,
            task_design=task_design,
            model=model,
            max_tokens=max_tokens,
            source_text_by_row=source_text_by_row,
        )
        for predeclared in sorted(
            predeclared_rows, key=lambda row: int(row["source_row_index"])
        )
        for task_design in task_designs
    ]
    return rows, summarize_results(rows, model=model)


def summarize_results(rows: Sequence[Mapping[str, Any]], *, model: str) -> dict[str, Any]:
    by_design: dict[str, dict[str, Any]] = {}
    for task_design in sorted({str(row["task_design"]) for row in rows}):
        design_rows = [row for row in rows if row["task_design"] == task_design]
        delta_counts = Counter(row["verifier_vs_routing"]["delta"] for row in design_rows)
        action_counts = Counter(row["design_action"] for row in design_rows)
        changed_rows = [
            row for row in design_rows if row["verifier_vs_routing"]["decision_changed"]
        ]
        changed_scorable_rows = [
            row for row in changed_rows if row["verifier_decision"]["scorable"] is True
        ]
        changed_correct_rows = [
            row
            for row in changed_scorable_rows
            if row["verifier_decision"]["purist_correct"] is True
        ]
        by_design[task_design] = {
            "row_count": len(design_rows),
            "call_ok_rows": sum(row["call_status"] == "ok" for row in design_rows),
            "parse_ok_rows": sum(
                row.get("parsed_output") is not None and not row["parse_errors"]
                for row in design_rows
            ),
            "parse_error_rows": sum(
                row.get("parsed_output") is None or bool(row["parse_errors"])
                for row in design_rows
            ),
            "all_evidence_quotes_exact_rows": sum(
                bool(row["verifier_decision"]["all_evidence_quotes_exact"])
                for row in design_rows
                if row.get("parsed_output") is not None and not row["parse_errors"]
            ),
            "decision_changed_rows": len(changed_rows),
            "changed_scorable_rows": len(changed_scorable_rows),
            "changed_decision_precision": base_experiment._safe_rate(
                len(changed_correct_rows), len(changed_scorable_rows)
            ),
            "w_to_c_vs_routing_rows": delta_counts["W_to_C"],
            "c_to_w_vs_routing_rows": delta_counts["C_to_W"],
            "c_to_review_vs_routing_rows": delta_counts["C_to_review"],
            "w_to_review_vs_routing_rows": delta_counts["W_to_review"],
            "unchanged_rows": delta_counts["unchanged"],
            "action_counts": dict(sorted(action_counts.items())),
            "delta_counts": dict(sorted(delta_counts.items())),
            "regression_source_row_indices": [
                int(row["source_row_index"])
                for row in design_rows
                if row["verifier_vs_routing"]["delta"] == "C_to_W"
            ],
        }
    return {
        "artifact_kind": "gan2026_selective_verifier_prompt_design_live_summary",
        "date": "2026-06-04",
        "model": model,
        "source_artifact": str(DEFAULT_PREDECLARATION_JSONL_PATH),
        "task_designs": sorted(by_design),
        "claim_boundary": (
            "Validation-development prompt-design comparison over the frozen "
            "42-row selective-verifier surface. This does not authorize locked-test "
            "inspection, whole-pipeline promotion, or benchmark-comparable claims."
        ),
        "row_count": len(rows),
        "by_design": by_design,
        "usage": _usage_summary(rows),
        "interpretation": _interpretation(by_design),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    lines = [
        "# Gan 2026 Selective Verifier Prompt Design Live Run",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        *(
            ["Reparse note: " + str(metadata["reparse_note"]), ""]
            if metadata.get("reparse_note")
            else []
        ),
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source predeclaration: `{metadata['source_artifact']}`",
        "",
        "## Metrics By Design",
        "",
    ]
    for task_design, metrics in metadata["by_design"].items():
        lines.extend(
            [
                f"### `{task_design}`",
                "",
                "| Metric | Value |",
                "| --- | ---: |",
            ]
        )
        for key, value in metrics.items():
            if key in {"action_counts", "delta_counts", "regression_source_row_indices"}:
                continue
            lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
        lines.extend(["", "Action counts:", ""])
        for key, value in metrics["action_counts"].items():
            lines.append(f"- `{key}`: {value}")
        lines.extend(["", "Delta counts:", ""])
        for key, value in metrics["delta_counts"].items():
            lines.append(f"- `{key}`: {value}")
        lines.extend(
            [
                "",
                "C->W rows: "
                + ", ".join(str(row) for row in metrics["regression_source_row_indices"]),
                "",
            ]
        )
    lines.extend(
        [
            "## Changed Rows",
            "",
            "| Design | Row | Action | Label | Delta | Quotes exact |",
            "| --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["verifier_vs_routing"]["decision_changed"]:
            continue
        decision = row["verifier_decision"]
        lines.append(
            f"| `{row['task_design']}` | {row['source_row_index']} | "
            f"{row['design_action']} | {decision.get('label')} | "
            f"{row['verifier_vs_routing']['delta']} | "
            f"{decision['all_evidence_quotes_exact']} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_row(
    predeclared: Mapping[str, Any],
    *,
    task_design: str,
    model: str,
    max_tokens: int,
    source_text_by_row: Mapping[int, str],
) -> dict[str, Any]:
    model_input = _model_input(predeclared, task_design, source_text_by_row)
    system_prompt = str(model_input.pop("system_prompt"))
    call_errors: list[str] = []
    raw_output = ""
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    try:
        raw_output, usage, latency_seconds = base_experiment._call_openai_responses(
            system_prompt,
            model_input,
            model=model,
            max_tokens=max_tokens,
        )
        call_status = "ok"
    except Exception as exc:  # pragma: no cover - live failure path
        call_status = "error"
        call_errors.append(f"{type(exc).__name__}: {exc}")
    parsed, parse_errors = _parse_output(task_design, raw_output) if raw_output else (None, [])
    if parsed is None and not call_errors and not parse_errors:
        parse_errors = ["empty_output"]
    if parsed is None and call_errors and not parse_errors:
        parse_errors = ["call_error_no_output"]
    verifier_decision = _design_decision(
        task_design,
        parsed,
        predeclared,
        parse_errors=parse_errors,
        model_input=model_input,
    )
    routing_decision = base_experiment._routing_decision(predeclared)
    return {
        "artifact_kind": "gan2026_selective_verifier_prompt_design_live_row",
        "source_row_index": int(predeclared["source_row_index"]),
        "split": predeclared.get("split", "validation"),
        "split_manifest": predeclared.get("split_manifest", "gan2026_split_v1"),
        "task_design": task_design,
        "hidden_families": list(predeclared.get("hidden_families") or []),
        "model": model,
        "call_status": call_status,
        "call_errors": call_errors,
        "latency_seconds": latency_seconds,
        "usage": usage,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "parsed_output": parsed.model_dump(mode="json") if parsed else None,
        "design_action": _action_from_output(task_design, parsed)
        if parsed and not parse_errors
        else "parse_error",
        "routing_decision": routing_decision,
        "verifier_decision": verifier_decision,
        "verifier_vs_routing": base_experiment._delta(
            verifier_decision, routing_decision
        ),
        "development_accounting": predeclared["development_accounting"],
        "claim_boundary": "validation_development_selective_verifier_prompt_design_live",
    }


def _parse_output(task_design: str, raw_output: str) -> tuple[ParsedOutput | None, list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
        payload = _normalize_payload(task_design, payload)
        if task_design == "veto_first_safety_reviewer":
            parsed: ParsedOutput = VetoFirstOutput.model_validate(payload)
            errors = _validate_action("decision", parsed.decision)
        elif task_design == "support_parts_fact_check":
            parsed = SupportPartsOutput.model_validate(payload)
            errors = _validate_action("recommended_action", parsed.recommended_action)
        elif task_design == FULL_LETTER_TASK_DESIGN:
            parsed = SupportPartsFullLetterOutput.model_validate(payload)
            errors = _validate_action("recommended_action", parsed.recommended_action)
        elif task_design == BINARY_TASK_DESIGN:
            parsed = BinaryQuoteHighestOutput.model_validate(payload)
            errors = []
        else:
            return None, [f"unsupported_task_design:{task_design}"]
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    return (None, errors) if errors else (parsed, [])


def _extract_json_object(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("{") and stripped.endswith("}"):
        return stripped
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL)
    if match:
        return match.group(1)
    first = stripped.find("{")
    last = stripped.rfind("}")
    if first >= 0 and last > first:
        return stripped[first : last + 1]
    raise ValueError("no JSON object found")


def _validate_action(field: str, action: str) -> list[str]:
    if action not in ACTION_VALUES:
        return [f"unsupported_{field}:{action}"]
    return []


def _normalize_payload(task_design: str, payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    if task_design == "veto_first_safety_reviewer":
        _collapse_single_item_list(normalized, "decision")
    if task_design == "support_parts_fact_check":
        _collapse_single_item_list(normalized, "recommended_action")
    if task_design == FULL_LETTER_TASK_DESIGN:
        _collapse_single_item_list(normalized, "recommended_action")
    if task_design == BINARY_TASK_DESIGN:
        _collapse_single_item_list(normalized, "selected_answer")
    return normalized


def _model_input(
    predeclared: Mapping[str, Any],
    task_design: str,
    source_text_by_row: Mapping[int, str],
) -> dict[str, Any]:
    if task_design not in {FULL_LETTER_TASK_DESIGN, BINARY_TASK_DESIGN}:
        return dict(predeclared["prompt_design_candidates"][task_design])
    snippet_payload = predeclared["prompt_design_candidates"]["support_parts_fact_check"]
    source_row_index = int(predeclared["source_row_index"])
    if task_design == BINARY_TASK_DESIGN:
        selected_label = snippet_payload.get("proposed_answer")
        return {
            "task_design": BINARY_TASK_DESIGN,
            "system_prompt": BINARY_SYSTEM_PROMPT,
            "clinical_text": source_text_by_row.get(source_row_index)
            or snippet_payload.get("clinical_text"),
            "selected_quote": snippet_payload.get("clinical_text"),
            "selected_label": selected_label,
            "answer_choices": [selected_label, "unknown", "human_review"],
            "competing_possibilities": snippet_payload.get("competing_possibilities", []),
            "review_reasons": snippet_payload.get("review_reasons", []),
            "output_schema": {
                "quote_supports_label": "true or false.",
                "selected_label_is_highest_frequency": "true or false.",
                "certain": "true or false.",
                "selected_answer": "One value copied from answer_choices.",
                "supporting_quotes": ["Exact copied phrases from clinical_text."],
                "reason": "Brief explanation using only the provided clinical text.",
            },
        }
    return {
        "task_design": FULL_LETTER_TASK_DESIGN,
        "system_prompt": SUPPORT_PARTS_FULL_LETTER_SYSTEM_PROMPT,
        "clinical_text": source_text_by_row.get(source_row_index)
        or snippet_payload.get("clinical_text"),
        "evidence_snippet": snippet_payload.get("clinical_text"),
        "proposed_answer": snippet_payload.get("proposed_answer"),
        "competing_possibilities": snippet_payload.get("competing_possibilities", []),
        "review_reasons": snippet_payload.get("review_reasons", []),
        "output_schema": {
            "seizure_or_event_type_supported": "true or false.",
            "count_supported": "true or false.",
            "timeframe_supported": "true or false.",
            "current_highest_frequency_supported": "true or false.",
            "all_answer_parts_supported": "true or false.",
            "recommended_action": ["use_proposed_answer", "use_unknown", "needs_review"],
            "missing_or_conflicting_parts": [
                "Short names of any unsupported or conflicting parts."
            ],
            "quotes": ["Exact copied phrases from clinical_text."],
            "reason": "Brief explanation using only the provided clinical text.",
        },
    }


def _collapse_single_item_list(payload: dict[str, Any], key: str) -> None:
    value = payload.get(key)
    if isinstance(value, list) and len(value) == 1:
        payload[key] = value[0]


def _design_decision(
    task_design: str,
    parsed: ParsedOutput | None,
    predeclared: Mapping[str, Any],
    *,
    parse_errors: Sequence[str],
    model_input: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    accounting = predeclared["development_accounting"]
    if parsed is None or parse_errors:
        return base_experiment._decision(
            "parse_error", None, False, accounting["gold_label"], False
        )
    action = _action_from_output(task_design, parsed)
    evidence_ok = _evidence_quotes_exact(
        task_design, parsed, predeclared, model_input=model_input
    )
    if task_design == BINARY_TASK_DESIGN:
        return _binary_design_decision(
            parsed, predeclared, evidence_ok=evidence_ok  # type: ignore[arg-type]
        )
    if action == "needs_review":
        return base_experiment._decision(
            "abstain_review", None, False, accounting["gold_label"], evidence_ok
        )
    if action == "use_unknown":
        return base_experiment._decision(
            "render", "unknown", True, accounting["gold_label"], evidence_ok
        )
    if action == "use_proposed_answer":
        label = base_experiment._normalized_label(
            str(
                _proposed_answer(predeclared, task_design)
                or ""
            )
        )
        return base_experiment._decision(
            "render", label, label is not None, accounting["gold_label"], evidence_ok
        )
    return base_experiment._decision(
        "unsupported", None, False, accounting["gold_label"], evidence_ok
    )


def _action_from_output(task_design: str, parsed: ParsedOutput | None) -> str:
    if parsed is None:
        return "parse_error"
    if task_design == "veto_first_safety_reviewer":
        return parsed.decision  # type: ignore[union-attr]
    if task_design == "support_parts_fact_check":
        return parsed.recommended_action  # type: ignore[union-attr]
    if task_design == FULL_LETTER_TASK_DESIGN:
        return parsed.recommended_action  # type: ignore[union-attr]
    if task_design == BINARY_TASK_DESIGN:
        return parsed.selected_answer  # type: ignore[union-attr]
    return "unsupported"


def _evidence_quotes_exact(
    task_design: str,
    parsed: ParsedOutput,
    predeclared: Mapping[str, Any],
    *,
    model_input: Mapping[str, Any] | None = None,
) -> bool:
    payload = model_input or _model_input(predeclared, task_design, {})
    clinical_text = str(payload.get("clinical_text") or "")
    quotes = _quotes_from_output(task_design, parsed)
    return bool(quotes) and all(quote and quote in clinical_text for quote in quotes)


def _quotes_from_output(task_design: str, parsed: ParsedOutput) -> list[str]:
    if task_design == "veto_first_safety_reviewer":
        return list(parsed.supporting_quotes)  # type: ignore[union-attr]
    if task_design == "support_parts_fact_check":
        return list(parsed.quotes)  # type: ignore[union-attr]
    if task_design == FULL_LETTER_TASK_DESIGN:
        return list(parsed.quotes)  # type: ignore[union-attr]
    if task_design == BINARY_TASK_DESIGN:
        return list(parsed.supporting_quotes)  # type: ignore[union-attr]
    return []


def _proposed_answer(predeclared: Mapping[str, Any], task_design: str) -> Any:
    if task_design in {FULL_LETTER_TASK_DESIGN, BINARY_TASK_DESIGN}:
        return predeclared["prompt_design_candidates"]["support_parts_fact_check"].get(
            "proposed_answer"
        )
    return predeclared["prompt_design_candidates"][task_design].get("proposed_answer")


def _binary_design_decision(
    parsed: BinaryQuoteHighestOutput,
    predeclared: Mapping[str, Any],
    *,
    evidence_ok: bool,
) -> dict[str, Any]:
    accounting = predeclared["development_accounting"]
    proposed = str(_proposed_answer(predeclared, BINARY_TASK_DESIGN) or "")
    answer_choices = {proposed, "unknown", "human_review"}
    if parsed.selected_answer not in answer_choices:
        return base_experiment._decision(
            "abstain_review", None, False, accounting["gold_label"], evidence_ok
        )
    if parsed.quote_supports_label and parsed.selected_label_is_highest_frequency:
        label = base_experiment._normalized_label(proposed)
        return base_experiment._decision(
            "render", label, label is not None, accounting["gold_label"], evidence_ok
        )
    if parsed.certain and parsed.selected_answer not in {proposed, "human_review"}:
        label = base_experiment._normalized_label(parsed.selected_answer)
        return base_experiment._decision(
            "render", label, label is not None, accounting["gold_label"], evidence_ok
        )
    return base_experiment._decision(
        "abstain_review", None, False, accounting["gold_label"], evidence_ok
    )


def _usage_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    input_tokens = sum(int((row.get("usage") or {}).get("input_tokens") or 0) for row in rows)
    output_tokens = sum(int((row.get("usage") or {}).get("output_tokens") or 0) for row in rows)
    total_tokens = sum(int((row.get("usage") or {}).get("total_tokens") or 0) for row in rows)
    latency = sum(float(row.get("latency_seconds") or 0.0) for row in rows)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "wall_clock_latency_seconds": latency,
    }


def _interpretation(by_design: Mapping[str, Mapping[str, Any]]) -> str:
    regressions = {
        design: metrics["c_to_w_vs_routing_rows"]
        for design, metrics in by_design.items()
        if metrics["c_to_w_vs_routing_rows"]
    }
    if regressions:
        return (
            "Keep prompt designs diagnostic: at least one design introduced C->W "
            f"regressions versus routing ({regressions})."
        )
    wins = {
        design: metrics["w_to_c_vs_routing_rows"]
        for design, metrics in by_design.items()
        if metrics["w_to_c_vs_routing_rows"]
    }
    if wins:
        return (
            "No C->W regressions were observed; designs with W->C changes need row "
            f"adjudication before any prediction-bearing use ({wins})."
        )
    return "Both prompt designs remain diagnostic: no useful changed-decision gain observed."


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _load_source_text_by_row(path: Path) -> dict[int, str]:
    rows = json.loads(path.read_text())
    return {
        int(row["source_row_index"]): str(row.get("clinic_date") or "")
        for row in rows
        if "source_row_index" in row
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predeclaration-jsonl-path", type=Path, default=DEFAULT_PREDECLARATION_JSONL_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--source-data-path", type=Path, default=DEFAULT_SOURCE_DATA_PATH)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--max-tokens", type=int, default=900)
    parser.add_argument(
        "--task-design",
        choices=[*TASK_DESIGNS, FULL_LETTER_TASK_DESIGN, BINARY_TASK_DESIGN, "all"],
        default="all",
    )
    args = parser.parse_args(argv)

    task_designs: Sequence[str]
    if args.task_design == "all":
        task_designs = TASK_DESIGNS
    else:
        task_designs = (args.task_design,)
    predeclared_rows = load_jsonl_rows(args.predeclaration_jsonl_path)
    rows, metadata = run_experiment(
        predeclared_rows,
        model=args.model,
        max_tokens=args.max_tokens,
        task_designs=task_designs,
        source_text_by_row=_load_source_text_by_row(args.source_data_path),
    )
    metadata = {**metadata, "source_artifact": str(args.predeclaration_jsonl_path)}
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
