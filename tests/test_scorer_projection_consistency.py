"""Phase-4 standing guardrail: scorer <-> projection scope consistency.

The pipeline-assumption audit found the *same* future/weight-based concept
implemented at three layers with inconsistent text scope (Phase 0 doc,
"Scorer <-> projection scope disagreements"). The scorer used to match the whole
span while the convention/projection layer already truncated at the cue and kept
the current-dose head. Phase 1 reconciled the scorer to the projection's
clause-scope.

This test fails if the two layers ever drift apart again: on a set of spans
where a naive full-span decision and a clause-scoped decision *disagree*, the
scorer's ``clinical_headline`` membership decision must match the convention
layer's current-regimen retention decision (``prescription_residual_additions``,
whose truncation at ``deterministic/conventions/prescription.py`` L266-268 is the
reference clause-scope implementation).

Each construct pairs:
- a ``note_text`` the projection reads, and
- an ``ExectAnnotation`` the scorer reads,

describing the same regimen, and is chosen so that a full-span reading (cue
anywhere -> drop) and a clause-scoped reading (current dose before the cue ->
keep) give opposite answers. The two layers must now agree construct-by-construct.

Constructs use only future cues shared by both layers' cue vocabularies
("to reduce", "increase to", "reducing") and drug/dose/frequency tuples on the
convention layer's residual whitelist, so the only free variable is text scope.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions.prescription import (
    prescription_residual_additions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
    _prescription_component_key,
)


@dataclass(frozen=True)
class _ScopeCase:
    name: str
    note_text: str
    annotation: ExectAnnotation
    # The clause-scoped (correct) expectation: True = current dose precedes the
    # cue, so the current fact is retained; False = the dose only appears after
    # the cue (future-only), so it is dropped.
    keep_expected: bool


def _rx(text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity="Prescription", text=text, attributes=dict(attrs))


# Each RETAIN case is precisely where full-span and clause-scope DISAGREE: a
# future cue is present (full-span would drop) but a concrete current dose
# precedes it (clause-scope keeps). Each DROP case has the dose only after the
# cue, so both readings drop — included to pin the negative side of the boundary.
_CASES: tuple[_ScopeCase, ...] = (
    _ScopeCase(
        name="valproate_reducing_tail_retain",
        note_text="Current medication: sodium valproate 500mg od, reducing over the next month.",
        annotation=_rx(
            "sodium valproate 500mg od, reducing over the next month",
            DrugName="sodium valproate",
            DrugDose="500",
            DoseUnit="mg",
            Frequency="1",
        ),
        keep_expected=True,
    ),
    _ScopeCase(
        name="valproate_reduce_to_target_drop",
        note_text="Current medication: sodium valproate, reducing to 500mg od.",
        annotation=_rx(
            "sodium valproate, reducing to 500mg od",
            DrugName="sodium valproate",
            DrugDose="500",
            DoseUnit="mg",
            Frequency="1",
        ),
        keep_expected=False,
    ),
    _ScopeCase(
        name="lamotrigine_reduce_and_stop_tail_retain",
        note_text="Current medication: lamotrigine 100mg bd, to reduce and stop over 6 weeks.",
        annotation=_rx(
            "lamotrigine 100mg bd, to reduce and stop over 6 weeks",
            DrugName="lamotrigine",
            DrugDose="100",
            DoseUnit="mg",
            Frequency="2",
        ),
        keep_expected=True,
    ),
    _ScopeCase(
        name="lamotrigine_increase_to_target_drop",
        note_text="Current medication: lamotrigine, increase to 100mg bd.",
        annotation=_rx(
            "lamotrigine, increase to 100mg bd",
            DrugName="lamotrigine",
            DrugDose="100",
            DoseUnit="mg",
            Frequency="2",
        ),
        keep_expected=False,
    ),
    _ScopeCase(
        name="valproate_weight_tail_retain",
        note_text="Current medication: sodium valproate 500mg od (60mg/kg/day).",
        annotation=_rx(
            "sodium valproate 500mg od (60mg/kg/day)",
            DrugName="sodium valproate",
            DrugDose="500",
            DoseUnit="mg",
            Frequency="1",
        ),
        keep_expected=True,
    ),
)


def _scorer_keeps(case: _ScopeCase) -> bool:
    """True iff the scorer keeps the regimen in the clinical headline."""

    return _prescription_component_key(case.annotation, "clinical_headline") is not None


def _projection_keeps(case: _ScopeCase) -> bool:
    """True iff the convention layer retains the regimen as a current addition."""

    return len(prescription_residual_additions(case.note_text)) > 0


@pytest.mark.parametrize("case", _CASES, ids=lambda c: c.name)
def test_scorer_and_projection_agree_on_current_vs_future(case: _ScopeCase) -> None:
    scorer = _scorer_keeps(case)
    projection = _projection_keeps(case)

    assert scorer == case.keep_expected, (
        f"{case.name}: scorer keep={scorer} but clause-scope expects {case.keep_expected}"
    )
    assert projection == case.keep_expected, (
        f"{case.name}: projection keep={projection} but clause-scope expects {case.keep_expected}"
    )
    assert scorer == projection, (
        f"{case.name}: scorer and projection classify current-vs-future differently "
        f"(scorer keep={scorer}, projection keep={projection}) -- the two layers "
        "have drifted apart on text scope again"
    )


def test_retain_cases_are_where_full_span_would_disagree() -> None:
    """Sanity: the RETAIN constructs really are full-span/clause-scope conflicts.

    Without this, the consistency assertions could pass vacuously on spans where
    no future cue is present. Every RETAIN case must contain a future cue (so a
    naive full-span scorer would drop it) yet be kept by both layers.
    """

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
        _PRESCRIPTION_FUTURE_PLAN,
        _PRESCRIPTION_WEIGHT_BASED_DOSE,
    )

    retain_cases = [c for c in _CASES if c.keep_expected]
    assert retain_cases, "no RETAIN cases defined"
    for case in retain_cases:
        text = case.annotation.text
        has_cue = bool(_PRESCRIPTION_FUTURE_PLAN.search(text)) or bool(
            _PRESCRIPTION_WEIGHT_BASED_DOSE.search(text)
        )
        assert has_cue, (
            f"{case.name} has no future/weight cue -- it is not a full-span "
            "conflict and cannot test scope reconciliation"
        )
        assert _scorer_keeps(case) and _projection_keeps(case)
