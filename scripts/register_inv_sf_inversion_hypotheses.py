"""Pre-work for the Inv + SF inversion-generalization experiment (2026-07-03).

Two zero-LLM operations:
  1. Register two hypotheses in experiments/hypothesis_registry.jsonl:
     - inv_llm_precision_vs_hybrid_inversion_2026-07-03 (PENDING)
     - sf_direction_extraction_probe_2026-07-03 (PENDING)
  2. Score the SF state_profile_directional baseline on the v08 SF producer
     saved-jsonl artifacts (dev140 + full-200). This is the
     deterministic-blind baseline number the direction probe must beat.
     Free scorer replay -- no LLM calls (FrequencyChange is already populated
     in the stored v08 predictions).

The baseline numbers are recorded into the predeclaration doc for the SF
direction probe so the kill-criterion / success-gate has a concrete reference.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    score_frequency_state,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "experiments" / "hypothesis_registry.jsonl"
SF_DEV_JSONL = (
    ROOT / "experiments" / "exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl"
)
SF_FULL200_JSONL = (
    ROOT / "experiments" / "exectv2_v08_full200_currentcode_sf_union_arbitration_20260624.jsonl"
)

SF_ENTITY = "SeizureFrequency"
TODAY = "2026-07-03"


# --------------------------------------------------------------------------------------
# 1. Hypothesis registration.
# --------------------------------------------------------------------------------------
HYPOTHESES: list[dict[str, Any]] = [
    {
        "date": TODAY,
        "downstream_corrections": [],
        "evidence_docs": [
            "docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_comparator_2026-07-03.md",
            "docs/experiments/exectv2/prescription/exectv2_rx_llm_vs_deterministic_comparator_2026-07-03.md",
        ],
        "evidence_run_ids": [],
        "family": "Investigations",
        "hypothesis_id": "inv_llm_precision_vs_hybrid_inversion_2026-07-03",
        "kill_criterion": (
            "Phase A1 (dev140): the LLM-tuned Inv extractor's dev140 Inv clinical_headline must be "
            "within -0.02 of the hybrid baseline (0.9132). A collapse below 0.8932 kills -- the "
            "precision instruction is harming dev140 too much to support the inversion hypothesis, "
            "which requires only a MODEST dev140 loss (the recall probe was already REFUTED so the "
            "LLM cannot recover the MRI-crowds-EEG recall gap). Phase A2 (full-200, gated on A1, "
            "aggregate-only): the inversion CONFIRMS only if LLM-tuned Inv F1 > hybrid Inv F1 on "
            "full-200 (precision failures more prevalent on the broader test surface)."
        ),
        "notes": "PENDING 2026-07-03. Generalizes the 07-03 Rx split-dependent inversion.",
        "owner": "ExECTv2 workstream",
        "predeclaration_doc": (
            "docs/experiments/exectv2/investigations/exectv2_inv_llm_vs_hybrid_full200_predeclaration_2026-07-03.md"
        ),
        "statement": (
            "An LLM-tuned Inv extractor with a completed-neuro-investigations-only PRECISION "
            "instruction inverts against the v08 hybrid Inv lane across splits: loses on dev140 "
            "(recall-dominated -- the hybrid arbitration recovers MRI-crowds-EEG, the precision "
            "probe cannot) but wins on full-200 (precision-dominated -- the deterministic producer "
            "is a bare surface-token anchor EEG|MRI|CT with no neuro-investigation scope gate, so "
            "it over-captures planned investigations and incidental mentions more prevalent on the "
            "broader test surface). This is the direct analog of the Rx AED-only precision mechanism."
        ),
        "verdict": "PENDING",
    },
    {
        "date": TODAY,
        "downstream_corrections": [],
        "evidence_docs": [
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_direction_probe_results_2026-07-03.md",
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md",
            "docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md",
        ],
        "evidence_run_ids": [],
        "family": "SeizureFrequency",
        "hypothesis_id": "sf_direction_extraction_probe_2026-07-03",
        "kill_criterion": (
            "Phase B1 (dev140 post-hoc, ~20 calls): if post-hoc direction adjudication recovers "
            "non-Same direction on <=2 of the ~13 changed-state mentions, the model cannot judge "
            "direction even when explicitly asked -- the schema is not the bottleneck, kill the "
            "full extraction-time probe. Phase B2 (full two-stage, gated on B1): CONFIRMS only if "
            "state_profile_directional on the direction-aware run strictly beats the deterministic-"
            "blind baseline (recorded in the predeclaration) on dev140 AND full-200, WITHOUT "
            "regressing state_profile or clinical_headline (the direction field is additive)."
        ),
        "notes": (
            "PENDING 2026-07-03. Closes the explicitly-open SF Phase-6 extraction-behavior probe "
            "(the SF-2 metric-side fix made direction-blindness visible but did not fix extraction). "
            "NOT a split-dependent inversion test -- the deterministic side is direction-blind by "
            "construction (SF-5 deliberately left sf_unknown_suppression.py unreconciled), so this "
            "is expected to be a clean LLM win on both splits, not an inversion."
        ),
        "owner": "ExECTv2 workstream",
        "predeclaration_doc": (
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_direction_probe_predeclaration_2026-07-03.md"
        ),
        "statement": (
            "A direction-aware SF emission schema (add change_direction to the generate-stage event "
            "schema -- currently absent, the documented schema defect) plus seizure-adjacency prompt "
            "discipline recovers non-Same FrequencyChange on state_profile_directional where the "
            "deterministic side is structurally blind. The SF Phase 6 finding (model defaults every "
            "changed to Same, recovers direction 0/12) was measured under a schema that never asked "
            "for direction; this probe tests whether the model can judge direction when asked."
        ),
        "verdict": "PENDING",
    },
]


def register_hypotheses() -> None:
    existing_ids: set[str] = set()
    if REGISTRY.exists():
        for line in REGISTRY.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                existing_ids.add(json.loads(line)["hypothesis_id"])
            except (json.JSONDecodeError, KeyError):
                continue
    new = [h for h in HYPOTHESES if h["hypothesis_id"] not in existing_ids]
    if not new:
        print("[hypotheses] both already registered; skipping")
        return
    with REGISTRY.open("a", encoding="utf-8") as fh:
        for h in new:
            fh.write(json.dumps(h, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"[hypotheses] registered {len(new)}: {[h['hypothesis_id'] for h in new]}")


# --------------------------------------------------------------------------------------
# 2. SF state_profile_directional baseline (free scorer replay).
# --------------------------------------------------------------------------------------
def _pred_letters_from_jsonl(
    jsonl_path: Path, gold_by_id: dict[str, ExectLetter]
) -> list[ExectLetter]:
    """Build predicted ExectLetters from a saved-jsonl's SF predicted_mentions.

    Each mention's attributes are already post-adapter (the v08 union arbitration
    persists its projected attributes), so we wrap them as ExectAnnotations
    directly. FrequencyChange is already populated, so the direction-aware metric
    can read it.
    """

    out: list[ExectLetter] = []
    for line in jsonl_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        lid = row["letter_id"]
        gold = gold_by_id.get(lid)
        if gold is None:
            continue
        sf_mentions = [m for m in row.get("predicted_mentions", []) if m.get("entity") == SF_ENTITY]
        annotations = tuple(
            ExectAnnotation(
                entity=SF_ENTITY,
                text=str(m.get("text", "")),
                attributes={str(k): str(v) for k, v in dict(m.get("attributes", {})).items()},
            )
            for m in sf_mentions
        )
        out.append(ExectLetter(letter_id=lid, note_text=gold.note_text, annotations=annotations))
    return out


def score_sf_baseline(
    label: str, jsonl_path: Path, gold_letters: list[ExectLetter]
) -> dict[str, float]:
    gold_by_id = {le.letter_id: le for le in gold_letters}
    pred_letters = _pred_letters_from_jsonl(jsonl_path, gold_by_id)
    scores = score_frequency_state(gold_letters, pred_letters)
    result = {
        "state_profile_directional_f1": round(scores.state_profile_directional.f1, 4),
        "state_profile_directional_p": round(scores.state_profile_directional.precision, 4),
        "state_profile_directional_r": round(scores.state_profile_directional.recall, 4),
        "state_profile_directional_tp": scores.state_profile_directional.tp,
        "state_profile_directional_fp": scores.state_profile_directional.fp,
        "state_profile_directional_fn": scores.state_profile_directional.fn,
        "state_profile_f1": round(scores.state_profile.f1, 4),
        "state_profile_tp": scores.state_profile.tp,
        "state_profile_fp": scores.state_profile.fp,
        "state_profile_fn": scores.state_profile.fn,
        "clinical_headline_f1": round(scores.clinical_headline.f1, 4),
        "n_pred_letters": len(pred_letters),
    }
    print(f"[sf-baseline] {label} ({jsonl_path.name}):")
    for k, v in result.items():
        print(f"  {k}: {v}")
    return result


def main() -> None:
    register_hypotheses()
    print()
    all_gold = load_letters()
    dev_gold = load_letters_for_split("dev")
    dev_result = score_sf_baseline("dev140 v08 SF union arbitration", SF_DEV_JSONL, dev_gold)
    full200_result = score_sf_baseline(
        "full-200 v08 SF union arbitration", SF_FULL200_JSONL, all_gold
    )
    # Emit a compact machine-readable summary for the predeclaration docs.
    summary = {
        "dev140": dev_result,
        "full200": full200_result,
        "note": (
            "Free scorer replay on the v08 SF union-arbitration saved-jsonl. "
            "FrequencyChange already populated in stored predictions. These are the "
            "deterministic-blind baselines the SF direction probe must beat."
        ),
    }
    out_path = (
        ROOT
        / "docs"
        / "experiments"
        / "exectv2"
        / "seizure_frequency"
        / ("_sf_directional_baseline_replay_2026-07-03.json")
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"\n[sf-baseline] summary -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
