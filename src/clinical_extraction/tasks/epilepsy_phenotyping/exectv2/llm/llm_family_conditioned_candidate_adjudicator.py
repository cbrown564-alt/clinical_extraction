"""Candidate-backed family-conditioned adjudicator for ExECTv2 key families.

This is the next iteration after the direct-from-letter event ledger failed its
dev25 gate. It keeps one shared Gan-style event schema and one adjudication
prompt, but it gives the model family-specific candidate bundles produced by
the stronger upstream components.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_family_conditioned_event_ledger as direct,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    _extract_json_object,
    check_evidence,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_hybrid_family_conditioned_candidate_adjudicator_v0.4"
PIPELINE_FAMILY = "exectv2_hybrid_family_conditioned_candidate_adjudicator"
COMPONENT_OWNER = "hybrid_family_conditioned_candidate_adjudicator"

Mode = Literal["live", "live-actions", "prompt-only", "candidate-passthrough"]


class ExECTv2FamilyConditionedCandidateAdjudicatorSignature(dspy.Signature):
    """Adjudicate target-family candidates into source-near clinical events.

    Return exactly one JSON object with a 'clinical_events' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one letter, one target family, and candidate bundles."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"clinical_events\": [{\"family\": ..., "
            "\"anchor_text\": ..., \"evidence\": ..., \"event_state\": {...}, "
            "\"mentions\": [{\"entity\": ..., \"text\": ..., \"attributes\": {...}}], "
            "\"confidence\": ..., \"rationale\": ...}, ...]}"
        )
    )


class DspyFamilyConditionedCandidateAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2FamilyConditionedCandidateAdjudicatorSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


