"""Remasure named rule revisits on saved v13 raws; optional live v16.

``check`` verifies the v16 payload and scores the two no-call arms.
``run --live`` then calls Luna with v16 on all 140 development letters.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run
from scripts import run_exectv2_structured_prompt_v13_luna_dev20 as v13

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815"
V13_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v13_luna_dev140_20260815/v13_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v16_rules_and_shapes_luna_dev140_protocol_2026-08-15.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "docs/research/exectv2/structured_prompt_v16_rules_and_shapes_luna_dev140_2026-08-15.md"
)
MODEL = "openai/gpt-5.6-luna"
EXPECTED_N = 140


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="Verify v16. Score no-call arms.")
    check_parser.add_argument("--overwrite", action="store_true")
    run_parser = sub.add_parser("run", help="No-call remasure; live v16 with --live")
    run_parser.add_argument("--live", action="store_true")
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=5)
    run_parser.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check(overwrite=args.overwrite), indent=2, sort_keys=True))
        return
    print(
        json.dumps(
            run_study(
                live=args.live,
                overwrite=args.overwrite,
                progress_every=args.progress_every,
                api_base=args.api_base,
            ),
            indent=2,
            sort_keys=True,
        )
    )


def _letters() -> list[Any]:
    letters = list(load_letters_for_split("dev"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != EXPECTED_N:
        raise RuntimeError(f"expected {EXPECTED_N} dev letters, found {len(letters)}")
    return letters


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V16)
        payload = json.loads(structured.build_prompt_input(letter))
    finally:
        structured.set_active_prompt_version(original)
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("check must not leave v16 as the active default")
    if payload["prompt_version"] != structured.PROMPT_VERSION_V16:
        raise RuntimeError("v16 payload did not emit the v16 identity")
    if len(payload.get("worked_examples") or []) != 8:
        raise RuntimeError("v16 must carry exactly eight shape examples")
    if "architecture" in payload or "candidate_evidence_ledger" in payload:
        raise RuntimeError("v16 restored architecture or ledger")
    return {
        "ok": True,
        "prompt_version": payload["prompt_version"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "n_examples": len(payload["worked_examples"]),
        "n_letters": EXPECTED_N,
        "protocol": PROTOCOL,
    }


def check(*, overwrite: bool = False) -> dict[str, Any]:
    verify_payload()
    return {**run_study(live=False, overwrite=overwrite), "ok": True}


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 5,
    api_base: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    if not V13_STRUCTURED.exists():
        raise RuntimeError(f"missing saved v13 structured rows: {V13_STRUCTURED}")
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = "v16 rules-and-shapes Luna dev140 under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_v16_rules_and_shapes_luna_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="ExECTv2 Luna v16 shapes plus named rule revisits on dev140.",
            )

        v10_run._arm_assembly = _patched_assembly
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        control = v13._run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=progress_every,
            api_base=api_base,
        )
        v10_run.CONTROL_STRUCTURED = V13_STRUCTURED
        v13_head = v13._run_enriched_arm(
            slug="v13_head",
            prompt_version=structured.PROMPT_VERSION_V13,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            candidate = v13._run_enriched_arm(
                slug="v16_live",
                prompt_version=structured.PROMPT_VERSION_V16,
                letters=letters,
                call_mode="live",
                overwrite=overwrite,
                progress_every=progress_every,
                api_base=api_base,
            )
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    artifact: dict[str, Any] = {
        "schema_version": "exectv2.v16_rules_and_shapes_luna_dev140.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_count": EXPECTED_N,
        "row_policy": "dev_rows_permitted",
        "scorer": "four-family clinical_headline",
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v13_head": "saved_structured_no_call",
            "v16_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": EXPECTED_N if live else 0,
        "letter_ids": [letter.letter_id for letter in letters],
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": {
            "v0924_head": control["summary"],
            "v13_head": v13_head["summary"],
        },
        "comparison": {
            "v13_head_minus_v0924_head": v13._compare_pair(control, v13_head, letters)
        },
        "claim_boundary": (
            "Development remasure of named rule revisits on frozen v13 raws, "
            "with optional live v16. Not holdout and not a fill."
        ),
    }
    if candidate is not None:
        artifact["arms"]["v16_live"] = candidate["summary"]
        artifact["comparison"]["v16_live_minus_v0924_head"] = v13._compare_pair(
            control, candidate, letters
        )
        artifact["comparison"]["v16_live_minus_v13_head"] = v13._compare_pair(
            v13_head, candidate, letters
        )
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    v13_arm = artifact["arms"]["v13_head"]
    vs13 = artifact["comparison"]["v13_head_minus_v0924_head"]["surfaces"]["hybrid"]
    live = bool(artifact["live"])
    cand = artifact["arms"].get("v16_live")
    live_block = "Live v16 arm not run."
    if live and cand is not None:
        vs16 = artifact["comparison"]["v16_live_minus_v0924_head"]["surfaces"]["hybrid"]
        vs16_v13 = artifact["comparison"]["v16_live_minus_v13_head"]["surfaces"]["hybrid"]
        live_block = f"""## Live v16 vs `v0.9.24` (hybrid)

