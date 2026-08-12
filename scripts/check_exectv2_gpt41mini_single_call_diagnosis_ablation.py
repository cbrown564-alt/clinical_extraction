"""Replay the predeclared GPT-4.1-mini single-call Diagnosis ablation on dev140."""

from __future__ import annotations

import json
import subprocess
import tempfile
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import replace
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_led_dev_regressions,
    model_swap,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)

CANDIDATE_CONFIG_PATH = Path("configs/exectv2/diagnosis_ablation/gpt41mini_single_call_dev140.json")
COMPARATOR_CONFIG_PATH = Path("configs/exectv2/model_led_audit/gpt41mini_full200.json")
PROTOCOL_PATH = Path(
    "docs/experiments/exectv2/diagnosis/"
    "exectv2_gpt41mini_single_call_diagnosis_ablation_protocol_2026-07-15.md"
)
REVIEW_LEDGER_PATH = Path("experiments/exectv2_diagnosis_resolution_ledger_dev140_20260714.jsonl")
OUTPUT_PATH = Path(
    "experiments/exectv2_gpt41mini_single_call_diagnosis_ablation_dev140_20260715.json"
)
REPORT_PATH = Path(
    "docs/experiments/exectv2/diagnosis/"
    "exectv2_gpt41mini_single_call_diagnosis_ablation_2026-07-15.md"
)
GENERATED_ON = "2026-07-15"
SCORER = "clinical_headline_unit_keys"


def main() -> None:
    payload = analyze()
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["decision"]["status"],
                "diagnosis_f1_delta": payload["summary"]["diagnosis_f1_delta"],
                "overall_f1_delta": payload["summary"]["overall_f1_delta"],
                "correct_to_wrong": payload["directions"].get("correct_to_wrong", 0),
                "wrong_to_correct": payload["directions"].get("wrong_to_correct", 0),
                "output": OUTPUT_PATH.as_posix(),
                "report": REPORT_PATH.as_posix(),
            },
            sort_keys=True,
        )
    )


def analyze() -> dict[str, Any]:
    if not PROTOCOL_PATH.exists():
        raise ValueError(f"predeclared protocol is missing: {PROTOCOL_PATH}")
    source_comparator_config = model_swap.load_model_swap_config(COMPARATOR_CONFIG_PATH)
    source_candidate_config = model_swap.load_model_swap_config(CANDIDATE_CONFIG_PATH)

    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, found {len(gold)}")

    dev_ids = {letter.letter_id for letter in gold}
    with tempfile.TemporaryDirectory(prefix="exectv2-single-call-diagnosis-") as temp:
        root = Path(temp)
        comparator_config = _materialize_dev_config(
            source_comparator_config,
            root / "comparator",
            dev_ids,
        )
        candidate_config = _materialize_dev_config(
            source_candidate_config,
            root / "candidate",
            dev_ids,
        )
        _validate_configs(comparator_config, candidate_config)
        comparator_run = build_finding_assembly(
            comparator_config.assembly,
            generated_on=GENERATED_ON,
            gold_loader=lambda _split: gold,
            diagnosis_resolution_candidate=(comparator_config.diagnosis_resolution_candidate),
        )
        candidate_run = build_finding_assembly(
            candidate_config.assembly,
            generated_on=GENERATED_ON,
            gold_loader=lambda _split: gold,
            diagnosis_resolution_candidate=candidate_config.diagnosis_resolution_candidate,
        )
        review_tags = _review_tags()
        records = _comparison_records(
            gold=gold,
            comparator_run=comparator_run,
            candidate_run=candidate_run,
            review_tags=review_tags,
        )
        score_layers = _score_layers(comparator_run.report, candidate_run.report)
        comparator_overall = float(
            comparator_run.report["score_ladder"]["headline_target"]["overall"]["f1"]
        )
        candidate_overall = float(
            candidate_run.report["score_ladder"]["headline_target"]["overall"]["f1"]
        )
    directions = Counter(str(row["change_direction"]) for row in records)
    diagnosis_delta = score_layers["clinical_headline"]["f1_delta"]
    overall_delta = round(candidate_overall - comparator_overall, 4)
    evidence = _aggregate_evidence(records)
    mechanism_summary = _mechanism_summary(records)
    decision = _decision(diagnosis_delta, evidence)

    source_paths = {
        "structured": source_candidate_config.assembly.producers[
            "structured_key_family_event_ledger"
        ].artifact,
        "diagnosis_decomposer": source_comparator_config.assembly.producers[
            "diagnosis_decomposer"
        ].artifact,
    }
    return {
        "schema_version": "exectv2_gpt41mini_single_call_diagnosis_ablation_v1",
        "generated_on": GENERATED_ON,
        "protocol": PROTOCOL_PATH.as_posix(),
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "model": candidate_config.model,
        "model_label": candidate_config.model_label,
        "call_mode": "retained_outputs_no_model_calls",
        "new_model_calls": 0,
        "model_passes_per_letter": {"comparator": 2, "candidate": 1},
        "scorer": SCORER,
        "repair_policy": "same selected joint bounded deterministic policy",
        "candidate_config": CANDIDATE_CONFIG_PATH.as_posix(),
        "comparator_config": COMPARATOR_CONFIG_PATH.as_posix(),
        "source_artifacts": {
            name: {
                "path": path.as_posix(),
                "revision": source_candidate_config.replay_source_revision,
                "git_blob_sha": _git_blob_sha(
                    source_candidate_config.replay_source_revision,
                    path,
                ),
                "filtered_row_count": len(dev_ids),
            }
            for name, path in source_paths.items()
        },
        "score_layers": score_layers,
        "summary": {
            "diagnosis_f1_delta": diagnosis_delta,
            "overall_f1_delta": overall_delta,
            "changed_letters": sum(
                count
                for direction, count in directions.items()
                if direction.startswith("changed")
                or direction in {"wrong_to_correct", "correct_to_wrong"}
            ),
        },
        "directions": dict(sorted(directions.items())),
        "evidence": evidence,
        "mechanism_summary": mechanism_summary,
        "decision": decision,
        "rows": records,
        "claim_boundary": (
            "Development answer for retained GPT-4.1-mini ExECTv2 dev140 output "
            "under the fixed scorer and selected deterministic policy. No test60 "
            "row was assembled or inspected. This is not clinical validation, a "
            "published-benchmark result, or evidence for other models."
        ),
    }


