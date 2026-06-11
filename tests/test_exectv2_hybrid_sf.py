"""Tests for the ExECTv2 hybrid (candidate + assessment) SeizureFrequency extractor.

Covers:
  - Prompt hygiene: no internal architecture vocabulary in model-facing strings
  - build_candidate_set: live, high-recall (keeps bare seizure-type anchors)
  - parse_assessment_json: valid/invalid/coerced
  - normalize_attributes: number-word / unit / month canonicalization
  - render_mentions: keep/drop, deterministic CUI render, illegal-flag stripping
  - verify_and_route: evidence + plausibility routing; routed taxonomy
  - assess_letter: end-to-end render + route on a fixture
"""

from __future__ import annotations

import json

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    SEIZURE_FREQUENCY,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
    candidate_set,
    clinical_assessment,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.candidate_set import (
    build_candidate_set,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.clinical_assessment import (
    AssessmentRecord,
    CandidateAssessment,
    assess_letter,
    build_prompt_input,
    normalize_attributes,
    parse_assessment_json,
    render_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.verify_route import (
    routed_taxonomy,
    verify_and_route,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────

_NOTE = (
    "This lady is a 42-year-old with focal epilepsy. "
    "She reports approximately 2 seizures per month, down from 4 per month "
    "before the medication change. She has been seizure free for 3 months "
    "following the last dose adjustment."
)
_LETTER = ExectLetter(letter_id="TEST001", note_text=_NOTE)
_SF_SPEC = ENTITY_REGISTRY[SEIZURE_FREQUENCY]

# A bare seizure type (no frequency) plus one with a rate, to prove high recall.
_BARE_NOTE = "He has focal seizures. His tonic-clonic seizures occur 3 times a week."
_BARE_LETTER = ExectLetter(letter_id="TEST002", note_text=_BARE_NOTE)


# ── Prompt hygiene ────────────────────────────────────────────────────────────

FORBIDDEN_PHRASES = (
    "Decision 000",
    "decision 000",
    "deterministic code",
    "downstream deterministic",
    "architecture gate",
    "deterministic candidates",
    "gold labels",
    "gold_label",
    "parser-ready",
    "scorer-facing",
    "scoring-facing",
    "benchmark",
    "synthetic",
    "prompt_policy_taxonomy",
    " -> ",
)


def test_prompt_hygiene_no_internal_vocabulary() -> None:
    candidates = build_candidate_set(_LETTER)
    text = build_prompt_input(_LETTER, candidates)
    leaked = [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]
    assert leaked == [], f"leaked internal phrases {leaked}"


def test_prompt_is_valid_json_and_carries_candidates() -> None:
    candidates = build_candidate_set(_LETTER)
    payload = json.loads(build_prompt_input(_LETTER, candidates))
    assert payload["letter_id"] == "TEST001"
    assert payload["candidates"]  # non-empty
    assert {"candidate_id", "anchor_text", "evidence"} <= set(payload["candidates"][0])


# ── Candidate set ─────────────────────────────────────────────────────────────


def test_candidate_set_evidence_is_substring() -> None:
    for c in build_candidate_set(_LETTER):
        assert c.evidence in _NOTE
        assert c.candidate_id.startswith("C")


def test_candidate_set_is_high_recall_keeps_bare_anchor() -> None:
    """A seizure type with no nearby frequency is still offered as a candidate."""
    cands = build_candidate_set(_BARE_LETTER)
    anchors = {c.anchor_text for c in cands}
    # 'focal seizures' has no frequency information — the deterministic pipeline
    # would drop it, but the candidate set must keep it for the LLM to judge.
    assert any("focal seizures" in a for a in anchors)
    bare = [c for c in cands if "focal seizures" in c.anchor_text]
    assert bare and bare[0].suggested_attributes == {}


def test_candidate_set_union_with_llm_candidates() -> None:
    base = build_candidate_set(_LETTER)
    extra = candidate_set.SFCandidate(
        candidate_id="X",
        anchor_text="drop attacks",
        evidence="rare drop attacks",
        span=(0, 5),
        source="llm",
    )
    merged = build_candidate_set(_LETTER, llm_candidates=[extra])
    assert len(merged) == len(base) + 1
    assert merged[-1].source == "llm"
    assert merged[-1].anchor_text == "drop attacks"


# ── parse_assessment_json ─────────────────────────────────────────────────────


def test_parse_valid_assessment() -> None:
    raw = json.dumps({
        "assessments": [
            {
                "candidate_id": "C0",
                "keep": True,
                "text": "seizures",
                "attributes": {"NumberOfSeizures": "2", "TimePeriod": "Month"},
                "confidence": "high",
                "uncertainty_flags": [],
                "rationale": "2 per month.",
            }
        ],
        "additional_mentions": [],
        "aggregation_policy": "one_mention_per_seizure_type",
    })
    record, errors = parse_assessment_json(raw)
    assert record is not None
    assert len(record.assessments) == 1
    assert record.assessments[0].keep is True
    assert not any(e.startswith(("invalid_json:", "schema_validation_error:")) for e in errors)


def test_parse_invalid_json() -> None:
    record, errors = parse_assessment_json("not json {")
    assert record is None
    assert any(e.startswith("invalid_json:") for e in errors)


def test_parse_empty_defaults() -> None:
    record, errors = parse_assessment_json(json.dumps({"other": 1}))
    assert record is not None
    assert record.assessments == []
    assert record.aggregation_policy == "one_mention_per_seizure_type"


def test_parse_python_dict_literal_is_repaired() -> None:
    """qwen3.6 emits Python-dict-style output (single quotes, True/False); the
    parser recovers it via a neutral literal_eval fallback."""
    raw = (
        "{'assessments': [{'candidate_id': 'C0', 'keep': True, 'text': 'seizures', "
        "'attributes': {'NumberOfSeizures': '2', 'TimePeriod': 'Month'}, "
        "'confidence': 'high', 'uncertainty_flags': [], 'rationale': \"two per month\"}], "
        "'additional_mentions': [], 'aggregation_policy': 'one_mention_per_seizure_type'}"
    )
    record, errors = parse_assessment_json(raw)
    assert record is not None
    assert record.assessments[0].keep is True
    assert record.assessments[0].attributes["NumberOfSeizures"] == "2"
    assert any("repaired_python_dict_literal" in e for e in errors)


def test_parse_coerces_numeric_attribute_values() -> None:
    raw = json.dumps({
        "assessments": [
            {"candidate_id": "C0", "keep": True, "attributes": {"NumberOfSeizures": 2}}
        ]
    })
    record, errors = parse_assessment_json(raw)
    assert record is not None
    assert record.assessments[0].attributes["NumberOfSeizures"] == "2"
    assert any("coerced_attribute_value" in e for e in errors)


# ── normalize_attributes ──────────────────────────────────────────────────────


def test_normalize_attributes_canonicalizes() -> None:
    out = normalize_attributes(
        {"NumberOfSeizures": "two", "TimePeriod": "months", "MonthDate": "January"}
    )
    assert out["NumberOfSeizures"] == "2"
    assert out["TimePeriod"] == "Month"
    assert out["MonthDate"] == "1"


# ── render_mentions ───────────────────────────────────────────────────────────


def test_render_drops_unkept_and_attaches_cui() -> None:
    candidates = build_candidate_set(_LETTER)
    c0 = candidates[0]
    record = AssessmentRecord(
        assessments=[
            CandidateAssessment(
                candidate_id=c0.candidate_id,
                keep=True,
                text=c0.anchor_text,
                attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
            ),
            CandidateAssessment(candidate_id="C1", keep=False),
        ]
    )
    mentions, _warn = render_mentions(_LETTER, candidates, record, spec=_SF_SPEC)
    assert len(mentions) == 1
    m = mentions[0]
    assert m.text == c0.anchor_text
    if assign_cui(c0.anchor_text) is not None:
        assert m.attributes["CUI"] == assign_cui(c0.anchor_text)


def test_render_strips_illegal_attribute_and_flag() -> None:
    candidates = build_candidate_set(_LETTER)
    c0 = candidates[0]
    record = AssessmentRecord(
        assessments=[
            CandidateAssessment(
                candidate_id=c0.candidate_id,
                keep=True,
                text=c0.anchor_text,
                attributes={"TimePeriod": "Month", "BogusAttr": "x"},
                uncertainty_flags=["vague_count", "not_a_real_flag"],
            )
        ]
    )
    mentions, warnings = render_mentions(_LETTER, candidates, record, spec=_SF_SPEC)
    assert "BogusAttr" not in mentions[0].attributes
    assert mentions[0].uncertainty_flags == ("vague_count",)
    assert any("dropped_illegal_attribute" in w for w in warnings)
    assert any("dropped_uncertainty_flag" in w for w in warnings)


def test_render_additional_mention_must_be_substring() -> None:
    record = AssessmentRecord(
        additional_mentions=[
            clinical_assessment.AdditionalMention(
                text="phrase not present in letter",
                attributes={"TimePeriod": "Week"},
                evidence="phrase not present in letter",
            )
        ]
    )
    mentions, warnings = render_mentions(_LETTER, [], record, spec=_SF_SPEC)
    assert mentions == []
    assert any("dropped_additional_text_not_substring" in w for w in warnings)


# ── verify_and_route ──────────────────────────────────────────────────────────


def _mention(text: str, attrs: dict[str, str], evidence: str) -> PredictedMention:
    return PredictedMention(
        entity=SEIZURE_FREQUENCY, text=text, attributes=attrs, evidence=evidence
    )


def test_route_bare_nonzero_count() -> None:
    m = _mention("seizures", {"NumberOfSeizures": "4"}, "4 seizures")
    kept, routed = verify_and_route([m], note_text="he had 4 seizures")
    assert kept == []
    assert routed[0].reason == "bare_nonzero_count"


def test_keep_frequency_bearing_and_zero_count() -> None:
    freq = _mention("seizures", {"NumberOfSeizures": "2", "TimePeriod": "Month"}, "2 seizures per month")
    zero = _mention("seizure free", {"NumberOfSeizures": "0"}, "seizure free")
    note = "2 seizures per month; now seizure free"
    kept, routed = verify_and_route([freq, zero], note_text=note)
    assert len(kept) == 2
    assert routed == []


def test_route_evidence_not_substring_and_empty_attrs() -> None:
    bad_ev = _mention("seizures", {"TimePeriod": "Week"}, "not in the note")
    no_attr = _mention("seizures", {}, "seizures")
    note = "weekly seizures"
    kept, routed = verify_and_route([bad_ev, no_attr], note_text=note)
    reasons = {r.reason for r in routed}
    assert kept == []
    assert reasons == {"evidence_not_substring", "no_frequency_attributes"}
    tax = routed_taxonomy(routed)
    assert tax["evidence_not_substring"] == 1
    assert tax["no_frequency_attributes"] == 1


def test_cui_only_attrs_are_not_frequency_bearing() -> None:
    m = _mention("seizures", {"CUI": "C0036572", "CUIPhrase": "seizures"}, "seizures")
    kept, routed = verify_and_route([m], note_text="he had seizures")
    assert kept == []
    assert routed[0].reason == "no_frequency_attributes"


# ── assess_letter (integration) ───────────────────────────────────────────────


def test_run_split_resume_skips_completed(tmp_path) -> None:
    """A second run with resume=True processes only the not-yet-done letters and
    merges old+new back into split order (foundational runner requirement)."""
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.clinical_assessment import (
        run_split,
        write_jsonl,
    )

    letters = load_letters_for_split("dev")[:5]
    ckpt = tmp_path / "ckpt.jsonl"

    # First pass: only the first 3 letters, checkpointed.
    rows3, _ = run_split(
        letters[:3], split="dev", model="x", temperature=0.0, max_tokens=10,
        mode="prompt-only", checkpoint_jsonl_path=ckpt,
    )
    write_jsonl(rows3, ckpt)

    # Resume over all 5: must reuse the 3, process 2, return 5 in order.
    rows5, meta = run_split(
        letters, split="dev", model="x", temperature=0.0, max_tokens=10,
        mode="prompt-only", checkpoint_jsonl_path=ckpt, resume=True,
    )
    assert meta["n_resumed"] == 3
    assert [r["letter_id"] for r in rows5] == [letter.letter_id for letter in letters]
    assert len(rows5) == 5


def test_assess_letter_end_to_end() -> None:
    candidates = build_candidate_set(_LETTER)
    # Keep both deterministic candidates with their suggested attributes.
    record = AssessmentRecord(
        assessments=[
            CandidateAssessment(
                candidate_id=c.candidate_id,
                keep=True,
                text=c.anchor_text,
                attributes=dict(c.suggested_attributes),
                confidence="high",
            )
            for c in candidates
        ]
    )
    predicted, routed, warnings = assess_letter(_LETTER, candidates, record, spec=_SF_SPEC)
    assert predicted.letter_id == "TEST001"
    # Both candidates are frequency-bearing → kept, none routed.
    assert len(predicted.mentions) == len(candidates)
    assert routed == []
    assert predicted.diagnostics["aggregation_policy"] == "one_mention_per_seizure_type"
    for m in predicted.mentions:
        assert m.evidence in _NOTE
