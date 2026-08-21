"""Hybrid ExECT select does not invent leftover letter cues."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    ClinicalFinding,
    FindingSource,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses.diagnosis import (
    DiagnosisDictionaryLens,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)


def test_diagnosis_lens_does_not_add_letter_scan_residuals() -> None:
    note = "Diagnosis: Epilepsy, probable focal onset. She remains well."
    leftovers = sd.diagnosis_residual_additions(note)
    assert leftovers
    source = FindingSource(
        producer_id="model",
        artifact_path="test",
        pipeline_family="test",
        model="test",
        prompt_version="test",
        mode="replay",
        ownership_label="model",
        source_lane="model",
    )
    store = ClinicalFindingStore("EA0000", note)
    store.add(
        ClinicalFinding(
            finding_id="EA0000:dx",
            letter_id="EA0000",
            entity="Diagnosis",
            text="epilepsy",
            attributes={"DiagCategory": "Epilepsy"},
            evidence="Diagnosis: Epilepsy, probable focal onset.",
            normalized_concept="epilepsy",
            assertion=None,
            confidence="high",
            source=source,
            provenance=(),
        )
    )
    result = DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09",
        entity="Diagnosis",
    ).reconcile(
        store,
        policy=LensPolicy(
            producer_id="model",
            source_lane="model",
            ownership_label="model",
            portability="clinical_epilepsy",
        ),
    )
    assert [finding.text for finding in result.findings] == ["focal epilepsy"]
    assert result.diagnostics["added_dictionary_findings"] == 0


def test_pre_post_suggested_evidence_uses_high_priority_cues() -> None:
    letter = ExectLetter(
        letter_id="EA0000",
        note_text="Diagnosis: Epilepsy, probable focal onset. She remains well.",
    )
    payload = json.loads(
        structured.build_prompt_input(
            letter, prompt_version=structured.EXECT_LLM_PRE_POST
        )
    )
    expected = [
        {
            "family": str(row["family"]),
            "evidence": str(row["evidence"]),
            "name_hint": str(row["anchor_hint"]),
            "category": str(row["lane_hint"]),
        }
        for row in structured.high_priority_evidence_ledger_for_letter(letter)
    ]
    assert payload["suggested_evidence"] == expected
    assert payload["suggested_evidence"]
