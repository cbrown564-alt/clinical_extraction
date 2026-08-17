"""No-call replays for the six retained architecture reference cells."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def replay_gan_saved_comparisons(path: Path) -> dict[str, int | float]:
    """Recount Gan comparison outcomes from a permitted saved JSONL artifact."""

    rows = _load_jsonl(path)
    purist_correct = pragmatic_correct = prediction_records = 0
    for row in rows:
        comparison = row.get("comparison")
        if isinstance(comparison, dict):
            purist_correct += int(bool(comparison.get("purist_correct")))
            pragmatic_correct += int(bool(comparison.get("pragmatic_correct")))
        prediction_records += int(_has_gan_prediction_record(row))
    return {
        "rows": len(rows),
        "purist_correct": purist_correct,
        "pragmatic_correct": pragmatic_correct,
        "prediction_records": prediction_records,
    }


def replay_exectv2_deterministic(*, split: str) -> dict[str, int | float]:
    """Re-run the deterministic all-entity reference through current scorers."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
        run_all9_on_letters,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
        deterministic_all9_scorecard,
    )

    gold_letters = load_letters_for_split(split)
    scorecard = deterministic_all9_scorecard.build_scorecard(
        gold_letters, run_all9_on_letters(gold_letters)
    )
    return {
        "row_count": int(scorecard["row_count"]),
        "benchmark_per_item_f1": float(scorecard["scores"]["benchmark"]["per_item"]["f1"]),
        "evidence_validity_rate": float(scorecard["validation"]["evidence_validity_rate"]),
    }


def replay_exectv2_saved_predictions(path: Path, *, split: str) -> dict[str, int | float]:
    """Re-score saved ExECT prediction mentions without invoking a model."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
        ExectLetter,
        load_letters_for_split,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
        benchmark_config_for,
        score_overall,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
        aggregate_scores,
        clinical_headline_scores,
    )

    rows = _load_jsonl(path)
    rows_by_id = {str(row.get("letter_id", "")): row for row in rows}
    if len(rows_by_id) != len(rows):
        raise ValueError(f"duplicate or empty letter_id in {path}")

    gold_letters = load_letters_for_split(split)
    gold_ids = {letter.letter_id for letter in gold_letters}
    if set(rows_by_id) != gold_ids:
        missing = sorted(gold_ids - rows_by_id.keys())
        extra = sorted(rows_by_id.keys() - gold_ids)
        raise ValueError(
            f"saved prediction coverage mismatch for {path}: "
            f"missing={missing[:5]} extra={extra[:5]}"
        )

    pred_letters = []
    for gold in gold_letters:
        mentions = rows_by_id[gold.letter_id].get("predicted_mentions", [])
        if not isinstance(mentions, list):
            raise ValueError(f"predicted_mentions must be an array for {gold.letter_id}")
        pred_letters.append(
            ExectLetter(
                letter_id=gold.letter_id,
                note_text=gold.note_text,
                annotations=tuple(_exect_annotation(mention) for mention in mentions),
            )
        )

    family_scores = clinical_headline_scores(gold_letters, pred_letters)
    aggregate = aggregate_scores(family_scores.values())
    strict = score_overall(
        gold_letters,
        pred_letters,
        ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations"),
        benchmark_config_for,
    ).per_item
    return {
        "row_count": len(rows),
        "clinical_headline_f1": float(aggregate["f1"]),
        "strict_benchmark_per_item_f1": round(float(strict.f1), 4),
    }


def replay_current_stack_primary(repo_root: Path) -> dict[str, int | float]:
    """Read living Decision 0050 / 0046 fills without inspecting holdout rows."""

    fills = _load_json_object(
        repo_root / "paper_experiments/current_stack/latest/fills.json"
    )
    sources = _load_json_object(repo_root / "paper_experiments/current_stack/SOURCES.json")
    e5 = _load_json_object(
        repo_root
        / "paper_experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json"
    )
    hybrid = fills["hybrid"]
    unchanged = sources["unchanged_primary_fills"]
    return {
        "gan_sol_hybrid_purist": int(hybrid["gan_test450"]["gpt56sol"]["purist"]),
        "exect_sol_hybrid_dev140_f1": float(hybrid["exect_dev140"]["gpt56sol"]["f1"]),
        "exect_sol_hybrid_test60_f1": float(hybrid["exect_test60"]["gpt56sol"]["f1"]),
        "gan_sol_llm_only_rate": float(unchanged["gan_test450_sol_llm_only"]),
        "exect_sol_llm_only_dev140_f1": float(unchanged["exect_dev140_sol_llm_only"]),
        "exect_sol_llm_only_test60_f1": float(unchanged["exect_test60_sol_llm_only"]),
        "exect_rules_dev140_f1": float(e5["dev140"]["four_family_headline_f1"]),
        "exect_rules_test60_f1": float(e5["test60"]["four_family_headline_f1"]),
    }


def replay_exectv2_finding_assembly(path: Path) -> dict[str, int | float]:
    """Rebuild a saved-output finding assembly and return its primary scores."""

    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.manifests import (
        load_finding_assembly_manifest,
    )
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.pipeline import (
        build_finding_assembly,
    )

    run = build_finding_assembly(load_finding_assembly_manifest(path))
    ladder = run.report["score_ladder"]
    post_lens_f1 = float(ladder["post_lens_score"]["overall"]["f1"])
    return {
        "row_count": int(run.report["row_count"]),
        "clinical_headline_f1": float(ladder["headline_target"]["overall"]["f1"]),
        "post_lens_f1": post_lens_f1,
        "evidence_valid_f1": post_lens_f1,
        "benchmark_cui_f1": float(ladder["benchmark"]["after_cui_projection"]),
    }


def _load_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"expected JSON object at {path}:{line_number}")
        rows.append(value)
    return rows


def _has_gan_prediction_record(row: dict[str, Any]) -> bool:
    if row.get("final_label") not in (None, ""):
        return True
    decision = row.get("decision_record")
    if isinstance(decision, dict) and decision.get("final_label") not in (None, ""):
        return True
    structured = row.get("structured_record")
    if not isinstance(structured, dict):
        return False
    selection = structured.get("selection")
    return isinstance(selection, dict) and selection.get("final_label") not in (None, "")


def _exect_annotation(mention: object) -> Any:
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation

    if not isinstance(mention, dict):
        raise ValueError("saved predicted mention must be a JSON object")
    attributes = mention.get("attributes") or {}
    if not isinstance(attributes, dict):
        raise ValueError("saved predicted mention attributes must be a JSON object")
    return ExectAnnotation(
        entity=str(mention.get("entity", "")),
        text=str(mention.get("text", "")),
        attributes={str(key): str(value) for key, value in attributes.items() if value is not None},
    )
