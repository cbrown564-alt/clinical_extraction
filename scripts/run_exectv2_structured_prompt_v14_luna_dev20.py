"""Luna-only ExECT v14 SF-role study on the frozen v10 dev20 sample.

``check`` builds the v14 payload and scores the no-call arms.
``run --live`` is 20 Luna calls and is not authorized by the protocol
alone.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
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
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v14_luna_dev20_20260815"
V13_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v13_luna_dev20_20260815/v13_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v14_luna_dev20_protocol_2026-08-15.md"
)
REPORT_PATH = (
    REPO_ROOT / "docs/research/exectv2/structured_prompt_v14_luna_dev20_2026-08-15.md"
)
MODEL = "openai/gpt-5.6-luna"
FORBIDDEN_PAYLOAD_TOKENS = (
    "several",
    "couple",
    "candidate_evidence_ledger",
    "architecture",
    "worked_examples",
    "LastClinic",
)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser(
        "check",
        help="Verify v14 payload and score the no-call arms. No model calls.",
    )
    check_parser.add_argument("--overwrite", action="store_true")
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


def verify_payload() -> dict[str, Any]:
    sample = json.loads(v13.V10_SAMPLE.read_text(encoding="utf-8"))
    if sample["letter_ids"] != list(v13.FROZEN_IDS):
        raise RuntimeError("frozen v10 sample IDs drifted; protocol must not redraw")
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    original = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.PROMPT_VERSION_V14)
        payload = json.loads(structured.build_prompt_input(letter))
    finally:
        structured.set_active_prompt_version(original)
    joined = (
        " ".join(payload["clinical_rules"])
        + " "
        + payload["task"]
        + " "
        + " ".join(payload["family_guidance"].values())
    )
    leaks = [token for token in FORBIDDEN_PAYLOAD_TOKENS if token in joined]
    if leaks:
        raise RuntimeError(f"v14 payload leaked codebook or ledger terms: {leaks}")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("check must not leave v14 as the active default")
    if payload["prompt_version"] != structured.PROMPT_VERSION_V14:
        raise RuntimeError("v14 payload did not emit the v14 identity")
    if "letter's own words" not in joined:
        raise RuntimeError("v14 payload missing English-quantity permission")
    if "driving" in joined.lower() or "Completed tests only" in joined:
        raise RuntimeError("v14 payload restored the v12 scope sermon")
    if "current_rate" not in joined or "seizure_free" not in joined:
        raise RuntimeError("v14 payload missing SF roles")
    if "change_companion" not in joined:
        raise RuntimeError("v14 payload missing change_companion role")
    if len(payload["clinical_rules"]) != 14:
        raise RuntimeError(
            f"v14 should have 14 hygiene rules, found {len(payload['clinical_rules'])}"
        )
    for key in (
        "architecture",
        "decision_procedure",
        "candidate_evidence_ledger",
        "event_lane_guide",
        "worked_examples",
    ):
        if key in payload:
            raise RuntimeError(f"v14 payload still contains {key}")
    return {
        "ok": True,
        "model_calls": 0,
        "prompt_version": payload["prompt_version"],
        "default_prompt_version": structured.PROMPT_VERSION,
        "n_rules": len(payload["clinical_rules"]),
        "letter_ids": list(v13.FROZEN_IDS),
        "protocol": PROTOCOL,
    }


def check(*, overwrite: bool = False) -> dict[str, Any]:
    payload = verify_payload()
    scored = run_study(live=False, overwrite=overwrite)
    return {**payload, **scored, "model_calls": 0}


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    sample = json.loads(v13.V10_SAMPLE.read_text(encoding="utf-8"))
    letters = [
        letter
        for letter in load_letters_for_split("dev")
        if letter.letter_id in set(v13.FROZEN_IDS)
    ]
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 20:
        raise RuntimeError(f"expected 20 letters, found {len(letters)}")

    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        v10_run.ESCALATION_REASON = (
            "Predeclared Luna-only ExECT v14 SF-role study on the frozen "
            "v10 20-letter sample under " + PROTOCOL
        )
        v10_run._arm_assembly = v13._patched_arm_assembly
        control = v13._run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        v10_run.CONTROL_STRUCTURED = V13_STRUCTURED
        mechanism = v13._run_enriched_arm(
            slug="v13_head",
            prompt_version=structured.PROMPT_VERSION_V13,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            candidate = v13._run_enriched_arm(
                slug="v14_live",
                prompt_version=structured.PROMPT_VERSION_V14,
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

    arms = {
        "v0924_head": control["summary"],
        "v13_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v14_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_count": 20,
        "sample": sample,
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v13_head": "saved_structured_no_call",
            "v14_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": 20 if live else 0,
        "letter_ids": list(v13.FROZEN_IDS),
        "default_prompt_version": structured.PROMPT_VERSION,
        "arms": arms,
        "comparison": {
            "v13_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)
        },
        "decision": {
            "status": "live_not_run",
            "verdict": None,
            "rule": (
                "topology sufficient on hybrid vs v0924_head if headline F1 "
                "drop < 0.05, no family F1 drop >= 0.08, and net four-family "
                "letter-exact losses < 3"
            ),
        },
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development comparison of v14+HEAD "
            "against frozen v0.9.24 through the same stack. Not holdout, "
            "not a selected prompt, and not benchmark performance."
        ),
    }
    if candidate is not None:
        artifact["arms"]["v14_live"] = candidate["summary"]
        versus_control = v13._compare_pair(control, candidate, letters)
        versus_mechanism = v13._compare_pair(mechanism, candidate, letters)
        artifact["comparison"]["v14_live_minus_v0924_head"] = versus_control
        artifact["comparison"]["v14_live_minus_v13_head"] = versus_mechanism
        artifact["decision"] = v13.decide_topology(versus_control, versus_mechanism)

    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    del artifact
    return (
        "# Luna `dev20` test of ExECT v14 SF roles\n\n"
        "Date: 2026-08-15\n"
        "Status: protocol frozen; live arm not run\n"
        f"Protocol: [{PROTOCOL}]({Path(PROTOCOL).name})\n"
        "Model: `openai/gpt-5.6-luna`\n"
        "Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched\n\n"
        "## Boundary\n\n"
        "Not `test60`. Not a selected prompt. Not a fill.\n"
    )


if __name__ == "__main__":
    main()
