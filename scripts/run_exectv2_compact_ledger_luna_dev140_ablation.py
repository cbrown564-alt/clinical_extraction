"""Luna dev140 Compact-ledger ablation.

Replay Full ledger and current Compact. Live-generate authored Compact
and the three study arms. Score every arm against authored Compact.
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
PROTOCOL = "docs/research/exectv2/compact_ledger_luna_dev140_ablation_protocol_2026-08-17.md"
STUDY_DIR = ROOT / "experiments/exectv2_compact_ledger_luna_dev140_ablation_20260817"
FULL_STRUCTURED = (
    ROOT / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl"
)
CURRENT_COMPACT_STRUCTURED = (
    ROOT
    / "experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816"
    / "drop_encoding_non_sf_all_examples"
    / "structured.jsonl"
)
MODEL = "openai/gpt-5.6-luna"
HEADLINE_DROP_LIMIT = 0.02
FAMILY_DROP_LIMIT = 0.04
NET_LOSS_LIMIT = 3
CONTROL_ARM = "compact_ledger"
REPLAY_ARMS = {
    "full_ledger": (structured.FULL_LEDGER, FULL_STRUCTURED),
    "compact_current": (
        structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES,
        CURRENT_COMPACT_STRUCTURED,
    ),
}
LIVE_ARMS = {
    CONTROL_ARM: structured.COMPACT_LEDGER,
    "drop_examples": structured.FULL_LEDGER_DROP_EXAMPLES,
    "drop_encoding_non_sf": structured.FULL_LEDGER_DROP_ENCODING_NON_SF,
    "compact_further_prune": structured.COMPACT_LEDGER_FURTHER_PRUNE,
}
COMPACT_AUTHORED_KEYS = (
    "task",
    "output_schema",
    "decision_procedure",
    "family_guidance",
    "attribute_vocabulary",
    "categories",
    "clinical_rules",
    "suggested_evidence",
    "letter_text",
)


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
        help="Generate one live arm. Replay arms always run when scoring.",
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
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        compact_raw = structured.build_prompt_input(
            letter, prompt_version=structured.COMPACT_LEDGER
        )
        compact = json.loads(compact_raw)
        current = json.loads(
            structured.build_prompt_input(
                letter,
                prompt_version=(
                    structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
                ),
            )
        )
        drop_examples = json.loads(
            structured.build_prompt_input(
                letter, prompt_version=structured.FULL_LEDGER_DROP_EXAMPLES
            )
        )
        drop_encoding = json.loads(
            structured.build_prompt_input(
                letter, prompt_version=structured.FULL_LEDGER_DROP_ENCODING_NON_SF
            )
        )
        further = json.loads(
            structured.build_prompt_input(
                letter, prompt_version=structured.COMPACT_LEDGER_FURTHER_PRUNE
            )
        )
        if list(compact) != list(COMPACT_AUTHORED_KEYS):
            raise RuntimeError(f"Compact key order drifted: {list(compact)}")
        if "letter_id" in compact or "prompt_version" in compact:
            raise RuntimeError("Compact still emits research metadata")
        if len(compact["clinical_rules"]) != 67 or "worked_examples" in compact:
            raise RuntimeError("Compact content drifted")
        if "letter_id" not in current or current.get("prompt_version") != (
            structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
        ):
            raise RuntimeError("current Compact ablation lost its replay dump")
        if "letter_id" in drop_examples or "worked_examples" in drop_examples:
            raise RuntimeError("drop_examples drifted")
        if len(drop_encoding["clinical_rules"]) != 67:
            raise RuntimeError("drop_encoding_non_sf rule count drifted")
        if "letter_id" in drop_encoding or "letter_id" in further:
            raise RuntimeError("study arm still emits letter_id")
        if list(drop_examples)[0] != "task" or list(further)[-1] != "letter_text":
            raise RuntimeError("study arm key order drifted")
        payload_chars = {
            "compact_ledger": len(compact_raw),
            "compact_current": len(
                structured.build_prompt_input(
                    letter,
                    prompt_version=(
                        structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
                    ),
                )
            ),
        }
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "control": structured.COMPACT_LEDGER,
        "payload_chars": payload_chars,
        "protocol": PROTOCOL,
    }


def topology_failures(hybrid: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    delta = float(hybrid["headline_f1_delta"])
    if delta <= -HEADLINE_DROP_LIMIT:
        failures.append(f"hybrid four-family F1 drop {delta}")
    for family, family_delta in dict(hybrid["family_f1_delta"]).items():
        if float(family_delta) <= -FAMILY_DROP_LIMIT:
            failures.append(f"hybrid {family} F1 drop {family_delta}")
    losses = int(hybrid["four_family_letter_exact_losses"])
    wins = int(hybrid["four_family_letter_exact_wins"])
    if losses - wins >= NET_LOSS_LIMIT:
        failures.append(f"hybrid net four-family letter-exact losses {losses - wins}")
    return failures


def decide_arm(hybrid: Mapping[str, Any], quality: Mapping[str, Any]) -> str:
    if int(quality.get("parse") or 0) or int(quality.get("schema") or 0):
        return "revise"
    return "load_bearing" if topology_failures(hybrid) else "cheap"


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
    only_arm: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    if not live:
        raise RuntimeError("run_study requires live=True")
    load_dotenv(ROOT / ".env", override=False)
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
        raise RuntimeError("live default drifted before the run")

    scored: dict[str, Any] = {}
    for slug, (version, sidecar) in REPLAY_ARMS.items():
        scored[slug] = _run_replay(slug, version, sidecar, letters)
    live_slugs = [CONTROL_ARM]
    if only_arm is None:
        live_slugs.extend(slug for slug in LIVE_ARMS if slug != CONTROL_ARM)
    elif only_arm != CONTROL_ARM:
        live_slugs.append(only_arm)
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
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
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
        verdict = (
            "descriptive" if slug == "full_ledger" else decide_arm(hybrid, quality)
        )
        comparison[f"{slug}_minus_{CONTROL_ARM}"] = versus
        decision[slug] = {
            "status": "scored",
            "verdict": verdict,
            "failures": [] if verdict == "descriptive" else topology_failures(hybrid),
            "headline_f1_delta": hybrid["headline_f1_delta"],
            "family_f1_delta": hybrid["family_f1_delta"],
            "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
        }
        changed[slug] = _changed_rows(control, arm, letters)

    artifact = {
        "schema_version": "exectv2.compact_ledger_luna_dev140_ablation.v1",
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
        "arms": {slug: arm["summary"] for slug, arm in scored.items()},
        "comparison": comparison,
        "decision": decision,
        "changed_rows": changed,
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 140-letter Compact-ledger ablation. Not holdout, "
            "not six-model transfer, and not a Decision 0050 change."
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
