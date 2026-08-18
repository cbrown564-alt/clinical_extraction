"""One Compact versus Full remasure for the paper ExECT methods."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.exect_score import (
    assembly_row,
    changed_rows,
    compare_pair,
    existing_complete_rows,
    letters_dev140,
    score_arm,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

ROOT = discover_repo_root(start=Path(__file__))
CONTROL_VERSION = structured.FULL_LEDGER
CANDIDATE_VERSION = structured.COMPACT_LEDGER
CONTROL_ARM = "exect_full_ledger"
CANDIDATE_ARM = "exect_llm_with_rules"
OLLAMA_NUM_CTX_ENV = "CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"
HOSTED_SLUGS = ("grok46", "gpt56luna", "gemini37flash", "deepseek_v4_flash")
LOCAL_SLUGS = ("qwen38_27b", "gemma4_26b")
GROK46_SLUG = "grok46"
WORK_ROOT = ROOT / "experiments/paper/exect_llm_with_rules"
HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper/exect_llm_with_rules"

_DEV140_CONTROLS = {
    "gpt56sol": (
        "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715"
        "_structured.jsonl"
    ),
    "gpt56luna": (
        "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715"
        "_structured.jsonl"
    ),
    "gemini37flash": (
        "experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813"
        "_structured.jsonl"
    ),
    "deepseek_v4_flash": (
        "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731"
        "_structured.jsonl"
    ),
    "gemma4_26b": (
        "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715"
        "_structured.jsonl"
    ),
    "qwen38_27b": (
        "experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814"
        "_structured.jsonl"
    ),
}
_DEV140_COMPACT_PAPER = {
    "gemini37flash": (
        "paper_experiments/exect/exect_llm_with_rules/gemini37flash/dev140/"
        "structured.jsonl"
    ),
    "gpt56luna": (
        "paper_experiments/exect/exect_llm_with_rules/gpt56luna/dev140/"
        "structured.jsonl"
    ),
}
ALLOWED_REASONING_ABLATIONS = frozenset(
    {
        ("gemini37flash", "medium"),
    }
)
_TEST60_CONTROLS = {
    "gpt56sol": "experiments/current_stack/sidecars/exect_test60/gpt56sol.jsonl",
    "gpt56luna": "experiments/current_stack/sidecars/exect_test60/gpt56luna.jsonl",
    "gemini37flash": (
        "experiments/current_stack/sidecars/exect_test60/gemini37flash.jsonl"
    ),
    "deepseek_v4_flash": (
        "experiments/current_stack/sidecars/exect_test60/deepseek_v4_flash_0731.jsonl"
    ),
    "gemma4_26b": (
        "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/"
        "gemma4_26b_structured.jsonl"
    ),
    "qwen38_27b": (
        "scratch/holdout/qwen38_27b_20260814/exect_test60/qwen38_27b_structured.jsonl"
    ),
}


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


REASONING_EFFORT_SLUGS = frozenset({"grok46", "gpt56luna", "gemini37flash"})


def thinking_work_segment(spec: ModelSpec) -> str | None:
    """Return a sidecar directory for an explicit DeepSeek thinking-off remasure."""

    if spec.thinking_type == "disabled":
        return "thinking_disabled"
    return None


def paper_work_suffix(spec: ModelSpec) -> str | None:
    """Return the remasure directory for thinking-off or non-living effort."""

    thinking = thinking_work_segment(spec)
    if thinking:
        return thinking
    living = MODELS.get(spec.slug)
    living_effort = living.reasoning_effort if living is not None else None
    if spec.reasoning_effort and spec.reasoning_effort != living_effort:
        return f"reasoning_{spec.reasoning_effort}"
    return None


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
        temperature=1.0 if slug in {"grok46", "gpt56luna"} else 0.0,
        max_tokens=64000 if slug == "deepseek_v4_flash" else 16000,
        route=str(item["route"]),
        credential_env=credentials.get(slug, ()),
        timeout=900 if not hosted else hosted_timeout,
        num_ctx=32768 if slug == "qwen38_27b" else (65536 if slug == "gemma4_26b" else None),
        reasoning_effort="low" if slug in {"grok46", "gpt56luna", "gemini37flash"} else None,
        provider_revision=item.get("provider_revision"),
    )


MODELS: dict[str, ModelSpec] = {item["slug"]: _spec_for(item) for item in living_models()}


def has_full_control(slug: str, split: str) -> bool:
    """Return whether a living model has a Full-ledger sidecar for this split."""

    if split == "test60":
        return slug in _TEST60_CONTROLS
    if split == "dev140":
        return slug in _DEV140_CONTROLS
    raise ValueError(f"unsupported ExECT split {split}")


def control_path(slug: str, split: str) -> Path:
    """Return the Full-ledger sidecar used as the Compact control."""

    if slug not in MODELS:
        raise ValueError(f"unknown paper model {slug}")
    if not has_full_control(slug, split):
        raise ValueError(f"{slug} has no Full-ledger {split} control")
    if split == "test60":
        path = ROOT / _TEST60_CONTROLS[slug]
    elif split == "dev140":
        path = ROOT / _DEV140_CONTROLS[slug]
    else:
        raise ValueError(f"unsupported ExECT split {split}")
    _reject_lfs_pointer(path)
    return path


def _reject_lfs_pointer(path: Path) -> None:
    if not path.is_file():
        return
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
    if first and first[0].startswith("version https://git-lfs.github.com/spec/v1"):
        raise RuntimeError(f"{path} is a Git LFS pointer, not a replayable JSONL sidecar")


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


def verify_compact(*, split: str = "dev140", slug: str | None = None) -> dict[str, Any]:
    """Check Compact payload identity and optional control presence."""

    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        compact = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if list(compact) != list(structured.COMPACT_AUTHORED_KEYS):
            raise RuntimeError(f"Compact key order drifted: {list(compact)}")
        if "letter_id" in compact or "prompt_version" in compact:
            raise RuntimeError("Compact still emits research metadata")
        if len(compact["clinical_rules"]) != 67 or "worked_examples" in compact:
            raise RuntimeError("Compact content drifted")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("payload check changed the live default")
    if (
        slug is not None
        and has_full_control(slug, split)
        and not control_path(slug, split).is_file()
    ):
        raise RuntimeError(f"missing Full ledger {split} control: {control_path(slug, split)}")
    holdout = holdout_is_aggregate_only(split)
    return {
        "ok": True,
        "method": CANDIDATE_ARM,
        "candidate": CANDIDATE_VERSION,
        "control": CONTROL_VERSION,
        "split": split,
        "row_count": 59 if holdout else 140,
        "row_policy": "aggregate_only" if holdout else "development_review_permitted",
        "test60_authorized": holdout,
        "n_rules": 67,
        "n_examples": 0,
        "authored_order": True,
        "drops_research_metadata": True,
        "hosted": list(HOSTED_SLUGS),
        "local": list(LOCAL_SLUGS),
        "work_root": WORK_ROOT.relative_to(ROOT).as_posix(),
        "holdout_scratch": HOLDOUT_SCRATCH.relative_to(ROOT).as_posix(),
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
    """Run Compact live against a saved Full-ledger control."""

    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not a living paper model")
    verify_compact(split=split, slug=slug)
    if not live:
        raise RuntimeError("run_compact requires live=True")
    spec = apply_reasoning_effort(MODELS[slug], reasoning_effort)
    if thinking is not None:
        if slug != "deepseek_v4_flash":
            raise RuntimeError("thinking toggle is DeepSeek only")
        spec = replace(spec, thinking_type=thinking)
    load_dotenv(ROOT / ".env", override=False)
    letters = letters_for_split(split)
    holdout = holdout_is_aggregate_only(split)
    work_root = HOLDOUT_SCRATCH if holdout else WORK_ROOT
    segment = paper_work_suffix(spec)
    if segment:
        work_root = work_root / spec.slug / segment / split
    else:
        work_root = work_root / spec.slug / split
    work_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("live default drifted before the run")
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    candidate = _run_candidate(
        spec,
        letters,
        overwrite=overwrite,
        api_base=resolved_base,
        timeout=timeout or spec.timeout,
        progress_every=progress_every,
        out_dir=work_root / CANDIDATE_ARM,
        split=split,
    )
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("candidate arm left the live default changed")
    quality = candidate["summary"]["quality"]
    if has_full_control(slug, split):
        control = _run_replay_arm(
            spec,
            letters,
            arm=CONTROL_ARM,
            prompt_version=CONTROL_VERSION,
            raws=_raws_from_sidecar(control_path(slug, split), letters, holdout=holdout),
            out_dir=work_root / CONTROL_ARM,
            split=split,
        )
        versus = compare_pair(control, candidate, letters)
        hybrid = versus["surfaces"]["hybrid"]
        artifact = {
            "schema_version": "paper.exect_llm_with_rules.v1",
            "generated_on": "2026-08-17",
            "method": CANDIDATE_ARM,
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
                CONTROL_ARM: _public_arm_summary(control["summary"], holdout=holdout),
                CANDIDATE_ARM: _public_arm_summary(candidate["summary"], holdout=holdout),
            },
            "comparison": {f"{CANDIDATE_ARM}_minus_{CONTROL_ARM}": versus},
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
            "claim_boundary": (
                "ExECT aggregate-only test60 Compact versus saved Full ledger."
                if holdout
                else "ExECT development Compact versus saved Full ledger. Not holdout."
            ),
        }
        if not holdout:
            artifact["letter_ids"] = [letter.letter_id for letter in letters]
            artifact["changed_rows"] = changed_rows(control, candidate, letters)
    else:
        artifact = {
            "schema_version": "paper.exect_llm_with_rules.v1",
            "generated_on": "2026-08-17",
            "method": CANDIDATE_ARM,
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
                CANDIDATE_ARM: _public_arm_summary(candidate["summary"], holdout=holdout),
            },
            "decision": {
                CANDIDATE_ARM: {
                    "status": "scored",
                    "raw_headline_f1": candidate["summary"]["raw_headline_f1"],
                    "hybrid_headline_f1": candidate["summary"]["hybrid_headline_f1"],
                    "raw_family_f1": candidate["summary"]["raw_family_f1"],
                    "hybrid_family_f1": candidate["summary"]["hybrid_family_f1"],
                    "parse": quality["parse"],
                    "schema": quality["schema"],
                }
            },
            "claim_boundary": (
                "ExECT aggregate-only test60 Compact. No Full-ledger control for this model."
                if holdout
                else (
                    "ExECT development Compact. No Full-ledger control for this model. "
                    "Not holdout."
                )
            ),
        }
        if not holdout:
            artifact["letter_ids"] = [letter.letter_id for letter in letters]
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
    paper_sidecar = ROOT / _DEV140_COMPACT_PAPER[slug]
    if not paper_sidecar.is_file():
        raise RuntimeError(f"missing living Compact {split} cell: {paper_sidecar}")
    verify_compact(split=split, slug=None)
    spec = replace(paper_spec, reasoning_effort=effort)
    load_dotenv(ROOT / ".env", override=False)
    letters = letters_for_split(split)
    work_root = WORK_ROOT / spec.slug / f"reasoning_{effort}" / split
    work_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("live default drifted before the run")
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    paper_effort = paper_spec.reasoning_effort or "provider_default"
    control = _run_replay_arm(
        paper_spec,
        letters,
        arm=f"{CANDIDATE_ARM}_{paper_effort}",
        prompt_version=CANDIDATE_VERSION,
        raws=_raws_from_sidecar(paper_sidecar, letters),
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
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("candidate arm left the live default changed")
    versus = compare_pair(control, candidate, letters)
    hybrid = versus["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    artifact = {
        "schema_version": "paper.exect_llm_with_rules.reasoning_ablation.v1",
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


def _raws_from_sidecar(
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
                "a test60 control sidecar row has no replayable events"
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
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
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
) -> dict[str, Any]:
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    out_dir.mkdir(parents=True, exist_ok=True)
    holdout = holdout_is_aggregate_only(split)
    existing = (
        [] if overwrite else existing_complete_rows(structured_path, CANDIDATE_VERSION)
    )
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(CANDIDATE_VERSION)
        if todo:
            _prepare_live_runtime(spec, api_base=api_base, timeout=timeout)
            program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
            rows = list(existing)
            for index, letter in enumerate(todo, start=1):
                producer = structured_one_call.produce_structured_letter(
                    letter,
                    model=spec.model,
                    temperature=spec.temperature,
                    max_tokens=spec.max_tokens,
                    mode="live",
                    dspy_cache=False,
                    api_base=api_base,
                    timeout=timeout,
                    split=split,
                    program=program,
                    config=StructuredMethodConfig.selected(),
                )
                row = dict(producer.row)
                if row.get("prompt_version") != CANDIDATE_VERSION:
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
                        f"{spec.slug} compact {split}: {len(rows)}/{len(letters)}",
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
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
            assembly_rows.append(assembly_row(hybrid.row, CANDIDATE_VERSION, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return score_arm(
        slug=CANDIDATE_ARM,
        prompt_version=CANDIDATE_VERSION,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        model=spec.model,
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
