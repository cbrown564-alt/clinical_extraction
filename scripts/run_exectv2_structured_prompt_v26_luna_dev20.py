"""Luna-only ExECT v26/v27 clinical-family prompt study on frozen dev20."""

# ruff: noqa: E501

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
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
STUDY_DIR = REPO_ROOT / "experiments/exectv2_structured_prompt_v26_luna_dev20_20260816"
V19_STRUCTURED = REPO_ROOT / (
    "experiments/exectv2_structured_prompt_v19_luna_dev20_20260815/"
    "v19_live/structured.jsonl"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v26_clinical_family_luna_dev20_protocol_2026-08-16.md"
)
REPORT_PATH = REPO_ROOT / (
    "docs/research/exectv2/structured_prompt_v26_clinical_family_luna_dev20_2026-08-16.md"
)
MODEL = "openai/gpt-5.6-luna"


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="Verify the selected prompt and score saved controls.")
    check.add_argument("--overwrite", action="store_true")
    check.add_argument("--v27", action="store_true")
    run = sub.add_parser("run", help="Score controls; live only with --live.")
    run.add_argument("--live", action="store_true", help="Make exactly 20 Luna calls.")
    run.add_argument("--overwrite", action="store_true")
    run.add_argument("--progress-every", type=int, default=1)
    run.add_argument("--api-base")
    run.add_argument("--v27", action="store_true")
    args = parser.parse_args(argv)
    result = (
        check_study(overwrite=args.overwrite, v27=args.v27)
        if args.command == "check"
        else run_study(
            live=args.live,
            overwrite=args.overwrite,
            progress_every=args.progress_every,
            api_base=args.api_base,
            v27=args.v27,
        )
    )
    print(json.dumps(result, indent=2, sort_keys=True))


def _letters() -> list[ExectLetter]:
    frozen = set(v13.FROZEN_IDS)
    letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in frozen]
    letters.sort(key=lambda item: item.letter_id)
    if [letter.letter_id for letter in letters] != sorted(v13.FROZEN_IDS):
        raise RuntimeError("the frozen v13-v26 20-letter sample is unavailable or changed")
    return letters


def verify_payload(prompt_version: str = structured.PROMPT_VERSION_V26) -> dict[str, Any]:
    letter = ExectLetter(letter_id="EA0002", note_text="placeholder")
    payload_str = structured.build_prompt_input(
        letter, prompt_version=prompt_version
    )
    payload = json.loads(payload_str)
    expected_order = [
        "task",
        "output_schema",
        "output_schema_notes",
        "attribute_vocabulary",
        "clinical_family_guidance",
        "shared_rules",
        "letter_text",
    ]
    if list(payload) != expected_order:
        raise RuntimeError(f"{prompt_version} top-level order drifted: {list(payload)}")
    if "prompt_version" in payload or "letter_id" in payload:
        raise RuntimeError(f"{prompt_version} leaked research metadata into the model request")
    instructions = json.dumps(
        {key: value for key, value in payload.items() if key != "letter_text"}
    ).lower()
    for phrase in (
        "one clinical fact per object",
        "find every distinct frequency statement",
        "dated, historical, or past-only count belongs in history",
        "planned, requested, or future tests are not investigation events",
    ):
        if phrase not in instructions:
            raise RuntimeError(f"{prompt_version} contract is missing: {phrase}")
    program = structured.DspyKeyEntitiesStructuredExtractor(
        prompt_version=prompt_version
    )
    messages = program.render_messages(prompt_input_json=payload_str)
    system_message = (
        "Extract structured clinical events from the supplied clinical letter. "
        "Return the requested output fields exactly."
    )
    user_content = str(messages[1]["content"])
    if messages[0] != {"role": "system", "content": system_message}:
        raise RuntimeError(f"{prompt_version} did not retain the minimal system message")
    if user_content.count(payload_str) != 1:
        raise RuntimeError(f"{prompt_version} rendered the payload more than once or not at all")
    if "prompt_version" in user_content or "letter_id" in user_content:
        raise RuntimeError(f"{prompt_version} rendered hidden research metadata")
    if structured.PROMPT_VERSION != structured.PROMPT_VERSION_V0_9_24:
        raise RuntimeError(f"{prompt_version} verification changed the live default")
    return {
        "sample_letter_id": letter.letter_id,
        "prompt_version": prompt_version,
        "default_prompt_version": structured.PROMPT_VERSION,
        "system_message": system_message,
        "top_level_user_json_keys": expected_order,
        "user_message_sha256": hashlib.sha256(user_content.encode()).hexdigest(),
        "payload_sha256": hashlib.sha256(payload_str.encode()).hexdigest(),
    }


