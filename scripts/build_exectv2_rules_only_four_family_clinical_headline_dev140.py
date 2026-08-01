"""Phase B: rules-only four-family clinical_headline on ExECT dev140.

Protocol:
docs/experiments/exectv2/reliability/
exectv2_primary_method_comparison_surface_protocol_2026-08-01.md

Uses Sol-matched assembly headline_target via build_scoring_views on
all-nine deterministic predictions restricted to the four key families.
No model calls.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    build_scoring_views,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/experiments/exectv2/reliability/"
    "exectv2_primary_method_comparison_surface_protocol_2026-08-01.md"
)
OUT_JSON = (
    REPO_ROOT
    / "experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json"
)
OUT_MD = (
    REPO_ROOT
    / "docs/experiments/exectv2/reliability/"
    / "exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-01.md"
)


def main() -> None:
    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, got {len(gold)}")

    all9 = tuple(
        run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=False,
            include_diagnosis_benchmark_residuals=False,
        )
    )
    restricted = tuple(_restrict_to_four_families(letter) for letter in all9)
    dropped = _count_dropped_mentions(all9, restricted)

    _views, score_ladder, _headline = build_scoring_views(
        candidate_name="exectv2_rules_only_four_family_dev140",
        ownership="rules_only_restrict_and_rescore",
        gold_letters=gold,
        raw_predictions=restricted,
        scored_predictions=restricted,
    )
    headline = score_ladder["headline_target"]
    overall = headline["overall"]
    by_family = {
        family: {
            "f1": float(values["f1"]),
            "precision": float(values["precision"]),
            "recall": float(values["recall"]),
        }
        for family, values in headline["by_indicator"].items()
    }
    if set(by_family) != set(TARGET_INDICATORS):
        raise ValueError(f"unexpected families in headline: {sorted(by_family)}")

    payload: dict[str, Any] = {
        "schema_version": "exectv2.rules_only_four_family_clinical_headline.dev140.v1",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0046-exect-primary-method-comparison-boundary.md",
        "generated_on": date.today().isoformat(),
        "split": "dev140",
        "split_loader": "dev",
        "row_count": len(gold),
        "row_policy": "dev140_rows_permitted_test60_forbidden",
        "method": {
            "pipeline": "deterministic_all9",
            "scoring": "assembly_headline_target",
            "production_rule": "restrict_and_rescore",
            "include_diagnosis_resolution_candidate": False,
            "include_diagnosis_benchmark_residuals": False,
            "scored_families": list(TARGET_INDICATORS),
            "non_key_entities_excluded_from_peer_score_only": True,
        },
        "clinical_headline": {
            "f1": float(overall["f1"]),
            "precision": float(overall["precision"]),
            "recall": float(overall["recall"]),
        },
        "clinical_headline_by_family": by_family,
        "mention_accounting": dropped,
        "claim_boundary": (
            "Development rules-only four-family clinical_headline on ExECT "
            "dev140 for decision 0046. Sol-matched assembly headline_target "
            "on all-nine deterministic predictions with non-key entities "
            "excluded from the peer score only. Not nine-entity published "
            "metrics, not clinical_recovery_scorecard overall, not holdout "
            "evidence, and not clinical validation."
        ),
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(_render_markdown(payload), encoding="utf-8")
    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(
        f"overall F1={payload['clinical_headline']['f1']:.4f} "
        f"dropped_mentions={dropped['dropped_non_key_mentions']}"
    )


def _restrict_to_four_families(letter: PredictedLetter) -> PredictedLetter:
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(m for m in letter.mentions if m.entity in TARGET_INDICATORS),
    )


def _count_dropped_mentions(
    all9: tuple[PredictedLetter, ...],
    restricted: tuple[PredictedLetter, ...],
) -> dict[str, int]:
    before = sum(len(letter.mentions) for letter in all9)
    after = sum(len(letter.mentions) for letter in restricted)
    return {
        "all9_mentions": before,
        "four_family_mentions": after,
        "dropped_non_key_mentions": before - after,
    }


def _render_markdown(payload: dict[str, Any]) -> str:
    overall = payload["clinical_headline"]
    lines = [
        "# ExECTv2 rules-only four-family clinical_headline (dev140)",
        "",
        f"Date: {payload['generated_on']}",
        "Status: complete; Phase B of the 0046 evidence protocol",
        "Row policy: development (`dev140`)",
        "",
        "Protocol: "
        "[primary method-comparison surface protocol]"
        "(exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)",
        "",
        "Decision: "
        "[0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)",
        "",
        "Machine artifact: "
        "[JSON](../../../experiments/"
        "exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json)",
        "",
        "## Question",
        "",
        "What is rules-only four-family `clinical_headline` F1 on `dev140` "
        "under the Sol-matched assembly `headline_target` surface?",
        "",
        "## Result",
        "",
        f"| Overall clinical_headline F1 | {overall['f1']:.4f} |",
        f"| Precision | {overall['precision']:.4f} |",
        f"| Recall | {overall['recall']:.4f} |",
        "",
        "| Family | F1 | Precision | Recall |",
        "| --- | ---: | ---: | ---: |",
    ]
    for family in TARGET_INDICATORS:
        values = payload["clinical_headline_by_family"][family]
        lines.append(
            f"| {family} | {values['f1']:.4f} | "
            f"{values['precision']:.4f} | {values['recall']:.4f} |"
        )
    accounting = payload["mention_accounting"]
    lines.extend(
        [
            "",
            "## Method",
            "",
            "- Pipeline: deterministic all-nine (`run_all9_on_letters`, "
            "diagnosis resolution candidate and benchmark residuals off).",
            "- Production rule: restrict-and-rescore to Diagnosis, "
            "Seizure Frequency, Prescription, and Investigations.",
            "- Scorer: assembly `headline_target` via `build_scoring_views` "
            "(same surface as Sol hybrid cells).",
            f"- Mentions: {accounting['all9_mentions']} all-nine → "
            f"{accounting['four_family_mentions']} four-family "
            f"({accounting['dropped_non_key_mentions']} non-key excluded "
            "from this peer score only).",
            "",
            "## Claim boundary",
            "",
            str(payload["claim_boundary"]),
            "",
            "## Next action",
            "",
            "Phase C of the same protocol: aggregate-only rules-only "
            "four-family `clinical_headline` on `test60`.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
