"""Authorized name-in-cheap transfer of ExECT cheap stack on Luna dev140."""

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
    CONTROL_STRUCTURED,
    CONTROL_VERSION,
    FROZEN_DEV20_IDS,
    MODEL,
    SCAFFOLD_KEYS,
    _assembly_row,
    _changed_rows,
    _compare_pair,
    _existing_complete_rows,
    _letters,
    _provenance,
    _require_api_key,
    _score_arm,
    _subset_arm,
    decide_arm,
    topology_failures,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/mention_unit_cheap_combo_luna_dev140_protocol_2026-08-17.md"
)
REPORT = ROOT / "docs/research/exectv2/mention_unit_cheap_combo_luna_dev140_2026-08-17.md"
STUDY_DIR = ROOT / "experiments/exectv2_mention_unit_cheap_combo_luna_dev140_20260817"
CHEAP_STRUCTURED = (
    ROOT
    / "experiments/exectv2_v0924_cheap_stack_luna_dev140_20260816"
    / "drop_encoding_non_sf_all_examples"
    / "structured.jsonl"
)
CHEAP_VERSION = structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
CANDIDATE_ARM = "name_in_cheap"
CANDIDATE_VERSION = structured.PROMPT_VERSION_V0_9_40_COMBO_CLINICAL_NAME
SAVED_DEV20 = (
    ROOT / "experiments/exectv2_mention_unit_cheap_combo_luna_dev20_20260817" / "comparison.json"
)


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
        cheap = json.loads(
            structured.build_prompt_input(letter, prompt_version=CHEAP_VERSION)
        )
        if len(cheap["clinical_rules"]) != 67 or len(cheap.get("worked_examples") or []):
            raise RuntimeError("cheap stack payload drifted")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=CANDIDATE_VERSION)
        )
        if payload["prompt_version"] != CANDIDATE_VERSION:
            raise RuntimeError(f"name_in_cheap emitted {payload['prompt_version']}")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError("name_in_cheap leaked CUI")
        n_rules = len(payload["clinical_rules"])
        n_examples = len(payload.get("worked_examples") or [])
        has_scaffold = all(key in payload for key in SCAFFOLD_KEYS)
        task = str(payload.get("task") or "")
        if n_rules != 67 or n_examples != 0 or not has_scaffold:
            raise RuntimeError("name_in_cheap contract drifted")
        if "2 to 3 focal seizures a week" not in task:
            raise RuntimeError("name_in_cheap missing the naming sentence")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "prompt_version": CANDIDATE_VERSION,
        "n_rules": 67,
        "n_examples": 0,
        "has_scaffold": True,
        "has_name_sentence": True,
        "protocol": PROTOCOL,
    }


