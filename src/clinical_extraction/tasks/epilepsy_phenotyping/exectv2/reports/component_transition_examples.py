"""Illustrative per-letter component-transition examples for the Component Impact sidebar.

This is an *explanatory-only* artifact. It shows, for a few curated dev letters,
how the mention set evolves stage-to-stage (added / dropped / changed) as the
replay walks the pipeline from raw lane candidates through to the assembled
mention set and headline projection. It is NOT a scoring surface and never feeds
an architecture decision: the scoring
component-impact ladder (`component_ablation_replay`) stays strictly
`aggregate_only`. We expose a handful of letters purely so the stage ladder is
intuitive at a glance — you can see what each component actually does to one
prediction.

The example letters are selected deterministically — most cross-stage changes
first, then by letter id — so curation cannot be mistaken for score
cherry-picking. No model calls are made; everything is read from saved per-row
finding-assembly surfaces.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.frontend_review import REPO_ROOT
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.component_ablation_replay import (  # noqa: E501
    DEFAULT_REPLAY_SPECS,
    LAYER_DEFINITIONS,
    ComponentImpactReplaySpec,
    LayerDefinition,
)

DEFAULT_GENERATED_ON = "2026-06-24"
DEFAULT_EXAMPLES_PER_ARCH = 3
EVIDENCE_MAX = 160
CLAIM_BOUNDARY = (
    "Illustrative per-letter stage transitions; explanatory only, not a scoring surface."
)

# How to recover each ladder stage's per-row mention set from a saved row.
#   ("raw",  None)        -> row["raw_lane_mentions"]
#   ("surface", key)      -> row["prediction_surfaces"][key]
#   ("projection", None)  -> no per-mention surface (deterministic headline projection)
LAYER_SURFACE_SOURCE: dict[str, tuple[str, str | None]] = {
    "raw_lane_candidates": ("raw", None),
    "source_scored": ("surface", "source_scored"),
    "evidence_valid": ("surface", "evidence_valid"),
    "dictionary_normalized": ("surface", "dictionary_normalized"),
    "residual_semantic_added": ("surface", "residual_benchmark_added"),
    "headline_projection": ("projection", None),
}

PROJECTION_NOTE = (
    "Deterministic projection of the assembled mentions onto the clinical headline "
    "target. Not a per-mention surface, so there is no add/drop to show here."
)


@dataclass(frozen=True)
class CompactMention:
    entity: str
    text: str
    concept: str
    attributes: dict[str, str]
    source_lane: str
    evidence: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity": self.entity,
            "text": self.text,
            "concept": self.concept,
            "attributes": self.attributes,
            "source_lane": self.source_lane,
            "evidence": self.evidence,
        }

    @property
    def key(self) -> tuple[str, str]:
        return (self.entity, self.text.strip().lower())

    @property
    def value_sig(self) -> tuple[str, tuple[tuple[str, str], ...]]:
        return (self.concept, tuple(sorted(self.attributes.items())))


def _short(value: Any) -> str:
    text = str(value or "").strip()
    if len(text) <= EVIDENCE_MAX:
        return text
    return text[: EVIDENCE_MAX - 1].rstrip() + "…"


def _compact(mention: dict[str, Any]) -> CompactMention:
    attributes = mention.get("attributes") or {}
    return CompactMention(
        entity=str(mention.get("entity") or ""),
        text=str(mention.get("text") or ""),
        concept=str(mention.get("normalized_concept") or ""),
        attributes={str(k): str(v) for k, v in attributes.items()},
        source_lane=str(mention.get("source_lane") or ""),
        evidence=_short(mention.get("evidence")),
    )


def _stage_mentions(row: dict[str, Any], layer: LayerDefinition) -> list[CompactMention] | None:
    kind, surface_key = LAYER_SURFACE_SOURCE[layer.layer_id]
    if kind == "projection":
        return None
    if kind == "raw":
        raw = row.get("raw_lane_mentions") or []
    else:
        raw = (row.get("prediction_surfaces") or {}).get(surface_key) or []
    return [_compact(mention) for mention in raw]


def _diff(
    previous: list[CompactMention], current: list[CompactMention]
) -> tuple[list[CompactMention], list[CompactMention], list[dict[str, Any]], int]:
    prev_by: dict[tuple[str, str], CompactMention] = {}
    for mention in previous:
        prev_by.setdefault(mention.key, mention)
    cur_by: dict[tuple[str, str], CompactMention] = {}
    for mention in current:
        cur_by.setdefault(mention.key, mention)

    added = [m for key, m in cur_by.items() if key not in prev_by]
    dropped = [m for key, m in prev_by.items() if key not in cur_by]
    changed: list[dict[str, Any]] = []
    kept = 0
    for key, mention in cur_by.items():
        before = prev_by.get(key)
        if before is None:
            continue
        if before.value_sig != mention.value_sig:
            changed.append({"before": before.to_dict(), "after": mention.to_dict()})
        else:
            kept += 1
    return added, dropped, changed, kept


def _stage_transition(
    layer: LayerDefinition,
    previous: list[CompactMention] | None,
    current: list[CompactMention] | None,
) -> dict[str, Any]:
    base = {
        "stage_id": layer.layer_id,
        "label": layer.label,
        "component_type": layer.component_type,
        "interpretation": layer.interpretation,
    }
    if current is None:
        return {
            **base,
            "has_transition": False,
            "is_baseline": False,
            "mention_count": None,
            "added": [],
            "dropped": [],
            "changed": [],
            "kept": 0,
            "note": PROJECTION_NOTE,
        }
    if previous is None:
        # First mention surface — everything here is freshly emitted by the producers.
        return {
            **base,
            "has_transition": True,
            "is_baseline": True,
            "mention_count": len(current),
            "added": [m.to_dict() for m in current],
            "dropped": [],
            "changed": [],
            "kept": 0,
        }
    added, dropped, changed, _ = _diff(previous, current)
    # Reconcile against the real surface size so "carried through unchanged" sums
    # cleanly with added/changed even when a letter has duplicate-span mentions.
    kept = max(len(current) - len(added) - len(changed), 0)
    return {
        **base,
        "has_transition": True,
        "is_baseline": False,
        "mention_count": len(current),
        "added": [m.to_dict() for m in added],
        "dropped": [m.to_dict() for m in dropped],
        "changed": changed,
        "kept": kept,
    }


def _letter_stages(row: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    stages: list[dict[str, Any]] = []
    previous: list[CompactMention] | None = None
    change_count = 0
    for layer in LAYER_DEFINITIONS:
        current = _stage_mentions(row, layer)
        transition = _stage_transition(layer, previous, current)
        if current is not None and not transition["is_baseline"]:
            change_count += (
                len(transition["added"])
                + len(transition["dropped"])
                + len(transition["changed"])
            )
        stages.append(transition)
        if current is not None:
            previous = current
    return stages, change_count


def _final_count(stages: list[dict[str, Any]]) -> int | None:
    for stage in reversed(stages):
        if stage.get("mention_count") is not None:
            return int(stage["mention_count"])
    return None


def build_letter_example(row: dict[str, Any]) -> dict[str, Any]:
    stages, change_count = _letter_stages(row)
    gold = [
        {"entity": str(g.get("entity") or ""), "text": str(g.get("text") or "")}
        for g in (row.get("gold_mentions") or [])
    ]
    return {
        "letter_id": str(row.get("letter_id") or ""),
        "gold": gold,
        "gold_count": len(gold),
        "final_count": _final_count(stages),
        "change_count": change_count,
        "stages": stages,
    }


def _load_rows(path: Path) -> list[dict[str, Any]]:
    resolved = REPO_ROOT / path
    rows: list[dict[str, Any]] = []
    with resolved.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def build_architecture_examples(
    spec: ComponentImpactReplaySpec,
    *,
    examples_per_arch: int = DEFAULT_EXAMPLES_PER_ARCH,
) -> dict[str, Any]:
    rows = _load_rows(spec.source_jsonl_path)
    examples = [build_letter_example(row) for row in rows]
    # Most illustrative first (most stage changes), deterministic tie-break on id.
    examples.sort(key=lambda ex: (-ex["change_count"], ex["letter_id"]))
    chosen = [ex for ex in examples if ex["change_count"] > 0][:examples_per_arch]
    if not chosen:
        chosen = examples[:examples_per_arch]
    return {
        "run_id": spec.run_id,
        "label": spec.label,
        "model": spec.model,
        "decision": spec.decision,
        "examples": chosen,
    }


def build_component_transitions_payload(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    examples_per_arch: int = DEFAULT_EXAMPLES_PER_ARCH,
) -> dict[str, Any]:
    architectures = [
        build_architecture_examples(spec, examples_per_arch=examples_per_arch)
        for spec in specs
    ]
    return {
        "artifact_kind": "exectv2_component_transition_examples",
        "dataset": "exectv2",
        "generated_on": generated_on,
        "row_inspection_policy": "illustrative_examples_only",
        "allow_model_calls": False,
        "allow_post_run_tuning": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "examples_per_architecture": examples_per_arch,
        "stage_order": [layer.layer_id for layer in LAYER_DEFINITIONS],
        "architectures": architectures,
    }


_CACHED_PAYLOAD: dict[str, Any] | None = None
_CACHED_JSON: str | None = None


def cached_component_transitions_payload() -> dict[str, Any]:
    global _CACHED_PAYLOAD
    if _CACHED_PAYLOAD is None:
        _CACHED_PAYLOAD = build_component_transitions_payload()
    return _CACHED_PAYLOAD


def cached_component_transitions_json() -> str:
    global _CACHED_JSON
    if _CACHED_JSON is None:
        _CACHED_JSON = json.dumps(
            cached_component_transitions_payload(), ensure_ascii=False
        )
    return _CACHED_JSON


def write_component_transitions_artifacts(
    specs: tuple[ComponentImpactReplaySpec, ...] = DEFAULT_REPLAY_SPECS,
    *,
    json_path: Path = Path(
        "experiments/exectv2_component_transition_examples_dev140_20260624.json"
    ),
    frontend_path: Path | None = Path(
        "frontend/public/mock-data/exectv2/component-transitions.json"
    ),
    generated_on: str = DEFAULT_GENERATED_ON,
    examples_per_arch: int = DEFAULT_EXAMPLES_PER_ARCH,
) -> dict[str, Path]:
    payload = build_component_transitions_payload(
        specs, generated_on=generated_on, examples_per_arch=examples_per_arch
    )
    serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    (REPO_ROOT / json_path).parent.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / json_path).write_text(serialized, encoding="utf-8")
    resolved = {"json": json_path}
    if frontend_path is not None:
        (REPO_ROOT / frontend_path).parent.mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / frontend_path).write_text(serialized, encoding="utf-8")
        resolved["frontend"] = frontend_path
    return resolved
