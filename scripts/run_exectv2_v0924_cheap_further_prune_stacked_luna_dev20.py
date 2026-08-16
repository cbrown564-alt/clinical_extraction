"""Score the stacked further prune of the cleaned cheap stack on Luna dev20."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts.run_exectv2_v0924_cheap_further_prune_luna_dev20 import (
    ARMS as ONE_CUT_ARMS,
)
from scripts.run_exectv2_v0924_cheap_further_prune_luna_dev20 import (
    CHEAP_STRUCTURED,
    CHEAP_VERSION,
    CONTROL_STRUCTURED,
    _letters,
    _raws,
    _replay_arm,
    _run_candidate,
)
from scripts.run_exectv2_v0924_cheap_stack_luna_dev140 import (
    CONTROL_VERSION,
    MODEL,
    _changed_rows,
    _compare_pair,
    _provenance,
    decide_arm,
    topology_failures,
)
from scripts.run_exectv2_v0924_cheap_stack_plain_luna_dev20 import (
    CONTAMINATION_LETTERS,
)

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/exectv2/v0924_cheap_further_prune_stacked_luna_dev20_protocol_2026-08-17.md"
)
REPORT_PATH = (
    ROOT / "docs/research/exectv2/v0924_cheap_further_prune_stacked_luna_dev20_2026-08-17.md"
)
STUDY_DIR = ROOT / "experiments/exectv2_v0924_cheap_further_prune_stacked_luna_dev20_20260817"
ONE_CUT_STUDY = ROOT / "experiments/exectv2_v0924_cheap_further_prune_luna_dev20_20260816"
STACKED_ARM = "stacked"
STACKED_VERSION = structured.PROMPT_VERSION_V0_9_44_CHEAP_STACK_FURTHER_PRUNES
ONE_CUT_ORDER = ("ix_pending", "scaffold_reprint", "refuse_chorus")
STACKED_SPEC = {
    "version": STACKED_VERSION,
    "n_rules": 54,
    "drops_prompt_version": True,
    "label": "stacked further prune",
}


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
        cheap = json.loads(
            structured.build_prompt_input(letter, prompt_version=CHEAP_VERSION)
        )
        if len(cheap["clinical_rules"]) != 67 or cheap.get("worked_examples"):
            raise RuntimeError("live cheap-stack contract drifted")
        payload = json.loads(
            structured.build_prompt_input(letter, prompt_version=STACKED_VERSION)
        )
        if "prompt_version" in payload or "letter_id" in payload:
            raise RuntimeError("stacked arm still shows research metadata")
        if len(payload["clinical_rules"]) != 54:
            raise RuntimeError(
                f"stacked arm has {len(payload['clinical_rules'])} rules, expected 54"
            )
        if payload.get("worked_examples"):
            raise RuntimeError("stacked arm still has examples")
        if "cui" in json.dumps(payload).lower():
            raise RuntimeError("stacked arm leaked CUI")
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("payload check changed the live default")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "arm": STACKED_ARM,
        "prompt_version": STACKED_VERSION,
        "n_rules": 54,
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
    for path in (CONTROL_STRUCTURED, CHEAP_STRUCTURED):
        if not path.exists():
            raise RuntimeError(f"missing saved sidecar: {path}")
    for arm in ONE_CUT_ORDER:
        sidecar = ONE_CUT_STUDY / arm / "structured.jsonl"
        if not sidecar.exists():
            raise RuntimeError(f"missing one-cut sidecar: {sidecar}")

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
        study_dir=STUDY_DIR,
    )
    cheap = _replay_arm(
        slug="plain_cheap",
        prompt_version=CHEAP_VERSION,
        raws=_raws(CHEAP_STRUCTURED, letters),
        letters=letters,
        call_mode="saved_structured_no_call",
        study_dir=STUDY_DIR,
    )
    one_cuts: dict[str, dict[str, Any]] = {}
    for arm in ONE_CUT_ORDER:
        one_cuts[arm] = _replay_arm(
            slug=arm,
            prompt_version=str(ONE_CUT_ARMS[arm]["version"]),
            raws=_raws(ONE_CUT_STUDY / arm / "structured.jsonl", letters),
            letters=letters,
            call_mode="saved_structured_no_call",
            study_dir=STUDY_DIR,
        )
    candidate = _run_candidate(
        STACKED_ARM,
        letters,
        overwrite=overwrite,
        api_base=api_base,
        timeout=timeout,
        progress_every=progress_every,
        study_dir=STUDY_DIR,
        arms={STACKED_ARM: STACKED_SPEC},
    )
    if structured.PROMPT_VERSION != CONTROL_VERSION:
        raise RuntimeError("candidate arm left the live default changed")

    versus_cheap = _compare_pair(cheap, candidate, letters)
    versus_control = _compare_pair(control, candidate, letters)
    versus_one_cuts = {
        arm: _compare_pair(one_cuts[arm], candidate, letters) for arm in ONE_CUT_ORDER
    }
    hybrid = versus_cheap["surfaces"]["hybrid"]
    quality = candidate["summary"]["quality"]
    verdict = decide_arm(hybrid, quality)
    arms = {
        "v0924_head": control["summary"],
        "plain_cheap": cheap["summary"],
        STACKED_ARM: candidate["summary"],
    }
    for arm in ONE_CUT_ORDER:
        arms[arm] = one_cuts[arm]["summary"]
    comparison = {
        "stacked_minus_plain_cheap": versus_cheap,
        "stacked_minus_v0924_head": versus_control,
    }
    for arm in ONE_CUT_ORDER:
        comparison[f"stacked_minus_{arm}"] = versus_one_cuts[arm]
    changed = {
        "stacked_versus_plain_cheap": _changed_rows(cheap, candidate, letters),
        "stacked_versus_v0924_head": _changed_rows(control, candidate, letters),
    }
    for arm in ONE_CUT_ORDER:
        changed[f"stacked_versus_{arm}"] = _changed_rows(
            one_cuts[arm], candidate, letters
        )
    artifact = {
        "schema_version": "exectv2.v0924_cheap_further_prune_stacked_luna_dev20.v1",
        "generated_on": "2026-08-17",
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
        "requested_arms": [STACKED_ARM],
        "arms": arms,
        "comparison": comparison,
        "decision": {
            STACKED_ARM: {
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
        "changed_rows": changed,
        "provenance": _provenance(),
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development study of the stacked further "
            "cheap-stack cuts versus the cleaned cheap stack. Not holdout, not "
            "a selected prompt, not a slot-2 change, and not a Decision 0050 "
            "change."
        ),
    }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    _write_report(artifact)
    return {
        "artifact": out.relative_to(ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(ROOT).as_posix(),
        "live": True,
        "arm": STACKED_ARM,
        "model_calls": candidate["summary"]["new_model_calls"],
        "decision": artifact["decision"],
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _write_report(artifact: Mapping[str, Any]) -> None:
    control = artifact["arms"]["v0924_head"]
    cheap = artifact["arms"]["plain_cheap"]
    candidate = artifact["arms"][STACKED_ARM]
    versus_cheap = artifact["comparison"]["stacked_minus_plain_cheap"]["surfaces"][
        "hybrid"
    ]
    versus_control = artifact["comparison"]["stacked_minus_v0924_head"]["surfaces"][
        "hybrid"
    ]
    versus_scaffold = artifact["comparison"]["stacked_minus_scaffold_reprint"][
        "surfaces"
    ]["hybrid"]
    decision = artifact["decision"][STACKED_ARM]
    lines = [
        "# ExECT cheap-stack stacked further prune — GPT-5.6 Luna `dev20`",
        "",
        "Date: 2026-08-17  ",
        f"Status: complete; stacked arm **{decision['verdict']}**  ",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})  ",
        "Parent: [one-at-a-time further prune](v0924_cheap_further_prune_luna_dev20_2026-08-16.md)",
        "",
        "## Executive result",
        "",
        "The three low_value cheap-stack choruses are applied together.",
        "Default remains `v0.9.24`. Slot 2 remains `v0.9.40`.",
        "Decision 0050 is unchanged.",
        "",
        "| Arm | hybrid | Δ vs cheap | SF | SF Δ | exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| cleaned cheap | {cheap['hybrid_headline_f1']:.4f} | — | "
            f"{cheap['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{cheap['hybrid_four_family_letter_exact']}/20 |"
        ),
        (
            f"| `v0.9.24` | {control['hybrid_headline_f1']:.4f} | — | "
            f"{control['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{control['hybrid_four_family_letter_exact']}/20 |"
        ),
    ]
    for arm in ONE_CUT_ORDER:
        one = artifact["arms"][arm]
        lines.append(
            f"| {ONE_CUT_ARMS[arm]['label']} | {one['hybrid_headline_f1']:.4f} | "
            f"— | {one['hybrid_family_f1']['SeizureFrequency']:.4f} | — | "
            f"{one['hybrid_four_family_letter_exact']}/20 |"
        )
    lines.extend(
        [
            (
                f"| stacked further prune | {candidate['hybrid_headline_f1']:.4f} | "
                f"{versus_cheap['headline_f1_delta']:+.4f} | "
                f"{candidate['hybrid_family_f1']['SeizureFrequency']:.4f} | "
                f"{versus_cheap['family_f1_delta']['SeizureFrequency']:+.4f} | "
                f"{candidate['hybrid_four_family_letter_exact']}/20 |"
            ),
            "",
            f"{artifact['model_calls']} fresh Luna calls. "
            f"parse={candidate['quality']['parse']} "
            f"schema={candidate['quality']['schema']}. "
            f"Verdict versus cleaned cheap: **{decision['verdict']}**.",
            "",
            "Versus `v0.9.24`: "
            f"headline {versus_control['headline_f1_delta']:+.4f}, "
            f"SeizureFrequency {versus_control['family_f1_delta']['SeizureFrequency']:+.4f}, "
            f"exact net {versus_control['four_family_letter_exact_net']:+d}.",
            "",
            "Versus scaffold-reprint one-cut: "
            f"headline {versus_scaffold['headline_f1_delta']:+.4f}, "
            f"SeizureFrequency {versus_scaffold['family_f1_delta']['SeizureFrequency']:+.4f}, "
            f"exact net {versus_scaffold['four_family_letter_exact_net']:+d}.",
            "",
            "## Valid evidence",
            "",
            "- Same frozen 20 development letters. `test60` not inspected.",
            f"- Model `{artifact['model']}`. Temperature 1.0. Cache off.",
            "- Control: saved cleaned cheap stack through HEAD.",
            "- One-cut arms: saved further-prune raws through HEAD.",
            "- Secondary: saved `v0.9.24` through HEAD.",
            "- Candidate: live stacked further prune.",
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
    for arm in ONE_CUT_ORDER:
        lines.append(_family_row(str(ONE_CUT_ARMS[arm]["label"]), artifact["arms"][arm]))
    lines.extend(
        [
            _family_row("stacked further prune", candidate),
            "",
            "## Decision",
            "",
            f"**{decision['verdict']}** versus cleaned cheap "
            f"(headline {decision['headline_f1_delta']:+.4f}, exact net "
            f"{decision['four_family_letter_exact_net']:+d}). Live default stays "
            "`v0.9.24`. Slot 2 stays `v0.9.40`. Do not start `dev140` from this "
            "result.",
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
