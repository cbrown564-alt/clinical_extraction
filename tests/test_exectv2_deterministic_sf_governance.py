"""Invariant-focused tests for exectv2 deterministic sf governance."""

from __future__ import annotations

from importlib import import_module

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.candidates import (
    AnchorCandidate,
    AttributeExtraction,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
    extract_seizure_frequency,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rule_metadata import (
    DEFAULT_ABLATION,
    ExtractionContext,
)

_sf_rules = import_module(
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.extraction"
)
ANCHOR_RULES = _sf_rules.ANCHOR_RULES
CHANGE_RULES = _sf_rules.CHANGE_RULES
RATE_RULES = _sf_rules.RATE_RULES
SEIZURE_FREE_RULES = _sf_rules.SEIZURE_FREE_RULES
TEMPORAL_RULES = _sf_rules.TEMPORAL_RULES


def _apply(spec, text: str) -> list[AttributeExtraction]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AttributeExtraction)]


def _apply_anchors(spec, text: str) -> list[AnchorCandidate]:
    ctx = ExtractionContext(text=text)
    return [c for c in spec.apply(ctx, DEFAULT_ABLATION) if isinstance(c, AnchorCandidate)]


def _make_letter(letter_id: str, note_text: str) -> ExectLetter:
    return ExectLetter(letter_id=letter_id, note_text=note_text)


_PINNED_DEV_PER_ITEM_F1 = {
    "phrase_only": 0.756,
    "sf_semantic": 0.705,
    "sf_benchmark": 0.705,
}

_F1_BAND = 0.02


def test_lexicon_canonical_phrases_map_to_their_cui() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    assert assign_cui("generalised tonic clonic seizures") == "C0494475"
    assert assign_cui("focal seizures with altered awareness") == "C0270834"
    assert assign_cui("secondary generalised seizures") == "C0270838"
    assert assign_cui("myoclonic jerks") == "C0027066"
    assert assign_cui("seizure free") == "C1299590"
    assert assign_cui("absences") == "C0563606"


def test_lexicon_normalizes_surface_variation() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    # Hyphens, case, and "loss of"/"altered" awareness wording all resolve.
    assert assign_cui("Generalised-Tonic-Clonic-Seizures") == "C0494475"
    assert assign_cui("focal seizures with loss of awareness") == "C0270834"
    assert assign_cui("focal impaired awareness seizures") == "C0270834"
    assert assign_cui("focal dyscognitive seizures") == "C0270834"
    assert assign_cui("focal to bilateral seizures") == "C0877017"
    assert assign_cui("no further seizures") == "C0036572"
    assert assign_cui("absence events") == "C0563606"


def test_lexicon_collisions_resolve_to_dominant_cui() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    # Bare truncation tokens resolve to the dominant gold CUI, not seizure-free /
    # focal-motor.
    assert assign_cui("seizure") == "C0036572"
    assert assign_cui("seizures") == "C0036572"
    assert assign_cui("focal") == "C0877017"


def test_lexicon_unknown_phrase_returns_none() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
        assign_cui,
    )

    assert assign_cui("photosensitive episodes") is None
    assert assign_cui("") is None


def test_pipeline_emits_cui_for_known_seizure_type() -> None:
    letter = _make_letter(
        "T010",
        "Seizure type and frequency: generalised tonic clonic seizures twice weekly.",
    )
    result = extract_seizure_frequency(letter)
    sf = [m for m in result.mentions if m.entity == SEIZURE_FREQUENCY.name]
    assert sf
    assert any(m.attributes.get("CUI") == "C0494475" for m in sf)


def test_no_duplicate_rule_ids() -> None:
    all_rules = ANCHOR_RULES + RATE_RULES + SEIZURE_FREE_RULES + CHANGE_RULES + TEMPORAL_RULES
    ids = [spec.rule_id for spec in all_rules]
    assert len(ids) == len(set(ids)), f"Duplicate rule_ids: {[x for x in ids if ids.count(x) > 1]}"


def test_all_rules_have_examples() -> None:
    all_rules = ANCHOR_RULES + RATE_RULES + SEIZURE_FREE_RULES + CHANGE_RULES + TEMPORAL_RULES
    missing = [spec.rule_id for spec in all_rules if not spec.examples]
    assert not missing, f"Rules without examples: {missing}"


def test_dev_split_baseline_pinned() -> None:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
        to_exect_letter,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.pipeline import (
        run_on_letters,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        PHRASE_ONLY,
        SF_BENCHMARK,
        SF_SEMANTIC,
        score_entity,
    )

    gold = load_letters_for_split("dev")
    preds = run_on_letters(gold)
    pred_exect = [
        to_exect_letter(p, note_text=g.note_text) for p, g in zip(preds, gold, strict=True)
    ]

    configs = {
        "phrase_only": PHRASE_ONLY,
        "sf_semantic": SF_SEMANTIC,
        "sf_benchmark": SF_BENCHMARK,
    }
    for name, cfg in configs.items():
        f1 = score_entity(gold, pred_exect, SEIZURE_FREQUENCY.name, cfg).per_item.f1
        pinned = _PINNED_DEV_PER_ITEM_F1[name]
        assert pinned - _F1_BAND <= f1 <= pinned + _F1_BAND, (
            f"dev {name} per-item F1={f1:.3f} drifted from pinned {pinned:.3f} "
            f"(±{_F1_BAND}). If this is a deliberate improvement, re-pin "
            f"_PINNED_DEV_PER_ITEM_F1 and record it in the error-analysis artifact."
        )
