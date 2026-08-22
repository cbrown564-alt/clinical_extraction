"""ADR 0030 target-indicator report for ExECTv2 Plan 11."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores as aggregate_exact_clinical_headline_scores,
)

TARGET_INDICATORS: tuple[str, ...] = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
DEFAULT_TARGET_F1 = 0.9
ADR_PATH = "docs/decisions/0030-four-exact-indicators-drive-exectv2-plan11.md"
HEADLINE_SCORE_POLICIES: dict[str, str] = {
    DIAGNOSIS.name: (
        "exact per-letter clinical-fact unit-key score after deterministic "
        "Diagnosis normalization/projection"
    ),
    SEIZURE_FREQUENCY.name: (
        "projected seizure-state clinical_headline score after deterministic "
        "frequency-state normalization/projection"
    ),
    PRESCRIPTION.name: (
        "clinical_headline regimen score after deterministic medication normalization/projection"
    ),
    INVESTIGATIONS.name: (
        "clinical_headline modality/performed/result score after deterministic "
        "investigation normalization/projection"
    ),
}


def build_target_indicator_report(
    source_report: Mapping[str, Any],
    *,
    threshold: float = DEFAULT_TARGET_F1,
) -> dict[str, Any]:
    """Project an existing routed comparison onto the ADR 0030 target surface."""

    candidates = [
        _candidate_target_report(candidate, threshold=threshold)
        for candidate in source_report.get("candidates", [])
    ]
    best_by_indicator = {
        indicator: _best_candidate_for_indicator(candidates, indicator)
        for indicator in TARGET_INDICATORS
    }
    return {
        "pipeline_family": "exectv2_adr0030_target_indicator_report",
        "source_pipeline_family": source_report.get("pipeline_family", ""),
        "source_generated_on": source_report.get("generated_on", ""),
        "split": source_report.get("split", ""),
        "stage": source_report.get("stage", ""),
        "row_count": source_report.get("row_count", 0),
        "adr": ADR_PATH,
        "target_f1": threshold,
        "target_indicators": list(TARGET_INDICATORS),
        "headline_score_policies": dict(HEADLINE_SCORE_POLICIES),
        "scope_note": (
            "ADR 0030 surface only: Diagnosis, SeizureFrequency, Prescription, "
            "and Investigations. Non-target ExECT families are intentionally omitted."
        ),
        "candidates": candidates,
        "best_by_indicator": best_by_indicator,
    }


def render_target_indicator_markdown(report: Mapping[str, Any]) -> str:
    """Render a compact target-only readout."""

    lines = [
        "# ExECTv2 ADR 0030 Target Indicator Report",
        "",
        f"- Source: `{report['source_pipeline_family']}`",
        f"- Split/stage: `{report['split']}` / `{report['stage']}`",
        f"- Rows: `{report['row_count']}`",
        f"- Target F1: `>{report['target_f1']:.3f}` for each indicator",
        f"- ADR: `{report['adr']}`",
        "",
        "## Headline Scoring Policy",
        "",
        "| Indicator | Headline score used |",
        "| --- | --- |",
    ]
    for indicator in report["target_indicators"]:
        lines.append(f"| {indicator} | {report['headline_score_policies'][indicator]} |")
    lines.extend(
        [
            "",
            "## Candidate Readout",
            "",
            "| Candidate | Ownership | Overall target F1 | Clears all four? | "
            "Blocking indicators |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for candidate in report["candidates"]:
        blocking = ", ".join(candidate["blocking_indicators"]) or "none"
        clears = "yes" if candidate["meets_all_targets"] else "no"
        lines.append(
            f"| {candidate['name']} | `{candidate['ownership']}` | "
            f"{candidate['overall_target_score']['f1']:.4f} | {clears} | {blocking} |"
        )

    lines += [
        "",
        "## Indicator Scores",
        "",
        "| Candidate | Indicator | F1 | Precision | Recall | TP | FP | FN | Shortfall |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for candidate in report["candidates"]:
        for indicator in report["target_indicators"]:
            score = candidate["headline_scores"][indicator]
            lines.append(
                f"| {candidate['name']} | {indicator} | {score['f1']:.4f} "
                f"| {score['precision']:.4f} | {score['recall']:.4f} "
                f"| {score['tp']} | {score['fp']} | {score['fn']} "
                f"| {score['shortfall_to_target']:.4f} |"
            )

    lines += [
        "",
        "## Error Analysis",
        "",
        (
            "| Candidate | Indicator | candidate_miss | wrong_detail_selection "
            "| projection_gap | evidence_failure |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for candidate in report["candidates"]:
        per_indicator = candidate["error_analysis"]["per_indicator"]
        for indicator in report["target_indicators"]:
            errors = per_indicator.get(indicator, {})
            lines.append(
                f"| {candidate['name']} | {indicator} "
                f"| {int(errors.get('candidate_miss', 0))} "
                f"| {int(errors.get('wrong_detail_selection', 0))} "
                f"| {int(errors.get('projection_gap', 0))} "
                f"| {int(errors.get('evidence_failure', 0))} |"
            )

    lines += [
        "",
        "## Clinical Fidelity Companions",
        "",
        (
            "Headline keys deliberately demote projectable attributes. The "
            "SeizureFrequency companion exposes one clinical-fidelity gap: its "
            "`clinical_headline` forgives rate magnitude (for example, 2-4/month "
            "and 6-9/week share one key)."
        ),
        "",
        (
            "| Candidate | Indicator | Companion | Forgives | Headline F1 "
            "| Companion F1 | Fidelity gap |"
        ),
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for candidate in report["candidates"]:
        companions = candidate.get("fidelity_companions", {})
        for indicator in report["target_indicators"]:
            companion = companions.get(indicator)
            if not companion:
                continue
            lines.append(
                f"| {candidate['name']} | {indicator} | `{companion['companion']}` "
                f"| {companion['forgives']} | {companion['headline_f1']:.4f} "
                f"| {companion['companion_f1']:.4f} | {companion['fidelity_gap']:.4f} |"
            )

    lines += [
        "",
        "## Best Current Indicator Scores",
        "",
        "| Indicator | Best candidate | F1 | Shortfall |",
        "| --- | --- | ---: | ---: |",
    ]
    for indicator, best in report["best_by_indicator"].items():
        lines.append(
            f"| {indicator} | {best['candidate']} | {best['f1']:.4f} "
            f"| {best['shortfall_to_target']:.4f} |"
        )
    lines.append("")
    return "\n".join(lines)


def _candidate_target_report(
    candidate: Mapping[str, Any],
    *,
    threshold: float,
) -> dict[str, Any]:
    recovery = candidate.get("routed_primary_recovery", {})
    headline_scores = recovery.get("headline_scores", {})
    scores = {
        indicator: _score_with_shortfall(headline_scores[indicator], threshold)
        for indicator in TARGET_INDICATORS
    }
    blocking = [
        indicator for indicator, score in scores.items() if float(score.get("f1", 0.0)) <= threshold
    ]
    return {
        "name": candidate.get("name", ""),
        "ownership": candidate.get("ownership", ""),
        "overall_target_score": _aggregate_scores(tuple(scores.values())),
        "headline_scores": scores,
        "meets_all_targets": not blocking,
        "blocking_indicators": blocking,
        "error_analysis": {
            "per_indicator": _target_only_errors(candidate),
        },
        "fidelity_companions": dict(candidate.get("fidelity_companions", {})),
    }


def _score_with_shortfall(
    score: Mapping[str, Any],
    threshold: float,
) -> dict[str, Any]:
    out = dict(score)
    out["shortfall_to_target"] = round(max(0.0, threshold - float(out["f1"])), 4)
    return out


def _target_only_errors(candidate: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    per_entity = candidate.get("routed_primary_errors", {}).get("per_entity", {})
    return {
        indicator: {key: int(value) for key, value in dict(per_entity.get(indicator, {})).items()}
        for indicator in TARGET_INDICATORS
    }


def _aggregate_scores(scores: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return aggregate_exact_clinical_headline_scores(dict(score) for score in scores)


def _best_candidate_for_indicator(
    candidates: Sequence[Mapping[str, Any]],
    indicator: str,
) -> dict[str, Any]:
    best = max(
        candidates,
        key=lambda c: float(c["headline_scores"][indicator]["f1"]),
    )
    score = best["headline_scores"][indicator]
    return {
        "candidate": best["name"],
        "f1": score["f1"],
        "precision": score["precision"],
        "recall": score["recall"],
        "shortfall_to_target": score["shortfall_to_target"],
    }
