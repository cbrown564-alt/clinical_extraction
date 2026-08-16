"""No-call v19 H4 negative-context projection on saved ExECT dev140 rows."""

# ruff: noqa: E501

from __future__ import annotations

import copy
import json
import re
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
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run
from scripts import run_exectv2_structured_prompt_v13_luna_dev20 as v13
from scripts import run_exectv2_structured_prompt_v17_luna_dev20 as v17_run

REPO_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_N = 140
V19_SOURCE = REPO_ROOT / (
    "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815/"
    "v19_live/structured.jsonl"
)
STUDY_DIR = REPO_ROOT / "experiments/exectv2_v19_h4_never_had_projection_dev140_20260816"
PROTOCOL = "docs/research/exectv2/v19_h4_never_had_projection_dev140_protocol_2026-08-16.md"
REPORT = REPO_ROOT / "docs/research/exectv2/v19_h4_never_had_projection_dev140_2026-08-16.md"
SEIZURE_FAMILY = "SeizureFrequency"
_NEVER_HAD_RE = re.compile(
    r"\bnever\s+(?:had|experienced)\b"
    r"|\b(?:has|have)\s+never\s+had\b"
    r"|\b(?:has|have|had)\s+not\s+had\b"
    r"(?:(?!\b(?:further|more)\b).){0,100}\b(?:resembl\w*|similar\s+to)\b",
    re.IGNORECASE | re.DOTALL,
)


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


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(dict(row), ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def _derive() -> tuple[Path, Path, list[dict[str, str]]]:
    rows = _read_jsonl(V19_SOURCE)
    retained, retained_actions = h123._derive_rows(rows, h1=True, h2=False, h3=False, h7=True)
    candidate = copy.deepcopy(retained)
    h4_actions = list(retained_actions)
    for row in candidate:
        kept: list[dict[str, Any]] = []
        for mention in row.get("predicted_mentions", []):
            if (
                str(mention.get("entity")) == SEIZURE_FAMILY
                and _NEVER_HAD_RE.search(str(mention.get("evidence") or ""))
            ):
                h4_actions.append(
                    {"letter_id": str(row["letter_id"]), "rule": "H4.drop_never_had_or_resemble"}
                )
                continue
            kept.append(mention)
        row["predicted_mentions"] = kept
    retained_path = STUDY_DIR / "source" / "v19_h1_h7_derived_structured.jsonl"
    candidate_path = STUDY_DIR / "source" / "v19_h1_h7_h4_derived_structured.jsonl"
    _write_jsonl(retained, retained_path)
    _write_jsonl(candidate, candidate_path)
    return retained_path, candidate_path, h4_actions


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


def run_study() -> dict[str, Any]:
    letters = _letters()
    STUDY_DIR.mkdir(parents=True, exist_ok=True)
    retained_source, candidate_source, actions = _derive()
    started = datetime.now(UTC).isoformat()
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    try:
        v10_run.STUDY_DIR = STUDY_DIR
        v10_run.ESCALATION_REASON = "No-call v19 H4 projection under " + PROTOCOL

        def _patched_assembly(slug: str, structured_path: Path, sf_final_path: Path) -> Any:
            cfg = original_assembly(slug, structured_path, sf_final_path)
            return replace(
                cfg,
                candidate_id=f"exectv2_v19_h4_never_had_projection_dev140_{slug}",
                split="dev",
                row_count=EXPECTED_N,
                claim_boundary="No-call v19 H4 projection on saved ExECT dev140 rows.",
            )

        v10_run._arm_assembly = _patched_assembly
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        control = _run("v0924_head", structured.PROMPT_VERSION_V0_9_24, letters)
        v10_run.CONTROL_STRUCTURED = V19_SOURCE
        mechanism = _run("v19_head", structured.PROMPT_VERSION_V19, letters)
        v10_run.CONTROL_STRUCTURED = retained_source
        retained = _run("v19_h1_h7", structured.PROMPT_VERSION_V19, letters)
        v10_run.CONTROL_STRUCTURED = candidate_source
        candidate = _run("v19_h1_h7_h4", structured.PROMPT_VERSION_V19, letters)
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    results = (
        (control, "v0924_head"),
        (mechanism, "v19_head"),
        (retained, "v19_h1_h7"),
        (candidate, "v19_h1_h7_h4"),
    )
    for result, slug in results:
        v17_run._add_sink_summary(result, STUDY_DIR / slug / "structured.jsonl")
    delta = v13._compare_pair(retained, candidate, letters)
    artifact: dict[str, Any] = {
        "schema_version": "exectv2.v19_h4_never_had_projection_dev140.v1",
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
            "v19_h1_h7_derived_structured": retained_source.relative_to(REPO_ROOT).as_posix(),
            "v19_h1_h7_h4_derived_structured": candidate_source.relative_to(REPO_ROOT).as_posix(),
        },
        "replay_mode": {slug: "saved_structured_no_call" for _, slug in results},
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "model_calls": 0,
        "arms": {slug: result["summary"] for result, slug in results},
        "projection": {
            "rules": ["H1.retarget_seizure_free_span", "H7.drop_stale_older_zero", "H4.drop_never_had_or_resemble"],
            "actions": actions,
            "action_count": len(actions),
            "h4_action_count": sum(action["rule"] == "H4.drop_never_had_or_resemble" for action in actions),
            "affected_letter_ids": sorted({action["letter_id"] for action in actions}),
            "h4_affected_letter_ids": sorted({action["letter_id"] for action in actions if action["rule"] == "H4.drop_never_had_or_resemble"}),
        },
        "comparison": {
            "v19_head_minus_v0924_head": v13._compare_pair(control, mechanism, letters),
            "v19_h1_h7_minus_v19_head": v13._compare_pair(mechanism, retained, letters),
            "v19_h1_h7_h4_minus_v19_h1_h7": delta,
        },
        "row_observations": _observations(actions),
        "decision": _decision(delta),
        "claim_boundary": "No-call deterministic v19 H4 projection counterfactual on saved Luna dev140 output. Not a new model result, holdout evidence, selected-fill change, or benchmark claim.",
    }
    artifact_path = STUDY_DIR / "comparison.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(_render_report(artifact), encoding="utf-8")
    return {
        "artifact": artifact_path.relative_to(REPO_ROOT).as_posix(),
        "report": REPORT.relative_to(REPO_ROOT).as_posix(),
        "model_calls": 0,
        "h4_action_count": artifact["projection"]["h4_action_count"],
        "decision": artifact["decision"],
    }


