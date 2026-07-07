"""Phase 0: re-score the v0.42 saved predictions under BOTH scoring surfaces.

No model calls. Loads the v0.42 reproject artifact (the predictions that produced
the claimed 0.94 headline), then scores the SAME predictions on the SAME 25 letters
under every surface architecture_report already computes:

  A) target headline   = cui_projected_headline_scores  (the claimed number)
  B) cui-free headline = headline_scores                (semantic recovery, concept_only for Dx)
  C) benchmark raw-LLM = cui_audit benchmark_f1         (paper-comparable item key: CUI+Certainty+attrs)
  E) semantic          = cui_audit semantic_f1          (benchmark key minus CUI)

The A - C gap per indicator is how much of the headline is the lenient redefinition.
"""

from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    architecture_report,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
)

ARTIFACT = Path(
    "experiments/"
    "exectv2_target_indicators_single_call_v042_reproject_v041live_dev25_"
    "qwen36_35b_ollama_cpu_ctx16384_20260619.jsonl"
)


def _load_rows(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    rows = _load_rows(ARTIFACT)
    split = str(rows[0].get("split", "dev"))
    note_by_id = {l.letter_id: l.note_text for l in load_letters_for_split(split)}

    gold_letters: list[ExectLetter] = []
    pred_letters: list[PredictedLetter] = []
    for row in rows:
        lid = str(row["letter_id"])
        note = note_by_id.get(lid, "")
        gold_letters.append(
            ExectLetter(
                letter_id=lid,
                note_text=note,
                annotations=tuple(
                    ExectAnnotation(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                        },
                    )
                    for m in row.get("gold_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )
        pred_letters.append(
            PredictedLetter(
                letter_id=lid,
                mentions=tuple(
                    PredictedMention(
                        entity=str(m["entity"]),
                        text=str(m.get("text", "")),
                        attributes={
                            str(k): str(v) for k, v in dict(m.get("attributes", {})).items()
                        },
                        evidence=str(m.get("evidence", "")),
                    )
                    for m in row.get("predicted_mentions", [])
                    if str(m.get("entity")) in TARGET_INDICATORS
                ),
            )
        )

    report = architecture_report(
        name="phase0_v042",
        ownership="llm_first_with_deterministic_normalization_projection",
        gold_letters=gold_letters,
        pred_letters=pred_letters,
        entities=TARGET_INDICATORS,
    )

    cr = report["clinical_recovery"]
    headline = cr["cui_projected_headline_scores"]  # A: claimed headline
    cui_free = cr["headline_scores"]  # B: cui-free concept/clinical headline
    cui_audit = report["cui_audit"]["per_entity"]  # C benchmark / E semantic

    print(f"Artifact: {ARTIFACT.name}")
    print(f"Letters: {len(rows)}  Split: {split}")
    print()
    cols = ["Indicator", "A:headline", "B:cui_free", "C:benchmark", "E:semantic", "A-C gap"]
    print("{:<18}{:>12}{:>12}{:>12}{:>12}{:>10}".format(*cols))
    for ind in TARGET_INDICATORS:
        a = float(headline[ind]["f1"])
        b = float(cui_free[ind]["f1"])
        c = float(cui_audit[ind]["benchmark_f1"])
        e = float(cui_audit[ind]["semantic_f1"])
        print(f"{ind:<18}{a:>12.4f}{b:>12.4f}{c:>12.4f}{e:>12.4f}{a - c:>10.4f}")

    ov = report["cui_audit"]["overall"]
    print()
    print("Overall (cui_audit):")
    print(f"  benchmark_f1_raw_llm              = {ov['benchmark_f1_raw_llm']:.4f}")
    print(f"  benchmark_f1_after_cui_projection = {ov['benchmark_f1_after_cui_projection']:.4f}")
    print(f"  semantic_f1                       = {ov['semantic_f1']:.4f}")
    print(f"  cui_projection_recovers_f1        = {ov['cui_projection_recovers_f1']:.4f}")
    print()
    print(f"  headline overall (cui_projected)  = {cr['cui_projected_overall']['f1']:.4f}")
    print(f"  headline overall (cui_free)       = {cr['overall']['f1']:.4f}")


if __name__ == "__main__":
    main()
