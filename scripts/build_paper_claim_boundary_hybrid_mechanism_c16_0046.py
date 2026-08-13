#!/usr/bin/env python3
"""Package paper claim-boundary wording against C16 / Decision 0046.

No model calls. No score-fill rewrite. See
docs/research/shared/paper_claim_boundary_hybrid_mechanism_c16_0046_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def build_artifact() -> dict[str, Any]:
    return {
        "artifact_id": "paper.claim_boundary.hybrid_mechanism_c16_0046.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/shared/paper_claim_boundary_hybrid_mechanism_c16_0046_"
            "protocol_2026-08-06.md"
        ),
        "git": _git_note(),
        "preserved_primary_claims": {
            "C16": {
                "owner": "docs/canon/10_paper_provenance.md",
                "owns": (
                    "Gan final 2026-07-31 hybrid_full_stack no-call Purist fills "
                    "on saved raws (dev750 + aggregate test450)"
                ),
                "score_fill_changed_by_this_study": False,
            },
            "C17_decision_0046": {
                "owners": [
                    "docs/canon/10_paper_provenance.md",
                    "docs/decisions/0046-exect-primary-method-comparison-boundary.md",
                ],
                "owns": (
                    "ExECT Sol-matched primary three-method clinical-fact fills "
                    "(rules / llm raw_lane / llm_with_rules) on dev140 and "
                    "aggregate-only test60"
                ),
                "score_fill_changed_by_this_study": False,
            },
        },
        "companion_claims_recommended": [
            {
                "proposed_id": "C18",
                "claim": (
                    "On retained Gan and ExECT development hybrid surfaces, "
                    "named deterministic stages account for the bulk of first "
                    "label or inventory changes under ordered no-call replay: "
                    "Gan evidence reconcile (selected_evidence); ExECT Diagnosis "
                    "lens and SeizureFrequency project_and_gate."
                ),
                "strength": "Bounded development answer",
                "evidence_limit": (
                    "First-changer attribution on development ledgers only; "
                    "not leave-one-stage-out necessity; not holdout "
                    "generalization; does not rewrite C16 or Decision 0046 fills."
                ),
                "evidence_owners": [
                    "docs/research/gan2026/gan2026_hybrid_stage_ablation_2026-08-06.md",
                    "docs/research/exectv2/exectv2_hybrid_stage_ablation_2026-08-06.md",
                    "docs/research/shared/cross_task_hybrid_mechanism_synthesis_2026-08-06.md",
                ],
                "recommendation": "accept_into_canon",
            },
            {
                "proposed_id": "C19",
                "claim": (
                    "Some hybrid deterministic stages can harm development "
                    "correctness on named slices: Gan repair.breakthrough on "
                    "unknown gold recovers under leave-one-family-out but costs "
                    "full-ledger Purist; ExECT Prescription lens raises letter "
                    "exactness without improving mean Prescription F1."
                ),
                "strength": "Bounded development residual evidence",
                "evidence_limit": (
                    "Development residual / counterfactual studies only; "
                    "production rewrite not authorized; not holdout; does not "
                    "change Decision 0046 or C16 headlines."
                ),
                "evidence_owners": [
                    "docs/research/gan2026/gan2026_unknown_sentinel_clinical_harm_2026-08-06.md",
                    "docs/research/gan2026/gan2026_unknown_breakthrough_loo_2026-08-06.md",
                    "docs/research/exectv2/exectv2_prescription_lens_counterfactual_2026-08-06.md",
                ],
                "recommendation": "accept_into_canon",
            },
        ],
        "allowed_paper_wording": [
            {
                "id": "A1",
                "text": (
                    "Hybrid competence on the retained development surfaces is "
                    "attributable to named deterministic stages, not an "
                    "undifferentiated rules blob."
                ),
                "strength": "development_answer",
                "maps_to": ["C18"],
            },
            {
                "id": "A2",
                "text": (
                    "On Gan, rules create easy mass in seizure-free, range, and "
                    "no-reference buckets and lift ordinary point rates out of "
                    "the llm-only floor; clusters remain the practical floor; "
                    "unknown is not a clean hybrid rescue."
                ),
                "strength": "development_answer",
                "maps_to": ["category_cut", "C18"],
            },
            {
                "id": "A3",
                "text": (
                    "On ExECT, rules rescue Diagnosis inventory and partially "
                    "trim SeizureFrequency; Prescription becomes common "
                    "competence on development hybrid but does not remain "
                    "strict x on aggregate test60 family lenses; "
                    "SeizureFrequency remains the practical floor."
                ),
                "strength": "development_answer_plus_aggregate_holdout_family",
                "maps_to": ["category_cut", "holdout_family", "C18"],
            },
            {
                "id": "A4",
                "text": (
                    "Some deterministic hybrid stages can harm named "
                    "development slices; first-changer harm is not by itself a "
                    "license to disable a stage in the selected pipeline."
                ),
                "strength": "development_answer",
                "maps_to": ["C19"],
            },
            {
                "id": "A5",
                "text": (
                    "Primary paper score tables remain C16 for Gan final "
                    "llm_with_rules fills and Decision 0046 / C17 for ExECT "
                    "Sol-matched three-method fills."
                ),
                "strength": "canon_preserving",
                "maps_to": ["C16", "C17"],
            },
        ],
        "forbidden_paper_wording": [
            {
                "id": "F1",
                "text": (
                    "Do not say the 2026-08-06 ladder revises C16 Purist fills "
                    "or Decision 0046 primary method numbers."
                ),
            },
            {
                "id": "F2",
                "text": (
                    "Do not claim leave-one-stage-out necessity from "
                    "first-changer attribution alone."
                ),
            },
            {
                "id": "F3",
                "text": (
                    "Do not claim that disabling repair.breakthrough or the "
                    "Prescription lens would raise C16 or Decision 0046 "
                    "headlines."
                ),
            },
            {
                "id": "F4",
                "text": (
                    "Do not treat development category/stage effects as sealed "
                    "holdout row competence; Gan a_priori holdout bucket scores "
                    "remain blocked without sealed ledgers."
                ),
            },
            {
                "id": "F5",
                "text": (
                    "Do not numerically rank Gan Purist against ExECT clinical "
                    "fact F1, or claim cross-task reliability transfer."
                ),
            },
            {
                "id": "F6",
                "text": (
                    "Do not present clinical fact recovery as the published "
                    "ExECT benchmark, or present these studies as clinical "
                    "validation."
                ),
            },
            {
                "id": "F7",
                "text": (
                    "Do not reopen v08, GEPA, or nine-entity rules-only metrics "
                    "as primary ExECT method peers."
                ),
            },
        ],
        "paste_ready_manuscript_paragraphs": [
            {
                "section_hint": "Results / mechanism (development)",
                "text": (
                    "On retained development surfaces, LLM-with-rules is not a "
                    "single polish step. Ordered no-call replay attributes most "
                    "first hybrid changes to named deterministic stages: evidence "
                    "reconcile on Gan, and Diagnosis lens plus SeizureFrequency "
                    "projection/gating on ExECT. Category cuts show that rules "
                    "create Gan easy mass and promote ExECT Diagnosis and "
                    "Prescription, while clusters and SeizureFrequency remain "
                    "practical floors."
                ),
            },
            {
                "section_hint": "Discussion / limits",
                "text": (
                    "These mechanism readings are development attributions under "
                    "ordered replay. They do not revise the paper’s primary score "
                    "fills—Gan’s finalized 2026-07-31 llm_with_rules no-call "
                    "Purist panel (C16) and ExECT’s Sol-matched three-method "
                    "clinical-fact comparison (Decision 0046 / C17). Residual "
                    "studies show that some stages can harm named slices "
                    "(unknown-gold breakthrough; Prescription lens), but "
                    "leave-one-family-out and lens counterfactuals do not "
                    "authorize changing the selected pipeline from this evidence "
                    "alone. Aggregate test60 family lenses support SeizureFrequency "
                    "as a holdout floor; Gan per-bucket holdout scores remain "
                    "unavailable without sealed ledgers."
                ),
            },
        ],
        "decision": {
            "label": "package_companion_claims_preserve_primary_fills",
            "summary": (
                "Preserve C16 and Decision 0046 / C17 score ownership. Accept "
                "bounded companion claims C18 (stage attribution) and C19 "
                "(named hybrid harm residuals) into paper provenance."
            ),
            "primary_fills_rewritten": False,
            "canon_update": "add_C18_C19",
        },
        "claim_boundary": (
            "Paper claim-boundary packaging from the 2026-08-06 hybrid mechanism "
            "ladder. Not a C16 or Decision 0046 score rewrite. Not clinical "
            "validation. Not a repair or lens authorization."
        ),
    }


def write_report(artifact: dict[str, Any]) -> str:
    decision = artifact["decision"]
    lines = [
        "# Paper claim-boundary packaging: hybrid mechanism vs C16 / Decision 0046",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: packaging complete; primary score fills preserved  ",
        "Protocol: [claim-boundary packaging protocol]"
        "(paper_claim_boundary_hybrid_mechanism_c16_0046_protocol_2026-08-06.md)  ",
        "Canon owner: [paper provenance](../canon/10_paper_provenance.md)  ",
        "Decision owner: [Decision 0046]"
        "(../decisions/0046-exect-primary-method-comparison-boundary.md)  ",
        "Parent: [cross-task hybrid mechanism synthesis]"
        "(cross_task_hybrid_mechanism_synthesis_2026-08-06.md)  ",
        "Artifact: "
        f"[`experiments/paper_claim_boundary_hybrid_mechanism_c16_0046_{DATE_STAMP}.json`]"
        f"(../../experiments/paper_claim_boundary_hybrid_mechanism_c16_0046_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        decision["summary"],
        "",
        "**Primary fills rewritten:** no.",
        "",
        "## What the primary claims already own",
        "",
        "| Claim | Owns | This study |",
        "| --- | --- | --- |",
        (
            "| **C16** | Gan final 2026-07-31 `hybrid_full_stack` no-call "
            "Purist fills (dev750 + aggregate test450) | unchanged |"
        ),
        (
            "| **C17 / Decision 0046** | ExECT Sol-matched rules / llm "
            "`raw_lane` / llm_with_rules clinical-fact fills (dev140 + "
            "aggregate test60) | unchanged |"
        ),
        "",
        "Mechanism language from the 2026-08-06 ladder is **companion "
        "interpretation**, not a substitute primary table.",
        "",
        "## Recommended companion claims",
        "",
    ]
    for claim in artifact["companion_claims_recommended"]:
        lines.extend(
            [
                f"### {claim['proposed_id']}",
                "",
                claim["claim"],
                "",
                f"- **Strength:** {claim['strength']}",
                f"- **Evidence limit:** {claim['evidence_limit']}",
                "- **Owners:** "
                + "; ".join(f"`{path}`" for path in claim["evidence_owners"]),
                f"- **Recommendation:** `{claim['recommendation']}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Allowed paper wording",
            "",
        ]
    )
    for row in artifact["allowed_paper_wording"]:
        lines.append(f"- **{row['id']}** ({row['strength']}): {row['text']}")

    lines.extend(
        [
            "",
            "## Forbidden upgrades",
            "",
        ]
    )
    for row in artifact["forbidden_paper_wording"]:
        lines.append(f"- **{row['id']}:** {row['text']}")

    lines.extend(
        [
            "",
            "## Paste-ready manuscript paragraphs",
            "",
        ]
    )
    for para in artifact["paste_ready_manuscript_paragraphs"]:
        lines.extend(
            [
                f"### {para['section_hint']}",
                "",
                para["text"],
                "",
            ]
        )

    git = artifact["git"]
    lines.extend(
        [
            "## Decision",
            "",
            decision["summary"],
            "",
            "Update `docs/canon/10_paper_provenance.md` with C18 and C19. Do not "
            "edit Decision 0046 fills or C16 headline numbers from this page.",
            "",
            "## Next",
            "",
            "1. Keep manuscript primary tables on C16 / Decision 0046 ownership.",
            "2. Optionally paste the mechanism / limits paragraphs into the "
            "working manuscript in a later editing pass.",
            "3. Operational primary remains the vLLM dev10 task.",
            "",
            "## Method",
            "",
            "- No new model calls; packaging over retained 2026-08-06 ladder.",
            f"- Git: `{git.get('commit')}` "
            f"({'dirty tree' if git.get('dirty_tree') else 'clean'}).",
            "",
            "## Claim boundary",
            "",
            artifact["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT
        / f"experiments/paper_claim_boundary_hybrid_mechanism_c16_0046_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / (
            "docs/research/shared/paper_claim_boundary_hybrid_mechanism_c16_0046_"
            f"{REPORT_DATE}.md"
        ),
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n")
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(write_report(artifact))
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    print(artifact["decision"]["label"])


if __name__ == "__main__":
    main()
