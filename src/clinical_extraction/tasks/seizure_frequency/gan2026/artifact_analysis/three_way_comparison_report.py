"""Phase 1 three-way architecture comparison report (gpt-4.1-mini, validation750).

Assembles the shared comparison table and hybrid-only routing appendix designed in
docs/research/gan2026_three_way_comparison_phase1_report_design_2026-06-07.md by
reading the six already-completed gpt-4.1-mini validation750 run artifacts. This
module makes no model calls and performs no re-run.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import CandidateSet
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.reports.base import write_markdown_report
from clinical_extraction.tasks.seizure_frequency.gan2026.runner import (
    build_unified_pipeline_artifact,
)

ARCHITECTURES: tuple[str, ...] = (
    "deterministic",
    "deterministic_canonical_pipeline",
    "hybrid",
    "llm_only_direct_labeler",
    "llm_only_structured_events",
    "llm_only_canonical_pipeline",
)

DEFAULT_ARTIFACT_JSONL_PATHS: dict[str, Path] = {
    "deterministic": Path(
        "experiments/gan2026_three_way_comparison_validation750_deterministic"
        "_gpt41mini_2026-06-07.jsonl"
    ),
    "deterministic_canonical_pipeline": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_deterministic_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
    ),
    "hybrid": Path(
        "experiments/gan2026_three_way_comparison_validation750_hybrid"
        "_live_candidate_sets_gpt41mini_2026-06-08.jsonl"
    ),
    "llm_only_direct_labeler": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl"
    ),
    "llm_only_structured_events": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_structured_events_gpt41mini_2026-06-07.jsonl"
    ),
    "llm_only_canonical_pipeline": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
    ),
}

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_three_way_comparison_phase1_report_gpt41mini_validation750_2026-06-08.md"
)

CLAIM_BOUNDARY = (
    "Phase 1 three-way architecture comparison, gpt-4.1-mini pass, validation750 only. "
    "No test450 read, no holdout-facing or benchmark-comparable claim. Compares six "
    "PipelineArchitecture configs on the axes that are universally meaningful "
    "(rendered/null disposition, Purist/Pragmatic-correct of rendered rows, "
    "evidence-trace validity, final-answer distribution); hybrid additionally carries "
    "a routing-taxonomy appendix that no other architecture has an analogous surface for."
)

EVIDENCE_TRACE_FOOTNOTE = (
    "Evidence-trace metrics are NOT uniform across architectures: deterministic, "
    "deterministic_canonical_pipeline, llm_only_direct_labeler, and "
    "llm_only_structured_events report `evidence_valid` (free-text substring presence "
    "in the source note); llm_only_canonical_pipeline reports the deliberately distinct "
    "`evidence_text_contained`; hybrid reports a formal CandidateSet source-id validity "
    "rate sourced from its deep-replay projection stage. These measure different things "
    "-- do not read them as comparable accuracy numbers (see the per-architecture metric "
    "table below the shared table)."
)

HYBRID_DATA_SOURCE_FOOTNOTE = (
    "hybrid's row above is the only one not sourced from raw `run_split` output: its "
    "assessment-stage probe reports schema-fit diagnostics only and has no "
    "rendered/null/purist/routed numbers of its own (design doc Section 2-3). This "
    "report replays its assessment rows -- using the live-generated CandidateSets the "
    "fixed `run_split` now embeds in its own output rows, so no static-artifact "
    "dependency or 250-row scoping applies -- through "
    "projection_render -> score -> verification_route -> verification_decision "
    "(`build_unified_pipeline_artifact`). This asymmetry is the architectural fact "
    "under comparison, not a methodology artifact."
)


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _rendered_split(
    architecture: str,
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[Mapping[str, Any]]]:
    """Split rows into (rendered, null) using each architecture's own give-up signal.

    The five single-shot architectures express "gave up" three different ways:
    deterministic/deterministic_canonical_pipeline emit the literal final_label
    `"unknown"`; llm_only_direct_labeler/llm_only_canonical_pipeline never give up
    structurally (every row carries a `decision_record.final_label`, even when the
    answer is a scoring category like `seizure_freq_unknown` -- that is a *scoring*
    category, not a render-failure signal, so all of their rows count as rendered);
    llm_only_structured_events has no single rendered-label string and instead
    exposes a scorable predicted category per row, absent only on the rare parse
    failure.
    """
    if architecture in ("deterministic", "deterministic_canonical_pipeline"):
        rendered = [row for row in rows if row.get("final_label") != "unknown"]
    elif architecture in ("llm_only_direct_labeler", "llm_only_canonical_pipeline"):
        rendered = [
            row for row in rows if (row.get("decision_record") or {}).get("final_label") is not None
        ]
    elif architecture == "llm_only_structured_events":
        rendered = [
            row
            for row in rows
            if (row.get("comparison") or {}).get("predicted_purist_category") is not None
        ]
    else:
        raise ValueError(f"_rendered_split does not support architecture {architecture!r}")
    rendered_indices = {int(row["source_row_index"]) for row in rendered}
    null_rows = [row for row in rows if int(row["source_row_index"]) not in rendered_indices]
    return rendered, null_rows


def _evidence_trace_metric(
    architecture: str,
    rows: Sequence[Mapping[str, Any]],
) -> tuple[str, int, int]:
    """Return (metric_name, valid_rows, denominator) for one architecture's row set.

    `evidence_valid` (substring presence) and `evidence_text_contained` are
    deliberately distinct metrics (design doc Section 2/4) -- never conflate them.
    """
    if architecture == "llm_only_canonical_pipeline":
        key, metric_name = "evidence_text_contained", "evidence_text_contained"
    else:
        key, metric_name = "evidence_valid", "evidence_valid"
    valid = sum(1 for row in rows if row.get(key) is True)
    return metric_name, valid, len(rows)


def _final_label_distribution(architecture: str, rows: Sequence[Mapping[str, Any]]) -> Counter[str]:
    if architecture in ("deterministic", "deterministic_canonical_pipeline"):
        return Counter(str(row.get("final_label")) for row in rows)
    if architecture in ("llm_only_direct_labeler", "llm_only_canonical_pipeline"):
        return Counter(str((row.get("decision_record") or {}).get("final_label")) for row in rows)
    if architecture == "llm_only_structured_events":
        return Counter(
            str((row.get("comparison") or {}).get("predicted_purist_category")) for row in rows
        )
    raise ValueError(f"_final_label_distribution does not support architecture {architecture!r}")


def _single_shot_summary_row(architecture: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    rendered, null_rows = _rendered_split(architecture, rows)
    purist_correct = sum(bool((row.get("comparison") or {}).get("purist_correct")) for row in rendered)
    pragmatic_correct = sum(
        bool((row.get("comparison") or {}).get("pragmatic_correct")) for row in rendered
    )
    evidence_metric_name, evidence_valid_rows, evidence_denominator = _evidence_trace_metric(
        architecture, rows
    )
    return {
        "architecture": architecture,
        "data_source": "run_split",
        "examples": len(rows),
        "rendered_rows": len(rendered),
        "null_rows": len(null_rows),
        "routed_rows": None,
        "purist_correct_of_rendered": purist_correct,
        "purist_correct_rate_of_rendered": _rate(purist_correct, len(rendered)),
        "pragmatic_correct_of_rendered": pragmatic_correct,
        "pragmatic_correct_rate_of_rendered": _rate(pragmatic_correct, len(rendered)),
        "evidence_trace_metric": evidence_metric_name,
        "evidence_trace_valid_rows": evidence_valid_rows,
        "evidence_trace_valid_rate": _rate(evidence_valid_rows, evidence_denominator),
        "final_label_distribution": dict(
            _final_label_distribution(architecture, rows).most_common(12)
        ),
    }


def _hybrid_candidate_sets(rows: Sequence[Mapping[str, Any]]) -> dict[int, CandidateSet]:
    """Reconstruct hybrid's CandidateSet inputs from its own (now-embedded) output rows.

    The fixed `run_split` embeds the full live-generated `candidate_set` on every row
    (see llm_candidate_set_clinical_assessment_probe.run_split), so the deep-replay
    Mapping[int, CandidateSet] this report needs comes from the run's own artifact --
    no static 250-row file dependency.
    """
    candidate_sets: dict[int, CandidateSet] = {}
    for row in rows:
        raw_candidate_set = row.get("candidate_set")
        if raw_candidate_set is None:
            continue
        candidate_sets[int(row["source_row_index"])] = CandidateSet.model_validate(raw_candidate_set)
    return candidate_sets


def _hybrid_final_label_distribution(
    route_rows: Sequence[Mapping[str, Any]],
    decision_rows: Sequence[Mapping[str, Any]],
) -> Counter[str]:
    """Combine route-stage pass-through labels with decision-stage overrides.

    Only routed rows reach `verification_decision` -- the V0 deterministic
    baseline acts on routed rows only (clinical_assessment_verification_decision
    .build_verification_decision_artifact filters on `verification_route.routed`)
    and its `final_rendered_label` is a plain string-or-None (a string only on
    `affirm`; None on every other action == abstention). Unrouted rows never
    reach that stage and keep the dict-shaped
    `final_rendered_label.rendered_label` that `verification_route` passed
    through unchanged from `projection_render`. The two stages use different
    shapes for the "same" field name -- this merges them into one
    row -> label map representing the architecture's actual final answer.
    """
    decided_labels: dict[int, str | None] = {
        int(row["source_row_index"]): (row.get("verification_decision") or {}).get(
            "final_rendered_label"
        )
        for row in decision_rows
    }
    counts: Counter[str] = Counter()
    for row in route_rows:
        source_row_index = int(row["source_row_index"])
        if source_row_index in decided_labels:
            label = decided_labels[source_row_index]
        else:
            label = (row.get("final_rendered_label") or {}).get("rendered_label")
        counts[str(label)] += 1
    return counts


def _hybrid_summary_row(
    rows: Sequence[Mapping[str, Any]],
    *,
    gold_records: Mapping[int, GanFrequencyRecord],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build hybrid's shared-table row AND its routing appendix from one deep-replay.

    hybrid's run_split is an assessment-stage probe with no rendered/null/purist/
    routed numbers of its own (design doc Section 2-3) -- both surfaces here are
    sourced from replaying its assessment rows through
    projection_render -> score -> verification_route -> verification_decision
    (`build_unified_pipeline_artifact`), not from raw `run_split` output. One
    assembly, two presentations: shared-table row + routing appendix.
    """
    candidate_sets = _hybrid_candidate_sets(rows)
    artifact = build_unified_pipeline_artifact(
        architecture="hybrid",
        assessment_rows=rows,
        candidate_sets=candidate_sets,
        gold_records=gold_records,
    )
    summary = artifact.metadata["summary"]
    score_summary = dict(artifact.metadata["stage_metadata"]["score"].get("summary") or {})
    route_summary = dict(artifact.metadata["stage_metadata"]["route"].get("summary") or {})
    decision_summary = dict(
        artifact.metadata["stage_metadata"]["verification_decision"].get("summary") or {}
    )

    rendered = int(summary["rendered_label_rows"])
    purist_correct = int(score_summary.get("purist_correct", 0))
    pragmatic_correct = int(score_summary.get("pragmatic_correct", 0))
    source_id_valid = sum(
        1
        for row in artifact.projection_render_rows
        if (
            ((row.get("projection_decision") or {}).get("selected_evidence_status") or {}).get(
                "source_id_status"
            )
        )
        == "valid"
    )
    final_label_counts = _hybrid_final_label_distribution(
        artifact.route_rows, artifact.decision_rows
    )

    summary_row = {
        "architecture": "hybrid",
        "data_source": "build_unified_pipeline_artifact_deep_replay",
        "examples": int(summary["input_assessment_rows"]),
        "rendered_rows": rendered,
        "null_rows": int(summary["null_rendered_label_rows"]),
        "routed_rows": int(summary["routed_rows"]),
        "purist_correct_of_rendered": purist_correct,
        "purist_correct_rate_of_rendered": _rate(purist_correct, rendered),
        "pragmatic_correct_of_rendered": pragmatic_correct,
        "pragmatic_correct_rate_of_rendered": _rate(pragmatic_correct, rendered),
        "evidence_trace_metric": "candidate_set_source_id_status==valid",
        "evidence_trace_valid_rows": source_id_valid,
        "evidence_trace_valid_rate": _rate(source_id_valid, len(artifact.projection_render_rows)),
        "final_label_distribution": dict(final_label_counts.most_common(12)),
    }
    routed_rows = int(route_summary.get("routed_rows", 0))
    appendix = {
        "routed_rows": routed_rows,
        "unrouted_rows": int(route_summary.get("unrouted_rows", 0)),
        "routed_rate_of_rendered": _rate(routed_rows, rendered),
        "route_family_counts": dict(route_summary.get("route_family_counts") or {}),
        "action_counts": dict(decision_summary.get("action_counts") or {}),
    }
    return summary_row, appendix


