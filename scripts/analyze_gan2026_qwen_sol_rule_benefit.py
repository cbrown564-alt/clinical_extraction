from __future__ import annotations

# ruff: noqa: E501
import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluate import (
    convert_to_categories,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_frequency_record,
)

ROOT = Path(__file__).resolve().parents[1]
PANEL_ROOT = ROOT / "experiments" / "gan2026_six_model_validation_20260718"
ATTRIBUTION_PATH = ROOT / "experiments" / "gan2026_six_model_post_panel_attribution_20260720.json"
OUTPUT_JSON = ROOT / "experiments" / "gan2026_qwen_sol_rule_benefit_audit_20260720.json"
OUTPUT_MD = (
    ROOT / "docs" / "experiments" / "gan2026" / "gan2026_qwen_sol_rule_benefit_audit_2026-07-20.md"
)
PROTOCOL = "docs/experiments/gan2026/gan2026_qwen_sol_rule_benefit_audit_protocol_2026-07-20.md"

MODELS = {
    "qwen36_35b": "Qwen 3.6:35B",
    "gpt56sol": "GPT-5.6 Sol",
}
METHODS = ("llm_only", "llm_with_rules")

REGRESSION_INTERPRETATIONS = {
    2459: (
        "The deterministic diary logic overwrites Qwen's selected recent `7 to 9 per 2 weeks` "
        "with the older calendar total `5 per 5 month`. This is a clear temporal/denominator "
        "over-rule on this row."
    ),
    2932: (
        "Both models explicitly select the current seizure-free statement and mark the February "
        "and March counts historical. Fixed code nevertheless sums those historical counts to "
        "`13 per 2 month`. This is a shared deterministic temporal regression, not a Qwen-specific one."
    ),
    6368: (
        "The apparent Qwen raw correctness is a scorer/normalizer artifact: the unsupported vague "
        "label `multiple per week` maps to the numeric unknown sentinel. It is not clean evidence "
        "that fixed code overwrote a clinically correct Qwen decision."
    ),
    10183: (
        "Qwen selects unknown because the general cluster pattern is explicitly not countable; "
        "fixed code promotes two uncertain nocturnal episodes in six weeks to the final rate. "
        "Against the Gan reference, this is a clear deterministic uncertainty-boundary over-rule."
    ),
    10542: (
        "The note gives two to four events per cluster but says cluster frequency is not tracked. "
        "Fixed code turns the three-month diary observation window into `2 to 4 per 3 month`, "
        "inventing a cluster cadence. This is a clear deterministic denominator error."
    ),
    12979: (
        "Qwen selects the stated three seizures in the current year. Fixed code first derives the "
        "reference-compatible `3 per 4 month`, then overwrites it with `4 per 3 month` even though "
        "only three events are listed. This is a deterministic calendar aggregation error."
    ),
    16161: (
        "Sol selects the current seven-per-month burden. Fixed code aggregates `11 per 3 month`, "
        "omitting the seven August events; the reference uses all 18 July-to-September events. "
        "This is a deterministic diary aggregation error."
    ),
    16774: (
        "Fixed code sums the 19 events listed across November, February, March, and May but uses a "
        "four-month denominator instead of the seven-month observation span. The error is in "
        "deterministic denominator construction, not Qwen's selected current fact."
    ),
}


def load_jsonl(path: Path) -> dict[int, dict[str, Any]]:
    rows: dict[int, dict[str, Any]] = {}
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            index = int(row["source_row_index"])
            if index in rows:
                raise ValueError(f"duplicate source_row_index {index} in {path}")
            rows[index] = row
    return rows


def correct(row: dict[str, Any]) -> bool:
    return bool((row.get("comparison") or {}).get("purist_correct"))


def compact_space(value: Any) -> str:
    return " ".join(str(value or "").split())


def clipped(value: Any, limit: int = 280) -> str:
    text = compact_space(value)
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def md(value: Any) -> str:
    return compact_space(value).replace("|", "\\|").replace("\n", " ")


def bool_word(value: bool) -> str:
    return "correct" if value else "wrong"


