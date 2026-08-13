#!/usr/bin/env python3
"""Build per-mode real examples for hard-slice error modes.

Companion to scripts/build_six_model_hard_slice_error_modes.py.
No new model calls. No locked-test row inspection. Development evidence spans
come from saved prediction artifacts only (not full notes).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_MODE = 2
_STATE_RE = re.compile(r"'(active-rate|seizure-free|unknown)'")

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


def _truncate(text: str | None, limit: int = 280) -> str | None:
    if text is None:
        return None
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _state_token(key: str) -> str | None:
    match = _STATE_RE.search(key)
    return match.group(1) if match else None


def _compact_sf_mentions(mentions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for mention in mentions:
        if str(mention.get("entity", "")) != "SeizureFrequency":
            continue
        attrs = {
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value is not None
        }
        out.append(
            {
                "text": mention.get("text"),
                "attributes": attrs,
            }
        )
    return out


def _pick_examples(
    candidates: list[dict[str, Any]],
    *,
    consensus_ids: set[Any],
    id_key: str,
) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        consensus_rank = 0 if row.get(id_key) in consensus_ids else 1
        # Prefer ExECT examples where coarse state sets visibly differ.
        gold_states = row.get("gold_states")
        pred_states = row.get("pred_states")
        if isinstance(gold_states, list) and isinstance(pred_states, list):
            state_clarity = 0 if set(gold_states) != set(pred_states) else 1
        else:
            state_clarity = 0
        return (consensus_rank, state_clarity, model_rank, str(row.get(id_key)))

    ordered = sorted(candidates, key=sort_key)
    picked: list[dict[str, Any]] = []
    seen_ids: set[Any] = set()
    for row in ordered:
        row_id = row.get(id_key)
        if row_id in seen_ids:
            continue
        picked.append(row)
        seen_ids.add(row_id)
        if len(picked) >= EXAMPLES_PER_MODE:
            break
    return picked


def _collect_gan_ordinary(
    gold_index: dict[int, dict[str, Any]],
    hybrid: dict[str, dict[int, dict[str, Any]]],
    consensus: set[int],
) -> dict[str, Any]:
    scored: dict[str, list[dict[str, Any]]] = defaultdict(list)
    boundary: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for slug, display in hs.MODEL_SPECS:
        for row in hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl"):
            index = int(row["source_row_index"])
            meta = gold_index.get(index)
            if meta is None or meta["a_priori_bucket"] != "ordinary_point_rate":
                continue
            comparison = row.get("comparison")
            if comparison and comparison.get("purist_correct"):
                continue
            scored_label = hs._llm_scored_label(row)
            boundary_label = hs._llm_model_boundary_label(row)
            mode = hs._ordinary_error_mode(
                scored_label, comparison if isinstance(comparison, dict) else None
            )
            boundary_mode = hs._ordinary_error_mode(
                boundary_label, comparison if isinstance(comparison, dict) else None
            )
            decision = row.get("decision_record") or {}
            hybrid_row = hybrid[slug].get(index) or {}
            payload = {
                "model_slug": slug,
                "model_display": display,
                "source_row_index": index,
                "gold_label": meta["gold_label"],
                "scored_predicted_label": scored_label,
                "model_boundary_label": boundary_label,
                "error_mode": mode,
                "model_boundary_error_mode": boundary_mode,
                "gold_purist_category": (comparison or {}).get("gold_purist_category"),
                "predicted_purist_category": (comparison or {}).get(
                    "predicted_purist_category"
                ),
                "pragmatic_near_miss": bool(
                    comparison and comparison.get("pragmatic_correct")
                ),
                "hybrid_rescues": bool(hybrid_row.get("purist_correct")),
                "hybrid_final_label": hybrid_row.get("final_label"),
                "selected_evidence": _truncate(decision.get("evidence")),
                "rationale": _truncate(decision.get("rationale"), 220),
                "call_error": row.get("call_error"),
                "parse_errors": (row.get("parse_errors") or [])[:3],
                "consensus_wrong_all_six": index in consensus,
            }
            scored[mode].append(payload)
            boundary[boundary_mode].append(payload)

    return {
        "slice": "ordinary_point_rate",
        "surface": "llm",
        "modes_scored_label": {
            mode: _pick_examples(rows, consensus_ids=consensus, id_key="source_row_index")
            for mode, rows in sorted(scored.items())
        },
        "modes_model_boundary": {
            mode: _pick_examples(rows, consensus_ids=consensus, id_key="source_row_index")
            for mode, rows in sorted(boundary.items())
        },
        "mode_inventory_scored": sorted(scored),
        "mode_inventory_boundary": sorted(boundary),
    }


def _attr_evidence_index() -> dict[str, dict[int, dict[str, Any]]]:
    attr = json.loads(hs.GAN_ATTR.read_text(encoding="utf-8"))
    out: dict[str, dict[int, dict[str, Any]]] = defaultdict(dict)
    for row in attr["rows"]:
        out[str(row["model_slug"])][int(row["source_row_index"])] = {
            "selected_evidence": row.get("selected_evidence"),
            "selected_evidence_exact": row.get("selected_evidence_exact"),
            "clinical_subproblem": row.get("clinical_subproblem"),
            "model_boundary_label": row.get("model_boundary_label"),
            "model_boundary_purist_correct": row.get("model_boundary_purist_correct"),
        }
    return out


def _collect_gan_cluster(
    gold_index: dict[int, dict[str, Any]],
    hybrid: dict[str, dict[int, dict[str, Any]]],
    attr_evidence: dict[str, dict[int, dict[str, Any]]],
    *,
    surface: str,
    consensus: set[int],
) -> dict[str, Any]:
    scored: dict[str, list[dict[str, Any]]] = defaultdict(list)
    boundary: dict[str, list[dict[str, Any]]] = defaultdict(list)
    cluster_indexes = {
        index
        for index, meta in gold_index.items()
        if meta["a_priori_bucket"] == "cluster_burden"
    }

    for slug, display in hs.MODEL_SPECS:
        if surface == "llm":
            rows_by_index = {
                int(row["source_row_index"]): row
                for row in hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_only.jsonl")
            }
            for index in sorted(cluster_indexes):
                row = rows_by_index[index]
                comparison = row.get("comparison")
                if comparison and comparison.get("purist_correct"):
                    continue
                scored_label = hs._llm_scored_label(row)
                boundary_label = hs._llm_model_boundary_label(row)
                mode = hs._cluster_error_mode(
                    scored_label, comparison if isinstance(comparison, dict) else None
                )
                boundary_mode = hs._cluster_error_mode(
                    boundary_label, comparison if isinstance(comparison, dict) else None
                )
                decision = row.get("decision_record") or {}
                payload = {
                    "model_slug": slug,
                    "model_display": display,
                    "source_row_index": index,
                    "gold_label": gold_index[index]["gold_label"],
                    "scored_predicted_label": scored_label,
                    "model_boundary_label": boundary_label,
                    "error_mode": mode,
                    "model_boundary_error_mode": boundary_mode,
                    "selected_evidence": _truncate(decision.get("evidence")),
                    "rationale": _truncate(decision.get("rationale"), 220),
                    "call_error": row.get("call_error"),
                    "parse_errors": (row.get("parse_errors") or [])[:3],
                    "consensus_wrong_all_six": index in consensus,
                }
                scored[mode].append(payload)
                boundary[boundary_mode].append(payload)
        else:
            for index in sorted(cluster_indexes):
                hybrid_row = hybrid[slug][index]
                if hybrid_row["purist_correct"]:
                    continue
                pred_label = str(hybrid_row["final_label"])
                mode = hs._cluster_error_mode(pred_label, {"purist_correct": False})
                meta = attr_evidence[slug].get(index) or {}
                payload = {
                    "model_slug": slug,
                    "model_display": display,
                    "source_row_index": index,
                    "gold_label": gold_index[index]["gold_label"],
                    "scored_predicted_label": pred_label,
                    "model_boundary_label": meta.get("model_boundary_label")
                    or hybrid_row.get("model_boundary_label"),
                    "error_mode": mode,
                    "model_boundary_purist_correct": meta.get(
                        "model_boundary_purist_correct",
                        hybrid_row.get("model_boundary_purist_correct"),
                    ),
                    "selected_evidence": _truncate(meta.get("selected_evidence")),
                    "selected_evidence_exact": meta.get(
                        "selected_evidence_exact",
                        hybrid_row.get("selected_evidence_exact"),
                    ),
                    "clinical_subproblem": meta.get(
                        "clinical_subproblem", hybrid_row.get("clinical_subproblem")
                    ),
                    "consensus_wrong_all_six": index in consensus,
                }
                scored[mode].append(payload)

    result: dict[str, Any] = {
        "slice": "cluster_burden",
        "surface": surface,
        "modes_scored_label": {
            mode: _pick_examples(rows, consensus_ids=consensus, id_key="source_row_index")
            for mode, rows in sorted(scored.items())
        },
        "mode_inventory_scored": sorted(scored),
    }
    if surface == "llm":
        result["modes_model_boundary"] = {
            mode: _pick_examples(rows, consensus_ids=consensus, id_key="source_row_index")
            for mode, rows in sorted(boundary.items())
        }
        result["mode_inventory_boundary"] = sorted(boundary)
    return result


def _collect_exect_sf(*, surface: str, consensus: set[str]) -> dict[str, Any]:
    field = "raw_lane_mentions" if surface == "llm" else "predicted_mentions"
    by_mode: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for slug, display in hs.MODEL_SPECS:
        for row in hs._read_jsonl(hs.EXECT_JSONL[slug]):
            letter_id = str(row["letter_id"])
            gold_keys = headline_keys(row, "SeizureFrequency", field="gold_mentions")
            pred_keys = headline_keys(row, "SeizureFrequency", field=field)
            mode = hs._exect_mode(gold_keys, pred_keys)
            if mode.startswith("correct_"):
                continue
            gold_mentions = _compact_sf_mentions(row.get("gold_mentions") or [])
            pred_mentions = _compact_sf_mentions(row.get(field) or [])
            payload = {
                "model_slug": slug,
                "model_display": display,
                "letter_id": letter_id,
                "prediction_field": field,
                "error_mode": mode,
                "gold_states": sorted(
                    {token for key in gold_keys if (token := _state_token(key))}
                ),
                "pred_states": sorted(
                    {token for key in pred_keys if (token := _state_token(key))}
                ),
                "gold_keys": gold_keys,
                "pred_keys": pred_keys,
                "gold_mentions": gold_mentions,
                "pred_mentions": pred_mentions,
                "consensus_imperfect_all_six": letter_id in consensus,
            }
            by_mode[mode].append(payload)

    return {
        "slice": "SeizureFrequency",
        "surface": surface,
        "modes": {
            mode: _pick_examples(rows, consensus_ids=consensus, id_key="letter_id")
            for mode, rows in sorted(by_mode.items())
        },
        "mode_inventory": sorted(by_mode),
    }


def build_artifact() -> dict[str, Any]:
    parent = json.loads(
        (
            REPO_ROOT / f"experiments/six_model_hard_slice_error_modes_{DATE_STAMP}.json"
        ).read_text(encoding="utf-8")
    )
    gold_index = hs._gan_gold_index()
    hybrid = hs._load_gan_hybrid_rows()
    attr_evidence = _attr_evidence_index()

    ordinary_consensus = set(
        parent["gan"]["ordinary_point_rate_llm"]["consensus_wrong_all_six"][
            "source_row_indexes"
        ]
    )
    cluster_llm_consensus = set(
        parent["gan"]["cluster_burden_llm"]["consensus_wrong_all_six"][
            "source_row_indexes"
        ]
    )
    cluster_hybrid_consensus = set(
        parent["gan"]["cluster_burden_llm_with_rules"]["consensus_wrong_all_six"][
            "source_row_indexes"
        ]
    )
    exect_llm_consensus = set(
        parent["exect"]["seizure_frequency_llm"]["consensus_imperfect_all_six"][
            "letter_ids"
        ]
    )
    exect_hybrid_consensus = set(
        parent["exect"]["seizure_frequency_llm_with_rules"]["consensus_imperfect_all_six"][
            "letter_ids"
        ]
    )

    return {
        "schema_version": "six_model.hard_slice_error_mode_examples.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/shared/six_model_hard_slice_error_mode_examples_protocol_2026-08-06.md"
        ),
        "parent_report": "docs/research/shared/six_model_hard_slice_error_modes_2026-08-06.md",
        "parent_artifact": f"experiments/six_model_hard_slice_error_modes_{DATE_STAMP}.json",
        "call_mode": "saved_output_no_call",
        "text_policy": (
            "development_selected_evidence_spans_only; no full clinical notes; "
            "no locked-test rows"
        ),
        "git": hs._git_note(),
        "examples_per_mode": EXAMPLES_PER_MODE,
        "selection_policy": (
            "Prefer consensus-wrong ids, then stronger hosted models "
            "(Sol > Luna > mini > DeepSeek > Qwen > Gemma), unique ids first."
        ),
        "gan": {
            "ordinary_point_rate_llm": _collect_gan_ordinary(
                gold_index, hybrid, ordinary_consensus
            ),
            "cluster_burden_llm": _collect_gan_cluster(
                gold_index,
                hybrid,
                attr_evidence,
                surface="llm",
                consensus=cluster_llm_consensus,
            ),
            "cluster_burden_llm_with_rules": _collect_gan_cluster(
                gold_index,
                hybrid,
                attr_evidence,
                surface="llm_with_rules",
                consensus=cluster_hybrid_consensus,
            ),
        },
        "exect": {
            "seizure_frequency_llm": _collect_exect_sf(
                surface="llm", consensus=exect_llm_consensus
            ),
            "seizure_frequency_llm_with_rules": _collect_exect_sf(
                surface="llm_with_rules", consensus=exect_hybrid_consensus
            ),
        },
        "claim_boundary": (
            "Development illustration of hard-slice error modes. Evidence strings "
            "are model-selected spans from retained artifacts, not full notes and "
            "not clinical validation."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / f"experiments/six_model_hard_slice_error_mode_examples_{DATE_STAMP}.json",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {args.output}")
    for track, block in (("gan", artifact["gan"]), ("exect", artifact["exect"])):
        for name, section in block.items():
            if "modes_scored_label" in section:
                modes = section["modes_scored_label"]
            elif "modes" in section:
                modes = section["modes"]
            else:
                modes = {}
            counts = {mode: len(rows) for mode, rows in modes.items()}
            print(f"  {track}.{name}: {counts}")


if __name__ == "__main__":
    main()
