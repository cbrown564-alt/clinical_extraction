"""Luna-only ExECT v14 SF-role study on the frozen v10 dev20 sample.

``check`` builds the v14 payload and scores the no-call arms.
``run --live`` is 20 Luna calls and is not authorized by the protocol
alone.
"""

# ruff: noqa: E501

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
    live = bool(artifact["live"])
    decision = artifact["decision"]
    sample = artifact["sample"]
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v13_head"]
    cand = artifact["arms"].get("v14_live")
    bands = "\n".join(
        f"- **{band}:** {', '.join(ids)}" for band, ids in sample["bands"].items()
    )
    if not live:
        status = "no-call check complete; live arm not run"
        verdict = (
            "Live Luna is not authorized by the protocol alone. "
            "The two no-call arms are scored through HEAD."
        )
        live_tables = (
            "Live arm not run. `v14_live` scores, the topology decision, "
            "and paired deltas versus `v0924_head` / `v13_head` are absent."
        )
    else:
        status = f"complete; {decision['verdict']}"
        verdict = (
            f"**{decision['verdict']}.** This is not a promotion and not a "
            "benchmark score. Failures: "
            + (", ".join(decision.get("failures") or ["none"]) + ".")
        )
        vs_ctrl = artifact["comparison"]["v14_live_minus_v0924_head"]
        vs_mech = artifact["comparison"]["v14_live_minus_v13_head"]
        raw = vs_ctrl["surfaces"]["raw"]
        hybrid = vs_ctrl["surfaces"]["hybrid"]
        hybrid_v13 = vs_mech["surfaces"]["hybrid"]
        live_tables = f"""## Headline F1 on the 20-letter pool

| Surface | v0.9.24 HEAD | v13 HEAD | v14 live | v14 − v0.9.24 | v14 − v13 |
| :--- | ---: | ---: | ---: | ---: | ---: |
| raw | {ctrl["raw_headline_f1"]:.4f} | {mech["raw_headline_f1"]:.4f} | {cand["raw_headline_f1"]:.4f} | {raw["headline_f1_delta"]:+.4f} | {vs_mech["surfaces"]["raw"]["headline_f1_delta"]:+.4f} |
| hybrid | {ctrl["hybrid_headline_f1"]:.4f} | {mech["hybrid_headline_f1"]:.4f} | {cand["hybrid_headline_f1"]:.4f} | {hybrid["headline_f1_delta"]:+.4f} | {hybrid_v13["headline_f1_delta"]:+.4f} |

## Family F1 delta (hybrid)

| Family | v14 − v0.9.24 | v14 − v13 |
| :--- | ---: | ---: |
| Diagnosis | {hybrid["family_f1_delta"]["Diagnosis"]:+.4f} | {hybrid_v13["family_f1_delta"]["Diagnosis"]:+.4f} |
| SeizureFrequency | {hybrid["family_f1_delta"]["SeizureFrequency"]:+.4f} | {hybrid_v13["family_f1_delta"]["SeizureFrequency"]:+.4f} |
| Prescription | {hybrid["family_f1_delta"]["Prescription"]:+.4f} | {hybrid_v13["family_f1_delta"]["Prescription"]:+.4f} |
| Investigations | {hybrid["family_f1_delta"]["Investigations"]:+.4f} | {hybrid_v13["family_f1_delta"]["Investigations"]:+.4f} |

## Four-family letter-exact wins / losses (v14 vs v0.9.24)

| Surface | wins | losses | net |
| :--- | ---: | ---: | ---: |
| raw | {raw["four_family_letter_exact_wins"]} | {raw["four_family_letter_exact_losses"]} | {raw["four_family_letter_exact_net"]} |
| hybrid | {hybrid["four_family_letter_exact_wins"]} | {hybrid["four_family_letter_exact_losses"]} | {hybrid["four_family_letter_exact_net"]} |

## SF encoding rewrites on model NumberOfSeizures

| Arm | several | few | range split | interval → 1 |
| :--- | ---: | ---: | ---: | ---: |
| v0.9.24 HEAD | {ctrl["sf_encoding_rewrites"]["several"]} | {ctrl["sf_encoding_rewrites"]["few"]} | {ctrl["sf_encoding_rewrites"]["range_split"]} | {ctrl["sf_encoding_rewrites"]["interval_missing_1"]} |
| v13 HEAD | {mech["sf_encoding_rewrites"]["several"]} | {mech["sf_encoding_rewrites"]["few"]} | {mech["sf_encoding_rewrites"]["range_split"]} | {mech["sf_encoding_rewrites"]["interval_missing_1"]} |
| v14 live | {cand["sf_encoding_rewrites"]["several"]} | {cand["sf_encoding_rewrites"]["few"]} | {cand["sf_encoding_rewrites"]["range_split"]} | {cand["sf_encoding_rewrites"]["interval_missing_1"]} |
"""
    return f"""# Luna `dev20` test of ExECT v14 SF roles

Date: 2026-08-15
Status: {status}
Protocol: [structured_prompt_v14_luna_dev20_protocol_2026-08-15.md](structured_prompt_v14_luna_dev20_protocol_2026-08-15.md)
Model: `{artifact["model"]}`
Sample: frozen 20 letters from ExECT `dev140` (same IDs as v10–v13); `test60` not touched

## Verdict

{verdict}

This study cannot promote v14 or change a fill.

## Frozen sample

Copied from the v10 freeze. Lowest `letter_id` within each band;
`EA0133` forced into hard. Not redrawn after scoring.

{bands}

Letter IDs: {", ".join(sample["letter_ids"])}

## Conditions

| Item | Value |
| :--- | :--- |
| Control | no-call reuse of the 15 Jul Luna `v0.9.24` structured sidecar through HEAD |
| Mechanism | no-call reuse of the saved v13 `dev20` structured sidecar through HEAD |
| Candidate | {"live Luna, `exectv2_hybrid_key_family_event_ledger_v14`, then HEAD" if live else "not run"} |
| Profile | `full` |
| Repair | default / default |
| Scorer | four-family `clinical_headline` unit keys; family-local letter exactness |
| Gold at prompt-build time | forbidden |
| Holdout | not touched |
| Default `PROMPT_VERSION` after run | `{artifact["default_prompt_version"]}` |

## No-call HEAD baselines on this cut

| Arm | raw F1 | hybrid F1 | hybrid four-family exact | SF several→N | SF few→N |
| :--- | ---: | ---: | ---: | ---: | ---: |
| v0924_head | {ctrl["raw_headline_f1"]:.4f} | {ctrl["hybrid_headline_f1"]:.4f} | {ctrl["hybrid_four_family_letter_exact"]}/20 | {ctrl["sf_encoding_rewrites"]["several"]} | {ctrl["sf_encoding_rewrites"]["few"]} |
| v13_head | {mech["raw_headline_f1"]:.4f} | {mech["hybrid_headline_f1"]:.4f} | {mech["hybrid_four_family_letter_exact"]}/20 | {mech["sf_encoding_rewrites"]["several"]} | {mech["sf_encoding_rewrites"]["few"]} |

{live_tables}

## Quality counts

| Arm | schema | parse | illegal enum | inexact evidence |
| :--- | ---: | ---: | ---: | ---: |
| v0924_head | {ctrl["quality"]["schema"]} | {ctrl["quality"]["parse"]} | {ctrl["quality"]["illegal_enum"]} | {ctrl["quality"]["inexact_evidence"]} |
| v13_head | {mech["quality"]["schema"]} | {mech["quality"]["parse"]} | {mech["quality"]["illegal_enum"]} | {mech["quality"]["inexact_evidence"]} |{"" if cand is None else chr(10) + f"| v14_live | {cand['quality']['schema']} | {cand['quality']['parse']} | {cand['quality']['illegal_enum']} | {cand['quality']['inexact_evidence']} |"}

## Boundary

Not `test60`. Not a selected prompt. Not a six-model claim. Parser, evidence
gate, attribute gate, and the Phase 3–5 hybrid codebook stayed at HEAD; only
the model-facing JSON changes on the v14 arm. v14 is not `PROMPT_VERSION`.
"""


if __name__ == "__main__":
    main()
