"""Markdown report rendering for Gan 2026 run-registry entries."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from clinical_extraction.core.registry import (
    MetricValue,
    RunDecision,
    RunRegistryEntry,
)

DECISION_RENDER_ORDER: tuple[RunDecision, ...] = (
    "reliability_scorecard",
    "promote",
    "promote_hybrid_structured_events_direction",
    "promote_to_phase3_report",
    "revise",
    "reject",
    "inform_phase7",
    "phase4_complete",
    "inform_phase4",
    "phase3_complete_gpt41mini",
    "inform_phase3",
    "inform_architecture_loop",
    "clinical_recovery_reporting",
    "superseded",
    "historical",
)


def render_run_registry_markdown(entries: Sequence[RunRegistryEntry]) -> str:
    """Render registry entries as a compact human-facing Markdown index."""

    lines = [
        "# Gan 2026 Run Registry",
        "",
        "Generated from `experiments/registry.jsonl`. The JSONL file remains the canonical "
        "machine-readable registry.",
        "",
        "**Start here for humans:** [`experiments/KEY_EXPERIMENTS.md`](../../KEY_EXPERIMENTS.md) "
        "— one-screen summaries of the ~12 runs that matter. "
        "Term definitions: [`docs/reference/plain_language_glossary.md`](../../docs/reference/plain_language_glossary.md).",
        "",
        "### Gan holdout promotion ladder (Gates 1–4)",
        "",
        "- **Gate 1 — Validation hard-slice audit:** Selector gains must not hide brittle "
        "behavior in weak families.",
        "- **Gate 2 — Robustness panels:** Stress-test gates on adversarial component states "
        "before holdout spend.",
        "- **Gate 3 — Test source-symmetry preflight:** Hash-pin every test450 component role.",
        "- **Gate 4 — Locked test450 aggregate audit:** User-authorized, aggregate-only readout "
        "after Gates 1–3; no row-level tuning.",
        "",
    ]
    ordered_decisions = [
        *DECISION_RENDER_ORDER,
        *sorted({entry.decision for entry in entries} - set(DECISION_RENDER_ORDER)),
    ]
    for decision in ordered_decisions:
        group = sorted(
            (entry for entry in entries if entry.decision == decision),
            key=lambda entry: (entry.date, entry.run_id),
            reverse=True,
        )
        if not group:
            continue
        lines.extend([f"## {_title(decision)}", ""])
        for entry in group:
            lines.extend(_entry_markdown_lines(entry))
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_run_registry_markdown(entries: Sequence[RunRegistryEntry], path: Path) -> None:
    """Write a Markdown index for a run registry."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_run_registry_markdown(entries), encoding="utf-8")


def _entry_markdown_lines(entry: RunRegistryEntry) -> list[str]:
    metrics = _format_metrics(entry.primary_metrics)
    artifacts = ", ".join(f"`{path}`" for path in entry.artifact_paths)
    lines = [
        f"### `{entry.run_id}`",
        f"- Date/split: `{entry.date}`; `{entry.split}`; `{entry.row_count}` rows.",
        (
            f"- Pipeline: `{entry.pipeline_family}`; mode `{entry.mode}`; "
            f"replay `{entry.replay_status}`."
        ),
        f"- Model role: {entry.model_role}; model `{entry.model}`.",
    ]
    if entry.registry_roles:
        roles = ", ".join(f"`{role}`" for role in entry.registry_roles)
        lines.append(f"- Registry roles: {roles}.")
    if entry.repair_mode:
        lines.append(f"- Repair mode/config: `{entry.repair_mode}`.")
    if metrics:
        lines.append(f"- Primary metrics: {metrics}.")
    if entry.evidence_validity:
        lines.append(_sentence_line("Evidence validity", entry.evidence_validity))
    if entry.cache_reuse_source:
        lines.append(_sentence_line("Cache/reuse source", entry.cache_reuse_source))
    if entry.supersedes:
        supersedes = ", ".join(f"`{run_id}`" for run_id in entry.supersedes)
        lines.append(f"- Supersedes: {supersedes}.")
    if entry.superseded_by:
        lines.append(f"- Superseded by: `{entry.superseded_by}`.")
    if entry.claim_language_notes:
        lines.append(f"- Claim language: {entry.claim_language_notes}")
    lines.append(f"- Artifacts: {artifacts}.")
    return lines


def _format_metrics(metrics: Mapping[str, MetricValue]) -> str:
    return ", ".join(f"{key}={metrics[key]}" for key in sorted(metrics))


def _sentence_line(label: str, value: str) -> str:
    ending = "" if value.endswith((".", "!", "?")) else "."
    return f"- {label}: {value}{ending}"


def _title(decision: RunDecision) -> str:
    return decision.replace("_", " ").title()
