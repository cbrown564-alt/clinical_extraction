"""Dev-split SeizureFrequency scorer for the deterministic ExECTv2 extractor.

Loads the 140-letter "dev" split of the ExECTv2 corpus (see
data/ExECTv2 (2025)/splits/exectv2_split_v1.json), runs the deterministic SF
pipeline, and reports per-item and per-letter PRF1 scores under three match
configurations:

  phrase_only     — entity + phrase only (ignores all attributes)
  no_ref_attrs    — entity + phrase + semantic attributes
                    (ignores CUI, CUIPhrase, Certainty — requires ontology)
  full_features   — entity + phrase + all attributes except CUIPhrase

Usage::

    uv run python -m clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.run_deterministic_sf

Phase-2 milestone: per-item and per-letter F1 on dev, with a row-level error
list.  The three configs bound the range: phrase_only shows phrase recall,
no_ref_attrs shows semantic-attribute accuracy, full_features shows the strict
score including Certainty and Negation.
"""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
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
    MatchConfig,
    score_entity,
)


def _prf(score_obj: object) -> str:  # type: ignore[return]
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import EntityScore

    assert isinstance(score_obj, EntityScore)
    pi = score_obj.per_item
    pl = score_obj.per_letter
    return (
        f"  per-item:   P={pi.precision:.3f}  R={pi.recall:.3f}  F1={pi.f1:.3f}"
        f"  (TP={pi.tp} FP={pi.fp} FN={pi.fn})\n"
        f"  per-letter: P={pl.precision:.3f}  R={pl.recall:.3f}  F1={pl.f1:.3f}"
        f"  (TP={pl.tp} FP={pl.fp} FN={pl.fn})"
    )


def _row_errors(
    gold_letters: list,
    pred_letters: list,
    config: MatchConfig,
    limit: int = 30,
) -> list[str]:
    """Return up to ``limit`` row-level error descriptions (FP/FN mentions)."""
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        _keys,
        _letters_by_id,
    )

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    errors: list[str] = []

    for letter_id in sorted(gold_by_id.keys() | pred_by_id.keys()):
        gold_anns = (
            gold_by_id[letter_id].entities(SEIZURE_FREQUENCY.name)
            if letter_id in gold_by_id
            else ()
        )
        pred_anns = (
            pred_by_id[letter_id].entities(SEIZURE_FREQUENCY.name)
            if letter_id in pred_by_id
            else ()
        )

        gold_keys = _keys(gold_anns, config)
        pred_keys = list(_keys(pred_anns, config))

        # Multiset match: consume pred_keys greedily
        remaining_pred = list(pred_keys)
        for gk in gold_keys:
            if gk in remaining_pred:
                remaining_pred.remove(gk)
            else:
                errors.append(f"FN [{letter_id}] gold: {gk}")
                if len(errors) >= limit:
                    return errors

        for pk in remaining_pred:
            errors.append(f"FP [{letter_id}] pred: {pk}")
            if len(errors) >= limit:
                return errors

    return errors


def main() -> None:
    print("Loading dev-split letters ...", flush=True)
    gold_letters = load_letters_for_split("dev")
    print(f"  {len(gold_letters)} dev letters loaded.")

    print("\nRunning deterministic SF pipeline ...", flush=True)
    predicted_pred_letters = run_on_letters(gold_letters)

    # Convert PredictedLetter → ExectLetter for scoring
    pred_exect = [
        to_exect_letter(p, note_text=g.note_text)
        for p, g in zip(predicted_pred_letters, gold_letters, strict=False)
    ]

    total_pred = sum(len(p.mentions) for p in predicted_pred_letters)
    total_gold = sum(len(g.entities(SEIZURE_FREQUENCY.name)) for g in gold_letters)
    print(f"  Gold SF mentions:      {total_gold}")
    print(f"  Predicted SF mentions: {total_pred}")

    print("\n── phrase_only ─────────────────────────────────────────────────────")
    s_phrase = score_entity(gold_letters, pred_exect, SEIZURE_FREQUENCY.name, PHRASE_ONLY)
    print(_prf(s_phrase))

    print("\n── sf_semantic (guideline-aligned; ignores CUI/CUIPhrase/Certainty/Negation) ──")
    s_semantic = score_entity(gold_letters, pred_exect, SEIZURE_FREQUENCY.name, SF_SEMANTIC)
    print(_prf(s_semantic))

    print("\n── sf_benchmark (keeps CUI; needs phrase→CUI lexicon) ──────────────")
    s_bench = score_entity(gold_letters, pred_exect, SEIZURE_FREQUENCY.name, SF_BENCHMARK)
    print(_prf(s_bench))

    print("\n── error sample (phrase_only, first 30 FP/FN) ──────────────────────")
    errs = _row_errors(gold_letters, pred_exect, PHRASE_ONLY)
    for e in errs:
        print(" ", e)
    if not errs:
        print("  (none)")


if __name__ == "__main__":
    main()
