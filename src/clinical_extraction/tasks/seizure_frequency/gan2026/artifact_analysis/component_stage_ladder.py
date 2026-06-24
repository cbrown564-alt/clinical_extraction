"""Gan 2026 component stage-ladder replay artifacts.

The Component Impact surface renders every architecture as the *same* cumulative
stage ladder it uses for ExECTv2: a baseline producer surface plus the marginal
contribution of each deterministic layer stacked on top, scored as purist
category accuracy. This module materializes that ladder for the Gan architectures
with no model calls.

Every architecture is decomposed through one seam — ``StageLadderProvider`` — so
the builder is architecture-agnostic: it asks each provider for its ordered
``stages()`` and its cumulative per-stage predictions, scores purist accuracy and
per-band deltas at each rung, and emits one ``ComponentLadder`` payload. The three
legacy ablation mechanisms become thin adapters *behind* that seam, each owning
exactly one architecture family:

- ``DeterministicCanonicalProvider`` (``AblationConfig`` adapter) — re-runs the
  canonical rule stages with benchmark repair and the evidence-trace gate
  cumulatively enabled. **Flat** on purist *category* (rules already emit clean
  Gan labels) — an honest finding, not a gap.
- ``HybridDeepReplayProvider`` (``disabled_ablation_switches`` adapter) — the LLM
  produces a *clinical assessment* of a candidate set, so the deterministic
  Normalize / Projection / Verify layers do real work turning it into a scored
  label. Each layer's contribution is the score gained when its ablation switches
  are enabled, via the reset-clinical-assessment deep-replay (no model calls).
- ``StructuredEventsProvider`` (``StructuredRepairConfig`` adapter) — the LLM
  extracts source-near events and a selection; the deterministic stack normalizes
  the label, re-derives it from the selected evidence, then applies the
  clinical-pattern repair families. Replayed from the saved ``raw_output`` with the
  repair config cumulatively enabled (no model calls). This is the architecture the
  old single-bar builder collapsed.
- ``LlmOnlyProvider`` (label-repair adapter) — a single produce pass emits a
  free-text label; the deterministic format/evidence label repair makes it a
  scorable Gan label. The producer floor is the model's raw label; the second rung
  is that repair.

Metric: purist category accuracy. Split: validation (750). No model calls.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any, Protocol

from clinical_extraction.core.evidence import evidence_is_substring
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.candidate_set import (
    CandidateSet,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages import (
    extract_stage,
    normalize_stage,
    select_and_render_stage,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import boundary_band, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_canonical_pipeline,
    llm_only_direct_labeler,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredRepairConfig,
    parse_structured_json,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
DEFAULT_GENERATED_ON = "2026-06-24"
DEFAULT_SPLIT = "validation"
UNKNOWN_FREQUENCY = 1000.0
METRIC_LABEL = "Purist accuracy"
METHOD = "Cumulative stage ladder"
CLAIM_BOUNDARY = "validation replay-only aggregate component-impact ladder"

_FULL_CONFIG = AblationConfig()
_NO_REPAIR_CONFIG = AblationConfig(
    enabled_groups=frozenset(RuleGroup) - {RuleGroup.BENCHMARK_REPAIR}
)

# Hybrid deep-replay ablation switches, grouped by reset stage. Disabling a group
# removes that layer from the deep-replay so its marginal contribution is the score
# gained when it is enabled. Sourced from the reset-stage component inventory plus
# the switches the projection/route code checks directly.
_HYBRID_NORMALIZE = frozenset(
    {
        "normalize_diary_date_list_frequency_recovery",
        "normalize_frequency_anchor_window_value_recovery",
        "normalize_frequency_multi_month_bucket_value_recovery",
        "normalize_seizure_free_duration_date_instrumentation",
        "normalize_selected_evidence_frequency_value_recovery",
        "normalize_vague_period_frequency_value_recovery",
    }
)
_HYBRID_PROJECT = frozenset(
    {
        "project_current_summary_rate_priority",
        "project_major_recent_relapse_over_background_frequency",
        "project_previous_active_month_over_current_month_zero",
        "project_cluster_cadence_default_multiple_per_cluster",
        "project_date_anchored_ytd_denominator",
    }
)
_HYBRID_VERIFY = frozenset(
    {
        "route_conditional_only_trigger",
        "route_denominator_window_mismatch",
        "route_relative_only_trend",
        "route_selected_evidence_missing_exact_trace",
        "route_selected_source_id_invalid",
        "route_unresolved_cluster_cadence_with_per_cluster_burden",
        "route_cyclic_window_patterns",
        "route_sleep_restricted_patterns",
        "verify_named_comparator_preservation_action_policy",
    }
)


# ── Per-category (boundary band) breakdown, the Gan analog of ExECTv2 families ──
@dataclass(frozen=True)
class BandCategory:
    id: str
    label: str
    short_label: str
    tone: str


BAND_CATEGORIES: tuple[BandCategory, ...] = (
    BandCategory("band_zero", "No seizures", "Zero", "success"),
    BandCategory("band_submonthly", "Sub-monthly", "<Mon", "deterministic"),
    BandCategory("band_monthly", "Monthly", "Mon", "deterministic-alt"),
    BandCategory("band_weekly", "Weekly", "Wk", "hybrid"),
    BandCategory("band_daily", "Daily", "Day", "llm"),
    BandCategory("band_unknown", "Unknown", "Unk", "muted"),
)
_BAND_IDS = tuple(category.id for category in BAND_CATEGORIES)


@dataclass(frozen=True)
class StageDefinition:
    stage_id: str
    label: str
    component_type: str
    interpretation: str


@dataclass(frozen=True)
class ArchitectureSpec:
    run_id: str
    label: str
    model: str
    decision: str
    kind: str  # "deterministic" | "hybrid" | "structured_events" | "llm_only"
    source_jsonl: Path | None = None
    stages: tuple[StageDefinition, ...] = field(default_factory=tuple)


_DETERMINISTIC_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        "deterministic_core",
        "Extract + normalize + select",
        "deterministic_rule",
        "Rule extraction, frequency normalization, and selection, with benchmark repair off.",
    ),
    StageDefinition(
        "benchmark_repair",
        "Benchmark repair",
        "repair",
        "Gan-format label repair on the selected fact (format-level; preserves the category).",
    ),
    StageDefinition(
        "evidence_trace_check",
        "Evidence trace check",
        "scorer",
        "Predictions whose evidence is not an exact note substring are dropped to unknown.",
    ),
)

_HYBRID_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        "raw_assessment",
        "LLM clinical assessment",
        "llm_assessment",
        "The LLM's selection over the candidate set, rendered with every deterministic layer off.",
    ),
    StageDefinition(
        "normalize",
        "Normalize",
        "normalize",
        "Frequency value recovery: anchor windows, multi-month buckets, seizure-free duration, "
        "vague periods.",
    ),
    StageDefinition(
        "projection",
        "Projection",
        "projection",
        "Projection policy: current-summary rate priority, relapse-over-background, "
        "cluster cadence, YTD denominator.",
    ),
    StageDefinition(
        "verify_route",
        "Verify / route",
        "verify_route",
        "Routing of ambiguous/unsupported rows for review; affects disposition more than purist "
        "category.",
    ),
)

_STRUCTURED_EVENTS_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        "llm_selection",
        "LLM events + selection",
        "llm_assessment",
        "The model's extracted events and selected final label, parsed with no deterministic "
        "label repair.",
    ),
    StageDefinition(
        "normalize",
        "Normalize",
        "normalize",
        "Format-level normalization turning the model's source-near label into a canonical "
        "Gan label.",
    ),
    StageDefinition(
        "evidence_projection",
        "Evidence projection",
        "projection",
        "Re-derives the label from the selected evidence and note context "
        "(selected-evidence repair).",
    ),
    StageDefinition(
        "clinical_repair",
        "Clinical repair families",
        "repair",
        "Pattern-specific repairs: monthly diary, usual interval, breakthrough, non-epileptic, "
        "residual jerk, post-change burst, dated sequence, elapsed-since-anchor.",
    ),
)

_LLM_ONLY_STAGES: tuple[StageDefinition, ...] = (
    StageDefinition(
        "model_label",
        "Model label",
        "llm_assessment",
        "The model's raw final label, as emitted, before any deterministic repair.",
    ),
    StageDefinition(
        "label_repair",
        "Label repair",
        "repair",
        "Format and evidence-grounded label normalization that makes the model's label a "
        "scorable Gan label.",
    ),
)


def _comparison_jsonl(name: str) -> Path:
    return Path(f"experiments/gan2026_three_way_comparison_validation750_{name}.jsonl")


_HYBRID_JSONL = _comparison_jsonl("hybrid_live_candidate_sets_gpt41mini_2026-06-08")

DEFAULT_ARCHITECTURE_SPECS: tuple[ArchitectureSpec, ...] = (
    ArchitectureSpec(
        run_id="deterministic_canonical_pipeline",
        label="Deterministic canonical",
        model="rules",
        decision="control",
        kind="deterministic",
        stages=_DETERMINISTIC_STAGES,
    ),
    ArchitectureSpec(
        run_id="hybrid",
        label="Hybrid (reset-native)",
        model="openai/gpt-4.1-mini",
        decision="diagnostic",
        kind="hybrid",
        source_jsonl=_HYBRID_JSONL,
        stages=_HYBRID_STAGES,
    ),
    ArchitectureSpec(
        run_id="hybrid_structured_events",
        label="Hybrid (LLM extract)",
        model="openai/gpt-4.1-mini",
        decision="diagnostic",
        kind="structured_events",
        source_jsonl=_comparison_jsonl("hybrid_structured_events_gpt41mini_2026-06-07"),
        stages=_STRUCTURED_EVENTS_STAGES,
    ),
    ArchitectureSpec(
        run_id="llm_only_canonical_pipeline",
        label="LLM-only (rules in prompt)",
        model="openai/gpt-4.1-mini",
        decision="diagnostic",
        kind="llm_only",
        source_jsonl=_comparison_jsonl("llm_only_canonical_pipeline_gpt41mini_2026-06-07"),
        stages=_LLM_ONLY_STAGES,
    ),
    ArchitectureSpec(
        run_id="llm_only_direct_labeler",
        label="LLM-only (direct label)",
        model="openai/gpt-4.1-mini",
        decision="diagnostic",
        kind="llm_only",
        source_jsonl=_comparison_jsonl("llm_only_direct_labeler_gpt41mini_2026-06-07"),
        stages=_LLM_ONLY_STAGES,
    ),
)


# ── Scoring ──────────────────────────────────────────────────────────────────
def _accuracy(predictions: list[float], golds: list[float]) -> float:
    if not golds:
        return 0.0
    correct = sum(
        map_purist(pred) == map_purist(gold)
        for pred, gold in zip(predictions, golds, strict=True)
    )
    return correct / len(golds)


def _band_accuracy(predictions: list[float], golds: list[float]) -> dict[str, float | None]:
    out: dict[str, float | None] = {}
    for band in _BAND_IDS:
        rows = [
            (pred, gold)
            for pred, gold in zip(predictions, golds, strict=True)
            if boundary_band(gold) == band
        ]
        out[band] = (
            sum(map_purist(p) == map_purist(g) for p, g in rows) / len(rows)
            if rows
            else None
        )
    return out


def _label_to_frequency(label: str | None) -> float:
    """Map a Gan label to a monthly frequency, or unknown when unscorable."""

    if not label:
        return UNKNOWN_FREQUENCY
    try:
        return label_to_frequency_record(label).monthly_frequency
    except ValueError:
        return UNKNOWN_FREQUENCY


# ── The seam: one StageLadderProvider every architecture implements ────────────
@dataclass(frozen=True)
class StageLadder:
    """A provider's cumulative output: golds plus per-stage predictions."""

    golds: list[float]
    predictions_by_stage: dict[str, list[float]]


