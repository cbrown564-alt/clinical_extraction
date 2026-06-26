"""MLflow local observability doctor.

Prints install status, environment configuration, and guardrail warnings.
The run registry remains canonical; this command is diagnostic only.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from clinical_extraction.core.mlflow_tracking import (
    MLFLOW_ALLOW_FILE_STORE_ENV,
    MLFLOW_DISABLED_ENV,
    MLFLOW_STRICT_ENV,
    MLFLOW_TRACKING_URI_ENV,
    mlflow_available,
)
from clinical_extraction.core.paths import discover_repo_root, resolve_under_root

DEFAULT_REGISTRY_PATH = Path("experiments") / "registry.jsonl"
DEFAULT_MLRUNS_DIR = Path("mlruns")


@dataclass(frozen=True)
class MlflowDoctorReport:
    """Structured doctor output for tests and machine-readable checks."""

    repo_root: str
    mlflow_installed: bool
    mlflow_version: str | None
    mirroring_disabled: bool
    strict_mode: bool
    tracking_uri: str | None
    tracking_uri_source: str
    allow_file_store: str | None
    mlruns_path: str
    mlruns_exists: bool
    mlruns_run_count: int | None
    registry_path: str
    registry_exists: bool
    registry_row_count: int | None
    warnings: tuple[str, ...]
    ready_for_sync: bool


def build_doctor_report(
    *,
    repo_root: Path,
    registry_path: Path = DEFAULT_REGISTRY_PATH,
    mlruns_dir: Path = DEFAULT_MLRUNS_DIR,
) -> MlflowDoctorReport:
    """Collect MLflow install/config/status without mutating tracking state."""

    root = repo_root.resolve()
    resolved_registry = resolve_under_root(root, registry_path)
    resolved_mlruns = resolve_under_root(root, mlruns_dir)
    tracking_uri, tracking_uri_source = _resolve_tracking_uri(resolved_mlruns)
    warnings = _build_warnings(
        root=root,
        tracking_uri=tracking_uri,
        tracking_uri_source=tracking_uri_source,
        mlruns_path=resolved_mlruns,
        registry_path=resolved_registry,
    )
    ready = (
        mlflow_available()
        and os.getenv(MLFLOW_DISABLED_ENV) != "1"
        and resolved_registry.exists()
    )
    return MlflowDoctorReport(
        repo_root=str(root),
        mlflow_installed=mlflow_available(),
        mlflow_version=_mlflow_version(),
        mirroring_disabled=os.getenv(MLFLOW_DISABLED_ENV) == "1",
        strict_mode=os.getenv(MLFLOW_STRICT_ENV) == "1",
        tracking_uri=tracking_uri,
        tracking_uri_source=tracking_uri_source,
        allow_file_store=os.getenv(MLFLOW_ALLOW_FILE_STORE_ENV),
        mlruns_path=str(resolved_mlruns),
        mlruns_exists=resolved_mlruns.exists(),
        mlruns_run_count=_count_mlruns(resolved_mlruns),
        registry_path=str(resolved_registry),
        registry_exists=resolved_registry.exists(),
        registry_row_count=_count_registry_rows(resolved_registry),
        warnings=warnings,
        ready_for_sync=ready,
    )


def render_doctor_report(report: MlflowDoctorReport) -> str:
    """Render a compact human-facing doctor report."""

    lines = [
        "# MLflow local observability doctor",
        "",
        "## Status",
        f"- Repo root: {report.repo_root}",
        f"- MLflow installed: {'yes' if report.mlflow_installed else 'no'}",
    ]
    if report.mlflow_version:
        lines.append(f"- MLflow version: {report.mlflow_version}")
    lines.extend(
        [
            f"- Mirroring disabled ({MLFLOW_DISABLED_ENV}=1): "
            f"{'yes' if report.mirroring_disabled else 'no'}",
            f"- Strict mode ({MLFLOW_STRICT_ENV}=1): {'yes' if report.strict_mode else 'no'}",
            f"- Tracking URI: {report.tracking_uri or 'unset'}",
            f"- Tracking URI source: {report.tracking_uri_source}",
            f"- {MLFLOW_ALLOW_FILE_STORE_ENV}: {report.allow_file_store or 'unset'}",
            f"- Local store: {report.mlruns_path} "
            f"({'exists' if report.mlruns_exists else 'missing'})",
        ]
    )
    if report.mlruns_run_count is not None:
        lines.append(f"- Local runs indexed: {report.mlruns_run_count}")
    lines.extend(
        [
            f"- Registry: {report.registry_path} "
            f"({'exists' if report.registry_exists else 'missing'})",
        ]
    )
    if report.registry_row_count is not None:
        lines.append(f"- Registry rows: {report.registry_row_count}")
    lines.append(f"- Ready for sync: {'yes' if report.ready_for_sync else 'no'}")
    lines.extend(["", "## Guardrails"])
    lines.append(
        "- `experiments/registry.jsonl`, reports, and predeclarations remain the claim-of-record."
    )
    lines.append(
        "- MLflow is optional observability only; missing MLflow must not break runners."
    )
    lines.append(
        "- Restricted surfaces (Gan test450, ExECTv2 full-200/holdout) stay aggregate-only."
    )
    lines.append("- Raw row-level traces stay disabled unless a later protocol authorizes them.")
    if report.warnings:
        lines.extend(["", "## Warnings"])
        lines.extend(f"- {warning}" for warning in report.warnings)
    else:
        lines.extend(["", "## Warnings", "- none"])
    lines.extend(
        [
            "",
            "## Next commands",
            "Install optional MLflow support:",
            '  uv pip install -e ".[dev,mlops]"',
            "Dry-run a registry mirror plan:",
            "  clinical-extraction-mlflow-sync --since-date 2026-06-24",
            "Mirror the same-core dev140 parent/child group:",
            "  clinical-extraction-mlflow-sync --same-core-dev140-group --sync",
            "Start the local UI (PowerShell):",
            '  $env:MLFLOW_TRACKING_URI = "file:C:/path/to/repo/mlruns"',
            '  mlflow server --backend-store-uri $env:MLFLOW_TRACKING_URI --port 5000',
            "",
            "See docs/runbooks/mlflow_local_tracking.md for the full local runbook.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for MLflow local observability checks."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--mlruns", type=Path, default=DEFAULT_MLRUNS_DIR)
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    report = build_doctor_report(
        repo_root=repo_root,
        registry_path=args.registry,
        mlruns_dir=args.mlruns,
    )
    if args.json:
        print(json.dumps(asdict(report), indent=2, sort_keys=True))
    else:
        print(render_doctor_report(report), end="")
    if not report.ready_for_sync:
        raise SystemExit(1)


def _build_warnings(
    *,
    root: Path,
    tracking_uri: str | None,
    tracking_uri_source: str,
    mlruns_path: Path,
    registry_path: Path,
) -> tuple[str, ...]:
    warnings: list[str] = []
    if not mlflow_available():
        warnings.append(
            'MLflow is not installed. Install with `uv pip install -e ".[dev,mlops]"`.'
        )
    if os.getenv(MLFLOW_DISABLED_ENV) == "1":
        warnings.append(f"{MLFLOW_DISABLED_ENV}=1 disables all mirroring.")
    if os.getenv(MLFLOW_STRICT_ENV) == "1":
        warnings.append(
            f"{MLFLOW_STRICT_ENV}=1 makes MLflow logging failures fatal after registry writes."
        )
    if not registry_path.exists():
        warnings.append(f"Registry file is missing: {registry_path}")
    if tracking_uri_source == "default_repo_local":
        if os.getenv(MLFLOW_ALLOW_FILE_STORE_ENV) not in {None, "true"}:
            warnings.append(
                f"{MLFLOW_ALLOW_FILE_STORE_ENV} should be true for the default repo-local file store."
            )
    elif tracking_uri and not tracking_uri.startswith("file:"):
        warnings.append(
            "Tracking URI is not a local file store. Keep remote tracking out of paper claims."
        )
    if mlflow_available() and not mlruns_path.exists():
        warnings.append("Local mlruns/ is missing. The first successful sync will create it.")
    if mlruns_path.exists() and _count_mlruns(mlruns_path) == 0:
        warnings.append(
            "Local mlruns/ exists but has no indexed runs yet. Run a dry-run sync, then `--sync`."
        )
    artifact_policy = os.getenv("CLINICAL_EXTRACTION_MLFLOW_ARTIFACT_POLICY")
    if artifact_policy == "full_artifacts":
        warnings.append(
            "CLINICAL_EXTRACTION_MLFLOW_ARTIFACT_POLICY=full_artifacts may copy large row-level files."
        )
    trace_policy = os.getenv("CLINICAL_EXTRACTION_MLFLOW_TRACE_POLICY")
    if trace_policy not in {None, "disabled"}:
        warnings.append(
            "Trace policy is not disabled. Confirm split discipline before enabling traces."
        )
    if (root / ".git").exists() and mlruns_path.exists() and _directory_size_bytes(mlruns_path) > 0:
        gitignore = (root / ".gitignore").read_text(encoding="utf-8")
        if "mlruns" not in gitignore:
            warnings.append("mlruns/ is not listed in .gitignore.")
    return tuple(warnings)


def _resolve_tracking_uri(mlruns_dir: Path) -> tuple[str | None, str]:
    explicit = os.getenv(MLFLOW_TRACKING_URI_ENV)
    if explicit:
        return explicit, "environment"
    return f"file:{mlruns_dir.as_posix()}", "default_repo_local"


def _mlflow_version() -> str | None:
    if not mlflow_available():
        return None
    import importlib

    module = importlib.import_module("mlflow")
    return str(getattr(module, "__version__", "unknown"))


def _count_registry_rows(registry_path: Path) -> int | None:
    if not registry_path.exists():
        return None
    count = 0
    for line in registry_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            count += 1
    return count


def _count_mlruns(mlruns_dir: Path) -> int | None:
    if not mlruns_dir.exists():
        return None
    count = 0
    for experiment_dir in mlruns_dir.iterdir():
        if not experiment_dir.is_dir():
            continue
        for child in experiment_dir.iterdir():
            if child.is_dir() and (child / "meta.yaml").exists():
                count += 1
    return count


def _directory_size_bytes(path: Path) -> int:
    total = 0
    for child in path.rglob("*"):
        if child.is_file():
            total += child.stat().st_size
    return total


def _repo_root() -> Path:
    return discover_repo_root(start=Path(__file__), include_cwd=False)


if __name__ == "__main__":
    main()
