"""Build the audited v0.8 dev750 reference and rescore saved R8 responses.

This reads no holdout data, makes no model calls, and never edits the v0.7
reference, R8 responses, or previous scores.

    .venv/bin/python scripts/benchmarks/score_findings_v08.py
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_v08 as v08,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r8 as r8,
)
from scripts.benchmarks.run_r8 import load_reference, records
from scripts.benchmarks.score_finding_purist import R8_OUT, R8_RUN, REFERENCE, r8_predictions

SCHEMA_V07 = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_7/annotation.schema.json"
)
SCHEMA_V08 = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8/dev750_r8_saved")
RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8/dev750_r8_saved/score.json"
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, payload: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as output:
        for row in payload:
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def schema() -> dict[str, Any]:
    data = json.loads(SCHEMA_V07.read_text())
    data["$defs"]["QualitativeFrequency"]["properties"]["frequency"]["enum"] = [
        "occasional",
        "frequent",
    ]
    data["properties"]["guide_version"]["const"] = v08.GUIDE_VERSION
    data["description"] = (
        "Seizure-finding annotation v0.8 wrapper. Structural validation only; "
        "the v0.8 guide and source-audit rules define the annotation unit."
    )
    data["title"] = "Annotation v0.8"
    Draft202012Validator.check_schema(data)
    return data


def aggregate(scores: list[dict[str, Any]]) -> dict[str, Any]:
    tp = sum(row["tp"] for row in scores)
    fp = sum(row["fp"] for row in scores)
    fn = sum(row["fn"] for row in scores)
    usable = sum(bool(row["usable"]) for row in scores)
    return {
        "matching_version": v08.VERSION,
        "letters": len(scores),
        "usable_letters": usable,
        "unusable_letters": len(scores) - usable,
        "reference_findings": sum(row["reference"] for row in scores),
        "predicted_findings_usable": sum(row["predicted"] or 0 for row in scores),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
        "exact_inventory": sum(row["usable"] and row["fp"] == row["fn"] == 0 for row in scores),
    }


def main() -> None:
    selected = records("dev750")
    if len(selected) != 750:
        raise ValueError("Expected 750 development letters")
    refs = load_reference(REFERENCE, selected)
    predicted = r8_predictions(selected)
    diagnostics = {
        row["source_row_index"]: row
        for row in json.loads((R8_RUN / "diagnostics.json").read_text())
    }
    if set(diagnostics) != set(refs):
        raise ValueError("R8 answer diagnostics do not cover the development manifest")
    baseline = json.loads(R8_OUT.read_text())
    if baseline["finding_purist"]["tp"] != 1226 or baseline["reference_sha256"] != study.old.digest(
        REFERENCE.read_bytes()
    ):
        raise ValueError("Frozen v0.7 Finding Purist result does not match the source reference")
    v08_schema = schema()
    validator = Draft202012Validator(v08_schema)
    reference_rows: list[dict[str, Any]] = []
    audit_rows: list[dict[str, Any]] = []
    review_rows: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    actions: Counter[str] = Counter()
    for record in selected:
        index = record.source_row_index
        source = refs[index]
        if source["annotation_state"] != "complete":
            raise ValueError(f"Incomplete reference on row {index}")
        note = record.note_text
        gold, gold_actions = v08.project(note, source["findings"], source_row_index=index)
        raw_prediction = predicted[index]
        prediction, prediction_actions = v08.project(
            note, raw_prediction or [], source_row_index=index
        )
        if v08.project(note, gold, source_row_index=index)[0] != gold:
            raise ValueError(f"Reference conversion is not idempotent on row {index}")
        if v08.project(note, prediction, source_row_index=index)[0] != prediction:
            raise ValueError(f"Prediction projection is not idempotent on row {index}")
        if len({f["id"] for f in gold}) != len(gold):
            raise ValueError(f"Duplicate reference finding id on row {index}")
        if any(f["evidence"] not in note for f in gold):
            raise ValueError(f"Reference evidence absent from source on row {index}")
        migrated = copy.deepcopy(source)
        migrated["guide_version"] = v08.GUIDE_VERSION
        migrated["findings"] = gold
        validator.validate(migrated)
        reference_rows.append(migrated)
        scored = v08.score_letter(note, gold, prediction if raw_prediction is not None else None)
        scores.append(scored)
        matched_prediction = {pred_id for pred_id, _ in scored["pairs"]}
        matched_gold = {gold_id for _, gold_id in scored["pairs"]}
        review_rows.append(
            {
                "source_row_index": index,
                "source_id": source["source_id"],
                "note": note,
                "gold_answer": record.gold_label,
                "predicted_answer": diagnostics[index]["answers"]["r8_rich"],
                "answer_correct": diagnostics[index]["answer_correct"]["r8_rich"]["purist"],
                "usable": scored["usable"],
                "reference": gold,
                "predicted": prediction,
                "pairs": scored["pairs"],
                "unmatched_reference_ids": [f["id"] for f in gold if f["id"] not in matched_gold],
                "unmatched_prediction_ids": [
                    f["id"] for f in prediction if f["id"] not in matched_prediction
                ],
                "v08_tp": scored["tp"],
                "v08_fp": scored["fp"],
                "v08_fn": scored["fn"],
                "purist_tp": scored["tp"],
                "purist_fp": scored["fp"],
                "purist_fn": scored["fn"],
            }
        )
        actions.update("gold:" + action["rule"] for action in gold_actions)
        actions.update("prediction:" + action["rule"] for action in prediction_actions)
        audit_rows.append(
            {
                "source_row_index": index,
                "source_id": source["source_id"],
                "source_sha256": source["source_sha256"],
                "gold_before": len(source["findings"]),
                "gold_after": len(gold),
                "prediction_usable": raw_prediction is not None,
                "prediction_before": len(raw_prediction or []),
                "prediction_after": len(prediction),
                "gold_actions": gold_actions,
                "prediction_actions": prediction_actions,
            }
        )
    write_json(SCHEMA_V08, v08_schema)
    write_jsonl(RUN / "reference.jsonl", reference_rows)
    write_jsonl(RUN / "conversion_audit.jsonl", audit_rows)
    summary = aggregate(scores)
    write_json(
        RUN / "review_bundle.json",
        {
            "scope": "Gan synthetic dev750 only; v0.8 reference and projected saved R8 predictions",
            "matcher": v08.VERSION,
            "aggregate": summary,
            "rows": review_rows,
        },
    )
    output = {
        "version": v08.VERSION,
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": (
            f"all 750 development rows; {summary['unusable_letters']} unusable "
            "R8 responses retained"
        ),
        "reference_path": str(RUN / "reference.jsonl"),
        "reference_sha256": study.old.digest((RUN / "reference.jsonl").read_bytes()),
        "v07_reference_path": str(REFERENCE),
        "v07_reference_sha256": study.old.digest(REFERENCE.read_bytes()),
        "v07_baseline_score_path": str(R8_OUT),
        "v07_baseline_score_sha256": study.old.digest(R8_OUT.read_bytes()),
        "r8_requests_sha256": study.old.digest((R8_RUN / "requests.jsonl").read_bytes()),
        "r8_responses_sha256": study.old.digest((R8_RUN / "responses.jsonl").read_bytes()),
        "r8_diagnostics_sha256": study.old.digest((R8_RUN / "diagnostics.json").read_bytes()),
        "schema_path": str(SCHEMA_V08),
        "schema_sha256": study.old.digest(SCHEMA_V08.read_bytes()),
        "conversion_and_scorer_path": v08.__file__,
        "conversion_and_scorer_sha256": study.old.digest(Path(v08.__file__).read_bytes()),
        "model": study.old.MODEL,
        "prompt_version": r8.VERSION,
        "prompt_revision": r8.REVISION,
        "saved_run_condition": "r8_rich",
        "replay_mode": "saved responses; no model call",
        "repair_policy": "none; semantic v0.8 projection recorded separately",
        "actions": dict(sorted(actions.items())),
        "finding_v08": summary,
        "finding_purist_v07_baseline": {
            key: baseline["finding_purist"][key]
            for key in ("tp", "fp", "fn", "precision", "recall", "f1")
        },
        "scope": (
            "Development rescore with a changed target and scoring rule; the two scores "
            "do not estimate a model improvement or holdout generalization."
        ),
    }
    output["letters"] = [
        {
            "source_row_index": record.source_row_index,
            "usable": score["usable"],
            "reference": score["reference"],
            "predicted": score["predicted"],
            "tp": score["tp"],
            "fp": score["fp"],
            "fn": score["fn"],
            "pairs": score["pairs"],
        }
        for record, score in zip(selected, scores, strict=True)
    ]
    write_json(RESULT, output)
    print(
        json.dumps(
            {"result": str(RESULT), "finding_v08": summary, "actions": dict(actions)}, indent=2
        )
    )


if __name__ == "__main__":
    main()