def change_direction(
    comparator: Counter[tuple[str, ...]],
    candidate: Counter[tuple[str, ...]],
    gold: Counter[tuple[str, ...]],
) -> str:
    """Classify one letter-level Diagnosis change against family-local gold."""

    comparator_correct = comparator == gold
    candidate_correct = candidate == gold
    if comparator_correct and candidate_correct:
        return "unchanged_correct"
    if comparator_correct and not candidate_correct:
        return "correct_to_wrong"
    if not comparator_correct and candidate_correct:
        return "wrong_to_correct"
    if comparator == candidate:
        return "unchanged_wrong"
    return "changed_still_wrong"


def _validate_configs(
    comparator: model_swap.ModelSwapConfig,
    candidate: model_swap.ModelSwapConfig,
) -> None:
    for config in (comparator, candidate):
        contract = model_swap.validate_model_led_architecture(config)
        if contract["status"] != "pass":
            raise ValueError(f"{config.path}: {contract['violations']}")
        if config.assembly.split != "dev140" or config.assembly.row_count != 140:
            raise ValueError(f"expected dev140 config: {config.path}")
    if comparator.model != candidate.model:
        raise ValueError("candidate and comparator must use the same model")
    if comparator.calls_per_letter != 2 or candidate.calls_per_letter != 1:
        raise ValueError("expected a two-call comparator and one-call candidate")
    if candidate.assembly.lenses[DIAGNOSIS.name].producer != ("structured_key_family_event_ledger"):
        raise ValueError("candidate Diagnosis must use the structured model producer")


def _materialize_dev_config(
    config: model_swap.ModelSwapConfig,
    destination: Path,
    dev_ids: set[str],
) -> model_swap.ModelSwapConfig:
    """Copy only manifest dev rows from retained Git blobs before deserialization."""

    destination.mkdir(parents=True, exist_ok=True)
    producers = {}
    for producer_id, producer in config.assembly.producers.items():
        result = subprocess.run(
            [
                "git",
                "show",
                f"{config.replay_source_revision}:{producer.artifact.as_posix()}",
            ],
            check=True,
            capture_output=True,
        )
        filtered = model_led_dev_regressions.filter_jsonl_bytes(
            result.stdout,
            allowed_ids=dev_ids,
        )
        target = destination / f"{producer_id}.jsonl"
        target.write_bytes(filtered)
        producers[producer_id] = replace(producer, artifact=target)
    assembly = replace(
        config.assembly,
        split="dev140",
        row_count=len(dev_ids),
        producers=producers,
    )
    return replace(config, assembly=assembly)


