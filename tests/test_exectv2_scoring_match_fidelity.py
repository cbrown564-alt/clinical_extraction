"""Invariant-focused tests for exectv2 scoring match fidelity."""


from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_AND_FEATURES,
    PHRASE_ONLY,
    canonicalize_medication_name,
    match_key,
    resolve_point_range,
    score_concept_identity,
    score_frequency_state,
    score_prescription_benchmark_projection,
    score_prescription_components,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_normalize_phrase_strips_hyphens_quotes_and_case() -> None:
    assert (
        normalize_phrase("generalised-tonic-clonic-seizures") == "generalised tonic clonic seizures"
    )
    assert normalize_phrase("“absence-like”-episodes") == "absence like episodes"


def test_match_key_ignores_cuiphrase_by_default() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="seizures")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2", CUIPhrase="different")
    assert match_key(a) == match_key(b)


def test_phrase_only_ignores_attributes() -> None:
    a = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2")
    b = _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="9")
    assert match_key(a, PHRASE_ONLY) == match_key(b, PHRASE_ONLY)
    assert match_key(a, PHRASE_AND_FEATURES) != match_key(b, PHRASE_AND_FEATURES)


def test_match_key_canonicalizes_format_only_attribute_values() -> None:
    a = _ann("Prescription", "levetiracetam", DrugName="Levetiracetam", DoseUnit="MG")
    b = _ann("Prescription", "levetiracetam", DrugName="levetiracetam", DoseUnit="mg")

    assert match_key(a, PHRASE_AND_FEATURES) == match_key(b, PHRASE_AND_FEATURES)


def test_canonicalize_medication_name_accepts_brand_synonym_and_typo_variants() -> None:
    assert canonicalize_medication_name("Keppra") == "levetiracetam"
    assert canonicalize_medication_name("Lamictal") == "lamotrigine"
    assert canonicalize_medication_name("Eplim") == "sodium-valproate"
    assert canonicalize_medication_name("Tegretaol") == "carbamazepine"
    assert canonicalize_medication_name("Zonismaide") == "zonisamide"


def test_canonicalize_medication_name_unifies_valproate_and_brand_gaps() -> None:
    # rx_drug_lexicon_valproate_brand_gaps_2026-07-02: bare valproate and its
    # chemical variants unify with sodium valproate; brand->generic omissions added.
    assert canonicalize_medication_name("valproate") == "sodium-valproate"
    assert canonicalize_medication_name("Valproic acid") == "sodium-valproate"
    assert canonicalize_medication_name("valproate semisodium") == "sodium-valproate"
    assert canonicalize_medication_name("Lyrica") == "pregabalin"
    assert canonicalize_medication_name("Topamax") == "topiramate"
    assert canonicalize_medication_name("Vimpat") == "lacosamide"
    assert canonicalize_medication_name("Briviact") == "brivaracetam"
    assert canonicalize_medication_name("Frisium") == "clobazam"
    assert canonicalize_medication_name("Trileptal") == "oxcarbazepine"
    assert canonicalize_medication_name("Neurontin") == "gabapentin"
    assert canonicalize_medication_name("Buccolam") == "midazolam"
    assert canonicalize_medication_name("eslicarbazepine acetate") == "eslicarbazepine"


def test_score_prescription_components_uses_clinical_regimen_keys() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="MG",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(gold, pred)

    assert score.name.f1 == 1.0
    assert score.dose.f1 == 1.0
    assert score.frequency.f1 == 1.0
    assert score.complete.f1 == 1.0
    assert score.ordinary_complete.f1 == 1.0
    assert score.clinical_headline.f1 == 1.0


def test_prescription_benchmark_projection_separates_clinical_identity_from_cui() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Keppra-500mg-bd",
                    DrugName="Keppra",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0876060",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "levetiracetam 500 mg twice daily",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0377265",
                ),
            ),
        )
    ]

    score = score_prescription_benchmark_projection(gold, pred)

    assert score.clinical_medication_identity.f1 == 1.0
    assert score.drugname_cui_projection.f1 == 0.0
    assert score.phrase_scope.f1 == 0.0
    assert score.benchmark_with_cui.f1 == 0.0


def test_concept_negation_penalizes_negated_match_that_concept_only_forgives() -> None:
    # concept_only ignores assertion entirely, so an affirmed prediction "matches"
    # a negated gold. concept_negation must catch this; certainty is still ignored.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "epilepsy", Certainty="5", Negation="Negated"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "epilepsy", Certainty="3", Negation="Affirmed"),),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_only.f1 == 1.0  # forgives the negation flip
    assert score.concept_negation.f1 == 0.0  # catches it
    assert score.concept_negation.gold_count == 1
    assert score.concept_negation.recall == 0.0


