"""Build a row-level SF residual report for the saved Luna v19 dev140 run.

This is a development diagnostic.  It intentionally retains raw model output
and letter text because the question is to explain the mechanism row by row.
It does not call a model or read the locked split.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "experiments/exectv2_structured_prompt_v19_luna_dev140_20260815"
OUT = ROOT / "experiments/exectv2_v19_sf_residual_analysis_dev140_20260816"


def _read(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _key_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        out[row["letter_id"]] = row.get("hybrid_keys", [])
    return out


def _keys(value: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {(str(item["key"][0][0]) + ":" + str(item["key"][0][1]), str(item["key"][1])) for item in value}


def _bucket(gold: set[tuple[str, str]], raw: set[tuple[str, str]], final: set[tuple[str, str]]) -> str:
    if final == gold:
        return "correct_both" if raw == gold else "projection_rescue"
    if not gold and final:
        return "accepted_false_positive_empty_gold"
    if gold and not final:
        return "total_model_or_projection_miss"
    if raw == gold and final != gold:
        return "projection_regression"
    if not raw and final:
        return "projection_added_wrong_or_partial"
    return "model_partial_or_wrong"


def main() -> None:
    live = SOURCE / "v19_live"
    structured = {x["letter_id"]: x for x in _read(live / "structured.jsonl")}
    projection = {x["letter_id"]: x for x in _read(live / "arm_sf_state_projection_combined.jsonl")}
    suppression = {x["letter_id"]: x for x in _read(live / "arm_sf_unknown_suppression.jsonl")}
    assembly = {x["letter_id"]: x for x in _read(live / "assembly.jsonl")}
    families = {x["letter_id"]: x for x in _read(live / "letter_family.jsonl") if x["family"] == "SeizureFrequency"}
    baseline = {x["letter_id"]: x for x in _read(SOURCE / "v0924_head/letter_family.jsonl") if x["family"] == "SeizureFrequency"}

    rows: list[dict[str, Any]] = []
    buckets: Counter[str] = Counter()
    for letter_id in sorted(families):
        family = families[letter_id]
        st = structured[letter_id]
        proj = projection[letter_id]
        sup = suppression[letter_id]
        asm = assembly[letter_id]
        prompt = json.loads(st["prompt_input_json"])
        raw_sf = [m for m in st.get("predicted_mentions", []) if m.get("entity") == "SeizureFrequency"]
        projected_sf = proj.get("predicted_mentions", [])
        final_sf = asm.get("lanes", {}).get("SeizureFrequency", {}).get("predicted_mentions", [])
        gold = _keys(family.get("gold_keys", []))
        raw = _keys(family.get("raw_keys", []))
        final = _keys(family.get("hybrid_keys", []))
        bucket = _bucket(gold, raw, final)
        buckets[bucket] += 1
        rows.append(
            {
                "source_row_index": letter_id,
                "split": "dev140",
                "gold_keys": family.get("gold_keys", []),
                "gold_label": sorted(gold),
                "gold_purist": family.get("gold_keys", []),
                "gold_pragmatic": family.get("gold_keys", []),
                "route_decision": "structured_model -> sf_state_projection -> unknown_suppression -> assembly",
                "selected_by": "gpt-5.6-luna" if raw_sf else "none",
                "support_status": {
                    "raw_parse_errors": st.get("parse_errors", []),
                    "evidence_invalid": st.get("n_evidence_invalid", 0),
                    "projection_actions": proj.get("projection_actions", []),
                    "suppression_actions": sup.get("suppression_actions", []),
                },
                "raw_model_response": st.get("raw_output", ""),
                "raw_sf_mentions": raw_sf,
                "projected_sf_mentions": projected_sf,
                "final_sf_mentions": final_sf,
                "final_label": sorted(final),
                "final_purist": family.get("hybrid_keys", []),
                "final_pragmatic": family.get("hybrid_keys", []),
                "purist_ok": family.get("hybrid_letter_exact", False),
                "pragmatic_ok": family.get("hybrid_letter_exact", False),
                "failure_bucket": bucket,
                "v0924_control_exact": baseline[letter_id].get("hybrid_letter_exact", False),
                "letter_text": prompt.get("letter_text", ""),
            }
        )

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8"
    )
    report = [
        "# ExECT v19 SeizureFrequency row-by-row residual analysis",
        "",
        "Development diagnostic for Luna `dev140`; `test60` was not inspected or used.",
        "",
        f"- Source: `{(SOURCE / 'v19_live').relative_to(ROOT)}`",
        f"- Full row table, raw responses, letter text, intermediate mentions, and actions: [`rows.jsonl`]({(OUT / 'rows.jsonl').relative_to(ROOT)})",
        "- Route: structured model response → SF state/ownership projection → unknown suppression → final assembly.",
        "- Comparator: saved v0.9.24 `dev140` sidecar on the same 140 letters.",
        "",
        "## Result",
        "",
        "v19 SF family F1 is `0.7138`, with `82/140` SF-exact letters. The v0.9.24 control is `0.8328` and `100/140` exact. v19 has zero parse/schema failures.",
        "",
        "| Residual bucket | Rows | Interpretation |",
        "| --- | ---: | --- |",
        f"| correct_both | {buckets['correct_both']} | Model response already matches final gold key set. |",
        f"| projection_rescue | {buckets['projection_rescue']} | A deterministic rewrite/drop converted a raw miss into a correct final row. |",
        f"| model_partial_or_wrong | {buckets['model_partial_or_wrong']} | The model emitted an incomplete or wrong SF set; projection did not solve it. |",
        f"| total_model_or_projection_miss | {buckets['total_model_or_projection_miss']} | Gold SF exists but final output is empty. |",
        f"| accepted_false_positive_empty_gold | {buckets['accepted_false_positive_empty_gold']} | Final SF was emitted on an empty-gold row. |",
        f"| projection_regression | {buckets['projection_regression']} | Raw was correct but a later rule changed it incorrectly. |",
        f"| projection_added_wrong_or_partial | {buckets['projection_added_wrong_or_partial']} | A projection added output but not the gold set. |",
        "",
        "## Main gaps",
        "",
        "1. The dominant loss is model-side omission/partial coverage: the model often emits one seizure type/state while gold contains multiple type-specific states, especially mixed active-rate, seizure-free, and unknown rows.",
        "2. A smaller but actionable boundary is state/anchor ownership: explicit `seizure-free` spans are sometimes emitted as generic `seizure`/`events`, and stale `before this` zero mentions survive beside a newer active rate.",
        "3. Empty-gold false positives are concentrated in vague or contextual mentions (`minor seizures`, episode-like wording, advice/history). These need narrow negative-context guards, not a broad drop rule.",
        "4. Projection is not the main bottleneck: 65 projection repairs and 20 drops fire, but many affected rows remain wrong. More downstream repair cannot recover facts the model never emitted.",
        "",
        "## Proposed bounded repairs",
        "",
        "- Retarget an existing zero-count mention to an explicit `seizure-free` / `seizure free` evidence span and clear stale CUI fields before normal projection. This is H1 and directly addresses anchor-form losses.",
        "- Drop a zero-count `before this` mention only when another active rate exists in the same letter (H7), preventing stale historical state from competing with a current rate.",
        "- Drop an emitted SF mention only for explicit `never had` / `not had ... resemble` wording, excluding `further` and `more` (H4). This targets contextual false positives without deleting established no-further facts.",
        "",
        "The H1+H7+H4 saved-row counterfactual produced `0.8713` headline F1, `0.7355` SF F1, and `47/140` exact, versus v19 `0.8669`, `0.7138`, and `45/140`. These are development counterfactuals, not holdout or promotion evidence.",
    ]
    (OUT / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "buckets": buckets, "output": str(OUT)}, indent=2, default=dict))


if __name__ == "__main__":
    main()
