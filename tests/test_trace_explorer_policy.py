from __future__ import annotations

import pytest

from clinical_extraction.trace_explorer.policy import RowPolicy, derive_row_policy


@pytest.mark.parametrize(
    ("dataset", "split", "source_ids", "expected"),
    [
        ("synthetic", "SYN-014", ("SYN-014",), RowPolicy.ILLUSTRATIVE),
        ("ExECTv2", "dev140", ("EA0001",), RowPolicy.DEVELOPMENT_ROW_LEVEL),
        ("ExECTv2", "test60", (), RowPolicy.AGGREGATE_ONLY),
        ("ExECTv2", "full200", (), RowPolicy.AGGREGATE_ONLY),
        ("Gan 2026", "validation750", ("42",), RowPolicy.DEVELOPMENT_ROW_LEVEL),
        ("Gan 2026", "test450", (), RowPolicy.AGGREGATE_ONLY),
        ("unknown", "dev", (), RowPolicy.DENIED),
    ],
)
def test_row_policy_is_derived_from_canonical_dataset_and_split(
    dataset: str,
    split: str,
    source_ids: tuple[str, ...],
    expected: RowPolicy,
) -> None:
    assert derive_row_policy(dataset=dataset, split=split, source_ids=source_ids) is expected


def test_full200_is_row_inspectable_only_with_manifest_proven_dev140_ids() -> None:
    assert (
        derive_row_policy(
            dataset="ExECTv2",
            split="full200",
            source_ids=("EA0001", "EA0002"),
            permitted_development_ids=frozenset({"EA0001", "EA0002"}),
        )
        is RowPolicy.DEVELOPMENT_ROW_LEVEL
    )


def test_mixed_or_unproven_source_ids_fail_closed() -> None:
    assert (
        derive_row_policy(
            dataset="ExECTv2",
            split="dev140",
            source_ids=("EA0001", "EA0199"),
            permitted_development_ids=frozenset({"EA0001"}),
        )
        is RowPolicy.DENIED
    )
    assert (
        derive_row_policy(dataset="synthetic", split="SYN-014", source_ids=("SYN-999",))
        is RowPolicy.DENIED
    )
