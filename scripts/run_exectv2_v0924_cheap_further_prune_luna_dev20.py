"""Score one further prune of the cleaned cheap stack on frozen Luna dev20."""

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
from scripts.run_exectv2_v0924_cheap_stack_plain_luna_dev20 import (
    CONTAMINATION_LETTERS,
    FROZEN_IDS,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2/v0924_cheap_further_prune_luna_dev20_protocol_2026-08-16.md"
REPORT_PATH = ROOT / "docs/research/exectv2/v0924_cheap_further_prune_luna_dev20_2026-08-16.md"
STUDY_DIR = ROOT / "experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816"
CONTROL_STRUCTURED = (
    ROOT
    / "experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816"
    / "v0924_head"
    / "structured.jsonl"
)
CHEAP_STRUCTURED = (
    ROOT
    / "experiments/exectv2_v0924_cheap_stack_plain_luna_dev20_20260816"
    / "plain_cheap"
    / "structured.jsonl"
)
CHEAP_VERSION = structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
ARM_ORDER = ("ix_pending", "scaffold_reprint", "refuse_chorus")
ARMS: dict[str, dict[str, Any]] = {
    "ix_pending": {
        "version": structured.PROMPT_VERSION_V0_9_41_CHEAP_DROP_IX_PENDING_REPEAT,
        "n_rules": 64,
        "drops_prompt_version": False,
        "label": "investigation pending collapse",
    },
    "scaffold_reprint": {
        "version": structured.PROMPT_VERSION_V0_9_42_CHEAP_DROP_SCAFFOLD_REPRINT,
        "n_rules": 66,
        "drops_prompt_version": True,
        "label": "scaffold reprint drop",
    },
    "refuse_chorus": {
        "version": structured.PROMPT_VERSION_V0_9_43_CHEAP_COLLAPSE_REFUSE,
        "n_rules": 58,
        "drops_prompt_version": False,
        "label": "refuse chorus collapse",
    },
}


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--arm", choices=ARM_ORDER, required=True)
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
                    arm=args.arm,
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
    print(json.dumps(verify_payload(args.arm), indent=2, sort_keys=True))


def verify_payload(arm: str) -> dict[str, Any]:
    spec = ARMS[arm]
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    try:
        control = json.loads(
            structured.build_prompt_input(letter, prompt_version=CONTROL_VERSION)
        )
        if len(control["clinical_rules"]) != 83 or len(control["worked_examples"]) != 49:
            raise RuntimeError("v0.9.24 control payload drifted")
        cheap = json.loads(
            structured.build_prompt_input(letter, prompt_version=CHEAP_VERSION)
        )
        if len(cheap["clinical_rules"]) != 67 or cheap.get("worked_examples"):
            raise RuntimeError("live cheap-stack contract drifted")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=spec["version"])
        )
        if spec["drops_prompt_version"]:
            if "prompt_version" in payload or "letter_id" in payload:
                raise RuntimeError("scaffold arm still shows research metadata")
        elif payload.get("prompt_version") != spec["version"]:
            raise RuntimeError(f"{arm} emitted {payload.get('prompt_version')}")
        if len(payload["clinical_rules"]) != spec["n_rules"]:
            raise RuntimeError(
                f"{arm} has {len(payload['clinical_rules'])} rules, "
                f"expected {spec['n_rules']}"
            )
        if payload.get("worked_examples"):
            raise RuntimeError(f"{arm} still has examples")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError(f"{arm} leaked CUI")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "arm": arm,
        "prompt_version": spec["version"],
        "n_rules": spec["n_rules"],
        "protocol": PROTOCOL,
    }


