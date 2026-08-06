#!/usr/bin/env python3
"""Sealed holdout category aggregates from public panels only.

No sealed row JSONL. No failure examples. See
docs/research/six_model_holdout_category_aggregates_protocol_2026-08-06.md.
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
EXECT_HOLDOUT_N = 59

EXECT_PANEL = (
    REPO_ROOT / "experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json"
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


def _exect_holdout_section() -> dict[str, Any]:
    panel = json.loads(EXECT_PANEL.read_text(encoding="utf-8"))
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
        "lenses_llm_families": _family_lens_table(
            surfaces["llm"], n=EXECT_HOLDOUT_N
        ),
        "lenses_llm_with_rules_families": _family_lens_table(
            surfaces["llm_with_rules"], n=EXECT_HOLDOUT_N
        ),
    }


def _gan_overall_holdout() -> dict[str, Any]:
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
                "by_model": {slug: _round(score) for slug, score in llm_by_model.items()},
            },
            "llm_with_rules": {
                "source": GAN_FLOORS.relative_to(REPO_ROOT).as_posix(),
                "note": "current-floors after_purist / rows from test450_aggregate",
                "min": _round(min(hybrid_by_model.values())),
                "max": _round(max(hybrid_by_model.values())),
                "by_model": hybrid_by_model,
            },
        },
        "a_priori_bucket_scores": {
            "status": "blocked",
            "reason": (
                "Sealed Gan test450 prediction ledgers are not present in this "
                "checkout for Phase-C machine-only aggregate scoring. Public "
                "panels retain overall Purist only."
            ),
        },
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


def build_artifact() -> dict[str, Any]:
    gan_tax = json.loads(GAN_TAXONOMY.read_text(encoding="utf-8"))
    exect_tax = json.loads(EXECT_TAXONOMY.read_text(encoding="utf-8"))
    exect_holdout = _exect_holdout_section()
    gan_holdout = _gan_overall_holdout()
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

    artifact: dict[str, Any] = {
        "artifact_id": "six_model.holdout_category_aggregates.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/six_model_holdout_category_aggregates_protocol_2026-08-06.md"
        ),
        "parent_report": (
            "docs/research/six_model_category_cut_performance_2026-08-06.md"
        ),
        "git": _git_note(),
        "lens_thresholds": {
            "x_min": X_MIN,
            "x_spread_max": X_SPREAD_MAX,
            "z_max": Z_MAX,
            "exect_min_n": EXECT_MIN_N,
            "surfaces": ["llm", "llm_with_rules"],
        },
        "row_policy": {
            "sealed_row_jsonl_opened": False,
            "public_row_identifiers_allowed": False,
            "failure_examples_allowed": False,
        },
        "exectv2_test60": exect_holdout,
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
        "blocked_arms": [
            {
                "id": "gan_a_priori_bucket_scores",
                "status": "blocked",
                "reason": gan_holdout["a_priori_bucket_scores"]["reason"],
            },
            {
                "id": "exect_a_priori_letter_bucket_scores",
                "status": "blocked",
                "reason": (
                    "Sealed ExECT test60 prediction JSONL is not present for "
                    "Phase-C machine-only letter-bucket aggregate scoring. "
                    "Family F1 from the public stage panel is available."
                ),
            },
        ],
        "decision": {
            "label": "partial_answer_family_holdout_plus_mix",
            "summary": (
                "ExECT holdout family lenses are answered from public aggregates. "
                "Gan a_priori holdout bucket scores remain blocked without sealed "
                "ledgers. Gold mix share shifts are small."
            ),
        },
        "claim_boundary": (
            "Aggregate-only sealed holdout category packaging from retained public "
            "panels and gold taxonomy. No sealed row inspection. Not a Decision "
            "0046 rewrite. Not Gan a_priori holdout competence by bucket."
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
    return f"{block['min']:.2f}–{block['max']:.2f} (**{block['lens']}**)"


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
    return " ".join(parts)


def write_report(artifact: dict[str, Any]) -> str:
    exect = artifact["exectv2_test60"]
    gan = artifact["gan2026_test450"]
    transfer = artifact["exect_family_lens_transfer"]
    gan_mix = artifact["gold_mix"]["gan_a_priori_buckets"]["delta"]
    exect_mix = artifact["gold_mix"]["exect_a_priori_letter_buckets"]["delta"]
    decision = artifact["decision"]

    lines = [
        "# Sealed holdout category aggregates",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: aggregate-only holdout packaging; Gan a_priori bucket scores blocked  ",
        "Protocol: [holdout category aggregates protocol]"
        "(six_model_holdout_category_aggregates_protocol_2026-08-06.md)  ",
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
            f"Gan `test450` overall Purist only: llm "
            f"{gan['surfaces']['llm']['min']:.2f}–{gan['surfaces']['llm']['max']:.2f}; "
            f"llm_with_rules (current floors) "
            f"{gan['surfaces']['llm_with_rules']['min']:.2f}–"
            f"{gan['surfaces']['llm_with_rules']['max']:.2f}. "
            "Per a_priori bucket scores are blocked."
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
        "| Family | llm min–max (lens) | llm_with_rules min–max (lens) | Dev hybrid lens |",
        "| --- | --- | --- | --- |",
    ]
    dev_hybrid = artifact["development_family_lenses_for_transfer"][
        "lenses_llm_with_rules_families"
    ]
    for family in FAMILIES:
        llm = exect["lenses_llm_families"][family]
        hybrid = exect["lenses_llm_with_rules_families"][family]
        lines.append(
            f"| {family} | {_fmt_band(llm)} | {_fmt_band(hybrid)} | "
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
            "## Gan `test450` overall only",
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
            "Per-model values are in the artifact. a_priori bucket × model scores: "
            f"**{gan['a_priori_bucket_scores']['status']}** — "
            f"{gan['a_priori_bucket_scores']['reason']}",
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
            "1. To unlock Gan a_priori / ExECT letter-bucket holdout scores: restore "
            "sealed prediction ledgers and run a Phase-C machine-only aggregate "
            "extension of this builder (still no public row content).",
            "2. Do not open sealed rows for failure catalogs.",
            "3. Operational primary remains the vLLM dev10 task.",
            "",
            "## Method",
            "",
            "- Sources: public ExECT stage panel, Gan llm-only panel, Gan floors "
            "replay summary, gold taxonomies, development category-cut lenses.",
            "- Sealed row JSONL opened: no.",
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
    hybrid = artifact["exectv2_test60"]["lenses_llm_with_rules_families"]
    print(
        "exect hybrid lenses: "
        + ", ".join(f"{name}={block['lens']}" for name, block in hybrid.items())
    )
    print(f"decision={artifact['decision']['label']}")


if __name__ == "__main__":
    main()
