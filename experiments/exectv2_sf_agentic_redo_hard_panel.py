"""Phase 3 (Task 23): run all 4 ExECTv2 SF conditions over the 53-letter
hard panel, score against gold via the production score_frequency_state,
apply the predeclared gate.

See docs/plans/proud-bubbling-ocean.md and
docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_predeclaration_2026-07-01.md
for the locked design/gates this script implements. Resumable: each
condition/letter result is checkpointed to JSONL and skipped on rerun.
NEVER reads or runs test59/test450; letters come only from the dev140 split.

Usage:
    python experiments/exectv2_sf_agentic_redo_hard_panel.py --stage run
    python experiments/exectv2_sf_agentic_redo_hard_panel.py --stage report
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.agentic import (
    multi_agent_ceiling,
    react_single_agent,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    DspySinglePassSFExtractor,
    build_prompt_input,
    to_predicted_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.mention_pipeline import (
    parse_extraction_json,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    score_frequency_state,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
TEMPERATURE = 0.0
MAX_TOKENS = 800
SPEC = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]

HARD_PANEL_SOURCE = Path(
    "docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md"
)
OUT_DIR = Path("experiments")
RESULTS_JSONL = OUT_DIR / "exectv2_sf_agentic_redo_hard_panel_results.jsonl"
RESULTS_REPORT = OUT_DIR / "exectv2_sf_agentic_redo_hard_panel_results.md"

CONDITIONS = (
    "single_greedy",
    "single_agent_tools_react",
    "multi_agent_d3_static",
    "multi_agent_dynamic_orchestrator",
)


def load_hard_panel_letter_ids() -> list[str]:
    """Parse the 53 hard-panel letter IDs directly from the source
    adjudication table (avoids manual transcription)."""
    lines = HARD_PANEL_SOURCE.read_text(encoding="utf-8").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("| letter | gold |"))
    ids: list[str] = []
    for line in lines[start + 2 :]:
        if not line.startswith("|"):
            break
        cell = line.split("|")[1].strip()
        match = re.match(r"^(EA\d{4})$", cell)
        if not match:
            break
        ids.append(match.group(1))
    assert len(ids) == 53, f"expected 53 hard-panel letters, got {len(ids)}"
    return ids


def load_hard_panel_letters() -> list[ExectLetter]:
    ids = set(load_hard_panel_letter_ids())
    letters = [letter for letter in load_letters_for_split("dev") if letter.letter_id in ids]
    assert len(letters) == 53, f"expected 53 dev letters matched, got {len(letters)}"
    return letters


def score_extraction(letter: ExectLetter, raw_output: str) -> tuple[float | None, list[str]]:
    extraction, parse_errors = (
        parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
    )
    if extraction is None:
        return None, parse_errors
    predicted_letter, warnings = to_predicted_letter(
        letter.letter_id, extraction.mentions, spec=SPEC, note_text=letter.note_text
    )
    pred_exect_letter = to_exect_letter(predicted_letter, note_text=letter.note_text)
    scores = score_frequency_state([letter], [pred_exect_letter])
    return scores.clinical_headline.f1, parse_errors + warnings


def run_condition_on_letter(condition: str, letter: ExectLetter) -> dict[str, Any]:
    dspy.configure(
        lm=build_dspy_lm(MODEL, temperature=TEMPERATURE, max_tokens=MAX_TOKENS, cache=True)
    )
    prompt_input_json = build_prompt_input(letter)

    call_error: str | None = None
    raw_output: str | None = None
    n_tool_turns: int | None = None
    try:
        if condition == "single_greedy":
            prediction = DspySinglePassSFExtractor()(prompt_input_json=prompt_input_json)
            raw_output = str(prediction.extraction_json)
        elif condition == "single_agent_tools_react":
            prediction = react_single_agent.run_single_row(
                prompt_input_json, note_text=letter.note_text
            )
            raw_output = str(prediction.extraction_json)
            n_tool_turns = sum(1 for k in prediction.trajectory if k.startswith("tool_name_"))
        elif condition == "multi_agent_d3_static":
            result = multi_agent_ceiling.run_d3_static(prompt_input_json)
            raw_output = result["extraction_json"]
        elif condition == "multi_agent_dynamic_orchestrator":
            prediction = multi_agent_ceiling.run_dynamic_orchestrator_row(
                prompt_input_json, note_text=letter.note_text
            )
            raw_output = str(prediction.extraction_json)
            n_tool_turns = sum(1 for k in prediction.trajectory if k.startswith("tool_name_"))
        else:
            raise ValueError(f"Unknown condition: {condition}")
    except Exception as exc:  # pragma: no cover - live transport only
        call_error = f"{type(exc).__name__}: {exc}"

    f1, notes = (
        score_extraction(letter, raw_output)
        if raw_output and not call_error
        else (None, ["not_run"])
    )
    return {
        "letter_id": letter.letter_id,
        "condition": condition,
        "f1": f1,
        "call_error": call_error,
        "notes": notes,
        "n_tool_turns": n_tool_turns,
    }


def _read_completed() -> set[tuple[str, str]]:
    if not RESULTS_JSONL.exists():
        return set()
    completed = set()
    for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        completed.add((row["condition"], row["letter_id"]))
    return completed


def run_stage() -> None:
    letters = load_hard_panel_letters()
    completed = _read_completed()
    total = len(letters) * len(CONDITIONS)
    done = len(completed)
    print(f"Resuming: {done}/{total} (condition, letter) pairs already completed.")

    with RESULTS_JSONL.open("a", encoding="utf-8") as fh:
        for letter in letters:
            for condition in CONDITIONS:
                key = (condition, letter.letter_id)
                if key in completed:
                    continue
                row = run_condition_on_letter(condition, letter)
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                done += 1
                if done % 25 == 0:
                    print(f"progress: {done}/{total}")

    print(f"Run stage complete: {done}/{total}.")


def _non_empty_gold_letter_ids() -> set[str]:
    """Letters in the hard panel whose gold has at least one SeizureFrequency
    entity. `clinical_headline` F1 is structurally 0.0 for empty-gold
    letters regardless of prediction quality (found post-hoc, not
    predeclared) -- 22/53 of this panel's letters are empty-gold, which
    mechanically floors every condition to a tied 0.0 on those letters and
    swamps the real per-letter signal. Reported separately, not silently
    dropped."""
    return {
        letter.letter_id
        for letter in load_hard_panel_letters()
        if letter.entities("SeizureFrequency")
    }


def _condition_table(
    lines: list[str], by_condition: dict[str, list[dict[str, Any]]], letter_ids: set[str] | None
) -> dict[str, float]:
    means: dict[str, float] = {}
    lines.append("| Condition | Mean F1 | n | True Failures |")
    lines.append("| --- | ---: | ---: | ---: |")
    for condition in CONDITIONS:
        cond_rows = by_condition.get(condition, [])
        if letter_ids is not None:
            cond_rows = [r for r in cond_rows if r["letter_id"] in letter_ids]
        n = len(cond_rows)
        true_failures = sum(1 for r in cond_rows if r.get("call_error") or r.get("f1") is None)
        scored = [r["f1"] for r in cond_rows if r.get("f1") is not None]
        mean_f1 = sum(scored) / len(scored) if scored else 0.0
        means[condition] = mean_f1
        lines.append(f"| {condition} | {mean_f1:.4f} | {n} | {true_failures}/{n} |")
    return means


def _win_loss_table(
    lines: list[str], by_condition: dict[str, list[dict[str, Any]]], letter_ids: set[str] | None
) -> dict[tuple[str, str], tuple[int, int]]:
    def win_loss(candidate: str, comparator: str) -> tuple[int, int, int]:
        cand_by_letter = {r["letter_id"]: r for r in by_condition.get(candidate, [])}
        comp_by_letter = {r["letter_id"]: r for r in by_condition.get(comparator, [])}
        wins = losses = ties = 0
        for letter_id, cand_row in cand_by_letter.items():
            if letter_ids is not None and letter_id not in letter_ids:
                continue
            comp_row = comp_by_letter.get(letter_id)
            if comp_row is None:
                continue
            cand_f1 = cand_row.get("f1") or 0.0
            comp_f1 = comp_row.get("f1") or 0.0
            if cand_f1 > comp_f1:
                wins += 1
            elif cand_f1 < comp_f1:
                losses += 1
            else:
                ties += 1
        return wins, losses, ties

    comparisons = [
        ("single_agent_tools_react", "single_greedy"),
        ("multi_agent_d3_static", "single_greedy"),
        ("multi_agent_dynamic_orchestrator", "single_greedy"),
        ("multi_agent_dynamic_orchestrator", "multi_agent_d3_static"),
    ]
    lines.append("| Candidate | Wins | Losses | Ties |")
    lines.append("| --- | ---: | ---: | ---: |")
    gate_results = {}
    for candidate, comparator in comparisons:
        wins, losses, ties = win_loss(candidate, comparator)
        lines.append(f"| {candidate} vs {comparator} | {wins} | {losses} | {ties} |")
        gate_results[(candidate, comparator)] = (wins, losses)
    return gate_results


def report_stage() -> None:
    rows = [
        json.loads(line)
        for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_condition: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_condition[row["condition"]].append(row)

    non_empty_ids = _non_empty_gold_letter_ids()

    lines = ["# ExECTv2 SeizureFrequency Agentic Redo — Hard Panel Results", ""]
    lines.append(
        "Self-contained fresh study on the 53-letter dev140 hard panel "
        "(disagreement-bearing letters from the SF canonical row-adjudication), "
        "rescored on the production score_frequency_state.clinical_headline "
        "metric (not the state_profile/GEPA metric those letters were "
        "originally adjudicated on)."
    )
    lines.append("")
    lines.append(
        f"**Post-hoc finding (not predeclared):** {53 - len(non_empty_ids)}/53 of this "
        "panel's letters have EMPTY gold SeizureFrequency annotations (the "
        'adjudication doc\'s own "gold annotated nothing" cases). '
        "`clinical_headline` F1 is structurally 0.0 on an empty-gold letter "
        "regardless of what's predicted -- even a perfectly correct empty "
        "prediction scores 0.0, not 1.0 (verified directly). This mechanically "
        "ties all 4 conditions at 0.0 on those letters and floors every "
        "condition's mean F1 equally, which is why the all-53 numbers below "
        f"look far lower than the production SF headline (0.9053). The "
        f"gate is evaluated on the {len(non_empty_ids)} non-empty-gold letters "
        "only, where real per-letter signal exists; all-53 numbers are kept "
        "for transparency, not used for the gate decision."
    )
    lines.append("")
    lines.append("## Condition Mean F1 -- all 53 letters (includes floor-effect letters)")
    lines.append("")
    _condition_table(lines, by_condition, None)

    lines.append("")
    lines.append(
        f"## Condition Mean F1 -- {len(non_empty_ids)} non-empty-gold letters (informative subset)"
    )
    lines.append("")
    _condition_table(lines, by_condition, non_empty_ids)

    lines.append("")
    lines.append(
        f"## Win/Loss vs single_greedy -- {len(non_empty_ids)} non-empty-gold letters (gate basis)"
    )
    lines.append("")
    gate_results = _win_loss_table(lines, by_condition, non_empty_ids)

    lines.append("")
    lines.append("## Win/Loss vs single_greedy -- all 53 letters (reference only, not gate basis)")
    lines.append("")
    _win_loss_table(lines, by_condition, None)

    lines.append("")
    lines.append("## Predeclared Gate Outcomes")
    lines.append("")
    lines.append(
        "Evaluated on the non-empty-gold subset per the post-hoc finding "
        "above -- a metric-mechanics correction to where the panel actually "
        "carries signal, not a threshold change. The locked thresholds "
        "themselves are unchanged from the predeclaration."
    )
    lines.append("")
    react_wins, react_losses = gate_results[("single_agent_tools_react", "single_greedy")]
    angle1_pass = react_wins >= 5 and react_losses <= 1
    lines.append(
        f"- Angle 1 gate (react vs greedy): wins={react_wins} losses={react_losses} -> "
        f"{'PASS' if angle1_pass else 'FAIL'} (locked threshold: wins>=5, losses<=1)"
    )
    orch_wins, orch_losses = gate_results[
        ("multi_agent_dynamic_orchestrator", "multi_agent_d3_static")
    ]
    dynamism_pass = orch_wins >= 3 and orch_losses <= 1
    lines.append(
        f"- Angle 2 dynamism gate (dynamic orchestrator vs d3-static): "
        f"wins={orch_wins} losses={orch_losses} -> "
        f"{'PASS' if dynamism_pass else 'FAIL'} (locked threshold: wins>=3, losses<=1)"
    )

    lines.append("")
    lines.append("## Claim Boundary")
    lines.append("")
    lines.append(
        "dev140-only, aggregate + per-letter F1 on a fixed hard panel; "
        "no test59/test450 use, no holdout row-level inspection, no benchmark claim."
    )

    RESULTS_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report written to {RESULTS_REPORT}")
    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["run", "report"], required=True)
    args = parser.parse_args()
    if args.stage == "run":
        run_stage()
    else:
        report_stage()


if __name__ == "__main__":
    main()
