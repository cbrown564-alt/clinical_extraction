"""Quantitative skeleton for the changed-class deep dive (model-independent).

For every changed-involved letter, compute:
  - gold FC values, pred FC values
  - whether an explicit change lexeme occurs ADJACENT to a seizure term
    (within ADJ chars) -> the deterministic-whitelist-recoverable signal
  - whether a change lexeme occurs anywhere in the note (weaker)
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa import data as gepa_data
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import frequency_state_faithful

RUN_PATH = Path("experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.jsonl")
ADJ = 50  # chars between a change lexeme and a seizure term to count as "adjacent"

SEIZURE = re.compile(
    r"seizure|epilep|convuls|myoclon|absence|tonic|clonic|focal|jerk|spasm|aura|"
    r"drop attack|status epilepticus|episode|event|attack|fit\b",
    re.IGNORECASE,
)
# directional / band change lexemes adjacent to seizures (NOT med titration words alone)
CHANGE_LEX = re.compile(
    r"decreas\w*|reduc\w*|improv\w*|declin\w*|lessen\w*|increas\w*|worsen\w*|escalat\w*|"
    r"more frequent|less frequent|unchanged|\bstable\b|the same|no change|settl\w*|"
    r"well[- ]controlled|poorly[- ]controlled|better[- ]controlled|infrequent\w*|"
    r"frequent\w*|\brare\b|\brarely\b|best it\W*s ever|deteriorat\w*|breakthrough|"
    r"under control|fewer|more often|less often",
    re.IGNORECASE,
)


def state_of(attrs: dict) -> str:
    return frequency_state_faithful({str(k): str(v) for k, v in attrs.items()})


def load_preds(path: Path) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            out[row["letter_id"]] = row.get("predicted_mentions", [])
    return out


def adjacent_change_lexeme(note: str) -> list[str]:
    """Return change lexemes that sit within ADJ chars of a seizure term."""
    seiz = [(m.start(), m.end()) for m in SEIZURE.finditer(note)]
    hits = []
    for cm in CHANGE_LEX.finditer(note):
        cs, ce = cm.start(), cm.end()
        for ss, se in seiz:
            if min(abs(cs - se), abs(ss - ce)) <= ADJ or (ss <= cs <= se) or (cs <= ss <= ce):
                hits.append(cm.group(0))
                break
    return hits


def main() -> None:
    letters = {g.letter_id: g for g in gepa_data.load_dev_letters()}
    preds = load_preds(RUN_PATH)

    rows = []
    for lid, g in letters.items():
        gold_sf = list(g.entities("SeizureFrequency"))
        pred_sf = [m for m in preds.get(lid, []) if m.get("entity") == "SeizureFrequency"]
        gstates = {state_of(e.attributes) for e in gold_sf}
        pstates = {state_of(m.get("attributes", {})) for m in pred_sf}
        if "changed" not in (gstates | pstates):
            continue
        if "changed" in gstates and "changed" in pstates:
            verdict = "TP"
        elif "changed" in pstates:
            verdict = "FP"
        else:
            verdict = "FN"
        gold_fc = [str(e.attributes.get("FrequencyChange", "")) for e in gold_sf
                   if e.attributes.get("FrequencyChange")]
        pred_fc = [str(m.get("attributes", {}).get("FrequencyChange", "")) for m in pred_sf
                   if m.get("attributes", {}).get("FrequencyChange")]
        adj = adjacent_change_lexeme(g.note_text)
        rows.append({"lid": lid, "verdict": verdict, "gold_fc": gold_fc, "pred_fc": pred_fc,
                     "adj_lexeme": sorted(set(adj))})

    rows.sort(key=lambda r: (r["verdict"], r["lid"]))

    print(f"{'lid':<8}{'verdict':<4} {'gold_FC':<22}{'pred_FC':<14}{'adj change-lexeme?'}")
    print("-" * 90)
    for r in rows:
        gfc = ",".join(r["gold_fc"]) or "-"
        pfc = ",".join(r["pred_fc"]) or "-"
        adj = ("YES: " + ",".join(r["adj_lexeme"])) if r["adj_lexeme"] else "no"
        print(f"{r['lid']:<8}{r['verdict']:<4} {gfc:<22}{pfc:<14}{adj}")

    print("\n=== ROLLUP ===")
    for v in ("FP", "FN", "TP"):
        vr = [r for r in rows if r["verdict"] == v]
        adj_yes = sum(1 for r in vr if r["adj_lexeme"])
        print(f"\n{v} (n={len(vr)}): adjacent change-lexeme present in {adj_yes}/{len(vr)} "
              f"({adj_yes/len(vr)*100:.0f}%)")
        if v == "FP":
            fc = Counter(x for r in vr for x in r["pred_fc"])
            print(f"   pred FC composition: {dict(fc)}")
        else:
            fc = Counter(x for r in vr for x in r["gold_fc"])
            print(f"   gold FC composition: {dict(fc)}")


if __name__ == "__main__":
    main()