| Surface | v0.9.24 | v16 | delta |
| :--- | ---: | ---: | ---: |
| headline | {ctrl["hybrid_headline_f1"]:.4f} | {cand["hybrid_headline_f1"]:.4f} | {vs16["headline_f1_delta"]:+.4f} |
| Diagnosis | {ctrl["hybrid_family_f1"]["Diagnosis"]:.4f} | {cand["hybrid_family_f1"]["Diagnosis"]:.4f} | {vs16["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {ctrl["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {cand["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {vs16["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {ctrl["hybrid_family_f1"]["Prescription"]:.4f} | {cand["hybrid_family_f1"]["Prescription"]:.4f} | {vs16["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {ctrl["hybrid_family_f1"]["Investigations"]:.4f} | {cand["hybrid_family_f1"]["Investigations"]:.4f} | {vs16["family_f1_delta"]["Investigations"]:+.4f} |
| Four-family exact | {ctrl["hybrid_four_family_letter_exact"]}/140 | {cand["hybrid_four_family_letter_exact"]}/140 | net {vs16["four_family_letter_exact_net"]:+d} |

v16 − remasured v13 headline {vs16_v13["headline_f1_delta"]:+.4f}.
"""
    return f"""# v16 shapes + named rule revisits on Luna `dev140`

Date: 2026-08-15
Status: {"complete" if live else "no-call remasure complete; live arm not run"}
Protocol: [structured_prompt_v16_rules_and_shapes_luna_dev140_protocol_2026-08-15.md](structured_prompt_v16_rules_and_shapes_luna_dev140_protocol_2026-08-15.md)
Model: `{artifact["model"]}`
Split: ExECT `dev140` (n=140). `test60` not touched.
Replay: v0.9.24 and v13 no-call sidecars through new HEAD; {"v16 live" if live else "v16 not run"}.

## Verdict

Development measurement only. Does not promote v16 or change a fill.

## No-call remasure: v13 raws through new HEAD

| Surface | v0.9.24 | v13+new HEAD | delta |
| :--- | ---: | ---: | ---: |
| raw | {ctrl["raw_headline_f1"]:.4f} | {v13_arm["raw_headline_f1"]:.4f} | {artifact["comparison"]["v13_head_minus_v0924_head"]["surfaces"]["raw"]["headline_f1_delta"]:+.4f} |
| hybrid | {ctrl["hybrid_headline_f1"]:.4f} | {v13_arm["hybrid_headline_f1"]:.4f} | {vs13["headline_f1_delta"]:+.4f} |
| Diagnosis | {ctrl["hybrid_family_f1"]["Diagnosis"]:.4f} | {v13_arm["hybrid_family_f1"]["Diagnosis"]:.4f} | {vs13["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {ctrl["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {v13_arm["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {vs13["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {ctrl["hybrid_family_f1"]["Prescription"]:.4f} | {v13_arm["hybrid_family_f1"]["Prescription"]:.4f} | {vs13["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {ctrl["hybrid_family_f1"]["Investigations"]:.4f} | {v13_arm["hybrid_family_f1"]["Investigations"]:.4f} | {vs13["family_f1_delta"]["Investigations"]:+.4f} |
| Four-family exact | {ctrl["hybrid_four_family_letter_exact"]}/140 | {v13_arm["hybrid_four_family_letter_exact"]}/140 | net {vs13["four_family_letter_exact_net"]:+d} |

Prior v13+old HEAD hybrid headline was 0.8136 (−0.0861). This table is the
same v13 raws through the five named revisits.

{live_block}

## Boundary

Not `test60`. Not a selected prompt. Not Decision 0046 / 0050.
"""


if __name__ == "__main__":
    main()
