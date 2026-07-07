"""Shared helpers for ExECTv2 aggregate-only validation audit reports."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from pathlib import Path
from typing import Any

from . import cross_model_reliability_analysis as reliability

REPO_ROOT = reliability.REPO_ROOT

FULL200_ARTIFACT: dict[str, str] = {
    "path": (
        "experiments/"
        "exectv2_holistic_finding_assembly_v08_full200_currentcode_"
        "gpt41mini_20260624.jsonl"
    ),
    "surface": "current-code v08-shape rich-schema holistic assembly",
    "eligibility": "eligible",
}

SURFACE = "rich-schema holistic assembly reliability scorecard"
SPLIT = "full-200 aggregate-only validation requested"


def git_head(repo_root: Path) -> str:
    try:
        head = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo_root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        dirty = (
            subprocess.run(
                ["git", "diff", "--quiet"],
                cwd=repo_root,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            != 0
        )
    except (OSError, subprocess.SubprocessError):
        return "unavailable"
    return f"{head}+dirty" if dirty else head


def count_jsonl_rows(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def round_rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def format_optional_float(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.4f}"


def gate(gate_name: str, outcome: str, note: str) -> dict[str, str]:
    return {"gate": gate_name, "outcome": outcome, "note": note}


def promotion_decision_from_gates(gates: Sequence[Mapping[str, str]]) -> str:
    return "promoted" if all(item["outcome"] == "pass" for item in gates) else "not_promoted"


def artifact_inventory_item(
    repo_root: Path,
    artifact: Mapping[str, str],
) -> dict[str, Any]:
    path = repo_root / str(artifact["path"])
    return {
        "path": artifact["path"],
        "exists": path.exists(),
        "rows": count_jsonl_rows(path) if path.exists() else 0,
        "surface": artifact["surface"],
        "eligible": path.exists() and artifact["eligibility"] == "eligible",
        "reason": artifact["reason"],
    }


def artifact_inventory_single(
    repo_root: Path,
    artifact: Mapping[str, str],
) -> list[dict[str, Any]]:
    return [artifact_inventory_item(repo_root, artifact)]


def artifact_inventory_multi(
    repo_root: Path,
    candidates: Sequence[Mapping[str, str]],
) -> list[dict[str, Any]]:
    return [artifact_inventory_item(repo_root, item) for item in candidates]


def stop_rule_outcome(
    *,
    validation: Mapping[str, Any] | None,
    promotion_decision: str,
    promoted_reason: str,
    blocked_reason: str = "No eligible aggregate validation artifact was available.",
) -> dict[str, Any]:
    return {
        "status": (
            "completed_current_code_surface_validation"
            if validation
            else "blocked_no_same_surface_full200_artifact"
        ),
        "validation_run_executed": bool(validation),
        "promotion_decision": promotion_decision,
        "reason": promoted_reason if promotion_decision == "promoted" else blocked_reason,
    }


def audit_envelope(
    *,
    audit_kind: str,
    repo_root: Path,
    scorer: str,
    row_inspection_boundary: str,
) -> dict[str, Any]:
    return {
        "audit_kind": audit_kind,
        "generated_on": date.today().isoformat(),
        "surface": SURFACE,
        "scorer": scorer,
        "split": SPLIT,
        "code_hash": git_head(repo_root),
        "row_inspection_boundary": row_inspection_boundary,
    }


def write_validation_report(
    *,
    build_audit: Callable[..., dict[str, Any]],
    render_markdown: Callable[[Mapping[str, Any]], str],
    repo_root: Path,
    report_path: Path,
) -> Path:
    audit = build_audit(repo_root=repo_root)
    out_path = repo_root / report_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_markdown(audit), encoding="utf-8")
    return out_path


def render_preflight_section(
    audit: Mapping[str, Any],
    *,
    title: str,
    status_line: str,
) -> list[str]:
    return [
        title,
        "",
        f"Date: {audit['generated_on']}",
        "",
        status_line,
        "",
        "## Preflight",
        "",
        f"- Surface: {audit['surface']}",
        f"- Scorer: `{audit['scorer']}`",
        f"- Split: `{audit['split']}`",
        f"- Code hash: `{audit['code_hash']}`",
        f"- Row-inspection boundary: {audit['row_inspection_boundary']}",
    ]


def render_artifact_inventory_section(
    inventory: Sequence[Mapping[str, Any]],
) -> list[str]:
    lines = [
        "",
        "## Validation Artifact Inventory",
        "",
        "| Artifact | Rows | Surface | Eligibility | Reason |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for item in inventory:
        eligibility = "eligible" if item["eligible"] else "ineligible"
        lines.append(
            f"| `{item['path']}` | {item['rows']} | {item['surface']} | "
            f"{eligibility} | {item['reason']} |"
        )
    return lines


def render_stop_rule_outcome_section(audit: Mapping[str, Any]) -> list[str]:
    stop = audit["stop_rule_outcome"]
    return [
        "",
        "## Stop-Rule Outcome",
        "",
        f"- Status: `{stop['status']}`",
        f"- Validation run executed: `{stop['validation_run_executed']}`",
        f"- Promotion decision: `{stop['promotion_decision']}`",
        f"- Reason: {stop['reason']}",
    ]


def render_promotion_gates_section(audit: Mapping[str, Any]) -> list[str]:
    lines = [
        "",
        "## Promotion Gates",
        "",
        "| Gate | Outcome | Note |",
        "| --- | --- | --- |",
    ]
    for gate_row in audit["promotion_gates"]:
        lines.append(f"| {gate_row['gate']} | {gate_row['outcome']} | {gate_row['note']} |")
    return lines


def render_report_footer(
    audit: Mapping[str, Any],
    result_paragraph: str,
) -> list[str]:
    return [
        "",
        "## Result",
        "",
        result_paragraph,
        "",
        f"Next action: {audit['next_action']}",
        "",
    ]
