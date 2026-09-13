"""The provisional longitudinal format must preserve evidence and time boundaries.

Always-on admission: this new track has no existing schema/evidence coverage.
These checks protect authored references from invalid spans, reversed bounds and
future evidence; they do not test clinical correctness or old benchmark labels.
"""

import json
import shutil
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.longitudinal.check_annotations import check_annotations, load_example

EXAMPLE = Path("examples/longitudinal/authored_patient_001")


def test_authored_annotations_preserve_original_sources_and_all_families() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    check_annotations(annotations, documents, schema)
    assert {a["content"]["family"] for a in annotations["assertions"]} == {
        "diagnosis",
        "seizure",
        "medication",
        "investigation",
    }


def test_reject_invalid_evidence_and_future_letter() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    altered["assertions"][0]["evidence"][0]["text"] = "Invented evidence"
    with pytest.raises(ValueError, match="span"):
        check_annotations(altered, documents, schema)
    with pytest.raises(ValueError, match="cutoff"):
        check_annotations(annotations, documents, schema, cutoff="2025-01-15")


def test_reject_reversed_time_and_dangling_link() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    altered["assertions"][0]["time"]["start"] = {"earliest": "2025-02-01", "latest": "2025-01-01"}
    with pytest.raises(ValueError, match="bounds"):
        check_annotations(altered, documents, schema)
    altered = deepcopy(annotations)
    altered["links"][0]["earlier_assertion"] = "missing"
    with pytest.raises(ValueError, match="endpoint"):
        check_annotations(altered, documents, schema)


def test_preserve_unknown_and_cluster_quantities_without_point_imputation() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    seizure = next(a for a in altered["assertions"] if a["content"]["family"] == "seizure")
    # Shape probe only: the source sentence is not claimed to support these values.
    seizure["content"]["burden"] = {
        "kind": "clusters",
        "text": "unknown spacing, 2 to 4 events per cluster",
        "count": {"lower": None, "upper": None},
        "period": None,
        "events_per_cluster": {"lower": 2, "upper": 4},
        "approximate": False,
    }
    check_annotations(altered, documents, schema)
    assert seizure["content"]["burden"]["count"]["lower"] is None
    seizure["content"]["burden"]["events_per_cluster"]["lower"] = 5
    with pytest.raises(ValueError, match="quantity"):
        check_annotations(altered, documents, schema)


def test_all_pilot_cases_pass_verification() -> None:
    from scripts.longitudinal.verify_patient_case import verify_patient_case

    pilot_cases = sorted(Path("examples/longitudinal").glob("authored_patient_*"))
    assert len(pilot_cases) == 12
    for case_dir in pilot_cases:
        report = verify_patient_case(case_dir)
        assert report["documents"] == 3
        assert report["requests"] == 20
        assert report["answers"] == 20
        assert report["annotations_checked"] is True
        annotations, documents, _ = load_example(case_dir)
        annotated = {a["letter_id"] for a in annotations["assertions"]}
        manifest = json.loads((case_dir / "manifest.json").read_text())
        no_assertions = manifest.get("annotation", {}).get("no_assertion_letters", {})
        assert annotated.isdisjoint(no_assertions)
        assert annotated | set(no_assertions) == set(documents)
        assert all(reason.strip() for reason in no_assertions.values())


