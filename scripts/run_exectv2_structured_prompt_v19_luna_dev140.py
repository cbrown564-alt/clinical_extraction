"""Luna-only ExECT v19 transfer study on all 140 development letters."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
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
from scripts import run_exectv2_structured_prompt_v17_luna_dev20 as v17_run

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815"
V16_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/v16_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v19_historical_guard_luna_dev140_protocol_2026-08-15.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "docs/research/exectv2/structured_prompt_v19_historical_guard_luna_dev140_2026-08-15.md"
)
MODEL = "openai/gpt-5.6-luna"
EXPECTED_N = 140


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Verify v19 request shape and score controls.")
    check.add_argument("--overwrite", action="store_true")
    run = sub.add_parser("run", help="Score controls; live only with --live")
    run.add_argument("--live", action="store_true", help="Make exactly 140 Luna calls.")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--progress-every", type=int, default=5)
    run.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        print(json.dumps(check_study(overwrite=args.overwrite), indent=2, sort_keys=True))
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
    payload_str = structured.build_prompt_input(
        letter, prompt_version=structured.PROMPT_VERSION_V19
    )
    payload = json.loads(payload_str)
    expected_order = [
        "task",
        "output_schema",
        "family_guidance",
        "attribute_vocabulary",
        "clinical_rules",
        "worked_examples",
        "letter_text",
    ]
    if list(payload) != expected_order:
        raise RuntimeError(f"v19 top-level order drifted: {list(payload)}")
    if "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError("v19 leaked research metadata into the model-facing payload")
    instructions = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    ).lower()
    for phrase in (
        "current means present, ongoing, or described as happening now",
        "dated, historical, or past-only event stays in patient_history",
    ):
        if phrase not in instructions:
            raise RuntimeError(f"v19 contract is missing: {phrase}")
    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=structured.PROMPT_VERSION_V19
    )
    messages = program.render_messages(prompt_input_json=payload_str)
    system_message = (
        "Extract structured clinical events from the supplied clinical letter. "
        "Return the requested output fields exactly."
    )
    user_content = str(messages[1]["content"])
    if messages[0] != {"role": "system", "content": system_message}:
        raise RuntimeError("v19 did not retain the minimal system message")
    if user_content.count(payload_str) != 1:
        raise RuntimeError("v19 rendered payload more than once or not at all")
    if "prompt_version" in user_content or "letter_id" in user_content:
        raise RuntimeError("v19 rendered request contains hidden research metadata")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("v19 verification changed the live default")
    return {
        "sample_letter_id": letter.letter_id,
        "prompt_version": structured.PROMPT_VERSION_V19,
        "default_prompt_version": structured.PROMPT_VERSION,
        "system_message": system_message,
        "top_level_user_json_keys": expected_order,
        "user_message_sha256": hashlib.sha256(user_content.encode()).hexdigest(),
        "payload_sha256": hashlib.sha256(payload_str.encode()).hexdigest(),
        "worked_example_count": len(payload["worked_examples"]),
        "clinical_rule_count": len(payload["clinical_rules"]),
    }


def check_study(*, overwrite: bool = False) -> dict[str, Any]:
    request_shape = verify_payload()
    result = run_study(live=False, overwrite=overwrite)
    return {**result, "request_shape": request_shape, "model_calls": 0}


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 5,
    api_base: str | None = None,
) -> dict[str, Any]:
    request_shape = verify_payload()
    if not V16_STRUCTURED.exists():
        raise FileNotFoundError(f"missing saved v16 structured rows: {V16_STRUCTURED}")
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = "Predeclared Luna-only ExECT v19 historical-guard dev140 study under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_v19_luna_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="ExECTv2 Luna v19 historical-guard transfer study on dev140.",
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
        v10_run.CONTROL_STRUCTURED = V16_STRUCTURED
        mechanism = v13._run_enriched_arm(
            slug="v16_head",
            prompt_version=structured.PROMPT_VERSION_V16,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate: dict[str, Any] | None = None
        if live:
            candidate = v13._run_enriched_arm(
                slug="v19_live",
                prompt_version=structured.PROMPT_VERSION_V19,
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

    for result, slug in (
        (control, "v0924_head"),
        (mechanism, "v16_head"),
    ):
        v17_run._add_sink_summary(result, STUDY_DIR / slug / "structured.jsonl")
    arms: dict[str, Any] = {
        "v0924_head": control["summary"],
        "v16_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v19_luna_dev140.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_policy": "development rows permitted; test60 sealed",
        "scorer": "four-family clinical_headline through unchanged HEAD assembly",
        "row_count": EXPECTED_N,
        "letter_ids": [letter.letter_id for letter in letters],
        "source_artifacts": {
            "v0924_structured": v13.V0924_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v16_structured": V16_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v19_dev20": "experiments/exectv2_structured_prompt_v19_luna_dev20_20260815/comparison.json",
        },
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v16_head": "saved_structured_no_call",
            "v19_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": EXPECTED_N if live else 0,
        "default_prompt_version": structured.PROMPT_VERSION,
        "request_shape": request_shape,
        "arms": arms,
        "comparison": {
            "v16_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)
        },
        "claim_boundary": (
            "ExECTv2 Luna v19 development transfer comparison on dev140. "
            "Not holdout evidence, not a selected prompt, not a benchmark claim, "
            "and not a fill change."
        ),
    }
    if candidate is not None:
        v17_run._add_sink_summary(candidate, STUDY_DIR / "v19_live/structured.jsonl")
        arms["v19_live"] = candidate["summary"]
        versus_control = v13._compare_pair(control, candidate, letters)
        versus_mechanism = v13._compare_pair(mechanism, candidate, letters)
        artifact["comparison"]["v19_live_minus_v0924_head"] = versus_control
        artifact["comparison"]["v19_live_minus_v16_head"] = versus_mechanism
        artifact["changed_rows"] = _changed_rows()
        artifact["decision"] = _decide(candidate, mechanism, versus_control, versus_mechanism)
    else:
        artifact["decision"] = {
            "status": "live_not_run",
            "verdict": None,
            "failures": [],
            "rule": "Run one live dev140 arm before deciding whether v19 transfers.",
        }

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


def _changed_rows() -> dict[str, Any]:
    def family_map(slug: str) -> dict[str, dict[str, bool]]:
        out: dict[str, dict[str, bool]] = {}
        for row in v10_run._read_jsonl(STUDY_DIR / slug / "letter_family.jsonl"):
            out.setdefault(str(row["letter_id"]), {})[str(row["family"])] = bool(
                row["hybrid_letter_exact"]
            )
        return out

    baseline = family_map("v16_head")
    candidate = family_map("v19_live")
    by_direction: dict[str, list[dict[str, Any]]] = {"win": [], "loss": []}
    for letter_id in sorted(candidate):
        for family in sorted(candidate[letter_id]):
            before = baseline[letter_id][family]
            after = candidate[letter_id][family]
            if before == after:
                continue
            direction = "win" if after else "loss"
            by_direction[direction].append(
                {
                    "letter_id": letter_id,
                    "family": family,
                    "before": before,
                    "after": after,
                }
            )
    return {
        "versus_v16": by_direction,
        "counts": {direction: len(rows) for direction, rows in by_direction.items()},
    }


def _decide(
    candidate: Mapping[str, Any],
    mechanism: Mapping[str, Any],
    versus_control: Mapping[str, Any],
    versus_mechanism: Mapping[str, Any],
) -> dict[str, Any]:
    failures = list(v13.topology_failures(versus_mechanism["surfaces"]["hybrid"]))
    before_quality = mechanism["summary"].get("quality", {})
    after_quality = candidate["summary"].get("quality", {})
    for key in ("schema", "parse"):
        if int(after_quality.get(key, 0)) > int(before_quality.get(key, 0)):
            failures.append(f"{key} failures worsened from {before_quality.get(key, 0)} to {after_quality.get(key, 0)}")
    return {
        "status": "scored",
        "verdict": "preserve_v19_dev140" if not failures else "revise_v19_before_promotion",
        "failures": failures,
        "hybrid_vs_v0924_head": versus_control["surfaces"]["hybrid"],
        "hybrid_vs_v16_head": versus_mechanism["surfaces"]["hybrid"],
        "rule": (
            "Preserve v19 as a development candidate only if parse/schema and "
            "transfer thresholds remain acceptable. This does not select a fill."
        ),
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v16_head"]
    cand = artifact["arms"].get("v19_live")
    if cand is None:
        return f"""# Luna `dev140` transfer test of ExECT v19