def run_study(
    *, live: bool, overwrite: bool = False, progress_every: int = 1, api_base: str | None = None,
    v27: bool = False,
) -> dict[str, Any]:
    prompt_tag = "v27" if v27 else "v26"
    prompt_version = structured.PROMPT_VERSION_V27 if v27 else structured.PROMPT_VERSION_V26
    study_dir = REPO_ROOT / f"experiments/exectv2_structured_prompt_{prompt_tag}_luna_dev20_20260816"
    protocol = REPO_ROOT / f"docs/research/exectv2/structured_prompt_{prompt_tag}_clinical_family_luna_dev20_protocol_2026-08-16.md"
    report_path = REPO_ROOT / f"docs/research/exectv2/structured_prompt_{prompt_tag}_clinical_family_luna_dev20_2026-08-16.md"
    request_shape = verify_payload(prompt_version)
    if not V19_STRUCTURED.exists():
        raise FileNotFoundError(f"missing saved v19 structured rows: {V19_STRUCTURED}")
    letters = _letters()
    study_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = study_dir
        v10_run.ESCALATION_REASON = f"Predeclared Luna-only ExECT {prompt_tag} clinical-family study under {protocol}"

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_structured_prompt_{prompt_tag}_luna_dev20_{slug}",
                split="dev",
                row_count=20,
                claim_boundary=f"ExECTv2 Luna {prompt_tag} clinical-family prompt study on the frozen 20-letter dev20 sample.",
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
                slug=f"{prompt_tag}_live",
                prompt_version=prompt_version,
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
        v17_run._add_sink_summary(result, study_dir / slug / "structured.jsonl")
    arms: dict[str, Any] = {
        "v0924_head": control["summary"],
        "v19_head": mechanism["summary"],
    }
    artifact: dict[str, Any] = {
        "schema_version": f"exectv2.structured_prompt_{prompt_tag}_luna_dev20.v1",
        "generated_on": "2026-08-16",
        "protocol": protocol.relative_to(REPO_ROOT).as_posix(),
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
            f"{prompt_tag}_live": "live" if live else "not_run",
        },
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "live": live,
        "model_calls": 20 if live else 0,
        "default_prompt_version": structured.PROMPT_VERSION,
        "request_shape": request_shape,
        "arms": arms,
        "comparison": {"v19_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters)},
        "claim_boundary": f"ExECTv2 Luna 20-letter development comparison of {prompt_tag} through HEAD. Not holdout evidence, not a selected prompt, not a benchmark claim, and not a fill change.",
    }
    if candidate is not None:
        v17_run._add_sink_summary(candidate, study_dir / f"{prompt_tag}_live" / "structured.jsonl")
        arms[f"{prompt_tag}_live"] = candidate["summary"]
        artifact["comparison"][f"{prompt_tag}_live_minus_v19_head"] = v13._compare_pair(mechanism, candidate, letters)
        artifact["comparison"][f"{prompt_tag}_live_minus_v0924_head"] = v13._compare_pair(control, candidate, letters)
    else:
        artifact["decision"] = {"status": "live_not_run", "verdict": None}
    out = study_dir / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report_path.write_text(_render_report(artifact), encoding="utf-8")
    return {"artifact": out.relative_to(REPO_ROOT).as_posix(), "report": report_path.relative_to(REPO_ROOT).as_posix(), "live": live, "model_calls": artifact["model_calls"]}


def check_study(*, overwrite: bool = False, v27: bool = False) -> dict[str, Any]:
    prompt_version = structured.PROMPT_VERSION_V27 if v27 else structured.PROMPT_VERSION_V26
    request_shape = verify_payload(prompt_version)
    result = run_study(live=False, overwrite=overwrite, v27=v27)
    return {**result, "request_shape": request_shape, "model_calls": 0}


def _render_report(artifact: dict[str, Any]) -> str:
    arms = artifact["arms"]
    lines = [
        f"# Luna `dev20` test of ExECT {'v27' if 'v27' in artifact['protocol'] else 'v26'} clinical-family prompt",
        "",
        "Date: 2026-08-16",
        "Status: complete; candidate measured" if artifact["live"] else "Status: controls checked; live arm not run",
        f"Protocol: [{Path(artifact['protocol']).name}]({Path(artifact['protocol']).name})",
        "Model: `openai/gpt-5.6-luna`",
        "Sample: frozen 20 letters from ExECT `dev140`; `test60` not touched",
        "",
        "| Arm | headline F1 | Diagnosis | SeizureFrequency | Prescription | Investigations | exact |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for slug, summary in arms.items():
        lines.append(
            f"| {slug} | {summary.get('hybrid_headline_f1', 0):.4f} | "
            f"{summary.get('hybrid_family_f1', {}).get('Diagnosis', 0):.4f} | "
            f"{summary.get('hybrid_family_f1', {}).get('SeizureFrequency', 0):.4f} | "
            f"{summary.get('hybrid_family_f1', {}).get('Prescription', 0):.4f} | "
            f"{summary.get('hybrid_family_f1', {}).get('Investigations', 0):.4f} | "
            f"{summary.get('hybrid_four_family_letter_exact', 0)}/20 |"
        )
    lines += [
        "",
        "Raw output, parsed events, history sinks, projected mentions, and per-family exactness are retained in `comparison.json` and the arm directories.",
        "Boundary: exactly 20 live Luna calls when run with `--live`; `test60` untouched; default remains v0.9.24.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