def label_family(label: Any) -> str:
    text = compact_space(label).lower()
    if not text:
        return "missing"
    if "no seizure frequency reference" in text or text == "no_reference":
        return "no_reference"
    if "unknown" in text or "unresolved" in text:
        return "unknown"
    if "seizure free" in text or "seizure-free" in text:
        return "seizure_free"
    if "cluster" in text:
        return "cluster"
    return "frequency"


def purist_category(label: Any) -> str | None:
    text = compact_space(label)
    if not text:
        return None
    try:
        monthly = float(label_to_frequency_record(text).monthly_frequency)
    except (TypeError, ValueError):
        return None
    return str(convert_to_categories([monthly], method="purist")[0])


def scoring_error(gold: str, predicted: str) -> str:
    gold_family = label_family(gold)
    predicted_family = label_family(predicted)
    if not predicted:
        return "no scorable final answer was retained"
    if gold_family == predicted_family:
        if gold_family in {"frequency", "cluster"}:
            return (
                "the selected count, denominator, or Gan frequency band differs from the reference"
            )
        if gold_family == "seizure_free":
            return "the seizure-free duration differs from the reference"
        return "the sentinel choice is close in kind but not Purist-equivalent to the reference"
    explanations = {
        ("frequency", "unknown"): "countable frequency evidence was reduced to unknown",
        ("cluster", "unknown"): "renderable cluster evidence was reduced to unknown",
        ("unknown", "frequency"): "an uncertain burden was converted into a specific rate",
        (
            "no_reference",
            "frequency",
        ): "the pipeline inferred a rate where the reference records no usable frequency",
        (
            "no_reference",
            "unknown",
        ): "the pipeline treated absence of usable frequency as an unknown clinical burden",
        (
            "unknown",
            "no_reference",
        ): "the pipeline treated an discussed-but-unquantified burden as no reference",
        (
            "seizure_free",
            "frequency",
        ): "active-frequency evidence was preferred over the reference seizure-free state",
        (
            "frequency",
            "seizure_free",
        ): "a seizure-free statement displaced the reference active frequency",
        ("seizure_free", "unknown"): "the explicit remission interval was reduced to unknown",
        ("unknown", "seizure_free"): "an uncertain burden was promoted to seizure-free",
    }
    return explanations.get(
        (gold_family, predicted_family),
        f"the pipeline selected {predicted_family} instead of the reference {gold_family} state",
    )


def extract_note(row: dict[str, Any]) -> str:
    try:
        payload = json.loads(row.get("prompt_input_json") or "{}")
    except json.JSONDecodeError:
        return ""
    return compact_space(payload.get("note_text"))


def direct_stage(row: dict[str, Any], attribution: dict[str, Any]) -> dict[str, Any]:
    trace = row.get("row_trace") or {}
    record = (trace.get("model_prediction") or {}).get("record") or {}
    adapter = trace.get("deterministic_adapter") or {}
    comparison = row.get("comparison") or {}
    return {
        "raw_label": compact_space(record.get("final_label")),
        "raw_purist_correct": bool(attribution.get("model_boundary_purist_correct")),
        "raw_purist_category": purist_category(record.get("final_label")),
        "raw_evidence": compact_space(record.get("evidence")),
        "raw_rationale": compact_space(record.get("rationale")),
        "final_label": compact_space(adapter.get("after_label") or record.get("final_label")),
        "final_purist_correct": bool(comparison.get("purist_correct")),
        "final_purist_category": comparison.get("predicted_purist_category"),
        "adapter_events": list(adapter.get("events") or []),
        "evidence_valid": bool((trace.get("evidence_validation") or {}).get("exact_substring")),
        "first_failure_owner": attribution.get("first_failure_owner"),
        "clinical_subproblem": attribution.get("clinical_subproblem"),
    }


