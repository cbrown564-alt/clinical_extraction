"""First-class scoring views over assembled ExECTv2 findings."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.reporting import (
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
    build_target_indicator_report,
)


@dataclass(frozen=True)
class FindingViewResult:
    view_id: str
    predictions: tuple[PredictedLetter, ...]
    summary: Mapping[str, Any]


def predictions_from_rows(
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


def predictions_from_prediction_surface(
    rows: Sequence[Mapping[str, Any]],
    surface_key: str,
) -> list[PredictedLetter]:
    return [
        PredictedLetter(
            letter_id=str(row["letter_id"]),
            mentions=tuple(
                _predicted_mention(m)
                for m in row.get("prediction_surfaces", {}).get(surface_key, [])
            ),
        )
        for row in rows
    ]


def build_scoring_views(
    *,
    candidate_name: str,
    ownership: str,
    gold_letters: Sequence[ExectLetter],
    raw_predictions: Sequence[PredictedLetter],
    scored_predictions: Sequence[PredictedLetter],
    materialized_predictions: Mapping[str, Sequence[PredictedLetter]] | None = None,
) -> tuple[dict[str, FindingViewResult], dict[str, Any], dict[str, Any]]:
    """Render raw, evidence-valid, headline, fidelity, and benchmark/CUI views."""

    raw_arch = architecture_report(
        name=f"{candidate_name}_raw",
        ownership=ownership,
        gold_letters=gold_letters,
        pred_letters=raw_predictions,
        entities=TARGET_INDICATORS,
    )
    scored_arch = architecture_report(
        name=candidate_name,
        ownership=ownership,
        gold_letters=gold_letters,
        pred_letters=scored_predictions,
        entities=TARGET_INDICATORS,
    )
    projected = [project_cuis(letter) for letter in scored_predictions]
    projected_arch = architecture_report(
        name=f"{candidate_name}_cui_projected",
        ownership=ownership,
        gold_letters=gold_letters,
        pred_letters=projected,
        entities=TARGET_INDICATORS,
    )
    fidelity = _fidelity_companions(scored_arch)
    benchmark = {
        "raw": scored_arch["cui_audit"]["overall"]["benchmark_f1_raw_llm"],
        "after_cui_projection": scored_arch["cui_audit"]["overall"][
            "benchmark_f1_after_cui_projection"
        ],
        "by_indicator_raw": {
            entity: scored_arch["cui_audit"]["per_entity"][entity]["benchmark_f1"]
            for entity in TARGET_INDICATORS
        },
    }
    score_ladder = {
        "raw_lane_score": _target_surface(raw_arch, projected=False),
        "evidence_valid_score": _target_surface(scored_arch, projected=False),
        "cui_projection_companion": _target_surface(projected_arch, projected=False),
        "headline_target": _target_surface(scored_arch, projected=True),
        "benchmark": benchmark,
        "fidelity_companions": fidelity,
    }
    materialized_scores: dict[str, Any] = {}
    for surface_key, predictions in (materialized_predictions or {}).items():
        arch = architecture_report(
            name=f"{candidate_name}_{surface_key}",
            ownership=ownership,
            gold_letters=gold_letters,
            pred_letters=predictions,
            entities=TARGET_INDICATORS,
        )
        materialized_scores[surface_key] = _target_surface(arch, projected=False)
    if materialized_scores:
        score_ladder["materialized_surfaces"] = materialized_scores
    view_results = {
        "raw_candidate": FindingViewResult(
            view_id="raw_candidate",
            predictions=tuple(raw_predictions),
            summary=score_ladder["raw_lane_score"],
        ),
        "evidence_valid": FindingViewResult(
            view_id="evidence_valid",
            predictions=tuple(scored_predictions),
            summary=score_ladder["evidence_valid_score"],
        ),
        "clinical_headline": FindingViewResult(
            view_id="clinical_headline",
            predictions=tuple(scored_predictions),
            summary=score_ladder["headline_target"],
        ),
        "fidelity_companion": FindingViewResult(
            view_id="fidelity_companion",
            predictions=tuple(scored_predictions),
            summary=fidelity,
        ),
        "benchmark_cui": FindingViewResult(
            view_id="benchmark_cui",
            predictions=tuple(projected),
            summary=benchmark,
        ),
    }
    headline_report = _target_report(scored_arch, projected=True)
    return view_results, score_ladder, headline_report


def changed_row_accounting(
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
                mention_to_dict(m)
                for m in baseline_by_id[letter_id].mentions
                if m.entity == indicator
            ]
            new_mentions = [
                mention_to_dict(m)
                for m in candidate_by_id[letter_id].mentions
                if m.entity == indicator
            ]
            if mention_set(old_mentions) == mention_set(new_mentions):
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


def control_predictions_from_rows(
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
                    _predicted_mention(m)
                    for m in row.get("predicted_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
    return out


def comparator_predictions_from_rows(
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


def mention_to_dict(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "component_owner": mention.component_owner,
    }


def mention_set(mentions: Sequence[Mapping[str, Any]]) -> set[str]:
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


def _target_report(arch: Mapping[str, Any], *, projected: bool) -> dict[str, Any]:
    scores_key = "cui_projected_headline_scores" if projected else "headline_scores"
    recovery = arch["clinical_recovery"]
    source = {
        "pipeline_family": "exectv2_finding_assembly_views",
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
    if not _only_cui_changed(old_mentions, new_mentions):
        return ["model_output"]
    return ["projection_only"]


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
        return mention_set(stripped)

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
