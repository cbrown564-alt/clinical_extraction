"""Replay the saved timed probe: wall time, format/evidence checks and bounded disagreement."""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.analyze_agy_annotation_pass import (  # noqa: E402
    compare_assertions,
    valid_span,
)
from scripts.longitudinal.audit_temporal_relationships import compare_time  # noqa: E402
from scripts.longitudinal.check_annotations import check_annotations, grounded_span  # noqa: E402
from scripts.longitudinal.review_pilot_alignment import align_assertions  # noqa: E402

PACK = ROOT / "results/longitudinal/pilot_v0.8/timed_pass"
FAMILIES = ("diagnosis", "seizure", "medication", "investigation")


def summarize() -> dict:
    hashes, rows = {}, []

    def read(path: Path) -> dict:
        hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        return json.loads(path.read_text())

    manifest = read(PACK / "manifest.json")
    captures = {r["job"]: r for r in read(PACK / "outputs/capture_summary.json")}
    for job in manifest["jobs"]:
        payload = read(PACK / job["input"])
        if hashes[str((PACK / job["input"]).relative_to(ROOT))] != job["sha256"]:
            raise ValueError("Input changed after preparation")
        capture = captures.get(job["id"], {"status": "not_started"})
        row = {
            **job,
            "capture_status": capture["status"],
            "wall_seconds": capture.get("wall_seconds"),
        }
        rows.append(row)
        if capture["status"] != "parsed":
            continue
        attempt = PACK / "outputs/attempts" / job["id"]
        metadata = read(attempt / "attempt.json")
        if metadata["input_sha256"] != job["sha256"] or metadata["observed_tool_steps"] != 0:
            raise ValueError("Invalid capture provenance")
        observed = read(attempt / "parsed.json")
        reference = read(ROOT / "examples/longitudinal" / job["case"] / "annotations.json")
        documents = {d["letter_id"]: d for d in payload["documents"]}
        schema = payload["annotation_schema"]
        errors = list(
            Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(observed)
        )
        row["schema_errors"] = [f"{e.json_path}: {e.message}" for e in errors]
        row["telemetry"] = metadata.get("telemetry")
        row["source_characters"] = sum(len(d["text"]) for d in documents.values())
        if errors:
            continue
        for offsets in (False, True):
            try:
                check_annotations(observed, documents, schema, require_offsets=offsets)
                failure = None
            except ValueError as error:
                failure = str(error)
            row["offset_check_error" if offsets else "grounded_structure_check_error"] = failure
        spans = [
            e
            for a in observed["assertions"]
            for e in a["evidence"] + a.get("all_prior_history_evidence", [])
        ]
        spans += [
            e
            for link in observed["links"]
            for e in link["evidence"] + link.get("first_reinterpretation_evidence", [])
        ]
        row["spans"] = {
            "total": len(spans),
            "grounded": sum(grounded_span(e, documents) for e in spans),
            "exact_offsets": sum(valid_span(e, documents) for e in spans),
        }
        row["observed_by_family"] = dict(
            Counter(a["content"]["family"] for a in observed["assertions"])
        )
        if job["activity"] in FAMILIES:
            reference["assertions"] = [
                a for a in reference["assertions"] if a["content"]["family"] == job["activity"]
            ]
            ids = {a["assertion_id"] for a in reference["assertions"]}
            reference["links"] = [
                link
                for link in reference["links"]
                if all(link[k] in ids for k in ("earlier_assertion", "later_assertion"))
            ]
            row["off_task_assertions"] = sum(
                a["content"]["family"] != job["activity"] for a in observed["assertions"]
            )
        row["literal_comparison"] = compare_assertions(reference, observed, documents)
        mapping, candidates = align_assertions(
            reference["assertions"], observed["assertions"], documents
        )
        row["alignment"] = {
            "mapping": mapping,
            "candidates": candidates,
            "reference_count": len(reference["assertions"]),
            "observed_count": len(observed["assertions"]),
        }
        ref = {a["assertion_id"]: a for a in reference["assertions"]}
        pred = {a["assertion_id"]: a for a in observed["assertions"]}
        row["temporal_pairs"] = [
            {
                "reference_id": a,
                "observed_id": b,
                "classification": compare_time(ref[a]["time"], pred[b]["time"]),
                "reference_time": ref[a]["time"],
                "observed_time": pred[b]["time"],
                "reference_evidence": ref[a]["evidence"],
                "observed_evidence": pred[b]["evidence"],
            }
            for b, a in mapping.items()
        ]
        ref_links = Counter(
            (
                link["earlier_assertion"],
                link["later_assertion"],
                link["relation"],
                link["certainty"],
            )
            for link in reference["links"]
            if all(link[k] in mapping.values() for k in ("earlier_assertion", "later_assertion"))
        )
        pred_links = Counter(
            (
                mapping[link["earlier_assertion"]],
                mapping[link["later_assertion"]],
                link["relation"],
                link["certainty"],
            )
            for link in observed["links"]
            if all(link[k] in mapping for k in ("earlier_assertion", "later_assertion"))
            and link["evidence"]
            and all(grounded_span(e, documents) for e in link["evidence"])
        )
        row["links_on_aligned_endpoints"] = {
            "reference_total": len(reference["links"]),
            "observed_total": len(observed["links"]),
            "reference_aligned": sum(ref_links.values()),
            "observed_grounded_aligned": sum(pred_links.values()),
            "relation_and_certainty_matches": sum((ref_links & pred_links).values()),
        }
    by_activity = {}
    for activity in (*FAMILIES, "temporal", "relationships"):
        selected = [r for r in rows if r["activity"] == activity]
        times = [r["wall_seconds"] for r in selected if r["capture_status"] == "parsed"]
        by_activity[activity] = {
            "planned": len(selected),
            "parsed": len(times),
            "wall_seconds": {
                "total": sum(times),
                "min": min(times) if times else None,
                "median": statistics.median(times) if times else None,
                "max": max(times) if times else None,
            },
            "schema_valid": sum(r.get("schema_errors") == [] for r in selected),
            "grounded_structure_valid": sum(
                r.get("schema_errors") == [] and r.get("grounded_structure_check_error") is None
                for r in selected
            ),
            "literal_pairs": sum(
                r.get("literal_comparison", {}).get("matched_assertions", 0) for r in selected
            ),
            "temporal_comparison_counts": dict(
                Counter(p["classification"] for r in selected for p in r.get("temporal_pairs", []))
            ),
            "links_on_aligned_endpoints": dict(
                sum((Counter(r.get("links_on_aligned_endpoints", {})) for r in selected), Counter())
            ),
        }
    return {
        "dataset": "authored development patients 002, 006, 011; full three-letter histories",
        "split": "development_only",
        "model": manifest["model"],
        "schema_version": manifest["schema_version"],
        "mode": "saved-output replay; no new calls",
        "repair_policy": "none; raw, parsed, schema, grounding and offset results remain separate",
        "claim": (
            "Measured AI wall time and representation disagreement by focused activity; "
            "no human effort, clinical accuracy, pure field cost or population timing estimate"
        ),
        "charge_gbp": manifest["incremental_charge_gbp"],
        "charge_basis": manifest["cost_basis"],
        "human_minutes": None,
        "input_sha256": hashes,
        "program_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (
                Path(__file__),
                ROOT / "scripts/longitudinal/analyze_agy_annotation_pass.py",
                ROOT / "scripts/longitudinal/audit_temporal_relationships.py",
                ROOT / "scripts/longitudinal/check_annotations.py",
                ROOT / "scripts/longitudinal/review_pilot_alignment.py",
            )
        },
        "by_activity": by_activity,
        "jobs": rows,
    }


if __name__ == "__main__":
    report = summarize()
    (PACK / "analysis.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report["by_activity"], indent=2))
