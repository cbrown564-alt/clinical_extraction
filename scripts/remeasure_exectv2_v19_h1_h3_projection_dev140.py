"""No-call H1+H3 projection on saved v19 ExECT dev140 rows."""

# ruff: noqa: E501

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts import remeasure_exectv2_v16_h123_projection_luna_dev140 as h123
from scripts import remeasure_exectv2_v19_h1_seizure_free_projection_dev140 as h1
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run
from scripts import run_exectv2_structured_prompt_v13_luna_dev20 as v13
from scripts import run_exectv2_structured_prompt_v17_luna_dev20 as v17_run

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_N = 140
V19_SOURCE = REPO_ROOT / (
    "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815/"
    "v19_live/structured.jsonl"
)
STUDY_DIR = REPO_ROOT / "experiments/exectv2_v19_h1_h3_projection_dev140_20260816"
PROTOCOL = "docs/research/exectv2/v19_h1_h3_projection_dev140_protocol_2026-08-16.md"
REPORT = REPO_ROOT / "docs/research/exectv2/v19_h1_h3_projection_dev140_2026-08-16.md"


def main(argv: Sequence[str] | None = None) -> None:
    del argv
    print(json.dumps(run_study(), indent=2, sort_keys=True))


def _letters() -> list[Any]:
    letters = sorted(load_letters_for_split("dev"), key=lambda letter: letter.letter_id)
    if len(letters) != EXPECTED_N:
        raise RuntimeError(f"expected {EXPECTED_N} development letters, found {len(letters)}")
    if not V19_SOURCE.exists():
        raise FileNotFoundError(f"missing saved v19 dev140 rows: {V19_SOURCE}")
    return letters


def _derive() -> tuple[Path, list[dict[str, str]]]:
    rows = h1._read_jsonl(V19_SOURCE)
    derived, actions = h123._derive_rows(rows, h1=True, h2=False, h3=True, h7=False)
    destination = STUDY_DIR / "source" / "v19_h1_h3_derived_structured.jsonl"
    h1._write_jsonl(derived, destination)
    return destination, actions


def run_study() -> dict[str, Any]:
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    derived_source, actions = _derive()
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = "No-call H1+H3 projection under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_v19_h1_h3_projection_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="No-call H1+H3 projection on saved v19 ExECT dev140 rows.",
            )

        v10_run._arm_assembly = _patched_assembly
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        control = _run("v0924_head", structured.PROMPT_VERSION_V0_9_24, letters)
        v10_run.CONTROL_STRUCTURED = V19_SOURCE
        mechanism = _run("v19_head", structured.PROMPT_VERSION_V19, letters)
        v10_run.CONTROL_STRUCTURED = derived_source
        candidate = _run("v19_h1_h3", structured.PROMPT_VERSION_V19, letters)
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    delta = v13._compare_pair(mechanism, candidate, letters)
    for result, slug in (
        (control, "v0924_head"),
        (mechanism, "v19_head"),
        (candidate, "v19_h1_h3"),
    ):
        v17_run._add_sink_summary(result, STUDY_DIR / slug / "structured.jsonl")
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.v19_h1_h3_projection_dev140.v1",
        "generated_on": "2026-08-16",
        "protocol": PROTOCOL,
        "model": "openai/gpt-5.6-luna",
        "split": "dev140",
        "row_policy": "development rows permitted; test60 sealed",
        "scorer": "four-family clinical_headline through unchanged HEAD assembly",
        "repair_policy": "default/default",
        "row_count": EXPECTED_N,
        "letter_ids": [letter.letter_id for letter in letters],
        "source_artifacts": {
            "v0924_structured": v13.V0924_STRUCTURED.relative_to(REPO_ROOT).as_posix(),
            "v19_structured": V19_SOURCE.relative_to(REPO_ROOT).as_posix(),
            "derived_structured": derived_source.relative_to(REPO_ROOT).as_posix(),
        },
        "replay_mode": {slug: "saved_structured_no_call" for slug in ("v0924_head", "v19_head", "v19_h1_h3")},
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "model_calls": 0,
        "arms": {
            "v0924_head": control["summary"],
            "v19_head": mechanism["summary"],
            "v19_h1_h3": candidate["summary"],
        },
        "projection": {
            "rules": ["H1.retarget_seizure_free_span", "H3.retarget_clause_head"],
            "actions": actions,
            "action_count": len(actions),
            "affected_letter_ids": sorted({action["letter_id"] for action in actions}),
        },
        "comparison": {
            "v19_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters),
            "v19_h1_h3_minus_v19_head": delta,
        },
        "row_observations": _observations(actions),
        "decision": _decision(delta),
        "claim_boundary": "No-call deterministic H1+H3 projection counterfactual on saved v19 Luna dev140 output. Not a new model result, holdout evidence, selected-fill change, or benchmark claim.",
    }
    artifact_path = STUDY_DIR / "comparison.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    return {"artifact": artifact_path.relative_to(REPO_ROOT).as_posix(), "report": REPORT.relative_to(REPO_ROOT).as_posix(), "model_calls": 0, "action_count": len(actions), "decision": artifact["decision"]}


