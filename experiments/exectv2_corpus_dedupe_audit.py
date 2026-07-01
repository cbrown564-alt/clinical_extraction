"""Phase 0 of docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md.

Read-only, zero-LLM audit of the ExECTv2 200-letter corpus
(`data/ExECTv2 (2025)/Gold1-200_corrected_spelling/`). Reproduces the 4 known
duplicate-letter pairs disclosed by the source paper (Fonferko-Shadrach et al.
2024: "Four letters were duplicated within the set to test for consistency in
annotations"), confirms which `.ann` pair differs by a trivial offset typo, and
confirms each pair's placement against `exectv2_split_v1.json` (same-side vs.
cross-split).

Usage: uv run python experiments/exectv2_corpus_dedupe_audit.py
"""

from __future__ import annotations

import difflib
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "ExECTv2 (2025)" / "Gold1-200_corrected_spelling"
SPLIT_PATH = ROOT / "data" / "ExECTv2 (2025)" / "splits" / "exectv2_split_v1.json"
OUTPUT_PATH = ROOT / "experiments" / "exectv2_corpus_dedupe_audit.json"


def _md5(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _letter_ids() -> list[str]:
    return sorted({p.stem for p in DATA_DIR.glob("*.txt")})


def _find_duplicate_pairs(letter_ids: list[str], suffix: str) -> dict[str, list[str]]:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for letter_id in letter_ids:
        path = DATA_DIR / f"{letter_id}{suffix}"
        if path.exists():
            by_hash[_md5(path)].append(letter_id)
    return {h: ids for h, ids in by_hash.items() if len(ids) > 1}


def _split_membership(split_manifest: dict) -> dict[str, str]:
    membership: dict[str, str] = {}
    splits = split_manifest.get("splits", {})
    for split_name, split_body in splits.items():
        for letter_id in split_body.get("letter_ids", []):
            membership[letter_id] = split_name
    return membership


def main() -> None:
    letter_ids = _letter_ids()
    assert len(letter_ids) == 200, f"expected 200 letters, found {len(letter_ids)}"

    txt_dupes = _find_duplicate_pairs(letter_ids, ".txt")
    ann_dupes = _find_duplicate_pairs(letter_ids, ".ann")

    split_manifest = json.loads(SPLIT_PATH.read_text(encoding="utf-8"))
    membership = _split_membership(split_manifest)

    pairs_report = []
    for ids in sorted(txt_dupes.values(), key=lambda x: x[0]):
        pair = tuple(sorted(ids))
        ann_identical = any(pair == tuple(sorted(a)) for a in ann_dupes.values())
        a_lines = (DATA_DIR / f"{pair[0]}.ann").read_text(encoding="utf-8").splitlines()
        b_lines = (DATA_DIR / f"{pair[1]}.ann").read_text(encoding="utf-8").splitlines()
        diff_line_count = sum(
            1 for line in difflib.unified_diff(a_lines, b_lines, lineterm="") if line[:1] in "+-"
        )
        splits_for_pair = [membership.get(i, "UNKNOWN") for i in pair]
        pairs_report.append(
            {
                "pair": list(pair),
                "txt_byte_identical": True,
                "ann_byte_identical": ann_identical,
                "ann_diff_line_count": diff_line_count,
                "splits": dict(zip(pair, splits_for_pair, strict=True)),
                "cross_split": len(set(splits_for_pair)) > 1,
            }
        )

    # Pairs whose .txt matches but .ann does NOT (varying degrees; see ann_diff_line_count).
    ann_mismatch_pairs = [p for p in pairs_report if not p["ann_byte_identical"]]

    result = {
        "total_letters": len(letter_ids),
        "txt_duplicate_pair_count": len(txt_dupes),
        "duplicate_letters_total": sum(len(ids) for ids in txt_dupes.values()),
        "pairs": pairs_report,
        "ann_mismatch_pairs": [p["pair"] for p in ann_mismatch_pairs],
        "cross_split_pairs": [p["pair"] for p in pairs_report if p["cross_split"]],
    }

    OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Letters: {result['total_letters']}")
    print(f"Duplicate .txt pairs: {result['txt_duplicate_pair_count']} "
          f"({result['duplicate_letters_total']} letters)")
    for p in pairs_report:
        flag = " <-- CROSS-SPLIT" if p["cross_split"] else ""
        ann_flag = "" if p["ann_byte_identical"] else f" [ANN DIFFERS: {p['ann_diff_line_count']} lines]"
        print(f"  {p['pair']}: {p['splits']}{flag}{ann_flag}")
    print(f"\nWrote {OUTPUT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
