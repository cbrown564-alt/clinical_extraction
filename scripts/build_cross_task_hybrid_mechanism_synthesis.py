#!/usr/bin/env python3
"""Cross-task hybrid mechanism synthesis from retained 2026-08-06 artifacts.

See docs/research/cross_task_hybrid_mechanism_synthesis_protocol_2026-08-06.md.
No model calls; reads parent JSON only.
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

PARENTS = {
    "task_shape_framework": "docs/research/task_shape_framework_2026-08-06.md",
    "category_cut": "docs/research/six_model_category_cut_performance_2026-08-06.md",
    "category_cut_artifact": f"experiments/six_model_category_cut_performance_{DATE_STAMP}.json",
    "gan_catalog": "docs/research/gan2026_category_error_catalog_2026-08-06.md",
    "gan_catalog_artifact": f"experiments/gan2026_category_error_catalog_{DATE_STAMP}.json",
    "exect_catalog": "docs/research/exectv2_family_error_catalog_2026-08-06.md",
    "exect_catalog_artifact": f"experiments/exectv2_family_error_catalog_{DATE_STAMP}.json",
    "gan_stage": "docs/research/gan2026_hybrid_stage_ablation_2026-08-06.md",
    "gan_stage_artifact": f"experiments/gan2026_hybrid_stage_ablation_{DATE_STAMP}.json",
    "exect_stage": "docs/research/exectv2_hybrid_stage_ablation_2026-08-06.md",
    "exect_stage_artifact": f"experiments/exectv2_hybrid_stage_ablation_{DATE_STAMP}.json",
    "hard_slice": "docs/research/six_model_hard_slice_error_modes_2026-08-06.md",
    "hard_slice_artifact": f"experiments/six_model_hard_slice_error_modes_{DATE_STAMP}.json",
}


def _git_meta() -> dict[str, Any]:
    commit = (
        subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
    )
    dirty = bool(
        subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            text=True,
        ).strip()
    )
    return {"commit": commit, "dirty_tree": dirty}


def _load(rel: str) -> dict[str, Any]:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def _lens_row(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "n": entry.get("n"),
        "min": entry.get("min"),
        "max": entry.get("max"),
        "spread": entry.get("spread"),
        "lens": entry.get("lens"),
    }


def _family_stage_summary(stage: dict[str, Any]) -> dict[str, Any]:
    return {
        "fires": stage.get("fires", 0),
        "first_changer": stage.get("first_changer", 0),
        "first_rescue": stage.get("first_rescue", 0),
        "first_harm": stage.get("first_harm", 0),
        "any_rescue": stage.get("any_rescue", 0),
        "any_harm": stage.get("any_harm", 0),
        "examples_rescue": stage.get("examples_rescue", [])[:2],
        "examples_harm": stage.get("examples_harm", [])[:2],
    }


def build_artifact() -> dict[str, Any]:
    cut = _load(PARENTS["category_cut_artifact"])
    gan_cat = _load(PARENTS["gan_catalog_artifact"])
    exect_cat = _load(PARENTS["exect_catalog_artifact"])
    gan_stage = _load(PARENTS["gan_stage_artifact"])
    exect_stage = _load(PARENTS["exect_stage_artifact"])
    hard = _load(PARENTS["hard_slice_artifact"])

    gan_llm = cut["gan2026"]["lenses_llm_a_priori"]
    gan_hyb = cut["gan2026"]["lenses_llm_with_rules_a_priori"]
    ex_llm = cut["exectv2"]["lenses_llm_families"]
    ex_hyb = cut["exectv2"]["lenses_llm_with_rules_families"]

    gan_unknown_homes: dict[str, int] = {}
    for name, fam in gan_stage["families"].items():
        homes = fam.get("by_bucket_first_changer", {})
        if "unknown_sentinel" in homes:
            gan_unknown_homes[name] = homes["unknown_sentinel"]

    clinical_harm_examples = []
    for name in (
        "repair.monthly_diary",
        "repair.breakthrough",
        "repair.non_epileptic",
        "repair.elapsed_anchor",
    ):
        fam = gan_stage["families"][name]
        for ex in fam.get("examples_harm", []):
            clinical_harm_examples.append({"stage": name, **ex})

    sf_fam = exect_stage["clinical_families"]["SeizureFrequency"]
    rx_fam = exect_stage["clinical_families"]["Prescription"]
    dx_fam = exect_stage["clinical_families"]["Diagnosis"]
    inv_fam = exect_stage["clinical_families"]["Investigations"]

    artifact: dict[str, Any] = {
        "schema_version": "cross_task.hybrid_mechanism_synthesis.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/cross_task_hybrid_mechanism_synthesis_protocol_2026-08-06.md"
        ),
        "git": _git_meta(),
        "call_mode": "saved_output_no_call_synthesis",
        "parents": PARENTS,
        "plain_answer": {
            "rules_job": (
                "On Gan, rules create the easy mass (free/range/no-reference) "
                "and lift ordinary rates; clusters stay the practical floor; "
                "unknown_sentinel is not cleanly helped. On ExECT, rules rescue "
                "Diagnosis inventory and trim SF precision, can hurt "
                "Prescription, and leave Investigations unchanged."
            ),
            "mass_first_changers": {
                "gan": "repair.selected_evidence (evidence reconcile)",
                "exect_diagnosis": "lens.diagnosis",
                "exect_seizure_frequency": "project_and_gate",
                "exect_prescription": "lens.prescription (net harm)",
                "exect_investigations": "near no-op on lenses",
            },
            "residuals": [
                "gan_unknown_sentinel",
                "gan_cluster_burden",
                "exect_sf_inventory",
                "exect_prescription_lens_harm",
            ],
        },
        "category_competence": {
            "gan": {
                "llm": {k: _lens_row(v) for k, v in gan_llm.items()},
                "llm_with_rules": {k: _lens_row(v) for k, v in gan_hyb.items()},
                "strict_x_llm": sorted(
                    k for k, v in gan_llm.items() if v.get("lens") == "x"
                ),
                "strict_x_hybrid": sorted(
                    k for k, v in gan_hyb.items() if v.get("lens") == "x"
                ),
                "practical_floor_hybrid": "cluster_burden",
                "rules_not_clean_rescue": "unknown_sentinel",
            },
            "exect": {
                "llm_families": {k: _lens_row(v) for k, v in ex_llm.items()},
                "llm_with_rules_families": {
                    k: _lens_row(v) for k, v in ex_hyb.items()
                },
                "strict_x_llm": sorted(
                    k for k, v in ex_llm.items() if v.get("lens") == "x"
                ),
                "strict_x_hybrid": sorted(
                    k for k, v in ex_hyb.items() if v.get("lens") == "x"
                ),
                "practical_floor_both_surfaces": "SeizureFrequency",
            },
        },
        "stage_ownership": {
            "gan": {
                "band_first_changer_counts": gan_stage["band_first_changer_counts"],
                "changed_row_count": gan_stage["changed_row_count"],
                "residual_ownership": gan_stage["residual_ownership"],
                "top_pathways": gan_stage["top_pathways"][:8],
                "families": {
                    name: {
                        "band": fam["band"],
                        "fires": fam["fires"],
                        "first_changer": fam["first_changer"],
                        "first_rescue": fam["first_rescue"],
                        "first_harm": fam["first_harm"],
                        "any_rescue": fam["any_rescue"],
                        "any_harm": fam["any_harm"],
                        "by_bucket_first_changer": fam.get(
                            "by_bucket_first_changer", {}
                        ),
                    }
                    for name, fam in gan_stage["families"].items()
                },
                "bucket_band_endpoints": {
                    bucket: {
                        "n": payload["n_row_model_cells"],
                        "model_final_acc": payload["bands"]["model_final"]["accuracy"],
                        "after_evidence_acc": payload["bands"]["evidence_reconcile"][
                            "accuracy"
                        ],
                        "after_clinical_acc": payload["bands"]["clinical_selection"][
                            "accuracy"
                        ],
                        "final_acc": payload["bands"]["free_interval"]["accuracy"],
                        "final_wrong_modes": payload["bands"]["free_interval"][
                            "wrong_mode_counts"
                        ],
                    }
                    for bucket, payload in gan_stage["buckets"].items()
                },
                "fidelity": gan_stage["fidelity"],
            },
            "exect": {
                "fidelity": exect_stage["fidelity"],
                "families": {
                    family: {
                        "n": payload["n_letter_model_cells"],
                        "band_first_changer_counts": payload[
                            "band_first_changer_counts"
                        ],
                        "residual_ownership": payload["residual_ownership"],
                        "top_pathways": payload["top_pathways"][:6],
                        "final_exact_rate": payload["bands"]["evidence_gate"][
                            "exact_rate"
                        ],
                        "final_modes": payload["bands"]["evidence_gate"]["mode_counts"],
                        "active_stages": {
                            sname: _family_stage_summary(stage)
                            for sname, stage in payload["stages"].items()
                            if stage.get("fires", 0) or stage.get("first_changer", 0)
                        },
                    }
                    for family, payload in exect_stage["clinical_families"].items()
                },
            },
        },
        "residual_ownership": {
            "gan_unknown_sentinel": {
                "question": (
                    "Why does hybrid not cleanly improve unknown-gold, and which "
                    "stages first-change those rows?"
                ),
                "category_cut": {
                    "llm": _lens_row(gan_llm["unknown_sentinel"]),
                    "llm_with_rules": _lens_row(gan_hyb["unknown_sentinel"]),
                },
                "catalog_hybrid_modes": gan_cat["surfaces"]["llm_with_rules"][
                    "buckets"
                ]["unknown_sentinel"]["pooled_wrong_mode_counts"],
                "band_accuracy": {
                    band: gan_stage["buckets"]["unknown_sentinel"]["bands"][band][
                        "accuracy"
                    ]
                    for band in (
                        "model_final",
                        "representation",
                        "evidence_reconcile",
                        "clinical_selection",
                        "free_interval",
                    )
                },
                "clinical_selection_mode_delta": gan_stage["buckets"][
                    "unknown_sentinel"
                ]["bands"]["clinical_selection"]["mode_delta_from_previous_band"],
                "first_changer_homes_on_unknown": gan_unknown_homes,
                "clinical_selection_family_any_harm": {
                    name: gan_stage["families"][name]["any_harm"]
                    for name in (
                        "repair.monthly_diary",
                        "repair.breakthrough",
                        "repair.non_epileptic",
                        "repair.dated_sequence",
                        "repair.elapsed_anchor",
                    )
                },
                "harm_examples": clinical_harm_examples[:6],
                "interpretation": (
                    "Evidence reconcile lifts unknown accuracy sharply; clinical "
                    "selection then adds false_active_rate / false_seizure_free. "
                    "This is assertion damage on abstention gold, not missing "
                    "format cleanup."
                ),
            },
            "gan_cluster_burden": {
                "question": (
                    "After grammar cleanup, what residual shapes remain on "
                    "cluster gold?"
                ),
                "category_cut": {
                    "llm": _lens_row(gan_llm["cluster_burden"]),
                    "llm_with_rules": _lens_row(gan_hyb["cluster_burden"]),
                },
                "hard_slice_hybrid_exact_evidence": hard.get("gan", {})
                .get("cluster_burden_llm_with_rules", {})
                .get("exact_evidence_among_wrong"),
                "band_accuracy": {
                    band: gan_stage["buckets"]["cluster_burden"]["bands"][band][
                        "accuracy"
                    ]
                    for band in (
                        "model_final",
                        "evidence_reconcile",
                        "clinical_selection",
                        "free_interval",
                    )
                },
                "final_wrong_modes": gan_stage["buckets"]["cluster_burden"]["bands"][
                    "free_interval"
                ]["wrong_mode_counts"],
                "interpretation": (
                    "Mass lift is evidence reconcile clearing incomplete cluster "
                    "grammar. Clinical/free-interval add little. Residual is "
                    "collapse_to_unknown and dropped_to_smooth_rate with quotes "
                    "usually already selected."
                ),
            },
            "exect_sf_inventory": {
                "question": (
                    "After project_and_gate and SF clinical stages, what imperfect "
                    "shapes remain?"
                ),
                "category_cut": {
                    "llm": _lens_row(ex_llm["SeizureFrequency"]),
                    "llm_with_rules": _lens_row(ex_hyb["SeizureFrequency"]),
                },
                "band_exact": {
                    band: sf_fam["bands"][band]["exact_rate"]
                    for band in (
                        "post_flatten",
                        "producer_gate",
                        "sf_clinical",
                        "evidence_gate",
                    )
                },
                "final_modes": sf_fam["bands"]["evidence_gate"]["mode_counts"],
                "stage_ownership": {
                    sname: _family_stage_summary(stage)
                    for sname, stage in sf_fam["stages"].items()
                    if stage.get("fires", 0) or stage.get("first_changer", 0)
                },
                "residual_ownership": sf_fam["residual_ownership"],
                "catalog_token_pressure": exect_cat["surfaces"]["llm_with_rules"][
                    "families"
                ]["SeizureFrequency"].get("top_missed_extra_tokens")
                or exect_cat["surfaces"]["llm_with_rules"]["families"][
                    "SeizureFrequency"
                ].get("pooled_imperfect_mode_counts"),
                "interpretation": (
                    "Producer gate is the mass first-changer and rescue. Residual "
                    "imperfect mass is empty_gold_spurious, missed_only, and "
                    "substituted_or_mixed—inventory/precision, not missing Dx/Rx "
                    "lenses."
                ),
            },
            "exect_prescription_lens_harm": {
                "question": (
                    "Does the Prescription lens earn its keep under default policy?"
                ),
                "category_cut": {
                    "llm": _lens_row(ex_llm["Prescription"]),
                    "llm_with_rules": _lens_row(ex_hyb["Prescription"]),
                },
                "band_exact": {
                    "pre_rx_lens": rx_fam["bands"]["diagnosis_lens"]["exact_rate"],
                    "after_rx_lens": rx_fam["bands"]["prescription_lens"]["exact_rate"],
                    "final": rx_fam["bands"]["evidence_gate"]["exact_rate"],
                },
                "lens_stage": _family_stage_summary(rx_fam["stages"]["lens.prescription"]),
                "mode_delta_across_rx_lens": rx_fam["bands"]["prescription_lens"][
                    "mode_delta_from_previous_band"
                ],
                "residual_ownership": rx_fam["residual_ownership"],
                "interpretation": (
                    "lens.prescription is the first-changer and net-hurts "
                    "(any-harm 60 vs any-rescue 44). Exactness falls across the "
                    "Rx band. This justifies a policy counterfactual study, not "
                    "an immediate default rewrite from this synthesis alone."
                ),
            },
            "exect_investigations_noop": {
                "question": "Do Investigations family rules change this roster?",
                "band_exact_final": inv_fam["bands"]["evidence_gate"]["exact_rate"],
                "band_first_changer_counts": inv_fam["band_first_changer_counts"],
                "lens_fires": inv_fam["stages"]["lens.investigations"].get("fires", 0),
                "interpretation": (
                    "Investigations lens fires 0; only thin project_and_gate "
                    "movement. Residual wrongs are mostly no_stage_change."
                ),
            },
            "exect_diagnosis_mass_rescue": {
                "question": "What owns Diagnosis hybrid lift?",
                "band_exact": {
                    "post_flatten": dx_fam["bands"]["post_flatten"]["exact_rate"],
                    "after_diagnosis_lens": dx_fam["bands"]["diagnosis_lens"][
                        "exact_rate"
                    ],
                    "final": dx_fam["bands"]["evidence_gate"]["exact_rate"],
                },
                "lens_stage": _family_stage_summary(dx_fam["stages"]["lens.diagnosis"]),
                "interpretation": (
                    "lens.diagnosis is the mass Diagnosis first-changer and net "
                    "rescue. Later bands are no-ops for Diagnosis keys."
                ),
            },
        },
        "blocked_or_unanswered": [
            {
                "id": "holdout_category_cuts",
                "status": "blocked",
                "note": "Sealed holdout category aggregates remain protocol-gated.",
            },
            {
                "id": "leave_one_stage_out",
                "status": "unanswered",
                "note": (
                    "First-changer attribution is not factorial necessity."
                ),
            },
            {
                "id": "prescription_policy_counterfactual",
                "status": "answered_mixed",
                "note": (
                    "Thin identity raises letter exactness but not mean "
                    "Prescription F1; no default rewrite. See "
                    "exectv2_prescription_lens_counterfactual_2026-08-06."
                ),
            },
            {
                "id": "unknown_sentinel_repair_design",
                "status": "localized_not_authorized",
                "note": (
                    "Breakthrough dominates unknown any-harm; no repair "
                    "candidate authorized. See "
                    "gan2026_unknown_sentinel_clinical_harm_2026-08-06."
                ),
            },
        ],
        "claim_boundary": (
            "Development mechanism synthesis from retained 2026-08-06 no-call "
            "artifacts on Gan dev750 and ExECT dev140. Not holdout competence, "
            "not leave-one-stage-out, not a Decision 0046 or C16 rewrite, not "
            "clinical validation. Scores are not interchangeable across tasks."
        ),
    }
    return artifact


def _fmt_band(min_v: float | None, max_v: float | None) -> str:
    if min_v is None or max_v is None:
        return "—"
    return f"{min_v:.2f}–{max_v:.2f}"


def render_report(artifact: dict[str, Any]) -> str:
    gan_comp = artifact["category_competence"]["gan"]
    ex_comp = artifact["category_competence"]["exect"]
    gan_stage = artifact["stage_ownership"]["gan"]
    ex_stage = artifact["stage_ownership"]["exect"]
    residuals = artifact["residual_ownership"]

    lines: list[str] = [
        "# Cross-task hybrid mechanism synthesis",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development mechanism synthesis from retained no-call ladder  ",
        "Protocol: [cross-task hybrid mechanism synthesis protocol]"
        "(cross_task_hybrid_mechanism_synthesis_protocol_2026-08-06.md)  ",
        "Parents: [task-shape](task_shape_framework_2026-08-06.md), "
        "[category-cut](six_model_category_cut_performance_2026-08-06.md), "
        "[Gan catalog](gan2026_category_error_catalog_2026-08-06.md), "
        "[Gan stage ablation](gan2026_hybrid_stage_ablation_2026-08-06.md), "
        "[ExECT catalog](exectv2_family_error_catalog_2026-08-06.md), "
        "[ExECT stage ablation](exectv2_hybrid_stage_ablation_2026-08-06.md)  ",
        "Artifact: "
        f"[`experiments/cross_task_hybrid_mechanism_synthesis_{DATE_STAMP}.json`]"
        f"(../../experiments/cross_task_hybrid_mechanism_synthesis_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "Across both tracks, `llm_with_rules` is not one polish step.",
        "",
        "1. **Gan** — rules **create** easy mass (seizure-free, range, "
        "no-reference) and lift ordinary rates out of the llm-only floor. "
        "Inside hybrid, **`selected_evidence`** is the mass first-changer; "
        "clinical selection adds the next Purist lift and most harm; "
        "clusters stay the practical floor; **`unknown_sentinel` is not a "
        "clean rescue**.",
        "2. **ExECT** — rules **rescue Diagnosis inventory** and **trim SF "
        "precision**; **Prescription lens can net-hurt**; Investigations "
        "lenses are a no-op on this roster. Mass first-changers are "
        "`lens.diagnosis` (Dx) and `project_and_gate` (SF).",
        "3. **Similarity across models** on overall scores is "
        "surface-dependent: shared weakness without rules, shared easy mass "
        "with rules—not interchangeable competence.",
        "4. **Residuals after the stack** are selection / convention / "
        "inventory problems, usually with evidence already in hand—not "
        "missing format cleanup.",
        "",
        "## What the ladder already established",
        "",
        "| Layer | What it answered |",
        "| --- | --- |",
        "| Task shape + gold taxonomies | What each letter asks; gold buckets / "
        "families |",
        "| Category-cut x/y/z | Which gold categories are common, discriminating, "
        "or shared floors on `llm` vs hybrid |",
        "| Error catalogs | Wrong-answer shapes and llm→hybrid ablation |",
        "| Hybrid stage ablations | Named first-changer stages inside hybrid |",
        "",
        "This page is the cross-task packaging. Numbers below are copied from "
        "those parents; regenerate the parents first if they change.",
        "",
        "## Rules job by track",
        "",
        "### Gan (`dev750` Purist)",
        "",
        "| Bucket | llm lens | hybrid lens | Rules job |",
        "| --- | --- | --- | --- |",
    ]

    for bucket in (
        "ordinary_point_rate",
        "cluster_burden",
        "seizure_free",
        "range_rate",
        "no_reference_sentinel",
        "unresolved_multiple",
        "unknown_sentinel",
    ):
        a = gan_comp["llm"][bucket]
        b = gan_comp["llm_with_rules"][bucket]
        job = {
            "ordinary_point_rate": "Lift main mass out of shared floor",
            "cluster_burden": "Help, but remain practical floor",
            "seizure_free": "Create easy / common competence",
            "range_rate": "Create easy / common competence",
            "no_reference_sentinel": "Collapse wild llm variance to ceiling",
            "unresolved_multiple": "Already easy without rules",
            "unknown_sentinel": "Not clean; can hurt",
        }[bucket]
        lines.append(
            f"| `{bucket}` | {_fmt_band(a['min'], a['max'])} (**{a['lens']}**) | "
            f"{_fmt_band(b['min'], b['max'])} (**{b['lens']}**) | {job} |"
        )

    lines.extend(
        [
            "",
            f"Strict **x** without rules: "
            f"{', '.join(f'`{x}`' for x in gan_comp['strict_x_llm']) or 'none'}.  ",
            f"Strict **x** with rules: "
            f"{', '.join(f'`{x}`' for x in gan_comp['strict_x_hybrid'])}.",
            "",
            "### ExECT (`dev140` four-family clinical fact F1)",
            "",
            "| Family | llm lens | hybrid lens | Rules job |",
            "| --- | --- | --- | --- |",
        ]
    )

    for family, job in (
        ("Prescription", "Compress into common competence (**x**)"),
        ("Diagnosis", "Large inventory rescue; still **y**"),
        ("Investigations", "Little/no band change on this roster"),
        ("SeizureFrequency", "Partial precision trim; remains practical floor"),
    ):
        a = ex_comp["llm_families"][family]
        b = ex_comp["llm_with_rules_families"][family]
        lines.append(
            f"| {family} | {_fmt_band(a['min'], a['max'])} (**{a['lens']}**) | "
            f"{_fmt_band(b['min'], b['max'])} (**{b['lens']}**) | {job} |"
        )

    lines.extend(
        [
            "",
            f"Strict **x** without rules: "
            f"{', '.join(f'`{x}`' for x in ex_comp['strict_x_llm']) or 'none'}.  ",
            f"Strict **x** with rules: "
            f"{', '.join(f'`{x}`' for x in ex_comp['strict_x_hybrid'])}.",
            "",
            "## Mass first-changers inside hybrid",
            "",
            "```mermaid",
            "flowchart TB",
            '  subgraph gan["Gan llm_with_rules"]',
            "    g0[Model / resolve]",
            "    g1[Evidence reconcile<br/>selected_evidence]",
            "    g2[Clinical selection]",
            "    g3[Free-interval]",
            "    g0 --> g1 --> g2 --> g3",
            "  end",
            '  subgraph exect["ExECT llm_with_rules"]',
            "    e0[Flatten]",
            "    e1[project_and_gate]",
            "    e2[SF clinical]",
            "    e3[Diagnosis lens]",
            "    e4[Prescription lens]",
            "    e5[Investigations lens]",
            "    e0 --> e1 --> e2 --> e3 --> e4 --> e5",
            "  end",
            "```",
            "",
            "### Gan",
            "",
            "| Band / stage | First-changer rows | Role |",
            "| --- | ---: | --- |",
            f"| Evidence reconcile (`selected_evidence`) | "
            f"{gan_stage['band_first_changer_counts']['evidence_reconcile']} | "
            "Mass grammar/evidence rewrite; dominant rescue |",
            f"| Clinical selection | "
            f"{gan_stage['band_first_changer_counts']['clinical_selection']} | "
            "Next Purist lift; diary-led; main harm surface |",
            f"| Free-interval | "
            f"{gan_stage['band_first_changer_counts']['free_interval']} | "
            "Smaller, cleaner seizure-free/window commits |",
            "",
            "Residual ownership after full stack (pooled row×model): "
            f"`final_correct_after_repair` "
            f"{gan_stage['residual_ownership']['final_correct_after_repair']}, "
            f"`final_correct_no_repair` "
            f"{gan_stage['residual_ownership']['final_correct_no_repair']}, "
            f"`final_wrong_after_repair` "
            f"{gan_stage['residual_ownership']['final_wrong_after_repair']}, "
            f"`final_wrong_no_repair` "
            f"{gan_stage['residual_ownership']['final_wrong_no_repair']}.",
            "",
            "### ExECT",
            "",
            "| Family | Mass first-changer | Rescue / harm (any) | Final exact |",
            "| --- | --- | --- | ---: |",
        ]
    )

    dx = ex_stage["families"]["Diagnosis"]
    sf = ex_stage["families"]["SeizureFrequency"]
    rx = ex_stage["families"]["Prescription"]
    inv = ex_stage["families"]["Investigations"]
    dx_lens = dx["active_stages"]["lens.diagnosis"]
    sf_gate = sf["active_stages"]["project_and_gate"]
    rx_lens = rx["active_stages"]["lens.prescription"]

    lines.extend(
        [
            f"| Diagnosis | `lens.diagnosis` "
            f"({dx['band_first_changer_counts'].get('diagnosis_lens', 0)} first) | "
            f"{dx_lens['any_rescue']} / {dx_lens['any_harm']} | "
            f"{dx['final_exact_rate']:.2f} |",
            f"| SeizureFrequency | `project_and_gate` "
            f"({sf['band_first_changer_counts'].get('producer_gate', 0)} first) | "
            f"{sf_gate['any_rescue']} / {sf_gate['any_harm']} | "
            f"{sf['final_exact_rate']:.2f} |",
            f"| Prescription | `lens.prescription` "
            f"({rx['band_first_changer_counts'].get('prescription_lens', 0)} first) | "
            f"{rx_lens['any_rescue']} / {rx_lens['any_harm']} | "
            f"{rx['final_exact_rate']:.2f} |",
            f"| Investigations | near no-op "
            f"(lens fires 0; gate "
            f"{inv['band_first_changer_counts'].get('producer_gate', 0)}) | "
            "thin | "
            f"{inv['final_exact_rate']:.2f} |",
            "",
            "## Residual ownership (the four open slices)",
            "",
            "### 1. Gan `unknown_sentinel` — assertion damage after evidence",
            "",
            residuals["gan_unknown_sentinel"]["interpretation"],
            "",
            "| Band | Accuracy |",
            "| --- | ---: |",
        ]
    )
    for band, acc in residuals["gan_unknown_sentinel"]["band_accuracy"].items():
        lines.append(f"| `{band}` | {acc:.2f} |")

    delta = residuals["gan_unknown_sentinel"]["clinical_selection_mode_delta"]
    lines.extend(
        [
            "",
            "Clinical-selection mode Δ vs evidence reconcile: "
            + ", ".join(f"`{k}` {v:+d}" for k, v in delta.items())
            + ".",
            "",
            "First-changer homes on unknown gold: "
            + ", ".join(
                f"`{k}` {v}"
                for k, v in residuals["gan_unknown_sentinel"][
                    "first_changer_homes_on_unknown"
                ].items()
            )
            + ".",
            "",
            "### 2. Gan `cluster_burden` — grammar cleaned; selection residual",
            "",
            residuals["gan_cluster_burden"]["interpretation"],
            "",
            "| Band | Accuracy |",
            "| --- | ---: |",
        ]
    )
    for band, acc in residuals["gan_cluster_burden"]["band_accuracy"].items():
        lines.append(f"| `{band}` | {acc:.2f} |")

    modes = residuals["gan_cluster_burden"]["final_wrong_modes"]
    ee = residuals["gan_cluster_burden"].get("hard_slice_hybrid_exact_evidence") or {}
    ee_rate = ee.get("exact_evidence_rate")
    ee_note = (
        f" Hard-slice exact selected evidence among hybrid wrongs: "
        f"{ee.get('exact_evidence')}/{ee.get('n_wrong_rows_pooled')} "
        f"({ee_rate:.2f})."
        if ee_rate is not None
        else ""
    )
    lines.extend(
        [
            "",
            "Final wrong modes: "
            + ", ".join(f"`{k}` {v}" for k, v in modes.items())
            + "."
            + ee_note,
            "",
            "### 3. ExECT SeizureFrequency — gate rescues; inventory remains",
            "",
            residuals["exect_sf_inventory"]["interpretation"],
            "",
            "| Band | Exact |",
            "| --- | ---: |",
        ]
    )
    for band, acc in residuals["exect_sf_inventory"]["band_exact"].items():
        lines.append(f"| `{band}` | {acc:.2f} |")

    sf_modes = residuals["exect_sf_inventory"]["final_modes"]
    lines.extend(
        [
            "",
            "Final imperfect / correct modes: "
            + ", ".join(
                f"`{k}` {v}"
                for k, v in sf_modes.items()
                if not k.startswith("correct") or k
            )
            + ".",
            "",
            "### 4. ExECT Prescription lens — measured net harm",
            "",
            residuals["exect_prescription_lens_harm"]["interpretation"],
            "",
            "| Checkpoint | Exact |",
            "| --- | ---: |",
            f"| Before Rx lens | "
            f"{residuals['exect_prescription_lens_harm']['band_exact']['pre_rx_lens']:.2f} |",
            f"| After Rx lens | "
            f"{residuals['exect_prescription_lens_harm']['band_exact']['after_rx_lens']:.2f} |",
            "",
            f"`lens.prescription`: fires "
            f"{rx_lens['fires']}, first "
            f"{rx_lens['first_changer']}, any-rescue "
            f"{rx_lens['any_rescue']}, any-harm "
            f"{rx_lens['any_harm']}.",
            "",
            "### Investigations note",
            "",
            residuals["exect_investigations_noop"]["interpretation"],
            "",
            "## What this changes about “models perform similarly”",
            "",
            "| Surface | Overall similarity means |",
            "| --- | --- |",
            "| Gan `llm` | Shared weakness on ordinary rates + clusters |",
            "| Gan hybrid | Shared strength on free/range/sentinel mass; "
            "clusters / unknown still break it |",
            "| ExECT `llm` | No strict **x**; Diagnosis + SF pull everyone down |",
            "| ExECT hybrid | Prescription carries ease; SF still separates |",
            "",
            "Compatible with "
            "[why the error floor persists](why_the_error_floor_persists_2026-07-31.md): "
            "evidence is usually present; forced clinical choice and required "
            "label/inventory shape are what remain.",
            "",
            "## Paper / claim packaging",
            "",
            "Safe development wording supported by this ladder:",
            "",
            "- Hybrid competence on these development surfaces is attributable "
            "to named deterministic stages, not an undifferentiated “rules” blob.",
            "- Gan hybrid lift is mostly evidence reconcile plus smaller "
            "clinical-selection effects; ExECT hybrid lift is family-specific.",
            "- Some deterministic stages can harm (`unknown_sentinel` clinical "
            "selection; ExECT Prescription lens).",
            "",
            "Do **not** claim from this synthesis alone:",
            "",
            "- holdout generalization of category or stage effects;",
            "- leave-one-stage-out necessity;",
            "- that turning off Prescription lens or unknown-asserting repairs "
            "would raise Decision 0046 / C16 headlines;",
            "- cross-task numerical ranking or reliability transfer;",
            "- clinical validation.",
            "",
            "## Still open",
            "",
        ]
    )
    for item in artifact["blocked_or_unanswered"]:
        lines.append(f"- **{item['id']}** ({item['status']}): {item['note']}")

    lines.extend(
        [
            "",
            "## Next executable actions",
            "",
            "1. Keep operational primary on the fixed vLLM dev10 endpoint task "
            "(unchanged by this synthesis).",
            "2. Done: ExECT Prescription lens on/off counterfactual — "
            "[report](exectv2_prescription_lens_counterfactual_2026-08-06.md) "
            "(mixed metric split; no default rewrite).",
            "3. Done: Gan `unknown_sentinel` clinical-selection harm catalog — "
            "[report](gan2026_unknown_sentinel_clinical_harm_2026-08-06.md).",
            "4. Optional sealed holdout category aggregates under protocol.",
            "5. Do not authorize repair or lens rewrites from this packaging "
            "page alone.",
            "",
            "## How to explore further",
            "",
            "| Need | Where |",
            "| --- | --- |",
            "| Machine-readable synthesis tables | JSON artifact |",
            "| Gan stage ledger | [Gan hybrid stage ablation]"
            "(gan2026_hybrid_stage_ablation_2026-08-06.md) |",
            "| ExECT stage ledger | [ExECT hybrid stage ablation]"
            "(exectv2_hybrid_stage_ablation_2026-08-06.md) |",
            "| Full error-mode catalogs | "
            "[Gan](gan2026_category_error_catalog_2026-08-06.md), "
            "[ExECT](exectv2_family_error_catalog_2026-08-06.md) |",
            "| Regenerate this page | "
            "`python scripts/build_cross_task_hybrid_mechanism_synthesis.py` |",
            "",
            "## Method",
            "",
            "- No new model calls.",
            "- Inputs: retained 2026-08-06 category-cut, catalog, stage-ablation, "
            "and hard-slice JSON artifacts.",
            "- Attribution language inherits parent first-changer definitions.",
            f"- Git at build: `{artifact['git']['commit']}`"
            f"{' (dirty tree)' if artifact['git']['dirty_tree'] else ''}.",
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
        / f"experiments/cross_task_hybrid_mechanism_synthesis_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/cross_task_hybrid_mechanism_synthesis_{REPORT_DATE}.md",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")


if __name__ == "__main__":
    main()
