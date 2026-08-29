"""Live Gan paper cells: cleaned hybrid and LLM-only."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import dspy
from dotenv import load_dotenv

from clinical_extraction.core.local_structured_output import FormatOnlyJsonRetry
from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.batch import (
    BatchChatItem,
    complete_chat_batch,
    uses_provider_batch,
)
from clinical_extraction.paper.comparison_contract import attach_living_envelope
from clinical_extraction.paper.exect import (
    HOSTED_SLUGS,
    LOCAL_SLUGS,
    MODELS,
    OLLAMA_NUM_CTX_ENV,
    ModelSpec,
    apply_reasoning_effort,
    cell3_thinking_max_tokens,
    paper_work_suffix,
)
from clinical_extraction.paper.gan_cell_replay import living_gan_stages
from clinical_extraction.paper.gan_later_stage import (
    CITED_SLUG as LATER_STAGE_SLUG,
)
from clinical_extraction.paper.gan_later_stage import (
    MAX_TOKENS as LATER_STAGE_MAX_TOKENS,
)
from clinical_extraction.paper.gan_later_stage import (
    LaterStageMethod,
    run_later_stage,
    verify_later_stage_prompt,
)
from clinical_extraction.paper.gan_later_stage import (
    prompt_version as later_stage_prompt_version,
)
from clinical_extraction.paper.lm import build_paper_lm, resolve_paper_api_base
from clinical_extraction.paper.methods import (
    METHOD_ALIASES,
    gan_machine_split,
    gan_row_count,
    holdout_is_aggregate_only,
    method_spec,
    split_for,
)
from clinical_extraction.paper.roster import model_by_slug
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    hybrid_structured_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm as gan_llm_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_and_rules_extract as and_rules_extract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    normalize_prompt_version,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_encode import (
    LLM_ENCODE_AUTHORED_KEYS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_extract import (
    GAN_LLM_EXTRACT,
    LLM_EXTRACT_AUTHORED_KEYS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.prompt_llm_select import (
    LLM_SELECT_AUTHORED_KEYS,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import llm as orch_llm
from clinical_extraction.tasks.seizure_frequency.gan2026.orchestration import (
    llm_with_rules as orch_hybrid,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.runners.config import (
    PipelineConfiguration,
)

ROOT = discover_repo_root(start=Path(__file__))
SPLIT_MANIFEST = "gan2026_split_v1"
WORK_ROOT = ROOT / "experiments/paper"
HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper"
MAX_TOKENS = {
    "gan_llm_only": 1200,
    "gan_llm_extract_raw": 5000,
    "gan_llm_extract": 5000,
    "gan_llm_and_rules_extract": 5000,
    "gan_llm_encode": LATER_STAGE_MAX_TOKENS,
    "gan_llm_select": LATER_STAGE_MAX_TOKENS,
    "gan_llm_select_from_extract": LATER_STAGE_MAX_TOKENS,
}
DEEPSEEK_MAX_TOKENS = 24000
HIGH_REASONING_GAN_LLM_ONLY_MAX_TOKENS = 16000


def _max_tokens_for(
    method: str,
    slug: str | None = None,
    reasoning_effort: str | None = None,
) -> int:
    if slug == "deepseek_v4_flash":
        return DEEPSEEK_MAX_TOKENS
    if method == "gan_llm_only" and reasoning_effort == "high":
        return HIGH_REASONING_GAN_LLM_ONLY_MAX_TOKENS
    base = MAX_TOKENS[method]
    if method == "gan_llm_extract":
        return cell3_thinking_max_tokens(base, reasoning_effort)
    return base


def verify_gan(
    method: str,
    split: str,
    slug: str | None = None,
) -> dict[str, Any]:
    """Check a Gan paper identity without calling a model or loading holdout notes."""

    method = METHOD_ALIASES.get(method, method)
    spec = method_spec(method)
    if spec["task"] != "gan2026":
        raise ValueError(f"{method} is not a Gan paper method")
    split_for(method, split)
    prompt = _prompt_version(method)
    holdout = holdout_is_aggregate_only(split)
    if method == "gan_llm_only":
        before = gan_llm_only.PROMPT_VERSION
        payload = json.loads(gan_llm_only.build_prompt_input(_placeholder_record()))
        authored = list(gan_llm_only.LLM_ONLY_AUTHORED_KEYS)
        if list(payload) != authored:
            raise RuntimeError("gan_llm_only prompt drifted from authored keys")
        if gan_llm_only.PROMPT_VERSION != before:
            raise RuntimeError("LLM-only payload check changed the live default")
        if gan_llm_only.PROMPT_VERSION != gan_llm_only.GAN_LLM_ONLY:
            raise RuntimeError("gan_llm_only live default drifted")
    elif method == "gan_llm_extract":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=GAN_LLM_EXTRACT,
            )
        )
        authored = list(LLM_EXTRACT_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError("gan_llm_extract prompt drifted from authored keys")
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError("gan_llm_extract request still emits the research envelope")
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract request still names the dataset")
        if "label_forms" not in payload:
            raise RuntimeError("gan_llm_extract request dropped label_forms")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("extract payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_and_rules_extract":
        if slug is not None and slug != LATER_STAGE_SLUG:
            raise RuntimeError("gan_llm_and_rules_extract runs on Gemini only")
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=and_rules_extract.GAN_LLM_AND_RULES_EXTRACT,
            )
        )
        authored = list(and_rules_extract.LLM_AND_RULES_EXTRACT_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_and_rules_extract prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_and_rules_extract request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_and_rules_extract request still names the dataset")
        if "label_forms" not in payload or "suggested_evidence" not in payload:
            raise RuntimeError("gan_llm_and_rules_extract request dropped a required block")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("both-extract payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method in {
        "gan_llm_encode",
        "gan_llm_select",
        "gan_llm_select_from_extract",
    }:
        if slug is not None and slug != LATER_STAGE_SLUG:
            raise RuntimeError("later-stage Gan encode and select run on Gemini only")
        verify_later_stage_prompt(cast(LaterStageMethod, method))
        authored = (
            list(LLM_ENCODE_AUTHORED_KEYS)
            if method == "gan_llm_encode"
            else list(LLM_SELECT_AUTHORED_KEYS)
        )
    else:
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=hybrid_structured_events.GAN_LLM_EXTRACT_RAW,
            )
        )
        authored = list(hybrid_structured_events.LLM_EXTRACT_RAW_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError("gan_llm_extract_raw prompt drifted from authored keys")
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_raw request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_raw request still names the dataset")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("hybrid payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    result: dict[str, Any] = {
        "ok": True,
        "method": method,
        "prompt_version": prompt,
        "split": split,
        "split_machine": gan_machine_split(split),
        "split_manifest": SPLIT_MANIFEST,
        "row_count": gan_row_count(split),
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "test450_authorized": holdout,
        "hosted": list(HOSTED_SLUGS),
        "local": list(LOCAL_SLUGS),
        "max_tokens": _max_tokens_for(method, slug),
        "work_root": (WORK_ROOT / method).relative_to(ROOT).as_posix(),
        "holdout_scratch": (HOLDOUT_SCRATCH / method).relative_to(ROOT).as_posix(),
        "authored_keys": authored,
        "default_prompt_version": (
            gan_llm_only.PROMPT_VERSION
            if method == "gan_llm_only"
            else prompt
        ),
    }
    if slug is not None:
        result["model"] = model_by_slug(slug)["model"]
        result["model_slug"] = slug
    return result


def run_gan(
    method: str,
    slug: str,
    *,
    live: bool,
    split: str,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
    temperature: float | None = None,
) -> dict[str, Any]:
    """Run one allowed Gan paper cell."""

    method = METHOD_ALIASES.get(method, method)
    verify_gan(method, split, slug)
    if not live:
        raise RuntimeError("run_gan requires live=True")
    if method in {
        "gan_llm_encode",
        "gan_llm_select",
        "gan_llm_select_from_extract",
    }:
        if temperature is not None:
            raise RuntimeError("temperature override is not wired for later-stage Gan")
        return run_later_stage(
            cast(LaterStageMethod, method),
            slug,
            split=split,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout,
            progress_every=progress_every,
            reasoning_effort=reasoning_effort,
        )
    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    spec = apply_reasoning_effort(MODELS[slug], reasoning_effort)
    if temperature is not None:
        spec = replace(spec, temperature=temperature)
    if thinking is not None:
        if slug != "deepseek_v4_flash":
            raise RuntimeError("thinking toggle is DeepSeek only")
        spec = replace(spec, thinking_type=thinking)
    elif slug == "deepseek_v4_flash" and spec.reasoning_effort:
        spec = replace(spec, thinking_type="enabled")
    holdout = holdout_is_aggregate_only(split)
    machine = gan_machine_split(split)
    expected = gan_row_count(split)
    load_dotenv(ROOT / ".env", override=False)
    records = load_records_for_split(machine)
    if len(records) != expected:
        raise RuntimeError(f"expected {expected} {split} records, found {len(records)}")
    work_root = (HOLDOUT_SCRATCH if holdout else WORK_ROOT) / method / spec.slug
    segment = paper_work_suffix(spec)
    if segment:
        work_root = work_root / segment
    work_root = work_root / split
    work_root.mkdir(parents=True, exist_ok=True)
    rows_path = work_root / "rows.jsonl"
    started = datetime.now(UTC).isoformat()
    prompt = _prompt_version(method)
    existing = [] if overwrite else _existing_complete_rows(rows_path, prompt)
    done = {int(row["source_row_index"]) for row in existing}
    todo = [record for record in records if record.source_row_index not in done]
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    max_tokens = _max_tokens_for(method, spec.slug, spec.reasoning_effort)
    if todo and not uses_provider_batch(spec.slug):
        _prepare_live_runtime(
            spec,
            api_base=resolved_base,
            timeout=timeout or spec.timeout,
            max_tokens=max_tokens,
        )
    rows = list(existing)
    by_index = {int(row["source_row_index"]): row for row in existing}
    program, retry_program = _programs(method) if todo else (None, None)
    config = PipelineConfiguration(
        architecture="llm" if method == "gan_llm_only" else "llm_with_rules",
        model=spec.model,
        temperature=spec.temperature,
        max_tokens=max_tokens,
        dspy_cache=False,
        api_base=resolved_base,
        timeout=timeout or spec.timeout,
        prompt_version=prompt,
        repair_mode=_repair_mode(method),
    )
    batch_raws: dict[str, str] = {}
    call_transport = "sync"
    if todo and uses_provider_batch(spec.slug):
        call_transport = "openai_batch" if spec.slug == "gpt56luna" else "openrouter_batch"
        batch_raws = complete_chat_batch(
            spec,
            _gan_batch_items(method, todo, program),
            work_dir=work_root,
            max_tokens=max_tokens,
            overwrite=overwrite,
        )
    for index, record in enumerate(todo, start=1):
        raw_output = batch_raws.get(str(record.source_row_index))
        row = _run_record(
            method,
            record,
            config,
            split=split,
            machine=machine,
            program=None if raw_output is not None else program,
            retry_program=None if raw_output is not None else retry_program,
            raw_output=raw_output,
        )
        if row.get("prompt_version") != prompt:
            raise RuntimeError(
                "a test450 row used the wrong prompt version"
                if holdout
                else f"{record.source_row_index} used {row.get('prompt_version')}"
            )
        if row.get("call_error"):
            raise RuntimeError(
                "a test450 row call failed"
                if holdout
                else f"{record.source_row_index} call failed: {row['call_error']}"
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
    summary = _summarize(method, rows)
    artifact = {
        "schema_version": f"paper.{method}.v1",
        "generated_on": "2026-08-17",
        "method": method,
        "model_slug": spec.slug,
        "model": spec.model,
        "model_label": spec.label,
        "temperature": spec.temperature,
        "max_tokens": max_tokens,
        "thinking_type": spec.thinking_type,
        "reasoning_effort": spec.reasoning_effort,
        "cache": False,
        "split": split,
        "split_machine": machine,
        "split_manifest": SPLIT_MANIFEST,
        "row_count": len(records),
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "prompt_version": prompt,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "call_transport": call_transport,
        "model_calls": len(todo),
        "summary": _public_summary(summary, holdout=holdout),
        "claim_boundary": (
            "Gan aggregate-only test450. Do not inspect holdout rows."
            if holdout
            else "Gan development cell. Not holdout."
        ),
    }
    if not holdout:
        artifact["incorrect_source_row_indices"] = [
            int(row["source_row_index"])
            for row in rows
            if not (row.get("comparison") or {}).get("purist_correct")
        ]
    artifact = attach_living_envelope(
        artifact,
        method=method,
        stages=living_gan_stages(
            rows,
            {record.source_row_index: record for record in records},
            method=method,
        ),
        replay_mode="live",
        prompt_version=prompt,
    )
    out = work_root / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "method": method,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "summary": artifact["summary"],
        "default_prompt_version": prompt,
    }


def _prompt_version(method: str) -> str:
    method = METHOD_ALIASES.get(method, method)
    if method == "gan_llm_only":
        return gan_llm_only.GAN_LLM_ONLY
    if method == "gan_llm_extract_raw":
        return hybrid_structured_events.GAN_LLM_EXTRACT_RAW
    if method == "gan_llm_extract":
        return GAN_LLM_EXTRACT
    if method == "gan_llm_and_rules_extract":
        return and_rules_extract.GAN_LLM_AND_RULES_EXTRACT
    if method in {
        "gan_llm_encode",
        "gan_llm_select",
        "gan_llm_select_from_extract",
    }:
        return later_stage_prompt_version(cast(LaterStageMethod, method))
    raise ValueError(method)


def _repair_mode(method: str) -> str | None:
    method = METHOD_ALIASES.get(method, method)
    if method == "gan_llm_only":
        return None
    if method == "gan_llm_extract":
        return "raw_model"
    return "llm_select"


def _placeholder_record() -> GanFrequencyRecord:
    return GanFrequencyRecord(
        source_row_index=10,
        note_text="Present seizure frequency: two seizures per month.",
        gold_label="2 per month",
        gold_reference="two seizures per month",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label="2 per month",
        gold_label_kind=FrequencyLabelKind.FREQUENCY,
        gold_yearly_bounds=(24.0, 24.0),
        gold_monthly_frequency=2.0,
    )


def _existing_complete_rows(path: Path, prompt_version: str) -> list[dict[str, Any]]:
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
        if normalize_prompt_version(str(row.get("prompt_version"))) != normalize_prompt_version(
            prompt_version
        ):
            raise RuntimeError(f"{path} has {index} with {row.get('prompt_version')}")
        if row.get("call_error") or not row.get("raw_output"):
            continue
        seen.add(index)
        rows.append(row)
    return rows


def _gan_batch_items(
    method: str,
    records: Sequence[GanFrequencyRecord],
    program: Any,
) -> list[BatchChatItem]:
    items: list[BatchChatItem] = []
    for record in records:
        if method == "gan_llm_only":
            prompt_input = gan_llm_only.build_prompt_input(record)
        else:
            prompt_input = hybrid_structured_events.build_prompt_input(
                record,
                prompt_version=_prompt_version(method),
            )
        items.append(
            BatchChatItem(
                custom_id=str(record.source_row_index),
                messages=program.render_messages(prompt_input_json=prompt_input),
            )
        )
    return items


def _programs(method: str) -> tuple[Any, Any]:
    if method == "gan_llm_only":
        return gan_llm_only.DspyCanonicalLlmExtractor(), None
    return hybrid_structured_events.DspyStructuredExtractor(), FormatOnlyJsonRetry()


def hydrate_saved_raw_row(
    method: str,
    record: GanFrequencyRecord,
    raw_output: str,
    *,
    split: str = "dev750",
    repair_mode: str | None = None,
) -> dict[str, Any]:
    """Rebuild parse, repair, and row_trace from a promoted paper raw_output."""

    method = METHOD_ALIASES.get(method, method)
    spec = method_spec(method)
    if spec["task"] != "gan2026":
        raise ValueError(f"{method} is not a Gan paper method")
    machine = gan_machine_split(split)
    config = PipelineConfiguration(
        architecture="llm" if method == "gan_llm_only" else "llm_with_rules",
        dspy_cache=False,
        prompt_version=_prompt_version(method),
        repair_mode=_repair_mode(method) if repair_mode is None else repair_mode,
    )
    return _run_record(
        method,
        record,
        config,
        split=split,
        machine=machine,
        program=None,
        retry_program=None,
        raw_output=raw_output,
    )


def _run_record(
    method: str,
    record: GanFrequencyRecord,
    config: PipelineConfiguration,
    *,
    split: str,
    machine: str,
    program: Any,
    retry_program: Any,
    raw_output: str | None = None,
) -> dict[str, Any]:
    if method == "gan_llm_only":
        result = orch_llm.run_record(
            record, config, mode="live", program=program, raw_output=raw_output
        )
        decision = result.parsed_model_output
        comparison = gan_llm_only._compare_to_gold(record, decision) if decision else None
        row_trace = dict(result.diagnostics["row_trace"])
        row_trace["scoring"] = comparison
        return {
            "source_row_index": record.source_row_index,
            "split": machine,
            "paper_split": split,
            "split_manifest": SPLIT_MANIFEST,
            "prompt_version": gan_llm_only.PROMPT_VERSION,
            "prompt_input_json": result.diagnostics["prompt_input_json"],
            "raw_output": result.raw_model_output or "",
            "reused_raw_output": result.diagnostics["reused_raw_output"],
            "call_error": result.diagnostics["call_error"],
            "parse_errors": result.diagnostics["parse_errors"],
            "decision_record": decision.model_dump() if decision else None,
            "evidence_text_contained": result.scorer_projection["evidence_text_contained"],
            "row_trace": row_trace,
            "reference": {
                "gold_label": record.gold_label,
                "gold_monthly_frequency": record.gold_monthly_frequency,
                "row_ok": record.row_ok,
            },
            "comparison": comparison,
        }
    result = orch_hybrid.run_record(
        record,
        config,
        mode="live",
        program=program,
        format_retry_program=retry_program,
        raw_output=raw_output,
    )
    extraction = result.parsed_model_output
    comparison = (
        hybrid_structured_events._compare_to_gold(record, extraction) if extraction else None
    )
    row_trace = dict(result.diagnostics["row_trace"])
    row_trace["scoring"] = comparison
    return {
        "source_row_index": record.source_row_index,
        "split": machine,
        "paper_split": split,
        "split_manifest": SPLIT_MANIFEST,
        "pipeline_family": "llm_with_rules",
        "prompt_version": _prompt_version(method),
        "prompt_input_json": result.diagnostics["prompt_input_json"],
        "raw_output": result.raw_model_output or "",
        "reused_raw_output": result.diagnostics["reused_raw_output"],
        "call_error": result.diagnostics["call_error"],
        "initial_parse_errors": result.diagnostics["initial_parse_errors"],
        "parse_errors": result.diagnostics["parse_errors"],
        "structured_output_failure_codes": result.diagnostics[
            "structured_output_failure_codes"
        ],
        "format_retry_output": result.diagnostics["format_retry_output"],
        "format_retry_notes": result.diagnostics["format_retry_notes"],
        "structured_record": extraction.model_dump() if extraction else None,
        "normalized_events": result.diagnostics["normalized_events"],
        "evidence_valid": result.diagnostics["evidence_valid"],
        "row_trace": row_trace,
        "reference": {
            "gold_label": record.gold_label,
            "gold_normalized_label": record.gold_normalized_label,
            "gold_label_kind": str(record.gold_label_kind),
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "row_ok": record.row_ok,
        },
        "comparison": comparison,
    }


def _summarize(method: str, rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    if method == "gan_llm_only":
        return gan_llm_only.summarize_records(rows)
    return hybrid_structured_events.summarize_records(rows)


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
