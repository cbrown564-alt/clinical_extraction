import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    focused_lane_component_evidence as replay,
)


def test_focused_lane_replay_selects_predeclared_lanes_and_provenance(
    tmp_path: Path,
    monkeypatch,
) -> None:
    letters = _letters()
    monkeypatch.setattr(replay, "load_letters_for_split", lambda _split: letters)
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1"), _control_row("EA2")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [_diagnosis_row("EA1"), _diagnosis_row("EA2")],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1"), _sf_row("EA2")])

    rows, report = replay.build_focused_lane_replay(
        row_count=2,
        control_artifact=control,
        diagnosis_artifact=diagnosis,
        sf_artifact=sf,
        focused_comparator_artifact=None,
        generated_on="2026-06-20",
    )

    first = rows[0]
    assert [(m["entity"], m["source_lane"]) for m in first["predicted_mentions"]] == [
        ("Diagnosis", "focused_diagnosis_reconciler_v01"),
        ("SeizureFrequency", "focused_sf_unknown_suppression_v07"),
        ("Prescription", "v0.42_control"),
        ("Investigations", "v0.42_control"),
    ]
    assert first["lanes"]["Diagnosis"]["ownership_label"] == "hybrid_diagnosis_route"
    assert first["lanes"]["Prescription"]["ownership_label"] == "llm_first_control"
    assert set(report["score_ladder"]["headline_target"]["by_indicator"]) == {
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    }
    assert report["lane_diagnostics"]["Diagnosis"]["exact_evidence_rate"] == 1.0


def test_focused_lane_replay_reconstructs_raw_lane_mentions(
    tmp_path: Path,
    monkeypatch,
) -> None:
    letters = _letters()[:1]
    monkeypatch.setattr(replay, "load_letters_for_split", lambda _split: letters)

    rows, _report = replay.build_focused_lane_replay(
        row_count=1,
        control_artifact=_write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")]),
        diagnosis_artifact=_write_jsonl(
            tmp_path / "diagnosis.jsonl",
            [_diagnosis_row("EA1", raw_text="raw focal epilepsy")],
        ),
        sf_artifact=_write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")]),
        focused_comparator_artifact=None,
    )

    raw_dx = [
        mention
        for mention in rows[0]["raw_lane_mentions"]
        if mention["entity"] == "Diagnosis"
    ]
    assert raw_dx[0]["text"] == "raw focal epilepsy"
    assert raw_dx[0]["raw_surface"] is True
    assert raw_dx[0]["source_artifact"].endswith("diagnosis.jsonl")


def test_focused_lane_replay_fails_closed_on_missing_source_row(
    tmp_path: Path,
    monkeypatch,
) -> None:
    letters = _letters()
    monkeypatch.setattr(replay, "load_letters_for_split", lambda _split: letters)
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1"), _control_row("EA2")])
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [_diagnosis_row("EA1")])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1"), _sf_row("EA2")])

    with pytest.raises(ValueError, match="does not match frozen row set"):
        replay.build_focused_lane_replay(
            row_count=2,
            control_artifact=control,
            diagnosis_artifact=diagnosis,
            sf_artifact=sf,
            focused_comparator_artifact=None,
        )


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


def _control_row(letter_id: str) -> dict:
    mentions = [
        _mention("Prescription", "lamotrigine", "lamotrigine 100 mg bd", _presc_attrs()),
        _mention("Investigations", "MRI", "MRI was normal", _inv_attrs()),
        _mention("Diagnosis", "epilepsy", "Diagnosis: focal epilepsy", _dx_attrs()),
        _mention("SeizureFrequency", "seizures", "focal seizures twice a month", _sf_attrs()),
    ]
    return {
        "letter_id": letter_id,
        "split": "dev",
        "pipeline_family": "exectv2_target_indicators_single_call",
        "prompt_version": "v0.42",
        "model": "local",
        "mode": "live",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(mentions),
        "n_evidence_invalid": 0,
        "predicted_mentions": mentions,
        "raw_output": json.dumps({"mentions": mentions}),
    }


def _diagnosis_row(letter_id: str, *, raw_text: str = "focal epilepsy") -> dict:
    mention = _mention("Diagnosis", "focal epilepsy", "Diagnosis: focal epilepsy", _dx_attrs())
    raw = dict(mention)
    raw.pop("entity")
    raw["text"] = raw_text
    return {
        "letter_id": letter_id,
        "split": "dev",
        "pipeline_family": "exectv2_hybrid_diagnosis_reconciler",
        "prompt_version": "v0.1",
        "model": "gpt",
        "mode": "live",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "n_mentions_raw": 1,
        "n_mentions_scored": 1,
        "n_evidence_invalid": 0,
        "predicted_mentions": [mention],
        "raw_output": json.dumps({"mentions": [raw]}),
    }


def _sf_row(letter_id: str) -> dict:
    mention = _mention(
        "SeizureFrequency",
        "focal seizures",
        "focal seizures twice a month",
        _sf_attrs(),
    )
    raw = dict(mention)
    raw.pop("entity")
    return {
        "letter_id": letter_id,
        "split": "dev",
        "pipeline_family": "exectv2_hybrid_sf_unknown_suppression",
        "prompt_version": "v0.7",
        "model": "gpt",
        "mode": "live",
        "component_owner": "deterministic_sf_unknown_suppression",
        "projection_version": "v0.6",
        "suppression_version": "v0.7",
        "projection_actions": [{"action": "kept"}],
        "suppression_actions": [],
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "n_mentions_raw": 1,
        "n_mentions_scored": 1,
        "n_evidence_invalid": 0,
        "predicted_mentions": [mention],
        "raw_output": json.dumps({"mentions": [raw]}),
    }


def _mention(entity: str, text: str, evidence: str, attrs: dict[str, str]) -> dict:
    return {
        "entity": entity,
        "text": text,
        "attributes": attrs,
        "evidence": evidence,
        "confidence": "high",
        "rationale": "",
    }


def _dx_attrs() -> dict[str, str]:
    return {"DiagCategory": "Epilepsy", "Certainty": "5", "Negation": "Affirmed"}


def _sf_attrs() -> dict[str, str]:
    return {"NumberOfSeizures": "2", "NumberOfTimePeriods": "1", "TimePeriod": "Month"}


def _presc_attrs() -> dict[str, str]:
    return {"DrugName": "lamotrigine", "DrugDose": "100", "DoseUnit": "mg", "Frequency": "2"}


def _inv_attrs() -> dict[str, str]:
    return {"MRI_Performed": "Yes", "MRI_Results": "Normal"}


def _write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
    return path