class StageLadderProvider(Protocol):
    """One stage-ablation seam for the architecture-agnostic ladder builder.

    ``stages()`` is the ordered downstream stack; ``predict(disabled)`` returns the
    per-row monthly frequency with the named stages turned off (replay-only, no
    model calls); ``build()`` walks the ladder, cumulatively re-enabling stages.
    """

    spec: ArchitectureSpec

    def stages(self) -> tuple[StageDefinition, ...]: ...

    def predict(self, disabled_stage_ids: frozenset[str]) -> list[float]: ...

    def golds(self) -> list[float]: ...

    def build(self) -> StageLadder: ...

    def source_artifacts(self) -> list[str]: ...


def _cumulative_build(provider: StageLadderProvider) -> StageLadder:
    """Walk a provider's stages, disabling everything strictly downstream of each.

    Rung *i* enables stages ``0..i`` and disables ``i+1..n``, so each rung's
    prediction is "the answer with this much of the deterministic stack on" and the
    delta versus the previous rung is the marginal contribution of stage *i*.
    """

    stage_ids = [stage.stage_id for stage in provider.stages()]
    by_stage: dict[str, list[float]] = {}
    for index, stage_id in enumerate(stage_ids):
        disabled = frozenset(stage_ids[index + 1 :])
        by_stage[stage_id] = provider.predict(disabled)
    return StageLadder(golds=provider.golds(), predictions_by_stage=by_stage)


