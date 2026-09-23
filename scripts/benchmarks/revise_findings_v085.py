"""Keep within-cluster spans as evidence, not scored observation periods.

The v0.8.4 reference and saved R8 predictions are immutable inputs. Every
source-backed edit and the changed scorer are recorded in a versioned replay.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import finding_v085
from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_thinking as study,
)
from scripts.benchmarks.score_findings_v08 import aggregate, write_json, write_jsonl

BASE = Path("runs/seizure_finding_annotation_v0_8_4/dev750_r8_saved")
BASE_RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_4/dev750_r8_saved/score.json"
)
BASE_SCHEMA = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_4/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8_5/dev750_r8_saved")
RESULT = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_5/dev750_r8_saved")
SCHEMA = RESULT.parent / "annotation.schema.json"
GUIDE = "seizure_finding_annotation_v0.8.5"

SPAN_PERIODS: dict[int, str] = {
    8820: "f1",
    15376: "f2",
    15404: "f2",
    15429: "f1",
    15431: "f1",
    15442: "f2",
    15470: "f2",
    15479: "f1",
    15497: "f1",
    15503: "f1",
    15513: "f1",
    15519: "f1",
    15529: "f2",
    15593: "f4",
    16757: "f1",
    16772: "f1",
    16839: "f2",
    16907: "f1",
}
SPAN_TEXT = {"a day", "one day", "a single day", "within 24 hours", "within half an hour"}


def revise(row: dict[str, Any], note: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    revised = copy.deepcopy(row)
    revised["guide_version"] = GUIDE
    index = row["source_row_index"]
    ident = SPAN_PERIODS.get(index)
    if ident is None:
        return revised, []
    finding = next(f for f in revised["findings"] if f["id"] == ident)
    if finding["measurement"]["type"] != "cluster":
        raise ValueError(f"Expected cluster finding on {index}/{ident}")
    before = copy.deepcopy(finding)
    period = finding.pop("period")
    if period["time"].lower() not in SPAN_TEXT or period["time"] not in note:
        raise ValueError(f"Expected source-backed within-cluster span on {index}/{ident}")
    if period["time"] not in finding["evidence"]:
        raise ValueError(f"Span must remain in exact evidence on {index}/{ident}")
    return revised, [
        {
            "source_row_index": index,
            "source_id": row["source_id"],
            "source_sha256": row["source_sha256"],
            "finding_id": ident,
            "reason": "within-cluster span retained in evidence, removed from scored period",
            "before": before,
            "after": finding,
        }
    ]


def main() -> None:
    refs = [json.loads(line) for line in (BASE / "reference.jsonl").read_text().splitlines()]
    old_bundle = json.loads((BASE / "review_bundle.json").read_text())
    baseline = json.loads(BASE_RESULT.read_text())
    if len(refs) != len(old_bundle["rows"]) or len(refs) != 750:
        raise ValueError("Expected all 750 development letters")
    schema = json.loads(BASE_SCHEMA.read_text())
    schema["properties"]["guide_version"]["const"] = GUIDE
    schema["description"] = (
        "Seizure-finding annotation v0.8.5: within-cluster spans remain in "
        "evidence, not in scored observation periods."
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
        score = finding_v085.score_letter(
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
    if set(SPAN_PERIODS) != {item["source_row_index"] for item in audit}:
        raise ValueError("A declared span edit was not applied")
    summary = aggregate(scores)
    summary["matching_version"] = finding_v085.VERSION
    if summary["letters"] != 750 or summary["usable_letters"] != 714:
        raise ValueError("Development coverage changed")
    write_json(SCHEMA, schema)
    write_jsonl(RUN / "reference.jsonl", output)
    write_jsonl(RUN / "claim_adjudications.jsonl", audit)
    write_json(
        RUN / "review_bundle.json",
        {
            "scope": (
                "Gan synthetic dev750; v0.8.5 unscored cluster spans versus saved R8 predictions"
            ),
            "matcher": finding_v085.VERSION,
            "aggregate": summary,
            "rows": reviews,
        },
    )
    write_json(
        RESULT / "score.json",
        {
            "version": "v0.8.5_unscored_cluster_spans_dev750_v1",
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
            "scorer": finding_v085.VERSION,
            "scorer_sha256": study.old.digest(Path(finding_v085.__file__).read_bytes()),
            "model": baseline["model"],
            "prompt_version": baseline["prompt_version"],
            "prompt_revision": baseline["prompt_revision"],
            "replay_mode": "saved R8 responses; no model call",
            "repair_policy": "none; predictions unchanged from v0.8 projection",
            "gold_edits": len(audit),
            "edit_reasons": dict(Counter(item["reason"] for item in audit)),
            "finding_v085": summary,
            "letters": [
                {"source_row_index": row["source_row_index"], **score}
                for row, score in zip(reviews, scores, strict=True)
            ],
        },
    )
    print(json.dumps({"edits": len(audit), "score": summary}, indent=2))


if __name__ == "__main__":
    main()
