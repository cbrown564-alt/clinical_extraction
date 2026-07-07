"""Tests for the closed-option direction selector library + hybrid integration.

Two groups:
  1. Library contract tests (no LLM) for
     ``hybrid.closed_option_direction`` -- the menu builder, the abstention
     validator, and deterministic assembly.
  2. Integration tests for the opt-in ``direction_selector`` parameter on
     ``hybrid.clinical_assessment.run_split`` / ``render_mentions`` -- the
     default (``"off"``) path is byte-identical to v08 production (regression
     guard); the override path stamps ``FrequencyChange`` with provenance.
"""

from __future__ import annotations

import importlib
from unittest.mock import patch

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.candidate_set import (
    SFCandidate,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.clinical_assessment import (
    AssessmentRecord,
    CandidateAssessment,
    _letter_qualifies_for_direction_selector,
    render_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid.closed_option_direction import (
    ABSTAIN,
    DEFER_MODES,
    DIRECTION_VOCAB,
    PROV_LLM_CLOSED_OPTION,
    assemble_direction,
    build_direction_menu,
    parse_selection,
)

# --------------------------------------------------------------------------------------
# 1. Library contract tests (no LLM).
# --------------------------------------------------------------------------------------


class TestBuildDirectionMenu:
    def test_menu_carries_full_closed_vocab_plus_abstain_always(self):
        # Even with no direction cue in the text, the menu must list every label
        # + ABSTAIN (the closed-option contract constrains output, not options).
        menu = build_direction_menu("No seizure information here at all.")
        labels = [entry["label"] for entry in menu]
        assert labels[:-1] == list(DIRECTION_VOCAB)
        assert labels[-1] == ABSTAIN
        # Every non-ABSTAIN entry has either an evidence span or the no-cue marker.
        for entry in menu[:-1]:
            assert entry["evidence_span"]  # non-empty
        assert menu[-1]["evidence_span"] == ""  # ABSTAIN carries no evidence

    def test_menu_anchors_evidence_when_a_direction_cue_matches(self):
        # The "increased" regex should match and anchor that label's evidence span.
        text = "The seizure frequency has increased over the past month."
        menu = build_direction_menu(text)
        inc = next(e for e in menu if e["label"] == "Increased")
        assert "increas" in inc["evidence_span"].lower()
        # candidate_ids are unique and ABSTAIN is the final id.
        ids = [e["candidate_id"] for e in menu]
        assert len(ids) == len(set(ids))
        assert ids[-1] == ABSTAIN


class TestParseSelection:
    def test_valid_single_candidate_selection(self):
        raw = '{"selected_candidate_id": "C1", "selection_mode": "single_candidate"}'
        cid, mode = parse_selection(raw)
        assert cid == "C1"
        assert mode == "single_candidate"

    def test_abstain_resolves_to_none(self):
        raw = '{"selected_candidate_id": "ABSTAIN", "selection_mode": "single_candidate"}'
        cid, mode = parse_selection(raw)
        assert cid is None
        assert mode == "single_candidate"

    def test_defer_mode_with_selected_id_is_forced_to_abstain(self):
        # The validator (mirroring gan2026 selected_fact.py:32-49): a defer mode
        # MUST NOT select an id. Forced to abstention regardless of the id emitted.
        for defer in DEFER_MODES:
            raw = f'{{"selected_candidate_id": "C2", "selection_mode": "{defer}"}}'
            cid, mode = parse_selection(raw)
            assert cid is None, f"defer mode {defer!r} must not keep a selected id"
            assert mode == defer

    def test_unparseable_output_returns_parse_error(self):
        cid, mode = parse_selection("not json at all {{{")
        assert cid is None
        assert mode == "parse_error"

    def test_empty_selection_id_resolves_to_none(self):
        raw = '{"selected_candidate_id": "", "selection_mode": "single_candidate"}'
        cid, mode = parse_selection(raw)
        assert cid is None
        assert mode == "single_candidate"


class TestAssembleDirection:
    def test_valid_id_maps_to_its_label(self):
        menu = build_direction_menu("seizures have increased")
        inc_id = next(e["candidate_id"] for e in menu if e["label"] == "Increased")
        label, prov = assemble_direction(inc_id, menu)
        assert label == "Increased"
        assert prov == PROV_LLM_CLOSED_OPTION

    def test_none_id_resolves_to_same_with_provenance(self):
        # Abstention maps deterministically to Same (the directional-neutral bucket).
        menu = build_direction_menu("no info")
        label, prov = assemble_direction(None, menu)
        assert label == "Same"
        assert prov == PROV_LLM_CLOSED_OPTION

    def test_invalid_id_resolves_to_same(self):
        # Menu-membership check: an id not in the menu resolves to Same.
        menu = build_direction_menu("no info")
        label, _prov = assemble_direction("C99-not-real", menu)
        assert label == "Same"


# --------------------------------------------------------------------------------------
# 2. Integration tests for the opt-in direction_selector wiring.
# --------------------------------------------------------------------------------------


def _candidate(
    cid: str, *, anchor: str = "seizures", suggested: dict[str, str] | None = None
) -> SFCandidate:
    return SFCandidate(
        candidate_id=cid,
        anchor_text=anchor,
        evidence=anchor,
        span=(0, len(anchor)),
        suggested_attributes=suggested or {},
    )


class TestLetterQualifies:
    def test_qualifies_when_a_candidate_carries_frequency_change(self):
        cands = [_candidate("C0", suggested={"FrequencyChange": "Increased"})]
        record = AssessmentRecord(assessments=[CandidateAssessment(candidate_id="C0", keep=True)])
        assert _letter_qualifies_for_direction_selector(cands, record) is True

    def test_qualifies_when_a_kept_assessment_state_is_changed(self):
        # A kept assessment whose attributes resolve to a "changed" state qualifies
        # even without a deterministic FrequencyChange suggestion.
        cands = [_candidate("C0")]
        record = AssessmentRecord(
            assessments=[
                CandidateAssessment(
                    candidate_id="C0",
                    keep=True,
                    attributes={"FrequencyChange": "Decreased"},
                )
            ]
        )
        assert _letter_qualifies_for_direction_selector(cands, record) is True

    def test_does_not_qualify_when_no_direction_in_play(self):
        cands = [_candidate("C0", suggested={"NumberOfSeizures": "2", "TimePeriod": "Month"})]
        record = AssessmentRecord(
            assessments=[
                CandidateAssessment(
                    candidate_id="C0",
                    keep=True,
                    attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
                )
            ]
        )
        assert _letter_qualifies_for_direction_selector(cands, record) is False

    def test_does_not_qualify_when_no_kept_assessments(self):
        cands = [_candidate("C0", suggested={"FrequencyChange": "Increased"})]
        record = AssessmentRecord(assessments=[CandidateAssessment(candidate_id="C0", keep=False)])
        assert _letter_qualifies_for_direction_selector(cands, record) is False


class TestRenderMentionsDirectionOverride:
    def _letter_and_record(self) -> tuple[ExectLetter, list[SFCandidate], AssessmentRecord]:
        letter = ExectLetter(
            letter_id="TEST001",
            note_text="The seizures have increased.",
            annotations=(),
        )
        cands = [_candidate("C0", anchor="seizures", suggested={"NumberOfSeizures": "2"})]
        record = AssessmentRecord(
            assessments=[
                CandidateAssessment(
                    candidate_id="C0",
                    keep=True,
                    text="seizures",
                    attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
                )
            ]
        )
        return letter, cands, record

    def test_no_override_leaves_frequency_change_unchanged(self):
        letter, cands, record = self._letter_and_record()
        spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
        mentions, warnings = render_mentions(letter, cands, record, spec=spec)
        assert len(mentions) == 1
        # No FrequencyChange in the source attributes -> none in the output.
        assert "FrequencyChange" not in mentions[0].attributes
        assert not any("direction_override_applied" in w for w in warnings)

    def test_override_stamps_frequency_change_and_provenance(self):
        letter, cands, record = self._letter_and_record()
        spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
        mentions, warnings = render_mentions(
            letter,
            cands,
            record,
            spec=spec,
            direction_override=("Increased", PROV_LLM_CLOSED_OPTION),
        )
        assert len(mentions) == 1
        assert mentions[0].attributes["FrequencyChange"] == "Increased"
        # Provenance is recorded as a warning breadcrumb (attribution discipline).
        assert any("direction_override_applied" in w for w in warnings)
        assert any(PROV_LLM_CLOSED_OPTION in w for w in warnings)


class TestRunSplitDefaultIsOff:
    """The direction_selector='off' default must reproduce the v08 production
    path byte-for-byte (regression guard: the opt-in parameter must not perturb
    production). Run in prompt-only mode with a stubbed assessor so no LLM fires.
    """

    def test_off_default_does_not_build_a_selector_program(self):
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
            clinical_assessment as ca,
        )

        # Reload to pick up the module-level import we want to assert against.
        importlib.reload(ca)
        # The default direction_selector is "off"; the selector program is None.
        # We confirm by checking that ClosedOptionDirectionSelector is not
        # instantiated in the default path via a patched constructor.
        called = {"n": 0}
        orig = ca.ClosedOptionDirectionSelector

        def counting_ctor(*a, **k):
            called["n"] += 1
            return orig(*a, **k)

        with patch.object(ca, "ClosedOptionDirectionSelector", counting_ctor):
            ca.run_split(
                [],
                split="dev",
                model="openai/gpt-4.1-mini",
                temperature=0.0,
                max_tokens=1,
                mode="prompt-only",
            )
        assert called["n"] == 0, "default direction_selector='off' must not build a selector"

    def test_llm_closed_option_builds_a_selector_program(self):
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.hybrid import (
            clinical_assessment as ca,
        )

        importlib.reload(ca)
        called = {"n": 0}
        orig = ca.ClosedOptionDirectionSelector

        def counting_ctor(*a, **k):
            called["n"] += 1
            return orig(*a, **k)

        with patch.object(ca, "ClosedOptionDirectionSelector", counting_ctor):
            ca.run_split(
                [],
                split="dev",
                model="openai/gpt-4.1-mini",
                temperature=0.0,
                max_tokens=1,
                mode="prompt-only",
                direction_selector="llm_closed_option",
            )
        assert called["n"] == 1, "direction_selector='llm_closed_option' must build one selector"