# ── AblationConfig adapter: deterministic canonical pipeline ───────────────────
class DeterministicCanonicalProvider:
    """Re-runs the canonical rule stages; benchmark repair + evidence gate ablate."""

    def __init__(self, spec: ArchitectureSpec, records: list[GanFrequencyRecord]) -> None:
        self.spec = spec
        self._golds = [record.gold_monthly_frequency for record in records]
        # Extraction is config-independent, so do it once and reuse across rungs.
        self._extracted: list[tuple[str, Any, Any]] = []
        for record in records:
            raw_candidates, _candidate_set, candidate_events = extract_stage(
                record.note_text,
                source_row_index=record.source_row_index,
                ablation_config=_FULL_CONFIG,
            )
            self._extracted.append((record.note_text, raw_candidates, candidate_events))

    def stages(self) -> tuple[StageDefinition, ...]:
        return self.spec.stages

    def golds(self) -> list[float]:
        return self._golds

    def predict(self, disabled_stage_ids: frozenset[str]) -> list[float]:
        repair_on = "benchmark_repair" not in disabled_stage_ids
        gate_on = "evidence_trace_check" not in disabled_stage_ids
        config = _FULL_CONFIG if repair_on else _NO_REPAIR_CONFIG
        predictions: list[float] = []
        for note, raw_candidates, candidate_events in self._extracted:
            normalized = normalize_stage(candidate_events, raw_candidates, ablation_config=config)
            selected = select_and_render_stage(candidate_events, normalized, ablation_config=config)
            frequency = selected.monthly_frequency
            if gate_on and not evidence_is_substring(note, selected.evidence):
                frequency = UNKNOWN_FREQUENCY
            predictions.append(frequency)
        return predictions

    def build(self) -> StageLadder:
        return _cumulative_build(self)

    def source_artifacts(self) -> list[str]:
        return ["re-run: deterministic_canonical_stages (no model calls)"]


