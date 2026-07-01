"""Phase 1-2 (Tasks 13-14): run all 5 conditions over the robustness
battery (27 cases) + hard50 (50 rows), score against gold, apply the
predeclared gates.

See docs/plans/proud-bubbling-ocean.md and
docs/experiments/gan2026/agentic/gan2026_agentic_redo_predeclaration_2026-07-01.md
for the locked design/gates this script implements. Resumable: each
condition/panel/row result is checkpointed to JSONL and skipped on rerun.
NEVER reads or runs test450.

Usage:
    python experiments/gan2026_agentic_redo_battery_hard50.py --stage run
    python experiments/gan2026_agentic_redo_battery_hard50.py --stage report
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import dspy

from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    multi_agent_ceiling,
    react_single_agent,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.contracts import AgentBudget
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.runner import (
    _build_prompt_input,
    _compare_to_gold,
    _condition_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_direct_labeler import (
    LlmOnlyDirectLabelerDecisionRecord,
    parse_decision_json,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

MODEL = "openai/gpt-4.1-mini"
# Deterministic/best-effort conditions run at temperature=0.0, matching house
# convention (every reference "greedy"/production-style script in this repo
# uses temp 0). single_self_consistency_temperature is the one condition
# that must genuinely vary temperature (project convention, see
# feedback_self_consistency_varying_temperature.md) -- 0.7 is used for it
# specifically. runner.py::_run_model_call ignores its own temperature
# argument and always uses whatever LM is globally configured
# (dspy.configure), so this script switches the global config per condition
# rather than relying on runner.py to vary it internally.
DEFAULT_TEMPERATURE = 0.0
SELF_CONSISTENCY_TEMPERATURE = 0.7
MAX_TOKENS = 600
HARD50_PATH = Path("experiments/gan2026_agentic_validation_hard50_source_rows_2026-06-12.txt")
BATTERY_CASES_PATH = Path("experiments/gan2026_robustness_battery_v1_cases.json")
OUT_DIR = Path("experiments")
RESULTS_JSONL = OUT_DIR / "gan2026_agentic_redo_battery_hard50_results.jsonl"
RESULTS_REPORT = OUT_DIR / "gan2026_agentic_redo_battery_hard50_results.md"

PANELS = ("A_minimal_pairs", "B_source_near_perturbations", "C_kcl_style_ood")
INDEX_BASE = 990000  # matches build_gan2026_robustness_battery_v1.py's convention

CONDITIONS_EXISTING = ("single_greedy", "single_self_consistency_temperature")
CONDITIONS_NEW = (
    "single_agent_tools_react",
    "multi_agent_d3_static",
    "multi_agent_dynamic_orchestrator",
)
ALL_CONDITIONS = CONDITIONS_EXISTING + CONDITIONS_NEW

# Shared matched-budget bookkeeping for the two existing Angle-1 conditions
# (single_agent_tools_react's own module already defines the identical
# shape; not reused directly here to avoid a confusing cross-import).
MATCHED_BUDGET = AgentBudget(
    model_calls_per_row=4,
    prompt_token_budget=2_500,
    max_completion_tokens_per_call=600,
    max_tool_calls_per_row=3,
    max_tool_output_tokens_per_row=700,
    aggregation_budget_model_calls=1,
)


def load_hard50() -> list[GanFrequencyRecord]:
    idx = {int(line) for line in HARD50_PATH.read_text().splitlines() if line.strip()}
    records = [r for r in load_records_for_split("validation") if r.source_row_index in idx]
    assert len(records) == 50, f"expected 50 hard50 rows, got {len(records)}"
    return records


def _case_index(panel: str, case_id: str) -> int:
    panel_offset = PANELS.index(panel) * 1000
    digits = "".join(ch for ch in case_id if ch.isdigit()) or "0"
    letter_spread = sum(ord(ch) for ch in case_id if ch.isalpha())
    return INDEX_BASE + panel_offset + int(digits) * 4 + (letter_spread % 4)


def _build_battery_record(panel: str, case: dict[str, Any]) -> GanFrequencyRecord:
    fr = label_to_frequency_record(case["gold_label"])
    return GanFrequencyRecord(
        source_row_index=_case_index(panel, case["id"]),
        note_text=case["note"],
        gold_label=case["gold_label"],
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={"battery_case_id": case["id"], "axis": case.get("axis", "")},
        gold_normalized_label=fr.normalized_label,
        gold_label_kind=fr.kind,
        gold_yearly_bounds=fr.yearly_bounds,
        gold_monthly_frequency=fr.monthly_frequency,
    )


def load_battery() -> list[GanFrequencyRecord]:
    payload = json.loads(BATTERY_CASES_PATH.read_text(encoding="utf-8"))
    panels = payload["panels"]
    records = [
        _build_battery_record(panel, case) for panel in PANELS for case in panels[panel]
    ]
    assert len(records) == 27, f"expected 27 battery cases, got {len(records)}"
    return records


def _safe_compare_to_gold(
    record: GanFrequencyRecord, decision: LlmOnlyDirectLabelerDecisionRecord | None
) -> dict[str, Any] | None:
    """`_compare_to_gold` raises `ValueError` on an unparseable `final_label`
    (e.g. the model returns a vague word like "uncommon" instead of a
    normalizable rate). That is an expected occasional model failure mode,
    not a harness bug — record it as a scoring miss, don't crash the run."""
    if decision is None:
        return None
    try:
        return _compare_to_gold(record, decision)
    except ValueError as exc:
        return {
            "predicted_monthly_frequency": None,
            "gold_monthly_frequency": record.gold_monthly_frequency,
            "predicted_purist_category": None,
            "gold_purist_category": None,
            "purist_correct": False,
            "predicted_pragmatic_category": None,
            "gold_pragmatic_category": None,
            "pragmatic_correct": False,
            "unparseable_label_error": str(exc),
        }


