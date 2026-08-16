"""Luna-only ExECT v17 request-shape study on the frozen 20-letter dev20 sample.

``check`` verifies the v17 rendered request and scores the no-call controls.
``run --live`` runs exactly one 20-letter Luna arm when explicitly requested.
"""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
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
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v17_luna_dev20_20260815"
V16_STRUCTURED = (
    REPO_ROOT
    / "experiments/exectv2_v16_rules_and_shapes_luna_dev140_20260815/v16_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v17_request_shape_luna_dev20_protocol_2026-08-15.md"
)
REPORT_PATH = (
    REPO_ROOT
    / "docs/research/exectv2/structured_prompt_v17_request_shape_luna_dev20_2026-08-15.md"
)
MODEL = "openai/gpt-5.6-luna"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check_parser = sub.add_parser(
        "check", help="Verify v17 request shape and score no-call controls."
    )
    check_parser.add_argument("--overwrite", action="store_true")
    run_parser = sub.add_parser("run", help="Score controls; live only with --live")
    run_parser.add_argument(
        "--live", action="store_true", help="Make exactly 20 Luna calls."
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


def _letters() -> list[Any]:
    frozen = set(v13.FROZEN_IDS)
    letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in frozen]
    letters.sort(key=lambda item: item.letter_id)
    if [letter.letter_id for letter in letters] != sorted(v13.FROZEN_IDS):
        raise RuntimeError("the frozen v13-v15 20-letter sample is unavailable or changed")
    return letters


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload_str = structured.build_prompt_input(
        letter, prompt_version=structured.PROMPT_VERSION_V17
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
        raise RuntimeError(f"v17 top-level order drifted: {list(payload)}")
    if "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError("v17 leaked research metadata into the model-facing payload")
    if len(payload["worked_examples"]) != 8:
        raise RuntimeError("v17 must retain exactly the eight v16 shape examples")
    if set(payload["output_schema"]) != {
        "clinical_events",
        "patient_history",
        "medication_history",
    }:
        raise RuntimeError("v17 output schema does not contain the three declared fields")
    instructions = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    ).lower()
    for phrase in (
        "instead of diagnosis or seizurefrequency",
        "generic seizure with a real rate",
        "last-event zero",
        "instead of prescription",
        "not clinical_events or output mentions",
    ):
        if phrase not in instructions:
            raise RuntimeError(f"v17 annotation contract is missing: {phrase}")

    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=structured.PROMPT_VERSION_V17
    )
    messages = program.render_messages(prompt_input_json=payload_str)
    expected_system = (
        "Extract structured clinical events from the supplied clinical letter. "
        "Return the requested output fields exactly."
    )
    if messages[0] != {"role": "system", "content": expected_system}:
        raise RuntimeError("v17 did not render the minimal system message")
    user_content = str(messages[1]["content"])
    if user_content.count(payload_str) != 1:
        raise RuntimeError("v17 rendered payload more than once or not at all")
    if "prompt_version" in user_content or "letter_id" in user_content:
        raise RuntimeError("v17 rendered request contains hidden research metadata")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("v17 request verification changed the live default")
    return {
        "sample_letter_id": letter.letter_id,
        "prompt_version": structured.PROMPT_VERSION_V17,
        "default_prompt_version": structured.PROMPT_VERSION,
        "system_message": expected_system,
        "top_level_user_json_keys": expected_order,
        "user_message_sha256": hashlib.sha256(user_content.encode()).hexdigest(),
        "payload_sha256": hashlib.sha256(payload_str.encode()).hexdigest(),
        "payload_contains_prompt_version": "prompt_version" in payload,
        "payload_contains_letter_id": "letter_id" in payload,
        "worked_example_count": len(payload["worked_examples"]),
        "output_schema_keys": list(payload["output_schema"]),
    }


def check(*, overwrite: bool = False) -> dict[str, Any]:
    request_shape = verify_payload()
    result = run_study(live=False, overwrite=overwrite)
    return {**result, "request_shape": request_shape, "model_calls": 0}


