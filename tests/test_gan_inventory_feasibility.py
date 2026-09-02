"""Always-on contract for the Gan inventory feasibility study."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.gan_inventory_feasibility import (
    CLAIM_BOUNDARY,
    FAMILIES,
    MACHINE_SPLIT,
    PERMITTED_SPLIT,
    SAMPLE_SEED,
    SAMPLE_SIZE,
    choose_illustration_indices,
    family_summaries,
    load_inventory_panel,
    mention_subtype,
    require_permitted_split,
    select_sample_indices,
)


def test_sample_is_deterministic_and_stays_inside_the_pool() -> None:
    pool = list(range(1000, 1750))
    first = select_sample_indices(pool)
    second = select_sample_indices(list(reversed(pool)))

    assert first == second
    assert len(first) == SAMPLE_SIZE
    assert first == tuple(sorted(first))
    assert set(first).issubset(set(pool))


def test_sample_seed_and_size_match_the_protocol() -> None:
    assert SAMPLE_SEED == 20260828
    assert SAMPLE_SIZE == 100
    assert PERMITTED_SPLIT == "dev750"
    assert MACHINE_SPLIT == "validation"


def test_locked_and_unknown_splits_are_refused() -> None:
    with pytest.raises(ValueError, match="test450"):
        require_permitted_split("test450")
    with pytest.raises(ValueError, match="dev750"):
        require_permitted_split("dev140")
    require_permitted_split("dev750")


def test_family_summaries_are_descriptive_and_omit_accuracy() -> None:
    rows = [
        {
            "source_row_index": 1,
            "mentions": [
                {"entity": "Diagnosis", "subtype": "Epilepsy"},
                {"entity": "Prescription", "subtype": "levetiracetam"},
            ],
        },
        {
            "source_row_index": 2,
            "mentions": [
                {"entity": "Diagnosis", "subtype": "Epilepsy"},
                {"entity": "Diagnosis", "subtype": "MultipleSeizures"},
            ],
        },
        {"source_row_index": 3, "mentions": []},
    ]

    summary = family_summaries(rows)
    diagnosis = summary["Diagnosis"]

    assert diagnosis["letters_with_at_least_one"] == 2
    assert diagnosis["total_facts"] == 3
    assert diagnosis["median_facts_per_letter"] == 1.0
    assert diagnosis["min_facts_per_letter"] == 0
    assert diagnosis["max_facts_per_letter"] == 2
    assert diagnosis["common_subtypes"][:1] == [{"subtype": "Epilepsy", "count": 2}]
    assert summary["any_family"]["letters_with_at_least_one"] == 2
    assert "precision" not in summary
    assert "recall" not in summary
    assert "f1" not in summary
    assert "accuracy" not in summary
    assert set(FAMILIES) <= set(summary)


def test_illustration_rule_prefers_multi_family_then_volume() -> None:
    rows = [
        {
            "source_row_index": 10,
            "mentions": [
                {"entity": "Diagnosis"},
                {"entity": "Prescription"},
                {"entity": "Investigations"},
            ],
        },
        {
            "source_row_index": 4,
            "mentions": [
                {"entity": "Diagnosis"},
                {"entity": "Prescription"},
                {"entity": "Investigations"},
                {"entity": "SeizureFrequency"},
            ],
        },
        {
            "source_row_index": 7,
            "mentions": [{"entity": "Diagnosis"}, {"entity": "Prescription"}],
        },
    ]

    assert choose_illustration_indices(rows) == (4, 10, 7)


def test_mention_subtype_uses_the_declared_preference_order() -> None:
    assert (
        mention_subtype(
            "Diagnosis",
            "focal epilepsy",
            {"DiagCategory": "Epilepsy", "CUIPhrase": "focal-epilepsy"},
        )
        == "Epilepsy"
    )
    assert mention_subtype("Prescription", "keppra 500", {"DrugName": "levetiracetam"}) == (
        "levetiracetam"
    )
    assert mention_subtype(
        "Investigations",
        "MRI brain",
        {"MRI_Results": "Normal", "EEG_Results": "Abnormal"},
    ) == "MRI:Normal+EEG:Abnormal"
    assert mention_subtype("SeizureFrequency", "2 per week", {"FrequencyChange": "Decreased"}) == (
        "Decreased"
    )


def _write_inventory_artifact(root: Path) -> Path:
    artifact = root / "inventory"
    artifact.mkdir()
    rows = [
        {
            "source_row_index": 2748,
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "subtype": "Epilepsy",
                    "attributes": {"DiagCategory": "Epilepsy"},
                    "evidence": "focal epilepsy",
                }
            ],
        },
        {"source_row_index": 5551, "mentions": []},
    ]
    (artifact / "rows.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )
    (artifact / "summary.json").write_text(
        json.dumps(
            {
                "schema_version": "gan_inventory_feasibility.v1",
                "study": "gan_inventory_feasibility_dev750_n100_v1",
                "split": "dev750",
                "sample_size": 2,
                "selected_source_row_indices": [2748, 5551],
                "illustration_source_row_indices": [2748],
                "family_summaries": family_summaries(rows),
                "program_entry": "run_letter",
                "program_config": "ACCEPTED_THREE_STAGE_CONFIG",
                "scorer": None,
            }
        ),
        encoding="utf-8",
    )
    return artifact


def test_inventory_panel_is_descriptive_and_lists_only_sampled_letters(
    tmp_path: Path,
) -> None:
    panel = load_inventory_panel(artifact_dir=_write_inventory_artifact(tmp_path))

    assert panel["split"] == "dev750"
    assert panel["sample_size"] == 2
    assert panel["scorer"] is None
    assert panel["claim_boundary"] == CLAIM_BOUNDARY
    assert "accuracy" not in panel
    assert "f1" not in panel
    assert [letter["source_row_index"] for letter in panel["letters"]] == [2748, 5551]
    assert "note_text" not in panel["letters"][0]
    assert panel["letters"][0]["mentions"][0]["entity"] == "Diagnosis"
    assert panel["illustration_source_row_indices"] == [2748]


def test_inventory_panel_refuses_locked_or_unsampled_artifacts(tmp_path: Path) -> None:
    artifact = _write_inventory_artifact(tmp_path)
    summary_path = artifact / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    summary["split"] = "test450"
    summary_path.write_text(json.dumps(summary), encoding="utf-8")

    with pytest.raises(ValueError, match="test450"):
        load_inventory_panel(artifact_dir=artifact)

    summary["split"] = "dev750"
    summary["selected_source_row_indices"] = [2748, 1]
    summary_path.write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(ValueError, match="unsampled"):
        load_inventory_panel(artifact_dir=artifact)


@pytest.mark.local_corpus
def test_living_inventory_artifact_stays_descriptive_and_sampled() -> None:
    panel = load_inventory_panel()

    assert panel["split"] == "dev750"
    assert panel["sample_size"] == SAMPLE_SIZE
    assert len(panel["letters"]) == SAMPLE_SIZE
    assert panel["scorer"] is None
    assert panel["claim_boundary"] == CLAIM_BOUNDARY
    assert "accuracy" not in panel
    assert "f1" not in json.dumps(panel["family_summaries"])
    assert 2748 in panel["selected_source_row_indices"]
