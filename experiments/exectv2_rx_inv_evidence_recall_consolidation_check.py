"""Phase 4 of
``docs/plans/exectv2_gepa_ev_recall_consolidation_reexamination_plan_2026-06-30.md``
(Prescription + Investigations extension, fresh predeclaration in that plan's Phase 4
section).

Question: Phase 1 (Diagnosis, 93.5% H-inflated) and Phase 3 (SeizureFrequency, 83.3% /
61.1% H-inflated under two readings) both found that the gold-multiplicity /
cardinality-exhaustion mechanism inflates `source_near` evidence-recall misses for the
two `clinical_headline`-DEDUPING entities. Does the same mechanism transfer to
Prescription and Investigations, which are scored PER-OCCURRENCE (no headline-level
deduping, per `_DEDUPING_HEADLINE_ENTITIES` in `scoring/match.py`)? The live open
question (plan §5 Phase 4): the dedup convention is plausibly the *cause* of H1
cardinality artifacts (annotators tag exhaustively because dedup will collapse it later);
Rx/Inv lack that incentive, so this phase may legitimately return a clean negative.

Method: identical structural definition to the SF Phase 3 script -- H1/H2 applied
directly to each family's own `source_near` FN population (no `clinical_headline`-level
intermediate list, since neither family's scored unit is concept-key annotation-keyed
the way Dx's is):

  H1_CARDINALITY        -- overlap exists ignoring used_pred, absent respecting it (the
                            model's text WAS retrieved but another gold annotation of the
                            same family in the same letter claimed the matching
                            prediction first).
  H2_GENUINE_DIVERGENCE -- no overlapping same-family prediction exists at all.

Zero new LLM calls for the mechanical split -- replays the cached GEPA per-family
prediction jsonl (`exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628`, the same
GEPA-best run Phase 1/Phase 3 and the evidence-decomposition doc use).

No existing per-case clinical verdict to cross-reference for either family (no prior
adjudication exists, per the plan's original non-goals). This script's second half writes
a full adjudication substrate (letter text + gold/pred family mentions + cross-entity
overlap flag) per FN case to ``_rx_inv_ev_recall/<entity>/<case>.md`` and a manifest to
``_rx_inv_ev_recall/_cases.json``, for a FRESH clinical pass using the same GOLD_RIGHT /
MODEL_DEFENSIBLE / BOTH_DEFENSIBLE taxonomy as the Dx and SF adjudications.

Usage: uv run python experiments/exectv2_rx_inv_evidence_recall_consolidation_check.py
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
    source_near_diagnostic,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _first_overlapping_prediction,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
OUT = ROOT / "_rx_inv_ev_recall"
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
ENTITIES = ("Prescription", "Investigations")

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


def _any_entity_overlap(gold: ExectAnnotation, all_pred_anns: list[ExectAnnotation], entity: str) -> bool:
    gold_phrase = normalize_phrase(gold.text)
    if not gold_phrase:
        return False
    for pred in all_pred_anns:
        if pred.entity == entity:
            continue
        pred_phrase = normalize_phrase(pred.text)
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return True
    return False


def _ann_dump(a: ExectAnnotation) -> dict:
    return {"text": a.text, "attributes": dict(a.attributes)}


def _fmt_ann(d: dict) -> str:
    attrs = ", ".join(f"{k}={v}" for k, v in d["attributes"].items() if v) or "(no attributes)"
    return f"- {d['text']!r} -> {attrs}"


def process_entity(
    entity: str,
    gold_letters: list[ExectLetter],
    pred_by_id: dict[str, ExectLetter],
    empty_letter,
) -> tuple[dict, list[dict]]:
    # --- self-validation gate -------------------------------------------- #
    pred_letters = [pred_by_id.get(g.letter_id) or empty_letter(g.letter_id) for g in gold_letters]
    official_sn = source_near_diagnostic(gold_letters, pred_letters, [entity], benchmark_config_for)
    official = official_sn.per_entity[entity]

    own_tp = own_fn = 0
    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)
        gold_anns = list(g.entities(entity))
        pred_anns = list(p.entities(entity))
        trace = _respecting_used_pred_trace(gold_anns, pred_anns)
        own_tp += sum(1 for t in trace if t is not None)
        own_fn += sum(1 for t in trace if t is None)

    gate_pass = own_tp == official.overlap.tp and own_fn == official.overlap.fn
    print(f"=== PHASE 0: self-validation gate ({entity}) ===")
    print(f"official source_near {entity}: tp={official.overlap.tp} fn={official.overlap.fn} "
          f"recall={official.overlap.recall:.4f}")
    print(f"own trace reproduction       : tp={own_tp} fn={own_fn}")
    print(f"GATE {'PASS' if gate_pass else 'FAIL'}")
    if not gate_pass:
        raise SystemExit(f"Phase 0 gate failed for {entity} -- own trace does not reproduce official "
                          f"source_near tp/fn. Stopping before Phase 1.")

    # --- Phase 1: mechanical H1/H2 split + substrate dump ------------------ #
    entity_out = OUT / entity.lower()
    entity_out.mkdir(parents=True, exist_ok=True)

    mechanism_counts: Counter[str] = Counter()
    cross_entity_flags = 0
    cases: list[dict] = []
    case_id = 0

    for g in gold_letters:
        p = pred_by_id.get(g.letter_id) or empty_letter(g.letter_id)
        gold_anns = list(g.entities(entity))
        pred_anns = list(p.entities(entity))
        if not gold_anns:
            continue
        all_pred_anns = list(p.annotations)
        all_gold_anns_other = [a for a in g.annotations if a.entity != entity]

        trace = _respecting_used_pred_trace(gold_anns, pred_anns)

        for i, gold in enumerate(gold_anns):
            if trace[i] is not None:
                continue  # not an FN
            matched_ignoring = _ignoring_used_pred_match(gold, pred_anns)
            mechanism = H1_CARDINALITY if matched_ignoring else H2_GENUINE_DIVERGENCE
            mechanism_counts[mechanism] += 1

            cross_entity = False
            if mechanism == H2_GENUINE_DIVERGENCE:
                cross_entity = _any_entity_overlap(gold, all_pred_anns, entity)
                if cross_entity:
                    cross_entity_flags += 1

            case_id += 1
            case = {
                "case_id": case_id,
                "entity": entity,
                "letter_id": g.letter_id,
                "mechanism": mechanism,
                "cross_entity_overlap": cross_entity,
                "gold_missed": _ann_dump(gold),
                "gold_family_all": [_ann_dump(a) for a in gold_anns],
                "pred_family_all": [_ann_dump(a) for a in pred_anns],
                "gold_other_entities": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in all_gold_anns_other
                ],
                "verdict": "UNADJUDICATED",
            }
            cases.append(case)
            write_substrate(entity_out, g, case)

    total = sum(mechanism_counts.values())
    assert total == official.overlap.fn, (
        f"{entity}: classified {total} cases but official fn={official.overlap.fn}"
    )

    h1 = mechanism_counts[H1_CARDINALITY]
    h2 = mechanism_counts[H2_GENUINE_DIVERGENCE]
    print(f"\n=== PHASE 1: mechanical H1/H2 split ({total} {entity} source_near FNs) ===")
    print(f"H1_CARDINALITY        = {h1} ({h1/total:.1%})" if total else "H1_CARDINALITY        = 0")
    print(f"H2_GENUINE_DIVERGENCE = {h2} ({h2/total:.1%})" if total else "H2_GENUINE_DIVERGENCE = 0")
    print(f"  cross-entity overlap among H2 (informational): {cross_entity_flags}/{h2}" if h2 else "")

    out = {
        "entity": entity,
        "phase0_gate_pass": gate_pass,
        "official_source_near": official.model_dump(),
        "n_fn_cases": total,
        "mechanism_counts": dict(mechanism_counts),
        "cross_entity_overlap_among_h2": cross_entity_flags,
    }
    return out, cases


def write_substrate(out_dir: Path, letter: ExectLetter, case: dict) -> None:
    entity = case["entity"]
    lines = [
        f"# case {case['case_id']} -- {letter.letter_id} -- entity={entity} "
        f"mechanism={case['mechanism']} cross_entity_overlap={case['cross_entity_overlap']}\n",
        f"## MISSED gold {entity} mention (the source_near FN under adjudication)",
        _fmt_ann(case["gold_missed"]),
        "",
        f"## ALL gold {entity} mentions in this letter",
    ]
    lines += [_fmt_ann(d) for d in case["gold_family_all"]] or ["(none)"]
    lines += ["", f"## ALL predicted {entity} mentions (GEPA-best run) in this letter"]
    lines += [_fmt_ann(d) for d in case["pred_family_all"]] or ["(none)"]
    lines += ["", "## gold annotations of OTHER entities in this letter (context)"]
    lines += [
        f"- {a['entity']}: {a['text']!r} {a['attributes']}" for a in case["gold_other_entities"]
    ] or ["(none)"]
    lines += ["", "## FULL LETTER TEXT", "```", letter.note_text, "```"]
    (out_dir / f"case_{case['case_id']:03d}_{letter.letter_id}.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gold_letters = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(RUN_ID)
    empty_letter = lambda lid: ExectLetter(letter_id=lid, note_text="", annotations=())  # noqa: E731

    per_entity_summary = {}
    all_cases: list[dict] = []
    for entity in ENTITIES:
        summary, cases = process_entity(entity, gold_letters, pred_by_id, empty_letter)
        per_entity_summary[entity] = summary
        all_cases.extend(cases)

    out = {
        "run_id": RUN_ID,
        "entities": list(ENTITIES),
        "per_entity": per_entity_summary,
        "n_total_cases": len(all_cases),
        "cases": all_cases,
    }
    (EXPERIMENTS / "exectv2_rx_inv_evidence_recall_consolidation_check.json").write_text(
        json.dumps(out, indent=2), encoding="utf-8"
    )
    (OUT / "_cases.json").write_text(json.dumps(all_cases, indent=2), encoding="utf-8")
    print(f"\nWrote {EXPERIMENTS / 'exectv2_rx_inv_evidence_recall_consolidation_check.json'}")
    print(f"Wrote {OUT / '_cases.json'} and {len(all_cases)} per-case substrate files to {OUT}")


if __name__ == "__main__":
    main()
