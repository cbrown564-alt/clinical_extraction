"""Run the predeclared ExECT semantic-inventory re-evaluation."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    HYBRID_METHOD,
    LLM_METHOD,
    SEMANTIC_MODEL,
    SEMANTIC_PROMPT_VERSION,
    InventoryMaterialization,
    SemanticInventoryExtractor,
    build_inventory_prompt,
    materialize_inventory,
    parse_inventory_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
    semantic_config_for,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/semantic_inventory_revaluation_luna_2026-08-16_protocol.md"
REPORT = ROOT / "docs/research/exectv2/semantic_inventory_revaluation_luna_2026-08-16.md"
DEV20_IDS = (
    "EA0002",
    "EA0004",
    "EA0005",
    "EA0006",
    "EA0007",
    "EA0008",
    "EA0009",
    "EA0010",
    "EA0011",
    "EA0012",
    "EA0015",
    "EA0016",
    "EA0047",
    "EA0074",
    "EA0093",
    "EA0120",
    "EA0131",
    "EA0133",
    "EA0154",
    "EA0158",
)
CONTROL_DEV140 = (
    ROOT / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
CONTROL_TEST60 = ROOT / "experiments/current_stack/sidecars/exect_test60/gpt56luna.jsonl"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev20", "dev140", "test60"), required=True)
    parser.add_argument("--live", action="store_true", help="Make the two candidate calls per row.")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=10)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    letters = _load_letters(args.split)
    study_dir = _study_dir(args.split)
    study_dir.mkdir(parents=True, exist_ok=True)
    if not args.overwrite and (study_dir / "comparison.json").exists():
        raise SystemExit(f"study exists; pass --overwrite: {study_dir}")
    _verify_prompt_contracts(letters[0])
    controls = _load_controls(args.split)
    started = datetime.now(UTC).isoformat()

    if not args.live:
        artifact = {
            "schema_version": "exectv2.semantic_inventory_revaluation.v1",
            "status": "prompt_checked_live_not_run",
            "protocol": PROTOCOL,
            "split": args.split,
            "row_count": len(letters),
            "model": SEMANTIC_MODEL,
            "prompt_version": SEMANTIC_PROMPT_VERSION,
            "model_calls": 0,
            "claim_boundary": "Prompt and contract check only; no candidate result.",
        }
        (study_dir / "comparison.json").write_text(
            json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(artifact, indent=2, sort_keys=True))
        return

    candidate_results, control_results, rows, operational = _run_live(
        letters,
        controls,
        split=args.split,
        api_base=args.api_base,
        timeout=args.timeout,
        progress_every=args.progress_every,
    )
    gold = letters
    summaries = {
        "control_llm": _score_method(gold, control_results[LLM_METHOD]),
        "control_llm_with_rules": _score_method(gold, control_results[HYBRID_METHOD]),
        LLM_METHOD: _score_method(gold, candidate_results[LLM_METHOD]),
        HYBRID_METHOD: _score_method(gold, candidate_results[HYBRID_METHOD]),
    }
    ablations = {}
    if args.split != "test60":
        ablations = _run_ablations(letters, rows)

    artifact: dict[str, Any] = {
        "schema_version": "exectv2.semantic_inventory_revaluation.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": args.split,
        "row_count": len(letters),
        "model": SEMANTIC_MODEL,
        "prompt_version": SEMANTIC_PROMPT_VERSION,
        "temperature": 1.0,
        "max_tokens": 2400,
        "cache": False,
        "model_calls": len(letters) * 2,
        "controls": {
            "llm": "saved_current_stack_v0.9.24_replay",
            "llm_with_rules": "saved_current_stack_v0.9.24_replay",
        },
        "methods": summaries,
        "operational": operational,
        "ablations": ablations,
        "provenance": _provenance(),
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "claim_boundary": (
            "GPT-5.6 Luna ExECT semantic-inventory development result on the named split. "
            "test60 is aggregate-only; this is not clinical validation and does not change Decision 0050."
        ),
    }
    if args.split == "test60":
        artifact["row_policy"] = (
            "locked test60 aggregate-only; no row identifiers or row-level outputs retained"
        )
    else:
        artifact["row_policy"] = "development rows permitted; test60 sealed"
        _write_development_rows(study_dir / "rows.jsonl", rows)
    out = study_dir / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.split != "test60":
        REPORT.write_text(_render_report(artifact, args.split), encoding="utf-8")
    print(json.dumps(_public_artifact_summary(artifact), indent=2, sort_keys=True))


def _load_letters(split: str) -> list[ExectLetter]:
    if split == "dev20":
        wanted = set(DEV20_IDS)
        letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in wanted]
        if [letter.letter_id for letter in letters] != sorted(DEV20_IDS):
            raise RuntimeError("the frozen dev20 sample is unavailable or changed")
        return letters
    if split == "dev140":
        letters = list(load_letters_for_split("dev"))
        if len(letters) != 140:
            raise RuntimeError(f"expected dev140, found {len(letters)}")
        return letters
    letters = list(load_letters_for_split("test"))
    if len(letters) != 59:
        raise RuntimeError(f"expected 59 loadable test60 rows under split v2, found {len(letters)}")
    return letters


def _study_dir(split: str) -> Path:
    return ROOT / f"experiments/exectv2_semantic_inventory_revaluation_luna_{split}_20260816"


def _load_controls(split: str) -> dict[str, dict[str, Any]]:
    source = CONTROL_TEST60 if split == "test60" else CONTROL_DEV140
    if not source.exists():
        raise FileNotFoundError(source)
    controls: dict[str, dict[str, Any]] = {}
    with source.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            controls[str(row["letter_id"])] = row
    return controls


def _verify_prompt_contracts(letter: ExectLetter) -> None:
    for method in (LLM_METHOD, HYBRID_METHOD):
        payload = json.loads(build_inventory_prompt(letter, method=method))
        if list(payload) != ["task", "output_schema", "family_guidance", "letter_text"]:
            raise RuntimeError(f"{method} prompt top-level order drifted")
        serialized = json.dumps(
            {key: value for key, value in payload.items() if key != "letter_text"}
        ).lower()
        if "prompt_version" in serialized or "letter_id" in serialized or "gold" in serialized:
            raise RuntimeError(f"{method} prompt leaked research metadata")
        if method == HYBRID_METHOD and "attributes" in json.dumps(payload["output_schema"]).lower():
            raise RuntimeError("hybrid model schema exposes clinical attributes")
        program = SemanticInventoryExtractor(method=method)
        messages = program.render_messages(
            prompt_input_json=build_inventory_prompt(letter, method=method)
        )
        if messages[0] != {
            "role": "system",
            "content": "Extract atomic clinical facts from the supplied clinical letter. Return the requested JSON exactly.",
        }:
            raise RuntimeError("semantic system message drifted")


def _run_live(
    letters: list[ExectLetter],
    controls: dict[str, dict[str, Any]],
    *,
    split: str,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> tuple[dict[str, list[Any]], dict[str, list[Any]], list[dict[str, Any]], dict[str, Any]]:
    candidate_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    control_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    rows: list[dict[str, Any]] = []
    operational: dict[str, dict[str, int]] = {
        method: {
            "calls": 0,
            "rows_with_blocking_parse_failure": 0,
            "parse_notes": 0,
            "facts": 0,
            "evidence_invalid": 0,
            "rows_with_forbidden_fields": 0,
            "rule_changed_facts": 0,
        }
        for method in (LLM_METHOD, HYBRID_METHOD)
    }
    extractors = {
        method: SemanticInventoryExtractor(method=method) for method in (LLM_METHOD, HYBRID_METHOD)
    }
    for method in (LLM_METHOD, HYBRID_METHOD):
        dspy.configure(
            lm=build_dspy_lm(
                SEMANTIC_MODEL,
                temperature=1.0,
                max_tokens=2400,
                cache=False,
                api_base=api_base,
                timeout=timeout,
            )
        )
        extractors[method]._configured = True

    for index, letter in enumerate(letters, start=1):
        control_llm, control_hybrid = _replay_current_controls(
            letter, controls[letter.letter_id], split
        )
        control_predictions[LLM_METHOD].append(control_llm)
        control_predictions[HYBRID_METHOD].append(control_hybrid)
        row: dict[str, Any] = {
            "letter_id": letter.letter_id,
            "split": split,
            "model": SEMANTIC_MODEL,
            "prompt_version": SEMANTIC_PROMPT_VERSION,
            "methods": {},
            "controls": {
                "llm": control_llm.model_dump(mode="json"),
                "llm_with_rules": control_hybrid.model_dump(mode="json"),
            },
        }
        for method in (LLM_METHOD, HYBRID_METHOD):
            prompt = build_inventory_prompt(letter, method=method)
            raw_output = ""
            call_error: str | None = None
            try:
                prediction = extractors[method](prompt_input_json=prompt)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover - provider behavior.
                call_error = f"{type(exc).__name__}: {exc}"
            parsed = parse_inventory_json(raw_output, method=method)
            stats = operational[method]
            stats["calls"] += 1
            stats["parse_notes"] += len(parsed.errors)
            stats["facts"] += len(parsed.record.facts) if parsed.record is not None else 0
            stats["rows_with_blocking_parse_failure"] += int(
                parsed.record is None
                or any(
                    str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
                    for error in parsed.errors
                )
            )
            stats["rows_with_forbidden_fields"] += int(bool(parsed.forbidden_fields))
            if parsed.record is None:
                materialized = _empty_materialization(letter, parsed.errors)
            else:
                materialized = materialize_inventory(letter, parsed.record, method=method)
            candidate_predictions[method].append(materialized.prediction)
            stats["evidence_invalid"] += materialized.evidence_invalid
            stats["rule_changed_facts"] += sum(
                int(trace.get("changed", False)) for trace in materialized.rule_trace
            )
            row["methods"][method] = {
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parsed.errors,
                "forbidden_model_fields": parsed.forbidden_fields,
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        if split != "test60":
            rows.append(row)
        if index % max(progress_every, 1) == 0:
            print(f"{split}: completed {index}/{len(letters)} rows", flush=True)
    return candidate_predictions, control_predictions, rows, operational


def _replay_current_controls(
    letter: ExectLetter,
    saved: dict[str, Any],
    split: str,
) -> tuple[Any, Any]:
    raw = str(saved.get("raw_output") or "")
    if not raw:
        raw = json.dumps({"clinical_events": saved.get("structured_events", [])})
    producer = structured_one_call.produce_structured_letter(
        letter,
        model="openai/gpt-5.6-luna",
        mode="replay",
        raw_output=raw,
        split=split,
        config=StructuredMethodConfig.selected(),
    )
    llm = structured_one_call.run_llm_only_letter(letter, producer).prediction
    hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer).prediction
    return llm, hybrid


def _empty_materialization(letter: ExectLetter, errors: list[str]) -> InventoryMaterialization:
    return InventoryMaterialization(
        prediction=PredictedLetter(letter_id=letter.letter_id, mentions=()),
        semantic_facts=[],
        rule_trace=[],
        warnings=[],
        evidence_invalid=0,
        parse_failures=errors,
    )


def _score_method(gold: list[ExectLetter], predictions: list[Any]) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    semantic = score_overall(
        gold,
        pred_letters,
        ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"),
        semantic_config_for,
    )
    benchmark = score_overall(
        gold,
        pred_letters,
        ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"),
        benchmark_config_for,
    )
    headline_scores = {
        "Diagnosis": score_concept_identity(gold, pred_letters, "Diagnosis").concept_only,
        "SeizureFrequency": score_frequency_state(gold, pred_letters).clinical_headline,
        "Prescription": score_prescription_components(gold, pred_letters).clinical_headline,
        "Investigations": score_investigations_components(gold, pred_letters).clinical_headline,
    }
    headline_f1 = _aggregate_f1(headline_scores.values())
    return {
        "semantic_f1": round(semantic.per_item.f1, 4),
        "semantic_family_f1": {
            family: round(score.per_item.f1, 4) for family, score in semantic.per_entity.items()
        },
        "benchmark_projection_f1": round(benchmark.per_item.f1, 4),
        "benchmark_family_f1": {
            family: round(score.per_item.f1, 4) for family, score in benchmark.per_entity.items()
        },
        "clinical_headline_f1": round(headline_f1, 4),
        "clinical_headline_family_f1": {
            family: round(score.f1, 4) for family, score in headline_scores.items()
        },
        "semantic_counts": _counts(semantic.per_item),
    }


def _aggregate_f1(scores: Iterable[Any]) -> float:
    tp = fp = fn = 0
    for score in scores:
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _counts(score: Any) -> dict[str, int]:
    return {"tp": int(score.tp), "fp": int(score.fp), "fn": int(score.fn)}


def _run_ablations(letters: list[ExectLetter], rows: list[dict[str, Any]]) -> dict[str, Any]:
    ablations: dict[str, Any] = {}
    for family in ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"):
        predictions = []
        for letter, row in zip(letters, rows, strict=True):
            raw = row["methods"][HYBRID_METHOD]["raw_output"]
            parsed = parse_inventory_json(raw, method=HYBRID_METHOD)
            if parsed.record is None:
                predictions.append(PredictedLetter(letter_id=letter.letter_id, mentions=()))
            else:
                predictions.append(
                    materialize_inventory(
                        letter,
                        parsed.record,
                        method=HYBRID_METHOD,
                        disabled_rule_families={family},
                    ).prediction
                )
        ablations[f"disable_{family}"] = _score_method(letters, predictions)
    return ablations


def _write_development_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    return {
        "git_head": commit,
        "working_tree": "dirty_before_study; pre-existing user changes preserved",
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }


def _public_artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        key: artifact[key]
        for key in (
            "status",
            "split",
            "row_count",
            "model_calls",
            "methods",
            "ablations",
            "claim_boundary",
        )
        if key in artifact
    }


def _render_report(artifact: dict[str, Any], split: str) -> str:
    methods = artifact["methods"]
    lines = [
        "# ExECT semantic inventory and hybrid re-evaluation",
        "",
        "Date: 2026-08-16  ",
        "Status: complete; GPT-5.6 Luna candidate measured",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        f"Split: `{split}` (n={artifact['row_count']})  ",
        "Model: `openai/gpt-5.6-luna`",
        "",
        "## Result",
        "",
        "| Method | semantic F1 | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, summary in methods.items():
        family = summary["clinical_headline_family_f1"]
        lines.append(
            f"| {name} | {summary['semantic_f1']:.4f} | {summary['clinical_headline_f1']:.4f} | "
            f"{family['Diagnosis']:.4f} | {family['SeizureFrequency']:.4f} | "
            f"{family['Prescription']:.4f} | {family['Investigations']:.4f} |"
        )
    lines += [
        "",
        "The development artifact retains row-level raw output, semantic facts, evidence checks, rule traces, and predictions for permitted mechanism analysis.",
        "The selected v0.9.24 / Decision 0050 result remains unchanged by this study.",
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
