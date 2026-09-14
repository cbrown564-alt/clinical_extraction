"""Always-on: new paper first-attempt, native scoring and denominator safeguards."""

from __future__ import annotations

import copy
import json

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation.one_shot_analysis import (
    summarize,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.one_shot_contract import (
    fictional_cases,
    inspect_output,
    messages,
    native_categories,
)


def test_paired_contract_and_native_scoring_without_semantic_repair() -> None:
    for case in fictional_cases():
        rich = json.loads(messages(case["note_text"], "rich")[0]["content"])
        simple = json.loads(messages(case["note_text"], "simple")[0]["content"])
        for key in ("task", "instructions", "label_rules", "label_forms", "selection_guidance"):
            assert rich[key] == simple[key]
        assert [e["note_text"] for e in rich["examples"]] == [
            e["note_text"] for e in simple["examples"]
        ]
        for condition in ("rich", "simple"):
            output = case["output"] if condition == "rich" else {"answer": case["output"]["answer"]}
            result = inspect_output(json.dumps(output), case["note_text"], condition)
            assert result["failure"] is None
            assert result["label"] == output["answer"]["label"]
            assert result["all_quotes_exact"] != result["no_evidence_state"]
    # Native weekly cutoff is intentionally not the intuitive weekly bucket (365/7/12).
    assert native_categories("1 per week")["purist"] == "seizure_freq_more1week_less1day"
    assert native_categories("unknown") == native_categories("no seizure frequency reference")
    for invalid in ("unknown junk", "0 per month", "1 per 0 month", "4 to 2 per week", "NaN"):
        with pytest.raises(ValueError):
            native_categories(invalid)


def test_unusable_outputs_cannot_be_salvaged_or_given_vacuous_quote_success() -> None:
    case = fictional_cases()[0]
    payload = case["output"]
    altered = []
    missing = copy.deepcopy(payload)
    del missing["answer"]["label"]
    altered.append((json.dumps(missing), "invalid_schema"))
    bad_link = copy.deepcopy(payload)
    bad_link["selected_finding_ids"] = ["absent"]
    altered.append((json.dumps(bad_link), "invalid_schema"))
    extra = copy.deepcopy(payload)
    extra["rationale"] = "salvage me"
    altered.append((json.dumps(extra), "invalid_schema"))
    missing_quote = copy.deepcopy(payload)
    missing_quote["answer"]["evidence"] = None
    altered.append((json.dumps(missing_quote), "absent_required_evidence"))
    altered.extend(
        [
            (None, "no_response"),
            ("", "no_response"),
            ('{"answer":1,"answer":2}', "invalid_syntax"),
            ("```json\n" + json.dumps(payload) + "\n```", "invalid_syntax"),
        ]
    )
    for raw, failure in altered:
        assert inspect_output(raw, case["note_text"], "rich")["failure"] == failure
    assert (
        inspect_output(json.dumps(payload), case["note_text"], "rich", finish_reason="length")[
            "failure"
        ]
        == "truncation"
    )
    wrong_quote = copy.deepcopy(payload)
    wrong_quote["answer"]["evidence"] = "A fabricated quotation"
    result = inspect_output(json.dumps(wrong_quote), case["note_text"], "rich")
    assert result["failure"] is None  # Quote location is a separately reported outcome.
    assert not result["all_quotes_exact"]
    assert result["exact_quotes"] == 1


def test_all_note_denominators_and_pairing_include_failures() -> None:
    case = fictional_cases()[0]
    rich = inspect_output(json.dumps(case["output"]), case["note_text"], "rich")
    failed = inspect_output(None, case["note_text"], "simple")
    for method in ("purist", "pragmatic"):
        rich[method + "_correct"] = True
        failed[method + "_correct"] = False
    result = summarize([{"rich": rich, "simple": failed}, {"rich": failed, "simple": failed}])
    assert result["conditions"]["rich"]["purist"]["agreement"] == 0.5
    assert result["conditions"]["rich"]["purist"]["conditional_agreement"] == 1
    assert result["conditions"]["simple"]["purist"]["agreement"] == 0
    assert result["paired"]["purist"]["rich_wins"] == 1
    assert result["paired"]["purist"]["ties"] == 1


def test_study_freeze_budget_and_split_barriers(tmp_path, monkeypatch) -> None:
    from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
        one_shot_study as study,
    )

    root = tmp_path / "run"
    root.mkdir()
    data = tmp_path / "data.json"
    manifest = tmp_path / "manifest.json"
    study.write_json(
        data,
        [
            {"source_row_index": 1, "clinic_date": "development"},
            {"source_row_index": 2, "clinic_date": "sealed"},
        ],
    )
    study.write_json(
        manifest,
        {
            "dataset_sha256": study.digest(data.read_bytes()),
            "splits": {
                "validation": {"source_row_indices": [1]},
                "test": {"source_row_indices": [2]},
            },
        },
    )
    monkeypatch.setattr(study, "ROOT", root)
    monkeypatch.setattr(study, "DEFAULT_DATA_PATH", data)
    monkeypatch.setattr(study, "DEFAULT_SPLIT_MANIFEST_PATH", manifest)
    monkeypatch.setattr(study, "identity", lambda: {"version": "frozen"})
    assert [r["source_row_index"] for r in study.selected_rows("dev")] == [1]
    with pytest.raises(FileNotFoundError):
        study.selected_rows("evaluate")
    study.write_json(root / "freeze.json", {"identity": {"version": "old"}})
    with pytest.raises(ValueError, match="identity changed"):
        study.selected_rows("evaluate")
    with pytest.raises(ValueError):
        study.selected_rows("real")
    with pytest.raises(ValueError, match="after evaluation freeze"):
        study.render()
    # An interrupted attempt remains fully charged; a completed attempt reconciles only itself.
    attempts = [
        {"request_id": "a", "charged_upper_usd": 0.5},
        {"request_id": "b", "charged_upper_usd": 0.5},
        {"request_id": "a", "charged_upper_usd": 0.1},
    ]
    assert study.charged(attempts) == pytest.approx(0.6)
    assert study.upper_cost(study.request_body("fictional note", "rich")) > 0
