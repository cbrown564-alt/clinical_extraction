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
    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        consensus_rank = 0 if int(row["source_row_index"]) in consensus else 1
        # Prefer rows where hybrid later rescues when illustrating llm failures.
        rescue_rank = 0 if row.get("hybrid_rescues") is True else 1
        return (
            consensus_rank,
            rescue_rank,
            model_rank,
            str(row["source_row_index"]),
        )

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


def _acc_band(block: dict[str, Any]) -> str:
    accs = [
        model["accuracy"]
        for model in block["models"].values()
        if model["accuracy"] is not None
    ]
    if not accs:
        return "n/a"
    return f"{min(accs):.2f}–{max(accs):.2f}"


def _top_modes(counts: dict[str, int], limit: int = 3) -> str:
    if not counts:
        return "_(none)_"
    return ", ".join(f"`{mode}` ({count})" for mode, count in list(counts.items())[:limit])


def _mode_delta_rows(
    llm_counts: dict[str, int],
    hybrid_counts: dict[str, int],
    *,
    min_either: int = 5,
) -> list[tuple[str, int, int, int]]:
    modes = sorted(
        set(llm_counts) | set(hybrid_counts),
        key=lambda mode: -(llm_counts.get(mode, 0) + hybrid_counts.get(mode, 0)),
    )
    rows: list[tuple[str, int, int, int]] = []
    for mode in modes:
        llm_n = int(llm_counts.get(mode, 0))
        hybrid_n = int(hybrid_counts.get(mode, 0))
        if max(llm_n, hybrid_n) < min_either:
            continue
        rows.append((mode, llm_n, hybrid_n, hybrid_n - llm_n))
    return rows


BUCKET_BLURBS: dict[str, str] = {
    "ordinary_point_rate": (
        "Largest gold mass. Without rules this is a shared floor; rules mostly "
        "erase abstention and many wrong-rate / false-free readings."
    ),
    "cluster_burden": (
        "Practical floor on both surfaces. Format repair hides incomplete "
        "cluster grammar as sentinels; hybrid still leaves smooth-rate and "
        "unknown residuals."
    ),
    "seizure_free": (
        "Rules turn a separator into common competence mainly by clearing "
        "over-abstention."
    ),
    "range_rate": (
        "Same pattern as seizure-free: abstention falls hard; band-edge and "
        "false-free remain the thin residual."
    ),
    "unknown_sentinel": (
        "The hybrid step that does **not** cleanly help: false active-rate and "
        "false seizure-free both rise."
    ),
    "no_reference_sentinel": (
        "llm variance is mostly parse/call failure on one weak model; hybrid "
        "collapses the bucket to near-ceiling."
    ),
    "unresolved_multiple": (
        "Already easy without rules; residual is rare false resolution or "
        "false seizure-free."
    ),
}


