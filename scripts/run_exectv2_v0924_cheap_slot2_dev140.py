"""Run the reassigned cheap-stack slot 2 on ExECT dev140.

Luna and Gemini replay a complete saved v0.9.24 control, then call the
stacked further-prune prompt live. Qwen 3.8 27B collects slot-2 raws
now; a same-model v0.9.24 sidecar may be completed later.
"""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

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
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
    build_dspy_lm,
)
from scripts.run_exectv2_v0924_cheap_further_prune_luna_dev20 import _raws
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    _assembly_row,
    _changed_rows,
    _compare_pair,
    _existing_complete_rows,
    _letters,
    _provenance,
    _score_arm,
    decide_arm,
    topology_failures,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/v0924_cheap_slot2_dev140_protocol_2026-08-17.md"
CONTROL_VERSION = structured.PROMPT_VERSION_V0_9_24
CANDIDATE_ARM = "slot2"
CANDIDATE_VERSION = structured.PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES
MODELS: dict[str, dict[str, Any]] = {
    "luna": {
        "model": "openai/gpt-5.6-luna",
        "temperature": 1.0,
        "timeout": 300,
        "api_key_env": "OPENAI_API_KEY",
        "api_base": None,
        "require_full_control": True,
        "control_structured": (
            ROOT
            / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
        ),
        "study_dir": ROOT / "experiments/exectv2_v0924_cheap_slot2_luna_dev140_20260817",
    },
    "gemini": {
        "model": "gemini/gemini-3.7-flash",
        "temperature": 0.0,
        "timeout": 600,
        "api_key_env": "OPENROUTER_API_KEY",
        "api_base": OPENROUTER_OPENAI_BASE,
        "require_full_control": True,
        "control_structured": (
            ROOT
            / (
                "experiments/exectv2_six_model_single_call_"
                "gemini37flash_dev140_20260813_structured.jsonl"
            )
        ),
        "study_dir": ROOT / "experiments/exectv2_v0924_cheap_slot2_gemini_dev140_20260817",
    },
    "qwen": {
        "model": "ollama_chat/qwen3.8:27b",
        "temperature": 0.0,
        "timeout": 900,
        "api_key_env": None,
        "api_base": None,
        "require_full_control": False,
        "control_structured": (
            ROOT
            / "experiments/exectv2_v0924_cheap_slot2_qwen_dev140_20260817"
            / "v0924_head"
            / "seed_structured.jsonl"
        ),
        "study_dir": ROOT / "experiments/exectv2_v0924_cheap_slot2_qwen_dev140_20260817",
    },
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=sorted(MODELS), required=True)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--progress-every", type=int, default=1)
    args = parser.parse_args(argv)
    if args.live:
        print(
            json.dumps(
                run_study(
                    args.model,
                    live=True,
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
    print(json.dumps(verify_payload(), indent=2, sort_keys=True))


def model_spec(name: str) -> dict[str, Any]:
    if name not in MODELS:
        raise ValueError(f"unknown model {name!r}; expected one of {sorted(MODELS)}")
    return dict(MODELS[name])


def require_credentials(spec: Mapping[str, Any]) -> None:
    env_name = spec.get("api_key_env")
    if not env_name:
        return
    if not os.environ.get(str(env_name), "").strip():
        raise RuntimeError(f"{env_name} is missing; stopping before any candidate call")


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        control = json.loads(
            structured.build_prompt_input(letter, prompt_version=CONTROL_VERSION)
        )
        if len(control["clinical_rules"]) != 83 or len(control["worked_examples"]) != 49:
            raise RuntimeError("v0.9.24 control payload drifted")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if "prompt_version" in payload or "letter_id" in payload:
            raise RuntimeError("slot 2 still shows research metadata")
        if len(payload["clinical_rules"]) != 54:
            raise RuntimeError(
                f"slot 2 has {len(payload['clinical_rules'])} rules, expected 54"
            )
        if payload.get("worked_examples"):
            raise RuntimeError("slot 2 still has examples")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError("slot 2 leaked CUI")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "prompt_version": CANDIDATE_VERSION,
        "n_rules": 54,
        "n_examples": 0,
        "drops_research_metadata": True,
        "protocol": PROTOCOL,
    }


def run_study(
    model_name: str,
    *,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_payload()
    if not live:
        raise RuntimeError("run_study requires live=True")
    load_dotenv(ROOT / ".env", override=False)
    spec = model_spec(model_name)
    require_credentials(spec)
    letters = _letters()
    study_dir = Path(spec["study_dir"])
    study_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("live default drifted before the run")

    control = None
    control_status = "deferred"
    if spec["require_full_control"]:
        control_path = Path(spec["control_structured"])
        if not control_path.is_file():
            raise RuntimeError(f"missing saved control sidecar: {control_path}")
        control = _replay_arm(
            slug="v0924_head",
            prompt_version=CONTROL_VERSION,
            raws=_raws(control_path, letters),
            letters=letters,
            call_mode="saved_structured_no_call",
            study_dir=study_dir,
            model=str(spec["model"]),
        )
        control_status = "complete"
    candidate = _run_candidate(
        spec,
        letters,
        overwrite=overwrite,
        api_base=api_base or spec.get("api_base"),
        timeout=timeout or int(spec["timeout"]),
        progress_every=progress_every,
    )
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("candidate arm left the live default changed")

    artifact: dict[str, Any] = {
        "schema_version": "exectv2.v0924_cheap_slot2_dev140.v1",
        "generated_on": "2026-08-17",
        "protocol": PROTOCOL,
        "model": spec["model"],
        "model_slug": model_name,
        "temperature": spec["temperature"],
        "max_tokens": 16000,
        "cache": False,
        "split": "dev140",
        "row_count": len(letters),
        "letter_ids": [letter.letter_id for letter in letters],
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": candidate["summary"]["new_model_calls"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "requested_arms": [CANDIDATE_ARM],
        "control_status": control_status,
        "arms": {CANDIDATE_ARM: candidate["summary"]},
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 140-letter development remasure of cheap-stack slot 2 "
            f"({CANDIDATE_VERSION}) on {spec['model']}. Not holdout, not a "
            "selected prompt, and not a Decision 0050 change."
        ),
    }
    if control is not None:
        versus = _compare_pair(control, candidate, letters)
        hybrid = versus["surfaces"]["hybrid"]
        quality = candidate["summary"]["quality"]
        verdict = decide_arm(hybrid, quality)
        artifact["arms"]["v0924_head"] = control["summary"]
        artifact["comparison"] = {f"{CANDIDATE_ARM}_minus_v0924_head": versus}
        artifact["changed_rows"] = _changed_rows(control, candidate, letters)
        artifact["decision"] = {
            CANDIDATE_ARM: {
                "status": "scored",
                "verdict": verdict,
                "failures": topology_failures(hybrid)
                if verdict != "revise"
                else [
                    *topology_failures(hybrid),
                    f"parse={quality['parse']} schema={quality['schema']}",
                ],
                "headline_f1_delta": hybrid["headline_f1_delta"],
                "family_f1_delta": hybrid["family_f1_delta"],
                "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
            }
        }
    else:
        artifact["decision"] = {
            CANDIDATE_ARM: {
                "status": "candidate_raws_only",
                "verdict": "deferred_until_v0924_sidecar",
                "note": (
                    "Same-model v0.9.24 control is incomplete. Slot-2 raws "
                    "may be scored after that sidecar is completed."
                ),
            }
        }
    out = study_dir / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "model": spec["model"],
        "model_calls": artifact["model_calls"],
        "control_status": control_status,
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _replay_arm(
    *,
    slug: str,
    prompt_version: str,
    raws: Mapping[str, str],
    letters: Sequence[ExectLetter],
    call_mode: str,
    study_dir: Path,
    model: str,
) -> dict[str, Any]:
    out_dir = study_dir / slug
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    producer_rows: list[dict[str, Any]] = []
    assembly_rows: list[dict[str, Any]] = []
    for letter in letters:
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=model,
            mode="replay",
            raw_output=raws[letter.letter_id],
            split="dev140",
            config=StructuredMethodConfig.selected(),
        )
        hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
        producer_rows.append(dict(producer.row))
        assembly_rows.append(_assembly_row(hybrid.row, prompt_version, call_mode))
    write_jsonl_rows(producer_rows, structured_path)
    write_jsonl_rows(assembly_rows, assembly_path)
    return _score_arm(
        slug=slug,
        prompt_version=prompt_version,
        call_mode=call_mode,
        new_model_calls=0,
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        model=model,
    )


def _run_candidate(
    spec: Mapping[str, Any],
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    out_dir = Path(spec["study_dir"]) / CANDIDATE_ARM
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    existing = [] if overwrite else _existing_complete_rows(structured_path, CANDIDATE_VERSION)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    model = str(spec["model"])
    try:
        structured.set_active_prompt_version(CANDIDATE_VERSION)
        if todo:
            require_credentials(spec)
            dspy.configure(
                lm=build_dspy_lm(
                    model,
                    temperature=float(spec["temperature"]),
                    max_tokens=16000,
                    cache=False,
                    api_base=api_base,
                    timeout=timeout,
                )
            )
            program = structured_one_call.DspyKeyEntitiesStructuredExtractor()
            rows = list(existing)
            for index, letter in enumerate(todo, start=1):
                producer = structured_one_call.produce_structured_letter(
                    letter,
                    model=model,
                    temperature=float(spec["temperature"]),
                    max_tokens=16000,
                    mode="live",
                    dspy_cache=False,
                    api_base=api_base,
                    timeout=timeout,
                    split="dev140",
                    program=program,
                    config=StructuredMethodConfig.selected(),
                )
                row = dict(producer.row)
                if row.get("prompt_version") != CANDIDATE_VERSION:
                    raise RuntimeError(
                        f"{letter.letter_id} used {row.get('prompt_version')}"
                    )
                if producer.call_error:
                    raise RuntimeError(
                        f"{letter.letter_id} call failed: {producer.call_error}"
                    )
                rows.append(row)
                write_jsonl_rows(rows, structured_path)
                if progress_every and index % progress_every == 0:
                    print(
                        f"{model} slot2 dev140: {len(rows)}/{len(letters)} structured",
                        flush=True,
                    )
            existing = rows
        assembly_rows = []
        by_id = {str(row["letter_id"]): row for row in existing}
        for letter in letters:
            saved = by_id[letter.letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=model,
                mode="replay",
                raw_output=str(saved["raw_output"]),
                split="dev140",
                config=StructuredMethodConfig.selected(),
            )
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
            assembly_rows.append(_assembly_row(hybrid.row, CANDIDATE_VERSION, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=CANDIDATE_ARM,
        prompt_version=CANDIDATE_VERSION,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
        model=model,
    )


if __name__ == "__main__":
    main()
