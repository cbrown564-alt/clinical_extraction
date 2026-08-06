#!/usr/bin/env python3
"""Gan 2026 full a_priori-bucket error catalog with examples.

No new model calls. No locked-test row inspection. See
docs/research/gan2026_category_error_catalog_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_MODE = 2
_MULTIPLE_WORD_RE = re.compile(r"\bmultiple\b", re.IGNORECASE)

_HS_PATH = REPO_ROOT / "scripts/build_six_model_hard_slice_error_modes.py"
_SPEC = importlib.util.spec_from_file_location("hard_slice_error_modes", _HS_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_HS_PATH}")
hs = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(hs)

MODEL_PREFERENCE = (
    "gpt56sol",
    "gpt56luna",
    "gpt41mini",
    "deepseek_v4_flash",
    "qwen36_35b",
    "gemma4_26b",
)

BUCKET_ORDER = (
    "ordinary_point_rate",
    "cluster_burden",
    "seizure_free",
    "range_rate",
    "unknown_sentinel",
    "no_reference_sentinel",
    "unresolved_multiple",
    "multiple_word_frequency",
    "other",
)


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _truncate(text: str | None, limit: int = 280) -> str | None:
    if text is None:
        return None
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _pred_shape(label: str) -> str:
    if not str(label).strip():
        return "empty"
    text = label.lower().strip()
    if text == "unknown":
        return "unknown"
    if text == "no seizure frequency reference":
        return "no_reference"
    if text.startswith("seizure free"):
        return "seizure_free"
    if text in {"multiple", "multiple frequencies", "multiple seizure frequencies"}:
        return "unresolved_multiple"
    if "cluster" in text:
        if "per cluster" in text:
            return "cluster_fullish"
        return "cluster_partial"
    if " to " in text:
        return "range"
    if _MULTIPLE_WORD_RE.search(text) and " per " in text:
        return "multiple_word"
    if " per " in text:
        return "point_rate"
    return "other"


def _error_mode(gold_bucket: str, pred_label: str, comparison: dict[str, Any] | None) -> str:
    if comparison is None or not str(pred_label).strip():
        return "parse_or_call_failure"
    shape = _pred_shape(pred_label)

    if gold_bucket == "cluster_burden":
        if shape == "unknown":
            return "collapse_to_unknown"
        if shape == "no_reference":
            return "collapse_to_no_reference"
        if shape == "seizure_free":
            return "false_seizure_free"
        if shape == "cluster_partial":
            return "incomplete_cluster_grammar"
        if shape == "cluster_fullish":
            return "wrong_cluster_parameters"
        if shape in {"point_rate", "range", "multiple_word"}:
            return "dropped_to_smooth_rate"
        if shape == "empty":
            return "parse_or_call_failure"
        return "other_malformed_or_unparsed"

    if gold_bucket == "seizure_free":
        if shape == "seizure_free":
            return "wrong_seizure_free_phrasing_or_band"
        if shape in {
            "point_rate",
            "range",
            "multiple_word",
            "cluster_partial",
            "cluster_fullish",
        }:
            return "false_active_rate"
        if shape == "unknown":
            return "over_abstain_unknown"
        if shape == "no_reference":
            return "over_abstain_no_reference"
        if shape == "unresolved_multiple":
            return "false_unresolved_multiple"
        return "other_malformed_or_unparsed"

    if gold_bucket == "unknown_sentinel":
        if shape == "unknown":
            return "wrong_unknown_variant_or_unscored"
        if shape == "no_reference":
            return "false_no_reference"
        if shape == "seizure_free":
            return "false_seizure_free"
        if shape in {
            "point_rate",
            "range",
            "multiple_word",
            "cluster_partial",
            "cluster_fullish",
        }:
            return "false_active_rate"
        if shape == "unresolved_multiple":
            return "false_unresolved_multiple"
        return "other_malformed_or_unparsed"

    if gold_bucket == "no_reference_sentinel":
        if shape == "no_reference":
            return "wrong_no_reference_variant_or_unscored"
        if shape == "unknown":
            return "false_unknown"
        if shape == "seizure_free":
            return "false_seizure_free"
        if shape in {
            "point_rate",
            "range",
            "multiple_word",
            "cluster_partial",
            "cluster_fullish",
        }:
            return "false_active_rate"
        return "other_malformed_or_unparsed"

    if gold_bucket == "unresolved_multiple":
        if shape == "unresolved_multiple":
            return "wrong_unresolved_multiple_variant"
        if shape == "unknown":
            return "over_abstain_unknown"
        if shape == "no_reference":
            return "over_abstain_no_reference"
        if shape == "seizure_free":
            return "false_seizure_free"
        if shape in {
            "point_rate",
            "range",
            "multiple_word",
            "cluster_partial",
            "cluster_fullish",
        }:
            return "false_resolved_rate"
        return "other_malformed_or_unparsed"

    if gold_bucket == "range_rate":
        if shape == "range":
            return "wrong_range_bounds_or_band"
        if shape == "point_rate":
            return "range_collapsed_to_point"
        if shape == "multiple_word":
            return "false_multiple_word"
        if shape in {"cluster_partial", "cluster_fullish"}:
            return "false_cluster_structure"
        if shape == "unknown":
            return "over_abstain_unknown"
        if shape == "no_reference":
            return "over_abstain_no_reference"
        if shape == "seizure_free":
            return "false_seizure_free"
        return "other_malformed_or_unparsed"

    # ordinary_point_rate and residual frequency-like buckets
    if shape == "unknown":
        return "over_abstain_unknown"
    if shape == "no_reference":
        return "over_abstain_no_reference"
    if shape == "seizure_free":
        return "false_seizure_free"
    if shape == "range":
        return "false_range"
    if shape == "multiple_word":
        return "false_multiple_word"
    if shape in {"cluster_partial", "cluster_fullish"}:
        return "false_cluster_structure"
    if shape == "point_rate":
        return "wrong_point_rate_selection"
    if shape == "unresolved_multiple":
        return "false_unresolved_multiple"
    return "other_malformed_or_unparsed"


def _attr_index() -> dict[str, dict[int, dict[str, Any]]]:
    attr = json.loads(hs.GAN_ATTR.read_text(encoding="utf-8"))
    out: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in attr["rows"]:
        out[str(row["model_slug"])][int(row["source_row_index"])] = row
    return out


def _pick_examples(
    candidates: list[dict[str, Any]],
    *,
    consensus: set[int],
) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        consensus_rank = 0 if int(row["source_row_index"]) in consensus else 1
        return (consensus_rank, model_rank, str(row["source_row_index"]))

    picked: list[dict[str, Any]] = []
    seen: set[int] = set()
    for row in sorted(candidates, key=sort_key):
        index = int(row["source_row_index"])
        if index in seen:
            continue
        picked.append(row)
        seen.add(index)
        if len(picked) >= EXAMPLES_PER_MODE:
            break
    return picked


def _count_modes(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(str(row["error_mode"]) for row in rows)
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def build_surface(
    *,
    surface: str,
    gold_index: dict[int, dict[str, Any]],
    hybrid: dict[str, dict[int, dict[str, Any]]],
    attr_index: dict[str, dict[int, dict[str, Any]]],
) -> dict[str, Any]:
    by_bucket: dict[str, dict[str, Any]] = {}
    buckets = sorted(
        {meta["a_priori_bucket"] for meta in gold_index.values()},
        key=lambda name: (
            BUCKET_ORDER.index(name) if name in BUCKET_ORDER else 99,
            name,
        ),
    )

    for bucket in buckets:
        indexes = [
            index
            for index, meta in gold_index.items()
            if meta["a_priori_bucket"] == bucket
        ]
        per_model: dict[str, Any] = {}
        wrong_by_model: dict[str, set[int]] = {}
        all_wrong: list[dict[str, Any]] = []
        boundary_wrong: list[dict[str, Any]] = []

        for slug, display in hs.MODEL_SPECS:
            wrong_rows: list[dict[str, Any]] = []
            n_correct = 0
            pragmatic_near = 0
            if surface == "llm":
                rows_by_index = {
                    int(row["source_row_index"]): row
                    for row in hs._read_jsonl(
                        hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl"
                    )
                }
                for index in indexes:
                    row = rows_by_index[index]
                    comparison = row.get("comparison")
                    if comparison and comparison.get("purist_correct"):
                        n_correct += 1
                        continue
                    scored = hs._llm_scored_label(row)
                    boundary = hs._llm_model_boundary_label(row)
                    mode = _error_mode(
                        bucket, scored, comparison if isinstance(comparison, dict) else None
                    )
                    boundary_mode = _error_mode(
                        bucket,
                        boundary,
                        comparison if isinstance(comparison, dict) else None,
                    )
                    decision = row.get("decision_record") or {}
                    hybrid_row = hybrid[slug].get(index) or {}
                    prag = bool(comparison and comparison.get("pragmatic_correct"))
                    if prag:
                        pragmatic_near += 1
                    payload = {
                        "model_slug": slug,
                        "model_display": display,
                        "source_row_index": index,
                        "gold_label": gold_index[index]["gold_label"],
                        "scored_predicted_label": scored,
                        "model_boundary_label": boundary,
                        "error_mode": mode,
                        "model_boundary_error_mode": boundary_mode,
                        "pragmatic_near_miss": prag,
                        "hybrid_rescues": bool(hybrid_row.get("purist_correct")),
                        "hybrid_final_label": hybrid_row.get("final_label"),
                        "selected_evidence": _truncate(decision.get("evidence")),
                        "rationale": _truncate(decision.get("rationale"), 220),
                        "parse_errors": (row.get("parse_errors") or [])[:3],
                        "call_error": row.get("call_error"),
                    }
                    wrong_rows.append(payload)
                    all_wrong.append(payload)
                    boundary_wrong.append(
                        {**payload, "error_mode": boundary_mode}
                    )
            else:
                for index in indexes:
                    hybrid_row = hybrid[slug][index]
                    if hybrid_row["purist_correct"]:
                        n_correct += 1
                        continue
                    attr = attr_index[slug].get(index) or {}
                    scored = str(hybrid_row["final_label"])
                    mode = _error_mode(bucket, scored, {"purist_correct": False})
                    payload = {
                        "model_slug": slug,
                        "model_display": display,
                        "source_row_index": index,
                        "gold_label": gold_index[index]["gold_label"],
                        "scored_predicted_label": scored,
                        "model_boundary_label": attr.get("model_boundary_label")
                        or hybrid_row.get("model_boundary_label"),
                        "error_mode": mode,
                        "selected_evidence": _truncate(attr.get("selected_evidence")),
                        "selected_evidence_exact": attr.get("selected_evidence_exact"),
                        "clinical_subproblem": attr.get("clinical_subproblem"),
                        "model_boundary_purist_correct": attr.get(
                            "model_boundary_purist_correct"
                        ),
                    }
                    wrong_rows.append(payload)
                    all_wrong.append(payload)

            wrong_by_model[slug] = {int(row["source_row_index"]) for row in wrong_rows}
            n_bucket = len(indexes)
            per_model[slug] = {
                "display_name": display,
                "n_bucket": n_bucket,
                "n_correct": n_correct,
                "n_wrong": len(wrong_rows),
                "accuracy": round(n_correct / n_bucket, 4) if n_bucket else None,
                "error_modes": _count_modes(wrong_rows),
                "pragmatic_near_miss_among_wrong": (
                    pragmatic_near if surface == "llm" else None
                ),
            }

        consensus = (
            set.intersection(*wrong_by_model.values()) if wrong_by_model else set()
        )
        modes = sorted({row["error_mode"] for row in all_wrong})
        examples = {
            mode: _pick_examples(
                [row for row in all_wrong if row["error_mode"] == mode],
                consensus=consensus,
            )
            for mode in modes
        }
        bucket_block: dict[str, Any] = {
            "bucket": bucket,
            "n_gold": len(indexes),
            "models": per_model,
            "pooled_wrong_mode_counts": _count_modes(all_wrong),
            "consensus_wrong_all_six": {
                "n": len(consensus),
                "source_row_indexes": sorted(consensus),
            },
            "examples_by_mode": examples,
        }
        if surface == "llm":
            bucket_block["pooled_model_boundary_mode_counts"] = _count_modes(
                boundary_wrong
            )
            boundary_modes = sorted({row["error_mode"] for row in boundary_wrong})
            bucket_block["boundary_examples_by_mode"] = {
                mode: _pick_examples(
                    [row for row in boundary_wrong if row["error_mode"] == mode],
                    consensus=consensus,
                )
                for mode in boundary_modes
            }
        by_bucket[bucket] = bucket_block

    return {
        "surface": surface,
        "split": "dev750",
        "metric": "purist_accuracy",
        "buckets": by_bucket,
    }


def _md_escape(text: str) -> str:
    return text.replace("|", "\\|")


def _render_example(row: dict[str, Any]) -> str:
    evidence = row.get("selected_evidence") or "_(no saved evidence span)_"
    lines = [
        f"- **Row {row['source_row_index']} / {row['model_display']}.** "
        f"Gold `{_md_escape(str(row['gold_label']))}` → scored "
        f"`{_md_escape(str(row['scored_predicted_label']))}`."
    ]
    boundary = row.get("model_boundary_label")
    if boundary and str(boundary) != str(row.get("scored_predicted_label")):
        lines.append(f"  Boundary: `{_md_escape(str(boundary))}`.")
    lines.append(f"  Evidence: {_md_escape(str(evidence))}")
    if row.get("hybrid_rescues") is True:
        lines.append(
            f"  Hybrid rescues to `{_md_escape(str(row.get('hybrid_final_label')))}`."
        )
    if row.get("parse_errors"):
        lines.append(f"  Parse: `{_md_escape(str(row['parse_errors'][:2]))}`.")
    return "\n".join(lines)


def render_report(artifact: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Gan 2026 category error catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development catalog on retained no-call artifacts  ",
        "Protocol: [gan category error catalog protocol]"
        "(gan2026_category_error_catalog_protocol_2026-08-06.md)  ",
        "Parent: [category-cut performance]"
        "(six_model_category_cut_performance_2026-08-06.md)  ",
        f"Artifact: [`experiments/gan2026_category_error_catalog_{DATE_STAMP}.json`]"
        f"(../../experiments/gan2026_category_error_catalog_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "Every Gan a_priori gold bucket has characteristic wrong-answer shapes.",
        "On `llm`, ordinary rates are mostly abstention / wrong-rate / false",
        "seizure-free, and clusters collapse incomplete grammar to unknown or",
        "smooth rates. Rules create easy mass on seizure-free, range, and",
        "no-reference by erasing those llm modes. The hybrid residual that does",
        "**not** cleanly improve is `unknown_sentinel` (false active-rate and",
        "false seizure-free). Clusters remain the practical floor.",
        "",
        "## Method",
        "",
        "- Split: `dev750`. Surfaces: `llm` and `llm_with_rules`.",
        "- Wrongness: Purist false.",
        "- Modes: mutually exclusive predicted-shape buckets (cluster refinements",
        "  kept). `llm` also reports model-boundary modes before format adapter.",
        "- Examples: up to two per observed mode; consensus-wrong and Sol preferred;",
        "  saved evidence spans only; holdout sealed.",
        "- Regenerate: `python scripts/build_gan2026_category_error_catalog.py`.",
        "",
    ]

    for surface in ("llm", "llm_with_rules"):
        surface_block = artifact["surfaces"][surface]
        lines.extend(
            [
                f"## Surface: `{surface}`",
                "",
                "### Bucket accuracy band (six models)",
                "",
                "| Bucket | n | min–max acc | Consensus wrong / n | Top wrong modes (pooled) |",
                "| --- | ---: | --- | --- | --- |",
            ]
        )
        for bucket, block in surface_block["buckets"].items():
            accs = [
                model["accuracy"]
                for model in block["models"].values()
                if model["accuracy"] is not None
            ]
            band = (
                f"{min(accs):.2f}–{max(accs):.2f}" if accs else "n/a"
            )
            top = ", ".join(
                f"{mode} ({count})"
                for mode, count in list(block["pooled_wrong_mode_counts"].items())[:3]
            ) or "_(no wrongs)_"
            lines.append(
                f"| `{bucket}` | {block['n_gold']} | {band} | "
                f"{block['consensus_wrong_all_six']['n']} / {block['n_gold']} | {top} |"
            )
        lines.append("")

        for bucket, block in surface_block["buckets"].items():
            lines.extend(
                [
                    f"### `{bucket}` (n={block['n_gold']})",
                    "",
                    "#### Per-model accuracy and wrongs",
                    "",
                    "| Model | Acc | Wrong | Mode counts |",
                    "| --- | ---: | ---: | --- |",
                ]
            )
            for slug, _display in hs.MODEL_SPECS:
                model = block["models"][slug]
                mode_txt = ", ".join(
                    f"{mode}:{count}"
                    for mode, count in model["error_modes"].items()
                ) or "—"
                lines.append(
                    f"| {model['display_name']} | {model['accuracy']:.4f} | "
                    f"{model['n_wrong']} | {mode_txt} |"
                )
            lines.extend(["", "#### Pooled wrong modes", ""])
            if not block["pooled_wrong_mode_counts"]:
                lines.append("_No Purist wrongs on this surface._")
                lines.append("")
                continue
            lines.extend(
                [
                    "| Mode | Pooled wrongs |",
                    "| --- | ---: |",
                ]
            )
            for mode, count in block["pooled_wrong_mode_counts"].items():
                lines.append(f"| `{mode}` | {count} |")
            lines.extend(["", "#### Examples by mode", ""])
            for mode, examples in block["examples_by_mode"].items():
                lines.append(f"##### `{mode}`")
                lines.append("")
                if not examples:
                    lines.append("_No retained example._")
                else:
                    for example in examples:
                        lines.append(_render_example(example))
                lines.append("")

            if surface == "llm" and block.get("pooled_model_boundary_mode_counts"):
                lines.extend(
                    [
                        "#### Model-boundary modes (diagnostic)",
                        "",
                        "| Mode | Pooled |",
                        "| --- | ---: |",
                    ]
                )
                for mode, count in block["pooled_model_boundary_mode_counts"].items():
                    lines.append(f"| `{mode}` | {count} |")
                lines.append("")
                # Only expand boundary modes that are absent or materially larger
                scored = block["pooled_wrong_mode_counts"]
                for mode, examples in block.get("boundary_examples_by_mode", {}).items():
                    if mode in scored and block["pooled_model_boundary_mode_counts"].get(
                        mode, 0
                    ) <= scored.get(mode, 0):
                        continue
                    lines.append(f"##### Boundary `{mode}`")
                    lines.append("")
                    for example in examples:
                        lines.append(_render_example(example))
                    lines.append("")

    lines.extend(
        [
            "## Claim boundary",
            "",
            "- Development Gan category error catalog on `dev750`.",
            "- Mode labels are analyst heuristics over saved predictions.",
            "- Evidence strings are model-selected spans, not full notes.",
            "- Not sealed holdout competence; DeepSeek `llm` remains pre-0731.",
            "",
        ]
    )
    return "\n".join(lines)


def build_artifact() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()
    hybrid = hs._load_gan_hybrid_rows()
    attr_index = _attr_index()
    return {
        "schema_version": "gan2026.category_error_catalog.v1",
        "date": REPORT_DATE,
        "protocol": "docs/research/gan2026_category_error_catalog_protocol_2026-08-06.md",
        "parent_category_cut": (
            "docs/research/six_model_category_cut_performance_2026-08-06.md"
        ),
        "call_mode": "saved_output_no_call",
        "text_policy": "development_selected_evidence_spans_only",
        "git": _git_note(),
        "models": [
            {"slug": slug, "display_name": display}
            for slug, display in hs.MODEL_SPECS
        ],
        "surfaces": {
            "llm": build_surface(
                surface="llm",
                gold_index=gold_index,
                hybrid=hybrid,
                attr_index=attr_index,
            ),
            "llm_with_rules": build_surface(
                surface="llm_with_rules",
                gold_index=gold_index,
                hybrid=hybrid,
                attr_index=attr_index,
            ),
        },
        "claim_boundary": (
            "Development Gan full-bucket error catalog with examples. "
            "Not holdout competence."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / f"experiments/gan2026_category_error_catalog_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / "docs/research/gan2026_category_error_catalog_2026-08-06.md",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Do not sort_keys: mode-count object order is frequency-ranked.
    args.output.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    report = render_report(artifact)
    args.report.write_text(report, encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"Wrote {args.report}")
    for surface, block in artifact["surfaces"].items():
        for bucket, bucket_block in block["buckets"].items():
            print(
                f"  {surface}.{bucket}: wrong_modes="
                f"{list(bucket_block['pooled_wrong_mode_counts'])}"
            )


if __name__ == "__main__":
    main()
