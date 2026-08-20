"""Manifest-driven clinical finding assembly pipeline."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.finding_store import (
    ClinicalFindingStore,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.lenses import (
    LensPolicy,
    lens_from_manifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
    FindingAssemblyManifest,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.producers import (
    SavedJsonlProducer,
    findings_from_row,
    lane_diagnostics_from_row,
    status_from_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    FindingViewResult,
    build_scoring_views,
    changed_row_accounting,
    comparator_predictions_from_rows,
    control_predictions_from_rows,
    predictions_from_prediction_surface,
    predictions_from_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (
    TARGET_INDICATORS,
)

BASELINE_HEADLINES = {
    DIAGNOSIS.name: 0.6693,
    SEIZURE_FREQUENCY.name: 0.5572,
    PRESCRIPTION.name: 0.8214,
    INVESTIGATIONS.name: 0.8615,
}
FOCUSED_ROUTE_HEADLINES = {
    DIAGNOSIS.name: 0.7127,
    SEIZURE_FREQUENCY.name: 0.6321,
}
BASELINE_DX_CONCEPT_NEGATION = 0.6693
# Lower-bound regression gate ("must beat"), not a frozen equality target. The
# 2026-07-08 point/range shape-equivalence fix (scoring/normalize.py:
# resolve_point_range -- a bare count/cadence and an equal-bounds Lower/Upper
# range now key identically) only ever raises active_rate_fidelity, so this
# threshold stays a safe (if now conservative) floor and needs no change.
BASELINE_SF_ACTIVE_RATE_FIDELITY = 0.2887
MATERIALIZED_SURFACES = (
    "source_scored",
    "evidence_valid",
    "format_only",
    "protocol_model_preserving_canonical",
    "dictionary_normalized",
    "residual_benchmark_added",
)


@dataclass(frozen=True)
class AssemblyRun:
    manifest: FindingAssemblyManifest
    rows: list[dict[str, Any]]
    report: dict[str, Any]
    stores: Mapping[str, ClinicalFindingStore]
    views: Mapping[str, FindingViewResult]


GoldLoader = Callable[[str], list[ExectLetter]]


def build_finding_assembly(
    manifest: FindingAssemblyManifest,
    *,
    generated_on: str | None = None,
    gold_loader: GoldLoader = load_letters_for_split,
    diagnosis_resolution_candidate: bool = False,
    model_preserving_policy_candidate: bool = False,
    prescription_rescue_scope_candidate: bool = False,
    prescription_policy_variant: str = "default",
    diagnosis_policy_variant: str = "default",
) -> AssemblyRun:
    """Build a no-call finding assembly from saved producer artifacts."""

    generated_on = generated_on or date.today().isoformat()
    gold_letters = gold_loader(manifest.split)[: manifest.row_count]
    producers = {
        producer_id: SavedJsonlProducer.from_manifest(producer_manifest)
        for producer_id, producer_manifest in manifest.producers.items()
    }
    source_rows = {
        producer_id: producer.rows_by_id() for producer_id, producer in producers.items()
    }
    _validate_source_rows(gold_letters, source_rows, producers)
    comparator_rows = (
        _rows_by_id(manifest.focused_comparator_artifact)
        if manifest.focused_comparator_artifact is not None
        and manifest.focused_comparator_artifact.exists()
        else None
    )
    rows: list[dict[str, Any]] = []
    stores: dict[str, ClinicalFindingStore] = {}
    for letter in gold_letters:
        store, row = _assemble_letter(
            letter,
            manifest=manifest,
            producers=producers,
            source_rows=source_rows,
            diagnosis_resolution_candidate=diagnosis_resolution_candidate,
            model_preserving_policy_candidate=model_preserving_policy_candidate,
            prescription_rescue_scope_candidate=prescription_rescue_scope_candidate,
            prescription_policy_variant=prescription_policy_variant,
            diagnosis_policy_variant=diagnosis_policy_variant,
        )
        stores[letter.letter_id] = store
        rows.append(row)
    _validate_replay_rows(rows, gold_letters)

    raw_predictions = predictions_from_rows(rows, "raw_lane_mentions")
    scored_predictions = predictions_from_rows(rows, "predicted_mentions")
    materialized_predictions = {
        surface_key: predictions_from_prediction_surface(rows, surface_key)
        for surface_key in MATERIALIZED_SURFACES
    }
    views, score_ladder, target_report = build_scoring_views(
        candidate_name=manifest.candidate_id,
        ownership=manifest.ownership,
        gold_letters=gold_letters,
        raw_predictions=raw_predictions,
        scored_predictions=scored_predictions,
        materialized_predictions=materialized_predictions,
    )
    baseline_producer = manifest.baseline_producer or _first_control_like_producer(manifest)
    control_predictions = control_predictions_from_rows(
        gold_letters,
        source_rows[baseline_producer],
    )
    changed = {
        "versus_v042_default_quarantine": changed_row_accounting(
            rows,
            baseline=control_predictions,
            candidate=scored_predictions,
        )
    }
    if comparator_rows is not None:
        focused_comparator_predictions = comparator_predictions_from_rows(
            gold_letters,
            comparator_rows,
        )
        changed["versus_existing_focused_route_comparator"] = changed_row_accounting(
            rows,
            baseline=focused_comparator_predictions,
            candidate=scored_predictions,
        )

    report = _build_report(
        manifest=manifest,
        rows=rows,
        gold_letters=gold_letters,
        source_rows=source_rows,
        generated_on=generated_on,
        score_ladder=score_ladder,
        target_report=target_report,
        changed=changed,
    )
    report["diagnosis_resolution_candidate"] = diagnosis_resolution_candidate
    report["model_preserving_policy_candidate"] = model_preserving_policy_candidate
    report["prescription_rescue_scope_candidate"] = prescription_rescue_scope_candidate
    report["prescription_policy_variant"] = prescription_policy_variant
    report["diagnosis_policy_variant"] = diagnosis_policy_variant
    return AssemblyRun(
        manifest=manifest,
        rows=rows,
        report=report,
        stores=stores,
        views=views,
    )


def render_finding_assembly_markdown(
    report: Mapping[str, Any],
    *,
    json_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> str:
    """Render the finding/lens/view replay report."""

    gate = report["gate_decision"]
    title = report.get("report_title", "ExECTv2 Clinical Finding Assembly Replay")
    lines = [
        f"# {title}",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- Split/stage: `{report['split']}` / `{report['stage']}`",
        f"- Candidate: `{report['candidate_name']}`",
        f"- Gate decision: **{gate['decision']}**",
        f"- Claim boundary: {report['claim_boundary']}",
    ]
    if json_path is not None:
        lines.append(f"- JSON: `{json_path.as_posix()}`")
    if jsonl_path is not None:
        lines.append(f"- JSONL: `{jsonl_path.as_posix()}`")
    lines += [
        "",
        "## Finding Assembly",
        "",
        (
            "This replay builds a per-letter clinical finding store, applies "
            "entity-specific lenses, and renders scoring views from the same "
            "final findings. It is a structural replay over frozen artifacts; "
            "it introduces no live model calls."
        ),
        "",
        "| Entity | Producer | Lens | Ownership |",
        "| --- | --- | --- | --- |",
    ]
    for indicator in TARGET_INDICATORS:
        lane = report["lane_sources"][indicator]
        lines.append(
            f"| {indicator} | `{lane['artifact']}` | `{lane['lens']}` | "
            f"`{lane['ownership_label']}` |"
        )

    lines += [
        "",
        "## Score Views",
        "",
        (
            "| View | Legacy surface | Overall F1 | Diagnosis | SeizureFrequency "
            "| Prescription | Investigations |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    view_to_surface = {
        "raw_candidate": "raw_lane_score",
        "post_lens": "post_lens_score",
        "benchmark_cui": "cui_projection_companion",
        "clinical_headline": "headline_target",
    }
    for view_id, surface in view_to_surface.items():
        scores = report["score_ladder"][surface]
        by_indicator = scores["by_indicator"]
        lines.append(
            f"| {view_id} | `{surface}` | {scores['overall']['f1']:.4f} | "
            f"{by_indicator[DIAGNOSIS.name]['f1']:.4f} | "
            f"{by_indicator[SEIZURE_FREQUENCY.name]['f1']:.4f} | "
            f"{by_indicator[PRESCRIPTION.name]['f1']:.4f} | "
            f"{by_indicator[INVESTIGATIONS.name]['f1']:.4f} |"
        )

    materialized = report["score_ladder"].get("materialized_surfaces", {})
    if materialized:
        lines += [
            "",
            "## Materialized Intermediate Surfaces",
            "",
            (
                "| Surface | Overall F1 | Diagnosis | SeizureFrequency "
                "| Prescription | Investigations |"
            ),
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for surface in MATERIALIZED_SURFACES:
            scores = materialized[surface]
            by_indicator = scores["by_indicator"]
            lines.append(
                f"| `{surface}` | {scores['overall']['f1']:.4f} | "
                f"{by_indicator[DIAGNOSIS.name]['f1']:.4f} | "
                f"{by_indicator[SEIZURE_FREQUENCY.name]['f1']:.4f} | "
                f"{by_indicator[PRESCRIPTION.name]['f1']:.4f} | "
                f"{by_indicator[INVESTIGATIONS.name]['f1']:.4f} |"
            )

    origin_counts = report.get("fact_origin_accounting", {}).get("by_surface", {})
    if origin_counts:
        all_origins = sorted(
            {origin for counts in origin_counts.values() for origin in counts if origin}
        )
        lines += [
            "",
            "## Fact-Origin Accounting",
            "",
            "| Surface | " + " | ".join(all_origins) + " |",
            "| --- | " + " | ".join("---:" for _ in all_origins) + " |",
        ]
        for surface in MATERIALIZED_SURFACES:
            counts = origin_counts.get(surface, {})
            lines.append(
                f"| `{surface}` | "
                + " | ".join(str(counts.get(origin, 0)) for origin in all_origins)
                + " |"
            )

    benchmark = report["score_ladder"]["benchmark"]
    companions = report["score_ladder"]["fidelity_companions"]
    lines += [
        "",
        "## Benchmark And Fidelity Views",
        "",
        "| Surface | Value |",
        "| --- | ---: |",
        f"| Benchmark raw | {benchmark['raw']:.4f} |",
        f"| Benchmark after CUI/projection | {benchmark['after_cui_projection']:.4f} |",
        (
            f"| Diagnosis.concept_negation | "
            f"{companions[DIAGNOSIS.name]['concept_negation']['f1']:.4f} |"
        ),
        (
            f"| SeizureFrequency.active_rate_fidelity | "
            f"{companions[SEIZURE_FREQUENCY.name]['active_rate_fidelity']['f1']:.4f} |"
        ),
        "",
        "## Gate Summary",
        "",
        "| Gate | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in gate["checks"]:
        status = "pass" if check["passed"] else "fail"
        lines.append(f"| {check['name']} | {status} | {check['detail']} |")

    lines += [
        "",
        "## Lens Diagnostics",
        "",
        (
            "| Entity | Call failures | Parse/schema failures | Evidence-invalid dropped "
            "| Exact evidence rate |"
        ),
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for lane, stats in report["lane_diagnostics"].items():
        lines.append(
            f"| {lane} | {stats['call_failures']} | {stats['parse_schema_failures']} | "
            f"{stats['evidence_invalid_dropped']} | {stats['exact_evidence_rate']:.4f} |"
        )

    lines += [
        "",
        "## Changed Rows",
        "",
        "| Comparison | Indicator | Changed rows | Categories |",
        "| --- | --- | ---: | --- |",
    ]
    for comparison, payload in report["changed_row_accounting"].items():
        for indicator, summary in payload["by_indicator"].items():
            categories = (
                ", ".join(f"{name}={count}" for name, count in summary["categories"].items())
                or "none"
            )
            lines.append(
                f"| {comparison} | {indicator} | {summary['changed_rows']} | {categories} |"
            )
    lines += [
        "",
        "Every row-level mention carries source artifact, source lane, ownership, "
        "producer provenance, lens provenance, evidence-valid status, and the "
        "rendered scoring view can be reconstructed from the JSONL.",
        "",
    ]
    return "\n".join(lines)


def _assemble_letter(
    letter: ExectLetter,
    *,
    manifest: FindingAssemblyManifest,
    producers: Mapping[str, SavedJsonlProducer],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    diagnosis_resolution_candidate: bool,
    model_preserving_policy_candidate: bool,
    prescription_rescue_scope_candidate: bool,
    prescription_policy_variant: str,
    diagnosis_policy_variant: str,
) -> tuple[ClinicalFindingStore, dict[str, Any]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )

    from ..orchestration import letter_assembly

    config = StructuredMethodConfig(
        diagnosis_policy_variant=diagnosis_policy_variant,
        prescription_policy_variant=prescription_policy_variant,
        archived_replay=(
            diagnosis_policy_variant == "combined"
            or prescription_policy_variant == "combined"
            or diagnosis_resolution_candidate
            or model_preserving_policy_candidate
            or prescription_rescue_scope_candidate
        ),
        diagnosis_resolution_candidate=diagnosis_resolution_candidate,
        model_preserving_policy_candidate=model_preserving_policy_candidate,
        prescription_rescue_scope_candidate=prescription_rescue_scope_candidate,
    )
    return letter_assembly.assemble_letter(
        letter,
        manifest=manifest,
        producers=producers,
        source_rows=source_rows,
        config=config,
    )

    # Legacy implementation retained below as a rollback reference. Active
    # replay callers delegate above; it can be removed after parity evidence is
    # accepted in the follow-up cleanup change.
    store = ClinicalFindingStore(letter.letter_id, letter.note_text)
    lane_blocks: dict[str, Any] = {}
    predicted_mentions: list[dict[str, Any]] = []
    raw_mentions: list[dict[str, Any]] = []
    prediction_surfaces: dict[str, list[dict[str, Any]]] = {
        surface_key: [] for surface_key in MATERIALIZED_SURFACES
    }

    for indicator in TARGET_INDICATORS:
        lens_config = manifest.lenses[indicator]
        producer = producers[lens_config.producer]
        row = source_rows[lens_config.producer][letter.letter_id]
        source = producer.source_for_row(
            row,
            source_lane=lens_config.source_lane or producer.source_lane,
        )
        store.register_source(source)
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=indicator,
                note_text=letter.note_text,
                source=source,
                raw_surface=True,
            )
        )
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=indicator,
                note_text=letter.note_text,
                source=source,
                raw_surface=False,
            )
        )

    for indicator in TARGET_INDICATORS:
        lens_config = manifest.lenses[indicator]
        producer = producers[lens_config.producer]
        row = source_rows[lens_config.producer][letter.letter_id]
        lens = lens_from_manifest(lens_config)
        source_lane = lens_config.source_lane or producer.source_lane or lens_config.producer
        lens_result = lens.reconcile(
            store,
            policy=LensPolicy(
                producer_id=lens_config.producer,
                source_lane=source_lane,
                ownership_label=lens_config.ownership_label or producer.ownership_label,
                portability=lens_config.portability,
                diagnosis_resolution_candidate=diagnosis_resolution_candidate,
                model_preserving_policy_candidate=model_preserving_policy_candidate,
                prescription_rescue_scope_candidate=(
                    prescription_rescue_scope_candidate
                ),
                prescription_policy_variant=prescription_policy_variant,
                diagnosis_policy_variant=diagnosis_policy_variant,
            ),
        )
        lane_scored = [finding.to_row() for finding in lens_result.findings]
        lane_surfaces = _lane_prediction_surfaces(
            store,
            entity=indicator,
            producer_id=lens_config.producer,
            final_findings=lens_result.findings,
        )
        lane_surface_rows = {
            surface_key: [finding.to_row() for finding in findings]
            for surface_key, findings in lane_surfaces.items()
        }
        lane_raw_findings = list(
            store.findings(
                entity=indicator,
                producer_id=lens_config.producer,
                raw_surface=True,
            )
        )
        if not lane_raw_findings:
            lane_raw_findings = list(
                findings_from_row(
                    row,
                    letter_id=letter.letter_id,
                    entity=indicator,
                    note_text=letter.note_text,
                    source=source,
                    raw_surface=True,
                    predicted_fallback=True,
                )
            )
        lane_raw = [finding.to_row() for finding in lane_raw_findings]
        predicted_mentions.extend(lane_scored)
        raw_mentions.extend(lane_raw)
        for surface_key, surface_rows in lane_surface_rows.items():
            prediction_surfaces[surface_key].extend(surface_rows)
        lane_blocks[indicator] = {
            "source_artifact": producer.artifact_path.as_posix(),
            "source_lane": source_lane,
            "lens": lens_config.lens,
            "ownership_label": lens_config.ownership_label or producer.ownership_label,
            "source_pipeline_family": row.get("pipeline_family", ""),
            "prompt_version": row.get("prompt_version", ""),
            "model": row.get("model", ""),
            "mode": row.get("mode", ""),
            "status": status_from_row(row),
            "diagnostics": lane_diagnostics_from_row(row),
            "lens_diagnostics": lens_result.diagnostics,
            "predicted_mentions": lane_scored,
            "raw_lane_mentions": lane_raw,
            "prediction_surfaces": lane_surface_rows,
        }
    return store, {
        "letter_id": letter.letter_id,
        "split": manifest.split,
        "stage": manifest.stage,
        "pipeline_family": manifest.pipeline_family,
        "candidate_name": manifest.candidate_id,
        "ownership": manifest.ownership,
        "gold_mentions": [
            _gold_to_row(annotation)
            for annotation in letter.annotations
            if annotation.entity in TARGET_INDICATORS
        ],
        "predicted_mentions": predicted_mentions,
        "raw_lane_mentions": raw_mentions,
        "prediction_surfaces": prediction_surfaces,
        "lanes": lane_blocks,
    }


def _lane_prediction_surfaces(
    store: ClinicalFindingStore,
    *,
    entity: str,
    producer_id: str,
    final_findings: Sequence[Any],
) -> dict[str, list[Any]]:
    source_scored = list(store.findings(entity=entity, producer_id=producer_id, raw_surface=False))
    evidence_valid = [finding for finding in source_scored if finding.evidence_valid]
    protocol_model_preserving_canonical = [
        finding
        for finding in source_scored
        if finding.source.fact_origin == "target_model_generated"
    ]
    final = list(final_findings)
    dictionary_normalized = [
        finding for finding in final if not _is_deterministic_addition(finding)
    ]
    # `residual_benchmark_added` is the full assembled set after residual recovery —
    # i.e. the pipeline's final surface. We deliberately do not emit a separate
    # "final" surface: it was a literal alias of this one and only created a
    # confusing always-zero "final assembly" delta downstream.
    residual_benchmark_added = list(final)
    return {
        "source_scored": source_scored,
        "evidence_valid": evidence_valid,
        "format_only": list(source_scored),
        "protocol_model_preserving_canonical": protocol_model_preserving_canonical,
        "dictionary_normalized": dictionary_normalized,
        "residual_benchmark_added": residual_benchmark_added,
    }


def _is_deterministic_addition(finding: Any) -> bool:
    return any(event.action.startswith("added_") for event in finding.provenance)


def _build_report(
    *,
    manifest: FindingAssemblyManifest,
    rows: Sequence[dict[str, Any]],
    gold_letters: Sequence[ExectLetter],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    generated_on: str,
    score_ladder: Mapping[str, Any],
    target_report: Mapping[str, Any],
    changed: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "pipeline_family": manifest.pipeline_family,
        "candidate_name": manifest.candidate_id,
        "report_title": _report_title(manifest),
        "generated_on": generated_on,
        "split": manifest.split,
        "stage": manifest.stage,
        "row_count": len(rows),
        "input_artifacts": {
            producer_id: producer.artifact.as_posix()
            for producer_id, producer in manifest.producers.items()
        }
        | {
            "focused_comparator": (
                manifest.focused_comparator_artifact.as_posix()
                if manifest.focused_comparator_artifact is not None
                else ""
            )
        },
        "lane_sources": _lane_sources(manifest),
        "score_ladder": dict(score_ladder),
        "target_report": dict(target_report),
        "lane_diagnostics": _lane_diagnostics(rows, gold_letters),
        "fact_origin_accounting": _fact_origin_accounting(rows),
        "changed_row_accounting": dict(changed),
        "gate_decision": _gate_decision(
            score_ladder,
            changed,
            promotion_decision=manifest.promotion_decision,
        ),
        "finding_views": list(manifest.views),
        "claim_boundary": (
            "Dev-only component-attributed architecture evidence. This artifact "
            "does not authorize a benchmark claim, full-200 audit, or locked-test "
            "analysis."
            if manifest.claim_boundary == "dev_only_component_evidence"
            else manifest.claim_boundary
        ),
        "structural_replay": {
            "producer_count": len(manifest.producers),
            "lens_count": len(manifest.lenses),
            "source_row_counts": {
                producer_id: len(rows_by_id) for producer_id, rows_by_id in source_rows.items()
            },
        },
    }


def _gate_decision(
    score_ladder: Mapping[str, Any],
    changed: Mapping[str, Any],
    *,
    promotion_decision: str,
) -> dict[str, Any]:
    headline = score_ladder["headline_target"]["by_indicator"]
    companions = score_ladder["fidelity_companions"]
    p_delta = headline[PRESCRIPTION.name]["f1"] - BASELINE_HEADLINES[PRESCRIPTION.name]
    i_delta = headline[INVESTIGATIONS.name]["f1"] - BASELINE_HEADLINES[INVESTIGATIONS.name]
    dx_f1 = headline[DIAGNOSIS.name]["f1"]
    sf_f1 = headline[SEIZURE_FREQUENCY.name]["f1"]
    dx_fid = companions[DIAGNOSIS.name]["concept_negation"]["f1"]
    sf_fid = companions[SEIZURE_FREQUENCY.name]["active_rate_fidelity"]["f1"]
    checks = [
        {
            "name": "Prescription control regression",
            "passed": p_delta >= -0.01,
            "detail": f"delta vs v0.42 control {p_delta:+.4f}; floor -0.0100",
        },
        {
            "name": "Investigations control regression",
            "passed": i_delta >= -0.01,
            "detail": f"delta vs v0.42 control {i_delta:+.4f}; floor -0.0100",
        },
        {
            "name": "Diagnosis headline",
            "passed": dx_f1 > BASELINE_HEADLINES[DIAGNOSIS.name]
            and dx_f1 >= FOCUSED_ROUTE_HEADLINES[DIAGNOSIS.name],
            "detail": (
                f"{dx_f1:.4f}; must beat {BASELINE_HEADLINES[DIAGNOSIS.name]:.4f} "
                f"and tie/beat {FOCUSED_ROUTE_HEADLINES[DIAGNOSIS.name]:.4f}"
            ),
        },
        {
            "name": "Diagnosis concept_negation",
            "passed": dx_fid >= BASELINE_DX_CONCEPT_NEGATION,
            "detail": f"{dx_fid:.4f}; baseline {BASELINE_DX_CONCEPT_NEGATION:.4f}",
        },
        {
            "name": "SeizureFrequency headline",
            "passed": sf_f1 > BASELINE_HEADLINES[SEIZURE_FREQUENCY.name]
            and sf_f1 >= FOCUSED_ROUTE_HEADLINES[SEIZURE_FREQUENCY.name],
            "detail": (
                f"{sf_f1:.4f}; must beat {BASELINE_HEADLINES[SEIZURE_FREQUENCY.name]:.4f} "
                f"and tie/beat {FOCUSED_ROUTE_HEADLINES[SEIZURE_FREQUENCY.name]:.4f}"
            ),
        },
        {
            "name": "SeizureFrequency active_rate_fidelity",
            "passed": sf_fid >= BASELINE_SF_ACTIVE_RATE_FIDELITY,
            "detail": f"{sf_fid:.4f}; baseline {BASELINE_SF_ACTIVE_RATE_FIDELITY:.4f}",
        },
    ]
    pi_changes = changed["versus_v042_default_quarantine"]["by_indicator"]
    checks.extend(
        [
            {
                "name": "Prescription changed-row control",
                "passed": pi_changes[PRESCRIPTION.name]["changed_rows"] == 0,
                "detail": f"{pi_changes[PRESCRIPTION.name]['changed_rows']} changed rows",
            },
            {
                "name": "Investigations changed-row control",
                "passed": pi_changes[INVESTIGATIONS.name]["changed_rows"] == 0,
                "detail": f"{pi_changes[INVESTIGATIONS.name]['changed_rows']} changed rows",
            },
        ]
    )
    passed = all(check["passed"] for check in checks)
    return {
        "decision": promotion_decision if passed else "do-not-promote",
        "checks": checks,
    }


def _lane_diagnostics(
    rows: Sequence[Mapping[str, Any]],
    gold_letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    note_by_id = {letter.letter_id: letter.note_text for letter in gold_letters}
    out: dict[str, Any] = {}
    for indicator in TARGET_INDICATORS:
        calls = parses = evidence_invalid = raw = scored = exact = 0
        for row in rows:
            lane = row["lanes"][indicator]
            status = lane["status"]
            calls += int(bool(status["call_error"]))
            parses += int(_has_blocking_parse_issue(status["parse_errors"]))
            evidence_invalid += _evidence_invalid_for_lane(lane, indicator)
            raw += len(lane["raw_lane_mentions"])
            scored += len(lane["predicted_mentions"])
            exact += sum(
                _evidence_exact(
                    mention.get("evidence", ""),
                    note_by_id[str(row["letter_id"])],
                )
                for mention in lane["predicted_mentions"]
            )
        out[indicator] = {
            "call_failures": calls,
            "parse_schema_failures": parses,
            "evidence_invalid_dropped": evidence_invalid,
            "raw_mentions": raw,
            "scored_mentions": scored,
            "exact_evidence_mentions": exact,
            "exact_evidence_rate": round(exact / scored, 4) if scored else 1.0,
        }
    return out


def _fact_origin_accounting(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_surface: dict[str, Counter[str]] = {surface: Counter() for surface in MATERIALIZED_SURFACES}
    by_lane: dict[str, dict[str, Counter[str]]] = {}
    for row in rows:
        for indicator, lane in row.get("lanes", {}).items():
            lane_counters = by_lane.setdefault(
                str(indicator),
                {surface: Counter() for surface in MATERIALIZED_SURFACES},
            )
            for surface, mentions in lane.get("prediction_surfaces", {}).items():
                if surface not in by_surface:
                    continue
                for mention in mentions:
                    origin = str(mention.get("fact_origin", "unknown"))
                    by_surface[surface][origin] += 1
                    lane_counters[surface][origin] += 1
    return {
        "by_surface": {
            surface: dict(sorted(counter.items())) for surface, counter in by_surface.items()
        },
        "by_lane": {
            lane: {
                surface: dict(sorted(counter.items()))
                for surface, counter in surface_counts.items()
            }
            for lane, surface_counts in by_lane.items()
        },
    }


def _evidence_invalid_for_lane(lane: Mapping[str, Any], indicator: str) -> int:
    diagnostics = lane.get("diagnostics", {})
    warnings = [str(w) for w in diagnostics.get("gate_warnings", [])]
    prefixed = [
        warning
        for warning in warnings
        if warning.startswith(f"{indicator}: ") and "dropped_evidence_not_substring" in warning
    ]
    if prefixed:
        return len(prefixed)
    source_family = str(lane.get("source_pipeline_family", ""))
    if source_family in {
        "exectv2_hybrid_diagnosis_reconciler",
        "exectv2_hybrid_sf_unknown_suppression",
    }:
        return int(diagnostics.get("n_evidence_invalid", 0) or 0)
    return 0


def _validate_source_rows(
    gold_letters: Sequence[ExectLetter],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    producers: Mapping[str, SavedJsonlProducer],
) -> None:
    expected = {letter.letter_id for letter in gold_letters}
    for producer_id, rows in source_rows.items():
        observed = set(rows)
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        if missing or extra:
            raise ValueError(
                f"{producers[producer_id].artifact_path.as_posix()} does not match "
                f"frozen row set: missing={missing[:5]} extra={extra[:5]}"
            )


def _validate_replay_rows(
    rows: Sequence[Mapping[str, Any]],
    gold_letters: Sequence[ExectLetter],
) -> None:
    notes = {letter.letter_id: letter.note_text for letter in gold_letters}
    invalid: list[str] = []
    for row in rows:
        note = notes[str(row["letter_id"])]
        for mention in row["predicted_mentions"]:
            evidence = str(mention.get("evidence", ""))
            if not evidence or evidence not in note:
                invalid.append(f"{row['letter_id']}:{mention.get('entity')}:{evidence[:40]}")
    if invalid:
        raise ValueError(
            "finding assembly has scored mentions without exact source evidence: "
            + ", ".join(invalid[:10])
        )


def _rows_by_id(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["letter_id"])] = row
    return rows


def _lane_sources(manifest: FindingAssemblyManifest) -> dict[str, dict[str, str]]:
    out = {}
    for indicator in TARGET_INDICATORS:
        lens = manifest.lenses[indicator]
        producer = manifest.producers[lens.producer]
        out[indicator] = {
            "artifact": producer.artifact.as_posix(),
            "source_lane": lens.source_lane or producer.source_lane or lens.producer,
            "lens": lens.lens,
            "ownership_label": lens.ownership_label or producer.ownership_label,
        }
    return out


def _first_control_like_producer(manifest: FindingAssemblyManifest) -> str:
    for producer_id in manifest.producers:
        if "control" in producer_id or "v042" in producer_id:
            return producer_id
    return next(iter(manifest.producers))


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in (errors or [])
    )


def _evidence_exact(evidence: str, note_text: str) -> bool:
    return bool(evidence) and evidence in note_text


def _gold_to_row(annotation: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "attributes": dict(annotation.attributes),
    }


def _report_title(manifest: FindingAssemblyManifest) -> str:
    if "holistic" in manifest.candidate_id:
        return "ExECTv2 Holistic Finding Assembly Replay"
    return "ExECTv2 Focused-Lane Component-Evidence Replay"
