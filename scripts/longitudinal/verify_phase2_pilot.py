"""Verify the Phase 2 evidence package without model calls or clinical adjudication."""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.check_annotations import check_annotations, load_example  # noqa: E402
from scripts.longitudinal.evaluate_query_witnesses import replay  # noqa: E402
from scripts.longitudinal.summarize_timed_annotation_probe import summarize  # noqa: E402
from scripts.longitudinal.verify_patient_case import verify_patient_case  # noqa: E402

OUT = ROOT / "results/longitudinal/pilot_v0.8"


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def verify() -> dict:
    cases = []
    for case in sorted((ROOT / "examples/longitudinal").glob("authored_patient_*")):
        annotations, documents, schema = load_example(case)
        check_annotations(annotations, documents, schema)
        cases.append({"case": case.name, **verify_patient_case(case)})
    assert len(cases) == 12
    for path, digest in read(OUT / "preserved_inputs.json")["sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path

    temporal = read(ROOT / "results/longitudinal/pilot_v0.7/temporal_adjudication.json")
    source_path = ROOT / "results/longitudinal/pilot_v0.5/temporal_relationship_audit.json"
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == temporal["source_sha256"]
    source = read(source_path)
    expected = {
        (r["job"], r["reference_id"], r["observed_id"])
        for r in source["rows"]
        if r["classification"] not in ("exact", "representation_only")
    }
    reviewed = [
        (j["job"], r["reference_id"], j["observed_id"])
        for r in temporal["reviews"]
        for j in r["jobs"]
    ]
    assert len(reviewed) == len(set(reviewed)) == 144 and set(reviewed) == expected
    assert all(r["decision"] and r["reason"] for r in temporal["reviews"])

    links = read(OUT / "link_adjudication.json")
    source_path = ROOT / links["source"]
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == links["source_sha256"]
    source = read(source_path)
    expected = {
        (j["job"], link["origin"], link["link"]["link_id"])
        for j in source["jobs"]
        for link in j["links"]
        if not link["aligned"]
    }
    reviewed_links = [
        (i["job"], i["origin"], i["link_id"]) for r in links["reviews"] for i in r["instances"]
    ]
    assert len(reviewed_links) == len(set(reviewed_links)) == 89
    assert set(reviewed_links) == expected
    assert all(r["decision"] and r["reason"] for r in links["reviews"])

    query = read(OUT / "query_field_ablation.json")
    assert query == replay(), "Query replay drift"
    mechanism = read(OUT / "query_mechanism_review.json")
    assert (
        hashlib.sha256((OUT / "query_field_ablation.json").read_bytes()).hexdigest()
        == mechanism["source_sha256"]
    )
    gaps = {
        (r["case"], r["request_id"])
        for r in query["rows"]
        if r["variant"] == "full" and r["status"] != r["reference_status"]
    }
    assert gaps == {(r["case"], r["request_id"]) for r in mechanism["reviews"]}

    timed = read(OUT / "timed_pass/analysis.json")
    assert read(OUT / "timed_pass/manifest.json")["status"] == "captured"
    assert timed == summarize(), "Timing replay drift"
    assert len(timed["jobs"]) == 18
    assert all(r["capture_status"] == "parsed" for r in timed["jobs"])
    assert all(a["parsed"] == 3 for a in timed["by_activity"].values())
    config = read(ROOT / "configs/longitudinal/seed_free_pilot.json")
    for path, digest in config["pinned_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    return {
        "scope": "Internal synthetic-development Phase 2 evidence; no expert validation",
        "case_checks": cases,
        "source_letters_and_query_references_preserved": 48,
        "temporal_pairs_reviewed": len(reviewed),
        "unaligned_link_instances_reviewed": len(reviewed_links),
        "query_replay_matches": sum(
            v["reference_matches"] for v in query["summary"]["full"].values()
        ),
        "query_replay_requests": 240,
        "explicit_query_mechanism_gaps": len(gaps),
        "timed_calls": len(timed["jobs"]),
        "timed_capture_counts": dict(Counter(r["capture_status"] for r in timed["jobs"])),
        "query_and_timing_replay_equal": True,
        "generation_config_hashes_match": True,
        "human_effort_measured": False,
        "clinical_validation": False,
    }


if __name__ == "__main__":
    result = verify()
    (OUT / "completion_checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "case_checks"}, indent=2))