# ── disabled_ablation_switches adapter: reset-native hybrid ────────────────────
class HybridDeepReplayProvider:
    """Cumulatively enables the deterministic layers in the hybrid deep-replay."""

    def __init__(
        self,
        spec: ArchitectureSpec,
        *,
        data_path: Path | None,
        manifest_path: Path | None,
    ) -> None:
        if spec.source_jsonl is None:
            raise ValueError("hybrid deep-replay needs a source_jsonl")
        self.spec = spec
        self._rows: list[dict[str, Any]] = []
        with (REPO_ROOT / spec.source_jsonl).open(encoding="utf-8-sig") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                if isinstance(row.get("candidate_set"), dict) and row.get("assessment_draft"):
                    self._rows.append(row)
        self._candidate_sets = {
            int(row["source_row_index"]): CandidateSet.model_validate(row["candidate_set"])
            for row in self._rows
        }
        record_kwargs: dict[str, Any] = {}
        if data_path is not None:
            record_kwargs["data_path"] = data_path
        if manifest_path is not None:
            record_kwargs["manifest_path"] = manifest_path
        self._gold_records = {
            record.source_row_index: record
            for record in load_records_for_split(DEFAULT_SPLIT, **record_kwargs)
        }
        self._order = [int(row["source_row_index"]) for row in self._rows]
        self._golds = [self._gold_records[idx].gold_monthly_frequency for idx in self._order]

    def stages(self) -> tuple[StageDefinition, ...]:
        return self.spec.stages

    def golds(self) -> list[float]:
        return self._golds

    def predict(self, disabled_stage_ids: frozenset[str]) -> list[float]:
        from clinical_extraction.tasks.seizure_frequency.gan2026.hybrid.reset_clinical_assessment_pipeline import (  # noqa: E501
            build_reset_clinical_assessment_pipeline_artifact as run_deep_replay,
        )

        switches: set[str] = set()
        if "normalize" in disabled_stage_ids:
            switches |= _HYBRID_NORMALIZE
        if "projection" in disabled_stage_ids:
            switches |= _HYBRID_PROJECT
        if "verify_route" in disabled_stage_ids:
            switches |= _HYBRID_VERIFY
        artifact = run_deep_replay(
            assessment_rows=self._rows,
            candidate_sets=self._candidate_sets,
            gold_records=self._gold_records,
            assessment_artifact_path="in_memory",
            candidate_set_artifact_path="in_memory",
            disabled_ablation_switches=switches,
        )
        predicted_by_index: dict[int, float] = {}
        for score_row in artifact.score_rows:
            index = int(score_row["source_row_index"])
            score = score_row.get("score") or {}
            frequency = score.get("predicted_monthly_frequency")
            predicted_by_index[index] = (
                UNKNOWN_FREQUENCY if frequency is None else float(frequency)
            )
        return [predicted_by_index.get(idx, UNKNOWN_FREQUENCY) for idx in self._order]

    def build(self) -> StageLadder:
        return _cumulative_build(self)

    def source_artifacts(self) -> list[str]:
        assert self.spec.source_jsonl is not None
        return [
            self.spec.source_jsonl.as_posix(),
            "deep-replay: reset_clinical_assessment_pipeline (no model calls)",
        ]


