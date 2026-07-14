#!/usr/bin/env python3
"""Documentation sprawl hygiene gates (Path D).

Rules enforced
--------------
1. Repository root may contain only AGENTS.md, README.md, CONTEXT.md, and
   PROJECT_STATUS.md as markdown files.
2. No underscore-prefixed directories at repository root (orphan dumps).
3. experiments/*.md at repo root is frozen to the allowlist snapshot unless
   deliberately extended in the same change.

Run: python scripts/check_doc_hygiene.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_MARKDOWN_ALLOWED = frozenset(
    {"AGENTS.md", "README.md", "CONTEXT.md", "PROJECT_STATUS.md"}
)
ALLOWLIST_PATH = Path(__file__).resolve().parent / "doc_hygiene_experiments_root_allowlist.txt"


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


def check_experiments_root_allowlist(root: Path, allowlist: frozenset[str]) -> list[str]:
    experiments = root / "experiments"
    if not experiments.is_dir():
        return [f"missing experiments/ directory at {experiments}"]

    current = frozenset(p.name for p in experiments.glob("*.md"))
    unexpected = sorted(current - allowlist)
    if not unexpected:
        return []

    return [
        "new experiments/*.md outside allowlist (move narrative to docs/experiments/ "
        "or append to scripts/doc_hygiene_experiments_root_allowlist.txt): " + ", ".join(unexpected)
    ]


def check_doc_hygiene(root: Path | None = None) -> list[str]:
    base = repo_root() if root is None else root
    allowlist = load_allowlist()
    return (
        check_root_markdown(base)
        + check_root_underscore_dirs(base)
        + check_experiments_root_allowlist(base, allowlist)
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