def render_report(artifact: dict[str, Any]) -> str:
    llm = artifact["surfaces"]["llm"]["buckets"]
    hybrid = artifact["surfaces"]["llm_with_rules"]["buckets"]

    lines: list[str] = [
        "# Gan 2026 category error catalog",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development catalog with pipeline ablation reading  ",
        "Protocol: [gan category error catalog protocol]"
        "(gan2026_category_error_catalog_protocol_2026-08-06.md)  ",
        "Parent: [category-cut performance]"
        "(six_model_category_cut_performance_2026-08-06.md)  ",
        "Companions: [task-shape framework]"
        "(task_shape_framework_2026-08-06.md), "
        "[hard-slice modes](six_model_hard_slice_error_modes_2026-08-06.md)  ",
        f"Artifact: [`experiments/gan2026_category_error_catalog_{DATE_STAMP}.json`]"
        f"(../../experiments/gan2026_category_error_catalog_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "Category errors are not a flat list of wrong labels. They are a small",
        "set of wrong-answer **shapes**, and different pipeline layers erase,",
        "reshape, or amplify them.",
        "",
        "1. The **raw model label** often emits incomplete cluster grammar,",
        "   illegal fragments, or soft `unknown`.",
        "2. **Format repair** (llm-only scored label) collapses many of those",
        "   fragments into sentinels or invented year totals—so Purist sees",
        "   abstention / wrong-rate even when the model almost said something",
        "   cluster-like.",
        "3. **Semantic rules** (`llm_with_rules`) erase most over-abstention and",
        "   create the easy mass on seizure-free, range, and no-reference. They",
        "   do **not** cleanly fix `unknown_sentinel`, and clusters remain the",
        "   practical floor.",
        "",
        "## Why this document exists",
        "",
        "The [category-cut report]"
        "(six_model_category_cut_performance_2026-08-06.md) shows **which**",
        "gold buckets move under rules. This catalog shows **how**: which wrong",
        "shapes dominate each bucket, and which observable pipeline layer",
        "changes those shapes. Full per-model counts and every retained example",
        "live in the JSON artifact; this page is the readable ablation.",
        "",
        "## Observable ablation layers",
        "",
        "No new calls. Same retained `dev750` rows. Three labels we can already",
        "separate in saved artifacts:",
        "",
        "```mermaid",
        "flowchart LR",
        '  raw["1. Raw model label<br/>before format repair"]',
        '  adapter["2. After format repair<br/>llm scored label"]',
        '  rules["3. After semantic rules<br/>llm_with_rules final"]',
        "  raw --> adapter --> rules",
        "```",
        "",
        "| Layer | What it is | What it typically does to errors |",
        "| --- | --- | --- |",
        "| **1. Raw model label** | What the model selected before llm-only "
        "format repair | Emits incomplete cluster grammar, malformed "
        "fragments, soft `unknown` |",
        "| **2. After format repair** | llm-only scored `final_label` | Erases "
        "illegal fragments into sentinels or year-rate guesses; can *create* "
        "scored wrong-rate / no-reference from an almost-right raw label |",
        "| **3. After semantic rules** | Hybrid final after deterministic "
        "repairs | Clears most abstention and many false-free / wrong-rate "
        "cases on easy mass; can *worsen* unknown-gold by asserting a rate "
        "or free interval |",
        "",
        "This is an ablation over **saved surfaces**, not a claim that every",
        "numbered repair rule was toggled in isolation. Attribute a rescue to",
        "the first layer that changes the answer.",
        "",
        "## Four cases that explain the catalog",
        "",
        "Read these first. Each arrow is one pipeline layer changing the label.",
        "Green end-state = Purist-correct; red = still wrong.",
        "",
        "### A. Format invents a year total; rules rescue",
        "",
        "Ordinary point rate. Gold is a short observation window; the note says",
        "“so far this year.”",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>6 per 4 month"]',
        '  raw["1. Raw model<br/>unknown"]',
        '  fmt["2. Format repair<br/>6 per year"]',
        '  hyb["3. Semantic rules<br/>6 per 4 month"]',
        "  gold -.-> raw",
        "  raw -->|invents YTD total| fmt",
        "  fmt -->|rescues| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class raw,fmt bad;",
        "  class hyb ok;",
        "```",
        "",
        "Row 12788 / Sol. Evidence: six focal seizures “so far this year.”",
        "Lesson: format repair can **create** a scored wrong-rate from soft",
        "`unknown`; rules undo it when the diary/window reading is recoverable.",
        "",
        "### B. Incomplete cluster grammar collapses, then rebuilds",
        "",
        "Cluster burden. Model almost has the answer but omits ",
        "`…, M per cluster`.",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>3 cluster per month,<br/>multiple per cluster"]',
        '  raw["1. Raw model<br/>3 clusters per month"]',
        '  fmt["2. Format repair<br/>unknown"]',
        '  hyb["3. Semantic rules<br/>full cluster label"]',
        "  gold -.-> raw",
        "  raw -->|illegal / incomplete| fmt",
        "  fmt -->|rebuilds from evidence| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class raw,fmt bad;",
        "  class hyb ok;",
        "```",
        "",
        "Row 10097 / Sol. Lesson: the llm-only **z** floor on clusters is partly",
        "a format collapse of almost-right answers—not pure non-comprehension.",
        "",
        "### C. Rules clear ordinary abstention",
        "",
        "Ordinary point rate. Model abstains; hybrid recovers the rate.",
        "",
        "```mermaid",
        "flowchart LR",
        '  gold["Gold<br/>1 per 5 month"]',
        '  raw["1–2. Raw / format<br/>unknown"]',
        '  hyb["3. Semantic rules<br/>1 per 5 month"]',
        "  gold -.-> raw",
        "  raw -->|clears abstention| hyb",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class gold gold;",
        "  class raw bad;",
        "  class hyb ok;",
        "```",
        "",
        "Row 13190 / Sol. This is the mass effect behind −207",
        "`over_abstain_unknown` on ordinary rates.",
        "",
        "### D. Two residuals rules do not fix",
        "",
        "Left: cluster still read as a smooth rate. Right: unknown gold gets a",
        "confident active rate.",
        "",
        "```mermaid",
        "flowchart TB",
        "  subgraph clusterFloor[\"Cluster floor — smooth-rate residual\"]",
        "    direction LR",
        '    cg["Gold<br/>multiple cluster / week,<br/>2 to 3 per cluster"]',
        '    cr["Raw / format / rules<br/>multiple per week"]',
        "    cg -.-> cr",
        "  end",
        "  subgraph unknownHurt[\"Unknown gold — rules keep a false rate\"]",
        "    direction LR",
        '    ug["Gold<br/>unknown"]',
        '    ur["Raw / format / rules<br/>1 per 1 to 2 week"]',
        "    ug -.-> ur",
        "  end",
        "  classDef ok fill:#e8f5e9,stroke:#2e7d32,color:#1b5e20;",
        "  classDef bad fill:#fbe9e7,stroke:#c62828,color:#b71c1c;",
        "  classDef gold fill:#eef0fb,stroke:#5b6abf,color:#1a237e;",
        "  class cg,ug gold;",
        "  class cr,ur bad;",
        "```",
        "",
        "Rows 10434 and 6368 / Sol. Lesson: after rules, the hard remainder is",
        "**selection / convention**, often with evidence already in hand—not",
        "parse failure.",
        "",
        "## Ablation map: which step addresses which mode",
        "",
        "```mermaid",
        "flowchart TB",
        '  raw["Raw model label"]',
        '  fmt["Format repair"]',
        '  rules["Semantic rules"]',
        "  raw --> fmt --> rules",
        '  fmt -->|reshapes| r1["incomplete cluster → sentinel<br/>YTD → year rate"]',
        '  rules -->|erases| r2["over-abstain / wrong-rate / parse"]',
        '  rules -->|amplifies| r3["false rate on unknown gold"]',
        '  rules -->|leaves| r4["cluster smooth-rate residual"]',
        "```",
        "",
        "| Error shape | Main gold homes | Format repair | Semantic rules |",
        "| --- | --- | --- | --- |",
        "| Incomplete cluster grammar / illegal "
        "`N per cluster` | clusters; some ordinary rates | "
        "**Reshapes** → `unknown` / no-reference | "
        "Often rebuilds a legal label when evidence supports it |",
        "| Over-abstain `unknown` | ordinary, free, range | "
        "Sometimes invents a year total instead | "
        "**Clears** most of this mass (−207 ordinary, −43 free, −39 range) |",
        "| Wrong point-rate / wrong range band | ordinary, range | "
        "Can increase wrong-rate by repairing YTD phrases | "
        "Large but incomplete cut (−85 ordinary wrong-rate) |",
        "| False seizure-free on active gold | ordinary, range | "
        "Usually passes through | "
        "Cuts ordinary false-free (−58); thinner residual remains |",
        "| Parse / call failure | weak models, no-reference | "
        "Still empty / unscored | "
        "**Erases** (hybrid path recovers a label) |",
        "| False active-rate / false free on "
        "`unknown` gold | unknown sentinel | "
        "Passes through or slightly worsens | "
        "**Amplifies** (+19 false active-rate, +5 false free) |",
        "| Dropped cluster → smooth rate | clusters | "
        "Passes through | "
        "Does not clear; can become the dominant residual (+22) |",
        "",
        "## Rules lift by bucket (llm → hybrid modes)",
        "",
        "Pooled six-model Purist wrongs. Delta = hybrid − llm (negative means",
        "rules removed that error shape).",
        "",
        "| Bucket | n | llm acc | hybrid acc | Dominant llm modes | What rules do |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]

    for bucket in BUCKET_ORDER:
        if bucket not in llm:
            continue
        llm_block = llm[bucket]
        hybrid_block = hybrid[bucket]
        top_llm = _top_modes(llm_block["pooled_wrong_mode_counts"], limit=2)
        blurb = BUCKET_BLURBS.get(bucket, "")
        lines.append(
            f"| `{bucket}` | {llm_block['n_gold']} | {_acc_band(llm_block)} | "
            f"{_acc_band(hybrid_block)} | {top_llm} | {blurb} |"
        )

    lines.extend(
        [
            "",
            "### Mode deltas worth remembering",
            "",
        ]
    )

    for bucket in (
        "ordinary_point_rate",
        "cluster_burden",
        "seizure_free",
        "range_rate",
        "unknown_sentinel",
    ):
        llm_counts = llm[bucket]["pooled_wrong_mode_counts"]
        hybrid_counts = hybrid[bucket]["pooled_wrong_mode_counts"]
        rows = _mode_delta_rows(llm_counts, hybrid_counts, min_either=8)
        if not rows:
            continue
        lines.extend(
            [
                f"#### `{bucket}`",
                "",
                "| Mode | llm wrongs | hybrid wrongs | Δ |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for mode, llm_n, hybrid_n, delta in rows:
            sign = f"{delta:+d}"
            lines.append(f"| `{mode}` | {llm_n} | {hybrid_n} | {sign} |")
        lines.append("")

    lines.extend(
        [
            "## Format-repair ablation (raw model label → llm scored)",
            "",
            "On `llm` only we also keep the raw model label. The interesting",
            "deltas are where format repair **changes the error shape** before",
            "rules ever run.",
            "",
        ]
    )

    adapter_stories = (
        (
            "ordinary_point_rate",
            (
                "Raw `unknown` falls (−51) while scored wrong-rate rises "
                "(+81): YTD / “so far this year” phrases get repaired into a "
                "year total. Illegal cluster fragments (−28) become "
                "no-reference (+19)."
            ),
        ),
        (
            "cluster_burden",
            (
                "Incomplete cluster grammar (91 in the raw label) disappears "
                "from scored labels; collapse-to-unknown (+78) and no-reference "
                "(+31) absorb it. The floor Purist sees is partly a format "
                "collapse of almost-cluster answers."
            ),
        ),
        (
            "range_rate",
            (
                "False cluster structure in the raw label (8) is cleared; a "
                "few rows become scored abstention or collapsed point rates."
            ),
        ),
        (
            "unknown_sentinel",
            (
                "Wrong unknown variants in the raw label (10) are reshaped "
                "into active rates before scoring (+10 false active-rate)."
            ),
        ),
    )
    for bucket, story in adapter_stories:
        lines.extend([f"### `{bucket}`", "", story, ""])
        llm_block = llm[bucket]
        raw_counts = llm_block.get("pooled_model_boundary_mode_counts") or {}
        scored = llm_block["pooled_wrong_mode_counts"]
        modes = sorted(
            set(raw_counts) | set(scored),
            key=lambda mode: -(raw_counts.get(mode, 0) + scored.get(mode, 0)),
        )
        lines.extend(
            [
                "| Mode | raw model | scored llm | Δ |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for mode in modes:
            b_n = int(raw_counts.get(mode, 0))
            s_n = int(scored.get(mode, 0))
            if max(b_n, s_n) < 8:
                continue
            lines.append(f"| `{mode}` | {b_n} | {s_n} | {s_n - b_n:+d} |")
        lines.append("")

    lines.extend(
        [
            "## Bucket cards",
            "",
            "Accuracy bands are six-model min–max Purist on `dev750`. Mode",
            "counts are pooled wrong row×model cells. Mechanism pictures are",
            "in [Four cases](#four-cases-that-explain-the-catalog) above.",
            "",
        ]
    )

    for bucket in BUCKET_ORDER:
        if bucket not in llm:
            continue
        llm_block = llm[bucket]
        hybrid_block = hybrid[bucket]
        lines.extend(
            [
                f"### `{bucket}` (n={llm_block['n_gold']})",
                "",
                BUCKET_BLURBS.get(bucket, ""),
                "",
                "| Surface | Acc band | Consensus wrong | Top modes |",
                "| --- | --- | ---: | --- |",
                f"| `llm` | {_acc_band(llm_block)} | "
                f"{llm_block['consensus_wrong_all_six']['n']} / {llm_block['n_gold']} | "
                f"{_top_modes(llm_block['pooled_wrong_mode_counts'])} |",
                f"| `llm_with_rules` | {_acc_band(hybrid_block)} | "
                f"{hybrid_block['consensus_wrong_all_six']['n']} / {hybrid_block['n_gold']} | "
                f"{_top_modes(hybrid_block['pooled_wrong_mode_counts'])} |",
                "",
            ]
        )

    lines.extend(
        [
            "## How to explore further",
            "",
            "| Need | Where |",
            "| --- | --- |",
            "| Per-model accuracy and mode counts | JSON "
            f"`surfaces.*.buckets.*.models` in "
            f"[`gan2026_category_error_catalog_{DATE_STAMP}.json`]"
            f"(../../experiments/gan2026_category_error_catalog_{DATE_STAMP}.json) |",
            "| Up to two examples per observed mode × surface | "
            "JSON `examples_by_mode` / `boundary_examples_by_mode` "
            "(raw-label examples; field name is historical) |",
            "| Hard-slice rescue rates on ordinary rates / clusters | "
            "[hard-slice error modes]"
            "(six_model_hard_slice_error_modes_2026-08-06.md) |",
            "| Gold-bucket definitions and x/y/z lenses | "
            "[task-shape](task_shape_framework_2026-08-06.md), "
            "[category-cut](six_model_category_cut_performance_2026-08-06.md) |",
            "| Regenerate this page + artifact | "
            "`python scripts/build_gan2026_category_error_catalog.py` |",
            "",
            "## Method",
            "",
            "- Split: Gan `dev750`. Surfaces: `llm` and `llm_with_rules`.",
            "- Wrongness: Purist false. Modes: mutually exclusive predicted-shape",
            "  buckets (cluster refinements kept).",
            "- Ablation layers: raw model label (llm only), format-repaired",
            "  scored label, hybrid final label.",
            "- Examples in JSON: up to two per observed mode; consensus-wrong",
            "  and Sol preferred; saved evidence spans only; holdout sealed.",
            "",
            "## Claim boundary",
            "",
            "- Development Gan category error catalog on `dev750`.",
            "- Mode labels are analyst heuristics over saved predictions.",
            "- Ablation is across retained surfaces / label stages, not a",
            "  full leave-one-repair-out experiment.",
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
