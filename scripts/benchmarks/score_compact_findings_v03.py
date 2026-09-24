"""Freeze the compact dev750 reference and score saved R9-shaped responses.

No model calls or holdout access. Prediction input is JSONL with one object per
source row: source_id, source_row_index, source_sha256, response. Response is a
parsed JSON object or null; this scorer performs no format or semantic repair.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v03 as scorer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)

CANDIDATE = Path(
    "runs/seizure_finding_annotation_compact_v0_1/dev750/"
    "candidate_v0_3_owner_adjudicated.json"
)
EXPECTED_CANDIDATE_SHA256 = "25e1b63c71f4ddd29bee3f6cf9f40da360f840f4477c88e74d60f36387b46d06"
EXPECTED_SCHEMA_SHA256 = "0d73189f09b860eca9fb78350b66dbf4c3f9ccb1a7c94d08b2548eecf4c06a81"
REFERENCE = Path("runs/seizure_finding_annotation_compact_v0_1/dev750/scorer_v03/reference.jsonl")
MANIFEST = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "scorer_v03_manifest.json"
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as output:
        for row in rows:
            output.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_reference() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if sha(CANDIDATE) != EXPECTED_CANDIDATE_SHA256:
        raise ValueError("Compact v0.3 candidate changed; freeze a new scorer version")
    if sha(r9.SCHEMA_PATH) != EXPECTED_SCHEMA_SHA256:
        raise ValueError("Compact response schema changed; freeze a new scorer version")
    source = json.loads(CANDIDATE.read_text())
    if source["policy"] != "compact_primary_finding_candidate_v0_3":
        raise ValueError("Wrong annotation policy")
    if source["dataset"] != "Gan 2026 synthetic" or source["split"] != "dev750":
        raise ValueError("Wrong dataset or split")
    if source["schema_sha256"] != EXPECTED_SCHEMA_SHA256:
        raise ValueError("Candidate schema provenance mismatch")
    schema = json.loads(r9.SCHEMA_PATH.read_text())
    Draft202012Validator.check_schema(schema)
    finding_validator = Draft202012Validator(
        {"$defs": schema["$defs"], "$ref": "#/$defs/finding"}
    )
    rows = []
    for row in source["rows"]:
        if row["annotation_state"] != "complete":
            raise ValueError(f"Incomplete reference: {row['source_id']}")
        if hashlib.sha256(row["note"].encode()).hexdigest() != row["source_sha256"]:
            raise ValueError(f"Source hash mismatch: {row['source_id']}")
        findings = []
        origins = []
        for claim in row["claims"]:
            if claim["disposition"] == "primary":
                findings.append(claim["candidate"])
                origins.append(claim["legacy_id"])
        for claim in row.get("added_claims", []):
            if claim["disposition"] == "primary":
                findings.append(claim["candidate"])
                origins.append(claim["id"])
        if len(origins) != len(set(origins)):
            raise ValueError(f"Duplicate claim origin: {row['source_id']}")
        for finding in findings:
            finding_validator.validate(finding)
            if any(quote not in row["note"] for quote in finding["evidence"]):
                raise ValueError(f"Reference evidence absent: {row['source_id']}")
        rows.append(
            {
                "source_row_index": row["source_row_index"],
                "source_id": row["source_id"],
                "source_sha256": row["source_sha256"],
                "note": row["note"],
                "origin_ids": origins,
                "findings": findings,
            }
        )
    if len(rows) != 750 or len({row["source_id"] for row in rows}) != 750:
        raise ValueError("Expected 750 unique development letters")
    if len({row["source_row_index"] for row in rows}) != 750:
        raise ValueError("Duplicate source row index")
    if sum(len(row["findings"]) for row in rows) != 1219:
        raise ValueError("Unexpected compact reference claim count")
    manifest = {
        "dataset": source["dataset"],
        "split": source["split"],
        "row_policy": "all 750 source rows, including row_ok=False",
        "annotation_policy": source["policy"],
        "annotation_sha256": sha(CANDIDATE),
        "schema_sha256": sha(r9.SCHEMA_PATH),
        "prompt_version": r9.VERSION,
        "prompt_revision": r9.REVISION,
        "prompt_source_sha256": sha(Path(r9.__file__)),
        "scorer": scorer.VERSION,
        "scorer_source_sha256": sha(Path(scorer.__file__)),
        "matching": (
            "whole-claim maximum one-to-one match; residual source-evidence alignment "
            "for separate component precision and recall"
        ),
        "reported_scores": [
            "whole_claim",
            "source_aligned",
            *scorer.COMPONENTS,
        ],
        "letters": len(rows),
        "reference_findings": sum(len(row["findings"]) for row in rows),
        "reference_local_only": str(REFERENCE),
        "repair_policy": "none",
        "scorer_model_calls": 0,
    }
    return rows, manifest


def validate_response(
    response: Any, note: str, validator: Draft202012Validator
) -> tuple[list[dict[str, Any]] | None, str | None]:
    if not isinstance(response, dict):
        return None, "response_not_object"
    try:
        validator.validate(response)
    except ValidationError as exc:
        return None, f"schema:{exc.json_path}"
    answer = response["answer"]
    findings = response["findings"]
    if any(index >= len(findings) for index in answer["claim_indices"]):
        return None, "answer_claim_index_out_of_range"
    if answer["label"] == "no seizure frequency reference":
        if answer["evidence"] is not None or findings or answer["claim_indices"]:
            return None, "no_reference_contract"
    elif answer["evidence"] is None or answer["evidence"] not in note:
        return None, "answer_evidence_absent"
    if any(quote not in note for finding in findings for quote in finding["evidence"]):
        return None, "finding_evidence_absent"
    return findings, None


def score_saved(
    references: list[dict[str, Any]],
    prediction_path: Path,
    schema: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    input_rows = [json.loads(line) for line in prediction_path.read_text().splitlines() if line]
    if len(input_rows) != len(references):
        raise ValueError("Prediction file must cover all 750 source rows")
    by_index = {}
    for row in input_rows:
        index = row["source_row_index"]
        if index in by_index:
            raise ValueError(f"Duplicate prediction row: {index}")
        by_index[index] = row
    if set(by_index) != {row["source_row_index"] for row in references}:
        raise ValueError("Prediction row indices do not match reference")
    validator = Draft202012Validator(schema)
    scores = []
    local_rows = []
    invalid = {}
    for ref in references:
        pred = by_index[ref["source_row_index"]]
        for key in ("source_id", "source_sha256"):
            if pred[key] != ref[key]:
                raise ValueError(f"Prediction {key} mismatch on {ref['source_row_index']}")
        findings, error = validate_response(pred.get("response"), ref["note"], validator)
        score = scorer.score_letter(ref["note"], ref["findings"], findings)
        scores.append(score)
        if error:
            invalid[error] = invalid.get(error, 0) + 1
        local_rows.append(
            {
                "source_row_index": ref["source_row_index"],
                "source_id": ref["source_id"],
                "source_sha256": ref["source_sha256"],
                "score": score,
                "invalid_reason": error,
                "reference_origin_ids": ref["origin_ids"],
            }
        )
    summary = scorer.aggregate(scores)
    summary["invalid_reasons"] = invalid
    summary["prediction_sha256"] = sha(prediction_path)
    return summary, local_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", type=Path)
    parser.add_argument("--run-metadata", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    references, manifest = load_reference()
    write_jsonl(REFERENCE, references)
    manifest["reference_sha256"] = sha(REFERENCE)
    write_json(MANIFEST, manifest)
    if args.predictions is None:
        if args.output is not None or args.run_metadata is not None:
            parser.error("--output and --run-metadata require --predictions")
        print(json.dumps(manifest, indent=2))
        return
    if args.output is None or args.run_metadata is None:
        parser.error("--predictions requires --output and --run-metadata")
    if args.output.exists():
        raise FileExistsError(f"Output exists: {args.output}")
    run_metadata = json.loads(args.run_metadata.read_text())
    required = ("model", "prompt_version", "prompt_revision", "replay_mode", "repair_policy")
    if any(not isinstance(run_metadata.get(key), str) or not run_metadata[key] for key in required):
        raise ValueError(f"Run metadata requires nonempty strings: {', '.join(required)}")
    if (
        run_metadata["prompt_version"] != r9.VERSION
        or run_metadata["prompt_revision"] != r9.REVISION
    ):
        raise ValueError("Saved responses do not declare the frozen R9 prompt")
    schema = json.loads(r9.SCHEMA_PATH.read_text())
    summary, local_rows = score_saved(references, args.predictions, schema)
    summary.update(manifest)
    summary["run_metadata"] = run_metadata
    summary["run_metadata_sha256"] = sha(args.run_metadata)
    args.output.mkdir(parents=True)
    write_json(args.output / "score.json", summary)
    write_jsonl(args.output / "per_letter.jsonl", local_rows)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
