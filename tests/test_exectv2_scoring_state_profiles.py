"""Invariant-focused tests for exectv2 scoring state profiles."""


from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ONSET,
    PATIENT_HISTORY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_direction_deconf,
    frequency_state_directional,
    frequency_state_faithful,
    frequency_state_magnitude,
    match_key,
    score_concept_identity,
    score_frequency_state,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _dx(text: str) -> ExectAnnotation:
    return _ann(DIAGNOSIS.name, text, DiagCategory="Epilepsy", Certainty="5", Negation="Affirmed")


def test_match_key_collapses_onset_and_patient_history_age_range() -> None:
    for entity in (ONSET, PATIENT_HISTORY):
        bare = _ann(entity.name, "onset", Age="8")
        ranged = _ann(entity.name, "onset", AgeLower="8", AgeUpper="8")
        assert match_key(bare) == match_key(ranged)

        genuine_range = _ann(entity.name, "onset", AgeLower="6", AgeUpper="10")
        assert match_key(bare) != match_key(genuine_range)


def test_frequency_state_faithful_distinguishes_change_from_unknown() -> None:
    assert frequency_state_faithful({"NumberOfSeizures": "0"}) == "seizure-free"
    assert frequency_state_faithful({"NumberOfSeizures": "3"}) == "active-rate"
    assert frequency_state_faithful({"FrequencyChange": "Decreased"}) == "changed"
    assert frequency_state_faithful({}) == "unknown"
    # A concrete count is more specific than a qualitative change descriptor.
    assert (
        frequency_state_faithful({"NumberOfSeizures": "0", "FrequencyChange": "Decreased"})
        == "seizure-free"
    )


def test_state_profile_credits_correct_state_despite_different_seizure_type_cui() -> None:
    # Same clinical reality (seizure-free), different — both valid — seizure-type CUI
    # granularity: generic 'seizure' vs a specific focal subtype.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="0", CUI="C0036572"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "focal seizures", NumberOfSeizures="0", CUI="C0270834"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    # The strict key conditions on the seizure-type CUI -> different bucket -> no credit.
    assert score.clinical_headline.f1 == 0.0
    # The clinical-recovery profile keys only the (change-aware) state -> full credit.
    assert score.state_profile.f1 == 1.0


def test_state_profile_stays_state_sensitive_and_collapses_per_type_multiplicity() -> None:
    # Gold tags the SAME type twice (a numeric rate AND a separate qualitative change);
    # the profile keeps both as distinct states, so a model emitting only the rate is
    # still penalized for missing the change — faithful, not blind.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(SEIZURE_FREQUENCY.name, "gtc", NumberOfSeizures="2", CUI="C0494475"),
                _ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Frequent", CUI="C0494475"),
            ),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", NumberOfSeizures="1", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    # Gold presence {active-rate, changed}; pred {active-rate}: the change is a real miss.
    assert score.state_profile.precision == 1.0
    assert score.state_profile.recall == 0.5


def test_frequency_state_directional_distinguishes_change_direction() -> None:
    # Concrete counts behave exactly like frequency_state_faithful.
    assert frequency_state_directional({"NumberOfSeizures": "0"}) == "seizure-free"
    assert frequency_state_directional({"NumberOfSeizures": "3"}) == "active-rate"
    assert frequency_state_directional({}) == "unknown"
    # A concrete count is still more specific than a qualitative change descriptor.
    assert (
        frequency_state_directional({"NumberOfSeizures": "0", "FrequencyChange": "Decreased"})
        == "seizure-free"
    )
    # Unlike frequency_state_faithful, each FrequencyChange value is its own state
    # (SF-2, 2026-07-02) instead of collapsing to a single "changed" bucket.
    assert frequency_state_directional({"FrequencyChange": "Increased"}) == "increased"
    assert frequency_state_directional({"FrequencyChange": "Decreased"}) == "decreased"
    assert frequency_state_directional({"FrequencyChange": "Frequent"}) == "frequent"
    assert frequency_state_directional({"FrequencyChange": "Infrequent"}) == "infrequent"
    assert frequency_state_directional({"FrequencyChange": "Same"}) == "same"


def test_state_profile_directional_penalizes_wrong_direction_that_state_profile_forgives() -> None:
    # Gold reports a worsening (Increased); the model reports an improvement
    # (Decreased). The direction-blind state_profile scores this a match (both
    # collapse to "changed"); the direction-sensitive companion must not.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Increased", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Decreased", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.state_profile.f1 == 1.0
    assert score.state_profile_directional.f1 == 0.0


def test_state_profile_directional_matches_state_profile_when_direction_agrees() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Frequent", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Frequent", CUI="C0270834"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.state_profile.f1 == 1.0
    assert score.state_profile_directional.f1 == 1.0


def test_frequency_state_direction_deconf_projects_magnitude_labels_to_same() -> None:
    # Count-bearing states pass through unchanged on the direction axis, exactly
    # like frequency_state_directional.
    assert frequency_state_direction_deconf({"NumberOfSeizures": "0"}) == "seizure-free"
    assert frequency_state_direction_deconf({"NumberOfSeizures": "3"}) == "active-rate"
    assert frequency_state_direction_deconf({}) == "unknown"
    # A concrete count still takes precedence over a qualitative descriptor.
    assert (
        frequency_state_direction_deconf({"NumberOfSeizures": "0", "FrequencyChange": "Decreased"})
        == "seizure-free"
    )
    # Change-direction labels carry their own direction.
    assert frequency_state_direction_deconf({"FrequencyChange": "Increased"}) == "increased"
    assert frequency_state_direction_deconf({"FrequencyChange": "Decreased"}) == "decreased"
    assert frequency_state_direction_deconf({"FrequencyChange": "Same"}) == "same"
    # The deconflation: magnitude labels carry NO direction signal, so they
    # project to the direction-neutral `same` bucket, not their own value.
    assert frequency_state_direction_deconf({"FrequencyChange": "Frequent"}) == "same"
    assert frequency_state_direction_deconf({"FrequencyChange": "Infrequent"}) == "same"


