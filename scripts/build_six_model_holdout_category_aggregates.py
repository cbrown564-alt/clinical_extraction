#!/usr/bin/env python3
"""Sealed holdout category aggregates, including unlocked bucket scores.

Machine-only scoring of sealed prediction ledgers. Public outputs stay
aggregate-only. See
docs/research/six_model_holdout_category_aggregates_protocol_2026-08-06.md and
docs/research/six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    clinical_headline_scores,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import hybrid_structured_events

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
_MULTIPLE_WORD_RE = re.compile(r"\bmultiple\b", re.IGNORECASE)

MODEL_SPECS = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)
FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)
X_MIN = 0.85
X_SPREAD_MAX = 0.08
Z_MAX = 0.75
EXECT_MIN_N = 10
GAN_MIN_N = 20
EXECT_HOLDOUT_N = 59
FIDELITY_F1_TOL = 1e-4

EXECT_PANEL = (
    REPO_ROOT / "experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json"
)
EXECT_RULES_HOLDOUT = REPO_ROOT / (
    "experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json"
)
GAN_LLM_PANEL = (
    REPO_ROOT / "experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json"
)
GAN_FLOORS = (
    REPO_ROOT
    / "experiments/gan2026_six_model_current_floors_replay_20260731/replay_summary.json"
)
DEV_CATEGORY_CUT = (
    REPO_ROOT / "experiments/six_model_category_cut_performance_20260806.json"
)
GAN_TAXONOMY = REPO_ROOT / "experiments/gan2026_gold_task_taxonomy_20260806.json"
EXECT_TAXONOMY = REPO_ROOT / "experiments/exectv2_gold_task_taxonomy_20260806.json"

GAN_LLM_ROOT = REPO_ROOT / "scratch/holdout/gan2026_six_model_llm_only_test450_20260801"
GAN_HYBRID_SOURCES = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt41mini/rows.jsonl",
    "gpt56luna": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt56luna/rows.jsonl",
    "gpt56sol": REPO_ROOT / "scratch/holdout/gan2026_matched_v05/gpt56sol/rows.jsonl",
    "deepseek_v4_flash": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05/deepseek_v4_flash/rows.jsonl"
    ),
    "qwen36_35b": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05_local/qwen36_35b/rows.jsonl"
    ),
    "gemma4_26b": (
        REPO_ROOT / "scratch/holdout/gan2026_matched_v05_local/gemma4_26b/rows.jsonl"
    ),
}
GAN_HYBRID_MODELS = {
    "gpt41mini": ("openai/gpt-4.1-mini", 0.0, 10_000),
    "gpt56luna": ("openai/gpt-5.6-luna", 1.0, 10_000),
    "gpt56sol": ("openai/gpt-5.6-sol", 0.0, 10_000),
    "deepseek_v4_flash": ("deepseek/deepseek-v4-flash", 0.0, 32_000),
    "qwen36_35b": ("ollama_chat/qwen3.6:35b", 0.0, 16_000),
    "gemma4_26b": ("ollama_chat/gemma4:26b", 0.0, 16_000),
}
EXECT_SEALED = {
    "gpt41mini": (
        REPO_ROOT / "scratch/holdout/exectv2_test60/gpt41mini/gpt41mini_sealed_rows.jsonl"
    ),
    "gpt56luna": (
        REPO_ROOT / "scratch/holdout/exectv2_test60/gpt56luna/gpt56luna_sealed_rows.jsonl"
    ),
    "gpt56sol": (
        REPO_ROOT
        / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/gpt56sol_sealed_rows.jsonl"
    ),
    "deepseek_v4_flash": (
        REPO_ROOT
        / "scratch/holdout/exectv2_test60/deepseek_v4_flash"
        / "deepseek_v4_flash_sealed_rows.jsonl"
    ),
    "qwen36_35b": (
        REPO_ROOT
        / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b"
        / "qwen36_35b_sealed_rows.jsonl"
    ),
    "gemma4_26b": (
        REPO_ROOT
        / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b"
        / "gemma4_26b_sealed_rows.jsonl"
    ),
}

FORBIDDEN_KEYS = {
    "letter_id",
    "letter_ids",
    "source_row_index",
    "source_row_indices",
    "note_text",
    "raw_output",
    "predicted_mentions",
    "gold_mentions",
    "sealed_rows",
}


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


def _round(value: float) -> float:
    return round(float(value), 4)


def _display_score(value: float) -> str:
    return str(
        Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    )


def _assign_lens(*, scores: dict[str, float], n: int, min_n: int) -> str | None:
    if n < min_n:
        return None
    values = list(scores.values())
    low = min(values)
    high = max(values)
    spread = high - low
    if low >= X_MIN and spread <= X_SPREAD_MAX:
        return "x"
    if high <= Z_MAX:
        return "z"
    return "y"


def _gan_shape_flags(label: str) -> dict[str, bool]:
    text = label.lower().strip()
    return {
        "is_range": " to " in text,
        "is_cluster": "cluster" in text,
        "is_multiple_word": bool(_MULTIPLE_WORD_RE.search(text)),
        "is_seizure_free": text.startswith("seizure free"),
        "is_unknown_exact": text == "unknown",
        "is_no_reference": text == "no seizure frequency reference",
        "has_per": " per " in text,
    }


def _gan_bucket(kind: str, flags: dict[str, bool]) -> str:
    if kind == "frequency" and flags["is_cluster"]:
        return "cluster_burden"
    if kind == "frequency" and flags["is_range"]:
        return "range_rate"
    if kind == "frequency" and flags["is_multiple_word"]:
        return "multiple_word_frequency"
    if kind == "frequency":
        return "ordinary_point_rate"
    if kind == "seizure_free":
        return "seizure_free"
    if kind == "unknown":
        return "unknown_sentinel"
    if kind == "no_reference":
        return "no_reference_sentinel"
    if kind == "unresolved_multiple":
        return "unresolved_multiple"
    return "other"


def _exect_letter_bucket(dx: int, sf: int, rx: int, inv: int) -> str:
    counts = (dx, sf, rx, inv)
    n_families = sum(1 for count in counts if count)
    multi_any = any(count >= 2 for count in counts)
    if n_families == 0:
        return "no_four_family_gold"
    if sf == 0 and n_families >= 1:
        if multi_any:
            return "present_families_multi_mention_empty_sf"
        return "present_families_single_mention_empty_sf"
    if multi_any:
        return "multi_mention_with_sf"
    if n_families >= 3:
        return "broad_single_mention_with_sf"
    if n_families == 1:
        return "single_family_single_mention_with_sf"
    return "sparse_multi_family_single_mention_with_sf"


def _family_lens_table(
    by_family_scores: dict[str, dict[str, float]],
    *,
    n: int,
) -> dict[str, Any]:
    table: dict[str, Any] = {}
    for family in FAMILIES:
        scores = by_family_scores[family]
        low = min(scores.values())
        high = max(scores.values())
        table[family] = {
            "n": n,
            "min": _round(low),
            "max": _round(high),
            "spread": _round(high - low),
            "mean": _round(sum(scores.values()) / len(scores)),
            "by_model": {slug: _round(score) for slug, score in scores.items()},
            "lens": _assign_lens(scores=scores, n=n, min_n=EXECT_MIN_N),
        }
    return table


def _lens_table(
    method_block: dict[str, Any],
    *,
    partition: str,
    score_key: str,
    min_n: int,
    n_key: str = "n",
) -> dict[str, Any]:
    bucket_names: set[str] = set()
    for slug_block in method_block.values():
        bucket_names.update(slug_block[partition].keys())
    table: dict[str, Any] = {}
    for bucket in sorted(bucket_names):
        scores: dict[str, float] = {}
        n_values: list[int] = []
        for slug, slug_block in method_block.items():
            entry = slug_block[partition].get(bucket)
            if not entry or entry.get(score_key) is None:
                continue
            scores[slug] = float(entry[score_key])
            n_values.append(int(entry[n_key]))
        if not scores:
            continue
        n = max(n_values) if n_values else 0
        low = min(scores.values())
        high = max(scores.values())
        table[bucket] = {
            "n": n,
            "min": _round(low),
            "max": _round(high),
            "spread": _round(high - low),
            "mean": _round(sum(scores.values()) / len(scores)),
            "by_model": {slug: _round(score) for slug, score in scores.items()},
            "lens": _assign_lens(scores=scores, n=n, min_n=min_n),
        }
    return table


def _share_table(counts: dict[str, int]) -> dict[str, Any]:
    total = sum(counts.values())
    return {
        "n": total,
        "counts": dict(counts),
        "shares": {
            name: _round(count / total) if total else None
            for name, count in counts.items()
        },
    }


def _mix_delta(
    development: dict[str, int], holdout: dict[str, int]
) -> dict[str, Any]:
    keys = sorted(set(development) | set(holdout))
    dev_total = sum(development.values())
    hold_total = sum(holdout.values())
    share_rows = []
    for key in keys:
        dev_n = int(development.get(key, 0))
        hold_n = int(holdout.get(key, 0))
        dev_share = (dev_n / dev_total) if dev_total else 0.0
        hold_share = (hold_n / hold_total) if hold_total else 0.0
        share_rows.append(
            {
                "bucket": key,
                "development_n": dev_n,
                "holdout_n": hold_n,
                "development_share": _round(dev_share),
                "holdout_share": _round(hold_share),
                "share_delta_holdout_minus_dev": _round(hold_share - dev_share),
            }
        )
    share_rows.sort(
        key=lambda row: (-abs(row["share_delta_holdout_minus_dev"]), row["bucket"])
    )
    return {
        "development_n": dev_total,
        "holdout_n": hold_total,
        "share_rows": share_rows,
        "max_abs_share_delta": _round(
            max(abs(row["share_delta_holdout_minus_dev"]) for row in share_rows)
        )
        if share_rows
        else None,
    }


def _forbidden_paths(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_KEYS or (
                str(key) == "rows" and isinstance(item, (dict, list))
            ):
                found.append(path)
            found.extend(_forbidden_paths(item, path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_forbidden_paths(item, f"{prefix}[{index}]"))
    return found


def _require_paths(paths: list[Path]) -> None:
    missing = [path.relative_to(REPO_ROOT).as_posix() for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "sealed ledgers missing; restore per runbook: " + ", ".join(missing)
        )


def _gan_gold_index() -> dict[int, str]:
    out: dict[int, str] = {}
    for record in load_records_for_split("test"):
        kind = record.gold_label_kind.value
        flags = _gan_shape_flags(record.gold_label)
        out[int(record.source_row_index)] = _gan_bucket(kind, flags)
    return out


def _gan_bucket_scores(
    *,
    correctness: dict[int, bool],
    gold_index: dict[int, str],
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[bool]] = defaultdict(list)
    for index, bucket in gold_index.items():
        if index not in correctness:
            continue
        buckets[bucket].append(correctness[index])
    return {
        name: {
            "n": len(values),
            "correct": sum(values),
            "accuracy": _round(sum(values) / len(values)) if values else None,
        }
        for name, values in sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def _load_gan_llm_correct(slug: str) -> dict[int, bool]:
    path = GAN_LLM_ROOT / slug / "rows.jsonl"
    out: dict[int, bool] = {}
    for row in load_jsonl_rows(path):
        comparison = row.get("comparison")
        out[int(row["source_row_index"])] = bool(
            comparison and comparison.get("purist_correct")
        )
    return out


def _replay_gan_hybrid_correct(slug: str) -> dict[int, bool]:
    source = GAN_HYBRID_SOURCES[slug]
    model, temperature, max_tokens = GAN_HYBRID_MODELS[slug]
    source_rows = load_jsonl_rows(source)
    raw_outputs = {
        int(row["source_row_index"]): str(row.get("raw_output") or "")
        for row in source_rows
    }
    if any(not value for value in raw_outputs.values()):
        raise ValueError(f"{slug} hybrid source has empty raw_output")
    hybrid_structured_events.set_active_prompt_version(
        hybrid_structured_events.PROMPT_VERSION_V0_5
    )
    manifest = load_split_manifest()
    replay_rows, _metadata = hybrid_structured_events.run_split(
        load_records_for_split("test"),
        split="test",
        split_manifest=str(manifest.get("manifest_version", "gan2026_split_v1")),
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        mode="prompt-only",
        dspy_cache=False,
        reuse_raw_outputs=raw_outputs,
        reuse_source=str(source.relative_to(REPO_ROOT).as_posix()),
        repair_config=hybrid_structured_events.StructuredRepairConfig(),
    )
    out: dict[int, bool] = {}
    for row in replay_rows:
        comparison = row.get("comparison")
        out[int(row["source_row_index"])] = bool(
            comparison and comparison.get("purist_correct")
        )
    return out


def _exect_gold_index() -> dict[str, str]:
    out: dict[str, str] = {}
    for letter in load_letters_for_split("test"):
        dx = len(letter.entities("Diagnosis"))
        sf = len(letter.entities("SeizureFrequency"))
        rx = len(letter.entities("Prescription"))
        inv = len(letter.entities("Investigations"))
        out[letter.letter_id] = _exect_letter_bucket(dx, sf, rx, inv)
    return out


def _score_exect_rows(rows: list[dict[str, Any]], *, field: str) -> dict[str, Any]:
    gold_letters: list[ExectLetter] = []
    pred_letters: list[ExectLetter] = []
    for row in rows:
        gold_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(
                    annotation_from_mapping(mention)
                    for mention in row.get("gold_mentions", [])
                ),
            )
        )
        pred_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(
                    annotation_from_mapping(mention) for mention in row.get(field, [])
                ),
            )
        )
    family = clinical_headline_scores(gold_letters, pred_letters)
    overall = aggregate_scores(family.values())
    return {
        "n_letters": len(rows),
        "clinical_fact_f1": overall["f1"],
        "precision": overall["precision"],
        "recall": overall["recall"],
        "by_family": {name: _round(score["f1"]) for name, score in family.items()},
        "counts": {
            name: {
                "pred_count": score["pred_count"],
                "gold_count": score["gold_count"],
                "precision_tp": score["precision_tp"],
                "recall_tp": score["recall_tp"],
            }
            for name, score in family.items()
        },
    }


def _exect_partition_scores(
    rows_by_id: dict[str, dict[str, Any]],
    gold_index: dict[str, str],
    *,
    field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for letter_id, bucket in gold_index.items():
        row = rows_by_id.get(letter_id)
        if row is None:
            continue
        groups[bucket].append(row)
    return {
        name: _score_exect_rows(group_rows, field=field)
        for name, group_rows in sorted(
            groups.items(), key=lambda item: (-len(item[1]), item[0])
        )
    }


def _exect_holdout_section() -> dict[str, Any]:
    panel = json.loads(EXECT_PANEL.read_text(encoding="utf-8"))
    rules_artifact = json.loads(EXECT_RULES_HOLDOUT.read_text(encoding="utf-8"))
    by_slug = {condition["slug"]: condition for condition in panel["conditions"]}
    surfaces: dict[str, dict[str, dict[str, float]]] = {
        "llm": {family: {} for family in FAMILIES},
        "llm_with_rules": {family: {} for family in FAMILIES},
    }
    overall: dict[str, dict[str, float]] = {"llm": {}, "llm_with_rules": {}}
    for slug, _display in MODEL_SPECS:
        condition = by_slug[slug]
        overall["llm"][slug] = float(condition["raw_lane_score"]["f1"])
        overall["llm_with_rules"][slug] = float(condition["clinical_headline"]["f1"])
        for family in FAMILIES:
            surfaces["llm"][family][slug] = float(
                condition["raw_lane_score_by_family"][family]["f1"]
            )
            surfaces["llm_with_rules"][family][slug] = float(
                condition["clinical_headline_by_family"][family]["f1"]
            )
    return {
        "split": "test60",
        "row_count": int(panel["row_count"]),
        "row_policy": "aggregate_only",
        "metric": "four_family_clinical_fact_f1",
        "source": EXECT_PANEL.relative_to(REPO_ROOT).as_posix(),
        "surface_fields": {
            "rules": "clinical_headline_by_family",
            "llm": "raw_lane_score_by_family",
            "llm_with_rules": "clinical_headline_by_family",
        },
        "overall": {
            surface: {
                "min": _round(min(scores.values())),
                "max": _round(max(scores.values())),
                "by_model": {slug: _round(score) for slug, score in scores.items()},
            }
            for surface, scores in overall.items()
        },
        "rules_only": {
            "source": EXECT_RULES_HOLDOUT.relative_to(REPO_ROOT).as_posix(),
            "method": "deterministic_all9_restrict_and_rescore",
            "overall": rules_artifact["clinical_headline"],
            "by_family": rules_artifact["clinical_headline_by_family"],
            "bands": {
                family: (
                    "high" if values["f1"] >= X_MIN
                    else "floor" if values["f1"] <= Z_MAX
                    else "mid"
                )
                for family, values in rules_artifact["clinical_headline_by_family"].items()
            },
            "note": "Single deterministic method; high/mid/floor bands, not x/y/z.",
        },
        "lenses_llm_families": _family_lens_table(
            surfaces["llm"], n=EXECT_HOLDOUT_N
        ),
        "lenses_llm_with_rules_families": _family_lens_table(
            surfaces["llm_with_rules"], n=EXECT_HOLDOUT_N
        ),
    }


def _build_gan_bucket_section() -> dict[str, Any]:
    _require_paths(
        [GAN_LLM_ROOT / slug / "rows.jsonl" for slug, _ in MODEL_SPECS]
        + [GAN_HYBRID_SOURCES[slug] for slug, _ in MODEL_SPECS]
    )
    gold_index = _gan_gold_index()
    floors = json.loads(GAN_FLOORS.read_text(encoding="utf-8"))
    llm_panel = json.loads(GAN_LLM_PANEL.read_text(encoding="utf-8"))
    llm_expected = {
        condition["slug"]: float(condition["purist_accuracy"])
        for condition in llm_panel["conditions"]
    }
    methods: dict[str, Any] = {"llm": {}, "llm_with_rules": {}}
    fidelity: list[dict[str, Any]] = []

    for slug, display in MODEL_SPECS:
        llm_correct = _load_gan_llm_correct(slug)
        hybrid_correct = _replay_gan_hybrid_correct(slug)
        llm_correct_n = sum(llm_correct.values())
        llm_acc = llm_correct_n / len(llm_correct)
        hybrid_correct_n = sum(hybrid_correct.values())
        expected_after = int(floors["test450_aggregate"][slug]["after_purist"])
        expected_llm_correct = int(round(llm_expected[slug] * len(llm_correct)))
        llm_ok = llm_correct_n == expected_llm_correct
        hybrid_ok = hybrid_correct_n == expected_after
        fidelity.append(
            {
                "slug": slug,
                "llm_overall_matches_panel": llm_ok,
                "llm_correct": llm_correct_n,
                "llm_panel_correct": expected_llm_correct,
                "llm_overall": _round(llm_acc),
                "llm_panel": _round(llm_expected[slug]),
                "hybrid_after_purist_matches_floors": hybrid_ok,
                "hybrid_correct": hybrid_correct_n,
                "floors_after_purist": expected_after,
            }
        )
        if not llm_ok or not hybrid_ok:
            raise RuntimeError(f"Gan fidelity gate failed for {slug}: {fidelity[-1]}")
        methods["llm"][slug] = {
            "display_name": display,
            "a_priori_buckets": _gan_bucket_scores(
                correctness=llm_correct, gold_index=gold_index
            ),
            "overall": {"n": len(llm_correct), "accuracy": _round(llm_acc)},
        }
        methods["llm_with_rules"][slug] = {
            "display_name": display,
            "a_priori_buckets": _gan_bucket_scores(
                correctness=hybrid_correct, gold_index=gold_index
            ),
            "overall": {
                "n": len(hybrid_correct),
                "accuracy": _round(hybrid_correct_n / len(hybrid_correct)),
            },
        }

    return {
        "status": "complete",
        "split": "test450",
        "row_count": 450,
        "row_policy": "machine_only_sealed_scoring",
        "metric": "purist_accuracy",
        "llm_source_root": GAN_LLM_ROOT.relative_to(REPO_ROOT).as_posix(),
        "hybrid_scoring": (
            "no_call_reuse_matched_v05_raw_through_current_hybrid_full_stack"
        ),
        "hybrid_source_roots": {
            "hosted": "scratch/holdout/gan2026_matched_v05",
            "local": "scratch/holdout/gan2026_matched_v05_local",
        },
        "methods": methods,
        "lenses_llm_a_priori": _lens_table(
            methods["llm"],
            partition="a_priori_buckets",
            score_key="accuracy",
            min_n=GAN_MIN_N,
        ),
        "lenses_llm_with_rules_a_priori": _lens_table(
            methods["llm_with_rules"],
            partition="a_priori_buckets",
            score_key="accuracy",
            min_n=GAN_MIN_N,
        ),
        "fidelity": fidelity,
    }


def _build_exect_letter_bucket_section() -> dict[str, Any]:
    _require_paths([EXECT_SEALED[slug] for slug, _ in MODEL_SPECS])
    panel = json.loads(EXECT_PANEL.read_text(encoding="utf-8"))
    by_slug = {condition["slug"]: condition for condition in panel["conditions"]}
    gold_index = _exect_gold_index()
    methods: dict[str, Any] = {"llm": {}, "llm_with_rules": {}}
    fidelity: list[dict[str, Any]] = []

    for slug, display in MODEL_SPECS:
        rows = load_jsonl_rows(EXECT_SEALED[slug])
        rows_by_id = {str(row["letter_id"]): row for row in rows}
        for method, field in (
            ("llm", "raw_lane_mentions"),
            ("llm_with_rules", "predicted_mentions"),
        ):
            overall = _score_exect_rows(rows, field=field)
            methods[method][slug] = {
                "display_name": display,
                "prediction_field": field,
                "overall": overall,
                "a_priori_letter_buckets": _exect_partition_scores(
                    rows_by_id, gold_index, field=field
                ),
            }
        hybrid_f1 = float(
            methods["llm_with_rules"][slug]["overall"]["clinical_fact_f1"]
        )
        panel_f1 = float(by_slug[slug]["clinical_headline"]["f1"])
        hybrid_ok = abs(hybrid_f1 - panel_f1) <= FIDELITY_F1_TOL
        fidelity.append(
            {
                "slug": slug,
                "n_letters": len(rows),
                "hybrid_matches_panel_clinical_headline": hybrid_ok,
                "helper_hybrid_f1": _round(hybrid_f1),
                "panel_clinical_headline_f1": _round(panel_f1),
                "llm_helper_f1": _round(
                    methods["llm"][slug]["overall"]["clinical_fact_f1"]
                ),
                "panel_raw_lane_f1": _round(by_slug[slug]["raw_lane_score"]["f1"]),
                "llm_note": (
                    "llm uses clinical_headline helper on raw_lane_mentions; "
                    "absolute F1 may differ from panel raw_lane_score"
                ),
            }
        )
        if not hybrid_ok:
            raise RuntimeError(f"ExECT hybrid fidelity gate failed for {slug}")

    return {
        "status": "complete",
        "split": "test60",
        "row_count": EXECT_HOLDOUT_N,
        "row_policy": "machine_only_sealed_scoring",
        "metric": "four_family_clinical_fact_f1",
        "llm_scoring_note": (
            "llm uses clinical_headline helper on raw_lane_mentions; "
            "absolute F1 may differ from panel raw_lane_score ladder. "
            "Lens assignment still uses the same x/y/z thresholds."
        ),
        "methods": methods,
        "lenses_llm_a_priori": _lens_table(
            methods["llm"],
            partition="a_priori_letter_buckets",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
        "lenses_llm_with_rules_a_priori": _lens_table(
            methods["llm_with_rules"],
            partition="a_priori_letter_buckets",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
        "fidelity": fidelity,
    }


def _gan_overall_holdout(bucket_section: dict[str, Any]) -> dict[str, Any]:
    llm_panel = json.loads(GAN_LLM_PANEL.read_text(encoding="utf-8"))
    floors = json.loads(GAN_FLOORS.read_text(encoding="utf-8"))
    llm_by_model = {
        condition["slug"]: float(condition["purist_accuracy"])
        for condition in llm_panel["conditions"]
    }
    hybrid_by_model = {
        slug: _round(int(block["after_purist"]) / int(block["rows"]))
        for slug, block in floors["test450_aggregate"].items()
    }
    return {
        "split": "test450",
        "row_count": 450,
        "row_policy": "aggregate_only",
        "metric": "purist_accuracy",
        "surfaces": {
            "llm": {
                "source": GAN_LLM_PANEL.relative_to(REPO_ROOT).as_posix(),
                "min": _round(min(llm_by_model.values())),
                "max": _round(max(llm_by_model.values())),
                "by_model": {
                    slug: _round(score) for slug, score in llm_by_model.items()
                },
            },
            "llm_with_rules": {
                "source": GAN_FLOORS.relative_to(REPO_ROOT).as_posix(),
                "note": "current-floors after_purist / rows from test450_aggregate",
                "min": _round(min(hybrid_by_model.values())),
                "max": _round(max(hybrid_by_model.values())),
                "by_model": hybrid_by_model,
            },
        },
        "a_priori_bucket_scores": bucket_section,
    }


def _development_family_lenses() -> dict[str, Any]:
    cut = json.loads(DEV_CATEGORY_CUT.read_text(encoding="utf-8"))
    exect = cut["exectv2"]
    return {
        "source": DEV_CATEGORY_CUT.relative_to(REPO_ROOT).as_posix(),
        "split": exect["split"],
        "lenses_llm_families": exect["lenses_llm_families"],
        "lenses_llm_with_rules_families": exect["lenses_llm_with_rules_families"],
    }


def _lens_transfer(
    development: dict[str, Any], holdout: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for surface, key in (
        ("llm", "lenses_llm_families"),
        ("llm_with_rules", "lenses_llm_with_rules_families"),
    ):
        for family in FAMILIES:
            dev = development[key][family]
            hol = holdout[key][family]
            rows.append(
                {
                    "surface": surface,
                    "family": family,
                    "development_lens": dev["lens"],
                    "holdout_lens": hol["lens"],
                    "development_min_max": [dev["min"], dev["max"]],
                    "holdout_min_max": [hol["min"], hol["max"]],
                    "lens_changed": dev["lens"] != hol["lens"],
                }
            )
    return rows


def _bucket_lens_summary(lenses: dict[str, Any]) -> dict[str, list[str]]:
    summary = {"x": [], "y": [], "z": [], "below_floor": []}
    for name, block in lenses.items():
        lens = block.get("lens")
        if lens is None:
            summary["below_floor"].append(name)
        else:
            summary[str(lens)].append(name)
    return summary


def build_artifact() -> dict[str, Any]:
    gan_tax = json.loads(GAN_TAXONOMY.read_text(encoding="utf-8"))
    exect_tax = json.loads(EXECT_TAXONOMY.read_text(encoding="utf-8"))
    exect_holdout = _exect_holdout_section()
    gan_buckets = _build_gan_bucket_section()
    exect_buckets = _build_exect_letter_bucket_section()
    gan_holdout = _gan_overall_holdout(gan_buckets)
    development_families = _development_family_lenses()
    transfer = _lens_transfer(development_families, exect_holdout)
    gan_mix = _mix_delta(
        gan_tax["validation"]["a_priori_buckets"],
        gan_tax["test"]["a_priori_buckets"],
    )
    exect_mix = _mix_delta(
        exect_tax["dev"]["a_priori_letter_buckets"],
        exect_tax["test"]["a_priori_letter_buckets"],
    )
    gan_hybrid_lenses = gan_buckets["lenses_llm_with_rules_a_priori"]
    gan_hybrid_summary = _bucket_lens_summary(gan_hybrid_lenses)
    exect_hybrid_summary = _bucket_lens_summary(
        exect_buckets["lenses_llm_with_rules_a_priori"]
    )

    artifact: dict[str, Any] = {
        "artifact_id": "six_model.holdout_category_aggregates.v2",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/six_model_holdout_category_aggregates_protocol_2026-08-06.md"
        ),
        "unlock_protocol": (
            "docs/research/six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md"
        ),
        "parent_report": (
            "docs/research/six_model_category_cut_performance_2026-08-06.md"
        ),
        "git": _git_note(),
        "lens_thresholds": {
            "x_min": X_MIN,
            "x_spread_max": X_SPREAD_MAX,
            "z_max": Z_MAX,
            "gan_min_n": GAN_MIN_N,
            "exect_min_n": EXECT_MIN_N,
            "surfaces": ["rules", "llm", "llm_with_rules"],
        },
        "row_policy": {
            "sealed_row_jsonl_machine_scored": True,
            "sealed_row_jsonl_human_inspected": False,
            "public_row_identifiers_allowed": False,
            "failure_examples_allowed": False,
        },
        "exectv2_test60": {
            **exect_holdout,
            "a_priori_letter_bucket_scores": exect_buckets,
        },
        "gan2026_test450": gan_holdout,
        "development_family_lenses_for_transfer": development_families,
        "exect_family_lens_transfer": transfer,
        "gold_mix": {
            "gan_a_priori_buckets": {
                "development_split": "validation/dev750",
                "holdout_split": "test/test450",
                "development": _share_table(gan_tax["validation"]["a_priori_buckets"]),
                "holdout": _share_table(gan_tax["test"]["a_priori_buckets"]),
                "delta": gan_mix,
            },
            "exect_a_priori_letter_buckets": {
                "development_split": "dev/dev140",
                "holdout_split": "test/test60",
                "development": _share_table(
                    exect_tax["dev"]["a_priori_letter_buckets"]
                ),
                "holdout": _share_table(exect_tax["test"]["a_priori_letter_buckets"]),
                "delta": exect_mix,
            },
        },
        "blocked_arms": [],
        "decision": {
            "label": "holdout_bucket_lenses_unlocked",
            "summary": (
                "ExECT holdout family lenses remain from public panels. "
                "Gan a_priori and ExECT letter-bucket holdout scores are unlocked "
                "via machine-only sealed scoring with panel/floors fidelity checks. "
                f"Gan hybrid a_priori lenses: x={_fmt_lens_list(gan_hybrid_summary['x'])}; "
                f"z={_fmt_lens_list(gan_hybrid_summary['z'])}. "
                f"ExECT hybrid letter-bucket lenses with n≥10: "
                f"x={_fmt_lens_list(exect_hybrid_summary['x'])}; "
                f"z={_fmt_lens_list(exect_hybrid_summary['z'])}."
            ),
        },
        "claim_boundary": (
            "Aggregate-only sealed holdout category packaging, including machine-only "
            "a_priori bucket scores from restored sealed ledgers. No human sealed-row "
            "inspection. Not a Decision 0046 rewrite. Not repair or prompt tuning from "
            "holdout."
        ),
    }
    forbidden = _forbidden_paths(artifact)
    if forbidden:
        raise RuntimeError(f"locked-aggregate safety failed: {forbidden}")
    artifact["locked_aggregate_safety"] = {
        "passed": True,
        "forbidden_keys_found": [],
    }
    return artifact


def _fmt_band(block: dict[str, Any]) -> str:
    lens = block.get("lens")
    lens_txt = f" (**{lens}**)" if lens else " (below floor)"
    return f"{block['min']:.2f}–{block['max']:.2f}{lens_txt}"


def _decision_transfer_note(transfer: list[dict[str, Any]]) -> str:
    changed = [
        row
        for row in transfer
        if row["surface"] == "llm_with_rules" and row["lens_changed"]
    ]
    sf = next(
        row
        for row in transfer
        if row["surface"] == "llm_with_rules" and row["family"] == "SeizureFrequency"
    )
    parts = [
        "Holdout family evidence supports the development reading that "
        f"SeizureFrequency remains the ExECT floor "
        f"(holdout hybrid lens **{sf['holdout_lens']}**)."
    ]
    if changed:
        details = ", ".join(
            f"{row['family']} {row['development_lens']}→{row['holdout_lens']}"
            for row in changed
        )
        parts.append(f"Hybrid lens changes vs development: {details}.")
    else:
        parts.append("No hybrid family lens labels change vs development.")
    return " ".join(parts)


def _plain_exect_summary(exect: dict[str, Any]) -> str:
    hybrid = exect["lenses_llm_with_rules_families"]
    llm = exect["lenses_llm_families"]
    hybrid_x = [name for name, block in hybrid.items() if block["lens"] == "x"]
    hybrid_z = [name for name, block in hybrid.items() if block["lens"] == "z"]
    hybrid_y = [name for name, block in hybrid.items() if block["lens"] == "y"]
    llm_z = [name for name, block in llm.items() if block["lens"] == "z"]
    parts = [
        "ExECT `test60` family lenses under `llm_with_rules`: "
        + (
            "strict **x** = " + ", ".join(hybrid_x)
            if hybrid_x
            else "no strict **x**"
        )
        + "; "
        + ("**z** = " + ", ".join(hybrid_z) if hybrid_z else "no **z**")
        + "; "
        + ("**y** = " + ", ".join(hybrid_y) if hybrid_y else "no **y**")
        + "."
    ]
    parts.append(
        "Under `llm`, "
        + ("**z** = " + ", ".join(llm_z) if llm_z else "no **z**")
        + f"; Prescription is **{llm['Prescription']['lens']}**."
    )
    rules = exect["rules_only"]
    parts.append(
        "Independent rules-only bands: "
        + ", ".join(
            f"{family} {_display_score(rules['by_family'][family]['f1'])} "
            f"({rules['bands'][family]})"
            for family in FAMILIES
        )
        + "."
    )
    return " ".join(parts)


def _fmt_lens_list(names: list[str]) -> str:
    return ", ".join(f"`{name}`" for name in names) if names else "none"


def write_report(artifact: dict[str, Any]) -> str:
    exect = artifact["exectv2_test60"]
    gan = artifact["gan2026_test450"]
    gan_buckets = gan["a_priori_bucket_scores"]
    exect_buckets = exect["a_priori_letter_bucket_scores"]
    transfer = artifact["exect_family_lens_transfer"]
    gan_mix = artifact["gold_mix"]["gan_a_priori_buckets"]["delta"]
    exect_mix = artifact["gold_mix"]["exect_a_priori_letter_buckets"]["delta"]
    decision = artifact["decision"]
    gan_hyb = _bucket_lens_summary(gan_buckets["lenses_llm_with_rules_a_priori"])
    gan_llm = _bucket_lens_summary(gan_buckets["lenses_llm_a_priori"])
    exect_hyb = _bucket_lens_summary(exect_buckets["lenses_llm_with_rules_a_priori"])
    exect_llm = _bucket_lens_summary(exect_buckets["lenses_llm_a_priori"])

    lines = [
        "# Sealed holdout category aggregates",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: holdout family + a_priori bucket lenses unlocked; "
        "ExECT rules-only family scores included  ",
        "Protocol: [holdout category aggregates protocol]"
        "(six_model_holdout_category_aggregates_protocol_2026-08-06.md)  ",
        "Unlock protocol: [blocked-arm unlock]"
        "(six_model_holdout_category_aggregates_unlock_protocol_2026-08-06.md)  ",
        "Parent: [category-cut performance]"
        "(six_model_category_cut_performance_2026-08-06.md)  ",
        "Artifact: "
        f"[`experiments/six_model_holdout_category_aggregates_{DATE_STAMP}.json`]"
        f"(../../experiments/six_model_holdout_category_aggregates_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        decision["summary"],
        "",
        _plain_exect_summary(exect),
        "",
        (
            f"Gan `test450` overall Purist: llm "
            f"{gan['surfaces']['llm']['min']:.2f}–{gan['surfaces']['llm']['max']:.2f}; "
            f"llm_with_rules (current floors) "
            f"{gan['surfaces']['llm_with_rules']['min']:.2f}–"
            f"{gan['surfaces']['llm_with_rules']['max']:.2f}."
        ),
        "",
        (
            "Gan hybrid a_priori holdout lenses: "
            f"**x** = {_fmt_lens_list(gan_hyb['x'])}; "
            f"**z** = {_fmt_lens_list(gan_hyb['z'])}; "
            f"**y** = {_fmt_lens_list(gan_hyb['y'])}."
        ),
        "",
        (
            "ExECT hybrid letter-bucket holdout lenses (n≥10): "
            f"**x** = {_fmt_lens_list(exect_hyb['x'])}; "
            f"**z** = {_fmt_lens_list(exect_hyb['z'])}; "
            f"**y** = {_fmt_lens_list(exect_hyb['y'])}."
        ),
        "",
        (
            f"Gold mix share shifts are small "
            f"(Gan max |Δshare| {gan_mix['max_abs_share_delta']}; "
            f"ExECT max |Δshare| {exect_mix['max_abs_share_delta']}), so mix alone "
            "does not explain the ExECT SF holdout floor."
        ),
        "",
        "## ExECT `test60` family lenses",
        "",
        "| Family | rules (band) | llm min–max (lens) | "
        "llm_with_rules min–max (lens) | Dev hybrid lens |",
        "| --- | --- | --- | --- | --- |",
    ]
    dev_hybrid = artifact["development_family_lenses_for_transfer"][
        "lenses_llm_with_rules_families"
    ]
    for family in FAMILIES:
        llm = exect["lenses_llm_families"][family]
        hybrid = exect["lenses_llm_with_rules_families"][family]
        rules = exect["rules_only"]["by_family"][family]
        rules_band = exect["rules_only"]["bands"][family]
        lines.append(
            f"| {family} | **{_display_score(rules['f1'])} ({rules_band})** | "
            f"{_fmt_band(llm)} | {_fmt_band(hybrid)} | "
            f"**{dev_hybrid[family]['lens']}** "
            f"({dev_hybrid[family]['min']:.2f}–{dev_hybrid[family]['max']:.2f}) |"
        )

    lines.extend(
        [
            "",
            "### Overall holdout bands",
            "",
            (
                f"- llm (`raw_lane`): "
                f"{exect['overall']['llm']['min']:.4f}–"
                f"{exect['overall']['llm']['max']:.4f}"
            ),
            (
                f"- llm_with_rules (`clinical_headline`): "
                f"{exect['overall']['llm_with_rules']['min']:.4f}–"
                f"{exect['overall']['llm_with_rules']['max']:.4f}"
            ),
            "",
            "### Lens transfer vs development family cut",
            "",
            "| Surface | Family | Dev lens | Holdout lens | Changed? |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in transfer:
        lines.append(
            f"| {row['surface']} | {row['family']} | **{row['development_lens']}** | "
            f"**{row['holdout_lens']}** | "
            f"{'yes' if row['lens_changed'] else 'no'} |"
        )

    lines.extend(
        [
            "",
            "## Gan `test450` a_priori bucket lenses",
            "",
            "| Bucket | n | llm min–max (lens) | llm_with_rules min–max (lens) |",
            "| --- | ---: | --- | --- |",
        ]
    )
    bucket_names = sorted(
        set(gan_buckets["lenses_llm_a_priori"])
        | set(gan_buckets["lenses_llm_with_rules_a_priori"])
    )
    for bucket in bucket_names:
        llm_block = gan_buckets["lenses_llm_a_priori"].get(bucket)
        hyb_block = gan_buckets["lenses_llm_with_rules_a_priori"].get(bucket)
        n = (hyb_block or llm_block or {}).get("n", 0)
        llm_txt = _fmt_band(llm_block) if llm_block else "—"
        hyb_txt = _fmt_band(hyb_block) if hyb_block else "—"
        lines.append(f"| `{bucket}` | {n} | {llm_txt} | {hyb_txt} |")

    lines.extend(
        [
            "",
            (
                f"llm lenses: **x**={_fmt_lens_list(gan_llm['x'])}; "
                f"**z**={_fmt_lens_list(gan_llm['z'])}; "
                f"**y**={_fmt_lens_list(gan_llm['y'])}; "
                f"below floor={_fmt_lens_list(gan_llm['below_floor'])}."
            ),
            (
                f"hybrid lenses: **x**={_fmt_lens_list(gan_hyb['x'])}; "
                f"**z**={_fmt_lens_list(gan_hyb['z'])}; "
                f"**y**={_fmt_lens_list(gan_hyb['y'])}; "
                f"below floor={_fmt_lens_list(gan_hyb['below_floor'])}."
            ),
            "",
            "### Overall Purist bands",
            "",
            "| Surface | min–max Purist | Source |",
            "| --- | --- | --- |",
            (
                f"| llm | {gan['surfaces']['llm']['min']:.4f}–"
                f"{gan['surfaces']['llm']['max']:.4f} | "
                f"`{gan['surfaces']['llm']['source']}` |"
            ),
            (
                f"| llm_with_rules | {gan['surfaces']['llm_with_rules']['min']:.4f}–"
                f"{gan['surfaces']['llm_with_rules']['max']:.4f} | "
                f"`{gan['surfaces']['llm_with_rules']['source']}` |"
            ),
            "",
            "## ExECT `test60` a_priori letter-bucket lenses",
            "",
            "| Bucket | n | llm min–max (lens) | llm_with_rules min–max (lens) |",
            "| --- | ---: | --- | --- |",
        ]
    )
    letter_names = sorted(
        set(exect_buckets["lenses_llm_a_priori"])
        | set(exect_buckets["lenses_llm_with_rules_a_priori"])
    )
    for bucket in letter_names:
        llm_block = exect_buckets["lenses_llm_a_priori"].get(bucket)
        hyb_block = exect_buckets["lenses_llm_with_rules_a_priori"].get(bucket)
        n = (hyb_block or llm_block or {}).get("n", 0)
        llm_txt = _fmt_band(llm_block) if llm_block else "—"
        hyb_txt = _fmt_band(hyb_block) if hyb_block else "—"
        lines.append(f"| `{bucket}` | {n} | {llm_txt} | {hyb_txt} |")

    lines.extend(
        [
            "",
            (
                f"llm lenses: **x**={_fmt_lens_list(exect_llm['x'])}; "
                f"**z**={_fmt_lens_list(exect_llm['z'])}; "
                f"**y**={_fmt_lens_list(exect_llm['y'])}; "
                f"below floor={_fmt_lens_list(exect_llm['below_floor'])}."
            ),
            (
                f"hybrid lenses: **x**={_fmt_lens_list(exect_hyb['x'])}; "
                f"**z**={_fmt_lens_list(exect_hyb['z'])}; "
                f"**y**={_fmt_lens_list(exect_hyb['y'])}; "
                f"below floor={_fmt_lens_list(exect_hyb['below_floor'])}."
            ),
            "",
            "## Gold mix (shares only)",
            "",
            "### Gan a_priori buckets",
            "",
            "| Bucket | Dev n (share) | Holdout n (share) | Δ share |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in gan_mix["share_rows"]:
        lines.append(
            f"| `{row['bucket']}` | {row['development_n']} "
            f"({row['development_share']:.3f}) | {row['holdout_n']} "
            f"({row['holdout_share']:.3f}) | "
            f"{row['share_delta_holdout_minus_dev']:+.3f} |"
        )

    lines.extend(
        [
            "",
            "### ExECT a_priori letter buckets",
            "",
            "| Bucket | Dev n (share) | Holdout n (share) | Δ share |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for row in exect_mix["share_rows"]:
        lines.append(
            f"| `{row['bucket']}` | {row['development_n']} "
            f"({row['development_share']:.3f}) | {row['holdout_n']} "
            f"({row['holdout_share']:.3f}) | "
            f"{row['share_delta_holdout_minus_dev']:+.3f} |"
        )

    git = artifact["git"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            decision["summary"],
            "",
            _decision_transfer_note(transfer),
            "",
            "## Next",
            "",
            "1. Treat unlocked holdout bucket lenses as aggregate transfer evidence "
            "only; do not open sealed rows for failure catalogs.",
            "2. Operational primary remains the vLLM dev10 task.",
            "",
            "## Method",
            "",
            "- Family lenses: public ExECT stage panel.",
            "- Rules-only family scores: Decision 0046 test60 aggregate.",
            "- Gan llm buckets: sealed llm-only `test450` ledgers.",
            "- Gan hybrid buckets: no-call matched-v0.5 raw replay through current "
            "`hybrid_full_stack`; fidelity to floors `after_purist`.",
            "- ExECT letter buckets: sealed `*_sealed_rows.jsonl` scored with the "
            "clinical-headline helper; hybrid fidelity to panel "
            "`clinical_headline`.",
            "- Gold taxonomies supply mix shares only; bucket membership recomputed "
            "in-process from locked gold loaders.",
            "- Public row identifiers / failure examples: no.",
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
        / f"experiments/six_model_holdout_category_aggregates_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/six_model_holdout_category_aggregates_{REPORT_DATE}.md",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2, sort_keys=False) + "\n")
    report = write_report(artifact)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report)
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    gan = artifact["gan2026_test450"]["a_priori_bucket_scores"]
    exect = artifact["exectv2_test60"]["a_priori_letter_bucket_scores"]
    print(
        "gan hybrid lenses: "
        + ", ".join(
            f"{name}={block['lens']}"
            for name, block in gan["lenses_llm_with_rules_a_priori"].items()
        )
    )
    print(
        "exect hybrid letter lenses: "
        + ", ".join(
            f"{name}={block['lens']}"
            for name, block in exect["lenses_llm_with_rules_a_priori"].items()
        )
    )
    print(f"decision={artifact['decision']['label']}")


if __name__ == "__main__":
    main()
