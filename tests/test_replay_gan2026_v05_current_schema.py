import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


def _module():
    path = Path("scripts/replay_gan2026_v05_current_schema.py")
    spec = spec_from_file_location("replay_gan2026_v05_current_schema", path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _row(source_id: int, label: str, purist: bool, pragmatic: bool) -> dict:
    return {
        "source_row_index": source_id,
        "structured_record": {"selection": {"final_label": label}},
        "comparison": {"purist_correct": purist, "pragmatic_correct": pragmatic},
    }


def test_build_delta_summary_counts_score_directions() -> None:
    replay = _module()
    before = [_row(1, "unknown", False, False), _row(2, "1 per week", True, True)]
    after = [_row(1, "1 per month", True, True), _row(2, "unknown", False, True)]

    assert replay.build_delta_summary(before, after) == {
        "changed_final_labels": 2,
        "purist_wrong_to_correct": 1,
        "purist_correct_to_wrong": 1,
        "pragmatic_wrong_to_correct": 1,
        "pragmatic_correct_to_wrong": 0,
    }