class ExECTv2FamilyConditionedCandidateActionSignature(dspy.Signature):
    """Audit target-family candidate IDs.

    Return exactly one JSON object with a 'candidate_actions' list. No markdown.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one letter, one target family, and candidate IDs."
    )
    candidate_actions_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"candidate_actions\": [{\"candidate_id\": ..., "
            "\"action\": \"keep\"|\"reject\", \"reason_code\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyFamilyConditionedCandidateActionAdjudicator(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2FamilyConditionedCandidateActionSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def read_candidate_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None:
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def rows_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    by_letter: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_letter.setdefault(str(row.get("letter_id", "")), []).append(row)
    return by_letter


def build_candidate_bundle(
    letter: ExectLetter,
    target_family: str,
    candidate_sources: Mapping[str, Sequence[Mapping[str, Any]]],
) -> dict[str, Any]:
    profile = direct.family_profile(target_family)
    candidate_mentions: list[dict[str, Any]] = []
    auxiliary: list[dict[str, Any]] = []
    seen: set[tuple[str, str, tuple[tuple[str, str], ...], str]] = set()

    for source_name, rows in candidate_sources.items():
        for row in rows:
            if str(row.get("letter_id")) != letter.letter_id:
                continue
            source_meta = {
                "source": source_name,
                "source_prompt_version": row.get("prompt_version", ""),
                "source_pipeline_family": row.get("pipeline_family", ""),
                "source_mode": row.get("mode", ""),
            }
            for index, mention in enumerate(row.get("predicted_mentions") or []):
                if str(mention.get("entity")) != profile.entity:
                    continue
                candidate = _candidate_mention(
                    mention,
                    candidate_id=f"{source_name}:M{len(candidate_mentions)}",
                    source_meta=source_meta,
                    row_index=index,
                )
                key = _candidate_key(candidate)
                if key in seen:
                    continue
                seen.add(key)
                candidate_mentions.append(candidate)
            auxiliary.extend(_auxiliary_candidates(row, source_meta))

    return {
        "candidate_mentions": candidate_mentions,
        "candidate_evidence_ledger": _target_ledger(letter, profile.event_family),
        "auxiliary_candidates": auxiliary[:48],
        "candidate_policy": _candidate_policy(profile.entity),
    }


def build_prompt_input(
    letter: ExectLetter,
    target_family: str,
    candidate_sources: Mapping[str, Sequence[Mapping[str, Any]]],
) -> str:
    profile = direct.family_profile(target_family)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Convert the target-family candidate mentions into source-near clinical "
            "events for one clinical letter. Candidate mentions are already the "
            "prediction-bearing proposals. Copy each candidate mention's text, "
            "evidence, attributes, confidence, and rationale exactly unless its "
            "evidence is not an exact substring of the letter."
        ),
        "architecture": {
            "name": "single candidate-backed family-conditioned event adjudicator",
            "inspiration": (
                "Gan structured-events discipline: candidate facts, source-near "
                "event state, typed decision lanes, exact evidence, final renderings."
            ),
            "component_ownership": (
                "Upstream components propose candidate clinical facts. The model "
                "owns target-family event packaging and only minimal evidence "
                "rejection. Validation later checks evidence and schema."
            ),
        },
        "target_family": profile.entity,
        "target_event_family": profile.event_family,
        "family_profile": profile.as_prompt_payload(),
        "candidate_bundle": build_candidate_bundle(letter, profile.entity, candidate_sources),
        "decision_procedure": _decision_procedure(profile.entity),
        "event_lane_guide": {
            profile.event_family: structured._event_lane_guide()[profile.event_family],
        },
        "output_schema": direct._output_schema(profile),
        "attribute_vocabulary": {profile.entity: direct._attribute_vocabulary(profile.entity)},
        "clinical_rules": _clinical_rules(profile.entity),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def build_action_prompt_input(
    letter: ExectLetter,
    target_family: str,
    candidate_sources: Mapping[str, Sequence[Mapping[str, Any]]],
) -> str:
    profile = direct.family_profile(target_family)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Audit target-family candidate IDs for one clinical letter. Candidate "
            "mentions are already the prediction-bearing facts. Return candidate "
            "actions only; do not rewrite mention text, evidence, or attributes."
        ),
        "architecture": {
            "name": "single candidate-ID family-conditioned action adjudicator",
            "inspiration": (
                "Gan structured-events discipline: source-near candidate facts, "
                "typed keep/reject actions, exact evidence, deterministic copy-through."
            ),
            "component_ownership": (
                "Upstream components propose candidate clinical facts. The model "
                "may flag verifiable rejects by candidate_id only. Deterministic "
                "code copies kept candidate mentions verbatim."
            ),
        },
        "target_family": profile.entity,
        "target_event_family": profile.event_family,
        "family_profile": profile.as_prompt_payload(),
        "candidate_bundle": build_candidate_bundle(letter, profile.entity, candidate_sources),
        "output_schema": {
            "candidate_actions": [
                {
                    "candidate_id": "candidate_bundle.candidate_mentions[].candidate_id",
                    "action": "keep | reject",
                    "reason_code": (
                        "supported | evidence_not_substring | wrong_entity | duplicate_context"
                    ),
                    "rationale": "One short sentence. Do not include rewritten mention content.",
                }
            ]
        },
        "decision_procedure": _action_decision_procedure(profile.entity),
        "clinical_rules": _action_clinical_rules(profile.entity),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def candidate_mentions_as_flat_mentions(
    candidate_bundle: Mapping[str, Any],
    *,
    target_family: str,
) -> list[structured.MentionForEvidence]:
    profile = direct.family_profile(target_family)
    mentions: list[structured.MentionForEvidence] = []
    for candidate in candidate_bundle.get("candidate_mentions") or []:
        mentions.append(
            structured.MentionForEvidence(
                entity=profile.entity,
                text=str(candidate.get("text", "")),
                evidence=str(candidate.get("evidence", "")),
                attributes={
                    str(k): str(v)
                    for k, v in dict(candidate.get("attributes") or {}).items()
                    if v is not None
                },
                confidence=str(candidate.get("confidence") or "medium"),  # type: ignore[arg-type]
                rationale=str(candidate.get("rationale", "")),
            )
        )
    return mentions


def parse_candidate_events_json(
    raw_output: str,
) -> tuple[structured.StructuredExtractionRecord | None, list[str]]:
    record, errors = structured.parse_structured_events_json(raw_output)
    if record is not None:
        return record, errors

    try:
        extracted = _extract_json_object(raw_output)
        payload, end_index = json.JSONDecoder().raw_decode(extracted)
    except Exception:
        return None, errors

    suffix = extracted[end_index:].strip()
    if not suffix or any(char not in "]}" for char in suffix):
        return None, errors

    payload, coerce_notes = structured._coerce_structured_payload(payload)
    try:
        repaired = structured.StructuredExtractionRecord.model_validate(payload)
    except Exception:
        return None, errors
    return repaired, [*coerce_notes, f"ignored_trailing_json_brackets: {suffix!r}"]


def parse_candidate_actions_json(raw_output: str) -> tuple[list[dict[str, str]], list[str]]:
    try:
        payload = json.loads(_extract_json_object(raw_output))
    except json.JSONDecodeError as exc:
        return [], [f"invalid_json: {exc.msg}"]
    if not isinstance(payload, dict):
        return [], ["schema_validation_error: top-level value is not an object"]
    actions = payload.get("candidate_actions")
    if not isinstance(actions, list):
        return [], ["schema_validation_error: missing candidate_actions list"]

    parsed: list[dict[str, str]] = []
    notes: list[str] = []
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            notes.append(f"dropped_non_object_action: {index}")
            continue
        candidate_id = str(action.get("candidate_id") or "").strip()
        action_value = str(action.get("action") or "").strip().lower()
        if not candidate_id or action_value not in {"keep", "reject"}:
            notes.append(f"dropped_invalid_action: {index}")
            continue
        parsed.append(
            {
                "candidate_id": candidate_id,
                "action": action_value,
                "reason_code": str(action.get("reason_code") or "").strip(),
                "rationale": str(action.get("rationale") or "").strip(),
            }
        )
    return parsed, notes


def apply_candidate_actions(
    candidate_bundle: Mapping[str, Any],
    actions: Sequence[Mapping[str, str]],
    *,
    target_family: str,
    note_text: str,
) -> tuple[list[structured.MentionForEvidence], list[str]]:
    profile = direct.family_profile(target_family)
    action_by_id = {
        str(action.get("candidate_id")): {
            "action": str(action.get("action", "")).lower(),
            "reason_code": str(action.get("reason_code", "")),
            "rationale": str(action.get("rationale", "")),
        }
        for action in actions
    }
    warnings: list[str] = []
    mentions: list[structured.MentionForEvidence] = []
    for candidate in candidate_bundle.get("candidate_mentions") or []:
        candidate_id = str(candidate.get("candidate_id", ""))
        action = action_by_id.get(candidate_id, {"action": "keep", "reason_code": "missing"})
        if _honor_reject(candidate, action, profile.entity, note_text):
            warnings.append(
                f"honored_reject: {candidate_id}: {action.get('reason_code', '')}"
            )
            continue
        if action.get("action") == "reject":
            warnings.append(
                f"ignored_unverified_reject: {candidate_id}: {action.get('reason_code', '')}"
            )
        mentions.append(_candidate_as_flat_mention(candidate, profile.entity))
    return mentions, warnings


def _candidate_as_flat_mention(
    candidate: Mapping[str, Any],
    target_entity: str,
) -> structured.MentionForEvidence:
    return structured.MentionForEvidence(
        entity=target_entity,
        text=str(candidate.get("text", "")),
        evidence=str(candidate.get("evidence", "")),
        attributes={
            str(k): str(v)
            for k, v in dict(candidate.get("attributes") or {}).items()
            if v is not None
        },
        confidence=str(candidate.get("confidence") or "medium"),  # type: ignore[arg-type]
        rationale=str(candidate.get("rationale", "")),
    )


def _honor_reject(
    candidate: Mapping[str, Any],
    action: Mapping[str, str],
    target_entity: str,
    note_text: str,
) -> bool:
    if action.get("action") != "reject":
        return False
    reason_code = str(action.get("reason_code", "")).lower()
    if str(candidate.get("entity", "")) != target_entity:
        return True
    if reason_code == "wrong_entity":
        return str(candidate.get("entity", "")) != target_entity
    if reason_code == "evidence_not_substring":
        return str(candidate.get("evidence", "")) not in note_text
    return False


def to_predicted_letter(
    letter_id: str,
    mentions: Sequence[structured.MentionForEvidence],
    *,
    note_text: str,
    target_family: str,
) -> tuple[PredictedLetter, list[str]]:
    profile = direct.family_profile(target_family)
    warnings: list[str] = []
    target_mentions = [mention for mention in mentions if mention.entity == profile.entity]
    evidence_valid, evidence_invalid, evidence_warnings = check_evidence(
        target_mentions,
        note_text=note_text,
    )
    warnings.extend(evidence_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        spec = direct.ENTITY_REGISTRY[profile.entity]
        attrs = {str(k): str(v) for k, v in dict(mention.attributes).items()}
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        warnings.extend(f"{profile.entity}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=profile.entity,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    pred = PredictedLetter(
        letter_id=letter_id,
        mentions=tuple(predicted_mentions),
        diagnostics={
            "prompt_version": PROMPT_VERSION,
            "pipeline_family": PIPELINE_FAMILY,
            "target_family": profile.entity,
            "n_evidence_invalid": len(evidence_invalid),
            "attribute_warnings": warnings,
        },
    )
    return project_cuis(pred), warnings


def run_split(
    letters: Sequence[ExectLetter],
    *,
    target_family: str,
    candidate_sources: Mapping[str, Sequence[Mapping[str, Any]]],
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Mode,
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    profile = direct.family_profile(target_family)
    program = DspyFamilyConditionedCandidateAdjudicator()
    action_program = DspyFamilyConditionedCandidateActionAdjudicator()
    if mode in {"live", "live-actions"}:
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None,
        key="letter_id",
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        candidate_bundle = build_candidate_bundle(letter, profile.entity, candidate_sources)
        prompt_input_json = (
            build_action_prompt_input(letter, profile.entity, candidate_sources)
            if mode == "live-actions"
            else build_prompt_input(letter, profile.entity, candidate_sources)
        )
        raw_output = ""
        call_error: str | None = None
        record = None
        candidate_actions: list[dict[str, str]] = []
        action_warnings: list[str] = []
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"
        elif mode == "live-actions":
            try:
                prediction = action_program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.candidate_actions_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        if mode == "candidate-passthrough":
            parse_errors = ["candidate_passthrough"]
            mentions = candidate_mentions_as_flat_mentions(
                candidate_bundle,
                target_family=profile.entity,
            )
        elif mode == "live-actions" and raw_output:
            candidate_actions, parse_errors = parse_candidate_actions_json(raw_output)
            mentions, action_warnings = apply_candidate_actions(
                candidate_bundle,
                candidate_actions,
                target_family=profile.entity,
                note_text=letter.note_text,
            )
        elif mode == "live-actions":
            parse_errors = ["not_run"]
            mentions, action_warnings = apply_candidate_actions(
                candidate_bundle,
                [],
                target_family=profile.entity,
                note_text=letter.note_text,
            )
        elif raw_output:
            record, parse_errors = parse_candidate_events_json(raw_output)
            mentions = structured.flatten_events(record) if record else []
        else:
            parse_errors = ["not_run"]
            mentions = []

        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
            target_family=profile.entity,
        )
        gate_warnings = [*action_warnings, *gate_warnings]

        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "target_family": profile.entity,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "candidate_actions": candidate_actions,
                "candidate_bundle": candidate_bundle,
                "n_candidate_mentions": len(candidate_bundle["candidate_mentions"]),
                "n_events_raw": len(record.clinical_events) if record else 0,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "structured_events": [
                    event.model_dump() for event in (record.clinical_events if record else [])
                ],
                "predicted_mentions": [
                    direct._mention_to_row(m) for m in predicted_letter.mentions
                ],
                "gold_mentions": [
                    {"entity": a.entity, "text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(profile.entity)
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
                target_family=profile.entity,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "target_family": profile.entity,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows, target_family=profile.entity)
    return rows, metadata


def summarize_rows(
    rows: Sequence[dict[str, Any]],
    *,
    target_family: str | None = None,
) -> dict[str, Any]:
    return direct.summarize_rows(rows, target_family=target_family)


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    direct.write_report(rows, metadata, path, jsonl_path=jsonl_path)


def _candidate_mention(
    mention: Mapping[str, Any],
    *,
    candidate_id: str,
    source_meta: Mapping[str, Any],
    row_index: int,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "row_index": row_index,
        **source_meta,
        "entity": str(mention.get("entity", "")),
        "text": str(mention.get("text", "")),
        "attributes": dict(mention.get("attributes") or {}),
        "evidence": str(mention.get("evidence", "")),
        "confidence": str(mention.get("confidence") or "medium"),
        "rationale": str(mention.get("rationale", "")),
    }


def _candidate_key(
    candidate: Mapping[str, Any],
) -> tuple[str, str, tuple[tuple[str, str], ...], str]:
    attrs = tuple(
        sorted((str(k), str(v)) for k, v in dict(candidate.get("attributes") or {}).items())
    )
    return (
        str(candidate.get("entity", "")),
        str(candidate.get("text", "")).lower(),
        attrs,
        str(candidate.get("evidence", "")).lower(),
    )


def _auxiliary_candidates(
    row: Mapping[str, Any],
    source_meta: Mapping[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key in (
        "candidate_spans",
        "candidate_concept_groups",
        "diagnosis_spans",
        "verifier_mentions",
        "decomposer_mentions",
        "draft_mentions",
    ):
        value = row.get(key)
        if value:
            out.append({"kind": key, **source_meta, "items": value})
    return out


def _target_ledger(letter: ExectLetter, event_family: str) -> list[dict[str, Any]]:
    return [
        row
        for row in structured.candidate_evidence_ledger_for_letter(letter)
        if row.get("family") == event_family
    ]


def _candidate_policy(entity: str) -> list[str]:
    return [
        "Candidate mentions are prediction-bearing proposals from upstream components.",
        "Default action is keep and copy unchanged.",
        (
            "When keeping a candidate, copy its text, evidence, attributes, "
            "confidence, and rationale exactly into the final mention."
        ),
        "Do not add new mentions from the letter or auxiliary candidates.",
        "Do not rewrite candidate mention text to a longer or shorter span.",
        (
            "Do not remove duplicate-looking candidates; repeated candidates may "
            "represent repeated gold mentions."
        ),
        (
            "Reject only when the candidate evidence is not an exact substring of "
            "the letter or the candidate entity is not the target family."
        ),
        f"Return only {entity} mentions.",
    ]


def _decision_procedure(entity: str) -> list[str]:
    return [
        "Read candidate_bundle.candidate_mentions first.",
        "For each candidate mention, create exactly one clinical_event unless evidence is absent.",
        "For kept candidates, copy the candidate mention unchanged.",
        "Use auxiliary candidates and ledger rows only as context, not as new mention sources.",
        "Represent every kept fact as a source-near clinical_event, then render final mentions.",
        f"Before returning, remove any mention whose entity is not {entity}.",
    ]


def _action_decision_procedure(entity: str) -> list[str]:
    return [
        "Read candidate_bundle.candidate_mentions.",
        "For each candidate_id, decide keep unless the evidence is absent or entity is wrong.",
        "Return only candidate_id actions; never return rewritten mention text.",
        "Do not add candidate IDs that are not present in candidate_bundle.candidate_mentions.",
        f"Before returning, ensure every action refers to a {entity} candidate.",
    ]


def _clinical_rules(entity: str) -> list[str]:
    profile = direct.family_profile(entity)
    return [
        "Candidate bundle rows are proposals to transcribe into events.",
        "Every final evidence value must be an exact substring of the letter.",
        "Every final mention text must be supported by its evidence.",
        "Do not emit CUI or CUIPhrase unless it came from a candidate mention.",
        "If no target-family finding is supported, return {\"clinical_events\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ] + profile.attribute_policy + profile.lane_policy


def _action_clinical_rules(entity: str) -> list[str]:
    return [
        "Candidate mentions are already prediction-bearing proposals.",
        "Default to keep when the evidence is present in the letter.",
        "Reject only for evidence_not_substring or wrong_entity.",
        "Do not reject because a candidate seems duplicated or clinically broad.",
        "Do not emit mention text, attributes, evidence, clinical_events, or markdown.",
        f"Return actions only for {entity} candidate IDs.",
    ]


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
    target_family: str,
) -> None:
    summary = summarize_rows(rows, target_family=target_family)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "target_family": target_family,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
            },
            _checkpoint_report_path(report_path),
            jsonl_path=jsonl_path,
        )
    progress = {
        "processed": len(rows),
        "total": total,
        "target_family": target_family,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)


def _checkpoint_report_path(path: Path) -> Path:
    if path.stem.endswith("_checkpoint"):
        return path
    return path.with_name(f"{path.stem}_checkpoint{path.suffix}")
