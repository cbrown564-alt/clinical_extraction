"""Invariant-focused tests for exectv2 scoring headlines."""

from dataclasses import replace

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
    INVESTIGATIONS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    concepts_hierarchically_related,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    HEADLINE_DEDUPLICATED,
    HEADLINE_DISTINCT_ASSERTION,
    PHRASE_AND_FEATURES,
    PHRASE_ONLY,
    benchmark_config_for,
    clinical_headline_unit_keys,
    headline_duplicate_tags,
    score_concept_identity,
    score_entity,
    score_frequency_state,
    score_overall,
    score_prescription_benchmark_projection,
    score_prescription_components,
    source_near_diagnostic,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_frequency_state_counts_unique_projected_states_per_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),
                _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="1", CUI="C0036572"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.clinical_headline.gold_count == 1
    assert score.clinical_headline.f1 == 1.0


def test_prescription_drugname_cui_projection_accepts_format_variants_with_same_cui() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Sodium-Valproate-500mg-bd",
                    DrugName="sodiumvalproate",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0037567",
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
                    "sodium valproate 500 mg twice daily",
                    DrugName="sodium-valproate",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                    CUI="C0037567",
                ),
            ),
        )
    ]

    score = score_prescription_benchmark_projection(gold, pred)

    assert score.drugname_cui_projection.f1 == 1.0


def test_prescription_clinical_headline_counts_rescue_regimen_without_dose() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "buccal midazolam",
                    DrugName="Midazolam",
                    Frequency="As_Required",
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
                    "rescue midazolam as required",
                    DrugName="midazolam",
                    Frequency="As_Required",
                ),
            ),
        )
    ]

    score = score_prescription_components(gold, pred)

    assert score.rescue_regimen.f1 == 1.0
    assert score.clinical_headline.f1 == 1.0
    assert score.complete.gold_count == 0
    assert score.ordinary_complete.gold_count == 0