def test_frequency_state_magnitude_isolates_the_magnitude_axis() -> None:
    # Count-bearing states and the absent case project to magnitude `none`.
    assert frequency_state_magnitude({"NumberOfSeizures": "0"}) == "none"
    assert frequency_state_magnitude({"NumberOfSeizures": "3"}) == "none"
    assert frequency_state_magnitude({}) == "none"
    # Change-direction labels carry no magnitude.
    assert frequency_state_magnitude({"FrequencyChange": "Increased"}) == "none"
    assert frequency_state_magnitude({"FrequencyChange": "Decreased"}) == "none"
    assert frequency_state_magnitude({"FrequencyChange": "Same"}) == "none"
    # The magnitude labels are the only values that populate the magnitude axis.
    assert frequency_state_magnitude({"FrequencyChange": "Frequent"}) == "frequent"
    assert frequency_state_magnitude({"FrequencyChange": "Infrequent"}) == "infrequent"


def test_direction_deconf_still_scores_a_direction_disagreement_as_a_miss() -> None:
    # The motivating case for the probe. Gold is a magnitude statement
    # (Infrequent); the model answers the plain-English "direction" question
    # (Decreased). The conflated state_profile_directional scores this a total
    # miss (infrequent != decreased). The deconflated direction axis scores it a
    # match: gold projects to direction `same` (magnitude carries no direction),
    # and Decreased is... still `decreased`. So the *direction* miss the
    # conflated metric registers is spurious for this pair.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Infrequent", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Decreased", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    # Conflated metric: a hard miss (different FrequencyChange values).
    assert score.state_profile_directional.f1 == 0.0
    # Deconflated direction axis: gold is `same` (magnitude), pred is `decreased`
    # -> still a miss. (The model claimed a direction the gold did not; that is a
    # real direction disagreement, NOT forgiven. What WOULD be forgiven is the
    # reverse: gold Decreased, model Infrequent -- the model making no direction
    # claim where gold did. See the next test.)
    assert score.state_profile_direction_deconf.f1 == 0.0


def test_direction_deconf_penalizes_direction_drop_where_conflated_saw_a_value_swap() -> None:
    # The reconciliation case. Gold asserts a direction (Decreased); the model,
    # reading the same sentence as a magnitude, emits Infrequent. Under the
    # conflated metric this is a miss (decreased != infrequent). Under the
    # deconflated *direction* axis the model made no direction claim (magnitude
    # -> `same`), so the direction miss is genuine -- BUT the disagreement is now
    # attributable to the vocab axis rather than counted as a flat direction
    # error. The magnitude axis records the model's Infrequent as correct-on-
    # magnitude only if gold also carried magnitude, which it did not here.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Decreased", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Infrequent", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    # Conflated metric: miss.
    assert score.state_profile_directional.f1 == 0.0
    # Direction axis: gold `decreased`, pred `same` -> miss (model dropped the
    # direction). This is the "selector abandons magnitude labels" signature
    # from the integration ledger, measured cleanly.
    assert score.state_profile_direction_deconf.f1 == 0.0
    # Magnitude axis: gold `none`, pred `infrequent` -> pred over-emits a
    # magnitude gold did not assert -> precision-side miss (fp). f1 = 0.
    assert score.state_profile_magnitude.f1 == 0.0


def test_direction_deconf_matches_when_both_sides_make_the_same_magnitude_claim() -> None:
    # Two magnitude labels agree -> direction axis matches (both `same`),
    # magnitude axis matches (both the same magnitude value). The conflated
    # metric also matches here; the deconflated metrics decompose the match.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Frequent", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Frequent", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.state_profile_directional.f1 == 1.0
    assert score.state_profile_direction_deconf.f1 == 1.0
    assert score.state_profile_magnitude.f1 == 1.0


def test_direction_deconf_leaves_state_profile_unchanged() -> None:
    # Guardrail: adding the projected metrics must not perturb the existing
    # direction- and magnitude-blind state_profile, which keys only on the
    # change-aware 4-way state. A direction disagreement both metrics see as a
    # change must still score as a state_profile match.
    gold = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Increased", CUI="C0494475"),),
        )
    ]
    pred = [
        ExectLetter(
            "L1",
            "note",
            (_ann(SEIZURE_FREQUENCY.name, "gtc", FrequencyChange="Decreased", CUI="C0494475"),),
        )
    ]

    score = score_frequency_state(gold, pred)

    assert score.state_profile.f1 == 1.0
    assert score.state_profile_direction_deconf.f1 == 0.0


def test_concept_identity_recall_is_entity_agnostic_precision_home_tagged() -> None:
    gold = [
        ExectLetter(
            "L1",
            "note",
            (
                _ann(
                    DIAGNOSIS.name,
                    "focal seizures",
                    DiagCategory="MultipleSeizures",
                    Certainty="5",
                    Negation="Affirmed",
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
                    "PatientHistory",
                    "focal seizures",
                    Certainty="5",
                    Negation="Affirmed",
                ),
            ),
        )
    ]

    score = score_concept_identity(gold, pred, DIAGNOSIS.name)

    assert score.concept_assertion.recall == 1.0
    assert score.concept_assertion.precision == 0.0
    assert score.concept_assertion.pred_count == 0
    assert score.concept_assertion.gold_count == 1
