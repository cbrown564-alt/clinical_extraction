"""Tests for ExECTv2 runner atomic artifact writers."""

from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.artifact_io import (
    atomic_artifact_bundle,
    commit_artifact_bundle,
    write_artifact_bundle,
)


def test_write_artifact_bundle_writes_all_targets(tmp_path: Path) -> None:
    json_path = tmp_path / "bundle.json"
    md_path = tmp_path / "bundle.md"

    write_artifact_bundle(
        {
            json_path: '{"ok": true}\n',
            md_path: "# ok\n",
        }
    )

    assert json_path.read_text(encoding="utf-8") == '{"ok": true}\n'
    assert md_path.read_text(encoding="utf-8") == "# ok\n"


def test_write_artifact_bundle_leaves_existing_files_on_failure(tmp_path: Path) -> None:
    first = tmp_path / "first.txt"
    second = tmp_path / "nested" / "second.txt"
    first.write_text("keep-me", encoding="utf-8")

    def _writer(staging: dict[Path, Path]) -> None:
        staging[first.resolve()].write_text("lost", encoding="utf-8")
        raise OSError("boom")

    with pytest.raises(OSError, match="boom"):
        commit_artifact_bundle([first, second], _writer)

    assert first.read_text(encoding="utf-8") == "keep-me"
    assert not second.exists()


def test_atomic_artifact_bundle_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "artifact.json"

    with atomic_artifact_bundle(target) as staging:
        staging[target.resolve()].write_text("{}", encoding="utf-8")

    assert target.read_text(encoding="utf-8") == "{}"
