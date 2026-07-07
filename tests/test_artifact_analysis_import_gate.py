"""Pytest wrapper for the artifact_analysis import-quarantine gate (P2-1)."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import pytest
from check_artifact_analysis_imports import (  # noqa: E402
    ALLOWLIST,
    ARTIFACT_ANALYSIS_PKG,
    check_artifact_analysis_imports,
    file_imports_artifact_analysis,
    find_importers,
    src_root,
)


def test_production_tree_passes_import_gate(repo_root: Path) -> None:
    violations = check_artifact_analysis_imports(src_root(repo_root))
    assert violations == [], "\n".join(v.format() for v in violations)


def test_allowlist_paths_exist_under_src(repo_root: Path) -> None:
    package_root = src_root(repo_root)
    missing = [rel for rel in ALLOWLIST if not (package_root / rel).is_file()]
    assert missing == [], f"stale allowlist entries: {missing}"


def test_allowlist_paths_are_real_importers(repo_root: Path) -> None:
    """Every allowlisted file must actually import artifact_analysis today."""
    package_root = src_root(repo_root)
    not_importing = [
        rel
        for rel in ALLOWLIST
        if (package_root / rel).is_file() and not file_imports_artifact_analysis(package_root / rel)
    ]
    assert not_importing == [], f"allowlist entries that no longer import: {not_importing}"


def test_allowlist_is_frozen_to_current_importers(repo_root: Path) -> None:
    """The allowlist must equal the current importer set exactly (frozen quarantine)."""
    current = set(find_importers(src_root(repo_root)))
    assert set(ALLOWLIST) == current, (
        f"missing from allowlist: {sorted(current - set(ALLOWLIST))}; "
        f"stale in allowlist: {sorted(set(ALLOWLIST) - current)}"
    )


def test_new_unallowlisted_importer_is_caught(tmp_path: Path) -> None:
    """A new production file importing artifact_analysis must fail without allowlisting."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / "observatory" / "new_research_consumer.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "from clinical_extraction.tasks.seizure_frequency.gan2026."
        "artifact_analysis.replay_io import load_replay\n",
        encoding="utf-8",
    )

    violations = check_artifact_analysis_imports(package_root)
    assert len(violations) == 1
    violation = violations[0]
    assert violation.rel_path == "observatory/new_research_consumer.py"
    assert "not allowlisted" in violation.format()


def test_relative_star_import_is_caught(tmp_path: Path) -> None:
    """Relative star re-export shims (the experiments pattern) are detected."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / "tasks/seizure_frequency/gan2026/experiments/new_shim.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "from ..artifact_analysis.some_module import *  # noqa: F403\n",
        encoding="utf-8",
    )

    violations = check_artifact_analysis_imports(package_root)
    assert [v.rel_path for v in violations] == [
        "tasks/seizure_frequency/gan2026/experiments/new_shim.py"
    ]


def test_allowlisted_importer_passes(tmp_path: Path) -> None:
    """An importer whose path is in the real allowlist passes in a synthetic tree."""
    if not ALLOWLIST:
        pytest.skip("no allowlisted importers remain after quarantine migration")
    rel = next(iter(ALLOWLIST))
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        "from clinical_extraction.tasks.seizure_frequency.gan2026."
        "artifact_analysis import candidate_union\n",
        encoding="utf-8",
    )

    violations = check_artifact_analysis_imports(package_root)
    assert violations == []


def test_string_mention_is_not_an_import(tmp_path: Path) -> None:
    """A bare string/comment mention of artifact_analysis must NOT count as an import."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / "tasks/seizure_frequency/gan2026/experiments/audit.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        'CURRENT_MODULE = "artifact_analysis.month_bucket_duration_selection_ablation"\n'
        "# references artifact_analysis only in text\n",
        encoding="utf-8",
    )

    assert file_imports_artifact_analysis(target) is False
    assert check_artifact_analysis_imports(package_root) == []


def test_files_inside_artifact_analysis_are_skipped(tmp_path: Path) -> None:
    """Imports *within* the research layer itself are out of scope."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / f"tasks/seizure_frequency/gan2026/{ARTIFACT_ANALYSIS_PKG}/internal.py"
    target.parent.mkdir(parents=True)
    target.write_text(
        "from .candidate_union import main  # internal wiring\n"
        "from clinical_extraction.tasks.seizure_frequency.gan2026."
        "artifact_analysis.replay_io import load\n",
        encoding="utf-8",
    )

    assert find_importers(package_root) == []
    assert check_artifact_analysis_imports(package_root) == []


def test_unparseable_file_falls_back_to_regex(tmp_path: Path) -> None:
    """A file that fails to AST-parse still gets scanned via the regex fallback."""
    package_root = tmp_path / "src" / "clinical_extraction"
    target = package_root / "observatory" / "broken.py"
    target.parent.mkdir(parents=True)
    # Syntactically invalid (dangling def) but the import line is still present.
    target.write_text(
        "from ..artifact_analysis.replay_io import load\ndef broken(:\n",
        encoding="utf-8",
    )

    assert file_imports_artifact_analysis(target) is True
