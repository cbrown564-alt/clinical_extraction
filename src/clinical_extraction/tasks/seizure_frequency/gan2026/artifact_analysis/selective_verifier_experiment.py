"""Run the Gan 2026 selective verifier over a frozen predeclared surface."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist

from . import selective_verifier_predeclaration as predecl

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_verifier_live_gpt41mini_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_verifier_live_gpt41mini_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_selective_verifier_live_gpt41mini_2026-06-04.md"
)
PROMPT_VERSION = "gan2026_selective_verifier_v0"
ALLOWED_RECOMMENDATIONS = predecl.ALLOWED_RECOMMENDATIONS
DEFAULT_PREDECLARATION_JSONL_PATH = predecl.DEFAULT_JSONL_PATH


class VerifierOutput(BaseModel):
    recommendation: str
    recommended_label: str | None = None
    chosen_competing_hypothesis: str | None = None
    evidence_quotes: list[str] = Field(default_factory=list)
    reason: str = ""
    confidence: str = ""


def run_experiment(
    predeclared_rows: Sequence[Mapping[str, Any]],
    *,
    model: str,
    max_tokens: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        _run_row(predeclared, model=model, max_tokens=max_tokens)
        for predeclared in sorted(predeclared_rows, key=lambda row: int(row["source_row_index"]))
    ]
    return rows, summarize_results(rows, model=model)


def summarize_results(rows: Sequence[Mapping[str, Any]], *, model: str) -> dict[str, Any]:
    parse_ok = [not row["parse_errors"] for row in rows]
    recommendation_counts = Counter(row["verifier_recommendation"] for row in rows)
    delta_counts = Counter(row["verifier_vs_routing"]["delta"] for row in rows)
    changed_rows = [row for row in rows if row["verifier_vs_routing"]["decision_changed"]]
    changed_scorable_rows = [
        row for row in changed_rows if row["verifier_decision"]["scorable"] is True
    ]
    changed_correct_rows = [
        row
        for row in changed_scorable_rows
        if row["verifier_decision"]["purist_correct"] is True
    ]
    evidence_exact_rows = [
        row
        for row in rows
        if not row["parse_errors"] and row["verifier_decision"]["all_evidence_quotes_exact"]
    ]
    return {
        "artifact_kind": "gan2026_selective_verifier_live_summary",
        "date": "2026-06-04",
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "source_artifact": str(DEFAULT_PREDECLARATION_JSONL_PATH),
        "claim_boundary": (
            "Validation-development selective verifier over the frozen predeclared "
            "suspicious selected-state surface. This does not authorize locked-test "
            "inspection, whole-pipeline promotion, or benchmark-comparable claims."
        ),
        "row_count": len(rows),
        "metrics": {
            "call_ok_rows": sum(row["call_status"] == "ok" for row in rows),
            "parse_ok_rows": sum(parse_ok),
            "parse_error_rows": len(rows) - sum(parse_ok),
            "all_evidence_quotes_exact_rows": len(evidence_exact_rows),
            "abstain_review_rows": recommendation_counts["abstain_review"],
            "decision_changed_rows": len(changed_rows),
            "changed_scorable_rows": len(changed_scorable_rows),
            "changed_decision_precision": _safe_rate(
                len(changed_correct_rows), len(changed_scorable_rows)
            ),
            "w_to_c_vs_routing_rows": delta_counts["W_to_C"],
            "c_to_w_vs_routing_rows": delta_counts["C_to_W"],
            "c_to_review_vs_routing_rows": delta_counts["C_to_review"],
            "w_to_review_vs_routing_rows": delta_counts["W_to_review"],
            "unchanged_rows": delta_counts["unchanged"],
        },
        "recommendation_counts": dict(sorted(recommendation_counts.items())),
        "delta_counts": dict(sorted(delta_counts.items())),
        "regression_source_row_indices": [
            int(row["source_row_index"])
            for row in rows
            if row["verifier_vs_routing"]["delta"] == "C_to_W"
        ],
        "changed_source_row_indices": [
            int(row["source_row_index"])
            for row in rows
            if row["verifier_vs_routing"]["decision_changed"]
        ],
        "usage": _usage_summary(rows),
        "interpretation": _interpretation(delta_counts),
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
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Selective Verifier Live Run",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(metadata["interpretation"]),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Source predeclaration: `{metadata['source_artifact']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Recommendations", "", "| Recommendation | Rows |", "| --- | ---: |"])
    for key, value in metadata["recommendation_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Deltas Versus Routing", "", "| Delta | Rows |", "| --- | ---: |"])
    for key, value in metadata["delta_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Changed Rows",
            "",
            "| Row | Routing | Verifier recommendation | Label | Delta | Quotes exact |",
            "| ---: | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if not row["verifier_vs_routing"]["decision_changed"]:
            continue
        decision = row["verifier_decision"]
        lines.append(
            f"| {row['source_row_index']} | "
            f"{row['routing_decision'].get('policy_action', row['routing_decision']['action'])} | "
            f"{row['verifier_recommendation']} | "
            f"{decision.get('label')} | "
            f"{row['verifier_vs_routing']['delta']} | "
            f"{decision['all_evidence_quotes_exact']} |"
        )
    lines.extend(
        [
            "",
            "## Promotion Boundary",
            "",
            "The verifier is not promoted to prediction-bearing use unless C->W rows are "
            "zero or explicitly adjudicated under a separate protocol. Abstentions and "
            "review recommendations remain routing actions, not correct final labels.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _run_row(
    predeclared: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> dict[str, Any]:
    model_input = dict(predeclared["verifier_model_input"])
    system_prompt = str(model_input.pop("system_prompt"))
    call_errors: list[str] = []
    raw_output = ""
    usage: dict[str, Any] = {}
    latency_seconds: float | None = None
    try:
        raw_output, usage, latency_seconds = _call_openai_responses(
            system_prompt,
            model_input,
            model=model,
            max_tokens=max_tokens,
        )
        call_status = "ok"
    except Exception as exc:  # pragma: no cover - live failure path
        call_status = "error"
        call_errors.append(f"{type(exc).__name__}: {exc}")

    parsed, parse_errors = _parse_output(raw_output) if raw_output else (None, [])
    if parsed is None and not call_errors and not parse_errors:
        parse_errors = ["empty_output"]
    verifier_decision = _verifier_decision(parsed, predeclared, parse_errors=parse_errors)
    routing_decision = _routing_decision(predeclared)
    return {
        "artifact_kind": "gan2026_selective_verifier_live_row",
        "source_row_index": int(predeclared["source_row_index"]),
        "split": predeclared.get("split", "validation"),
        "split_manifest": predeclared.get("split_manifest", "gan2026_split_v1"),
        "hidden_families": list(predeclared.get("hidden_families") or []),
        "model": model,
        "prompt_version": PROMPT_VERSION,
        "call_status": call_status,
        "call_errors": call_errors,
        "latency_seconds": latency_seconds,
        "usage": usage,
        "raw_model_output": raw_output,
        "parse_errors": parse_errors,
        "parsed_verifier_output": parsed.model_dump(mode="json") if parsed else None,
        "verifier_recommendation": parsed.recommendation if parsed else "parse_error",
        "routing_decision": routing_decision,
        "verifier_decision": verifier_decision,
        "verifier_vs_routing": _delta(verifier_decision, routing_decision),
        "development_accounting": predeclared["development_accounting"],
        "claim_boundary": "validation_development_selective_verifier_live",
    }


def _parse_output(raw_output: str) -> tuple[VerifierOutput | None, list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
        parsed = VerifierOutput.model_validate(payload)
    except (json.JSONDecodeError, ValidationError, ValueError) as exc:
        return None, [f"{type(exc).__name__}: {exc}"]
    errors = []
    if parsed.recommendation not in ALLOWED_RECOMMENDATIONS:
        errors.append(f"unsupported_recommendation:{parsed.recommendation}")
    if parsed.confidence and parsed.confidence not in {"low", "medium", "high"}:
        errors.append(f"unsupported_confidence:{parsed.confidence}")
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


def _call_openai_responses(
    system_prompt: str,
    model_input: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> tuple[str, dict[str, Any], float]:
    if model.startswith("ollama_chat/"):
        return _call_ollama_chat(
            system_prompt,
            model_input,
            model=model,
            max_tokens=max_tokens,
        )
    api_key = os.environ["OPENAI_API_KEY"].strip()
    body = {
        "model": model.removeprefix("openai/"),
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(model_input, ensure_ascii=False, sort_keys=True),
                    }
                ],
            },
        ],
        "temperature": 0,
        "max_output_tokens": max_tokens,
    }
    started = time.monotonic()
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"OpenAI HTTP {exc.code}: {detail[:500]}") from exc
    latency = time.monotonic() - started
    texts = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if text:
                texts.append(str(text))
    output_text = str(payload.get("output_text") or "\n".join(texts)).strip()
    if not output_text:
        raise RuntimeError("OpenAI response contained no output text")
    return output_text, dict(payload.get("usage") or {}), latency


def _call_ollama_chat(
    system_prompt: str,
    model_input: Mapping[str, Any],
    *,
    model: str,
    max_tokens: int,
) -> tuple[str, dict[str, Any], float]:
    api_base = os.environ.get("GAN2026_API_BASE") or os.environ.get("OPENAI_API_BASE")
    api_base = (api_base or "http://localhost:11434").rstrip("/")
    if api_base.endswith("/v1"):
        api_base = api_base[: -len("/v1")]
    body = {
        "model": model.removeprefix("ollama_chat/"),
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(model_input, ensure_ascii=False, sort_keys=True),
            },
        ],
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
            "num_predict": max_tokens,
        },
    }
    started = time.monotonic()
    request = urllib.request.Request(
        f"{api_base}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail[:500]}") from exc
    latency = time.monotonic() - started
    output_text = str((payload.get("message") or {}).get("content") or "").strip()
    if not output_text:
        raise RuntimeError("Ollama response contained no assistant content")
    usage = {
        key: payload[key]
        for key in [
            "total_duration",
            "load_duration",
            "prompt_eval_count",
            "prompt_eval_duration",
            "eval_count",
            "eval_duration",
        ]
        if key in payload
    }
    return output_text, usage, latency


def _routing_decision(predeclared: Mapping[str, Any]) -> dict[str, Any]:
    accounting = predeclared["development_accounting"]
    action = str(accounting.get("routing_policy_action") or "")
    label = accounting.get("routing_policy_label")
    scorable = action != "route_review" and bool(label)
    return {
        "policy_action": action,
        "action": "abstain_review" if action == "route_review" else "render",
        "label": label,
        "scorable": scorable,
        "purist_correct": _purist_correct(label, accounting["gold_label"]) if scorable else None,
        "pragmatic_correct": _pragmatic_correct(label, accounting["gold_label"])
        if scorable
        else None,
    }


def _verifier_decision(
    parsed: VerifierOutput | None,
    predeclared: Mapping[str, Any],
    *,
    parse_errors: Sequence[str],
) -> dict[str, Any]:
    accounting = predeclared["development_accounting"]
    if parsed is None or parse_errors:
        return _decision("parse_error", None, False, accounting["gold_label"], False)
    evidence_ok = _evidence_quotes_exact(parsed, predeclared)
    recommendation = parsed.recommendation
    if recommendation == "abstain_review":
        return _decision("abstain_review", None, False, accounting["gold_label"], evidence_ok)
    if recommendation == "render_as_unknown":
        return _decision("render", "unknown", True, accounting["gold_label"], evidence_ok)
    if recommendation in {"render_as_selected_state", "choose_listed_competing_hypothesis"}:
        label = _normalized_label(parsed.recommended_label)
        return _decision(
            "render",
            label,
            label is not None,
            accounting["gold_label"],
            evidence_ok,
        )
    return _decision("unsupported", None, False, accounting["gold_label"], evidence_ok)


def _decision(
    action: str,
    label: str | None,
    scorable: bool,
    gold_label: str,
    all_evidence_quotes_exact: bool,
) -> dict[str, Any]:
    return {
        "action": action,
        "label": label,
        "scorable": scorable,
        "purist_correct": _purist_correct(label, gold_label) if scorable else None,
        "pragmatic_correct": _pragmatic_correct(label, gold_label) if scorable else None,
        "all_evidence_quotes_exact": all_evidence_quotes_exact,
    }


def _delta(
    verifier_decision: Mapping[str, Any],
    routing_decision: Mapping[str, Any],
) -> dict[str, Any]:
    changed = (
        verifier_decision["action"] != routing_decision["action"]
        or verifier_decision.get("label") != routing_decision.get("label")
    )
    routing_correct = routing_decision.get("purist_correct")
    verifier_correct = verifier_decision.get("purist_correct")
    if not changed:
        delta = "unchanged"
    elif verifier_decision["action"] == "abstain_review":
        delta = "C_to_review" if routing_correct is True else "W_to_review"
    elif routing_correct is True and verifier_correct is False:
        delta = "C_to_W"
    elif routing_correct is False and verifier_correct is True:
        delta = "W_to_C"
    elif routing_correct is True and verifier_correct is True:
        delta = "C_to_C_changed"
    else:
        delta = "W_to_W_changed"
    return {
        "decision_changed": changed,
        "delta": delta,
    }


def _normalized_label(label: str | None) -> str | None:
    if not label:
        return None
    try:
        return label_to_frequency_record(label).normalized_label
    except ValueError:
        return None


def _purist_correct(predicted_label: str | None, gold_label: str) -> bool:
    if not predicted_label:
        return False
    predicted = label_to_frequency_record(predicted_label)
    gold = label_to_frequency_record(gold_label)
    return map_purist(predicted.monthly_frequency) == map_purist(gold.monthly_frequency)


def _pragmatic_correct(predicted_label: str | None, gold_label: str) -> bool:
    if not predicted_label:
        return False
    predicted = label_to_frequency_record(predicted_label)
    gold = label_to_frequency_record(gold_label)
    return map_pragmatic(predicted.monthly_frequency) == map_pragmatic(gold.monthly_frequency)


def _evidence_quotes_exact(
    parsed: VerifierOutput,
    predeclared: Mapping[str, Any],
) -> bool:
    if not parsed.evidence_quotes:
        return False
    model_input = predeclared["verifier_model_input"]
    allowed_texts = [
        str(model_input.get("proposed_evidence") or ""),
        str((model_input.get("selected_state") or {}).get("selected_evidence") or ""),
        *[str(item) for item in model_input.get("provided_competing_hypotheses") or []],
    ]
    return all(
        any(quote and quote in allowed_text for allowed_text in allowed_texts)
        for quote in parsed.evidence_quotes
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


def _interpretation(delta_counts: Counter[str]) -> str:
    if delta_counts["C_to_W"]:
        return (
            "Do not promote the verifier to prediction-bearing use: it introduced "
            f"{delta_counts['C_to_W']} C->W regression(s) versus the routing policy."
        )
    if delta_counts["W_to_C"]:
        return (
            "Verifier is a promotion candidate for this slice: it produced W->C "
            "changes without C->W regressions, subject to evidence and abstention review."
        )
    return "Verifier remains diagnostic: no useful changed-decision gain was observed."


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predeclaration-jsonl-path", type=Path, default=DEFAULT_PREDECLARATION_JSONL_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--model", default="openai/gpt-4.1-mini")
    parser.add_argument("--max-tokens", type=int, default=1200)
    args = parser.parse_args(argv)

    predeclared_rows = load_jsonl_rows(args.predeclaration_jsonl_path)
    rows, metadata = run_experiment(
        predeclared_rows,
        model=args.model,
        max_tokens=args.max_tokens,
    )
    metadata = {
        **metadata,
        "source_artifact": str(args.predeclaration_jsonl_path),
    }
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