# ── StructuredRepairConfig adapter: hybrid structured events ───────────────────
def _structured_events_config(
    *, normalize_on: bool, evidence_on: bool, clinical_on: bool
) -> StructuredRepairConfig:
    """Project the three downstream stages onto the StructuredRepairConfig flags.

    JSON-dialect repair stays on at every rung — it is parse-level recovery of a
    well-formed answer, not a label transformation — so the producer floor is the
    model's own selected label, scored as-is.
    """

    return StructuredRepairConfig(
        json_dialect_repair=True,
        basic_label_repair=normalize_on,
        basic_label_repair_format_only=False,
        clean_scorer_facing_gold_policy=False,
        selected_evidence_repair=evidence_on,
        monthly_diary_repair=clinical_on,
        usual_interval_repair=clinical_on,
        breakthrough_repair=clinical_on,
        non_epileptic_repair=clinical_on,
        residual_jerk_repair=clinical_on,
        post_change_burst_repair=clinical_on,
        dated_sequence_repair=clinical_on,
        elapsed_anchor_repair=clinical_on,
    )


class StructuredEventsProvider:
    """Replays the structured-events deterministic stack over the saved raw output."""

    def __init__(self, spec: ArchitectureSpec) -> None:
        if spec.source_jsonl is None:
            raise ValueError(f"{spec.run_id} needs a source_jsonl")
        self.spec = spec
        self._rows = _load_rows(spec.source_jsonl)
        self._golds = [row["gold"] for row in self._rows]

    def stages(self) -> tuple[StageDefinition, ...]:
        return self.spec.stages

    def golds(self) -> list[float]:
        return self._golds

    def predict(self, disabled_stage_ids: frozenset[str]) -> list[float]:
        config = _structured_events_config(
            normalize_on="normalize" not in disabled_stage_ids,
            evidence_on="evidence_projection" not in disabled_stage_ids,
            clinical_on="clinical_repair" not in disabled_stage_ids,
        )
        predictions: list[float] = []
        for row in self._rows:
            extraction, _normalized, _errors = parse_structured_json(
                row["raw_output"], note_text=row["note_text"], repair_config=config
            )
            label = extraction.selection.final_label if extraction else None
            predictions.append(_label_to_frequency(label))
        return predictions

    def build(self) -> StageLadder:
        return _cumulative_build(self)

    def source_artifacts(self) -> list[str]:
        assert self.spec.source_jsonl is not None
        return [
            self.spec.source_jsonl.as_posix(),
            "replay: hybrid_structured_events.parse_structured_json (no model calls)",
        ]


