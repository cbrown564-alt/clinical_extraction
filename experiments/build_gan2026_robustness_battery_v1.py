"""Gan 2026 Robustness Battery v1 — predeclared OOD / overfit gate driver.

This is fitness tier 2 (OOD / robustness survival) for the F1 dynamic workflow
(``). It scores a
candidate live on `gpt-4.1-mini` against three predeclared panels of
*authored-fresh* cases (NOT Gan rows, NOT test450):

- Panel A — synthetic minimal-pair hard-negatives (overfit trap). A pair passes
  only if BOTH sides are Purist-correct; a pair correct only on the "quantify"
  side is the overfit signature.
- Panel B — source-near perturbations of the 7 core validation failure
  situations (lexical-overfit trap).
- Panel C — KCL-style out-of-distribution real-letter prose (transfer estimate).

Pass bars are predeclared in
`experiments/gan2026_robustness_battery_v1_predeclaration_2026-06-15.md` and are
NOT changed here. Gold monthly frequency and Purist category are computed from
each authored `gold_label` with the project normalizer + `labels.map_purist`
(never hardcoded). The candidate is the current best holdout family: the
LLM-only direct labeler (prompt v0.5 in code, the post-unknown-policy state) on
`openai/gpt-4.1-mini`, temperature 0.

The run is resumable: each panel's raw model outputs are checkpointed to a JSONL
and reused on a re-run, so a live battery never re-pays for completed cases.

NEVER reads or runs test450.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_direct_labeler as labeler,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

CASES_PATH = EXPERIMENTS / "gan2026_robustness_battery_v1_cases.json"
PREDECLARATION_PATH = (
    EXPERIMENTS / "gan2026_robustness_battery_v1_predeclaration_2026-06-15.md"
)

RUN_ID = "gan2026_robustness_battery_v1_gpt41mini_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"
CHECKPOINT_DIR = EXPERIMENTS / "gan2026_robustness_battery_v1_checkpoints"

DATE = "2026-06-15"
MODEL = "openai/gpt-4.1-mini"
TEMPERATURE = 0.0
MAX_TOKENS = 900

# Stable synthetic source_row_index per case id so checkpoint reuse keys are
# deterministic and never collide with real Gan source_row_index values.
_INDEX_BASE = 990000

PANELS = ("A_minimal_pairs", "B_source_near_perturbations", "C_kcl_style_ood")

# Predeclared bars (mirrors the predeclaration doc; not changed here).
PANEL_B_MIN_CORRECT = 6  # of 7
PANEL_C_MIN_FRACTION = 0.80


def main() -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    panels = cases["panels"]
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

    panel_results: dict[str, Any] = {}
    for panel in PANELS:
        panel_results[panel] = _run_panel(panel, panels[panel])

    summary = _judge(panel_results)
    payload = {
        "run_id": RUN_ID,
        "date": DATE,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "candidate": (
            "llm_only_direct_labeler (prompt v0.5, post-unknown-policy state) "
            "live on openai/gpt-4.1-mini, temperature 0"
        ),
        "cases_artifact": str(CASES_PATH.relative_to(ROOT)),
        "predeclaration": str(PREDECLARATION_PATH.relative_to(ROOT)),
        "evidence_validity": (
            "Authored-fresh OOD/adversarial cases (NOT Gan rows, NOT test450). "
            "Gold monthly frequency and Purist category computed from each "
            "authored gold_label via the project normalizer + labels.map_purist. "
            "Live gpt-4.1-mini, temperature 0. This is a transfer/overfit "
            "estimate, not a holdout benchmark."
        ),
        "panels": panel_results,
        "summary": summary,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(summary)
    print(json.dumps(summary, indent=2, sort_keys=True))


def _case_index(panel: str, case_id: str) -> int:
    # Deterministic per-case synthetic index; panel offset keeps them disjoint.
    panel_offset = PANELS.index(panel) * 1000
    digits = "".join(ch for ch in case_id if ch.isdigit()) or "0"
    # Combine the numeric part with a small per-letter spread to stay unique.
    letter_spread = sum(ord(ch) for ch in case_id if ch.isalpha())
    return _INDEX_BASE + panel_offset + int(digits) * 4 + (letter_spread % 4)


def _build_record(panel: str, case: dict[str, Any]) -> GanFrequencyRecord:
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


def _run_panel(panel: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    records = [_build_record(panel, case) for case in cases]
    index_to_case = {rec.source_row_index: case for rec, case in zip(records, cases)}

    checkpoint_jsonl = CHECKPOINT_DIR / f"{RUN_ID}_{panel}.jsonl"
    checkpoint_report = CHECKPOINT_DIR / f"{RUN_ID}_{panel}.md"

    reuse_raw_outputs: dict[int, str] = {}
    if checkpoint_jsonl.exists():
        reuse_raw_outputs = labeler.load_reusable_raw_outputs(checkpoint_jsonl)

    rows, _meta = labeler.run_split(
        records,
        split="robustness_battery",
        split_manifest="authored_v1",
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        mode="live",
        dspy_cache=True,
        api_base=None,
        reuse_raw_outputs=reuse_raw_outputs or None,
        reuse_source=str(checkpoint_jsonl) if reuse_raw_outputs else None,
        escalation_reason=None,
        progress_every=1,
        checkpoint_jsonl_path=checkpoint_jsonl,
        checkpoint_report_path=checkpoint_report,
    )
    # Persist final state so a subsequent run is fully resumable.
    labeler.write_jsonl(rows, checkpoint_jsonl)

    scored: list[dict[str, Any]] = []
    for row in rows:
        case = index_to_case[row["source_row_index"]]
        decision = row.get("decision_record") or {}
        comparison = row.get("comparison") or {}
        gold_purist = str(map_purist(row["reference"]["gold_monthly_frequency"]))
        scored.append(
            {
                "id": case["id"],
                "axis": case.get("axis", ""),
                "expected_unknown": bool(case.get("expected_unknown")),
                "pair": case.get("pair"),
                "gold_label": case["gold_label"],
                "gold_purist": gold_purist,
                "predicted_label": decision.get("final_label"),
                "predicted_purist": comparison.get("predicted_purist_category"),
                "purist_correct": bool(comparison.get("purist_correct")),
                "call_error": row.get("call_error"),
                "parse_errors": row.get("parse_errors") or [],
            }
        )

    panel_summary = {
        "panel": panel,
        "cases": len(scored),
        "purist_correct": sum(s["purist_correct"] for s in scored),
        "call_failures": sum(bool(s["call_error"]) for s in scored),
        "rows": scored,
    }
    if panel == "A_minimal_pairs":
        panel_summary["pairs"] = _score_pairs(scored)
    return panel_summary


def _score_pairs(scored: list[dict[str, Any]]) -> dict[str, Any]:
    by_pair: dict[str, list[dict[str, Any]]] = {}
    for s in scored:
        by_pair.setdefault(str(s["pair"]), []).append(s)
    pair_records: list[dict[str, Any]] = []
    both_correct = 0
    overfit_only = 0  # only the quantify (expected_unknown=False) side is correct
    for pair_id, sides in sorted(by_pair.items()):
        quantify = [s for s in sides if not s["expected_unknown"]]
        unknown = [s for s in sides if s["expected_unknown"]]
        all_correct = all(s["purist_correct"] for s in sides)
        quantify_correct = all(s["purist_correct"] for s in quantify) if quantify else None
        unknown_correct = all(s["purist_correct"] for s in unknown) if unknown else None
        # Overfit signature: the easy/quantify side is right but the hard
        # (expected_unknown or otherwise) side is wrong.
        is_overfit_only = bool(quantify) and quantify_correct and not all_correct
        if all_correct:
            both_correct += 1
        if is_overfit_only:
            overfit_only += 1
        pair_records.append(
            {
                "pair": pair_id,
                "axis": sides[0]["axis"],
                "both_correct": all_correct,
                "quantify_side_correct": quantify_correct,
                "unknown_side_correct": unknown_correct,
                "overfit_only": is_overfit_only,
                "sides": [
                    {
                        "id": s["id"],
                        "expected_unknown": s["expected_unknown"],
                        "purist_correct": s["purist_correct"],
                        "predicted_label": s["predicted_label"],
                    }
                    for s in sides
                ],
            }
        )
    return {
        "pairs": len(pair_records),
        "both_correct_pairs": both_correct,
        "overfit_only_pairs": overfit_only,
        "records": pair_records,
    }


def _judge(panel_results: dict[str, Any]) -> dict[str, Any]:
    a = panel_results["A_minimal_pairs"]
    b = panel_results["B_source_near_perturbations"]
    c = panel_results["C_kcl_style_ood"]

    a_pairs = a["pairs"]
    a_pass = (
        a_pairs["both_correct_pairs"] == a_pairs["pairs"]
        and a_pairs["overfit_only_pairs"] == 0
    )
    b_pass = b["purist_correct"] >= PANEL_B_MIN_CORRECT
    c_fraction = c["purist_correct"] / c["cases"] if c["cases"] else 0.0
    c_pass = c_fraction >= PANEL_C_MIN_FRACTION

    if a_pass and b_pass and c_pass:
        verdict = "transfers"
    elif not (a_pass or b_pass or c_pass):
        verdict = "overfit"
    else:
        # Some bars pass, some fail: not a clean transfer, not a total collapse.
        verdict = "overfit"

    failing_cases = []
    for panel in PANELS:
        for row in panel_results[panel]["rows"]:
            if not row["purist_correct"]:
                failing_cases.append(
                    {
                        "panel": panel,
                        "id": row["id"],
                        "axis": row["axis"],
                        "gold_purist": row["gold_purist"],
                        "predicted_label": row["predicted_label"],
                        "predicted_purist": row["predicted_purist"],
                    }
                )

    # Weakest axis = axis with the most failures across all panels.
    axis_fail: dict[str, int] = {}
    axis_total: dict[str, int] = {}
    for panel in PANELS:
        for row in panel_results[panel]["rows"]:
            axis_total[row["axis"]] = axis_total.get(row["axis"], 0) + 1
            if not row["purist_correct"]:
                axis_fail[row["axis"]] = axis_fail.get(row["axis"], 0) + 1
    weakest_axis = (
        max(axis_fail.items(), key=lambda kv: (kv[1], kv[1] / axis_total[kv[0]]))[0]
        if axis_fail
        else None
    )

    return {
        "verdict": verdict,
        "panel_A": {
            "pass": a_pass,
            "pairs": a_pairs["pairs"],
            "both_correct_pairs": a_pairs["both_correct_pairs"],
            "overfit_only_pairs": a_pairs["overfit_only_pairs"],
            "case_purist_correct": a["purist_correct"],
            "cases": a["cases"],
            "bar": "every pair both-correct, zero overfit-only pairs",
        },
        "panel_B": {
            "pass": b_pass,
            "purist_correct": b["purist_correct"],
            "cases": b["cases"],
            "bar": f">= {PANEL_B_MIN_CORRECT}/{b['cases']} correct, trigger-word-independent",
        },
        "panel_C": {
            "pass": c_pass,
            "purist_correct": c["purist_correct"],
            "cases": c["cases"],
            "fraction": round(c_fraction, 4),
            "bar": f">= {int(PANEL_C_MIN_FRACTION * 100)}% correct",
        },
        "failing_cases": failing_cases,
        "weakest_axis": weakest_axis,
        "axis_failure_counts": dict(sorted(axis_fail.items())),
    }


def _markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    a, b, c = s["panel_A"], s["panel_B"], s["panel_C"]
    lines = [
        "# Gan 2026 Robustness Battery v1 — Result",
        "",
        f"Date: {payload['date']}",
        "",
        "Fitness tier 2 (OOD / robustness survival) for the F1 dynamic workflow. "
        "This is the predeclared overfit/transfer gate; it does not read or run "
        "test450. Cases are authored-fresh (NOT Gan rows). Gold Purist is computed "
        "from each authored label via the project normalizer + `labels.map_purist`.",
        "",
        f"Candidate: {payload['candidate']}",
        "",
        f"Predeclaration: `{payload['predeclaration']}`",
        f"Cases: `{payload['cases_artifact']}`",
        "",
        "## Verdict",
        "",
        f"**{s['verdict']}**",
        "",
        "| Panel | Result | Bar | Pass |",
        "| --- | --- | --- | :---: |",
        (
            f"| A (minimal pairs) | {a['both_correct_pairs']}/{a['pairs']} pairs "
            f"both-correct; {a['overfit_only_pairs']} overfit-only "
            f"({a['case_purist_correct']}/{a['cases']} cases) | {a['bar']} | "
            f"{'yes' if a['pass'] else 'NO'} |"
        ),
        (
            f"| B (source-near) | {b['purist_correct']}/{b['cases']} correct | "
            f"{b['bar']} | {'yes' if b['pass'] else 'NO'} |"
        ),
        (
            f"| C (KCL OOD) | {c['purist_correct']}/{c['cases']} correct "
            f"({c['fraction']:.0%}) | {c['bar']} | {'yes' if c['pass'] else 'NO'} |"
        ),
        "",
        f"Weakest clinical axis: `{s['weakest_axis']}`",
        f"Axis failure counts: `{s['axis_failure_counts']}`",
        "",
        "## Failing cases",
        "",
    ]
    if not s["failing_cases"]:
        lines.append("None.")
    else:
        lines.append("| Panel | Case | Axis | Gold Purist | Predicted | Pred Purist |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for f in s["failing_cases"]:
            lines.append(
                f"| {f['panel']} | {f['id']} | {f['axis']} | {f['gold_purist']} | "
                f"{f['predicted_label']} | {f['predicted_purist']} |"
            )
    lines.extend(["", "## Panel A — minimal-pair detail", "", "| Pair | Axis | Both correct | Quantify side | Unknown/hard side | Overfit-only |", "| --- | --- | :---: | :---: | :---: | :---: |"])
    for rec in payload["panels"]["A_minimal_pairs"]["pairs"]["records"]:
        lines.append(
            f"| {rec['pair']} | {rec['axis']} | "
            f"{'yes' if rec['both_correct'] else 'no'} | "
            f"{_tri(rec['quantify_side_correct'])} | "
            f"{_tri(rec['unknown_side_correct'])} | "
            f"{'yes' if rec['overfit_only'] else 'no'} |"
        )
    for panel in PANELS:
        lines.extend(["", f"## {panel} — rows", "", "| Case | Axis | Gold Purist | Predicted | Pred Purist | Correct |", "| --- | --- | --- | --- | --- | :---: |"])
        for row in payload["panels"][panel]["rows"]:
            lines.append(
                f"| {row['id']} | {row['axis']} | {row['gold_purist']} | "
                f"{row['predicted_label']} | {row['predicted_purist']} | "
                f"{'yes' if row['purist_correct'] else 'no'} |"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This baseline quantifies how much of the component-generation wall is "
            "surface-overfit versus genuine clinical gap. A `transfers` verdict "
            "requires all three predeclared bars; anything less is reported as "
            "`overfit` (or `inconclusive` only on wiring failure) and sent back as "
            "`revise`. Failure is the informative outcome and is reported verbatim.",
            "",
        ]
    )
    return "\n".join(lines)


def _tri(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


def _register(summary: dict[str, Any]) -> None:
    decision = "promote" if summary["verdict"] == "transfers" else "revise"
    entries = [
        entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID
    ]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{CASES_PATH.name}",
            ),
            date=DATE,
            pipeline_family="robustness_battery_generalization_adversary",
            split="validation",
            row_count=sum(
                summary[f"panel_{p}"]["cases"] for p in ("A", "B", "C")
            ),
            model=MODEL,
            model_role=(
                "LLM-only direct labeler scored live on authored-fresh OOD / "
                "adversarial cases for synthetic-artifact overfit and transfer."
            ),
            mode="live",
            replay_status="live",
            repair_mode="robustness_battery_v1",
            cache_reuse_source=str(CHECKPOINT_DIR.relative_to(ROOT)),
            primary_metrics={
                "verdict": summary["verdict"],
                "panel_A_both_correct_pairs": summary["panel_A"]["both_correct_pairs"],
                "panel_A_pairs": summary["panel_A"]["pairs"],
                "panel_A_overfit_only_pairs": summary["panel_A"]["overfit_only_pairs"],
                "panel_A_pass": summary["panel_A"]["pass"],
                "panel_B_correct": summary["panel_B"]["purist_correct"],
                "panel_B_cases": summary["panel_B"]["cases"],
                "panel_B_pass": summary["panel_B"]["pass"],
                "panel_C_correct": summary["panel_C"]["purist_correct"],
                "panel_C_cases": summary["panel_C"]["cases"],
                "panel_C_fraction": summary["panel_C"]["fraction"],
                "panel_C_pass": summary["panel_C"]["pass"],
                "weakest_axis": summary["weakest_axis"],
            },
            evidence_validity=(
                "Authored-fresh OOD/adversarial cases (NOT Gan rows, NOT test450 "
                "holdout). Gold Purist computed from authored labels via the "
                "project normalizer + labels.map_purist. Live gpt-4.1-mini, "
                "temperature 0. Transfer/overfit estimate, not a holdout benchmark."
            ),
            decision=decision,
            claim_language_notes=(
                "Fitness tier 2 robustness gate. 'transfers' is necessary (not "
                "sufficient) for Freeze Warden test450 authorisation; any failed "
                "bar returns the candidate as revise."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
