"""ExECTv2 GEPA under-performance diagnostics (committed from the investigation).

Companion to ``docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md``.

Two probes, both no new LLM calls:

**H4 / D1** — does a *perfect model-style* SeizureFrequency answer score ~1.0 on the
de-dup ``clinical_headline`` surface, or does the clinical_facts -> mention adapter +
render-safety gate + CUI projection silently cap it? "Model-style" means facts shaped
exactly as the dedup LLM emits them (``seizure_type`` + coarse ``state``, NO raw
``attributes`` dict), routed through the *production* path the GEPA metric scores:

    gold SF -> model-style fact -> clinical_facts_to_mentions
            -> to_predicted_letter_from_mentions (evidence gate + render gate
               + CUI projection) -> to_exect_letter -> score_frequency_state

**H2 / H6** — is the GEPA selection signal too noisy to detect the ~+0.01-0.03 real
gains? Parses a saved GEPA run log (per-candidate full-valset per-letter scores +
the accept/aggregate trajectory) and reports the selection signal-to-noise: the SE of
the valset-mean (n=50) and the minibatch-mean (n=3) against the actual inter-candidate
step gains, plus the best-so-far trajectory (H6: monotone? argmax returned?).

Run:
    uv run python experiments/exectv2_gepa_diagnostics.py
"""

from __future__ import annotations

import ast
import re
import statistics as stats
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

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


# --- H2 / H6: GEPA selection signal-to-noise from a saved run log ----------------

#: Default GEPA run log to analyse (the H1 diff-feedback run).
DEFAULT_GEPA_LOG = (
    Path(__file__).resolve().parents[1]
    / "experiments"
    / "gepa_overnight_exectv2"
    / "h1_diff_run.log"
)
_FLOAT = r"([0-9]+\.[0-9]+)"


def _parse_gepa_log(path: Path) -> dict[str, object] | None:
    if not path.exists():
        return None
    txt = path.read_text(encoding="utf-8", errors="replace")
    base = re.search(rf"Base program full valset score: {_FLOAT}", txt)
    per_candidate = [
        list(ast.literal_eval(d).values())
        for d in re.findall(r"Individual valset scores for new program: (\{.*?\})", txt)
    ]
    aggregates = [
        float(a) for a in re.findall(rf"Val aggregate for new program: {_FLOAT}", txt)
    ]
    best_so_far = [
        float(b) for b in re.findall(rf"Best valset aggregate score so far: {_FLOAT}", txt)
    ]
    decisions = re.findall(
        rf"New subsample score {_FLOAT} is (better|not better) than old score {_FLOAT}", txt
    )
    return {
        "seed_aggregate": float(base.group(1)) if base else None,
        "per_candidate": per_candidate,
        "aggregates": aggregates,
        "best_so_far": best_so_far,
        "decisions": decisions,
    }


def _report_h2(path: Path, minibatch_size: int = 3) -> None:
    parsed = _parse_gepa_log(path)
    print(f"\n=== H2/H6 selection signal-to-noise ({path.name}) ===")
    if parsed is None:
        print(f"  (log not found at {path}; skipping)")
        return

    per_candidate = parsed["per_candidate"]
    aggregates = parsed["aggregates"]
    best_so_far = parsed["best_so_far"]

    # Per-letter score spread -> SE of the selection estimators.
    per_letter_std = stats.median(stats.pstdev(v) for v in per_candidate if len(v) > 1)
    n_val = len(per_candidate[0]) if per_candidate else 0
    se_val = per_letter_std / (n_val**0.5) if n_val else float("nan")
    se_mini = per_letter_std / (minibatch_size**0.5)

    step_deltas = [
        round(aggregates[i] - aggregates[i - 1], 4) for i in range(1, len(aggregates))
    ]
    median_abs_step = stats.median(abs(d) for d in step_deltas) if step_deltas else float("nan")

    print(f"seed valset aggregate          = {parsed['seed_aggregate']:.4f}")
    print(f"accepted candidates (full-eval)= {len(per_candidate)} (valset n={n_val})")
    print(f"per-letter score std (median)  = {per_letter_std:.3f}")
    print(f"SE of valset mean (n={n_val})       = {se_val:.4f}")
    print(f"SE of minibatch mean (n={minibatch_size})    = {se_mini:.4f}  <-- accept-gate noise")
    print(f"median |accepted-step gain|    = {median_abs_step:.4f}")
    print(
        f"selection SNR  valset={median_abs_step / se_val:.2f}  "
        f"minibatch={median_abs_step / se_mini:.2f}  "
        f"({'NOISY: gains < noise' if median_abs_step < se_mini else 'ok'})"
    )
    print(f"best-so-far trajectory         = {[round(b, 3) for b in best_so_far]}")
    monotone = all(b2 >= b1 - 1e-9 for b1, b2 in zip(best_so_far, best_so_far[1:], strict=False))
    print(f"H6: best-so-far monotone       = {monotone}; final best = {max(best_so_far):.4f}")
    if parsed["decisions"]:
        accepted = sum(1 for d in parsed["decisions"] if d[1] == "better")
        margins = [abs(float(n) - float(o)) / minibatch_size for n, _, o in parsed["decisions"]]
        print(
            f"minibatch decisions            = {len(parsed['decisions'])} "
            f"(accepted {accepted}); median per-example margin = {stats.median(margins):.3f} "
            f"(vs SE {se_mini:.3f})"
        )


def main() -> None:
    print("H4 / D1 probe: can a PERFECT model-style SF answer score ~1.0?")
    print("(production path: model-style fact -> adapter -> gates -> CUI projection -> scorer)")
    _report("MODEL-STYLE perfect SF answer (production path)", _score_dev(_model_style_sf_facts))
    _report("ORACLE-REPLAY perfect SF answer (full gold attrs preserved)",
            _score_dev(_oracle_replay_sf_facts))
    _report("MODEL-STYLE + RAW hyphenated gold text as evidence (reproduces D1 0.0)",
            _score_dev(_model_style_sf_facts_raw_evidence))
    _report_h2(DEFAULT_GEPA_LOG, minibatch_size=3)


if __name__ == "__main__":
    main()