def run_study(
    *,
    arm: str,
    live: bool,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_payload(arm)
    if not live:
        raise RuntimeError("run_study requires live=True")
    load_dotenv(ROOT / ".env", override=False)
    if not os.environ.get("OPENAI_API_KEY", "").strip():
        raise RuntimeError("OPENAI_API_KEY is missing; stopping before any candidate call")
    if not CONTROL_STRUCTURED.exists():
        raise RuntimeError(f"missing saved control sidecar: {CONTROL_STRUCTURED}")
    if not CHEAP_STRUCTURED.exists():
        raise RuntimeError(f"missing saved cheap sidecar: {CHEAP_STRUCTURED}")

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
    cheap = _replay_arm(
        slug="plain_cheap",
        prompt_version=CHEAP_VERSION,
        raws=_raws(CHEAP_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
    )
    candidate = _run_candidate(
        arm,
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("candidate arm left the live default changed")

    versus_cheap = _compare_pair(cheap, candidate, letters)
    versus_control = _compare_pair(control, candidate, letters)
    hybrid = versus_cheap["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    verdict = decide_arm(hybrid, quality)
    previous = _load_artifact()
    arms = dict(previous.get("arms") or {})
    arms["v0924_head"] = control["summary"]
    arms["plain_cheap"] = cheap["summary"]
    arms[arm] = candidate["summary"]
    comparison = dict(previous.get("comparison") or {})
    comparison[f"{arm}_minus_plain_cheap"] = versus_cheap
    comparison[f"{arm}_minus_v0924_head"] = versus_control
    decision = dict(previous.get("decision") or {})
    decision[arm] = {
        "status": "scored",
        "verdict": verdict,
        "failures": topology_failures(hybrid)
        if verdict != "revise"
        else [*topology_failures(hybrid), f"parse={quality['parse']} schema={quality['schema']}"],
        "headline_f1_delta": hybrid["headline_f1_delta"],
        "family_f1_delta": hybrid["family_f1_delta"],
        "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
    }
    changed = dict(previous.get("changed_rows") or {})
    changed[f"{arm}_versus_plain_cheap"] = _changed_rows(cheap, candidate, letters)
    changed[f"{arm}_versus_v0924_head"] = _changed_rows(control, candidate, letters)
    requested = list(previous.get("requested_arms") or [])
    if arm not in requested:
        requested.append(arm)
    artifact = {
        "schema_version": "exectv2.v0924_cheap_further_prune_luna_dev20.v1",
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
        "started_utc": previous.get("started_utc") or started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True,
        "model_calls": int(previous.get("model_calls") or 0)
        + int(candidate["summary"]["new_model_calls"]),
        "default_prompt_version": structured.PROMPT_VERSION,
        "requested_arms": requested,
        "arms": arms,
        "comparison": comparison,
        "decision": decision,
        "changed_rows": changed,
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development study of one further cheap-stack "
            "cut versus the cleaned cheap stack. Not holdout, not a selected "
            "prompt, not a slot-2 change, and not a Decision 0050 change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(artifact)
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(ROOT).as_posix(),
        "live": True,
        "arm": arm,
        "model_calls": candidate["summary"]["new_model_calls"],
        "decision": {arm: decision[arm]},
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
    arm: str,
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    spec = ARMS[arm]
    version = spec["version"]
    out_dir = STUDY_DIR / arm
    structured_path = out_dir / "structured.jsonl"
    assembly_path = out_dir / "assembly.jsonl"
    existing = [] if overwrite else _existing_complete_rows(structured_path, version)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(version)
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
                if row.get("prompt_version") != version:
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
                        f"{arm} further-prune dev20: {len(rows)}/{len(letters)} structured",
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
            assembly_rows.append(_assembly_row(hybrid.row, version, "live"))
        write_jsonl_rows(existing, structured_path)
        write_jsonl_rows(assembly_rows, assembly_path)
    finally:
        structured.set_active_prompt_version(before)
    return _score_arm(
        slug=arm,
        prompt_version=version,
        call_mode="live",
        new_model_calls=len(todo),
        letters=letters,
        structured_path=structured_path,
        assembly_path=assembly_path,
    )


def _load_artifact() -> dict[str, Any]:
    path = STUDY_DIR / "comparison.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_report(artifact: Mapping[str, Any]) -> None:
    control = artifact["arms"]["v0924_head"]
    cheap = artifact["arms"]["plain_cheap"]
    scored = [arm for arm in ARM_ORDER if arm in artifact["decision"]]
    pending = [arm for arm in ARM_ORDER if arm not in artifact["decision"]]
    lines = [
        "# ExECT cheap-stack further prune — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-16  ",
        f"Status: {'complete' if not pending else 'in progress'}; "
        f"scored {', '.join(scored) or 'none'}  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [cleaned cheap remasure](v0924_cheap_stack_plain_luna_dev20_2026-08-16.md)",
        "",
        "## Executive result",
        "",
        "Each arm is one further cut of the cleaned cheap stack, scored",
        "against that stack. Default remains `v0.9.24`. Slot 2 remains",
        "`v0.9.40`. Decision 0050 is unchanged.",
        "",
        "| Arm | hybrid | Δ vs cheap | SF | SF Δ | exact | verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
        (
            f"| cleaned cheap | {cheap['hybrid_headline_f1']:.4f} | — | "
            f"{cheap['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{cheap['hybrid_four_family_letter_exact']}/20 | control |"
        ),
        (
            f"| `v0.9.24` | {control['hybrid_headline_f1']:.4f} | — | "
            f"{control['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{control['hybrid_four_family_letter_exact']}/20 | secondary |"
        ),
    ]
    for arm in scored:
        candidate = artifact["arms"][arm]
        versus = artifact["comparison"][f"{arm}_minus_plain_cheap"]["surfaces"]["hybrid"]
        decision = artifact["decision"][arm]
        lines.append(
            f"| {ARMS[arm]['label']} | {candidate['hybrid_headline_f1']:.4f} | "
            f"{versus['headline_f1_delta']:+.4f} | "
            f"{candidate['hybrid_family_f1']['SeizureFrequency']:.4f} | "
            f"{versus['family_f1_delta']['SeizureFrequency']:+.4f} | "
            f"{candidate['hybrid_four_family_letter_exact']}/20 | "
            f"**{decision['verdict']}** |"
        )
    lines.extend(
        [
            "",
            f"{artifact['model_calls']} fresh Luna calls across scored arms. "
            "Primary verdicts are versus the cleaned cheap stack.",
            "",
        ]
    )
    if pending:
        lines.append(f"Not yet scored: {', '.join(pending)}.")
        lines.append("")
    lines.extend(
        [
            "## Valid evidence",
            "",
            "- Same frozen 20 development letters. `test60` not inspected.",
            f"- Model `{artifact['model']}`. Temperature 1.0. Cache off.",
            "- Control: saved cleaned cheap stack through HEAD.",
            "- Secondary: saved `v0.9.24` through HEAD.",
            "- Each candidate is one live further cut.",
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
            _family_row("cleaned cheap", cheap),
            _family_row("`v0.9.24`", control),
        ]
    )
    for arm in scored:
        lines.append(_family_row(ARMS[arm]["label"], artifact["arms"][arm]))
    lines.extend(
        [
            "",
            "## Decision",
            "",
        ]
    )
    for arm in scored:
        decision = artifact["decision"][arm]
        versus_control = artifact["comparison"][f"{arm}_minus_v0924_head"]["surfaces"][
            "hybrid"
        ]
        lines.append(
            f"**{ARMS[arm]['label']}: {decision['verdict']}** versus cleaned cheap "
            f"(headline {decision['headline_f1_delta']:+.4f}, exact net "
            f"{decision['four_family_letter_exact_net']:+d}). Versus `v0.9.24`: "
            f"headline {versus_control['headline_f1_delta']:+.4f}, SF "
            f"{versus_control['family_f1_delta']['SeizureFrequency']:+.4f}, "
            f"exact net {versus_control['four_family_letter_exact_net']:+d}."
        )
        lines.append("")
    lines.extend(
        [
            "Live default stays `v0.9.24`. Slot 2 stays `v0.9.40`. Do not",
            "start `dev140` from these results.",
            "",
            "## Claim boundary",
            "",
            str(artifact["claim_boundary"]),
            "",
        ]
    )
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
