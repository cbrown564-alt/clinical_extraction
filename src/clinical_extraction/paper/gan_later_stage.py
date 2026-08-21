"""Gemini later-stage Gan encode and select on a saved extract ledger."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from dotenv import load_dotenv

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.batch import BatchChatItem, complete_chat_batch
from clinical_extraction.paper.exect import (
    MODELS,
    OLLAMA_NUM_CTX_ENV,
    ModelSpec,
    apply_reasoning_effort,
)
from clinical_extraction.paper.lm import build_paper_lm, resolve_paper_api_base
from clinical_extraction.paper.methods import (
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    DspyStructuredExtractor,
    StructuredExtractionRecord,
    StructuredRepairConfig,
    _compare_to_gold,
    parse_structured_json,
    summarize_records,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_encode import (
    GAN_LLM_ENCODE,
    LLM_ENCODE_AUTHORED_KEYS,
    build_llm_encode_prompt_input,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    GAN_LLM_SELECT,
    LLM_SELECT_AUTHORED_KEYS,
    build_llm_select_prompt_input,
)

LaterStageMethod = Literal["gan_llm_encode", "gan_llm_select"]
CITED_SLUG = "gemini37flash"
EXTRACT_METHOD = "gan_llm_with_rules"
MAX_TOKENS = 1500
ROOT = discover_repo_root(start=Path(__file__))
SPLIT_MANIFEST = "gan2026_split_v1"
WORK_ROOT = ROOT / "experiments/paper"


def prompt_version(method: LaterStageMethod) -> str:
    if method == "gan_llm_encode":
        return GAN_LLM_ENCODE
    return GAN_LLM_SELECT


def parse_extract_ledger(
    raw_output: str,
    *,
    note_text: str | None,
) -> StructuredExtractionRecord:
    extraction, _, errors = parse_structured_json(
        raw_output,
        note_text=note_text,
        repair_config=StructuredRepairConfig.for_mode("raw_model"),
    )
    if extraction is None:
        raise ValueError(f"extract raw did not parse: {errors}")
    return extraction


def extract_rows_path(split: str, slug: str = CITED_SLUG) -> Path:
    return (
        ROOT
        / "paper_experiments/gan"
        / EXTRACT_METHOD
        / slug
        / split
        / "rows.jsonl"
    )


def encode_work_rows_path(split: str, slug: str = CITED_SLUG) -> Path:
    return WORK_ROOT / "gan_llm_encode" / slug / split / "rows.jsonl"


def parse_encode_labels(raw_output: str) -> list[dict[str, str]]:
    payload = _payload(raw_output)
    rows = payload.get("labels")
    if rows is None:
        rows = payload.get("events")
    if not isinstance(rows, list):
        raise ValueError("encode output has no labels list")
    labels: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("encode label row is not an object")
        event_id = row.get("event_id")
        label = row.get("label")
        if not event_id or label is None:
            raise ValueError("encode label row is missing event_id or label")
        labels.append({"event_id": str(event_id), "label": str(label)})
    return labels


def parse_select_answer(raw_output: str) -> dict[str, Any]:
    payload = _payload(raw_output)
    ids = payload.get("selected_event_ids")
    if not isinstance(ids, list):
        raise ValueError("select output has no selected_event_ids")
    answer: dict[str, Any] = {
        "selected_event_ids": [str(item) for item in ids],
    }
    if payload.get("label") not in (None, ""):
        answer["label"] = str(payload["label"])
    return answer


def project_encode_label(
    labels_by_id: Mapping[str, str],
    selected_event_ids: Sequence[str],
) -> str | None:
    for event_id in selected_event_ids:
        label = labels_by_id.get(event_id)
        if label:
            return label
    if selected_event_ids:
        return "unknown"
    return "no seizure frequency reference"


def project_select_label(
    labels_by_id: Mapping[str, str],
    selected_event_ids: Sequence[str],
    written_label: str | None,
) -> str | None:
    if written_label:
        return written_label
    return project_encode_label(labels_by_id, selected_event_ids)


def verify_later_stage_prompt(method: LaterStageMethod) -> None:
    events = [
        {
            "event_id": "e1",
            "raw_value": "two per month",
            "evidence": "two seizures per month",
            "kind": "frequency_rate",
            "temporality": "current",
            "assertion_status": "asserted",
            "applies_to": None,
            "time_window": None,
        }
    ]
    if method == "gan_llm_encode":
        payload = json.loads(build_llm_encode_prompt_input(events))
        if set(payload) != set(LLM_ENCODE_AUTHORED_KEYS):
            raise RuntimeError("gan_llm_encode prompt drifted from authored keys")
        return
    payload = json.loads(
        build_llm_select_prompt_input(
            [{**events[0], "label": "2 per month"}],
            extract_selected_event_ids=["e1"],
            extract_label="two per month",
        )
    )
    if set(payload) != set(LLM_SELECT_AUTHORED_KEYS):
        raise RuntimeError("gan_llm_select prompt drifted from authored keys")


def run_later_stage(
    method: LaterStageMethod,
    slug: str,
    *,
    split: str,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    if slug != CITED_SLUG:
        raise RuntimeError("later-stage Gan encode and select run on Gemini only")
    if holdout_is_aggregate_only(split):
        raise RuntimeError("later-stage Gan calls are development-only in this cut")
    spec = apply_reasoning_effort(MODELS[slug], reasoning_effort)
    load_dotenv(ROOT / ".env", override=False)
    machine = gan_machine_split(split)
    expected = gan_row_count(split)
    records = load_records_for_split(machine)
    if len(records) != expected:
        raise RuntimeError(f"expected {expected} {split} records, found {len(records)}")
    extract_by_index = _load_jsonl_by_index(extract_rows_path(split, slug))
    encode_by_index: dict[int, dict[str, Any]] = {}
    if method == "gan_llm_select":
        encode_path = encode_work_rows_path(split, slug)
        if not encode_path.exists():
            raise RuntimeError("gan_llm_select needs a finished gan_llm_encode work cell")
        encode_by_index = _load_jsonl_by_index(encode_path)
    work_root = WORK_ROOT / method / spec.slug / split
    work_root.mkdir(parents=True, exist_ok=True)
    rows_path = work_root / "rows.jsonl"
    started = datetime.now(UTC).isoformat()
    prompt = prompt_version(method)
    existing = [] if overwrite else _existing_complete_rows(rows_path, prompt)
    done = {int(row["source_row_index"]) for row in existing}
    todo = [record for record in records if record.source_row_index not in done]
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    program = DspyStructuredExtractor()
    if todo:
        _prepare_live_runtime(
            spec,
            api_base=resolved_base,
            timeout=timeout or spec.timeout,
            max_tokens=MAX_TOKENS,
        )
    batch_raws = complete_chat_batch(
        spec,
        _batch_items(method, todo, extract_by_index, encode_by_index, program),
        work_dir=work_root,
        max_tokens=MAX_TOKENS,
    ) if todo else {}
    by_index = {int(row["source_row_index"]): row for row in existing}
    for index, record in enumerate(todo, start=1):
        raw_output = batch_raws.get(str(record.source_row_index), "")
        row = score_later_stage_row(
            method,
            record,
            raw_output,
            extract_row=extract_by_index[record.source_row_index],
            encode_row=encode_by_index.get(record.source_row_index),
            split=split,
            machine=machine,
        )
        if row.get("call_error"):
            raise RuntimeError(
                f"{record.source_row_index} call failed: {row['call_error']}"
            )
        by_index[record.source_row_index] = row
        rows = [
            by_index[item.source_row_index]
            for item in records
            if item.source_row_index in by_index
        ]
        write_jsonl_rows(rows, rows_path)
        if progress_every and index % progress_every == 0:
            print(f"{spec.slug} {method} {split}: {len(rows)}/{len(records)}", flush=True)
    if len(by_index) != len(records):
        raise RuntimeError(f"{method} {split} has {len(by_index)} rows, expected {len(records)}")
    rows = [by_index[record.source_row_index] for record in records]
    write_jsonl_rows(rows, rows_path)
    summary = summarize_records(rows)
    artifact = {
        "schema_version": f"paper.{method}.v1",
        "generated_on": "2026-08-21",
        "method": method,
        "model_slug": spec.slug,
        "model": spec.model,
        "split": split,
        "split_machine": machine,
        "split_manifest": SPLIT_MANIFEST,
        "row_count": len(records),
        "row_policy": "development_review_permitted",
        "prompt_version": prompt,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "call_transport": "openrouter_batch",
        "model_calls": len(todo),
        "summary": _public_summary(summary, holdout=False),
        "claim_boundary": "Gan development later-stage cell. Not holdout. No hybrid post-stack.",
        "incorrect_source_row_indices": [
            int(row["source_row_index"])
            for row in rows
            if not (row.get("comparison") or {}).get("purist_correct")
        ],
    }
    out = work_root / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "method": method,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "summary": artifact["summary"],
        "default_prompt_version": prompt,
    }


def score_later_stage_row(
    method: LaterStageMethod,
    record: GanFrequencyRecord,
    raw_output: str,
    *,
    extract_row: Mapping[str, Any],
    encode_row: Mapping[str, Any] | None,
    split: str,
    machine: str,
) -> dict[str, Any]:
    extract = parse_extract_ledger(
        str(extract_row["raw_output"]),
        note_text=record.note_text,
    )
    parse_errors: list[str] = []
    call_error = None if raw_output else "missing_raw_output"
    submitted = extract.model_copy(deep=True)
    labels_by_id: dict[str, str] = {}
    prompt_input = ""
    try:
        if method == "gan_llm_encode":
            prompt_input = build_llm_encode_prompt_input(
                [event.model_dump() for event in extract.events]
            )
            for item in parse_encode_labels(raw_output):
                labels_by_id[item["event_id"]] = item["label"]
            for event in extract.events:
                labels_by_id.setdefault(event.event_id, "unknown")
            submitted = extract.model_copy(
                update={
                    "selection": extract.selection.model_copy(
                        update={
                            "final_label": project_encode_label(
                                labels_by_id,
                                extract.selection.selected_event_ids,
                            )
                        }
                    )
                }
            )
        else:
            if encode_row is None:
                raise RuntimeError("select row is missing its encode row")
            encoded_events = list(encode_row["encoded_events"])
            labels_by_id = {
                str(event["event_id"]): str(event["label"]) for event in encoded_events
            }
            prompt_input = build_llm_select_prompt_input(
                encoded_events,
                extract_selected_event_ids=extract.selection.selected_event_ids,
                extract_label=extract.selection.final_label,
            )
            answer = parse_select_answer(raw_output)
            selected_ids = answer["selected_event_ids"]
            submitted = extract.model_copy(
                update={
                    "selection": extract.selection.model_copy(
                        update={
                            "selected_event_ids": selected_ids,
                            "final_label": project_select_label(
                                labels_by_id,
                                selected_ids,
                                answer.get("label"),
                            ),
                        }
                    )
                }
            )
    except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parse_errors.append(str(exc))
        submitted = extract
    comparison = _compare_to_gold(record, submitted) if not parse_errors else {}
    encoded_events = [
        {
            "event_id": event.event_id,
            "label": labels_by_id.get(event.event_id, ""),
            "kind": event.kind,
            "temporality": event.temporality,
            "assertion_status": event.assertion_status,
            "applies_to": event.applies_to,
            "time_window": event.time_window,
            "evidence": event.evidence,
        }
        for event in extract.events
    ]
    return {
        "source_row_index": record.source_row_index,
        "split": machine,
        "paper_split": split,
        "split_manifest": SPLIT_MANIFEST,
        "prompt_version": prompt_version(method),
        "prompt_input_json": prompt_input,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "structured_record": submitted.model_dump(),
        "encoded_events": encoded_events,
        "row_trace": {"scoring": comparison},
        "reference": {
            "gold_label": record.gold_label,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "comparison": comparison,
    }


def _payload(raw_output: str) -> dict[str, Any]:
    blob = extract_json_object(raw_output) or raw_output
    payload = json.loads(blob)
    if not isinstance(payload, dict):
        raise ValueError("later-stage output is not a JSON object")
    return payload


def _load_jsonl_by_index(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        rows[int(row["source_row_index"])] = row
    return rows


def _existing_complete_rows(path: Path, prompt_version_name: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    seen: set[int] = set()
    for row in load_jsonl_rows(path):
        source = row.get("source_row_index")
        if source is None:
            continue
        index = int(source)
        if index in seen:
            continue
        if row.get("prompt_version") != prompt_version_name:
            raise RuntimeError(f"{path} has {index} with {row.get('prompt_version')}")
        if row.get("call_error") or not row.get("raw_output"):
            continue
        seen.add(index)
        rows.append(row)
    return rows


def _public_summary(summary: Mapping[str, Any], *, holdout: bool) -> dict[str, Any]:
    payload = dict(summary)
    if holdout:
        payload.pop("final_labels", None)
        payload.pop("applied_rule_family_counts", None)
    return payload


def _prepare_live_runtime(
    spec: ModelSpec,
    *,
    api_base: str | None,
    timeout: int,
    max_tokens: int,
) -> None:
    if spec.num_ctx is not None:
        existing = os.environ.get(OLLAMA_NUM_CTX_ENV)
        declared = str(spec.num_ctx)
        if existing is not None and existing != declared:
            raise RuntimeError(
                f"{OLLAMA_NUM_CTX_ENV}={existing} conflicts with {declared}"
            )
        os.environ[OLLAMA_NUM_CTX_ENV] = declared
    if spec.slug == "gemini37flash" and spec.reasoning_effort:
        os.environ["GEMINI_REASONING_EFFORT"] = spec.reasoning_effort
    if spec.credential_env and not any(
        os.environ.get(name, "").strip() for name in spec.credential_env
    ):
        names = " or ".join(spec.credential_env)
        raise RuntimeError(f"{names} is missing; stopping before any candidate call")
    dspy.configure(
        lm=build_paper_lm(
            spec.model,
            temperature=spec.temperature,
            max_tokens=max_tokens,
            cache=False,
            api_base=api_base,
            timeout=timeout,
            reasoning_effort=spec.reasoning_effort,
            thinking_type=spec.thinking_type,
        )
    )


def _batch_items(
    method: LaterStageMethod,
    records: Sequence[GanFrequencyRecord],
    extract_by_index: Mapping[int, Mapping[str, Any]],
    encode_by_index: Mapping[int, Mapping[str, Any]],
    program: DspyStructuredExtractor,
) -> list[BatchChatItem]:
    items: list[BatchChatItem] = []
    for record in records:
        extract = parse_extract_ledger(
            str(extract_by_index[record.source_row_index]["raw_output"]),
            note_text=record.note_text,
        )
        if method == "gan_llm_encode":
            prompt_input = build_llm_encode_prompt_input(
                [event.model_dump() for event in extract.events]
            )
        else:
            encoded_events = list(
                encode_by_index[record.source_row_index]["encoded_events"]
            )
            prompt_input = build_llm_select_prompt_input(
                encoded_events,
                extract_selected_event_ids=extract.selection.selected_event_ids,
                extract_label=extract.selection.final_label,
            )
        items.append(
            BatchChatItem(
                custom_id=str(record.source_row_index),
                messages=program.render_messages(prompt_input_json=prompt_input),
            )
        )
    return items
