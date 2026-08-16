"""Leave-one-out / cheap-stack prune checks for ExECT v0.9.24 on Luna dev20.

Live remasure helpers that lived in the structured-prompt zoo runners were
pruned with that zoo. Payload contract checks for the retained cheap-stack
slot remain here. Recover the deleted runners from git history to remasure.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LEAVE_ONE_OUT_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_ablation_luna_dev20_20260816"
)
CUMULATIVE_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_cumulative_prune_luna_dev20_20260816"
)
SCOPE_CLUSTER_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_scope_cluster_luna_dev20_20260816"
)
NON_SF_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_non_sf_slice_luna_dev20_20260816"
)
SF_EXAMPLES_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_sf_examples_luna_dev20_20260816"
)
CHEAP_STACK_STUDY_DIR = (
    REPO_ROOT / "experiments/exectv2_v0924_cheap_stack_luna_dev20_20260816"
)
LEAVE_ONE_OUT_PROTOCOL = (
    "docs/research/exectv2/v0924_prompt_ablation_luna_dev20_protocol_2026-08-16.md"
)
CUMULATIVE_PROTOCOL = (
    "docs/research/exectv2/v0924_cumulative_prune_luna_dev20_protocol_2026-08-16.md"
)
SCOPE_CLUSTER_PROTOCOL = (
    "docs/research/exectv2/v0924_scope_cluster_luna_dev20_protocol_2026-08-16.md"
)
NON_SF_PROTOCOL = (
    "docs/research/exectv2/v0924_non_sf_slice_luna_dev20_protocol_2026-08-16.md"
)
SF_EXAMPLES_PROTOCOL = (
    "docs/research/exectv2/v0924_sf_examples_luna_dev20_protocol_2026-08-16.md"
)
CHEAP_STACK_PROTOCOL = (
    "docs/research/exectv2/v0924_cheap_stack_luna_dev20_protocol_2026-08-16.md"
)
LEAVE_ONE_OUT_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_prompt_ablation_luna_dev20_2026-08-16.md"
)
CUMULATIVE_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_cumulative_prune_luna_dev20_2026-08-16.md"
)
SCOPE_CLUSTER_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_scope_cluster_luna_dev20_2026-08-16.md"
)
NON_SF_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_non_sf_slice_luna_dev20_2026-08-16.md"
)
SF_EXAMPLES_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_sf_examples_luna_dev20_2026-08-16.md"
)
CHEAP_STACK_REPORT = (
    REPO_ROOT / "docs/research/exectv2/v0924_cheap_stack_luna_dev20_2026-08-16.md"
)
STUDY_DIR = CHEAP_STACK_STUDY_DIR
PROTOCOL = CHEAP_STACK_PROTOCOL
REPORT_PATH = CHEAP_STACK_REPORT
MODEL = "openai/gpt-5.6-luna"
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
SERIES_ORDER: tuple[str, ...] = ()
CUMULATIVE_ARMS: tuple[str, ...] = ()
SCOPE_CLUSTER_ARMS: tuple[str, ...] = ()
NON_SF_ARMS: tuple[str, ...] = ()
SF_EXAMPLE_ARMS: tuple[str, ...] = ()
CHEAP_STACK_ARMS = ("drop_encoding_non_sf_all_examples",)
ARM_VERSIONS = {
    "drop_encoding_non_sf_all_examples": (
        structured.PROMPT_VERSION_V0_9_40_DROP_ENCODING_NON_SF_ALL_EXAMPLES
    ),
}
CONTAMINATION_LETTERS = ("EA0004", "EA0010")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Verify ablation payloads and score the control.")
    check.add_argument("--overwrite", action="store_true")
    run = sub.add_parser("run", help="Score control; live only with --live")
    run.add_argument(
        "--arm",
        choices=(
            *SERIES_ORDER,
            *CUMULATIVE_ARMS,
            *SCOPE_CLUSTER_ARMS,
            *NON_SF_ARMS,
            *SF_EXAMPLE_ARMS,
            *CHEAP_STACK_ARMS,
        ),
    )
    run.add_argument("--series", action="store_true", help="Run every leave-one-out arm.")
    run.add_argument("--live", action="store_true")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--progress-every", type=int, default=1)
    run.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check_study(overwrite=args.overwrite), indent=2, sort_keys=True))
        return
    arms = list(SERIES_ORDER) if args.series else [args.arm] if args.arm else []
    if not arms:
        raise SystemExit("run requires --arm NAME or --series")
    print(
        json.dumps(
            run_study(
                arms=arms,
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
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    before = structured.PROMPT_VERSION
    checks: dict[str, Any] = {}
    try:
        control = json.loads(
            structured.build_prompt_input(
                letter, prompt_version=structured.PROMPT_VERSION_V0_9_24
            )
        )
        if len(control["clinical_rules"]) != 83 or len(control["worked_examples"]) != 49:
            raise RuntimeError("v0.9.24 control payload drifted")
        for arm, version in ARM_VERSIONS.items():
            payload = json.loads(
                structured.build_prompt_input(letter, prompt_version=version)
            )
            if payload["prompt_version"] != version:
                raise RuntimeError(f"{arm} emitted {payload['prompt_version']}")
            if "cui" in json.dumps(payload).lower():
                raise RuntimeError(f"{arm} leaked CUI")
            checks[arm] = {
                "prompt_version": version,
                "n_rules": len(payload["clinical_rules"]),
                "n_examples": len(payload.get("worked_examples") or []),
                "has_scaffold": "architecture" in payload,
            }
    finally:
        structured.set_active_prompt_version(before)
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("ablation check changed the live default")
    if (
        checks["drop_encoding_non_sf_all_examples"]["n_examples"] != 0
        or checks["drop_encoding_non_sf_all_examples"]["n_rules"] != 67
        or not checks["drop_encoding_non_sf_all_examples"]["has_scaffold"]
    ):
        raise RuntimeError("drop_encoding_non_sf_all_examples contract drifted")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "letter_ids": list(FROZEN_IDS),
        "protocol": PROTOCOL,
        "arms": checks,
    }


def check_study(*, overwrite: bool = False) -> dict[str, Any]:
    del overwrite
    return verify_payload()


def run_study(
    *,
    arms: Sequence[str],
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    del overwrite, progress_every, api_base
    verify_payload()
    _select_study(arms)
    if live:
        raise RuntimeError(
            "Live v0.9.24 prune remasure helpers were pruned with the ExECT "
            "prompt zoo. Recover run_exectv2_structured_prompt_v10_luna_dev20.py "
            "and run_exectv2_structured_prompt_v13_luna_dev20.py from git history "
            "to remasure; retained cheap-stack comparison.json stays the answer."
        )
    previous = _load_previous_artifact()
    if not previous:
        raise RuntimeError(
            f"no retained comparison artifact at {STUDY_DIR / 'comparison.json'}"
        )
    return {
        "artifact": (STUDY_DIR / "comparison.json").relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": bool(previous.get("live")),
        "model_calls": int(previous.get("model_calls") or 0),
        "decision": previous.get("decision", {}),
        "default_prompt_version": structured.PROMPT_VERSION,
    }


def _select_study(arms: Sequence[str]) -> None:
    global STUDY_DIR, PROTOCOL, REPORT_PATH
    if any(arm in CUMULATIVE_ARMS for arm in arms):
        STUDY_DIR = CUMULATIVE_STUDY_DIR
        PROTOCOL = CUMULATIVE_PROTOCOL
        REPORT_PATH = CUMULATIVE_REPORT
        return
    if any(arm in SCOPE_CLUSTER_ARMS for arm in arms):
        STUDY_DIR = SCOPE_CLUSTER_STUDY_DIR
        PROTOCOL = SCOPE_CLUSTER_PROTOCOL
        REPORT_PATH = SCOPE_CLUSTER_REPORT
        return
    if any(arm in NON_SF_ARMS for arm in arms):
        STUDY_DIR = NON_SF_STUDY_DIR
        PROTOCOL = NON_SF_PROTOCOL
        REPORT_PATH = NON_SF_REPORT
        return
    if any(arm in SF_EXAMPLE_ARMS for arm in arms):
        STUDY_DIR = SF_EXAMPLES_STUDY_DIR
        PROTOCOL = SF_EXAMPLES_PROTOCOL
        REPORT_PATH = SF_EXAMPLES_REPORT
        return
    if any(arm in CHEAP_STACK_ARMS for arm in arms) or not arms:
        STUDY_DIR = CHEAP_STACK_STUDY_DIR
        PROTOCOL = CHEAP_STACK_PROTOCOL
        REPORT_PATH = CHEAP_STACK_REPORT
        return
    STUDY_DIR = LEAVE_ONE_OUT_STUDY_DIR
    PROTOCOL = LEAVE_ONE_OUT_PROTOCOL
    REPORT_PATH = LEAVE_ONE_OUT_REPORT


def _load_previous_artifact() -> dict[str, Any]:
    path = STUDY_DIR / "comparison.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def _letters() -> list[Any]:
    frozen = set(FROZEN_IDS)
    letters = [
        letter for letter in load_letters_for_split("dev") if letter.letter_id in frozen
    ]
    letters.sort(key=lambda item: item.letter_id)
    if [letter.letter_id for letter in letters] != sorted(FROZEN_IDS):
        raise RuntimeError("the frozen 20-letter Luna sample is unavailable or changed")
    return letters


def _claim_boundary() -> str:
    if STUDY_DIR == CUMULATIVE_STUDY_DIR:
        return (
            "ExECTv2 Luna 20-letter development cumulative prune of v0.9.24. "
            "Not holdout, not a selected prompt, and not a Decision 0050 change."
        )
    if STUDY_DIR == SCOPE_CLUSTER_STUDY_DIR:
        return (
            "ExECTv2 Luna 20-letter development scope-cluster prune of v0.9.24. "
            "Not holdout, not a selected prompt, and not a Decision 0050 change."
        )
    if STUDY_DIR == NON_SF_STUDY_DIR:
        return (
            "ExECTv2 Luna 20-letter development non-SF encoding/example prune of "
            "v0.9.24. Not holdout, not a selected prompt, and not a Decision 0050 "
            "change."
        )
    if STUDY_DIR == SF_EXAMPLES_STUDY_DIR:
        return (
            "ExECTv2 Luna 20-letter development SF-example split of v0.9.24. "
            "Not holdout, not a selected prompt, and not a Decision 0050 change."
        )
    if STUDY_DIR == CHEAP_STACK_STUDY_DIR:
        return (
            "ExECTv2 Luna 20-letter development cheap-slice stack of v0.9.24. "
            "Not holdout, not a selected prompt, and not a Decision 0050 change."
        )
    return (
        "ExECTv2 Luna 20-letter development leave-one-out prune of v0.9.24. "
        "Not holdout, not a selected prompt, and not a Decision 0050 change."
    )


def _should_write_stub_report() -> bool:
    if not REPORT_PATH.exists():
        return True
    return "Executive result" not in REPORT_PATH.read_text(encoding="utf-8")


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    if STUDY_DIR == CUMULATIVE_STUDY_DIR:
        title = "# ExECT `v0.9.24` cumulative prune — GPT-5.6 Luna `dev20`"
    elif STUDY_DIR == SCOPE_CLUSTER_STUDY_DIR:
        title = "# ExECT `v0.9.24` scope-cluster prune — GPT-5.6 Luna `dev20`"
    elif STUDY_DIR == NON_SF_STUDY_DIR:
        title = "# ExECT `v0.9.24` non-SF slice prune — GPT-5.6 Luna `dev20`"
    elif STUDY_DIR == SF_EXAMPLES_STUDY_DIR:
        title = "# ExECT `v0.9.24` SF-example split — GPT-5.6 Luna `dev20`"
    elif STUDY_DIR == CHEAP_STACK_STUDY_DIR:
        title = "# ExECT `v0.9.24` cheap-slice stack — GPT-5.6 Luna `dev20`"
    else:
        title = "# ExECT `v0.9.24` leave-one-out prompt prune — GPT-5.6 Luna `dev20`"
    lines = [
        title,
        "",
        "Date: 2026-08-16",
        f"Status: {'live arms scored' if artifact['live'] else 'no-call check; live not run'}",
        f"Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})",
        "",
        "## Headline context",
        "",
        f"Control hybrid F1: **{ctrl.get('hybrid_headline_f1', ctrl.get('headline_f1', 'n/a'))}**.",
        f"Model calls: {artifact['model_calls']}. Default remains `v0.9.24`.",
        "",
        "## Decisions",
        "",
    ]
    if not artifact["decision"]:
        lines.append("No ablation arm scored yet.")
    for arm, decision in artifact["decision"].items():
        verdict = decision.get("verdict") or "not_run"
        delta = decision.get("headline_f1_delta")
        lines.append(
            f"- **{arm}:** {verdict}; hybrid headline delta {delta}."
        )
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            artifact["claim_boundary"],
            "",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
