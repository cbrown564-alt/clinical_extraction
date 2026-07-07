"""Projection-rule registry and attribution sidecar for ExECTv2 target runs."""

from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from clinical_extraction.core.scoring import PRF1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_concept_identity,
    score_entity,
    score_frequency_state,
    semantic_config_for,
)


class ProjectionPortability(StrEnum):
    GENERAL = "general"
    CLINICAL_EPILEPSY = "clinical_epilepsy"
    SEIZURE_FREQUENCY = "seizure_frequency"
    GAN2026_SPECIFIC = "gan2026_specific"
    BENCHMARK_FORMAT = "benchmark_format"


@dataclass(frozen=True)
class ProjectionRuleSpec:
    rule_id: str
    entity: str
    portability: ProjectionPortability
    enabled_by_default: bool = True
    switch_name: str | None = None
    switch_status: str = "declared_registry_only"

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "entity": self.entity,
            "portability_category": self.portability.value,
            "enabled_by_default": self.enabled_by_default,
            "switch_name": self.switch_name or f"projection_rules.{self.rule_id}",
            "switch_status": self.switch_status,
        }


TARGET_ENTITIES = frozenset(
    {
        DIAGNOSIS.name,
        SEIZURE_FREQUENCY.name,
        PRESCRIPTION.name,
        INVESTIGATIONS.name,
    }
)


def _spec(
    rule_id: str,
    entity: str,
    portability: ProjectionPortability,
) -> ProjectionRuleSpec:
    return ProjectionRuleSpec(rule_id=rule_id, entity=entity, portability=portability)


def _quarantined_spec(
    rule_id: str,
    entity: str,
    portability: ProjectionPortability,
) -> ProjectionRuleSpec:
    return ProjectionRuleSpec(
        rule_id=rule_id,
        entity=entity,
        portability=portability,
        enabled_by_default=False,
        switch_name=f"target_projection_family_switches.{rule_id}",
        switch_status="adapter_quarantined_default_audit_replay",
    )


