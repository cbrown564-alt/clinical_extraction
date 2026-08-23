"""ExECT rung replay is split-aware and holdout-safe."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.paper.cli import main
from clinical_extraction.paper.exect_rung_replay import (
    exect_llm_only_rows_path,
    exect_rung_out_dir,
    format_render_mention_rows,
    replay_exect_dev140,
    replay_exect_rungs,
    schema_mention_rows,
    write_exect_rung_artifacts,
)
from clinical_extraction.paper.methods import exect_row_count


def _scored_row() -> dict[str, object]:
    rung = {"surface": "predicted_mentions", "inventory_hash": "h"}
    return {
        "letter_id": "EA0001",
        "rungs": {
            "llm_extract": rung,
            "llm_encode": rung,
            "llm_select": rung,
        },
    }


def test_exect_rung_paths_follow_slug_and_split() -> None:
    assert exect_llm_only_rows_path("grok46", "dev140").as_posix().endswith(
        "paper_experiments/exect/exect_llm_only/grok46/dev140/structured.jsonl"
    )
    assert exect_llm_only_rows_path("gemini37flash", "test60").as_posix().endswith(
        "paper_experiments/exect/exect_llm_only/gemini37flash/test60/structured.jsonl"
    )
    assert exect_rung_out_dir("grok46", "test60").as_posix().endswith(
        "paper_experiments/exect/rungs/grok46/test60"
    )
    assert exect_row_count("test60") == 59


def test_holdout_exect_rung_artifacts_are_aggregates_only(tmp_path: Path) -> None:
    summary = {
        "claim_boundary": "ExECT aggregate-only test60 replay. Do not inspect holdout rows.",
        "row_policy": "aggregate_only",
        "split": "test60",
        "model_slug": "grok46",
        "row_count": 1,
        "rungs": {
            "llm_extract": {
                "clinical_fact_f1": 0.77,
                "precision": 0.8,
                "recall": 0.75,
                "family_f1": {},
            }
        },
        "format_only_check": {
            "surface": "format_only",
            "same_as_schema": False,
        },
    }
    (tmp_path / "scored.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "hops.jsonl").write_text("{}\n", encoding="utf-8")

    written = write_exect_rung_artifacts(
        tmp_path,
        summary,
        scored=[_scored_row()],
        hops=[{"letter_id": "EA0001", "answer_states": []}],
        holdout=True,
    )

    assert written == tmp_path / "comparison.json"
    assert not (tmp_path / "scored.jsonl").exists()
    assert not (tmp_path / "hops.jsonl").exists()
    payload = json.loads(written.read_text(encoding="utf-8"))
    blob = json.dumps(payload)
    assert payload["row_policy"] == "aggregate_only"
    assert payload["claim_boundary"].startswith("ExECT aggregate-only")
    assert "letter_id" not in blob
    assert "EA0001" not in blob
    assert "letter_ids" not in payload


def test_development_exect_rung_artifacts_keep_row_files(tmp_path: Path) -> None:
    summary = {
        "claim_boundary": "ExECT development replay. Not holdout.",
        "split": "dev140",
        "row_count": 1,
        "rungs": {},
    }
    write_exect_rung_artifacts(
        tmp_path,
        summary,
        scored=[_scored_row()],
        hops=[{"letter_id": "EA0001", "answer_states": []}],
        holdout=False,
    )
    assert (tmp_path / "scored.jsonl").is_file()
    assert (tmp_path / "hops.jsonl").is_file()
    assert (tmp_path / "comparison.json").is_file()


def test_replay_exect_dev140_stays_a_development_alias() -> None:
    assert replay_exect_dev140.__doc__
    assert "development" in (replay_exect_dev140.__doc__ or "").lower()


@pytest.mark.local_corpus
def test_format_render_uses_pre_assembly_mentions_not_materialized_format_only() -> None:
    summary = replay_exect_rungs("dev140", slug="grok46")
    check = summary["format_only_check"]
    assert check["surface"] == "format_render"
    assert check["same_as_schema"] is False
    assert "same-fact format" in check["note"]
    rungs = summary["rungs"]
    assert rungs["llm_extract"]["clinical_fact_f1"] != rungs["llm_encode"]["clinical_fact_f1"]
    assert rungs["llm_select"]["clinical_fact_f1"] > rungs["llm_encode"]["clinical_fact_f1"]
    assert rungs["llm_extract"]["gold_count"] == rungs["llm_encode"]["gold_count"]
    assert rungs["llm_extract"]["predicted_mention_count"] > 0
    assert rungs["llm_encode"]["predicted_mention_count"] > 0
    assert rungs["llm_select"]["predicted_mention_count"] > 0
    assert (
        rungs["llm_encode"]["family_f1"]["SeizureFrequency"]
        < rungs["llm_select"]["family_f1"]["SeizureFrequency"]
    )


@pytest.mark.local_corpus
def test_format_render_is_not_schema_or_gated_predicted_mentions() -> None:
    from clinical_extraction.paper.exect import letters_for_split
    from clinical_extraction.paper.roster import model_by_slug
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
        llm_only_key_entities_structured as structured,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
        structured_one_call,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
        StructuredMethodConfig,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
        load_jsonl_rows,
    )

    letter = next(iter(letters_for_split("dev140")))
    raw_path = exect_llm_only_rows_path("grok46", "dev140")
    raw_output = next(
        row["raw_output"]
        for row in load_jsonl_rows(raw_path)
        if row["letter_id"] == letter.letter_id
    )
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.EXECT_LLM_ONLY)
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=str(model_by_slug("grok46")["model"]),
            mode="replay",
            raw_output=str(raw_output),
            split="dev",
            config=StructuredMethodConfig.selected(),
        )
    finally:
        structured.set_active_prompt_version(before)
    rendered = format_render_mention_rows(producer, letter.note_text)
    schema_rows = schema_mention_rows(producer)
    gated = list(producer.row.get("predicted_mentions") or [])
    assert rendered != schema_rows
    schema_missing_cui = any(
        "CUI" not in dict(row.get("attributes") or {}) for row in schema_rows
    )
    assert schema_missing_cui or not schema_rows
    assert rendered != gated


def test_cli_replay_rungs_accepts_test60(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_replay(split: str, *, slug: str = "grok46") -> dict[str, object]:
        captured["split"] = split
        captured["slug"] = slug
        return {"split": split, "model_slug": slug, "row_policy": "aggregate_only"}

    monkeypatch.setattr(
        "clinical_extraction.paper.cli.replay_exect_rungs", fake_replay
    )
    main(
        [
            "replay-rungs",
            "--method",
            "exect_llm_only",
            "--model",
            "gpt56luna",
            "--split",
            "test60",
        ]
    )
    assert captured == {"split": "test60", "slug": "gpt56luna"}
