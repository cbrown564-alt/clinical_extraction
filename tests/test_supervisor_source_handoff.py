from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from scripts import build_supervisor_source_handoff as handoff_builder
from scripts.build_supervisor_source_handoff import closure_mismatches

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

    mismatches = closure_mismatches(
        PUBLIC_SOURCE, SHIPPED_PUBLIC, exact_tree=True
    )
    mismatches.extend(
        closure_mismatches(
            INTERNAL_SOURCE, SHIPPED_INTERNAL, exact_tree=False
        )
    )
    assert mismatches == [], "\n".join(mismatches)


def test_closure_mismatches_reports_drift_and_respects_internal_subset(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shipped = tmp_path / "shipped"
    (source / "nested").mkdir(parents=True)
    (shipped / "nested").mkdir(parents=True)
    (source / "same.py").write_text("value = 1\n", encoding="utf-8")
    (shipped / "same.py").write_text("value = 2\n", encoding="utf-8")
    (source / "nested" / "missing.py").write_text("value = 3\n", encoding="utf-8")
    (shipped / "extra.py").write_text("value = 4\n", encoding="utf-8")

    assert closure_mismatches(source, shipped, exact_tree=True) == [
        "extra shipped file: extra.py",
        "missing shipped file: nested/missing.py",
        "content drift: same.py",
    ]
    assert closure_mismatches(source, shipped, exact_tree=False) == [
        "extra shipped file: extra.py",
        "content drift: same.py",
    ]


def test_closure_mismatches_rejects_missing_internal_subtree(tmp_path: Path) -> None:
    source = tmp_path / "source"
    shipped = tmp_path / "shipped"
    (source / "required").mkdir(parents=True)
    shipped.mkdir()
    (source / "required" / "runtime.py").write_text("value = 1\n", encoding="utf-8")
    (source / "required_file.py").write_text("value = 2\n", encoding="utf-8")

    assert closure_mismatches(
        source,
        shipped,
        exact_tree=False,
        required_paths=("required/", "required_file.py"),
    ) == [
        "missing shipped subtree: required/",
        "missing shipped file: required_file.py",
    ]


def test_source_closure_check_is_non_mutating(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    template = tmp_path / "template"
    public_source = tmp_path / "public-source"
    internal_source = tmp_path / "internal-source"
    handoff = tmp_path / "handoff"
    public_shipped = handoff / "clinical_extraction_local"
    internal_shipped = handoff / "clinical_extraction"
    template.mkdir()
    public_source.mkdir()
    internal_source.mkdir()
    public_shipped.mkdir(parents=True)
    internal_shipped.mkdir(parents=True)
    (public_source / "api.py").write_text("value = 1\n", encoding="utf-8")
    (internal_source / "runtime.py").write_text("value = 2\n", encoding="utf-8")
    (public_shipped / "api.py").write_text("value = 1\n", encoding="utf-8")
    (internal_shipped / "runtime.py").write_text("value = 2\n", encoding="utf-8")
    monkeypatch.setattr(handoff_builder, "TEMPLATE", template)
    monkeypatch.setattr(handoff_builder, "PUBLIC_PACKAGE", public_source)
    monkeypatch.setattr(handoff_builder, "SOURCE_PACKAGE", internal_source)
    monkeypatch.setattr(handoff_builder, "HANDOFF", handoff)
    monkeypatch.setattr(handoff_builder, "ALLOWED_RUNTIME_PREFIXES", ("runtime.py",))

    handoff_builder.main(["--check-source-closure"])
    (internal_shipped / "runtime.py").unlink()

    with pytest.raises(RuntimeError, match="source-to-shipped handoff closure is stale"):
        handoff_builder.main(["--check-source-closure"])
    assert not (internal_shipped / "runtime.py").exists()


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