def test_prescription_frequency_diagnostics_separate_stated_from_defaulted() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "Lamotrigine 100mg bd",
                    DrugName="Lamotrigine",
                    DrugDose="100",
                    DoseUnit="mg",
                    Frequency="2",
                ),
                _ann(
                    "Prescription",
                    "Levetiracetam 500mg",
                    DrugName="Levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="1",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.tp == 1
    assert score.frequency.tp == 2


def test_prescription_frequency_source_ignores_note_only_cadence() -> None:
    # P4 (rx_frequency_source_note_window_2026-07-02): a cadence stated only in the
    # surrounding note -- not in the fact's OWN span -- no longer promotes the fact
    # to source-stated. Own-span decides, so this cadence-less span is
    # guideline-defaulted even though the note reads "twice a day".
    note = (
        "He previously tried topiramate and phenytoin and he is currently taking "
        "levetiracetam 1250mg twice a day."
    )
    letters = [
        ExectLetter(
            "L1",
            note,
            (
                _ann(
                    "Prescription",
                    "levetiracetam-",
                    DrugName="levetiracetam",
                    DrugDose="1250",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.gold_count == 0
    assert score.guideline_defaulted_frequency.tp == 1


def test_prescription_frequency_source_neighbour_cadence_does_not_leak() -> None:
    # P4: the core mis-attribution the fix targets -- a *neighbouring* drug's cadence
    # in the note must not reclassify a cadence-less fact as source-stated. Levetiracetam
    # states "twice a day"; the adjacent phenytoin span carries no cadence of its own.
    note = "He takes levetiracetam 500mg twice a day and phenytoin 300mg."
    letters = [
        ExectLetter(
            "L1",
            note,
            (
                _ann(
                    "Prescription",
                    "levetiracetam 500mg twice a day",
                    DrugName="levetiracetam",
                    DrugDose="500",
                    DoseUnit="mg",
                    Frequency="2",
                ),
                _ann(
                    "Prescription",
                    "phenytoin-",
                    DrugName="phenytoin",
                    DrugDose="300",
                    DoseUnit="mg",
                    Frequency="1",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    # Only the levetiracetam fact (own-span cadence) is source-stated; phenytoin,
    # whose own span has no cadence, is guideline-defaulted despite sitting next to it.
    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.tp == 1


def test_prescription_frequency_source_reads_cadence_from_own_span() -> None:
    # Own-span cadence (including the dotted "b.d." abbreviation) is source-stated.
    letters = [
        ExectLetter(
            "L1",
            "Medication: Lamotrigine 100mg b.d.",
            (
                _ann(
                    "Prescription",
                    "Lamotrigine 100mg b.d.",
                    DrugName="Lamotrigine",
                    DrugDose="100",
                    DoseUnit="mg",
                    Frequency="2",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.source_stated_frequency.tp == 1
    assert score.guideline_defaulted_frequency.gold_count == 0


def test_future_and_weight_based_prescriptions_are_diagnostics_not_headline() -> None:
    letters = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    "Prescription",
                    "increase Lamotrigine to 150mg bd",
                    DrugName="Lamotrigine",
                    DrugDose="150",
                    DoseUnit="mg",
                    Frequency="2",
                ),
                _ann(
                    "Prescription",
                    "levetiracetam 10 mg/kg/day",
                    DrugName="Levetiracetam",
                    DrugDose="10",
                    DoseUnit="mg",
                    Frequency="1",
                ),
            ),
        )
    ]

    score = score_prescription_components(letters, letters)

    assert score.future_medication.tp == 1
    assert score.weight_based_dosing.tp == 1
    assert score.clinical_headline.gold_count == 0
    assert score.ordinary_complete.gold_count == 0


def test_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    score = score_entity(letters, letters, SEIZURE_FREQUENCY.name)
    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert score.per_item.tp == 263
    assert score.per_letter.tp == 142


def test_all_entity_gold_scored_against_itself_is_perfect() -> None:
    letters = load_letters()
    entities = tuple(ENTITY_REGISTRY)
    score = score_overall(letters, letters, entities, benchmark_config_for)

    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert set(score.per_entity) == set(entities)
    assert all(entity_score.per_item.f1 == 1.0 for entity_score in score.per_entity.values())
    assert all(entity_score.per_letter.f1 == 1.0 for entity_score in score.per_entity.values())


def test_score_overall_micro_averages_item_and_entity_presence_cells() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY.name, "absence-seizures", NumberOfSeizures="1"),
                _ann(DIAGNOSIS.name, "epilepsy", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter("L2", "note", (_ann(DIAGNOSIS.name, "single-seizure"),)),
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(DIAGNOSIS.name, "wrong-diagnosis", DiagCategory="Epilepsy"),
            ),
        ),
        ExectLetter(
            "L2",
            "note",
            (
                _ann(DIAGNOSIS.name, "single-seizure"),
                _ann(SEIZURE_FREQUENCY.name, "spurious-seizures", NumberOfSeizures="2"),
            ),
        ),
    ]

    score = score_overall(
        gold,
        pred,
        (SEIZURE_FREQUENCY.name, DIAGNOSIS.name),
        lambda _e: PHRASE_AND_FEATURES,
    )

    assert (score.per_item.tp, score.per_item.fp, score.per_item.fn) == (2, 2, 2)
    assert score.per_item.f1 == 0.5
    assert (score.per_letter.tp, score.per_letter.fp, score.per_letter.fn) == (2, 1, 1)
    assert score.per_letter.f1 == 2 / 3


def test_empty_predictions_score_zero_recall() -> None:
    letters = load_letters()
    empty = [
        ExectLetter(letter_id=letter.letter_id, note_text=letter.note_text) for letter in letters
    ]
    score = score_entity(letters, empty, SEIZURE_FREQUENCY.name)
    assert score.per_item.recall == 0.0
    assert score.per_item.tp == 0
    assert score.per_item.fn == 263
    assert score.per_letter.fn == 142


def test_per_item_and_per_letter_diverge_on_partial_letter() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),
                _ann(SEIZURE_FREQUENCY.name, "absence-seizures", NumberOfSeizures="1"),
            ),
        )
    ]
    # one of two mentions correct: per-item recall 0.5, but the letter counts as
    # a per-letter true positive (at least one correct mention).
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),),
        )
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY.name)
    assert (score.per_item.tp, score.per_item.fn) == (1, 1)
    assert score.per_item.recall == 0.5
    assert score.per_letter.f1 == 1.0


def test_spurious_mention_in_empty_gold_letter_is_per_letter_false_positive() -> None:
    gold = [ExectLetter("L1", "note", ())]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "two-seizures", NumberOfSeizures="2"),),
        )
    ]
    score = score_entity(gold, pred, SEIZURE_FREQUENCY.name)
    assert (score.per_letter.tp, score.per_letter.fp, score.per_letter.fn) == (0, 1, 0)
    assert score.per_item.fp == 1


