"""Preflight gate for the Plan 11 family-routed LLM-first comparison.

This module is deliberately non-executing: it prepares the checklist a
coordinator should review before launching the dev ladder, but it never calls a
model or reads held-out rows.
"""

from __future__ import annotations

import ast
import importlib.util
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

PLAN11_PATH = Path("docs/plans/exectv2/11_llm_first_essential_clinical_evaluation_plan.md")
PREDECLARATION_PATH = Path(
    "docs/experiments/exectv2/predeclarations/"
    "exectv2_family_routed_llm_first_comparison_predeclaration_2026-06-18.md"
)
PI_PRESERVATION_PATH = Path(
    "docs/experiments/exectv2/predeclarations/"
    "exectv2_prescription_investigations_shared_pass_preservation_2026-06-18.md"
)
SF_SCHEMA_DESIGN_PATH = Path(
    "docs/experiments/exectv2/seizure_frequency/"
    "exectv2_sf_llm_first_event_state_schema_design_2026-06-18.md"
)
REQUIRED_ROUTE_MODULE = (
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm."
    "llm_family_routed_llm_first"
)
SCHEMA_BASE_MODULE = (
    "clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm."
    "llm_only_clinical_findings"
)
SCHEMA_BASE_SOURCE_PATH = Path(
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
    "llm_only_clinical_findings.py"
)
REQUIRED_SCHEMA_BASE_CLASSES = (
    "ClinicalFindingsRecord",
    "EventFrameRecord",
    "ClinicalFindingRecord",
)

DEV_LADDER_STAGES = ("pilot25", "dev140")
BLOCKED_SURFACES = ("full-200", "test450", "holdout", "full 200")
PI_ROUTE_POLICY = "shared_broad_pass_only"


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class FamilyRoutedPreflightReport:
    """Machine-readable readiness report for the gated comparison."""

    checks: tuple[PreflightCheck, ...]
    planned_dev_ladder: tuple[str, ...] = DEV_LADDER_STAGES
    blocked_surfaces: tuple[str, ...] = BLOCKED_SURFACES

    @property
    def can_run_dev_ladder(self) -> bool:
        return all(check.passed for check in self.checks)

    @property
    def blockers(self) -> tuple[PreflightCheck, ...]:
        return tuple(check for check in self.checks if not check.passed)


def build_family_routed_preflight(root: Path | str = Path(".")) -> FamilyRoutedPreflightReport:
    """Evaluate whether the predeclared routed dev ladder may run."""

    repo_root = Path(root)
    plan_text = _read_text(repo_root / PLAN11_PATH)
    predeclaration_text = _read_text(repo_root / PREDECLARATION_PATH)
    pi_preservation_text = _read_text(repo_root / PI_PRESERVATION_PATH)
    schema_text = _read_text(repo_root / SF_SCHEMA_DESIGN_PATH)
    checks = (
        PreflightCheck(
            "plan11_artifact_present",
            bool(plan_text),
            _presence_detail(PLAN11_PATH, bool(plan_text)),
        ),
        PreflightCheck(
            "routed_predeclaration_present",
            bool(predeclaration_text),
            _presence_detail(PREDECLARATION_PATH, bool(predeclaration_text)),
        ),
        PreflightCheck(
            "prescription_investigations_shared_pass_preserved",
            _pi_preservation_policy_present(pi_preservation_text),
            (
                "Prescription/Investigations must remain on the shared broad pass "
                "unless a fresh no-call ablation is predeclared and passes"
            ),
        ),
        PreflightCheck(
            "dev_ladder_scope_predeclared",
            _contains_all(predeclaration_text, DEV_LADDER_STAGES)
            and "full-200/test audit blocked" in predeclaration_text.lower(),
            "predeclaration must name pilot25 -> dev140 and block full-200/test execution",
        ),
        PreflightCheck(
            "sf_event_state_design_present",
            "EventFrameRecord" in schema_text and "ClinicalFindingRecord" in schema_text,
            "SF design must reference the event/state schema base classes",
        ),
        PreflightCheck(
            "sf_schema_base_importable",
            _schema_base_available(repo_root),
            (
                f"{SCHEMA_BASE_MODULE} must expose or declare "
                "ClinicalFindingsRecord/EventFrameRecord"
            ),
        ),
        PreflightCheck(
            "plan11_routed_adapter_contract_implemented",
            _module_importable(REQUIRED_ROUTE_MODULE),
            f"missing routed adapter/runner module: {REQUIRED_ROUTE_MODULE}",
        ),
        PreflightCheck(
            "explicit_dev_ladder_authorization_present",
            predeclaration_authorizes_dev_ladder(predeclaration_text),
            "predeclaration status must explicitly authorize the dev ladder before any run",
        ),
    )
    return FamilyRoutedPreflightReport(checks=checks)


