"""Replay sf_state_projection on dev140 for the 2026-08-12 rule-fix hypothesis.

Repeatable producer for hypothesis
``sf_state_projection_rule_fix_2026-08-12``. Rebuilds the SeizureFrequency
projection input the same way ``scripts/run_exectv2_2call_model_swap.py`` does
(direct SF mentions from each saved single-call structured artifact), runs
``sf_state_projection.project_rows(ablation="combined")``, and scores the
result. No model calls; reads only permitted dev140 rows.

The pre-fix column is pinned from the replay run recorded in the predeclaration
doc (the parent commit of the fix, b27d0a40). Re-running this script on that
commit with ``--write-baseline`` regenerates it.

    python scripts/check_sf_state_projection_rule_fix_dev140_20260812.py
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection as sf_projection,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = REPO_ROOT / "experiments"
OUTPUT_PATH = EXPERIMENTS / "sf_state_projection_rule_fix_dev140_20260812.json"
PREDECLARATION_PATH = Path(
    "docs/experiments/exectv2/reliability/"
    "exectv2_sf_state_projection_rule_fix_predeclaration_2026-08-12.md"
)
HYPOTHESIS_ID = "sf_state_projection_rule_fix_2026-08-12"
GENERATED_ON = "2026-08-12"
SPLIT = "dev"
EXPECTED_LETTERS = 140

MODELS: tuple[tuple[str, str], ...] = (
    ("deepseek_v4_flash", "DeepSeek v4 flash"),
    ("gemma4_26b", "Gemma 4 26B"),
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("qwen36_35b", "Qwen 3.6 35B"),
)

# Pre-fix replay at commit b27d0a40 (benchmark/semantic per-item counts).
PREFIX_BASELINE: Mapping[str, Mapping[str, int]] = {
    "deepseek_v4_flash": {"tp": 85, "fp": 70, "fn": 102},
    "gemma4_26b": {"tp": 56, "fp": 153, "fn": 131},
    "gpt41mini": {"tp": 65, "fp": 125, "fn": 122},
    "gpt56luna": {"tp": 97, "fp": 75, "fn": 90},
    "gpt56sol": {"tp": 108, "fp": 68, "fn": 79},
    "qwen36_35b": {"tp": 61, "fp": 115, "fn": 126},
}

# Kill criterion: no model may regress on the attribute-exact surface, and the
# pooled attribute-exact F1 must rise.
POOLED_PREFIX_F1 = 0.4291


def _structured_artifact(model_key: str) -> Path:
    return EXPERIMENTS / (
        f"exectv2_six_model_single_call_{model_key}_dev140_20260715_structured.jsonl"
    )


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sf_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    attributes = mention.get("attributes")
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(attributes) if isinstance(attributes, Mapping) else {},
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
        "component_owner": "single_gpt_structured_no_sf_adjudicator",
    }


def build_projection_rows(
    structured_path: Path,
    letter_by_id: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Rebuild the `_sf_structured_direct` projection input for one model."""

    rows: list[dict[str, Any]] = []
    for row in _read_jsonl(structured_path):
        letter_id = str(row["letter_id"])
        mentions = [
            _sf_mention(mention)
            for mention in row.get("predicted_mentions", [])
            if str(mention.get("entity")) == SEIZURE_FREQUENCY.name
        ]
        rows.append(
            {
                "letter_id": letter_id,
                "split": row.get("split", SPLIT),
                "prompt_version": "structured_direct_no_sf_adjudicator_v01",
                "pipeline_family": "exectv2_structured_direct_no_sf_adjudicator",
                "predicted_mentions": mentions,
                "parse_errors": [],
                "gold_mentions": [
                    {
                        "entity": annotation.entity,
                        "text": annotation.text,
                        "attributes": dict(annotation.attributes),
                    }
                    for annotation in letter_by_id[letter_id].annotations
                    if annotation.entity == SEIZURE_FREQUENCY.name
                ],
            }
        )
    return rows


def _counts(score: Mapping[str, Any]) -> dict[str, int]:
    return {"tp": int(score["tp"]), "fp": int(score["fp"]), "fn": int(score["fn"])}