Date: 2026-08-15
Status: no-call check complete; live arm not run
Protocol: [{PROTOCOL.split('/')[-1]}]({PROTOCOL.split('/')[-1]})
Model: `{artifact['model']}`
Split: ExECT `dev140` (n=140); `test60` not touched

| Arm | hybrid F1 | exact | SF F1 |
| :--- | ---: | ---: | ---: |
| v0.9.24 | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/140 | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} |
| v16 | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_four_family_letter_exact']}/140 | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} |

No model calls were made. v19 is not selected and the default remains v0.9.24.
"""
    delta = artifact["comparison"]["v19_live_minus_v0924_head"]["surfaces"]["hybrid"]
    delta_v16 = artifact["comparison"]["v19_live_minus_v16_head"]["surfaces"]["hybrid"]
    return f"""# Luna `dev140` transfer test of ExECT v19

Date: 2026-08-15
Status: complete; {artifact['decision']['verdict']}
Protocol: [{PROTOCOL.split('/')[-1]}]({PROTOCOL.split('/')[-1]})
Model: `{artifact['model']}`
Split: ExECT `dev140` (n=140); `test60` not touched

## Hybrid comparison

| Arm | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | exact |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| v0.9.24 | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['Diagnosis']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_family_f1']['Prescription']:.4f} | {ctrl['hybrid_family_f1']['Investigations']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/140 |
| v16 | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['Diagnosis']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_family_f1']['Prescription']:.4f} | {mech['hybrid_family_f1']['Investigations']:.4f} | {mech['hybrid_four_family_letter_exact']}/140 |
| v19 | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['Diagnosis']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_family_f1']['Prescription']:.4f} | {cand['hybrid_family_f1']['Investigations']:.4f} | {cand['hybrid_four_family_letter_exact']}/140 |