def build_three_way_comparison_report(
    architecture_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    gold_records: Mapping[int, GanFrequencyRecord],
    model: str = "openai/gpt-4.1-mini",
    split: str = "validation",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    missing = [name for name in ARCHITECTURES if name not in architecture_rows]
    if missing:
        raise ValueError(f"missing architecture rows for: {missing}")

    summary_rows: list[dict[str, Any]] = []
    hybrid_appendix: dict[str, Any] = {}
    for architecture in ARCHITECTURES:
        rows = architecture_rows[architecture]
        if architecture == "hybrid":
            summary_row, hybrid_appendix = _hybrid_summary_row(rows, gold_records=gold_records)
        else:
            summary_row = _single_shot_summary_row(architecture, rows)
        summary_rows.append(summary_row)

    metadata = {
        "artifact_kind": "gan2026_three_way_comparison_phase1_report",
        "claim_boundary": CLAIM_BOUNDARY,
        "model": model,
        "split": split,
        "row_counts": {row["architecture"]: row["examples"] for row in summary_rows},
        "evidence_trace_footnote": EVIDENCE_TRACE_FOOTNOTE,
        "hybrid_data_source_footnote": HYBRID_DATA_SOURCE_FOOTNOTE,
        "hybrid_routing_appendix": hybrid_appendix,
    }
    return summary_rows, metadata


def write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    write_jsonl_rows(rows, path)


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Phase 1 Three-Way Architecture Comparison (gpt-4.1-mini, validation750)",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Comparison JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Model: `{metadata['model']}`",
        f"- Split: `{metadata['split']}`",
        "",
        "## Shared Comparison Table",
        "",
        "| Architecture | Examples | Rendered | Null | Routed | "
        "Purist-correct (of rendered) | Pragmatic-correct (of rendered) | "
        "Evidence-trace valid | Source |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        routed = "N/A" if row["routed_rows"] is None else str(row["routed_rows"])
        lines.append(
            f"| `{row['architecture']}` | {row['examples']} | {row['rendered_rows']} | "
            f"{row['null_rows']} | {routed} | "
            f"{row['purist_correct_of_rendered']} "
            f"({row['purist_correct_rate_of_rendered']:.3f}) | "
            f"{row['pragmatic_correct_of_rendered']} "
            f"({row['pragmatic_correct_rate_of_rendered']:.3f}) | "
            f"{row['evidence_trace_valid_rows']} ({row['evidence_trace_valid_rate']:.3f}) | "
            f"`{row['data_source']}` |"
        )
    lines.extend(
        [
            "",
            "Footnotes:",
            "",
            f"- {metadata['evidence_trace_footnote']}",
            f"- {metadata['hybrid_data_source_footnote']}",
            "",
            "### Evidence-Trace Metric By Architecture",
            "",
            "| Architecture | Metric reported |",
            "| --- | --- |",
        ]
    )
    for row in rows:
        lines.append(f"| `{row['architecture']}` | `{row['evidence_trace_metric']}` |")
    lines.extend(["", "### Final-Answer Distribution (top entries)", ""])
    for row in rows:
        lines.append(f"- `{row['architecture']}`: {row['final_label_distribution']}")

    appendix = dict(metadata.get("hybrid_routing_appendix") or {})
    lines.extend(
        [
            "",
            "## Hybrid-Only Routing Appendix",
            "",
            (
                "No other architecture in this comparison has a routing stage; this "
                "appendix exists to characterize what `hybrid` does with the rows it "
                "doesn't render directly, not to provide a column the other five could "
                "also fill. Drawn from the same deep-replay artifact that supplies "
                "hybrid's shared-table row above."
            ),
            "",
            f"- Routed rows: {appendix.get('routed_rows', 0)} "
            f"({appendix.get('routed_rate_of_rendered', 0.0):.3f} of rendered)",
            f"- Unrouted rows: {appendix.get('unrouted_rows', 0)}",
            "",
            "### Route Family Counts",
            "",
        ]
    )
    family_counts = appendix.get("route_family_counts") or {}
    if not family_counts:
        lines.append("- None.")
    for family, count in family_counts.items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "### Verification Decision Action Counts", ""])
    action_counts = appendix.get("action_counts") or {}
    if not action_counts:
        lines.append("- None.")
    for action, count in action_counts.items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(
        [
            "",
            "## What This Report Does Not Claim",
            "",
            "- validation750-only; no `test450` read; no holdout-facing or "
            "benchmark-comparable claim.",
            "- Evidence-trace metrics are not uniform across architectures (see "
            "footnote and per-architecture metric table above) -- they measure "
            "different things and must not be compared as if they were one accuracy "
            "number.",
            "- hybrid's shared-table numbers come from deep-replay, not its raw "
            "`run_split` output (see footnote above); the other five architectures' "
            "numbers come directly from their `run_split` output.",
            "",
        ]
    )
    write_markdown_report(path, lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for architecture in ARCHITECTURES:
        parser.add_argument(
            f"--{architecture.replace('_', '-')}-jsonl",
            type=Path,
            default=DEFAULT_ARTIFACT_JSONL_PATHS[architecture],
        )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    architecture_rows = {
        architecture: load_jsonl_rows(getattr(args, f"{architecture}_jsonl"))
        for architecture in ARCHITECTURES
    }
    gold_records = {
        record.source_row_index: record for record in load_records_for_split("validation")
    }
    rows, metadata = build_three_way_comparison_report(architecture_rows, gold_records=gold_records)
    write_jsonl(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps({"row_counts": metadata["row_counts"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
