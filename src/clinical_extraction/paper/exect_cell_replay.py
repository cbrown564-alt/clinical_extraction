"""Replay ExECT rungs 1-4 from saved llm_only raw_output. No new model calls."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.answer_states import graph_from_hops, make_hop
from clinical_extraction.paper.exect import letters_for_split
from clinical_extraction.paper.methods import (
    exect_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.paper.roster import model_by_slug
from clinical_extraction.paper.cells import EXECT_HOP_EFFECT_CLASS, RUNG_IDS
from clinical_extraction.paper.volume import count_predicted_mentions
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    predictions_from_prediction_surface,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
    StructuredProducerResult,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.letter_assembly import (
    assemble_structured_rows,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SURFACE_FOR_RUNG = {
    "llm_extract": "predicted_mentions",
    "llm_encode": "format_render",
    "llm_select": "residual_benchmark_added",
}
RUNG3_REPLAY_SURFACE = "format_render"
PRE_POST_METHOD = "exect_llm_pre_post"


def exect_llm_only_rows_path(slug: str, split: str) -> Path:
    """Return the living llm-only replay file for one model and split."""

    return (
        ROOT
        / "paper_experiments/exect/exect_llm_only"
        / slug
        / split
        / "structured.jsonl"
    )


def exect_pre_post_structured_path(slug: str, split: str) -> Path:
    """Return the living or promoted pre-post raw file for one model and split."""

    living = (
        ROOT
        / "scratch/holdout/paper/exect_llm_pre_post"
        / slug
        / split
        / PRE_POST_METHOD
        / "structured.jsonl"
    )
    if living.is_file():
        return living
    promoted = (
        ROOT
        / "paper_experiments/exect"
        / PRE_POST_METHOD
        / slug
        / split
        / "structured.jsonl"
    )
    return promoted


def exect_pre_post_cell_path(slug: str, split: str) -> Path:
    """Return the living rung-5 cell for one model and split."""

    return (
        ROOT
        / "paper_experiments/exect"
        / PRE_POST_METHOD
        / slug
        / split
        / "cell.json"
    )


def exect_rules_path(split: str) -> Path:
    """Return the standalone-rules headline file that covers this split."""

    del split
    return ROOT / "paper_experiments/exect/exect_rules/dev140.json"


def exect_rung_out_dir(slug: str, split: str) -> Path:
    """Return the rung-replay directory for one model and split."""

    return ROOT / "paper_experiments/exect/rungs" / slug / split


def write_exect_rung_artifacts(
    out_dir: Path,
    summary: Mapping[str, Any],
    *,
    scored: Sequence[Mapping[str, Any]],
    hops: Sequence[Mapping[str, Any]],
    holdout: bool,
) -> Path:
    """Write replay artifacts. Holdout keeps comparison.json only."""

    out_dir.mkdir(parents=True, exist_ok=True)
    comparison = out_dir / "comparison.json"
    comparison.write_text(
        json.dumps(dict(summary), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    scored_path = out_dir / "scored.jsonl"
    hops_path = out_dir / "hops.jsonl"
    if holdout:
        scored_path.unlink(missing_ok=True)
        hops_path.unlink(missing_ok=True)
        return comparison
    write_jsonl_rows(list(scored), scored_path)
    write_jsonl_rows(list(hops), hops_path)
    return comparison


def schema_mention_rows(producer: StructuredProducerResult) -> list[dict[str, Any]]:
    """Four-family events as flattened. No CUI attach, gates, or family format."""

    return structured.assign_flatten_mention_ids(
        [
            structured.mention_row(mention)
            for mention in structured.schema_mentions(producer.spelled_mentions)
        ]
    )


def format_render_mention_rows(
    producer: StructuredProducerResult,
    note_text: str,
) -> list[dict[str, Any]]:
    """Same findings, standard writing. No evidence reject or clinical post."""

    formatted, _warnings = structured.apply_format_stack(
        producer.spelled_mentions, note_text
    )
    return structured.assign_flatten_mention_ids(
        [structured.mention_row(mention) for mention in formatted]
    )


def inventory_hash(mentions: Sequence[Mapping[str, Any]], note_text: str) -> str:
    """Stable hash of the four-family clinical-fact inventory."""

    predicted = predictions_from_prediction_surface(
        [{"letter_id": "tmp", "prediction_surfaces": {"all": list(mentions)}}],
        "all",
    )[0]
    predicted_letter = to_exect_letter(predicted, note_text)
    keys: list[str] = []
    for family in FAMILIES:
        family_mentions = [
            annotation
            for annotation in predicted_letter.annotations
            if annotation.entity == family
        ]
        for key in clinical_headline_unit_keys(family, family_mentions, note_text):
            keys.append(json.dumps(key, sort_keys=True, default=str))
    return "|".join(sorted(keys))


def replay_exect_rungs(split: str, *, slug: str = "grok46") -> dict[str, Any]:
    """Replay saved llm_only raw_output through rungs 1-4. No new model calls."""

    if split not in {"dev140", "test60"}:
        raise ValueError("ExECT rung replay accepts split dev140 or test60")
    holdout = holdout_is_aggregate_only(split)
    expected_n = exect_row_count(split)
    raw_path = exect_llm_only_rows_path(slug, split)
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"missing exect_llm_only replay file for {slug} {split}: {raw_path}"
        )
    letters = {letter.letter_id: letter for letter in letters_for_split(split)}
    structured_rows = load_jsonl_rows(raw_path)
    raws = {str(row["letter_id"]): str(row["raw_output"]) for row in structured_rows}
    if len(raws) != expected_n:
        raise RuntimeError(
            f"expected {expected_n} llm_only raw rows for {split}, found {len(raws)}"
        )
    rules = json.loads(exect_rules_path(split).read_text(encoding="utf-8"))
    hybrid_cell_path = exect_pre_post_cell_path(slug, split)
    hybrid_cell = (
        json.loads(hybrid_cell_path.read_text(encoding="utf-8"))
        if hybrid_cell_path.is_file()
        else {}
    )
    model = str(model_by_slug(slug)["model"])
    before = structured.PROMPT_VERSION
    scored: list[dict[str, Any]] = []
    hops_rows: list[dict[str, Any]] = []
    family_rows: dict[str, list[dict[str, Any]]] = {
        rung: [] for rung in ("llm_extract", "llm_encode", "llm_select")
    }
    mention_counts = {rung: 0 for rung in ("llm_extract", "llm_encode", "llm_select")}
    try:
        structured.set_active_prompt_version(structured.EXECT_LLM_ONLY)
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
                config=StructuredMethodConfig.selected(),
            )[letter.letter_id]
            surfaces = assembled["prediction_surfaces"]
            schema_rows = schema_mention_rows(producer)
            format_render_mentions = format_render_mention_rows(producer, letter.note_text)
            schema_hash = inventory_hash(schema_rows, letter.note_text)
            format_hash = inventory_hash(format_render_mentions, letter.note_text)
            materialized_format_only = list(surfaces.get("format_only") or [])
            dict_hash = inventory_hash(
                surfaces.get("dictionary_normalized") or [], letter.note_text
            )
            post_hash = inventory_hash(
                surfaces["residual_benchmark_added"], letter.note_text
            )
            hops = [
                make_hop(
                    stage_id="exect.schema.parse",
                    owner="model",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.schema.parse"],
                    before=None,
                    after=schema_hash,
                    cell_id="llm_extract",
                ),
                make_hop(
                    stage_id="exect.format.stop",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.format.stop"],
                    before=schema_hash,
                    after=format_hash,
                    cell_id="llm_encode",
                ),
                make_hop(
                    stage_id="exect.select.dictionary",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.select.dictionary"],
                    before=format_hash,
                    after=dict_hash,
                    cell_id="llm_select",
                ),
                make_hop(
                    stage_id="exect.select.residual",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.select.residual"],
                    before=dict_hash,
                    after=post_hash,
                    cell_id="llm_select",
                ),
            ]
            by_rung: dict[str, dict[str, Any]] = {}
            rung_mentions = {
                "llm_extract": schema_rows,
                "llm_encode": format_render_mentions,
                "llm_select": list(surfaces.get("residual_benchmark_added") or []),
            }
            for rung, surface in SURFACE_FOR_RUNG.items():
                mentions = rung_mentions[rung]
                mention_counts[rung] += count_predicted_mentions(mentions)
                by_rung[rung] = {
                    "surface": surface,
                    "inventory_hash": inventory_hash(mentions, letter.note_text),
                    "predicted_mention_count": count_predicted_mentions(mentions),
                }
                keys = _family_keys(letter, mentions)
                for family in FAMILIES:
                    gold_keys = Counter(
                        clinical_headline_unit_keys(
                            family,
                            [
                                annotation
                                for annotation in letter.annotations
                                if annotation.entity == family
                            ],
                            letter.note_text,
                        )
                    )
                    family_rows[rung].append(
                        {
                            "letter_id": letter_id,
                            "family": family,
                            "gold_keys": _counter_rows(gold_keys),
                            "pred_keys": _counter_rows(keys[family]),
                        }
                    )
            unused = [
                {
                    "id": str(mention.get("finding_id") or mention.get("text")),
                    "label": mention.get("text"),
                    "kind": mention.get("entity"),
                }
                for mention in surfaces.get("source_scored") or []
                if mention not in (surfaces.get("residual_benchmark_added") or [])
            ]
            scored.append(
                {
                    "letter_id": letter_id,
                    "rungs": by_rung,
                    "format_render_vs_materialized_format_only": (
                        inventory_hash(format_render_mentions, letter.note_text)
                        != inventory_hash(materialized_format_only, letter.note_text)
                    ),
                }
            )
            if not holdout:
                hops_rows.append(
                    {
                        "letter_id": letter_id,
                        "answer_states": hops,
                        "graph": graph_from_hops(hops, unused),
                    }
                )
    finally:
        structured.set_active_prompt_version(before)
    summary = _comparison_summary(
        family_rows,
        slug=slug,
        split=split,
        holdout=holdout,
        row_count=len(scored),
        rules=rules,
        hybrid_cell=hybrid_cell,
        mention_counts=mention_counts,
        scored=scored,
    )
    write_exect_rung_artifacts(
        exect_rung_out_dir(slug, split),
        summary,
        scored=scored,
        hops=hops_rows,
        holdout=holdout,
    )
    return summary


def replay_exect_pre_post_encode(split: str, *, slug: str = "gemini37flash") -> dict[str, Any]:
    """Score rule encode on a saved pre-post raw. No new model calls."""

    if split not in {"dev140", "test60"}:
        raise ValueError("pre-post encode replay accepts split dev140 or test60")
    holdout = holdout_is_aggregate_only(split)
    expected_n = exect_row_count(split)
    raw_path = exect_pre_post_structured_path(slug, split)
    if not raw_path.is_file():
        raise FileNotFoundError(
            f"missing exect_llm_pre_post raw for {slug} {split}: {raw_path}"
        )
    letters = {letter.letter_id: letter for letter in letters_for_split(split)}
    raws = {
        str(row["letter_id"]): str(row["raw_output"])
        for row in load_jsonl_rows(raw_path)
    }
    if len(raws) != expected_n:
        raise RuntimeError(
            f"expected {expected_n} pre_post raw rows for {split}, found {len(raws)}"
        )
    model = str(model_by_slug(slug)["model"])
    before = structured.PROMPT_VERSION
    encode_rows: list[dict[str, Any]] = []
    extract_rows: list[dict[str, Any]] = []
    select_rows: list[dict[str, Any]] = []
    mention_counts = {"extract": 0, "encode": 0, "select": 0}
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
                config=StructuredMethodConfig.selected(),
            )[letter.letter_id]
            schema_rows = schema_mention_rows(producer)
            format_rows = format_render_mention_rows(producer, letter.note_text)
            select_mentions = list(
                assembled["prediction_surfaces"].get("residual_benchmark_added") or []
            )
            schema_keys = _family_keys(letter, schema_rows)
            format_keys = _family_keys(letter, format_rows)
            select_keys = _family_keys(letter, select_mentions)
            mention_counts["extract"] += count_predicted_mentions(schema_rows)
            mention_counts["encode"] += count_predicted_mentions(format_rows)
            mention_counts["select"] += count_predicted_mentions(select_mentions)
            for family in FAMILIES:
                gold_keys = Counter(
                    clinical_headline_unit_keys(
                        family,
                        [
                            annotation
                            for annotation in letter.annotations
                            if annotation.entity == family
                        ],
                        letter.note_text,
                    )
                )
                extract_rows.append(
                    {
                        "family": family,
                        "gold_keys": _counter_rows(gold_keys),
                        "pred_keys": _counter_rows(schema_keys[family]),
                    }
                )
                encode_rows.append(
                    {
                        "family": family,
                        "gold_keys": _counter_rows(gold_keys),
                        "pred_keys": _counter_rows(format_keys[family]),
                    }
                )
                select_rows.append(
                    {
                        "family": family,
                        "gold_keys": _counter_rows(gold_keys),
                        "pred_keys": _counter_rows(select_keys[family]),
                    }
                )
    finally:
        structured.set_active_prompt_version(before)
    extract = _surface_prf(extract_rows)
    encode = _surface_prf(encode_rows)
    select = _surface_prf(select_rows)
    extract["predicted_mention_count"] = mention_counts["extract"]
    encode["predicted_mention_count"] = mention_counts["encode"]
    select["predicted_mention_count"] = mention_counts["select"]
    summary = {
        "claim_boundary": (
            "ExECT aggregate-only test60 pre-post rule encode. "
            "Do not inspect holdout rows."
            if holdout
            else "ExECT development pre-post rule encode. Not holdout."
        ),
        "generated_on": datetime.now(UTC).date().isoformat(),
        "method": PRE_POST_METHOD,
        "model_slug": slug,
        "no_new_model_calls": True,
        "row_count": expected_n,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "split": split,
        "source_raw": raw_path.relative_to(ROOT).as_posix(),
        "surface": RUNG3_REPLAY_SURFACE,
        "extract": extract,
        "encode": encode,
        "select": select,
        "encode_same_as_extract": extract == encode,
    }
    if raw_path.parent.name == PRE_POST_METHOD:
        cell_dir = raw_path.parent.parent
    else:
        cell_dir = raw_path.parent
    cell_dir.mkdir(parents=True, exist_ok=True)
    encode_path = cell_dir / "encode_stop.json"
    encode_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    summary["artifact"] = encode_path.relative_to(ROOT).as_posix()
    comparison_path = cell_dir / "comparison.json"
    if "scratch/holdout" in comparison_path.as_posix() and comparison_path.is_file():
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        decision = comparison.setdefault("decision", {}).setdefault(PRE_POST_METHOD, {})
        decision["encode_headline_f1"] = encode["clinical_fact_f1"]
        decision["encode_family_f1"] = encode["family_f1"]
        decision["encode_same_as_extract"] = extract == encode
        comparison_path.write_text(
            json.dumps(comparison, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary["comparison"] = comparison_path.relative_to(ROOT).as_posix()
    return summary


def replay_exect_dev140(*, slug: str = "grok46") -> dict[str, Any]:
    """Replay llm_only raw_output through rungs 1-4 on development letters."""

    return replay_exect_rungs("dev140", slug=slug)


def _comparison_summary(
    family_rows: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    slug: str,
    split: str,
    holdout: bool,
    row_count: int,
    rules: Mapping[str, Any],
    hybrid_cell: Mapping[str, Any],
    mention_counts: Mapping[str, int],
    scored: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    nested = rules.get(split)
    if isinstance(nested, Mapping) and nested.get("four_family_headline_f1") is not None:
        rules_f1 = nested["four_family_headline_f1"]
    else:
        headline = rules.get("clinical_headline") or {}
        rules_f1 = headline.get("f1") if isinstance(headline, Mapping) else None
    rungs: dict[str, Any] = {
        "rules_only": {
            "clinical_fact_f1": rules_f1,
            "source": "exect_rules",
        },
        "llm_extract": {
            **_surface_prf(family_rows["llm_extract"]),
            "predicted_mention_count": mention_counts["llm_extract"],
        },
        "llm_encode": {
            **_surface_prf(family_rows["llm_encode"]),
            "predicted_mention_count": mention_counts["llm_encode"],
        },
        "llm_select": {
            **_surface_prf(family_rows["llm_select"]),
            "predicted_mention_count": mention_counts["llm_select"],
        },
    }
    if hybrid_cell.get("hybrid_headline_f1") is not None:
        rungs["llm_pre_post"] = {
            "clinical_fact_f1": hybrid_cell.get("hybrid_headline_f1"),
            "source": "living_exect_llm_pre_post",
            "note": "Different prompt from rungs 2-4. Not a shared raw_output.",
        }
    return {
        "claim_boundary": (
            "ExECT aggregate-only test60 replay. Do not inspect holdout rows."
            if holdout
            else "ExECT development replay. Not holdout."
        ),
        "format_only_check": {
            "surface": RUNG3_REPLAY_SURFACE,
            "materialized_format_only_differs_from_rung3": (
                sum(
                    1
                    for row in scored or []
                    if row.get("format_render_vs_materialized_format_only")
                )
                if scored is not None
                else None
            ),
            "same_as_schema": (
                _surface_prf(family_rows["llm_extract"])
                == _surface_prf(family_rows["llm_encode"])
            ),
            "note": (
                "Rung 2 is flatten only. Rung 3 is same-fact format (closed-vocab "
                "canonicalize, CUI attach, Rx name/unit/dose, SF encoding, Inv "
                "attribute strip) without evidence reject or family post. "
                "Materialized format_only remains a stop marker, not rung 3."
            ),
        },
        "generated_on": datetime.now(UTC).date().isoformat(),
        "model_slug": slug,
        "row_count": row_count,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "rungs": {rung: rungs[rung] for rung in RUNG_IDS if rung in rungs},
        "shared_raw_output": "exect_llm_only",
        "split": split,
    }


def _family_keys(
    letter: ExectLetter, mentions: Sequence[Mapping[str, Any]]
) -> dict[str, Counter[Any]]:
    predicted = predictions_from_prediction_surface(
        [{"letter_id": letter.letter_id, "prediction_surfaces": {"all": list(mentions)}}],
        "all",
    )[0]
    predicted_letter = to_exect_letter(predicted, letter.note_text)
    return {
        family: Counter(
            clinical_headline_unit_keys(
                family,
                [
                    annotation
                    for annotation in predicted_letter.annotations
                    if annotation.entity == family
                ],
                letter.note_text,
            )
        )
        for family in FAMILIES
    }


def _surface_prf(letter_rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    overall: Counter[str] = Counter()
    by_family: dict[str, dict[str, float]] = {}
    for family in FAMILIES:
        counts: Counter[str] = Counter()
        for row in letter_rows:
            if row["family"] != family:
                continue
            gold = _counter_from_rows(row["gold_keys"])
            pred = _counter_from_rows(row["pred_keys"])
            counts += Counter(
                {
                    "tp": sum((gold & pred).values()),
                    "fp": sum((pred - gold).values()),
                    "fn": sum((gold - pred).values()),
                }
            )
        overall += counts
        by_family[family] = _prf(counts)
    headline = _prf(overall)
    return {
        "clinical_fact_f1": headline["f1"],
        "precision": headline["precision"],
        "recall": headline["recall"],
        "gold_count": int(overall["tp"]) + int(overall["fn"]),
        "pred_count": int(overall["tp"]) + int(overall["fp"]),
        "family_f1": {family: by_family[family]["f1"] for family in FAMILIES},
    }


def _prf(counts: Mapping[str, int]) -> dict[str, float]:
    tp = int(counts.get("tp", 0))
    fp = int(counts.get("fp", 0))
    fn = int(counts.get("fn", 0))
    precision = 0.0 if tp + fp == 0 else round(tp / (tp + fp), 4)
    recall = 0.0 if tp + fn == 0 else round(tp / (tp + fn), 4)
    denom = 2 * tp + fp + fn
    f1 = 0.0 if denom == 0 else round(2 * tp / denom, 4)
    return {"precision": precision, "recall": recall, "f1": f1}


def _counter_rows(counter: Counter[Any]) -> list[dict[str, Any]]:
    return sorted(
        ({"key": key, "count": count} for key, count in counter.items()),
        key=lambda row: json.dumps(row["key"], sort_keys=True, default=str),
    )


def _counter_from_rows(rows: Sequence[Mapping[str, Any]]) -> Counter[Any]:
    counter: Counter[Any] = Counter()
    for row in rows:
        key = row["key"]
        if isinstance(key, list):
            key = tuple(key)
        counter[key] += int(row["count"])
    return counter
