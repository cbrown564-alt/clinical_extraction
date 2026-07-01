"""Tests for documentation sprawl hygiene gates."""

from __future__ import annotations

from pathlib import Path

from scripts.check_doc_hygiene import (
    check_doc_hygiene,
    check_experiments_root_allowlist,
    check_root_markdown,
    check_root_underscore_dirs,
    load_allowlist,
)


def test_load_allowlist_non_empty() -> None:
    assert len(load_allowlist()) >= 100


def test_repo_root_markdown_allowed_only() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_root_markdown(root) == []


def test_no_underscore_root_directories() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_root_underscore_dirs(root) == []


def test_experiments_root_matches_allowlist() -> None:
    root = Path(__file__).resolve().parents[1]
    allowlist = load_allowlist()
    assert check_experiments_root_allowlist(root, allowlist) == []


def test_check_doc_hygiene_passes_on_real_repo() -> None:
    root = Path(__file__).resolve().parents[1]
    assert check_doc_hygiene(root) == []
