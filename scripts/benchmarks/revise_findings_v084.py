"""Apply owner cluster-unit and explicit seizure-link decisions to dev750.

The v0.8.3 reference and saved R8 predictions are immutable inputs. This
producer records each source-backed edit and rescoring under a versioned matcher.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v084
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.score_findings_v08 import aggregate, write_json, write_jsonl

BASE = Path("runs/seizure_finding_annotation_v0_8_3/dev750_r8_saved")
BASE_RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_3/dev750_r8_saved/score.json"
)
BASE_SCHEMA = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_3/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8_4/dev750_r8_saved")
RESULT = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_4/dev750_r8_saved")
SCHEMA = RESULT.parent / "annotation.schema.json"
GUIDE = "seizure_finding_annotation_v0.8.4"

REMOVE = {
    6738: {"f1": "concern for reduced-awareness spells is not an explicit seizure link"},
    11109: {"f2": "cluster days and within-day size form one cluster finding"},
    11118: {"f1": "cluster days and within-day size form one cluster finding"},
    11131: {"f1": "cluster days and within-day size form one cluster finding"},
    11197: {"f1": "header repeats the same single cluster as the clinical narrative"},
    15513: {"f4": "ten-day absence is below the two-week minimum"},
}
MERGE = {11109: ("f3", "f2"), 11118: ("f2", "f1"), 11131: ("f2", "f1")}


def cluster_label(label: str) -> str:
    name = label.strip()
    if "cluster" in name.lower():
        return name
    if name.lower() in {"seizures", "events", "seizure", "event"}:
        return "clusters"
    if name.lower() == "tonic seizure":
        return "clusters of tonic seizures"
    return f"clusters of {name}"


def revise(row: dict[str, Any], note: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    index = row["source_row_index"]
    revised = copy.deepcopy(row)
    revised["guide_version"] = GUIDE
    before_by_id = {f["id"]: f for f in row["findings"]}
    edits: list[dict[str, Any]] = []

    def record(ident: str, reason: str, before: Any, after: Any) -> None:
        edits.append(
            {
                "source_row_index": index,
                "source_id": row["source_id"],
                "source_sha256": row["source_sha256"],
                "finding_id": ident,
                "reason": reason,
                "before": before,
                "after": after,
            }
        )

    for ident, reason in REMOVE.get(index, {}).items():
        record(ident, reason, before_by_id[ident], None)
    revised["findings"] = [f for f in revised["findings"] if f["id"] not in REMOVE.get(index, {})]
    kept = {f["id"]: f for f in revised["findings"]}

    if index in MERGE:
        survivor_id, old_id = MERGE[index]
        survivor, old = kept[survivor_id], before_by_id[old_id]
        before = copy.deepcopy(survivor)
        survivor["measurement"]["count"] = copy.deepcopy(old["measurement"]["count"])
        survivor["period"] = copy.deepcopy(old["period"])
        if index == 11118:
            survivor["event"]["type"] = "clusters of generalised convulsions"
            survivor["event"]["scope"] = "specific"
            start = note.index("Over the last four weeks, the records note:")
            end = note.index("rapid recovery", start) + len("rapid recovery")
            survivor["evidence"] = note[start:end]
        else:
            survivor["event"]["type"] = "clusters"
        record(
            survivor_id,
            "combine cluster-day count and seizures per cluster",
            before,
            copy.deepcopy(survivor),
        )

    for finding in revised["findings"]:
        m = finding["measurement"]
        if m["type"] != "cluster" or m.get("count") != {"type": "number", "value": 1}:
            continue
        if m.get("seizures_per_cluster") is None:
            continue
        label = cluster_label(finding["event"]["type"])
        if label == finding["event"]["type"]:
            continue
        before = copy.deepcopy(finding)
        finding["event"]["type"] = label
        record(
            finding["id"],
            "single grouped occurrence names the cluster unit",
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
        "Seizure-finding annotation v0.8.4: two-week absence minimum, single "
        "clusters, combined cluster-day size, and explicit seizure link."
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
        predictions = previous["predicted"]
        score = finding_v084.score_letter(
            previous["note"], revised["findings"], predictions if previous["usable"] else None
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
            f["id"] for f in predictions if f["id"] not in matched_pred
        ]
        for prefix in ("v08", "purist"):
            for field in ("tp", "fp", "fn"):
                review[f"{prefix}_{field}"] = score[field]
        reviews.append(review)
    if set(REMOVE) - {item["source_row_index"] for item in audit}:
        raise ValueError("A declared removal was not applied")
    summary = aggregate(scores)
    summary["matching_version"] = finding_v084.VERSION
    if summary["letters"] != 750 or summary["usable_letters"] != 714:
        raise ValueError("Development coverage changed")
    write_json(SCHEMA, schema)
    write_jsonl(RUN / "reference.jsonl", output)
    write_jsonl(RUN / "claim_adjudications.jsonl", audit)
    write_json(
        RUN / "review_bundle.json",
        {
            "scope": "Gan synthetic dev750; v0.8.4 owner decisions versus saved R8 predictions",
            "matcher": finding_v084.VERSION,
            "aggregate": summary,
            "rows": reviews,
        },
    )
    write_json(
        RESULT / "score.json",
        {
            "version": "v0.8.4_owner_cluster_and_seizure_link_dev750_v1",
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
            "scorer": finding_v084.VERSION,
            "scorer_sha256": study.old.digest(Path(finding_v084.__file__).read_bytes()),
            "model": baseline["model"],
            "prompt_version": baseline["prompt_version"],
            "prompt_revision": baseline["prompt_revision"],
            "replay_mode": "saved R8 responses; no model call",
            "repair_policy": "none; predictions unchanged from v0.8 projection",
            "gold_edits": len(audit),
            "edit_reasons": dict(Counter(item["reason"] for item in audit)),
            "finding_v084": summary,
            "letters": [
                {"source_row_index": row["source_row_index"], **score}
                for row, score in zip(reviews, scores, strict=True)
            ],
        },
    )
    print(json.dumps({"edits": len(audit), "score": summary}, indent=2))


if __name__ == "__main__":
    main()