def predeclaration_authorizes_dev_ladder(text: str) -> bool:
    """Return True only for an explicit dev-ladder authorization status line."""

    status = _status_line(text).lower()
    if not status or "not authorized" in status or "not executed" in status:
        return False
    return "authorized" in status and any(stage in status for stage in DEV_LADDER_STAGES)


def render_preflight_markdown(report: FamilyRoutedPreflightReport) -> str:
    decision = "GO" if report.can_run_dev_ladder else "BLOCKED - do not run"
    lines = [
        "# ExECTv2 Family-Routed LLM-First Comparison Preflight",
        "",
        f"- Decision: **{decision}**",
        f"- Planned dev ladder: `{' -> '.join(report.planned_dev_ladder)}`",
        "- Blocked surfaces: `Gan test450`, ExECTv2 full-200/test, holdout row-level review",
        f"- Prescription/Investigations route policy: `{PI_ROUTE_POLICY}`",
        "",
        "## Gate Checklist",
        "",
        "| Gate | Status | Detail |",
        "| --- | --- | --- |",
    ]
    for check in report.checks:
        status = "pass" if check.passed else "blocked"
        lines.append(f"| `{check.name}` | {status} | {check.detail} |")

    lines += [
        "",
        "## If The Gate Opens",
        "",
        "Run only the predeclared dev ladder:",
        "",
        "1. `pilot25`: output-contract, parse/schema, evidence, and catastrophic route smoke.",
        "2. `dev140`: primary development comparison after the pilot gate passes.",
        "",
        "Do not run full-200/test, inspect Gan `test450`, inspect holdout rows, or tune from "
        "holdout-facing artifacts under this predeclaration.",
    ]
    return "\n".join(lines)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _contains_all(text: str, needles: Iterable[str]) -> bool:
    lower = text.lower()
    return all(needle.lower() in lower for needle in needles)


def _pi_preservation_policy_present(text: str) -> bool:
    lower = text.lower()
    return (
        PI_ROUTE_POLICY in text
        and "preserve prescription and investigations" in lower
        and (
            "fresh predeclaration" in lower
            or "fresh predeclared" in lower
            or "new predeclaration" in lower
        )
        and "no-call" in lower
        and "regression" in lower
    )


def _presence_detail(path: Path, present: bool) -> str:
    return f"{path.as_posix()} {'present' if present else 'missing'}"


def _status_line(text: str) -> str:
    for line in text.splitlines():
        if line.lower().startswith("status:"):
            return line
    return ""


def _module_importable(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, AttributeError, ValueError):
        return False


def _schema_base_available(repo_root: Path) -> bool:
    if _schema_base_importable():
        return True
    return _schema_base_classes_declared(repo_root / SCHEMA_BASE_SOURCE_PATH)


def _schema_base_importable() -> bool:
    try:
        module = __import__(SCHEMA_BASE_MODULE, fromlist=["ClinicalFindingsRecord"])
    except ImportError:
        return False
    return all(hasattr(module, name) for name in REQUIRED_SCHEMA_BASE_CLASSES)


def _schema_base_classes_declared(path: Path) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, SyntaxError):
        return False
    declared = {
        node.name
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    return all(name in declared for name in REQUIRED_SCHEMA_BASE_CLASSES)
