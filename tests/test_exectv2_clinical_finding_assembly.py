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
    assert set(first["prediction_surfaces"]) == {
        "source_scored",
        "evidence_valid",
        "protocol_model_preserving_canonical",
        "dictionary_normalized",
        "residual_benchmark_added",
    }
    assert run.report["score_ladder"]["materialized_surfaces"]["source_scored"][
        "overall"
    ]["f1"] == run.report["score_ladder"]["raw_lane_score"]["overall"]["f1"]


def test_assembly_materializes_dictionary_and_residual_intermediate_surfaces(
    tmp_path: Path,
) -> None:
    letters = _letters()[:1]
    control_row = _control_row("EA1")
    control_row["predicted_mentions"] = [
        mention
        for mention in control_row["predicted_mentions"]
        if mention["entity"] != "Prescription"
    ]
    control_row["raw_output"] = json.dumps({"mentions": control_row["predicted_mentions"]})
    control = _write_jsonl(tmp_path / "control.jsonl", [control_row])
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [_diagnosis_row("EA1")])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])
    manifest = _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1)
    manifest = FindingAssemblyManifest(
        **{
            **manifest.__dict__,
            "candidate_id": "test_materialized_surfaces",
            "lenses": {
                **manifest.lenses,
                "Prescription": LensManifest(
                    entity="Prescription",
                    producer="control",
                    lens="prescription_dictionary_v09",
                    source_lane="v0.42_control",
                    ownership_label="llm_first_control+standard_dictionary_prescription",
                    portability="clinical_epilepsy",
                ),
            },
        }
    )

    run = build_finding_assembly(
        manifest,
        generated_on="2026-06-22",
        gold_loader=lambda _split: letters,
    )

    rx_surfaces = run.rows[0]["lanes"]["Prescription"]["prediction_surfaces"]
    assert rx_surfaces["source_scored"] == []
    assert rx_surfaces["protocol_model_preserving_canonical"] == []
    assert rx_surfaces["dictionary_normalized"] == []
    assert [m["text"] for m in rx_surfaces["residual_benchmark_added"]] == ["lamotrigine"]
    assert "lamotrigine 100 mg bd" in rx_surfaces["residual_benchmark_added"][0][
        "evidence"
    ]
    materialized = run.report["score_ladder"]["materialized_surfaces"]
    assert materialized["protocol_model_preserving_canonical"]["overall"]["pred_count"] == 3
    assert materialized["dictionary_normalized"]["overall"]["pred_count"] == 3
    assert materialized["residual_benchmark_added"]["overall"]["pred_count"] == 4


def test_protocol_clean_surface_excludes_candidate_backed_passthrough(
    tmp_path: Path,
) -> None:
    letters = _letters()[:1]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    candidate_backed_diagnosis = _diagnosis_row("EA1")
    candidate_backed_diagnosis["pipeline_family"] = (
        "exectv2_hybrid_family_conditioned_candidate_adjudicator"
    )
    candidate_backed_diagnosis["mode"] = "live-actions-strict"
    candidate_backed_diagnosis["candidate_actions"] = [
        {"candidate_id": "best_diagnosis:M0", "action": "keep"}
    ]
    candidate_backed_diagnosis["candidate_mentions"] = list(
        candidate_backed_diagnosis["predicted_mentions"]
    )
    diagnosis = _write_jsonl(tmp_path / "diagnosis.jsonl", [candidate_backed_diagnosis])
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])

    run = build_finding_assembly(
        _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1),
        generated_on="2026-06-23",
        gold_loader=lambda _split: letters,
    )

    dx_surfaces = run.rows[0]["lanes"]["Diagnosis"]["prediction_surfaces"]
    assert len(dx_surfaces["source_scored"]) == 1
    assert dx_surfaces["source_scored"][0]["fact_origin"] == "upstream_candidate_copied"
    assert dx_surfaces["protocol_model_preserving_canonical"] == []
    assert len(dx_surfaces["residual_benchmark_added"]) == 1
    accounting = run.report["fact_origin_accounting"]["by_surface"]
    assert accounting["source_scored"]["upstream_candidate_copied"] == 1
    assert accounting["protocol_model_preserving_canonical"].get(
        "upstream_candidate_copied", 0
    ) == 0
    assert run.report["score_ladder"]["materialized_surfaces"][
        "protocol_model_preserving_canonical"
    ]["overall"]["pred_count"] == 3


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


