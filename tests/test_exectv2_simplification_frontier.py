from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    simplification_frontier,
)


def test_candidate_runner_records_cost_metadata_and_outputs(tmp_path: Path) -> None:
    letters = _letters()
    structured = _write_jsonl(
        tmp_path / "structured.jsonl",
        [_row("EA1"), _row("EA2")],
    )
    config_path = _write_config(
        tmp_path,
        structured=structured,
        output_stem="candidate",
        calls_per_letter=1,
    )

    paths = simplification_frontier.write_simplification_candidate_artifacts(
        config_path,
        generated_on="2026-06-24",
        gold_loader=lambda _split: letters,
    )

    report = json.loads(paths["json"].read_text(encoding="utf-8"))
    meta = report["simplification_frontier"]
    assert meta["calls_per_letter"] == 1
    assert meta["full_200_calls"] == 2
    assert meta["live_call_components"] == ["structured"]
    assert meta["acceptability"]["decision"] == "fail"
    markdown = paths["markdown"].read_text(encoding="utf-8")
    assert "## Simplification Contract" in markdown
    assert "| overall | 0.7500 | 0.8350 | fail |" in markdown


def test_structured_direct_sf_derivative_filters_non_sf_mentions(tmp_path: Path) -> None:
    letters = _letters()
    structured = _write_jsonl(tmp_path / "structured.jsonl", [_row("EA1"), _row("EA2")])
    sf_direct = tmp_path / "sf_direct.jsonl"
    config_path = _write_config(
        tmp_path,
        structured=structured,
        output_stem="candidate",
        calls_per_letter=1,
        derived_artifacts=[
            {
                "kind": "sf_structured_direct",
                "source": str(structured),
                "output": str(sf_direct),
            }
        ],
    )
    config = simplification_frontier.load_simplification_config(config_path)

    simplification_frontier.materialize_derived_artifacts(
        config,
        letters=letters,
        force=True,
    )

    rows = _read_jsonl(sf_direct)
    assert len(rows) == 2
    assert [mention["entity"] for row in rows for mention in row["predicted_mentions"]] == [
        "SeizureFrequency",
        "SeizureFrequency",
    ]
    assert rows[0]["predicted_mentions"][0]["component_owner"] == (
        "single_gpt_structured_no_sf_adjudicator"
    )
    assert rows[0]["source_pipeline_family"] == "toy_structured"


def test_frontier_recommends_lowest_call_passing_candidate() -> None:
    passing_3call = _report(
        candidate_id="threecall",
        calls_per_letter=3,
        overall=0.85,
        diagnosis=0.84,
        sf=0.78,
        prescription=0.89,
        investigations=0.86,
    )
    passing_1call = _report(
        candidate_id="onecall",
        calls_per_letter=1,
        overall=0.841,
        diagnosis=0.831,
        sf=0.771,
        prescription=0.881,
        investigations=0.841,
    )
    failing_1call = _report(
        candidate_id="failed",
        calls_per_letter=1,
        overall=0.834,
        diagnosis=0.84,
        sf=0.78,
        prescription=0.89,
        investigations=0.86,
    )

    payload = simplification_frontier.build_frontier_payload(
        [passing_3call, passing_1call, failing_1call],
        generated_on="2026-06-24",
    )

    assert payload["recommended_candidate"]["candidate_id"] == "onecall"
    decisions = {
        candidate["candidate_id"]: candidate["acceptability"]["decision"]
        for candidate in payload["candidates"]
    }
    assert decisions == {"threecall": "pass", "onecall": "pass", "failed": "fail"}


def test_frontier_accepts_selected_2call_no_sf_cost_profile() -> None:
    threecall = _report(
        candidate_id="threecall",
        calls_per_letter=3,
        overall=0.8426,
        diagnosis=0.8397,
        sf=0.7850,
        prescription=0.8926,
        investigations=0.8563,
    )
    selected_2call = _report(
        candidate_id="exectv2_gpt41mini_simplification_2call_no_sf_adjudicator",
        calls_per_letter=2,
        overall=0.8356,
        diagnosis=0.8397,
        sf=0.7525,
        prescription=0.8926,
        investigations=0.8563,
    )

    payload = simplification_frontier.build_frontier_payload(
        [threecall, selected_2call],
        generated_on="2026-06-24",
    )

    assert payload["recommended_candidate"]["candidate_id"] == (
        "exectv2_gpt41mini_simplification_2call_no_sf_adjudicator"
    )
    decisions = {
        candidate["candidate_id"]: candidate["acceptability"]["decision"]
        for candidate in payload["candidates"]
    }
    assert decisions == {
        "threecall": "pass",
        "exectv2_gpt41mini_simplification_2call_no_sf_adjudicator": "pass",
    }
    selected = next(
        candidate
        for candidate in payload["candidates"]
        if candidate["candidate_id"] == "exectv2_gpt41mini_simplification_2call_no_sf_adjudicator"
    )
    sf_check = next(
        check
        for check in selected["acceptability"]["checks"]
        if check["name"] == "SeizureFrequency"
    )
    assert sf_check == {
        "name": "SeizureFrequency",
        "value": 0.7525,
        "floor": 0.75,
        "passed": True,
    }


