"""Tests for the ExECTv2 all-entity projection-gap ledger."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PATIENT_HISTORY,
    PRESCRIPTION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.projection_gap_ledger import (
    GAP_ATTRIBUTE_BUNDLE,
    GAP_CUI_PROJECTION,
    GAP_OVER_EMISSION,
    GAP_PHRASE_COVERAGE,
    MISS_CANDIDATE_SOURCE,
    MISS_PROJECTION,
    build_projection_gap_ledger,
    build_projection_gap_records,
    summarize_records,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def _pred(entity: str, text: str, *, evidence: str = "ev", **attrs: str) -> PredictedMention:
    return PredictedMention(entity=entity, text=text, attributes=dict(attrs), evidence=evidence)


def test_phrase_coverage_split_into_candidate_source_and_projection() -> None:
    # Gold A: concept (CUI) absent from preds -> candidate-source miss.
    # Gold B: a prediction in the letter carries the same CUI at a different phrase
    #   altitude -> phrase_coverage miss but tagged projection (concept recovered).
    gold = ExectLetter(
        "L1",
        "note",
        (
            _ann(PATIENT_HISTORY.name, "anxiety", CUI="C0003467"),
            _ann(PATIENT_HISTORY.name, "febrile-seizures", CUI="C0009952"),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L1",
        mentions=(_pred(PATIENT_HISTORY.name, "recurrent febrile seizure", CUI="C0009952"),),
    )

    records = build_projection_gap_records([gold], [prediction])
    by_phrase = {r.gold_phrase: r for r in records if r.side == "gold"}

    anxiety = by_phrase["anxiety"]
    assert anxiety.gap_family == GAP_PHRASE_COVERAGE
    assert anxiety.miss_kind == MISS_CANDIDATE_SOURCE
    assert anxiety.concept_cui_present is False

    febrile = by_phrase["febrile-seizures"]
    assert febrile.gap_family == GAP_PHRASE_COVERAGE
    assert febrile.miss_kind == MISS_PROJECTION
    assert febrile.concept_cui_present is True

    over = [r for r in records if r.gap_family == GAP_OVER_EMISSION]
    assert len(over) == 1
    assert over[0].predicted_phrase == "recurrent febrile seizure"


def test_attribute_bundle_vs_cui_projection_pairing() -> None:
    # Phrase matches on both; the attribute bundle differs (Certainty) -> attribute
    # bundle family. CUI differs only -> cui_projection family.
    gold = ExectLetter(
        "L2",
        "note",
        (
            _ann(PATIENT_HISTORY.name, "depression", Certainty="4", Negation="Affirmed",
                 CUI="C0011570"),
            _ann(PATIENT_HISTORY.name, "migraine", Certainty="5", Negation="Affirmed",
                 CUI="C0149931"),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L2",
        mentions=(
            _pred(PATIENT_HISTORY.name, "depression", Certainty="5", Negation="Affirmed",
                  CUI="C0011570"),
            _pred(PATIENT_HISTORY.name, "migraine", Certainty="5", Negation="Affirmed",
                  CUI="C0149999"),
        ),
    )

    records = build_projection_gap_records([gold], [prediction])
    families = {r.gold_phrase: r for r in records}

    depression = families["depression"]
    assert depression.gap_family == GAP_ATTRIBUTE_BUNDLE
    assert depression.phrase_match is True
    assert depression.semantic_match is False
    assert depression.miss_kind == MISS_PROJECTION
    assert depression.predicted_attributes is not None

    # CUI-only mismatch: phrase + non-CUI attributes agree, so the key broke at the
    # CUI layer. The gold CUI is genuinely absent from preds, so by Finding 2's
    # concept-recovery proxy the miss_kind is candidate_source (the axes are
    # orthogonal: cui_projection gap, candidate_source miss).
    migraine = families["migraine"]
    assert migraine.gap_family == GAP_CUI_PROJECTION
    assert migraine.phrase_match is True
    assert migraine.semantic_match is True
    assert migraine.miss_kind == MISS_CANDIDATE_SOURCE
    assert migraine.concept_cui_present is False


def test_full_benchmark_match_emits_no_records() -> None:
    gold = ExectLetter(
        "L3",
        "note",
        (_ann(PATIENT_HISTORY.name, "depression", Certainty="5", Negation="Affirmed",
              CUI="C0011570", CUIPhrase="depression"),),
    )
    prediction = PredictedLetter(
        letter_id="L3",
        mentions=(_pred(PATIENT_HISTORY.name, "depression", Certainty="5", Negation="Affirmed",
                        CUI="C0011570", CUIPhrase="depression"),),
    )

    records = build_projection_gap_records([gold], [prediction])
    assert records == []


def test_summary_regime_from_projection_share() -> None:
    # Two projection misses, no candidate-source misses -> representation_bound.
    gold = ExectLetter(
        "L4",
        "note",
        (
            _ann(PATIENT_HISTORY.name, "depression", Certainty="4", CUI="C0011570"),
            _ann(PATIENT_HISTORY.name, "migraine", Certainty="4", CUI="C0149931"),
        ),
    )
    prediction = PredictedLetter(
        letter_id="L4",
        mentions=(
            _pred(PATIENT_HISTORY.name, "depression", Certainty="5", CUI="C0011570"),
            _pred(PATIENT_HISTORY.name, "migraine", Certainty="5", CUI="C0149931"),
        ),
    )

    records = build_projection_gap_records([gold], [prediction])
    summary = summarize_records(records)
    entry = summary["per_entity"][PATIENT_HISTORY.name]

    assert entry["projection_misses"] == 2
    assert entry["candidate_source_misses"] == 0
    assert entry["projection_share"] == 1.0
    assert entry["regime"] == "representation_bound"


def test_build_ledger_on_dev_split_is_consistent_and_has_rx_families() -> None:
    gold_letters = load_letters_for_split("dev")
    predictions = run_all9_on_letters(gold_letters)

    ledger = build_projection_gap_ledger(gold_letters, predictions)

    assert ledger["row_count"] == len(gold_letters)
    assert len(ledger["records"]) > 0

    summary = ledger["summary"]
    totals = summary["totals"]
    # Totals reconcile with the per-entity rollup.
    assert totals["gold_misses"] == sum(
        e["gold_misses"] for e in summary["per_entity"].values()
    )
    assert totals["projection_misses"] + totals["candidate_source_misses"] == totals["gold_misses"]

    # Every gold-side record is one of the three FN families; predicted-side is
    # over-emission only.
    for record in ledger["records"]:
        if record["side"] == "gold":
            assert record["gap_family"] in {
                GAP_PHRASE_COVERAGE,
                GAP_ATTRIBUTE_BUNDLE,
                GAP_CUI_PROJECTION,
            }
        else:
            assert record["gap_family"] == GAP_OVER_EMISSION

    rx = ledger["prescription_component_families"]
    assert "rescue_regimen" in rx
    assert "source_stated_frequency" in rx
    assert "phrase_scope" in rx

    # Regimes are a reproducibility contract for the current deterministic dev
    # snapshot. Diagnosis moved into the representation-bound bucket after the
    # extractor began surfacing more diagnosis CUIs; the 2026-06-17 research note
    # remains the historical baseline, not this regression fixture.
    assert summary["per_entity"][DIAGNOSIS.name]["regime"] == "representation_bound"
    assert summary["per_entity"][PATIENT_HISTORY.name]["regime"] == "recall_bound"
    assert summary["per_entity"][INVESTIGATIONS.name]["regime"] == "recall_bound"
    assert summary["per_entity"][PRESCRIPTION.name]["regime"] == "representation_bound"

    # Total concept-recovered (projection) share for the current dev snapshot.
    assert totals["projection_misses"] == 522
    assert totals["projection_share"] == round(522 / totals["gold_misses"], 4)