@pytest.mark.parametrize(
    "defect", ["input_text", "input_date", "duplicate_request", "schedule", "link", "bounds"]
)
def test_case_verifier_rejects_broken_contract(tmp_path: Path, defect: str) -> None:
    # Admission: exercise the public case validator, replacing a happy-path-only
    # assumption with corruption checks for the same pilot validity obligation.
    from scripts.longitudinal.verify_patient_case import verify_patient_case

    target = tmp_path / "patient"
    shutil.copytree(EXAMPLE, target)
    if defect.startswith("input"):
        path = target / "inputs/T1_visit.json"
        value = json.loads(path.read_text())
        key = "text" if defect == "input_text" else "visit_date"
        value["documents"][0][key] = "later information" if key == "text" else "2026-01-01"
    elif defect in {"duplicate_request", "schedule"}:
        path = target / "manifest.json"
        value = json.loads(path.read_text())
        if defect == "duplicate_request":
            value["requests"][1] = value["requests"][0]
        else:
            value["requests"][0]["retrospective_cutoff"] = "2026-01-01"
    else:
        path = target / "annotations.json"
        value = json.loads(path.read_text())
        if defect == "link":
            value["links"][0]["earlier_assertion"] = "missing"
        else:
            value["assertions"][0]["time"]["start"] = {
                "earliest": "2025-02-01",
                "latest": "2025-01-01",
            }
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        verify_patient_case(target)


def test_pilot_summary_does_not_substitute_measurements() -> None:
    from scripts.longitudinal.run_pilot_scoring_dry_run import summarize_pilot

    report = summarize_pilot(Path("examples/longitudinal"))
    assert report["total_requests"] == 240
    # Task-defined minimum, not a desired class balance or a fitted outcome.
    assert all(n >= 2 for row in report["query_breakdown"].values() for n in row.values())
    assert report["inter_annotator_agreement"] is None
    assert report["effort_analysis"] is None
    assert report["field_cost_utility"] is None
    assert report["independent_pass_status"] == "not_performed"
    counts = report["overall_status_distribution"]
    assert report["constant_baselines"]["indeterminate"][
        "patient_averaged_accuracy"
    ] == pytest.approx(counts["indeterminate"] / 240)


def test_agy_trace_requires_tool_free_success_and_valid_json() -> None:
    # Admission: new external annotation adapter must not accept tool-assisted
    # or failed output as an independent response.
    from scripts.longitudinal.run_agy_annotation_pass import decode_trace

    events = [
        {"event": "init", "init": {"model": "test", "tools": ["view_file"]}},
        {"event": "step_update", "step_update": {"step_type": "agent_response"}},
        {"event": "result", "result": {"status": "SUCCESS", "response": '{"answers": []}'}},
    ]
    assert decode_trace(events)[0] == {"answers": []}
    events.insert(1, {"event": "step_update", "step_update": {"step_type": "tool_call"}})
    with pytest.raises(ValueError, match="tool"):
        decode_trace(events)
    events.pop(1)
    events[-1]["result"]["status"] = "ERROR"
    with pytest.raises(ValueError, match="successful"):
        decode_trace(events)


def test_independent_answer_audit_keeps_status_and_evidence_separate() -> None:
    # Admission: primary agreement must count missing/duplicate answers as failures,
    # while evidence validity stays an independently visible diagnostic.
    from scripts.longitudinal.analyze_agy_annotation_pass import audit_answers

    expected = [{"request_id": "q", "status": "eligible"}]
    document = {"L1": {"text": "actual source"}}
    answer = {
        "request_id": "q",
        "status": "eligible",
        "reason": "Supported",
        "evidence": [{"letter_id": "L1", "start": 0, "end": 4, "text": "fake"}],
    }
    row = audit_answers(expected, [answer], document)[0]
    assert row["status_agrees"] is True
    assert row["evidence_valid"] is False
    assert audit_answers(expected, [], document)[0]["status_agrees"] is False
    assert audit_answers(expected, [answer, answer], document)[0]["status_agrees"] is False


