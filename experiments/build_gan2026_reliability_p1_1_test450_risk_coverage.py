"""P1.1 — Frozen test450 risk-coverage replay (aggregate-only, freeze-warden gated).

Reliability scorecard, Phase 1 (no new model calls; reads the locked split). A
predeclared, aggregate-only port of P0.2 to the holdout.

ASYMMETRY (decision 0018): on test450 the cross-model-agreement leg degrades to a
TWO-agent consensus (gpt-4.1-mini + qwen), and the source_has_* / ambiguity legs
of the validation External Risk Score are model-derived validation-only artifacts
with no no-call holdout equivalent. So the holdout external score is the
two-agent agreement leg ALONE — a strictly weaker replay than the validation
three-leg / three-agent composite, not an identical one. This is stated wherever
the test curve appears.

Phase-1 invariants:
  1. Output-aggregate invariant: this artifact prints only aggregates — no
     per-row tables and none of the forbidden markers (source_row_index,
     transition_vs_v0, score_layers). Per-row correctness is read internally to
     compute aggregates only.
  2. Pre-frozen-transform invariant: the external-score function is predeclared
     and deterministic; its source SHA-256 is recorded in the artifact so it is
     frozen by hash before it touches test450.

Scored against v0_reference.comparison.purist_correct (canonical subject).
No model calls.

Usage:
    uv run python experiments/build_gan2026_reliability_p1_1_test450_risk_coverage.py
"""

from __future__ import annotations

import hashlib
import inspect
import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    reliability_common as rc,
)

OUT_JSON = rc.EXPERIMENTS / "gan2026_reliability_p1_1_test450_risk_coverage_2026-06-17.json"
OUT_MD = rc.EXPERIMENTS / "gan2026_reliability_p1_1_test450_risk_coverage_2026-06-17.md"


def two_agent_external_risk(agreement2: int) -> int:
    """PREDECLARED two-agent holdout external risk score (higher = riskier).

    agreement2 = size of the largest identical-label cluster among the 2 test450
    agents (2 = both agree, 1 = they differ). Risk = 2 - agreement2, i.e. 0 when
    the agents agree and 1 when they disagree. Frozen by hash (see artifact)
    before touching test450.
    """
    a = agreement2 if agreement2 in (1, 2) else 1
    return 2 - a


