"""Paper runner for ExECT both-extract, filtered extract, and inventory extract."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from dotenv import load_dotenv

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.batch import (
    BatchChatItem,
    complete_chat_batch,
    uses_provider_batch,
)
from clinical_extraction.paper.comparison_contract import (
    attach_living_envelope,
    living_exect_stages_from_surfaces,
)
from clinical_extraction.paper.exect_score import (
    FROZEN_GEMINI_LLM_ONLY_DEV140,
    assembly_row,
    changed_rows,
    compare_pair,
    existing_complete_rows,
    letters_dev140,
    score_arm,
    write_inventory_baseline_comparison,
    write_inventory_residual_comparison,
)
from clinical_extraction.paper.lm import build_paper_lm, resolve_paper_api_base
from clinical_extraction.paper.methods import holdout_is_aggregate_only
from clinical_extraction.paper.roster import living_models
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_inventory_unit_keys,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.trace_explorer.exectv2_comparison import _frontend_letter

ROOT = discover_repo_root(start=Path(__file__))
CANDIDATE_VERSION = structured.EXECT_LLM_PRE_POST
CANDIDATE_ARM = "exect_llm_pre_post"
LLM_ONLY_ARM = "exect_llm_extract_and_select"
LLM_ONLY_VERSION = structured.EXECT_LLM_EXTRACT_AND_SELECT
EXTRACT_ARM = "exect_llm_extract"
EXTRACT_VERSION = structured.EXECT_LLM_EXTRACT
INVENTORY_ARM = EXTRACT_ARM
INVENTORY_VERSION = EXTRACT_VERSION
OLLAMA_NUM_CTX_ENV = "CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"
HOSTED_SLUGS = ("grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash")
LOCAL_SLUGS = ("qwen38_27b", "gemma4_26b")
GROK46_SLUG = "grok46"
WORK_ROOT = ROOT / "experiments/paper/exect_llm_pre_post"
HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper/exect_llm_pre_post"
LLM_ONLY_WORK_ROOT = ROOT / "experiments/paper/exect_llm_extract_filtered"
LLM_ONLY_HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper/exect_llm_extract_filtered"
EXTRACT_WORK_ROOT = ROOT / "experiments/paper/exect_llm_extract"
EXTRACT_HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper/exect_llm_extract"
INVENTORY_WORK_ROOT = EXTRACT_WORK_ROOT
INVENTORY_HOLDOUT_SCRATCH = EXTRACT_HOLDOUT_SCRATCH

_DEV140_COMPACT_PAPER = {
    "gemini37flash": (
        "paper_experiments/exect/exect_llm_pre_post/gemini37flash/dev140/"
        "structured.jsonl"
    ),
    "gpt56luna": (
        "paper_experiments/exect/exect_llm_pre_post/gpt56luna/dev140/"
        "structured.jsonl"
    ),
}
ALLOWED_REASONING_ABLATIONS = frozenset(
    {
        ("gemini37flash", "medium"),
    }
)


@dataclass(frozen=True)
class _ExectArmSpec:
    method: str
    prompt_version: str
    work_root: Path
    holdout_scratch: Path
    schema_version: str
    generated_on: str
    progress_label: str
    holdout_claim_boundary: str
    dev_claim_boundary: str
    drift_before: str
    drift_after: str
    run_requires: str
    verify_version_key: Literal["candidate", "prompt_version"]


_PRE_POST_ARM = _ExectArmSpec(
    method=CANDIDATE_ARM,
    prompt_version=CANDIDATE_VERSION,
    work_root=WORK_ROOT,
    holdout_scratch=HOLDOUT_SCRATCH,
    schema_version="paper.exect_llm_pre_post.v1",
    generated_on="2026-08-23",
    progress_label="both_extract",
    holdout_claim_boundary="ExECT aggregate-only test60 both-extract.",
    dev_claim_boundary="ExECT development both-extract. Not holdout.",
    drift_before="live default drifted before the run",
    drift_after="candidate arm left the live default changed",
    run_requires="run_compact requires live=True",
    verify_version_key="candidate",
)
_LLM_ONLY_ARM = _ExectArmSpec(
    method=LLM_ONLY_ARM,
    prompt_version=LLM_ONLY_VERSION,
    work_root=LLM_ONLY_WORK_ROOT,
    holdout_scratch=LLM_ONLY_HOLDOUT_SCRATCH,
    schema_version="paper.exect_llm_extract_filtered.v1",
    generated_on="2026-08-18",
    progress_label="extract_and_select",
    holdout_claim_boundary=(
        "ExECT aggregate-only test60 extract-and-select ablation. "
        "Not the cited cell-3 extract."
    ),
    dev_claim_boundary=(
        "ExECT development extract-and-select ablation. Gemini comparison "
        "only. Not holdout."
    ),
    drift_before="live default drifted before the extract-and-select run",
    drift_after="extract-and-select left the live default changed",
    run_requires="run_llm_extract_filtered requires live=True",
    verify_version_key="prompt_version",
)

_EXTRACT_ARM = _ExectArmSpec(
    method=EXTRACT_ARM,
    prompt_version=EXTRACT_VERSION,
    work_root=EXTRACT_WORK_ROOT,
    holdout_scratch=EXTRACT_HOLDOUT_SCRATCH,
    schema_version="paper.exect_llm_extract.v1",
    generated_on="2026-08-23",
    progress_label="llm_extract",
    holdout_claim_boundary=(
        "ExECT aggregate-only test60 inventory extract. Do not inspect "
        "holdout rows."
    ),
    dev_claim_boundary=(
        "Extract proposes; select filters. Residual dictionary is an "
        "invent-from-letter ablation, not the default inventory score. "
        "Not holdout."
    ),
    drift_before="live default drifted before the extract run",
    drift_after="extract arm left the live Compact default changed",
    run_requires="run_llm_extract requires live=True",
    verify_version_key="prompt_version",
)
_INVENTORY_ARM = _EXTRACT_ARM


@dataclass(frozen=True)
class ModelSpec:
    slug: str
    model: str
    label: str
    temperature: float
    max_tokens: int
    route: str
    credential_env: tuple[str, ...]
    timeout: int
    num_ctx: int | None = None
    reasoning_effort: str | None = None
    thinking_type: str | None = None
    provider_revision: str | None = None


REASONING_EFFORT_SLUGS = frozenset(
    {"grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash"}
)


def thinking_work_segment(spec: ModelSpec) -> str | None:
    """Return a work-directory segment when thinking differs from the living spec."""

    living = MODELS.get(spec.slug)
    living_thinking = living.thinking_type if living is not None else None
    if spec.thinking_type == living_thinking:
        return None
    if spec.thinking_type == "disabled":
        return "thinking_disabled"
    if spec.thinking_type == "enabled":
        return "thinking_enabled"
    return None


def _temperature_work_segment(spec: ModelSpec) -> str | None:
    living = MODELS.get(spec.slug)
    if living is None or spec.temperature == living.temperature:
        return None
    if spec.temperature == int(spec.temperature):
        return f"temperature_{int(spec.temperature)}"
    return f"temperature_{str(spec.temperature).replace('.', '_')}"


def paper_work_suffix(spec: ModelSpec) -> str | None:
    """Return the work-directory segment for thinking-off or non-living effort."""

    parts: list[str] = []
    thinking = thinking_work_segment(spec)
    if thinking:
        parts.append(thinking)
    living = MODELS.get(spec.slug)
    living_effort = living.reasoning_effort if living is not None else None
    if spec.reasoning_effort and spec.reasoning_effort != living_effort:
        parts.append(f"reasoning_{spec.reasoning_effort}")
    temperature = _temperature_work_segment(spec)
    if temperature:
        parts.append(temperature)
    if not parts:
        return None
    return "_".join(parts)


CELL3_THINKING_TOKEN_MULTIPLIER = {"medium": 2, "high": 2}


def cell3_thinking_max_tokens(base: int, effort: str | None) -> int:
    """Raise the cell-3 extract budget for medium and high thinking (both 2x)."""

    multiplier = CELL3_THINKING_TOKEN_MULTIPLIER.get(effort or "")
    if multiplier is None:
        return base
    return base * multiplier


def apply_reasoning_effort(spec: ModelSpec, effort: str | None) -> ModelSpec:
    """Pin a non-living reasoning effort on a hosted reasoning model."""

    if effort is None:
        return spec
    if spec.slug not in REASONING_EFFORT_SLUGS:
        raise RuntimeError("reasoning effort is only for hosted reasoning models")
    if effort == spec.reasoning_effort:
        raise RuntimeError(
            f"{effort} is the living paper setting for {spec.slug}; omit --reasoning-effort"
        )
    return replace(spec, reasoning_effort=effort)


def apply_temperature(spec: ModelSpec, temperature: float | None) -> ModelSpec:
    """Pin a non-living temperature on a paper model."""

    if temperature is None:
        return spec
    if temperature == spec.temperature:
        raise RuntimeError(
            f"{temperature} is the living paper setting for {spec.slug}; omit --temperature"
        )
    return replace(spec, temperature=temperature)


def _spec_for(item: Mapping[str, Any]) -> ModelSpec:
    slug = str(item["slug"])
    hosted = item["route"] == "hosted"
    credentials = {
        "grok46": ("AI_GATEWAY_API_KEY",),
        "gpt56luna": ("OPENAI_API_KEY",),
        "gemini37flash": ("OPENROUTER_API_KEY",),
        "deepseek_v4_flash": ("DEEPSEEK_API_KEY",),
    }
    hosted_timeout = 600 if slug in {"deepseek_v4_flash", "grok46"} else 300
    return ModelSpec(
        slug=slug,
        model=str(item["model"]),
        label=str(item["label"]),
        temperature=1.0 if slug == "gpt56luna" else 0.0,
        max_tokens=64000 if slug == "deepseek_v4_flash" else 16000,
        route=str(item["route"]),
        credential_env=credentials.get(slug, ()),
        timeout=900 if not hosted else hosted_timeout,
        num_ctx=32768 if slug == "qwen38_27b" else (65536 if slug == "gemma4_26b" else None),
        reasoning_effort=(
            "low"
            if slug in {"grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash"}
            else None
        ),
        thinking_type="enabled" if slug == "deepseek_v4_flash" else None,
        provider_revision=item.get("provider_revision"),
    )


MODELS: dict[str, ModelSpec] = {item["slug"]: _spec_for(item) for item in living_models()}


def letters_for_split(split: str) -> list[ExectLetter]:
    """Load the development or locked-test ExECT letters."""

    if split == "dev140":
        return letters_dev140()
    if split != "test60":
        raise ValueError(f"unsupported ExECT split {split}")
    letters = list(load_letters_for_split("test"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 59:
        raise RuntimeError(f"expected 59 loadable test letters, found {len(letters)}")
    return letters


def _verify_arm(
    arm: _ExectArmSpec,
    *,
    split: str = "dev140",
    slug: str | None = None,
    verify_payload: Callable[[ExectLetter], Mapping[str, Any]],
    verify_drift_message: str,
) -> dict[str, Any]:
    if slug is not None and slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        payload = verify_payload(letter)
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.EXECT_LLM_PRE_POST:
        raise RuntimeError(verify_drift_message)
    holdout = holdout_is_aggregate_only(split)
    result: dict[str, Any] = {
        "ok": True,
        "method": arm.method,
        arm.verify_version_key: arm.prompt_version,
        "split": split,
        "row_count": 59 if holdout else 140,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "test60_authorized": holdout,
        "n_rules": structured.compact_rule_count(payload["clinical_rules"]),
        "n_examples": len(payload.get("examples") or []),
        "authored_order": True,
        "drops_research_metadata": True,
        "hosted": list(HOSTED_SLUGS),
        "local": list(LOCAL_SLUGS),
        "work_root": arm.work_root.relative_to(ROOT).as_posix(),
        "holdout_scratch": arm.holdout_scratch.relative_to(ROOT).as_posix(),
        "default_prompt_version": structured.PROMPT_VERSION,
    }
    return result


def verify_compact(*, split: str = "dev140", slug: str | None = None) -> dict[str, Any]:
    """Check Compact payload identity."""

    def _payload(letter: ExectLetter) -> Mapping[str, Any]:
        compact = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if list(compact) != list(structured.INVENTORY_BOTH_AUTHORED_KEYS):
            raise RuntimeError(f"both-extract key order drifted: {list(compact)}")
        if "letter_id" in compact or "prompt_version" in compact:
            raise RuntimeError("both-extract still emits research metadata")
        if "categories" in compact or "suggested_evidence" not in compact:
            raise RuntimeError("both-extract is not extract plus suggested candidates")
        if (
            structured.compact_rule_count(compact["clinical_rules"])
            != structured.INVENTORY_RULE_COUNT
            or len(compact.get("examples") or []) != 5
        ):
            raise RuntimeError("both-extract content drifted")
        return compact

    del slug
    return _verify_arm(
        _PRE_POST_ARM,
        split=split,
        verify_payload=_payload,
        verify_drift_message="payload check changed the live default",
    )


def verify_llm_extract_filtered(
    *, split: str = "dev140", slug: str | None = None
) -> dict[str, Any]:
    """Check filtered-extract payload identity without changing the live default."""

    def _payload(letter: ExectLetter) -> Mapping[str, Any]:
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=LLM_ONLY_VERSION)
        )
        if list(payload) != list(structured.LLM_ONLY_AUTHORED_KEYS):
            raise RuntimeError(f"LLM-only key order drifted: {list(payload)}")
        if "categories" in payload or "suggested_evidence" in payload:
            raise RuntimeError("LLM-only still emits suggested evidence")
        if "letter_id" in payload or "prompt_version" in payload:
            raise RuntimeError("LLM-only still emits research metadata")
        if list(payload["clinical_rules"]) != list(structured.SHARED_RULE_SECTION_KEYS):
            raise RuntimeError("LLM-only rule sections drifted")
        if structured.compact_rule_count(payload["clinical_rules"]) != 52:
            raise RuntimeError("LLM-only content drifted")
        diagnosis = " ".join(payload["clinical_rules"]["diagnosis"])
        shared = " ".join(payload["clinical_rules"]["shared"])
        procedure = " ".join(payload["decision_procedure"])
        if "Prefer the most specific epilepsy syndrome or seizure type" in diagnosis:
            raise RuntimeError("one-call extract still prefers most-specific collapse")
        if "Do not add a separate generic epilepsy diagnosis to a specific" in diagnosis:
            raise RuntimeError("one-call extract still asks to drop generic epilepsy")
        if "Onset-history phrases such as" in diagnosis:
            raise RuntimeError("one-call extract still drops onset-history as a diagnosis")
        if "Use one event per medication, diagnostic concept" in shared:
            raise RuntimeError("one-call extract still asks for one diagnostic concept")
        if "remove duplicates" in procedure:
            raise RuntimeError("one-call extract still asks to remove duplicates")
        if "Keep a generic epilepsy diagnosis when the letter states it" not in diagnosis:
            raise RuntimeError("one-call extract lost the keep-generic diagnosis rule")
        if "named seizure type in a seizure-type or frequency heading" not in diagnosis:
            raise RuntimeError("one-call extract lost the heading-type-is-diagnosis rule")
        return payload

    return _verify_arm(
        _LLM_ONLY_ARM,
        split=split,
        slug=slug,
        verify_payload=_payload,
        verify_drift_message="filtered extract verify changed the live Compact default",
    )


verify_llm_extract_and_select = verify_llm_extract_filtered
verify_llm_only = verify_llm_extract_filtered


def _run_live(
    slug: str,
    arm: _ExectArmSpec,
    *,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
    verify: Callable[..., dict[str, Any]],
) -> dict[str, Any]:
    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    verify(split=split, slug=slug)
    if not live:
        raise RuntimeError(arm.run_requires)
    spec = apply_reasoning_effort(MODELS[slug], reasoning_effort)
    if arm.method in {EXTRACT_ARM, LLM_ONLY_ARM}:
        spec = replace(
            spec,
            max_tokens=cell3_thinking_max_tokens(spec.max_tokens, spec.reasoning_effort),
        )
    if thinking is not None:
        if slug != "deepseek_v4_flash":
            raise RuntimeError("thinking toggle is DeepSeek only")
        spec = replace(spec, thinking_type=thinking)
    elif slug == "deepseek_v4_flash" and spec.reasoning_effort and not spec.thinking_type:
        spec = replace(spec, thinking_type="enabled")
    load_dotenv(ROOT / ".env", override=False)
    letters = letters_for_split(split)
    holdout = holdout_is_aggregate_only(split)
    work_root = arm.holdout_scratch if holdout else arm.work_root
    segment = paper_work_suffix(spec)
    if segment:
        work_root = work_root / spec.slug / segment / split
    else:
        work_root = work_root / spec.slug / split
    work_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.EXECT_LLM_PRE_POST:
        raise RuntimeError(arm.drift_before)
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    candidate = _run_candidate(
        spec,
        letters,
        overwrite=overwrite,
        api_base=resolved_base,
        timeout=timeout or spec.timeout,
        progress_every=progress_every,
        out_dir=work_root / arm.method,
        split=split,
        prompt_version=arm.prompt_version,
        arm=arm.method,
        progress_label=arm.progress_label,
        unit_keys=(
            clinical_inventory_unit_keys
            if _uses_inventory_select(arm.method)
            else None
        ),
    )
    if structured.PROMPT_VERSION != structured.EXECT_LLM_PRE_POST:
        raise RuntimeError(arm.drift_after)
    quality = candidate["summary"]["quality"]
    artifact = {
        "schema_version": arm.schema_version,
        "generated_on": arm.generated_on,
        "method": arm.method,
        "model_slug": spec.slug,
        "model": spec.model,
        "model_label": spec.label,
        "temperature": spec.temperature,
        "max_tokens": spec.max_tokens,
        "cache": False,
        "split": split,
        "row_count": len(letters),
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": candidate["summary"]["new_model_calls"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "provider_revision": spec.provider_revision,
        "reasoning_effort": spec.reasoning_effort,
        "thinking_type": spec.thinking_type,
        "arms": {
            arm.method: _public_arm_summary(candidate["summary"], holdout=holdout),
        },
        "decision": {
            arm.method: {
                "status": "scored",
                "raw_headline_f1": candidate["summary"]["raw_headline_f1"],
                "hybrid_headline_f1": candidate["summary"]["hybrid_headline_f1"],
                "raw_family_f1": candidate["summary"]["raw_family_f1"],
                "hybrid_family_f1": candidate["summary"]["hybrid_family_f1"],
                "parse": quality["parse"],
                "schema": quality["schema"],
            }
        },
        "claim_boundary": arm.holdout_claim_boundary if holdout else arm.dev_claim_boundary,
        "scorer": (
            "clinical_inventory_unit_keys"
            if _uses_inventory_select(arm.method)
            else "clinical_headline_unit_keys"
        ),
        "prompt_version": arm.prompt_version,
    }
    if not holdout:
        artifact["letter_ids"] = [letter.letter_id for letter in letters]
    if arm.method in {
        "exect_llm_extract",
        "exect_llm_pre_post",
        LLM_ONLY_ARM,
        "exect_llm_extract_filtered",
    }:
        artifact = attach_living_envelope(
            artifact,
            method=arm.method,
            stages=living_exect_stages_from_surfaces(candidate["summary"]),
            replay_mode="live",
            prompt_version=arm.prompt_version,
        )
    out = work_root / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def run_compact(
    slug: str,
    *,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Run Compact live."""

    return _run_live(
        slug,
        _PRE_POST_ARM,
        live=live,
        split=split,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
        verify=verify_compact,
    )


