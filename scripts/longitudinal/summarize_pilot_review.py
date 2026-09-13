"""Recompute pilot review coverage and measured machine effort without inventing human time."""

from __future__ import annotations

import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.longitudinal.verify_patient_case import verify_patient_case  # noqa: E402

OUT = ROOT / "results/longitudinal/pilot_v0.7"
PASS = ROOT / "results/longitudinal/pilot_v0.3/agy_pass_medium"


def summarize() -> dict:
    source = ROOT / "results/longitudinal/pilot_v0.5/temporal_relationship_audit.json"
    adjudication = json.loads((OUT / "temporal_adjudication.json").read_text())
    assert hashlib.sha256(source.read_bytes()).hexdigest() == adjudication["source_sha256"]
    triage = json.loads(source.read_text())
    expected = {
        (r["job"], r["reference_id"], r["observed_id"])
        for r in triage["rows"]
        if r["classification"] not in ("exact", "representation_only")
    }
    reviewed = [
        (j["job"], r["reference_id"], j["observed_id"])
        for r in adjudication["reviews"]
        for j in r["jobs"]
    ]
    assert len(reviewed) == len(set(reviewed)) and set(reviewed) == expected
    # Check that every recorded decision is attached to the same time values.
    original = {(r["job"], r["reference_id"], r["observed_id"]): r for r in triage["rows"]}
    for r in adjudication["reviews"]:
        assert r["decision"] and r["reason"] and r["reference_evidence"]
        for j in r["jobs"]:
            old = original[j["job"], r["reference_id"], j["observed_id"]]
            assert old["reference_time"] == r["reference_time"]
            assert old["observed_time"] == r["observed_time"]
    cases = []
    distribution = {q: Counter() for q in ("Q1", "Q2", "Q3", "Q4", "Q5")}
    for case in sorted((ROOT / "examples/longitudinal").glob("authored_patient_*")):
        cases.append({"case": case.name, **verify_patient_case(case)})
        reference = json.loads((case / "reference.json").read_text())
        for answer in reference["answers"]:
            distribution[answer["request_id"].split("_")[-1]][answer["status"]] += 1
    attempts = []
    for path in sorted((PASS / "attempts").glob("*/*/attempt.json")):
        a = json.loads(path.read_text())
        attempts.append(
            {
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "status": a["status"],
                "wall_seconds": a.get("wall_seconds"),
                "model": a.get("model_requested"),
                "provider_cost": a.get("provider_cost"),
                "usage": (a.get("telemetry") or {}).get("usage"),
            }
        )
    timings = sorted(
        a["wall_seconds"]
        for a in attempts
        if a["status"] == "parsed" and a["wall_seconds"] is not None
    )
    by_family = {}
    saved = json.loads((PASS / "analysis_evidence_v2.json").read_text())
    for family in ("diagnosis", "seizure", "medication", "investigation"):
        pairs = [
            p
            for j in saved["job_audits"]
            if j["comparison"]
            for p in j["comparison"]["matched_details"]
            if p["family"] == family
        ]
        by_family[family] = {
            "literal_matched_pairs": len(pairs),
            "field_difference_counts": {
                field: sum(not p["field_agreement"][field] for p in pairs)
                for field in ("time", "reporter", "certainty", "polarity", "coverage")
            },
            "machine_seconds": None,
            "human_minutes": None,
        }
    return {
        "date": "2026-09-10",
        "scope": "authored development pilot and saved primary attempts only",
        "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "temporal_flagged_pairs_reviewed": len(reviewed),
        "temporal_unreviewed": 0,
        "case_checks": cases,
        "query_status_counts": distribution,
        "query_minimums_met": all(
            all(c[s] >= 2 for s in ("eligible", "ineligible", "indeterminate"))
            for c in distribution.values()
        ),
        "attempts": attempts,
        "attempt_counts": dict(Counter(a["status"] for a in attempts)),
        "successful_job_wall_seconds": {
            "n": len(timings),
            "sum": sum(timings),
            "min": min(timings),
            "median": statistics.median(timings),
            "p90_nearest_rank": timings[math.ceil(0.9 * len(timings)) - 1],
            "max": max(timings),
        },
        "failed_job_wall_seconds": [a["wall_seconds"] for a in attempts if a["status"] != "parsed"],
        "family_review": by_family,
        "human_annotation_minutes": None,
        "human_cost": None,
        "effort_decision": (
            "Human effort and within-call family time are not identifiable from saved captures. "
            "No schema deletion or scale-up claim may use total model wall time as human time."
        ),
        "timing_limit": (
            "Successful call wall time includes CLI overhead and may include interruption; "
            "it is not active inference or annotation labor. Four failed primary calls remain "
            "separate; diagnostic retry excluded."
        ),
    }


if __name__ == "__main__":
    report = summarize()
    (OUT / "review_summary.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("attempts", "case_checks", "family_review")
            },
            indent=2,
        )
    )