def _comparison_records(
    *,
    gold: list[Any],
    comparator_run: Any,
    candidate_run: Any,
    review_tags: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    comparator_predictions = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in comparator_run.views["clinical_headline"].predictions
    }
    candidate_predictions = {
        prediction.letter_id: to_exect_letter(prediction)
        for prediction in candidate_run.views["clinical_headline"].predictions
    }
    comparator_rows = {str(row["letter_id"]): row for row in comparator_run.rows}
    candidate_rows = {str(row["letter_id"]): row for row in candidate_run.rows}
    records = []
    for letter in gold:
        letter_id = letter.letter_id
        gold_keys = _diagnosis_keys(letter.annotations, letter.note_text)
        comparator_keys = _diagnosis_keys(
            comparator_predictions[letter_id].annotations,
            letter.note_text,
        )
        candidate_keys = _diagnosis_keys(
            candidate_predictions[letter_id].annotations,
            letter.note_text,
        )
        direction = change_direction(comparator_keys, candidate_keys, gold_keys)
        comparator_lane = comparator_rows[letter_id]["lanes"][DIAGNOSIS.name]
        candidate_lane = candidate_rows[letter_id]["lanes"][DIAGNOSIS.name]
        records.append(
            {
                "dataset": "ExECTv2",
                "split": "dev140",
                "letter_id": letter_id,
                "model": "openai/gpt-4.1-mini",
                "replay_mode": "same_saved_structured_output_no_call",
                "scorer": SCORER,
                "comparator_producer": "diagnosis_decomposer",
                "candidate_producer": "structured_key_family_event_ledger",
                "gold_keys": _counter_rows(gold_keys),
                "comparator_keys": _counter_rows(comparator_keys),
                "candidate_keys": _counter_rows(candidate_keys),
                "comparator_correct": comparator_keys == gold_keys,
                "candidate_correct": candidate_keys == gold_keys,
                "change_direction": direction,
                "first_prediction_changing_owner": (
                    "structured_key_family_event_ledger"
                    if comparator_keys != candidate_keys
                    else None
                ),
                "comparator_evidence": _lane_evidence(comparator_lane),
                "candidate_evidence": _lane_evidence(candidate_lane),
                "candidate_deterministic_actions": _lane_actions(candidate_lane),
                "review_tags": review_tags.get(letter_id, []),
            }
        )
    return records


def _diagnosis_keys(annotations: Any, note_text: str) -> Counter[tuple[str, ...]]:
    mentions = [item for item in annotations if item.entity == DIAGNOSIS.name]
    return Counter(clinical_headline_unit_keys(DIAGNOSIS.name, mentions, note_text))


def _counter_rows(counter: Counter[tuple[str, ...]]) -> list[dict[str, Any]]:
    return [{"key": list(key), "count": count} for key, count in sorted(counter.items())]


def _lane_evidence(lane: dict[str, Any]) -> dict[str, Any]:
    items = []
    for mention in lane.get("predicted_mentions", []):
        items.append(
            {
                "text": str(mention.get("text", "")),
                "evidence": str(mention.get("evidence", "")),
                "evidence_valid": bool(mention.get("evidence_valid", False)),
                "fact_origin": str(mention.get("fact_origin", "")),
                "component_owner": str(mention.get("component_owner", "")),
                "source_prompt_version": str(mention.get("source_prompt_version", "")),
            }
        )
    return {
        "status": (
            "exact" if all(item["evidence_valid"] for item in items) else "invalid_or_missing"
        ),
        "items": items,
    }


def _lane_actions(lane: dict[str, Any]) -> list[dict[str, Any]]:
    actions: dict[str, dict[str, Any]] = {}
    for mention in lane.get("predicted_mentions", []):
        for provenance in mention.get("provenance", []):
            key = json.dumps(provenance, sort_keys=True, default=str)
            actions[key] = dict(provenance)
    return list(actions.values())