v19 minus v0.9.24 headline: {delta['headline_f1_delta']:+.4f}; SF: {delta['family_f1_delta']['SeizureFrequency']:+.4f}.
v19 minus v16 headline: {delta_v16['headline_f1_delta']:+.4f}; SF: {delta_v16['family_f1_delta']['SeizureFrequency']:+.4f}.

## Quality and changed rows

| Arm | parse | schema | patient_history | medication_history |
| :--- | ---: | ---: | ---: | ---: |
| v0.9.24 | {ctrl['quality']['parse']} | {ctrl['quality']['schema']} | {ctrl.get('n_patient_history', 0)} | {ctrl.get('n_medication_history', 0)} |
| v16 | {mech['quality']['parse']} | {mech['quality']['schema']} | {mech.get('n_patient_history', 0)} | {mech.get('n_medication_history', 0)} |
| v19 | {cand['quality']['parse']} | {cand['quality']['schema']} | {cand.get('n_patient_history', 0)} | {cand.get('n_medication_history', 0)} |

v19 changed rows versus v16: {artifact['changed_rows']['counts']}.
Per-letter raw outputs and final rows remain in the three arm directories.

Boundary: exactly 140 live Luna calls; `test60` untouched; default remains v0.9.24.
"""


if __name__ == "__main__":
    main()
