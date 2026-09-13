"""One vertical slice protects the new history/query and replay boundaries.

Admission: these are the declared Phase 4 semantic obligations, not additional
cases for the frozen pilot diagnostic. No locked records or model calls.
"""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from clinical_extraction.longitudinal.evidence import normalize_evidence
from clinical_extraction.longitudinal.history import link_assertions
from clinical_extraction.longitudinal.queries import evaluate_query
from scripts.longitudinal.check_annotations import load_example


def test_declared_phase4_mechanisms_with_reference_facts_and_links() -> None:
    phase2 = json.loads(
        Path("results/longitudinal/pilot_v0.8/query_mechanism_review.json").read_text()
    )
    phase3 = json.loads(Path("results/longitudinal/generation_v0.1/summary.json").read_text())
    cases = [
        (Path("examples/longitudinal") / r["case"], r["request_id"]) for r in phase2["reviews"]
    ]
    cases += [
        (Path("results/longitudinal/generation_v0.1/cases") / r["patient_id"], r["request_id"])
        for r in phase3["diagnostic_rows"]
    ]
    assert len(cases) == 44
    failures = []
    for case, rid in cases:
        annotations, docs, _ = load_example(case)
        request = next(
            r
            for r in json.loads((case / "manifest.json").read_text())["requests"]
            if r["request_id"] == rid
        )
        expected = next(
            r
            for r in json.loads((case / "reference.json").read_text())["answers"]
            if r["request_id"] == rid
        )
        permitted = {
            k: d for k, d in docs.items() if d["available_date"] <= request["information_cutoff"]
        }
        facts = [a for a in annotations["assertions"] if a["letter_id"] in permitted]
        inferred = evaluate_query(
            {"assertions": facts, "links": link_assertions(facts, permitted)}, permitted, request
        )
        assert inferred["status"] == expected["status"]
        result = evaluate_query(annotations, docs, request)
        if result["status"] != expected["status"]:
            failures.append((case.name, rid, result["status"], expected["status"]))
        for span in result["evidence"]:
            assert docs[span["letter_id"]]["text"][span["start"] : span["end"]] == span["text"]
            assert docs[span["letter_id"]]["available_date"] <= request["information_cutoff"]
    assert failures == []


def test_linked_correction_changes_retrospective_not_visit_and_preserves_inputs() -> None:
    case = Path("examples/longitudinal/authored_patient_001")
    annotations, docs, _ = load_example(case)
    original = deepcopy(annotations)
    requests = json.loads((case / "manifest.json").read_text())["requests"]
    results = []
    for view in ("visit", "retrospective"):
        request = next(r for r in requests if r["request_id"] == f"T1_{view}_Q2")
        permitted = {
            k: v for k, v in docs.items() if v["available_date"] <= request["information_cutoff"]
        }
        assertions = [a for a in annotations["assertions"] if a["letter_id"] in permitted]
        linked = link_assertions(assertions, permitted)
        results.append(
            evaluate_query({"assertions": assertions, "links": linked}, permitted, request)
        )
    assert [r["status"] for r in results] == ["eligible", "ineligible"]
    assert annotations == original
    assert all(e["letter_id"] == "L1" for e in results[0]["evidence"])
    assert any(e["letter_id"] == "L2" for e in results[1]["evidence"])


def test_negative_scope_and_evidence_repair_remain_conservative() -> None:
    case = Path("results/longitudinal/generation_v0.1/cases/generated-004")
    annotations, docs, _ = load_example(case)
    req = next(
        r
        for r in json.loads((case / "manifest.json").read_text())["requests"]
        if r["request_id"] == "T2_retrospective_Q4"
    )
    assert evaluate_query(annotations, docs, req)["status"] == "indeterminate"
    raw = deepcopy(annotations)
    raw["assertions"][0]["evidence"][0]["start"] = 0
    normalized, changes = normalize_evidence(raw, docs)
    assert normalized == annotations
    assert changes and raw != annotations
    assert normalized["assertions"][0]["content"] == raw["assertions"][0]["content"]
    raw["assertions"][0]["evidence"][0]["text"] = "Invented clinical fact"
    with pytest.raises(ValueError, match="evidence"):
        normalize_evidence(raw, docs)