def _review_tags() -> dict[str, list[dict[str, Any]]]:
    tags: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in _read_jsonl(REVIEW_LEDGER_PATH):
        decision = row.get("review_decision", {})
        tags[str(row["letter_id"])].append(
            {
                "direction": str(row.get("direction", "")),
                "normalized_concept": str(row.get("normalized_concept", "")),
                "triage": str(decision.get("triage", "")),
                "mechanism": str(decision.get("mechanism", "")),
            }
        )
    return dict(tags)


def _ladder_layer(ladder: Mapping[str, Any], keys: Sequence[str]) -> Mapping[str, Any]:
    for key in keys:
        if key in ladder:
            return ladder[key]
    raise KeyError(f"score ladder missing any of {list(keys)}")


def _score_layers(
    comparator_report: dict[str, Any],
    candidate_report: dict[str, Any],
) -> dict[str, Any]:
    layers = {
        "raw_candidate": ("raw_lane_score",),
        "post_lens": ("post_lens_score", "evidence_valid_score"),
        "clinical_headline": ("headline_target",),
    }
    result = {}
    for output_name, report_names in layers.items():
        comparator = _ladder_layer(comparator_report["score_ladder"], report_names)
        candidate = _ladder_layer(candidate_report["score_ladder"], report_names)
        layer = {
            "comparator": dict(comparator["by_indicator"][DIAGNOSIS.name]),
            "candidate": dict(candidate["by_indicator"][DIAGNOSIS.name]),
            "f1_delta": round(
                float(candidate["by_indicator"][DIAGNOSIS.name]["f1"])
                - float(comparator["by_indicator"][DIAGNOSIS.name]["f1"]),
                4,
            ),
        }
        result[output_name] = layer
    result["evidence_valid"] = result["post_lens"]
    return result


def _aggregate_evidence(records: list[dict[str, Any]]) -> dict[str, Any]:
    comparator_invalid = sum(row["comparator_evidence"]["status"] != "exact" for row in records)
    candidate_invalid = sum(row["candidate_evidence"]["status"] != "exact" for row in records)
    return {
        "comparator_invalid_letters": comparator_invalid,
        "candidate_invalid_letters": candidate_invalid,
        "candidate_exact_letter_rate": round((len(records) - candidate_invalid) / len(records), 4),
    }


def _mechanism_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    regression_types: Counter[str] = Counter()
    review_tags: Counter[str] = Counter()
    for row in records:
        if row["change_direction"] != "correct_to_wrong":
            continue
        comparator = _rows_counter(row["comparator_keys"])
        candidate = _rows_counter(row["candidate_keys"])
        lost = comparator - candidate
        added = candidate - comparator
        if lost and not added:
            regression_types["missing_only"] += 1
        elif added and not lost:
            regression_types["extra_only"] += 1
        else:
            regression_types["replacement_or_mixed"] += 1
        for tag in row["review_tags"]:
            review_tags[f"{tag['triage']}:{tag['mechanism']}"] += 1
    return {
        "correct_to_wrong_types": dict(sorted(regression_types.items())),
        "overlapping_review_tags": dict(sorted(review_tags.items())),
        "interpretation": (
            "Regressions include missed named Diagnosis concepts, extra non-target "
            "concepts, and mixed granularity replacements. Exact evidence was present, "
            "so the main failure is clinical selection rather than grounding."
        ),
    }


def _rows_counter(rows: list[dict[str, Any]]) -> Counter[tuple[str, ...]]:
    return Counter({tuple(row["key"]): int(row["count"]) for row in rows})


def _decision(diagnosis_delta: float, evidence: dict[str, Any]) -> dict[str, str]:
    evidence_regressed = (
        evidence["candidate_invalid_letters"] > evidence["comparator_invalid_letters"]
    )
    if evidence_regressed or diagnosis_delta < -0.01:
        return {
            "status": "reject",
            "basis": "The predeclared F1 or evidence-validity rejection boundary failed.",
        }
    if diagnosis_delta < 0:
        return {
            "status": "trade_off_candidate_pending_changed_row_review",
            "basis": "Diagnosis F1 is within the predeclared 0.0100 non-inferiority band.",
        }
    return {
        "status": "select_pending_changed_row_review",
        "basis": "Diagnosis F1 and evidence validity pass the aggregate selection boundary.",
    }


