"""Verify authored pilot structure and source integrity, not clinical entailment."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # Allow direct execution from the repository checkout.

from scripts.longitudinal.check_annotations import check_annotations, load_example  # noqa: E402


def expected_requests(first_index: str) -> list[dict[str, Any]]:
    """Task v0.2: two indices and retrospective horizons exactly 180 days apart."""
    requests = []
    for index in (1, 2):
        day = date.fromisoformat(first_index) + timedelta(days=180 * (index - 1))
        retro = day + timedelta(days=180)
        for view in ("visit", "retrospective"):
            for query in range(1, 6):
                requests.append(
                    {
                        "request_id": f"T{index}_{view}_Q{query}",
                        "query_id": f"Q{query}",
                        "parameters": {"medication": "lamotrigine"}
                        if query == 3
                        else {"modality": "EEG"}
                        if query == 4
                        else {},
                        "index_date": day.isoformat(),
                        "view": view,
                        "information_cutoff": (day if view == "visit" else retro).isoformat(),
                        "retrospective_cutoff": retro.isoformat(),
                        "lookback_90_start": (day - timedelta(days=89)).isoformat(),
                        "lookback_180_start": (day - timedelta(days=179)).isoformat(),
                        "input_path": f"inputs/T{index}_{view}.json",
                    }
                )
    return requests


def input_payload(case_id: str, documents: dict, cutoff: str) -> dict:
    return {
        "patient_id": case_id,
        "documents": [
            {key: doc[key] for key in ("letter_id", "visit_date", "available_date", "text")}
            for doc in documents.values()
            if doc["available_date"] <= cutoff
        ],
    }


def unique(items: list[dict], key: str) -> dict:
    result = {item[key]: item for item in items}
    if len(result) != len(items):
        raise ValueError(f"Duplicate {key}")
    return result


def verify_patient_case(case_dir: Path) -> dict[str, Any]:
    manifest = json.loads((case_dir / "manifest.json").read_text())
    annotations, documents, schema = load_example(case_dir)
    check_annotations(annotations, documents, schema)
    if len(documents) != 3:
        raise ValueError("Pilot requires three letters")
    for doc in documents.values():
        if date.fromisoformat(doc["visit_date"]) > date.fromisoformat(doc["available_date"]):
            raise ValueError("Letter available before consultation")
    requests = unique(manifest["requests"], "request_id")
    if "T1_visit_Q1" not in requests:
        raise ValueError("Missing first index")
    expected = expected_requests(requests["T1_visit_Q1"]["index_date"])
    if requests != {r["request_id"]: r for r in expected}:
        raise ValueError("Requests violate fixed schedule, query parameters or coverage")
    for req in expected:
        payload = json.loads((case_dir / req["input_path"]).read_text())
        if payload != input_payload(manifest["case_id"], documents, req["information_cutoff"]):
            raise ValueError(f"Input source or cutoff mismatch: {req['request_id']}")

    reference = json.loads((case_dir / "reference.json").read_text())
    if reference["case_id"] != manifest["case_id"]:
        raise ValueError("Reference patient mismatch")
    evidence = unique(reference["evidence"], "evidence_id")
    for ev in evidence.values():
        if ev["letter_id"] not in documents:
            raise ValueError("Unknown evidence letter")
        source = documents[ev["letter_id"]]["text"]
        start, end = ev["start"], ev["end"]
        if not 0 <= start < end <= len(source) or source[start:end] != ev["text"]:
            raise ValueError("Invalid reference evidence span")
    links = unique(reference["links"], "link_id")
    for link in links.values():
        for eid in [
            link["earlier_evidence"],
            link["later_evidence"],
            *link.get("supporting_evidence", []),
        ]:
            if eid not in evidence:
                raise ValueError("Unknown reference link endpoint/evidence")
    answers = unique(reference["answers"], "request_id")
    if answers.keys() != requests.keys():
        raise ValueError("Answers must cover each request exactly once")
    for rid, answer in answers.items():
        if answer["status"] not in {"eligible", "ineligible", "indeterminate"}:
            raise ValueError("Invalid answer status")
        if not answer.get("reason", "").strip():
            raise ValueError("Missing answer reason")
        for eid in answer["evidence_ids"]:
            if eid not in evidence:
                raise ValueError("Unknown answer evidence")
            available = documents[evidence[eid]["letter_id"]]["available_date"]
            if available > requests[rid]["information_cutoff"]:
                raise ValueError("Answer uses evidence beyond cutoff")
    return {
        "case_dir": str(case_dir),
        "documents": len(documents),
        "requests": len(requests),
        "evidence_spans": len(evidence),
        "answers": len(answers),
        "annotations_checked": True,
        "assertions": len(annotations["assertions"]),
        "links": len(annotations["links"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify_patient_case(args.case_dir), indent=2))


if __name__ == "__main__":
    main()
