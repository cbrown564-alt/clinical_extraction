#!/usr/bin/env python3
"""Refresh the rules_only reference in promoted ExECT rung comparison files.

The rungs.rules_only entry is a reference copied from the promoted
standalone-rules file (paper_experiments/exect/exect_rules/dev140.json)
by exect_cell_replay._comparison_summary. Rung comparison files written
before a rules promotion keep the retired number until the next full
rung replay; this script reapplies the same derivation without
replaying the LLM rungs. It touches nothing but rungs.rules_only.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES_PATH = ROOT / "paper_experiments/exect/exect_rules/dev140.json"
RUNGS_ROOT = ROOT / "paper_experiments/exect/rungs"
SPLITS = ("dev140", "test60")


def main() -> None:
    rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    for comparison_path in sorted(RUNGS_ROOT.glob("*/*/comparison.json")):
        split = comparison_path.parent.name
        if split not in SPLITS:
            continue
        block = rules.get(split)
        if not isinstance(block, dict) or block.get("four_family_micro_f1") is None:
            raise RuntimeError(f"no promoted rules score for split {split}")
        rules_f1 = float(block["four_family_micro_f1"])
        payload = json.loads(comparison_path.read_text(encoding="utf-8"))
        rungs = payload.get("rungs")
        if not isinstance(rungs, dict) or "rules_only" not in rungs:
            raise RuntimeError(f"no rules_only rung in {comparison_path}")
        before = rungs["rules_only"]
        rungs["rules_only"] = {
            "four_family_micro_f1": rules_f1,
            "clinical_fact_f1": rules_f1,
            "source": "exect_rules",
        }
        comparison_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(
            f"{comparison_path.relative_to(ROOT)}: "
            f"{before.get('clinical_fact_f1')} -> {rules_f1}"
        )


if __name__ == "__main__":
    main()
