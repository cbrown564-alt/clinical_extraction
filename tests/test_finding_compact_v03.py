from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    finding_compact_v03 as compact,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r9 as r9,
)
from scripts.benchmarks.score_compact_findings_v03 import (
    load_reference,
    validate_response,
)

FIXTURES = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_r9_compact_v03_no_call/"
    "v03_fictional_fixtures.json"
)
BASE_FIXTURES = Path(
    "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "fictional_fixtures.json"
)


def test_compact_match_preserves_population_unit_phase_and_reporting_scope() -> None:
    case = json.loads(FIXTURES.read_text())[0]
    note = case["note"]
    gold = case["response"]["findings"]
    assert compact.score_letter(note, gold, copy.deepcopy(gold))["tp"] == 2
    for field, value in (
        ("counted_unit", "seizure_day"),
        ("status", "uncertain"),
    ):
        wrong = copy.deepcopy(gold[0])
        wrong[field] = value
        assert field in compact.attribute_diffs(wrong, gold[0], note)
    wrong_phase = copy.deepcopy(gold[0])
    wrong_phase["time"]["phase"] = "superseded"
    assert "phase" in compact.attribute_diffs(wrong_phase, gold[0], note)
    global_absence = copy.deepcopy(gold[1])
    global_absence.pop("restriction")
    assert "restriction" in compact.attribute_diffs(global_absence, gold[1], note)
    changed_scope = copy.deepcopy(gold[0])
    changed_scope["event"]["scope"] = "overall"
    assert "event" in compact.attribute_diffs(changed_scope, gold[0], note)


def test_measurement_and_evidence_are_scored_without_duplicate_credit() -> None:
    cases = json.loads(FIXTURES.read_text())
    note = cases[1]["note"]
    gold = cases[1]["response"]["findings"]
    duplicate_score = compact.score_letter(note, gold, gold + copy.deepcopy(gold))
    assert (duplicate_score["tp"], duplicate_score["fp"], duplicate_score["fn"]) == (1, 1, 0)
    assert duplicate_score["pairs"] == [[0, 0]]
    assert len(duplicate_score["source_aligned_pairs"]) == 1
    wrong_unit = copy.deepcopy(gold[0])
    wrong_unit["counted_unit"] = "individual_seizure"
    assert compact.score_letter(note, gold, [wrong_unit])["tp"] == 0
    wrong_count = copy.deepcopy(gold[0])
    wrong_count["measurement"]["quantity"]["value"] = 3
    assert "measurement_value" in compact.attribute_diffs(wrong_count, gold[0], note)
    partial = compact.score_letter(note, gold, [wrong_count])
    assert partial["tp"] == 0
    assert partial["source_aligned_pairs"][0]["components"]["measurement_value"] is False
    assert partial["source_aligned_pairs"][0]["components"]["event"] is True
    component_summary = compact.aggregate([partial])
    assert component_summary["source_aligned"]["tp"] == 1
    assert component_summary["components"]["event"]["tp"] == 1
    assert component_summary["components"]["measurement_value"]["tp"] == 0
    wrong_event = copy.deepcopy(gold[0])
    wrong_event["event"]["label"] = "focal seizures"
    event_partial = compact.score_letter(note, gold, [wrong_event])
    event_summary = compact.aggregate([event_partial])
    assert event_summary["components"]["event"]["tp"] == 0
    assert event_summary["components"]["measurement_value"]["tp"] == 1
    wrong_window = copy.deepcopy(gold[0])
    wrong_window["time"]["source"] = "last year"
    assert "window" in compact.attribute_diffs(wrong_window, gold[0], note)
    missing_quote = copy.deepcopy(gold[0])
    missing_quote["evidence"] = ["There were two episodes of status epilepticus."]
    assert "evidence" in compact.attribute_diffs(missing_quote, gold[0], note)
    assert compact.score_letter(note, gold, None)["fn"] == 1


def test_absence_anchor_cluster_size_and_exact_window_remain_distinct() -> None:
    cases = json.loads(BASE_FIXTURES.read_text())
    cluster_case = next(c for c in cases if c["case"].startswith("cluster_days"))
    cluster = cluster_case["response"]["findings"][0]
    wrong_size = copy.deepcopy(cluster)
    wrong_size["measurement"]["seizures_per_cluster"]["value"] = 5
    assert "measurement_value" in compact.attribute_diffs(
        wrong_size, cluster, cluster_case["note"]
    )
    absence_case = next(c for c in cases if c["case"].startswith("subtype_absence"))
    absence = absence_case["response"]["findings"][0]
    other_anchor = copy.deepcopy(absence)
    other_anchor["measurement"]["since"] = "March 2020"
    assert "measurement_value" in compact.attribute_diffs(
        other_anchor, absence, absence_case["note"]
    )
    assert compact.phrase_equal("on 3 June", "3 June")
    assert not compact.phrase_equal("May 2022", "May 2023")


def test_reference_is_frozen_and_invalid_response_is_unusable() -> None:
    references, manifest = load_reference()
    assert manifest["letters"] == 750
    assert manifest["reference_findings"] == 1219
    case = json.loads(FIXTURES.read_text())[0]
    validator = Draft202012Validator(r9.prompt_payload(case["note"])["output_schema"])
    response = copy.deepcopy(case["response"])
    assert validate_response(response, case["note"], validator)[1] is None
    response["answer"]["claim_indices"] = [len(response["findings"])]
    assert validate_response(response, case["note"], validator)[1] == (
        "answer_claim_index_out_of_range"
    )
