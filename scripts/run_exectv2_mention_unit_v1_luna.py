"""Run the predeclared ExECT mention-unit v1 Luna study on frozen dev20."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.mention_unit import (
    HYBRID_METHOD,
    LLM_METHOD,
    MENTION_UNIT_MODEL,
    MENTION_UNIT_PROMPT_VERSION,
    SYSTEM_MESSAGE,
    MentionUnitExtractor,
    build_mention_unit_prompt,
    materialize_mention_unit,
    parse_mention_unit_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.semantic_inventory import (
    InventoryMaterialization,
    materialize_inventory,
    parse_inventory_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    benchmark_config_for,
    score_concept_identity,
    score_frequency_state,
    score_investigations_components,
    score_overall,
    score_prescription_components,
    semantic_config_for,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/mention_unit_v1_fork_a_luna_dev20_protocol_2026-08-16.md"
REPORT = ROOT / "docs/research/exectv2/mention_unit_v1_fork_a_luna_dev20_2026-08-16.md"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_v1_luna_dev20_20260816"
V4_ROWS = (
    ROOT / "experiments/exectv2_semantic_inventory_v4_fork_a_luna_dev20_20260816" / "rows.jsonl"
)
CONTROL_DEV140 = (
    ROOT / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
DEV20_IDS = (
    "EA0002",
    "EA0004",
    "EA0005",
    "EA0006",
    "EA0007",
    "EA0008",
    "EA0009",
    "EA0010",
    "EA0011",
    "EA0012",
    "EA0015",
    "EA0016",
    "EA0047",
    "EA0074",
    "EA0093",
    "EA0120",
    "EA0131",
    "EA0133",
    "EA0154",
    "EA0158",
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
_NONTARGET_RE = re.compile(r"\b(ECG|EKG|blood|glucose|exam)\b", re.I)
_REWRITE_ACTIONS = frozenset({"convention_split_heading", "closed_table_rewrite"})


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("dev20",), default="dev20")
    parser.add_argument("--live", action="store_true", help="Make the two candidate calls per row.")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=5)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    if args.split != "dev20":
        raise SystemExit("this protocol authorizes frozen dev20 only")

    letters = _load_dev20()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    if not args.overwrite and (STUDY_DIR / "comparison.json").exists():
        raise SystemExit(f"study exists; pass --overwrite: {STUDY_DIR}")
    _verify_prompt_contracts(letters[0])
    started = datetime.now(UTC).isoformat()

    if not args.live:
        artifact = {
            "schema_version": "exectv2.mention_unit_v1.v1",
            "status": "prompt_checked_live_not_run",
            "protocol": PROTOCOL,
            "split": "dev20",
            "row_count": len(letters),
            "model": MENTION_UNIT_MODEL,
            "prompt_version": MENTION_UNIT_PROMPT_VERSION,
            "model_calls": 0,
            "claim_boundary": "Prompt and contract check only; no candidate result.",
        }
        (STUDY_DIR / "comparison.json").write_text(
            json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(json.dumps(artifact, indent=2, sort_keys=True))
        return

    controls = _load_controls()
    v4_rows = _load_v4_rows()
    candidate_results, control_results, v4_results, trust_results, rows, operational = _run_live(
        letters,
        controls,
        v4_rows,
        api_base=args.api_base,
        timeout=args.timeout,
        progress_every=args.progress_every,
    )
    summaries = {
        "control_llm": _score_method(letters, control_results[LLM_METHOD]),
        "control_llm_with_rules": _score_method(letters, control_results[HYBRID_METHOD]),
        "v4_llm": _score_method(letters, v4_results[LLM_METHOD]),
        "v4_llm_with_rules": _score_method(letters, v4_results[HYBRID_METHOD]),
        "trust_item_llm": _score_method(letters, trust_results[LLM_METHOD]),
        "trust_item_llm_with_rules": _score_method(letters, trust_results[HYBRID_METHOD]),
        LLM_METHOD: _score_method(letters, candidate_results[LLM_METHOD]),
        HYBRID_METHOD: _score_method(letters, candidate_results[HYBRID_METHOD]),
    }
    stop = _stop_checks(letters, rows, v4_results, trust_results)
    emission = _emission_census(letters, rows, v4_rows)
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.mention_unit_v1.v1",
        "status": "complete",
        "protocol": PROTOCOL,
        "split": "dev20",
        "row_count": len(letters),
        "model": MENTION_UNIT_MODEL,
        "prompt_version": MENTION_UNIT_PROMPT_VERSION,
        "temperature": 1.0,
        "max_tokens": 2400,
        "cache": False,
        "model_calls": len(letters) * 2,
        "controls": {
            "llm": "saved_current_stack_v0.9.24_replay",
            "llm_with_rules": "saved_current_stack_v0.9.24_replay",
            "v4": "saved_fork_a_dev20_default_projection",
            "trust_item": "saved_fork_a_dev20_trust_item_rematerialization",
        },
        "methods": summaries,
        "operational": operational,
        "stop_checks": stop,
        "gold_span_emission": emission,
        "provenance": _provenance(),
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "row_policy": "development rows permitted; test60 sealed",
        "claim_boundary": (
            "GPT-5.6 Luna ExECT mention-unit development result on frozen dev20. "
            "Headline F1 is context. test60 was not inspected. Decision 0050 is unchanged."
        ),
    }
    _write_development_rows(STUDY_DIR / "rows.jsonl", rows)
    (STUDY_DIR / "comparison.json").write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (STUDY_DIR / "emission_census.json").write_text(
        json.dumps(emission, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    print(json.dumps(_public_artifact_summary(artifact), indent=2, sort_keys=True))


def _load_dev20() -> list[ExectLetter]:
    wanted = set(DEV20_IDS)
    letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in wanted]
    if [letter.letter_id for letter in letters] != sorted(DEV20_IDS):
        raise RuntimeError("the frozen dev20 sample is unavailable or changed")
    return letters


def _load_controls() -> dict[str, dict[str, Any]]:
    if not CONTROL_DEV140.exists():
        raise FileNotFoundError(CONTROL_DEV140)
    controls: dict[str, dict[str, Any]] = {}
    with CONTROL_DEV140.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            letter_id = str(row["letter_id"])
            if letter_id in DEV20_IDS:
                controls[letter_id] = row
    missing = [letter_id for letter_id in DEV20_IDS if letter_id not in controls]
    if missing:
        raise RuntimeError(f"missing v0.9.24 controls: {missing}")
    return controls


def _load_v4_rows() -> dict[str, dict[str, Any]]:
    if not V4_ROWS.exists():
        raise FileNotFoundError(V4_ROWS)
    rows: dict[str, dict[str, Any]] = {}
    with V4_ROWS.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            rows[str(row["letter_id"])] = row
    missing = [letter_id for letter_id in DEV20_IDS if letter_id not in rows]
    if missing:
        raise RuntimeError(f"missing v4 fork-A rows: {missing}")
    return rows


def _verify_prompt_contracts(letter: ExectLetter) -> None:
    for method in (LLM_METHOD, HYBRID_METHOD):
        payload = json.loads(build_mention_unit_prompt(letter, method=method))
        if list(payload) != ["task", "output_schema", "family_guidance", "letter_text"]:
            raise RuntimeError(f"{method} prompt top-level order drifted")
        serialized = json.dumps(
            {key: value for key, value in payload.items() if key != "letter_text"}
        ).lower()
        if "prompt_version" in serialized or "letter_id" in serialized or "gold" in serialized:
            raise RuntimeError(f"{method} prompt leaked research metadata")
        if "list 9" in serialized or "list 11" in serialized or "named type not generic" in serialized:
            raise RuntimeError(f"{method} prompt dumped a closed table or v16 cue")
        if method == HYBRID_METHOD and "attributes" in json.dumps(payload["output_schema"]).lower():
            raise RuntimeError("hybrid model schema exposes clinical attributes")
        program = MentionUnitExtractor(method=method)
        messages = program.render_messages(
            prompt_input_json=build_mention_unit_prompt(letter, method=method)
        )
        if messages[0] != {"role": "system", "content": SYSTEM_MESSAGE}:
            raise RuntimeError("mention-unit system message drifted")


def _run_live(
    letters: list[ExectLetter],
    controls: dict[str, dict[str, Any]],
    v4_rows: dict[str, dict[str, Any]],
    *,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> tuple[
    dict[str, list[Any]],
    dict[str, list[Any]],
    dict[str, list[Any]],
    dict[str, list[Any]],
    list[dict[str, Any]],
    dict[str, Any],
]:
    candidate_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    control_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    v4_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    trust_predictions: dict[str, list[Any]] = {LLM_METHOD: [], HYBRID_METHOD: []}
    rows: list[dict[str, Any]] = []
    operational: dict[str, dict[str, int]] = {
        method: {
            "calls": 0,
            "rows_with_blocking_parse_failure": 0,
            "parse_notes": 0,
            "items": 0,
            "evidence_invalid": 0,
            "rows_with_forbidden_fields": 0,
            "rule_changed_facts": 0,
        }
        for method in (LLM_METHOD, HYBRID_METHOD)
    }
    extractors = {
        method: MentionUnitExtractor(method=method) for method in (LLM_METHOD, HYBRID_METHOD)
    }
    for method in (LLM_METHOD, HYBRID_METHOD):
        dspy.configure(
            lm=build_dspy_lm(
                MENTION_UNIT_MODEL,
                temperature=1.0,
                max_tokens=2400,
                cache=False,
                api_base=api_base,
                timeout=timeout,
            )
        )
        extractors[method]._configured = True

    for index, letter in enumerate(letters, start=1):
        control_llm, control_hybrid = _replay_current_controls(letter, controls[letter.letter_id])
        control_predictions[LLM_METHOD].append(control_llm)
        control_predictions[HYBRID_METHOD].append(control_hybrid)
        v4_pair = _rematerialize_v4(letter, v4_rows[letter.letter_id], projection="v4")
        trust_pair = _rematerialize_v4(letter, v4_rows[letter.letter_id], projection="trust_item")
        for method in (LLM_METHOD, HYBRID_METHOD):
            v4_predictions[method].append(v4_pair[method])
            trust_predictions[method].append(trust_pair[method])
        row: dict[str, Any] = {
            "letter_id": letter.letter_id,
            "split": "dev20",
            "model": MENTION_UNIT_MODEL,
            "prompt_version": MENTION_UNIT_PROMPT_VERSION,
            "methods": {},
            "comparators": {
                "control_llm": control_llm.model_dump(mode="json"),
                "control_llm_with_rules": control_hybrid.model_dump(mode="json"),
                "v4_llm": v4_pair[LLM_METHOD].model_dump(mode="json"),
                "v4_llm_with_rules": v4_pair[HYBRID_METHOD].model_dump(mode="json"),
                "trust_item_llm": trust_pair[LLM_METHOD].model_dump(mode="json"),
                "trust_item_llm_with_rules": trust_pair[HYBRID_METHOD].model_dump(mode="json"),
            },
        }
        for method in (LLM_METHOD, HYBRID_METHOD):
            prompt = build_mention_unit_prompt(letter, method=method)
            raw_output = ""
            call_error: str | None = None
            try:
                prediction = extractors[method](prompt_input_json=prompt)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover - provider behavior.
                call_error = f"{type(exc).__name__}: {exc}"
            parsed = parse_mention_unit_json(raw_output, method=method)
            stats = operational[method]
            stats["calls"] += 1
            stats["parse_notes"] += len(parsed.errors)
            stats["items"] += len(parsed.record.items) if parsed.record is not None else 0
            stats["rows_with_blocking_parse_failure"] += int(
                parsed.record is None
                or any(
                    str(error).startswith(("invalid_json:", "schema_validation_error:", "not_run"))
                    for error in parsed.errors
                )
            )
            stats["rows_with_forbidden_fields"] += int(bool(parsed.forbidden_fields))
            if parsed.record is None:
                materialized = _empty_materialization(letter, parsed.errors)
            else:
                materialized = materialize_mention_unit(letter, parsed.record, method=method)
            candidate_predictions[method].append(materialized.prediction)
            stats["evidence_invalid"] += materialized.evidence_invalid
            stats["rule_changed_facts"] += sum(
                int(trace.get("changed", False)) for trace in materialized.rule_trace
            )
            row["methods"][method] = {
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parsed.errors,
                "forbidden_model_fields": parsed.forbidden_fields,
                "semantic_facts": materialized.semantic_facts,
                "rule_trace": materialized.rule_trace,
                "warnings": materialized.warnings,
                "evidence_invalid": materialized.evidence_invalid,
                "prediction": materialized.prediction.model_dump(mode="json"),
            }
        rows.append(row)
        if index % max(progress_every, 1) == 0:
            print(f"dev20: completed {index}/{len(letters)} rows", flush=True)
    return (
        candidate_predictions,
        control_predictions,
        v4_predictions,
        trust_predictions,
        rows,
        operational,
    )


def _replay_current_controls(letter: ExectLetter, saved: dict[str, Any]) -> tuple[Any, Any]:
    raw = str(saved.get("raw_output") or "")
    if not raw:
        raw = json.dumps({"clinical_events": saved.get("structured_events", [])})
    producer = structured_one_call.produce_structured_letter(
        letter,
        model="openai/gpt-5.6-luna",
        mode="replay",
        raw_output=raw,
        split="dev20",
        config=StructuredMethodConfig.selected(),
    )
    llm = structured_one_call.run_llm_only_letter(letter, producer).prediction
    hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer).prediction
    return llm, hybrid


def _rematerialize_v4(
    letter: ExectLetter,
    saved: dict[str, Any],
    *,
    projection: str,
) -> dict[str, PredictedLetter]:
    out: dict[str, PredictedLetter] = {}
    for method in (LLM_METHOD, HYBRID_METHOD):
        raw = str(saved["methods"][method]["raw_output"])
        parsed = parse_inventory_json(raw, method=method)
        if parsed.record is None:
            out[method] = PredictedLetter(letter_id=letter.letter_id, mentions=())
            continue
        out[method] = materialize_inventory(
            letter,
            parsed.record,
            method=method,
            projection=projection,  # type: ignore[arg-type]
        ).prediction
    return out


def _empty_materialization(letter: ExectLetter, errors: list[str]) -> InventoryMaterialization:
    return InventoryMaterialization(
        prediction=PredictedLetter(letter_id=letter.letter_id, mentions=()),
        semantic_facts=[],
        rule_trace=[],
        warnings=[],
        evidence_invalid=0,
        parse_failures=errors,
    )


def _score_method(gold: list[ExectLetter], predictions: list[Any]) -> dict[str, Any]:
    pred_letters = [to_exect_letter(prediction) for prediction in predictions]
    semantic = score_overall(
        gold,
        pred_letters,
        FAMILIES,
        semantic_config_for,
    )
    benchmark = score_overall(
        gold,
        pred_letters,
        FAMILIES,
        benchmark_config_for,
    )
    headline_scores = {
        "Diagnosis": score_concept_identity(gold, pred_letters, "Diagnosis").concept_only,
        "SeizureFrequency": score_frequency_state(gold, pred_letters).clinical_headline,
        "Prescription": score_prescription_components(gold, pred_letters).clinical_headline,
        "Investigations": score_investigations_components(gold, pred_letters).clinical_headline,
    }
    headline_f1 = _aggregate_f1(headline_scores.values())
    return {
        "semantic_f1": round(semantic.per_item.f1, 4),
        "semantic_family_f1": {
            family: round(score.per_item.f1, 4) for family, score in semantic.per_entity.items()
        },
        "benchmark_projection_f1": round(benchmark.per_item.f1, 4),
        "benchmark_family_f1": {
            family: round(score.per_item.f1, 4) for family, score in benchmark.per_entity.items()
        },
        "clinical_headline_f1": round(headline_f1, 4),
        "clinical_headline_family_f1": {
            family: round(score.f1, 4) for family, score in headline_scores.items()
        },
        "semantic_counts": _counts(semantic.per_item),
        "empty_gold_extras": _empty_gold_extras(gold, predictions),
        "nontarget_mentions": _nontarget_mentions(predictions),
    }


def _empty_gold_extras(
    gold: list[ExectLetter],
    predictions: Sequence[Any],
) -> dict[str, Any]:
    letters: dict[str, list[str]] = {family: [] for family in FAMILIES}
    counts: dict[str, int] = {family: 0 for family in FAMILIES}
    for letter, prediction in zip(gold, predictions, strict=True):
        for family in FAMILIES:
            if letter.entities(family):
                continue
            extras = [mention for mention in prediction.mentions if mention.entity == family]
            if extras:
                letters[family].append(letter.letter_id)
                counts[family] += len(extras)
    return {"letter_counts": {family: len(ids) for family, ids in letters.items()}, "mention_counts": counts, "letters": letters}


def _nontarget_mentions(predictions: Sequence[Any]) -> list[dict[str, str]]:
    found: list[dict[str, str]] = []
    for prediction in predictions:
        for mention in prediction.mentions:
            haystack = f"{mention.entity} {mention.text}"
            if _NONTARGET_RE.search(haystack):
                found.append(
                    {
                        "letter_id": prediction.letter_id,
                        "entity": mention.entity,
                        "text": mention.text,
                    }
                )
    return found


def _stop_checks(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    v4_results: dict[str, list[Any]],
    trust_results: dict[str, list[Any]],
) -> dict[str, Any]:
    candidate_empty = {
        method: _empty_gold_extras(letters, [PredictedLetter.model_validate(row["methods"][method]["prediction"]) for row in rows])
        for method in (LLM_METHOD, HYBRID_METHOD)
    }
    v4_empty = {
        method: _empty_gold_extras(letters, v4_results[method]) for method in (LLM_METHOD, HYBRID_METHOD)
    }
    trust_empty = {
        method: _empty_gold_extras(letters, trust_results[method])
        for method in (LLM_METHOD, HYBRID_METHOD)
    }
    candidate_nontargets = [
        hit
        for row in rows
        for method in (LLM_METHOD, HYBRID_METHOD)
        for hit in _nontarget_mentions(
            [PredictedLetter.model_validate(row["methods"][method]["prediction"])]
        )
    ]
    growth = _hybrid_growth(letters, rows)
    sf_rise = any(
        candidate_empty[method]["mention_counts"]["SeizureFrequency"]
        > max(
            v4_empty[method]["mention_counts"]["SeizureFrequency"],
            trust_empty[method]["mention_counts"]["SeizureFrequency"],
        )
        for method in (LLM_METHOD, HYBRID_METHOD)
    )
    revise = bool(sf_rise or candidate_nontargets or growth)
    return {
        "empty_gold_sf_extras_rose": sf_rise,
        "nontarget_mentions": candidate_nontargets,
        "hybrid_growth_from_unused_letter": growth,
        "verdict": "revise" if revise else "mechanically_clean",
        "baselines": {
            "v4": v4_empty,
            "trust_item": trust_empty,
            "mention_unit": candidate_empty,
        },
    }


def _hybrid_growth(letters: list[ExectLetter], rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_id = {letter.letter_id: letter for letter in letters}
    growth: list[dict[str, str]] = []
    for row in rows:
        letter = by_id[row["letter_id"]]
        method_row = row["methods"][HYBRID_METHOD]
        emitted = [
            f"{fact.get('text', '')} {fact.get('evidence', '')}"
            for fact in method_row.get("semantic_facts", [])
        ]
        haystack = _norm_span(" ".join(emitted))
        rewrite_texts = []
        for trace in method_row.get("rule_trace", []):
            if trace.get("action") not in _REWRITE_ACTIONS:
                continue
            after = trace.get("after") or {}
            rewrite_texts.extend(after.get("phrases") or [])
            if after.get("text"):
                rewrite_texts.append(str(after["text"]))
        allowed = {_norm_span(text) for text in rewrite_texts if text}
        prediction = PredictedLetter.model_validate(method_row["prediction"])
        for mention in prediction.mentions:
            mention_norm = _norm_span(mention.text)
            if mention_norm in haystack or mention_norm in allowed:
                continue
            if mention.text and mention.text.lower() in letter.note_text.lower():
                growth.append(
                    {
                        "letter_id": letter.letter_id,
                        "entity": mention.entity,
                        "text": mention.text,
                    }
                )
    return growth


def _emission_census(
    letters: list[ExectLetter],
    rows: list[dict[str, Any]],
    v4_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    census: dict[str, Any] = {"families": {}, "letters": []}
    totals = {
        family: {
            "gold_units": 0,
            "mention_unit_llm_exact": 0,
            "mention_unit_hybrid_exact": 0,
            "mention_unit_llm_read": 0,
            "mention_unit_hybrid_read": 0,
            "v4_llm_exact": 0,
            "v4_hybrid_exact": 0,
            "v4_llm_read": 0,
            "v4_hybrid_read": 0,
        }
        for family in FAMILIES
    }
    for letter, row in zip(letters, rows, strict=True):
        v4 = v4_rows[letter.letter_id]
        letter_row: dict[str, Any] = {"letter_id": letter.letter_id, "families": {}}
        for family in FAMILIES:
            gold_units = [
                {
                    "text": annotation.text,
                    "raw_text": annotation.raw_text or annotation.text,
                }
                for annotation in letter.entities(family)
            ]
            mu_llm = _carrier_texts(row["methods"][LLM_METHOD], "text")
            mu_hybrid = _carrier_texts(row["methods"][HYBRID_METHOD], "text")
            v4_llm = _v4_carrier_texts(v4["methods"][LLM_METHOD])
            v4_hybrid = _v4_carrier_texts(v4["methods"][HYBRID_METHOD])
            family_row = {
                "gold_units": gold_units,
                "mention_unit_llm": _span_matches(gold_units, mu_llm),
                "mention_unit_hybrid": _span_matches(gold_units, mu_hybrid),
                "v4_llm": _span_matches(gold_units, v4_llm),
                "v4_hybrid": _span_matches(gold_units, v4_hybrid),
            }
            letter_row["families"][family] = family_row
            totals[family]["gold_units"] += len(gold_units)
            for key, matched in (
                ("mention_unit_llm", family_row["mention_unit_llm"]),
                ("mention_unit_hybrid", family_row["mention_unit_hybrid"]),
                ("v4_llm", family_row["v4_llm"]),
                ("v4_hybrid", family_row["v4_hybrid"]),
            ):
                totals[family][f"{key}_exact"] += matched["exact"]
                totals[family][f"{key}_read"] += matched["read"]
        census["letters"].append(letter_row)
    census["families"] = totals
    return census


def _carrier_texts(method_row: dict[str, Any], field: str) -> list[str]:
    return [
        str(fact.get(field) or "")
        for fact in method_row.get("semantic_facts", [])
        if fact.get(field)
    ]


def _v4_carrier_texts(method_row: dict[str, Any]) -> list[str]:
    return [
        str(fact.get("event") or "")
        for fact in method_row.get("semantic_facts", [])
        if fact.get("event")
    ]


def _span_matches(gold_units: list[dict[str, str]], carriers: list[str]) -> dict[str, Any]:
    exact = 0
    read = 0
    unread: list[str] = []
    carrier_norms = [_norm_span(carrier) for carrier in carriers if carrier]
    for unit in gold_units:
        needles = {_norm_span(unit["text"]), _norm_span(unit["raw_text"])}
        needles.discard("")
        if any(needle in carrier_norms for needle in needles):
            exact += 1
            read += 1
            continue
        if any(needle in carrier for needle in needles for carrier in carrier_norms):
            read += 1
            continue
        unread.append(unit["raw_text"] or unit["text"])
    return {
        "exact": exact,
        "read": read,
        "unread": unread,
        "unread_count": len(unread),
    }


def _norm_span(text: str) -> str:
    return " ".join(text.lower().replace("-", " ").split())


def _aggregate_f1(scores: Iterable[Any]) -> float:
    tp = fp = fn = 0
    for score in scores:
        tp += int(score.tp)
        fp += int(score.fp)
        fn += int(score.fn)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return 2 * precision * recall / (precision + recall) if precision + recall else 0.0


def _counts(score: Any) -> dict[str, int]:
    return {"tp": int(score.tp), "fp": int(score.fp), "fn": int(score.fn)}


def _write_development_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _provenance() -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    return {
        "git_head": commit,
        "working_tree": "dirty_before_study; pre-existing user changes preserved",
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }


def _public_artifact_summary(artifact: dict[str, Any]) -> dict[str, Any]:
    return {
        key: artifact[key]
        for key in (
            "status",
            "split",
            "row_count",
            "model_calls",
            "methods",
            "stop_checks",
            "gold_span_emission",
            "claim_boundary",
        )
        if key in artifact
    }


def _render_report(artifact: dict[str, Any]) -> str:
    methods = artifact["methods"]
    lines = [
        "# ExECT mention-unit v1 — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-16  ",
        "Status: complete; GPT-5.6 Luna candidate measured",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Split: `dev20` (n=20)  ",
        "Model: `openai/gpt-5.6-luna`",
        "",
        "## Result",
        "",
        "| Method | semantic F1 | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, summary in methods.items():
        family = summary["clinical_headline_family_f1"]
        lines.append(
            f"| {name} | {summary['semantic_f1']:.4f} | {summary['clinical_headline_f1']:.4f} | "
            f"{family['Diagnosis']:.4f} | {family['SeizureFrequency']:.4f} | "
            f"{family['Prescription']:.4f} | {family['Investigations']:.4f} |"
        )
    stop = artifact["stop_checks"]
    lines += [
        "",
        f"Stop-check verdict: `{stop['verdict']}`.",
        "",
        "The development artifact retains row-level raw output, mention units, evidence checks, rule traces, gold-span emission, and comparator keys.",
        "The selected v0.9.24 / Decision 0050 result remains unchanged by this study.",
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