def test_diagnosis_heading_recovery_lens_adds_explicit_focal_epilepsy(
    tmp_path: Path,
) -> None:
    letters = _letters()[:1]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [_diagnosis_row("EA1", text="epilepsy", evidence="Diagnosis: focal epilepsy")],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])
    manifest = _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1)
    manifest = FindingAssemblyManifest(
        **{
            **manifest.__dict__,
            "candidate_id": "test_heading_recovery",
            "lenses": {
                **manifest.lenses,
                "Diagnosis": LensManifest(
                    entity="Diagnosis",
                    producer="diagnosis",
                    lens="diagnosis_heading_recovery_v02",
                    source_lane="focused_diagnosis_reconciler_v01",
                    ownership_label="hybrid_diagnosis_route",
                    portability="clinical_epilepsy",
                ),
            },
        }
    )

    run = build_finding_assembly(
        manifest,
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    diagnoses = [
        mention for mention in run.rows[0]["predicted_mentions"] if mention["entity"] == "Diagnosis"
    ]
    assert [mention["text"] for mention in diagnoses] == ["epilepsy", "focal epilepsy"]
    added = diagnoses[1]
    assert added["component_owner"] == ("hybrid_diagnosis_route+deterministic_heading_recovery")
    assert added["provenance"][0]["action"] == "added_focal_epilepsy_from_diagnosis_heading"
    assert added["provenance"][0]["portability"] == "clinical_epilepsy"
    assert (
        run.rows[0]["lanes"]["Diagnosis"]["lens_diagnostics"]["added_heading_recovery_findings"]
        == 1
    )


def test_diagnosis_convention_cleanup_lens_drops_standalone_overemissions(
    tmp_path: Path,
) -> None:
    note = (
        "Diagnosis: focal epilepsy. He understands DVLA laws on driving with epilepsy. "
        "Occasional absences. Current medication: lamotrigine 100 mg bd. MRI was "
        "normal. She has focal seizures twice a month."
    )
    letters = [
        ExectLetter(
            letter_id="EA1",
            note_text=note,
            annotations=_letters()[0].annotations,
        )
    ]
    diagnosis_mentions = [
        _mention("Diagnosis", "epilepsy", "driving with epilepsy", _dx_attrs()),
        _mention(
            "Diagnosis",
            "absence seizures",
            "Occasional absences",
            {
                "DiagCategory": "MultipleSeizures",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
    ]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [
            {
                **_diagnosis_row("EA1"),
                "n_mentions_raw": len(diagnosis_mentions),
                "n_mentions_scored": len(diagnosis_mentions),
                "predicted_mentions": diagnosis_mentions,
            }
        ],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])
    manifest = _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1)
    manifest = FindingAssemblyManifest(
        **{
            **manifest.__dict__,
            "candidate_id": "test_convention_cleanup",
            "lenses": {
                **manifest.lenses,
                "Diagnosis": LensManifest(
                    entity="Diagnosis",
                    producer="diagnosis",
                    lens="diagnosis_heading_recovery_convention_cleanup_v03",
                    source_lane="focused_diagnosis_reconciler_v01",
                    ownership_label="hybrid_diagnosis_route",
                    portability="clinical_epilepsy",
                ),
            },
        }
    )

    run = build_finding_assembly(
        manifest,
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    diagnoses = [
        mention for mention in run.rows[0]["predicted_mentions"] if mention["entity"] == "Diagnosis"
    ]
    assert [mention["text"] for mention in diagnoses] == ["focal epilepsy"]
    diagnostics = run.rows[0]["lanes"]["Diagnosis"]["lens_diagnostics"]
    assert diagnostics["dropped_convention_noise_findings"] == 2
    assert diagnostics["dropped_convention_noise_text_counts"] == {
        "absence seizures": 1,
        "epilepsy": 1,
    }


def test_diagnosis_convention_alias_lens_rewrites_and_drops_residuals(
    tmp_path: Path,
) -> None:
    note = (
        "Diagnosis: Hydrocephalus. She gets focal dyscognitive seizures. "
        "He will get grand mal episodes. Current medication: lamotrigine 100 mg bd. "
        "MRI was normal. She has focal seizures twice a month."
    )
    letters = [
        ExectLetter(
            letter_id="EA1",
            note_text=note,
            annotations=_letters()[0].annotations,
        )
    ]
    diagnosis_mentions = [
        _mention("Diagnosis", "Hydrocephalus", "Diagnosis: Hydrocephalus", _dx_attrs()),
        _mention(
            "Diagnosis",
            "focal dyscognitive seizures",
            "focal dyscognitive seizures",
            {
                "DiagCategory": "MultipleSeizures",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
        _mention(
            "Diagnosis",
            "grand mal seizure",
            "grand mal episodes",
            {
                "DiagCategory": "SingleSeizure",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
    ]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [
            {
                **_diagnosis_row("EA1"),
                "n_mentions_raw": len(diagnosis_mentions),
                "n_mentions_scored": len(diagnosis_mentions),
                "predicted_mentions": diagnosis_mentions,
            }
        ],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])
    manifest = _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1)
    manifest = FindingAssemblyManifest(
        **{
            **manifest.__dict__,
            "candidate_id": "test_convention_alias_repair",
            "lenses": {
                **manifest.lenses,
                "Diagnosis": LensManifest(
                    entity="Diagnosis",
                    producer="diagnosis",
                    lens="diagnosis_heading_recovery_convention_alias_v04",
                    source_lane="focused_diagnosis_reconciler_v01",
                    ownership_label="hybrid_diagnosis_route",
                    portability="benchmark_format",
                ),
            },
        }
    )

    run = build_finding_assembly(
        manifest,
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    diagnoses = [
        mention for mention in run.rows[0]["predicted_mentions"] if mention["entity"] == "Diagnosis"
    ]
    assert [mention["text"] for mention in diagnoses] == [
        "dyscognitive seizures",
        "grand mal",
    ]
    assert diagnoses[0]["component_owner"] == (
        "hybrid_diagnosis_route+deterministic_convention_alias_repair"
    )
    rewrite_events = [
        event
        for event in diagnoses[0]["provenance"]
        if event["action"] == "rewrote_diagnosis_convention_alias"
    ]
    assert rewrite_events
    assert rewrite_events[0]["portability"] == "benchmark_format"
    diagnostics = run.rows[0]["lanes"]["Diagnosis"]["lens_diagnostics"]
    assert diagnostics["rewritten_convention_alias_findings"] == 2
    assert diagnostics["dropped_residual_convention_noise_findings"] == 1


def test_diagnosis_residual_benchmark_lens_repairs_convention_phrases(
    tmp_path: Path,
) -> None:
    note = (
        "Diagnosis: symptomatic epilepsy with focal motor seizures with secondary "
        "generalised seizures. She has no epilepsy protocol imaging planned. "
        "Previous episode of status epilepticus. Current medication: lamotrigine "
        "100 mg bd. MRI was normal. She has focal seizures twice a month."
    )
    letters = [
        ExectLetter(
            letter_id="EA1",
            note_text=note,
            annotations=_letters()[0].annotations,
        )
    ]
    diagnosis_mentions = [
        _mention(
            "Diagnosis",
            "symptomatic structural focal epilepsy",
            "Diagnosis: symptomatic epilepsy",
            _dx_attrs(),
        ),
        _mention(
            "Diagnosis",
            "secondary generalised tonic clonic seizures",
            "secondary generalised seizures",
            {
                "DiagCategory": "MultipleSeizures",
                "Certainty": "5",
                "Negation": "Affirmed",
            },
        ),
        _mention(
            "Diagnosis", "tonic clonic seizures", "secondary generalised seizures", _dx_attrs()
        ),
        _mention("Diagnosis", "epilepsy", "epilepsy protocol", _dx_attrs()),
    ]
    control = _write_jsonl(tmp_path / "control.jsonl", [_control_row("EA1")])
    diagnosis = _write_jsonl(
        tmp_path / "diagnosis.jsonl",
        [
            {
                **_diagnosis_row("EA1"),
                "n_mentions_raw": len(diagnosis_mentions),
                "n_mentions_scored": len(diagnosis_mentions),
                "predicted_mentions": diagnosis_mentions,
            }
        ],
    )
    sf = _write_jsonl(tmp_path / "sf.jsonl", [_sf_row("EA1")])
    manifest = _manifest(control=control, diagnosis=diagnosis, sf=sf, row_count=1)
    manifest = FindingAssemblyManifest(
        **{
            **manifest.__dict__,
            "candidate_id": "test_residual_benchmark_repair",
            "lenses": {
                **manifest.lenses,
                "Diagnosis": LensManifest(
                    entity="Diagnosis",
                    producer="diagnosis",
                    lens="diagnosis_heading_recovery_residual_benchmark_v05",
                    source_lane="focused_diagnosis_reconciler_v01",
                    ownership_label="hybrid_diagnosis_route",
                    portability="benchmark_format",
                ),
            },
        }
    )

    run = build_finding_assembly(
        manifest,
        generated_on="2026-06-21",
        gold_loader=lambda _split: letters,
    )

    diagnoses = [
        mention for mention in run.rows[0]["predicted_mentions"] if mention["entity"] == "Diagnosis"
    ]
    assert [mention["text"] for mention in diagnoses] == [
        "symptomatic epilepsy",
        "secondary generalised seizures",
        "status epilepticus",
    ]
    assert diagnoses[0]["component_owner"] == (
        "hybrid_diagnosis_route+deterministic_residual_benchmark_repair"
    )
    diagnostics = run.rows[0]["lanes"]["Diagnosis"]["lens_diagnostics"]
    assert diagnostics["rewritten_residual_benchmark_findings"] == 2
    assert diagnostics["added_residual_benchmark_findings"] == 1
    assert diagnostics["dropped_residual_benchmark_noise_findings"] == 2


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
    assert benchmark["after_cui_projection"] == 0.3786
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
