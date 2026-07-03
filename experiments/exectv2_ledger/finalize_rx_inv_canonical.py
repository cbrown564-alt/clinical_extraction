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
case has no verdict under any matching strategy, or if a verdict/mechanism
value isn't in the shared taxonomy -- adjudication coverage gaps should be
visible, not silently dropped.

== Content-keyed verdict matching (2026-07-03 fix) ==

The verdict batches carry ONLY a positional ``case_id`` + verdict/mechanism/
reason -- they have no letter_id/match_key of their own. The 2026-07-02
scorer-correctness sweep regenerated ``_cases.json`` under the finalized
scorer, which RESOLVED 14 Rx disagreements and SURFACED new ones, renumbering
the positional case_ids (48->36 Rx, 31->35 Inv). Under the old positional
``verdicts[case_id]`` join this silently mis-paired Rx (48 verdicts vs 36
cases) and crashed Inv (case_ids 32-35 uncovered).

The durable fix: join verdicts to cases by CONTENT KEY
``(letter_id, match_key, disagreement_type)`` rather than positional case_id.
The verdict batches are bridged to content keys via the PRE-swEEP ``_cases.json``
recovered from git (commit 4def0b73, the 48-Rx/31-Inv case set the verdicts
were originally authored against). This recovers 5 of the 6 rows the direct
ledger reconciliation had orphaned as ``unadjudicated``: they were already
adjudicated under the same content key in the old set, the reconciliation
just failed to match them.

Genuinely-new disagreements (key not present in the pre-sweep case set) are
sourced from ``_new_case_verdicts.json`` in each family dir -- authored
adjudications for cases the scorer fix newly surfaced (currently only
EA0114 carbamazepine-400/2, whose form flipped from spurious-FP to missed-FN
under the CUI-unification + clause-scope fixes; it inherits the clinical
logic of old case 24, ``MODEL_DEFENSIBLE``/``scorer_mechanics_artifact``).

Usage: uv run python experiments/exectv2_ledger/finalize_rx_inv_canonical.py
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

_EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from exectv2_ledger.mechanism import MECHANISM_VALUES  # noqa: E402
from exectv2_ledger.schema import GoldCaseRow, write_gold_case_ledger  # noqa: E402

ROOT = _EXPERIMENTS_DIR.parent
RUN_ID = "exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628"
# Commit at which the pre-sweep _cases.json (48 Rx / 31 Inv) was last written,
# i.e. the case set the positional verdict batches were authored against.
PRE_SWEEP_COMMIT = "4def0b73"
_VALID_VERDICTS = {"GOLD_RIGHT", "MODEL_DEFENSIBLE", "BOTH_DEFENSIBLE"}
_VERDICT_MAP = {"GOLD_RIGHT": "gold_right", "MODEL_DEFENSIBLE": "model_defensible", "BOTH_DEFENSIBLE": "both_defensible"}

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


def _content_key(case: dict[str, Any]) -> tuple[str, str, str]:
    """The stable join key: (letter_id, match_key, disagreement_type).

    Robust to the positional case_id renumbering the scorer-correctness sweep
    caused. ``match_key`` is the scored key tuple (repr'd to a string in the
    JSON), which uniquely identifies the disagreement within a letter.
    """
    return (case["letter_id"], case["match_key"], case["disagreement_type"])


