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
from clinical_extraction.paper.exect_score import letters_dev140
from clinical_extraction.paper.rungs import EXECT_HOP_EFFECT_CLASS
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
GROK_LLM_ONLY = ROOT / "paper_experiments/exect/exect_llm_only/grok46/dev140"
GROK_HYBRID_CELL = (
    ROOT / "paper_experiments/exect/exect_llm_with_rules/grok46/dev140/cell.json"
)
RULES_DEV140 = ROOT / "paper_experiments/exect/exect_rules/dev140.json"
OUT_DIR = ROOT / "paper_experiments/exect/rungs/grok46/dev140"
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SURFACE_FOR_RUNG = {
    "llm_schema": "predicted_mentions",
    "llm_format": "format_only",
    "llm_post": "residual_benchmark_added",
}


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


def replay_exect_dev140(*, slug: str = "grok46") -> dict[str, Any]:
    """Replay Grok llm_only raw_output through rungs 1-4 on development letters."""

    if slug != "grok46":
        raise ValueError("ExECT rung replay is implemented for grok46 dev140 only")
    letters = {letter.letter_id: letter for letter in letters_dev140()}
    structured_rows = load_jsonl_rows(GROK_LLM_ONLY / "structured.jsonl")
    raws = {str(row["letter_id"]): str(row["raw_output"]) for row in structured_rows}
    if len(raws) != 140:
        raise RuntimeError(f"expected 140 llm_only raw rows, found {len(raws)}")
    rules = json.loads(RULES_DEV140.read_text(encoding="utf-8"))
    hybrid_cell = json.loads(GROK_HYBRID_CELL.read_text(encoding="utf-8"))
    before = structured.PROMPT_VERSION
    scored: list[dict[str, Any]] = []
    hops_rows: list[dict[str, Any]] = []
    family_rows: dict[str, list[dict[str, Any]]] = {
        rung: [] for rung in ("llm_schema", "llm_format", "llm_post")
    }
    try:
        structured.set_active_prompt_version(structured.EXECT_LLM_ONLY)
        for letter_id, raw_output in sorted(raws.items()):
            letter = letters[letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model="xai/grok-4.6",
                mode="replay",
                raw_output=raw_output,
                split="dev",
                config=StructuredMethodConfig.selected(),
            )
            assembled = assemble_structured_rows(
                [letter],
                [dict(producer.row)],
                config=StructuredMethodConfig.selected(),
            )[letter.letter_id]
            surfaces = assembled["prediction_surfaces"]
            schema_mentions = list(producer.row.get("predicted_mentions") or [])
            schema_hash = inventory_hash(schema_mentions, letter.note_text)
            format_hash = inventory_hash(surfaces["format_only"], letter.note_text)
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
                    rung=2,
                ),
                make_hop(
                    stage_id="exect.format.stop",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.format.stop"],
                    before=schema_hash,
                    after=format_hash,
                    rung=3,
                ),
                make_hop(
                    stage_id="exect.select.dictionary",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.select.dictionary"],
                    before=format_hash,
                    after=dict_hash,
                    rung=4,
                ),
                make_hop(
                    stage_id="exect.select.residual",
                    owner="replay",
                    effect_class=EXECT_HOP_EFFECT_CLASS["exect.select.residual"],
                    before=dict_hash,
                    after=post_hash,
                    rung=4,
                ),
            ]
            by_rung: dict[str, dict[str, Any]] = {}
            for rung, surface in SURFACE_FOR_RUNG.items():
                mentions = (
                    schema_mentions
                    if rung == "llm_schema"
                    else list(surfaces.get(surface) or [])
                )
                by_rung[rung] = {
                    "surface": surface,
                    "inventory_hash": inventory_hash(mentions, letter.note_text),
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
            scored.append({"letter_id": letter_id, "rungs": by_rung})
            hops_rows.append(
                {
                    "letter_id": letter_id,
                    "answer_states": hops,
                    "graph": graph_from_hops(hops, unused),
                }
            )
    finally:
        structured.set_active_prompt_version(before)
    summary = {
        "claim_boundary": "ExECT development replay. Not holdout.",
        "generated_on": datetime.now(UTC).date().isoformat(),
        "model_slug": slug,
        "split": "dev140",
        "shared_raw_output": "exect_llm_only",
        "row_count": len(scored),
        "rungs": {
            "rules_only": {
                "clinical_fact_f1": rules["dev140"]["four_family_headline_f1"],
                "source": "exect_rules",
            },
            "llm_schema": _surface_prf(family_rows["llm_schema"]),
            "llm_format": _surface_prf(family_rows["llm_format"]),
            "llm_post": _surface_prf(family_rows["llm_post"]),
            "llm_pre_post": {
                "clinical_fact_f1": hybrid_cell.get("hybrid_headline_f1"),
                "source": "living_exect_llm_with_rules",
                "note": "Different prompt from rungs 2-4. Not a shared raw_output.",
            },
        },
        "format_only_check": {
            "surface": "format_only",
            "same_as_schema": (
                family_rows["llm_schema"] == family_rows["llm_format"]
                or _surface_prf(family_rows["llm_schema"])
                == _surface_prf(family_rows["llm_format"])
            ),
            "note": (
                "format_only is the stop before dictionary rewrite. "
                "dictionary_normalized is semantic, not format."
            ),
        },
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_jsonl_rows(scored, OUT_DIR / "scored.jsonl")
    write_jsonl_rows(hops_rows, OUT_DIR / "hops.jsonl")
    (OUT_DIR / "comparison.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return summary


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
