import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly import (
    FindingAssemblyManifest,
    LensManifest,
    ProducerManifest,
    build_finding_assembly,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    manifest_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)


def test_manifest_driven_assembly_preserves_sources_and_views(tmp_path: Path) -> None:
    letters = _letters()
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1"), _control_row("EA2")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [_diagnosis_row("EA1"), _diagnosis_row("EA2")],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1"), _sf_row("EA2")])

    run = build_finding_assembly(
        _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=2),
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    first = run.rows[0]
    assert first["candidate_name"] == "test_holistic_finding_assembly_dev2"
    assert [(m["entity"], m["source_lane"]) for m in first["predicted_mentions"]] == [
        ("Diagnosis", "focused_diagnosis_reconciler_v01"),
        ("SeizureFrequency", "focused_sf_unknown_suppression_v07"),
        ("Prescription", "v0.42_control"),
        ("Investigations", "v0.42_control"),
    ]
    assert run.stores["EA1"].findings(entity="SeizureFrequency")
    assert run.report["finding_views"] == [
        "raw_candidate",
        "post_lens",
        "clinical_headline",
        "fidelity_companion",
        "benchmark_cui",
    ]
    assert run.views["post_lens"].view_id == "post_lens"
    assert run.report["score_ladder"]["post_lens_score"] == run.report["score_ladder"][
        "evidence_valid_score"
    ]


def test_manifest_remaps_retired_evidence_valid_score_view() -> None:
    payload = {
        "candidate_id": "alias_check",
        "split": "dev",
        "row_count": 1,
        "claim_boundary": "dev_only_component_evidence",
        "producers": {
            "control": {
                "kind": "saved_jsonl",
                "artifact": "control.jsonl",
                "ownership_label": "control",
            }
        },
        "lenses": {
            "Diagnosis": {
                "producer": "control",
                "lens": "diagnosis_hierarchy_negation_v01",
            }
        },
        "views": ["raw_candidate", "evidence_valid", "clinical_headline"],
    }
    manifest = manifest_from_mapping(payload)
    assert manifest.views == ("raw_candidate", "post_lens", "clinical_headline")


def test_assembly_sf_lens_applies_state_adjudication_without_expanding_mentions(
    tmp_path: Path,
) -> None:
    letters = _letters()[:1]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [_diagnosis_row("EA1")])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])

    run = build_finding_assembly(
        _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1),
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    sf_lane = run.rows[0]["lanes"]["SeizureFrequency"]
    assert sf_lane["lens"] == "sf_state_adjudication_v01"
    sf_mentions = [
        m
        for m in run.rows[0]["predicted_mentions"]
        if m["entity"] == "SeizureFrequency"
    ]
    assert len(sf_mentions) == 1
    assert sf_mentions[0]["text"] == "focal seizures"


def test_assembly_keeps_distinct_investigation_occurrences_from_control_lane(
    tmp_path: Path,
) -> None:
    note = (
        "Diagnosis: focal epilepsy. Current medication: lamotrigine 100 mg bd. "
        "MRI was normal. EEG was abnormal. She has focal seizures twice a month."
    )
    letters = [
        ExectLetter(
            letter_id="EA1",
            note_text=note,
            annotations=_letters()[0].annotations,
        )
    ]
    control_row = _control_row("EA1")
    control_row["predicted_mentions"].append(
        _mention(
            "Investigations",
            "EEG",
            "EEG was abnormal",
            {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
        )
    )
    control_row["n_mentions_raw"] = len(control_row["predicted_mentions"])
    control_row["n_mentions_scored"] = len(control_row["predicted_mentions"])
    control = _write_jsonl(tmp_path / "control.jsonl", [control_row])
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [_diagnosis_row("EA1")])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])

    run = build_finding_assembly(
        _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1),
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    investigations = [
        mention
        for mention in run.rows[0]["predicted_mentions"]
        if mention["entity"] == "Investigations"
    ]
    assert [mention["text"] for mention in investigations] == ["MRI", "EEG"]
    assert len({mention["evidence"] for mention in investigations}) == 2


def test_assembly_retains_evidence_invalid_raw_findings_but_fails_final_invalid(
    tmp_path: Path,
) -> None:
    letters = _letters()[:1]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [_diagnosis_row("EA1", raw_evidence="not in note")],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])

    run = build_finding_assembly(
        _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1),
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )
    invalid_raw = run.stores["EA1"].findings(
        entity="Diagnosis",
        raw_surface=True,
        evidence_valid=False,
    )
    assert len(invalid_raw) == 1

    bad_final = _diagnosis_row("EA1")
    bad_final["predicted_mentions"][0]["evidence"] = "not in note"
    _write_jsonl(tmp_path / "bad_diagnosis.jsonl", [bad_final])
    with pytest.raises(ValueError, match="without exact source evidence"):
        build_finding_assembly(
            _manifest(
                control=control,
                diagnosis=tmp_path / "bad_diagnosis.jsonl",
                sf=sf,
                row_count=1,
            ),
            generated_on="2026-06-21",
            gold_loader=lambda _split: letters,
        )


