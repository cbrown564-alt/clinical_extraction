"""Compact reliability scorecard for the ExECTv2 GPT-first hybrid (satellite 09, Phase E).

Turns a combined all-entity hybrid run into the compact scorecard the plan's
measurement plan asks for, with a per-letter (cluster) bootstrap CI on the
benchmark + semantic headlines and an explicit promotion-gate verdict. It reads
an existing combined JSONL — it never makes model calls and never touches the
locked test split. The full-200 audit is **gated**: this scorecard only reports
whether the dev evidence clears the freeze targets; it does not authorize or run
the holdout.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from clinical_extraction.core.scoring import PRF1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ALL_ENTITIES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    MatchConfig,
    benchmark_config_for,
    score_overall,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.bootstrap import (
    BootstrapCI,
    bootstrap_f1_ci,
)

ENTITY_NAMES: tuple[str, ...] = tuple(spec.name for spec in ALL_ENTITIES)
FREEZE_TARGET_PER_ITEM = 0.87
FREEZE_TARGET_PER_LETTER = 0.90
PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97, "Diagnosis": 0.85, "EpilepsyCause": 0.90,
    "Investigations": 0.95, "Onset": 0.96, "PatientHistory": 0.78,
    "Prescription": 0.87, "SeizureFrequency": 0.66, "WhenDiagnosed": 0.91,
}


def _single_letters(row: dict[str, Any]) -> tuple[ExectLetter, ExectLetter]:
    gold = ExectLetter(
        letter_id=row["letter_id"],
        note_text="",
        annotations=tuple(
            ExectAnnotation(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
            )
            for m in (row.get("gold_mentions") or [])
        ),
    )
    pred_letter = PredictedLetter(
        letter_id=row["letter_id"],
        mentions=tuple(
            PredictedMention(
                entity=str(m["entity"]),
                text=str(m["text"]),
                attributes={str(k): str(v) for k, v in (m.get("attributes") or {}).items()},
                evidence="",
            )
            for m in (row.get("predicted_mentions") or [])
        ),
    )
    return gold, to_exect_letter(pred_letter)


def _per_letter_counts(
    rows: Sequence[dict[str, Any]],
    config_for: Callable[[str], MatchConfig],
    *,
    level: str,
) -> list[tuple[int, int, int]]:
    """Per-letter (tp, fp, fn) summed over all entities, item- or letter-level."""
    counts: list[tuple[int, int, int]] = []
    for row in rows:
        gold, pred = _single_letters(row)
        overall = score_overall([gold], [pred], ENTITY_NAMES, config_for)
        prf: PRF1 = overall.per_item if level == "item" else overall.per_letter
        counts.append((prf.tp, prf.fp, prf.fn))
    return counts


def build_scorecard(
    rows: Sequence[dict[str, Any]],
    summary: dict[str, Any],
    *,
    model: str,
    split: str,
    augment_rules: bool,
    bootstrap_reps: int = 1000,
) -> dict[str, Any]:
    """Assemble the compact reliability scorecard from a combined hybrid run."""
    scores = summary.get("scores", {})
    semantic = scores.get("semantic", {})
    benchmark = scores.get("benchmark", {})
    bench_item = benchmark.get("per_item", {})
    bench_letter = benchmark.get("per_letter", {})

    sem_ci = bootstrap_f1_ci(
        _per_letter_counts(rows, semantic_config_for, level="item"), reps=bootstrap_reps
    )
    bench_ci = bootstrap_f1_ci(
        _per_letter_counts(rows, benchmark_config_for, level="item"), reps=bootstrap_reps
    )

    gate_item = bench_item.get("f1", 0.0) >= FREEZE_TARGET_PER_ITEM
    gate_letter = bench_letter.get("f1", 0.0) >= FREEZE_TARGET_PER_LETTER
    gate_met = gate_item and gate_letter

    per_entity_bench = benchmark.get("per_entity", {})
    per_entity_sem = semantic.get("per_entity", {})
    robustness = []
    for entity in ENTITY_NAMES:
        bf1 = per_entity_bench.get(entity, {}).get("per_item", {}).get("f1", 0.0)
        sf1 = per_entity_sem.get(entity, {}).get("per_item", {}).get("f1", 0.0)
        target = PUBLISHED_PER_ENTITY_ITEM_F1.get(entity, 0.0)
        robustness.append(
            {
                "entity": entity,
                "semantic_item_f1": sf1,
                "benchmark_item_f1": bf1,
                "published_target": target,
                "gap_to_target": round(bf1 - target, 4),
            }
        )

    routed = summary.get("routed_taxonomy", {})
    proj = summary.get("projection_ablation", {}).get("overall", {})
    return {
        "split": split,
        "model": model,
        "augment_rules": augment_rules,
        "letters": summary.get("examples", 0),
        "dimensions": {
            "task_correctness": {
                "semantic_item_f1": semantic.get("per_item", {}).get("f1", 0.0),
                "semantic_item_f1_ci": [sem_ci.lower, sem_ci.upper],
                "benchmark_item_f1": bench_item.get("f1", 0.0),
                "benchmark_item_f1_ci": [bench_ci.lower, bench_ci.upper],
                "benchmark_letter_f1": bench_letter.get("f1", 0.0),
                "phrase_item_f1": scores.get("phrase_only", {}).get("per_item", {}).get("f1", 0.0),
            },
            "candidate_generation": {
                "source_near_recall": summary.get("diagnostic_ladder", {})
                .get("source_near", {})
                .get("overall", {})
                .get("overlap", {})
                .get("recall", 0.0),
            },
            "faithfulness": {
                "evidence_not_substring_routed": routed.get("evidence_not_substring", 0)
                + routed.get("empty_evidence", 0),
            },
            "schema_reliability": {
                "routed_taxonomy": routed,
                "mentions_scored": summary.get("n_mentions_scored", 0),
                "candidates": summary.get("n_candidates", 0),
            },
            "benchmark_format": {
                "semantic_minus_benchmark_item_f1": round(
                    semantic.get("per_item", {}).get("f1", 0.0)
                    - bench_item.get("f1", 0.0),
                    4,
                ),
                "projection_delta_item_f1": proj.get("delta_item_f1", 0.0),
            },
            "calibration_routing": {
                "routed_total": summary.get("n_routed", 0),
                "by_reason": routed,
            },
            "robustness": robustness,
            "operational": {
                "candidates": summary.get("n_candidates", 0),
                "scored": summary.get("n_mentions_scored", 0),
                "routed": summary.get("n_routed", 0),
            },
        },
        "promotion_gate": {
            "freeze_target_per_item": FREEZE_TARGET_PER_ITEM,
            "freeze_target_per_letter": FREEZE_TARGET_PER_LETTER,
            "benchmark_per_item_f1": bench_item.get("f1", 0.0),
            "benchmark_per_letter_f1": bench_letter.get("f1", 0.0),
            "gate_met": gate_met,
            "full_200_audit_authorized": gate_met,
            "verdict": (
                "Dev evidence clears the freeze targets; full-200 audit may be "
                "predeclared and registered."
                if gate_met
                else "Dev evidence does NOT clear the freeze targets; the full-200 "
                "holdout audit is NOT authorized."
            ),
        },
    }


def render_markdown(scorecard: dict[str, Any], *, source: str = "") -> str:
    dims = scorecard["dimensions"]
    tc = dims["task_correctness"]
    gate = scorecard["promotion_gate"]
    lines = [
        "# ExECTv2 GPT-First Reliability Scorecard (Phase E)",
        "",
    ]
    if source:
        lines.append(f"- Source: `{source}`")
    lines.extend([
        f"- Split: `{scorecard['split']}`  Letters: {scorecard['letters']}",
        f"- Candidate model: `{scorecard['model']}`  Rule augmentation: "
        f"`{scorecard['augment_rules']}`",
        "",
        "## Promotion gate",
        "",
        f"- Freeze targets: per-item {gate['freeze_target_per_item']:.2f} / "
        f"per-letter {gate['freeze_target_per_letter']:.2f} (benchmark, with-CUI).",
        f"- Benchmark per-item F1: {gate['benchmark_per_item_f1']:.3f}  "
        f"per-letter F1: {gate['benchmark_per_letter_f1']:.3f}",
        f"- **Gate met: {gate['gate_met']}** — full-200 audit authorized: "
        f"{gate['full_200_audit_authorized']}.",
        f"- {gate['verdict']}",
        "",
        "## Scorecard dimensions",
        "",
        "| Dimension | Reading |",
        "| --- | --- |",
        f"| Task correctness | semantic item F1 {tc['semantic_item_f1']:.3f} "
        f"CI[{tc['semantic_item_f1_ci'][0]:.3f}, {tc['semantic_item_f1_ci'][1]:.3f}]; "
        f"benchmark item F1 {tc['benchmark_item_f1']:.3f} "
        f"CI[{tc['benchmark_item_f1_ci'][0]:.3f}, {tc['benchmark_item_f1_ci'][1]:.3f}]; "
        f"letter F1 {tc['benchmark_letter_f1']:.3f} |",
        f"| Candidate generation | source-near recall "
        f"{dims['candidate_generation']['source_near_recall']:.3f} |",
        f"| Faithfulness | evidence-routed "
        f"{dims['faithfulness']['evidence_not_substring_routed']} mentions |",
        f"| Schema reliability | scored {dims['schema_reliability']['mentions_scored']} "
        f"/ {dims['schema_reliability']['candidates']} candidates |",
        f"| Benchmark format | semantic−benchmark item F1 "
        f"{dims['benchmark_format']['semantic_minus_benchmark_item_f1']:+.3f}; "
        f"projection Δ {dims['benchmark_format']['projection_delta_item_f1']:+.3f} |",
        f"| Calibration/routing | routed {dims['calibration_routing']['routed_total']} "
        f"by reason {dims['calibration_routing']['by_reason']} |",
        f"| Operational | candidates {dims['operational']['candidates']}, "
        f"scored {dims['operational']['scored']}, routed {dims['operational']['routed']} |",
        "",
        "## Robustness — per-entity benchmark item F1 vs published target",
        "",
        "| Entity | Semantic F1 | Benchmark F1 | Published | Gap |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for r in dims["robustness"]:
        lines.append(
            f"| {r['entity']} | {r['semantic_item_f1']:.3f} | {r['benchmark_item_f1']:.3f} "
            f"| {r['published_target']:.2f} | {r['gap_to_target']:+.3f} |"
        )
    lines.append("")
    return "\n".join(lines)