def run_study(
    *,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int = 300,
    progress_every: int = 1,
) -> dict[str, Any]:
    verify_payload()
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
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
        raise RuntimeError("live default drifted before the run")

    control = _replay_saved(
        slug="v0924_head",
        prompt_version=CONTROL_VERSION,
        sidecar=CONTROL_STRUCTURED,
        letters=letters,
    )
    cheap = _replay_saved(
        slug="plain_cheap",
        prompt_version=CHEAP_VERSION,
        sidecar=CHEAP_STRUCTURED,
        letters=letters,
    )
    candidate = _run_candidate(
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
    )
    if structured.PROMPT_VERSION != structured.FULL_LEDGER:
        raise RuntimeError("candidate arm left the live default changed")

    versus_cheap = _compare_pair(cheap, candidate, letters)
    versus_control = _compare_pair(control, candidate, letters)
    hybrid_cheap = versus_cheap["surfaces"]["hybrid"]
    hybrid_control = versus_control["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    versus_v0924 = decide_arm(hybrid_control, quality)
    named = _named_outcomes(
        cheap,
        candidate,
        STUDY_DIR / "plain_cheap" / "assembly.jsonl",
        STUDY_DIR / CANDIDATE_ARM / "assembly.jsonl",
    )
    if quality["parse"] or quality["schema"]:
        versus_cheap_status = "revise"
    elif named["cluster_recovered"] and not named["extras_rose"]:
        versus_cheap_status = "answer"
    elif not named["cluster_recovered"] and not named["extras_rose"]:
        versus_cheap_status = "negative_result"
    else:
        versus_cheap_status = "revise"
    artifact = {
        "schema_version": "exectv2.mention_unit_cheap_combo_luna_dev140.v1",
        "status": "complete",
        "generated_on": "2026-08-17",
        "protocol": PROTOCOL,
        "model": MODEL,
        "temperature": 1.0,
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
        "arms": {
            "v0924_head": control["summary"],
            "plain_cheap": cheap["summary"],
            CANDIDATE_ARM: candidate["summary"],
        },
        "comparison": {
            "name_in_cheap_minus_plain_cheap": versus_cheap,
            "name_in_cheap_minus_v0924_head": versus_control,
        },
        "decision": {
            "versus_cheap": {
                "status": versus_cheap_status,
                "cluster_recovered": named["cluster_recovered"],
                "extras_rose": named["extras_rose"],
                "headline_f1_delta": hybrid_cheap["headline_f1_delta"],
                "family_f1_delta": hybrid_cheap["family_f1_delta"],
                "four_family_letter_exact_net": hybrid_cheap["four_family_letter_exact_net"],
            },
            "versus_v0924": {
                "status": "scored",
                "verdict": versus_v0924,
                "failures": topology_failures(hybrid_control)
                if versus_v0924 != "revise"
                else [
                    *topology_failures(hybrid_control),
                    f"parse={quality['parse']} schema={quality['schema']}",
                ],
                "headline_f1_delta": hybrid_control["headline_f1_delta"],
                "family_f1_delta": hybrid_control["family_f1_delta"],
                "four_family_letter_exact_net": hybrid_control["four_family_letter_exact_net"],
            },
        },
        "named_outcomes": named,
        "frozen_dev20_overlap": _overlap_dev20(control, cheap, candidate, letters),
        "changed_versus_cheap": _changed_rows(cheap, candidate, letters),
        "changed_versus_v0924": _changed_rows(control, candidate, letters),
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 140-letter development transfer of the study-only "
            "name_in_cheap graft. Not holdout, not a slot-2 change, and not a "
            "Decision 0050 change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "report": REPORT.relative_to(ROOT).as_posix(),
        "live": True,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
        "named_outcomes": named,
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _replay_saved(
    *,
    slug: str,
    prompt_version: str,
    sidecar: Path,
    letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    raws: dict[str, str] = {}
    wanted = {letter.letter_id for letter in letters}
    for row in load_jsonl_rows(sidecar):
        letter_id = str(row.get("letter_id") or "")
        if letter_id not in wanted:
            continue
        raw = str(row.get("raw_output") or "")
        if not raw:
            raise RuntimeError(f"{sidecar} missing raw_output for {letter_id}")
        raws[letter_id] = raw
    missing = sorted(wanted - set(raws))
    if missing:
        raise RuntimeError(f"{sidecar} missing letters: {missing}")
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


def _run_candidate(
    letters: Sequence[ExectLetter],
    *,
    overwrite: bool,
    api_base: str | None,
    timeout: int,
    progress_every: int,
) -> dict[str, Any]:
    out_dir = STUDY_DIR / CANDIDATE_ARM
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
                        f"name_in_cheap dev140: {len(rows)}/{len(letters)} structured",
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
    )


def _named_outcomes(
    cheap: Mapping[str, Any],
    candidate: Mapping[str, Any],
    cheap_assembly: Path,
    candidate_assembly: Path,
) -> dict[str, Any]:
    cheap_names = _sf_names_from_assembly(cheap_assembly)
    candidate_names = _sf_names_from_assembly(candidate_assembly)
    cluster = any("cluster" in name.casefold() for name in candidate_names.get("EA0009", []))
    cheap_extras = _empty_gold_sf(cheap)
    candidate_extras = _empty_gold_sf(candidate)
    return {
        "cluster_recovered": cluster,
        "ea0009_names": candidate_names.get("EA0009", []),
        "cheap_ea0009_names": cheap_names.get("EA0009", []),
        "empty_gold_sf_mention_count": sum(candidate_extras.values()),
        "cheap_empty_gold_sf_mention_count": sum(cheap_extras.values()),
        "empty_gold_sf_letters": candidate_extras,
        "cheap_empty_gold_sf_letters": cheap_extras,
        "extras_rose": sum(candidate_extras.values()) > sum(cheap_extras.values()),
    }


def _sf_names_from_assembly(path: Path) -> dict[str, list[str]]:
    names: dict[str, list[str]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            names[str(row["letter_id"])] = sorted(
                {
                    str(mention.get("text") or "")
                    for mention in row.get("predicted_mentions") or []
                    if mention.get("entity") == "SeizureFrequency"
                }
            )
    return names


def _empty_gold_sf(arm: Mapping[str, Any]) -> dict[str, int]:
    extras: dict[str, int] = {}
    for row in arm["letter_rows"]:
        if row["family"] != "SeizureFrequency" or not row["empty_gold"]:
            continue
        count = int(row["hybrid_mention_count"])
        if count:
            extras[str(row["letter_id"])] = count
    return extras


def _overlap_dev20(
    control: Mapping[str, Any],
    cheap: Mapping[str, Any],
    candidate: Mapping[str, Any],
    letters: Sequence[ExectLetter],
) -> dict[str, Any]:
    wanted = set(FROZEN_DEV20_IDS)
    overlap_letters = [letter for letter in letters if letter.letter_id in wanted]
    control_overlap = _subset_arm(control, wanted)
    cheap_overlap = _subset_arm(cheap, wanted)
    candidate_overlap = _subset_arm(candidate, wanted)
    saved: dict[str, Any] = {}
    if SAVED_DEV20.exists():
        previous = json.loads(SAVED_DEV20.read_text(encoding="utf-8"))
        graft = previous.get("name_in_cheap") or {}
        versus = (graft.get("versus_cheap") or {}).get("surfaces") or {}
        hybrid = versus.get("hybrid") or {}
        saved = {
            "cluster_recovered": (graft.get("named_outcomes") or {}).get("cluster_recovered"),
            "headline_f1_delta": hybrid.get("headline_f1_delta"),
            "sf_f1_delta": (hybrid.get("family_f1_delta") or {}).get("SeizureFrequency"),
        }
    return {
        "letter_ids": [letter.letter_id for letter in overlap_letters],
        "row_count": len(overlap_letters),
        "arms": {
            "v0924_head": control_overlap["summary"],
            "plain_cheap": cheap_overlap["summary"],
            CANDIDATE_ARM: candidate_overlap["summary"],
        },
        "comparison": {
            "name_in_cheap_minus_plain_cheap": _compare_pair(
                cheap_overlap, candidate_overlap, overlap_letters
            ),
            "name_in_cheap_minus_v0924_head": _compare_pair(
                control_overlap, candidate_overlap, overlap_letters
            ),
        },
        "saved_dev20_artifact": saved,
        "note": (
            "Frozen 20-letter overlap only. Do not treat this slice as the "
            "140-letter result."
        ),
    }


def _render_report(artifact: dict[str, Any]) -> str:
    cheap = artifact["decision"]["versus_cheap"]
    v0924 = artifact["decision"]["versus_v0924"]
    arms = artifact["arms"]
    named = artifact["named_outcomes"]
    lines = [
        "# ExECT mention-unit naming graft on cheap stack, Luna `dev140`",
        "",
        "Date: 2026-08-17  ",
        f"Status: complete; versus cheap **{cheap['status']}**; "
        f"versus `v0.9.24` **{v0924['verdict']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [combination `dev20`](mention_unit_cheap_combo_luna_dev20_2026-08-17.md)",
        "",
        f"`model_calls`: {artifact['model_calls']}. Saved `v0.9.24` and cheap-stack "
        "sidecars only for the two controls.",
        "",
        "## Headlines",
        "",
        "| Arm | Headline | SF | exact | extras |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    extras = {
        "v0924_head": None,
        "plain_cheap": named["cheap_empty_gold_sf_mention_count"],
        CANDIDATE_ARM: named["empty_gold_sf_mention_count"],
    }
    for slug in ("v0924_head", "plain_cheap", CANDIDATE_ARM):
        arm = arms[slug]
        extra = extras[slug]
        extra_cell = "—" if extra is None else str(extra)
        lines.append(
            f"| `{slug}` | {arm['hybrid_headline_f1']:.4f} | "
            f"{arm['hybrid_family_f1']['SeizureFrequency']:.4f} | "
            f"{arm['hybrid_four_family_letter_exact']}/140 | {extra_cell} |"
        )
    lines += [
        "",
        f"EA0009 cluster recovered: {named['cluster_recovered']}.",
        f"Empty-gold SF extras rose versus cheap: {named['extras_rose']}.",
        "",
        "## Claim boundary",
        "",
        artifact["claim_boundary"],
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
