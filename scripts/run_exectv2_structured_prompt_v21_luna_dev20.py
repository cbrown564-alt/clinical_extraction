"""Luna-only ExECT v21 clause-head-only study on frozen dev20."""

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
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v21_luna_dev20_20260816"
V19_STRUCTURED = REPO_ROOT / (
    "experiments/exectv2_structured_prompt_v19_luna_dev20_20260815/"
    "v19_live/structured.jsonl"
)
PROTOCOL = "docs/research/exectv2/structured_prompt_v21_clause_head_only_luna_dev20_protocol_2026-08-16.md"
REPORT_PATH = REPO_ROOT / "docs/research/exectv2/structured_prompt_v21_clause_head_only_luna_dev20_2026-08-16.md"
MODEL = "openai/gpt-5.6-luna"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--overwrite", action="store_true")
    run = sub.add_parser("run")
    run.add_argument("--live", action="store_true")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--progress-every", type=int, default=1)
    run.add_argument("--api-base")
    args = parser.parse_args(argv)
    if args.command == "check":
        result = check_study(overwrite=args.overwrite)
    else:
        result = run_study(
            live=args.live,
            overwrite=args.overwrite,
            progress_every=args.progress_every,
            api_base=args.api_base,
        )
    print(json.dumps(result, indent=2, sort_keys=True))


