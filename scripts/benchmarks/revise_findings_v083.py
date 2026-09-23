"""Owner-adjudicated v0.8.3 inventory revision over all dev750 letters.

Every semantic edit is explicit below and emitted with before/after source
evidence. The saved R8 projection, v0.8.2 reference, and locked split are never
modified. The all-letter triage is in audit_claim_representation_v082.py.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v082 as scorer
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.score_findings_v08 import aggregate, write_json, write_jsonl

BASE = Path("runs/seizure_finding_annotation_v0_8_2/dev750_r8_saved")
BASE_RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_2/dev750_r8_saved/score.json"
)
BASE_SCHEMA = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_2/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8_3/dev750_r8_saved")
RESULT = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_3/dev750_r8_saved")
SCHEMA = RESULT.parent / "annotation.schema.json"
GUIDE = "seizure_finding_annotation_v0.8.3"

# Source-checked removals after the owner selected overall diary counts, one
# additional broad absence summary, recurring cluster patterns, and the
# clinician-link boundary for uncertain symptoms. Prior v0.8.2 edits remain in
# the frozen input and are not repeated here.
REMOVE: dict[int, dict[str, str]] = {
    2822: {"f1": "qualitative restatement of the daily myoclonic-jerk rate"},
    3988: {"f3": "most-weeks summary repeats the quantified blanking-spell rate"},
    4690: {"f1": "limb twitching is not linked to an established seizure type"},
    4694: {"f2": "non-specific nocturnal restlessness lacks a seizure link"},
    5092: {"f1": "prior collapse is assessed as non-epileptic rather than seizure"},
    5995: {
        "f1": "infrequent is context for the complete diary count",
        "f2": "zero diary month is context for the aggregate interval",
        "f4": "zero diary month is context for the aggregate interval",
        "f5": "zero diary month is context for the aggregate interval",
        "f7": "three absence events are already represented by cluster size",
        "f8": "zero diary month is context for the aggregate interval",
        "f9": "zero diary month is context for the aggregate interval",
        "f10": "August convulsion is combined with February convulsion",
        "f11": "zero diary month is context for the aggregate interval",
    },
    6738: {"f2": "infrequency summary repeats the six-to-eight-week rate"},
    7093: {"f3": "uncertain nocturnal restlessness lacks defining seizure features"},
    7195: {"f4": "possible isolated brief event lacks seizure identification"},
    9190: {
        "f1": "vague occasional background is context beside dated aura absence",
        "f6": "supervisor report corroborates the February focal-event absence",
        "f7": "several-month broad summary repeats intervening-month summary",
    },
    15783: {"f4": "bed disarray and confusion only suggest unwitnessed nocturnal events"},
    16041: {"f4": "December awake count is combined with October daytime count"},
}

# Each has a recurring cadence or pattern of grouped events in its source.
# Labels that already state a cluster unit are left as they are.
RECURRING_SIZE: dict[int, tuple[str, ...]] = {
    10542: ("f2",),
    10578: ("f2",),
    10583: ("f2",),
    10594: ("f2",),
    10618: ("f2",),
    10629: ("f2",),
    15376: ("f2",),
    15404: ("f2",),
    15429: ("f1",),
    15431: ("f1",),
    15442: ("f2",),
    15470: ("f2",),
    15479: ("f1",),
    15497: ("f1",),
    15503: ("f1",),
    15513: ("f1",),
    15519: ("f1",),
    15529: ("f2",),
    15593: ("f4",),
}


def revise(row: dict[str, Any], note: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index = row["source_row_index"]
    revised = copy.deepcopy(row)
    revised["guide_version"] = GUIDE
    edits: list[dict[str, Any]] = []

    def record(finding_id: str, reason: str, before: Any, after: Any) -> None:
        edits.append(
            {
                "source_row_index": index,
                "source_id": row["source_id"],
                "source_sha256": row["source_sha256"],
                "finding_id": finding_id,
                "reason": reason,
                "before": before,
                "after": after,
            }
        )

    removed = REMOVE.get(index, {})
    by_id = {f["id"]: f for f in revised["findings"]}
    if not set(removed) <= set(by_id):
        raise ValueError(f"Missing removal ID on {index}")
    for ident, reason in removed.items():
        record(ident, reason, by_id[ident], None)
    revised["findings"] = [f for f in revised["findings"] if f["id"] not in removed]
    kept = {f["id"]: f for f in revised["findings"]}
    if index == 9190:
        specific_absence = kept["f2"]
        before = copy.deepcopy(specific_absence)
        specific_absence["event"]["type"] = "focal impaired-awareness events or convulsions"
        specific_absence["event"]["scope"] = "specific"
        record(
            "f2",
            "combined absence retains the two named event types",
            before,
            copy.deepcopy(specific_absence),
        )
    if index == 5995:
        diary = note[note.index("January 0;") : note.index("September 0.") + len("September 0.")]
        convulsions = kept["f3"]
        before = copy.deepcopy(convulsions)
        convulsions["measurement"] = {"type": "count", "count": {"type": "number", "value": 2}}
        convulsions.pop("condition", None)
        convulsions["period"] = {"time": "February to August 2025"}
        convulsions["evidence"] = diary
        record(
            "f3",
            "February and August generalised convulsions combined",
            before,
            copy.deepcopy(convulsions),
        )
        total = {
            "id": "f12",
            "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
            "measurement": {"type": "count", "count": {"type": "number", "value": 5}},
            "timing": "current",
            "period": {"time": "January to September 2025"},
            "evidence": diary,
        }
        revised["findings"].append(total)
        record(
            "f12",
            "overall individual events: two convulsions plus three absences in one cluster",
            None,
            total,
        )
    if index == 15982:
        total = {
            "id": "f3",
            "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
            "measurement": {"type": "count", "count": {"type": "number", "value": 9}},
            "timing": "current",
            "period": {"time": "June to July"},
            "evidence": kept["f1"]["evidence"],
        }
        revised["findings"].append(total)
        record("f3", "four nocturnal plus five daytime events across June and July", None, total)
    if index == 16041:
        daytime = kept["f1"]
        before = copy.deepcopy(daytime)
        daytime["measurement"]["count"]["value"] = 7
        daytime["period"] = {"time": "October and December"}
        daytime["evidence"] = kept["f2"]["evidence"]
        record(
            "f1",
            "five October daytime plus two December awake events",
            before,
            copy.deepcopy(daytime),
        )
        total = {
            "id": "f6",
            "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
            "measurement": {"type": "count", "count": {"type": "number", "value": 9}},
            "timing": "current",
            "period": {"time": "October and December"},
            "evidence": kept["f2"]["evidence"],
        }
        revised["findings"].append(total)
        record("f6", "seven daytime plus two nocturnal events in listed months", None, total)
    for finding in revised["findings"]:
        measurement = finding["measurement"]
        if measurement["type"] != "cluster" or "cluster" in finding["event"]["type"].lower():
            continue
        if "rate" not in measurement and finding["id"] not in RECURRING_SIZE.get(index, ()):
            continue
        before = copy.deepcopy(finding)
        label = finding["event"]["type"]
        if label.lower() in {
            "events",
            "seizures",
            "bursts",
            "brief bursts",
            "short runs of events",
        }:
            finding["event"]["type"] = "clusters"
        else:
            finding["event"]["type"] = f"clusters of {label}"
        record(
            finding["id"],
            "recurring grouped-event pattern has a cluster counted unit",
            before,
            copy.deepcopy(finding),
        )
    return revised, edits


def main() -> None:
    refs = [json.loads(line) for line in (BASE / "reference.jsonl").read_text().splitlines()]
    old_bundle = json.loads((BASE / "review_bundle.json").read_text())
    baseline = json.loads(BASE_RESULT.read_text())
    if len(refs) != len(old_bundle["rows"]) or len(refs) != 750:
        raise ValueError("Expected all 750 development letters")
    schema = json.loads(BASE_SCHEMA.read_text())
    schema["properties"]["guide_version"]["const"] = GUIDE
    schema["description"] = (
        "Seizure-finding annotation v0.8.3: mixed-diary totals, broad summaries, "
        "recurring cluster units, and uncertain-event boundaries."
    )
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    output: list[dict[str, Any]] = []
    reviews: list[dict[str, Any]] = []
    scores: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for source, previous in zip(refs, old_bundle["rows"], strict=True):
        index = source["source_row_index"]
        if (index, source["source_id"]) != (previous["source_row_index"], previous["source_id"]):
            raise ValueError(f"Source order changed at {index}")
        revised, edits = revise(source, previous["note"])
        for item in edits:
            evidence = (item["after"] or item["before"])["evidence"]
            if evidence not in previous["note"]:
                raise ValueError(f"Changed finding evidence is not source exact at {index}")
        validator.validate(revised)
        output.append(revised)
        audit.extend(edits)
        prediction = previous["predicted"]
        score = scorer.score_letter(
            previous["note"], revised["findings"], prediction if previous["usable"] else None
        )
        scores.append(score)
        matched_pred = {pid for pid, _ in score["pairs"]}
        matched_ref = {gid for _, gid in score["pairs"]}
        review = copy.deepcopy(previous)
        review["reference"] = revised["findings"]
        review["pairs"] = score["pairs"]
        review["unmatched_reference_ids"] = [
            f["id"] for f in revised["findings"] if f["id"] not in matched_ref
        ]
        review["unmatched_prediction_ids"] = [
            f["id"] for f in prediction if f["id"] not in matched_pred
        ]
        for prefix in ("v08", "purist"):
            for field in ("tp", "fp", "fn"):
                review[f"{prefix}_{field}"] = score[field]
        reviews.append(review)
    if set(REMOVE) - {x["source_row_index"] for x in audit}:
        raise ValueError("A declared removal was not applied")
    expected_cluster_labels = {
        (index, ident) for index, ids in RECURRING_SIZE.items() for ident in ids
    }
    applied_cluster_labels = {
        (item["source_row_index"], item["finding_id"])
        for item in audit
        if item["reason"] == "recurring grouped-event pattern has a cluster counted unit"
    }
    if not expected_cluster_labels <= applied_cluster_labels:
        missing = sorted(expected_cluster_labels - applied_cluster_labels)
        raise ValueError(f"Missing recurring cluster labels: {missing}")
    summary = aggregate(scores)
    summary["matching_version"] = scorer.VERSION
    if summary["letters"] != 750 or summary["usable_letters"] != 714:
        raise ValueError("Development coverage changed")
    write_json(SCHEMA, schema)
    write_jsonl(RUN / "reference.jsonl", output)
    write_jsonl(RUN / "claim_adjudications.jsonl", audit)
    write_json(
        RUN / "review_bundle.json",
        {
            "scope": "Gan synthetic dev750; v0.8.3 owner decisions versus saved R8 predictions",
            "matcher": scorer.VERSION,
            "aggregate": summary,
            "rows": reviews,
        },
    )
    write_json(
        RESULT / "score.json",
        {
            "version": "v0.8.3_owner_batch_adjudications_dev750_v1",
            "dataset": "Gan 2026 synthetic",
            "split": "dev750",
            "row_policy": "all 750 development letters; 36 unusable saved R8 responses retained",
            "base_score_path": str(BASE_RESULT),
            "base_score_sha256": study.old.digest(BASE_RESULT.read_bytes()),
            "base_reference_sha256": study.old.digest((BASE / "reference.jsonl").read_bytes()),
            "reference_path": str(RUN / "reference.jsonl"),
            "reference_sha256": study.old.digest((RUN / "reference.jsonl").read_bytes()),
            "schema_path": str(SCHEMA),
            "schema_sha256": study.old.digest(SCHEMA.read_bytes()),
            "scorer": scorer.VERSION,
            "scorer_sha256": study.old.digest(Path(scorer.__file__).read_bytes()),
            "model": baseline["model"],
            "prompt_version": baseline["prompt_version"],
            "prompt_revision": baseline["prompt_revision"],
            "replay_mode": "saved R8 responses; no model call",
            "repair_policy": "none; predictions unchanged from v0.8 projection",
            "gold_edits": len(audit),
            "edit_reasons": dict(Counter(x["reason"] for x in audit)),
            "finding_v083": summary,
            "letters": [
                {"source_row_index": row["source_row_index"], **score}
                for row, score in zip(reviews, scores, strict=True)
            ],
        },
    )
    print(json.dumps({"edits": len(audit), "score": summary}, indent=2))


if __name__ == "__main__":
    main()
