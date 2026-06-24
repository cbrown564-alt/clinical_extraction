"""Illustrative per-note stage label trajectories for the Gan Component Impact sidebar.

This is an *explanatory-only* artifact, the Gan analog of the ExECTv2
component-transition examples. Where an ExECTv2 prediction is a *set* of mentions
(so its worked example is an add/drop/change diff), a Gan prediction is a *single*
seizure-frequency label, so its worked example is a **label trajectory**: for a
few curated validation notes, how the one predicted label — and the purist
boundary band it lands in — evolves rung-to-rung as each deterministic stage is
cumulatively enabled.

It is NOT a scoring surface and never feeds an architecture decision: the scoring
ladder (`component_stage_ladder`) stays strictly ``aggregate_only``. We expose a
handful of notes purely so the stage ladder is intuitive at a glance — you can see
what each component actually does to one prediction.

The example notes are selected deterministically — most band changes first, then
most label-text changes, then by row index — so curation cannot be mistaken for
score cherry-picking. No model calls are made; every rung is replayed from the
saved producer outputs (or the deterministic re-run) through the same
``StageLadderProvider`` seam the aggregate ladder uses.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.component_stage_ladder import (  # noqa: E501
    BAND_CATEGORIES,
    DEFAULT_ARCHITECTURE_SPECS,
    DEFAULT_SPLIT,
    METRIC_LABEL,
    REPO_ROOT,
    ArchitectureSpec,
    RowMeta,
    StageCell,
    StageDefinition,
    _provider_for,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band

DEFAULT_GENERATED_ON = "2026-06-24"
DEFAULT_EXAMPLES_PER_ARCH = 3
EVIDENCE_MAX = 200
CLAIM_BOUNDARY = (
    "Illustrative per-note stage label trajectories; explanatory only, not a scoring surface."
)

_BAND_LABELS: dict[str, str] = {category.id: category.label for category in BAND_CATEGORIES}


def _short(value: Any, limit: int = EVIDENCE_MAX) -> str:
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _band_label(band: str | None) -> str | None:
    if band is None:
        return None
    return _BAND_LABELS.get(band, band)


def _stage_view(
    stage: StageDefinition,
    cell: StageCell,
    *,
    is_baseline: bool,
    gold_band: str,
    previous_label: str | None,
    previous_band: str | None,
) -> dict[str, Any]:
    band = boundary_band(cell.monthly_frequency)
    label = cell.label or "—"
    changed = (not is_baseline) and label.strip() != (previous_label or "").strip()
    band_changed = (not is_baseline) and band != previous_band
    return {
        "stage_id": stage.stage_id,
        "label": stage.label,
        "component_type": stage.component_type,
        "interpretation": stage.interpretation,
        "is_baseline": is_baseline,
        "predicted_label": label,
        "band": band,
        "band_label": _band_label(band),
        "evidence": _short(cell.evidence),
        "changed": changed,
        "band_changed": band_changed,
        "previous_label": None if is_baseline else (previous_label or "—"),
        "previous_band": None if is_baseline else previous_band,
        "previous_band_label": None if is_baseline else _band_label(previous_band),
        "correct": band == gold_band,
    }


def build_note_example(
    row_index: int,
    stages: tuple[StageDefinition, ...],
    cells_by_stage: dict[str, list[StageCell]],
    gold_frequency: float,
    meta: RowMeta,
) -> dict[str, Any]:
    gold_band = boundary_band(gold_frequency)
    stage_views: list[dict[str, Any]] = []
    previous_label: str | None = None
    previous_band: str | None = None
    change_count = 0
    band_change_count = 0
    for index, stage in enumerate(stages):
        cell = cells_by_stage[stage.stage_id][row_index]
        view = _stage_view(
            stage,
            cell,
            is_baseline=index == 0,
            gold_band=gold_band,
            previous_label=previous_label,
            previous_band=previous_band,
        )
        if view["changed"]:
            change_count += 1
        if view["band_changed"]:
            band_change_count += 1
        stage_views.append(view)
        previous_label = view["predicted_label"]
        previous_band = view["band"]

    final = stage_views[-1]
    row_id = meta.source_row_index
    return {
        "row_id": row_id,
        "row_label": f"row {row_id}" if row_id is not None else "note",
        "gold_label": meta.gold_label or "—",
        "gold_band": gold_band,
        "gold_band_label": _band_label(gold_band),
        "final_label": final["predicted_label"],
        "final_band": final["band"],
        "final_correct": final["correct"],
        "change_count": change_count,
        "band_change_count": band_change_count,
        "stages": stage_views,
    }


def _sort_key(example: dict[str, Any]) -> tuple[int, int, int]:
    # Most band changes first (the moves that fix the score), then most label-text
    # changes, then ascending row id — fully deterministic, no score peeking.
    row_id = example.get("row_id")
    return (
        -int(example["band_change_count"]),
        -int(example["change_count"]),
        int(row_id) if isinstance(row_id, int) else 1_000_000,
    )


def build_architecture_examples(
    spec: ArchitectureSpec,
    *,
    records: list[GanFrequencyRecord] | None,
    examples_per_arch: int = DEFAULT_EXAMPLES_PER_ARCH,
) -> dict[str, Any]:
    provider = _provider_for(spec, records=records)
    stages = provider.stages()
    golds = provider.golds()
    metas = provider.rows_metadata()
    stage_ids = [stage.stage_id for stage in stages]

    # Cumulative per-rung cells: rung i enables stages 0..i, disables i+1..n — the
    # same walk the aggregate ladder scores, but keeping each row's label/evidence.
    cells_by_stage: dict[str, list[StageCell]] = {}
    for index, stage_id in enumerate(stage_ids):
        disabled = frozenset(stage_ids[index + 1 :])
        cells_by_stage[stage_id] = provider.predict_cells(disabled)

    examples = [
        build_note_example(row_index, stages, cells_by_stage, golds[row_index], metas[row_index])
        for row_index in range(len(golds))
    ]
    examples.sort(key=_sort_key)
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
    specs: tuple[ArchitectureSpec, ...] = DEFAULT_ARCHITECTURE_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
    examples_per_arch: int = DEFAULT_EXAMPLES_PER_ARCH,
    data_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    needs_records = any(spec.kind == "deterministic" for spec in specs)
    records = None
    if needs_records:
        kwargs: dict[str, Any] = {}
        if data_path is not None:
            kwargs["data_path"] = data_path
        if manifest_path is not None:
            kwargs["manifest_path"] = manifest_path
        records = load_records_for_split(DEFAULT_SPLIT, **kwargs)
    architectures = [
        build_architecture_examples(spec, records=records, examples_per_arch=examples_per_arch)
        for spec in specs
    ]
    return {
        "artifact_kind": "gan2026_component_transition_examples",
        "dataset": "gan2026",
        "generated_on": generated_on,
        "row_inspection_policy": "illustrative_examples_only",
        "allow_model_calls": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "metric_label": METRIC_LABEL,
        "split": DEFAULT_SPLIT,
        "examples_per_architecture": examples_per_arch,
        "categories": [category.__dict__ for category in BAND_CATEGORIES],
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
        _CACHED_JSON = json.dumps(cached_component_transitions_payload(), ensure_ascii=False)
    return _CACHED_JSON


def write_component_transitions_artifacts(
    specs: tuple[ArchitectureSpec, ...] = DEFAULT_ARCHITECTURE_SPECS,
    *,
    json_path: Path = Path(
        "experiments/gan2026_component_transition_examples_validation_20260624.json"
    ),
    frontend_path: Path | None = Path(
        "frontend/public/mock-data/gan2026/component-transitions.json"
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


def main() -> None:
    paths = write_component_transitions_artifacts(generated_on=date.today().isoformat())
    for label, path in paths.items():
        print(f"Wrote {label}: {path}")


if __name__ == "__main__":
    main()
