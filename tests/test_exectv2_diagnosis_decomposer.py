"""Tests for the ExECTv2 Diagnosis heading/narrative decomposer."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.clinical_finding import (
    FindingSource,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lens_ops import (
    LensPolicy,
    diagnosis_added_finding,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    diagnosis_concept,
    diagnosis_fragment_concept,
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import DIAGNOSIS
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    diagnosis_decomposer as decomposer,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    MentionRecord,
)

_NOTE = (
    "Diagnosis: epilepsy - probable focal. "
    "Seizure type and frequency: generalised tonic clonic seizures every month. "
    "Family history of epilepsy but no history of febrile seizures."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)


def test_diagnosis_spans_decompose_heading_and_narrative() -> None:
    spans = decomposer.diagnosis_spans_for_letter(_LETTER)
    payloads = [span.as_payload() for span in spans]

    heading = next(item for item in payloads if item["span_role"] == "diagnosis-heading")
    assert heading["evidence"] == "Diagnosis: epilepsy - probable focal."
    assert "epilepsy" in heading["concept_hints"]
    assert "focal epilepsy" in heading["concept_hints"]

    narrative = next(item for item in payloads if item["span_role"] == "narrative-seizure-type")
    assert "generalised tonic clonic seizures" in narrative["evidence"]
    assert "tonic clonic seizures" in narrative["concept_hints"]

    assert all("Family history" not in item["evidence"] for item in payloads)


def test_build_prompt_input_includes_decomposition_contract() -> None:
    payload = json.loads(
        decomposer.build_prompt_input(
            _LETTER,
            [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
        )
    )

    assert payload["prompt_version"] == decomposer.PROMPT_VERSION
    assert payload["prompt_version"].endswith("_v0.1")
    assert payload["diagnosis_candidate_spans"]
    assert {"diagnosis-heading", "narrative-seizure-type", "reconcile"} <= set(
        payload["decomposition_contract"]
    )
    rules = " ".join(payload["clinical_rules"])
    assert "candidate spans as a clinical checklist" in rules
    assert "explicitly ask: does this contain the word epilepsy" in rules
    assert "Do not emit CUI or CUIPhrase" in rules


def test_resolution_candidate_prompt_is_explicit_and_opt_in() -> None:
    payload = json.loads(
        decomposer.build_prompt_input(
            _LETTER,
            [],
            prompt_variant="resolution_v02",
        )
    )

    assert payload["prompt_version"].endswith("_v0.2")
    rules = " ".join(payload["clinical_rules"])
    assert "epileptic disorders and named epileptic seizure types only" in rules
    assert "service header" in rules
    assert "status epilepticus" in rules


def test_to_predicted_letter_strips_projection_attrs_and_projects_cui() -> None:
    pred, warnings = decomposer.to_predicted_letter(
        "TEST001",
        [
            MentionRecord(
                text="focal epilepsy",
                attributes={
                    "CUI": "WRONG",
                    "CUIPhrase": "wrong",
                    "DiagCategory": "Epilepsy",
                    "Certainty": "4",
                    "Negation": "Affirmed",
                },
                evidence="Diagnosis: epilepsy - probable focal.",
                confidence="high",
                rationale="Probable focal epilepsy.",
            )
        ],
        note_text=_NOTE,
    )

    assert pred.mentions[0].text == "focal epilepsy"
    assert pred.mentions[0].attributes["CUI"]
    assert pred.mentions[0].component_owner == decomposer.COMPONENT_OWNER
    assert any("dropped_model_supplied_projection_attribute" in warning for warning in warnings)


def test_summarize_rows_reports_diagnosis_spans() -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 1,
            "n_diagnosis_spans": 2,
            "n_mentions_raw": 1,
            "n_mentions_scored": 1,
            "n_evidence_invalid": 0,
            "gold_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                }
            ],
            "predicted_mentions": [
                {
                    "text": "focal epilepsy",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "Diagnosis: epilepsy - probable focal.",
                }
            ],
        }
    ]

    summary = decomposer.summarize_rows(rows)

    assert summary["clinical_recovery"]["diagnosis"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_only"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_negation"]["f1"] == 1.0
    assert summary["clinical_recovery"]["concept_assertion"]["f1"] == 1.0
    assert summary["clinical_recovery"]["target_headline_f1"] == 0.8
    assert summary["n_diagnosis_spans"] == 2


def test_write_report_includes_diagnosis_span_summary(tmp_path) -> None:
    rows = [
        {
            "letter_id": "TEST001",
            "parse_errors": [],
            "n_draft_mentions": 0,
            "n_diagnosis_spans": 2,
            "n_mentions_raw": 0,
            "n_mentions_scored": 0,
            "n_evidence_invalid": 0,
            "gold_mentions": [],
            "predicted_mentions": [],
        }
    ]
    path = tmp_path / "report.md"

    decomposer.write_report(
        rows,
        {
            "prompt_version": decomposer.PROMPT_VERSION,
            "pipeline_family": decomposer.PIPELINE_FAMILY,
            "split": "dev",
            "model": "test-model",
            "mode": "prompt-only",
        },
        path,
        jsonl_path=tmp_path / "rows.jsonl",
    )

    text = path.read_text(encoding="utf-8")
    assert "Heading/Narrative Decomposer" in text
    assert "Diagnosis spans" in text


def test_diagnosis_residual_gtcs_receives_benchmark_cui() -> None:
    """Hybrid residual additions must attach CUI after the model-lane projection."""

    note = (
        "Diagnosis: Complex partial seizures with secondary generalised tonic clonic seizures"
    )
    source = FindingSource(
        producer_id="gpt56sol_structured_model_facts",
        artifact_path="test.jsonl",
        pipeline_family="exectv2_structured_direct",
        model="openai/gpt-5.6-sol",
        prompt_version="test",
        mode="replay",
        ownership_label="gpt56sol_structured_model_facts",
        source_lane="model",
    )
    store = ClinicalFindingStore("EA0021", note_text=note)
    store.register_source(source)
    finding = diagnosis_added_finding(
        store,
        text="generalised tonic clonic seizures",
        evidence=note,
        selected=[],
        policy=LensPolicy(
            producer_id=source.producer_id,
            source_lane="model",
            ownership_label=source.ownership_label,
            portability="benchmark_format",
        ),
        lens_id="diagnosis_convention_dictionary_v09",
    )
    assert finding is not None
    assert finding.attributes.get("CUI") == "C0494475"
    assert finding.attributes.get("CUIPhrase") == "generalised-tonic-clonic-seizures"


def test_symptomatic_structural_focal_epilepsy_uses_gold_cui() -> None:
    """Gold CUI for this phrase is C0472349, not focal-epilepsy C0014547."""

    structural = diagnosis_concept("symptomatic structural focal epilepsy")
    hyphenated = diagnosis_concept("symptomatic-structural-focal-epilepsy")
    symptomatic_focal = diagnosis_concept("symptomatic focal epilepsy")
    focal = diagnosis_concept("focal epilepsy")
    assert structural is not None and hyphenated is not None
    assert symptomatic_focal is not None and focal is not None
    assert structural.cui == hyphenated.cui == "C0472349"
    assert structural.cui_phrase == "symptomatic structural focal epilepsy"
    assert symptomatic_focal.cui == "C0472349"
    assert symptomatic_focal.cui_phrase == "symptomatic-focal-epilepsy"
    assert focal.cui == "C0014547"

    target = sd.diagnosis_convention_target(
        "Symptomatic structural epilepsy",
        "Diagnosis: Symptomatic structural epilepsy",
    )
    assert target == "symptomatic structural focal epilepsy"
    rewritten = diagnosis_concept(target)
    assert rewritten is not None
    assert rewritten.cui == "C0472349"

    projected = project_cuis(
        PredictedLetter(
            letter_id="EA0133",
            mentions=(
                PredictedMention(
                    entity=DIAGNOSIS.name,
                    text="symptomatic structural focal epilepsy",
                    attributes={
                        "CUI": "C0014547",
                        "CUIPhrase": "symptomatic structural focal epilepsy",
                        "DiagCategory": "Epilepsy",
                    },
                    evidence="Diagnosis: Symptomatic structural epilepsy",
                ),
            ),
        )
    )
    assert projected.mentions[0].attributes["CUI"] == "C0472349"
    assert (
        projected.mentions[0].attributes["CUIPhrase"]
        == "symptomatic structural focal epilepsy"
    )


def test_genetic_and_primary_generalised_epilepsy_share_cui_keep_surface() -> None:
    genetic = diagnosis_concept("genetic generalised epilepsy")
    primary = diagnosis_concept("primary generalised epilepsy")
    assert genetic is not None and primary is not None
    assert genetic.cui == primary.cui == "C0270850"
    assert genetic.cui_phrase == "genetic-generalised-epilepsy"
    assert primary.cui_phrase == "primary-generalised-epilepsy"
    projected = project_cuis(
        PredictedLetter(
            letter_id="EA0200",
            mentions=(
                PredictedMention(
                    entity=DIAGNOSIS.name,
                    text="genetic generalised epilepsy",
                    attributes={
                        "CUI": "C0270850",
                        "CUIPhrase": "primary-generalised-epilepsy",
                        "DiagCategory": "Epilepsy",
                    },
                    evidence="Diagnosis: genetic generalised epilepsy",
                ),
            ),
        )
    )
    assert projected.mentions[0].attributes["CUIPhrase"] == "genetic-generalised-epilepsy"


def test_heading_fragment_residuals_keep_gold_cuis() -> None:
    assert diagnosis_concept("symptomatic") is None
    assert diagnosis_concept("generalised") is None
    symptomatic = diagnosis_fragment_concept("symptomatic")
    generalised = diagnosis_fragment_concept("generalised")
    assert symptomatic is not None and generalised is not None
    assert symptomatic.cui == "C1406659"
    assert symptomatic.cui_phrase == "symptomatic"
    assert generalised.cui == "C0494475"
    assert generalised.cui_phrase == "generalised"
