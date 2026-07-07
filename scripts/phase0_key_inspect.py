"""Phase 0 deep dive: show WHAT each headline key forgives vs the benchmark key.

For each indicator, per letter, print gold vs predicted mentions with the
attributes that matter, plus the headline-key and benchmark-key sets, so we can
read off whether a 'forgiven' discrepancy is a format artifact (CUI/phrase) or a
clinically material relaxation (e.g. SF quantitative collapse).
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    _concept_keys,
    _frequency_state_keys,
    _investigation_component_keys,
    _prescription_component_keys,
    benchmark_config_for,
    match_key,
)

ARTIFACT = Path(
    "experiments/"
    "exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_"
    "qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl"
)


def _rows():
    out = []
    for line in ARTIFACT.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def _ann(m):
    return ExectAnnotation(
        entity=str(m["entity"]),
        text=str(m.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(m.get("attributes", {})).items()},
    )


def main() -> None:
    rows = _rows()
    split = str(rows[0].get("split", "dev"))
    note_by_id = {l.letter_id: l.note_text for l in load_letters_for_split(split)}

    for indicator in ("SeizureFrequency", "Prescription", "Diagnosis", "Investigations"):
        print("=" * 90)
        print(f"INDICATOR: {indicator}")
        print("=" * 90)
        for row in rows:
            lid = str(row["letter_id"])
            note = note_by_id.get(lid, "")
            gold = [_ann(m) for m in row.get("gold_mentions", []) if m.get("entity") == indicator]
            pred = [
                _ann(m) for m in row.get("predicted_mentions", []) if m.get("entity") == indicator
            ]
            if not gold and not pred:
                continue

            ExectLetter(letter_id=lid, note_text=note, annotations=tuple(gold))
            ExectLetter(letter_id=lid, note_text=note, annotations=tuple(pred))

            # benchmark keys
            bg = Counter(match_key(a, benchmark_config_for(indicator)) for a in gold)
            bp = Counter(match_key(a, benchmark_config_for(indicator)) for a in pred)
            bench_tp = sum((bg & bp).values())

            # headline keys
            if indicator == "SeizureFrequency":
                hg = Counter(_frequency_state_keys(gold, "clinical_headline"))
                hp = Counter(_frequency_state_keys(pred, "clinical_headline"))
            elif indicator == "Prescription":
                hg = Counter(_prescription_component_keys(gold, "clinical_headline", note))
                hp = Counter(_prescription_component_keys(pred, "clinical_headline", note))
            elif indicator == "Investigations":
                hg = Counter(_investigation_component_keys(gold, "clinical_headline"))
                hp = Counter(_investigation_component_keys(pred, "clinical_headline"))
            else:  # Diagnosis concept_only
                hg = Counter(_concept_keys(gold, indicator, "concept"))
                hp = Counter(_concept_keys(pred, indicator, "concept"))
            head_tp = sum((hg & hp).values())

            # Only show letters where the headline forgives something the benchmark penalizes
            if head_tp <= bench_tp and len(gold) == bench_tp:
                continue

            print(
                f"\n--- letter {lid}  (bench_tp={bench_tp}/{len(gold)}  head_tp={head_tp}/{sum(hg.values())}) ---"
            )
            for a in gold:
                attrs = {k: v for k, v in a.attributes.items() if k not in ("CUI", "CUIPhrase")}
                print(f"  GOLD  {a.text!r:45} {attrs}")
            for a in pred:
                attrs = {k: v for k, v in a.attributes.items() if k not in ("CUI", "CUIPhrase")}
                print(f"  PRED  {a.text!r:45} {attrs}")
            print(f"  headline GOLD keys: {list(hg)}")
            print(f"  headline PRED keys: {list(hp)}")


if __name__ == "__main__":
    main()
