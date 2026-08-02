from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from scripts import build_supervisor_source_handoff as handoff_builder
from scripts.build_supervisor_source_handoff import (
    canonical_bytes,
    closure_mismatches,
)

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff" / "supervisor"
ARCHIVE = ROOT / "handoff" / "clinical_extraction_supervisor_handoff.zip"
PUBLIC_SOURCE = ROOT / "src" / "clinical_extraction_local"
SHIPPED_PUBLIC = HANDOFF / "clinical_extraction_local"
INTERNAL_SOURCE = ROOT / "src" / "clinical_extraction"
SHIPPED_INTERNAL = HANDOFF / "clinical_extraction"


def _is_runtime_generated(path: Path) -> bool:
    return "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}


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
    assert manifest.get("hash_policy"), "manifest must declare the text-hash policy"
    for name, path in actual.items():
        content = canonical_bytes(path)
        assert recorded[name]["sha256"] == hashlib.sha256(content).hexdigest()
        assert recorded[name]["bytes"] == len(content)


def test_shipped_package_matches_current_source_closure() -> None:
    runtime_files, runtime_assets = handoff_builder._trace_runtime_closure()
    required_runtime_files = tuple(
        sorted(
            path.relative_to(INTERNAL_SOURCE).as_posix()
            for path in runtime_files | runtime_assets
        )
    )
    mismatches = closure_mismatches(
        PUBLIC_SOURCE, SHIPPED_PUBLIC, exact_tree=True
    )
    mismatches.extend(
        closure_mismatches(
            INTERNAL_SOURCE,
            SHIPPED_INTERNAL,
            exact_tree=False,
            required_paths=required_runtime_files,
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