def test_replay_refuses_changed_inputs_and_retains_failures_and_unknowns() -> None:
    """Admission: the saved-extraction boundary cannot substitute gold or future facts."""
    from clinical_extraction.longitudinal.evidence import load_case
    from clinical_extraction.longitudinal.pipeline import saved_extraction
    from clinical_extraction.longitudinal.temporal import holiday_inside, within

    case = Path("examples/longitudinal/authored_patient_001")
    manifest, documents, annotations = load_case(case)
    permitted = {"L1": documents["L1"]}
    replay = saved_extraction(Path("."), case.name, "T1_visit", permitted, manifest["case_id"])
    assert replay["status"] == "ready"
    assert replay["provenance"]["new_model_calls"] == 0
    assert replay["annotations"]["links"] == []
    changed = deepcopy(permitted)
    changed["L1"]["text"] += " Changed input."
    assert (
        saved_extraction(Path("."), case.name, "T1_visit", changed, manifest["case_id"])["status"]
        == "failed"
    )
    other = Path("examples/longitudinal/authored_patient_005")
    m, docs, facts = load_case(other)
    failed = saved_extraction(Path("."), other.name, "T1_visit", {"L1": docs["L1"]}, m["case_id"])
    assert failed["status"] == "failed" and "Original model capture failed" in failed["error"]
    christmas = next(a for a in facts["assertions"] if a["assertion_id"] == "L1.christmas")
    assert not within(christmas["time"], "2024-11-04", "2025-02-01")
    assert not holiday_inside(christmas, docs, "2024-12-20", "2025-01-15")

    request = next(r for r in manifest["requests"] if r["request_id"] == "T1_visit_Q3")
    assert evaluate_query(annotations, documents, request)["status"] == "indeterminate"
    # A later quote attached to an earlier assertion cannot cross the cutoff.
    contaminated = deepcopy(annotations)
    prior = next(
        a
        for a in contaminated["assertions"]
        if a["letter_id"] == "L1" and a["content"].get("status") == "proposed"
    )
    prior["content"]["status"] = "not_started"
    prior["coverage"] = "complete"
    prior["all_prior_history_evidence"] = [
        next(a for a in annotations["assertions"] if a["letter_id"] == "L2")["evidence"][0]
    ]
    result = evaluate_query(contaminated, documents, request)
    assert result["status"] == "indeterminate"
    assert all(e["letter_id"] == "L1" for e in result["evidence"])

    # Narrow predicted quotations still link the expressly disputed reports in
    # their common source paragraph; the extraction itself remains unchanged.
    disputed = Path("examples/longitudinal/authored_patient_006")
    dm, dd, _ = load_case(disputed)
    predicted = saved_extraction(
        Path("."), disputed.name, "T1_visit", {"L1": dd["L1"]}, dm["case_id"]
    )
    dr = next(r for r in dm["requests"] if r["request_id"] == "T1_visit_Q1")
    extracted = predicted["annotations"]["assertions"]
    linked = link_assertions(extracted, {"L1": dd["L1"]})
    assert (
        evaluate_query({"assertions": extracted, "links": linked}, dd, dr)["status"]
        == "indeterminate"
    )

    # Equal event names alone do not establish cross-letter identity. A copied
    # historical account links as repetition without moving the occurrence date.
    from clinical_extraction.longitudinal.evidence import normalize_evidence

    pair = [deepcopy(extracted[1]), deepcopy(extracted[1])]
    pair[0]["assertion_id"], pair[1]["assertion_id"] = "earlier", "later"
    pair[0]["letter_id"], pair[1]["letter_id"] = "L1", "L2"
    for a in pair:
        a["evidence"] = [
            {"letter_id": a["letter_id"], "start": 0, "end": 16, "text": "An event report."}
        ]
    simple_docs = {
        "L1": {
            "text": "An event report.",
            "available_date": "2025-01-01",
            "visit_date": "2025-01-01",
        },
        "L2": {
            "text": "An event report.",
            "available_date": "2025-07-01",
            "visit_date": "2025-07-01",
        },
    }
    assert link_assertions(pair, simple_docs) == []
    simple_docs["L2"]["text"] = "Copied history: An event report."
    pair[1]["evidence"][0].update(text=simple_docs["L2"]["text"])
    normalized, _ = normalize_evidence({"assertions": pair, "links": []}, simple_docs)
    copied = link_assertions(normalized["assertions"], simple_docs)
    assert [edge["relation"] for edge in copied] == ["repeats"]
    assert normalized["assertions"][1]["time"] == pair[0]["time"]
