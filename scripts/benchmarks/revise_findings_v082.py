"""Source-adjudicated v0.8.2 inventory revision over all dev750 letters.

Every semantic edit is explicit below and emitted with before/after source
evidence. The saved R8 projection, v0.8.1 reference, and locked split are never
modified. The all-letter triage is produced separately by
audit_claim_representation_v082.py.
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

BASE = Path("runs/seizure_finding_annotation_v0_8_1/dev750_r8_saved")
BASE_RESULT = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_1/dev750_r8_saved/score.json"
)
BASE_SCHEMA = Path(
    "results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_1/annotation.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_v0_8_2/dev750_r8_saved")
RESULT = Path("results/letter-benchmarks/gan/seizure_finding_annotation_v0_8_2/dev750_r8_saved")
SCHEMA = RESULT.parent / "annotation.schema.json"
GUIDE = "seizure_finding_annotation_v0.8.2"

# These are source-checked occurrences of the owner's one-claim rule. The
# accompanying audit retains their original evidence and IDs. Other multiple-
# absence letters require their own scope/window adjudication before editing.
REMOVE: dict[int, dict[str, str]] = {
    743: {"f4": "same current most-shifts frequency restated as most working days"},
    744: {
        "f1": "qualitative generalised frequency replaced by one event in eight weeks",
        "f4": "same qualitative generalised frequency repeated in summary",
    },
    2938: {"f2": "same seizure-free interval restated as November 2015"},
    2992: {"f1": "vague background frequency beside dated last event and current absence"},
    4919: {"f2": "possible aura-like episode without established seizure identity"},
    4956: {"f2": "same seven-month event-free interval; since anchor is context"},
    5528: {
        "f1": "summary repeats the single dated event",
        "f3": "qualitative summary repeats the single dated event",
    },
    5696: {
        "f1": "intermittent description contextualises the four-month total",
        "f3": "morning breakdown of the stated total of three events",
        "f4": "evening breakdown of the stated total of three events",
    },
    7872: {"f2": "same since-last-review absence elaborated with symptom list"},
    8089: {"f2": "same remission interval restated with relative anchor"},
    8145: {"f1": "same continuous absence interval; six-month duration is scored"},
    8355: {
        "f2": "same continuous absence interval; June anchor is context",
        "f3": "same continuous absence interval; summary repeats duration",
    },
    8805: {"f2": "possible confusion episode without established seizure identity"},
    8924: {"f2": "same interval and event corroborated by diary and partner"},
    12484: {"f8": "same since-last-appointment absence restated"},
    13598: {"f4": "same multi-year remission restated in summary"},
    14146: {
        "f3": "trigger subcount of the stated total of three",
        "f4": "trigger subcount of the stated total of three",
    },
    15193: {"f3": "same September 2022 generalised-seizure absence restated"},
    15267: {"f3": "same June 2017 tonic-clonic absence restated generically"},
    17003: {
        "f4": "same twelve-month generalised absence restated as one year",
        "f5": "same twelve-month generalised absence repeated in impression",
    },
}


def revise(row: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
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
    if index == 8805:
        f = next(f for f in revised["findings"] if f["id"] == "f1")
        before = copy.deepcopy(f)
        f["event"]["type"] = "convulsive activity"
        f["event"]["scope"] = "specific"
        record(
            "f1",
            "device absence names convulsive activity; rescue-log wording corroborates",
            before,
            copy.deepcopy(f),
        )
    if index == 12506:
        evidence = (
            "There has been little alteration in seizure frequency over the past year; "
            "she experiences one to two generalised tonic-clonic seizures monthly "
            "with the longest seizure-free period being three weeks."
        )
        new = {
            "id": "f7",
            "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
            "measurement": {
                "type": "seizure_free",
                "duration": {"type": "number", "value": 3, "unit": "week"},
            },
            "timing": "current",
            "evidence": evidence,
            "period": {"time": "longest seizure-free period"},
        }
        revised["findings"].append(new)
        record(
            "f7", "longest gap amid ongoing monthly seizures is a distinct measurement", None, new
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
        "Seizure-finding annotation v0.8.2: source-adjudicated claim units "
        "and duration-scored absence."
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
        revised, edits = revise(source)
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
            "scope": "Gan synthetic dev750; v0.8.2 claim units versus saved R8 predictions",
            "matcher": scorer.VERSION,
            "aggregate": summary,
            "rows": reviews,
        },
    )
    write_json(
        RESULT / "score.json",
        {
            "version": "v0.8.2_source_adjudicated_claims_dev750_v1",
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
            "finding_v082": summary,
            "letters": [
                {"source_row_index": row["source_row_index"], **score}
                for row, score in zip(reviews, scores, strict=True)
            ],
        },
    )
    print(json.dumps({"edits": len(audit), "score": summary}, indent=2))


if __name__ == "__main__":
    main()
