"""Operational wrapper for the selected one-call ExECT LLM-with-rules pipeline."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig
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


def run_exect_notes(notes: Sequence[InputNote], runtime: RuntimeConfig) -> list[dict[str, Any]]:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured import (  # noqa: E501
        runner as structured_runner,
    )

    letters = [ExectLetter(note.note_id, note.text) for note in notes]
    rows, _ = structured_runner.run_split(
        letters,
        split="operational",
        model=runtime.model,
        temperature=runtime.temperature,
        max_tokens=runtime.max_tokens,
        mode="live",
        dspy_cache=False,
        api_base=runtime.base_url,
        api_key=runtime.api_key,
        timeout=int(runtime.timeout_seconds),
        prompt_profile="full",
    )
    failed = {
        str(row["letter_id"]): row
        for row in rows
        if row.get("call_error") or _blocking_parse_error(row.get("parse_errors", []))
    }
    usable_letters = [letter for letter in letters if letter.letter_id not in failed]
    usable_rows = [row for row in rows if str(row["letter_id"]) not in failed]
    assembled_by_id: dict[str, dict[str, Any]] = {}
    if usable_rows:
        assembled_by_id = _assemble(usable_letters, usable_rows)

    output: list[dict[str, Any]] = []
    for note in notes:
        if note.note_id in failed:
            row = failed[note.note_id]
            output.append(
                {
                    "id": note.note_id,
                    "task": "exect",
                    "status": "error",
                    "model": runtime.api_model,
                    "pipeline": "llm_with_rules_one_call",
                    "error": {
                        "type": "model_or_parse_failure",
                        "message": row.get("call_error") or "; ".join(row.get("parse_errors", [])),
                    },
                }
            )
            continue
        assembled = assembled_by_id[note.note_id]
        output.append(
            {
                "id": note.note_id,
                "task": "exect",
                "status": "ok",
                "model": runtime.api_model,
                "pipeline": "llm_with_rules_one_call",
                "prompt_version": usable_rows[0].get("prompt_version", ""),
                "prediction": {"mentions": assembled["predicted_mentions"]},
                "lanes": assembled["lanes"],
            }
        )
    return output


def _assemble(
    letters: Sequence[ExectLetter], structured_rows: Sequence[Mapping[str, Any]]
) -> dict[str, dict[str, Any]]:
    direct_rows = [_direct_sf_row(row) for row in structured_rows]
    projected_rows = [
        sf_state_projection.project_row(row, ablation="combined") for row in direct_rows
    ]
    suppressed_rows = [sf_unknown_suppression.suppress_row(row) for row in projected_rows]
    manifest = manifest_from_mapping(
        _manifest_payload(Path("structured.jsonl"), Path("sf.jsonl"), row_count=len(letters))
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
        letter.letter_id: _assemble_letter(
            letter,
            manifest=manifest,
            producers=producers,
            source_rows=source_rows,
        )
        for letter in letters
    }


def _assemble_letter(
    letter: ExectLetter,
    *,
    manifest: FindingAssemblyManifest,
    producers: Mapping[str, SavedJsonlProducer],
    source_rows: Mapping[str, Mapping[str, Mapping[str, Any]]],
) -> dict[str, Any]:
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
        source = producer.source_for_row(row, source_lane=source_lane)
        lens_result = lens_from_manifest(lens_config).reconcile(
            store,
            policy=LensPolicy(
                producer_id=lens_config.producer,
                source_lane=source_lane,
                ownership_label=lens_config.ownership_label or producer.ownership_label,
                portability=lens_config.portability,
                diagnosis_resolution_candidate=True,
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
                    source=source,
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
    return {
        "letter_id": letter.letter_id,
        "split": manifest.split,
        "stage": manifest.stage,
        "pipeline_family": manifest.pipeline_family,
        "candidate_name": manifest.candidate_id,
        "ownership": manifest.ownership,
        "gold_mentions": [],
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
    source_scored = list(
        store.findings(entity=entity, producer_id=producer_id, raw_surface=False)
    )
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
        "split": "operational",
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


def _manifest_payload(structured_path: Path, sf_path: Path, *, row_count: int) -> dict[str, Any]:
    return {
        "candidate_id": "exectv2_operational_single_call_v1",
        "pipeline_family": "exectv2_decision_0041_operational_single_call",
        "ownership": "component_attributed_model_led_single_call_live",
        "split": "operational",
        "row_count": row_count,
        "claim_boundary": "Operational inference; no benchmark or validation claim.",
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
    }


def _blocking_parse_error(errors: Sequence[Any]) -> bool:
    return any(
        str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
        for error in errors
    )
