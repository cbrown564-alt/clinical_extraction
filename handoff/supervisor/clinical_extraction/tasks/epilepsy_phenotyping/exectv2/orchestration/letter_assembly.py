"""Shared per-letter ExECT finding assembly used by replay and operations."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
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
    manifest_from_mapping,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.producers import (
    SavedJsonlProducer,
    findings_from_row,
    lane_diagnostics_from_row,
    status_from_row,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    INVESTIGATIONS,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    sf_state_projection,
    sf_unknown_suppression,
)

from .contracts import StructuredMethodConfig

TARGET_ENTITIES = (
    DIAGNOSIS.name,
    SEIZURE_FREQUENCY.name,
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
)
MATERIALIZED_SURFACES = (
    "source_scored",
    "evidence_valid",
    "protocol_model_preserving_canonical",
    "dictionary_normalized",
    "residual_benchmark_added",
)


def assemble_structured_rows(
    letters: Sequence[ExectLetter],
    structured_rows: Sequence[Mapping[str, Any]],
    *,
    config: StructuredMethodConfig | None = None,
) -> dict[str, dict[str, Any]]:
    """Apply SF projection and the four family lenses in one shared order."""

    config = config or StructuredMethodConfig.selected()
    direct_rows = [_direct_sf_row(row) for row in structured_rows]
    projected_rows = [
        sf_state_projection.project_row(row, ablation=config.sf_projection_ablation)
        for row in direct_rows
    ]
    suppressed_rows = [sf_unknown_suppression.suppress_row(row) for row in projected_rows]
    manifest = manifest_from_mapping(
        _manifest_payload(
            Path("structured.jsonl"),
            Path("sf.jsonl"),
            row_count=len(letters),
            config=config,
        )
    )
    source_rows: dict[str, dict[str, Mapping[str, Any]]] = {
        "structured_key_family_event_ledger": {
            str(row["letter_id"]): row for row in structured_rows
        },
        "sf_model_projection_suppression": {
            str(row["letter_id"]): row for row in suppressed_rows
        },
    }
    producers = {
        producer_id: SavedJsonlProducer.from_manifest(producer_manifest)
        for producer_id, producer_manifest in manifest.producers.items()
    }
    return {
        letter.letter_id: assemble_letter(
            letter,
            manifest=manifest,
            producers=producers,
            source_rows=source_rows,
            config=config,
        )[1]
        for letter in letters
    }


def assemble_letter(
    letter: ExectLetter,
    *,
    manifest: FindingAssemblyManifest,
    producers: Mapping[str, SavedJsonlProducer],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
    config: StructuredMethodConfig | None = None,
) -> tuple[ClinicalFindingStore, dict[str, Any]]:
    """Materialize one letter from raw/scored lanes and named lens policies."""

    config = config or StructuredMethodConfig.selected()
    store = ClinicalFindingStore(letter.letter_id, letter.note_text)
    lane_blocks: dict[str, Any] = {}
    predicted_mentions: list[dict[str, Any]] = []
    raw_mentions: list[dict[str, Any]] = []
    prediction_surfaces: dict[str, list[dict[str, Any]]] = {
        surface: [] for surface in MATERIALIZED_SURFACES
    }

    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
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
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=True,
            )
        )
        store.extend(
            findings_from_row(
                row,
                letter_id=letter.letter_id,
                entity=entity,
                note_text=letter.note_text,
                source=source,
                raw_surface=False,
            )
        )

    for entity in TARGET_ENTITIES:
        lens_config = manifest.lenses[entity]
        producer = producers[lens_config.producer]
        row = source_rows[lens_config.producer][letter.letter_id]
        source_lane = lens_config.source_lane or producer.source_lane or lens_config.producer
        lens_result = lens_from_manifest(lens_config).reconcile(
            store,
            policy=LensPolicy(
                producer_id=lens_config.producer,
                source_lane=source_lane,
                ownership_label=lens_config.ownership_label or producer.ownership_label,
                portability=lens_config.portability,
                diagnosis_resolution_candidate=config.diagnosis_resolution_candidate,
                model_preserving_policy_candidate=config.model_preserving_policy_candidate,
                prescription_rescue_scope_candidate=config.prescription_rescue_scope_candidate,
                prescription_policy_variant=config.prescription_policy_variant,
                diagnosis_policy_variant=config.diagnosis_policy_variant,
            ),
        )
        lane_scored = [finding.to_row() for finding in lens_result.findings]
        lane_surfaces = _lane_prediction_surfaces(
            store,
            entity=entity,
            producer_id=lens_config.producer,
            final_findings=lens_result.findings,
        )
        lane_surface_rows = {
            surface: [finding.to_row() for finding in findings]
            for surface, findings in lane_surfaces.items()
        }
        lane_raw_findings = list(
            store.findings(
                entity=entity,
                producer_id=lens_config.producer,
                raw_surface=True,
            )
        )
        if not lane_raw_findings:
            lane_raw_findings = list(
                findings_from_row(
                    row,
                    letter_id=letter.letter_id,
                    entity=entity,
                    note_text=letter.note_text,
                    source=producer.source_for_row(row, source_lane=source_lane),
                    raw_surface=True,
                    predicted_fallback=True,
                )
            )
        lane_raw = [finding.to_row() for finding in lane_raw_findings]
        predicted_mentions.extend(lane_scored)
        raw_mentions.extend(lane_raw)
        for surface, surface_rows in lane_surface_rows.items():
            prediction_surfaces[surface].extend(surface_rows)
        lane_blocks[entity] = {
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

    invalid = [
        mention
        for mention in predicted_mentions
        if not str(mention.get("evidence", ""))
        or str(mention.get("evidence", "")) not in letter.note_text
    ]
    if invalid:
        raise ValueError(
            f"assembled {letter.letter_id!r} with {len(invalid)} finding(s) "
            "without exact source evidence"
        )
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
            if annotation.entity in TARGET_ENTITIES
        ],
        "predicted_mentions": predicted_mentions,
        "raw_lane_mentions": raw_mentions,
        "prediction_surfaces": prediction_surfaces,
        "lanes": lane_blocks,
        "policy": {
            "diagnosis_policy_variant": config.diagnosis_policy_variant,
            "prescription_policy_variant": config.prescription_policy_variant,
            "sf_projection_ablation": config.sf_projection_ablation,
        },
    }


def _lane_prediction_surfaces(
    store: ClinicalFindingStore,
    *,
    entity: str,
    producer_id: str,
    final_findings: Sequence[Any],
) -> dict[str, list[Any]]:
    source_scored = list(store.findings(entity=entity, producer_id=producer_id, raw_surface=False))
    final = list(final_findings)
    return {
        "source_scored": source_scored,
        "evidence_valid": [finding for finding in source_scored if finding.evidence_valid],
        "protocol_model_preserving_canonical": [
            finding
            for finding in source_scored
            if finding.source.fact_origin == "target_model_generated"
        ],
        "dictionary_normalized": [
            finding
            for finding in final
            if not any(event.action.startswith("added_") for event in finding.provenance)
        ],
        "residual_benchmark_added": final,
    }


def _direct_sf_row(row: Mapping[str, Any]) -> dict[str, Any]:
    mentions = [
        _sf_mention(mention)
        for mention in row.get("predicted_mentions", [])
        if str(mention.get("entity")) == SEIZURE_FREQUENCY.name
    ]
    return {
        "letter_id": str(row["letter_id"]),
        "split": row.get("split", "operational"),
        "prompt_version": "structured_direct_no_sf_adjudicator_v01",
        "pipeline_family": "exectv2_structured_direct_no_sf_adjudicator",
        "model": row.get("model", ""),
        "mode": "no-call projection from structured extractor",
        "source_pipeline_family": row.get("pipeline_family", ""),
        "source_prompt_version": row.get("prompt_version", ""),
        "component_owner": "single_model_structured_no_sf_adjudicator",
        "call_error": None,
        "parse_errors": [],
        "gate_warnings": [],
        "predicted_mentions": mentions,
        "n_mentions_raw": len(mentions),
        "n_mentions_scored": len(mentions),
        "n_evidence_invalid": 0,
        "raw_output": json.dumps({"mentions": [_raw_mention(m) for m in mentions]}),
        "gold_mentions": [],
    }


def _sf_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    attributes = mention.get("attributes")
    return {
        "entity": SEIZURE_FREQUENCY.name,
        "text": str(mention.get("text", "")),
        "attributes": dict(attributes) if isinstance(attributes, Mapping) else {},
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
        "component_owner": "single_model_structured_no_sf_adjudicator",
    }


def _raw_mention(mention: Mapping[str, Any]) -> dict[str, Any]:
    raw = dict(mention)
    raw.pop("entity", None)
    return raw


def _gold_to_row(annotation: Any) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "attributes": dict(annotation.attributes),
    }


def _manifest_payload(
    structured_path: Path,
    sf_path: Path,
    *,
    row_count: int,
    config: StructuredMethodConfig,
) -> dict[str, Any]:
    return {
        "candidate_id": "exectv2_canonical_structured_one_call_v1",
        "pipeline_family": "exectv2_decision_0041_canonical_one_call",
        "ownership": "component_attributed_model_led_single_call",
        "split": "operational",
        "row_count": row_count,
        "claim_boundary": (
            "One-call model-led extraction with deterministic assembly; "
            "no implicit gold use."
        ),
        "baseline_producer": "structured_key_family_event_ledger",
        "producers": {
            "structured_key_family_event_ledger": {
                "kind": "saved_jsonl",
                "artifact": str(structured_path),
                "ownership_label": "named_model_structured_facts",
                "source_lane": "model_structured_key_families",
            },
            "sf_model_projection_suppression": {
                "kind": "saved_jsonl",
                "artifact": str(sf_path),
                "ownership_label": "named_model_sf_plus_projection_suppression",
                "source_lane": "model_sf_projection_suppression",
            },
        },
        "lenses": {
            "Diagnosis": {
                "producer": "structured_key_family_event_ledger",
                "lens": "diagnosis_heading_recovery_residual_benchmark_v05",
                "ownership_label": "named_model_structured_diagnosis_plus_rules",
                "portability": "benchmark_format",
            },
            "SeizureFrequency": {
                "producer": "sf_model_projection_suppression",
                "lens": "sf_state_projection_suppression_v01",
                "ownership_label": "named_model_sf_plus_projection_suppression",
                "portability": "seizure_frequency",
            },
            "Prescription": {
                "producer": "structured_key_family_event_ledger",
                "lens": "prescription_dictionary_v09",
                "ownership_label": "named_model_prescription_plus_shared_rules",
                "portability": "clinical_epilepsy",
            },
            "Investigations": {
                "producer": "structured_key_family_event_ledger",
                "lens": "investigations_result_v01",
                "ownership_label": "named_model_investigations",
                "portability": "clinical_epilepsy",
            },
        },
        "views": ["raw_candidate", "evidence_valid", "clinical_headline"],
        "diagnosis_policy_variant": config.diagnosis_policy_variant,
        "prescription_policy_variant": config.prescription_policy_variant,
    }