def event_stage(row: dict[str, Any], attribution: dict[str, Any]) -> dict[str, Any]:
    trace = row.get("row_trace") or {}
    model_record = (trace.get("model_prediction") or {}).get("record") or {}
    raw_selection = model_record.get("selection") or {}
    final_record = row.get("structured_record") or {}
    final_selection = final_record.get("selection") or {}
    semantic = trace.get("deterministic_semantic") or {}
    events = []
    for event in model_record.get("events") or []:
        events.append(
            {
                "event_id": event.get("event_id"),
                "kind": event.get("kind"),
                "temporality": event.get("temporality"),
                "raw_value": compact_space(event.get("raw_value")),
                "evidence": compact_space(event.get("evidence")),
            }
        )
    comparison = row.get("comparison") or {}
    final_label = compact_space(
        semantic.get("after_label")
        or final_selection.get("final_label")
        or raw_selection.get("final_label")
    )
    return {
        "raw_label": compact_space(raw_selection.get("final_label")),
        "raw_purist_correct": bool(attribution.get("model_boundary_purist_correct")),
        "raw_purist_category": purist_category(raw_selection.get("final_label")),
        "raw_evidence": compact_space(raw_selection.get("evidence")),
        "raw_rationale": compact_space(raw_selection.get("rationale")),
        "raw_selected_event_ids": list(raw_selection.get("selected_event_ids") or []),
        "raw_events": events,
        "final_label": final_label,
        "final_purist_correct": bool(comparison.get("purist_correct")),
        "final_purist_category": comparison.get("predicted_purist_category"),
        "semantic_events": list(semantic.get("events") or []),
        "format_events": list((trace.get("format_repair") or {}).get("events") or []),
        "evidence_valid": bool((trace.get("evidence_validation") or {}).get("exact_substring")),
        "first_failure_owner": attribution.get("first_failure_owner"),
        "clinical_subproblem": attribution.get("clinical_subproblem"),
    }


def transition_comment(
    stage: dict[str, Any], gold: str, gold_category: str, stage_name: str
) -> str:
    raw_correct = stage["raw_purist_correct"]
    final_correct = stage["final_purist_correct"]
    raw_label = stage["raw_label"] or "<missing>"
    final_label = stage["final_label"] or "<missing>"
    events = stage.get("semantic_events") or stage.get("adapter_events") or []
    event_text = "; ".join(compact_space(event) for event in events)
    if raw_correct and final_correct:
        effect = "preserved a raw Purist-correct category"
    elif not raw_correct and final_correct:
        effect = "rescued a raw Purist-wrong category"
    elif raw_correct and not final_correct:
        if label_family(raw_label) != label_family(gold):
            effect = (
                "changed a scorer-correct raw category to a wrong category, but the raw label's "
                "clinical kind differs from the gold label and may reflect sentinel normalization"
            )
        else:
            effect = "regressed a raw Purist-correct category; this is direct row-level over-rule evidence"
    else:
        effect = "left a raw error unresolved"
    detail = ""
    if not final_correct:
        detail = f"; {scoring_error(gold, final_label)}"
    event_detail = (
        f" through `{event_text}`" if event_text else " without a recorded label-changing event"
    )
    return (
        f"{stage_name} {effect}: `{raw_label}` ({stage.get('raw_purist_category')}) → "
        f"`{final_label}` ({stage.get('final_purist_category')}){event_detail}{detail}."
    )


