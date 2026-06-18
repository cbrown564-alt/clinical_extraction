"""Assemble the Diagnosis enumeration recall pass into the family-routed surface.

Predeclaration:
``docs/experiments/exectv2/predeclarations/
exectv2_diagnosis_enumeration_recall_pass_predeclaration_2026-06-18.md``

No model calls. Replays the frozen shared-pass (P/I), SF route, and the freshly
generated Diagnosis enumeration artifact, scores the routed four-family surface
with the enumeration lane swapped in at clean ``llm_first`` ownership, and emits
the predeclared readout: four-family table, Diagnosis P/R, and the seizure-type
vs epilepsy-syndrome recall split.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    run_all9_on_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_family_routed_llm_first import (  # noqa: E501
    DEFAULT_HYBRID_COMPARATOR_ARTIFACT,
    DEFAULT_SF_ROUTE_ARTIFACT,
    DEFAULT_SHARED_PASS_ARTIFACT,
    combine_family_routed_predictions,
    _routed_primary_recovery,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first_essential_evaluation import (  # noqa: E501
    align_predictions_to_gold,
    predicted_by_id_from_artifact,
    row_level_error_ledger,
)

ENUM_ARTIFACT = Path(
    "experiments/exectv2_llm_diagnosis_enumeration_v01_dev140_gpt41mini_20260618.jsonl"
)

# Seizure-type / semiology vs epilepsy-syndrome classifier (same rule used in the
# motivating candidate_miss analysis).
_SEIZURE_TYPE_WORDS = ("tonic", "clonic", "myoclonic", "partial", "convulsive", "absence")


def _is_seizure_type(concept: str) -> bool:
    c = concept.lower()
    if any(w in c for w in _SEIZURE_TYPE_WORDS):
        return True
    if c.endswith("seizures") or c.endswith("seizure"):
        return True
    return "altered awareness" in c


def _diagnosis_concepts(cell: str) -> list[str]:
    return re.findall(r"\('Diagnosis',\s*'([^']+)'\)", cell)


def _candidate_miss_by_slice(
    gold_letters: Any, pred_letters: Any
) -> dict[str, int]:
    rows = row_level_error_ledger(
        architecture="diagnosis_enumeration_readout",
        ownership="diagnostic",
        gold_letters=gold_letters,
        pred_letters=pred_letters,
        families=[DIAGNOSIS.name],
    )
    out = {"seizure_type": 0, "syndrome": 0}
    for row in rows:
        if row["error_type"] != "candidate_miss":
            continue
        for concept in _diagnosis_concepts(str(row.get("gold_examples", ""))):
            key = "seizure_type" if _is_seizure_type(concept) else "syndrome"
            out[key] += 1
    return out


def build_readout(
    *,
    split: str = "dev",
    pilot_size: int | None = None,
    enum_artifact: Path = ENUM_ARTIFACT,
) -> dict[str, Any]:
    gold = load_letters_for_split(split)
    if pilot_size is not None:
        gold = gold[:pilot_size]

    shared_by_id = predicted_by_id_from_artifact(DEFAULT_SHARED_PASS_ARTIFACT)
    sf_by_id = predicted_by_id_from_artifact(DEFAULT_SF_ROUTE_ARTIFACT)
    hybrid_by_id = predicted_by_id_from_artifact(DEFAULT_HYBRID_COMPARATOR_ARTIFACT)
    enum_by_id = predicted_by_id_from_artifact(enum_artifact)

    deterministic = run_all9_on_letters(gold)
    llm_only = align_predictions_to_gold(gold, shared_by_id)
    hybrid = align_predictions_to_gold(gold, hybrid_by_id)
    baseline_routed = combine_family_routed_predictions(gold, shared_by_id, sf_by_id)
    enum_routed = combine_family_routed_predictions(
        gold,
        shared_by_id,
        sf_by_id,
        enum_by_id,
        diagnosis_route_owner="llm_first",
        diagnosis_aggregate_ownership="llm_first_with_hybrid_sf_route",
    )

    candidates = {
        "deterministic_all9": _routed_primary_recovery(gold, deterministic),
        "llm_only_all_entities": _routed_primary_recovery(gold, llm_only),
        "hybrid_all_entities": _routed_primary_recovery(gold, hybrid),
        "family_routed_llm_first": _routed_primary_recovery(gold, baseline_routed),
        "family_routed_with_diagnosis_enumeration_pass": _routed_primary_recovery(
            gold, enum_routed
        ),
    }

    slice_baseline = _candidate_miss_by_slice(gold, baseline_routed)
    slice_enum = _candidate_miss_by_slice(gold, enum_routed)

    return {
        "pipeline_family": "exectv2_diagnosis_enumeration_readout",
        "generated_on": date.today().isoformat(),
        "split": split,
        "stage": f"pilot{pilot_size}" if pilot_size is not None else "dev140",
        "row_count": len(gold),
        "no_model_calls": True,
        "enum_artifact": str(enum_artifact).replace("\\", "/"),
        "aggregate_ownership": "llm_first_with_hybrid_sf_route",
        "candidates": candidates,
        "diagnosis_candidate_miss_fn": {
            "baseline_shared_diagnosis": slice_baseline,
            "enumeration_diagnosis": slice_enum,
        },
    }


def _fmt_overall(rec: dict[str, Any]) -> str:
    o = rec["overall"]
    return f"{o['f1']:.4f} | {o['precision']:.4f} | {o['recall']:.4f}"


def render_markdown(report: dict[str, Any]) -> str:
    c = report["candidates"]
    enum = c["family_routed_with_diagnosis_enumeration_pass"]
    base = c["family_routed_llm_first"]
    enum_dx = enum["headline_scores"][DIAGNOSIS.name]
    base_dx = base["headline_scores"][DIAGNOSIS.name]
    fn = report["diagnosis_candidate_miss_fn"]

    lines = [
        "# ExECTv2 Diagnosis Enumeration Recall Pass — Routed Readout",
        "",
        f"- Generated: `{report['generated_on']}`",
        f"- Split/stage: `{report['split']}` / `{report['stage']}` "
        f"({report['row_count']} letters)",
        f"- Enumeration artifact: `{report['enum_artifact']}`",
        f"- Aggregate ownership: `{report['aggregate_ownership']}`",
        "- Mode: **no model calls** (enumeration artifact + frozen lanes replayed).",
        "",
        "## Four-Family Routed Surface (CUI-free)",
        "",
        "| Candidate | F1 | Precision | Recall |",
        "| --- | ---: | ---: | ---: |",
    ]
    order = [
        "deterministic_all9",
        "llm_only_all_entities",
        "hybrid_all_entities",
        "family_routed_llm_first",
        "family_routed_with_diagnosis_enumeration_pass",
    ]
    for name in order:
        lines.append(f"| {name} | {_fmt_overall(c[name])} |")

    lines += [
        "",
        "## Diagnosis Lane (CUI-free)",
        "",
        "| Lane | F1 | Precision | Recall |",
        "| --- | ---: | ---: | ---: |",
        f"| shared-pass Diagnosis (baseline) | {base_dx['f1']:.4f} | "
        f"{base_dx['precision']:.4f} | {base_dx['recall']:.4f} |",
        f"| enumeration Diagnosis | {enum_dx['f1']:.4f} | "
        f"{enum_dx['precision']:.4f} | {enum_dx['recall']:.4f} |",
        "",
        "## Diagnosis candidate_miss FN by slice (lower is better)",
        "",
        "| Slice | Baseline shared FN | Enumeration FN |",
        "| --- | ---: | ---: |",
        f"| seizure-type / semiology | {fn['baseline_shared_diagnosis']['seizure_type']} | "
        f"{fn['enumeration_diagnosis']['seizure_type']} |",
        f"| epilepsy-syndrome / named dx | {fn['baseline_shared_diagnosis']['syndrome']} | "
        f"{fn['enumeration_diagnosis']['syndrome']} |",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default="dev")
    parser.add_argument("--pilot", type=int, default=None)
    parser.add_argument("--enum-artifact", type=Path, default=ENUM_ARTIFACT)
    parser.add_argument("--out-json", type=Path, default=None)
    parser.add_argument("--out-md", type=Path, default=None)
    args = parser.parse_args()

    report = build_readout(
        split=args.split, pilot_size=args.pilot, enum_artifact=args.enum_artifact
    )
    md = render_markdown(report)
    if args.out_json:
        args.out_json.parent.mkdir(parents=True, exist_ok=True)
        args.out_json.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Wrote {args.out_json}")
    if args.out_md:
        args.out_md.parent.mkdir(parents=True, exist_ok=True)
        args.out_md.write_text(md + "\n", encoding="utf-8")
        print(f"Wrote {args.out_md}")
    print()
    print(md)


if __name__ == "__main__":
    main()
