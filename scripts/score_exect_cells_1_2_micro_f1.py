#!/usr/bin/env python3
"""Score ExECT cells 1–2 with 4-family micro F1. No new model calls."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from typing import Any

from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.exect_cell_replay import (
    exect_pre_post_structured_path,
    format_render_mention_rows,
    schema_mention_rows,
)
from clinical_extraction.paper.methods import exect_row_count, holdout_is_aggregate_only
from clinical_extraction.paper.roster import model_by_slug
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    assemble_structured_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runner import (
    Exectv2PipelineConfiguration,
    Exectv2PipelineRunner,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    exact_clinical_inventory_scores,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)

CITED_SLUG = "gemini37flash"


def _letter_from_mentions(
    letter: ExectLetter, mentions: Sequence[Any]
) -> ExectLetter:
    annotations = []
    for mention in mentions:
        if hasattr(mention, "model_dump"):
            payload = mention.model_dump(mode="json")
        else:
            payload = dict(mention)
        annotations.append(annotation_from_mapping(payload))
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        annotations=tuple(annotations),
    )


def _score_pair(
    gold: Sequence[ExectLetter], pred: Sequence[ExectLetter]
) -> dict[str, Any]:
    family = exact_clinical_inventory_scores(gold, pred)
    overall = aggregate_scores(family.values())
    return {
        "f1": overall["f1"],
        "precision": overall["precision"],
        "recall": overall["recall"],
        "gold_count": overall["gold_count"],
        "family_f1": {name: family[name]["f1"] for name in family},
    }


def score_rules(split: str) -> dict[str, Any]:
    letters = letters_for_split(split)
    expected = exect_row_count(split)
    if len(letters) != expected:
        raise RuntimeError(f"{split} has {len(letters)} letters, expected {expected}")
    runner = Exectv2PipelineRunner(Exectv2PipelineConfiguration(method="rules"))
    pred = []
    for letter in letters:
        result = runner.run(letter).result
        pred.append(_letter_from_mentions(letter, result.comparison_projection.mentions))
    return _score_pair(letters, pred)


def score_both_extract(split: str, *, slug: str = CITED_SLUG) -> dict[str, Any]:
    holdout = holdout_is_aggregate_only(split)
    expected = exect_row_count(split)
    raw_path = exect_pre_post_structured_path(slug, split)
    if not raw_path.is_file():
        raise FileNotFoundError(f"missing both-extract raw: {raw_path}")
    letters = {letter.letter_id: letter for letter in letters_for_split(split)}
    raws = {
        str(row["letter_id"]): str(row["raw_output"])
        for row in load_jsonl_rows(raw_path)
    }
    if len(raws) != expected:
        raise RuntimeError(f"expected {expected} both-extract rows, found {len(raws)}")
    model = str(model_by_slug(slug)["model"])
    gold: list[ExectLetter] = []
    extract_pred: list[ExectLetter] = []
    encode_pred: list[ExectLetter] = []
    select_pred: list[ExectLetter] = []
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.EXECT_LLM_PRE_POST)
        for letter_id, raw_output in sorted(raws.items()):
            letter = letters[letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=model,
                mode="replay",
                raw_output=raw_output,
                split="test" if holdout else "dev",
                config=StructuredMethodConfig.selected(),
            )
            assembled = assemble_structured_rows(
                [letter],
                [dict(producer.row)],
                config=StructuredMethodConfig.inventory(),
            )[letter.letter_id]
            gold.append(letter)
            extract_pred.append(_letter_from_mentions(letter, schema_mention_rows(producer)))
            encode_pred.append(
                _letter_from_mentions(
                    letter, format_render_mention_rows(producer, letter.note_text)
                )
            )
            select_pred.append(
                _letter_from_mentions(
                    letter,
                    list(
                        assembled["prediction_surfaces"].get("residual_benchmark_added")
                        or []
                    ),
                )
            )
    finally:
        structured.set_active_prompt_version(before)
    return {
        "extract": _score_pair(gold, extract_pred),
        "encode": _score_pair(gold, encode_pred),
        "select": _score_pair(gold, select_pred),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("dev140", "test60"), required=True)
    args = parser.parse_args()
    payload = {
        "split": args.split,
        "row_policy": (
            "aggregate_only"
            if holdout_is_aggregate_only(args.split)
            else "development_review_permitted"
        ),
        "scorer": "4-family micro F1",
        "cell_1_rules": score_rules(args.split),
        "cell_2_both_extract": score_both_extract(args.split),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
