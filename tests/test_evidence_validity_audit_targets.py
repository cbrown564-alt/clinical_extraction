from pathlib import Path

from clinical_extraction.core.evidence_validity_audit import build_registry_targets
from clinical_extraction.core.registry import RunRegistryEntry


def test_registry_targets_use_registry_roles_without_task_ui_curation(tmp_path: Path) -> None:
    rows = tmp_path / "rows.jsonl"
    rows.write_text("{}\n", encoding="utf-8")
    entry = RunRegistryEntry(
        run_id="gan_hybrid_reference",
        artifact_paths=(str(rows),),
        date="2026-07-14",
        pipeline_family="hybrid_structured_events",
        split="validation",
        row_count=1,
        model="openai/gpt-4.1-mini",
        model_role="hybrid reference",
        mode="saved replay",
        replay_status="saved_output_replay",
        decision="revise",
        registry_roles=("architecture_comparator",),
    )

    targets = build_registry_targets([entry])

    assert len(targets) == 1
    assert targets[0].run_id == "gan_hybrid_reference"
    assert targets[0].rows_path == rows
    assert targets[0].source == "registry_architecture_comparator"