PROJECTION_RULE_REGISTRY: dict[str, ProjectionRuleSpec] = {
    spec.rule_id: spec
    for spec in (
        _spec("normalized_diagnosis_text", DIAGNOSIS.name, ProjectionPortability.CLINICAL_EPILEPSY),
        _spec(
            "projected_active_rate_seizure_type_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_typed_seizure_frequency_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_typed_controlled_state_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_sf_context_to_focal_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_focal_onset_sf_candidate_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_dropped_sf_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_remote_seizure_type_to_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_header_parent_epilepsy",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_context_parent_epilepsy",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "split_generalised_epilepsy_syndrome",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "split_syndrome_to_tonic_clonic_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "split_secondary_gtc_to_tonic_clonic_diagnosis",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "split_temporal_lobe_onset_to_focal_seizures",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "dropped_non_epilepsy_core",
            DIAGNOSIS.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec("normalized_time_period", SEIZURE_FREQUENCY.name, ProjectionPortability.GENERAL),
        _spec(
            "split_range_attribute",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GENERAL,
        ),
        _spec(
            "normalized_seizure_frequency_text",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "dropped_unsupported_episode_frequency_anchor",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "dropped_inconsistent_zero_state_with_active_rate",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_march_range_count",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _quarantined_spec(
            "projected_four_since_last_clinic",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _quarantined_spec(
            "projected_several_since_last_clinic",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _spec(
            "projected_generic_yearly_rate_anchor",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _spec(
            "projected_last_event_month_year_to_zero_since",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _spec(
            "projected_every_n_to_m_periods_to_one_event_rate",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _spec(
            "projected_every_n_periods_to_one_event_rate",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _spec(
            "projected_vague_yearly_rate",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "projected_remote_last_seizures_to_seizure_free",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _quarantined_spec(
            "projected_christmas_point_to_month_date",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _quarantined_spec(
            "projected_diagnosis_context_to_remote_last_seizures_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _quarantined_spec(
            "projected_infrequent_context_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _quarantined_spec(
            "projected_diagnosis_context_to_controlled_sf_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _quarantined_spec(
            "projected_diagnosis_context_to_frequent_myoclonic_jerks",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _spec(
            "projected_controlled_context_to_infrequent_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_controlled_drug_change_to_infrequent_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_returned_context_to_increased_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_dated_absence_like_zero_to_active_rate",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _spec(
            "projected_infrequent_diagnosis_year_to_change_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _spec(
            "split_cluster_of_seizures_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _spec(
            "split_convulsive_zero_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.SEIZURE_FREQUENCY,
        ),
        _quarantined_spec(
            "repaired_since_last_clinic_count_evidence",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.GAN2026_SPECIFIC,
        ),
        _quarantined_spec(
            "repaired_last_event_evidence",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _spec(
            "projected_frequency_header_diagnosis_to_sf_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_focal_diagnosis_context_to_sf_state",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_dated_diagnosis_context_to_sf",
            SEIZURE_FREQUENCY.name,
            ProjectionPortability.CLINICAL_EPILEPSY,
        ),
        _spec(
            "projected_prescription_frequency_from_evidence",
            PRESCRIPTION.name,
            ProjectionPortability.GENERAL,
        ),
        _spec(
            "projected_eeg_context_to_mri_normal",
            INVESTIGATIONS.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
        _spec(
            "projected_mri_context_to_eeg_result",
            INVESTIGATIONS.name,
            ProjectionPortability.BENCHMARK_FORMAT,
        ),
    )
}


@dataclass(frozen=True)
class ParsedRuleWarning:
    rule_id: str
    entity: str
    warning: str


def build_projection_rule_sidecar(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Summarize registered projection-rule fires against same-row raw-output replay.

    The current v0.39-v0.42 artifacts expose warning families, not isolated
    single-rule-disabled predictions. Correction/regression counts therefore
    compare the saved post-projection row with the same row's raw LLM output
    when available, and attribute the row-level change to every registered rule
    family that fired on that entity.
    """

    rule_rows: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    rule_warnings: dict[str, list[str]] = defaultdict(list)
    source_artifacts: set[str] = set()
    unknown_projection_warnings: list[str] = []
    for row in rows:
        source_artifact = str(row.get("source_artifact") or "")
        if source_artifact:
            source_artifacts.add(source_artifact)
        seen_for_row: set[str] = set()
        for parsed in parse_registered_rule_warnings(row.get("gate_warnings") or []):
            key = f"{parsed.rule_id}:{row.get('source_artifact', '')}:{row.get('letter_id', '')}"
            if key in seen_for_row:
                continue
            seen_for_row.add(key)
            rule_rows[parsed.rule_id].append(row)
            rule_warnings[parsed.rule_id].append(parsed.warning)
        unknown_projection_warnings.extend(
            warning
            for warning in row.get("gate_warnings") or []
            if _looks_projection_like(str(warning))
            and parse_rule_warning(str(warning)).rule_id not in PROJECTION_RULE_REGISTRY
        )

    rules = [
        _rule_attribution(rule_id, fired_rows, rule_warnings[rule_id])
        for rule_id, fired_rows in sorted(rule_rows.items())
    ]
    return {
        "pipeline_family": "exectv2_projection_rule_attribution_sidecar",
        "row_count": len(rows),
        "source_artifacts": sorted(source_artifacts),
        "attribution_note": (
            "Counts compare saved post-projection mentions with the same row's raw "
            "LLM output when available. They are warning-family attribution, not "
            "single-rule causal ablations, until switches are wired into the adapter."
        ),
        "registry": {
            rule_id: spec.as_dict() for rule_id, spec in sorted(PROJECTION_RULE_REGISTRY.items())
        },
        "rules": rules,
        "unknown_projection_warnings": sorted(set(unknown_projection_warnings)),
    }


def parse_registered_rule_warnings(warnings: Sequence[Any]) -> list[ParsedRuleWarning]:
    parsed: list[ParsedRuleWarning] = []
    for warning in warnings:
        item = parse_rule_warning(str(warning))
        if item.rule_id in PROJECTION_RULE_REGISTRY:
            parsed.append(item)
    return parsed


def parse_rule_warning(warning: str) -> ParsedRuleWarning:
    parts = [part.strip() for part in warning.split(":", 2)]
    if parts and parts[0] in TARGET_ENTITIES and len(parts) > 1:
        entity = parts[0]
        rule_id = parts[1].split()[0]
    else:
        rule_id = parts[0].split()[0] if parts else ""
        spec = PROJECTION_RULE_REGISTRY.get(rule_id)
        entity = spec.entity if spec else ""
    spec = PROJECTION_RULE_REGISTRY.get(rule_id)
    if spec is not None:
        entity = spec.entity
    return ParsedRuleWarning(rule_id=rule_id, entity=entity, warning=warning)


def render_projection_rule_sidecar_markdown(sidecar: Mapping[str, Any]) -> str:
    lines = [
        "# ExECTv2 Projection Rule Attribution Sidecar",
        "",
        f"- Rows: `{sidecar['row_count']}`",
        f"- Sources: `{', '.join(sidecar.get('source_artifacts') or ['in-memory'])}`",
        f"- Attribution: {sidecar['attribution_note']}",
        "",
        "## Fired Rules",
        "",
        (
            "| Rule | Entity | Portability | Default | Changed rows | "
            "Wrong-to-correct | Correct-to-wrong | Fidelity effect |"
        ),
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for rule in sidecar["rules"]:
        effects = ", ".join(
            f"{effect['metric']} {effect['before_f1']:.4f}->{effect['after_f1']:.4f}"
            for effect in rule["fidelity_effects"]
        )
        if not effects:
            effects = "n/a"
        lines.append(
            f"| `{rule['rule_id']}` | {rule['entity']} | "
            f"`{rule['portability_category']}` | {rule['enabled_by_default']} "
            f"| {rule['changed_row_count']} | {rule['wrong_to_correct_count']} "
            f"| {rule['correct_to_wrong_count']} | {effects} |"
        )
    if sidecar.get("unknown_projection_warnings"):
        lines.extend(["", "## Unregistered Projection-Like Warnings", ""])
        lines.extend(f"- `{warning}`" for warning in sidecar["unknown_projection_warnings"])
    lines.append("")
    return "\n".join(lines)


def read_jsonl_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        row["source_artifact"] = path.as_posix()
        rows.append(row)
    return rows


def _rule_attribution(
    rule_id: str,
    rows: Sequence[Mapping[str, Any]],
    warnings: Sequence[str],
) -> dict[str, Any]:
    spec = PROJECTION_RULE_REGISTRY[rule_id]
    wrong_to_correct = 0
    correct_to_wrong = 0
    for row in rows:
        before = _row_entity_primary_f1(row, spec.entity, prediction_key="raw")
        after = _row_entity_primary_f1(row, spec.entity, prediction_key="predicted_mentions")
        if before < 1.0 and after == 1.0:
            wrong_to_correct += 1
        elif before == 1.0 and after < 1.0:
            correct_to_wrong += 1
    return {
        **spec.as_dict(),
        "changed_row_count": len(rows),
        "changed_rows": sorted({str(row.get("letter_id", "")) for row in rows}),
        "wrong_to_correct_count": wrong_to_correct,
        "correct_to_wrong_count": correct_to_wrong,
        "fidelity_effects": _fidelity_effects(rows, spec.entity),
        "warning_examples": sorted(set(warnings))[:5],
    }


def _row_entity_primary_f1(
    row: Mapping[str, Any],
    entity: str,
    *,
    prediction_key: str,
) -> float:
    gold = _letter_from_mentions(row, "gold_mentions")
    pred = _letter_from_mentions(row, prediction_key)
    if entity == DIAGNOSIS.name:
        return score_concept_identity([gold], [pred], DIAGNOSIS.name).concept_only.f1
    if entity == SEIZURE_FREQUENCY.name:
        return score_frequency_state([gold], [pred]).clinical_headline.f1
    return score_entity([gold], [pred], entity, semantic_config_for(entity)).per_item.f1


def _fidelity_effects(rows: Sequence[Mapping[str, Any]], entity: str) -> list[dict[str, Any]]:
    if entity not in {DIAGNOSIS.name, SEIZURE_FREQUENCY.name}:
        return []
    gold = [_letter_from_mentions(row, "gold_mentions") for row in rows]
    raw = [_letter_from_mentions(row, "raw") for row in rows]
    projected = [_letter_from_mentions(row, "predicted_mentions") for row in rows]
    if entity == DIAGNOSIS.name:
        before = score_concept_identity(gold, raw, DIAGNOSIS.name).concept_negation
        after = score_concept_identity(gold, projected, DIAGNOSIS.name).concept_negation
        return [_effect_dict("Diagnosis.concept_negation", before, after)]
    before = score_frequency_state(gold, raw).active_rate_fidelity
    after = score_frequency_state(gold, projected).active_rate_fidelity
    return [_effect_dict("SeizureFrequency.active_rate_fidelity", before, after)]


def _effect_dict(metric: str, before: PRF1 | Any, after: PRF1 | Any) -> dict[str, Any]:
    return {
        "metric": metric,
        "before_f1": round(float(before.f1), 4),
        "after_f1": round(float(after.f1), 4),
        "delta_f1": round(float(after.f1) - float(before.f1), 4),
        "before": _score_counts(before),
        "after": _score_counts(after),
    }


def _score_counts(score: PRF1 | Any) -> dict[str, Any]:
    return {
        "tp": int(score.tp),
        "fp": int(score.fp),
        "fn": int(score.fn),
        "precision": round(float(score.precision), 4),
        "recall": round(float(score.recall), 4),
        "f1": round(float(score.f1), 4),
    }


def _letter_from_mentions(row: Mapping[str, Any], key: str) -> ExectLetter:
    if key == "raw":
        mentions = _raw_mentions(row)
    else:
        mentions = row.get(key) or []
    annotations = tuple(
        ExectAnnotation(
            entity=str(mention["entity"]),
            text=str(mention.get("text", "")),
            attributes={
                str(attr_key): str(attr_value)
                for attr_key, attr_value in dict(mention.get("attributes") or {}).items()
            },
        )
        for mention in mentions
        if str(mention.get("entity", "")) in TARGET_ENTITIES
    )
    return ExectLetter(
        letter_id=str(row.get("letter_id", "")),
        note_text="",
        annotations=annotations,
    )


def _raw_mentions(row: Mapping[str, Any]) -> Sequence[Mapping[str, Any]]:
    if row.get("raw_mentions") is not None:
        return row["raw_mentions"] or []
    raw_output = str(row.get("raw_output") or "").strip()
    if not raw_output:
        return row.get("predicted_mentions") or []
    try:
        payload = json.loads(raw_output)
    except json.JSONDecodeError:
        return row.get("predicted_mentions") or []
    mentions = payload.get("mentions", [])
    return mentions if isinstance(mentions, list) else []


def _looks_projection_like(warning: str) -> bool:
    parsed = parse_rule_warning(warning)
    return parsed.rule_id.startswith(
        ("projected_", "repaired_", "normalized_", "split_", "dropped_")
    )