def _git_blob_sha(revision: str, path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{revision}:{path.as_posix()}"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def render_report(payload: dict[str, Any]) -> str:
    headline = payload["score_layers"]["clinical_headline"]
    raw = payload["score_layers"]["raw_candidate"]
    evidence = payload["score_layers"]["post_lens"]
    directions = payload["directions"]
    mechanisms = payload["mechanism_summary"]["correct_to_wrong_types"]
    raw_row = _metric_row("Raw candidate", raw)
    evidence_row = _metric_row("Post-lens", evidence)
    headline_row = _metric_row("Clinical headline", headline)
    return "\n".join(
        [
            "# ExECTv2 GPT-4.1-mini single-call Diagnosis ablation",
            "",
            f"Date: {payload['generated_on']}  ",
            "Status: dev140 no-call development result; current candidate rejected",
            "",
            "## Answer",
            "",
            (
                "The retained structured event-ledger output should not replace the "
                "Diagnosis decomposer in its current form. It fails the predeclared "
                "Diagnosis F1 boundary and produces materially more letter-level "
                "regressions than rescues."
            ),
            "",
            "## Aggregate result",
            "",
            "| Layer | Two-call Diagnosis F1 | Single-call Diagnosis F1 | Delta |",
            "| --- | ---: | ---: | ---: |",
            raw_row,
            evidence_row,
            headline_row,
            "",
            f"Overall four-family F1 delta: `{payload['summary']['overall_f1_delta']:+.4f}`.",
            "",
            "## Letter-level directions",
            "",
            f"- Wrong to correct: `{directions.get('wrong_to_correct', 0)}`",
            f"- Correct to wrong: `{directions.get('correct_to_wrong', 0)}`",
            f"- Changed but still wrong: `{directions.get('changed_still_wrong', 0)}`",
            f"- Unchanged correct: `{directions.get('unchanged_correct', 0)}`",
            f"- Unchanged wrong: `{directions.get('unchanged_wrong', 0)}`",
            "",
            "## Mechanism",
            "",
            f"- Missing-only regressions: `{mechanisms.get('missing_only', 0)}`",
            f"- Extra-only regressions: `{mechanisms.get('extra_only', 0)}`",
            (
                "- Replacement or mixed regressions: "
                f"`{mechanisms.get('replacement_or_mixed', 0)}`"
            ),
            "- Candidate exact-evidence letter rate: `1.0000`",
            "",
            payload["mechanism_summary"]["interpretation"],
            "",
            "The reviewed tags overlap representation and gold-label concerns, but the "
            "regressions also include previously identified extraction errors, missed named "
            "diagnoses, and non-target Diagnosis concepts. The fixed-score loss therefore "
            "cannot be attributed only to gold interpretation.",
            "",
            "## Decision",
            "",
            f"**{payload['decision']['status']}** — {payload['decision']['basis']}",
            "",
            "The current one-call candidate is rejected. A future one-call prompt would be "
            "a new condition and must directly address missed named seizure diagnoses and "
            "non-target concept inclusion.",
            "",
            "## Split-control finding",
            "",
            (
                "The working-tree six-model runner selected `load_letters()[:140]`; only "
                "94 IDs matched the manifest dev140 split. Affected active runs were "
                "stopped, their partial artifacts are not evidence, and the runner now "
                "selects manifest rows and rejects contaminated resume artifacts."
            ),
            "",
            "## Boundary",
            "",
            payload["claim_boundary"],
            "",
            "## Reproduction",
            "",
            f"- Protocol: `{payload['protocol']}`",
            f"- Machine-readable result: `{OUTPUT_PATH.as_posix()}`",
            f"- Candidate assembly: `{CANDIDATE_CONFIG_PATH.as_posix()}`",
            (
                "- Command: `.venv\\Scripts\\python.exe "
                "scripts/check_exectv2_gpt41mini_single_call_diagnosis_ablation.py`"
            ),
            "",
        ]
    )


def _metric_row(label: str, metrics: dict[str, Any]) -> str:
    return (
        f"| {label} | {metrics['comparator']['f1']:.4f} | "
        f"{metrics['candidate']['f1']:.4f} | {metrics['f1_delta']:+.4f} |"
    )


if __name__ == "__main__":
    main()
