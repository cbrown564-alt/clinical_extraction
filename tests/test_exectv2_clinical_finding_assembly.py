import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly import (
    FindingAssemblyManifest,
    LensManifest,
    ProducerManifest,
    build_finding_assembly,
    load_finding_assembly_manifest,
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
    dx = first["predicted_mentions"][0]
    assert dx["provenance"][-1]["stage"] == "entity_lens"
    assert dx["evidence_valid"] is True
    assert run.report["finding_views"] == [
        "raw_candidate",
        "evidence_valid",
        "clinical_headline",
        "fidelity_companion",
        "benchmark_cui",
    ]
    assert set(run.views) == {
        "raw_candidate",
        "evidence_valid",
        "clinical_headline",
        "fidelity_companion",
        "benchmark_cui",
    }


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


def test_saved_artifact_producer_fails_closed_on_row_set_mismatch(tmp_path: Path) -> None:
    letters = _letters()
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1"), _control_row("EA2")])
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [_diagnosis_row("EA1")])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1"), _sf_row("EA2")])

    with pytest.raises(ValueError, match="does not match frozen row set"):
        build_finding_assembly(
            _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=2),
            gold_loader=lambda _split: letters,
        )


def test_yaml_manifest_parser(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(
        """
candidate_id: parsed_candidate
pipeline_family: parsed_family
ownership: parsed_owner
split: dev
row_count: 2
claim_boundary: dev_only_component_evidence
baseline_producer: control
producers:
  control:
    kind: saved_jsonl
    artifact: experiments/control.jsonl
    ownership_label: llm_first_control
lenses:
  Diagnosis:
    producer: control
    lens: diagnosis_hierarchy_negation_v01
    source_lane: v0.42_control
views:
  - raw_candidate
  - evidence_valid
""",
        encoding="utf-8",
    )

    manifest = load_finding_assembly_manifest(manifest_path)

    assert manifest.candidate_id == "parsed_candidate"
    assert manifest.producers["control"].artifact == Path("experiments/control.jsonl")
    assert manifest.lenses["Diagnosis"].lens == "diagnosis_hierarchy_negation_v01"


def test_holistic_manifest_reproduces_dev140_score_ladder() -> None:
    manifest = load_finding_assembly_manifest(
        Path("configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v01_dev140.yaml")
    )

    run = build_finding_assembly(manifest, generated_on="2026-06-21")

    headline = run.report["score_ladder"]["headline_target"]
    benchmark = run.report["score_ladder"]["benchmark"]
    companions = run.report["score_ladder"]["fidelity_companions"]
    assert run.report["gate_decision"]["decision"] == "promote-dev-holistic-finding-assembly"
    assert headline["overall"]["f1"] == 0.8006
    assert headline["by_indicator"]["Diagnosis"]["f1"] == 0.7572
    assert headline["by_indicator"]["SeizureFrequency"]["f1"] == 0.8068
    assert headline["by_indicator"]["Prescription"]["f1"] == 0.8214
    assert headline["by_indicator"]["Investigations"]["f1"] == 0.8615
    assert benchmark["raw"] == 0.2968
    assert benchmark["after_cui_projection"] == 0.3157
    assert companions["Diagnosis"]["concept_negation"]["f1"] == 0.7572
    assert companions["SeizureFrequency"]["active_rate_fidelity"]["f1"] == 0.3931


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
            "evidence_valid",
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
) -> dict:
    mention = _mention("Diagnosis", "focal epilepsy", "Diagnosis: focal epilepsy", _dx_attrs())
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
