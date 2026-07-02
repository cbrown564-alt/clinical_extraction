"""Canonical Prescription/Investigations row-by-row analysis on the scored `clinical_headline` metric.

Answers the question ``docs/canon/workstreams/`` couldn't before this script existed: Dx and
SF both got a full disagreement-by-disagreement adjudication of their `clinical_headline`
scoring gap (``exectv2_{dx,sf}_canonical_row_analysis.py``); Prescription and Investigations
only ever got a *narrower, different* investigation -- whether the `source_near` evidence-recall
*diagnostic* is trustworthy (``exectv2_rx_inv_evidence_recall_consolidation_check.py``). This
script closes that gap for the actual scored surface, one shared driver for both families (they
share the same simple, symmetric, home-tagged multiset `clinical_headline` scoring convention --
see ``experiments/exectv2_ledger/match_replay.py`` -- unlike Dx/SF, which each need their own
bespoke asymmetric/state-set logic and already have it).

Zero new LLM calls: replays the already-cached GEPA per-family prediction jsonl, the SAME run_id
Dx/SF's canonical analyses used (``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628``), so
all four families' ledger rows are comparable (same run, same date, same model).

Outputs (to ``docs/research/error_analysis/{rx,inv}_canonical/``):
* ``_index.json``   -- per-letter gold/missed/spurious counts + self-validation.
* ``_summary.json`` -- aggregate decomposition vs the official scorer.
* ``_cases.json``   -- one entry per disagreement case, ready for adjudication
                       (mirrors ``rx_inv_ev_recall/_cases.json``'s shape).
* ``<letter>.md``   -- per-letter substrate (gold/predicted mentions with full attributes, the
                       diff, full letter text) for every disagreement letter.

Usage:  uv run python experiments/exectv2_rx_inv_canonical_row_analysis.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parent
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from exectv2_ledger.match_replay import DisagreementCase, replay_clinical_headline  # noqa: E402

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter  # noqa: E402
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data  # noqa: E402
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (  # noqa: E402
    score_investigations_components,
    score_prescription_components,
)

ROOT = _EXPERIMENTS_DIR
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"

_FAMILY_CONFIG = {
    "Prescription": {
        "out_dir": ROOT.parent / "docs" / "research" / "error_analysis" / "rx_canonical",
        "official_fn": score_prescription_components,
    },
    "Investigations": {
        "out_dir": ROOT.parent / "docs" / "research" / "error_analysis" / "inv_canonical",
        "official_fn": score_investigations_components,
    },
}


def _pred_letters(run_id: str) -> dict[str, ExectLetter]:
    rows = [
        json.loads(line)
        for line in (ROOT / f"{run_id}.jsonl").read_text(encoding="utf-8").splitlines()
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


def _mention_record(ann: ExectAnnotation) -> dict:
    return {
        "raw_text": ann.raw_text,
        "text": ann.text,
        "attributes": dict(ann.attributes),
    }


def _mention_line(ann: ExectAnnotation) -> str:
    attrs = ", ".join(f"{k}={v!r}" for k, v in sorted(ann.attributes.items()))
    raw_note = f" (raw={ann.raw_text!r})" if ann.raw_text and ann.raw_text != ann.text else ""
    return f"- {ann.text!r}{raw_note} | {attrs or '(no attributes)'}"


def analyze_family(entity: str) -> None:
    config = _FAMILY_CONFIG[entity]
    out_dir: Path = config["out_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)

    gold_letters = gepa_data.load_dev_letters()
    pred_by_id = _pred_letters(RUN_ID)
    empty_letter = lambda lid: ExectLetter(letter_id=lid, note_text="", annotations=())  # noqa: E731
    pred_letters = [pred_by_id.get(g.letter_id) or empty_letter(g.letter_id) for g in gold_letters]
    gold_by_id = {g.letter_id: g for g in gold_letters}
    pred_by_letter_id = {p.letter_id: p for p in pred_letters}

    cases, replayed = replay_clinical_headline(gold_letters, pred_letters, entity)
    official = config["official_fn"](gold_letters, pred_letters).clinical_headline
    decomposition_matches_official = (
        official.tp == replayed.tp and official.fp == replayed.fp and official.fn == replayed.fn
    )

    cases_by_letter: dict[str, list[DisagreementCase]] = {}
    for case in cases:
        cases_by_letter.setdefault(case.letter_id, []).append(case)

    index = []
    for letter_id in sorted(gold_by_id.keys() | pred_by_letter_id.keys()):
        letter_cases = cases_by_letter.get(letter_id, [])
        missed = [c for c in letter_cases if c.disagreement_type == "missed"]
        spurious = [c for c in letter_cases if c.disagreement_type == "spurious"]
        index.append({
            "letter_id": letter_id,
            "n_missed": len(missed),
            "n_spurious": len(spurious),
            "letter_exact": not missed and not spurious,
        })
        if letter_cases:
            write_substrate(out_dir, gold_by_id.get(letter_id), pred_by_letter_id.get(letter_id),
                             entity, missed, spurious)

    n_disagreement_letters = sum(1 for rec in index if not rec["letter_exact"])
    summary = {
        "run_id": RUN_ID,
        "entity": entity,
        "n_letters": len(index),
        "official_clinical_headline": official.model_dump(),
        "replayed_clinical_headline": replayed.model_dump(),
        "decomposition_matches_official": decomposition_matches_official,
        "n_disagreement_letters": n_disagreement_letters,
        "n_disagreement_cases": len(cases),
        "n_missed": sum(1 for c in cases if c.disagreement_type == "missed"),
        "n_spurious": sum(1 for c in cases if c.disagreement_type == "spurious"),
    }
    (out_dir / "_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (out_dir / "_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    case_records = []
    for case_id, case in enumerate(sorted(cases, key=lambda c: (c.letter_id, c.disagreement_type, str(c.match_key))), start=1):
        letter = gold_by_id.get(case.letter_id)
        pred_letter = pred_by_letter_id.get(case.letter_id)
        case_records.append({
            "case_id": case_id,
            "entity": entity,
            "letter_id": case.letter_id,
            "disagreement_type": case.disagreement_type,
            "match_key": repr(case.match_key),
            "gold_mentions": [_mention_record(a) for a in case.gold_mentions],
            "pred_mentions": [_mention_record(a) for a in case.pred_mentions],
            "gold_family_all": [_mention_record(a) for a in (letter.entities(entity) if letter else ())],
            "pred_family_all": [_mention_record(a) for a in (pred_letter.entities(entity) if pred_letter else ())],
            "source_letter_text": letter.note_text if letter else "",
            "mechanism": "UNADJUDICATED",
            "verdict": "UNADJUDICATED",
        })
    (out_dir / "_cases.json").write_text(json.dumps(case_records, indent=2), encoding="utf-8")

    print(f"=== CANONICAL {entity.upper()} clinical_headline ANALYSIS ===")
    print(f"OFFICIAL : P={official.precision:.4f} R={official.recall:.4f} F1={official.f1:.4f} "
          f"(tp={official.tp} fp={official.fp} fn={official.fn})")
    print(f"REPLAYED : P={replayed.precision:.4f} R={replayed.recall:.4f} F1={replayed.f1:.4f} "
          f"(tp={replayed.tp} fp={replayed.fp} fn={replayed.fn})")
    print(f"decomposition matches official: {decomposition_matches_official}")
    print(f"disagreement letters: {n_disagreement_letters}/{len(index)}  "
          f"cases: {len(cases)} ({summary['n_missed']} missed, {summary['n_spurious']} spurious)")
    print(f"Wrote {len(case_records)} cases + {n_disagreement_letters} letter substrate files + "
          f"_index.json + _summary.json to {out_dir}\n")


def write_substrate(out_dir: Path, gold_letter, pred_letter, entity: str, missed, spurious) -> None:
    letter_id = (gold_letter or pred_letter).letter_id
    note_text = gold_letter.note_text if gold_letter else "(no gold letter)"
    lines = [
        f"# {letter_id} -- {entity} clinical_headline disagreements",
        f"missed (FN, gold key with no matching prediction) = {[repr(c.match_key) for c in missed]}",
        f"spurious (FP, predicted key with no matching gold) = {[repr(c.match_key) for c in spurious]}\n",
        f"## GOLD {entity} mentions",
    ]
    lines += [_mention_line(a) for a in (gold_letter.entities(entity) if gold_letter else ())] or ["(none)"]
    lines += ["", f"## PREDICTED {entity} mentions"]
    lines += [_mention_line(a) for a in (pred_letter.entities(entity) if pred_letter else ())] or ["(none)"]

    lines += ["", "## MISSED (FN) detail"]
    for case in missed:
        lines.append(f"- key={case.match_key!r}")
        for a in case.gold_mentions:
            lines.append(f"    gold: {_mention_line(a)}")
    if not missed:
        lines.append("(none)")

    lines += ["", "## SPURIOUS (FP) detail"]
    for case in spurious:
        lines.append(f"- key={case.match_key!r}")
        for a in case.pred_mentions:
            lines.append(f"    pred: {_mention_line(a)}")
    if not spurious:
        lines.append("(none)")

    lines += ["", "## FULL LETTER TEXT", "```", note_text, "```"]
    (out_dir / f"{letter_id}.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    for entity in _FAMILY_CONFIG:
        analyze_family(entity)


if __name__ == "__main__":
    main()
