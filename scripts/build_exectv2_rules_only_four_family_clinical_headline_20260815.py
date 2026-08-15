"""Remasure rules-only four-family clinical_headline after Investigations rewrite.

dev140: row-level development scoring is permitted.
test60: aggregate-only public artifact; no letter identifiers in public files.
No model calls. Does not overwrite the 2026-08-01 Decision 0046 artifacts.
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
LETTER_ID_RE = re.compile(r"\bEA\d{4}\b")
TEST_ROW_COUNT = 59


def main() -> None:
    _write_dev140()
    _write_test60()


def _write_dev140() -> None:
    gold = load_letters_for_split("dev")
    if len(gold) != 140:
        raise ValueError(f"expected 140 dev letters, got {len(gold)}")
    payload = _score(
        gold,
        split="dev140",
        split_loader="dev",
        row_policy="dev140_rows_permitted_test60_forbidden",
        candidate_name="exectv2_rules_only_four_family_dev140",
        claim_boundary=(
            "Development rules-only four-family clinical_headline on ExECT "
            "dev140 after the 2026-08-15 Investigations result-binding "
            "rewrite. Sol-matched assembly headline_target. Not nine-entity "
            "published metrics, not holdout evidence, and not clinical "
            "validation."
        ),
    )
    out_json = (
        REPO_ROOT
        / "experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260815.json"
    )
    out_md = (
        REPO_ROOT
        / "docs/experiments/exectv2/reliability/"
        / "exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-15.md"
    )
    _write_public(out_json, out_md, payload, split_label="dev140", check_ids=False)
    print(
        f"dev140 F1={payload['clinical_headline']['f1']:.4f} "
        f"Investigations={payload['clinical_headline_by_family']['Investigations']['f1']:.4f}"
    )


def _write_test60() -> None:
    gold = load_letters_for_split("test")
    if len(gold) != TEST_ROW_COUNT:
        raise ValueError(f"expected {TEST_ROW_COUNT} test letters, got {len(gold)}")
    all9, restricted, dropped = _run_restricted(gold)
    payload = _score_from_restricted(
        gold,
        restricted,
        dropped,
        split="test60",
        split_loader="test",
        row_policy="aggregate_only",
        candidate_name="exectv2_rules_only_four_family_test60",
        claim_boundary=(
            "Aggregate-only rules-only four-family clinical_headline on ExECT "
            "test60 after the 2026-08-15 Investigations result-binding rewrite. "
            "Sol-matched assembly headline_target. No letter identifiers, "
            "notes, predictions, or failure cases are included in this public "
            "artifact. Not the published ExECT benchmark or clinical validation."
        ),
    )
    sealed_root = (
        REPO_ROOT / "scratch/holdout/exectv2_rules_only_four_family_test60_20260815"
    )
    sealed_path = _write_sealed_predictions(sealed_root, restricted)
    payload["sealed_predictions"] = {
        "local_path": str(sealed_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "sha256": _sha256(sealed_path),
        "bytes": sealed_path.stat().st_size,
        "note": "Sealed under scratch/holdout; not for row inspection or public copy.",
    }
    _assert_aggregate_only(payload)
    out_json = (
        REPO_ROOT
        / "experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260815.json"
    )
    out_md = (
        REPO_ROOT
        / "docs/experiments/exectv2/reliability/"
        / "exectv2_rules_only_four_family_clinical_headline_test60_2026-08-15.md"
    )
    _write_public(out_json, out_md, payload, split_label="test60", check_ids=True)
    print(
        f"test60 F1={payload['clinical_headline']['f1']:.4f} "
        f"Investigations={payload['clinical_headline_by_family']['Investigations']['f1']:.4f}"
    )


def _run_restricted(
    gold: list[Any],
) -> tuple[tuple[PredictedLetter, ...], tuple[PredictedLetter, ...], dict[str, int]]:
    all9 = tuple(
        run_all9_on_letters(
            gold,
            include_diagnosis_resolution_candidate=False,
            include_diagnosis_benchmark_residuals=False,
        )
    )
    restricted = tuple(_restrict_to_four_families(letter) for letter in all9)
    dropped = _count_dropped_mentions(all9, restricted)
    return all9, restricted, dropped


def _score(
    gold: list[Any],
    *,
    split: str,
    split_loader: str,
    row_policy: str,
    candidate_name: str,
    claim_boundary: str,
) -> dict[str, Any]:
    _all9, restricted, dropped = _run_restricted(gold)
    return _score_from_restricted(
        gold,
        restricted,
        dropped,
        split=split,
        split_loader=split_loader,
        row_policy=row_policy,
        candidate_name=candidate_name,
        claim_boundary=claim_boundary,
    )


def _score_from_restricted(
    gold: list[Any],
    restricted: tuple[PredictedLetter, ...],
    dropped: dict[str, int],
    *,
    split: str,
    split_loader: str,
    row_policy: str,
    candidate_name: str,
    claim_boundary: str,
) -> dict[str, Any]:
    _views, score_ladder, _headline = build_scoring_views(
        candidate_name=candidate_name,
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
    return {
        "schema_version": f"exectv2.rules_only_four_family_clinical_headline.{split}.v1",
        "protocol": PROTOCOL,
        "decision": "docs/decisions/0046-exect-primary-method-comparison-boundary.md",
        "generated_on": date.today().isoformat(),
        "split": split,
        "split_loader": split_loader,
        "row_count": len(gold),
        "row_policy": row_policy,
        "method": {
            "pipeline": "deterministic_all9",
            "scoring": "assembly_headline_target",
            "production_rule": "restrict_and_rescore",
            "include_diagnosis_resolution_candidate": False,
            "include_diagnosis_benchmark_residuals": False,
            "scored_families": list(TARGET_INDICATORS),
            "non_key_entities_excluded_from_peer_score_only": True,
            "investigations_extractor": "result_binding_2026-08-15",
        },
        "clinical_headline": {
            "f1": float(overall["f1"]),
            "precision": float(overall["precision"]),
            "recall": float(overall["recall"]),
        },
        "clinical_headline_by_family": by_family,
        "mention_accounting": dropped,
        "supersedes": (
            f"experiments/exectv2_rules_only_four_family_clinical_headline_{split}_20260801.json"
        ),
        "claim_boundary": claim_boundary,
    }


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


def _write_sealed_predictions(
    sealed_root: Path, letters: tuple[PredictedLetter, ...]
) -> Path:
    sealed_root.mkdir(parents=True, exist_ok=True)
    path = sealed_root / "four_family_predictions.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for letter in letters:
            row = {
                "letter_id": letter.letter_id,
                "predicted_mentions": [mention_to_dict(m) for m in letter.mentions],
            }
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def _write_public(
    out_json: Path,
    out_md: Path,
    payload: dict[str, Any],
    *,
    split_label: str,
    check_ids: bool,
) -> None:
    out_json.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2) + "\n"
    if check_ids:
        _assert_no_letter_ids(text, "public JSON")
    out_json.write_text(text, encoding="utf-8")
    md = _render_markdown(payload, split_label)
    if check_ids:
        _assert_no_letter_ids(md, "public Markdown")
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(md, encoding="utf-8")
    print(f"wrote {out_json.relative_to(REPO_ROOT)}")
    print(f"wrote {out_md.relative_to(REPO_ROOT)}")


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


def _render_markdown(payload: dict[str, Any], split_label: str) -> str:
    overall = payload["clinical_headline"]
    lines = [
        f"# ExECTv2 rules-only four-family clinical_headline ({split_label})",
        "",
        f"Date: {payload['generated_on']}",
        "Status: complete; 2026-08-15 Investigations result-binding remasure",
        f"Row policy: {payload['row_policy']}",
        "",
        "Protocol: "
        "[primary method-comparison surface protocol]"
        "(exectv2_primary_method_comparison_surface_protocol_2026-08-01.md)",
        "",
        "Decision: "
        "[0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)",
        "",
        "Machine artifact: "
        f"[JSON](../../../experiments/"
        f"exectv2_rules_only_four_family_clinical_headline_{split_label}_20260815.json)",
        "",
        "Supersedes the 2026-08-01 fill for this split. Historical file kept.",
        "",
        "## Result",
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
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            str(payload["claim_boundary"]),
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