# ── label-repair adapter: single-pass LLM-only configs ─────────────────────────
@dataclass(frozen=True)
class _LlmOnlyModule:
    extract_json_object: Callable[[str], str]
    parse_decision_json: Callable[[str], tuple[Any, list[str]]]


_LLM_ONLY_MODULES: dict[str, _LlmOnlyModule] = {
    "llm_only_canonical_pipeline": _LlmOnlyModule(
        llm_only_canonical_pipeline._extract_json_object,
        llm_only_canonical_pipeline.parse_decision_json,
    ),
    "llm_only_direct_labeler": _LlmOnlyModule(
        llm_only_direct_labeler._extract_json_object,
        llm_only_direct_labeler.parse_decision_json,
    ),
}


class LlmOnlyProvider:
    """Producer floor (raw model label) plus the deterministic label-repair stage."""

    def __init__(self, spec: ArchitectureSpec) -> None:
        if spec.source_jsonl is None:
            raise ValueError(f"{spec.run_id} needs a source_jsonl")
        module = _LLM_ONLY_MODULES.get(spec.run_id)
        if module is None:
            raise ValueError(f"no LLM-only parser registered for {spec.run_id}")
        self.spec = spec
        self._module = module
        self._rows = _load_rows(spec.source_jsonl)
        self._golds = [row["gold"] for row in self._rows]

    def stages(self) -> tuple[StageDefinition, ...]:
        return self.spec.stages

    def golds(self) -> list[float]:
        return self._golds

    def predict(self, disabled_stage_ids: frozenset[str]) -> list[float]:
        repaired = "label_repair" not in disabled_stage_ids
        predictions: list[float] = []
        for row in self._rows:
            raw_output = row["raw_output"]
            if repaired:
                decision, _errors = self._module.parse_decision_json(raw_output)
                label = decision.final_label if decision else None
            else:
                label = self._raw_label(raw_output)
            predictions.append(_label_to_frequency(label))
        return predictions

    def _raw_label(self, raw_output: str) -> str | None:
        """The model's emitted final_label, before any deterministic repair."""

        if not raw_output:
            return None
        try:
            payload = json.loads(self._module.extract_json_object(raw_output))
        except (json.JSONDecodeError, ValueError):
            return None
        label = payload.get("final_label") if isinstance(payload, dict) else None
        return label if isinstance(label, str) else None

    def build(self) -> StageLadder:
        return _cumulative_build(self)

    def source_artifacts(self) -> list[str]:
        assert self.spec.source_jsonl is not None
        return [self.spec.source_jsonl.as_posix()]


