"""Prepare source-first compact-claim candidates from frozen v0.8.5 dev750 gold.

Only structural transformations are automatic. Every old finding is retained with
its exact quotation and original object; phase, primary-score inclusion, and
ambiguous units remain explicit review work. No prediction or locked row is read.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REFERENCE = Path("runs/seizure_finding_annotation_v0_8_5/dev750_r8_saved/reference.jsonl")
SOURCE = Path("runs/seizure_finding_annotation_v0_8_5/dev750_r8_saved/review_bundle.json")
SCHEMA = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.schema.json"
)
RUN = Path("runs/seizure_finding_annotation_compact_v0_1/dev750")
SUMMARY = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "migration_summary.json"
)
POLICY = "compact_primary_finding_candidate_v0_1"
BATCH_SIZE = 150


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))


def quantity(value: dict[str, Any]) -> dict[str, Any]:
    kind = value["type"]
    if kind == "number":
        return {"kind": "number", "value": value["value"]}
    if kind == "range":
        return {"kind": "range", "lower": value["lower"], "upper": value["upper"]}
    if kind == "qualitative":
        return {"kind": "verbatim", "text": value["quantity"]}
    if kind == "bound":
        bound = value["value"]
        if isinstance(bound, dict):
            bound = quantity(bound)
        return {"kind": "bound", "relation": value["relation"], "value": bound}
    raise ValueError(f"Unhandled quantity type: {kind}")


def duration(value: dict[str, Any]) -> dict[str, Any]:
    kind = value["type"]
    if kind == "qualitative":
        return {"kind": "verbatim", "text": value["quantity"]}
    fields = {key: copy.deepcopy(item) for key, item in value.items() if key != "type"}
    if kind not in {"number", "range", "bound"}:
        raise ValueError(f"Unhandled duration type: {kind}")
    return {"kind": kind, **fields}


def counted_unit(finding: dict[str, Any]) -> tuple[str, list[str]]:
    measurement = finding["measurement"]["type"]
    label = finding["event"]["type"].casefold().replace("–", "-")
    flags: list[str] = []
    if measurement in {"seizure_free", "last_seizure"}:
        return "not_applicable", flags
    if "cluster day" in label:
        return "cluster_day", flags
    if measurement == "cluster" or "cluster" in label:
        if "cluster days" in finding["evidence"].casefold():
            flags.append("cluster_day_unit_review")
        return "cluster", flags
    if "seizure day" in label or "days with seizure" in label:
        return "seizure_day", flags
    if "seizure night" in label or "nights with seizure" in label:
        return "seizure_night", flags
    if "night" in finding["evidence"].casefold() or "day" in finding["evidence"].casefold():
        flags.append("affected_period_unit_review")
    return "individual_seizure", flags


def convert_measurement(finding: dict[str, Any], unit: str) -> tuple[dict[str, Any], str]:
    old = finding["measurement"]
    kind = old["type"]
    source_time = finding.get("period", {}).get("time", "")
    if not source_time and old.get("occurred_at"):
        source_time = old["occurred_at"]["time"]
    if kind == "rate":
        rate = {"kind": "rate", "quantity": quantity(old["count"]), "per": duration(old["per"])}
        if unit in {"cluster", "cluster_day"}:
            return {"kind": "cluster", "cadence": rate}, source_time
        return rate, source_time
    if kind == "count":
        count = quantity(old["count"])
        if unit in {"cluster", "cluster_day"}:
            return {"kind": "cluster", "count": count}, source_time
        return {"kind": "observed_count", "quantity": count}, source_time
    if kind == "cluster":
        result: dict[str, Any] = {"kind": "cluster"}
        if old.get("count") is not None:
            result["count"] = quantity(old["count"])
        if old.get("rate") is not None:
            result["cadence"] = {
                "kind": "rate",
                "quantity": quantity(old["rate"]["count"]),
                "per": duration(old["rate"]["per"]),
            }
        if old.get("seizures_per_cluster") is not None:
            result["seizures_per_cluster"] = quantity(old["seizures_per_cluster"])
        return result, source_time
    if kind == "seizure_free":
        result = {"kind": "seizure_free"}
        if old.get("duration") is not None:
            result["duration"] = duration(old["duration"])
        if old.get("since") is not None:
            result["since"] = old["since"]["time"]
            if not source_time:
                source_time = old["since"]["time"]
        return result, source_time
    if kind == "last_seizure":
        return {"kind": "last_event", "occurred_at": old["occurred_at"]["time"]}, source_time
    if kind == "qualitative":
        return {"kind": "qualitative", "level": old["frequency"]}, source_time
    raise ValueError(f"Unhandled measurement type: {kind}")


def convert_finding(finding: dict[str, Any], note: str) -> dict[str, Any]:
    evidence = finding["evidence"]
    if evidence not in note:
        raise ValueError("Legacy finding evidence is not an exact source substring")
    unit, flags = counted_unit(finding)
    measurement, source_time = convert_measurement(finding, unit)
    scope = {
        "specific": "named",
        "combined": "combined",
        "unspecified": "unspecified",
    }[finding["event"]["scope"]]
    if scope == "unspecified":
        flags.append("event_scope_review")
    if finding.get("condition"):
        flags.append("condition_scope_review")
    if set(finding.get("period", {})) - {"time"}:
        flags.append("period_detail_review")
    if finding["measurement"]["type"] == "count" and unit in {"cluster", "cluster_day"}:
        flags.append("legacy_count_as_cluster_review")
    flags.extend(("clinical_phase_review", "primary_scope_review"))
    old_status = finding["event"].get("seizure_status", "stated")
    candidate: dict[str, Any] | None = None
    if old_status == "non_seizure":
        flags.append("non_seizure_scope_review")
    else:
        candidate = {
            "event": {"scope": scope, "label": finding["event"]["type"]},
            "counted_unit": unit,
            "status": old_status,
            "measurement": measurement,
            "time": {"phase": "past_or_unclear"},
            "evidence": [evidence],
        }
        if source_time:
            candidate["time"]["source"] = source_time
    return {
        "legacy_id": finding["id"],
        "legacy": finding,
        "candidate": candidate,
        "primary_scope": "review_pending",
        "review_flags": sorted(set(flags)),
    }


def main() -> None:
    reference_bytes = REFERENCE.read_bytes()
    source_bytes = SOURCE.read_bytes()
    schema_bytes = SCHEMA.read_bytes()
    refs = [json.loads(line) for line in reference_bytes.decode().splitlines()]
    bundle = json.loads(source_bytes)
    schema = json.loads(schema_bytes)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator({"$defs": schema["$defs"], "$ref": "#/$defs/finding"})
    if len(refs) != len(bundle["rows"]) or len(refs) != 750:
        raise ValueError("Expected 750 development rows")
    rows: list[dict[str, Any]] = []
    flags: Counter[str] = Counter()
    measurements: Counter[str] = Counter()
    for reference, source in zip(refs, bundle["rows"], strict=True):
        index = reference["source_row_index"]
        identity = (index, reference["source_id"])
        if identity != (source["source_row_index"], source["source_id"]):
            raise ValueError(f"Source order changed at {index}")
        note = source["note"]
        if digest(note.encode()) != reference["source_sha256"]:
            raise ValueError(f"Source hash mismatch at {index}")
        claims = [convert_finding(finding, note) for finding in reference["findings"]]
        for claim in claims:
            flags.update(claim["review_flags"])
            if claim["candidate"] is not None:
                validator.validate(claim["candidate"])
                measurements[claim["candidate"]["measurement"]["kind"]] += 1
        rows.append(
            {
                "source_row_index": index,
                "source_id": reference["source_id"],
                "source_sha256": reference["source_sha256"],
                "note": note,
                "annotation_state": reference["annotation_state"],
                "claims": claims,
            }
        )
    if sum(len(row["claims"]) for row in rows) != 1524:
        raise ValueError("The frozen finding inventory changed")
    write_jsonl(RUN / "machine_candidates.jsonl", rows)
    batches = []
    for start in range(0, len(rows), BATCH_SIZE):
        number = start // BATCH_SIZE + 1
        batch_rows = rows[start : start + BATCH_SIZE]
        path = RUN / "batches" / f"batch_{number:02d}_input.json"
        write_json(
            path,
            {
                "policy": POLICY,
                "batch": number,
                "row_range": [start, start + len(batch_rows) - 1],
                "schema_sha256": digest(schema_bytes),
                "rows": batch_rows,
            },
        )
        batches.append(
            {
                "batch": number,
                "path": str(path),
                "rows": len(batch_rows),
                "sha256": digest(path.read_bytes()),
            }
        )
    write_json(
        SUMMARY,
        {
            "policy": POLICY,
            "dataset": "Gan 2026 synthetic",
            "split": "dev750",
            "row_policy": "all 750 development letters including row_ok=False",
            "base_reference": str(REFERENCE),
            "base_reference_sha256": digest(reference_bytes),
            "source_bundle": str(SOURCE),
            "source_bundle_sha256": digest(source_bytes),
            "schema": str(SCHEMA),
            "schema_sha256": digest(schema_bytes),
            "scorer": "none; no finding score produced",
            "model": "none; deterministic migration",
            "prompt_version": "none; Pro review not yet started",
            "replay_mode": "deterministic structural migration; no model call",
            "repair_policy": "none",
            "rows": len(rows),
            "legacy_findings": sum(len(row["claims"]) for row in rows),
            "structural_candidates": sum(
                claim["candidate"] is not None for row in rows for claim in row["claims"]
            ),
            "review_only_non_seizure": sum(
                claim["candidate"] is None for row in rows for claim in row["claims"]
            ),
            "measurement_types": dict(measurements),
            "review_flags": dict(flags),
            "batches": batches,
        },
    )
    print(
        json.dumps(
            {
                "rows": len(rows),
                "findings": 1524,
                "batches": len(batches),
                "review_flags": dict(flags),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
