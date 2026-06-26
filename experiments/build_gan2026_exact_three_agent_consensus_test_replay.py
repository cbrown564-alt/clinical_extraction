"""Build the exact three-agent consensus test component for v0.9 source parity.

This is a no-call component replay. It applies the validation consensus rule to
locked test450 source artifacts: keep the rules-tool floor unless GPT, Qwen, and
DeepSeek structured-event components emit the same non-null final label.

The emitted component intentionally avoids row-level correctness, failures,
evidence, selected events, and transitions. Those remain outside the component
freeze and any later Gate 4 readout must be aggregate-only.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.structured_event_consensus import (
    AgentVote,
    build_exact_label_consensus_decision,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DATE = "2026-06-26"
RUN_ID = f"gan2026_agentic_structured_event_consensus_unanimous_exact_test450_{DATE}"
JSONL_OUT = EXPERIMENTS / f"{RUN_ID}.jsonl"
MD_OUT = EXPERIMENTS / f"{RUN_ID}.md"

RULES_TOOL_BASELINE = (
    EXPERIMENTS
    / "gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_"
    "v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl"
)
GPT_STRUCTURED_EVENTS = (
    EXPERIMENTS
    / "gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_"
    "2026-06-09.jsonl"
)
QWEN_STRUCTURED_EVENTS_PATCH = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_"
    "qwen3635b_2026-06-13.jsonl"
)
DEEPSEEK_STRUCTURED_EVENTS = (
    EXPERIMENTS / "gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl"
)


def main() -> None:
    rules_rows = _load_data_rows(RULES_TOOL_BASELINE)
    agent_rows = {
        "gpt": _rows_by_source_index(_load_data_rows(GPT_STRUCTURED_EVENTS)),
        "qwen": _rows_by_source_index(_load_data_rows(QWEN_STRUCTURED_EVENTS_PATCH)),
        "deepseek": _rows_by_source_index(_load_data_rows(DEEPSEEK_STRUCTURED_EVENTS)),
    }

    rows: list[dict[str, Any]] = []
    reason_counts: Counter[str] = Counter()
    action_counts: Counter[str] = Counter()
    missing_agent_rows: Counter[str] = Counter()

    for rules_row in rules_rows:
        source_row_index = rules_row.get("source_row_index")
        if source_row_index is None:
            continue
        votes: list[AgentVote] = []
        for agent_id, rows_by_id in agent_rows.items():
            agent_row = rows_by_id.get(int(source_row_index))
            if agent_row is None:
                missing_agent_rows[agent_id] += 1
            votes.append(
                AgentVote(
                    agent_id=agent_id,
                    final_label=_structured_event_label(agent_row),
                )
            )
        decision = build_exact_label_consensus_decision(
            source_row_index=int(source_row_index),
            baseline_label=_rules_top_label(rules_row),
            votes=votes,
        )
        reason_counts[decision.reason] += 1
        action_counts[decision.action] += 1
        rows.append(
            {
                "source_row_index": int(source_row_index),
                "baseline_label": decision.baseline_label,
                "consensus_final_label": decision.final_label,
                "consensus_decision": {
                    "action": decision.action,
                    "reason": decision.reason,
                    "consensus_label": decision.consensus_label,
                    "vote_labels": {
                        vote.agent_id: vote.final_label for vote in decision.votes
                    },
                },
            }
        )

    metadata = {
        "artifact_kind": "gan2026_agentic_structured_event_consensus_replay",
        "pipeline_family": "agentic_structured_event_consensus",
        "run_id": RUN_ID,
        "date": DATE,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "split": "test",
        "split_manifest": "gan2026_split_v1",
        "mode": "no_call_replay",
        "condition": "rules_tool_plus_three_structured_event_agents_unanimous_exact_label_v0",
        "prompt_version": "gan2026_structured_event_consensus_unanimous_exact_v0",
        "selector": (
            "exact-label unanimity across GPT, Qwen, and DeepSeek structured-event "
            "agents; otherwise keep the rules-tool baseline"
        ),
        "source_artifacts": {
            "rules_tool_baseline": _rel(RULES_TOOL_BASELINE),
            "structured_event_agent_gpt41mini_v05": _rel(GPT_STRUCTURED_EVENTS),
            "structured_event_agent_qwen3635b_recent_patch": _rel(
                QWEN_STRUCTURED_EVENTS_PATCH
            ),
            "structured_event_agent_deepseek_v06": _rel(DEEPSEEK_STRUCTURED_EVENTS),
        },
        "source_artifact_sha256": {
            "rules_tool_baseline": _sha256(RULES_TOOL_BASELINE),
            "structured_event_agent_gpt41mini_v05": _sha256(GPT_STRUCTURED_EVENTS),
            "structured_event_agent_qwen3635b_recent_patch": _sha256(
                QWEN_STRUCTURED_EVENTS_PATCH
            ),
            "structured_event_agent_deepseek_v06": _sha256(DEEPSEEK_STRUCTURED_EVENTS),
        },
        "row_count": len(rows),
        "summary": {
            "actions": dict(sorted(action_counts.items())),
            "reasons": dict(sorted(reason_counts.items())),
            "missing_agent_rows": dict(sorted(missing_agent_rows.items())),
        },
        "inspection_boundary": {
            "row_level_correctness_written": False,
            "row_level_failures_written": False,
            "row_level_evidence_written": False,
            "row_level_selected_events_written": False,
            "row_level_transitions_written": False,
        },
        "claim_boundary": (
            "Exact three-agent test consensus component for source parity only. "
            "It is not a Gate 4 result and does not authorize tuning or row-level "
            "test failure inspection."
        ),
    }

    _write_jsonl(metadata, rows)
    md_text = _render_markdown(metadata)
    MD_OUT.write_text(md_text, encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": True,
                "run_id": RUN_ID,
                "rows": len(rows),
                "jsonl": _rel(JSONL_OUT),
                "md": _rel(MD_OUT),
            },
            sort_keys=True,
        )
    )


def _load_data_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if isinstance(row, dict) and "_metadata" in row:
            continue
        rows.append(row)
    return rows


def _rows_by_source_index(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    return {
        int(row["source_row_index"]): row
        for row in rows
        if row.get("source_row_index") is not None
    }


def _rules_top_label(row: dict[str, Any]) -> str | None:
    scores = row.get("scores") or {}
    if isinstance(scores, dict):
        deterministic_top = scores.get("deterministic_top") or {}
        if isinstance(deterministic_top, dict) and deterministic_top.get("final_label"):
            return str(deterministic_top["final_label"])
    diagnostics = row.get("deterministic_diagnostics") or {}
    if isinstance(diagnostics, dict):
        final_selection = diagnostics.get("final_selection") or {}
        if isinstance(final_selection, dict) and final_selection.get("final_label"):
            return str(final_selection["final_label"])
    return None


def _structured_event_label(row: dict[str, Any] | None) -> str | None:
    if row is None:
        return None
    patched_label = row.get("patched_final_label")
    if patched_label is not None:
        return str(patched_label)
    structured = row.get("structured_record") or {}
    if isinstance(structured, dict):
        selection = structured.get("selection") or {}
        if isinstance(selection, dict) and selection.get("final_label") is not None:
            return str(selection["final_label"])
    return None


def _write_jsonl(metadata: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [json.dumps({"_metadata": metadata}, sort_keys=True)]
    lines.extend(json.dumps(row, sort_keys=True) for row in rows)
    JSONL_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_markdown(metadata: dict[str, Any]) -> str:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Agentic Structured-Event Consensus: Exact Three-Agent Test Replay",
        "",
        f"Date: {metadata['date']}",
        "",
        "## Experiment Unit",
        "",
        "- Work class: no-call component replay for exact v0.9 source parity.",
        "- Surface: locked `test450`, manifest `gan2026_split_v1`.",
        "- Policy: keep the rules-tool baseline unless GPT, Qwen, and DeepSeek "
        "structured-event agents emit the same non-null exact final label.",
        "- Inspection boundary: no row-level correctness, failures, evidence, "
        "selected events, or transitions are written.",
        "",
        "## Source Artifacts",
        "",
    ]
    for key, value in metadata["source_artifacts"].items():
        sha = metadata["source_artifact_sha256"][key]
        lines.append(f"- `{key}`: `{value}` (`{sha}`)")
    lines.extend(
        [
            "",
            "## Technical Summary",
            "",
            f"- Rows: `{metadata['row_count']}`",
            f"- Actions: `{summary['actions']}`",
            f"- Reasons: `{summary['reasons']}`",
            f"- Missing agent rows: `{summary['missing_agent_rows']}`",
            f"- JSONL artifact: `{_rel(JSONL_OUT)}`",
            "",
            "## Claim Boundary",
            "",
            metadata["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    main()
