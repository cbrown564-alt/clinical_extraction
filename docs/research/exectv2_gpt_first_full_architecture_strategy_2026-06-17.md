# ExECTv2 — GPT-First Full-Architecture Strategy From Gan Closeout

Date: 2026-06-17

Status: active strategy note. This document translates the Gan 2026 closeout and
reliability scorecard into the next ExECTv2 implementation plan. It does not
authorize new full-200 audits; development remains on the ExECTv2 dev split until
the benchmark-facing architecture is frozen.

## Decision

Pause Qwen 3.6:35B as the main development loop. Qwen remains a separate
overnight transfer track because local runs are slow and brittle under interactive
iteration. The active ExECTv2 architecture search uses `gpt-4.1-mini` for rapid
experimentation across `rules_only`, `llm_only`, and `hybrid`.

The transfer sequence is:

1. Use GPT to reach benchmark-beating ExECTv2 dev metrics with clean attribution
   and reliability artifacts.
2. Freeze the architecture shape and ablation plan.
3. Port the learned prompt/state/routing design to Qwen as a model-transfer
   experiment, not as the primary optimization loop.

## What Transfers From Gan

### 1. State beats final labels

Gan's strongest simple architecture was the single GPT structured-event pass, not
direct final-label prediction. ExECTv2 should follow the same rule:

- `llm_only` should emit source-near structured mention frames, not free-form final
  benchmark bundles.
- Each frame should carry exact evidence, phrase scope, entity type, attribute
  values, uncertainty flags, and a rationale for inclusion.
- Deterministic code may validate, repair syntax, attach benchmark-format fields
  from already selected facts, and score. It must not introduce or choose the
  clinical fact in an `llm_only` claim.

Practical implication: the earlier all-9 single-pass LLM-only run is a negative
baseline, not the go-forward shape. It was contract-clean but attention-diluted and
over-emitted. The next GPT LLM-only work should be entity-focused or small
entity-group focused, with one structured schema per entity family.

### 2. External gates beat self-confidence

Gan showed that model confidence was mostly uninformative; useful discipline came
from external signals: exact evidence, deterministic floors, peer agreement, and
family-specific failure slices.

For ExECTv2:

- Report evidence-validity, schema-validity, repair/drop counts, and parse failures
  beside every F1 table.
- Treat confidence as a diagnostic field, not a decision source.
- Build risk/routing signals from observable facts: missing evidence, conflicting
  attributes, broad phrase scope, candidate disagreement, unsupported CUI, and
  per-entity hard-family membership.
- Any verifier may route or abstain. It should not write labels.

### 3. Hybrid value is representation discipline, not agent depth

Gan's full hybrid stack bought modest lift at large complexity cost. The durable
lesson is narrower: let each component own the subproblem it is good at.

For ExECTv2 hybrid:

- deterministic components should generate high-recall candidates, normalize
  stable attributes, attach benchmark-format CUIs from finite lexicons, and enforce
  evidence gates;
- GPT should select, merge, reject, or route candidate mentions and adjudicate
  genuinely clinical boundaries;
- the hybrid should prefer one strong candidate-assessment pass over deep
  multi-agent reasoner ladders until a concrete ablation shows the extra stage
  earns its keep.

### 4. Family is the unit of generalization

Gan validation saturation hid family-specific failures. ExECTv2 has a natural
family structure by entity and by annotation convention. Aggregate overall F1 is
necessary but too blunt for development.

Every dev run should report:

- overall per-item and per-letter F1;
- per-entity F1;
- phrase-only vs semantic vs benchmark-with-CUI variants;
- error families: over-emission, phrase-scope mismatch, missing CUI, wrong
  attribute bundle, unsupported evidence, duplicate/merge failure, and routed
  unresolved.

Promotion should require both aggregate lift and no severe regression in any
already-strong entity family.

### 5. Benchmark formatting is a controlled variable

Gan made benchmark repairs explicit. ExECTv2 must do the same, especially because
the with-CUI headline can collapse even when the clinical mention is correct.

Practical rule:

- build shared phrase-to-CUI lexicons as `benchmark_format` components;
- report semantic CUI-dropped scores and benchmark with-CUI scores together;
- ablate CUI attachment separately from mention detection and clinical attribute
  selection;
- never credit CUI-format repair as LLM clinical reasoning.

## Architecture Tracks

### Track A — Deterministic all-9 baseline

Purpose: provide the transparent floor, benchmark-format lexicons, and candidate
source for hybrid.

Order:

