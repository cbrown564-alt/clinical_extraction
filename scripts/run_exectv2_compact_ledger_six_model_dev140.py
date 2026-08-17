"""Compact ledger versus saved Full ledger on ExECT dev140 and test60.

dev140: Luna replays saved cheap-stack raws. Sol, Gemini, and DeepSeek
are the authorized hosted live cells. Qwen and Gemma stay for a later
local device.

test60: Luna, Sol, Gemini, and DeepSeek are authorized aggregate-only
cells. Live dumps stay under scratch/holdout. Qwen and Gemma are out
of that authorization.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from clinical_extraction.core.six_model_roster import SUCCESSOR_SIX_MODELS
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
from scripts import run_exectv2_v0924_cheap_stack_luna_dev140 as cheap_stack
from scripts.run_exectv2_six_model_comparison import build_six_model_lm
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    _assembly_row,
    _changed_rows,
    _compare_pair,
    _existing_complete_rows,
    _letters,
    _score_arm,
    verify_payload,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/compact_ledger_six_model_dev140_protocol_2026-08-17.md"
TEST60_PROTOCOL = (
    "docs/research/exectv2/compact_ledger_six_model_test60_protocol_2026-08-17.md"
)
STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_six_model_dev140_20260817"
TEST60_STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_six_model_test60_20260817"
TEST60_SCRATCH_DIR = ROOT / "scratch/holdout/exectv2_compact_ledger_test60_20260817"
CONTROL_VERSION = structured.PROMPT_VERSION_V0_9_24
CANDIDATE_VERSION = structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
CONTROL_ARM = "full_ledger"
CANDIDATE_ARM = "compact_ledger"
OLLAMA_NUM_CTX_ENV = "CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"
HOSTED_LIVE_SLUGS = ("gpt56sol", "gemini37flash", "deepseek_v4_flash")
HOSTED_TEST60_SLUGS = ("gpt56luna", "gemini37flash", "gpt56sol", "deepseek_v4_flash")
LOCAL_SLUGS = ("qwen36_35b", "gemma4_26b")
TEST60_CONTROLS = {
    "gpt56luna": ROOT / "experiments/current_stack/sidecars/exect_test60/gpt56luna.jsonl",
    "gemini37flash": (
        ROOT / "experiments/current_stack/sidecars/exect_test60/gemini37flash.jsonl"
    ),
    "gpt56sol": ROOT / "experiments/current_stack/sidecars/exect_test60/gpt56sol.jsonl",
    "deepseek_v4_flash": (
        ROOT
        / "experiments/current_stack/sidecars/exect_test60/deepseek_v4_flash_0731.jsonl"
    ),
}


@dataclass(frozen=True)
class ModelSpec:
    slug: str
    model: str
    label: str
    temperature: float
    max_tokens: int
    control_structured: Path
    candidate_structured: Path | None
    execution_group: str
    credential_env: tuple[str, ...]
    timeout: int
    num_ctx: int | None = None
    reasoning_effort: str | None = None
    provider_revision: str | None = None


def _spec(
    slug: str,
    *,
    temperature: float,
    max_tokens: int,
    control: str,
    candidate: str | None = None,
    credential_env: tuple[str, ...] = (),
    timeout: int = 300,
    num_ctx: int | None = None,
    reasoning_effort: str | None = None,
    provider_revision: str | None = None,
) -> ModelSpec:
    roster = {item["slug"]: item for item in SUCCESSOR_SIX_MODELS}[slug]
    return ModelSpec(
        slug=slug,
        model=roster["model"],
        label=roster["label"],
        temperature=temperature,
        max_tokens=max_tokens,
        control_structured=ROOT / control,
        candidate_structured=None if candidate is None else ROOT / candidate,
        execution_group=roster["execution_group"],
        credential_env=credential_env,
        timeout=timeout,
        num_ctx=num_ctx,
        reasoning_effort=reasoning_effort,
        provider_revision=provider_revision,
    )


MODELS: dict[str, ModelSpec] = {
    "gpt56luna": _spec(
        "gpt56luna",
        temperature=1.0,
        max_tokens=16000,
        control=(
            "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715"
            "_structured.jsonl"
        ),
        candidate=(
            "experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816/"
            "drop_encoding_non_sf_all_examples/structured.jsonl"
        ),
        credential_env=("OPENAI_API_KEY",),
    ),
    "gemini37flash": _spec(
        "gemini37flash",
        temperature=0.0,
        max_tokens=16000,
        control=(
            "experiments/exectv2_six_model_single_call_gemini37flash_dev140_20260813"
            "_structured.jsonl"
        ),
        credential_env=("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        reasoning_effort="low",
    ),
    "gpt56sol": _spec(
        "gpt56sol",
        temperature=1.0,
        max_tokens=16000,
        control=(
            "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715"
            "_structured.jsonl"
        ),
        credential_env=("OPENAI_API_KEY",),
    ),
    "deepseek_v4_flash": _spec(
        "deepseek_v4_flash",
        temperature=0.0,
        max_tokens=64000,
        control=(
            "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731"
            "_structured.jsonl"
        ),
        credential_env=("DEEPSEEK_API_KEY",),
        timeout=600,
        provider_revision="DeepSeek-V4-Flash-0731",
    ),
    "qwen36_35b": _spec(
        "qwen36_35b",
        temperature=0.0,
        max_tokens=16000,
        control=(
            "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715"
            "_structured.jsonl"
        ),
        num_ctx=32768,
    ),
    "gemma4_26b": _spec(
        "gemma4_26b",
        temperature=0.0,
        max_tokens=16000,
        control=(
            "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715"
            "_structured.jsonl"
        ),
        num_ctx=65536,
    ),
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=tuple(MODELS))
    parser.add_argument("--split", choices=("dev140", "test60"), default="dev140")
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    if args.live:
        if args.model is None:
            raise SystemExit("--live requires --model")
        print(
            json.dumps(
                run_model(
                    args.model,
                    live=True,
                    split=args.split,
                    overwrite=args.overwrite,
                    api_base=args.api_base,
                    timeout=args.timeout,
                    progress_every=args.progress_every,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    print(json.dumps(verify_study(split=args.split), indent=2, sort_keys=True))


def verify_study(*, split: str = "dev140") -> dict[str, Any]:
    payload = verify_payload()
    if tuple(MODELS) != tuple(item["slug"] for item in SUCCESSOR_SIX_MODELS):
        raise RuntimeError("Compact ledger roster drifted from SUCCESSOR_SIX_MODELS")
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("payload check changed the live default")
    if split == "test60":
        missing = [
            slug
            for slug, path in TEST60_CONTROLS.items()
            if slug in HOSTED_TEST60_SLUGS and not path.is_file()
        ]
        if missing:
            raise RuntimeError(f"missing Full ledger test60 controls: {missing}")
        return {
            **payload,
            "ok": True,
            "protocol": TEST60_PROTOCOL,
            "split": "test60",
            "row_count": 59,
            "row_policy": "aggregate_only",
            "test60_authorized": True,
            "study_dir": TEST60_STUDY_DIR.relative_to(ROOT).as_posix(),
            "scratch_dir": TEST60_SCRATCH_DIR.relative_to(ROOT).as_posix(),
            "models": list(HOSTED_TEST60_SLUGS),
            "hosted_live": list(HOSTED_TEST60_SLUGS),
            "local_later": list(LOCAL_SLUGS),
        }
    missing = [
        spec.slug
        for spec in MODELS.values()
        if not spec.control_structured.is_file()
    ]
    if missing:
        raise RuntimeError(f"missing Full ledger controls: {missing}")
    luna = MODELS["gpt56luna"]
    if luna.candidate_structured is None or not luna.candidate_structured.is_file():
        raise RuntimeError("missing saved Luna Compact ledger sidecar")
    return {
        **payload,
        "ok": True,
        "protocol": PROTOCOL,
        "split": "dev140",
        "test60_authorized": False,
        "study_dir": STUDY_DIR.relative_to(ROOT).as_posix(),
        "models": [spec.slug for spec in MODELS.values()],
        "hosted_live": list(HOSTED_LIVE_SLUGS),
        "local_later": list(LOCAL_SLUGS),
        "luna_replay": luna.candidate_structured.relative_to(ROOT).as_posix(),
    }


def run_model(
    slug: str,
    *,
    live: bool,
    split: str = "dev140",
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_study(split=split)
    if not live:
        raise RuntimeError("run_model requires live=True")
    if split == "test60" and slug not in HOSTED_TEST60_SLUGS:
        raise RuntimeError(f"{slug} is not authorized for Compact ledger test60")
    spec = MODELS[slug]
    load_dotenv(ROOT / ".env", override=False)
    letters = _letters_for_split(split)
    holdout = split == "test60"
    work_root = (TEST60_SCRATCH_DIR if holdout else STUDY_DIR) / spec.slug
    public_root = (TEST60_STUDY_DIR if holdout else STUDY_DIR) / spec.slug
    work_root.mkdir(parents=True, exist_ok=True)
    public_root.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("live default drifted before the run")

    previous_model = cheap_stack.MODEL
    cheap_stack.MODEL = spec.model
    try:
        control = _run_replay_arm(
            spec,
            letters,
            arm=CONTROL_ARM,
            prompt_version=CONTROL_VERSION,
            raws=_raws_from_sidecar(
                _control_path(spec, split),
                letters,
                holdout=holdout,
            ),
            out_dir=work_root / CONTROL_ARM,
            split=split,
        )
        candidate = _run_candidate(
            spec,
            letters,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout or spec.timeout,
            progress_every=progress_every,
            out_dir=work_root / CANDIDATE_ARM,
            split=split,
        )
        if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
            raise RuntimeError("candidate arm left the live default changed")
        versus = _compare_pair(control, candidate, letters)
        hybrid = versus["surfaces"]["hybrid"]
        quality = candidate["summary"]["quality"]
        artifact = {
            "schema_version": (
                "exectv2.compact_ledger_six_model_test60.v1"
                if holdout
                else "exectv2.compact_ledger_six_model_dev140.v1"
            ),
            "generated_on": "2026-08-17",
            "protocol": TEST60_PROTOCOL if holdout else PROTOCOL,
            "model_slug": spec.slug,
            "model": spec.model,
            "model_label": spec.label,
            "temperature": spec.temperature,
            "max_tokens": spec.max_tokens,
            "cache": False,
            "split": split,
            "row_count": len(letters),
            "row_policy": "aggregate_only" if holdout else "development_review_permitted",
            "repair_policy": {
                "diagnosis_policy_variant": "default",
                "prescription_policy_variant": "default",
            },
            "started_utc": started,
            "finished_utc": datetime.now(UTC).isoformat(),
            "live": True,
            "model_calls": candidate["summary"]["new_model_calls"],
            "default_prompt_version": structured.PROMPT_VERSION,
            "provider_revision": spec.provider_revision,
            "reasoning_effort": spec.reasoning_effort,
            "arms": {
                CONTROL_ARM: _public_arm_summary(control["summary"], holdout=holdout),
                CANDIDATE_ARM: _public_arm_summary(
                    candidate["summary"], holdout=holdout
                ),
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
                "ExECTv2 aggregate-only test60 Compact ledger versus saved Full "
                "ledger. Not a selected prompt and not a Decision 0050 change."
                if holdout
                else (
                    "ExECTv2 development Compact ledger versus saved Full ledger. "
                    "Not holdout, not a selected prompt, and not a Decision 0050 change."
                )
            ),
        }
        if not holdout:
            artifact["letter_ids"] = [letter.letter_id for letter in letters]
            artifact["changed_rows"] = _changed_rows(control, candidate, letters)
        out = public_root / "comparison.json"
        out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    finally:
        cheap_stack.MODEL = previous_model
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _letters_for_split(split: str) -> list[ExectLetter]:
    if split == "dev140":
        return _letters()
    if split != "test60":
        raise ValueError(f"unsupported split {split}")
    letters = list(load_letters_for_split("test"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 59:
        raise RuntimeError(
            f"expected 59 loadable test letters, found {len(letters)}"
        )
    return letters


def _control_path(spec: ModelSpec, split: str) -> Path:
    if split == "test60":
        return TEST60_CONTROLS[spec.slug]
    return spec.control_structured


def _public_arm_summary(
    summary: Mapping[str, Any],
    *,
    holdout: bool,
) -> dict[str, Any]:
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
            if holdout:
                raise RuntimeError("a test60 control sidecar row has no replayable events")
            raise RuntimeError(f"{path} missing raw_output for {letter_id}")
        raws[letter_id] = raw
    missing = wanted - set(raws)
    if missing:
        if holdout:
            raise RuntimeError(f"{path} missing {len(missing)} test letters")
        raise RuntimeError(f"{path} missing letters: {sorted(missing)}")
    return raws


def _run_replay_arm(
    spec: ModelSpec,
    letters: Sequence[ExectLetter],
    *,
    arm: str,
    prompt_version: str,
    raws: Mapping[str, str],
    out_dir: Path,
    split: str = "dev140",
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
                _assembly_row(hybrid.row, prompt_version, "saved_structured_no_call")
            )
        write_jsonl_rows(producer_rows, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=arm,
        prompt_version=prompt_version,
        call_mode="saved_structured_no_call",
        new_model_calls=0,
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
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
    split: str = "dev140",
    candidate_version: str | None = None,
    progress_label: str | None = None,
) -> dict[str, Any]:
    version = candidate_version or CANDIDATE_VERSION
    label = progress_label or (
        "compact ledger test60" if split == "test60" else "compact ledger"
    )
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    out_dir.mkdir(parents=True, exist_ok=True)
    holdout = split == "test60"
    if split == "dev140" and spec.candidate_structured is not None:
        raws = _raws_from_sidecar(spec.candidate_structured, letters)
        return _run_replay_arm(
            spec,
            letters,
            arm=CANDIDATE_ARM,
            prompt_version=version,
            raws=raws,
            out_dir=out_dir,
            split=split,
        )
    existing = [] if overwrite else _existing_complete_rows(structured_path, version)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(version)
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
                if row.get("prompt_version") != version:
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
                        f"{spec.slug} {label}: {len(rows)}/{len(letters)} structured",
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
            assembly_rows.append(_assembly_row(hybrid.row, version, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=CANDIDATE_ARM,
        prompt_version=version,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
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
    if spec.reasoning_effort:
        os.environ["GEMINI_REASONING_EFFORT"] = spec.reasoning_effort
    _require_credentials(spec)
    dspy.configure(
        lm=build_six_model_lm(
            spec.model,
            temperature=spec.temperature,
            max_tokens=spec.max_tokens,
            cache=False,
            api_base=api_base,
            timeout=timeout,
        )
    )


def _require_credentials(spec: ModelSpec) -> None:
    if not spec.credential_env:
        return
    if any(os.environ.get(name, "").strip() for name in spec.credential_env):
        return
    names = " or ".join(spec.credential_env)
    raise RuntimeError(f"{names} is missing; stopping before any candidate call")


if __name__ == "__main__":
    main()