def row_comment(row: dict[str, Any]) -> str:
    gold = row["gold_label"]
    gold_category = row["gold_purist_category"]
    qwen = row["models"]["qwen36_35b"]
    sol = row["models"]["gpt56sol"]
    pieces = [
        transition_comment(qwen["llm_only"], gold, gold_category, "Qwen direct-label"),
        transition_comment(qwen["llm_with_rules"], gold, gold_category, "Qwen event-ledger"),
        transition_comment(sol["llm_only"], gold, gold_category, "Sol direct-label"),
        transition_comment(sol["llm_with_rules"], gold, gold_category, "Sol event-ledger"),
    ]
    q_final = qwen["llm_with_rules"]
    s_final = sol["llm_with_rules"]
    if q_final["final_purist_correct"] and not s_final["final_purist_correct"]:
        contrast = (
            "After the full deterministic policy, Qwen reaches the reference category while Sol does not. "
            f"The decisive recorded subproblem is Qwen `{q_final['clinical_subproblem']}` versus "
            f"Sol `{s_final['clinical_subproblem']}`, with Sol's first failure owned by "
            f"`{s_final['first_failure_owner']}`."
        )
    elif s_final["final_purist_correct"] and not q_final["final_purist_correct"]:
        contrast = (
            "After the full deterministic policy, Sol reaches the reference category while Qwen does not. "
            f"Qwen's first failure is owned by `{q_final['first_failure_owner']}` in "
            f"`{q_final['clinical_subproblem']}`."
        )
    elif not q_final["final_purist_correct"] and not s_final["final_purist_correct"]:
        if q_final["final_label"] == s_final["final_label"]:
            contrast = (
                "Both full pipelines converge on the same wrong label, indicating a shared "
                "selection/normalization failure or a Gan reference-policy mismatch rather than a "
                "Qwen-specific rule benefit."
            )
        else:
            contrast = (
                "Both full pipelines remain wrong but choose different labels, so this is not one "
                "shared deterministic overwrite; their extracted facts or selected clinical paths differ."
            )
    else:
        contrast = (
            "Both full event-ledger pipelines reach the reference category; this row is included because at "
            "least one direct-label condition was wrong, so it is a rescue comparison rather than a "
            "remaining hybrid error."
        )
    pieces.append(contrast)
    if row["source_row_index"] in REGRESSION_INTERPRETATIONS:
        pieces.append(REGRESSION_INTERPRETATIONS[row["source_row_index"]])
    return " ".join(pieces)


def transition_counts(
    rows: dict[int, dict[str, Any]], raw_key: str, final_key: str
) -> dict[str, int]:
    counts = Counter((bool(row[raw_key]), bool(row[final_key])) for row in rows.values())
    return {
        "wrong_to_correct": counts[(False, True)],
        "correct_to_wrong": counts[(True, False)],
        "unchanged_correct": counts[(True, True)],
        "unchanged_wrong": counts[(False, False)],
        "net_gain": counts[(False, True)] - counts[(True, False)],
    }


