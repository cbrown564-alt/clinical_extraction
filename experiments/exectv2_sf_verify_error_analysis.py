"""Deep row-by-row error analysis of the SF verify program (P2 mini run).

Analyzes exectv2_gepa_sf_verify_gpt41mini_20260628 (best SF verify: clinical_headline
0.597, state_profile 0.741). For each letter, compares gold vs pred state presence
sets (4-way: seizure-free / active-rate / changed / unknown) and categorizes every
error with its evidence.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import frequency_state_faithful

ROOT = Path(__file__).resolve().parents[1]
RUN_PATH = ROOT / "experiments" / "exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl"

STATES = ("seizure-free", "active-rate", "changed", "unknown")


def _load_preds(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        out[lid] = row.get("predicted_mentions", [])
    return out


def _state_of(mention: dict) -> str:
    attrs = {str(k): str(v) for k, v in mention.get("attributes", {}).items()}
    return frequency_state_faithful(attrs)


def _state_set(mentions: list[dict]) -> set[str]:
    return {_state_of(m) for m in mentions if m.get("entity") == "SeizureFrequency"}


def _mentions_for_state(mentions: list[dict], state: str) -> list[dict]:
    return [m for m in mentions if m.get("entity") == "SeizureFrequency" and _state_of(m) == state]


def _fmt_mention(m: dict) -> str:
    text = m.get("text", "")
    attrs = m.get("attributes", {})
    state = _state_of(m)
    cui = attrs.get("CUI", "")
    cui_s = f" [{cui}]" if cui else ""
    fc = attrs.get("FrequencyChange", "")
    fc_s = f" FC={fc}" if fc else ""
    n = attrs.get("NumberOfSeizures", "")
    n_s = f" N={n}" if n else ""
    return f"{text!r}{cui_s}{fc_s}{n_s} -> {state}"


def main() -> None:
    gold_letters = list(gepa_data.load_dev_letters())
    preds = _load_preds(RUN_PATH)

    # Per-letter state presence
    error_type_counts: Counter[str] = Counter()
    errors: list[dict] = []

    for g in gold_letters:
        lid = g.letter_id
        gold_sf = [
            {"text": a.text, "attributes": dict(a.attributes), "entity": "SeizureFrequency"}
            for a in g.entities("SeizureFrequency")
        ]
        pred_sf = preds.get(lid, [])

        gold_states = _state_set(gold_sf)
        pred_states = _state_set(pred_sf)

        for state in STATES:
            in_gold = state in gold_states
            in_pred = state in pred_states

            if in_gold and in_pred:
                continue
            if not in_gold and not in_pred:
                continue

            if in_pred and not in_gold:
                # FP — over-call
                if state == "changed":
                    # Sub-categorize: what does gold have instead?
                    gold_alt = gold_states - {"changed"}
                    if gold_alt & {"active-rate"}:
                        subtype = "FP_changed_gold_has_active_rate"
                    elif gold_alt & {"seizure-free"}:
                        subtype = "FP_changed_gold_has_seizure_free"
                    elif gold_alt & {"unknown"}:
                        subtype = "FP_changed_gold_has_unknown"
                    elif not gold_alt:
                        subtype = "FP_changed_gold_has_no_sf"
                    else:
                        subtype = "FP_changed_other"
                elif state == "active-rate":
                    subtype = "FP_active_rate"
                elif state == "seizure-free":
                    subtype = "FP_seizure_free"
                else:
                    subtype = "FP_unknown"
            else:
                # FN — miss
                if state == "changed":
                    subtype = "FN_changed"
                elif state == "active-rate":
                    subtype = "FN_active_rate"
                elif state == "seizure-free":
                    subtype = "FN_seizure_free"
                else:
                    subtype = "FN_unknown"

            error_type_counts[subtype] += 1
            errors.append({
                "letter_id": lid,
                "subtype": subtype,
                "state": state,
                "direction": "FP" if (in_pred and not in_gold) else "FN",
                "gold_states": sorted(gold_states),
                "pred_states": sorted(pred_states),
                "gold_mentions": [_fmt_mention(m) for m in _mentions_for_state(gold_sf, state)] if in_gold else [],
                "pred_mentions": [_fmt_mention(m) for m in _mentions_for_state(pred_sf, state)] if in_pred else [],
                "all_gold": [_fmt_mention(m) for m in gold_sf],
                "all_pred": [_fmt_mention(m) for m in pred_sf],
            })

    # Aggregate report
    print("# SF Verify P2 (mini) — full row-by-row error analysis\n")
    print(f"Run: exectv2_gepa_sf_verify_gpt41mini_20260628")
    print(f"Letters: {len(gold_letters)}, Total errors: {len(errors)}\n")

    print("## Error type summary\n")
    print(f"{'subtype':<40}{'count':>6}")
    print(f"{'-'*40}{'-'*6}")
    for subtype, count in error_type_counts.most_common():
        print(f"{subtype:<40}{count:>6}")

    # Per-state confusion matrix
    print("\n## Per-state presence confusion (state_profile)\n")
    for state in STATES:
        tp = sum(1 for g in gold_letters if state in _state_set([
            {"text": a.text, "attributes": dict(a.attributes), "entity": "SeizureFrequency"}
            for a in g.entities("SeizureFrequency")
        ]) and state in _state_set(preds.get(g.letter_id, [])))
        fp = sum(1 for e in errors if e["state"] == state and e["direction"] == "FP")
        fn = sum(1 for e in errors if e["state"] == state and e["direction"] == "FN")
        gold_n = tp + fn
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / gold_n if gold_n > 0 else 0
        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0
        print(f"  {state:<14} TP={tp:>3} FP={fp:>3} FN={fn:>3}  P={prec:.2f} R={rec:.2f} F1={f1:.3f}")

    # Detailed errors by category
    for category in [
        "FP_changed_gold_has_active_rate",
        "FP_changed_gold_has_no_sf",
        "FP_changed_gold_has_seizure_free",
        "FN_changed",
        "FN_seizure_free",
        "FN_active_rate",
        "FP_active_rate",
        "FP_seizure_free",
    ]:
        cat_errors = [e for e in errors if e["subtype"] == category]
        if not cat_errors:
            continue
        print(f"\n## {category} ({len(cat_errors)} cases)\n")
        for e in cat_errors[:12]:
            print(f"  [{e['letter_id']}] gold_states={e['gold_states']} pred_states={e['pred_states']}")
            if e["pred_mentions"]:
                print(f"    pred: {' | '.join(e['pred_mentions'])}")
            if e["gold_mentions"]:
                print(f"    gold: {' | '.join(e['gold_mentions'])}")
            if e["direction"] == "FP" and e["subtype"].startswith("FP_changed"):
                print(f"    all_gold: {' | '.join(e['all_gold'])}")
            if e["direction"] == "FN":
                print(f"    all_pred: {' | '.join(e['all_pred'])}")


if __name__ == "__main__":
    main()
