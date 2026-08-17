"""Living Compact ledger on local Gemma 4 26B, then Qwen 3.8 27B.

dev140: live remasure of ``exectv2_compact_ledger``. test60: the same
payload, aggregate-only, with live dumps under scratch/holdout. Qwen 3.8
is the reserved local successor, not a Decision 0051 roster swap.
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
from scripts import run_exectv2_v0924_cheap_stack_luna_dev140 as cheap_stack
from scripts.run_exectv2_compact_ledger_six_model_dev140 import (
    CANDIDATE_ARM,
    CONTROL_ARM,
    ModelSpec,
    _changed_rows,
    _compare_pair,
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
PROTOCOL = "docs/research/exectv2/compact_ledger_local_gemma_qwen38_protocol_2026-08-17.md"
TEST60_PROTOCOL = PROTOCOL
STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_local_dev140_20260817"
TEST60_STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_local_test60_20260817"
TEST60_SCRATCH_DIR = (
    ROOT / "scratch/holdout/exectv2_compact_ledger_local_test60_20260817"
)
CONTROL_VERSION = structured.FULL_LEDGER
CANDIDATE_VERSION = structured.COMPACT_LEDGER
LOCAL_SLUGS = ("gemma4_26b", "qwen38_27b")
QUEUE = (
    ("gemma4_26b", "dev140"),
    ("gemma4_26b", "test60"),
    ("qwen38_27b", "dev140"),
    ("qwen38_27b", "test60"),
)
MODELS: dict[str, ModelSpec] = {
    "gemma4_26b": replace(SIX_MODELS["gemma4_26b"], timeout=900),
    "qwen38_27b": ModelSpec(
        slug="qwen38_27b",
        model="ollama_chat/qwen3.8:27b",
        label="Qwen 3.8 27B",
        temperature=0.0,
        max_tokens=16000,
        control_structured=(
            ROOT
            / (
                "experiments/exectv2_six_model_single_call_qwen38_27b_dev140_20260814"
                "_structured.jsonl"
            )
        ),
        candidate_structured=None,
        execution_group="local",
        credential_env=(),
        timeout=900,
        num_ctx=32768,
    ),
}
TEST60_CONTROLS = {
    "gemma4_26b": (
        ROOT
        / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b"
        / "gemma4_26b_structured.jsonl"
    ),
    "qwen38_27b": (
        ROOT
        / "scratch/holdout/qwen38_27b_20260814/exect_test60/qwen38_27b_structured.jsonl"
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


def control_path(slug: str, split: str) -> Path:
    if slug not in MODELS:
        raise ValueError(f"unknown local Compact model {slug}")
    if split == "test60":
        path = TEST60_CONTROLS[slug]
    elif split != "dev140":
        raise ValueError(f"unsupported split {split}")
    else:
        path = MODELS[slug].control_structured
    _reject_lfs_pointer(path)
    return path


def _reject_lfs_pointer(path: Path) -> None:
    if not path.is_file():
        return
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
    if first and first[0].startswith("version https://git-lfs.github.com/spec/v1"):
        raise RuntimeError(
            f"{path} is a Git LFS pointer, not a replayable JSONL sidecar"
        )


def verify_study(*, split: str = "dev140", slug: str | None = None) -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        compact_raw = structured.build_prompt_input(
            letter, prompt_version=CANDIDATE_VERSION
        )
        compact = json.loads(compact_raw)
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
    if slug is not None and not control_path(slug, split).is_file():
        raise RuntimeError(
            f"missing Full ledger {split} control: {control_path(slug, split)}"
        )
    if split == "test60":
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
            "local": list(LOCAL_SLUGS),
            "default_prompt_version": structured.PROMPT_VERSION,
        }
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
        "local": list(LOCAL_SLUGS),
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
        raise RuntimeError(f"{slug} is not authorized for local Compact remasure")
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
    _require_six_model_credentials(spec)
    sidecar = control_path(slug, split)
    has_control = sidecar.is_file()

    previous_model = cheap_stack.MODEL
    cheap_stack.MODEL = spec.model
    try:
        control = None
        if has_control:
            control = _run_replay_arm(
                spec,
                letters,
                arm=CONTROL_ARM,
                prompt_version=CONTROL_VERSION,
                raws=_raws_from_sidecar(
                    sidecar,
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
            candidate_version=CANDIDATE_VERSION,
            progress_label="local compact test60" if holdout else "local compact",
        )
        if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
            raise RuntimeError("candidate arm left the live default changed")
        quality = candidate["summary"]["quality"]
        arms = {
            CANDIDATE_ARM: _public_arm_summary(candidate["summary"], holdout=holdout),
        }
        if control is not None:
            versus = _compare_pair(control, candidate, letters)
            hybrid = versus["surfaces"]["hybrid"]
            arms[CONTROL_ARM] = _public_arm_summary(control["summary"], holdout=holdout)
            decision = {
                CANDIDATE_ARM: {
                    "status": "scored",
                    "headline_f1_delta": hybrid["headline_f1_delta"],
                    "family_f1_delta": hybrid["family_f1_delta"],
                    "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
                    "parse": quality["parse"],
                    "schema": quality["schema"],
                }
            }
            comparison = {f"{CANDIDATE_ARM}_minus_{CONTROL_ARM}": versus}
            claim = (
                "ExECTv2 aggregate-only test60 living Compact versus saved Full "
                "ledger on a local model. Not a selected prompt, not a Decision "
                "0050 change, and not a Decision 0051 roster swap."
                if holdout
                else (
                    "ExECTv2 development living Compact versus saved Full ledger "
                    "on a local model. Not holdout, not a selected prompt, not a "
                    "Decision 0050 change, and not a Decision 0051 roster swap."
                )
            )
        else:
            comparison = {}
            decision = {
                CANDIDATE_ARM: {
                    "status": "compact_collected_without_full_ledger_control",
                    "parse": quality["parse"],
                    "schema": quality["schema"],
                }
            }
            claim = (
                "ExECTv2 living Compact collection on a local model. Full ledger "
                f"control was missing at {sidecar.relative_to(ROOT).as_posix()}. "
                "Not a Compact-versus-Full score, not a selected prompt, and not "
                "a Decision 0050 or 0051 change."
            )
        artifact = {
            "schema_version": (
                "exectv2.compact_ledger_local_test60.v1"
                if holdout
                else "exectv2.compact_ledger_local_dev140.v1"
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
            "control_sidecar": (
                sidecar.relative_to(ROOT).as_posix() if has_control else None
            ),
            "arms": arms,
            "comparison": comparison,
            "decision": decision,
            "claim_boundary": claim,
        }
        if not holdout:
            artifact["letter_ids"] = [letter.letter_id for letter in letters]
            if control is not None:
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


if __name__ == "__main__":
    main()
