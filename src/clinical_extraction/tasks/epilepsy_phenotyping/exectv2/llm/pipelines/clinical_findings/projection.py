"""Deterministic projection from model findings to ExECTv2 layers."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalizer import (
    normalize_count,
    normalize_month,
    normalize_unit,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    canonicalize_attribute_value,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    ENTITY_NAME,
    PLAN11_EVENT_STATE_LAYER_LADDER,
    PLAN11_EVENT_STATE_ROUTE_VERSION,
    PROMPT_VERSION,
    _FREQUENCY_CHANGE_ALIASES,
    _OUTPUT_LAYERS,
    _POINT_IN_TIME_ALIASES,
    _TIME_RELATION_ALIASES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingRecord,
    ClinicalFindingsRecord,
)

def project_finding_to_attributes(
    finding: ClinicalFindingRecord,
    *,
    include_cui: bool,
) -> tuple[dict[str, str], list[str]]:
    """Project explicit model-emitted finding fields to ExECTv2 attributes."""

    attrs: dict[str, str] = {}
    warnings: list[str] = []

    count_low = _normalized_count_or_none(finding.count_low)
    count_high = _normalized_count_or_none(finding.count_high)
    if count_low is not None and count_high is not None and count_low == count_high:
        attrs["NumberOfSeizures"] = count_low
    else:
        _add_count(attrs, "NumberOfSeizures", finding.count)
        if count_low is not None:
            attrs["LowerNumberOfSeizures"] = count_low
        if count_high is not None:
            attrs["UpperNumberOfSeizures"] = count_high

    period_low = _normalized_count_or_none(finding.period_low)
    period_high = _normalized_count_or_none(finding.period_high)
    period_has_range = period_low is not None or period_high is not None
    if not period_has_range:
        _add_count(attrs, "NumberOfTimePeriods", finding.period_count)
    elif period_low is not None and period_high is not None and period_low == period_high:
        attrs["NumberOfTimePeriods"] = period_low
    elif period_low is not None and period_high is None:
        attrs["NumberOfTimePeriods"] = period_low
    elif period_high is not None and period_low is None:
        attrs["NumberOfTimePeriods"] = period_high
    else:
        attrs["LowerNumberOfTimePeriods"] = period_low or ""
        attrs["UpperNumberOfTimePeriods"] = period_high or ""

    if finding.clinical_kind == "seizure_free" and not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        attrs["NumberOfSeizures"] = "0"
    elif finding.clinical_kind == "last_event" and not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ):
        attrs["NumberOfSeizures"] = "0"
    elif finding.frequency_statement_type == "calendar_occurrence_no_count" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["NumberOfSeizures"] = "1"
    elif not any(
        key in attrs
        for key in (
            "NumberOfSeizures",
            "LowerNumberOfSeizures",
            "UpperNumberOfSeizures",
        )
    ) and any(
        key in attrs
        for key in (
            "NumberOfTimePeriods",
            "LowerNumberOfTimePeriods",
            "UpperNumberOfTimePeriods",
        )
    ):
        attrs["NumberOfSeizures"] = "1"

    if _filled(finding.period_unit):
        period_unit = (finding.period_unit or "").strip().lower()
        if period_unit in {"fortnight", "fortnights"}:
            attrs["TimePeriod"] = "Week"
            attrs["NumberOfTimePeriods"] = "2"
        else:
            attrs["TimePeriod"] = normalize_unit(finding.period_unit or "")
        if (
            finding.frequency_statement_type == "background_rate"
            and "NumberOfTimePeriods" not in attrs
            and "LowerNumberOfTimePeriods" not in attrs
            and "UpperNumberOfTimePeriods" not in attrs
        ):
            attrs["NumberOfTimePeriods"] = "1"
    if _filled(finding.time_relation):
        mapped = _map_alias(finding.time_relation, _TIME_RELATION_ALIASES)
        if (
            mapped == "Since"
            and finding.frequency_statement_type == "background_rate"
            and not _filled(finding.point_in_time)
        ):
            warnings.append("dropped_unanchored_background_rate_since")
        elif mapped:
            attrs["TimeSince_or_TimeOfEvent"] = mapped
        else:
            warnings.append(f"dropped_unmapped_time_relation: {finding.time_relation!r}")
    elif finding.frequency_statement_type == "header_count_since_anchor":
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
    elif finding.clinical_kind == "last_event" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["TimeSince_or_TimeOfEvent"] = "Since"
    elif finding.clinical_kind == "dated_count" and any(
        _filled(value) for value in (finding.day, finding.month, finding.year)
    ):
        attrs["TimeSince_or_TimeOfEvent"] = "During"
    if _filled(finding.point_in_time):
        mapped = _map_alias(finding.point_in_time, _POINT_IN_TIME_ALIASES)
        if mapped:
            attrs["PointInTime"] = mapped
        else:
            warnings.append(f"dropped_unmapped_point_in_time: {finding.point_in_time!r}")
    elif finding.frequency_statement_type == "header_count_since_anchor":
        attrs["PointInTime"] = "LastClinic"
    if _filled(finding.frequency_change):
        mapped = _map_alias(finding.frequency_change, _FREQUENCY_CHANGE_ALIASES)
        if mapped:
            attrs["FrequencyChange"] = mapped
        else:
            warnings.append(f"dropped_unmapped_frequency_change: {finding.frequency_change!r}")

    if _filled(finding.day):
        attrs["DayDate"] = normalize_count(finding.day or "")
    if _filled(finding.month):
        attrs["MonthDate"] = normalize_month(finding.month or "")
    if _filled(finding.year):
        attrs["YearDate"] = str(finding.year).strip()
    if _filled(finding.age_low):
        attrs["AgeLower"] = normalize_count(finding.age_low or "")
    if _filled(finding.age_high):
        attrs["AgeUpper"] = normalize_count(finding.age_high or "")
    if _filled(finding.age_unit):
        attrs["AgeUnit"] = normalize_unit(finding.age_unit or "")

    repaired, warnings = _repair_projected_attributes(attrs, warnings)
    if not include_cui:
        return repaired, warnings

    projected = project_cuis(
        PredictedLetter(
            letter_id="projection-preview",
            mentions=(
                PredictedMention(
                    entity=ENTITY_NAME,
                    text=finding.text,
                    attributes=repaired,
                    evidence=finding.evidence,
                ),
            ),
        )
    )
    projected_attrs = dict(projected.mentions[0].attributes)
    if "CUI" not in projected_attrs:
        warnings.append(f"cui_not_mapped: {finding.text!r}")
    return projected_attrs, warnings


def _add_count(attrs: dict[str, str], key: str, value: str | None) -> None:
    if _filled(value):
        attrs[key] = normalize_count(value or "")


def _normalized_count_or_none(value: str | None) -> str | None:
    if not _filled(value):
        return None
    return normalize_count(value or "")


def _filled(value: str | None) -> bool:
    return bool(value and value.strip())


def _map_alias(value: str | None, aliases: Mapping[str, str]) -> str | None:
    if not value:
        return None
    compact = re.sub(r"[\s_-]+", " ", value.strip().lower()).strip()
    return aliases.get(compact) or aliases.get(value.strip().lower())


def _repair_projected_attributes(
    attrs: dict[str, str], warnings: list[str]
) -> tuple[dict[str, str], list[str]]:
    spec = ENTITY_REGISTRY[ENTITY_NAME]
    repaired: dict[str, str] = {}
    for key, value in attrs.items():
        if key in spec.noise_attributes:
            continue
        if key not in spec.legal_attributes:
            warnings.append(f"dropped_illegal_attribute: {key!r}")
            continue
        normalized_value = canonicalize_attribute_value(key, value)
        if normalized_value != value:
            warnings.append(
                f"normalized_attribute_value: {key!r}={value!r} -> {normalized_value!r}"
            )
        if key in spec.closed_vocab and normalized_value not in spec.closed_vocab[key]:
            warnings.append(
                f"dropped_illegal_value: {key!r}={normalized_value!r}"
            )
            continue
        repaired[key] = normalized_value
    return repaired, warnings


def to_predicted_letters(
    letter_id: str,
    findings: list[ClinicalFindingRecord],
    *,
    note_text: str,
) -> tuple[dict[str, PredictedLetter], list[str]]:
    """Build format-only and CUI-projected prediction layers."""

    warnings: list[str] = []
    layer_mentions: dict[str, list[PredictedMention]] = {
        layer: [] for layer in _OUTPUT_LAYERS
    }

    for finding in findings:
        if finding.frequency_statement_type == "current_control_no_duration":
            warnings.append(f"model_excluded_current_control_no_duration: text={finding.text!r}")
            continue
        if not finding.evidence:
            warnings.append(f"dropped_empty_evidence: text={finding.text!r}")
            continue
        if not evidence_is_substring(note_text, finding.evidence):
            warnings.append(f"dropped_evidence_not_substring: text={finding.text!r}")
            continue

        attrs, attr_warnings = project_finding_to_attributes(finding, include_cui=False)
        warnings.extend(f"format_projected: {w}" for w in attr_warnings)
        layer_mentions["format_projected"].append(
            PredictedMention(
                entity=ENTITY_NAME,
                text=finding.text,
                attributes=attrs,
                evidence=finding.evidence,
                confidence=finding.confidence,
                rationale=finding.rationale,
                component_owner="llm_only_clinical_findings",
            )
        )

    format_projected = PredictedLetter(
        letter_id=letter_id,
        mentions=tuple(layer_mentions["format_projected"]),
        diagnostics={"prompt_version": PROMPT_VERSION, "layer": "format_projected"},
    )
    cui_projected = project_cuis(format_projected)
    layers = {
        "format_projected": format_projected,
        "cui_projected": cui_projected.model_copy(
            update={
                "diagnostics": {
                    **dict(format_projected.diagnostics),
                    "layer": "cui_projected",
                    "source_layer": "format_projected",
                    "cui_projected_mentions": cui_projected.diagnostics[
                        "cui_projected_mentions"
                    ],
                }
            }
        ),
    }
    return layers, warnings


def build_plan11_event_state_route(
    letter_id: str,
    record: ClinicalFindingsRecord,
    *,
    note_text: str,
) -> tuple[dict[str, PredictedLetter], dict[str, Any], list[str]]:
    """Run the documented Plan 11 SF event/state ladder over model output.

    The helper intentionally consumes only model-owned ``findings`` for scored
    mentions. ``event_frames`` are audit substrate and never become scored
    findings here, which keeps deterministic code from acting as a hidden
    clinical selector.
    """

    layers, warnings = to_predicted_letters(letter_id, record.findings, note_text=note_text)
    policy_counts = _post_llm_state_policy_counts(warnings)
    diagnostics = {
        "route_version": PLAN11_EVENT_STATE_ROUTE_VERSION,
        "route_contract": (
            "LLM owns raw_event_frames and raw_findings; deterministic code is "
            "limited to schema transport, evidence validation, format projection, "
            "CUI sidecar projection, no-op SF certainty sidecar, and explicitly "
            "named post-LLM state policy."
        ),
        "aggregate_ownership": (
            "llm_first"
            if not policy_counts
            else "llm_first_with_declared_post_llm_state_policy"
        ),
        "deterministic_clinical_selection": False,
        "deterministic_selection_actions": [],
        "post_llm_state_policy_counts": policy_counts,
        "layers": _plan11_layer_rows(record, layers, warnings, policy_counts),
    }
    return layers, diagnostics, warnings


def _post_llm_state_policy_counts(warnings: Sequence[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for warning in warnings:
        if warning.startswith("model_excluded_current_control_no_duration"):
            key = "current_control_no_duration_excluded"
            counts[key] = counts.get(key, 0) + 1
    return counts


def _plan11_layer_rows(
    record: ClinicalFindingsRecord,
    layers: Mapping[str, PredictedLetter],
    warnings: Sequence[str],
    policy_counts: Mapping[str, int],
) -> list[dict[str, Any]]:
    evidence_invalid = sum(
        1
        for warning in warnings
        if warning.startswith(("dropped_empty_evidence", "dropped_evidence_not_substring"))
    )
    counts = {
        "raw_event_frames": len(record.event_frames),
        "raw_findings": len(record.findings),
        "schema_valid_findings": len(record.findings),
        "evidence_validated": len(layers["format_projected"].mentions),
        "format_projected": len(layers["format_projected"].mentions),
        "cui_projected": len(layers["cui_projected"].mentions),
        "certainty_projected": 0,
        "post_llm_state_policy": sum(policy_counts.values()),
        "benchmark_rendered": len(layers["cui_projected"].mentions),
    }
    diagnostics = {
        "evidence_validated": {
            "evidence_invalid": evidence_invalid,
            "input_findings": len(record.findings),
        },
        "post_llm_state_policy": {"actions": dict(policy_counts)},
        "certainty_projected": {"sf_policy": "no_op"},
    }
    return [
        {
            **layer,
            "count": counts[layer["layer"]],
            "diagnostics": diagnostics.get(layer["layer"], {}),
        }
        for layer in PLAN11_EVENT_STATE_LAYER_LADDER
    ]
