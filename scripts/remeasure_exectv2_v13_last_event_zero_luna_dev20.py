"""No-call remasure of last-event no/none→0 encoding on saved v13 raws."""

# ruff: noqa: E501

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_state_projection import (
    PROJECTION_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from scripts import run_exectv2_structured_prompt_v10_luna_dev20 as v10_run
from scripts import run_exectv2_structured_prompt_v13_luna_dev20 as v13

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "experiments/exectv2_v13_last_event_zero_remeasure_luna_dev20_20260815"
REPORT = REPO / "docs/research/exectv2/v13_last_event_zero_remeasure_luna_dev20_2026-08-15.md"
V13_STRUCTURED = (
    REPO
    / "experiments/exectv2_structured_prompt_v13_luna_dev20_20260815/v13_live/structured.jsonl"
)


def main() -> None:
    letters = [
        letter
        for letter in load_letters_for_split("dev")
        if letter.letter_id in set(v13.FROZEN_IDS)
    ]
    letters.sort(key=lambda item: item.letter_id)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    original_dir = v10_run.STUDY_DIR
    original_control = v10_run.CONTROL_STRUCTURED
    original_reason = v10_run.ESCALATION_REASON
    original_assembly = v10_run._arm_assembly
    started = datetime.now(UTC).isoformat()
    try:
        v10_run.STUDY_DIR = OUT_DIR
        v10_run.ESCALATION_REASON = (
            "No-call remasure of last-event no/none→0 on saved v13 raws"
        )
        v10_run._arm_assembly = v13._patched_arm_assembly
        v10_run.CONTROL_STRUCTURED = v13.V0924_STRUCTURED
        control = v13._run_enriched_arm(
            slug="v0924_head",
            prompt_version=structured.PROMPT_VERSION_V0_9_24,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=1,
            api_base=None,
        )
        v10_run.CONTROL_STRUCTURED = V13_STRUCTURED
        candidate = v13._run_enriched_arm(
            slug="v13_head",
            prompt_version=structured.PROMPT_VERSION_V13,
            letters=letters,
            call_mode="saved_structured_no_call",
            overwrite=True,
            progress_every=1,
            api_base=None,
        )
    finally:
        v10_run.STUDY_DIR = original_dir
        v10_run.CONTROL_STRUCTURED = original_control
        v10_run.ESCALATION_REASON = original_reason
        v10_run._arm_assembly = original_assembly

    versus = v13._compare_pair(control, candidate, letters)
    decision = v13.decide_topology(versus, versus)
    artifact = {
        "schema_version": "exectv2.v13_last_event_zero_remeasure_luna_dev20.v1",
        "generated_on": "2026-08-15",
        "live": False,
        "model_calls": 0,
        "projection_version": PROJECTION_VERSION,
        "started_utc": started,
        "finished_utc": datetime.now(UTC).isoformat(),
        "letter_ids": list(v13.FROZEN_IDS),
        "arms": {
            "v0924_head": control["summary"],
            "v13_head": candidate["summary"],
        },
        "comparison": {"v13_head_minus_v0924_head": versus},
        "decision": decision,
        "claim_boundary": (
            "No-call remasure of last-event no/none encoding on saved Luna "
            "v13 dev20 raws. Not holdout and not a fill promotion."
        ),
    }
    out = OUT_DIR / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    hybrid = versus["surfaces"]["hybrid"]
    ctrl = control["summary"]
    cand = candidate["summary"]
    REPORT.write_text(
        f"""# No-call remasure of last-event no/none → 0 on saved v13 raws

Date: 2026-08-15
Status: complete; {decision["verdict"]}
Sidecars: frozen Luna `dev20` `v0.9.24` and v13 structured JSONL
Stack: HEAD (`sf_state_projection` v0.18 last-event zero encoding)
Model calls: 0. `test60` not touched.

## Verdict

**{decision["verdict"]}.** Failures: {", ".join(decision.get("failures") or ["none"])}.
Does not promote v13 or change a selected fill.

## Hybrid on the 20-letter pool

| Arm | hybrid F1 | four-family exact | SF F1 |
| :--- | ---: | ---: | ---: |
| v0924_head | {ctrl["hybrid_headline_f1"]:.4f} | {ctrl["hybrid_four_family_letter_exact"]}/20 | {ctrl["hybrid_family_f1"]["SeizureFrequency"]:.4f} |
| v13_head | {cand["hybrid_headline_f1"]:.4f} | {cand["hybrid_four_family_letter_exact"]}/20 | {cand["hybrid_family_f1"]["SeizureFrequency"]:.4f} |

v13 − v0.9.24 hybrid headline {hybrid["headline_f1_delta"]:+.4f}; SF {hybrid["family_f1_delta"]["SeizureFrequency"]:+.4f}; net four-family exact {hybrid["four_family_letter_exact_net"]:+d}.

Prior leftover-drop remasure was hybrid 0.9035 / exact 7/20 / SF 0.8000.
This remasure applies last-event `no`/`none`/missing → `0` + Since on the same raws.

## Boundary

Gold-free only. Not `test60`. Not a fill.
""",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {"artifact": str(out.relative_to(REPO)), "decision": decision},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