def _run(slug: str, prompt_version: str, letters: Sequence[Any]) -> dict[str, Any]:
    return v13._run_enriched_arm(
        slug=slug,
        prompt_version=prompt_version,
        letters=letters,
        call_mode="saved_structured_no_call",
        overwrite=True,
        progress_every=20,
        api_base=None,
    )


def _observations(actions: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    affected = sorted({str(action["letter_id"]) for action in actions})
    out: list[dict[str, Any]] = []
    for letter_id in affected:
        rows: dict[str, dict[str, dict[str, Any]]] = {}
        for slug in ("v19_head", "v19_h1_h3"):
            rows[slug] = {}
            for row in h1._read_jsonl(STUDY_DIR / slug / "letter_family.jsonl"):
                if str(row["letter_id"]) == letter_id:
                    rows[slug][str(row["family"])] = row
        out.append(
            {
                "letter_id": letter_id,
                "actions": [dict(action) for action in actions if action["letter_id"] == letter_id],
                "v19_four_family_exact": all(row["hybrid_letter_exact"] for row in rows["v19_head"].values()),
                "h1_h3_four_family_exact": all(row["hybrid_letter_exact"] for row in rows["v19_h1_h3"].values()),
                "v19_seizure_frequency": rows["v19_head"].get("SeizureFrequency"),
                "h1_h3_seizure_frequency": rows["v19_h1_h3"].get("SeizureFrequency"),
            }
        )
    return out


def _decision(delta: Mapping[str, Any]) -> dict[str, Any]:
    hybrid = delta["surfaces"]["hybrid"]
    failures: list[str] = []
    if hybrid["headline_f1_delta"] < 0:
        failures.append(f"hybrid headline F1 drop {hybrid['headline_f1_delta']:+.4f}")
    if hybrid["family_f1_delta"]["SeizureFrequency"] < 0:
        failures.append(f"hybrid SeizureFrequency F1 drop {hybrid['family_f1_delta']['SeizureFrequency']:+.4f}")
    if hybrid["four_family_letter_exact_net"] < 0:
        failures.append(f"hybrid net four-family letter-exact losses {abs(hybrid['four_family_letter_exact_net'])}")
    return {"status": "scored", "verdict": "preserve_h1_h3_for_implementation_review" if not failures else "reject_h1_h3", "failures": failures, "hybrid_vs_v19_head": hybrid, "rule": "Keep only if H1+H3 improves v19 headline/SF without exactness regression."}


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v19_head"]
    cand = artifact["arms"]["v19_h1_h3"]
    delta = artifact["comparison"]["v19_h1_h3_minus_v19_head"]["surfaces"]["hybrid"]
    return f"""# v19 H1+H3 projection on ExECT `dev140`

Date: 2026-08-16
Status: complete; {artifact['decision']['verdict']}
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model source: saved GPT-5.6 Luna v19 `dev140` output; no model calls
Sample: all 140 ExECT `dev140` letters; `test60` not touched

| Arm | headline F1 | SeizureFrequency | exact |
| :--- | ---: | ---: | ---: |
| v0.9.24 HEAD | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/140 |
| v19 HEAD | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_four_family_letter_exact']}/140 |
| v19 + H1+H3 | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_four_family_letter_exact']}/140 |

Actions: {artifact['projection']['action_count']}; affected letters: {', '.join(artifact['projection']['affected_letter_ids']) or 'none'}.
H1+H3 minus v19 hybrid headline: {delta['headline_f1_delta']:+.4f}; SF: {delta['family_f1_delta']['SeizureFrequency']:+.4f}; exact net: {delta['four_family_letter_exact_net']:+d}.

This is a no-call projection counterfactual, not a new model result, holdout
evidence, selected-fill change, or benchmark claim.
"""


if __name__ == "__main__":
    main()
