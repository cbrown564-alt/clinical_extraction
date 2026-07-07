"""Phase-4 standing guardrail: scorer clause-scope invariants.

Encodes the ExECTv2 pipeline-assumption-audit *seed defect* as a general,
family-agnostic property test so the whole class is caught structurally at
commit time rather than reactively after a run.

Seed defect (one sentence): *a fact's scored ``clinical_headline`` membership
must not depend on text outside that fact's own clause/scope.* The loudest
instance was the Prescription full-span future/weight regex
(``rx_future_medication_regex_scope_bug_2026-07-02``): a titration or mg/kg
phrase anywhere in the whole gold span nulled the entire current-dose fact from
the headline. Phase 1 clause-scoped the scorer (mirroring the convention layer's
truncate-at-cue). These tests lock that fix in place and generalize the
invariant to every family's ``clinical_headline_unit_keys`` builder.

Two complementary invariants are asserted:

1. **Note-context invariance (all four families).** Appending unrelated letter
   context to ``note_text`` must never change a family's headline key set. This
   is the general statement of "text outside the fact's own scope".
2. **Clause-scope invariance (Prescription, the load-bearing case).** Appending
   future/titration or weight-based language *after* a current-dose clause inside
   ``annotation.text`` must not change headline membership. A local
   re-implementation of the pre-fix full-span check proves the same perturbation
   *would* have flipped membership, so the invariant is load-bearing, not vacuous.

See ``docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md``.
"""

from __future__ import annotations

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
    _PRESCRIPTION_FUTURE_PLAN,
    _PRESCRIPTION_WEIGHT_BASED_DOSE,
    _is_future_medication,
    _is_weight_based_dosing,
    _prescription_component_key,
)

# An unrelated trailing sentence — text that is genuinely outside every fact's
# own clause. No family's headline key may react to it.
_OUT_OF_SCOPE_SENTENCE = " The patient will be reviewed again in six months in the epilepsy clinic."


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


# A clean, minimal, in-scope headline span for each family. The comment names the
# clause that legitimately determines the key.
_CLEAN_BY_FAMILY: dict[str, ExectAnnotation] = {
    # Rx current-dose regimen: name+dose+frequency (from attributes).
    "Prescription": _ann(
        "Prescription",
        "lamotrigine 150mg bd",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    ),
    # SF active-rate: seizure-type CUI + count attributes.
    "SeizureFrequency": _ann(
        "SeizureFrequency",
        "focal seizures",
        NumberOfSeizures="3",
        CUI="C0036572",
    ),
    # Inv attributed modality: modality + performed/result attributes.
    "Investigations": _ann(
        "Investigations",
        "EEG",
        EEG_Performed="Yes",
        EEG_Results="Abnormal",
    ),
    # Dx diagnosis: the canonicalized concept phrase itself.
    "Diagnosis": _ann(
        "Diagnosis",
        "focal epilepsy",
        DiagCategory="Epilepsy",
        Certainty="5",
        Negation="Affirmed",
    ),
}


@pytest.mark.parametrize("entity", sorted(_CLEAN_BY_FAMILY))
def test_headline_key_is_invariant_to_surrounding_note_text(entity: str) -> None:
    """Appending unrelated letter context must not move any headline key.

    ``note_text`` is the clearest "outside the fact's own scope" channel: it is
    the surrounding letter, not the fact. Every family's headline key set must be
    identical with and without an appended, unrelated sentence.
    """

    annotation = _CLEAN_BY_FAMILY[entity]

    baseline = clinical_headline_unit_keys(entity, [annotation], "")
    with_context = clinical_headline_unit_keys(
        entity, [annotation], "prior letter text." + _OUT_OF_SCOPE_SENTENCE
    )

    assert baseline, f"{entity} produced no headline key to test invariance against"
    assert baseline == with_context


def test_prescription_future_tail_does_not_change_headline_membership() -> None:
    """A titration tail after the current dose must not null the current fact."""

    clean = _CLEAN_BY_FAMILY["Prescription"]
    # Same current dose (attributes unchanged); only trailing titration language
    # is appended, SEPARATED from the dose clause by a comma.
    future_tail = _ann(
        "Prescription",
        "lamotrigine 150mg bd, to reduce and stop over the next six weeks",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )

    clean_keys = clinical_headline_unit_keys("Prescription", [clean])
    tail_keys = clinical_headline_unit_keys("Prescription", [future_tail])

    assert clean_keys == tail_keys
    assert tail_keys == [("ordinary", "lamotrigine", "150", "mg", "2")]
    # The clause-scoped predicate agrees: the trailing titration is not future-only.
    assert _is_future_medication(future_tail) is False


