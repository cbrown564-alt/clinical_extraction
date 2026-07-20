from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HANDOFF = ROOT / "handoff" / "supervisor"
PACKAGE = HANDOFF / "clinical_extraction"


def test_supervisor_handoff_contains_only_the_exercised_source_closure() -> None:
    required = [
        PACKAGE / "operational" / "cli.py",
        PACKAGE
        / "tasks"
        / "seizure_frequency"
        / "gan2026"
        / "llm"
        / "hybrid_structured_events.py",
        PACKAGE
        / "tasks"
        / "epilepsy_phenotyping"
        / "exectv2"
        / "llm"
        / "pipelines"
        / "key_entities_structured"
        / "runner.py",
        PACKAGE
        / "tasks"
        / "epilepsy_phenotyping"
        / "exectv2"
        / "llm"
        / "prompts"
        / "key_entities"
        / "structured_worked_examples.yaml",
    ]
    assert all(path.is_file() for path in required)
    assert not (PACKAGE / "observatory").exists()
    assert not (PACKAGE / "trace_explorer").exists()
    assert not (
        PACKAGE
        / "tasks"
        / "epilepsy_phenotyping"
        / "exectv2"
        / "assembly"
        / "pipeline.py"
    ).exists()
    assert len(list(PACKAGE.rglob("*.py"))) <= 190
    assert not list(PACKAGE.rglob("*.pyc"))
    assert not list(PACKAGE.rglob("__pycache__"))


def test_supervisor_handoff_cli_imports_from_the_stripped_tree() -> None:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(HANDOFF)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import clinical_extraction; "
                "import clinical_extraction.operational.cli; "
                "print(clinical_extraction.__file__)"
            ),
        ],
        cwd=HANDOFF,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert probe.returncode == 0, probe.stderr
    assert str(HANDOFF) in probe.stdout