def build() -> dict[str, Any]:
    source: dict[str, dict[str, dict[int, dict[str, Any]]]] = {}
    expected_indices: set[int] | None = None
    for slug in MODELS:
        source[slug] = {}
        for method in METHODS:
            path = PANEL_ROOT / f"{slug}--{method}.jsonl"
            rows = load_jsonl(path)
            if len(rows) != 750:
                raise ValueError(f"expected 750 rows in {path}, found {len(rows)}")
            indices = set(rows)
            if expected_indices is None:
                expected_indices = indices
            elif indices != expected_indices:
                raise ValueError(f"source-row mismatch in {path}")
            source[slug][method] = rows

    attribution_doc = json.loads(ATTRIBUTION_PATH.read_text(encoding="utf-8"))
    attribution: dict[tuple[str, str, int], dict[str, Any]] = {}
    for row in attribution_doc["rows"]:
        key = (row["model_slug"], row["method"], int(row["source_row_index"]))
        attribution[key] = row

    assert expected_indices is not None
    error_indices = sorted(
        index
        for index in expected_indices
        if any(not correct(source[slug][method][index]) for slug in MODELS for method in METHODS)
    )

    audit_rows: list[dict[str, Any]] = []
    for index in error_indices:
        reference_row = source["qwen36_35b"]["llm_with_rules"][index]
        reference = reference_row.get("reference") or {}
        comparison = reference_row.get("comparison") or {}
        audit_row: dict[str, Any] = {
            "source_row_index": index,
            "gold_label": compact_space(
                reference.get("gold_normalized_label") or reference.get("gold_label")
            ),
            "gold_purist_category": comparison.get("gold_purist_category"),
            "gold_pragmatic_category": comparison.get("gold_pragmatic_category"),
            "note_text": extract_note(reference_row),
            "models": {},
        }
        for slug in MODELS:
            direct_row = source[slug]["llm_only"][index]
            event_row = source[slug]["llm_with_rules"][index]
            audit_row["models"][slug] = {
                "llm_only": direct_stage(direct_row, attribution[(slug, "llm_only", index)]),
                "llm_with_rules": event_stage(
                    event_row, attribution[(slug, "llm_with_rules", index)]
                ),
            }
        audit_row["deterministic_regression"] = any(
            stage["raw_purist_correct"] and not stage["final_purist_correct"]
            for model in audit_row["models"].values()
            for stage in model.values()
        )
        audit_row["comment"] = row_comment(audit_row)
        audit_rows.append(audit_row)

    aggregate: dict[str, Any] = {}
    for slug in MODELS:
        direct = source[slug]["llm_only"]
        event = source[slug]["llm_with_rules"]
        matched = {
            index: {
                "direct_correct": correct(direct[index]),
                "event_correct": correct(event[index]),
            }
            for index in expected_indices
        }
        direct_layers = {
            index: {
                "raw": bool(
                    attribution[(slug, "llm_only", index)]["model_boundary_purist_correct"]
                ),
                "final": correct(direct[index]),
            }
            for index in expected_indices
        }
        event_layers = {
            index: {
                "raw": bool(
                    attribution[(slug, "llm_with_rules", index)]["model_boundary_purist_correct"]
                ),
                "final": correct(event[index]),
            }
            for index in expected_indices
        }
        aggregate[slug] = {
            "model": MODELS[slug],
            "llm_only_final_correct": sum(correct(row) for row in direct.values()),
            "llm_with_rules_final_correct": sum(correct(row) for row in event.values()),
            "between_methods": transition_counts(matched, "direct_correct", "event_correct"),
            "llm_only_raw_to_final": transition_counts(direct_layers, "raw", "final"),
            "llm_with_rules_raw_to_final": transition_counts(event_layers, "raw", "final"),
            "llm_only_evidence_valid": sum(
                bool(attribution[(slug, "llm_only", i)]["evidence_valid"]) for i in expected_indices
            ),
            "llm_with_rules_evidence_valid": sum(
                bool(attribution[(slug, "llm_with_rules", i)]["evidence_valid"])
                for i in expected_indices
            ),
            "between_method_transitions_by_subproblem": {},
        }
        transition_subproblems: Counter[tuple[str, str]] = Counter()
        for index in expected_indices:
            direct_correct = correct(direct[index])
            event_correct = correct(event[index])
            if not direct_correct and event_correct:
                transition = "wrong_to_correct"
            elif direct_correct and not event_correct:
                transition = "correct_to_wrong"
            else:
                continue
            subproblem = str(attribution[(slug, "llm_with_rules", index)]["clinical_subproblem"])
            transition_subproblems[(transition, subproblem)] += 1
        aggregate[slug]["between_method_transitions_by_subproblem"] = {
            transition: {
                subproblem: transition_subproblems[(transition, subproblem)]
                for subproblem in sorted(
                    {key[1] for key in transition_subproblems if key[0] == transition}
                )
            }
            for transition in ("wrong_to_correct", "correct_to_wrong")
        }

    q_event_wrong = {
        i for i in expected_indices if not correct(source["qwen36_35b"]["llm_with_rules"][i])
    }
    s_event_wrong = {
        i for i in expected_indices if not correct(source["gpt56sol"]["llm_with_rules"][i])
    }
    final_error_overlap = {
        "qwen_wrong": len(q_event_wrong),
        "sol_wrong": len(s_event_wrong),
        "both_wrong": len(q_event_wrong & s_event_wrong),
        "qwen_only_wrong": len(q_event_wrong - s_event_wrong),
        "sol_only_wrong": len(s_event_wrong - q_event_wrong),
        "union_wrong": len(q_event_wrong | s_event_wrong),
    }

    return {
        "schema_version": "gan2026.qwen_sol_rule_benefit_audit.v1",
        "protocol": PROTOCOL,
        "dataset": "Gan 2026",
        "split": "dev750",
        "split_manifest": "gan2026_split_v1",
        "row_policy": "development_row_level",
        "replay_mode": "saved_outputs_no_call",
        "scorer": "Gan Purist primary; Pragmatic secondary",
        "repair_policy": "frozen saved row traces and deterministic outputs",
        "models": MODELS,
        "row_scope": (
            "Every source row where either model is Purist-wrong in either final "
            "llm_only or final llm_with_rules condition"
        ),
        "row_count": len(audit_rows),
        "aggregate": aggregate,
        "llm_with_rules_final_error_overlap": final_error_overlap,
        "rows": audit_rows,
        "claim_boundary": (
            "No-call dev750 mechanism evidence only; not clinical validation, pristine "
            "holdout evidence, or proof that validation-tuned deterministic rules transfer."
        ),
    }