def _letters() -> list[ExectLetter]:
    note = (
        "Diagnosis: focal epilepsy. Current medication: lamotrigine 100 mg bd. "
        "MRI was normal. She has focal seizures twice a month."
    )
    annotations = (
        ExectAnnotation(
            entity="Diagnosis",
            text="focal epilepsy",
            attributes={
                "DiagCategory": "Epilepsy",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
        ExectAnnotation(
            entity="SeizureFrequency",
            text="focal seizures",
            attributes={
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
        ExectAnnotation(
            entity="Prescription",
            text="lamotrigine",
            attributes={
                "DrugName": "lamotrigine",
                "DrugDose": "100",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        ExectAnnotation(
            entity="Investigations",
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
    )
    return [
        ExectLetter(letter_id="EA1", note_text=note, annotations=annotations),
        ExectLetter(letter_id="EA2", note_text=note, annotations=annotations),
    ]


def _row(letter_id: str) -> dict[str, object]:
    mentions = [
        _mention(
            "Diagnosis",
            "focal epilepsy",
            "Diagnosis: focal epilepsy",
            {"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"},
        ),
        _mention(
            "SeizureFrequency",
            "focal seizures",
            "focal seizures twice a month",
            {
                "NumberOfSeizures": "2",
                "NumberOfTimePeriods": "1",
                "TimePeriod": "Month",
            },
        ),
        _mention(
            "Prescription",
            "lamotrigine",
            "lamotrigine 100 mg bd",
            {
                "DrugName": "lamotrigine",
                "DrugDose": "100",
                "DoseUnit": "mg",
                "Frequency": "2",
            },
        ),
        _mention(
            "Investigations",
            "MRI",
            "MRI was normal",
            {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
    ]
    return {
        "letter_id": letter_id,
        "split": "toy",
        "pipeline_family": "toy_structured",
        "prompt_version": "toy_v1",
        "model": "none",
        "mode": "no-call",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(mentions),
        "n_evidence_invalid": 0,
        "predicted_mentions": mentions,
        "raw_output": json.dumps({"mentions": mentions}),
    }


def _mention(entity: str, text: str, evidence: str, attrs: dict[str, str]) -> dict[str, object]:
    return {
        "entity": entity,
        "text": text,
        "attributes": attrs,
        "evidence": evidence,
        "confidence": "high",
        "rationale": "",
    }


def _write_config(
    tmp_path: Path,
    *,
    structured: Path,
    output_stem: str,
    calls_per_letter: int,
    derived_artifacts: list[dict[str, str]] | None = None,
) -> Path:
    payload = {
        "candidate_id": "toy_simplification",
        "stage": "toy",
        "label": "toy simplification",
        "role": "test",
        "calls_per_letter": calls_per_letter,
        "live_call_components": ["structured"],
        "replayed_components": ["finding_assembly"],
        "removed_components": [],
        "derived_artifacts": derived_artifacts or [],
        "assembly": {
            "candidate_id": "toy_simplification",
            "pipeline_family": "toy_frontier",
            "ownership": "toy",
            "split": "toy",
            "row_count": 2,
            "claim_boundary": "toy aggregate",
            "baseline_producer": "structured",
            "producers": {
                "structured": {
                    "kind": "saved_jsonl",
                    "artifact": str(structured),
                    "ownership_label": "toy_structured",
                    "source_lane": "toy_structured",
                }
            },
            "lenses": {
                "Diagnosis": {
                    "producer": "structured",
                    "lens": "diagnosis_hierarchy_negation_v01",
                    "source_lane": "toy_structured_dx",
                    "ownership_label": "toy_structured_dx",
                },
                "SeizureFrequency": {
                    "producer": "structured",
                    "lens": "sf_state_direct_v01",
                    "source_lane": "toy_structured_sf",
                    "ownership_label": "toy_structured_sf",
                },
                "Prescription": {
                    "producer": "structured",
                    "lens": "prescription_regimen_v01",
                    "source_lane": "toy_structured_rx",
                    "ownership_label": "toy_structured_rx",
                },
                "Investigations": {
                    "producer": "structured",
                    "lens": "investigations_result_v01",
                    "source_lane": "toy_structured_inv",
                    "ownership_label": "toy_structured_inv",
                },
            },
            "views": [
                "raw_candidate",
                "evidence_valid",
                "clinical_headline",
                "fidelity_companion",
                "benchmark_cui",
            ],
        },
        "outputs": {
            "json": str(tmp_path / f"{output_stem}.json"),
            "jsonl": str(tmp_path / f"{output_stem}.jsonl"),
            "markdown": str(tmp_path / f"{output_stem}.md"),
        },
    }
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _report(
    *,
    candidate_id: str,
    calls_per_letter: int,
    overall: float,
    diagnosis: float,
    sf: float,
    prescription: float,
    investigations: float,
) -> dict[str, object]:
    by_indicator = {
        "Diagnosis": _score(diagnosis),
        "SeizureFrequency": _score(sf),
        "Prescription": _score(prescription),
        "Investigations": _score(investigations),
    }
    score_ladder = {
        "headline_target": {
            "overall": _score(overall),
            "by_indicator": by_indicator,
        }
    }
    report = {
        "candidate_name": candidate_id,
        "score_ladder": score_ladder,
        "lane_diagnostics": {},
    }
    report["simplification_frontier"] = {
        "stage": "test",
        "label": candidate_id,
        "role": "test",
        "calls_per_letter": calls_per_letter,
        "full_200_calls": calls_per_letter * 200,
        "live_call_components": [],
        "replayed_components": [],
        "removed_components": [],
        "config_path": "",
        "acceptability": simplification_frontier.evaluate_acceptability(report),
    }
    return report


def _score(f1: float) -> dict[str, float | int]:
    return {
        "f1": f1,
        "precision": f1,
        "recall": f1,
        "tp": 1,
        "fp": 0,
        "fn": 0,
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    return path


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
