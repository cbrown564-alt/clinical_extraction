"""Leave-one-out prune of ExECT v0.9.24 on the frozen Luna dev20 sample."""

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
STUDY_DIR = LEAVE_ONE_OUT_STUDY_DIR
PROTOCOL = LEAVE_ONE_OUT_PROTOCOL
REPORT_PATH = LEAVE_ONE_OUT_REPORT
MODEL = "openai/gpt-5.6-luna"
SERIES_ORDER = (
    "drop_scaffold",
    "drop_examples",
    "drop_encoding",
    "drop_scope",
)
CUMULATIVE_ARMS = (
    "drop_scaffold_examples",
    "drop_scaffold_examples_encoding",
)
SCOPE_CLUSTER_ARMS = (
    "drop_scope_sf_refuse",
    "drop_scope_sf_keep",
    "drop_scope_diagnosis",
    "drop_scope_rx_ix",
)
NON_SF_ARMS = (
    "drop_encoding_non_sf",
    "drop_examples_non_sf",
)
SF_EXAMPLE_ARMS = (
    "drop_examples_sf_encoding",
    "drop_examples_sf_scope",
)
CHEAP_STACK_ARMS = ("drop_encoding_non_sf_all_examples",)
ARM_VERSIONS = {
    "drop_scaffold": structured.PROMPT_VERSION_V0_9_26_DROP_SCAFFOLD,
    "drop_examples": structured.PROMPT_VERSION_V0_9_27_DROP_EXAMPLES,
    "drop_encoding": structured.PROMPT_VERSION_V0_9_28_DROP_ENCODING_RULES,
    "drop_scope": structured.PROMPT_VERSION_V0_9_29_DROP_SCOPE_RULES,
    "drop_scaffold_examples": structured.PROMPT_VERSION_V0_9_30_DROP_SCAFFOLD_EXAMPLES,
    "drop_scaffold_examples_encoding": (
        structured.PROMPT_VERSION_V0_9_31_DROP_SCAFFOLD_EXAMPLES_ENCODING
    ),
    "drop_scope_sf_refuse": structured.PROMPT_VERSION_V0_9_32_DROP_SCOPE_SF_REFUSE,
    "drop_scope_sf_keep": structured.PROMPT_VERSION_V0_9_33_DROP_SCOPE_SF_KEEP,
    "drop_scope_diagnosis": structured.PROMPT_VERSION_V0_9_34_DROP_SCOPE_DIAGNOSIS,
    "drop_scope_rx_ix": structured.PROMPT_VERSION_V0_9_35_DROP_SCOPE_RX_IX,
    "drop_encoding_non_sf": structured.PROMPT_VERSION_V0_9_36_DROP_ENCODING_NON_SF,
    "drop_examples_non_sf": structured.PROMPT_VERSION_V0_9_37_DROP_EXAMPLES_NON_SF,
    "drop_examples_sf_encoding": structured.PROMPT_VERSION_V0_9_38_DROP_EXAMPLES_SF_ENCODING,
    "drop_examples_sf_scope": structured.PROMPT_VERSION_V0_9_39_DROP_EXAMPLES_SF_SCOPE,
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
    if checks["drop_scaffold"]["has_scaffold"] or checks["drop_scaffold"]["n_rules"] != 79:
        raise RuntimeError("drop_scaffold contract drifted")
    if checks["drop_examples"]["n_examples"] != 0 or checks["drop_examples"]["n_rules"] != 83:
        raise RuntimeError("drop_examples contract drifted")
    if checks["drop_encoding"]["n_rules"] != 54:
        raise RuntimeError("drop_encoding contract drifted")
    if checks["drop_scope"]["n_rules"] != 58:
        raise RuntimeError("drop_scope contract drifted")
    if (
        checks["drop_scaffold_examples"]["has_scaffold"]
        or checks["drop_scaffold_examples"]["n_examples"] != 0
        or checks["drop_scaffold_examples"]["n_rules"] != 79
    ):
        raise RuntimeError("drop_scaffold_examples contract drifted")
    if (
        checks["drop_scaffold_examples_encoding"]["has_scaffold"]
        or checks["drop_scaffold_examples_encoding"]["n_examples"] != 0
        or checks["drop_scaffold_examples_encoding"]["n_rules"] != 50
    ):
        raise RuntimeError("drop_scaffold_examples_encoding contract drifted")
    if checks["drop_scope_sf_refuse"]["n_rules"] != 76:
        raise RuntimeError("drop_scope_sf_refuse contract drifted")
    if checks["drop_scope_sf_keep"]["n_rules"] != 79:
        raise RuntimeError("drop_scope_sf_keep contract drifted")
    if checks["drop_scope_diagnosis"]["n_rules"] != 76:
        raise RuntimeError("drop_scope_diagnosis contract drifted")
    if checks["drop_scope_rx_ix"]["n_rules"] != 76:
        raise RuntimeError("drop_scope_rx_ix contract drifted")
    if (
        checks["drop_encoding_non_sf"]["n_rules"] != 67
        or checks["drop_encoding_non_sf"]["n_examples"] != 49
    ):
        raise RuntimeError("drop_encoding_non_sf contract drifted")
    if (
        checks["drop_examples_non_sf"]["n_examples"] != 23
        or checks["drop_examples_non_sf"]["n_rules"] != 83
    ):
        raise RuntimeError("drop_examples_non_sf contract drifted")
    if (
        checks["drop_examples_sf_encoding"]["n_examples"] != 36
        or checks["drop_examples_sf_encoding"]["n_rules"] != 83
    ):
        raise RuntimeError("drop_examples_sf_encoding contract drifted")
    if (
        checks["drop_examples_sf_scope"]["n_examples"] != 39
        or checks["drop_examples_sf_scope"]["n_rules"] != 83
    ):
        raise RuntimeError("drop_examples_sf_scope contract drifted")
    if (
        checks["drop_encoding_non_sf_all_examples"]["n_examples"] != 0
        or checks["drop_encoding_non_sf_all_examples"]["n_rules"] != 67
        or not checks["drop_encoding_non_sf_all_examples"]["has_scaffold"]
    ):
        raise RuntimeError("drop_encoding_non_sf_all_examples contract drifted")
    return {
        "ok": True,
        "default_prompt_version": structured.PROMPT_VERSION,
        "letter_ids": list(v13.FROZEN_IDS),
        "protocol": PROTOCOL,
        "arms": checks,
    }


def check_study(*, overwrite: bool = False) -> dict[str, Any]:
    payload = verify_payload()
    scored = run_study(arms=(), live=False, overwrite=overwrite)
    return {**payload, **scored, "model_calls": 0}


def run_study(
    *,
    arms: Sequence[str],
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
    api_base: str | None = None,
) -> dict[str, Any]:
    verify_payload()
    letters = _letters()
    _select_study(arms)
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    scored: dict[str, dict[str, Any]] = {}
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        v10_run.ESCALATION_REASON = (
            "Predeclared Luna-only ExECT v0.9.24 leave-one-out prune under " + PROTOCOL
        )
        v10_run._arm_assembly = _patched_arm_assembly
        scored["v0924_head"] = v13._run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=overwrite,
            progress_every=progress_every,
            api_base=api_base,
        )
        if live:
            for arm in arms:
                scored[arm] = v13._run_enriched_arm(
                    slug=arm,
                    prompt_version=ARM_VERSIONS[arm],
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

    control = scored["v0924_head"]
    previous = _load_previous_artifact()
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.v0924_prompt_ablation_luna_dev20.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_count": 20,
        "letter_ids": list(v13.FROZEN_IDS),
        "contamination_letters": list(CONTAMINATION_LETTERS),
        "repair_policy": {
            "diagnosis_policy_variant": "default",
            "prescription_policy_variant": "default",
        },
        "started_utc": previous.get("started_utc", started),
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": True if previous.get("live") or live else live,
        "model_calls": int(previous.get("model_calls") or 0) + (20 * len(arms) if live else 0),
        "default_prompt_version": structured.PROMPT_VERSION,
        "requested_arms": list(dict.fromkeys([*previous.get("requested_arms", []), *arms])),
        "arms": {
            **previous.get("arms", {}),
            **{name: payload["summary"] for name, payload in scored.items()},
        },
        "comparison": dict(previous.get("comparison", {})),
        "decision": dict(previous.get("decision", {})),
        "claim_boundary": _claim_boundary(),
    }
    for arm in arms:
        versus = v13._compare_pair(control, scored[arm], letters)
        artifact["comparison"][f"{arm}_minus_v0924_head"] = versus
        hybrid = versus["surfaces"]["hybrid"]
        failures = v13.topology_failures(hybrid)
        artifact["decision"][arm] = {
            "status": "scored" if live else "live_not_run",
            "verdict": (
                "load_bearing"
                if failures
                else "low_value"
                if live
                else None
            ),
            "failures": failures,
            "headline_f1_delta": hybrid["headline_f1_delta"],
            "family_f1_delta": hybrid["family_f1_delta"],
            "four_family_letter_exact_net": hybrid["four_family_letter_exact_net"],
        }
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if _should_write_stub_report():
        REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": out.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(),
        "live": live,
        "model_calls": artifact["model_calls"],
        "decision": artifact["decision"],
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
    if any(arm in CHEAP_STACK_ARMS for arm in arms):
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
    frozen = set(v13.FROZEN_IDS)
    letters = [
        letter for letter in load_letters_for_split("dev") if letter.letter_id in frozen
    ]
    letters.sort(key=lambda item: item.letter_id)
    if [letter.letter_id for letter in letters] != sorted(v13.FROZEN_IDS):
        raise RuntimeError("the frozen v13-v19 20-letter sample is unavailable or changed")
    return letters


def _patched_arm_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
    cfg = v13._ORIGINAL_ARM_ASSEMBLY(slug, structured_path, sf_final_path)
    return replace(
        cfg,
        candidate_id=f"exectv2_v0924_ablation_luna_dev20_{slug}",
        split="dev",
        row_count=20,
        claim_boundary=_claim_boundary(),
    )


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