def _prf(tp: int, fp: int, fn: int) -> dict[str, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {"precision": precision, "recall": recall, "f1": f1}


def main() -> None:
    args = _parse_args()
    letters = load_letters_for_split(SPLIT)
    if len(letters) != EXPECTED_LETTERS:
        raise SystemExit(f"expected {EXPECTED_LETTERS} dev letters, got {len(letters)}")
    letter_by_id = {letter.letter_id: letter for letter in letters}

    per_model: dict[str, Any] = {}
    regressions: list[str] = []
    pooled_post = {"tp": 0, "fp": 0, "fn": 0}
    pooled_pre = {"tp": 0, "fp": 0, "fn": 0}

    for model_key, model_label in MODELS:
        path = _structured_artifact(model_key)
        if not path.exists():
            raise SystemExit(f"missing saved artifact: {path}")
        rows = build_projection_rows(path, letter_by_id)
        _projected, metadata = sf_projection.project_rows(rows, ablation="combined")
        summary = metadata["summary"]

        post = _counts(summary["benchmark"]["per_item"])
        pre = dict(PREFIX_BASELINE[model_key])
        post_scores = _prf(post["tp"], post["fp"], post["fn"])
        pre_scores = _prf(pre["tp"], pre["fp"], pre["fn"])
        if post_scores["f1"] + 1e-12 < pre_scores["f1"]:
            regressions.append(
                f"{model_label}: attribute-exact F1 "
                f"{pre_scores['f1']:.4f} -> {post_scores['f1']:.4f}"
            )
        for bucket, counts in ((pooled_post, post), (pooled_pre, pre)):
            for key in bucket:
                bucket[key] += counts[key]

        per_model[model_key] = {
            "model_label": model_label,
            "source_artifact": path.name,
            "attribute_exact_prefix": {**pre, **pre_scores},
            "attribute_exact_postfix": {**post, **post_scores},
            "clinical_headline_postfix": summary["clinical_recovery"]["seizure_frequency"],
            "projection_action_counts": metadata["projection_action_counts"],
        }

    pooled = {
        "prefix": {**pooled_pre, **_prf(**pooled_pre)},
        "postfix": {**pooled_post, **_prf(**pooled_post)},
    }
    pooled_improved = pooled["postfix"]["f1"] > pooled["prefix"]["f1"]
    verdict = "CONFIRMED" if pooled_improved and not regressions else "REFUTED"

    payload = {
        "hypothesis_id": HYPOTHESIS_ID,
        "predeclaration_doc": str(PREDECLARATION_PATH),
        "generated_on": GENERATED_ON,
        "split": SPLIT,
        "n_letters": EXPECTED_LETTERS,
        "model_calls": 0,
        "surface": (
            "sf_state_projection.project_rows(ablation='combined') over saved "
            "single-call structured dev140 outputs; benchmark/semantic per-item "
            "(attribute-exact) and clinical_recovery headline"
        ),
        "kill_criterion": (
            "REFUTED if any model's attribute-exact per-item F1 falls, or if the "
            "pooled attribute-exact F1 does not rise."
        ),
        "per_model": per_model,
        "pooled_attribute_exact": pooled,
        "regressions": regressions,
        "verdict": verdict,
    }

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    print(f"{'model':<22} {'pre F1':>8} {'post F1':>8} {'dF1':>8}")
    for model_key, _label in MODELS:
        entry = per_model[model_key]
        pre_f1 = entry["attribute_exact_prefix"]["f1"]
        post_f1 = entry["attribute_exact_postfix"]["f1"]
        print(f"{model_key:<22} {pre_f1:>8.4f} {post_f1:>8.4f} {post_f1 - pre_f1:>+8.4f}")
    print(
        f"{'POOLED':<22} {pooled['prefix']['f1']:>8.4f} "
        f"{pooled['postfix']['f1']:>8.4f} "
        f"{pooled['postfix']['f1'] - pooled['prefix']['f1']:>+8.4f}"
    )
    print(f"\nverdict: {verdict}")
    if regressions:
        for item in regressions:
            print(f"  regression: {item}")
    if args.output is not None:
        print(f"wrote {args.output}")
    if verdict != "CONFIRMED":
        raise SystemExit(1)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_PATH,
        help="machine artifact path (pass --no-output to skip)",
    )
    parser.add_argument(
        "--no-output",
        dest="output",
        action="store_const",
        const=None,
        help="print the replay without writing the machine artifact",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