def test_wrong_attribute_breaks_full_feature_match_but_not_phrase_match() -> None:
    letters = load_letters()
    target = next(letter for letter in letters if letter.entities(SEIZURE_FREQUENCY.name))
    mentions = list(target.annotations)
    sf_index = next(i for i, a in enumerate(mentions) if a.entity == SEIZURE_FREQUENCY.name)
    mentions[sf_index] = replace(
        mentions[sf_index],
        attributes={**mentions[sf_index].attributes, "NumberOfSeizures": "999"},
    )
    perturbed = [
        ExectLetter(target.letter_id, target.note_text, tuple(mentions))
        if letter.letter_id == target.letter_id
        else letter
        for letter in letters
    ]

    strict = score_entity(letters, perturbed, SEIZURE_FREQUENCY.name, PHRASE_AND_FEATURES)
    lenient = score_entity(letters, perturbed, SEIZURE_FREQUENCY.name, PHRASE_ONLY)
    assert strict.per_item.fp == 1
    assert strict.per_item.fn == 1
    assert lenient.per_item.f1 == 1.0


def test_source_near_diagnostic_counts_same_entity_substring_overlap() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann("Prescription", "lamotrigine", DrugName="lamotrigine", DoseUnit="mg"),
                _ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="2"),
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
                    "lamotrigine 200mg bd",
                    DrugName="Lamotrigine",
                    DoseUnit="MG",
                ),
                _ann(SEIZURE_FREQUENCY.name, "2 focal seizures per month", NumberOfSeizures="3"),
            ),
        )
    ]

    diagnostic = source_near_diagnostic(
        gold,
        pred,
        ("Prescription", SEIZURE_FREQUENCY.name),
        benchmark_config_for,
    )

    assert diagnostic.per_entity["Prescription"].overlap.tp == 1
    assert diagnostic.per_entity["Prescription"].attribute_agreement_tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY.name].overlap.tp == 1
    assert diagnostic.per_entity[SEIZURE_FREQUENCY.name].attribute_agreement_tp == 0
    assert diagnostic.overall.attribute_agreement_rate == 0.5