def test_adjudicated_negatives_distinguish_seizure_freedom_from_revision_history() -> None:
    # Admission: pin the reviewed reference boundary absent from structural checks;
    # seizure freedom refutes active patterns but does not inventory reclassifications.
    def answers(patient: str) -> dict:
        path = Path("examples/longitudinal") / patient / "reference.json"
        return {a["request_id"]: a["status"] for a in json.loads(path.read_text())["answers"]}

    ordinary = answers("authored_patient_002")
    copied = answers("authored_patient_003")
    assert ordinary["T2_retrospective_Q2"] == "indeterminate"
    assert ordinary["T2_retrospective_Q4"] == "indeterminate"
    assert copied["T2_retrospective_Q2"] == "ineligible"
    assert copied["T1_visit_Q5"] == "indeterminate"
    assert copied["T1_retrospective_Q5"] == "indeterminate"
    holiday = answers("authored_patient_005")
    for view in ("visit", "retrospective"):
        assert holiday[f"T1_{view}_Q1"] == "eligible"
        assert holiday[f"T1_{view}_Q2"] == "ineligible"
    assert holiday["T2_retrospective_Q2"] == "indeterminate"
    medication = answers("authored_patient_010")
    assert medication["T2_retrospective_Q3"] == "ineligible"
    assert medication["T2_visit_Q3"] == "indeterminate"


def test_evidence_grounding_and_overlap_do_not_require_offsets() -> None:
    # Admission: extends evidence validity coverage to the approved relaxed boundary.
    from scripts.longitudinal.analyze_agy_annotation_pass import audit_answers

    documents = {"L1": {"text": "She reports no seizures since May."}}
    span = {"letter_id": "L1", "start": 999, "end": 1000, "text": "no seizures since May"}
    expected = [
        {
            "request_id": "q",
            "status": "ineligible",
            "evidence": [{"letter_id": "L1", "text": "She reports no seizures since May."}],
        }
    ]
    answer = {
        "request_id": "q",
        "status": "ineligible",
        "reason": "Whole window",
        "evidence": [span],
    }
    row = audit_answers(expected, [answer], documents)[0]
    assert row["evidence_valid"] is True
    assert row["evidence_overlaps_reference"] is True
    assert row["offsets_valid"] is False
    span["letter_id"] = "L2"
    assert audit_answers(expected, [answer], documents)[0]["evidence_valid"] is False


def test_temporal_audit_ignores_wording_but_preserves_clinical_time() -> None:
    # Admission: narrow existing time-validity coverage to semantic comparison;
    # a decision date must never silently replace an occurrence interval.
    from scripts.longitudinal.audit_temporal_relationships import compare_time

    source = {
        "text": "never",
        "start": None,
        "end": None,
        "kind": "active_interval",
        "anchor_letter_id": "L1",
    }
    variant = {**source, "text": "at no time", "start": {"earliest": None, "latest": None}}
    assert compare_time(source, variant) == "representation_only"
    assert compare_time(source, {**variant, "kind": "decision"}) == "kind_or_anchor_difference"
    variant["end"] = {"earliest": "2025-01-01", "latest": "2025-01-01"}
    assert compare_time(source, variant) == "bounds_difference"