def _placeholder_decision(final_label: str) -> LlmOnlyDirectLabelerDecisionRecord:
    """Minimal decision object for scoring conditions whose driver only
    surfaces an aggregated final_label (single_greedy/self_consistency via
    _condition_trace's majority vote), not a full decision record. Only
    `.final_label` feeds `_compare_to_gold` — the other fields are
    scoring-inert placeholders, never reported as model output."""
    return LlmOnlyDirectLabelerDecisionRecord(
        final_label=final_label,
        evidence="",
        answer_kind="frequency",
        selected_seizure_type=None,
        time_window=None,
        confidence="medium",
        rationale="",
    )


def _temperature_for(condition: str) -> float:
    return SELF_CONSISTENCY_TEMPERATURE if condition == "single_self_consistency_temperature" else DEFAULT_TEMPERATURE


def _configure_lm_for_condition(condition: str) -> None:
    dspy.configure(
        lm=build_dspy_lm(
            MODEL, temperature=_temperature_for(condition), max_tokens=MAX_TOKENS, cache=True
        )
    )


def run_condition_on_record(condition: str, record: GanFrequencyRecord) -> dict[str, Any]:
    _configure_lm_for_condition(condition)
    temperature = _temperature_for(condition)
    if condition in CONDITIONS_EXISTING:
        trace = _condition_trace(
            condition,
            record=record,
            model=MODEL,
            temperature=temperature,
            max_tokens=MAX_TOKENS,
            mode="live",
            budget=MATCHED_BUDGET,
            parser_result={},
            guide_results=[],
        )
        final_label = trace.get("final_label")
        call_errors = [
            r.get("call_error") for r in trace.get("model_call_results", []) if r.get("call_error")
        ]
        decision = _placeholder_decision(final_label) if final_label else None
        comparison = _safe_compare_to_gold(record, decision)
        return {
            "source_row_index": record.source_row_index,
            "condition": condition,
            "final_label": final_label,
            "call_error": "; ".join(call_errors) if call_errors else None,
            "parse_errors": [],
            "comparison": comparison,
        }

    prompt_input_json = _build_prompt_input(
        record,
        condition=condition,
        call_plan={"call_role": condition},
        parser_result={},
        guide_results=[],
    )

    call_error: str | None = None
    decision_json: str | None = None
    trajectory: dict[str, Any] | None = None
    try:
        if condition == "single_agent_tools_react":
            prediction = react_single_agent.run_single_row(
                prompt_input_json, note_text=record.note_text
            )
            decision_json = str(prediction.decision_json)
            trajectory = prediction.trajectory
        elif condition == "multi_agent_d3_static":
            result = multi_agent_ceiling.run_d3_static(prompt_input_json)
            decision_json = result["decision_json"]
        elif condition == "multi_agent_dynamic_orchestrator":
            prediction = multi_agent_ceiling.run_dynamic_orchestrator_row(
                prompt_input_json, note_text=record.note_text
            )
            decision_json = str(prediction.decision_json)
            trajectory = prediction.trajectory
        else:
            raise ValueError(f"Unknown condition: {condition}")
    except Exception as exc:  # pragma: no cover - live transport only
        call_error = f"{type(exc).__name__}: {exc}"

    decision, parse_errors = (
        parse_decision_json(decision_json) if decision_json else (None, ["not_run"])
    )
    comparison = _safe_compare_to_gold(record, decision)
    n_tool_turns = (
        sum(1 for key in trajectory if key.startswith("tool_name_")) if trajectory else None
    )
    return {
        "source_row_index": record.source_row_index,
        "condition": condition,
        "final_label": decision.final_label if decision else None,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "comparison": comparison,
        "n_tool_turns": n_tool_turns,
    }


