"""Living Compact ledger on hosted Sol, Gemini, and DeepSeek.

dev140: live remasure of ``exectv2_compact_ledger``. test60: the same
payload, aggregate-only, with live dumps under scratch/holdout. Gemini
goes through OpenRouter. The in-flight ``v0.9.40`` cells stay separate.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import (
    OPENROUTER_OPENAI_BASE,
)
from scripts import run_exectv2_v0924_cheap_stack_luna_dev140 as cheap_stack
from scripts.run_exectv2_compact_ledger_luna_dev140_ablation import (
    COMPACT_AUTHORED_KEYS,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    CANDIDATE_ARM,
    CONTROL_ARM,
    TEST60_CONTROLS,
    ModelSpec,
    _changed_rows,
    _compare_pair,
    _control_path,
    _letters_for_split,
    _public_arm_summary,
    _raws_from_sidecar,
    _run_candidate,
    _run_replay_arm,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    MODELS as SIX_MODELS,
)
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    _require_credentials as _require_six_model_credentials,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/compact_ledger_living_hosted_dev140_protocol_2026-08-17.md"
TEST60_PROTOCOL = (
    "docs/research/exectv2/compact_ledger_living_hosted_test60_protocol_2026-08-17.md"
)
STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_living_hosted_dev140_20260817"
TEST60_STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_living_hosted_test60_20260817"
TEST60_SCRATCH_DIR = (
    ROOT / "scratch/holdout/exectv2_compact_ledger_living_hosted_test60_20260817"
)
CONTROL_VERSION = structured.FULL_LEDGER
CANDIDATE_VERSION = structured.COMPACT_LEDGER
HOSTED_SLUGS = ("gpt56sol", "gemini37flash", "deepseek_v4_flash")
MODELS: dict[str, ModelSpec] = {
    "gpt56sol": SIX_MODELS["gpt56sol"],
    "gemini37flash": replace(
        SIX_MODELS["gemini37flash"],
        credential_env=("OPENROUTER_API_KEY",),
    ),
    "deepseek_v4_flash": SIX_MODELS["deepseek_v4_flash"],
}


def gemini_api_base(api_base: str | None) -> str:
    """Resolve Gemini's OpenRouter endpoint unless a caller overrides it."""

    return api_base or OPENROUTER_OPENAI_BASE


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
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        compact_raw = structured.build_prompt_input(
            letter, prompt_version=CANDIDATE_VERSION
        )
        compact = json.loads(compact_raw)
        if list(compact) != list(COMPACT_AUTHORED_KEYS):
            raise RuntimeError(f"Compact key order drifted: {list(compact)}")
        if "letter_id" in compact or "prompt_version" in compact:
            raise RuntimeError("Compact still emits research metadata")
        if len(compact["clinical_rules"]) != 67 or "worked_examples" in compact:
            raise RuntimeError("Compact content drifted")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("payload check changed the live default")
    if split == "test60":
        missing = [
            slug
            for slug in HOSTED_SLUGS
            if slug not in TEST60_CONTROLS or not TEST60_CONTROLS[slug].is_file()
        ]
        if missing:
            raise RuntimeError(f"missing Full ledger test60 controls: {missing}")
        return {
            "ok": True,
            "protocol": TEST60_PROTOCOL,
            "split": "test60",
            "row_count": 59,
            "row_policy": "aggregate_only",
            "test60_authorized": True,
            "study_dir": TEST60_STUDY_DIR.relative_to(ROOT).as_posix(),
            "scratch_dir": TEST60_SCRATCH_DIR.relative_to(ROOT).as_posix(),
            "candidate": CANDIDATE_VERSION,
            "n_rules": 67,
            "n_examples": 0,
            "authored_order": True,
            "drops_research_metadata": True,
            "hosted": list(HOSTED_SLUGS),
            "default_prompt_version": structured.PROMPT_VERSION,
        }
    missing = [
        spec.slug for spec in MODELS.values() if not spec.control_structured.is_file()
    ]
    if missing:
        raise RuntimeError(f"missing Full ledger controls: {missing}")
    return {
        "ok": True,
        "protocol": PROTOCOL,
        "split": "dev140",
        "test60_authorized": False,
        "study_dir": STUDY_DIR.relative_to(ROOT).as_posix(),
        "candidate": CANDIDATE_VERSION,
        "n_rules": 67,
        "n_examples": 0,
        "authored_order": True,
        "drops_research_metadata": True,
        "hosted": list(HOSTED_SLUGS),
        "default_prompt_version": structured.PROMPT_VERSION,
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
    if slug not in MODELS:
        raise RuntimeError(f"{slug} is not authorized for living Compact remasure")
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
    resolved_base = _resolved_api_base(spec, api_base)
    _require_six_model_credentials(spec)

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
            api_base=resolved_base,
            timeout=timeout or spec.timeout,
            progress_every=progress_every,
            out_dir=work_root / CANDIDATE_ARM,
            split=split,
            candidate_version=CANDIDATE_VERSION,
            progress_label="living compact test60" if holdout else "living compact",
        )
        if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
            raise RuntimeError("candidate arm left the live default changed")
        versus = _compare_pair(control, candidate, letters)
        hybrid = versus["surfaces"]["hybrid"]
        quality = candidate["summary"]["quality"]
        artifact = {
            "schema_version": (
                "exectv2.compact_ledger_living_hosted_test60.v1"
                if holdout
                else "exectv2.compact_ledger_living_hosted_dev140.v1"
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
                "ExECTv2 aggregate-only test60 living Compact versus saved Full "
                "ledger. Not a selected prompt and not a Decision 0050 change."
                if holdout
                else (
                    "ExECTv2 development living Compact versus saved Full ledger. "
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


def _resolved_api_base(spec: ModelSpec, api_base: str | None) -> str | None:
    if spec.slug != "gemini37flash":
        return api_base
    return gemini_api_base(api_base)


if __name__ == "__main__":
    main()
