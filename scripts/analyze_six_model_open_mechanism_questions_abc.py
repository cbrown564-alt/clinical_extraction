"""No-call attribution for six-model open mechanism questions A–C.

Reads retained ExECT and Gan aggregates only. Never inspects locked holdout rows.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

PROTOCOL_PATH = Path(
    "docs/research/shared/six_model_open_mechanism_questions_abc_protocol_2026-08-03.md"
)
OUTPUT_PATH = Path("experiments/six_model_open_mechanism_questions_abc_20260803.json")
FINAL_PANEL = Path("experiments/six_model_final_panel_20260803/panel_aggregate.json")
TEST60_STAGE = Path(
    "experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json"
)
SF_OVERINFERENCE = Path(
    "experiments/exectv2_six_model_sf_overinference_dev140_20260718.json"
)
GAN_V05 = Path("experiments/gan2026_matched_v05_dev750_panel_20260727.json")
REPORT_PATH = Path("docs/research/shared/six_model_comparison_report_2026-07-18.md")

SLUGS = (
    "gpt41mini",
    "gpt56luna",
    "gpt56sol",
    "deepseek_v4_flash",
    "qwen36_35b",
    "gemma4_26b",
)
DISPLAY = {
    "gpt41mini": "GPT-4.1-mini",
    "gpt56luna": "GPT-5.6 Luna",
    "gpt56sol": "GPT-5.6 Sol",
    "deepseek_v4_flash": "DeepSeek V4 Flash",
    "qwen36_35b": "Qwen 3.6:35B",
    "gemma4_26b": "Gemma 4 26B",
}
FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)


def main() -> None:
    if not PROTOCOL_PATH.exists():
        raise SystemExit(f"predeclared protocol missing: {PROTOCOL_PATH}")
    payload = build_payload()
    OUTPUT_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "output": OUTPUT_PATH.as_posix(),
                "answers": {
                    key: payload["answers"][key]["status"] for key in ("A", "B", "C")
                },
            },
            sort_keys=True,
        )
    )


def build_payload() -> dict[str, Any]:
    final_panel = _load_json(FINAL_PANEL)
    test60 = _load_json(TEST60_STAGE)
    sf = _load_json(SF_OVERINFERENCE)
    gan = _load_json(GAN_V05)
    family_transfer = _family_transfer_table(test60)
    pre_gate = _pre_gate_by_slug(final_panel)
    sf_by_model = _sf_by_display(sf)
    gan_by_slug = {
        c["model_slug"]: c
        for c in gan["conditions"]
        if c.get("complete") and "first_failure_owner" in c
    }
    changed = {
        slug: _changed_row_summary(slug)
        for slug in ("gpt56sol", "qwen36_35b", "gpt41mini")
    }
    answers = {
        "A": _answer_a(family_transfer),
        "B": _answer_b(family_transfer, pre_gate, sf_by_model, gan_by_slug),
        "C": _answer_c(family_transfer, pre_gate, sf_by_model, changed),
    }
    return {
        "schema_version": "six_model.open_mechanism_questions_abc.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "protocol": PROTOCOL_PATH.as_posix(),
        "parent_report": REPORT_PATH.as_posix(),
        "call_mode": "saved_output_no_call",
        "row_policy": {
            "exect_dev140": "development_row_level",
            "exect_test60": "aggregate_only",
            "gan_dev750": "development_row_level",
            "gan_test450": "aggregate_only_rank_context_only",
        },
        "source_revision": _git_head(),
        "dirty_tree_note": _dirty_tree_note(),
        "sources": {
            "final_panel": _source_record(FINAL_PANEL),
            "test60_stage_panel": _source_record(TEST60_STAGE),
            "sf_overinference": _source_record(SF_OVERINFERENCE),
            "gan_matched_v05": _source_record(GAN_V05),
            "exect_dev140_score_ladders": {
                slug: _source_record(_dev140_path(slug)) for slug in SLUGS
            },
        },
        "family_transfer": family_transfer,
        "pre_gate_exact_evidence": pre_gate,
        "sf_state_transitions": {
            DISPLAY[slug]: sf_by_model.get(DISPLAY[slug])
            for slug in ("gpt56sol", "qwen36_35b", "gpt41mini", "gpt56luna")
        },
        "changed_row_categories_dev140": changed,
        "gan_matched_v05_focal": {
            slug: _gan_focal(gan_by_slug[slug])
            for slug in ("gpt41mini", "gpt56sol", "gpt56luna")
            if slug in gan_by_slug
        },
        "answers": answers,
        "claim_boundary": (
            "Development answers with aggregate-only holdout family transfer for "
            "A/C. Not clinical validation, not published ExECT benchmark, not "
            "general model superiority. Exact evidence ≠ semantic support. "
            "Decision 0046 Sol ExECT method-row fills unchanged. No test60/test450 "
            "row inspection."
        ),
    }


def _family_transfer_table(test60: dict[str, Any]) -> list[dict[str, Any]]:
    stage_by = {c["slug"]: c for c in test60["conditions"]}
    rows: list[dict[str, Any]] = []
    for slug in SLUGS:
        raw, final = _dev140_surfaces(slug)
        stage = stage_by[slug]
        for family in FAMILIES:
            dr = float(raw["by_indicator"][family]["f1"])
            df = float(final["by_indicator"][family]["f1"])
            tr = float(stage["raw_lane_score_by_family"][family]["f1"])
            tf = float(stage["clinical_headline_by_family"][family]["f1"])
            rows.append(
                {
                    "slug": slug,
                    "model": DISPLAY[slug],
                    "family": family,
                    "dev140_llm_only_f1": round(dr, 4),
                    "dev140_llm_with_rules_f1": round(df, 4),
                    "dev140_rules_lift": round(df - dr, 4),
                    "test60_llm_only_f1": round(tr, 4),
                    "test60_llm_with_rules_f1": round(tf, 4),
                    "test60_rules_lift": round(tf - tr, 4),
                    "transfer_gap_test_minus_dev": round((tf - tr) - (df - dr), 4),
                }
            )
        dro = float(raw["overall"]["f1"])
        dfo = float(final["overall"]["f1"])
        tro = float(stage["raw_lane_score"]["f1"])
        tfo = float(stage["clinical_headline"]["f1"])
        rows.append(
            {
                "slug": slug,
                "model": DISPLAY[slug],
                "family": "OVERALL",
                "dev140_llm_only_f1": round(dro, 4),
                "dev140_llm_with_rules_f1": round(dfo, 4),
                "dev140_rules_lift": round(dfo - dro, 4),
                "test60_llm_only_f1": round(tro, 4),
                "test60_llm_with_rules_f1": round(tfo, 4),
                "test60_rules_lift": round(tfo - tro, 4),
                "transfer_gap_test_minus_dev": round((tfo - tro) - (dfo - dro), 4),
            }
        )
    return rows


def _dev140_surfaces(slug: str) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = _load_json(_dev140_path(slug))
    ladder = payload["score_ladder"]
    return ladder["raw_lane_score"], ladder["headline_target"]


def _dev140_path(slug: str) -> Path:
    return Path(f"experiments/exectv2_six_model_single_call_{slug}_dev140_20260715.json")


def _pre_gate_by_slug(final_panel: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for condition in final_panel["conditions"]:
        slug = condition["slug"]
        exect = condition["exectv2"]["dev140"]
        out[slug] = {
            "model": DISPLAY[slug],
            "pre_gate_exact_evidence_rate": exect.get("pre_gate_exact_evidence_rate"),
            "pre_gate_mention_count": exect.get("pre_gate_mention_count"),
            "pre_gate_exact_evidence_count": exect.get("pre_gate_exact_evidence_count"),
            "evidence_repaired_count": exect.get("evidence_repaired_count"),
            "evidence_hard_dropped_count": exect.get("evidence_hard_dropped_count"),
            "evidence_warning_detail": exect.get("evidence_warning_detail"),
            "post_rules_exact_evidence_rate": exect.get(
                "post_rules_exact_evidence_rate"
            ),
        }
    return out


def _sf_by_display(sf: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for model in sf["models"]:
        agg = model["aggregate"]
        transitions = agg["correctness_transitions"]
        out[model["model"]] = {
            "comparator_state_f1": agg["comparator_state_profile"]["f1"],
            "candidate_state_f1": agg["candidate_state_profile"]["f1"],
            "state_f1_lift": round(
                agg["candidate_state_profile"]["f1"]
                - agg["comparator_state_profile"]["f1"],
                4,
            ),
            "wrong_to_correct": transitions.get("wrong_to_correct", 0),
            "correct_to_wrong": transitions.get("correct_to_wrong", 0),
            "changed_still_wrong": transitions.get("changed_still_wrong", 0),
            "unchanged_correct": transitions.get("unchanged_correct", 0),
            "unchanged_wrong": transitions.get("unchanged_wrong", 0),
        }
    return out


def _changed_row_summary(slug: str) -> dict[str, Any]:
    payload = _load_json(_dev140_path(slug))
    by_indicator = payload["changed_row_accounting"]["versus_v042_default_quarantine"][
        "by_indicator"
    ]
    sf_rules = _sf_rule_counts(slug)
    return {
        "model": DISPLAY[slug],
        "by_family": {
            family: {
                "changed_rows": by_indicator[family]["changed_rows"],
                "categories": by_indicator[family]["categories"],
            }
            for family in FAMILIES
        },
        "sf_rule_action_counts": sf_rules,
    }


def _sf_rule_counts(slug: str) -> dict[str, int]:
    path = Path(
        f"experiments/exectv2_six_model_single_call_{slug}_dev140_20260715"
        "_sf_unknown_suppression.jsonl"
    )
    if not path.exists():
        return {}
    counts: Counter[str] = Counter()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for action in row.get("projection_actions") or []:
            if isinstance(action, dict):
                rid = action.get("rule_id") or action.get("action") or "unknown"
                counts[f"projection:{rid}"] += 1
        for action in row.get("suppression_actions") or []:
            if isinstance(action, dict):
                rid = action.get("rule_id") or action.get("action") or "unknown"
                counts[f"suppression:{rid}"] += 1
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def _gan_focal(condition: dict[str, Any]) -> dict[str, Any]:
    owners = condition["first_failure_owner"]
    owned = sum(v for k, v in owners.items() if k != "none")
    return {
        "model": condition["model"],
        "model_boundary_purist_correct": condition["model_boundary_purist_correct"],
        "final_purist_correct": condition["final_purist_correct"],
        "model_boundary_purist": round(
            condition["model_boundary_purist_correct"] / 750, 4
        ),
        "final_purist": round(condition["final_purist_correct"] / 750, 4),
        "deterministic_wrong_to_correct": condition["deterministic_wrong_to_correct"],
        "deterministic_correct_to_wrong": condition["deterministic_correct_to_wrong"],
        "first_failure_owner": owners,
        "owned_failure_share": {
            key: round(owners.get(key, 0) / owned, 4) if owned else None
            for key in (
                "llm_clinical_selection",
                "evidence_selection",
                "deterministic_semantic",
                "format_or_schema",
            )
        },
        "clinical_subproblem": condition["clinical_subproblem"],
    }


def _answer_a(family_transfer: list[dict[str, Any]]) -> dict[str, Any]:
    overall = [r for r in family_transfer if r["family"] == "OVERALL"]
    by_family = [r for r in family_transfer if r["family"] != "OVERALL"]
    mean_gap = {
        family: round(
            sum(
                r["transfer_gap_test_minus_dev"]
                for r in by_family
                if r["family"] == family
            )
            / 6,
            4,
        )
        for family in FAMILIES
    }
    mean_test_lift = {
        family: round(
            sum(r["test60_rules_lift"] for r in by_family if r["family"] == family)
            / 6,
            4,
        )
        for family in FAMILIES
    }
    mean_dev_lift = {
        family: round(
            sum(r["dev140_rules_lift"] for r in by_family if r["family"] == family)
            / 6,
            4,
        )
        for family in FAMILIES
    }
    worst_families = sorted(mean_gap.items(), key=lambda kv: kv[1])
    return {
        "status": "answered",
        "claim_class": "development_answer_with_aggregate_holdout_family_transfer",
        "verdict": (
            "ExECT rules non-transfer is family-specific: Diagnosis has the "
            "largest average lift shrinkage from dev140 to aggregate test60; "
            "Prescription lift shrinks and often turns negative on holdout; "
            "Seizure Frequency still supplies most of the retained holdout "
            "rules lift; Investigations is unchanged by rules on both splits."
        ),
        "mean_dev140_rules_lift_by_family": mean_dev_lift,
        "mean_test60_rules_lift_by_family": mean_test_lift,
        "mean_transfer_gap_by_family": mean_gap,
        "families_ordered_worst_transfer": [f for f, _ in worst_families],
        "overall_lifts": overall,
        "evidence_limit": (
            "Family-level only. Individual rule-ID overfit on test60 is not "
            "asserted; holdout rows remain sealed."
        ),
    }


def _answer_b(
    family_transfer: list[dict[str, Any]],
    pre_gate: dict[str, dict[str, Any]],
    sf_by_model: dict[str, dict[str, Any]],
    gan_by_slug: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    mini_exect = {
        r["family"]: r
        for r in family_transfer
        if r["slug"] == "gpt41mini" and r["family"] != "OVERALL"
    }
    sol_exect = {
        r["family"]: r
        for r in family_transfer
        if r["slug"] == "gpt56sol" and r["family"] != "OVERALL"
    }
    return {
        "status": "answered",
        "claim_class": "development_answer_task_shaped_fit",
        "verdict": (
            "Mini suits Gan better than ExECT because Gan’s specialized "
            "deterministic stack turns a middling model boundary into a high "
            "final Purist with large wrong→correct mass, while ExECT needs "
            "broad four-family fact recovery where mini trails on Seizure "
            "Frequency and quote quality even after rules."
        ),
        "gan_matched_v05": {
            "mini": _gan_focal(gan_by_slug["gpt41mini"]),
            "sol": _gan_focal(gan_by_slug["gpt56sol"]),
            "luna": _gan_focal(gan_by_slug["gpt56luna"]),
        },
        "exect_dev140": {
            "mini_family_llm_only": {
                fam: mini_exect[fam]["dev140_llm_only_f1"] for fam in FAMILIES
            },
            "mini_family_final": {
                fam: mini_exect[fam]["dev140_llm_with_rules_f1"] for fam in FAMILIES
            },
            "sol_family_final": {
                fam: sol_exect[fam]["dev140_llm_with_rules_f1"] for fam in FAMILIES
            },
            "mini_pre_gate": pre_gate["gpt41mini"],
            "sol_pre_gate": pre_gate["gpt56sol"],
            "mini_sf_transitions": sf_by_model.get("GPT-4.1-mini"),
            "sol_sf_transitions": sf_by_model.get("GPT-5.6 Sol"),
        },
        "holdout_rank_context_only": {
            "gan_test450_llm_with_rules_rank": "mini 2nd (0.82), Sol 1st (0.85)",
            "exect_test60_llm_with_rules_rank": "mini 5th (0.76), Sol 2nd (0.80)",
        },
        "evidence_limit": (
            "Cross-task scores are not interchangeable. Attribution uses matched "
            "Gan v0.5 development owners and ExECT six-model development surfaces."
        ),
    }


def _answer_c(
    family_transfer: list[dict[str, Any]],
    pre_gate: dict[str, dict[str, Any]],
    sf_by_model: dict[str, dict[str, Any]],
    changed: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    qwen = {
        r["family"]: r
        for r in family_transfer
        if r["slug"] == "qwen36_35b"
    }
    sol = {
        r["family"]: r
        for r in family_transfer
        if r["slug"] == "gpt56sol"
    }
    family_delta_test = {
        fam: round(
            qwen[fam]["test60_rules_lift"] - sol[fam]["test60_rules_lift"],
            4,
        )
        for fam in FAMILIES
    }
    return {
        "status": "answered",
        "claim_class": "development_answer_with_aggregate_holdout_family_transfer",
        "verdict": (
            "Qwen’s larger ExECT holdout rules gain is concentrated in Seizure "
            "Frequency and Diagnosis, with less Prescription damage than Sol; "
            "on development, Qwen also needs far more quote repair before the "
            "evidence gate, so competitiveness is rules-rescued grounding plus "
            "SF/Dx lift, not raw producer quality."
        ),
        "qwen_minus_sol_test60_rules_lift_by_family": family_delta_test,
        "qwen_family_lifts": qwen,
        "sol_family_lifts": sol,
        "pre_gate": {
            "qwen": pre_gate["qwen36_35b"],
            "sol": pre_gate["gpt56sol"],
        },
        "sf_state_transitions": {
            "qwen": sf_by_model.get("Qwen 3.6:35B"),
            "sol": sf_by_model.get("GPT-5.6 Sol"),
        },
        "changed_row_categories_dev140": {
            "qwen": changed["qwen36_35b"],
            "sol": changed["gpt56sol"],
        },
        "evidence_limit": (
            "Family and development rule-class evidence only. Quote repair proves "
            "substring presence, not clinical support. No sealed per-rule "
            "test60 ablation."
        ),
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _source_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {
        "path": path.as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


def _git_head() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _dirty_tree_note() -> str:
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "git status unavailable"
    if not status:
        return "clean"
    return "dirty working tree at generation time; see git status"


if __name__ == "__main__":
    main()
