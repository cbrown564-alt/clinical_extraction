"""Luna ExECT v13 on full dev140 through the current hybrid stack.

``check`` verifies the v13 payload and scores the no-call v0.9.24 arm.
``run --live`` reuses the 20 saved v13 letters and calls Luna on the rest.
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
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v13_luna_dev140_20260815"
V13_DEV20 = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v13_luna_dev20_20260815/v13_live/structured.jsonl"
)
PROTOCOL = "docs/research/exectv2/structured_prompt_v13_luna_dev140_protocol_2026-08-15.md"
REPORT_PATH = REPO_ROOT / "docs/research/exectv2/structured_prompt_v13_luna_dev140_2026-08-15.md"
MODEL = "openai/gpt-5.6-luna"
EXPECTED_N = 140


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser("check", help="Verify v13 payload. No new model calls.")
    check_parser.add_argument("--overwrite", action="store_true")
    run_parser = sub.add_parser("run", help="Score v0.9.24; live v13 only with --live")
    run_parser.add_argument("--live", action="store_true")
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=5)
    run_parser.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check(), indent=2, sort_keys=True))
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
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V13)
        payload = json.loads(structured.build_prompt_input(letter))
    finally:
        structured.set_active_prompt_version(original)
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("check must not leave v13 as the active default")
    if payload["prompt_version"] != structured.PROMPT_VERSION_V13:
        raise RuntimeError("v13 payload did not emit the v13 identity")
    if "letter's own words" not in " ".join(payload["clinical_rules"]):
        raise RuntimeError("v13 payload missing English-quantity permission")
    if "worked_examples" in payload or "architecture" in payload:
        raise RuntimeError("v13 payload restored examples or architecture")
    return {
        "ok": True,
        "prompt_version": payload["prompt_version"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "n_letters": EXPECTED_N,
        "protocol": PROTOCOL,
        "reused_dev20_ids": list(v13.FROZEN_IDS),
    }


def check() -> dict[str, Any]:
    return {**verify_payload(), "model_calls": 0}


def _seed_v13_dev20(destination: Path) -> int:
    """Copy the 20 saved v13 rows and their checkpoint provenance."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    source_dir = V13_DEV20.parent
    if not destination.exists():
        destination.write_bytes(V13_DEV20.read_bytes())
    for name in (
        "structured.md",
        "structured_checkpoint.md",
        "structured_checkpoint.meta.json",
    ):
        src = source_dir / name
        dest = destination.parent / name
        if src.exists() and not dest.exists():
            dest.write_bytes(src.read_bytes())
    return len(v10_run._read_jsonl(destination))


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 5,
    api_base: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    seeded = 0
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        v10_run.ESCALATION_REASON = (
            "Predeclared Luna ExECT v13 full-dev140 study under " + PROTOCOL
        )

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_v13_luna_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="ExECTv2 Luna v13 short-extraction study on full dev140.",
            )

        v10_run._arm_assembly = _patched_assembly
        control = v13._run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            dest = STUDY_DIR / "v13_live" / "structured.jsonl"
            if overwrite and dest.exists():
                dest.unlink()
            seeded = _seed_v13_dev20(dest)
            candidate = v13._run_enriched_arm(
                slug="v13_live",
                prompt_version=structured.PROMPT_VERSION_V13,
                letters=letters,
                call_mode="live",
                overwrite=False,
                progress_every=progress_every,
                api_base=api_base,
            )
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v13_luna_dev140.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_count": EXPECTED_N,
        "row_policy": "dev_rows_permitted",
        "scorer": "four-family clinical_headline",
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v13_live": "live_plus_reused_dev20" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "seeded_dev20_rows": seeded,
        "model_calls": 0 if not live else max(0, EXPECTED_N - len(v13.FROZEN_IDS)),
        "letter_ids": [letter.letter_id for letter in letters],
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": {"v0924_head": control["summary"]},
        "claim_boundary": (
            "ExECTv2 Luna full-dev140 comparison of v13+HEAD against frozen "
            "v0.9.24 through the same stack. Not holdout and not a fill."
        ),
    }
    if candidate is not None:
        artifact["arms"]["v13_live"] = candidate["summary"]
        artifact["comparison"] = {
            "v13_live_minus_v0924_head": v13._compare_pair(control, candidate, letters)
        }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
        "seeded_dev20_rows": seeded,
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    live = bool(artifact["live"])
    ctrl = artifact["arms"]["v0924_head"]
    cand = artifact["arms"].get("v13_live")
    if not live or cand is None:
        verdict = "Live arm not run."
        tables = "Live v13 scores are absent."
    else:
        vs = artifact["comparison"]["v13_live_minus_v0924_head"]
        hybrid = vs["surfaces"]["hybrid"]
        raw = vs["surfaces"]["raw"]
        verdict = (
            "Development measurement only. SF drop versus `v0.9.24` is expected. "
            "Does not promote v13 or change a fill."
        )
        tables = f"""## Headline F1 on `dev140`

| Surface | v0.9.24 HEAD | v13 live | v13 − v0.9.24 |
| :--- | ---: | ---: | ---: |
| raw | {ctrl["raw_headline_f1"]:.4f} | {cand["raw_headline_f1"]:.4f} | {raw["headline_f1_delta"]:+.4f} |
| hybrid | {ctrl["hybrid_headline_f1"]:.4f} | {cand["hybrid_headline_f1"]:.4f} | {hybrid["headline_f1_delta"]:+.4f} |

## Family F1 (hybrid)

| Family | v0.9.24 | v13 | delta |
| :--- | ---: | ---: | ---: |
| Diagnosis | {ctrl["hybrid_family_f1"]["Diagnosis"]:.4f} | {cand["hybrid_family_f1"]["Diagnosis"]:.4f} | {hybrid["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {ctrl["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {cand["hybrid_family_f1"]["SeizureFrequency"]:.4f} | {hybrid["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {ctrl["hybrid_family_f1"]["Prescription"]:.4f} | {cand["hybrid_family_f1"]["Prescription"]:.4f} | {hybrid["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {ctrl["hybrid_family_f1"]["Investigations"]:.4f} | {cand["hybrid_family_f1"]["Investigations"]:.4f} | {hybrid["family_f1_delta"]["Investigations"]:+.4f} |

## Four-family letter-exact

| Surface | v0.9.24 | v13 | wins | losses | net |
| :--- | ---: | ---: | ---: | ---: | ---: |
| hybrid | {ctrl["hybrid_four_family_letter_exact"]}/140 | {cand["hybrid_four_family_letter_exact"]}/140 | {hybrid["four_family_letter_exact_wins"]} | {hybrid["four_family_letter_exact_losses"]} | {hybrid["four_family_letter_exact_net"]} |
"""
    return f"""# Luna ExECT v13 on full `dev140`

Date: 2026-08-15
Status: {"complete" if live else "protocol frozen; live arm not run"}
Protocol: [structured_prompt_v13_luna_dev140_protocol_2026-08-15.md](structured_prompt_v13_luna_dev140_protocol_2026-08-15.md)
Model: `{artifact["model"]}`
Split: ExECT `dev140` (n={artifact["row_count"]}). `test60` not touched.
Replay: v0.9.24 no-call sidecar; v13 live plus {len(v13.FROZEN_IDS)} reused `dev20` rows.
Stack: HEAD hybrid. Repair: default / default. Scorer: four-family `clinical_headline`.

## Verdict

{verdict}

{tables}

## Boundary

Not `test60`. Not a selected prompt. Not Decision 0046 / 0050.
"""


if __name__ == "__main__":
    main()