def run_llm_extract_filtered(
    slug: str,
    *,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Run the extract-and-select ablation. Gemini comparison only."""

    return _run_live(
        slug,
        _LLM_ONLY_ARM,
        live=live,
        split=split,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
        verify=verify_llm_extract_filtered,
    )


run_llm_extract_and_select = run_llm_extract_filtered
run_llm_only = run_llm_extract_filtered


def verify_llm_extract(*, split: str = "dev140", slug: str | None = None) -> dict[str, Any]:
    """Check inventory-extract prompt identity without changing the live default."""

    def _payload(letter: ExectLetter) -> Mapping[str, Any]:
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=INVENTORY_VERSION)
        )
        if list(payload) != list(structured.INVENTORY_AUTHORED_KEYS):
            raise RuntimeError(f"inventory key order drifted: {list(payload)}")
        if "categories" in payload or "suggested_evidence" in payload:
            raise RuntimeError("inventory still emits suggested evidence")
        if "letter_id" in payload or "prompt_version" in payload:
            raise RuntimeError("inventory still emits research metadata")
        joined = " ".join(payload["clinical_rules"]["diagnosis"])
        if "Do not add a separate generic epilepsy diagnosis to a specific" in joined:
            raise RuntimeError("inventory still asks to drop generic epilepsy")
        if "Prefer the most specific epilepsy syndrome or seizure type" in joined:
            raise RuntimeError("inventory still prefers most-specific collapse")
        if "Onset-history phrases such as" in joined:
            raise RuntimeError("inventory still drops onset-history as a diagnosis")
        sf_joined = " ".join(payload["clinical_rules"]["seizure_frequency"])
        procedure = " ".join(payload["decision_procedure"])
        if "keep a separate generic seizure event" not in sf_joined:
            raise RuntimeError("inventory lost the heading SF split rule")
        if "still write the event" not in sf_joined:
            raise RuntimeError("inventory lost the emit-without-rate rule")
        if "Heading-named myoclonic jerks and absences" not in sf_joined:
            raise RuntimeError("inventory lost the heading jerks and absences rule")
        if "Never include a seizure-frequency event with empty attributes" in sf_joined:
            raise RuntimeError("inventory still bans empty-attribute events")
        if "Include at most one seizure-frequency event" in sf_joined:
            raise RuntimeError("inventory still asks for one event per rate")
        if "are not enough on their own" in sf_joined:
            raise RuntimeError("inventory still bans bare seizure-free events")
        if "include each as its own diagnosis event" not in joined:
            raise RuntimeError("inventory lost the split-compound diagnosis rule")
        if "more specific place or type" not in joined:
            raise RuntimeError("inventory lost the heading place-or-type diagnosis rule")
        if "named seizure type in a seizure-type or frequency heading" not in joined:
            raise RuntimeError("inventory lost the heading-type-is-diagnosis rule")
        if "Do not write the hedge word alone as the fact" not in joined:
            raise RuntimeError("inventory lost the hedge-not-fact rule")
        if "Write diagnosis fact as only the short syndrome" in joined:
            raise RuntimeError("inventory still asks for short-name diagnosis fact")
        if "Do not include isolated symptoms or aura features as diagnosis" in joined:
            raise RuntimeError("inventory still drops isolated symptoms as diagnosis")
        if "Write fact as only that short name." in payload["family_guidance"]["diagnosis"]:
            raise RuntimeError("inventory family guidance still asks for short-name fact")
        if "Write every stated diagnosis" not in procedure:
            raise RuntimeError("inventory lost the write-every-stated instruction")
        if "Provide exact evidence from the letter" not in procedure:
            raise RuntimeError("inventory lost the exact-evidence instruction")
        if "Do not delete events before returning JSON" in procedure:
            raise RuntimeError("inventory still asks to delete events before return")
        if "remove exact duplicate events" in procedure:
            raise RuntimeError("inventory still asks to delete exact duplicates")
        if "only after the state is clear" in procedure:
            raise RuntimeError("inventory still waits until the state is clear")
        blob = json.dumps(payload).lower()
        for phrase in (
            "gold label",
            "headline",
            "unit key",
            "clinical f1",
            "scorer",
            "annotation",
            "leftover",
            "residual",
            "regex",
        ):
            if phrase in blob:
                raise RuntimeError(f"inventory prompt contains evaluation language: {phrase}")
        if structured.compact_rule_count(payload["clinical_rules"]) != (
            structured.INVENTORY_RULE_COUNT
        ):
            raise RuntimeError("inventory content drifted")
        if len(payload.get("examples") or []) != 5:
            raise RuntimeError("inventory lost recall examples")
        return payload

    return _verify_arm(
        _INVENTORY_ARM,
        split=split,
        slug=slug,
        verify_payload=_payload,
        verify_drift_message="inventory verify changed the live Compact default",
    )


def run_llm_extract(
    slug: str,
    *,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    thinking: str | None = None,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    """Run the inventory extract. Does not change the live Compact default."""

    return _run_live(
        slug,
        _INVENTORY_ARM,
        live=live,
        split=split,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        thinking=thinking,
        reasoning_effort=reasoning_effort,
        verify=verify_llm_extract,
    )


verify_llm_inventory = verify_llm_extract
run_llm_inventory = run_llm_extract


def rescore_inventory_baseline(*, slug: str = "gemini37flash") -> dict[str, Any]:
    """Rescore the frozen Gemini inventory extract on DEV140."""

    if slug != "gemini37flash":
        raise RuntimeError("inventory baseline rescore is Gemini DEV140 only")
    source = ROOT / FROZEN_GEMINI_LLM_ONLY_DEV140
    out = INVENTORY_WORK_ROOT / slug / "dev140" / "comparison.json"
    return write_inventory_baseline_comparison(
        source_structured=source,
        out_path=out,
        letters=letters_dev140(),
    )


def rescore_inventory_residuals(*, slug: str = "gemini37flash") -> dict[str, Any]:
    """Optional invent-from-letter ablation onto comparison_residual.json."""

    if slug != "gemini37flash":
        raise RuntimeError("inventory residual rescore is Gemini DEV140 only")
    work = INVENTORY_WORK_ROOT / slug / "dev140"
    return write_inventory_residual_comparison(
        structured_path=work / EXTRACT_ARM / "structured.jsonl",
        assembly_path=work / EXTRACT_ARM / "assembly.jsonl",
        out_path=work / "comparison_residual.json",
        letters=letters_dev140(),
        prompt_version=INVENTORY_VERSION,
        model=MODELS[slug].model,
    )


def run_compact_reasoning_ablation(
    slug: str,
    *,
    effort: str,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
) -> dict[str, Any]:
    """Run Compact at an explicit effort against the living paper cell."""

    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    paper_spec = MODELS[slug]
    if split != "dev140":
        raise RuntimeError("Compact reasoning ablation is development-only")
    if not live:
        raise RuntimeError("run_compact_reasoning_ablation requires live=True")
    if paper_spec.reasoning_effort == effort:
        raise RuntimeError(
            f"{effort} is the living paper setting for {slug}; omit --reasoning-effort"
        )
    if (slug, effort) not in ALLOWED_REASONING_ABLATIONS:
        raise RuntimeError(
            f"{slug} {effort} is not an allowed Compact reasoning ablation"
        )
    paper_structured_path = ROOT / _DEV140_COMPACT_PAPER[slug]
    if not paper_structured_path.is_file():
        raise RuntimeError(f"missing living Compact {split} cell: {paper_structured_path}")
    verify_compact(split=split, slug=None)
    spec = replace(paper_spec, reasoning_effort=effort)
    load_dotenv(ROOT / ".env", override=False)
    letters = letters_for_split(split)
    work_root = WORK_ROOT / spec.slug / f"reasoning_{effort}" / split
    work_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.EXECT_LLM_PRE_POST:
        raise RuntimeError("live default drifted before the run")
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    paper_effort = paper_spec.reasoning_effort or "provider_default"
    control = _run_replay_arm(
        paper_spec,
        letters,
        arm=f"{CANDIDATE_ARM}_{paper_effort}",
        prompt_version=CANDIDATE_VERSION,
        raws=_raws_from_structured_file(paper_structured_path, letters),
        out_dir=work_root / f"{CANDIDATE_ARM}_{paper_effort}",
        split=split,
    )
    candidate = _run_candidate(
        spec,
        letters,
        overwrite=overwrite,
        api_base=resolved_base,
        timeout=timeout or spec.timeout,
        progress_every=progress_every,
        out_dir=work_root / f"{CANDIDATE_ARM}_{effort}",
        split=split,
    )
    if structured.PROMPT_VERSION != structured.EXECT_LLM_PRE_POST:
        raise RuntimeError("candidate arm left the live default changed")
    versus = compare_pair(control, candidate, letters)
    hybrid = versus["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    artifact = {
        "schema_version": "paper.exect_llm_pre_post.reasoning_ablation.v1",
        "generated_on": "2026-08-17",
        "method": CANDIDATE_ARM,
        "diagnostic": True,
        "model_slug": spec.slug,
        "model": spec.model,
        "model_label": spec.label,
        "temperature": spec.temperature,
        "max_tokens": spec.max_tokens,
        "cache": False,
        "split": split,
        "row_count": len(letters),
        "row_policy": "development_review_permitted",
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": candidate["summary"]["new_model_calls"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "paper_reasoning_effort": paper_effort,
        "candidate_reasoning_effort": effort,
        "arms": {
            f"{CANDIDATE_ARM}_{paper_effort}": _public_arm_summary(
                control["summary"], holdout=False
            ),
            f"{CANDIDATE_ARM}_{effort}": _public_arm_summary(
                candidate["summary"], holdout=False
            ),
        },
        "comparison": {
            f"{CANDIDATE_ARM}_{effort}_minus_{CANDIDATE_ARM}_{paper_effort}": versus
        },
        "decision": {
            CANDIDATE_ARM: {
                "status": "scored",
                "headline_f1_delta": hybrid["headline_f1_delta"],
                "family_f1_delta": hybrid["family_f1_delta"],
                "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
                "parse": quality["parse"],
                "schema": quality["schema"],
            }
        },
        "letter_ids": [letter.letter_id for letter in letters],
        "changed_rows": changed_rows(control, candidate, letters),
        "claim_boundary": (
            f"Diagnostic {spec.label} Compact reasoning {effort} versus living "
            f"{paper_effort} on ExECT development. Not a paper cell. Not holdout."
        ),
    }
    out = work_root / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "claim_boundary": artifact["claim_boundary"],
    }


def _public_arm_summary(summary: Mapping[str, Any], *, holdout: bool) -> dict[str, Any]:
    payload = dict(summary)
    if holdout:
        payload.pop("hybrid_rewrite_letters", None)
    return payload


def _raws_from_structured_file(
    path: Path,
    letters: Sequence[ExectLetter],
    *,
    holdout: bool = False,
) -> dict[str, str]:
    wanted = {letter.letter_id for letter in letters}
    raws: dict[str, str] = {}
    for row in load_jsonl_rows(path):
        letter_id = str(row.get("letter_id") or "")
        if letter_id not in wanted:
            continue
        raw = str(row.get("raw_output") or "")
        if not raw:
            events = row.get("structured_events")
            if events:
                raw = json.dumps({"clinical_events": events})
        if not raw:
            raise RuntimeError(
                "a test60 control row has no replayable events"
                if holdout
                else f"{path} missing raw_output for {letter_id}"
            )
        raws[letter_id] = raw
    missing = wanted - set(raws)
    if missing:
        raise RuntimeError(
            f"{path} missing {len(missing)} test letters"
            if holdout
            else f"{path} missing letters: {sorted(missing)}"
        )
    return raws


def _uses_inventory_select(arm: str) -> bool:
    return (
        arm == INVENTORY_ARM
        or arm == CANDIDATE_ARM
        or arm.startswith(f"{CANDIDATE_ARM}_")
        or arm in {LLM_ONLY_ARM, "exect_llm_extract_filtered", "exect_llm_only"}
    )


def _hybrid_letter(
    letter: ExectLetter,
    producer: Any,
    *,
    inventory: bool,
) -> Any:
    if inventory:
        return structured_one_call.run_archived_llm_pre_post_letter(
            letter,
            producer,
            config=StructuredMethodConfig.inventory(),
        )
    return structured_one_call.run_llm_pre_post_letter(letter, producer)


def _run_replay_arm(
    spec: ModelSpec,
    letters: Sequence[ExectLetter],
    *,
    arm: str,
    prompt_version: str,
    raws: Mapping[str, str],
    out_dir: Path,
    split: str,
) -> dict[str, Any]:
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    out_dir.mkdir(parents=True, exist_ok=True)
    before = structured.PROMPT_VERSION
    producer_rows: list[dict[str, Any]] = []
    assembly_rows: list[dict[str, Any]] = []
    try:
        structured.set_active_prompt_version(prompt_version)
        for letter in letters:
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=spec.model,
                mode="replay",
                raw_output=raws[letter.letter_id],
                split=split,
                config=StructuredMethodConfig.selected(),
            )
            hybrid = _hybrid_letter(
                letter, producer, inventory=_uses_inventory_select(arm)
            )
            producer_rows.append(dict(producer.row))
            assembly_rows.append(
                assembly_row(hybrid.row, prompt_version, "saved_structured_no_call")
            )
        write_jsonl_rows(producer_rows, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return score_arm(
        slug=arm,
        prompt_version=prompt_version,
        call_mode="saved_structured_no_call",
        new_model_calls=0,
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        model=spec.model,
        unit_keys=(
            clinical_inventory_unit_keys if _uses_inventory_select(arm) else None
        ),
    )


def _run_candidate(
    spec: ModelSpec,
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
    out_dir: Path,
    split: str,
    prompt_version: str = CANDIDATE_VERSION,
    arm: str = CANDIDATE_ARM,
    progress_label: str = "both_extract",
    unit_keys: Any = None,
) -> dict[str, Any]:
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    out_dir.mkdir(parents=True, exist_ok=True)
    holdout = holdout_is_aggregate_only(split)
    existing = [] if overwrite else existing_complete_rows(structured_path, prompt_version)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(prompt_version)
        if todo:
            program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
            config = StructuredMethodConfig.selected()
            batch_raws: dict[str, str] = {}
            if uses_provider_batch(spec.slug):
                items = [
                    BatchChatItem(
                        custom_id=letter.letter_id,
                        messages=program.render_messages(
                            prompt_input_json=structured.build_prompt_input(letter)
                        ),
                    )
                    for letter in todo
                ]
                batch_raws = complete_chat_batch(
                    spec,
                    items,
                    work_dir=out_dir,
                    max_tokens=spec.max_tokens,
                    overwrite=overwrite,
                )
            else:
                _prepare_live_runtime(spec, api_base=api_base, timeout=timeout)
            rows = list(existing)
            for index, letter in enumerate(todo, start=1):
                raw_output = batch_raws.get(letter.letter_id)
                producer = structured_one_call.produce_structured_letter(
                    letter,
                    model=spec.model,
                    temperature=spec.temperature,
                    max_tokens=spec.max_tokens,
                    mode="replay" if raw_output is not None else "live",
                    dspy_cache=False,
                    api_base=api_base,
                    timeout=timeout,
                    split=split,
                    program=program,
                    raw_output=raw_output,
                    config=config,
                )
                row = dict(producer.row)
                if raw_output is not None:
                    row["mode"] = "live"
                if structured.canonicalize_prompt_version(
                    str(row.get("prompt_version") or "")
                ) != prompt_version:
                    raise RuntimeError(
                        "a test60 letter used the wrong prompt version"
                        if holdout
                        else f"{letter.letter_id} used {row.get('prompt_version')}"
                    )
                if producer.call_error:
                    raise RuntimeError(
                        "a test60 letter call failed"
                        if holdout
                        else f"{letter.letter_id} call failed: {producer.call_error}"
                    )
                rows.append(row)
                write_jsonl_rows(rows, structured_path)
                if progress_every and index % progress_every == 0:
                    print(
                        f"{spec.slug} {progress_label} {split}: "
                        f"{len(rows)}/{len(letters)}",
                        flush=True,
                    )
            existing = rows
        assembly_rows = []
        by_id = {str(row["letter_id"]): row for row in existing}
        for letter in letters:
            saved = by_id[letter.letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=spec.model,
                mode="replay",
                raw_output=str(saved["raw_output"]),
                split=split,
                config=StructuredMethodConfig.selected(),
            )
            hybrid = _hybrid_letter(
                letter, producer, inventory=_uses_inventory_select(arm)
            )
            assembly_rows.append(assembly_row(hybrid.row, prompt_version, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return score_arm(
        slug=arm,
        prompt_version=prompt_version,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        model=spec.model,
        unit_keys=unit_keys,
    )


def _prepare_live_runtime(
    spec: ModelSpec,
    *,
    api_base: str | None,
    timeout: int,
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
            max_tokens=spec.max_tokens,
            cache=False,
            api_base=api_base,
            timeout=timeout,
            reasoning_effort=spec.reasoning_effort,
            thinking_type=spec.thinking_type,
        )
    )


def hydrate_saved_exect_letter(
    letter: ExectLetter,
    raw_output: str,
    *,
    model: str,
    lane: Literal["llm", "llm_with_rules"] = "llm_with_rules",
    split: str = "dev140",
) -> dict[str, Any]:
    """Rebuild Compact mentions from a promoted paper raw_output."""

    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(CANDIDATE_VERSION)
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=model,
            mode="replay",
            raw_output=raw_output,
            split=split,
            config=StructuredMethodConfig.selected(),
        )
        if lane == "llm":
            predicted = list(producer.row.get("predicted_mentions") or [])
        else:
            hybrid = structured_one_call.run_llm_pre_post_letter(letter, producer)
            predicted = list(hybrid.row.get("predicted_mentions") or [])
            if not predicted:
                predicted = [
                    mention.model_dump(mode="json")
                    for mention in hybrid.prediction.mentions
                ]
    finally:
        structured.set_active_prompt_version(before)
    full = _frontend_letter(gold=letter, predicted=predicted, source_model=model)
    return {
        "letter_id": full["letter_id"],
        "split": full["split"],
        "stage": full["stage"],
        "predicted_mentions": full["predicted_mentions"],
        "predicted_family_counts": full["family_counts"]["predicted"],
        "evidence_spans": [
            span
            for span in full["evidence_spans"]
            if isinstance(span, dict) and span.get("kind") == "llm"
        ],
    }


def compact_metrics_from_structured(
    slug: str,
    structured_path: Path,
) -> list[dict[str, Any]]:
    """Replay Compact assembly from saved raws and return letter metrics."""

    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    spec = MODELS[slug]
    letters = letters_dev140()
    raws = {
        str(row["letter_id"]): str(row.get("raw_output") or "")
        for row in load_jsonl_rows(structured_path)
    }
    with tempfile.TemporaryDirectory() as tmp:
        scored = _run_replay_arm(
            spec,
            letters,
            arm=CANDIDATE_ARM,
            prompt_version=CANDIDATE_VERSION,
            raws=raws,
            out_dir=Path(tmp),
            split="dev140",
        )
    return list(scored["metrics"])
