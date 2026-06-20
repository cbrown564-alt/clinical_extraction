"""No-call focused-lane component-evidence replay for ExECTv2 Plan 11."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
    build_target_indicator_report,
)

PIPELINE_FAMILY = "exectv2_focused_lane_component_evidence"
CANDIDATE_NAME = "focused_lane_component_evidence_v01_dev140"
OWNERSHIP = "component_attributed_focused_lane_replay"
DEFAULT_CONTROL_ARTIFACT = Path(
    "experiments/"
    "exectv2_target_indicators_single_call_v042_live_default_quarantine_"
    "dev140_qwen36_35b_ollama_autogpu_ctx16384_20260620.jsonl"
)
DEFAULT_DIAGNOSIS_ARTIFACT = Path(
    "experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_SF_ARTIFACT = Path(
    "experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl"
)
DEFAULT_FOCUSED_COMPARATOR_ARTIFACT = Path(
    "experiments/"
    "exectv2_family_routed_with_focused_diagnosis_route_dev140_gpt41mini_20260618.jsonl"
)
DEFAULT_OUT_JSONL = Path(
    "experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.jsonl"
)
DEFAULT_OUT_JSON = Path(
    "experiments/exectv2_focused_lane_component_evidence_v01_dev140_20260620.json"
)
DEFAULT_OUT_MD = Path(
    "docs/experiments/exectv2/key_entities/"
    "exectv2_focused_lane_component_evidence_v01_dev140_20260620.md"
)
LANES: dict[str, dict[str, Any]] = {
    PRESCRIPTION.name: {
        "source_key": "control",
        "source_lane": "v0.42_control",
        "ownership": "llm_first_control",
    },
    INVESTIGATIONS.name: {
        "source_key": "control",
        "source_lane": "v0.42_control",
        "ownership": "llm_first_control",
    },
    DIAGNOSIS.name: {
        "source_key": "diagnosis",
        "source_lane": "focused_diagnosis_reconciler_v01",
        "ownership": "hybrid_diagnosis_route",
    },
    SEIZURE_FREQUENCY.name: {
        "source_key": "sf",
        "source_lane": "focused_sf_unknown_suppression_v07",
        "ownership": "hybrid_sf_route",
    },
}
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
BASELINE_SF_ACTIVE_RATE_FIDELITY = 0.2887


def build_focused_lane_replay(
    *,
    split: str = "dev",
    row_count: int = 140,
    control_artifact: Path = DEFAULT_CONTROL_ARTIFACT,
    diagnosis_artifact: Path = DEFAULT_DIAGNOSIS_ARTIFACT,
    sf_artifact: Path = DEFAULT_SF_ARTIFACT,
    focused_comparator_artifact: Path | None = DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    generated_on: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the frozen component replay rows and summary report without calls."""

    generated_on = generated_on or date.today().isoformat()
    gold_letters = load_letters_for_split(split)[:row_count]
    sources = {
        "control": _source(control_artifact, "v0.42 default-quarantine local-Qwen"),
        "diagnosis": _source(diagnosis_artifact, "focused Diagnosis reconciler v0.1"),
        "sf": _source(sf_artifact, "focused SF unknown suppression v0.7"),
    }
    source_rows = {key: _rows_by_id(src["path"]) for key, src in sources.items()}
    _validate_source_rows(gold_letters, source_rows, sources)

    comparator_rows = (
        _rows_by_id(focused_comparator_artifact)
        if focused_comparator_artifact is not None and focused_comparator_artifact.exists()
        else None
    )
    rows = [
        _build_replay_row(letter, source_rows, sources, split=split)
        for letter in gold_letters
    ]
    _validate_replay_rows(rows, gold_letters)

    raw_predictions = _predictions_from_rows(rows, "raw_lane_mentions")
    scored_predictions = _predictions_from_rows(rows, "predicted_mentions")
    control_predictions = _control_predictions(gold_letters, source_rows["control"])
    focused_comparator_predictions = (
        _comparator_predictions(gold_letters, comparator_rows)
        if comparator_rows is not None
        else None
    )
    report = _build_report(
        rows=rows,
        gold_letters=gold_letters,
        raw_predictions=raw_predictions,
        scored_predictions=scored_predictions,
        control_predictions=control_predictions,
        focused_comparator_predictions=focused_comparator_predictions,
        sources=sources,
        generated_on=generated_on,
        split=split,
        focused_comparator_artifact=focused_comparator_artifact,
    )
    return rows, report


