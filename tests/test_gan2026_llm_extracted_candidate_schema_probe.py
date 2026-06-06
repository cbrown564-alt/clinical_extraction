from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_extracted_candidate_schema_probe as probe,
)


def test_candidate_draft_set_wraps_bare_qwen_candidate_list() -> None:
    draft_set = probe.CandidateDraftSet.model_validate(
        [
            {
                "candidate_kind": "unknown_frequency",
                "event_type": "seizure",
                "unknown_frequency": {"source_phrase": "several episodes"},
                "temporality": "recent",
                "certainty": "uncertain",
                "assertion_status": "asserted",
                "evidence_text": "several episodes",
            }
        ]
    )

    draft = draft_set.candidates[0]
    assert draft.certainty_reason == "other"
    assert draft.unknown_frequency is not None
    assert draft.unknown_frequency.source_phrase == "several episodes"


def test_candidate_draft_accepts_qwen_alias_and_extra_fields() -> None:
    draft = probe.CandidateDraft.model_validate(
        {
            "candidate_kind": "frequency_rate",
            "event_type": "seizure",
            "detail": {
                "frequency": {
                    "source_phrase": "six seizures per month",
                    "parsed_count": 6,
                }
            },
            "temporality": "future",
            "certainty": "certain",
            "certainty_reason": "other",
            "assertion_status": "asserted",
            "evidence_text": "six seizures per month",
            "candidate_id": "c1",
        }
    )

    assert draft.temporality == "unclear"
    assert draft.certainty_reason is None
    assert draft.frequency is not None
    assert draft.frequency.source_phrase == "six seizures per month"


def test_candidate_draft_fills_missing_matching_detail_from_evidence() -> None:
    draft = probe.CandidateDraft.model_validate(
        {
            "candidate_kind": "cluster_frequency",
            "event_type": "seizure",
            "cluster_details": {"source_phrase": "clusters twice weekly"},
            "temporality": "current",
            "certainty": "certain",
            "assertion_status": "asserted",
            "evidence_text": "clusters twice weekly",
        }
    )

    assert draft.cluster_details is not None
    assert draft.cluster_details.cluster_frequency == "clusters twice weekly"
