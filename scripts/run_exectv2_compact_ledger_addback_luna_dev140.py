"""Luna dev140 Compact add-back: encoding, then encoding plus examples.

Replay living Compact. Live-generate the two add-back arms. Score each
add-back against Compact. Compact stays the live default.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import dspy
from dotenv import load_dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    _assembly_row,
    _changed_rows,
    _compare_pair,
    _existing_complete_rows,
    _letters,
    _provenance,
    _require_api_key,
    _score_arm,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/compact_ledger_addback_luna_dev140_protocol_2026-08-17.md"
STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_addback_luna_dev140_20260817"
COMPACT_STRUCTURED = (
    ROOT
    / "experiments/exectv2_compact_ledger_luna_dev140_ablation_20260817"
    / "compact_ledger"
    / "structured.jsonl"
)
MODEL = "openai/gpt-5.6-luna"
CONTROL_ARM = "compact"
REPLAY_ARMS = {
    CONTROL_ARM: (structured.COMPACT_LEDGER, COMPACT_STRUCTURED),
}
LIVE_ARMS = {
    "plus_encoding": structured.COMPACT_LEDGER_PLUS_ENCODING,
    "plus_encoding_examples": structured.COMPACT_LEDGER_PLUS_ENCODING_EXAMPLES,
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=1)
    parser.add_argument(
        "--only-arm",
        choices=tuple(LIVE_ARMS),
        help="Generate one live arm. Compact replay always runs when scoring.",
    )
    args = parser.parse_args(argv)
    if args.live:
        print(
            json.dumps(
                run_study(
                    live=True,
                    overwrite=args.overwrite,
                    api_base=args.api_base,
                    timeout=args.timeout,
                    progress_every=args.progress_every,
                    only_arm=args.only_arm,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return
    print(json.dumps(verify_payload(), indent=2, sort_keys=True))


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0133", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        compact_raw = structured.build_prompt_input(
            letter, prompt_version=structured.COMPACT_LEDGER
        )
        compact = json.loads(compact_raw)
        plus_encoding_raw = structured.build_prompt_input(
            letter, prompt_version=structured.COMPACT_LEDGER_PLUS_ENCODING
        )
        plus_encoding = json.loads(plus_encoding_raw)
        plus_both_raw = structured.build_prompt_input(
            letter, prompt_version=structured.COMPACT_LEDGER_PLUS_ENCODING_EXAMPLES
        )
        plus_both = json.loads(plus_both_raw)
        if "letter_id" in compact or "prompt_version" in compact:
            raise RuntimeError("Compact still emits research metadata")
        if len(compact["clinical_rules"]) != 67 or "worked_examples" in compact:
            raise RuntimeError("Compact content drifted")
        if not compact["task"].startswith("Read the clinical letter once"):
            raise RuntimeError("Compact lost its language pass")
        if "letter_id" in plus_encoding or "worked_examples" in plus_encoding:
            raise RuntimeError("plus_encoding drifted")
        if len(plus_encoding["clinical_rules"]) != 83:
            raise RuntimeError("plus_encoding rule count drifted")
        if plus_encoding["task"] != compact["task"]:
            raise RuntimeError("plus_encoding left Compact language")
        if "letter_id" in plus_both or len(plus_both.get("worked_examples") or []) != 49:
            raise RuntimeError("plus_encoding_examples drifted")
        if len(plus_both["clinical_rules"]) != 83:
            raise RuntimeError("plus_encoding_examples rule count drifted")
        if plus_both["task"] != compact["task"]:
            raise RuntimeError("plus_encoding_examples left Compact language")
        if list(plus_encoding)[0] != "task" or list(plus_both)[-1] != "letter_text":
            raise RuntimeError("add-back key order drifted")
        payload_chars = {
            "compact": len(compact_raw),
            "plus_encoding": len(plus_encoding_raw),
            "plus_encoding_examples": len(plus_both_raw),
        }
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "control": structured.COMPACT_LEDGER,
        "payload_chars": payload_chars,
        "protocol": PROTOCOL,
    }


def decide_arm(quality: Mapping[str, Any]) -> str:
    if int(quality.get("parse") or 0) or int(quality.get("schema") or 0):
        return "revise"
    return "descriptive"


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
    only_arm: str | None = None,
) -> dict[str, Any]:
    lengths = verify_payload()
    if not live:
        raise RuntimeError("run_study requires live=True")
    load_dotenv(ROOT / ".env", override=False)
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("live default drifted before the run")

    scored: dict[str, Any] = {}
    for slug, (version, sidecar) in REPLAY_ARMS.items():
        scored[slug] = _run_replay(slug, version, sidecar, letters)
    live_slugs = list(LIVE_ARMS) if only_arm is None else [only_arm]
    for slug in live_slugs:
        scored[slug] = _run_live(
            slug,
            LIVE_ARMS[slug],
            letters,
            overwrite=overwrite,
            api_base=api_base,
            timeout=timeout,
            progress_every=progress_every,
        )
    if CONTROL_ARM not in scored:
        raise RuntimeError("control arm was not scored")
    if structured.PROMPT_VERSION != structured.COMPACT_LEDGER:
        raise RuntimeError("a live arm left the default changed")

    control = scored[CONTROL_ARM]
    comparison: dict[str, Any] = {}
    decision: dict[str, Any] = {}
    changed: dict[str, Any] = {}
    for slug, arm in scored.items():
        if slug == CONTROL_ARM:
            continue
        versus = _compare_pair(control, arm, letters)
        hybrid = versus["surfaces"]["hybrid"]
        quality = arm["summary"]["quality"]
        verdict = decide_arm(quality)
        comparison[f"{slug}_minus_{CONTROL_ARM}"] = versus
        decision[slug] = {
            "status": "scored",
            "verdict": verdict,
            "headline_f1_delta": hybrid["headline_f1_delta"],
            "family_f1_delta": hybrid["family_f1_delta"],
            "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
        }
        changed[slug] = _changed_rows(control, arm, letters)

    artifact = {
        "schema_version": "exectv2.compact_ledger_addback_luna_dev140.v1",
        "generated_on": "2026-08-17",
        "protocol": PROTOCOL,
        "model": MODEL,
        "temperature": 1.0,
        "max_tokens": 16000,
        "cache": False,
        "split": "dev140",
        "row_count": len(letters),
        "letter_ids": [letter.letter_id for letter in letters],
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": sum(
            int(arm["summary"]["new_model_calls"]) for arm in scored.values()
        ),
        "default_prompt_version": structured.PROMPT_VERSION,
        "control_arm": CONTROL_ARM,
        "payload_chars": lengths["payload_chars"],
        "arms": {slug: arm["summary"] for slug, arm in scored.items()},
        "comparison": comparison,
        "decision": decision,
        "changed_rows": changed,
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 140-letter Compact add-back. Not holdout, "
            "not six-model transfer, and not a Decision 0050 fill change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "payload_chars": artifact["payload_chars"],
    }


def _run_replay(
    slug: str,
    prompt_version: str,
    sidecar: Path,
    letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    if not sidecar.exists():
        raise RuntimeError(f"missing replay sidecar: {sidecar}")
    raws = _raws_from_path(sidecar, letters)
    out_dir = STUDY_DIR / slug
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    producer_rows: list[dict[str, Any]] = []
    assembly_rows: list[dict[str, Any]] = []
    for letter in letters:
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=MODEL,
            mode="replay",
            raw_output=raws[letter.letter_id],
            split="dev140",
            config=StructuredMethodConfig.selected(),
        )
        hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
        producer_rows.append(dict(producer.row))
        assembly_rows.append(
            _assembly_row(hybrid.row, prompt_version, "saved_structured_no_call")
        )
    write_jsonl_rows(producer_rows, structured_path)
    write_jsonl_rows(assembly_rows, assembly_path)
    return _score_arm(
        slug=slug,
        prompt_version=prompt_version,
        call_mode="saved_structured_no_call",
        new_model_calls=0,
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


def _run_live(
    slug: str,
    prompt_version: str,
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / slug
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    existing = [] if overwrite else _existing_complete_rows(structured_path, prompt_version)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(prompt_version)
        if todo:
            _require_api_key()
            dspy.configure(
                lm=build_dspy_lm(
                    MODEL,
                    temperature=1.0,
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
                    model=MODEL,
                    temperature=1.0,
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
                if row.get("prompt_version") != prompt_version:
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
                        f"{slug}: {len(rows)}/{len(letters)} structured",
                        flush=True,
                    )
            existing = rows
        assembly_rows = []
        by_id = {str(row["letter_id"]): row for row in existing}
        for letter in letters:
            saved = by_id[letter.letter_id]
            producer = structured_one_call.produce_structured_letter(
                letter,
                model=MODEL,
                mode="replay",
                raw_output=str(saved["raw_output"]),
                split="dev140",
                config=StructuredMethodConfig.selected(),
            )
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
            assembly_rows.append(_assembly_row(hybrid.row, prompt_version, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=slug,
        prompt_version=prompt_version,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


def _raws_from_path(path: Path, letters: Sequence[ExectLetter]) -> dict[str, str]:
    wanted = {letter.letter_id for letter in letters}
    raws: dict[str, str] = {}
    for row in load_jsonl_rows(path):
        letter_id = str(row.get("letter_id") or "")
        if letter_id not in wanted:
            continue
        raw = str(row.get("raw_output") or "")
        if not raw:
            raise RuntimeError(f"{path} missing raw_output for {letter_id}")
        raws[letter_id] = raw
    missing = sorted(wanted - set(raws))
    if missing:
        raise RuntimeError(f"{path} missing letters: {missing}")
    return raws


if __name__ == "__main__":
    main()