1. Implement high-precision engines for the structured/easier entities first:
   Prescription, Investigations, Diagnosis.
2. Then add Onset, WhenDiagnosed, EpilepsyCause, BirthHistory.
3. Finish with PatientHistory and revisit SeizureFrequency only where the all-9
   context exposes reusable rules.

Each entity gets:

- named rule families with portability tags;
- entity-specific phrase/CUI policy;
- unit tests for extraction, normalization, and evidence trace;
- dev error ledger and an ablation-ready rule register.

The deterministic goal is not to brute-force the benchmark. It is to create a
precise, inspectable substrate whose misses are useful candidates for GPT and whose
CUIs/normalizers can be shared by hybrid.

### Track B — GPT LLM-only structured mention frames

Purpose: test unaided GPT clinical extraction without deterministic semantic
selection.

Replace broad all-9 single-pass extraction with focused calls:

- first by entity for high-value entities;
- optionally by small clinical groups once the per-entity behavior is understood;
- always with exact evidence and entity-specific legal attributes.

Development gates:

1. pilot 25 with zero unexplained parse/call failures;
2. dev140 with full per-entity table;
3. item-level failure ledger before prompt changes;
4. no prompt promotion without a before/after table showing what failure family
   improved and what regressed.

Likely first experiment:

- `llm_only_per_entity_all9_gpt41mini_v1`, starting with Prescription,
  Investigations, Diagnosis, and SeizureFrequency, because they test both the easy
  structured cells and the hard transfer cell.

### Track C — GPT hybrid candidate assessment

Purpose: the likely benchmark-beating route. It should combine deterministic
candidate recall/formatting with GPT selection over evidence-grounded candidates.

Shape:

```text
raw letter
  -> deterministic candidates + optional GPT mention-frame candidates
  -> GPT candidate assessment / merge / route
  -> deterministic benchmark-format projection from selected facts
  -> evidence and plausibility gate
  -> PredictedLetter
```

Priorities:

- extend the live candidate-set pattern from SF to all nine entities;
- use deterministic engines and LLM-only frames as candidate sources, not as final
  truth;
- make over-emission the first hybrid target, because SF hybrid already showed
  phrase recall improves while per-item precision suffers;
- keep routed mentions visible as reliability output.

Promotion gate:

- dev overall approaches or clears 0.87/0.90;
- no entity-level collapse hidden by easy cells;
- evidence validity and parse reliability stay high;
- rule/CUI/LLM-selection ablations explain where the score comes from.

## Measurement Plan

Every serious GPT run should produce a compact reliability scorecard, not just F1:

| Axis | Required fields |
| --- | --- |
| Task correctness | overall and per-entity per-item/per-letter F1 |
| Faithfulness | evidence-valid mentions / total; dropped-evidence count |
| Schema reliability | parse failures, schema repairs, dropped invalid mentions |
| Benchmark format | semantic vs benchmark-with-CUI gap; CUI attachment coverage |
| Calibration/routing | routed/abstained mentions by reason; routed-row outcome where scored |
| Robustness/generalization | per-entity error spread and hard-family regressions |
| Operational | calls, elapsed time, resume count, estimated or measured cost |

This mirrors the Gan reliability scorecard but stays ExECTv2-native.

## Immediate Work Plan

1. Freeze Qwen as an overnight transfer track in project status.
2. Build the GPT-first ExECTv2 run matrix:
   - deterministic all-9 baseline;
   - GPT per-entity LLM-only;
   - GPT all-9 hybrid candidate assessment.
3. Start with entity coverage that can move the overall benchmark fastest:
   Prescription, Investigations, Diagnosis, then SeizureFrequency as the hard
   transfer check.
4. Add shared phrase-to-CUI projection for the entities being actively scored,
   with a separate ablation so the clinical and benchmark-format gains do not
   blur.
5. Run pilot25 -> dev140 loops only. Defer any new full-200 audit until a frozen
   architecture has benchmark-beating dev evidence and a predeclared readout.

## Claim Language

Until the above gates are met, the honest claim is:

> Gan 2026 established the architecture and reliability discipline: source-near
> structured state, exact evidence, component attribution, benchmark-format
> ablations, and family-aware promotion gates. ExECTv2 now tests whether that
> discipline scales from deep seizure-frequency reasoning to broad epilepsy
> phenotyping.

The desired eventual claim is stronger but must be earned:

> A single modular extraction framework beats the ExECTv2 benchmark across broad
> epilepsy phenotyping while preserving transparent component attribution,
> evidence validity, and deterministic-rule ablations.
