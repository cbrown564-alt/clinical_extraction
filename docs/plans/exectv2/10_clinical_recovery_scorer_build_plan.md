> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# ExECTv2 Clinical-Recovery Scorer — Build Plan

Date: 2026-06-18 · Parent: [[00_overarching_implementation_plan]] ·
Decision basis: `docs/decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md`,
`docs/decisions/0028-concept-identity-recall-is-entity-agnostic-precision-is-home-tagged.md`

Implements the frame-(a) reframe from the 2026-06-18 grilling session: clinical-fact
recovery is the per-entity headline; ExECT mention-phrase and CUI projection are a
separately-credited artifact layer beneath it. Resolves the recurring gold-label-audit
issues by classifying each as clinical recovery (headline) or annotation-convention
projection (demoted), not as bugs to re-fix.

See `CONTEXT.md` (ExECTv2 Scoring) for the canonical terms used below:
`Clinical Recovery Headline`, `Concept-Identity Headline`, `Concept Recovery Unit`,
`Frequency State Recovery`, `Coverage-Diagnostic Entity`.

## Entity partition (locked)

| Class | Entities | Headline |
| --- | --- | --- |
| A — decomposable | Prescription, Investigations, SeizureFrequency | `Clinical Component Score` |
| B — atomic concept | Diagnosis, Onset, WhenDiagnosed, EpilepsyCause, BirthHistory | `Concept-Identity Headline` |
| diagnostic-only | PatientHistory | `CandidateSet Union Coverage` (no headline) |

## Already conforms — reuse, do not rebuild

- **Prescription** — `score_prescription_components` / `score_prescription_benchmark_projection`
  in `scoring.py` already implement the Class-A headline + demoted projection split
  (ADRs 0019–0026). This is the worked template for every new scorer.
- **Concept Recovery Unit primitives** — `benchmark_altitude.split_compound_phrase`,
  `_is_epilepsy_seizure_type`, `_diagnosis_copy`, `_apply_affirmed_defaults`.
- **Specificity hierarchy** — `_DIAGNOSIS_PARENT` / `_collapse_diagnoses_to_most_specific`
  in `datasets/exect.py`.
- **Coverage diagnostic** — `source_near_diagnostic` in `scoring.py`.
- **Scorecard assembler** — `reports/deterministic_all9_scorecard.build_scorecard`.

## Workstreams (dependency order)

### W0 — Normalization layer (prereq)
Extract compound-split, seizure-type→DiagCategory, specificity-collapse, and
affirmed-defaults out of `deterministic/benchmark_altitude.py` and `datasets/exect.py`
into one `deterministic/normalization.py` emitting atomic clinical concepts.
`benchmark_altitude.py` imports from it so the accepted altitude projection is unchanged.
This is `Concept Recovery Unit` realized: split coordinated same-kind compounds into
distinct facts; collapse specificity hierarchies to the most-specific concept.

### W1 — `Concept-Identity Headline` (Class B)
New `score_concept_identity()` in `scoring.py` on the Prescription template.
- Key = normalized concept + assertion attrs (Negation, surviving Certainty).
- Gold collapsed to most-specific; both sides compound-split (W0).
- **New behavior:** source-entity-agnostic *recall*, home-tagged *precision* (ADR 0028).
- Emits concept-only and concept+assertion variants for diagnosis.
- DiagCategory supplied by normalization, not demanded from the model's entity tag.

### W2 — Investigations component headline (Class A)
New `score_investigations_components()` — per-modality (MRI/CT/EEG) performed/result/
(EEG_)type tuple as headline; mention phrase + CUI demoted to a projection sublayer.
Direct clone of the Prescription scorer shape.

### W3 — `Frequency State Recovery` (Class A, SeizureFrequency)
New `score_frequency_state()` — per-seizure-type state {active-rate, seizure-free,
unknown}, matched on seizure-type/CUI, `unknown` a first-class TP. Reads existing SF
deterministic state (`deterministic/rules/rate.py`, `seizure_free.py`). Exact
counts/ranges/periods stay as the current `SF_BENCHMARK`/`SF_SEMANTIC` mention scores,
reported as component diagnostics (the quantification wall, off-headline).

### W4 — PatientHistory → `Coverage-Diagnostic Entity`
Drop PH from headline aggregation; report only `source_near_diagnostic` coverage.
Mark the entity class in `contract/evaluation.py` (entity-class registry).

### W5 — Recovery scorecard assembly
New `reports/clinical_recovery_scorecard.py` above the existing all-9 scoreboard:
per-entity headline (component for A, concept-identity for B), demoted projection layer,
PH coverage, overall clinical-recovery aggregate. Keep the all-9 scorecard as the
artifact-layer scoreboard. Register run rows in `experiments/RUN_INDEX.md`.

### W6 — Tests
Per-scorer units with worked cases as fixtures:
- EA0002 — dual-filing seizure type (Diagnosis recall via PH pass; entity-agnostic credit).
- EA0011 — two SF types, one seizure-free since 2017 → two facts, unknown-state TP.
- compound-split and specificity-collapse golden cases.

## Effort & constraints
W2/W4 small, W0 small refactor, W1/W3/W5 medium. No new model calls — pure scorers over
existing prediction artifacts. Dev140 only; locked test split untouched; Phase E
promotion gate unaffected (this changes how recovery is *reported*, not the gate).