def _observations(actions: Sequence[Mapping[str, str]]) -> list[dict[str, Any]]:
    affected = sorted({str(action["letter_id"]) for action in actions if action["rule"] == "H4.drop_never_had_or_resemble"})
    out: list[dict[str, Any]] = []
    for letter_id in affected:
        rows: dict[str, dict[str, Any]] = {}
        for slug in ("v19_h1_h7", "v19_h1_h7_h4"):
            rows[slug] = {
                str(row["family"]): row
                for row in _read_jsonl(STUDY_DIR / slug / "letter_family.jsonl")
                if str(row["letter_id"]) == letter_id
            }
        out.append(
            {
                "letter_id": letter_id,
                "actions": [dict(action) for action in actions if action["letter_id"] == letter_id],
                "h1_h7_four_family_exact": all(row["hybrid_letter_exact"] for row in rows["v19_h1_h7"].values()),
                "h1_h7_h4_four_family_exact": all(row["hybrid_letter_exact"] for row in rows["v19_h1_h7_h4"].values()),
                "h1_h7_seizure_frequency": rows["v19_h1_h7"].get("SeizureFrequency"),
                "h1_h7_h4_seizure_frequency": rows["v19_h1_h7_h4"].get("SeizureFrequency"),
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
    return {
        "status": "scored",
        "verdict": "preserve_h4_for_implementation_review" if not failures else "reject_h4",
        "failures": failures,
        "hybrid_vs_v19_h1_h7": hybrid,
        "rule": "Keep H4 only if it improves or preserves headline, SF, and exactness against v19+H1+H7.",
    }


def _render_report(artifact: Mapping[str, Any]) -> str:
    ctrl = artifact["arms"]["v0924_head"]
    mech = artifact["arms"]["v19_head"]
    retained = artifact["arms"]["v19_h1_h7"]
    cand = artifact["arms"]["v19_h1_h7_h4"]
    delta = artifact["comparison"]["v19_h1_h7_h4_minus_v19_h1_h7"]["surfaces"]["hybrid"]
    return f"""# v19 H4 never-had projection on ExECT `dev140`

Date: 2026-08-16
Status: complete; {artifact['decision']['verdict']}
Protocol: [{Path(PROTOCOL).name}]({Path(PROTOCOL).name})
Model source: saved GPT-5.6 Luna v19 `dev140` output; no model calls
Sample: all 140 ExECT `dev140` letters; `test60` not touched

| Arm | headline F1 | SeizureFrequency | exact |
| :--- | ---: | ---: | ---: |
| v0.9.24 HEAD | {ctrl['hybrid_headline_f1']:.4f} | {ctrl['hybrid_family_f1']['SeizureFrequency']:.4f} | {ctrl['hybrid_four_family_letter_exact']}/140 |
| v19 HEAD | {mech['hybrid_headline_f1']:.4f} | {mech['hybrid_family_f1']['SeizureFrequency']:.4f} | {mech['hybrid_four_family_letter_exact']}/140 |
| v19 + H1+H7 | {retained['hybrid_headline_f1']:.4f} | {retained['hybrid_family_f1']['SeizureFrequency']:.4f} | {retained['hybrid_four_family_letter_exact']}/140 |
| v19 + H1+H7+H4 | {cand['hybrid_headline_f1']:.4f} | {cand['hybrid_family_f1']['SeizureFrequency']:.4f} | {cand['hybrid_four_family_letter_exact']}/140 |

H4 actions: {artifact['projection']['h4_action_count']}; affected letters: {', '.join(artifact['projection']['h4_affected_letter_ids']) or 'none'}.
H4 minus H1+H7 hybrid headline: {delta['headline_f1_delta']:+.4f}; SF: {delta['family_f1_delta']['SeizureFrequency']:+.4f}; exact net: {delta['four_family_letter_exact_net']:+d}.

This is a no-call projection counterfactual, not a new model result, holdout
evidence, selected-fill change, or benchmark claim.
"""


if __name__ == "__main__":
    main()
