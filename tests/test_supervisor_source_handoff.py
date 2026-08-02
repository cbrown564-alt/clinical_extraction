from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff" / "supervisor"
ARCHIVE = ROOT / "handoff" / "clinical_extraction_supervisor_handoff.zip"
PUBLIC_SOURCE = ROOT / "src" / "clinical_extraction_local"
SHIPPED_PUBLIC = HANDOFF / "clinical_extraction_local"
INTERNAL_SOURCE = ROOT / "src" / "clinical_extraction"
SHIPPED_INTERNAL = HANDOFF / "clinical_extraction"
TEXT_FILENAMES = frozenset({".env.example", ".gitignore"})
TEXT_SUFFIXES = frozenset(
    {
        ".json",
        ".jsonl",
        ".lock",
        ".md",
        ".ps1",
        ".py",
        ".sh",
        ".txt",
        ".yaml",
        ".yml",
    }
)


def _is_runtime_generated(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}


def _canonical_bytes(path: Path) -> bytes:
    content = path.read_bytes()
    if path.name.lower() in TEXT_FILENAMES or path.suffix.lower() in TEXT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return content


def _source_files(root: Path) -> dict[str, Path]:
    return {
        path.relative_to(root).as_posix(): path
        for path in root.rglob("*")
        if path.is_file() and not _is_runtime_generated(path)
    }


def _closure_mismatches(source: Path, shipped: Path, *, exact_tree: bool) -> list[str]:
    source_files = _source_files(source)
    shipped_files = _source_files(shipped)
    names = set(source_files) | set(shipped_files) if exact_tree else set(shipped_files)
    mismatches: list[str] = []
    for name in sorted(names):
        source_path = source_files.get(name)
        shipped_path = shipped_files.get(name)
        if source_path is None:
            mismatches.append(f"extra shipped file: {name}")
        elif shipped_path is None:
            mismatches.append(f"missing shipped file: {name}")
        elif _canonical_bytes(source_path) != _canonical_bytes(shipped_path):
            mismatches.append(f"content drift: {name}")
    return mismatches


def test_handoff_is_readable_source_first_and_has_both_workflows() -> None:
    required = [
        HANDOFF / "run.py",
        HANDOFF / "clinical_extraction_local" / "client.py",
        HANDOFF / "clinical_extraction_local" / "seizure_frequency" / "pipeline.py",
        HANDOFF / "clinical_extraction_local" / "seizure_frequency" / "prompt.md",
        HANDOFF / "clinical_extraction_local" / "seizure_frequency" / "schema.json",
        HANDOFF / "clinical_extraction_local" / "clinical_findings" / "pipeline.py",
        HANDOFF / "clinical_extraction_local" / "clinical_findings" / "prompt.md",
        HANDOFF / "clinical_extraction_local" / "clinical_findings" / "schema.json",
        HANDOFF / "docs" / "PRIVATE_DATA.md",
        HANDOFF / "tests" / "test_source_package.py",
    ]
    assert all(path.is_file() for path in required)
    assert not list(HANDOFF.rglob("*.pyz"))
    assert not (HANDOFF / "gan_results.json").exists()
    assert not (HANDOFF / "exect_results.json").exists()


def test_source_manifest_lists_every_shipped_file_with_matching_hash() -> None:
    manifest = json.loads((HANDOFF / "SOURCE_MANIFEST.json").read_text(encoding="utf-8"))
    recorded = {entry["path"]: entry for entry in manifest["files"]}
    actual = {
        path.relative_to(HANDOFF).as_posix(): path
        for path in HANDOFF.rglob("*")
        if (
            path.is_file()
            and path.name != "SOURCE_MANIFEST.json"
            and not _is_runtime_generated(path)
        )
    }
    assert set(recorded) == set(actual)
    for name, path in actual.items():
        content = _canonical_bytes(path)
        assert recorded[name]["sha256"] == hashlib.sha256(content).hexdigest()
        assert recorded[name]["bytes"] == len(content)


@pytest.mark.xfail(
    strict=True,
    reason=(
        "handoff/supervisor is stale; rebuild it before Decision 0048 can "
        "call the standalone package current"
    ),
)
def test_shipped_package_matches_current_source_closure() -> None:
    """Hash self-consistency is insufficient; compare shipped code to source."""

    mismatches = _closure_mismatches(
        PUBLIC_SOURCE, SHIPPED_PUBLIC, exact_tree=True
    )
    mismatches.extend(
        _closure_mismatches(
            INTERNAL_SOURCE, SHIPPED_INTERNAL, exact_tree=False
        )
    )
    assert mismatches == [], "\n".join(mismatches)


def test_archive_matches_readable_tree_and_excludes_private_or_research_files() -> None:
    expected = {
        path.relative_to(HANDOFF).as_posix()
        for path in HANDOFF.rglob("*")
        if path.is_file() and not _is_runtime_generated(path)
    }
    with zipfile.ZipFile(ARCHIVE) as archive:
        names = set(archive.namelist())
        setup_mode = archive.getinfo("setup.sh").external_attr >> 16
    assert names == expected
    forbidden = (".pyz", "__pycache__", "gan_results", "exect_results")
    assert ".env" not in names
    assert not any(any(part in name for part in forbidden) for name in names)
    assert not any("/reports/" in name or "/artifact_analysis/" in name for name in names)
    assert setup_mode & 0o111


def test_clean_handoff_validates_synthetic_input_without_endpoint() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "run.py",
            "validate-input",
            "--input",
            "examples/seizure_frequency/notes.jsonl",
        ],
        cwd=HANDOFF,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout) == {"status": "ok", "notes": 1}


def test_readme_leads_with_frequency_then_documents_findings_and_all() -> None:
    readme = (HANDOFF / "README.md").read_text(encoding="utf-8")
    assert readme.index("seizure-frequency") < readme.index("clinical-findings")
    assert "normally makes two model calls per note" in readme
    assert "--trace-output" in readme
    assert "--resume" in readme
