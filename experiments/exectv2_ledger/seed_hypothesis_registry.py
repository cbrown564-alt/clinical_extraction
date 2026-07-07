"""Seed ``experiments/hypothesis_registry.jsonl`` with already-published hypotheses.

Zero LLM calls, zero new analysis: transcribes verdicts already reached (and
already dated/cited) in docs read during this session's research, so "what
have we already tried against family X" is queryable from day one instead of
starting empty. Idempotent -- rerun any time to regenerate from this list.

Usage: uv run python experiments/exectv2_ledger/seed_hypothesis_registry.py
"""

from __future__ import annotations

import sys
from pathlib import Path

_EXPERIMENTS_DIR = Path(__file__).resolve().parents[1]
if str(_EXPERIMENTS_DIR) not in sys.path:
    sys.path.insert(0, str(_EXPERIMENTS_DIR))

from exectv2_ledger.hypothesis_registry import (  # noqa: E402
    HypothesisEntry,
    write_hypothesis_registry,
)

ROOT = _EXPERIMENTS_DIR.parent
OUT = _EXPERIMENTS_DIR.parent / "experiments" / "hypothesis_registry.jsonl"

ENTRIES: list[HypothesisEntry] = [
    HypothesisEntry(
        hypothesis_id="dx_gold_multiplicity_2026-06-30",
        family="Diagnosis",
        statement=(
            "Dx clinical_headline disagreements are dominated by gold "
            "multiplicity/consolidation artifacts (gold lists multiple "
            "equivalent diagnoses the model correctly merges), not genuine "
            "model error."
        ),
        predeclaration_doc="docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md",
        kill_criterion="genuine-error share of row-adjudicated disagreements < 50%",
        verdict="CONFIRMED",
        date="2026-06-30",
        owner="ExECTv2 workstream",
        evidence_run_ids=("exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628",),
        evidence_docs=(
            "docs/experiments/exectv2/diagnosis/exectv2_dx_canonical_row_analysis_2026-06-30.md",
        ),
        notes="Only 14.8% genuine error, 85.2% gold multiplicity/consolidation; adjusted F1 0.6617 -> 0.9501.",
    ),
    HypothesisEntry(
        hypothesis_id="sf_gold_quality_ceiling_2026-06-29",
        family="SeizureFrequency",
        statement=(
            "SF's ~0.74-0.78 state_profile plateau is a gold-quality ceiling "
            "(SF human inter-annotator agreement is 0.47), not a model ceiling."
        ),
        predeclaration_doc="docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md",
        kill_criterion="genuine-error share of row-adjudicated metric-disagreements < 30%",
        verdict="CONFIRMED",
        date="2026-06-29",
        owner="ExECTv2 workstream",
        evidence_run_ids=("exectv2_gepa_sf_verify_gpt41mini_20260628",),
        evidence_docs=(
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md",
        ),
        notes=(
            "62.1% metric-defensible -> 89.3% clinically defensible; only 15/53 disagreements genuine "
            "error; metric itself noisy (+-0.03 band across identical re-runs)."
        ),
    ),
    HypothesisEntry(
        hypothesis_id="sf_direction_blind_schema_2026-06-29",
        family="SeizureFrequency",
        statement=(
            "SF's 'changed' class errors trace to a direction-blind schema/metric "
            "defect (no FrequencyChange direction field; metric collapses the "
            "5-way FC to bare presence), not an irreducible IAA floor."
        ),
        predeclaration_doc="docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md",
        kill_criterion="representation-fixable share of 'changed'-class errors > 50%",
        verdict="PARTIAL",
        date="2026-06-29",
        owner="ExECTv2 workstream",
        evidence_docs=(
            "docs/experiments/exectv2/seizure_frequency/exectv2_sf_changed_class_row_analysis_2026-06-29.md",
        ),
        notes="~52% fixable representation defect, 31% genuine IAA-0.47 ambiguity, 17% gold convention.",
    ),
    HypothesisEntry(
        hypothesis_id="rx_evrecall_typo_artifact_2026-06-30",
        family="Prescription",
        statement=(
            "Prescription's inflated source_near evidence-recall gap is driven "
            "mainly by spelling/transcription typos breaking literal substring "
            "matching (gold or letter misspells the drug), not gold multiplicity "
            "-- a different mechanism than Dx/SF."
        ),
        predeclaration_doc="docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        kill_criterion="H-inflated share of source_near FNs >= 50%",
        verdict="CONFIRMED",
        date="2026-06-30",
        owner="ExECTv2 GEPA workstream",
        evidence_run_ids=("exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628",),
        evidence_docs=(
            "docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        ),
        notes=(
            "52.2% H-inflated, knife's-edge (one case from the null); of 12 inflated, only 4 "
            "cardinality-linked, 8 typo/substring-artifact. 11 genuine misses = absent 2nd/3rd drug "
            "in a polypharmacy list. This ledger's Phase C/D extends the finding to the actual scored "
            "clinical_headline layer (never row-adjudicated before), not just this source_near diagnostic."
        ),
    ),
    HypothesisEntry(
        hypothesis_id="inv_evrecall_genuine_2026-06-30",
        family="Investigations",
        statement=(
            "Investigations' source_near evidence-recall gap is genuine (no "
            "dedup-consolidation rescue applies, unlike Dx/SF), concentrated in "
            "EEG under-extraction specifically when an MRI is also present."
        ),
        predeclaration_doc="docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        kill_criterion="H-inflated share of source_near FNs < 30%",
        verdict="CONFIRMED",
        date="2026-06-30",
        owner="ExECTv2 GEPA workstream",
        evidence_run_ids=("exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628",),
        evidence_docs=(
            "docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        ),
        notes="25.9-29.6% H-inflated, both readings under threshold -- cleanest negative of the 4-family sweep.",
    ),
    HypothesisEntry(
        hypothesis_id="inv_mri_anchoring_lane_2026-07-01",
        family="Investigations",
        statement=(
            "A dedicated GEPA lane with an explicit MRI/EEG anti-anchoring "
            "instruction will close Investigations' EEG-under-extraction gap."
        ),
        predeclaration_doc="docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        kill_criterion="targeted lane beats the untargeted DeepSeek-chat baseline",
        verdict="REFUTED",
        date="2026-07-01",
        owner="ExECTv2 GEPA workstream",
        evidence_run_ids=(
            "exectv2_gepa_investigations_lane_deepseekreasoner_20260630",
            "exectv2_gepa_baseline_multifamily_deepseekchat_20260628",
        ),
        evidence_docs=(
            "docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md",
        ),
        notes=(
            "0.9254/0.9412 vs baseline 0.9259/0.9412, statistically identical despite ~4x wall-clock. "
            "The DeepSeek model-family swap, not the instruction, closed the gap."
        ),
    ),
    HypothesisEntry(
        hypothesis_id="gepa_harness_vs_ceiling_2026-06-27",
        family="cross_family",
        statement=(
            "GEPA-from-scratch barely beating its own seed prompt (0.628 vs "
            "0.619) is a harness/feedback-signal bug, not evidence of a genuine "
            "task ceiling."
        ),
        predeclaration_doc="docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md",
        kill_criterion="enriching metric feedback recovers hand-tuned parity (0.710)",
        verdict="CONFIRMED",
        date="2026-06-27",
        owner="ExECTv2 GEPA workstream",
        evidence_docs=("docs/research/exectv2_gepa_underperformance_investigation_2026-06-27.md",),
        notes=(
            "H1: per-family gold-vs-pred diff feedback -> mini monolith 0.628 -> 0.702 (matches hand-tuned "
            "0.710). H2: minibatch=3 accept-gate was noise-dominated; minibatch=8 fix -> 0.7194, first "
            "GEPA-from-scratch to beat hand-tuned. Multi-family re-run -> new best 0.7313."
        ),
    ),
    HypothesisEntry(
        hypothesis_id="gepa_multistage_plateau_2026-06-28",
        family="cross_family",
        statement=(
            "Single-pass GEPA plateaus around 0.73 on clinical_headline_overall, "
            "an architectural gap below hybrid's 0.9155 (multi-stage "
            "verify/arbitrate) that instruction tuning alone cannot close."
        ),
        predeclaration_doc="docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md",
        kill_criterion="n/a -- synthesis finding, not a gated experiment",
        verdict="CONFIRMED",
        date="2026-06-28",
        owner="ExECTv2 GEPA workstream",
        evidence_docs=("docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md",),
        notes="Harness fixes climbed 0.628 -> 0.731 (+0.10, beats hand-tuned) but the remaining ~0.18 to 0.9155 needs a multi-stage program.",
    ),
    HypothesisEntry(
        hypothesis_id="gepa_verify_credit_assignment_2026-07-01",
        family="cross_family",
        statement=(
            "A verify/critique stage sharing an undecomposed scalar reward with "
            "its upstream generator learns to regenerate wholesale rather than "
            "filter -- decomposing the reward with stage-local feedback should "
            "make it filter-shaped and beat the prior multi-stage run."
        ),
        predeclaration_doc="docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md",
        kill_criterion="stage-local-feedback run beats the 0.731 single-pass ceiling by >= 0.03",
        verdict="PARTIAL",
        date="2026-07-01",
        owner="ExECTv2 workstream",
        evidence_run_ids=("exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701",),
        evidence_docs=("docs/research/exectv2_gepa_verify_stage_credit_assignment_2026-07-01.md",),
        notes=(
            "Qualitatively confirmed: 0.7235 -> 0.7596, verify instructions turned filter-shaped. "
            "Kill-criterion narrowly missed by -0.0014."
        ),
    ),
    HypothesisEntry(
        hypothesis_id="rx_future_medication_regex_scope_bug_2026-07-02",
        family="Prescription",
        statement=(
            "Scoping `_is_future_medication`/`_is_weight_based_dosing` in "
            "scoring/prescription.py to the clause containing the scored dose "
            "(instead of the full gold annotation span) will recover a "
            "meaningful share of Prescription's clinical_headline gap without "
            "regressing letters where the whole span genuinely is a "
            "future/weight-based dose."
        ),
        predeclaration_doc="docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",
        kill_criterion="dev140 replay after the scope fix must not regress any of the "
        "11 scorer_mechanics_artifact cases' sibling GOLD_RIGHT letters",
        verdict="OPEN",
        date="2026-07-02",
        owner="ExECTv2 workstream",
        evidence_docs=("docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",),
        notes="Not yet implemented or run. 11/48 (22.9%) of Prescription's row-adjudicated "
        "disagreements are this scorer_mechanics_artifact.",
    ),
    HypothesisEntry(
        hypothesis_id="rx_current_vs_future_dose_conflation_2026-07-02",
        family="Prescription",
        statement=(
            "An instruction/prompt fix teaching the extractor to distinguish a "
            "letter's current medication from a proposed future target dose "
            "will reduce Prescription's genuine-model-error share (the model "
            "currently asserts titration targets as the current prescription, "
            "dropping the true current dose)."
        ),
        predeclaration_doc="docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",
        kill_criterion="not yet predeclared -- needs a specific probe design before running",
        verdict="OPEN",
        date="2026-07-02",
        owner="ExECTv2 workstream",
        evidence_docs=("docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",),
        notes="Not yet implemented or run. Affects a meaningful share of Prescription's 29 genuine_model_error cases (e.g. EA0021).",
    ),
    HypothesisEntry(
        hypothesis_id="rx_non_aed_over_extraction_2026-07-02",
        family="Prescription",
        statement=(
            "An explicit 'tag only anti-epileptic drugs' scoping instruction "
            "will reduce Prescription's non-AED over-extraction (the model "
            "currently tags cardiac/diabetes comorbidity medication as "
            "Prescription facts in letters concluding a non-epileptic cause)."
        ),
        predeclaration_doc="docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",
        kill_criterion="not yet predeclared -- needs a specific probe design before running",
        verdict="OPEN",
        date="2026-07-02",
        owner="ExECTv2 workstream",
        evidence_docs=("docs/canon/workstreams/PRESCRIPTION_CANONICAL_LEDGER_CANON.md",),
        notes="Not yet implemented or run. Low-risk probe candidate.",
    ),
    HypothesisEntry(
        hypothesis_id="corpus_duplicate_letters_bug_2026-07-01",
        family="cross_family",
        statement=(
            "4 duplicate letter-pairs found by md5-hashing the ExECTv2 corpus "
            "are an undiscovered data-quality bug in the gold corpus."
        ),
        predeclaration_doc="docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md",
        kill_criterion="n/a -- corrected on citation check, not a gated experiment",
        verdict="REFUTED",
        date="2026-07-01",
        owner="ExECTv2 workstream",
        evidence_docs=(
            "docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md",
        ),
        downstream_corrections=(
            "PROJECT_STATUS.md",
            "docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md",
        ),
        notes=(
            "Source paper (Fonferko-Shadrach et al. 2024) discloses these 4 pairs as intentional "
            "annotation-QA duplicates, not a bug. What WAS genuinely ours to fix: one pair "
            "(EA0159 test / EA0160 dev) crossed the frozen dev/test split boundary undetected."
        ),
    ),
]


def main() -> None:
    write_hypothesis_registry(ENTRIES, OUT)
    print(f"Wrote {len(ENTRIES)} hypothesis entries to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
