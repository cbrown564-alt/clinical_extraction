"""Merge the 4-parallel-reviewer verdict batches into ``_adjudication.csv`` + the gold case ledger.

Reads ``docs/research/error_analysis/{rx,inv}_canonical/_cases.json`` (written by
``exectv2_rx_inv_canonical_row_analysis.py``) plus each family's
``_verdicts_batch{0,1,2,3}.json`` (written by 4 parallel adjudication agents,
same pattern as the existing Dx/SF/Rx-Inv-evidence-recall adjudications), and
writes:

* ``docs/research/error_analysis/{rx,inv}_canonical/_adjudication.csv`` --
  case-level CSV (entity, letter_id, case_id, disagreement_type, match_key,
  verdict, mechanism, reason).
* ``experiments/gold_case_ledger_prescription.jsonl`` /
  ``..._investigations.jsonl`` -- the final ``GoldCaseRow`` ledger entries for
  these two families, folding what would otherwise be a separate merge step
  into this one pass since the case + verdict data already has everything
  ``GoldCaseRow`` needs.

Zero LLM calls. Fails loudly (not silently) if a batch file is missing or a
case_id is covered by zero or more than one batch, or if a verdict/mechanism
value isn't in the shared taxonomy -- adjudication coverage gaps should be
visible, not silently dropped.

Usage: uv run python experiments/exectv2_ledger/finalize_rx_inv_canonical.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from exectv2_ledger.mechanism import MECHANISM_VALUES, VERDICT_VALUES  # noqa: E402
from exectv2_ledger.schema import GoldCaseRow, write_gold_case_ledger  # noqa: E402

ROOT = _EXPERIMENTS_DIR.parent
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"

_FAMILY_CONFIG = {
    "Prescription": {
        "case_dir": ROOT / "docs" / "research" / "error_analysis" / "rx_canonical",
        "ledger_out": _EXPERIMENTS_DIR / "gold_case_ledger_prescription.jsonl",
        "row_prefix": "prescription",
    },
    "Investigations": {
        "case_dir": ROOT / "docs" / "research" / "error_analysis" / "inv_canonical",
        "ledger_out": _EXPERIMENTS_DIR / "gold_case_ledger_investigations.jsonl",
        "row_prefix": "investigations",
    },
}


def _load_verdicts(case_dir: Path, n_cases: int) -> dict[int, dict]:
    verdicts: dict[int, dict] = {}
    batch_files = sorted(case_dir.glob("_verdicts_batch*.json"))
    if not batch_files:
        raise FileNotFoundError(f"no _verdicts_batch*.json found in {case_dir}")
    for batch_file in batch_files:
        batch = json.loads(batch_file.read_text(encoding="utf-8"))
        for entry in batch:
            case_id = entry["case_id"]
            if case_id in verdicts:
                raise ValueError(f"{case_dir.name}: case_id {case_id} covered by more than one batch "
                                  f"(duplicate in {batch_file.name})")
            if entry["verdict"] not in {"GOLD_RIGHT", "MODEL_DEFENSIBLE", "BOTH_DEFENSIBLE"}:
                raise ValueError(f"{case_dir.name} case_id {case_id}: unrecognized verdict {entry['verdict']!r}")
            mechanism = entry["mechanism"]
            if mechanism not in MECHANISM_VALUES:
                raise ValueError(f"{case_dir.name} case_id {case_id}: mechanism {mechanism!r} not in "
                                  f"shared taxonomy {sorted(MECHANISM_VALUES)}")
            verdicts[case_id] = entry
    missing = sorted(set(range(1, n_cases + 1)) - verdicts.keys())
    if missing:
        raise ValueError(f"{case_dir.name}: case_id(s) {missing} have no verdict in any batch file")
    return verdicts


def finalize_family(entity: str) -> None:
    config = _FAMILY_CONFIG[entity]
    case_dir: Path = config["case_dir"]
    cases = json.loads((case_dir / "_cases.json").read_text(encoding="utf-8"))
    verdicts = _load_verdicts(case_dir, len(cases))

    csv_rows = []
    ledger_rows: list[GoldCaseRow] = []
    verdict_map = {"GOLD_RIGHT": "gold_right", "MODEL_DEFENSIBLE": "model_defensible", "BOTH_DEFENSIBLE": "both_defensible"}

    for case in cases:
        case_id = case["case_id"]
        v = verdicts[case_id]
        csv_rows.append({
            "entity": entity,
            "letter_id": case["letter_id"],
            "case_id": case_id,
            "disagreement_type": case["disagreement_type"],
            "match_key": case["match_key"],
            "verdict": v["verdict"],
            "mechanism": v["mechanism"],
            "reason": v["reason"],
        })

        gold_ann = case["gold_mentions"][0] if case["gold_mentions"] else None
        pred_ann = case["pred_mentions"][0] if case["pred_mentions"] else None
        gold_record = None
        pred_record = None
        if gold_ann is not None:
            gold_record = {"raw_text": gold_ann["raw_text"], "normalized_text": gold_ann["text"],
                            "attributes": gold_ann["attributes"]}
        if pred_ann is not None:
            pred_record = {"raw_text": pred_ann["raw_text"], "normalized_text": pred_ann["text"],
                            "attributes": pred_ann["attributes"]}

        ledger_rows.append(GoldCaseRow(
            row_id=f"{config['row_prefix']}:{RUN_ID}:{case['letter_id']}:{case['disagreement_type']}:case{case_id}",
            family=entity,
            run_id=RUN_ID,
            letter_id=case["letter_id"],
            disagreement_type=case["disagreement_type"],
            match_key=case["match_key"],
            source_letter_text=case["source_letter_text"],
            gold=gold_record,
            pred=pred_record,
            mechanism=v["mechanism"],
            verdict=verdict_map[v["verdict"]],
            provenance={
                "adjudicated_by": "4 parallel general-purpose agents, 2026-07-02 canonical row adjudication",
                "adjudicated_at": "2026-07-02",
                "hypothesis_id": None,
                "reason": v["reason"],
            },
        ))

    csv_path = case_dir / "_adjudication.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["entity", "letter_id", "case_id", "disagreement_type",
                                                      "match_key", "verdict", "mechanism", "reason"])
        writer.writeheader()
        writer.writerows(csv_rows)

    write_gold_case_ledger(ledger_rows, config["ledger_out"])

    n = len(cases)
    verdict_counts = {}
    mechanism_counts = {}
    for row in csv_rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
        mechanism_counts[row["mechanism"]] = mechanism_counts.get(row["mechanism"], 0) + 1
    genuine = mechanism_counts.get("genuine_model_error", 0)

    print(f"=== {entity} finalized: {n} cases ===")
    print(f"  verdicts: {verdict_counts}")
    print(f"  mechanisms: {mechanism_counts}")
    print(f"  genuine_model_error share: {genuine}/{n} = {genuine/n:.1%}")
    print(f"  -> {csv_path.relative_to(ROOT)}")
    print(f"  -> {config['ledger_out'].relative_to(ROOT)}\n")


def main() -> None:
    for entity in _FAMILY_CONFIG:
        finalize_family(entity)


if __name__ == "__main__":
    main()
