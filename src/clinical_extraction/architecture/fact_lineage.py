"""Fact-keyed lineage for Assembly Line teaching runs.

A fact is one attributable predicted unit: a Gan candidate event, a Gan
one-call label plus its quoted span, or one ExECT predicted mention.
Stages that cannot be tied to that unit are omitted, not copied as idle
rows onto every fact.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal

from clinical_extraction.core.evidence import locate_evidence
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)

Band = Literal["propose", "reshape", "gate", "leave"]

_NO_SPAN_KINDS = frozenset({"no_reference", "unknown_frequency"})
_NO_SPAN_LABELS = frozenset(
    {
        "no seizure frequency reference",
        "unknown",
        "(no scorable label)",
    }
)
_FOUR_FAMILIES = frozenset(
    {"Diagnosis", "SeizureFrequency", "Prescription", "Investigations"}
)
_LENS_FOR_ENTITY = {
    "Diagnosis": "lens.diagnosis",
    "SeizureFrequency": "lens.seizure_frequency",
    "Prescription": "lens.prescription",
    "Investigations": "lens.investigations",
}
_ENTITY_FOR_FAMILY = {
    "diagnosis": "Diagnosis",
    "medication": "Prescription",
    "seizure_frequency": "SeizureFrequency",
    "investigation": "Investigations",
}


@dataclass(frozen=True)
class FactSpan:
    start: int
    end: int
    text: str

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "text": self.text}


@dataclass(frozen=True)
class FactGold:
    label: str
    has_counterpart: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "has_counterpart": self.has_counterpart,
            "note": self.note,
        }


@dataclass(frozen=True)
class FactTransform:
    stage_id: str
    stage_name: str
    band: Band
    entered: str
    left: str
    idle: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_name": self.stage_name,
            "band": self.band,
            "entered": self.entered,
            "left": self.left,
            "idle": self.idle,
            "note": self.note,
        }


@dataclass(frozen=True)
class PredictedFact:
    fact_id: str
    label: str
    span: FactSpan | None
    transforms: tuple[FactTransform, ...]
    gold: FactGold

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_id": self.fact_id,
            "label": self.label,
            "span": None if self.span is None else self.span.to_dict(),
            "transforms": [step.to_dict() for step in self.transforms],
            "gold": self.gold.to_dict(),
        }


@dataclass(frozen=True)
class GoldUnit:
    label: str
    has_counterpart: bool
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "has_counterpart": self.has_counterpart,
            "note": self.note,
        }


def empty_gold_unit(label: str, note: str = "") -> GoldUnit:
    return GoldUnit(label=label, has_counterpart=False, note=note)


def letter_gold_unit(label: str, *, has_facts: bool, note: str = "") -> GoldUnit:
    return GoldUnit(label=label, has_counterpart=has_facts, note=note)


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        return dumped if isinstance(dumped, Mapping) else None
    return None


def _as_items(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        try:
            parsed: Any = json.loads(text)
        except json.JSONDecodeError:
            return [text]
        return _as_items(parsed)
    if isinstance(value, Mapping):
        for key in ("clinical_events", "clinical_facts", "events", "mentions"):
            nested = value.get(key)
            if isinstance(nested, Sequence) and not isinstance(nested, str | bytes):
                return list(nested)
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return list(value)
    return [value]


_KEEP_FIELDS = (
    "entity",
    "text",
    "evidence",
    "attributes",
    "family",
    "anchor_text",
    "fact",
    "mentions",
    "confidence",
    "rationale",
    "event_id",
    "raw_value",
    "normalized_label",
)


def _public_fields(data: Mapping[str, Any]) -> dict[str, Any]:
    cleaned: dict[str, Any] = {}
    for key in _KEEP_FIELDS:
        if key not in data:
            continue
        item = data[key]
        if item is None or item == "" or item == [] or item == {}:
            continue
        if key == "attributes" and isinstance(item, Mapping):
            attributes = {
                str(name): str(value)
                for name, value in item.items()
                if value not in {None, ""}
            }
            if attributes:
                cleaned[key] = attributes
        elif key == "mentions" and isinstance(item, Sequence):
            mentions = [
                _public_fields(mapped)
                for mapped in (_as_mapping(mention) for mention in item)
                if mapped is not None
            ]
            if mentions:
                cleaned[key] = mentions
        else:
            cleaned[key] = item
    return cleaned


def _render_unit(value: Any) -> str:
    if value is None:
        return "(none)"
    if isinstance(value, str):
        return value
    data = _as_mapping(value)
    if data is None:
        return str(value)
    cleaned = _public_fields(data)
    if not cleaned:
        return str(value)
    return json.dumps(cleaned, indent=2, sort_keys=True, default=str)


def _locate_span(note_text: str, *candidates: str) -> FactSpan | None:
    for quote in candidates:
        quote = (quote or "").strip()
        if not quote:
            continue
        located = locate_evidence(note_text, quote)
        if located is None:
            continue
        start, end = located
        return FactSpan(start=start, end=end, text=note_text[start:end])
    return None


def _band_for(stage_id: str) -> Band:
    tail = stage_id.rsplit(".", 1)[-1]
    if tail in {"extract", "extract_entities", "model_call", "build_prompt"}:
        return "propose"
    if "evidence" in tail or tail.endswith("_containment") or tail.endswith("_check"):
        if "repair" in stage_id:
            return "reshape"
        if tail == "scorable_label_check":
            return "gate"
        return "gate"
    if tail in {"score"} or "materialize" in tail:
        return "leave"
    return "reshape"


def _stage_name(run: Any, stage_id: str, fallback: str) -> str:
    for observation in getattr(run, "observations", ()):
        if observation.stage_id == stage_id:
            return observation.stage_name
    if hasattr(run, "manifest"):
        try:
            return run.manifest.stage(stage_id).name
        except (KeyError, AttributeError):
            pass
    return fallback


def _transform(
    run: Any,
    stage_id: str,
    *,
    entered: str,
    left: str,
    idle: bool,
    note: str = "",
    fallback_name: str = "",
) -> FactTransform:
    return FactTransform(
        stage_id=stage_id,
        stage_name=_stage_name(run, stage_id, fallback_name or stage_id),
        band=_band_for(stage_id),
        entered=entered,
        left=left,
        idle=idle,
        note=note,
    )


def _mention_parts(mention: Any) -> dict[str, str]:
    data = _as_mapping(mention) or {}
    attributes = data.get("attributes") or {}
    if not isinstance(attributes, Mapping):
        attributes = {}
    return {
        "entity": str(data.get("entity") or ""),
        "text": str(data.get("text") or ""),
        "evidence": str(data.get("evidence") or ""),
        "cui": str(attributes.get("CUI") or ""),
        "cui_phrase": str(attributes.get("CUIPhrase") or data.get("text") or ""),
    }


def _entity_of(value: Any) -> str:
    parts = _mention_parts(value)
    if parts["entity"]:
        return parts["entity"]
    data = _as_mapping(value) or {}
    family = str(data.get("family") or "")
    return _ENTITY_FOR_FAMILY.get(family, "")


def _same_mention(left: Any, right: Any) -> bool:
    first = _mention_parts(left)
    second = _mention_parts(right)
    left_data = _as_mapping(left) or {}
    left_entity = _entity_of(left)
    right_entity = _entity_of(right)
    if left_entity and right_entity and left_entity != right_entity:
        return False
    left_evidence = first["evidence"] or str(left_data.get("evidence") or "")
    if (
        left_evidence
        and second["evidence"]
        and normalize_phrase(left_evidence) == normalize_phrase(second["evidence"])
    ):
        return True
    if left_data.get("mentions"):
        return any(_same_mention(item, right) for item in _as_items(left_data.get("mentions")))
    if first["evidence"] and second["evidence"] and first["evidence"] == second["evidence"]:
        return True
    left_anchor = str(left_data.get("anchor_text") or "")
    if left_anchor and second["text"] and normalize_phrase(left_anchor) == normalize_phrase(
        second["text"]
    ):
        return True
    if first["cui"] and first["cui"] == second["cui"]:
        return True
    return bool(
        first["text"]
        and second["text"]
        and normalize_phrase(first["text"]) == normalize_phrase(second["text"])
    )


def _find_item(items: Sequence[Any], target: Any) -> Any | None:
    for item in items:
        if _same_mention(item, target):
            return item
    return None


def _exect_gold_for(letter: Any, mention: Any) -> FactGold:
    parts = _mention_parts(mention)
    entity = parts["entity"]
    predicted_phrase = normalize_phrase(parts["cui_phrase"] or parts["text"])
    for annotation in getattr(letter, "annotations", ()):
        if annotation.entity != entity:
            continue
        gold_phrase = normalize_phrase(annotation.text)
        gold_cui = str((annotation.attributes or {}).get("CUI") or "")
        if (parts["cui"] and gold_cui == parts["cui"]) or gold_phrase == predicted_phrase:
            return FactGold(label=annotation.text, has_counterpart=True)
    return FactGold(label="no gold counterpart", has_counterpart=False)


def _exect_fact_id(mention: Any, index: int) -> str:
    parts = _mention_parts(mention)
    key = normalize_phrase(parts["evidence"] or parts["text"] or str(index))
    return f"{parts['entity']}:{key}:{index}"


def build_exect_facts(
    letter: Any,
    mentions: Sequence[Any],
    stage_events: Sequence[Any],
    run: Any,
    *,
    gold_label: str,
) -> list[PredictedFact]:
    facts: list[PredictedFact] = []
    indexed = [
        mention
        for mention in mentions
        if _mention_parts(mention)["entity"] in _FOUR_FAMILIES
    ]
    for index, mention in enumerate(indexed):
        parts = _mention_parts(mention)
        transforms: list[FactTransform] = []
        for event in stage_events:
            stage_id = event.stage_id
            if stage_id.endswith(".score") or "materialize" in stage_id:
                continue
            if "build_prompt" in stage_id:
                continue
            lens_tail = _LENS_FOR_ENTITY.get(parts["entity"])
            if ".lens." in stage_id:
                if lens_tail is None or not stage_id.endswith(lens_tail):
                    continue
                incoming = _find_item(_as_items(event.input_value), mention)
                outgoing = _find_item(_as_items(event.output_value), mention)
                if incoming is None and outgoing is None:
                    incoming = _find_item(_as_items(event.input_value), parts)
                    outgoing = _find_item(_as_items(event.output_value), parts)
                if incoming is None and outgoing is None:
                    continue
                entered = _render_unit(incoming) if incoming is not None else _render_unit(mention)
                left = _render_unit(outgoing) if outgoing is not None else entered
                note = ""
                if hasattr(run, "observations"):
                    for observation in run.observations:
                        if observation.stage_id == stage_id:
                            note = observation.note
                            break
                transforms.append(
                    _transform(
                        run,
                        stage_id,
                        entered=entered,
                        left=left,
                        idle=entered == left,
                        note=note,
                    )
                )
                continue
            if stage_id.endswith("sf_state_projection") or stage_id.endswith(
                "sf_unknown_suppression"
            ):
                if parts["entity"] != "SeizureFrequency":
                    continue
            incoming_items = _as_items(event.input_value)
            outgoing_items = _as_items(event.output_value)
            incoming = _find_item(incoming_items, mention)
            outgoing = _find_item(outgoing_items, mention)
            if incoming is None and outgoing is None:
                if stage_id.endswith("model_call"):
                    proposed = _find_item(_as_items(event.output_value), mention)
                    if proposed is None:
                        continue
                    transforms.append(
                        _transform(
                            run,
                            stage_id,
                            entered="(none)",
                            left=_render_unit(proposed),
                            idle=False,
                        )
                    )
                elif stage_id.endswith("extract_entities") or stage_id.endswith(
                    ".extract"
                ):
                    transforms.append(
                        _transform(
                            run,
                            stage_id,
                            entered="(letter)",
                            left=_render_unit(mention),
                            idle=False,
                            note="Rules proposed this mention.",
                        )
                    )
                elif "evidence" in stage_id.rsplit(".", 1)[-1]:
                    evidence = parts["evidence"] or parts["text"]
                    transforms.append(
                        _transform(
                            run,
                            stage_id,
                            entered=evidence,
                            left="evidence accepted"
                            if evidence
                            else "no evidence quote",
                            idle=True,
                        )
                    )
                continue
            entered = _render_unit(incoming) if incoming is not None else "(none)"
            left = _render_unit(outgoing) if outgoing is not None else entered
            transforms.append(
                _transform(
                    run,
                    stage_id,
                    entered=entered,
                    left=left,
                    idle=entered == left,
                )
            )
        leave_label = _render_unit(mention)
        transforms.append(
            _transform(
                run,
                next(
                    (
                        event.stage_id
                        for event in stage_events
                        if event.stage_id.endswith(".score")
                    ),
                    "score",
                ),
                entered=leave_label,
                left=leave_label,
                idle=True,
                note="What left the line.",
                fallback_name="What left the line",
            )
        )
        facts.append(
            PredictedFact(
                fact_id=_exect_fact_id(mention, index),
                label=parts["text"] or leave_label,
                span=_locate_span(
                    letter.note_text,
                    parts["evidence"],
                    parts["text"],
                ),
                transforms=tuple(transforms),
                gold=_exect_gold_for(letter, mention),
            )
        )
    _ = gold_label
    return facts


def _event_mapping(event: Any) -> dict[str, Any]:
    data = _as_mapping(event) or {}
    return {
        "event_id": str(data.get("event_id") or data.get("candidate_id") or ""),
        "raw_value": str(data.get("raw_value") or data.get("source_phrase") or ""),
        "normalized_label": str(data.get("normalized_label") or ""),
        "evidence": str(data.get("evidence") or ""),
        "kind": str(data.get("kind") or ""),
        "label": str(data.get("label") or data.get("normalized_label") or ""),
    }


def _clickable_span(note_text: str, event: Mapping[str, Any]) -> FactSpan | None:
    kind = event.get("kind") or ""
    label = (event.get("normalized_label") or event.get("label") or "").strip().lower()
    if kind in _NO_SPAN_KINDS or label in _NO_SPAN_LABELS:
        return None
    return _locate_span(
        note_text,
        str(event.get("evidence") or ""),
        str(event.get("raw_value") or ""),
    )


def build_gan_rules_facts(
    note_text: str,
    candidates: Sequence[Any],
    normalized: Sequence[Any],
    selection: Mapping[str, Any],
    final_label: str | None,
    run: Any,
    *,
    gold_label: str,
) -> list[PredictedFact]:
    selected_ids = {str(item) for item in selection.get("selected_event_ids") or []}
    facts: list[PredictedFact] = []
    normalized_by_id = {
        _event_mapping(event)["event_id"]: _event_mapping(event) for event in normalized
    }
    for event in candidates:
        parts = _event_mapping(event)
        event_id = parts["event_id"] or f"event_{len(facts) + 1}"
        norm = normalized_by_id.get(event_id, {})
        selected = event_id in selected_ids or (
            not selected_ids and final_label == (norm.get("normalized_label") or parts["label"])
        )
        transforms = [
            _transform(
                run,
                "gan.rules.extract",
                entered="(letter)",
                left=f"{event_id}: {parts['raw_value'] or parts['evidence']}",
                idle=False,
            ),
            _transform(
                run,
                "gan.rules.normalize",
                entered=f"{event_id}: {parts['raw_value'] or parts['evidence']}",
                left=f"{event_id}: {norm.get('normalized_label') or parts['label']}",
                idle=False,
            ),
        ]
        if selected:
            transforms.append(
                _transform(
                    run,
                    "gan.rules.select_and_render",
                    entered=f"{event_id}: {norm.get('normalized_label') or parts['label']}",
                    left=str(final_label or selection.get("final_label") or ""),
                    idle=False,
                )
            )
            evidence = str(selection.get("evidence") or parts["evidence"])
            transforms.append(
                _transform(
                    run,
                    "gan.rules.evidence_trace_check",
                    entered=evidence,
                    left="evidence accepted",
                    idle=True,
                )
            )
            transforms.append(
                _transform(
                    run,
                    "gan.rules.score",
                    entered=str(final_label or ""),
                    left=str(final_label or ""),
                    idle=True,
                    note="What left the line.",
                )
            )
        facts.append(
            PredictedFact(
                fact_id=event_id,
                label=str(norm.get("normalized_label") or parts["label"] or event_id),
                span=_clickable_span(note_text, {**parts, **norm}),
                transforms=tuple(transforms),
                gold=FactGold(label=gold_label, has_counterpart=True),
            )
        )
    return facts


def build_gan_llm_facts(
    note_text: str,
    evidence: str,
    before_label: str,
    after_label: str,
    final_label: str | None,
    run: Any,
    *,
    gold_label: str,
    method_prefix: str,
) -> list[PredictedFact]:
    span = None
    if (final_label or "").strip().lower() not in _NO_SPAN_LABELS:
        span = _locate_span(note_text, evidence)
    if span is None:
        return []
    prefix = method_prefix
    transforms = [
        _transform(
            run,
            f"{prefix}.model_call",
            entered="(none)",
            left=f"{before_label} [{evidence}]",
            idle=False,
            note="One-call label plus its quoted span.",
        )
    ]
    if before_label != after_label:
        transforms.append(
            _transform(
                run,
                f"{prefix}.selected_evidence_repair",
                entered=before_label,
                left=after_label,
                idle=False,
            )
        )
    if evidence:
        transforms.append(
            _transform(
                run,
                f"{prefix}.evidence_containment",
                entered=evidence,
                left="evidence accepted",
                idle=True,
            )
        )
    transforms.append(
        _transform(
            run,
            f"{prefix}.score",
            entered=str(final_label or after_label),
            left=str(final_label or after_label),
            idle=True,
            note="What left the line.",
        )
    )
    return [
        PredictedFact(
            fact_id="one_call",
            label=str(final_label or after_label),
            span=span,
            transforms=tuple(transforms),
            gold=FactGold(label=gold_label, has_counterpart=True),
        )
    ]


def build_gan_hybrid_facts(
    note_text: str,
    events: Sequence[Any],
    normalized_events: Sequence[Any],
    selection: Mapping[str, Any],
    repair_walk: Sequence[tuple[str, str, str, str | None]],
    final_label: str | None,
    run: Any,
    *,
    gold_label: str,
) -> list[PredictedFact]:
    selected_ids = {str(item) for item in selection.get("selected_event_ids") or []}
    selection_evidence = str(selection.get("evidence") or "")
    normalized_by_id = {
        _event_mapping(event)["event_id"]: _event_mapping(event)
        for event in normalized_events
    }
    facts: list[PredictedFact] = []
    for event in events:
        parts = _event_mapping(event)
        event_id = parts["event_id"] or f"e{len(facts) + 1}"
        norm = normalized_by_id.get(event_id, {})
        selected = event_id in selected_ids
        transforms = [
            _transform(
                run,
                "gan.llm_with_rules.model_call",
                entered="(none)",
                left=f"{event_id}: {parts['raw_value'] or parts['evidence']}",
                idle=False,
                note="Model proposed this event.",
            ),
            _transform(
                run,
                "gan.llm_with_rules.normalize_events",
                entered=f"{event_id}: {parts['raw_value'] or parts['evidence']}",
                left=f"{event_id}: {norm.get('normalized_label') or parts['raw_value']}",
                idle=False,
            ),
        ]
        if selected:
            transforms.append(
                _transform(
                    run,
                    "gan.llm_with_rules.resolve_label",
                    entered=str(selection.get("model_final_label") or parts["raw_value"]),
                    left=str(selection.get("resolved_label") or ""),
                    idle=False,
                )
            )
            for family, before, after, _vetoed in repair_walk:
                if before == after:
                    continue
                transforms.append(
                    _transform(
                        run,
                        f"gan.llm_with_rules.repair.{family}",
                        entered=before,
                        left=after,
                        idle=False,
                    )
                )
            if selection_evidence and selection_evidence == parts["evidence"]:
                transforms.append(
                    _transform(
                        run,
                        "gan.llm_with_rules.evidence_containment",
                        entered=selection_evidence,
                        left="evidence accepted",
                        idle=True,
                    )
                )
            transforms.append(
                _transform(
                    run,
                    "gan.llm_with_rules.score",
                    entered=str(final_label or ""),
                    left=str(final_label or ""),
                    idle=True,
                    note="What left the line.",
                )
            )
        facts.append(
            PredictedFact(
                fact_id=event_id,
                label=str(norm.get("normalized_label") or parts["raw_value"] or event_id),
                span=_clickable_span(note_text, parts),
                transforms=tuple(transforms),
                gold=FactGold(label=gold_label, has_counterpart=True),
            )
        )
    return facts


def attach_run_gold(run: Any, gold_label: str, note: str = "") -> None:
    run.gold_unit = letter_gold_unit(
        gold_label,
        has_facts=any(fact.span is not None for fact in run.facts),
        note=note,
    )