def stage_cell(stage: dict[str, Any]) -> str:
    raw_mark = "✓" if stage["raw_purist_correct"] else "✗"
    final_mark = "✓" if stage["final_purist_correct"] else "✗"
    return (
        f"raw `{md(stage['raw_label'] or '<missing>')}` {raw_mark} → "
        f"final `{md(stage['final_label'] or '<missing>')}` {final_mark}"
    )


def render_markdown(doc: dict[str, Any]) -> str:
    q = doc["aggregate"]["qwen36_35b"]
    s = doc["aggregate"]["gpt56sol"]
    lines = [
        "# Gan 2026 Qwen versus GPT-5.6 Sol: raw outputs, deterministic rules, and every error row",
        "",
        "Date: 2026-07-20  ",
        "Status: no-call development audit",
        "",
        "## Finding",
        "",
        "Qwen does **not** benefit more than Sol when deterministic processing is measured on the same saved event-ledger output. Qwen has 343 raw-boundary wrong-to-correct rescues and 7 raw-correct regressions (net +336); Sol has 389 rescues and 2 regressions (net +387). The apparent Qwen advantage in the six-model table comes from comparing two different methods and prompts: Qwen moves from 565/750 in the direct-label method to 667/750 in the event-ledger-plus-rules method (+102), whereas Sol moves from 590/750 to 655/750 (+65). That is a method-by-model interaction, not a clean estimate of rules added to an unchanged model output.",
        "",
        "There is direct evidence of deterministic over-rule on individual development rows, but it is small in the within-event-ledger comparison and is not concentrated in Qwen strongly enough to explain its aggregate advantage: 7 Qwen rows and 2 Sol rows change from raw Purist-correct to final wrong. Because the deterministic policy was developed on Gan validation data, policy-level validation overfitting remains possible. The retained aggregate-only test result does not show Qwen-specific collapse—Qwen falls from 667/750 (0.8893) to 367/450 (0.8156), while Sol falls from 655/750 (0.8733) to 358/450 (0.7956)—but the test was previously used and its rows cannot be inspected here, so it cannot clear that concern.",
        "",
        "## Why the headline comparison is confounded",
        "",
        "| Condition | Direct-label `llm_only` | Event-ledger `llm_with_rules` | Difference | Wrong→correct | Correct→wrong |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
        f"| Qwen 3.6:35B | {q['llm_only_final_correct']}/750 | {q['llm_with_rules_final_correct']}/750 | +{q['llm_with_rules_final_correct'] - q['llm_only_final_correct']} | {q['between_methods']['wrong_to_correct']} | {q['between_methods']['correct_to_wrong']} |",
        f"| GPT-5.6 Sol | {s['llm_only_final_correct']}/750 | {s['llm_with_rules_final_correct']}/750 | +{s['llm_with_rules_final_correct'] - s['llm_only_final_correct']} | {s['between_methods']['wrong_to_correct']} | {s['between_methods']['correct_to_wrong']} |",
        "",
        "The direct-label prompt asks the model to choose and render one final answer. The event-ledger prompt asks it to expose source-near events, after which deterministic selection and seizure-frequency rules may change clinical meaning. These are matched evaluation conditions, but they are not a same-raw-output ablation.",
        "",
        "### Where the between-method difference comes from",
        "",
        "| Event-ledger subproblem | Qwen wrong→correct | Sol wrong→correct | Qwen correct→wrong | Sol correct→wrong |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    subproblems = sorted(
        set(q["between_method_transitions_by_subproblem"]["wrong_to_correct"])
        | set(s["between_method_transitions_by_subproblem"]["wrong_to_correct"])
        | set(q["between_method_transitions_by_subproblem"]["correct_to_wrong"])
        | set(s["between_method_transitions_by_subproblem"]["correct_to_wrong"])
    )
    for subproblem in subproblems:
        lines.append(
            f"| `{subproblem}` | "
            f"{q['between_method_transitions_by_subproblem']['wrong_to_correct'].get(subproblem, 0)} | "
            f"{s['between_method_transitions_by_subproblem']['wrong_to_correct'].get(subproblem, 0)} | "
            f"{q['between_method_transitions_by_subproblem']['correct_to_wrong'].get(subproblem, 0)} | "
            f"{s['between_method_transitions_by_subproblem']['correct_to_wrong'].get(subproblem, 0)} |"
        )
    lines.extend(
        [
            "",
            "Qwen's larger between-method gain is concentrated in cluster/diary aggregation (29 rescues versus 13 for Sol) and the seizure-free boundary (30 versus 20), with another six-rescue advantage in rate/denominator rows. Sol's direct-label method starts higher and loses more previously correct rows when switching methods, especially in rate/denominator cases (12 versus 3). This pattern says that Qwen benefits more from the event-ledger representation plus downstream policy relative to its own direct-label prompt; it does not isolate deterministic rules as the cause.",
            "",
            "## Same-saved-output rule effect",
            "",
            "| Model and method | Raw-boundary correct | Final correct | Wrong→correct | Correct→wrong | Net | Exact selected evidence |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| Qwen direct-label | 405/750 | 565/750 | {q['llm_only_raw_to_final']['wrong_to_correct']} | {q['llm_only_raw_to_final']['correct_to_wrong']} | {q['llm_only_raw_to_final']['net_gain']:+d} | {q['llm_only_evidence_valid']}/750 |",
            f"| Qwen event-ledger | 331/750 | 667/750 | {q['llm_with_rules_raw_to_final']['wrong_to_correct']} | {q['llm_with_rules_raw_to_final']['correct_to_wrong']} | {q['llm_with_rules_raw_to_final']['net_gain']:+d} | {q['llm_with_rules_evidence_valid']}/750 |",
            f"| Sol direct-label | 468/750 | 590/750 | {s['llm_only_raw_to_final']['wrong_to_correct']} | {s['llm_only_raw_to_final']['correct_to_wrong']} | {s['llm_only_raw_to_final']['net_gain']:+d} | {s['llm_only_evidence_valid']}/750 |",
            f"| Sol event-ledger | 268/750 | 655/750 | {s['llm_with_rules_raw_to_final']['wrong_to_correct']} | {s['llm_with_rules_raw_to_final']['correct_to_wrong']} | {s['llm_with_rules_raw_to_final']['net_gain']:+d} | {s['llm_with_rules_evidence_valid']}/750 |",
            "",
            "Raw-boundary correctness is scorer-defined rather than a clinical review. Source-near labels such as `up to 4 per day` can be clinically usable but Purist-wrong before benchmark normalization; conversely, the unsupported label `multiple per week` currently maps to the numeric unknown sentinel and can be Purist-correct for an unknown gold row by accident. The large raw→final gains therefore mix mechanical rendering, sentinel behavior, and deterministic clinical selection. They must not be credited wholly to clinical rules or to the model.",
            "",
            "### Same-event-ledger deterministic regressions",
            "",
            "There are nine scorer-defined raw-correct→final-wrong transitions across eight unique rows: seven Qwen transitions and two Sol transitions. Row 6368 is not clean clinical over-rule evidence because Qwen's raw `multiple per week` is counted as unknown only through sentinel normalization. The remaining rows expose concrete temporal, uncertainty, cluster-cadence, or diary-denominator failures.",
            "",
            "| Row | Model | Raw selection | Deterministic final | Gold | Interpretation |",
            "| ---: | --- | --- | --- | --- | --- |",
            "| 2459 | Qwen | `7 to 9 per 2 weeks` | `5 per 5 month` | `7 to 9 per 2 week` | Recent fortnight burden overwritten by older calendar totals. |",
            "| 2932 | Qwen + Sol | `seizure free since 29/09/2017` | `13 per 2 month` | `seizure free for 9 month` | Historical February/March counts override explicit current remission. |",
            "| 6368 | Qwen | `multiple per week` | `3 per 6 week` | `unknown` | Apparent raw correctness comes from unsupported-label→unknown sentinel mapping. |",
            "| 10183 | Qwen | `unknown` | `2 per 6 week` | `unknown` | Two uncertain nocturnal events override explicitly unquantifiable cluster pattern. |",
            "| 10542 | Qwen | `unknown` | `2 to 4 per 3 month` | `unknown, 2 to 4 per cluster` | Three-month observation window is mistaken for cluster cadence. |",
            "| 12979 | Qwen | `3 per year` | `4 per 3 month` | `3 per 4 month` | Calendar aggregation changes both count and denominator. |",
            "| 16161 | Sol | `7 per month` | `11 per 3 month` | `18 per 3 month` | Diary aggregation omits seven August events. |",
            "| 16774 | Qwen | `3 per month` | `19 per 4 month` | `19 per 7 month` | Summed events use the wrong elapsed-month denominator. |",
            "",
            "## Final event-ledger error overlap",
            "",
            f"Qwen is wrong on {doc['llm_with_rules_final_error_overlap']['qwen_wrong']} final rows and Sol on {doc['llm_with_rules_final_error_overlap']['sol_wrong']}. They share {doc['llm_with_rules_final_error_overlap']['both_wrong']} errors; Qwen alone is wrong on {doc['llm_with_rules_final_error_overlap']['qwen_only_wrong']}, and Sol alone on {doc['llm_with_rules_final_error_overlap']['sol_only_wrong']}. The union contains {doc['llm_with_rules_final_error_overlap']['union_wrong']} rows.",
            "",
            "## Row-by-row audit",
            "",
            f"The {doc['row_count']} rows below are every dev750 row where either model is Purist-wrong in either scored method. `✓` and `✗` refer to Gan Purist correctness. Full raw event records, note text, evidence, rationale, format events, and rule events are retained in the machine artifact.",
            "",
        ]
    )
    for row in doc["rows"]:
        qwen = row["models"]["qwen36_35b"]
        sol = row["models"]["gpt56sol"]
        lines.extend(
            [
                f"### Row {row['source_row_index']}: gold `{md(row['gold_label'])}`",
                "",
                "| Model | Direct-label raw → adapter | Event-ledger raw → deterministic final | Event-ledger evidence |",
                "| --- | --- | --- | --- |",
                f"| Qwen | {stage_cell(qwen['llm_only'])} | {stage_cell(qwen['llm_with_rules'])} | {md(clipped(qwen['llm_with_rules']['raw_evidence'], 180))} |",
                f"| Sol | {stage_cell(sol['llm_only'])} | {stage_cell(sol['llm_with_rules'])} | {md(clipped(sol['llm_with_rules']['raw_evidence'], 180))} |",
                "",
                f"**Audit comment:** {row['comment']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "This is development evidence on `gan2026_split_v1`, replaying saved outputs with the frozen row traces and Gan Purist scorer. It supports the conclusion that the apparent +102 versus +65 difference is not a same-output rule-addition effect, and it identifies the exact deterministic regressions on the inspected distribution. It does not prove that the shared deterministic policy transfers, that Gan reference labels are clinically infallible, or that either model is generally superior.",
            "",
            "## Sources",
            "",
            f"- Protocol: `{PROTOCOL}`",
            "- Six-model panel: `experiments/gan2026_six_model_validation_comparison_20260718.json`",
            "- Post-panel attribution: `experiments/gan2026_six_model_post_panel_attribution_20260720.json`",
            "- Machine row audit: `experiments/gan2026_qwen_sol_rule_benefit_audit_20260720.json`",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    document = build()
    rendered_json = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    rendered_md = render_markdown(document)
    if args.check:
        if not OUTPUT_JSON.exists() or OUTPUT_JSON.read_text(encoding="utf-8") != rendered_json:
            raise SystemExit(f"stale or missing {OUTPUT_JSON.relative_to(ROOT)}")
        if not OUTPUT_MD.exists() or OUTPUT_MD.read_text(encoding="utf-8") != rendered_md:
            raise SystemExit(f"stale or missing {OUTPUT_MD.relative_to(ROOT)}")
        print(f"checked {document['row_count']} audited rows")
        return
    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.relative_to(ROOT)}")
    print(f"wrote {OUTPUT_MD.relative_to(ROOT)}")
    print(f"audited rows: {document['row_count']}")


if __name__ == "__main__":
    main()
