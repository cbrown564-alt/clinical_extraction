#!/usr/bin/env python3
"""Documentation sprawl hygiene gates (Path D).

Rules enforced
--------------
1. Repository root may contain only AGENTS.md, README.md, CONTEXT.md,
   PROJECT_STATUS.md, and VLLM.md as markdown files.
2. No underscore-prefixed directories at repository root (orphan dumps).
3. When experiments/ is present, experiments/*.md at repo root must exactly
   match the retained-evidence allowlist. A public clone without that tree
   skips this check.
4. Generated output roots must never be tracked.

Run: python scripts/check_doc_hygiene.py
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

ROOT_MARKDOWN_ALLOWED = frozenset(
    {"AGENTS.md", "README.md", "CONTEXT.md", "PROJECT_STATUS.md", "VLLM.md"}
)
ALLOWLIST_PATH = Path(__file__).resolve().parent / "doc_hygiene_experiments_root_allowlist.txt"
FORBIDDEN_TOOL_STATE = (".claude", ".playwright-cli", ".zcode")
FORBIDDEN_TRACKED_ROOTS = (".tmp", "logs", "mlruns", "output", "scratch", "tmp")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_allowlist() -> frozenset[str]:
    lines = ALLOWLIST_PATH.read_text(encoding="utf-8").splitlines()
    return frozenset(line.strip() for line in lines if line.strip())


def check_root_markdown(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.glob("*.md")):
        if path.name not in ROOT_MARKDOWN_ALLOWED:
            violations.append(
                f"unexpected root markdown: {path.name} "
                f"(allowed: {', '.join(sorted(ROOT_MARKDOWN_ALLOWED))})"
            )
    return violations


def check_root_underscore_dirs(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.iterdir()):
        if path.is_dir() and path.name.startswith("_"):
            violations.append(
                f"underscore-prefixed root directory: {path.name}/ "
                "(use docs/research/error_analysis/ or experiments/archive/)"
            )
    return violations


def existing_tracked_paths(root: Path) -> tuple[str, ...]:
    """Return tracked files that still exist in the working tree."""

    result = subprocess.run(
        ["git", "ls-files", "--cached"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return tuple(
        path
        for path in result.stdout.splitlines()
        if _is_file_without_access_error(root / Path(path))
    )


def check_forbidden_tool_state(
    root: Path, *, tracked_paths: Sequence[str] | None = None
) -> list[str]:
    """Reject checked-in state produced by local coding and browser tools."""

    paths = existing_tracked_paths(root) if tracked_paths is None else tracked_paths
    return [
        f"tool-generated state directory: {name}/ "
        "(keep agent configuration outside the repository)"
        for name in FORBIDDEN_TOOL_STATE
        if any(path == name or path.startswith(f"{name}/") for path in paths)
    ]


def check_forbidden_tracked_roots(
    root: Path, *, tracked_paths: Sequence[str] | None = None
) -> list[str]:
    """Reject generated output and scratch directories committed at repo root."""

    paths = existing_tracked_paths(root) if tracked_paths is None else tracked_paths
    return [
        f"generated output directory is tracked: {name}/"
        for name in FORBIDDEN_TRACKED_ROOTS
        if any(path == name or path.startswith(f"{name}/") for path in paths)
    ]


def _is_file_without_access_error(path: Path) -> bool:
    """Treat inaccessible stale paths like absent working-tree files."""

    try:
        return path.is_file()
    except OSError:
        return False


def check_experiments_root_allowlist(
    root: Path,
    allowlist: frozenset[str],
    *,
    tracked_paths: Sequence[str] | None = None,
) -> list[str]:
    experiments = root / "experiments"
    if not experiments.is_dir():
        return []

    paths = existing_tracked_paths(root) if tracked_paths is None else tracked_paths
    current = frozenset(
        Path(path).name
        for path in paths
        if path.startswith("experiments/")
        and path.count("/") == 1
        and path.endswith(".md")
    )
    unexpected = sorted(current - allowlist)
    missing = sorted(allowlist - current)
    if not unexpected and not missing:
        return []

    violations = []
    if unexpected:
        violations.append(
            "experiments/*.md outside retained allowlist: " + ", ".join(unexpected)
        )
    if missing:
        violations.append(
            "retained experiments/*.md missing from the working tree: " + ", ".join(missing)
        )
    return violations


def check_doc_hygiene(root: Path | None = None) -> list[str]:
    base = repo_root() if root is None else root
    allowlist = load_allowlist()
    tracked_paths = existing_tracked_paths(base)
    return (
        check_root_markdown(base)
        + check_root_underscore_dirs(base)
        + check_forbidden_tool_state(base, tracked_paths=tracked_paths)
        + check_forbidden_tracked_roots(base, tracked_paths=tracked_paths)
        + check_experiments_root_allowlist(base, allowlist, tracked_paths=tracked_paths)
    )


def main() -> int:
    violations = check_doc_hygiene()
    if not violations:
        print("doc-hygiene gates: OK")
        return 0

    print("doc-hygiene gate violations:", file=sys.stderr)
    for item in violations:
        print(f"  - {item}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
