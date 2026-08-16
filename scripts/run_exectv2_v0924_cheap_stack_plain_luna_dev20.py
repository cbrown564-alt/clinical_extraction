"""Remasure the cleaned cheap-stack ExECT prompt on frozen Luna dev20."""

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
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    CANDIDATE_VERSION,
    CONTROL_VERSION,
    MODEL,
    _assembly_row,
    _changed_rows,
    _compare_pair,
    _existing_complete_rows,
    _provenance,
    _require_api_key,
    _score_arm,
    decide_arm,
    topology_failures,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/v0924_cheap_stack_plain_luna_dev20_protocol_2026-08-16.md"
REPORT_PATH = ROOT / "docs/research/exectv2/v0924_cheap_stack_plain_luna_dev20_2026-08-16.md"
STUDY_DIR = ROOT / "experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816"
PREVIOUS_STUDY = ROOT / "experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816"
CONTROL_STRUCTURED = PREVIOUS_STUDY / "v0924_head" / "structured.jsonl"
PREVIOUS_CHEAP_STRUCTURED = (
    PREVIOUS_STUDY / "drop_encoding_non_sf_all_examples" / "structured.jsonl"
)
FROZEN_IDS = (
    "EA0002",
    "EA0004",
    "EA0005",
    "EA0006",
    "EA0007",
    "EA0008",
    "EA0009",
    "EA0010",
    "EA0011",
    "EA0012",
    "EA0015",
    "EA0016",
    "EA0047",
    "EA0074",
    "EA0093",
    "EA0120",
    "EA0131",
    "EA0133",
    "EA0154",
    "EA0158",
)
SCAFFOLD_KEYS = ("decision_procedure", "suggested_evidence", "categories")
CONTAMINATION_LETTERS = ("EA0004", "EA0010")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--api-base")
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--progress-every", type=int, default=1)
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
        control = json.loads(
            structured.build_prompt_input(letter, prompt_version=CONTROL_VERSION)
        )
        if len(control["clinical_rules"]) != 83 or len(control["worked_examples"]) != 49:
            raise RuntimeError("v0.9.24 control payload drifted")
        if "architecture" not in control:
            raise RuntimeError("v0.9.24 lost its architecture block")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if payload["prompt_version"] != CANDIDATE_VERSION:
            raise RuntimeError(f"cheap stack emitted {payload['prompt_version']}")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError("cheap stack leaked CUI")
        n_rules = len(payload["clinical_rules"])
        n_examples = len(payload.get("worked_examples") or [])
        has_scaffold = all(key in payload for key in SCAFFOLD_KEYS)
        if n_rules != 67 or n_examples != 0 or not has_scaffold:
            raise RuntimeError("plain cheap-stack contract drifted")
        if "architecture" in payload or "source-near" in json.dumps(payload):
            raise RuntimeError("plain cheap stack still has research leftover")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "prompt_version": CANDIDATE_VERSION,
        "n_rules": 67,
        "n_examples": 0,
        "has_scaffold": True,
        "protocol": PROTOCOL,
    }


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_payload()
    if not live:
        raise RuntimeError("run_study requires live=True")
    load_dotenv(ROOT / ".env", override=False)
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is missing; stopping before any candidate call")
    if not CONTROL_STRUCTURED.exists():
        raise RuntimeError(f"missing saved control sidecar: {CONTROL_STRUCTURED}")
    if not PREVIOUS_CHEAP_STRUCTURED.exists():
        raise RuntimeError(f"missing previous cheap sidecar: {PREVIOUS_CHEAP_STRUCTURED}")

    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("live default drifted before the run")

    control = _replay_arm(
        slug="v0924_head",
        prompt_version=CONTROL_VERSION,
        raws=_raws(CONTROL_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
    )
    previous = _replay_arm(
        slug="previous_cheap",
        prompt_version=CANDIDATE_VERSION,
        raws=_raws(PREVIOUS_CHEAP_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
    )
    candidate = _run_candidate(
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("candidate arm left the live default changed")

    versus_control = _compare_pair(control, candidate, letters)
    versus_previous = _compare_pair(previous, candidate, letters)
    hybrid = versus_control["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    verdict = decide_arm(hybrid, quality)
    artifact = {
        "schema_version": "exectv2.v0924_cheap_stack_plain_luna_dev20.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": MODEL,
        "temperature": 1.0,
        "max_tokens": 16000,
        "cache": False,
        "split": "dev20",
        "row_count": len(letters),
        "letter_ids": [letter.letter_id for letter in letters],
        "contamination_letters": list(CONTAMINATION_LETTERS),
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": candidate["summary"]["new_model_calls"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "requested_arms": ["plain_cheap"],
        "arms": {
            "v0924_head": control["summary"],
            "previous_cheap": previous["summary"],
            "plain_cheap": candidate["summary"],
        },
        "comparison": {
            "plain_cheap_minus_v0924_head": versus_control,
            "plain_cheap_minus_previous_cheap": versus_previous,
        },
        "decision": {
            "plain_cheap": {
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
        },
        "changed_rows": {
            "versus_v0924_head": _changed_rows(control, candidate, letters),
            "versus_previous_cheap": _changed_rows(previous, candidate, letters),
        },
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development remasure of the cleaned cheap "
            "stack versus saved v0.9.24. Not holdout, not a selected prompt, "
            "and not a Decision 0050 change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(artifact)
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(ROOT).as_posix(),
        "live": True,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _letters() -> list[ExectLetter]:
    wanted = set(FROZEN_IDS)
    letters = [
        letter for letter in load_letters_for_split("dev") if letter.letter_id in wanted
    ]
    if [letter.letter_id for letter in letters] != sorted(FROZEN_IDS):
        raise RuntimeError("the frozen dev20 sample is unavailable or changed")
    return letters


def _raws(path: Path, letters: Sequence[ExectLetter]) -> dict[str, str]:
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


def _replay_arm(
    *,
    slug: str,
    prompt_version: str,
    raws: Mapping[str, str],
    letters: Sequence[ExectLetter],
    call_mode: str,
) -> dict[str, Any]:
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
            split="dev20",
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
    )


def _run_candidate(
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / "plain_cheap"
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    existing = [] if overwrite else _existing_complete_rows(structured_path, CANDIDATE_VERSION)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(CANDIDATE_VERSION)
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
                    split="dev20",
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
                        f"plain cheap-stack dev20: {len(rows)}/{len(letters)} structured",
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
                split="dev20",
                config=StructuredMethodConfig.selected(),
            )
            hybrid = structured_one_call.run_llm_with_rules_letter(letter, producer)
            assembly_rows.append(_assembly_row(hybrid.row, CANDIDATE_VERSION, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug="plain_cheap",
        prompt_version=CANDIDATE_VERSION,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


def _write_report(artifact: Mapping[str, Any]) -> None:
    control = artifact["arms"]["v0924_head"]
    previous = artifact["arms"]["previous_cheap"]
    candidate = artifact["arms"]["plain_cheap"]
    versus_control = artifact["comparison"]["plain_cheap_minus_v0924_head"]["surfaces"][
        "hybrid"
    ]
    versus_previous = artifact["comparison"]["plain_cheap_minus_previous_cheap"][
        "surfaces"
    ]["hybrid"]
    decision = artifact["decision"]["plain_cheap"]
    lines = [
        "# ExECT cheap-stack plain-language remasure — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-16  ",
        f"Status: complete; one-arm **{decision['verdict']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [cheap-stack structural cut](v0924_cheap_stack_luna_dev20_2026-08-16.md)",
        "",
        "## Executive result",
        "",
        "The cleaned cheap stack is remasured on the same frozen 20-letter",
        "Luna pool as the structural cut. Default remains `v0.9.24`.",
        "Decision 0050 is unchanged.",
        "",
        "| Arm | hybrid | Δ vs `v0.9.24` | SF | SF Δ | exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| `v0.9.24` control | {control['hybrid_headline_f1']:.4f} | — | "
            f"{control['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{control['hybrid_four_family_letter_exact']}/20 |"
        ),
        (
            f"| previous cheap | {previous['hybrid_headline_f1']:.4f} | — | "
            f"{previous['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{previous['hybrid_four_family_letter_exact']}/20 |"
        ),
        (
            f"| plain cheap | {candidate['hybrid_headline_f1']:.4f} | "
            f"{versus_control['headline_f1_delta']:+.4f} | "
            f"{candidate['hybrid_family_f1']['SeizureFrequency']:.4f} | "
            f"{versus_control['family_f1_delta']['SeizureFrequency']:+.4f} | "
            f"{candidate['hybrid_four_family_letter_exact']}/20 |"
        ),
        "",
        f"{artifact['model_calls']} fresh Luna calls. "
        f"parse={candidate['quality']['parse']} "
        f"schema={candidate['quality']['schema']}. "
        f"Verdict versus `v0.9.24`: **{decision['verdict']}**.",
        "",
        "Versus the pre-cleanup cheap stack: "
        f"headline {versus_previous['headline_f1_delta']:+.4f}, "
        f"SeizureFrequency {versus_previous['family_f1_delta']['SeizureFrequency']:+.4f}, "
        f"exact net {versus_previous['four_family_letter_exact_net']:+d}.",
        "",
        "## Valid evidence",
        "",
        "- Same frozen 20 development letters. `test60` not inspected.",
        f"- Model `{artifact['model']}`. Temperature 1.0. Cache off.",
        "- Control: saved `v0.9.24` through HEAD.",
        "- Previous cheap: saved pre-cleanup cheap raws through HEAD.",
        "- Candidate: live cleaned cheap stack.",
        "",
        (
            "Artifact: [`comparison.json`]"
            f"(../../../{STUDY_DIR.relative_to(ROOT).as_posix()}/comparison.json)"
        ),
        "",
        "## Family context",
        "",
        "| Arm | Diagnosis | SeizureFrequency | Prescription | Investigations |",
        "| --- | ---: | ---: | ---: | ---: |",
        _family_row("`v0.9.24`", control),
        _family_row("previous cheap", previous),
        _family_row("plain cheap", candidate),
        "",
        "## Decision",
        "",
        f"**{decision['verdict']}.** The cheap stack stays the retained cheap",
        "variant. Live default stays `v0.9.24`. Do not start `dev140` from",
        "this result.",
        "",
        "## Claim boundary",
        "",
        str(artifact["claim_boundary"]),
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def _family_row(name: str, arm: Mapping[str, Any]) -> str:
    families = arm["hybrid_family_f1"]
    return (
        f"| {name} | {families['Diagnosis']:.4f} | "
        f"{families['SeizureFrequency']:.4f} | "
        f"{families['Prescription']:.4f} | "
        f"{families['Investigations']:.4f} |"
    )


if __name__ == "__main__":
    main()
