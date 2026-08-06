#!/usr/bin/env python3
"""Cut retained six-model development performance by gold task categories.

No new model calls. No locked-test row inspection. See
docs/research/six_model_category_cut_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
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
from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records_for_split
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
_MULTIPLE_WORD_RE = re.compile(r"\bmultiple\b", re.IGNORECASE)


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


def _sf_mention_bucket(attributes: dict[str, str]) -> str:
    has_count = any(
        key in attributes
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    )
    has_cadence = "TimePeriod" in attributes or any(
        "TimePeriod" in key for key in attributes
    )
    has_change = "FrequencyChange" in attributes
    has_anchor = any(
        key in attributes
        for key in (
            "PointInTime",
            "TimeSince_or_TimeOfEvent",
            "YearDate",
            "MonthDate",
            "DayDate",
        )
    )
    if has_count and has_cadence:
        return "numeric_cadence_rate"
    if has_count and has_anchor and not has_cadence:
        return "count_in_named_window"
    if has_change and not has_count:
        return "qualitative_frequency_change"
    if has_change and has_count:
        return "numeric_plus_frequency_change"
    if has_anchor and not has_count:
        return "temporal_anchor_without_count"
    if has_count:
        return "count_without_cadence_or_anchor"
    return "sparse_or_other"

MODEL_SPECS = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)

GAN_LLM_ONLY_DIR = REPO_ROOT / "experiments/gan2026_six_model_validation_20260718"
GAN_ATTR = REPO_ROOT / "experiments/gan2026_matched_v05_dev750_attribution_20260727.json"
GAN_FLOORS_PATCH = REPO_ROOT / (
    "experiments/gan2026_six_model_current_floors_replay_20260731/"
    "dev750_changed_rows.jsonl"
)
EXECT_JSONL = {
    "gpt41mini": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.jsonl",
    "gpt56luna": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715.jsonl",
    "gpt56sol": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.jsonl",
    "deepseek_v4_flash": REPO_ROOT
    / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl",
    "qwen36_35b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.jsonl",
    "gemma4_26b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.jsonl",
}
PANEL_PATH = REPO_ROOT / "experiments/six_model_final_panel_20260803/panel_aggregate.json"

GAN_MIN_N = 20
EXECT_MIN_N = 10
X_MIN = 0.85
X_SPREAD_MAX = 0.08
Z_MAX = 0.75


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _round(value: float) -> float:
    return round(float(value), 4)


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


def _gan_gold_index() -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for record in load_records_for_split("validation"):
        kind = record.gold_label_kind.value
        flags = _gan_shape_flags(record.gold_label)
        out[int(record.source_row_index)] = {
            "a_priori_bucket": _gan_bucket(kind, flags),
            "boundary_band": boundary_band(record.gold_monthly_frequency),
            "gold_label_kind": kind,
        }
    return out


def _load_gan_llm_correct(slug: str) -> dict[int, bool]:
    path = GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl"
    out: dict[int, bool] = {}
    for row in _read_jsonl(path):
        comparison = row.get("comparison")
        # Null comparison (parse/call failure) counts as incorrect, matching panel.
        out[int(row["source_row_index"])] = bool(
            comparison and comparison.get("purist_correct")
        )
    return out


def _load_gan_hybrid_correct() -> dict[str, dict[int, bool]]:
    attr = json.loads(GAN_ATTR.read_text(encoding="utf-8"))
    patch: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in _read_jsonl(GAN_FLOORS_PATCH):
        patch[str(row["slug"])][int(row["source_row_index"])] = row
    out: dict[str, dict[int, bool]] = defaultdict(dict)
    for row in attr["rows"]:
        slug = str(row["model_slug"])
        index = int(row["source_row_index"])
        delta = patch[slug].get(index)
        if delta is not None:
            out[slug][index] = bool(delta["after_purist"])
        else:
            out[slug][index] = bool(row["final_purist_correct"])
    return out


def _gan_bucket_scores(
    *,
    correctness: dict[int, bool],
    gold_index: dict[int, dict[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    buckets: dict[str, list[bool]] = defaultdict(list)
    for index, meta in gold_index.items():
        if index not in correctness:
            continue
        buckets[str(meta[field])].append(correctness[index])
    return {
        name: {
            "n": len(values),
            "correct": sum(values),
            "accuracy": _round(sum(values) / len(values)) if values else None,
        }
        for name, values in sorted(buckets.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def build_gan_section() -> dict[str, Any]:
    gold_index = _gan_gold_index()
    hybrid = _load_gan_hybrid_correct()
    methods: dict[str, Any] = {"llm": {}, "llm_with_rules": {}}
    for slug, display in MODEL_SPECS:
        llm_correct = _load_gan_llm_correct(slug)
        hybrid_correct = hybrid[slug]
        methods["llm"][slug] = {
            "display_name": display,
            "a_priori_buckets": _gan_bucket_scores(
                correctness=llm_correct,
                gold_index=gold_index,
                field="a_priori_bucket",
            ),
            "boundary_band": _gan_bucket_scores(
                correctness=llm_correct,
                gold_index=gold_index,
                field="boundary_band",
            ),
            "overall": {
                "n": len(llm_correct),
                "accuracy": _round(sum(llm_correct.values()) / len(llm_correct)),
            },
        }
        methods["llm_with_rules"][slug] = {
            "display_name": display,
            "a_priori_buckets": _gan_bucket_scores(
                correctness=hybrid_correct,
                gold_index=gold_index,
                field="a_priori_bucket",
            ),
            "boundary_band": _gan_bucket_scores(
                correctness=hybrid_correct,
                gold_index=gold_index,
                field="boundary_band",
            ),
            "overall": {
                "n": len(hybrid_correct),
                "accuracy": _round(sum(hybrid_correct.values()) / len(hybrid_correct)),
            },
        }

    return {
        "split": "dev750",
        "metric": "purist_accuracy",
        "surfaces": ["llm", "llm_with_rules"],
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
    }


def _exect_gold_index() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for letter in load_letters_for_split("dev"):
        dx = len(letter.entities("Diagnosis"))
        sf = len(letter.entities("SeizureFrequency"))
        rx = len(letter.entities("Prescription"))
        inv = len(letter.entities("Investigations"))
        if dx == 0:
            dx_mult = "absent"
        elif dx == 1:
            dx_mult = "single"
        else:
            dx_mult = "multi"
        sf_buckets = {
            _sf_mention_bucket(annotation.attributes)
            for annotation in letter.entities("SeizureFrequency")
        }
        out[letter.letter_id] = {
            "a_priori_letter_bucket": _exect_letter_bucket(dx, sf, rx, inv),
            "diag_letter_multiplicity": dx_mult,
            "sf_empty": sf == 0,
            "sf_mention_buckets": sorted(sf_buckets),
        }
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
                    annotation_from_mapping(mention) for mention in row.get("gold_mentions", [])
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
    gold_index: dict[str, dict[str, Any]],
    *,
    field: str,
    partition: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for letter_id, meta in gold_index.items():
        row = rows_by_id.get(letter_id)
        if row is None:
            continue
        if partition == "sf_mention_letter_groups":
            buckets = meta["sf_mention_buckets"]
            if not buckets:
                groups["no_sf_gold"].append(row)
            else:
                for bucket in buckets:
                    groups[bucket].append(row)
            continue
        if partition == "sf_empty":
            key = "empty_sf" if meta["sf_empty"] else "has_sf"
        else:
            key = str(meta[partition])
        groups[key].append(row)
    return {
        name: _score_exect_rows(group_rows, field=field)
        for name, group_rows in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
    }


def build_exect_section() -> dict[str, Any]:
    gold_index = _exect_gold_index()
    methods: dict[str, Any] = {"llm": {}, "llm_with_rules": {}}
    for slug, display in MODEL_SPECS:
        rows = _read_jsonl(EXECT_JSONL[slug])
        rows_by_id = {str(row["letter_id"]): row for row in rows}
        method_fields = (
            ("llm", "raw_lane_mentions"),
            ("llm_with_rules", "predicted_mentions"),
        )
        for method, field in method_fields:
            methods[method][slug] = {
                "display_name": display,
                "prediction_field": field,
                "overall": _score_exect_rows(rows, field=field),
                "a_priori_letter_buckets": _exect_partition_scores(
                    rows_by_id, gold_index, field=field, partition="a_priori_letter_bucket"
                ),
                "diag_letter_multiplicity": _exect_partition_scores(
                    rows_by_id, gold_index, field=field, partition="diag_letter_multiplicity"
                ),
                "sf_empty": _exect_partition_scores(
                    rows_by_id, gold_index, field=field, partition="sf_empty"
                ),
                "sf_mention_letter_groups": _exect_partition_scores(
                    rows_by_id,
                    gold_index,
                    field=field,
                    partition="sf_mention_letter_groups",
                ),
            }
    return {
        "split": "dev140",
        "metric": "four_family_clinical_fact_f1",
        "surfaces": ["llm", "llm_with_rules"],
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
        "lenses_llm_families": _exect_family_lens_table(methods["llm"]),
        "lenses_llm_with_rules_families": _exect_family_lens_table(
            methods["llm_with_rules"]
        ),
        "lenses_llm_sf_empty": _lens_table(
            methods["llm"],
            partition="sf_empty",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
        "lenses_llm_with_rules_sf_empty": _lens_table(
            methods["llm_with_rules"],
            partition="sf_empty",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
        "lenses_llm_diag_multiplicity": _lens_table(
            methods["llm"],
            partition="diag_letter_multiplicity",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
        "lenses_llm_with_rules_diag_multiplicity": _lens_table(
            methods["llm_with_rules"],
            partition="diag_letter_multiplicity",
            score_key="clinical_fact_f1",
            min_n=EXECT_MIN_N,
            n_key="n_letters",
        ),
    }


def _exect_family_lens_table(method_block: dict[str, Any]) -> dict[str, Any]:
    families = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
    table: dict[str, Any] = {}
    for family in families:
        scores = {
            slug: float(block["overall"]["by_family"][family])
            for slug, block in method_block.items()
        }
        low = min(scores.values())
        high = max(scores.values())
        table[family] = {
            "n": 140,
            "min": _round(low),
            "max": _round(high),
            "spread": _round(high - low),
            "mean": _round(sum(scores.values()) / len(scores)),
            "by_model": {slug: _round(score) for slug, score in scores.items()},
            "lens": _assign_lens(scores=scores, n=140, min_n=EXECT_MIN_N),
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


def _panel_checks(gan: dict[str, Any], exect: dict[str, Any]) -> dict[str, Any]:
    panel = json.loads(PANEL_PATH.read_text(encoding="utf-8"))
    by_slug = {condition["slug"]: condition for condition in panel["conditions"]}
    checks = []
    for slug, _display in MODEL_SPECS:
        panel_gan = by_slug[slug]["gan2026"]["dev750"]
        panel_exect = by_slug[slug]["exectv2"]["dev140"]
        gan_hybrid = gan["methods"]["llm_with_rules"][slug]["overall"]["accuracy"]
        gan_llm = gan["methods"]["llm"][slug]["overall"]["accuracy"]
        exect_hybrid = exect["methods"]["llm_with_rules"][slug]["overall"]["clinical_fact_f1"]
        checks.append(
            {
                "slug": slug,
                "gan_llm_match": abs(gan_llm - panel_gan["llm_purist_accuracy"]) < 1e-3,
                "gan_llm_with_rules_match": abs(
                    gan_hybrid - panel_gan["llm_with_rules_purist_accuracy"]
                )
                < 1e-3,
                "exect_llm_with_rules_match": abs(
                    exect_hybrid - panel_exect["llm_with_rules_clinical_fact_f1"]
                )
                < 1e-3,
                "gan_llm": gan_llm,
                "gan_llm_panel": panel_gan["llm_purist_accuracy"],
                "gan_llm_with_rules": gan_hybrid,
                "gan_llm_with_rules_panel": panel_gan["llm_with_rules_purist_accuracy"],
                "exect_llm_with_rules": exect_hybrid,
                "exect_llm_with_rules_panel": panel_exect["llm_with_rules_clinical_fact_f1"],
                "exect_llm_helper": exect["methods"]["llm"][slug]["overall"]["clinical_fact_f1"],
                "exect_llm_panel_raw_lane": panel_exect["llm_clinical_fact_f1"],
            }
        )
    return {
        "panel_path": str(PANEL_PATH.relative_to(REPO_ROOT)),
        "checks": checks,
        "all_gan_and_exect_hybrid_match": all(
            item["gan_llm_match"]
            and item["gan_llm_with_rules_match"]
            and item["exect_llm_with_rules_match"]
            for item in checks
        ),
    }


def build_artifact() -> dict[str, Any]:
    gan = build_gan_section()
    exect = build_exect_section()
    return {
        "artifact_id": "six_model.category_cut_performance.v1",
        "date": REPORT_DATE,
        "protocol": "docs/research/six_model_category_cut_protocol_2026-08-06.md",
        "parent_framework": "docs/research/task_shape_framework_2026-08-06.md",
        "claim_boundary": (
            "Development category cuts from retained no-call artifacts. "
            "No locked-test row inspection. Not Decision 0046 method-fill rewrite."
        ),
        "lens_thresholds": {
            "surfaces": ["llm", "llm_with_rules"],
            "x_min": X_MIN,
            "x_spread_max": X_SPREAD_MAX,
            "z_max": Z_MAX,
            "gan_min_n": GAN_MIN_N,
            "exect_min_n": EXECT_MIN_N,
        },
        "gan2026": gan,
        "exectv2": exect,
        "panel_reconstruction": _panel_checks(gan, exect),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / f"experiments/six_model_category_cut_performance_{DATE_STAMP}.json",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output.relative_to(REPO_ROOT)}")
    print("panel_match", artifact["panel_reconstruction"]["all_gan_and_exect_hybrid_match"])
    for surface_key, label in (
        ("lenses_llm_a_priori", "gan llm"),
        ("lenses_llm_with_rules_a_priori", "gan llm_with_rules"),
    ):
        print(
            label,
            {
                name: entry["lens"]
                for name, entry in artifact["gan2026"][surface_key].items()
            },
        )
    for surface_key, label in (
        ("lenses_llm_families", "exect llm families"),
        ("lenses_llm_with_rules_families", "exect llm_with_rules families"),
    ):
        print(
            label,
            {
                name: entry["lens"]
                for name, entry in artifact["exectv2"][surface_key].items()
            },
        )


if __name__ == "__main__":
    main()
