"""GPT-first ExECTv2 architecture-loop status report.

The report turns the active strategy note into a repeatable readiness check. It
does not score new model outputs; it reads the run registry and states which
architecture tracks have comparison-grade dev evidence, which only have
supporting/legacy evidence, and why a full-200 audit remains blocked.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Literal

DEFAULT_REGISTRY_PATH = Path("experiments/registry.jsonl")
FREEZE_TARGET_PER_ITEM = 0.87
FREEZE_TARGET_PER_LETTER = 0.90
FULL_DEV_LETTERS = 140
MODEL = "openai/gpt-4.1-mini"

TrackName = Literal["rules_only", "llm_only", "hybrid"]
Scope = Literal["all9", "sf_only", "unknown"]


@dataclass(frozen=True)
class TrackRequirement:
    track: TrackName
    required_shape: str
    required_scope: Scope
    preferred_families: tuple[str, ...]
    supporting_families: tuple[str, ...]
    next_action: str


@dataclass(frozen=True)
class TrackStatus:
    track: TrackName
    required_shape: str
    status: str
    next_action: str
    best_run_id: str | None = None
    pipeline_family: str | None = None
    scope: Scope = "unknown"
    row_count: int = 0
    semantic_per_item_f1: float | None = None
    semantic_per_letter_f1: float | None = None
    benchmark_per_item_f1: float | None = None
    benchmark_per_letter_f1: float | None = None
    evidence_validity_rate: float | None = None
    call_failures: int | None = None
    parse_failures: int | None = None
    routed_or_dropped: str | None = None
    artifact_paths: tuple[str, ...] = ()
    gap: str = ""


REQUIREMENTS: tuple[TrackRequirement, ...] = (
    TrackRequirement(
        track="rules_only",
        required_shape="deterministic all-9 baseline with rule families and CUI projection",
        required_scope="all9",
        preferred_families=("exectv2_deterministic_all9",),
        supporting_families=("exectv2_deterministic",),
        next_action=(
            "Use the deterministic all-9 scorecard to reduce active-entity "
            "over-emission, improve Prescription/Investigations exactness, and add "
            "the next entity engines with rule-family/CUI ablations."
        ),
    ),
    TrackRequirement(
        track="llm_only",
        required_shape="GPT per-entity all-9 structured mention frames",
        required_scope="all9",
        preferred_families=("exectv2_llm_only_per_entity_all9",),
        supporting_families=(
            "exectv2_llm_only_all_entities",
            "exectv2_llm_only_per_entity",
            "exectv2_llm_only_single_pass",
            "exectv2_llm_only_clinical_findings",
        ),
        next_action=(
            "Run GPT per-entity all-9 pilot25 then dev140, beginning with "
            "Prescription, Investigations, Diagnosis, and SeizureFrequency."
        ),
    ),
    TrackRequirement(
        track="hybrid",
        required_shape="GPT all-9 candidate assessment over evidence-grounded candidates",
        required_scope="all9",
        preferred_families=("exectv2_hybrid_all9",),
        supporting_families=("exectv2_hybrid",),
        next_action=(
            "Extend the live candidate-set and GPT candidate-assessment pattern from "
            "SeizureFrequency to all nine entities, with routing and CUI ablations."
        ),
    ),
)


def load_registry(path: Path = DEFAULT_REGISTRY_PATH) -> list[dict[str, Any]]:
    """Read a JSONL registry as plain dicts, skipping blank lines."""

    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def record_scope(record: Mapping[str, Any]) -> Scope:
    """Infer whether a run is all-entity, SF-only, or unclear."""

    family = str(record.get("pipeline_family", ""))
    metrics = record.get("primary_metrics") or {}
    model_role = str(record.get("model_role", "")).lower()
    run_id = str(record.get("run_id", "")).lower()
    if (
        family.endswith("_all9")
        or family == "exectv2_llm_only_all_entities"
        or "all_entities" in run_id
        or "all-entity" in model_role
        or "all nine" in model_role
        or "semantic_per_item_f1" in metrics
        or "benchmark_per_item_f1" in metrics
    ):
        return "all9"
    if any(str(key).startswith("sf_") for key in metrics) or "seizurefrequency" in model_role:
        return "sf_only"
    return "unknown"


def build_track_statuses(
    records: Sequence[Mapping[str, Any]],
    *,
    model: str = MODEL,
    split: str = "dev",
    full_dev_letters: int = FULL_DEV_LETTERS,
) -> list[TrackStatus]:
    """Evaluate registry records against the active GPT-first strategy tracks."""

    statuses: list[TrackStatus] = []
    for requirement in REQUIREMENTS:
        candidates = [
            record
            for record in records
            if _record_matches_context(record, model=model, split=split)
            and str(record.get("pipeline_family", ""))
            in requirement.preferred_families + requirement.supporting_families
        ]
        preferred = [
            record
            for record in candidates
            if str(record.get("pipeline_family", "")) in requirement.preferred_families
            and record_scope(record) == requirement.required_scope
            and int(record.get("row_count") or 0) >= full_dev_letters
        ]
        if preferred:
            statuses.append(_status_from_record(requirement, _best_record(preferred), "satisfied"))
            continue

        supporting = [_best_record(candidates)] if candidates else []
        if not supporting:
            statuses.append(
                TrackStatus(
                    track=requirement.track,
                    required_shape=requirement.required_shape,
                    status="missing_required_run",
                    next_action=requirement.next_action,
                    gap="No registry evidence for this GPT-first strategy track on dev.",
                )
            )
            continue

        best = supporting[0]
        scope = record_scope(best)
        family = str(best.get("pipeline_family", ""))
        if scope != requirement.required_scope:
            status = "scope_gap"
            gap = f"Best available run is {scope}, but the required scope is all9."
        elif family not in requirement.preferred_families:
            status = "shape_gap"
            gap = (
                "Best available run has the right broad scope, but not the strategy's "
                "required architecture shape."
            )
        else:
            status = "coverage_gap"
            gap = (
                f"Best available run has {int(best.get('row_count') or 0)} letters; "
                f"full dev requires {full_dev_letters}."
            )
        statuses.append(_status_from_record(requirement, best, status, gap=gap))
    return statuses


def render_status_markdown(
    statuses: Sequence[TrackStatus],
    *,
    generated_on: str | None = None,
    model: str = MODEL,
    split: str = "dev",
) -> str:
    """Render the strategy status report."""

    generated_on = generated_on or date.today().isoformat()
    ready, blockers = freeze_readiness(statuses)
    lines = [
        "# ExECTv2 GPT-First Architecture Loop Status",
        "",
        f"- Generated: `{generated_on}`",
        f"- Model loop: `{model}`",
        f"- Development split: `{split}`",
        "- Strategy: `docs/research/exectv2_gpt_first_full_architecture_strategy_2026-06-17.md`",
        f"- Freeze target: benchmark dev overall >= `{FREEZE_TARGET_PER_ITEM:.2f}` "
        f"per-item and >= `{FREEZE_TARGET_PER_LETTER:.2f}` per-letter, plus "
        "all three attribution-clean tracks.",
        f"- Architecture freeze readiness: `{'ready' if ready else 'not ready'}`",
        "",
    ]
    if blockers:
        lines.extend(["## Freeze Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in blockers)
        lines.append("")

    lines.extend(
        [
            "## Run Matrix",
            "",
            "| Track | Required shape | Status | Best run | Scope | Letters "
            "| Semantic F1 | Benchmark F1 | Reliability | Next action |",
            "| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- |",
        ]
    )
    for status in statuses:
        lines.append(
            "| "
            + " | ".join(
                [
                    status.track,
                    _md(status.required_shape),
                    f"`{status.status}`",
                    _run_cell(status),
                    status.scope,
                    str(status.row_count or ""),
                    _metric_pair(status.semantic_per_item_f1, status.semantic_per_letter_f1),
                    _metric_pair(status.benchmark_per_item_f1, status.benchmark_per_letter_f1),
                    _reliability_cell(status),
                    _md(status.next_action),
                ]
            )
            + " |"
        )

    lines.extend(
        [
            "",
            "## Reading",
            "",
            (
                "Current evidence is useful but not architecture-freeze evidence. "
                "The all-entity LLM single-pass baseline is retained as a negative "
                "baseline; it does not satisfy the new per-entity structured-frame "
                "track. SF-only rules and hybrid runs remain valuable transfer "
                "checks, but they do not satisfy all-9 breadth."
            ),
            "",
            (
                "Full-200 auditing remains blocked until dev140 has all-9 "
                "rules_only, llm_only, and hybrid evidence with reliability "
                "scorecards and component/CUI ablations."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def write_status_report(
    out_path: Path,
    *,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    generated_on: str | None = None,
    model: str = MODEL,
    split: str = "dev",
) -> Path:
    """Build and write the architecture-loop status report."""

    records = load_registry(registry_path)
    statuses = build_track_statuses(records, model=model, split=split)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_status_markdown(statuses, generated_on=generated_on, model=model, split=split),
        encoding="utf-8",
    )
    return out_path


def freeze_readiness(statuses: Sequence[TrackStatus]) -> tuple[bool, list[str]]:
    """Return whether the current matrix permits an architecture freeze."""

    blockers: list[str] = []
    for status in statuses:
        if status.status != "satisfied":
            blockers.append(f"{status.track}: {status.status} - {status.gap or status.next_action}")
            continue
        item = status.benchmark_per_item_f1
        letter = status.benchmark_per_letter_f1
        if item is None or letter is None:
            blockers.append(f"{status.track}: missing benchmark F1 fields")
        elif item < FREEZE_TARGET_PER_ITEM or letter < FREEZE_TARGET_PER_LETTER:
            blockers.append(
                f"{status.track}: benchmark F1 {item:.3f}/{letter:.3f} below "
                f"{FREEZE_TARGET_PER_ITEM:.2f}/{FREEZE_TARGET_PER_LETTER:.2f}"
            )
    return not blockers, blockers


def _record_matches_context(record: Mapping[str, Any], *, model: str, split: str) -> bool:
    record_model = str(record.get("model", ""))
    return str(record.get("split", "")) == split and (
        record_model == model or record_model == "(model-independent)"
    )


def _best_record(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    return max(
        records,
        key=lambda record: (
            int(record.get("row_count") or 0),
            _best_metric(record) or -1.0,
            str(record.get("date", "")),
        ),
    )


def _status_from_record(
    requirement: TrackRequirement,
    record: Mapping[str, Any],
    status: str,
    *,
    gap: str = "",
) -> TrackStatus:
    metrics = record.get("primary_metrics") or {}
    semantic_item, semantic_letter = _metric_pair_values(
        metrics, all9_key="semantic", sf_key="sf_semantic"
    )
    benchmark_item, benchmark_letter = _metric_pair_values(
        metrics, all9_key="benchmark", sf_key="sf_benchmark"
    )
    routed_or_dropped = _routed_or_dropped(metrics)
    return TrackStatus(
        track=requirement.track,
        required_shape=requirement.required_shape,
        status=status,
        next_action=requirement.next_action,
        best_run_id=str(record.get("run_id", "")) or None,
        pipeline_family=str(record.get("pipeline_family", "")) or None,
        scope=record_scope(record),
        row_count=int(record.get("row_count") or 0),
        semantic_per_item_f1=semantic_item,
        semantic_per_letter_f1=semantic_letter,
        benchmark_per_item_f1=benchmark_item,
        benchmark_per_letter_f1=benchmark_letter,
        evidence_validity_rate=_optional_float(metrics.get("evidence_validity_rate")),
        call_failures=_optional_int(metrics.get("call_failures")),
        parse_failures=_optional_int(metrics.get("parse_failures")),
        routed_or_dropped=routed_or_dropped,
        artifact_paths=tuple(str(path) for path in (record.get("artifact_paths") or ())),
        gap=gap,
    )


def _metric_pair_values(
    metrics: Mapping[str, Any],
    *,
    all9_key: str,
    sf_key: str,
) -> tuple[float | None, float | None]:
    item = _optional_float(metrics.get(f"{all9_key}_per_item_f1"))
    letter = _optional_float(metrics.get(f"{all9_key}_per_letter_f1"))
    if item is not None or letter is not None:
        return item, letter
    return (
        _optional_float(metrics.get(f"{sf_key}_per_item_f1")),
        _optional_float(metrics.get(f"{sf_key}_per_letter_f1")),
    )


def _best_metric(record: Mapping[str, Any]) -> float | None:
    metrics = record.get("primary_metrics") or {}
    _item, letter = _metric_pair_values(metrics, all9_key="benchmark", sf_key="sf_benchmark")
    return letter


def _routed_or_dropped(metrics: Mapping[str, Any]) -> str | None:
    parts: list[str] = []
    if metrics.get("mentions_routed") is not None:
        parts.append(f"routed={metrics['mentions_routed']}")
    if metrics.get("n_evidence_invalid") is not None:
        parts.append(f"evidence_invalid={metrics['n_evidence_invalid']}")
    if metrics.get("mentions_total") is not None and metrics.get("mentions_scored") is not None:
        total = _optional_int(metrics.get("mentions_total")) or 0
        scored = _optional_int(metrics.get("mentions_scored")) or 0
        parts.append(f"dropped={max(total - scored, 0)}")
    return ", ".join(parts) if parts else None


def _metric_pair(item: float | None, letter: float | None) -> str:
    if item is None and letter is None:
        return "-"
    return f"{_fmt_float(item)}/{_fmt_float(letter)}"


def _reliability_cell(status: TrackStatus) -> str:
    parts = []
    if status.call_failures is not None:
        parts.append(f"calls={status.call_failures}")
    if status.parse_failures is not None:
        parts.append(f"parse={status.parse_failures}")
    if status.evidence_validity_rate is not None:
        parts.append(f"ev={status.evidence_validity_rate:.3f}")
    if status.routed_or_dropped:
        parts.append(status.routed_or_dropped)
    return _md("; ".join(parts) if parts else "-")


def _run_cell(status: TrackStatus) -> str:
    if not status.best_run_id:
        return "-"
    family = f"<br>`{status.pipeline_family}`" if status.pipeline_family else ""
    return f"`{status.best_run_id}`{family}"


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _fmt_float(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f}"


def _md(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")
