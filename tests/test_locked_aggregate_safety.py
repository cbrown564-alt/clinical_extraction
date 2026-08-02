from scripts import check_locked_aggregate_safety as safety


def test_forbidden_paths_finds_nested_locked_row_content() -> None:
    assert safety.forbidden_paths({"aggregate": {"rows": [{"letter_id": "sealed"}]}}) == [
        "aggregate.rows",
        "aggregate.rows[0].letter_id",
    ]


def test_forbidden_paths_accepts_counts_and_scores() -> None:
    assert safety.forbidden_paths({"row_count": 450, "scores": {"purist": 350}}) == []