def write_focused_lane_outputs(
    *,
    out_jsonl: Path = DEFAULT_OUT_JSONL,
    out_json: Path = DEFAULT_OUT_JSON,
    out_md: Path = DEFAULT_OUT_MD,
    split: str = "dev",
    row_count: int = 140,
    control_artifact: Path = DEFAULT_CONTROL_ARTIFACT,
    diagnosis_artifact: Path = DEFAULT_DIAGNOSIS_ARTIFACT,
    sf_artifact: Path = DEFAULT_SF_ARTIFACT,
    focused_comparator_artifact: Path | None = DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
) -> dict[str, Path]:
    """Write the JSONL, JSON, and markdown focused-lane replay artifacts."""

    rows, report = build_focused_lane_replay(
        split=split,
        row_count=row_count,
        control_artifact=control_artifact,
        diagnosis_artifact=diagnosis_artifact,
        sf_artifact=sf_artifact,
        focused_comparator_artifact=focused_comparator_artifact,
    )
    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_jsonl.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    out_md.write_text(
        render_focused_lane_markdown(report, json_path=out_json, jsonl_path=out_jsonl),
        encoding="utf-8",
    )
    return {"jsonl": out_jsonl, "json": out_json, "md": out_md}


def render_focused_lane_markdown(
    report: Mapping[str, Any],
    *,
    json_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> str:
    """Render the predeclared score ladder and gate readout."""

    gate = report["gate_decision"]
    lines = [
        "# ExECTv2 Focused-Lane Component-Evidence Replay",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- Split/stage: `{report['split']}` / `dev{report['row_count']}`",
        f"- Candidate: `{report['candidate_name']}`",
        f"- Gate decision: **{gate['decision']}**",
        "- Claim boundary: dev-only architecture evidence; no full-200, test, or benchmark claim.",
    ]
    if json_path is not None:
        lines.append(f"- JSON: `{json_path.as_posix()}`")
    if jsonl_path is not None:
        lines.append(f"- JSONL: `{jsonl_path.as_posix()}`")
    lines += [
        "",
        "## Frozen Sources",
        "",
        "| Lane | Source | Ownership |",
        "| --- | --- | --- |",
    ]
    for indicator in TARGET_INDICATORS:
        lane = report["lane_sources"][indicator]
        lines.append(
            f"| {indicator} | `{lane['artifact']}` | `{lane['ownership_label']}` |"
        )

    lines += [
        "",
        "## Score Ladder",
        "",
        "| Surface | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for surface in (
        "raw_lane_score",
        "evidence_valid_score",
        "cui_projection_companion",
        "headline_target",
    ):
        scores = report["score_ladder"][surface]
        by_indicator = scores["by_indicator"]
        lines.append(
            f"| {surface} | {scores['overall']['f1']:.4f} | "
            f"{by_indicator[DIAGNOSIS.name]['f1']:.4f} | "
            f"{by_indicator[SEIZURE_FREQUENCY.name]['f1']:.4f} | "
            f"{by_indicator[PRESCRIPTION.name]['f1']:.4f} | "
            f"{by_indicator[INVESTIGATIONS.name]['f1']:.4f} |"
        )

    benchmark = report["score_ladder"]["benchmark"]
    companions = report["score_ladder"]["fidelity_companions"]
    lines += [
        "",
        "## Benchmark And Fidelity",
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
        "## Lane Diagnostics",
        "",
        "| Lane | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |",
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
            categories = ", ".join(
                f"{name}={count}" for name, count in summary["categories"].items()
            ) or "none"
            lines.append(
                f"| {comparison} | {indicator} | {summary['changed_rows']} | {categories} |"
            )
    lines += [
        "",
        "The row-level JSONL carries per-mention source artifact, source lane, "
        "ownership, and deterministic projection/suppression provenance.",
        "",
    ]
    return "\n".join(lines)


def _build_replay_row(
    letter: ExectLetter,
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    sources: Mapping[str, Mapping[str, Any]],
    *,
    split: str,
) -> dict[str, Any]:
    lane_blocks: dict[str, Any] = {}
    predicted_mentions: list[dict[str, Any]] = []
    raw_mentions: list[dict[str, Any]] = []
    for indicator in TARGET_INDICATORS:
        lane = LANES[indicator]
        source_key = str(lane["source_key"])
        row = source_rows[source_key][letter.letter_id]
        lane_scored = [
            _enhance_mention(m, row, sources[source_key], indicator=indicator, raw=False)
            for m in row.get("predicted_mentions", [])
            if str(m.get("entity")) == indicator
        ]
        lane_raw = [
            _enhance_mention(m, row, sources[source_key], indicator=indicator, raw=True)
            for m in _raw_mentions(row, default_entity=indicator)
            if str(m.get("entity", indicator)) == indicator
        ]
        predicted_mentions.extend(lane_scored)
        raw_mentions.extend(lane_raw)
        lane_blocks[indicator] = {
            "source_artifact": sources[source_key]["artifact"],
            "source_lane": lane["source_lane"],
            "ownership_label": lane["ownership"],
            "source_pipeline_family": row.get("pipeline_family", ""),
            "prompt_version": row.get("prompt_version", ""),
            "model": row.get("model", ""),
            "mode": row.get("mode", ""),
            "status": _status_from_row(row),
            "diagnostics": _lane_diagnostics_from_row(row),
            "predicted_mentions": lane_scored,
            "raw_lane_mentions": lane_raw,
        }
    return {
        "letter_id": letter.letter_id,
        "split": split,
        "stage": f"dev{len(source_rows['control'])}",
        "pipeline_family": PIPELINE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "ownership": OWNERSHIP,
        "gold_mentions": [
            _gold_to_row(annotation)
            for annotation in letter.annotations
            if annotation.entity in TARGET_INDICATORS
        ],
        "predicted_mentions": predicted_mentions,
        "raw_lane_mentions": raw_mentions,
        "lanes": lane_blocks,
    }


def _build_report(
    *,
    rows: Sequence[dict[str, Any]],
    gold_letters: Sequence[ExectLetter],
    raw_predictions: Sequence[PredictedLetter],
    scored_predictions: Sequence[PredictedLetter],
    control_predictions: Sequence[PredictedLetter],
    focused_comparator_predictions: Sequence[PredictedLetter] | None,
    sources: Mapping[str, Mapping[str, Any]],
    generated_on: str,
    split: str,
    focused_comparator_artifact: Path | None,
) -> dict[str, Any]:
    raw_arch = architecture_report(
        name=f"{CANDIDATE_NAME}_raw",
        ownership=OWNERSHIP,
        gold_letters=gold_letters,
        pred_letters=raw_predictions,
        entities=TARGET_INDICATORS,
    )
    scored_arch = architecture_report(
        name=CANDIDATE_NAME,
        ownership=OWNERSHIP,
        gold_letters=gold_letters,
        pred_letters=scored_predictions,
        entities=TARGET_INDICATORS,
    )
    projected = [project_cuis(letter) for letter in scored_predictions]
    projected_arch = architecture_report(
        name=f"{CANDIDATE_NAME}_cui_projected",
        ownership=OWNERSHIP,
        gold_letters=gold_letters,
        pred_letters=projected,
        entities=TARGET_INDICATORS,
    )
    headline_report = _target_report(scored_arch, projected=True)
    changed = {
        "versus_v042_default_quarantine": _changed_row_accounting(
            rows,
            baseline=control_predictions,
            candidate=scored_predictions,
        )
    }
    if focused_comparator_predictions is not None:
        changed["versus_existing_focused_route_comparator"] = _changed_row_accounting(
            rows,
            baseline=focused_comparator_predictions,
            candidate=scored_predictions,
        )

    score_ladder = {
        "raw_lane_score": _target_surface(raw_arch, projected=False),
        "evidence_valid_score": _target_surface(scored_arch, projected=False),
        "cui_projection_companion": _target_surface(projected_arch, projected=False),
        "headline_target": _target_surface(scored_arch, projected=True),
        "benchmark": {
            "raw": scored_arch["cui_audit"]["overall"]["benchmark_f1_raw_llm"],
            "after_cui_projection": scored_arch["cui_audit"]["overall"][
                "benchmark_f1_after_cui_projection"
            ],
            "by_indicator_raw": {
                entity: scored_arch["cui_audit"]["per_entity"][entity]["benchmark_f1"]
                for entity in TARGET_INDICATORS
            },
        },
        "fidelity_companions": _fidelity_companions(scored_arch),
    }
    return {
        "pipeline_family": PIPELINE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "generated_on": generated_on,
        "split": split,
        "row_count": len(rows),
        "input_artifacts": {
            key: value["artifact"]
            for key, value in sources.items()
        }
        | {
            "focused_comparator": (
                focused_comparator_artifact.as_posix()
                if focused_comparator_artifact is not None
                else ""
            )
        },
        "lane_sources": _lane_sources(sources),
        "score_ladder": score_ladder,
        "target_report": headline_report,
        "lane_diagnostics": _lane_diagnostics(rows, gold_letters),
        "changed_row_accounting": changed,
        "gate_decision": _gate_decision(score_ladder, changed),
        "claim_boundary": (
            "Dev-only component-attributed architecture evidence. This artifact "
            "does not authorize a benchmark claim, full-200 audit, or locked-test "
            "analysis."
        ),
    }


def _gate_decision(
    score_ladder: Mapping[str, Any],
    changed: Mapping[str, Any],
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
        "decision": "promote-dev-focused-lane-architecture" if passed else "do-not-promote",
        "checks": checks,
    }


def _target_report(arch: Mapping[str, Any], *, projected: bool) -> dict[str, Any]:
    scores_key = "cui_projected_headline_scores" if projected else "headline_scores"
    recovery = arch["clinical_recovery"]
    source = {
        "pipeline_family": PIPELINE_FAMILY,
        "split": "",
        "stage": f"dev{arch['row_count']}",
        "row_count": arch["row_count"],
        "candidates": [
            {
                "name": arch["name"],
                "ownership": arch["ownership"],
                "routed_primary_recovery": {
                    "overall": recovery[
                        "cui_projected_overall" if projected else "overall"
                    ],
                    "headline_scores": {
                        indicator: recovery[scores_key][indicator]
                        for indicator in TARGET_INDICATORS
                    },
                },
                "routed_primary_errors": {
                    "per_entity": arch.get("error_taxonomy", {}).get("per_entity", {})
                },
                "fidelity_companions": recovery.get("fidelity_companions", {}),
            }
        ],
    }
    return build_target_indicator_report(source)


def _target_surface(arch: Mapping[str, Any], *, projected: bool) -> dict[str, Any]:
    candidate = _target_report(arch, projected=projected)["candidates"][0]
    return {
        "overall": candidate["overall_target_score"],
        "by_indicator": candidate["headline_scores"],
    }


def _fidelity_companions(arch: Mapping[str, Any]) -> dict[str, Any]:
    companions = arch["clinical_recovery"].get("fidelity_companions", {})
    dx = companions.get(DIAGNOSIS.name, {})
    sf = companions.get(SEIZURE_FREQUENCY.name, {})
    return {
        DIAGNOSIS.name: {
            "concept_negation": {
                "f1": float(dx.get("companion_f1", 0.0)),
                "headline_f1": float(dx.get("headline_f1", 0.0)),
                "fidelity_gap": float(dx.get("fidelity_gap", 0.0)),
            }
        },
        SEIZURE_FREQUENCY.name: {
            "active_rate_fidelity": {
                "f1": float(sf.get("companion_f1", 0.0)),
                "headline_f1": float(sf.get("headline_f1", 0.0)),
                "fidelity_gap": float(sf.get("fidelity_gap", 0.0)),
            }
        },
    }


def _changed_row_accounting(
    rows: Sequence[Mapping[str, Any]],
    *,
    baseline: Sequence[PredictedLetter],
    candidate: Sequence[PredictedLetter],
) -> dict[str, Any]:
    baseline_by_id = {letter.letter_id: letter for letter in baseline}
    candidate_by_id = {letter.letter_id: letter for letter in candidate}
    details: list[dict[str, Any]] = []
    by_indicator = {
        indicator: {"changed_rows": 0, "categories": Counter()}
        for indicator in TARGET_INDICATORS
    }
    for row in rows:
        letter_id = str(row["letter_id"])
        for indicator in TARGET_INDICATORS:
            old_mentions = [
                _mention_to_dict(m)
                for m in baseline_by_id[letter_id].mentions
                if m.entity == indicator
            ]
            new_mentions = [
                _mention_to_dict(m)
                for m in candidate_by_id[letter_id].mentions
                if m.entity == indicator
            ]
            if _mention_set(old_mentions) == _mention_set(new_mentions):
                continue
            categories = _change_categories(indicator, row, old_mentions, new_mentions)
            by_indicator[indicator]["changed_rows"] += 1
            by_indicator[indicator]["categories"].update(categories)
            details.append(
                {
                    "letter_id": letter_id,
                    "indicator": indicator,
                    "categories": categories,
                    "old_mentions": old_mentions,
                    "new_mentions": new_mentions,
                }
            )
    return {
        "by_indicator": {
            indicator: {
                "changed_rows": stats["changed_rows"],
                "categories": dict(stats["categories"]),
            }
            for indicator, stats in by_indicator.items()
        },
        "details": details,
    }


def _change_categories(
    indicator: str,
    row: Mapping[str, Any],
    old_mentions: Sequence[Mapping[str, Any]],
    new_mentions: Sequence[Mapping[str, Any]],
) -> list[str]:
    if indicator == DIAGNOSIS.name:
        categories: list[str] = []
        if _has_attr_transition(old_mentions, new_mentions, "Negation"):
            categories.append("assertion_or_negation_change")
        if len(new_mentions) != len(old_mentions):
            categories.append("hierarchy_reconciliation_or_duplicate_collapse")
        if _only_cui_changed(old_mentions, new_mentions):
            categories.append("projection_only")
        return categories or ["hierarchy_reconciliation"]
    if indicator == SEIZURE_FREQUENCY.name:
        categories = sorted(
            {
                _sf_change_category(mention)
                for mention in [*old_mentions, *new_mentions]
            }
        )
        lane = row.get("lanes", {}).get(indicator, {})
        diagnostics = lane.get("diagnostics", {})
        if diagnostics.get("projection_actions"):
            categories.append("projection_action")
        if diagnostics.get("suppression_actions"):
            categories.append("reject_or_drop")
        return categories or ["unknown"]
    return ["model_output"] if not _only_cui_changed(old_mentions, new_mentions) else ["projection_only"]


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


def _evidence_invalid_for_lane(lane: Mapping[str, Any], indicator: str) -> int:
    diagnostics = lane.get("diagnostics", {})
    warnings = [str(w) for w in diagnostics.get("gate_warnings", [])]
    prefixed = [
        warning
        for warning in warnings
        if warning.startswith(f"{indicator}: ")
        and "dropped_evidence_not_substring" in warning
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


def _has_blocking_parse_issue(errors: Any) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in (errors or [])
    )


def _evidence_exact(evidence: str, note_text: str) -> bool:
    return bool(evidence) and evidence in note_text


def _lane_sources(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, str]]:
    out = {}
    for indicator in TARGET_INDICATORS:
        lane = LANES[indicator]
        source = sources[lane["source_key"]]
        out[indicator] = {
            "artifact": source["artifact"],
            "source_lane": lane["source_lane"],
            "ownership_label": lane["ownership"],
        }
    return out


def _validate_source_rows(
    gold_letters: Sequence[ExectLetter],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    sources: Mapping[str, Mapping[str, Any]],
) -> None:
    expected = {letter.letter_id for letter in gold_letters}
    for key, rows in source_rows.items():
        observed = set(rows)
        missing = sorted(expected - observed)
        extra = sorted(observed - expected)
        if missing or extra:
            raise ValueError(
                f"{sources[key]['artifact']} does not match frozen row set: "
                f"missing={missing[:5]} extra={extra[:5]}"
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
            "focused-lane replay has scored mentions without exact source evidence: "
            + ", ".join(invalid[:10])
        )


def _source(path: Path, label: str) -> dict[str, Any]:
    return {"path": path, "artifact": path.as_posix(), "label": label}


def _rows_by_id(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[str(row["letter_id"])] = row
    return rows


def _raw_mentions(row: Mapping[str, Any], *, default_entity: str) -> list[dict[str, Any]]:
    raw = row.get("raw_output") or ""
    if not raw:
        return []
    try:
        payload = json.loads(str(raw))
    except json.JSONDecodeError:
        return []
    mentions = payload.get("mentions", []) if isinstance(payload, dict) else []
    out = []
    for mention in mentions:
        if not isinstance(mention, dict):
            continue
        with_entity = dict(mention)
        with_entity.setdefault("entity", default_entity)
        out.append(with_entity)
    return out


def _enhance_mention(
    mention: Mapping[str, Any],
    row: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    indicator: str,
    raw: bool,
) -> dict[str, Any]:
    lane = LANES[indicator]
    diagnostics = _lane_diagnostics_from_row(row)
    return {
        "entity": indicator,
        "text": str(mention.get("text", "")),
        "attributes": {
            str(k): str(v)
            for k, v in dict(mention.get("attributes", {})).items()
        },
        "evidence": str(mention.get("evidence", "")),
        "rationale": str(mention.get("rationale", "")),
        "confidence": mention.get("confidence"),
        "component_owner": lane["ownership"],
        "source_artifact": source["artifact"],
        "source_lane": lane["source_lane"],
        "source_pipeline_family": row.get("pipeline_family", ""),
        "source_model": row.get("model", ""),
        "source_prompt_version": row.get("prompt_version", ""),
        "raw_surface": raw,
        "deterministic_provenance": diagnostics,
    }


def _lane_diagnostics_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "gate_warnings": list(row.get("gate_warnings", [])),
        "projection_version": row.get("projection_version", ""),
        "source_projection_version": row.get("source_projection_version", ""),
        "suppression_version": row.get("suppression_version", ""),
        "projection_actions": row.get("projection_actions", []),
        "suppression_actions": row.get("suppression_actions", []),
        "component_owner": row.get("component_owner", ""),
        "n_evidence_invalid": row.get("n_evidence_invalid", 0),
    }


def _status_from_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "call_error": row.get("call_error"),
        "parse_errors": row.get("parse_errors", []),
        "n_mentions_raw": row.get("n_mentions_raw", 0),
        "n_mentions_scored": row.get("n_mentions_scored", 0),
        "n_evidence_invalid": row.get("n_evidence_invalid", 0),
    }