def _manifest(
    *,
    control: Path,
    diagnosis: Path,
    sf: Path,
    row_count: int,
) -> FindingAssemblyManifest:
    producers = {
        "control": ProducerManifest(
            producer_id="control",
            kind="saved_jsonl",
            artifact=control,
            ownership_label="llm_first_control",
            source_lane="v0.42_control",
        ),
        "diagnosis": ProducerManifest(
            producer_id="diagnosis",
            kind="saved_jsonl",
            artifact=diagnosis,
            ownership_label="hybrid_diagnosis_route",
            source_lane="focused_diagnosis_reconciler_v01",
        ),
        "sf": ProducerManifest(
            producer_id="sf",
            kind="saved_jsonl",
            artifact=sf,
            ownership_label="hybrid_sf_route",
            source_lane="focused_sf_unknown_suppression_v07",
        ),
    }
    return FindingAssemblyManifest(
        candidate_id="test_holistic_finding_assembly_dev2",
        pipeline_family="test_finding_assembly",
        ownership="component_attributed_holistic_finding_replay",
        split="dev",
        row_count=row_count,
        claim_boundary="dev_only_component_evidence",
        producers=producers,
        lenses={
            "Diagnosis": LensManifest(
                entity="Diagnosis",
                producer="diagnosis",
                lens="diagnosis_hierarchy_negation_v01",
                source_lane="focused_diagnosis_reconciler_v01",
                ownership_label="hybrid_diagnosis_route",
            ),
            "SeizureFrequency": LensManifest(
                entity="SeizureFrequency",
                producer="sf",
                lens="sf_state_adjudication_v01",
                source_lane="focused_sf_unknown_suppression_v07",
                ownership_label="hybrid_sf_route",
            ),
            "Prescription": LensManifest(
                entity="Prescription",
                producer="control",
                lens="prescription_regimen_v01",
                source_lane="v0.42_control",
                ownership_label="llm_first_control",
            ),
            "Investigations": LensManifest(
                entity="Investigations",
                producer="control",
                lens="investigations_result_v01",
                source_lane="v0.42_control",
                ownership_label="llm_first_control",
            ),
        },
        views=(
            "raw_candidate",
            "post_lens",
            "clinical_headline",
            "fidelity_companion",
            "benchmark_cui",
        ),
        baseline_producer="control",
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


def _diagnosis_row(
    letter_id: str,
    *,
    raw_evidence: str = "Diagnosis: focal epilepsy",
    text: str = "focal epilepsy",
    evidence: str = "Diagnosis: focal epilepsy",
) -> dict:
    mention = _mention("Diagnosis", text, evidence, _dx_attrs())
    raw = dict(mention)
    raw.pop("entity")
    raw["evidence"] = raw_evidence
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


def test_diagnosis_heading_templates_split_collapsed_spans() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
        diagnosis as dx,
    )

    assert (
        dx.diagnosis_convention_target(
            "epilepsy probable focal",
            "Diagnosis: epilepsy – probable focal",
        )
        == "epilepsy"
    )
    heading = "Diagnosis: epilepsy – probable focal\n"
    added = [text for text, _evidence in dx.diagnosis_residual_additions(heading)]
    assert "focal epilepsy" in added
    temporal = "Diagnosis: focal epilepsy-Probable temporal\n"
    added_temporal = [text for text, _evidence in dx.diagnosis_residual_additions(temporal)]
    assert "temporal lobe epilepsy" in added_temporal


def test_pending_investigation_is_dropped_without_completed_result() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
        investigations as inv,
    )

    assert inv.is_pending_investigation(
        "EEG",
        evidence="We are awaiting an EEG appointment for her.",
        attributes={"EEG_Performed": "No"},
    )
    assert not inv.is_pending_investigation(
        "EEG",
        evidence="EEG 2012 generalised spike and wave.",
        attributes={"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
    )


def test_prescription_keeps_current_dose_not_target_range() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
        prescription as rx,
    )

    repaired = rx.prescription_convention_attribute_repairs(
        "Lamotrigine 75mg to 125mg",
        evidence=(
            "Currently Lamotrigine 75mg bd to increase over the following "
            "weeks to 125mg bd"
        ),
        attributes={"DrugName": "lamotrigine", "DrugDose": "75 to 125", "DoseUnit": "mg"},
    )
    assert repaired["DrugDose"] == "75"