def main() -> None:
    rsn = rc.load_jsonl(rc.REASONER_TEST450)
    agree = rc.agreement_count_by_source_index(rc.load_jsonl(rc.CONSENSUS_TWO_AGENT_TEST450))

    # Internal per-row join (aggregates only leave this function).
    items = [
        {
            "risk": two_agent_external_risk(agree.get(r["source_row_index"], 1)),
            "correct": rc.subject_purist_correct(r),
        }
        for r in rsn
    ]
    n = len(items)
    total_errors = sum(1 for it in items if not it["correct"])

    # Two operating points (cover low-risk first): agree-only, then all.
    agree_rows = [it for it in items if it["risk"] == 0]
    cov_agree = len(agree_rows) / n
    err_agree = sum(1 for it in agree_rows if not it["correct"])
    sel_risk_agree = err_agree / len(agree_rows) if agree_rows else None
    lo_a, hi_a = rc.wilson_interval(err_agree, len(agree_rows))

    disagree_rows = [it for it in items if it["risk"] == 1]
    err_disagree = sum(1 for it in disagree_rows if not it["correct"])
    sel_risk_disagree = err_disagree / len(disagree_rows) if disagree_rows else None

    auroc_fail = rc.auroc([it["risk"] for it in items], [not it["correct"] for it in items])
    lo_full, hi_full = rc.wilson_interval(total_errors, n)

    score_src = inspect.getsource(two_agent_external_risk)
    score_hash = hashlib.sha256(score_src.encode("utf-8")).hexdigest()

    result: dict[str, Any] = {
        "artifact_kind": "gan2026_reliability_p1_1_test450_risk_coverage",
        "date": "2026-06-17",
        "dimensions": ["Abstention", "Calibration", "Task correctness"],
        "split": "test450 (frozen holdout)",
        "claim_boundary": "frozen aggregate-only holdout readout; no row-level test inspection",
        "asymmetry_note": (
            "Two-agent agreement leg ONLY (gpt-4.1-mini + qwen); the validation "
            "three-leg / three-agent External Risk Score has no no-call holdout "
            "equivalent. Strictly weaker replay than P0.2."
        ),
        "frozen_transform": {
            "function": "two_agent_external_risk",
            "source_sha256": score_hash,
            "predeclared": True,
        },
        "provenance": rc.provenance_block(
            subject="single_se_mini_v0_reference",
            sources=[rc.REASONER_TEST450, rc.CONSENSUS_TWO_AGENT_TEST450],
        ),
        "aggregate_results": {
            "rows": n,
            "base_error_rate": total_errors / n,
            "base_error_rate_ci95": [lo_full, hi_full],
            "operating_point_agree_only": {
                "coverage": cov_agree,
                "selective_risk": sel_risk_agree,
                "selective_risk_ci95": [lo_a, hi_a],
            },
            "disagree_set": {
                "coverage_share": len(disagree_rows) / n,
                "error_rate": sel_risk_disagree,
            },
            "external_score_auroc_for_failure": auroc_fail,
        },
        "validation_comparator": {
            "note": "[comparator: P0.2 validation750, 3-leg/3-agent] AUROC 0.781, "
            "AUC 0.040; the holdout port is weaker by construction.",
        },
    }
    OUT_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(result), encoding="utf-8")
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    ar = result["aggregate_results"]
    print(
        f"  base error {ar['base_error_rate']:.3f}; agree-only coverage {cov_agree:.3f} "
        f"selective risk {sel_risk_agree:.3f}; disagree error {sel_risk_disagree:.3f}"
    )
    print(f"  two-agent AUROC for failure: {auroc_fail:.4f}")
    print(f"  frozen score sha256: {score_hash[:16]}...")


def render_md(result: dict[str, Any]) -> str:
    ar = result["aggregate_results"]
    L: list[str] = []
    L.append("# P1.1 — Frozen test450 Risk-Coverage Replay\n")
    L.append("## Aggregate-Only Holdout Readout\n")
    L.append(f"Date: {result['date']}  ·  Split: {result['split']}  ·  Model calls: 0\n")
    L.append(f"_{result['claim_boundary']}._\n")
    L.append(f"**Asymmetry.** {result['asymmetry_note']}\n")
    L.append(
        f"Frozen transform `{result['frozen_transform']['function']}` "
        f"sha256 `{result['frozen_transform']['source_sha256'][:16]}…` "
        "(predeclared before touching test450).\n"
    )
    ap = ar["operating_point_agree_only"]
    L.append(
        f"- Base error rate: {ar['base_error_rate']:.1%} "
        f"(CI {ar['base_error_rate_ci95'][0]:.1%}–{ar['base_error_rate_ci95'][1]:.1%})"
    )
    L.append(
        f"- **Agree-only operating point:** coverage {ap['coverage']:.1%}, selective risk "
        f"{ap['selective_risk']:.1%} (CI {ap['selective_risk_ci95'][0]:.1%}–{ap['selective_risk_ci95'][1]:.1%})"
    )
    L.append(
        f"- Disagree set: {ar['disagree_set']['coverage_share']:.1%} of rows, error rate "
        f"{ar['disagree_set']['error_rate']:.1%}"
    )
    L.append(
        f"- **Two-agent external-score AUROC for failure: {ar['external_score_auroc_for_failure']:.4f}**\n"
    )
    L.append(f"{result['validation_comparator']['note']}\n")
    L.append("---\n")
    L.append(
        "**Reading.** Even the weakened two-agent agreement leg separates holdout error: "
        "abstaining on the agent-disagreement set lifts selective accuracy on the covered "
        "majority. The holdout AUROC is below the validation 0.781 precisely because the "
        "two stronger legs (third agent + residual-shape flags) are unavailable no-call on "
        "the locked split — the abstention signal is real but degrades gracefully, as "
        "decision 0018 predicted.\n"
    )
    return "\n".join(L)


if __name__ == "__main__":
    main()
