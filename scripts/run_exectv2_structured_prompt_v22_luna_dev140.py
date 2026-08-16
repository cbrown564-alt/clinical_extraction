"""Luna-only ExECT v22 named-type-shape ablation on dev140."""

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
EXPECTED_N = 140
MODEL = "openai/gpt-5.6-luna"
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v22_luna_dev140_20260816"
V19_STRUCTURED = REPO_ROOT / (
    "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815/"
    "v19_live/structured.jsonl"
)
PROTOCOL = "docs/research/exectv2/structured_prompt_v22_named_type_ablation_luna_dev140_protocol_2026-08-16.md"
REPORT_PATH = REPO_ROOT / "docs/research/exectv2/structured_prompt_v22_named_type_ablation_luna_dev140_2026-08-16.md"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check")
    check.add_argument("--overwrite", action="store_true")
    run = sub.add_parser("run")
    run.add_argument("--live", action="store_true")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--progress-every", type=int, default=5)
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
    letters = sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)
    if len(letters) != EXPECTED_N:
        raise RuntimeError(f"expected {EXPECTED_N} dev letters, found {len(letters)}")
    return letters


def verify_payload() -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload_str = structured.build_prompt_input(
        letter, prompt_version=structured.PROMPT_VERSION_V22
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
        raise RuntimeError(f"v22 top-level order drifted: {list(payload)}")
    if "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError("v22 leaked research metadata into the model-facing payload")
    example_ids = {example["id"] for example in payload["worked_examples"]}
    if "named_type_not_generic" in example_ids or len(example_ids) != 7:
        raise RuntimeError("v22 did not perform the pure named-type-shape ablation")
    instructions = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    ).lower()
    for phrase in (
        "current means present, ongoing, or described as happening now",
        "dated, historical, or past-only event stays in patient_history",
    ):
        if phrase not in instructions:
            raise RuntimeError(f"v22 contract is missing: {phrase}")
    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=structured.PROMPT_VERSION_V22
    )
    messages = program.render_messages(prompt_input_json=payload_str)
    system_message = (
        "Extract structured clinical events from the supplied clinical letter. "
        "Return the requested output fields exactly."
    )
    user_content = str(messages[1]["content"])
    if messages[0] != {"role": "system", "content": system_message}:
        raise RuntimeError("v22 did not retain the minimal system message")
    if user_content.count(payload_str) != 1:
        raise RuntimeError("v22 rendered payload more than once or not at all")
    if "prompt_version" in user_content or "letter_id" in user_content:
        raise RuntimeError("v22 rendered request contains hidden research metadata")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError("v22 verification changed the live default")
    return {
        "sample_letter_id": letter.letter_id,
        "prompt_version": structured.PROMPT_VERSION_V22,
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
        v10_run.ESCALATION_REASON = "Predeclared Luna-only ExECT v22 named-type ablation under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_v22_luna_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="ExECTv2 Luna v22 pure named-type-shape ablation on dev140.",
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
        candidate: dict[str, Any] | None = None
        if live:
            candidate = v13._run_enriched_arm(
                slug="v22_live",
                prompt_version=structured.PROMPT_VERSION_V22,
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
    arms: dict[str, Any] = {
        "v0924_head": control["summary"],
        "v19_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.structured_prompt_v22_luna_dev140.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": MODEL,
        "split": "dev140",
        "row_policy": "development rows permitted; test60 sealed",
        "scorer": "four-family clinical_headline through unchanged HEAD assembly",
        "row_count": EXPECTED_N,
        "letter_ids": [letter.letter_id for letter in letters],
        "source_artifacts": {
            "v0924_structured": v13.V0924_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v19_structured": V19_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
        },
        "replay_mode": {
            "v0924_head": "saved_structured_no_call",
            "v19_head": "saved_structured_no_call",
            "v22_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": EXPECTED_N if live else 0,
        "default_prompt_version": structured.PROMPT_VERSION,
        "request_shape": request_shape,
        "arms": arms,
        "comparison": {
            "v19_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)
        },
        "claim_boundary": (
            "ExECTv2 Luna v22 development ablation on dev140. Not holdout evidence, "
            "not a selected prompt, not a benchmark claim, and not a fill change."
        ),
    }
    if candidate is not None:
        v17_run._add_sink_summary(candidate, STUDY_DIR / "v22_live/structured.jsonl")
        arms["v22_live"] = candidate["summary"]
        vs_v19 = v13._compare_pair(mechanism, candidate, letters)
        vs_control = v13._compare_pair(control, candidate, letters)
        artifact["comparison"]["v22_live_minus_v19_head"] = vs_v19
        artifact["comparison"]["v22_live_minus_v0924_head"] = vs_control
        artifact["changed_rows"] = _changed_rows()
        artifact["decision"] = _decide(candidate, mechanism, vs_v19)
    else:
        artifact["decision"] = {
            "status": "live_not_run",
            "verdict": None,
            "failures": [],
            "rule": "Run one live dev140 arm before deciding whether v22 survives.",
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
            out.setdefault(str(row["letter_id"]), {})[str(row["family"])] = bool(row["hybrid_letter_exact"])
        return out

    baseline = family_map("v19_head")
    candidate = family_map("v22_live")
    by_direction: dict[str, list[dict[str, Any]]] = {"win": [], "loss": []}
    for letter_id in sorted(candidate):
        for family in sorted(candidate[letter_id]):
            before = baseline[letter_id][family]
            after = candidate[letter_id][family]
            if before == after:
                continue
            by_direction["win" if after else "loss"].append(
                {"letter_id": letter_id, "family": family, "before": before, "after": after}
            )
    return {"versus_v19": by_direction, "counts": {key: len(value) for key, value in by_direction.items()}}


def _decide(
    candidate: Mapping[str, Any],
    mechanism: Mapping[str, Any],
    versus_mechanism: Mapping[str, Any],
) -> dict[str, Any]:
    hybrid = versus_mechanism["surfaces"]["hybrid"]
    failures: list[str] = []
    if hybrid["headline_f1_delta"] < 0:
        failures.append(f"hybrid headline F1 drop {hybrid['headline_f1_delta']:+.4f} vs v19")
    if hybrid["family_f1_delta"]["SeizureFrequency"] < 0:
        failures.append(f"hybrid SeizureFrequency F1 drop {hybrid['family_f1_delta']['SeizureFrequency']:+.4f} vs v19")
    if hybrid["four_family_letter_exact_net"] < 0:
        failures.append(f"hybrid net four-family exact loss {hybrid['four_family_letter_exact_net']:+d} vs v19")
    before_quality = mechanism["summary"].get("quality", {})
    after_quality = candidate["summary"].get("quality", {})
    for key in ("schema", "parse"):
        if int(after_quality.get(key, 0)) > int(before_quality.get(key, 0)):
            failures.append(f"{key} failures worsened from {before_quality.get(key, 0)} to {after_quality.get(key, 0)}")
    return {
        "status": "scored",
        "verdict": "preserve_v22_dev140" if not failures else "reject_v22",
        "failures": failures,
        "hybrid_vs_v19_head": hybrid,
        "rule": "Keep v22 only if it improves or preserves v19 headline/SF/exactness and quality.",
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v19_head"]
    cand = artifact["arms"].get("v22_live")
    if cand is None:
        return f"""# Luna `dev140` test of ExECT v22 named-type-shape ablation

Date: 2026-08-16
Status: live arm not run
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model: `{MODEL}`
Sample: all 140 ExECT `dev140` letters; `test60` not touched

Request-shape check passed. The live arm remains pending.
"""
    vs_v19 = artifact["comparison"]["v22_live_minus_v19_head"]["surfaces"]["hybrid"]
    vs_control = artifact["comparison"]["v22_live_minus_v0924_head"]["surfaces"]["hybrid"]
    return f"""# Luna `dev140` test of ExECT v22 named-type-shape ablation

Date: 2026-08-16
Status: complete; {artifact['decision']['verdict']}
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model: `{MODEL}`
Sample: all 140 ExECT `dev140` letters; `test60` not touched

| Arm | headline F1 | SeizureFrequency | exact |
| :--- | ---: | ---: | ---: |
| v0.9.24 HEAD | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/140 |
| v19 HEAD | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_four_family_letter_exact']}/140 |
| v22 live | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_four_family_letter_exact']}/140 |

v22 minus v19 hybrid headline: {vs_v19['headline_f1_delta']:+.4f}; SF: {vs_v19['family_f1_delta']['SeizureFrequency']:+.4f}; exact net: {vs_v19['four_family_letter_exact_net']:+d}.
v22 minus v0.9.24 hybrid headline: {vs_control['headline_f1_delta']:+.4f}; SF: {vs_control['family_f1_delta']['SeizureFrequency']:+.4f}; exact net: {vs_control['four_family_letter_exact_net']:+d}.

This is a development prompt comparison, not holdout evidence, a selected
prompt, or a benchmark claim.
"""


if __name__ == "__main__":
    main()
