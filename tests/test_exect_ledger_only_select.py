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


def _source() -> FindingSource:
    return FindingSource(
        producer_id="model",
        artifact_path="test",
        pipeline_family="test",
        model="test",
        prompt_version="test",
        mode="replay",
        ownership_label="model",
        source_lane="model",
    )


def _dx_finding(
    text: str,
    *,
    diag_category: str,
    evidence: str | None = None,
    letter_id: str = "EA0000",
) -> ClinicalFinding:
    return ClinicalFinding(
        finding_id=f"{letter_id}:{text}",
        letter_id=letter_id,
        entity="Diagnosis",
        text=text,
        attributes={"DiagCategory": diag_category},
        evidence=evidence or text,
        normalized_concept=text,
        assertion=None,
        confidence="high",
        source=_source(),
        provenance=(),
    )


def _reconcile_diagnosis(*findings: ClinicalFinding, note: str = ""):
    letter_id = findings[0].letter_id
    store = ClinicalFindingStore(letter_id, note)
    for finding in findings:
        store.add(finding)
    return DiagnosisDictionaryLens(
        lens_id="diagnosis_convention_dictionary_v09",
        entity="Diagnosis",
    ).reconcile(
        store,
        policy=LensPolicy(
            producer_id="model",
            source_lane="model",
            ownership_label="model",
            portability="benchmark_format",
        ),
    )


def test_diagnosis_lens_does_not_add_letter_scan_residuals() -> None:
    note = "Diagnosis: Epilepsy, probable focal onset. She remains well."
    leftovers = sd.diagnosis_residual_additions(note)
    assert leftovers
    result = _reconcile_diagnosis(
        _dx_finding(
            "epilepsy",
            diag_category="Epilepsy",
            evidence="Diagnosis: Epilepsy, probable focal onset.",
        ),
        note=note,
    )
    assert [finding.text for finding in result.findings] == ["focal epilepsy"]
    assert result.diagnostics["added_dictionary_findings"] == 0


def test_diagnosis_lens_repairs_category_on_kept_canonical_seizure_types() -> None:
    result = _reconcile_diagnosis(
        _dx_finding("secondary generalised seizures", diag_category="Epilepsy"),
        _dx_finding("partial motor seizures", diag_category="Epilepsy"),
        _dx_finding("epilepsy", diag_category="Epilepsy"),
        _dx_finding("focal seizure", diag_category="Epilepsy"),
        _dx_finding("focal seizures", diag_category="Epilepsy"),
    )
    by_text = {finding.text: finding.attributes["DiagCategory"] for finding in result.findings}
    assert by_text["secondary generalised seizures"] == "MultipleSeizures"
    assert by_text["partial motor seizures"] == "MultipleSeizures"
    assert by_text["epilepsy"] == "Epilepsy"
    assert by_text["focal seizure"] == "SingleSeizure"
    assert by_text["focal seizures"] == "MultipleSeizures"


def test_diagnosis_lens_repairs_category_after_noise_drop() -> None:
    result = _reconcile_diagnosis(
        _dx_finding("absence seizures", diag_category="Epilepsy"),
    )
    assert [finding.text for finding in result.findings] == ["absence seizures"]
    assert result.findings[0].attributes["DiagCategory"] == "MultipleSeizures"


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
