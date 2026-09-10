"""Audit saved independent outputs without repairing clinical meaning or references."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.longitudinal.check_annotations import (  # noqa: E402
    check_annotations,
    evidence_overlap,
    grounded_span,
)

PACK = ROOT / "results/longitudinal/pilot_v0.3/independent_pass"
PASS = ROOT / "results/longitudinal/pilot_v0.3/agy_pass_medium"
STATUSES = {"eligible", "ineligible", "indeterminate"}


def valid_span(span: dict, documents: dict) -> bool:
    try:
        source = documents[span["letter_id"]]["text"]
        start, end = span["start"], span["end"]
        return (
            type(start) is int
            and type(end) is int
            and 0 <= start < end <= len(source)
            and source[start:end] == span["text"]
        )
    except (KeyError, TypeError):
        return False


def audit_answers(expected: list[dict], observed: list[dict], documents: dict) -> list[dict]:
    rows = []
    for reference in expected:
        found = [
            a
            for a in observed
            if isinstance(a, dict) and a.get("request_id") == reference["request_id"]
        ]
        answer = found[0] if len(found) == 1 else {}
        evidence = answer.get("evidence")
        valid = (
            isinstance(answer.get("status"), str)
            and answer.get("status") in STATUSES
            and isinstance(answer.get("reason"), str)
            and bool(answer["reason"].strip())
            and isinstance(evidence, list)
        )
        rows.append(
            {
                "request_id": reference["request_id"],
                "reference_status": reference["status"],
                "observed_status": answer.get("status") if valid else None,
                "status_agrees": bool(valid and answer["status"] == reference["status"]),
                "answer_valid": valid,
                "answer_count": len(found),
                "evidence_valid": bool(
                    valid and all(grounded_span(e, documents) for e in evidence)
                ),
                "offsets_valid": bool(valid and all(valid_span(e, documents) for e in evidence)),
                "evidence_overlaps_reference": (
                    bool(valid and evidence)
                    and all(
                        grounded_span(e, documents)
                        and any(
                            grounded_span(ref, documents) and evidence_overlap(e, ref)
                            for ref in reference.get("evidence", [])
                        )
                        for e in evidence
                    )
                ),
                "evidence_count": len(evidence) if isinstance(evidence, list) else 0,
                "reference_reason": reference.get("reason"),
                "observed_reason": answer.get("reason"),
            }
        )
    return rows


def assertion_key(assertion: dict) -> str:
    """Literal content match, not semantic equivalence or adjudication."""
    return json.dumps([assertion["letter_id"], assertion["content"]], sort_keys=True)


def compare_assertions(reference: dict, observed: dict, documents: dict) -> dict:
    ref = [a for a in reference["assertions"] if a["letter_id"] in documents]
    pred = observed.get("assertions", [])
    by_ref, by_pred = defaultdict(list), defaultdict(list)
    for a in ref:
        by_ref[assertion_key(a)].append(a)
    for a in pred:
        if isinstance(a, dict) and "letter_id" in a and "content" in a:
            by_pred[assertion_key(a)].append(a)
    matched = [
        (items[0], by_pred[key][0])
        for key, items in by_ref.items()
        if len(items) == 1 and len(by_pred[key]) == 1
    ]
    fields = ("time", "reporter", "certainty", "polarity", "coverage")
    detail = [
        {
            "reference_id": a["assertion_id"],
            "observed_id": b.get("assertion_id"),
            "family": a["content"]["family"],
            "field_agreement": {field: a[field] == b.get(field) for field in fields},
        }
        for a, b in matched
    ]
    # Link equality is evaluated only where both endpoints have a unique literal
    # content match. Ambiguous or differently worded endpoints remain unaligned.
    endpoint_map = {b.get("assertion_id"): a["assertion_id"] for a, b in matched}
    matched_ref = set(endpoint_map.values())
    expected_links = [
        link
        for link in reference["links"]
        if link["earlier_assertion"] in matched_ref
        and link["later_assertion"] in matched_ref
        and all(e["letter_id"] in documents for e in link["evidence"])
    ]
    predicted_links = [
        link
        for link in observed.get("links", [])
        if isinstance(link, dict)
        and link.get("earlier_assertion") in endpoint_map
        and link.get("later_assertion") in endpoint_map
    ]
    expected_keys = Counter(
        (link["earlier_assertion"], link["later_assertion"], link["relation"])
        for link in expected_links
    )
    predicted_keys = Counter(
        (
            endpoint_map[link["earlier_assertion"]],
            endpoint_map[link["later_assertion"]],
            link.get("relation"),
        )
        for link in predicted_links
    )
    families = sorted({a["content"]["family"] for a in ref})
    return {
        "matching_rule": "unique identical letter_id and entire content object; no synonym mapping",
        "reference_assertions": len(ref),
        "observed_assertions": len(pred),
        "matched_assertions": len(matched),
        "matched_details": detail,
        "by_family": {
            f: {
                "reference": sum(a["content"]["family"] == f for a in ref),
                "observed": sum(
                    a.get("content", {}).get("family") == f for a in pred if isinstance(a, dict)
                ),
                "matched": sum(d["family"] == f for d in detail),
                "field_agreement_counts": {
                    field: sum(d["field_agreement"][field] for d in detail if d["family"] == f)
                    for field in fields
                },
            }
            for f in families
        },
        "link_comparison_on_matched_endpoints": {
            "reference": len(expected_links),
            "observed": len(predicted_links),
            "exact_relation_matches": sum((expected_keys & predicted_keys).values()),
        },
        "interpretation": (
            "limited literal representation comparison; not clinical agreement or kappa"
        ),
    }


def analyze() -> dict:
    jobs = json.loads((PACK / "manifest.json").read_text())["jobs"]
    rows, audits = [], []
    for job in jobs:
        input_path = PACK / job["input"]
        case_name, stem = input_path.parent.name, input_path.stem
        case = ROOT / "examples/longitudinal" / case_name
        reference = json.loads(
            (PACK.parent / "reference_snapshot" / case_name / "reference.json").read_text()
        )
        expected = [a for a in reference["answers"] if a["request_id"] in job["request_ids"]]
        ref_spans = {e["evidence_id"]: e for e in reference["evidence"]}
        expected = [{**a, "evidence": [ref_spans[e] for e in a["evidence_ids"]]} for a in expected]
        source = json.loads(input_path.read_text())
        documents = {d["letter_id"]: d for d in source["documents"]}
        attempt = PASS / "attempts" / case_name / stem
        meta = (
            json.loads((attempt / "attempt.json").read_text())
            if (attempt / "attempt.json").exists()
            else {}
        )
        output = (
            json.loads((attempt / "parsed.json").read_text())
            if meta.get("status") == "parsed"
            else {}
        )
        annotations = output.get("annotations", {})
        annotation_error = None
        try:
            check_annotations(
                annotations, documents, source["annotation_schema"], require_offsets=False
            )
        except (ValueError, KeyError, TypeError) as error:
            annotation_error = str(error)
        observed = output.get("answers", [])
        observed = observed if isinstance(observed, list) else []
        for row in audit_answers(expected, observed, documents):
            rows.append(
                {
                    "case_id": job["case_id"],
                    "job": f"{case_name}/{stem}",
                    "capture_status": meta.get("status", "not_started"),
                    **row,
                }
            )
        comparison = None
        schema_errors = list(
            Draft202012Validator(
                source["annotation_schema"], format_checker=FormatChecker()
            ).iter_errors(annotations)
        )
        if not schema_errors:
            comparison = compare_assertions(
                json.loads((case / "annotations.json").read_text()), annotations, documents
            )
        evidence_diagnostics = defaultdict(
            lambda: Counter(total=0, quote_present=0, offsets_valid=0)
        )
        if not schema_errors:
            for assertion in annotations["assertions"]:
                family = assertion["content"]["family"]
                for span in assertion["evidence"]:
                    group = evidence_diagnostics[family]
                    group["total"] += 1
                    group["offsets_valid"] += valid_span(span, documents)
                    group["quote_present"] += bool(
                        span["letter_id"] in documents
                        and span["text"] in documents[span["letter_id"]]["text"]
                    )
        audits.append(
            {
                "case_id": job["case_id"],
                "job": f"{case_name}/{stem}",
                "capture_status": meta.get("status", "not_started"),
                "annotation_error": annotation_error,
                "schema_error": schema_errors[0].message if schema_errors else None,
                "assertion_evidence_by_family": dict(evidence_diagnostics),
                "comparison": comparison,
                "wall_seconds": meta.get("wall_seconds"),
                "usage": meta.get("telemetry", {}).get("usage"),
            }
        )
    patients = sorted({r["case_id"] for r in rows})
    scores = {p: sum(r["status_agrees"] for r in rows if r["case_id"] == p) / 20 for p in patients}
    query_view = defaultdict(lambda: Counter(total=0, agree=0))
    confusion = Counter()
    for r in rows:
        _, view, query = r["request_id"].split("_")
        query_view[f"{query}/{view}"]["total"] += 1
        query_view[f"{query}/{view}"]["agree"] += r["status_agrees"]
        confusion[f"{r['reference_status']} -> {r['observed_status'] or 'invalid_or_missing'}"] += 1
    return {
        "dataset": "authored longitudinal pilot v0.3",
        "split": "development_only",
        "claim": "AI agreement with authored references, not clinical accuracy",
        "semantic_repair": False,
        "evidence_policy": (
            "v2: normalized source grounding; same-letter containment overlap; "
            "offsets diagnostic only"
        ),
        "status_rows": len(rows),
        "captured_jobs": sum(a["capture_status"] == "parsed" for a in audits),
        "total_jobs": len(jobs),
        "patient_scores": scores
        if all(a["capture_status"] != "not_started" for a in audits)
        else None,
        "patient_averaged_status_agreement": (
            sum(scores.values()) / len(scores)
            if all(a["capture_status"] != "not_started" for a in audits)
            else None
        ),
        "pass_complete": all(a["capture_status"] != "not_started" for a in audits),
        "confusion": dict(confusion),
        "by_query_view": dict(query_view),
        "valid_answer_evidence_rows": sum(r["evidence_valid"] for r in rows),
        "schema_and_evidence_valid_annotation_jobs": sum(
            a["annotation_error"] is None for a in audits
        ),
        "disagreements": [
            r
            for r in rows
            if r["capture_status"] == "parsed" and r["answer_valid"] and not r["status_agrees"]
        ],
        "unrun_requests": sum(r["capture_status"] == "not_started" for r in rows),
        "rows": rows,
        "job_audits": audits,
        "human_annotation_effort": None,
        "kappa": None,
        "field_utility": None,
    }


if __name__ == "__main__":
    report = analyze()
    (PASS / "analysis_evidence_v2.json").write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "captured_jobs",
                    "total_jobs",
                    "status_rows",
                    "patient_averaged_status_agreement",
                    "schema_and_evidence_valid_annotation_jobs",
                )
            }
        )
    )
