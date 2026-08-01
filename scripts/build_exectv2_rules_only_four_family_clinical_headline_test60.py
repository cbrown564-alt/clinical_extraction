"""Phase C: aggregate-only rules-only four-family clinical_headline on test60.

Protocol:
docs/experiments/exectv2/reliability/
exectv2_primary_method_comparison_surface_protocol_2026-08-01.md

Public experiments/ artifact is aggregate-only. Optional sealed predictions
remain under ignored scratch/holdout. No model calls.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    build_scoring_views,
    mention_to_dict,
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
SEALED_ROOT = (
    REPO_ROOT / "scratch/holdout/exectv2_rules_only_four_family_test60_20260801"
)
OUT_JSON = (
    REPO_ROOT
    / "experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json"
)
OUT_MD = (
    REPO_ROOT
    / "docs/experiments/exectv2/reliability/"
    / "exectv2_rules_only_four_family_clinical_headline_test60_2026-08-01.md"
)
LETTER_ID_RE = re.compile(r"\bEA\d{4}\b")
EXPECTED_ROW_COUNT = 59


def main() -> None:
    gold = load_letters_for_split("test")
    if len(gold) != EXPECTED_ROW_COUNT:
        raise ValueError(f"expected {EXPECTED_ROW_COUNT} test letters, got {len(gold)}")

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
        candidate_name="exectv2_rules_only_four_family_test60",
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

    sealed_path = _write_sealed_predictions(restricted)
    sealed_digest = _sha256(sealed_path)

    payload: dict[str, Any] = {
        "schema_version": "exectv2.rules_only_four_family_clinical_headline.test60.v1",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0046-exect-primary-method-comparison-boundary.md",
        "generated_on": date.today().isoformat(),
        "split": "test60",
        "split_loader": "test",
        "row_count": len(gold),
        "row_policy": "aggregate_only",
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
        "sealed_predictions": {
            "local_path": str(sealed_path.relative_to(REPO_ROOT)).replace("\\", "/"),
            "sha256": sealed_digest,
            "bytes": sealed_path.stat().st_size,
            "note": "Sealed under scratch/holdout; not for row inspection or public copy.",
        },
        "claim_boundary": (
            "Aggregate-only rules-only four-family clinical_headline on ExECT "
            "test60 for decision 0046. Sol-matched assembly headline_target on "
            "all-nine deterministic predictions with non-key entities excluded "
            "from the peer score only. No letter identifiers, notes, "
            "predictions, or failure cases are included in this public "
            "artifact. Not the published ExECT benchmark or clinical validation."
        ),
    }
    _assert_aggregate_only(payload)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    _assert_no_letter_ids(text, "public JSON")
    OUT_JSON.write_text(text, encoding="utf-8")

    md = _render_markdown(payload)
    _assert_no_letter_ids(md, "public Markdown")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md, encoding="utf-8")

    print(f"wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"sealed {sealed_path.relative_to(REPO_ROOT)}")
    print(f"overall F1={payload['clinical_headline']['f1']:.4f}")


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


def _write_sealed_predictions(letters: tuple[PredictedLetter, ...]) -> Path:
    SEALED_ROOT.mkdir(parents=True, exist_ok=True)
    path = SEALED_ROOT / "four_family_predictions.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for letter in letters:
            row = {
                "letter_id": letter.letter_id,
                "predicted_mentions": [mention_to_dict(m) for m in letter.mentions],
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def _assert_aggregate_only(payload: dict[str, Any]) -> None:
    forbidden = {"rows", "letters", "predictions", "traces", "letter_id", "note_text"}
    leaked = sorted(forbidden.intersection(payload))
    if leaked:
        raise ValueError(f"public payload contains forbidden keys: {leaked}")


def _assert_no_letter_ids(text: str, label: str) -> None:
    hits = LETTER_ID_RE.findall(text)
    if hits:
        raise ValueError(f"{label} leaked letter ids: {hits[:5]}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_markdown(payload: dict[str, Any]) -> str:
    overall = payload["clinical_headline"]
    lines = [
        "# ExECTv2 rules-only four-family clinical_headline (test60)",
        "",
        f"Date: {payload['generated_on']}",
        "Status: complete; Phase C of the 0046 evidence protocol",
        "Row policy: aggregate-only",
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
        "exectv2_rules_only_four_family_clinical_headline_test60_20260801.json)",
        "",
        "## Question",
        "",
        "What is rules-only four-family `clinical_headline` F1 on locked "
        "`test60` under the Sol-matched assembly `headline_target` surface?",
        "",
        "## Result",
        "",
        "Aggregate-only. No letter identifiers, notes, predictions, or row "
        "failures are reported. Sealed predictions remain under ignored "
        "`scratch/holdout/`.",
        "",
        f"| Overall clinical_headline F1 | {overall['f1']:.4f} |",
        f"| Precision | {overall['precision']:.4f} |",
        f"| Recall | {overall['recall']:.4f} |",
        f"| Letters scored | {payload['row_count']} |",
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
            "- Production rule: restrict-and-rescore to the four key families.",
            "- Scorer: assembly `headline_target` via `build_scoring_views`.",
            f"- Mentions (counts only): {accounting['all9_mentions']} all-nine → "
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
            "Update canon / manuscript method rows to decision 0046 using the "
            "completed A→B→C artifacts.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
