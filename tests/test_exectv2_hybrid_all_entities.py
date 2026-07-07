"""Tests for the ExECTv2 all-entity hybrid (satellite 09, Phase C).

Covers:
  - all_entity_gate: evidence routing, SF plausibility, duplicate collapse
  - assemble_letter: combine candidates, CUI projection, rule augmentation
  - run_replay / summarize_rows: overall + per-entity scores, projection ablation
  - load_candidates_from_per_entity: read focused per-entity JSONL artifacts
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    all_entity_assessment as hybrid,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.all_entity_gate import (
    gate_mentions,
    routed_taxonomy,
    routed_taxonomy_by_entity,
)

_NOTE = (
    "This gentleman has focal epilepsy. He takes lamotrigine 200mg twice a day. "
    "His EEG was abnormal. He reports 2 focal seizures per month."
)


def _letter() -> ExectLetter:
    return ExectLetter(letter_id="EA0001", note_text=_NOTE, annotations=())


def _m(entity: str, text: str, attrs: dict[str, str], evidence: str) -> PredictedMention:
    return PredictedMention(entity=entity, text=text, attributes=attrs, evidence=evidence)


# ── Gate ───────────────────────────────────────────────────────────────────────


def test_gate_routes_evidence_not_substring() -> None:
    m = _m("Diagnosis", "focal epilepsy", {"DiagCategory": "Epilepsy"}, "not in the letter")
    kept, routed = gate_mentions([m], note_text=_NOTE)
    assert kept == []
    assert routed_taxonomy(routed) == {"evidence_not_substring": 1}


def test_gate_routes_empty_evidence() -> None:
    m = _m("Diagnosis", "focal epilepsy", {"DiagCategory": "Epilepsy"}, "")
    _kept, routed = gate_mentions([m], note_text=_NOTE)
    assert routed_taxonomy(routed) == {"empty_evidence": 1}


def test_gate_routes_sf_bare_count() -> None:
    m = _m("SeizureFrequency", "focal seizures", {"NumberOfSeizures": "2"}, "2 focal seizures")
    _kept, routed = gate_mentions([m], note_text="he had 2 focal seizures once")
    assert routed_taxonomy(routed) == {"bare_nonzero_count": 1}


def test_gate_keeps_sf_with_frequency() -> None:
    m = _m(
        "SeizureFrequency",
        "focal seizures",
        {"NumberOfSeizures": "2", "TimePeriod": "Month", "NumberOfTimePeriods": "1"},
        "2 focal seizures per month",
    )
    kept, routed = gate_mentions([m], note_text=_NOTE)
    assert len(kept) == 1
    assert routed == []


def test_gate_keeps_sf_explicit_zero() -> None:
    m = _m("SeizureFrequency", "seizure-free", {"NumberOfSeizures": "0"}, "focal seizures")
    kept, _routed = gate_mentions([m], note_text="he is now focal seizures free")
    assert len(kept) == 1


def test_gate_collapses_duplicates() -> None:
    a = _m("Diagnosis", "focal epilepsy", {"DiagCategory": "Epilepsy"}, "focal epilepsy")
    b = _m("Diagnosis", "focal epilepsy", {"DiagCategory": "Epilepsy"}, "focal epilepsy")
    kept, routed = gate_mentions([a, b], note_text=_NOTE)
    assert len(kept) == 1
    assert routed_taxonomy(routed) == {"duplicate_mention": 1}


def test_gate_keeps_distinct_attributes() -> None:
    a = _m("Investigations", "EEG", {"EEG_Performed": "Yes"}, "EEG was abnormal")
    b = _m("Investigations", "EEG", {"EEG_Results": "Abnormal"}, "EEG was abnormal")
    kept, _routed = gate_mentions([a, b], note_text=_NOTE)
    assert len(kept) == 2


def test_routed_taxonomy_by_entity() -> None:
    a = _m("Diagnosis", "focal epilepsy", {}, "nope")
    b = _m("Onset", "epilepsy", {}, "also nope")
    _kept, routed = gate_mentions([a, b], note_text=_NOTE)
    by_entity = routed_taxonomy_by_entity(routed)
    assert by_entity["Diagnosis"] == {"evidence_not_substring": 1}
    assert by_entity["Onset"] == {"evidence_not_substring": 1}


# ── Assemble ───────────────────────────────────────────────────────────────────


def test_assemble_letter_projects_cui() -> None:
    cand = _m(
        "Prescription",
        "lamotrigine",
        {"DrugName": "Lamotrigine", "DrugDose": "200", "DoseUnit": "mg", "Frequency": "2"},
        "lamotrigine 200mg twice a day",
    )
    predicted, routed = hybrid.assemble_letter(_letter(), [cand])
    assert routed == []
    assert len(predicted.mentions) == 1
    assert predicted.mentions[0].attributes.get("CUI")  # projected deterministically


def test_assemble_letter_rule_augmentation_adds_candidates() -> None:
    predicted_plain, _ = hybrid.assemble_letter(_letter(), [])
    predicted_aug, _ = hybrid.assemble_letter(_letter(), [], augment_rules=True)
    assert len(predicted_aug.mentions) > len(predicted_plain.mentions)
    entities = {m.entity for m in predicted_aug.mentions}
    assert "Prescription" in entities  # the rules find lamotrigine


# ── Replay / summary ───────────────────────────────────────────────────────────


def _gold_letter() -> ExectLetter:
    return ExectLetter(
        letter_id="EA0001",
        note_text=_NOTE,
        annotations=(
            ExectAnnotation(
                entity="Prescription",
                text="lamotrigine",
                attributes={
                    "DrugName": "Lamotrigine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                    "CUI": "C0064636",
                },
            ),
        ),
    )


def test_run_replay_scores_overall_and_per_entity() -> None:
    cand = _m(
        "Prescription",
        "lamotrigine",
        {"DrugName": "Lamotrigine", "DrugDose": "200", "DoseUnit": "mg", "Frequency": "2"},
        "lamotrigine 200mg twice a day",
    )
    rows, metadata = hybrid.run_replay(
        [_gold_letter()],
        {"EA0001": [cand]},
        split="dev",
        model="test",
    )
    summary = metadata["summary"]
    assert summary["examples"] == 1
    assert "semantic" in summary["scores"]
    assert "projection_ablation" in summary
    presc = summary["scores"]["semantic"]["per_entity"]["Prescription"]["per_item"]
    assert presc["tp"] == 1  # matched the single gold prescription


def test_load_candidates_from_per_entity(tmp_path: Path) -> None:
    prefix = "probe"
    path = tmp_path / f"{prefix}_diagnosis.jsonl"
    row = {
        "letter_id": "EA0001",
        "predicted_mentions": [
            {
                "text": "focal epilepsy",
                "attributes": {"DiagCategory": "Epilepsy"},
                "evidence": "focal epilepsy",
                "confidence": "high",
                "rationale": "stated",
            }
        ],
    }
    path.write_text(json.dumps(row) + "\n", encoding="utf-8")
    candidates = hybrid.load_candidates_from_per_entity(
        prefix, out_dir=tmp_path, entities=["Diagnosis"]
    )
    assert "EA0001" in candidates
    assert candidates["EA0001"][0].entity == "Diagnosis"
    assert candidates["EA0001"][0].text == "focal epilepsy"
