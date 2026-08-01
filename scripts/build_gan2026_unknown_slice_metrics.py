#!/usr/bin/env python
"""Build Purist unknown-slice metrics for Gan matched v0.5 development traces.

Development-only. Does not read sealed test450 row predictions for analysis.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)

UNK = "seizure_freq_unknown"
ZERO = "currently_no_seizure"
ROOT = Path(__file__).resolve().parents[1]


def label_purist(label: str | None) -> str | None:
    if label is None or not str(label).strip():
        return None
    try:
        monthly = label_to_frequency_record(str(label)).monthly_frequency
    except Exception:
        return None
    return str(map_purist(monthly))


def load_gold(row_trace_path: Path) -> dict[int, dict[str, Any]]:
    gold: dict[int, dict[str, Any]] = {}
    with row_trace_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            idx = int(row["source_row_index"])
            ref = row.get("reference") or {}
            cmp = row.get("comparison") or {}
            scoring = ((row.get("row_trace") or {}).get("scoring") or {})
            purist = cmp.get("gold_purist_category") or scoring.get(
                "gold_purist_category"
            )
            monthly = ref.get("gold_monthly_frequency")
            if monthly is None:
                monthly = scoring.get("gold_monthly_frequency")
            gold[idx] = {
                "gold_label": ref.get("gold_normalized_label") or ref.get("gold_label"),
                "gold_purist": purist,
                "gold_monthly": monthly,
                "unknown": purist == UNK or monthly == 1000 or monthly == 1000.0,
            }
    return gold


def evaluate(preds: dict[int, str | None], gold: dict[int, dict[str, Any]]) -> dict[str, Any]:
    tp = fp = fn = 0
    overread = false_sf = false_abstain = 0
    gold_unk = pred_unk = 0
    overread_top: Counter[str] = Counter()
    fn_top: Counter[str] = Counter()
    for idx, g in gold.items():
        pred = preds.get(idx)
        pred_band = label_purist(pred)
        g_unk = bool(g["unknown"])
        p_unk = pred_band == UNK
        if g_unk:
            gold_unk += 1
        if p_unk:
            pred_unk += 1
        if g_unk and p_unk:
            tp += 1
        elif (not g_unk) and p_unk:
            fp += 1
            false_abstain += 1
        elif g_unk and not p_unk:
            fn += 1
            if pred_band == ZERO:
                false_sf += 1
            elif pred_band and pred_band != UNK:
                overread += 1
                overread_top[f"{pred} => {pred_band}"] += 1
            fn_top[str(pred or "<empty>")] += 1
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {
        "gold_unknown": gold_unk,
        "pred_unknown_band": pred_unk,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "unknown_gold_accuracy": round(tp / gold_unk, 4) if gold_unk else None,
        "overread_n": overread,
        "overread_rate": round(overread / gold_unk, 4) if gold_unk else None,
        "false_seizure_free_n": false_sf,
        "false_seizure_free_rate": round(false_sf / gold_unk, 4) if gold_unk else None,
        "false_abstention_n": false_abstain,
        "false_abstention_rate": round(false_abstain / (len(gold) - gold_unk), 4)
        if len(gold) > gold_unk
        else None,
        "overread_top": overread_top.most_common(10),
        "fn_pred_top": fn_top.most_common(10),
    }


def gate_status(arm: str, metrics: dict[str, Any]) -> dict[str, Any]:
    acc = metrics["unknown_gold_accuracy"]
    overread = metrics["overread_rate"]
    fsf = metrics["false_seizure_free_rate"]
    if arm == "llm_only":
        checks = {
            "unknown_accuracy_ge_0_80": acc is not None and acc >= 0.80,
            "overread_le_0_05": overread is not None and overread <= 0.05,
        }
    else:
        checks = {
            "unknown_accuracy_ge_0_90": acc is not None and acc >= 0.90,
            "overread_le_0_05": overread is not None and overread <= 0.05,
            "false_seizure_free_le_0_03": fsf is not None and fsf <= 0.03,
        }
    return {"passed": all(checks.values()), "checks": checks}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--attribution",
        type=Path,
        default=ROOT
        / "experiments/gan2026_matched_v05_dev750_attribution_20260727.json",
    )
    parser.add_argument(
        "--gold-rows",
        type=Path,
        default=ROOT
        / "scratch/validation/gan2026_matched_v05_dev750_20260727"
        / "gpt41mini/validation750.rows.jsonl",
    )
    parser.add_argument(
        "--floors-changed",
        type=Path,
        default=ROOT
        / "experiments/gan2026_six_model_current_floors_replay_20260731"
        / "dev750_changed_rows.jsonl",
    )
    parser.add_argument(
        "--model-slug",
        action="append",
        default=None,
        help="Restrict to one or more model slugs (default: deepseek_v4_flash).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT
        / "experiments/gan2026_deepseek_unknown_competence_baseline_dev750_20260731.json",
    )
    args = parser.parse_args()
    slugs = args.model_slug or ["deepseek_v4_flash"]

    attr = json.loads(args.attribution.read_text(encoding="utf-8"))
    gold = load_gold(args.gold_rows)
    by_model: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in attr["rows"]:
        if row["model_slug"] in slugs:
            by_model[row["model_slug"]].append(row)

    floors_by_model: dict[str, dict[int, str]] = defaultdict(dict)
    if args.floors_changed.exists():
        with args.floors_changed.open(encoding="utf-8") as handle:
            for line in handle:
                row = json.loads(line)
                slug = row.get("slug") or row.get("model_slug")
                if slug in slugs:
                    floors_by_model[slug][int(row["source_row_index"])] = row[
                        "after_label"
                    ]

    models_out: dict[str, Any] = {}
    for slug in slugs:
        rows = by_model.get(slug, [])
        if not rows:
            raise SystemExit(f"No attribution rows for model_slug={slug}")
        llm_only = {
            int(r["source_row_index"]): r["model_boundary_label"] for r in rows
        }
        llm_rules = {int(r["source_row_index"]): r["final_label"] for r in rows}
        floors = dict(llm_rules)
        floors.update(floors_by_model.get(slug, {}))
        overall_boundary = sum(1 for r in rows if r["model_boundary_purist_correct"])
        overall_final = sum(1 for r in rows if r["final_purist_correct"])
        m_only = evaluate(llm_only, gold)
        m_rules = evaluate(llm_rules, gold)
        m_floors = evaluate(floors, gold)
        models_out[slug] = {
            "n": len(rows),
            "route_caveat": (
                "Retained matched v0.5 DeepSeek condition is hosted V4 Flash API; "
                "not a local partner-server runtime."
                if slug == "deepseek_v4_flash"
                else "See panel configuration for route."
            ),
            "overall_purist_llm_only": overall_boundary,
            "overall_purist_llm_with_rules_frozen_panel": overall_final,
            "llm_only": {
                "metrics": m_only,
                "collaboration_gate": gate_status("llm_only", m_only),
            },
            "llm_with_rules_frozen_panel": {
                "metrics": m_rules,
                "collaboration_gate": gate_status("llm_with_rules", m_rules),
            },
            "llm_with_rules_final_ruleset_proxy": {
                "metrics": m_floors,
                "collaboration_gate": gate_status("llm_with_rules", m_floors),
                "note": (
                    "Frozen-panel finals with final-ruleset changed labels overlaid "
                    "from no-call floors replay."
                ),
            },
        }

    payload = {
        "schema_version": "gan2026.unknown_slice_metrics.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "protocol": (
            "docs/experiments/gan2026/"
            "gan2026_deepseek_unknown_competence_protocol_2026-07-31.md"
        ),
        "thread": "docs/research/gan2026_deepseek_unknown_competence_thread_2026-07-31.md",
        "dataset": "Gan 2026 synthetic clinical letters",
        "split": "validation750",
        "split_manifest": "gan2026_split_v1",
        "scorer": "Gan Purist unknown-band slice",
        "gold_unknown_count": sum(1 for g in gold.values() if g["unknown"]),
        "n": len(gold),
        "sources": {
            "attribution": str(args.attribution.relative_to(ROOT)).replace("\\", "/"),
            "gold_rows": str(args.gold_rows.relative_to(ROOT)).replace("\\", "/"),
            "floors_changed": str(args.floors_changed.relative_to(ROOT)).replace(
                "\\", "/"
            )
            if args.floors_changed.exists()
            else None,
        },
        "models": models_out,
        "claim_boundary": (
            "Development unknown-slice baseline on retained matched v0.5 "
            "validation750 traces. Hosted DeepSeek V4 Flash is not local-route "
            "evidence. Not Real(300), not test450 row inspection, not gate pass."
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}")
    for slug, block in models_out.items():
        for arm in (
            "llm_only",
            "llm_with_rules_frozen_panel",
            "llm_with_rules_final_ruleset_proxy",
        ):
            m = block[arm]["metrics"]
            g = block[arm]["collaboration_gate"]["passed"]
            print(
                f"{slug} {arm}: F1={m['f1']:.3f} acc={m['unknown_gold_accuracy']:.3f} "
                f"OR={m['overread_rate']:.3f} FSF={m['false_seizure_free_rate']:.3f} "
                f"gate={'PASS' if g else 'FAIL'}"
            )


if __name__ == "__main__":
    main()
