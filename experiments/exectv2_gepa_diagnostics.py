"""ExECTv2 GEPA under-performance diagnostics (committed from the investigation).

Companion to ``docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md``.

Currently implements the **H4 / D1** probe: does a *perfect model-style*
SeizureFrequency answer score ~1.0 on the de-dup ``clinical_headline`` surface,
or does the clinical_facts -> mention adapter + render-safety gate + CUI
projection silently cap it? "Model-style" means facts shaped exactly as the
dedup LLM emits them (``seizure_type`` + coarse ``state``, NO raw ``attributes``
dict), routed through the *production* path the GEPA metric scores:

    gold SF -> model-style fact -> clinical_facts_to_mentions
            -> to_predicted_letter_from_mentions (evidence gate + render gate
               + CUI projection) -> to_exect_letter -> score_frequency_state

Run:
    uv run python experiments/exectv2_gepa_diagnostics.py
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.facts import (
    _fact_state_from_seizure_attrs,
    clinical_facts_from_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_generation_selection.projection import (
    to_predicted_letter_from_dedup_facts,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    frequency_state_keys,
    score_frequency_state,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
)


def _valid_evidence(note_text: str, annotation: ExectAnnotation) -> str:
    """A guaranteed-valid evidence substring so the evidence gate is not the confound.

    Tries the gold span (and a de-hyphenated form) first so evidence stays
    semantically near the mention; falls back to a leading slice of the note,
    which is fine here because SF scoring keys on text+state, never on evidence.
    """

    for candidate in (annotation.text, annotation.text.replace("-", " "), annotation.raw_text):
        if candidate and candidate in note_text:
            return candidate
    return note_text[:40]


def _model_style_sf_facts(letter: ExectLetter) -> list[dict[str, str]]:
    """One model-style de-dup fact per gold SF mention (no raw ``attributes`` dict)."""

    facts: list[dict[str, str]] = []
    for ann in letter.entities("SeizureFrequency"):
        facts.append(
            {
                "family": "seizure_frequency",
                "seizure_type": ann.text,
                "state": _fact_state_from_seizure_attrs(ann.attributes),
                "evidence": _valid_evidence(letter.note_text, ann),
            }
        )
    return facts


def _model_style_sf_facts_raw_evidence(letter: ExectLetter) -> list[dict[str, str]]:
    """Same model-style facts but evidence = raw (hyphenated) gold text verbatim.

    Reproduces the likely construction of the prior ad-hoc oracle that reported
    SF=0.0: gold ``text`` renders spaces as hyphens, so it is usually NOT an exact
    substring of the note and every SF mention fails the evidence gate.
    """

    return [
        {
            "family": "seizure_frequency",
            "seizure_type": ann.text,
            "state": _fact_state_from_seizure_attrs(ann.attributes),
            "evidence": ann.text,
        }
        for ann in letter.entities("SeizureFrequency")
    ]


def _oracle_replay_sf_facts(letter: ExectLetter) -> list[dict[str, str]]:
    """Replay-helper facts (full gold attributes preserved) — reproduces the D1 oracle."""

    gold_rows = [
        {"entity": ann.entity, "text": ann.text, "attributes": dict(ann.attributes),
         "evidence": _valid_evidence(letter.note_text, ann)}
        for ann in letter.entities("SeizureFrequency")
    ]
    facts, _notes = clinical_facts_from_mentions(gold_rows)
    return facts


def _score_dev(make_facts) -> dict[str, object]:
    letters = sorted(load_letters_for_split("dev"), key=lambda x: x.letter_id)

    tp = fp = fn = 0
    gold_state_total: Counter[str] = Counter()
    gold_state_matched: Counter[str] = Counter()
    dropped = 0
    n_pred_mentions = 0
    n_facts = 0
    type_key_kind_gold: Counter[str] = Counter()
    type_key_kind_pred: Counter[str] = Counter()
    examples: list[str] = []

    for letter in letters:
        facts = make_facts(letter)
        n_facts += len(facts)
        record = {"clinical_facts": facts}
        predicted, gate_warnings, _prov, _notes = to_predicted_letter_from_dedup_facts(
            letter, record
        )
        dropped += sum(1 for w in gate_warnings if "dropped" in w)
        n_pred_mentions += len(predicted.mentions)
        pred_exect = to_exect_letter(predicted)

        score = score_frequency_state([letter], [pred_exect]).clinical_headline
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)

        gold_keys = frequency_state_keys(letter.entities("SeizureFrequency"), "clinical_headline")
        pred_keys = set(
            frequency_state_keys(pred_exect.entities("SeizureFrequency"), "clinical_headline")
        )
        for k in _type_key_kinds(letter.entities("SeizureFrequency")):
            type_key_kind_gold[k] += 1
        for k in _type_key_kinds(pred_exect.entities("SeizureFrequency")):
            type_key_kind_pred[k] += 1

        for ann in letter.entities("SeizureFrequency"):
            state = _frequency_state(ann.attributes)
            gold_state_total[state] += 1
        matched_keys = set(gold_keys) & pred_keys
        for ann in letter.entities("SeizureFrequency"):
            for key in frequency_state_keys([ann], "clinical_headline"):
                if key in matched_keys:
                    gold_state_matched[_frequency_state(ann.attributes)] += 1

        unmatched = [k for k in gold_keys if k not in pred_keys]
        if unmatched and len(examples) < 8:
            examples.append(
                f"  {letter.letter_id}: gold={list(gold_keys)} pred={sorted(pred_keys)}"
            )

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": precision, "recall": recall, "f1": f1,
        "gold_state_total": gold_state_total,
        "gold_state_matched": gold_state_matched,
        "dropped": dropped,
        "n_facts": n_facts,
        "n_pred_mentions": n_pred_mentions,
        "type_key_kind_gold": type_key_kind_gold,
        "type_key_kind_pred": type_key_kind_pred,
        "examples": examples,
    }


def _type_key_kinds(annotations: Iterable[ExectAnnotation]) -> list[str]:
    kinds: list[str] = []
    for ann in annotations:
        key = _frequency_type_key(ann)
        kinds.append(key[0] if isinstance(key, tuple) else "?")
    return kinds


def _report(title: str, res: dict[str, object]) -> None:
    print(f"\n=== {title} ===")
    print(
        f"SF clinical_headline  F1={res['f1']:.3f}  "
        f"P={res['precision']:.3f} R={res['recall']:.3f}  "
        f"(tp={res['tp']} fp={res['fp']} fn={res['fn']})"
    )
    print(f"facts emitted={res['n_facts']}  pred mentions scored={res['n_pred_mentions']}  "
          f"dropped-by-gate={res['dropped']}")
    gt = res["gold_state_total"]
    gm = res["gold_state_matched"]
    print("per gold-state recall (matched / total):")
    for state in ("active-rate", "seizure-free", "unknown"):
        total = gt.get(state, 0)
        matched = gm.get(state, 0)
        rate = matched / total if total else 0.0
        print(f"    {state:<13} {matched:>3} / {total:<3}  = {rate:.3f}")
    print(f"type-key kind gold={dict(res['type_key_kind_gold'])} "
          f"pred={dict(res['type_key_kind_pred'])}")
    if res["examples"]:
        print("sample unmatched letters (gold keys vs pred keys):")
        for line in res["examples"]:
            print(line)


def main() -> None:
    print("H4 / D1 probe: can a PERFECT model-style SF answer score ~1.0?")
    print("(production path: model-style fact -> adapter -> gates -> CUI projection -> scorer)")
    _report("MODEL-STYLE perfect SF answer (production path)", _score_dev(_model_style_sf_facts))
    _report("ORACLE-REPLAY perfect SF answer (full gold attrs preserved)",
            _score_dev(_oracle_replay_sf_facts))
    _report("MODEL-STYLE + RAW hyphenated gold text as evidence (reproduces D1 0.0)",
            _score_dev(_model_style_sf_facts_raw_evidence))


if __name__ == "__main__":
    main()
