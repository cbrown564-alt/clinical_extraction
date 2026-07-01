"""Phase 3 of
``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``
(SF extension, fresh predeclaration in that plan's Phase 3 section).

Question: does the SAME gold-multiplicity mechanism that inflated Diagnosis's
``source_near`` evidence-recall gap (Phase 1: 93.5% of Dx's 92 misses were cardinality
artifacts or clinically-defensible consolidation, not genuine retrieval failure) ALSO
inflate SeizureFrequency's evidence-recall gap?

SF has no ``clinical_headline``-level intermediate miss list to start from the way Dx's
92 ``missed_concepts`` did (``state_profile`` is a per-letter type-agnostic state set,
not an annotation-keyed metric), so this applies the H1/H2 split directly to SF's own
``source_near`` FN population on the GEPA-best run:

  H1_CARDINALITY        -- overlap exists ignoring used_pred, absent respecting it
                            (the model's text WAS retrieved but another gold
                            SeizureFrequency annotation in the same letter claimed the
                            matching prediction first -- itself evidence of gold
                            multiplicity, since this only happens when >1 gold
                            annotation competes for the same predicted text).
  H2_GENUINE_DIVERGENCE -- no overlapping SeizureFrequency prediction exists at all.

Zero new LLM calls for this mechanical split -- replays the cached GEPA per-family
prediction jsonl (``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628``, the same
GEPA-best run the evidence-decomposition doc's 0.694 figure and Dx's Phase 1 used).

Unlike Phase 1, there is no existing per-case clinical verdict to cross-reference (the
SF Phase 7 adjudication is letter-level, on a different model run, for a different
metric). This script's second half writes a full adjudication substrate (letter text +
gold/pred SF mentions + cross-entity overlap flag) per FN case to
``docs/research/error_analysis/sf_ev_recall/<letter>.md`` and a manifest to
``docs/research/error_analysis/sf_ev_recall/_cases.json``, for a
FRESH clinical pass (see ``exectv2_sf_evidence_recall_adjudication.py``, written after
this script's output is reviewed) using the same GOLD_RIGHT / MODEL_DEFENSIBLE /
BOTH_DEFENSIBLE taxonomy as the Dx and SF Phase-7 adjudications.

Usage: uv run python experiments/exectv2_sf_evidence_recall_consolidation_check.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    frequency_state_faithful,
    source_near_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _first_overlapping_prediction,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
OUT = ROOT / "docs" / "research" / "error_analysis" / "sf_ev_recall"
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
ENTITY = "SeizureFrequency"

H1_CARDINALITY = "H1_CARDINALITY"
H2_GENUINE_DIVERGENCE = "H2_GENUINE_DIVERGENCE"


def _pred_letters(run_id: str) -> dict[str, ExectLetter]:
    rows = [
        json.loads(line)
        for line in (EXPERIMENTS / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    letters: dict[str, ExectLetter] = {}
    for row in rows:
        anns = tuple(
            ExectAnnotation(
                entity=m["entity"],
                text=m.get("text", ""),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in row.get("predicted_mentions", [])
        )
        letters[row["letter_id"]] = ExectLetter(letter_id=row["letter_id"], note_text="", annotations=anns)
    return letters


def _respecting_used_pred_trace(
    gold_anns: list[ExectAnnotation], pred_anns: list[ExectAnnotation]
) -> list[int | None]:
    """Mirror ``_source_near_entity``'s per-letter loop exactly: shared ``used_pred``
    state across gold annotations processed in order."""
    used_pred: set[int] = set()
    trace: list[int | None] = []
    for gold in gold_anns:
        pred_index = _first_overlapping_prediction(gold, pred_anns, used_pred)
        trace.append(pred_index)
        if pred_index is not None:
            used_pred.add(pred_index)
    return trace


def _ignoring_used_pred_match(gold: ExectAnnotation, pred_anns: list[ExectAnnotation]) -> bool:
    return _first_overlapping_prediction(gold, pred_anns, set()) is not None


def _any_entity_overlap(gold: ExectAnnotation, all_pred_anns: list[ExectAnnotation]) -> bool:
    gold_phrase = normalize_phrase(gold.text)
    if not gold_phrase:
        return False
    for pred in all_pred_anns:
        if pred.entity == ENTITY:
            continue
        pred_phrase = normalize_phrase(pred.text)
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return True
    return False


def _ann_dump(a: ExectAnnotation) -> dict:
    attrs = {k: v for k, v in a.attributes.items()}
    return {
        "text": a.text,
        "state": frequency_state_faithful(a.attributes),
        "FC": attrs.get("FrequencyChange", ""),
        "N": attrs.get("NumberOfSeizures", ""),
        "Lo": attrs.get("LowerNumberOfSeizures", ""),
        "Hi": attrs.get("UpperNumberOfSeizures", ""),
        "CUI": attrs.get("CUI", ""),
        "CUIPhrase": attrs.get("CUIPhrase", ""),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gold_letters = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(RUN_ID)
    empty_letter = lambda lid: ExectLetter(letter_id=lid, note_text="", annotations=())  # noqa: E731

    # --- self-validation gate -------------------------------------------- #
    pred_letters = [pred_by_id.get(g.letter_id) or empty_letter(g.letter_id) for g in gold_letters]
    official_sn = source_near_diagnostic(gold_letters, pred_letters, [ENTITY], benchmark_config_for)
    official_sf = official_sn.per_entity[ENTITY]

    own_tp = own_fn = 0
    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)
        gold_anns = list(g.entities(ENTITY))
        pred_anns = list(p.entities(ENTITY))
        trace = _respecting_used_pred_trace(gold_anns, pred_anns)
        own_tp += sum(1 for t in trace if t is not None)
        own_fn += sum(1 for t in trace if t is None)

    gate_pass = own_tp == official_sf.overlap.tp and own_fn == official_sf.overlap.fn
    print("=== PHASE 0: self-validation gate ===")
    print(f"official source_near SeizureFrequency: tp={official_sf.overlap.tp} fn={official_sf.overlap.fn} "
          f"recall={official_sf.overlap.recall:.4f}")
    print(f"own trace reproduction                : tp={own_tp} fn={own_fn}")
    print(f"GATE {'PASS' if gate_pass else 'FAIL'}")
    if not gate_pass:
        raise SystemExit("Phase 0 gate failed -- own trace does not reproduce official source_near "
                          "SeizureFrequency tp/fn. Stopping before Phase 1.")

    # --- Phase 1: mechanical H1/H2 split + substrate dump ------------------ #
    mechanism_counts: Counter[str] = Counter()
    cross_entity_flags = 0
    cases: list[dict] = []
    case_id = 0

    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)
        gold_anns = list(g.entities(ENTITY))
        pred_anns = list(p.entities(ENTITY))
        if not gold_anns:
            continue
        all_pred_anns = list(p.annotations)
        all_gold_anns_other = [a for a in g.annotations if a.entity != ENTITY]

        trace = _respecting_used_pred_trace(gold_anns, pred_anns)

        for i, gold in enumerate(gold_anns):
            if trace[i] is not None:
                continue  # not an FN
            matched_ignoring = _ignoring_used_pred_match(gold, pred_anns)
            mechanism = H1_CARDINALITY if matched_ignoring else H2_GENUINE_DIVERGENCE
            mechanism_counts[mechanism] += 1

            cross_entity = False
            if mechanism == H2_GENUINE_DIVERGENCE:
                cross_entity = _any_entity_overlap(gold, all_pred_anns)
                if cross_entity:
                    cross_entity_flags += 1

            case_id += 1
            case = {
                "case_id": case_id,
                "letter_id": g.letter_id,
                "mechanism": mechanism,
                "cross_entity_overlap": cross_entity,
                "gold_missed": _ann_dump(gold),
                "gold_sf_all": [_ann_dump(a) for a in gold_anns],
                "pred_sf_all": [_ann_dump(a) for a in pred_anns],
                "gold_other_entities": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in all_gold_anns_other
                ],
                "verdict": "UNADJUDICATED",
            }
            cases.append(case)

            write_substrate(OUT, g, case)

    total = sum(mechanism_counts.values())
    assert total == official_sf.overlap.fn, (
        f"classified {total} cases but official fn={official_sf.overlap.fn}"
    )

    h1 = mechanism_counts[H1_CARDINALITY]
    h2 = mechanism_counts[H2_GENUINE_DIVERGENCE]
    print(f"\n=== PHASE 1: mechanical H1/H2 split ({total} SeizureFrequency source_near FNs) ===")
    print(f"H1_CARDINALITY        = {h1} ({h1/total:.1%})")
    print(f"H2_GENUINE_DIVERGENCE = {h2} ({h2/total:.1%})")
    print(f"  cross-entity overlap among H2 (informational): {cross_entity_flags}/{h2}")
    print("\nNo existing per-case clinical verdict to cross-reference (unlike Dx Phase 1) -- "
          "wrote full adjudication substrate for a FRESH pass.")

    out = {
        "run_id": RUN_ID,
        "entity": ENTITY,
        "phase0_gate_pass": gate_pass,
        "official_source_near_sf": official_sf.model_dump(),
        "n_fn_cases": total,
        "mechanism_counts": dict(mechanism_counts),
        "cross_entity_overlap_among_h2": cross_entity_flags,
        "cases": cases,
    }
    (EXPERIMENTS / "exectv2_sf_evidence_recall_consolidation_check.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    (OUT / "_cases.json").write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"\nWrote {EXPERIMENTS / 'exectv2_sf_evidence_recall_consolidation_check.json'}")
    print(f"Wrote {OUT / '_cases.json'} and {total} per-case substrate files to {OUT}")


def write_substrate(out_dir: Path, letter: ExectLetter, case: dict) -> None:
    lines = [
        f"# case {case['case_id']} -- {letter.letter_id} -- mechanism={case['mechanism']}"
        f" cross_entity_overlap={case['cross_entity_overlap']}\n",
        "## MISSED gold SeizureFrequency mention (the source_near FN under adjudication)",
        f"- {case['gold_missed']['text']!r} -> state={case['gold_missed']['state']} | "
        f"FC={case['gold_missed']['FC'] or '-'} N={case['gold_missed']['N'] or '-'} "
        f"Lo/Hi={case['gold_missed']['Lo'] or '-'}/{case['gold_missed']['Hi'] or '-'} "
        f"CUI={case['gold_missed']['CUI'] or '-'} ({case['gold_missed']['CUIPhrase'] or '-'})",
        "",
        "## ALL gold SeizureFrequency mentions in this letter",
    ]
    lines += [
        f"- {d['text']!r} -> state={d['state']} | FC={d['FC'] or '-'} N={d['N'] or '-'} "
        f"Lo/Hi={d['Lo'] or '-'}/{d['Hi'] or '-'} CUI={d['CUI'] or '-'} ({d['CUIPhrase'] or '-'})"
        for d in case["gold_sf_all"]
    ] or ["(none)"]
    lines += ["", "## ALL predicted SeizureFrequency mentions (GEPA-best run) in this letter"]
    lines += [
        f"- {d['text']!r} -> state={d['state']} | FC={d['FC'] or '-'} N={d['N'] or '-'} "
        f"Lo/Hi={d['Lo'] or '-'}/{d['Hi'] or '-'} CUI={d['CUI'] or '-'} ({d['CUIPhrase'] or '-'})"
        for d in case["pred_sf_all"]
    ] or ["(none)"]
    lines += ["", "## gold annotations of OTHER entities in this letter (context)"]
    lines += [
        f"- {a['entity']}: {a['text']!r} {a['attributes']}" for a in case["gold_other_entities"]
    ] or ["(none)"]
    lines += ["", "## FULL LETTER TEXT", "```", letter.note_text, "```"]
    (out_dir / f"case_{case['case_id']:03d}_{letter.letter_id}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