def _read_completed() -> set[tuple[str, int]]:
    if not RESULTS_JSONL.exists():
        return set()
    completed = set()
    for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        completed.add((row["condition"], row["source_row_index"]))
    return completed


def run_stage() -> None:
    # LM is configured per-condition inside run_condition_on_record (see
    # _configure_lm_for_condition) since temperature varies by condition.
    battery = load_battery()
    hard50 = load_hard50()
    all_records = [("battery", r) for r in battery] + [("hard50", r) for r in hard50]

    completed = _read_completed()
    total = len(all_records) * len(ALL_CONDITIONS)
    done = len(completed)
    print(f"Resuming: {done}/{total} (condition, row) pairs already completed.")

    with RESULTS_JSONL.open("a", encoding="utf-8") as fh:
        for panel_source, record in all_records:
            for condition in ALL_CONDITIONS:
                key = (condition, record.source_row_index)
                if key in completed:
                    continue
                row = run_condition_on_record(condition, record)
                row["panel_source"] = panel_source
                fh.write(json.dumps(row) + "\n")
                fh.flush()
                done += 1
                if done % 25 == 0:
                    print(f"progress: {done}/{total}")

    print(f"Run stage complete: {done}/{total}.")


def report_stage() -> None:
    rows = [json.loads(line) for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines() if line.strip()]

    by_panel_condition: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_panel_condition[(row["panel_source"], row["condition"])].append(row)

    lines = ["# Gan 2026 Agentic Redo — Battery + Hard50 Results", ""]
    lines.append(
        "Self-contained fresh study: all 5 conditions run in this session, same "
        "settings. Not compared against the 2026-06-12 hard50 numbers -- see "
        "docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md "
        "for why that comparison was dropped (likely hosted-model drift, "
        "unverifiable and irrelevant to this run's internal validity)."
    )
    lines.append("")
    lines.append("## Condition-Final Accuracy")
    lines.append("")
    lines.append(
        "\"True failures\" = no usable answer produced at all (call error or "
        "unparseable/missing final_label) -- this is the reliability-relevant "
        "failure metric. \"Repair rate\" = the schema/label repair layer fixed a "
        "format issue but still produced a scored answer -- informative, not a "
        "failure (see predeclaration's evidence/schema-validity reporting "
        "requirement)."
    )
    lines.append("")
    lines.append("| Panel | Condition | Purist | Pragmatic | True Failures | Repair Rate |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")

    summary: dict[str, dict[str, Any]] = {}
    for panel_source in ("battery", "hard50"):
        for condition in ALL_CONDITIONS:
            panel_rows = by_panel_condition.get((panel_source, condition), [])
            n = len(panel_rows)
            purist_correct = sum(
                1 for r in panel_rows if r["comparison"] and r["comparison"]["purist_correct"]
            )
            pragmatic_correct = sum(
                1 for r in panel_rows if r["comparison"] and r["comparison"]["pragmatic_correct"]
            )
            true_failures = sum(
                1 for r in panel_rows if r.get("call_error") or r.get("final_label") is None
            )
            repairs = sum(
                1
                for r in panel_rows
                if not r.get("call_error") and r.get("final_label") is not None and r.get("parse_errors")
            )
            lines.append(
                f"| {panel_source} | {condition} | {purist_correct}/{n} | {pragmatic_correct}/{n} | "
                f"{true_failures}/{n} | {repairs}/{n} |"
            )
            summary[f"{panel_source}::{condition}"] = {
                "n": n,
                "purist_correct": purist_correct,
                "pragmatic_correct": pragmatic_correct,
                "true_failures": true_failures,
                "repairs": repairs,
            }

    lines.append("")
    lines.append("## Win/Loss vs Comparators (hard50)")
    lines.append("")
    lines.append("| Candidate | Comparator | Wins | Losses | Both correct | Both wrong |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: |")

    def win_loss(candidate: str, comparator: str, panel_source: str = "hard50") -> tuple[int, int, int, int]:
        cand_by_row = {
            r["source_row_index"]: r for r in by_panel_condition.get((panel_source, candidate), [])
        }
        comp_by_row = {
            r["source_row_index"]: r for r in by_panel_condition.get((panel_source, comparator), [])
        }
        wins = losses = both_correct = both_wrong = 0
        for idx, cand_row in cand_by_row.items():
            comp_row = comp_by_row.get(idx)
            if comp_row is None:
                continue
            cand_correct = bool(cand_row["comparison"] and cand_row["comparison"]["purist_correct"])
            comp_correct = bool(comp_row["comparison"] and comp_row["comparison"]["purist_correct"])
            if cand_correct and not comp_correct:
                wins += 1
            elif comp_correct and not cand_correct:
                losses += 1
            elif cand_correct and comp_correct:
                both_correct += 1
            else:
                both_wrong += 1
        return wins, losses, both_correct, both_wrong

    comparisons = [
        ("single_agent_tools_react", "single_greedy"),
        ("multi_agent_d3_static", "single_greedy"),
        ("multi_agent_dynamic_orchestrator", "single_greedy"),
        ("multi_agent_dynamic_orchestrator", "multi_agent_d3_static"),
    ]
    gate_results = {}
    for candidate, comparator in comparisons:
        wins, losses, both_correct, both_wrong = win_loss(candidate, comparator)
        lines.append(
            f"| {candidate} | {comparator} | {wins} | {losses} | {both_correct} | {both_wrong} |"
        )
        gate_results[(candidate, comparator)] = (wins, losses)

    lines.append("")
    lines.append("## Predeclared Gate Outcomes")
    lines.append("")
    react_wins, react_losses = gate_results[("single_agent_tools_react", "single_greedy")]
    angle1_pass = react_wins >= 5 and react_losses <= 1
    lines.append(
        f"- Angle 1 gate (single_agent_tools_react vs single_greedy, hard50): "
        f"wins={react_wins} losses={react_losses} -> "
        f"{'PASS' if angle1_pass else 'FAIL'} (locked threshold: wins>=5, losses<=1)"
    )
    orch_wins, orch_losses = gate_results[("multi_agent_dynamic_orchestrator", "multi_agent_d3_static")]
    dynamism_pass = orch_wins >= 3 and orch_losses <= 1
    lines.append(
        f"- Angle 2 dynamism gate (dynamic_orchestrator vs d3_static, hard50): "
        f"wins={orch_wins} losses={orch_losses} -> "
        f"{'PASS' if dynamism_pass else 'FAIL'} (locked threshold: wins>=3, losses<=1)"
    )

    lines.append("")
    lines.append("## Claim Boundary")
    lines.append("")
    lines.append(
        "validation-development matched-budget agentic redo; no holdout use, "
        "no row-level test450 inspection, and no benchmark claim."
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
