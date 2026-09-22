"""Rescore saved R7 and R8 dev750 inventories with Finding Purist.

No model call, no repair, and no test450 access. The exact matcher is scored
again beside the new rule and must reproduce the published dev750 counts.
A seizure-free companion collapses duration only as a named secondary result.

    .venv/bin/python scripts/benchmarks/score_finding_purist.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_matching_v07 as exact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_purist as purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.run_r8 import inspect, load_reference, records
from scripts.benchmarks.score_r7_findings import REFERENCE, VIEW, predictions_for

R8_RUN = Path("runs/one_shot_frequency_v2_measurements_r8/dev750_rich_only")
R7_OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r7/"
    "dev750_timeout600/finding_purist_score.json"
)
R8_OUT = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_v2_measurements_r8/"
    "dev750_rich_only/finding_purist_score.json"
)

# Published exact-matcher counts. A loader change must not silently move them.
EXPECTED_EXACT = {
    "r7": {"tp": 742, "fp": 1455, "fn": 1355, "usable_letters": 709, "exact_inventory": 75},
    "r8": {"tp": 1032, "fp": 760, "fn": 1065, "usable_letters": 714, "exact_inventory": 185},
}


def ratio(num: int, den: int) -> float | str:
    return num / den if den else "not estimable"


def compact(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    kept = []
    for row in rows:
        kept.append(
            {
                "source_row_index": row["source_row_index"],
                "usable": row["usable"],
                "reference": row["reference"],
                "predicted": row["predicted"],
                "exact_tp": row["exact"]["tp"],
                "purist_tp": row["purist"]["tp"],
                "purist_fp": row["purist"]["fp"],
                "purist_fn": row["purist"]["fn"],
                "collapsed_tp": row["collapsed"]["tp"],
                "purist_pairs": row["purist"]["pairs"],
            }
        )
    return kept


def added_class(pred: dict[str, Any], ref: dict[str, Any], note: str) -> str:
    """Why a Finding Purist pair is not an exact match. Exact pairs return ``exact``."""
    diffs = exact.attribute_diffs(pred, ref, note)
    if not diffs:
        return "exact"
    left, right = purist.purist_band(pred), purist.purist_band(ref)
    qualitative = purist.qualitative_value(pred)
    if left is not None and left == right:
        kind = "same_band"
    elif qualitative and qualitative == purist.qualitative_value(ref):
        kind = "qualitative"
    elif (pred.get("measurement") or {}).get("type") == "seizure_free":
        kind = "seizure_free_anchor"
    elif (pred.get("measurement") or {}).get("type") == "last_seizure":
        kind = "last_seizure"
    else:
        kind = "other"
    return kind + ":" + "+".join(diffs)


def score_rows(
    selected: list[Any],
    refs: dict[int, dict[str, Any]],
    predictions: dict[int, list[dict[str, Any]] | None],
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], dict[str, Any]]:
    exact_letters = []
    purist_letters = []
    collapsed_letters = []
    rows = []
    classes: Counter[str] = Counter()
    for record in selected:
        ref = refs[record.source_row_index]
        if ref["annotation_state"] != "complete":
            raise ValueError(f"Row {record.source_row_index} is not a complete reference")
        predicted = predictions[record.source_row_index]
        note = record.note_text
        findings = ref["findings"]
        exact_score = exact.score_letter(note, findings, predicted)
        purist_score = purist.score_letter(note, findings, predicted)
        collapsed_score = purist.score_letter(
            note, findings, predicted, collapse_seizure_free=True
        )
        if purist_score["tp"] < exact_score["tp"] or collapsed_score["tp"] < purist_score["tp"]:
            raise ValueError(f"Row {record.source_row_index} lost a match under a weaker rule")
        predicted_by_id = {item.get("id"): item for item in predicted or []}
        reference_by_id = {item.get("id"): item for item in findings}
        for pred_id, ref_id in purist_score["pairs"]:
            classes[
                added_class(predicted_by_id[pred_id], reference_by_id[ref_id], note)
            ] += 1
        exact_letters.append(exact_score)
        purist_letters.append(purist_score)
        collapsed_letters.append(collapsed_score)
        rows.append(
            {
                "source_row_index": record.source_row_index,
                "usable": purist_score["usable"],
                "reference": purist_score["reference"],
                "predicted": purist_score["predicted"],
                "exact": exact_score,
                "purist": purist_score,
                "collapsed": collapsed_score,
            }
        )
    return (
        rows,
        exact.aggregate(exact_letters),
        purist.aggregate(purist_letters),
        purist.aggregate(collapsed_letters, collapse_seizure_free=True),
        dict(classes),
    )


def check_exact(name: str, summary: dict[str, Any]) -> None:
    expected = EXPECTED_EXACT[name]
    got = {key: summary[key] for key in expected}
    if got != expected:
        raise ValueError(f"{name} exact score changed: expected {expected}, got {got}")


def r7_predictions(selected: list[Any]) -> dict[int, list[dict[str, Any]] | None]:
    diagnostics = json.loads((VIEW / "diagnostics.json").read_text())
    by_index = {row["source_row_index"]: row for row in diagnostics}
    if set(by_index) != {record.source_row_index for record in selected}:
        raise ValueError("R7 mixed-view coverage is not the dev750 manifest")
    return {index: predictions_for(row) for index, row in by_index.items()}


def r8_predictions(selected: list[Any]) -> dict[int, list[dict[str, Any]] | None]:
    responses = {row["request_id"]: row for row in study.old.read_lines(R8_RUN / "responses.jsonl")}
    jobs = {row["source_row_index"]: row for row in study.old.read_lines(R8_RUN / "requests.jsonl")}
    if set(jobs) != {record.source_row_index for record in selected}:
        raise ValueError("R8 rich coverage is not the dev750 manifest")
    predicted: dict[int, list[dict[str, Any]] | None] = {}
    for record in selected:
        saved = responses[jobs[record.source_row_index]["request_id"]]
        content, finish = study.old.response_content(saved.get("response"))
        checked = inspect(content, finish, record, "r8_rich")
        predicted[record.source_row_index] = (
            checked["findings"] if checked["record_valid"] else None
        )
    return predicted


def report(
    name: str,
    rows: list[dict[str, Any]],
    exact_summary: dict[str, Any],
    purist_summary: dict[str, Any],
    collapsed_summary: dict[str, Any],
    classes: dict[str, int],
) -> dict[str, Any]:
    usable = [row for row in rows if row["usable"]]
    purist_tp = sum(row["purist"]["tp"] for row in usable)
    purist_fn = sum(row["purist"]["fn"] for row in usable)
    return {
        "version": "finding_purist_dev750_v1",
        "run": name,
        "dataset": "Gan 2026 synthetic",
        "split": "dev750",
        "row_policy": "all 750 development rows; complete v0.7 references; failures retained",
        "n_letters": 750,
        "n_reference_findings": sum(row["reference"] for row in rows),
        "repair_policy": "none",
        "replay_mode": "saved responses; no model call",
        "reference_path": str(REFERENCE),
        "reference_sha256": study.old.digest(REFERENCE.read_bytes()),
        "exact_matcher": exact.MATCHING_VERSION,
        "exact_matcher_sha256": study.old.digest(Path(exact.__file__).read_bytes()),
        "purist_matcher": purist.MATCHING_VERSION,
        "purist_matcher_sha256": study.old.digest(Path(purist.__file__).read_bytes()),
        "scope": (
            "Synthetic development inventory rescore. Not clinical validation, "
            "not a holdout result, and not a new model run."
        ),
        "exact": exact_summary,
        "finding_purist": purist_summary,
        "purist_pair_classes": classes,
        "seizure_free_collapsed_companion": {
            "note": (
                "Same rule, except every seizure-free pair with overlapping evidence, "
                "an equivalent event and the same timing matches. This is not the "
                "inventory endpoint."
            ),
            **collapsed_summary,
        },
        "purist_recall_on_usable_inventories": ratio(
            purist_tp, purist_tp + purist_fn
        ),
        "letters": compact(rows),
    }


def write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")


def headline(payload: dict[str, Any]) -> dict[str, Any]:
    purist_summary = payload["finding_purist"]
    exact_summary = payload["exact"]
    collapsed = payload["seizure_free_collapsed_companion"]
    return {
        "run": payload["run"],
        "exact_tp": exact_summary["tp"],
        "purist_tp": purist_summary["tp"],
        "purist_fp": purist_summary["fp"],
        "purist_fn": purist_summary["fn"],
        "purist_precision": purist_summary["precision"],
        "purist_recall": purist_summary["recall"],
        "purist_f1": purist_summary["f1"],
        "purist_exact_inventory": purist_summary["exact_inventory"],
        "purist_empty_state_correct": purist_summary["empty_state_correct"],
        "usable": purist_summary["usable_letters"],
        "collapsed_tp": collapsed["tp"],
        "recall_on_usable": payload["purist_recall_on_usable_inventories"],
        "pair_classes": payload["purist_pair_classes"],
    }


def main() -> None:
    if not REFERENCE.is_file():
        raise ValueError("Reviewed dev750 reference is not available")
    selected = records("dev750")
    refs = load_reference(REFERENCE, selected)
    outputs = {}
    for name, predicted, path in (
        ("r7", r7_predictions(selected), R7_OUT),
        ("r8", r8_predictions(selected), R8_OUT),
    ):
        rows, exact_summary, purist_summary, collapsed_summary, classes = score_rows(
            selected, refs, predicted
        )
        check_exact(name, exact_summary)
        if sum(classes.values()) != purist_summary["tp"]:
            raise ValueError(f"{name} pair classes do not cover Finding Purist matches")
        payload = report(
            name, rows, exact_summary, purist_summary, collapsed_summary, classes
        )
        write(path, payload)
        outputs[name] = headline(payload)
    print(json.dumps(outputs, indent=2))


if __name__ == "__main__":
    main()
