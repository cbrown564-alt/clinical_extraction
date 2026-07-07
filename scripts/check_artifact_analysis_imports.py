#!/usr/bin/env python3
"""CI import-quarantine gate: freeze production imports of ``artifact_analysis/`` (P2-1).

Gate rule
---------
``gan2026/artifact_analysis/`` is a ~24k-LOC research/diagnostics layer. Production
code should **not grow new dependencies** on it. This gate **fails** if any
``*.py`` under ``src/clinical_extraction/`` imports from the ``artifact_analysis``
package **unless** that file is documented in ``ALLOWLIST`` below.

Scope
-----
- Scans every ``*.py`` under ``src/clinical_extraction/`` (skipping
  ``__pycache__``).
- **Skips files that live under any ``artifact_analysis/`` directory** — we police
  *importers* of the research layer, not the research layer's own internal wiring.
- A file "imports artifact_analysis" when an actual ``import`` / ``from ... import``
  statement references the ``artifact_analysis`` package. Detection is
  AST-based (with a regex fallback for files that fail to parse) so that mere
  string/comment mentions of ``artifact_analysis`` do **not** count.

Allowlist policy (day-1 rollout)
--------------------------------
``ALLOWLIST`` is **frozen** to the set of importers that exist *today*. The gate
fails on:

- **New importers** — a production file imports ``artifact_analysis`` and is not
  allowlisted.

Removing a dependency (deleting the import) is always permitted. To intentionally
add a new allowlisted importer, extend ``ALLOWLIST`` with a justification string
referencing the relevant decomposition/quarantine plan.

How to run
----------
::

    python scripts/check_artifact_analysis_imports.py
    pytest tests/test_artifact_analysis_import_gate.py

Exit code 0 when clean (prints ``artifact_analysis import gate: OK``); exit 1 when
unexpected importers are printed to stderr.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

SRC_PACKAGE = "src/clinical_extraction"

# The quarantined package name (also the directory name we skip when scanning).
ARTIFACT_ANALYSIS_PKG = "artifact_analysis"


# Paths are posix-relative to ``src/clinical_extraction/`` → justification.
#
# Frozen to the CURRENT importers of ``artifact_analysis`` (derived by scanning the
# tree). ``rule_ownership_audit.py`` is intentionally **absent**: it only mentions
# ``artifact_analysis`` inside a string literal, not an import, so the AST detector
# does not flag it.
#
# Sprint 6 (P2-1): all 14 day-1 importers were migrated to canonical production
# modules; the allowlist is empty until a new dependency is intentionally added.
ALLOWLIST: dict[str, str] = {}


_IMPORT_LINE_RE = re.compile(
    r"^\s*(?:from|import)\s+\S*" + re.escape(ARTIFACT_ANALYSIS_PKG),
    re.MULTILINE,
)


@dataclass(frozen=True)
class ImportViolation:
    """An unexpected (non-allowlisted) production importer of ``artifact_analysis``."""

    rel_path: str

    def format(self) -> str:
        return (
            f"{self.rel_path}: imports artifact_analysis but is not allowlisted "
            f"(add an ALLOWLIST entry with justification, or drop the dependency)"
        )


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def src_root(root: Path | None = None) -> Path:
    base = repo_root() if root is None else root
    return base / "src" / "clinical_extraction"


def _dotted_references_pkg(dotted: str | None) -> bool:
    """True if any dotted component equals the quarantined package name."""
    if not dotted:
        return False
    return ARTIFACT_ANALYSIS_PKG in dotted.split(".")


def file_imports_artifact_analysis(path: Path) -> bool:
    """Return True if ``path`` contains an import referencing ``artifact_analysis``.

    AST-based so string/comment mentions are ignored. Handles absolute imports
    (``from clinical_extraction...artifact_analysis import x``) and relative imports
    (``from ..artifact_analysis.foo import *``). Falls back to a line regex if the
    file cannot be parsed.
    """
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return bool(_IMPORT_LINE_RE.search(source))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _dotted_references_pkg(alias.name):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if _dotted_references_pkg(node.module):
                return True
            # e.g. ``from clinical_extraction...gan2026 import artifact_analysis``
            for alias in node.names:
                if alias.name == ARTIFACT_ANALYSIS_PKG:
                    return True
    return False


def iter_production_python_files(package_root: Path) -> list[tuple[str, Path]]:
    """Production ``*.py`` files, skipping ``__pycache__`` and the research layer."""
    files: list[tuple[str, Path]] = []
    for path in sorted(package_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        if ARTIFACT_ANALYSIS_PKG in path.parts:
            # The research layer's own internal imports are out of scope; we only
            # police *external* importers of it.
            continue
        rel = path.relative_to(package_root).as_posix()
        files.append((rel, path))
    return files


def find_importers(package_root: Path | None = None) -> list[str]:
    """Sorted posix-relative paths of every production importer of ``artifact_analysis``."""
    root = src_root() if package_root is None else package_root
    importers = [
        rel_path
        for rel_path, path in iter_production_python_files(root)
        if file_imports_artifact_analysis(path)
    ]
    return sorted(importers)


def check_artifact_analysis_imports(
    package_root: Path | None = None,
) -> list[ImportViolation]:
    """Return violations for the production tree (empty list = pass)."""
    return [
        ImportViolation(rel_path=rel_path)
        for rel_path in find_importers(package_root)
        if rel_path not in ALLOWLIST
    ]


def main() -> int:
    violations = check_artifact_analysis_imports()
    if not violations:
        print("artifact_analysis import gate: OK")
        return 0

    print("artifact_analysis import gate violations:", file=sys.stderr)
    for violation in violations:
        print(f"  - {violation.format()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