def run_study(
    *,
    live: bool,
    overwrite: bool = False,
    progress_every: int = 1,
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
        v10_run.ESCALATION_REASON = "Predeclared Luna-only ExECT v17 request-shape study under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_v17_luna_dev20_{slug}",
                split="dev",
                row_count=20,
                claim_boundary="ExECTv2 Luna v17 request-shape study on the frozen 20-letter dev20 sample.",
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
                slug="v17_live",
                prompt_version=structured.PROMPT_VERSION_V17,
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

    _add_sink_summary(control, STUDY_DIR / "v0924_head/structured.jsonl")
    _add_sink_summary(mechanism, STUDY_DIR / "v16_head/structured.jsonl")
    arms: dict[str, Any] = {
        "v0924_head": control["summary"],
        "v16_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v17_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_policy": "frozen development rows permitted; test60 sealed",
        "scorer": "four-family clinical_headline through unchanged HEAD assembly",
        "row_count": 20,
        "letter_ids": [letter.letter_id for letter in letters],
        "source_artifacts": {
            "v0924_structured": v13.V0924_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v16_structured": V16_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
        },
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v16_head": "saved_structured_no_call",
            "v17_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": 20 if live else 0,
        "default_prompt_version": structured.PROMPT_VERSION,
        "request_shape": request_shape,
        "arms": arms,
        "comparison": {
            "v16_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)
        },
        "claim_boundary": (
            "ExECTv2 Luna 20-letter development comparison of v17 request framing "
            "and diversion sinks through HEAD. Not holdout evidence, not a selected "
            "prompt, not a benchmark claim, and not a fill change."
        ),
    }
    if candidate is not None:
        _add_sink_summary(candidate, STUDY_DIR / "v17_live/structured.jsonl")
        arms["v17_live"] = candidate["summary"]
        versus_control = v13._compare_pair(control, candidate, letters)
        versus_mechanism = v13._compare_pair(mechanism, candidate, letters)
        artifact["comparison"]["v17_live_minus_v0924_head"] = versus_control
        artifact["comparison"]["v17_live_minus_v16_head"] = versus_mechanism
        artifact["row_observations"] = _row_observations(letters)
        artifact["decision"] = _decide(candidate, control, versus_control, versus_mechanism)
    else:
        artifact["decision"] = {
            "status": "live_not_run",
            "verdict": None,
            "failures": [],
            "rule": "Run one live 20-letter arm before deciding whether v17 survives.",
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


def _add_sink_summary(result: dict[str, Any], structured_path: Path) -> None:
    rows = v10_run._read_jsonl(structured_path)
    patient_kinds = Counter(
        str(item["kind"])
        for row in rows
        for item in row.get("patient_history", [])
    )
    medication_kinds = Counter(
        str(item["kind"])
        for row in rows
        for item in row.get("medication_history", [])
    )
    result["summary"].update(
        {
            "n_patient_history": sum(len(row.get("patient_history", [])) for row in rows),
            "patient_history_by_kind": dict(sorted(patient_kinds.items())),
            "n_medication_history": sum(len(row.get("medication_history", [])) for row in rows),
            "medication_history_by_kind": dict(sorted(medication_kinds.items())),
            "structured_rows_path": structured_path.relative_to(REPO_ROOT).as_posix(),
        }
    )


def _row_observations(letters: Sequence[Any]) -> list[dict[str, Any]]:
    by_arm: dict[str, dict[str, dict[str, Any]]] = {}
    for arm in ("v0924_head", "v16_head", "v17_live"):
        structured_rows = {
            str(row["letter_id"]): row
            for row in v10_run._read_jsonl(STUDY_DIR / arm / "structured.jsonl")
        }
        family_rows = {
            str(row["letter_id"]): row
            for row in v10_run._read_jsonl(STUDY_DIR / arm / "letter_metrics.jsonl")
        }
        exact_by_letter: dict[str, dict[str, bool]] = {}
        for row in v10_run._read_jsonl(STUDY_DIR / arm / "letter_family.jsonl"):
            exact_by_letter.setdefault(str(row["letter_id"]), {})[str(row["family"])] = bool(
                row["hybrid_letter_exact"]
            )
        by_arm[arm] = {}
        for letter in letters:
            letter_id = letter.letter_id
            structured_row = structured_rows[letter_id]
            by_arm[arm][letter_id] = {
                "letter_id": letter_id,
                "raw_output": structured_row.get("raw_output", ""),
                "parse_errors": structured_row.get("parse_errors", []),
                "structured_events": structured_row.get("structured_events", []),
                "patient_history": structured_row.get("patient_history", []),
                "medication_history": structured_row.get("medication_history", []),
                "predicted_mentions": structured_row.get("predicted_mentions", []),
                "hybrid_family_exact": exact_by_letter[letter_id],
                "hybrid_four_family_exact": all(exact_by_letter[letter_id].values()),
                "letter_metric": family_rows.get(letter_id, {}),
            }
    observations: list[dict[str, Any]] = []
    for letter in letters:
        letter_id = letter.letter_id
        candidate = by_arm["v17_live"][letter_id]
        observations.append(
            {
                "letter_id": letter_id,
                "candidate": candidate,
                "versus_v0924": {
                    "hybrid_four_family_exact": by_arm["v0924_head"][letter_id][
                        "hybrid_four_family_exact"
                    ],
                    "changed_direction": _direction(
                        by_arm["v0924_head"][letter_id]["hybrid_four_family_exact"],
                        candidate["hybrid_four_family_exact"],
                    ),
                },
                "versus_v16": {
                    "hybrid_four_family_exact": by_arm["v16_head"][letter_id][
                        "hybrid_four_family_exact"
                    ],
                    "changed_direction": _direction(
                        by_arm["v16_head"][letter_id]["hybrid_four_family_exact"],
                        candidate["hybrid_four_family_exact"],
                    ),
                },
            }
        )
    return observations


def _direction(before: bool, after: bool) -> str:
    if after and not before:
        return "win"
    if before and not after:
        return "loss"
    return "same"


def _decide(
    candidate: Mapping[str, Any],
    control: Mapping[str, Any],
    versus_control: Mapping[str, Any],
    versus_mechanism: Mapping[str, Any],
) -> dict[str, Any]:
    failures = list(v13.topology_failures(versus_control["surfaces"]["hybrid"]))
    control_quality = control["summary"].get("quality", {})
    candidate_quality = candidate["summary"].get("quality", {})
    for key in ("schema", "parse"):
        if int(candidate_quality.get(key, 0)) > int(control_quality.get(key, 0)):
            failures.append(f"{key} failures worsened from {control_quality.get(key, 0)} to {candidate_quality.get(key, 0)}")
    return {
        "status": "scored",
        "verdict": "preserve_v17_for_next_batch" if not failures else "revise_v17",
        "failures": failures,
        "hybrid_vs_v0924_head": versus_control["surfaces"]["hybrid"],
        "hybrid_vs_v16_head": versus_mechanism["surfaces"]["hybrid"],
        "rule": (
            "Preserve for a separately declared next development batch only if "
            "headline/family/exactness regression thresholds and parse/schema "
            "behavior remain acceptable. This does not promote v17."
        ),
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v16_head"]
    cand = artifact["arms"].get("v17_live")
    live = bool(artifact["live"])
    if not live or cand is None:
        return f"""# Luna `dev20` test of ExECT v17 request shape

Date: 2026-08-15
Status: no-call check complete; live arm not run
Protocol: [{PROTOCOL.split('/')[-1]}]({PROTOCOL.split('/')[-1]})
Model: `{artifact['model']}`
Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched

## Purpose

v17 changes request framing and adds unscored `patient_history` and
`medication_history` sinks while retaining v16's rules and eight compact
worked cases. The live arm remains a separately authorized 20-call batch.

## No-call controls through HEAD

| Arm | raw F1 | hybrid F1 | hybrid exact | history sink | medication sink |
| :--- | ---: | ---: | ---: | ---: | ---: |
| v0.9.24 | {ctrl['raw_headline_f1']:.4f} | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/20 | {ctrl.get('n_patient_history', 0)} | {ctrl.get('n_medication_history', 0)} |
| v16 | {mech['raw_headline_f1']:.4f} | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_four_family_letter_exact']}/20 | {mech.get('n_patient_history', 0)} | {mech.get('n_medication_history', 0)} |

## Request audit

- System message: `{artifact['request_shape']['system_message']}`
- User JSON order: `{', '.join(artifact['request_shape']['top_level_user_json_keys'])}`
- Model-facing prompt version and letter ID: absent
- Worked examples: {artifact['request_shape']['worked_example_count']}

## Boundary

No model calls were made. This does not promote v17, change the default, or
authorize a broader development run.
"""
    vs_control = artifact["comparison"]["v17_live_minus_v0924_head"]["surfaces"]["hybrid"]
    vs_mechanism = artifact["comparison"]["v17_live_minus_v16_head"]["surfaces"]["hybrid"]
    return f"""# Luna `dev20` test of ExECT v17 request shape

Date: 2026-08-15
Status: complete; {artifact['decision']['verdict']}
Protocol: [{PROTOCOL.split('/')[-1]}]({PROTOCOL.split('/')[-1]})
Model: `{artifact['model']}`
Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched

## Verdict

**{artifact['decision']['verdict']}**. This is one development batch, not a
promotion, benchmark claim, or fill change. Failures: {', '.join(artifact['decision']['failures']) or 'none'}.

## Hybrid headline comparison

| Arm | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | exact |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| v0.9.24 | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['Diagnosis']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_family_f1']['Prescription']:.4f} | {ctrl['hybrid_family_f1']['Investigations']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/20 |
| v16 | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['Diagnosis']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_family_f1']['Prescription']:.4f} | {mech['hybrid_family_f1']['Investigations']:.4f} | {mech['hybrid_four_family_letter_exact']}/20 |
| v17 | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['Diagnosis']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_family_f1']['Prescription']:.4f} | {cand['hybrid_family_f1']['Investigations']:.4f} | {cand['hybrid_four_family_letter_exact']}/20 |

v17 minus v0.9.24 hybrid headline: {vs_control['headline_f1_delta']:+.4f};
v17 minus v16: {vs_mechanism['headline_f1_delta']:+.4f}.

## Diversion sinks

| Arm | patient_history | medication_history | patient kinds | medication kinds |
| :--- | ---: | ---: | :--- | :--- |
| v0.9.24 | {ctrl.get('n_patient_history', 0)} | {ctrl.get('n_medication_history', 0)} | {ctrl.get('patient_history_by_kind', {})} | {ctrl.get('medication_history_by_kind', {})} |
| v16 | {mech.get('n_patient_history', 0)} | {mech.get('n_medication_history', 0)} | {mech.get('patient_history_by_kind', {})} | {mech.get('medication_history_by_kind', {})} |
| v17 | {cand.get('n_patient_history', 0)} | {cand.get('n_medication_history', 0)} | {cand.get('patient_history_by_kind', {})} | {cand.get('medication_history_by_kind', {})} |

## Request audit

- System message: `{artifact['request_shape']['system_message']}`
- User JSON order: `{', '.join(artifact['request_shape']['top_level_user_json_keys'])}`
- Model-facing prompt version and letter ID: absent
- Worked examples: {artifact['request_shape']['worked_example_count']}
- Per-letter raw output, parse events, sink entries, projected mentions, and
  comparator direction are retained in `comparison.json`.

## Boundary

Exactly 20 live Luna calls. No `test60` access. v17 remains unselected and the
live default remains v0.9.24.
"""


if __name__ == "__main__":
    main()