def _git_show_json(rel_path: str, commit: str) -> Any:
    """Recover a JSON file from git at ``commit`` (the pre-sweep case set)."""
    result = subprocess.run(
        ["git", "show", f"{commit}:{rel_path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def _load_positional_verdicts(case_dir: Path) -> dict[int, dict]:
    """Load the 4-parallel-reviewer verdict batches keyed by positional case_id."""
    verdicts: dict[int, dict] = {}
    batch_files = sorted(case_dir.glob("_verdicts_batch*.json"))
    if not batch_files:
        raise FileNotFoundError(f"no _verdicts_batch*.json found in {case_dir}")
    for batch_file in batch_files:
        batch = json.loads(batch_file.read_text(encoding="utf-8"))
        for entry in batch:
            case_id = entry["case_id"]
            if case_id in verdicts:
                raise ValueError(
                    f"{case_dir.name}: case_id {case_id} covered by more than one "
                    f"batch (duplicate in {batch_file.name})"
                )
            if entry["verdict"] not in _VALID_VERDICTS:
                raise ValueError(
                    f"{case_dir.name} case_id {case_id}: unrecognized verdict {entry['verdict']!r}"
                )
            if entry["mechanism"] not in MECHANISM_VALUES:
                raise ValueError(
                    f"{case_dir.name} case_id {case_id}: mechanism {entry['mechanism']!r} not in "
                    f"shared taxonomy {sorted(MECHANISM_VALUES)}"
                )
            verdicts[case_id] = entry
    return verdicts


def _build_content_verdict_map(case_dir: Path, entity: str) -> dict[tuple[str, str, str], dict]:
    """Bridge positional verdicts to content keys via the pre-sweep ``_cases.json``.

    The verdict batches carry only positional case_id; the pre-sweep case set
    (recovered from git at ``PRE_SWEEP_COMMIT``) maps those case_ids to
    (letter_id, match_key, disagreement_type). Joining them yields a
    content-keyed verdict map that survives the post-sweep renumbering.
    """
    rel = f"docs/research/error_analysis/{case_dir.name}/_cases.json"
    pre_sweep_cases = _git_show_json(rel, PRE_SWEEP_COMMIT)
    positional = _load_positional_verdicts(case_dir)
    content_map: dict[tuple[str, str, str], dict] = {}
    for case in pre_sweep_cases:
        verdict = positional.get(case["case_id"])
        if verdict is not None:
            content_map[_content_key(case)] = verdict
    return content_map


def _load_new_case_verdicts(case_dir: Path) -> dict[tuple[str, str, str], dict]:
    """Load authored verdicts for genuinely-new disagreements.

    Sourced from ``_new_case_verdicts.json`` (keyed by content_key repr). These
    cover cases the scorer-correctness sweep newly surfaced whose content key
    does not exist in the pre-sweep case set (currently only EA0114, whose form
    flipped from spurious-FP to missed-FN under CUI-unification + clause-scope).
    """
    path = case_dir / "_new_case_verdicts.json"
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[tuple[str, str, str], dict] = {}
    for key_str, entry in raw.items():
        key = tuple(json.loads(key_str))
        if entry["verdict"] not in _VALID_VERDICTS:
            raise ValueError(f"{path.name}: unrecognized verdict {entry['verdict']!r}")
        if entry["mechanism"] not in MECHANISM_VALUES:
            raise ValueError(
                f"{path.name}: mechanism {entry['mechanism']!r} not in taxonomy"
            )
        out[key] = entry  # type: ignore[assignment]
    return out


def finalize_family(entity: str) -> None:
    config = _FAMILY_CONFIG[entity]
    case_dir: Path = config["case_dir"]
    cases = json.loads((case_dir / "_cases.json").read_text(encoding="utf-8"))

    content_verdicts = _build_content_verdict_map(case_dir, entity)
    new_verdicts = _load_new_case_verdicts(case_dir)

    csv_rows = []
    ledger_rows: list[GoldCaseRow] = []
    unresolved: list[str] = []

    for case in cases:
        key = _content_key(case)
        verdict = content_verdicts.get(key) or new_verdicts.get(key)
        if verdict is None:
            unresolved.append(f"{case['letter_id']} {case['match_key']} {case['disagreement_type']}")
            continue
        csv_rows.append({
            "entity": entity,
            "letter_id": case["letter_id"],
            "case_id": case["case_id"],
            "disagreement_type": case["disagreement_type"],
            "match_key": case["match_key"],
            "verdict": verdict["verdict"],
            "mechanism": verdict["mechanism"],
            "reason": verdict["reason"],
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
            row_id=f"{config['row_prefix']}:{RUN_ID}:{case['letter_id']}:{case['disagreement_type']}:case{case['case_id']}",
            family=entity,
            run_id=RUN_ID,
            letter_id=case["letter_id"],
            disagreement_type=case["disagreement_type"],
            match_key=case["match_key"],
            source_letter_text=case["source_letter_text"],
            gold=gold_record,
            pred=pred_record,
            mechanism=verdict["mechanism"],
            verdict=_VERDICT_MAP[verdict["verdict"]],
            provenance={
                "adjudicated_by": "4 parallel general-purpose agents, 2026-07-02 canonical row adjudication",
                "adjudicated_at": "2026-07-02",
                "hypothesis_id": None,
                "reason": verdict["reason"],
            },
        ))

    if unresolved:
        raise ValueError(
            f"{entity}: {len(unresolved)} case(s) have no verdict under content-key or "
            f"new-case-verdicts:\n  " + "\n  ".join(unresolved)
        )

    csv_path = case_dir / "_adjudication.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["entity", "letter_id", "case_id", "disagreement_type",
                                                      "match_key", "verdict", "mechanism", "reason"])
        writer.writeheader()
        writer.writerows(csv_rows)

    write_gold_case_ledger(ledger_rows, config["ledger_out"])

    n = len(cases)
    verdict_counts: dict[str, int] = {}
    mechanism_counts: dict[str, int] = {}
    for row in csv_rows:
        verdict_counts[row["verdict"]] = verdict_counts.get(row["verdict"], 0) + 1
        mechanism_counts[row["mechanism"]] = mechanism_counts.get(row["mechanism"], 0) + 1
    genuine = mechanism_counts.get("genuine_model_error", 0)
    bridge_recovered = sum(1 for c in cases if _content_key(c) in content_verdicts)
    new_sourced = sum(1 for c in cases if _content_key(c) in new_verdicts)

    print(f"=== {entity} finalized: {n} cases ===")
    print(f"  verdicts: {verdict_counts}")
    print(f"  mechanisms: {mechanism_counts}")
    print(f"  genuine_model_error share: {genuine}/{n} = {genuine/n:.1%}")
    print(f"  content-bridge recovered: {bridge_recovered} | new-case-verdicts sourced: {new_sourced}")
    print(f"  -> {csv_path.relative_to(ROOT)}")
    print(f"  -> {config['ledger_out'].relative_to(ROOT)}\n")


def main() -> None:
    for entity in _FAMILY_CONFIG:
        finalize_family(entity)


if __name__ == "__main__":
    main()
