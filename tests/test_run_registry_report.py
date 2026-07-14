from pathlib import Path

from clinical_extraction.core.registry import RunRegistryEntry
from clinical_extraction.core.run_registry_report import (
    render_run_registry_markdown,
    write_run_registry_markdown,
)


def _entry() -> RunRegistryEntry:
    return RunRegistryEntry(
        run_id="example_run",
        artifact_paths=("experiments/example.json",),
        date="2026-07-14",
        pipeline_family="hybrid",
        split="dev",
        row_count=12,
        model="openai/gpt-4.1-mini",
        model_role="hybrid reference",
        mode="saved replay",
        replay_status="saved_output_replay",
        decision="promote",
        primary_metrics={"f1": 0.9},
    )


def test_run_registry_report_is_task_neutral() -> None:
    rendered = render_run_registry_markdown([_entry()])

    assert rendered.startswith("# Clinical Extraction Run Registry\n")
    assert "## Promote" in rendered
    assert "`example_run`" in rendered
    assert "Gan holdout promotion ladder" not in rendered


def test_write_run_registry_markdown(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "RUN_INDEX.md"

    write_run_registry_markdown([_entry()], target)

    assert target.read_text(encoding="utf-8") == render_run_registry_markdown([_entry()])