def test_q5_evaluator_requires_permitted_correction_and_decision_time() -> None:
    # Admission: first executable query slice; protects cutoff and causal field removal.
    from scripts.longitudinal.evaluate_q5_slice import evaluate_q5

    annotations, documents, _ = load_example(EXAMPLE)
    request = {
        "query_id": "Q5",
        "index_date": "2025-07-14",
        "information_cutoff": "2025-07-14",
        "lookback_180_start": "2025-01-16",
    }
    assert evaluate_q5(annotations, documents, request)["status"] == "eligible"
    altered = deepcopy(annotations)
    altered["links"] = []
    assert evaluate_q5(altered, documents, request)["status"] == "indeterminate"
    altered = deepcopy(annotations)
    altered["links"][0]["decision_time"] = None
    assert evaluate_q5(altered, documents, request)["status"] == "indeterminate"
    earlier = {**request, "index_date": "2025-01-15", "lookback_180_start": "2024-07-20"}
    assert evaluate_q5(annotations, documents, earlier)["status"] == "ineligible"
    assert (
        evaluate_q5(annotations, documents, {**earlier, "information_cutoff": "2025-01-15"})[
            "status"
        ]
        == "indeterminate"
    )
    altered = deepcopy(annotations)
    altered["links"].append({**altered["links"][0], "relation": "contradicts"})
    assert evaluate_q5(altered, documents, request)["status"] == "indeterminate"

    altered = deepcopy(annotations)
    altered["links"][0].pop("first_reinterpretation_evidence", None)
    assert evaluate_q5(altered, documents, earlier)["status"] == "indeterminate"
    altered["links"][0]["first_reinterpretation_evidence"] = [
        {"letter_id": "L2", "text": "invented first revision claim"}
    ]
    assert evaluate_q5(altered, documents, earlier)["status"] == "indeterminate"
    altered = deepcopy(annotations)
    altered["links"][0]["decision_time"]["start"] = {
        "earliest": "2025-01-14",
        "latest": "2025-01-16",
    }
    altered["links"][0]["decision_time"]["end"] = {"earliest": "2025-01-14", "latest": "2025-01-16"}
    assert evaluate_q5(altered, documents, earlier)["status"] == "indeterminate"
    hidden = {**request, "information_cutoff": "2025-01-15"}
    with pytest.raises(ValueError, match="cutoff"):
        evaluate_q5(annotations, documents, hidden)
    altered = deepcopy(annotations)
    altered["links"][0]["certainty"] = "uncertain"
    assert evaluate_q5(altered, documents, request)["status"] == "indeterminate"
    altered = deepcopy(annotations)
    # A possible occurrence crossing the first day is not definitely in scope.
    for a in altered["assertions"]:
        if a["assertion_id"] in ("L1.staring", "L2.staring"):
            a["time"] = {
                "kind": "occurrence",
                "text": "boundary probe",
                "anchor_letter_id": None,
                "start": {"earliest": "2025-01-15", "latest": "2025-01-16"},
                "end": {"earliest": "2025-01-15", "latest": "2025-01-16"},
            }
    assert evaluate_q5(altered, documents, request)["status"] == "indeterminate"
    for a in altered["assertions"]:
        if a["assertion_id"] in ("L1.staring", "L2.staring"):
            a["time"]["start"] = a["time"]["end"] = {
                "earliest": "2025-01-16",
                "latest": "2025-01-16",
            }
    assert evaluate_q5(altered, documents, request)["status"] == "eligible"


def test_query_witnesses_keep_plans_dates_and_evidence_separate() -> None:
    # Admission: new Q1-Q4 witness path needs one boundary check per new mechanism.
    from scripts.longitudinal.evaluate_query_witnesses import evaluate_query

    case = Path("examples/longitudinal/authored_patient_010")
    annotations, documents, _ = load_example(case)
    requests = {
        r["request_id"]: r for r in json.loads((case / "manifest.json").read_text())["requests"]
    }
    assert (
        evaluate_query(annotations, documents, requests["T1_visit_Q3"])["status"] == "indeterminate"
    )
    assert (
        evaluate_query(annotations, documents, requests["T1_retrospective_Q3"])["status"]
        == "eligible"
    )
    assert (
        evaluate_query(annotations, documents, requests["T2_visit_Q4"])["status"] == "indeterminate"
    )
    # Directly ask at the clinical-result date, with the reporting letter available later.
    request = {
        **requests["T2_retrospective_Q4"],
        "index_date": "2025-02-16",
        "lookback_180_start": "2024-08-21",
        "lookback_90_start": "2024-11-19",
    }
    assert evaluate_query(annotations, documents, request)["status"] == "eligible"
    no_links = {**annotations, "links": []}
    assert evaluate_query(no_links, documents, request)["status"] == "indeterminate"
    changed = deepcopy(annotations)
    for a in changed["assertions"]:
        if a["content"]["family"] == "investigation" and a["content"]["status"] == "result":
            a["time"]["start"] = a["time"]["end"] = {
                "earliest": "2025-02-17",
                "latest": "2025-02-17",
            }
    assert evaluate_query(changed, documents, request)["status"] == "indeterminate"
    for a in changed["assertions"]:
        a["evidence"] = []
    assert evaluate_query(changed, documents, requests["T1_visit_Q1"])["status"] == "indeterminate"