def _predictions_from_rows(
    rows: Sequence[Mapping[str, Any]],
    mention_key: str,
) -> list[PredictedLetter]:
    return [
        PredictedLetter(
            letter_id=str(row["letter_id"]),
            mentions=tuple(_predicted_mention(m) for m in row.get(mention_key, [])),
        )
        for row in rows
    ]


def _control_predictions(
    gold_letters: Sequence[ExectLetter],
    control_rows: Mapping[str, Mapping[str, Any]],
) -> list[PredictedLetter]:
    out = []
    for letter in gold_letters:
        row = control_rows[letter.letter_id]
        out.append(
            PredictedLetter(
                letter_id=letter.letter_id,
                mentions=tuple(
                    _predicted_mention(
                        _enhance_mention(
                            m,
                            row,
                            _source(Path("control"), "control"),
                            indicator=str(m["entity"]),
                            raw=False,
                        )
                    )
                    for m in row.get("predicted_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
    return out


def _comparator_predictions(
    gold_letters: Sequence[ExectLetter],
    comparator_rows: Mapping[str, Mapping[str, Any]] | None,
) -> list[PredictedLetter]:
    if comparator_rows is None:
        return []
    return [
        PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                _predicted_mention(m)
                for m in comparator_rows[letter.letter_id].get("predicted_mentions", [])
                if str(m.get("entity")) in TARGET_INDICATORS
            ),
        )
        for letter in gold_letters
    ]


def _predicted_mention(row: Mapping[str, Any]) -> PredictedMention:
    confidence = row.get("confidence")
    if confidence not in {"low", "medium", "high"}:
        confidence = None
    return PredictedMention(
        entity=str(row["entity"]),
        text=str(row.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(row.get("attributes", {})).items()},
        evidence=str(row.get("evidence", "")),
        rationale=str(row.get("rationale", "")),
        confidence=confidence,
        component_owner=str(row.get("component_owner", "")),
    )


def _mention_to_dict(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "component_owner": mention.component_owner,
    }


def _mention_set(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
    return {
        json.dumps(
            {
                "entity": m.get("entity", ""),
                "text": m.get("text", ""),
                "attributes": dict(m.get("attributes", {})),
                "evidence": m.get("evidence", ""),
            },
            sort_keys=True,
        )
        for m in mentions
    }


def _gold_to_row(annotation: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "attributes": dict(annotation.attributes),
    }


def _has_attr_transition(
    old_mentions: Sequence[Mapping[str, Any]],
    new_mentions: Sequence[Mapping[str, Any]],
    attr: str,
) -> bool:
    old = Counter(str(m.get("attributes", {}).get(attr, "")) for m in old_mentions)
    new = Counter(str(m.get("attributes", {}).get(attr, "")) for m in new_mentions)
    return old != new


def _only_cui_changed(
    old_mentions: Sequence[Mapping[str, Any]],
    new_mentions: Sequence[Mapping[str, Any]],
) -> bool:
    def strip_cui(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
        stripped = []
        for mention in mentions:
            attrs = {
                k: v
                for k, v in dict(mention.get("attributes", {})).items()
                if k not in {"CUI", "CUIPhrase"}
            }
            stripped.append({**dict(mention), "attributes": attrs})
        return _mention_set(stripped)

    return strip_cui(old_mentions) == strip_cui(new_mentions)


def _sf_change_category(mention: Mapping[str, Any]) -> str:
    attrs = dict(mention.get("attributes", {}))
    if attrs.get("NumberOfSeizures") == "0":
        return "seizure_free"
    if attrs.get("FrequencyChange"):
        return "unknown_or_change_state"
    if any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        return "active_rate"
    if str(mention.get("text", "")).lower() in {"seizure", "seizures"}:
        return "generic_vs_specific"
    return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the ExECTv2 focused-lane component-evidence no-call replay",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--split", default="dev")
    parser.add_argument("--row-count", type=int, default=140)
    parser.add_argument("--control-artifact", type=Path, default=DEFAULT_CONTROL_ARTIFACT)
    parser.add_argument("--diagnosis-artifact", type=Path, default=DEFAULT_DIAGNOSIS_ARTIFACT)
    parser.add_argument("--sf-artifact", type=Path, default=DEFAULT_SF_ARTIFACT)
    parser.add_argument(
        "--focused-comparator-artifact",
        type=Path,
        default=DEFAULT_FOCUSED_COMPARATOR_ARTIFACT,
    )
    parser.add_argument("--out-jsonl", type=Path, default=DEFAULT_OUT_JSONL)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_OUT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_OUT_MD)
    args = parser.parse_args()

    outputs = write_focused_lane_outputs(
        out_jsonl=args.out_jsonl,
        out_json=args.out_json,
        out_md=args.out_md,
        split=args.split,
        row_count=args.row_count,
        control_artifact=args.control_artifact,
        diagnosis_artifact=args.diagnosis_artifact,
        sf_artifact=args.sf_artifact,
        focused_comparator_artifact=args.focused_comparator_artifact,
    )
    for name, path in outputs.items():
        print(f"Wrote {name}: {path}")


if __name__ == "__main__":
    main()