def test_prescription_weight_tail_does_not_change_headline_membership() -> None:
    """A mg/kg restatement after a concrete dose must not null the current fact."""

    clean = _ann(
        "Prescription",
        "levetiracetam 1500mg bd",
        DrugName="Levetiracetam",
        DrugDose="1500",
        DoseUnit="mg",
        Frequency="2",
    )
    weight_tail = _ann(
        "Prescription",
        "levetiracetam 1500mg bd (60mg/kg/day)",
        DrugName="Levetiracetam",
        DrugDose="1500",
        DoseUnit="mg",
        Frequency="2",
    )

    clean_keys = clinical_headline_unit_keys("Prescription", [clean])
    tail_keys = clinical_headline_unit_keys("Prescription", [weight_tail])

    assert clean_keys == tail_keys
    assert tail_keys == [("ordinary", "levetiracetam", "1500", "mg", "2")]
    assert _is_weight_based_dosing(weight_tail) is False


def _old_full_span_is_future(text: str) -> bool:
    """Pre-fix behavior: a future cue *anywhere* in the whole span nulled the fact.

    Reconstructed locally (the pre-Phase-1 ``_is_future_medication`` body) so the
    invariant above can be shown to be load-bearing rather than vacuous.
    """

    return _PRESCRIPTION_FUTURE_PLAN.search(text) is not None


def _old_full_span_is_weight(text: str) -> bool:
    """Pre-fix behavior: a mg/kg token anywhere in the whole span nulled the fact."""

    return _PRESCRIPTION_WEIGHT_BASED_DOSE.search(text) is not None


def test_prefix_full_span_behavior_would_have_flipped_membership() -> None:
    """Prove the invariant is load-bearing: the pre-fix full-span check flips.

    Under the old full-span logic the clean current-dose span was kept but the
    perturbed span (identical dose, trailing plan/weight language) was dropped —
    exactly the seed defect. The current clause-scoped scorer keeps both, so the
    perturbation is now inert. If a future refactor reintroduced full-span
    matching, ``test_prescription_*_tail_does_not_change_headline_membership``
    would fail; this test documents *why* those assertions matter.
    """

    clean_future = "lamotrigine 150mg bd"
    perturbed_future = "lamotrigine 150mg bd, to reduce and stop over the next six weeks"
    clean_weight = "levetiracetam 1500mg bd"
    perturbed_weight = "levetiracetam 1500mg bd (60mg/kg/day)"

    # Old full-span behavior: the perturbation flips the classification.
    assert _old_full_span_is_future(clean_future) is False
    assert _old_full_span_is_future(perturbed_future) is True
    assert _old_full_span_is_weight(clean_weight) is False
    assert _old_full_span_is_weight(perturbed_weight) is True

    # Current clause-scoped behavior: the perturbation is inert (no flip).
    future_clean_ann = _ann(
        "Prescription",
        clean_future,
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )
    future_pert_ann = _ann(
        "Prescription",
        perturbed_future,
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )
    assert _is_future_medication(future_clean_ann) is False
    assert _is_future_medication(future_pert_ann) is False


def test_prescription_future_medication_diagnostic_key_is_clause_scoped() -> None:
    """P6: the ``future_medication`` diagnostic key must depend only on the
    future-plan clause, not on unrelated text preceding it in the same span.

    Unlike the ``clinical_headline`` gate (fixed in Phase 1), the diagnostic
    key *construction* for a fact already gated in as future-only still used
    ``normalize_phrase(annotation.text)`` -- the whole span -- so two facts
    that share the same future clause but differ in unrelated leading text
    were spuriously treated as different keys. This diagnostic never feeds
    ``clinical_headline``, so the fix is cosmetic to a diagnostic component,
    not a citation-affecting change (see the Phase 4 guardrail doc, item P6).
    """

    future_only = _ann(
        "Prescription",
        "consider increasing lamotrigine to 300mg bd",
        DrugName="Lamotrigine",
        DrugDose="300",
        DoseUnit="mg",
        Frequency="2",
    )
    unrelated_prefix = _ann(
        "Prescription",
        "patient tolerating current regimen well, consider increasing lamotrigine to 300mg bd",
        DrugName="Lamotrigine",
        DrugDose="300",
        DoseUnit="mg",
        Frequency="2",
    )

    assert _is_future_medication(future_only) is True
    assert _is_future_medication(unrelated_prefix) is True

    key_a = _prescription_component_key(future_only, "future_medication")
    key_b = _prescription_component_key(unrelated_prefix, "future_medication")
    assert key_a is not None
    assert key_a == key_b

    # Load-bearing: the pre-P6 whole-span key construction would have differed.
    assert normalize_phrase(future_only.text) != normalize_phrase(unrelated_prefix.text)


