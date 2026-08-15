"""Luna-only ExECT v11 topology study on the frozen v10 dev20 sample.

``check`` is no-call. ``run --live`` is 20 Luna calls and is not
authorized by the protocol alone.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
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

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v11_luna_dev20_20260815"
V10_SAMPLE = (
    REPO_ROOT / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815/sample.json"
)
V10_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v10_luna_dev20_20260815/v10_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v11_luna_dev20_protocol_2026-08-15.md"
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


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Verify v11 payload and frozen IDs. No model calls.")
    run_parser = sub.add_parser("run", help="Score saved arms; live only with --live")
    run_parser.add_argument(
        "--live",
        action="store_true",
        help="Make 20 Luna calls. Forbidden unless the protocol is explicitly authorized.",
    )
    run_parser.add_argument("--overwrite", action="store_true")
    run_parser.add_argument("--progress-every", type=int, default=1)
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


def check() -> dict[str, Any]:
    sample = json.loads(V10_SAMPLE.read_text(encoding="utf-8"))
    if sample["letter_ids"] != list(FROZEN_IDS):
        raise RuntimeError("frozen v10 sample IDs drifted; protocol must not redraw")
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V11)
        payload = json.loads(structured.build_prompt_input(letter))
    finally:
        structured.set_active_prompt_version(original)
    joined = " ".join(payload["clinical_rules"]) + " " + payload["task"]
    forbidden = (
        "several",
        "couple",
        "candidate_evidence_ledger",
        "architecture",
        "worked_examples",
    )
    leaks = [token for token in forbidden if token in joined]
    if leaks:
        raise RuntimeError(f"v11 payload leaked codebook or ledger terms: {leaks}")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("check must not leave v11 as the active default")
    return {
        "ok": True,
        "model_calls": 0,
        "prompt_version": payload["prompt_version"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "n_rules": len(payload["clinical_rules"]),
        "letter_ids": list(FROZEN_IDS),
        "protocol": PROTOCOL,
    }


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    check()
    letters = [
        letter
        for letter in load_letters_for_split("dev")
        if letter.letter_id in set(FROZEN_IDS)
    ]
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 20:
        raise RuntimeError(f"expected 20 letters, found {len(letters)}")

    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = (
            "Predeclared Luna-only ExECT v11 topology study on the frozen "
            "v10 20-letter sample under " + PROTOCOL
        )
        control = v10_run._run_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        v10_run.CONTROL_STRUCTURED = V10_STRUCTURED
        mechanism = v10_run._run_arm(
            slug="v10_head",
            prompt_version=structured.PROMPT_VERSION_V10,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            v10_run.CONTROL_STRUCTURED = original_control
            candidate = v10_run._run_arm(
                slug="v11_live",
                prompt_version=structured.PROMPT_VERSION_V11,
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

    artifact = {
        "schema_version": "exectv2.structured_prompt_v11_luna_dev20.v1",
        "protocol": PROTOCOL,
        "model_calls": 20 if live else 0,
        "live": live,
        "letter_ids": list(FROZEN_IDS),
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": {
            "v0924_head": control["summary"],
            "v10_head": mechanism["summary"],
        },
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development comparison of v11+HEAD "
            "against frozen v0.9.24 through the same stack. Not holdout, "
            "not a selected prompt, and not benchmark performance."
        ),
    }
    if candidate is not None:
        artifact["arms"]["v11_live"] = candidate["summary"]
        artifact["comparison"] = v10_run._compare_arms(control, candidate, letters)
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
    }


if __name__ == "__main__":
    main()
