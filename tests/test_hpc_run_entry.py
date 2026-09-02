from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

from clinical_extraction.operational.script_argv import gan_script_argv

ROOT = Path(__file__).resolve().parents[1]


def test_requirements_txt_matches_pyproject_runtime_deps() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    listed = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

    assert listed == pyproject["project"]["dependencies"]


def test_gan_script_argv_defaults_to_gan() -> None:
    assert gan_script_argv(
        ["--input", "notes.jsonl", "--output", "out.jsonl"]
    ) == ["gan", "--input", "notes.jsonl", "--output", "out.jsonl"]


def test_gan_script_argv_probe_flag() -> None:
    assert gan_script_argv(["--probe", "--model", "vllm/x"]) == [
        "probe",
        "--model",
        "vllm/x",
    ]


def test_gan_script_argv_keeps_explicit_subcommand() -> None:
    assert gan_script_argv(["exect", "--input", "n.jsonl", "--output", "o.jsonl"]) == [
        "exect",
        "--input",
        "n.jsonl",
        "--output",
        "o.jsonl",
    ]


def test_run_py_help_does_not_require_console_script() -> None:
    probe = subprocess.run(
        [sys.executable, str(ROOT / "run.py"), "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stderr
    assert "--input" in probe.stdout
    assert "--output" in probe.stdout