def test_alignment_preserves_ambiguous_endpoints_and_status() -> None:
    # Admission: same-family paragraph overlap must not force a clinical identity match.
    from scripts.longitudinal.review_pilot_alignment import align_assertions

    a, documents, _ = load_example(EXAMPLE)
    plan = next(x for x in a["assertions"] if x["assertion_id"] == "L1.plan")
    other = deepcopy(plan)
    other["assertion_id"] = "different"
    other["content"]["name"] = "Lamotrigine"
    mapping, candidates = align_assertions([plan], [other], documents)
    assert mapping == {"different": "L1.plan"}
    duplicate = {**plan, "assertion_id": "second"}
    assert align_assertions([plan, duplicate], [other], documents)[0] == {}
    other["content"]["status"] = "started"
    assert align_assertions([plan], [other], documents)[0] == {}


def test_q5_second_case_and_temporal_reference_corrections() -> None:
    # Admission: extends representative Q5 and existing time-kind checks to reviewed defects.
    from scripts.longitudinal.evaluate_q5_slice import evaluate_q5

    case = Path("examples/longitudinal/authored_patient_011")
    annotations, documents, _ = load_example(case)
    requests = {
        r["request_id"]: r for r in json.loads((case / "manifest.json").read_text())["requests"]
    }
    assert (
        evaluate_q5(annotations, documents, requests["T1_retrospective_Q5"])["status"]
        == "ineligible"
    )
    for number in ("005", "010"):
        a, _, _ = load_example(Path(f"examples/longitudinal/authored_patient_{number}"))
        pending = next(x for x in a["assertions"] if x["assertion_id"] == "L1.pending")
        assert pending["time"]["kind"] == "as_of"


def test_query_conflict_cannot_be_bypassed_by_same_pattern_occurrence() -> None:
    # Admission: the first replay exposed a harmful eligible answer from a split assertion.
    from scripts.longitudinal.evaluate_query_witnesses import evaluate_query

    case = Path("examples/longitudinal/authored_patient_006")
    a, docs, _ = load_example(case)
    request = next(
        r
        for r in json.loads((case / "manifest.json").read_text())["requests"]
        if r["request_id"] == "T1_retrospective_Q1"
    )
    assert evaluate_query(a, docs, request)["status"] == "indeterminate"


def test_complete_prior_history_requires_its_own_grounded_evidence() -> None:
    # Admission: pin unknown start versus explicit lifelong scope at the existing evidence boundary.
    from scripts.longitudinal.evaluate_query_witnesses import evaluate_query

    a, docs, schema = load_example(EXAMPLE)
    request = next(
        r
        for r in json.loads((EXAMPLE / "manifest.json").read_text())["requests"]
        if r["request_id"] == "T1_retrospective_Q3"
    )
    no_start = next(x for x in a["assertions"] if x["assertion_id"] == "L2.no_start")
    no_start["all_prior_history_evidence"] = no_start["evidence"]
    check_annotations(a, docs, schema)
    assert evaluate_query(a, docs, request)["status"] == "ineligible"
    no_start["coverage"] = "not_stated"
    with pytest.raises(ValueError, match="Complete prior history"):
        check_annotations(a, docs, schema)
    no_start["coverage"] = "complete"
    visit = {**request, "information_cutoff": request["index_date"]}
    assert evaluate_query(a, docs, visit)["status"] == "indeterminate"
    no_start["all_prior_history_evidence"] = []
    assert evaluate_query(a, docs, request)["status"] == "indeterminate"
    no_start["all_prior_history_evidence"] = [
        {"letter_id": "L2", "start": 0, "end": 5, "text": "invented"}
    ]
    with pytest.raises(ValueError, match="span"):
        check_annotations(a, docs, schema)