def test_concept_negation_ignores_certainty_when_negation_agrees() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "epilepsy", Certainty="4", Negation="Affirmed"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(DIAGNOSIS.name, "epilepsy", Certainty="5", Negation="Affirmed"),),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    # Certainty differs but is deterministically projectable, so concept_negation
    # treats this as a match; only concept_assertion penalizes the certainty gap.
    assert score.concept_negation.f1 == 1.0
    assert score.concept_assertion.f1 == 0.0


def test_active_rate_fidelity_penalizes_wrong_rate_headline_forgives() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="6",
                    NumberOfTimePeriods="1",
                    TimePeriod="Week",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="6",
                    NumberOfTimePeriods="3",  # 6 per 3 weeks, not 6 per week
                    TimePeriod="Week",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.clinical_headline.f1 == 1.0  # both collapse to active-rate
    assert score.active_rate_fidelity.f1 == 0.0  # rate magnitude disagrees


def test_active_rate_fidelity_ignores_dates_when_rate_agrees() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="2",
                    NumberOfTimePeriods="1",
                    TimePeriod="Month",
                    YearDate="2017",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="2",
                    NumberOfTimePeriods="1",
                    TimePeriod="Month",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    # Rate matches; the missing date is timing, not magnitude, so fidelity is clean.
    assert score.active_rate_fidelity.f1 == 1.0


def test_resolve_point_range_collapses_degenerate_range_to_a_point() -> None:
    triple = ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
    assert resolve_point_range({"NumberOfSeizures": "2"}, triple) == ("point", "2")
    assert resolve_point_range(
        {"LowerNumberOfSeizures": "2", "UpperNumberOfSeizures": "2"}, triple
    ) == ("point", "2")
    # Asymmetric partial range consistent with the bare value (seen verbatim in an
    # EA0079 draft mention: NumberOfSeizures=1 alongside a redundant Lower=1).
    assert resolve_point_range({"NumberOfSeizures": "1", "LowerNumberOfSeizures": "1"}, triple) == (
        "point",
        "1",
    )
    assert resolve_point_range({}, triple) is None


def test_resolve_point_range_keeps_a_genuine_range_distinct_from_a_point() -> None:
    triple = ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
    assert resolve_point_range(
        {"LowerNumberOfSeizures": "1", "UpperNumberOfSeizures": "3"}, triple
    ) == ("range", "1", "3")
    assert resolve_point_range({"NumberOfSeizures": "2"}, triple) != resolve_point_range(
        {"LowerNumberOfSeizures": "1", "UpperNumberOfSeizures": "3"}, triple
    )


def test_resolve_point_range_flags_a_bare_value_that_disagrees_with_the_bounds() -> None:
    triple = ("NumberOfSeizures", "LowerNumberOfSeizures", "UpperNumberOfSeizures")
    conflict = resolve_point_range(
        {"NumberOfSeizures": "5", "LowerNumberOfSeizures": "2", "UpperNumberOfSeizures": "2"},
        triple,
    )
    assert conflict is not None and conflict[0] == "conflict"


def test_active_rate_fidelity_treats_bare_count_and_degenerate_range_as_equal() -> None:
    # EA0005 shape: gold states a bare count; pred expresses the identical value
    # as a lower==upper range. Same clinical fact, previously scored FP+FN.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="2"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    LowerNumberOfSeizures="2",
                    UpperNumberOfSeizures="2",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.active_rate_fidelity.f1 == 1.0
    assert match_key(gold[0].annotations[0]) == match_key(pred[0].annotations[0])


def test_active_rate_fidelity_treats_bare_cadence_and_degenerate_range_as_equal() -> None:
    # EA0008 shape: gold states a bare count + bare cadence; pred expresses both
    # as lower==upper ranges. Same clinical fact, previously scored FP+FN.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    NumberOfSeizures="1",
                    NumberOfTimePeriods="3",
                    TimePeriod="Week",
                ),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    LowerNumberOfSeizures="1",
                    UpperNumberOfSeizures="1",
                    LowerNumberOfTimePeriods="3",
                    UpperNumberOfTimePeriods="3",
                    TimePeriod="Week",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.active_rate_fidelity.f1 == 1.0


def test_active_rate_fidelity_still_penalizes_a_genuine_range_disagreement() -> None:
    # Regression guard: a real range (1-3) is a strictly looser claim than a
    # definite count (2) and must not be forgiven by the point/range collapse.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="2"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    SEIZURE_FREQUENCY.name,
                    "seizures",
                    LowerNumberOfSeizures="1",
                    UpperNumberOfSeizures="3",
                ),
            ),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.active_rate_fidelity.f1 == 0.0
