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
    apply_temperature,
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
    later_stage_slug_permitted,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as extract_encode_select,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_examples_only as extract_examples_only,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_holgate_label as extract_holgate_label,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_holgate_like as extract_holgate,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_no_evidence as extract_no_evidence,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_no_examples as extract_no_examples,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_no_examples_no_evidence_no_forms as extract_combined,
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
    "gan_llm_extract_no_examples": 5000,
    "gan_llm_extract_holgate_like": 5000,
    "gan_llm_extract_holgate_label": 1200,
    "gan_llm_extract_no_evidence": 5000,
    "gan_llm_extract_examples_only": 5000,
    "gan_llm_extract_no_examples_no_evidence_no_forms": 5000,
    "gan_llm_extract_encode_select": 8000,
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
    elif method == "gan_llm_extract_no_examples":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_no_examples.GAN_LLM_EXTRACT_NO_EXAMPLES,
            )
        )
        authored = list(extract_no_examples.LLM_EXTRACT_NO_EXAMPLES_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_no_examples prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_no_examples request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_no_examples request still names the dataset")
        if "label_forms" not in payload:
            raise RuntimeError("gan_llm_extract_no_examples request dropped label_forms")
        if "examples" in json.dumps(payload["label_forms"]):
            raise RuntimeError("gan_llm_extract_no_examples still lists examples")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("no-examples payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_holgate_like":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_holgate.GAN_LLM_EXTRACT_HOLGATE_LIKE,
            )
        )
        authored = list(extract_holgate.LLM_EXTRACT_HOLGATE_LIKE_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_holgate_like prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_holgate_like request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_holgate_like request still names the dataset")
        if "label_forms" in payload:
            raise RuntimeError("gan_llm_extract_holgate_like request still has label_forms")
        if "I do not know" not in blob:
            raise RuntimeError("gan_llm_extract_holgate_like dropped the Holgate abstention")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("Holgate-like payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_holgate_label":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_holgate_label.GAN_LLM_EXTRACT_HOLGATE_LABEL,
            )
        )
        authored = list(extract_holgate_label.LLM_EXTRACT_HOLGATE_LABEL_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_holgate_label prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_holgate_label request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_holgate_label request still names the dataset")
        if "event_schema" in payload or "label_forms" in payload:
            raise RuntimeError("gan_llm_extract_holgate_label still has a codebook schema")
        if "I do not know" not in blob:
            raise RuntimeError("gan_llm_extract_holgate_label dropped the Holgate abstention")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("Holgate-label payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_no_evidence":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_no_evidence.GAN_LLM_EXTRACT_NO_EVIDENCE,
            )
        )
        authored = list(extract_no_evidence.LLM_EXTRACT_NO_EVIDENCE_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_no_evidence prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_no_evidence request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_no_evidence request still names the dataset")
        if "evidence" in payload["event_schema"] or "evidence" in payload["selection_schema"]:
            raise RuntimeError("gan_llm_extract_no_evidence still asks for evidence")
        if "label_forms" not in payload:
            raise RuntimeError("gan_llm_extract_no_evidence dropped label_forms")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("no-evidence payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_examples_only":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_examples_only.GAN_LLM_EXTRACT_EXAMPLES_ONLY,
            )
        )
        authored = list(extract_examples_only.LLM_EXTRACT_EXAMPLES_ONLY_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_examples_only prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_examples_only request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError("gan_llm_extract_examples_only request still names the dataset")
        if "label_forms" in payload:
            raise RuntimeError("gan_llm_extract_examples_only still has label_forms")
        if "examples" not in payload:
            raise RuntimeError("gan_llm_extract_examples_only dropped examples")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("examples-only payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_no_examples_no_evidence_no_forms":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(hybrid_structured_events.build_prompt_input(
            _placeholder_record(),
            prompt_version=extract_combined.GAN_LLM_EXTRACT_NO_EXAMPLES_NO_EVIDENCE_NO_FORMS,
        ))
        authored = list(extract_combined.LLM_EXTRACT_COMBINED_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError("combined ablation prompt drifted from authored keys")
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError("combined ablation emits the research envelope")
        if "Gan 2026" in blob:
            raise RuntimeError("combined ablation request names the dataset")
        if "evidence" in payload["event_schema"] or "evidence" in payload["selection_schema"]:
            raise RuntimeError("combined ablation still asks for evidence")
        if "label_forms" in payload or "examples" in blob:
            raise RuntimeError("combined ablation still emits closed forms or examples")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("combined payload check changed the live default")
        if hybrid_structured_events.PROMPT_VERSION != hybrid_structured_events.GAN_LLM_EXTRACT_RAW:
            raise RuntimeError("gan_llm_extract_raw live default drifted")
    elif method == "gan_llm_extract_encode_select":
        before = hybrid_structured_events.PROMPT_VERSION
        payload = json.loads(
            hybrid_structured_events.build_prompt_input(
                _placeholder_record(),
                prompt_version=extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT,
            )
        )
        authored = list(extract_encode_select.LLM_EXTRACT_ENCODE_SELECT_AUTHORED_KEYS)
        blob = json.dumps(payload)
        if set(payload) != set(authored):
            raise RuntimeError(
                "gan_llm_extract_encode_select prompt drifted from authored keys"
            )
        if "prompt_version" in payload or "source_row_index" in payload:
            raise RuntimeError(
                "gan_llm_extract_encode_select request still emits the research envelope"
            )
        if "Gan 2026" in blob:
            raise RuntimeError(
                "gan_llm_extract_encode_select request still names the dataset"
            )
        if "cases" not in payload or "label_forms" not in payload:
            raise RuntimeError("gan_llm_extract_encode_select dropped a required block")
        if hybrid_structured_events.PROMPT_VERSION != before:
            raise RuntimeError("one-call payload check changed the live default")
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
        if slug is not None:
            later_stage_slug_permitted(cast(LaterStageMethod, method), slug)
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
    source_row_indices: Sequence[int] | None = None,
    work_leaf: str | None = None,
    recorded_prompt_version: str | None = None,
    live_sync: bool = False,
    extract_method: str | None = None,
    encode_work_leaf: str | None = None,
    encode_rows_path: Path | None = None,
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
            raise RuntimeError("--temperature is not used for later-stage Gan cells")
        return run_later_stage(
            cast(LaterStageMethod, method),
            slug,
            split=split,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout,
            progress_every=progress_every,
            reasoning_effort=reasoning_effort,
            work_leaf=work_leaf,
            recorded_prompt_version=recorded_prompt_version,
            live_sync=live_sync,
            extract_method=extract_method,
            encode_work_leaf=encode_work_leaf,
            encode_rows_path=encode_rows_path,
        )
    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    spec = apply_temperature(
        apply_reasoning_effort(MODELS[slug], reasoning_effort),
        temperature,
    )
    if thinking is not None:
        if slug not in {"deepseek_v4_flash", "qwen38_27b"}:
            raise RuntimeError("thinking toggle is DeepSeek or Qwen only")
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
    if source_row_indices is not None:
        if holdout:
            raise RuntimeError("development samples are not allowed on holdout")
        wanted = {int(index) for index in source_row_indices}
        records = [
            record for record in records if record.source_row_index in wanted
        ]
        found = {record.source_row_index for record in records}
        if found != wanted:
            missing = sorted(wanted - found)
            raise RuntimeError(f"sample is missing {len(missing)} {split} records")
    work_root = (HOLDOUT_SCRATCH if holdout else WORK_ROOT) / method / spec.slug
    segment = paper_work_suffix(spec)
    if segment:
        work_root = work_root / segment
    work_root = work_root / (work_leaf or split)
    work_root.mkdir(parents=True, exist_ok=True)
    rows_path = work_root / "rows.jsonl"
    started = datetime.now(UTC).isoformat()
    prompt = _prompt_version(method)
    existing = [] if overwrite else _existing_complete_rows(rows_path, prompt)
    done = {int(row["source_row_index"]) for row in existing}
    todo = [record for record in records if record.source_row_index not in done]
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    max_tokens = _max_tokens_for(method, spec.slug, spec.reasoning_effort)
    if spec.slug == "qwen38_27b" and spec.thinking_type == "enabled":
        max_tokens = cell3_thinking_max_tokens(max_tokens, "high")
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
        raise RuntimeError(
            f"{method} {split} has {len(by_index)} rows, expected {len(records)}"
        )
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
    if method == "gan_llm_extract_no_examples":
        return extract_no_examples.GAN_LLM_EXTRACT_NO_EXAMPLES
    if method == "gan_llm_extract_holgate_like":
        return extract_holgate.GAN_LLM_EXTRACT_HOLGATE_LIKE
    if method == "gan_llm_extract_holgate_label":
        return extract_holgate_label.GAN_LLM_EXTRACT_HOLGATE_LABEL
    if method == "gan_llm_extract_no_evidence":
        return extract_no_evidence.GAN_LLM_EXTRACT_NO_EVIDENCE
    if method == "gan_llm_extract_examples_only":
        return extract_examples_only.GAN_LLM_EXTRACT_EXAMPLES_ONLY
    if method == "gan_llm_extract_no_examples_no_evidence_no_forms":
        return extract_combined.GAN_LLM_EXTRACT_NO_EXAMPLES_NO_EVIDENCE_NO_FORMS
    if method == "gan_llm_extract_encode_select":
        return extract_encode_select.GAN_LLM_EXTRACT_ENCODE_SELECT
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
    if method in {
        "gan_llm_extract",
        "gan_llm_extract_no_examples",
        "gan_llm_extract_holgate_like",
        "gan_llm_extract_no_evidence",
        "gan_llm_extract_examples_only",
        "gan_llm_extract_no_examples_no_evidence_no_forms",
        "gan_llm_extract_encode_select",
    }:
        return "raw_model"
    if method == "gan_llm_extract_holgate_label":
        return "raw_model_single_answer"
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
    if method == "gan_llm_extract_holgate_label":
        return hybrid_structured_events.DspyHolgateLabelExtractor(), FormatOnlyJsonRetry()
    return hybrid_structured_events.DspyStructuredExtractor(), FormatOnlyJsonRetry()


def reparse_gan_llm_extract_raw(slug: str, split: str) -> dict[str, Any]:
    """Rebuild parse and scores from saved source-near raw_output. No model calls."""

    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    split_for("gan_llm_extract_raw", split)
    holdout = holdout_is_aggregate_only(split)
    dest = ROOT / "paper_experiments/gan/gan_llm_extract_raw" / slug / split
    rows_path = dest / "rows.jsonl"
    comparison_path = dest / "comparison.json"
    if not rows_path.is_file() or not comparison_path.is_file():
        raise FileNotFoundError(f"missing promoted gan_llm_extract_raw {slug} {split}")
    expected = gan_row_count(split)
    saved = load_jsonl_rows(rows_path)
    if len(saved) != expected:
        raise RuntimeError(f"{rows_path} has {len(saved)} rows, expected {expected}")
    machine = gan_machine_split(split)
    records = {record.source_row_index: record for record in load_records_for_split(machine)}
    hydrated: list[dict[str, Any]] = []
    for row in saved:
        source = int(row["source_row_index"])
        raw_output = str(row.get("raw_output") or "")
        if not raw_output.strip():
            raise RuntimeError(f"{rows_path} has an empty raw_output")
        rebuilt = hydrate_saved_raw_row(
            "gan_llm_extract_raw",
            records[source],
            raw_output,
            split=split,
        )
        if rebuilt["raw_output"] != raw_output:
            raise RuntimeError("reparse changed saved raw_output")
        if not rebuilt.get("reused_raw_output"):
            raise RuntimeError("reparse did not reuse saved raw_output")
        hydrated.append(rebuilt)
    existing = json.loads(comparison_path.read_text(encoding="utf-8"))
    summary = _summarize("gan_llm_extract_raw", hydrated)
    artifact = dict(existing)
    artifact["live"] = False
    artifact["model_calls"] = 0
    artifact["finished_utc"] = datetime.now(UTC).isoformat()
    artifact["summary"] = _public_summary(summary, holdout=holdout)
    artifact["claim_boundary"] = (
        "Gan aggregate-only test450. Do not inspect holdout rows."
        if holdout
        else "Gan development cell. Not holdout."
    )
    if holdout:
        artifact.pop("incorrect_source_row_indices", None)
        artifact["row_policy"] = "aggregate_only"
    else:
        artifact["incorrect_source_row_indices"] = [
            int(row["source_row_index"])
            for row in hydrated
            if not (row.get("comparison") or {}).get("purist_correct")
        ]
    artifact = attach_living_envelope(
        artifact,
        method="gan_llm_extract_raw",
        stages=living_gan_stages(hydrated, records, method="gan_llm_extract_raw"),
        replay_mode="no_call",
        prompt_version=_prompt_version("gan_llm_extract_raw"),
    )
    dest.mkdir(parents=True, exist_ok=True)
    comparison_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    if holdout:
        (dest / "scored.jsonl").unlink(missing_ok=True)
    else:
        scored = [
            {
                "source_row_index": int(row["source_row_index"]),
                "letter_id": str(row["source_row_index"]),
                "method": "gan_llm_extract_raw",
                "predicted_label": (
                    ((row.get("structured_record") or {}).get("selection") or {}).get(
                        "final_label"
                    )
                ),
                "purist_correct": (row.get("comparison") or {}).get("purist_correct"),
                "pragmatic_correct": (row.get("comparison") or {}).get(
                    "pragmatic_correct"
                ),
                "parse_ok": row.get("structured_record") is not None,
            }
            for row in hydrated
        ]
        write_jsonl_rows(scored, dest / "scored.jsonl")
    return {
        "artifact": comparison_path.relative_to(ROOT).as_posix(),
        "method": "gan_llm_extract_raw",
        "model_slug": slug,
        "split": split,
        "replay_mode": "no_call",
        "model_calls": 0,
        "reused_raw_outputs": int(summary.get("reused_raw_outputs") or 0),
        "summary": artifact["summary"],
    }


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
