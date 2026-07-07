"""P0.6 — Safety-property table (Safety & compliance, reframed: fail-closed + research integrity).

Reliability scorecard, Phase 0 (zero model budget). Collates the project's
fail-closed and research-integrity properties into one table. Where a number is
recomputable from frozen artifacts it is recomputed and tagged `recomputed`;
governance facts are tagged `code-enforced` with their source file; documented
selective-floor results are tagged with their comparator layer.

Includes the explicit out-of-scope finding: synthetic templated letters make
PHI-leakage and demographic-bias evals N/A, and they would require real-letter
validation before any deployment claim.

No model calls.

Usage:
    uv run python experiments/build_gan2026_reliability_p0_6_safety_table.py
"""

from __future__ import annotations

import collections
import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p0_6_safety_table_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p0_6_safety_table_2026-06-17.md"


def transition_floor(path) -> dict[str, Any]:
    rows = rc.load_jsonl(path)
    t = collections.Counter(
        (r.get("transition_vs_v0") or {}).get("purist_transition") for r in rows
    )
    changed = sum(1 for r in rows if (r.get("transition_vs_v0") or {}).get("label_changed"))
    return {
        "rows": len(rows),
        "changed": changed,
        "wrong_to_correct": t.get("wrong_to_correct", 0),
        "correct_to_wrong": t.get("correct_to_wrong", 0),
    }


def main() -> None:
    val = transition_floor(rc.REASONER_VALIDATION750)
    test = transition_floor(rc.REASONER_TEST450)

    properties = [
        {
            "property": "No-regression safety floor (selective gated action)",
            "status": "code-enforced + documented",
            "layer": "[comparator: hybrid-adjudicator] RQ6/rq9 selective intervention",
            "evidence": (
                "RQ6 selective gated action: validation750 21 changed, 11 W->C, 0 C->W "
                "(precision 1.000); frozen test450 14 changed, 8 W->C, 0 C->W. The "
                "selective layer never converts a correct row to wrong."
            ),
        },
        {
            "property": "Unconstrained replace mechanism DOES regress (why the floor matters)",
            "status": "recomputed",
            "layer": "[comparator: V12-full-gpt4.1] reasoner final vs v0_reference",
            "evidence": (
                f"validation750: {val['changed']} changed, {val['wrong_to_correct']} W->C, "
                f"{val['correct_to_wrong']} C->W; test450: {test['changed']} changed, "
                f"{test['wrong_to_correct']} W->C, {test['correct_to_wrong']} C->W. The "
                "full replace path trades regressions for coverage, so the production "
                "go-forward is the un-replaced single-SE subject (the floor itself)."
            ),
        },
        {
            "property": "Abstain-to-unknown policy",
            "status": "code-enforced",
            "layer": "subject + selective",
            "evidence": (
                "SAFETY_GATE_VERSION = 'gan2026_fresh_evidence_safety_gate_v0_9' "
                "(fresh_evidence_reasoner.py:70); the gate withholds to unknown rather "
                "than emit an unsupported rate."
            ),
        },
        {
            "property": "Contamination canaries + hash/version pinning",
            "status": "code-enforced",
            "layer": "governance",
            "evidence": (
                "frozen_test_preflight.py pins EXPECTED_SPLIT_MANIFEST='gan2026_split_v1', "
                "EXPECTED_TEST_ROW_COUNT=450, and verifies SHA-256 protocol hashes "
                "(_check_protocol_hashes) before any holdout run is permitted."
            ),
        },
        {
            "property": "Aggregate-only readout guard (no row-level test inspection)",
            "status": "code-enforced",
            "layer": "governance",
            "evidence": (
                "frozen_test_readout.py refuses any report containing forbidden markers "
                "(source_row_index, transition_vs_v0, score_layers) and requires the "
                "aggregate-only marker + a 450-row count check."
            ),
        },
        {
            "property": "Operational fail-closed integrity",
            "status": "recomputed elsewhere (P0.7)",
            "layer": "subject",
            "evidence": "0 parse failures / 0 evidence loss / source ids 1.000 across 2,295 rows.",
        },
    ]

    out_of_scope = {
        "finding": "PHI-leakage and demographic-bias evals are N/A on this benchmark",
        "reason": (
            "The Gan rows are synthetic templated letters with no real PHI and no "
            "reliable demographic signal, so jailbreak/PII/subgroup-demographic safety "
            "cannot be measured here. Clinical-family parity (P0.5) is the available "
            "fairness axis. Real-letter validation would be required before any "
            "deployment-grade PHI or demographic-fairness claim."
        ),
    }

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p0_6_safety_table",
        "date": "2026-06-17",
        "dimensions": ["Safety & compliance"],
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_VALIDATION750, rc.REASONER_TEST450],
        ),
        "safety_properties": properties,
        "out_of_scope": out_of_scope,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(
        f"  V12 reasoner C->W: validation {val['correct_to_wrong']}, test {test['correct_to_wrong']}"
    )
    print("  selective floor: 0 C->W (cited RQ6)")


def render_md(result: dict[str, Any]) -> str:
    L: list[str] = []
    L.append("# P0.6 — Safety-Property Table (fail-closed + research integrity)\n")
    L.append(f"Date: {result['date']}  ·  Model calls: 0\n")
    L.append("| Property | Status | Layer | Evidence |")
    L.append("|---|---|---|---|")
    for p in result["safety_properties"]:
        L.append(f"| {p['property']} | {p['status']} | {p['layer']} | {p['evidence']} |")
    oos = result["out_of_scope"]
    L.append(f"\n## Out of scope (stated finding)\n\n**{oos['finding']}.** {oos['reason']}\n")
    L.append("---\n")
    L.append(
        "**Reading.** Safety here is fail-closed extraction + research integrity, and it "
        "is code-enforced rather than aspirational: the selective layer holds a 0 C→W "
        "floor while the unconstrained replace path measurably regresses, which is exactly "
        "why the simpler subject is the go-forward. The contamination canaries, hash "
        "pinning, and aggregate-only readout guard are what make every holdout number in "
        "this scorecard trustworthy.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