def test_headline_duplicate_tags_ea0044_pattern():
    """SF same-offset/attribute-only twin de-duplicates; distinct-offset EEG
    duplicate is counted per occurrence (the EA0044 pattern, D20)."""
    annotations = [
        ExectAnnotation(
            entity=SEIZURE_FREQUENCY.name,
            text="seizures",
            attributes={"NumberOfSeizures": "0", "PointInTime": "LastClinic"},
        ),
        ExectAnnotation(
            entity=SEIZURE_FREQUENCY.name,
            text="seizures",
            attributes={"NumberOfSeizures": "0", "PointInTime": "DrugChange"},
        ),
        ExectAnnotation(
            entity=INVESTIGATIONS.name,
            text="MRI",
            attributes={"MRI_Performed": "Yes", "MRI_Results": "Normal"},
        ),
        ExectAnnotation(
            entity=INVESTIGATIONS.name,
            text="EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
        ),
        ExectAnnotation(
            entity=INVESTIGATIONS.name,
            text="EEG",
            attributes={"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
        ),
    ]

    tags = headline_duplicate_tags(annotations)
    # Only the second SF mention (a Redundant-Convention Duplicate) is collapsed.
    assert tags == [
        None,
        HEADLINE_DEDUPLICATED,
        None,
        HEADLINE_DISTINCT_ASSERTION,
        HEADLINE_DISTINCT_ASSERTION,
    ]

    sf = [a for a in annotations if a.entity == SEIZURE_FREQUENCY.name]
    inv = [a for a in annotations if a.entity == INVESTIGATIONS.name]
    # SF collapses 2 raw mentions to 1 headline unit; Investigations preserves all 3.
    assert len(clinical_headline_unit_keys(SEIZURE_FREQUENCY.name, sf)) == 1
    assert len(clinical_headline_unit_keys(INVESTIGATIONS.name, inv)) == 3


def test_headline_duplicate_tags_distinct_sf_states_not_deduplicated():
    """Two SF mentions of one seizure type in different states (active + seizure
    free) are distinct headline units, not duplicates — neither is tagged."""
    annotations = [
        ExectAnnotation(
            entity=SEIZURE_FREQUENCY.name,
            text="seizures",
            attributes={"NumberOfSeizures": "5", "TimePeriod": "Month"},
        ),
        ExectAnnotation(
            entity=SEIZURE_FREQUENCY.name,
            text="seizures",
            attributes={"NumberOfSeizures": "0", "PointInTime": "LastClinic"},
        ),
    ]
    assert headline_duplicate_tags(annotations) == [None, None]
    assert len(clinical_headline_unit_keys(SEIZURE_FREQUENCY.name, annotations)) == 2


def test_concepts_hierarchically_related_only_true_ancestor_descendant() -> None:
    # Ancestor/descendant (either direction) and identity are related...
    assert concepts_hierarchically_related("epilepsy", "focal epilepsy")
    assert concepts_hierarchically_related("focal epilepsy", "epilepsy")
    assert concepts_hierarchically_related("epilepsy", "temporal lobe epilepsy")  # 2 hops
    assert concepts_hierarchically_related("epilepsy", "epilepsy")
    # ...siblings and unrelated concepts are NOT (the kill-criterion guarantee).
    assert not concepts_hierarchically_related("focal epilepsy", "generalised epilepsy")
    assert not concepts_hierarchically_related(
        "temporal lobe epilepsy", "juvenile myoclonic epilepsy"
    )


def test_diagnosis_headline_credits_gold_parent_when_pred_emits_descendant() -> None:
    """Hypothesis example (D1): gold=[epilepsy], pred=[epilepsy, focal epilepsy].
    Per-side collapse leaves gold={epilepsy}, pred={focal epilepsy}; the
    hierarchy-aware match credits the verbatim-correct diagnosis instead of
    scoring it as a paired FN+FP."""
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("focal epilepsy")))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.f1 == 1.0
    assert score.precision_tp == 1 and score.recall_tp == 1
    assert score.pred_count == 1 and score.gold_count == 1


def test_diagnosis_headline_credits_gold_descendant_when_pred_emits_parent() -> None:
    """Symmetric gold-side collapse artifact (the realized dev140 case, e.g.
    EA0007): gold=[epilepsy, focal epilepsy] collapses to {focal epilepsy};
    pred=[epilepsy] matched the parent verbatim yet scored 0. The match recovers
    it because epilepsy is an ancestor of focal epilepsy."""
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("focal epilepsy")))]
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"),))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.f1 == 1.0
    assert score.precision_tp == 1 and score.recall_tp == 1


def test_diagnosis_headline_does_not_credit_unrelated_sibling_concept() -> None:
    """Kill criterion: an unrelated (sibling) prediction must never be credited
    against a gold concept. focal epilepsy and generalised epilepsy share only
    the ancestor 'epilepsy'; neither is a descendant of the other."""
    gold = [ExectLetter("L1", "note", (_dx("generalised epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("focal epilepsy"),))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.precision_tp == 0 and score.recall_tp == 0
    assert score.f1 == 0.0


def test_diagnosis_headline_exact_match_unchanged_by_hierarchy_logic() -> None:
    """Regression guard: a plain exact concept match is unaffected."""
    gold = [ExectLetter("L1", "note", (_dx("focal epilepsy"),))]
    pred = [ExectLetter("L1", "note", (_dx("focal epilepsy"),))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.f1 == 1.0
    assert score.precision_tp == 1 and score.recall_tp == 1


def test_diagnosis_headline_hierarchy_match_is_cardinality_bounded() -> None:
    """One extra unrelated gold concept stays a genuine miss even when a related
    pair is reconciled — the greedy match cannot over-credit."""
    gold = [ExectLetter("L1", "note", (_dx("epilepsy"), _dx("juvenile myoclonic epilepsy")))]
    # gold collapses to {juvenile myoclonic epilepsy}; pred parent 'epilepsy' is a
    # 2-hop ancestor of it, so it matches — but there is only one gold unit.
    pred = [ExectLetter("L1", "note", (_dx("epilepsy"),))]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name).concept_only

    assert score.gold_count == 1  # collapsed to the most specific
    assert score.pred_count == 1
    assert score.precision_tp == 1 and score.recall_tp == 1
    assert score.f1 == 1.0