def _letters() -> list[ExectLetter]:
    frozen = set(v13.FROZEN_IDS)
    letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in frozen]
    letters.sort(key=lambda letter: letter.letter_id)
    if [letter.letter_id for letter in letters] != sorted(v13.FROZEN_IDS):
        raise RuntimeError("the frozen v13-v21 20-letter sample is unavailable or changed")
    return letters


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload_str = structured.build_prompt_input(letter, prompt_version=structured.PROMPT_VERSION_V21)
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
        raise RuntimeError(f"v21 top-level order drifted: {list(payload)}")
    if "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError("v21 leaked research metadata into the model request")
    instructions = json.dumps({key: value for key, value in payload.items() if key != "letter_text"}).lower()
    if "noun phrase it modifies in that clause" not in instructions:
        raise RuntimeError("v21 clause-head rule is missing")
    if "use that exact source phrase as the seizurefrequency anchor" in instructions:
        raise RuntimeError("v21 accidentally includes v20's explicit seizure-free anchor rule")
    program = structured.DspyKeyEntitiesStructuredExtractor(prompt_version=structured.PROMPT_VERSION_V21)
    messages = program.render_messages(prompt_input_json=payload_str)
    system_message = "Extract structured clinical events from the supplied clinical letter. Return the requested output fields exactly."
    user_content = str(messages[1]["content"])
    if messages[0] != {"role": "system", "content": system_message}:
        raise RuntimeError("v21 did not retain the minimal system message")
    if user_content.count(payload_str) != 1:
        raise RuntimeError("v21 rendered the payload more than once or not at all")
    if "prompt_version" in user_content or "letter_id" in user_content:
        raise RuntimeError("v21 rendered hidden research metadata")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("v21 verification changed the live default")
    return {
        "sample_letter_id": letter.letter_id,
        "prompt_version": structured.PROMPT_VERSION_V21,
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


def run_study(*, live: bool, overwrite: bool = False, progress_every: int = 1, api_base: str | None = None) -> dict[str, Any]:
    request_shape = verify_payload()
    if not V19_STRUCTURED.exists():
        raise FileNotFoundError(f"missing saved v19 structured rows: {V19_STRUCTURED}")
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = "Predeclared Luna-only ExECT v21 clause-head-only study under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_v21_luna_dev20_{slug}",
                split="dev",
                row_count=20,
                claim_boundary="ExECTv2 Luna v21 clause-head-only study on frozen dev20.",
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
        v10_run.CONTROL_STRUCTURED = V19_STRUCTURED
        mechanism = v13._run_enriched_arm(
            slug="v19_head",
            prompt_version=structured.PROMPT_VERSION_V19,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=progress_every,
            api_base=api_base,
        )
        candidate = None
        if live:
            candidate = v13._run_enriched_arm(
                slug="v21_live",
                prompt_version=structured.PROMPT_VERSION_V21,
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

    for result, slug in ((control, "v0924_head"), (mechanism, "v19_head")):
        v17_run._add_sink_summary(result, STUDY_DIR / slug / "structured.jsonl")
    arms: dict[str, Any] = {"v0924_head": control["summary"], "v19_head": mechanism["summary"]}
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v21_luna_dev20.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_policy": "frozen development rows permitted; test60 sealed",
        "scorer": "four-family clinical_headline through unchanged HEAD assembly",
        "row_count": 20,
        "letter_ids": [letter.letter_id for letter in letters],
        "source_artifacts": {
            "v0924_structured": v13.V0924_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v19_structured": V19_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
        },
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v19_head": "saved_structured_no_call",
            "v21_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": 20 if live else 0,
        "default_prompt_version": structured.PROMPT_VERSION,
        "request_shape": request_shape,
        "arms": arms,
        "comparison": {"v19_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)},
        "claim_boundary": "ExECTv2 Luna 20-letter development comparison of v21 clause-head-only binding through HEAD. Not holdout evidence, not a selected prompt, not a benchmark claim, and not a fill change.",
    }
    if candidate is not None:
        v17_run._add_sink_summary(candidate, STUDY_DIR / "v21_live/structured.jsonl")
        arms["v21_live"] = candidate["summary"]
        delta = v13._compare_pair(mechanism, candidate, letters)
        artifact["comparison"]["v21_live_minus_v19_head"] = delta
        artifact["comparison"]["v21_live_minus_v0924_head"] = v13._compare_pair(control, candidate, letters)
        artifact["row_observations"] = _row_observations(letters)
        artifact["decision"] = _decision(candidate, mechanism, delta)
    else:
        artifact["decision"] = {"status": "live_not_run", "verdict": None, "failures": [], "rule": "Run one live 20-letter arm before deciding whether v21 survives."}
    out = STUDY_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(_render_report(artifact), encoding="utf-8")
    return {"artifact": out.relative_to(REPO_ROOT).as_posix(), "report": REPORT_PATH.relative_to(REPO_ROOT).as_posix(), "live": live, "model_calls": artifact["model_calls"], "decision": artifact["decision"]}


def _row_observations(letters: Sequence[ExectLetter]) -> list[dict[str, Any]]:
    arms: dict[str, dict[str, dict[str, Any]]] = {}
    for slug in ("v19_head", "v21_live"):
        rows = {str(row["letter_id"]): row for row in v10_run._read_jsonl(STUDY_DIR / slug / "structured.jsonl")}
        exact: dict[str, dict[str, bool]] = {}
        for row in v10_run._read_jsonl(STUDY_DIR / slug / "letter_family.jsonl"):
            exact.setdefault(str(row["letter_id"]), {})[str(row["family"])] = bool(row["hybrid_letter_exact"])
        arms[slug] = {}
        for letter in letters:
            row = rows[letter.letter_id]
            fam = exact[letter.letter_id]
            arms[slug][letter.letter_id] = {
                "letter_id": letter.letter_id,
                "raw_output": row.get("raw_output", ""),
                "parse_errors": row.get("parse_errors", []),
                "structured_events": row.get("structured_events", []),
                "patient_history": row.get("patient_history", []),
                "medication_history": row.get("medication_history", []),
                "predicted_mentions": row.get("predicted_mentions", []),
                "hybrid_family_exact": fam,
                "hybrid_four_family_exact": all(fam.values()),
            }
    observations = []
    for letter in letters:
        before = arms["v19_head"][letter.letter_id]
        after = arms["v21_live"][letter.letter_id]
        observations.append({
            "letter_id": letter.letter_id,
            "candidate": after,
            "versus_v19": {
                "hybrid_four_family_exact": before["hybrid_four_family_exact"],
                "changed_direction": _direction(before["hybrid_four_family_exact"], after["hybrid_four_family_exact"]),
            },
        })
    return observations


def _direction(before: bool, after: bool) -> str:
    if after and not before:
        return "win"
    if before and not after:
        return "loss"
    return "same"


def _decision(candidate: Mapping[str, Any], mechanism: Mapping[str, Any], delta: Mapping[str, Any]) -> dict[str, Any]:
    failures = list(v13.topology_failures(delta["surfaces"]["hybrid"]))
    before_quality = mechanism["summary"].get("quality", {})
    after_quality = candidate["summary"].get("quality", {})
    for key in ("schema", "parse"):
        if int(after_quality.get(key, 0)) > int(before_quality.get(key, 0)):
            failures.append(f"{key} failures worsened from {before_quality.get(key, 0)} to {after_quality.get(key, 0)}")
    return {
        "status": "scored",
        "verdict": "preserve_v21_for_next_batch" if not failures else "revise_v21",
        "failures": failures,
        "hybrid_vs_v19_head": delta["surfaces"]["hybrid"],
        "rule": "Preserve only if v21 does not materially regress v19 or worsen parse/schema behavior.",
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v19_head"]
    cand = artifact["arms"].get("v21_live")
    if cand is None:
        return f"""# Luna `dev20` test of ExECT v21 clause-head-only binding

Date: 2026-08-16
Status: no-call check complete; live arm not run
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model: `{artifact['model']}`
Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched

| Arm | hybrid F1 | SF F1 | exact |
| :--- | ---: | ---: | ---: |
| v0.9.24 | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/20 |
| v19 | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_four_family_letter_exact']}/20 |

No model calls were made. v21 is not selected and the default remains v0.9.24.
"""
    delta = artifact["comparison"]["v21_live_minus_v19_head"]["surfaces"]["hybrid"]
    return f"""# Luna `dev20` test of ExECT v21 clause-head-only binding

Date: 2026-08-16
Status: complete; {artifact['decision']['verdict']}
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model: `{artifact['model']}`
Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched

| Arm | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | exact |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| v0.9.24 | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['Diagnosis']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_family_f1']['Prescription']:.4f} | {ctrl['hybrid_family_f1']['Investigations']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/20 |
| v19 | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['Diagnosis']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_family_f1']['Prescription']:.4f} | {mech['hybrid_family_f1']['Investigations']:.4f} | {mech['hybrid_four_family_letter_exact']}/20 |
| v21 | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['Diagnosis']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_family_f1']['Prescription']:.4f} | {cand['hybrid_family_f1']['Investigations']:.4f} | {cand['hybrid_four_family_letter_exact']}/20 |

v21 minus v19 hybrid headline: {delta['headline_f1_delta']:+.4f}; SF: {delta['family_f1_delta']['SeizureFrequency']:+.4f}.

Raw output, parsed events, sinks, projected mentions, and per-letter direction
are retained in `comparison.json`. Boundary: exactly 20 live Luna calls;
`test60` untouched; default remains v0.9.24.
"""


if __name__ == "__main__":
    main()