def test_prescription_weight_based_dosing_diagnostic_key_is_clause_scoped() -> None:
    """P6: same invariant as above, for the ``weight_based_dosing`` key."""

    weight_only = _ann(
        "Prescription",
        "levetiracetam commenced at 60mg/kg/day",
        DrugName="Levetiracetam",
        DrugDose="60",
        DoseUnit="mg",
        Frequency="2",
    )
    unrelated_prefix = _ann(
        "Prescription",
        "patient reports good compliance, levetiracetam commenced at 60mg/kg/day",
        DrugName="Levetiracetam",
        DrugDose="60",
        DoseUnit="mg",
        Frequency="2",
    )

    assert _is_weight_based_dosing(weight_only) is True
    assert _is_weight_based_dosing(unrelated_prefix) is True

    key_a = _prescription_component_key(weight_only, "weight_based_dosing")
    key_b = _prescription_component_key(unrelated_prefix, "weight_based_dosing")
    assert key_a is not None
    assert key_a == key_b

    assert normalize_phrase(weight_only.text) != normalize_phrase(unrelated_prefix.text)


def test_seizure_frequency_headline_key_invariant_to_trailing_text() -> None:
    """SF active-rate key is attribute- and CUI-derived, not free-text-derived.

    Appending trailing narrative to the annotation phrase must not change the
    (seizure-type, state) headline key when the fact carries a CUI.
    """

    clean = _CLEAN_BY_FAMILY["SeizureFrequency"]
    trailing = _ann(
        "SeizureFrequency",
        "focal seizures, to be reviewed at the next appointment",
        NumberOfSeizures="3",
        CUI="C0036572",
    )

    assert clinical_headline_unit_keys("SeizureFrequency", [clean]) == clinical_headline_unit_keys(
        "SeizureFrequency", [trailing]
    )


def test_investigations_headline_key_invariant_to_trailing_text() -> None:
    """Inv modality key is attribute-derived; trailing narrative is out of scope."""

    clean = _CLEAN_BY_FAMILY["Investigations"]
    trailing = _ann(
        "Investigations",
        "EEG and clinic follow up arranged",
        EEG_Performed="Yes",
        EEG_Results="Abnormal",
    )

    assert clinical_headline_unit_keys("Investigations", [clean]) == clinical_headline_unit_keys(
        "Investigations", [trailing]
    )


def test_diagnosis_headline_unit_is_the_annotation_phrase_by_design() -> None:
    """Document Diagnosis's scope boundary: the phrase *is* the fact's clause.

    Unlike Rx/SF/Inv (attribute-keyed), the Diagnosis headline unit is the
    canonicalized concept *phrase itself*. Its correct scope boundary is therefore
    the annotation text, not a sub-clause of it. The out-of-scope channel for
    Diagnosis is the surrounding ``note_text`` (covered by
    ``test_headline_key_is_invariant_to_surrounding_note_text``). This test pins
    the design invariant so a future change that made the Diagnosis key read note
    context — or that silently merged an appended sentence into the concept — is
    caught: appending a second coordinated concept legitimately adds a key (it is
    a new fact, not out-of-clause noise), whereas note context never does.
    """

    single = _CLEAN_BY_FAMILY["Diagnosis"]
    assert clinical_headline_unit_keys("Diagnosis", [single]) == [("Diagnosis", "focal epilepsy")]

    # A coordinated second concept is a genuinely different fact and SHOULD add a
    # key — this is not the seed defect (the split is intra-annotation semantics,
    # not leakage from outside the fact's scope).
    coordinated = _ann(
        "Diagnosis",
        "focal epilepsy and generalised epilepsy",
        DiagCategory="Epilepsy",
        Certainty="5",
        Negation="Affirmed",
    )
    assert set(clinical_headline_unit_keys("Diagnosis", [coordinated])) == {
        ("Diagnosis", "focal epilepsy"),
        ("Diagnosis", "generalised epilepsy"),
    }

    # But the surrounding note never contributes a key.
    assert clinical_headline_unit_keys(
        "Diagnosis", [single], _OUT_OF_SCOPE_SENTENCE
    ) == clinical_headline_unit_keys("Diagnosis", [single], "")


def test_prescription_headline_uses_component_key_directly() -> None:
    """Guard the direct ``_prescription_component_key`` path the headline calls.

    ``clinical_headline_unit_keys`` delegates to ``_prescription_component_keys``;
    this asserts the single-fact key builder is itself clause-scope invariant, so
    the invariant holds at the unit the badge/tooling layer also calls.
    """

    clean = _CLEAN_BY_FAMILY["Prescription"]
    future_tail = _ann(
        "Prescription",
        "lamotrigine 150mg bd then titrate to 200mg bd",
        DrugName="Lamotrigine",
        DrugDose="150",
        DoseUnit="mg",
        Frequency="2",
    )

    assert _prescription_component_key(clean, "clinical_headline") == _prescription_component_key(
        future_tail, "clinical_headline"
    )
    assert _prescription_component_key(future_tail, "clinical_headline") is not None
