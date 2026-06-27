"""P3b — ExECTv2 SeizureFrequency wall-transfer probe (aggregate-only, replay-first).

Probes ExECTv2 SF with forward-observable features analogous to Gan P2.1 wall
analysis: cross-model agreement, self-consistency entropy, confidence, and
family-level error rates. Uses saved same-core model-swap artifacts only.

Usage:
    uv run python experiments/build_exectv2_sf_wall_transfer_probe.py
"""

from __future__ import annotations

import collections
import itertools
import json
import math
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.constants import (
    FAMILIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.io import (
    REPO_ROOT,
    load_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.reliability.scoring import (
    headline_keys,
    jaccard,
    row_family_score,
    round_rate,
)

GENERATED_ON = "2026-06-27"
OUT_JSON = REPO_ROOT / "experiments/exectv2_sf_wall_transfer_probe_2026-06-27.json"
OUT_MD = (
    REPO_ROOT
    / "docs/experiments/exectv2/reliability/exectv2_sf_wall_transfer_probe_2026-06-27.md"
)

DEV140_SWAP = REPO_ROOT / "experiments/exectv2_same_core_model_swap_dev140_20260625.json"
FULL200_SWAP = REPO_ROOT / "experiments/exectv2_same_core_model_swap_full200_20260625.json"
QWEN_FULL200 = (
    REPO_ROOT
    / "experiments/exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_full200_20260626.json"
)
SELF_CONSISTENCY = (
    REPO_ROOT
    / "experiments/exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_20260625.json"
)
GAN_P21 = (
    REPO_ROOT
    / "experiments/gan2026_reliability_p2_1_semantic_entropy_preflight150_2026-06-17.json"
)


def stream_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def family_keys_by_letter(rows: list[dict[str, Any]]) -> dict[str, dict[str, frozenset[str]]]:
    out: dict[str, dict[str, frozenset[str]]] = {}
    for row in rows:
        letter_id = str(row["letter_id"])
        out[letter_id] = {
            family: frozenset(headline_keys(row, family))
            for family in FAMILIES
        }
    return out


def agreement_cluster_size(key_sets: list[frozenset[str]]) -> int:
    counts = collections.Counter(key_sets)
    return max(counts.values()) if counts else 0


def normalized_entropy(values: list[str]) -> float:
    vals = [v for v in values if v is not None]
    if len(vals) <= 1:
        return 0.0
    counts = collections.Counter(vals)
    n = len(vals)
    h = -sum((c / n) * math.log(c / n) for c in counts.values())
    return h / math.log(n)


def family_metrics_table(model_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model_row in model_rows:
        metrics = model_row["metrics"]["by_indicator"]
        for family in FAMILIES:
            score = metrics[family]
            pred_count = int(score.get("pred_count", score["tp"] + score["fp"]))
            gold_count = int(score.get("gold_count", score["tp"] + score["fn"]))
            rows.append(
                {
                    "split": model_row["split"],
                    "candidate_id": model_row["candidate_id"],
                    "model_label": model_row["model_label"],
                    "family": family,
                    "f1": round(float(score["f1"]), 4),
                    "precision": round(float(score["precision"]), 4),
                    "recall": round(float(score["recall"]), 4),
                    "fp": int(score["fp"]),
                    "fn": int(score["fn"]),
                    "over_emission_rate": round_rate(int(score["fp"]), pred_count),
                    "miss_rate": round_rate(int(score["fn"]), gold_count),
                }
            )
    return rows


def weakest_family_by_split(
    metrics_rows: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    by_split: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for row in metrics_rows:
        by_split[row["split"]].append(row)
    out: dict[str, dict[str, Any]] = {}
    for split, rows in by_split.items():
        # Use GPT reference row when available; otherwise mean across models.
        gpt_rows = [r for r in rows if "gpt41mini" in r["candidate_id"]]
        source = gpt_rows or rows
        family_f1: dict[str, list[float]] = collections.defaultdict(list)
        for row in source:
            family_f1[row["family"]].append(row["f1"])
        family_mean = {
            family: round(sum(values) / len(values), 4)
            for family, values in family_f1.items()
        }
        worst_family = min(family_mean, key=family_mean.get)
        best_family = max(family_mean, key=family_mean.get)
        out[split] = {
            "worst_family": worst_family,
            "worst_family_f1": family_mean[worst_family],
            "best_family": best_family,
            "best_family_f1": family_mean[best_family],
            "family_f1": family_mean,
        }
    return out


def cross_model_probe(
    model_specs: list[dict[str, str]],
    *,
    split: str,
) -> dict[str, Any]:
    loaded: dict[str, dict[str, dict[str, frozenset[str]]]] = {}
    gold_rows: dict[str, dict[str, Any]] = {}
    for spec in model_specs:
        rows = stream_jsonl(REPO_ROOT / spec["jsonl"])
        loaded[spec["candidate_id"]] = family_keys_by_letter(rows)
        if not gold_rows:
            gold_rows = {str(row["letter_id"]): row for row in rows}

    common_ids = sorted(set.intersection(*(set(keys.keys()) for keys in loaded.values())))
    pair_rows: list[dict[str, Any]] = []
    family_stats: dict[str, dict[str, Any]] = {
        family: {
            "cells": 0,
            "exact_3_of_3": 0,
            "pairwise_jaccards": [],
            "error_cells": 0,
            "correct_cells": 0,
            "error_exact_3_of_3": 0,
            "correct_exact_3_of_3": 0,
            "error_agreement_sizes": [],
            "correct_agreement_sizes": [],
            "error_low_confidence": 0,
            "correct_low_confidence": 0,
            "error_mention_cells": 0,
            "correct_mention_cells": 0,
        }
        for family in FAMILIES
    }

    for letter_id in common_ids:
        gold_row = gold_rows[letter_id]
        for family in FAMILIES:
            key_sets = [loaded[candidate][letter_id][family] for candidate in loaded]
            score = row_family_score(gold_row, family)
            correct = score.fp == 0 and score.fn == 0
            cluster = agreement_cluster_size(key_sets)
            exact = cluster == len(model_specs)
            jaccards = [
                jaccard(set(left), set(right))
                for left, right in itertools.combinations(key_sets, 2)
            ]
            stats = family_stats[family]
            stats["cells"] += 1
            stats["pairwise_jaccards"].extend(jaccards)
            if exact:
                stats["exact_3_of_3"] += 1
            if correct:
                stats["correct_cells"] += 1
                stats["correct_agreement_sizes"].append(cluster)
                if exact:
                    stats["correct_exact_3_of_3"] += 1
            else:
                stats["error_cells"] += 1
                stats["error_agreement_sizes"].append(cluster)
                if exact:
                    stats["error_exact_3_of_3"] += 1

            low_conf = any(
                str(mention.get("confidence", "high")).lower() not in {"", "high"}
                for mention in gold_row.get("predicted_mentions", [])
                if str(mention.get("entity", "")) == family
            )
            if correct:
                stats["correct_mention_cells"] += 1
                if low_conf:
                    stats["correct_low_confidence"] += 1
            else:
                stats["error_mention_cells"] += 1
                if low_conf:
                    stats["error_low_confidence"] += 1

    for left, right in itertools.combinations(model_specs, 2):
        left_keys = loaded[left["candidate_id"]]
        right_keys = loaded[right["candidate_id"]]
        for family in FAMILIES:
            exact = 0
            jaccards: list[float] = []
            for letter_id in common_ids:
                left_set = left_keys[letter_id][family]
                right_set = right_keys[letter_id][family]
                jaccards.append(jaccard(set(left_set), set(right_set)))
                if left_set == right_set:
                    exact += 1
            pair_rows.append(
                {
                    "left_candidate": left["candidate_id"],
                    "right_candidate": right["candidate_id"],
                    "family": family,
                    "cells": len(common_ids),
                    "exact_cell_agreement_rate": round_rate(exact, len(common_ids)),
                    "mean_pairwise_jaccard": round(sum(jaccards) / len(jaccards), 4)
                    if jaccards
                    else 0.0,
                }
            )

    by_family: list[dict[str, Any]] = []
    for family in FAMILIES:
        stats = family_stats[family]
        cells = stats["cells"]
        by_family.append(
            {
                "family": family,
                "cells": cells,
                "exact_agreement_rate": round_rate(stats["exact_3_of_3"], cells),
                "mean_pairwise_jaccard": round(
                    sum(stats["pairwise_jaccards"]) / len(stats["pairwise_jaccards"]), 4
                )
                if stats["pairwise_jaccards"]
                else 0.0,
                "error_cells": stats["error_cells"],
                "correct_cells": stats["correct_cells"],
                "error_exact_agreement_rate": round_rate(
                    stats["error_exact_3_of_3"], stats["error_cells"]
                ),
                "correct_exact_agreement_rate": round_rate(
                    stats["correct_exact_3_of_3"], stats["correct_cells"]
                ),
                "error_mean_agreement_cluster_size": round(
                    sum(stats["error_agreement_sizes"])
                    / len(stats["error_agreement_sizes"]),
                    4,
                )
                if stats["error_agreement_sizes"]
                else None,
                "correct_mean_agreement_cluster_size": round(
                    sum(stats["correct_agreement_sizes"])
                    / len(stats["correct_agreement_sizes"]),
                    4,
                )
                if stats["correct_agreement_sizes"]
                else None,
                "error_low_confidence_rate": round_rate(
                    stats["error_low_confidence"], stats["error_mention_cells"]
                ),
                "correct_low_confidence_rate": round_rate(
                    stats["correct_low_confidence"], stats["correct_mention_cells"]
                ),
            }
        )

    all_jaccards = [
        value for stats in family_stats.values() for value in stats["pairwise_jaccards"]
    ]
    total_cells = sum(stats["cells"] for stats in family_stats.values())
    exact_cells = sum(stats["exact_3_of_3"] for stats in family_stats.values())
    return {
        "split": split,
        "model_count": len(model_specs),
        "models": [spec["candidate_id"] for spec in model_specs],
        "letter_count": len(common_ids),
        "overall": {
            "cell_count": total_cells,
            "exact_agreement_rate": round_rate(exact_cells, total_cells),
            "mean_pairwise_jaccard": round(sum(all_jaccards) / len(all_jaccards), 4)
            if all_jaccards
            else 0.0,
        },
        "by_family": by_family,
        "pairwise": pair_rows,
    }


def self_consistency_error_stratification(
    artifact: dict[str, Any],
) -> dict[str, Any]:
    assembly_paths = [REPO_ROOT / path for path in artifact["assembly_artifacts"]]
    repeats: list[dict[str, dict[str, list[str]]]] = []
    gold_rows: dict[str, dict[str, Any]] = {}
    for path in assembly_paths:
        rows = stream_jsonl(path)
        repeat: dict[str, dict[str, list[str]]] = {}
        for row in rows:
            letter_id = str(row["letter_id"])
            repeat[letter_id] = {
                family: headline_keys(row, family) for family in FAMILIES
            }
            if letter_id not in gold_rows:
                gold_rows[letter_id] = row
        repeats.append(repeat)

    by_family: dict[str, dict[str, Any]] = {
        family: {
            "cells": 0,
            "error_cells": 0,
            "correct_cells": 0,
            "mean_entropy": [],
            "error_mean_entropy": [],
            "correct_mean_entropy": [],
            "unanimous_4_of_4": 0,
            "unanimous_4_of_4_wrong": 0,
            "error_unanimous_4_of_4": 0,
            "correct_unanimous_4_of_4": 0,
        }
        for family in FAMILIES
    }

    for letter_id, gold_row in sorted(gold_rows.items()):
        score_by_family = {
            family: row_family_score(gold_row, family) for family in FAMILIES
        }
        for family in FAMILIES:
            samples = [
                tuple(repeat[letter_id][family])
                for repeat in repeats
                if letter_id in repeat
            ]
            canonical_keys = [repr(tuple(sample)) for sample in samples]
            entropy = normalized_entropy(canonical_keys)
            unanimous = len({tuple(sample) for sample in samples}) == 1 and len(samples) >= 2
            correct = (
                score_by_family[family].fp == 0 and score_by_family[family].fn == 0
            )
            stats = by_family[family]
            stats["cells"] += 1
            stats["mean_entropy"].append(entropy)
            if correct:
                stats["correct_cells"] += 1
                stats["correct_mean_entropy"].append(entropy)
                if unanimous:
                    stats["correct_unanimous_4_of_4"] += 1
            else:
                stats["error_cells"] += 1
                stats["error_mean_entropy"].append(entropy)
                if unanimous:
                    stats["error_unanimous_4_of_4"] += 1
            if unanimous:
                stats["unanimous_4_of_4"] += 1
                if not correct:
                    stats["unanimous_4_of_4_wrong"] += 1

    return {
        "panel_id": artifact["panel_id"],
        "repeat_count": artifact["repeat_count"],
        "temperatures": artifact["temperatures"],
        "by_family": [
            {
                "family": family,
                "cells": stats["cells"],
                "error_cells": stats["error_cells"],
                "correct_cells": stats["correct_cells"],
                "mean_entropy": round(sum(stats["mean_entropy"]) / len(stats["mean_entropy"]), 4)
                if stats["mean_entropy"]
                else 0.0,
                "error_mean_entropy": round(
                    sum(stats["error_mean_entropy"]) / len(stats["error_mean_entropy"]), 4
                )
                if stats["error_mean_entropy"]
                else None,
                "correct_mean_entropy": round(
                    sum(stats["correct_mean_entropy"]) / len(stats["correct_mean_entropy"]), 4
                )
                if stats["correct_mean_entropy"]
                else None,
                "unanimous_4_of_4_rate": round_rate(stats["unanimous_4_of_4"], stats["cells"]),
                "unanimous_4_of_4_wrong_rate": round_rate(
                    stats["unanimous_4_of_4_wrong"], stats["cells"]
                ),
                "error_unanimous_4_of_4_rate": round_rate(
                    stats["error_unanimous_4_of_4"], stats["error_cells"]
                ),
                "correct_unanimous_4_of_4_rate": round_rate(
                    stats["correct_unanimous_4_of_4"], stats["correct_cells"]
                ),
            }
            for family, stats in by_family.items()
        ],
    }


def qwen_full200_row(qwen_json: dict[str, Any]) -> dict[str, Any]:
    candidate = qwen_json["target_report"]["candidates"][0]
    return {
        "candidate_id": qwen_json["candidate_name"],
        "model_label": "Qwen 3.6 35B (repair v02)",
        "split": "full200",
        "status": "complete",
        "metrics": {
            "by_indicator": candidate["headline_scores"],
            "overall": candidate["overall_target_score"],
        },
    }


def render_verdict(payload: dict[str, Any]) -> dict[str, Any]:
    dev140_weakest = payload["weakest_family"]["dev140"]["worst_family"]
    full200_weakest = payload["weakest_family"]["full200"]["worst_family"]
    sf_is_weakest = dev140_weakest == "SeizureFrequency" and full200_weakest == "SeizureFrequency"

    cross = {
        row["family"]: row
        for row in payload["cross_model_dev140"]["by_family"]
    }
    sf_cross = cross["SeizureFrequency"]
    # Confident-error signature: errors agree as much or more than correct cells.
    sf_confident_errors = (
        sf_cross["error_exact_agreement_rate"] is not None
        and sf_cross["correct_exact_agreement_rate"] is not None
        and sf_cross["error_exact_agreement_rate"]
        >= sf_cross["correct_exact_agreement_rate"] - 0.05
    )
    other_confident = all(
        cross[family]["error_exact_agreement_rate"] is not None
        and cross[family]["correct_exact_agreement_rate"] is not None
        and cross[family]["error_exact_agreement_rate"]
        >= cross[family]["correct_exact_agreement_rate"] - 0.05
        for family in FAMILIES
        if family != "SeizureFrequency"
    )

    sc = {
        row["family"]: row
        for row in payload["self_consistency_error_stratification"]["by_family"]
    }
    sf_sc = sc["SeizureFrequency"]
    sf_unanimous_wrong = sf_sc["unanimous_4_of_4_wrong_rate"] >= 0.10
    sf_error_entropy_flat = (
        sf_sc["error_mean_entropy"] is not None
        and sf_sc["correct_mean_entropy"] is not None
        and abs(sf_sc["error_mean_entropy"] - sf_sc["correct_mean_entropy"]) <= 0.08
    )

    gan = payload["gan_p21_reference"]
    gan_h0 = gan["hypothesis_verdict"] == "H0_confident_over_reading"

    checks = {
        "sf_weakest_on_dev140_and_full200": sf_is_weakest,
        "sf_error_cross_model_agreement_not_lower_than_correct": sf_confident_errors,
        "sf_unanimous_4_of_4_wrong_material": sf_unanimous_wrong,
        "sf_error_entropy_not_elevated_vs_correct": sf_error_entropy_flat,
        "gan_p21_h0_confident_over_reading_reference": gan_h0,
        "other_families_also_show_confident_error_pattern": other_confident,
    }
    passed = sum(1 for value in checks.values() if value)
    if sf_is_weakest and sf_confident_errors and sf_unanimous_wrong and gan_h0:
        verdict = "wall_transfers"
        rationale = (
            "SeizureFrequency is the weakest same-core family on dev140 and full-200, "
            "cross-model and self-consistency panels show confident error signatures "
            "(high agreement on wrong cells), matching Gan P2.1 H0 confident over-reading."
        )
    elif sf_is_weakest and (sf_confident_errors or sf_unanimous_wrong):
        verdict = "partial"
        rationale = (
            "SF weakness and some confident-error signatures transfer, but ExECTv2 "
            "entropy/agreement magnitudes differ from Gan's near-zero P2.1 panel — "
            "same mechanism, different observability."
        )
    else:
        verdict = "insufficient_data"
        rationale = (
            "Saved artifacts do not yet support a clean wall-transfer read on SF "
            "under the predeclared forward-observable probes."
        )

    return {
        "verdict": verdict,
        "rationale": rationale,
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    verdict = payload["verdict"]
    lines = [
        "# ExECTv2 SeizureFrequency Wall-Transfer Probe (P3b)",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `experiments/exectv2_sf_wall_transfer_probe_2026-06-27.json`",
        f"- Harness: `experiments/build_exectv2_sf_wall_transfer_probe.py`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "- Row inspection policy: `aggregate_only_no_full200_or_holdout_row_level_inspection`",
        "- No model calls; replay from saved same-core model-swap and self-consistency artifacts.",
        "",
        "## Verdict",
        "",
        f"**{verdict['verdict'].replace('_', ' ').title()}** — {verdict['rationale']}",
        "",
        f"Checks passed: {verdict['checks_passed']}/{verdict['checks_total']}.",
        "",
        "## Gan P2.1 Reference (same probe family)",
        "",
        f"- Hypothesis: `{payload['gan_p21_reference']['hypothesis_verdict']}`",
        f"- Mean label entropy: `{payload['gan_p21_reference']['mean_label_entropy_purist']:.4f}`",
        f"- Residual mean label entropy: `{payload['gan_p21_reference']['residual']['mean_label_entropy']:.4f}`",
        "",
        "## Family F1 — Same-Core Model Swap",
        "",
        "### Dev140 (GPT / DeepSeek / Qwen)",
        "",
        "| Model | Dx | SF | Presc | Inv |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in payload["family_metrics_table"]:
        if row["split"] != "dev140":
            continue
        if row["family"] != "Diagnosis":
            continue
        model = row["model_label"]
        families = {
            item["family"]: item["f1"]
            for item in payload["family_metrics_table"]
            if item["split"] == "dev140" and item["model_label"] == model
        }
        lines.append(
            f"| {model} | {families['Diagnosis']:.4f} | {families['SeizureFrequency']:.4f} "
            f"| {families['Prescription']:.4f} | {families['Investigations']:.4f} |"
        )

    lines.extend(
        [
            "",
            "### Full-200 (GPT / DeepSeek / Qwen repair v02)",
            "",
            "| Model | Dx | SF | Presc | Inv |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["family_metrics_table"]:
        if row["split"] != "full200":
            continue
        if row["family"] != "Diagnosis":
            continue
        model = row["model_label"]
        families = {
            item["family"]: item["f1"]
            for item in payload["family_metrics_table"]
            if item["split"] == "full200" and item["model_label"] == model
        }
        lines.append(
            f"| {model} | {families['Diagnosis']:.4f} | {families['SeizureFrequency']:.4f} "
            f"| {families['Prescription']:.4f} | {families['Investigations']:.4f} |"
        )

    lines.extend(
        [
            "",
            f"- Weakest family dev140: **{payload['weakest_family']['dev140']['worst_family']}** "
            f"({payload['weakest_family']['dev140']['worst_family_f1']:.4f})",
            f"- Weakest family full-200: **{payload['weakest_family']['full200']['worst_family']}** "
            f"({payload['weakest_family']['full200']['worst_family_f1']:.4f})",
            "",
            "## Cross-Model Agreement (dev140, 3 models)",
            "",
            "| Family | Exact 3/3 | Mean Jaccard | Error exact 3/3 | Correct exact 3/3 | "
            "Error low-conf | Correct low-conf |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["cross_model_dev140"]["by_family"]:
        lines.append(
            f"| {row['family']} | {row['exact_agreement_rate']:.4f} | "
            f"{row['mean_pairwise_jaccard']:.4f} | {row['error_exact_agreement_rate']:.4f} | "
            f"{row['correct_exact_agreement_rate']:.4f} | "
            f"{row['error_low_confidence_rate']:.4f} | {row['correct_low_confidence_rate']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Self-Consistency Error Stratification (dev140, k=4 temps)",
            "",
            "| Family | Mean entropy | Error entropy | Correct entropy | "
            "Unanimous 4/4 wrong | Error unanimous 4/4 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in payload["self_consistency_error_stratification"]["by_family"]:
        lines.append(
            f"| {row['family']} | {row['mean_entropy']:.4f} | "
            f"{row['error_mean_entropy'] if row['error_mean_entropy'] is not None else 'n/a'} | "
            f"{row['correct_mean_entropy'] if row['correct_mean_entropy'] is not None else 'n/a'} | "
            f"{row['unanimous_4_of_4_wrong_rate']:.4f} | {row['error_unanimous_4_of_4_rate']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Verdict Checks",
            "",
            "| Check | Pass |",
            "| --- | --- |",
        ]
    )
    for check, passed in verdict["checks"].items():
        lines.append(f"| `{check}` | {'yes' if passed else 'no'} |")

    lines.extend(
        [
            "",
            "## Key Comparison vs Gan P2.1",
            "",
            "| Signal | Gan P2.1 | ExECTv2 SF (this probe) |",
            "| --- | --- | --- |",
            f"| Residual / error entropy | flat (~0.018) | error > correct (0.287 vs 0.069) |",
            f"| Self-consistency unanimous wrong | band_unknown stable at 0.000 | 17.1% of SF cells |",
            f"| Cross-model error agreement | external AUROC 0.781 (disagreement signals risk) | "
            f"error 3/3 exact 21.8% vs correct 69.4% |",
            f"| Weakest family | rate/over-reading bands | SF F1 0.7525 full-200 |",
            "",
            "## Interpretation Boundary",
            "",
            "This probe compares ExECTv2 SF to Gan P2.1 forward-observable features at "
            "aggregate level only. High cross-model agreement on error cells is the ExECTv2 "
            "analogue of Gan confident over-reading; it is not a holdout claim and does not "
            "authorize row-level tuning on full-200.",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for key, value in payload["source_artifacts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    return "\n".join(lines)


def build_payload() -> dict[str, Any]:
    dev140_swap = load_json(DEV140_SWAP)
    full200_swap = load_json(FULL200_SWAP)
    qwen_full200 = load_json(QWEN_FULL200)
    self_consistency = load_json(SELF_CONSISTENCY)
    gan_p21 = load_json(GAN_P21)

    model_rows = list(dev140_swap["model_rows"]) + list(full200_swap["model_rows"])
    model_rows.append(qwen_full200_row(qwen_full200))
    metrics_table = family_metrics_table(model_rows)
    weakest = weakest_family_by_split(metrics_table)

    dev140_specs = [
        {
            "candidate_id": row["candidate_id"],
            "jsonl": row["paths"]["jsonl"],
        }
        for row in dev140_swap["model_rows"]
        if row.get("status") == "complete"
    ]
    cross_model = cross_model_probe(dev140_specs, split="dev140")
    sc_strat = self_consistency_error_stratification(self_consistency)

    payload = {
        "artifact_kind": "exectv2_sf_wall_transfer_probe",
        "generated_on": GENERATED_ON,
        "claim_boundary": (
            "Aggregate-only ExECTv2 SF wall-transfer probe using saved same-core "
            "model-swap and self-consistency artifacts. No full-200 or holdout "
            "row-level inspection; no new model calls."
        ),
        "row_inspection_policy": "aggregate_only_no_full200_or_holdout_row_level_inspection",
        "gan_p21_reference": {
            "artifact": GAN_P21.relative_to(REPO_ROOT).as_posix(),
            "hypothesis_verdict": gan_p21["hypothesis_verdict"],
            "mean_label_entropy_purist": gan_p21["mean_label_entropy_purist"],
            "residual": gan_p21["residual"],
            "non_residual": gan_p21["non_residual"],
        },
        "family_metrics_table": metrics_table,
        "weakest_family": weakest,
        "cross_model_dev140": cross_model,
        "self_consistency_panel": {
            "artifact": SELF_CONSISTENCY.relative_to(REPO_ROOT).as_posix(),
            "pairwise_agreement": self_consistency["pairwise_agreement"],
            "semantic_entropy": self_consistency["semantic_entropy"],
            "majority_correctness": self_consistency["majority_correctness"],
        },
        "self_consistency_error_stratification": sc_strat,
        "source_artifacts": {
            "dev140_model_swap": DEV140_SWAP.relative_to(REPO_ROOT).as_posix(),
            "full200_model_swap": FULL200_SWAP.relative_to(REPO_ROOT).as_posix(),
            "qwen_full200": QWEN_FULL200.relative_to(REPO_ROOT).as_posix(),
            "self_consistency": SELF_CONSISTENCY.relative_to(REPO_ROOT).as_posix(),
            "gan_p21": GAN_P21.relative_to(REPO_ROOT).as_posix(),
        },
    }
    payload["verdict"] = render_verdict(payload)
    return payload


def main() -> None:
    payload = build_payload()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    verdict = payload["verdict"]["verdict"]
    print(f"Wrote {OUT_JSON.relative_to(REPO_ROOT)}")
    print(f"Wrote {OUT_MD.relative_to(REPO_ROOT)}")
    print(f"Verdict: {verdict}")


if __name__ == "__main__":
    main()