def _load_rows(path: Path) -> list[dict[str, Any]]:
    """Read saved producer rows, carrying gold + note_text for self-contained replay."""

    rows: list[dict[str, Any]] = []
    with (REPO_ROOT / path).open(encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            gold = (row.get("reference") or {}).get("gold_monthly_frequency")
            if gold is None:
                continue
            note_text: str | None = None
            prompt_input = row.get("prompt_input_json")
            if isinstance(prompt_input, str):
                try:
                    note_text = json.loads(prompt_input).get("note_text")
                except json.JSONDecodeError:
                    note_text = None
            rows.append(
                {
                    "source_row_index": row.get("source_row_index"),
                    "gold": float(gold),
                    "note_text": note_text,
                    "raw_output": row.get("raw_output") or "",
                }
            )
    return rows


def _provider_for(
    spec: ArchitectureSpec,
    *,
    records: list[GanFrequencyRecord] | None,
    data_path: Path | None,
    manifest_path: Path | None,
) -> StageLadderProvider:
    if spec.kind == "deterministic":
        if records is None:
            raise ValueError("deterministic re-run requires split records")
        return DeterministicCanonicalProvider(spec, records)
    if spec.kind == "hybrid":
        return HybridDeepReplayProvider(spec, data_path=data_path, manifest_path=manifest_path)
    if spec.kind == "structured_events":
        return StructuredEventsProvider(spec)
    if spec.kind == "llm_only":
        return LlmOnlyProvider(spec)
    raise ValueError(f"unknown architecture kind {spec.kind!r}")


# ── Ladder assembly ────────────────────────────────────────────────────────────
def _round(value: float) -> float:
    return round(float(value), 4)


def build_architecture_ladder(
    spec: ArchitectureSpec,
    *,
    records: list[GanFrequencyRecord] | None,
    generated_on: str,
    data_path: Path | None = None,
    manifest_path: Path | None = None,
) -> dict[str, Any]:
    provider = _provider_for(
        spec, records=records, data_path=data_path, manifest_path=manifest_path
    )
    ladder = provider.build()
    golds = ladder.golds
    by_stage = ladder.predictions_by_stage

    stages: list[dict[str, Any]] = []
    previous_score: float | None = None
    previous_bands: dict[str, float | None] | None = None
    for index, definition in enumerate(spec.stages):
        predictions = by_stage[definition.stage_id]
        score = _accuracy(predictions, golds)
        bands = _band_accuracy(predictions, golds)
        delta = 0.0 if previous_score is None else _round(score - previous_score)
        category_deltas: dict[str, float] = {}
        for band in _BAND_IDS:
            current = bands.get(band)
            prior = previous_bands.get(band) if previous_bands else None
            category_deltas[band] = (
                0.0 if current is None or prior is None else _round(current - prior)
            )
        stages.append(
            {
                "stage_id": definition.stage_id,
                "label": definition.label,
                "component_type": definition.component_type,
                "score": _round(score),
                "delta_from_previous": delta,
                "is_baseline": index == 0,
                "category_deltas": category_deltas,
                "interpretation": definition.interpretation,
            }
        )
        previous_score = score
        previous_bands = bands

    return {
        "artifact_kind": "gan2026_component_architecture_ladder",
        "dataset": "gan2026",
        "generated_on": generated_on,
        "run_id": spec.run_id,
        "label": spec.label,
        "model": spec.model,
        "decision": spec.decision,
        "split": DEFAULT_SPLIT,
        "row_count": len(golds),
        "final_score": stages[-1]["score"] if stages else 0.0,
        "stages": stages,
        "source_artifacts": provider.source_artifacts(),
        "claim_boundary": CLAIM_BOUNDARY,
        "row_inspection_policy": "aggregate_only",
    }


def build_component_stage_ladder_payload(
    specs: tuple[ArchitectureSpec, ...] = DEFAULT_ARCHITECTURE_SPECS,
    *,
    generated_on: str = DEFAULT_GENERATED_ON,
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
        build_architecture_ladder(
            spec,
            records=records,
            generated_on=generated_on,
            data_path=data_path,
            manifest_path=manifest_path,
        )
        for spec in specs
    ]
    return {
        "artifact_kind": "gan2026_component_stage_ladder_set",
        "dataset": "gan2026",
        "generated_on": generated_on,
        "metric": "purist_accuracy",
        "metric_label": METRIC_LABEL,
        "method": METHOD,
        "method_note": f"{DEFAULT_SPLIT} · replay only · no model calls · {generated_on}",
        "split": DEFAULT_SPLIT,
        "row_inspection_policy": "aggregate_only",
        "allow_model_calls": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "categories": [category.__dict__ for category in BAND_CATEGORIES],
        "architectures": architectures,
    }


@lru_cache(maxsize=1)
def cached_component_stage_ladder_payload() -> dict[str, Any]:
    return build_component_stage_ladder_payload()


@lru_cache(maxsize=1)
def cached_component_stage_ladder_json() -> str:
    return json.dumps(cached_component_stage_ladder_payload(), ensure_ascii=False)


def write_component_stage_ladder_artifacts(
    specs: tuple[ArchitectureSpec, ...] = DEFAULT_ARCHITECTURE_SPECS,
    *,
    json_path: Path = Path(
        "experiments/gan2026_component_stage_ladder_validation_20260624.json"
    ),
    md_path: Path = Path(
        "experiments/gan2026_component_stage_ladder_validation_20260624.md"
    ),
    frontend_path: Path | None = Path(
        "frontend/public/mock-data/gan2026/component-ablation.json"
    ),
    generated_on: str = DEFAULT_GENERATED_ON,
) -> dict[str, Path]:
    payload = build_component_stage_ladder_payload(specs, generated_on=generated_on)
    (REPO_ROOT / json_path).parent.mkdir(parents=True, exist_ok=True)
    (REPO_ROOT / json_path).write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (REPO_ROOT / md_path).write_text(
        render_markdown(payload, json_path=json_path), encoding="utf-8"
    )
    if frontend_path is not None:
        (REPO_ROOT / frontend_path).parent.mkdir(parents=True, exist_ok=True)
        (REPO_ROOT / frontend_path).write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
    return {"json": json_path, "markdown": md_path}


def render_markdown(payload: dict[str, Any], *, json_path: Path) -> str:
    lines = [
        "# Gan 2026 Component Stage-Ladder Replay",
        "",
        f"- Generated: `{payload['generated_on']}`",
        f"- JSON: `{json_path.as_posix()}`",
        f"- Metric: {payload['metric_label']} · split `{payload['split']}`",
        f"- Claim boundary: {payload['claim_boundary']}",
        "- No model calls; deterministic stages re-run, hybrid layers via deep-replay, "
        "structured-events + LLM-only stacks replayed from saved raw outputs.",
        "",
        "| Architecture | Decision | Rows | Final | Stages (score) |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for architecture in payload["architectures"]:
        stage_summary = " → ".join(
            f"{stage['label']} {stage['score']:.2f}" for stage in architecture["stages"]
        )
        lines.append(
            f"| `{architecture['run_id']}` | {architecture['decision']} | "
            f"{architecture['row_count']} | {architecture['final_score']:.2f} | "
            f"{stage_summary} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    paths = write_component_stage_ladder_artifacts(generated_on=date.today().isoformat())
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['markdown']}")


if __name__ == "__main__":
    main()
