"""Build the focused v19 SF omission and multi-state priority study.

No model calls.  Development rows only.  The category map is an analyst
judgment over the saved row-level residual artifact and is asserted to cover
exactly the selected 7 + 42 rows.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/exectv2_v19_sf_residual_analysis_dev140_20260816/rows.jsonl"
OUT = ROOT / "experiments/exectv2_v19_sf_priority_study_dev140_20260816"

OMISSION_CATEGORIES = {
    "missed_explicit_multi_type_history": ["EA0006"],
    "missed_teenage_last_event_seizure_free": ["EA0010"],
    "missed_explicit_multi_type_active_state": ["EA0025"],
    "dropped_recent_event_after_historical_free": ["EA0038"],
    "missed_epileptic_cluster_in_mixed_dissociative_note": ["EA0135"],
    "missed_controlled_plus_uncertain_events": ["EA0136"],
    "missed_recent_single_event": ["EA0182"],
}

PARTIAL_CATEGORIES = {
    "multi_state_recall": [
        "EA0002", "EA0005", "EA0009", "EA0011", "EA0049", "EA0054", "EA0056",
        "EA0022", "EA0057", "EA0059", "EA0061", "EA0082", "EA0087", "EA0096", "EA0106",
        "EA0108", "EA0110", "EA0111", "EA0119", "EA0121", "EA0123", "EA0127",
        "EA0128", "EA0137", "EA0161", "EA0168", "EA0169", "EA0178", "EA0180",
        "EA0186", "EA0195", "EA0198",
    ],
    "anchor_or_cui_representation": [
        "EA0004", "EA0019", "EA0085", "EA0088", "EA0156", "EA0173", "EA0191",
    ],
    "state_selection_error": ["EA0139"],
    "extra_mention_after_correct_state": ["EA0046", "EA0113"],
}

RECOMMENDATIONS = {
    "missed_explicit_multi_type_history": "Prompt-side multi-state recall: require separate mentions for each explicitly named type and dated historical state; deterministic repair cannot invent both types safely.",
    "missed_teenage_last_event_seizure_free": "Gold-free deterministic candidate-span rescue or a narrowly scoped prompt exemplar for teenage last-event → seizure-free; this is a known omission pattern.",
    "missed_explicit_multi_type_active_state": "Prompt-side recall for compound type/frequency sentences, including simultaneous named-type active rate and myoclonic state.",
    "dropped_recent_event_after_historical_free": "State precedence: preserve the recent explicit event over an older seizure-free interval; do not let a generic zero sibling replace the recent named event.",
    "missed_epileptic_cluster_in_mixed_dissociative_note": "Prompt-side disambiguation: retain an explicitly clinician-attributed epileptic cluster even when the note also contains dissociative events.",
    "missed_controlled_plus_uncertain_events": "Prompt-side state completeness: emit seizure-free/controlled state and a separate unknown state for additional attacks whose nature is explicitly uncertain.",
    "missed_recent_single_event": "Prompt-side recall for recent single-event narratives; do not require a frequency cadence when the benchmark marks the event state.",
    "multi_state_recall": "Primary next prompt panel: ask for every independent type × state combination, with one mention per type/state and no collapsing into one generic seizure mention.",
    "anchor_or_cui_representation": "Deterministic projection, not prompt tuning: preserve the correct state while retargeting explicit seizure-free or generic anchor spans to the benchmark concept.",
    "state_selection_error": "Add a narrow state guard for explicit current/recent seizure evidence so a bare change cue does not fall back to unknown.",
    "extra_mention_after_correct_state": "Tighten duplicate/sibling suppression only where the extra mention repeats the same evidence and state; do not remove distinct dated events.",
}


def main() -> None:
    rows = [json.loads(line) for line in SOURCE.read_text(encoding="utf-8").splitlines() if line]
    selected = [row for row in rows if row["failure_bucket"] in {"total_model_or_projection_miss", "model_partial_or_wrong"}]
    category_by_id: dict[str, str] = {}
    for category, ids in {**OMISSION_CATEGORIES, **PARTIAL_CATEGORIES}.items():
        for letter_id in ids:
            if letter_id in category_by_id:
                raise AssertionError(f"duplicate category assignment: {letter_id}")
            category_by_id[letter_id] = category
    selected_ids = {row["source_row_index"] for row in selected}
    if selected_ids != set(category_by_id):
        raise AssertionError(f"category coverage mismatch: missing={selected_ids - set(category_by_id)} extra={set(category_by_id) - selected_ids}")

    output_rows: list[dict[str, Any]] = []
    for row in selected:
        category = category_by_id[row["source_row_index"]]
        output_rows.append({
            "source_row_index": row["source_row_index"],
            "priority_surface": "total_omission" if row["failure_bucket"] == "total_model_or_projection_miss" else "partial_or_wrong",
            "study_category": category,
            "gold_label": row["gold_label"],
            "raw_sf_mentions": row["raw_sf_mentions"],
            "projected_sf_mentions": row["projected_sf_mentions"],
            "final_sf_mentions": row["final_sf_mentions"],
            "projection_actions": row["support_status"]["projection_actions"],
            "raw_model_response": row["raw_model_response"],
            "letter_text": row["letter_text"],
            "recommendation": RECOMMENDATIONS[category],
        })

    counts = Counter(row["study_category"] for row in output_rows)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "targeted_rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in output_rows), encoding="utf-8"
    )
    report = [
        "# ExECT v19 SF priority residual study",
        "",
        "No-call development study over the 7 total omissions and 42 partial/wrong rows from the v19 Luna `dev140` residual analysis. `test60` was not inspected.",
        "",
        f"- Full targeted row evidence: [`targeted_rows.jsonl`]({(OUT / 'targeted_rows.jsonl').relative_to(ROOT)})",
        "- Each row retains raw model response, letter text, raw SF mentions, projected mentions, final mentions, and fired rules.",
        "",
        "## Category counts",
        "",
        "| Category | Rows | Recommended owner |",
        "| --- | ---: | --- |",
    ]
    for category, count in counts.most_common():
        owner = "prompt/model" if category in {"multi_state_recall", "missed_explicit_multi_type_history", "missed_explicit_multi_type_active_state", "missed_epileptic_cluster_in_mixed_dissociative_note", "missed_controlled_plus_uncertain_events", "missed_recent_single_event"} else "projection/rules"
        report.append(f"| `{category}` | {count} | {owner} |")
    report.extend([
        "",
        "## Conclusions",
        "",
        "### 1. Run a multi-state recall prompt panel first",
        "",
        f"`multi_state_recall` accounts for {counts['multi_state_recall']} of the 49 priority rows. The raw model often gets one clinically valid mention but fails to emit the other type/state combinations. The next prompt experiment should explicitly require independent type × state mentions and should be evaluated on this panel before any broader dev run.",
        "",
        "### 2. Keep deterministic work focused on representation and precedence",
        "",
        f"`anchor_or_cui_representation` accounts for {counts['anchor_or_cui_representation']} rows. These are not primarily comprehension failures: the state is often present, but the model chooses a generic or malformed anchor. The opt-in v0.20 projection is the right layer for these cases.",
        "",
        "The omission `EA0038` is a separate precedence problem: the model emitted a stale zero state, then the existing scope rule dropped it, while the recent seizure was absent. A rule should not infer the recent event, but a future prompt should be tested for “recent explicit event overrides older seizure-free context.”",
        "",
        "### 3. Treat the seven omissions as separate mechanisms",
        "",
        "They are not one recall bucket: they include dated historical multi-type states, teenage last-event seizure-free, mixed epileptic/dissociative context, controlled plus uncertain events, and a recent single event. One broad prompt instruction is unlikely to solve them without increasing false positives.",
        "",
        "## Recommended next experiment",
        "",
        "1. Build a small prompt-only multi-state panel from the 32 `multi_state_recall` rows, with no new deterministic rules.",
        "2. Add explicit output requirements for independent type × state combinations and separate unknown states.",
        "3. Test first on a predeclared subset, then transfer to all dev140 if the subset improves without empty-gold harm.",
        "4. In parallel, replay the opt-in `residuals_v020` projection against the same targeted rows and quantify only anchor/CUI and precedence changes.",
        "5. Do not inspect or tune against `test60`.",
    ])
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"selected_rows": len(output_rows), "counts": counts, "output": str(OUT)}, indent=2, default=dict))


if __name__ == "__main__":
    main()
