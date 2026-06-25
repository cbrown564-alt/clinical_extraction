# ExECTv2 2-Call No-SF-Adjudicator Deterministic Rule Roles

- Generated: `2026-06-24`
- Candidate: `exectv2_gpt41mini_simplification_2call_no_sf_adjudicator`
- Candidate report: `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_2call_no_sf_adjudicator_20260624.md`
- Frontier report: `docs/experiments/exectv2/reliability/exectv2_gpt41mini_simplification_frontier_2026-06-24.md`
- Row inspection policy: `aggregate_only_no_full200_failure_ledgers`

## Claim Boundary

This note explains the role of deterministic rules in the 2-call no-SF-adjudicator simplification candidate. It does not use full-200 row-level failure inspection. Examples below are rule-behavior examples from rule definitions, tests, and generated aggregate reports, not a new row-level error analysis.

The candidate is the accepted cost-performance surface for the current lean GPT-4.1-mini package: it uses `400` full-200 calls instead of `600`, scores `0.8356` overall versus `0.8426` for the 3-call Diagnosis-decomposer + SF-adjudicator candidate, and preserves Diagnosis, Prescription, and Investigations guardrails. The project-owner decision relaxed the cost-profile thresholds to overall `0.8350` and SeizureFrequency `0.7500`, so this package passes the simplification frontier for the lean-candidate role.

## Family-Level Summary

| Family | Model role | Deterministic role | Observed effect | Attribution read |
| --- | --- | --- | --- | --- |
| Diagnosis | Diagnosis decomposer emits the main candidate facts. | Heading recovery, convention alias cleanup, dictionary normalization, hierarchy/dedupe, residual benchmark additions and rewrites. | Diagnosis moves from `0.7579` source-scored to `0.8397` after deterministic surfaces. | Prediction-bearing deterministic rescue, especially `clinical_epilepsy` and `benchmark_format` behavior. |
| SeizureFrequency | Structured GPT draft emits candidate SF facts; the SF adjudicator call is removed. | State projection, ownership projection, unknown suppression, union suppression, and benchmark-surface rewrites. | SF moves from `0.6221` source-scored to `0.7525` clinical-headline, passing the accepted `0.7500` cost-profile floor while remaining below the adjudicated `0.7850` frontier value. | Heavy prediction-bearing deterministic arbitration replacing most, but not all, of the adjudicator effect. |
| Prescription | The candidate uses deterministic prescription repair rather than raw structured-only prescription output. | Current-regimen parsing, drug alias normalization, dose/frequency parsing, split-dose handling, titration-tail trimming, and future/weight-based suppression. | Prescription stays at `0.8926`; structured-only is `0.8219` in the 1-call candidate. | Deterministic extractor/repair is the main successful component for this family. |
| Investigations | Structured GPT emits investigation facts in this 2-call candidate; the stronger full v08 lane uses an Investigations verifier/adjudicator stack. | Evidence/schema projection through the investigations result lens in this candidate; verifier-backed runs add narrow planned/requested-test suppression. | Investigations remains `0.8563` without the verifier/adjudicator stack, versus `0.9213` in the full current-code v08 run. | The biggest open replacement question: deterministic rules are currently thin, while the Investigations verifier/adjudicator has a large measured impact. |

## Diagnosis

Diagnosis is still model-led: the live call retained by this candidate is the diagnosis decomposer. Deterministic rules then materially change the scored surface.

The candidate report shows the stepwise effect:

| Surface | Diagnosis F1 |
| --- | ---: |
| `source_scored` | 0.7579 |
| `dictionary_normalized` | 0.8087 |
| `residual_benchmark_added` | 0.8397 |
| `clinical_headline` | 0.8397 |

The fact-origin accounting records `27` `post_model_rescue` facts at the residual benchmark surface. These are not neutral formatting. They are deterministic, prediction-bearing additions or rewrites that affect the clinical recovery score.

Representative rule behaviors:

- Heading recovery can preserve an explicit diagnosis such as `focal epilepsy` when it appears in a diagnosis heading.
- Convention aliases can rewrite `focal dyscognitive seizures` toward `dyscognitive seizures`.
- Historical or colloquial seizure-type surfaces can normalize `grand mal seizure` to `grand mal`.
- Residual benchmark rules can rewrite or add `secondary generalised seizures` when the evidence supports a benchmark-specific residual concept.
- Hierarchy/dedupe rules can collapse redundant generic and specific diagnosis concepts when they refer to the same clinical assertion.

Attribution category:

- `clinical_epilepsy`: seizure terminology, diagnosis-heading conventions, ontology/hierarchy handling.
- `benchmark_format`: residual benchmark additions and surface rewrites required to match the scoring target.

## SeizureFrequency

SeizureFrequency is the family most stressed by this candidate. The SF adjudicator was removed, and deterministic rules are asked to recover much of the adjudicator's effect.

The candidate report shows:

| Surface | SeizureFrequency F1 |
| --- | ---: |
| `source_scored` | 0.6221 |
| `clinical_headline` | 0.7525 |

The state/ownership projection report records these deterministic rule families:

| Rule | Count |
| --- | ---: |
| `state.drop_unlabelled_active_rate` | 13 |
| `state.drop_historical_or_advice_seizure_free` | 6 |
| `state.last_event_active_to_seizure_free` | 5 |
| `state.drop_historical_active_rate` | 2 |
| `ownership.generic_active_to_named` | 2 |
| `state.drop_preceded_by_current_seizure_free` | 1 |

The union arbitration report adds broader suppression and benchmark-surface actions:

| Rule | Count |
| --- | ---: |
| `drop_det_short_generic_anchor` | 114 |
| `drop_current_bare_named_event` | 18 |
| `drop_historical_or_advice_state` | 12 |
| `drop_non_target_event` | 7 |
| `drop_anaphoric_generic_state` | 6 |
| `drop_diffuse_unknown` | 4 |
| `drop_det_generic_short_rate` | 4 |
| `drop_generic_free_history_or_span` | 3 |
| `drop_bare_seizure_free_context` | 2 |
| `drop_named_unknown_long_context` | 2 |
| `drop_seizure_free_active_rate` | 2 |
| `rewrite_cluster_of_3_to_seizure_cluster` | 1 |
| `rewrite_up_to_range_lower_zero` | 1 |

Representative rule behaviors:

- A last-event expression can be projected from an active event into a seizure-free duration when the evidence states no seizures since that event.
- An active-rate candidate can be dropped when its evidence is unlabelled, for example an event/rate phrase without a clear seizure anchor.
- A seizure-free candidate can be dropped when the evidence is historical, advice-only, or superseded by a more current active seizure statement.
- A generic active-rate mention can be reassigned to a named seizure type when nearby evidence supports that ownership.
- Bare generic anchors such as short `seizures` mentions can be suppressed when they are source-shortened or non-target state artifacts.
- Benchmark-surface rewrites can convert phrases such as `cluster of 3` toward the benchmark-compatible `seizure cluster` surface.

Attribution category:

- `seizure_frequency`: state projection, ownership projection, unknown suppression, and most suppression actions.
- `benchmark_format`: benchmark-surface rewrites such as cluster or range-lower-bound rewrites.

The current aggregate answer is: deterministic SF rules replace a large part of the adjudicator's effect, but not all of it. The 2-call no-SF-adjudicator candidate is `0.0325` SF F1 below the adjudicated 3-call candidate (`0.7525` versus `0.7850`) while still passing the accepted lean-candidate SF floor (`0.7500`).

## Prescription

Prescription is the clearest successful deterministic family in the simplification frontier. The 2-call no-SF-adjudicator candidate uses `deterministic_prescription_repair_v03` as the prescription source, and the simplification frontier shows the cost of removing it:

| Candidate | Prescription F1 |
| --- | ---: |
| 2-call no SF adjudicator | 0.8926 |
| 1-call structured direct + deterministic prescription | 0.8926 |
| 1-call structured only | 0.8219 |

Representative rule behaviors:

- Drug aliases and spelling variants are normalized, such as `Epilim` / `Eplim` / `Episenta` to sodium valproate, `Tegretol` / `Tegretaol` to carbamazepine, `Lamictal` to lamotrigine, and `Keppra` to levetiracetam.
- Frequency expressions such as `bd`, `twice daily`, `od`, `tds`, `qds`, and `prn` are parsed into scoring-compatible frequency values.
- Current-regimen parsing handles medication phrases around current treatment sections.
- Split AM/PM dosing and left-bound regimen phrases are repaired when the current regimen is explicit.
- Future titration, prior-trial language, and weight-based dosing are suppressed or separated so they do not silently become current ordinary regimen facts.

Attribution category:

- Mostly `clinical_epilepsy` and prescription-task clinical parsing, with benchmark-facing projection for accepted medication/frequency surfaces.
- Prediction-bearing deterministic extraction/repair, not neutral normalization.

## Investigations

Investigations is the least deterministic family in this candidate. The producer is the structured GPT-4.1-mini artifact, passed through `investigations_result_v01`. The candidate report records:

| Metric | Value |
| --- | ---: |
| Investigations clinical-headline F1 | 0.8563 |
| Investigations changed rows versus comparator | 0 |
| Investigations exact evidence rate | 1.0000 |

The full current-code v08 and no-verifier reports show why this is the more important adjudicator-replacement question:

| Surface | Investigations source | Investigations F1 |
| --- | --- | ---: |
| 2-call no-SF-adjudicator candidate | structured direct, no Investigations verifier | 0.8563 |
| v08 no-verifier ablation | structured direct, no Investigations verifier | 0.8563 |
| Investigations verifier report | GPT-4.1-mini Investigations verifier | 0.877 |
| full current-code v08 | verifier + deterministic Investigations arbitration | 0.9213 |

The full-200 verifier report records F1 `0.877` with precision `0.859`, recall `0.896`, TP `164`, FP `27`, FN `19`. The no-call arbitration layer keeps TP and FN unchanged while reducing FP from `27` to `9`, lifting the verifier-backed lane to F1 `0.921`. That deterministic arbitration is useful, but it is a narrow cleanup layer over an effective LLM verifier rather than a full deterministic substitute.

Representative rule behaviors:

- Investigation mentions such as EEG, MRI, or CT are accepted when the structured model output has exact evidence.
- Performed/result attributes are projected into the scoring lens.
- In the verifier-backed lane, deterministic arbitration drops requested, arranged, planned, awaited, or otherwise pending tests when the mention itself indicates `Performed=No` or an unknown result in a pending-test context.
- No investigation verifier or arbitration layer is retained in this 2-call candidate.

Attribution category:

- Mostly schema/evidence projection.
- In this 2-call candidate, no strong evidence that deterministic investigation rules are doing semantic rescue.
- In the verifier-backed full v08 lane, planned/requested-test suppression is prediction-bearing `clinical_epilepsy` behavior, but it remains much narrower than the SF or Prescription deterministic stacks.

## Outstanding Question: Can Deterministic Investigations Rules Replace The Adjudicator?

The strongest outstanding replacement question is Investigations, not SeizureFrequency. SF already has a large deterministic projection/suppression/union stack. Investigations currently has the thinnest deterministic role, while the dedicated verifier/adjudicator stack has a large measured impact.

The full current-code v08 run reaches Investigations F1 `0.9213` with the Investigations verifier plus no-call arbitration. The no-verifier/direct structured path is `0.8563`, a `+0.0650` absolute F1 gap. The historical dev140 readout shows the same pattern: the dedicated Investigations verifier improved the structured baseline from `0.786` to `0.872`, and the later arbitration layer reached `0.913` by suppressing pending/requested-test residuals.

The next research question is whether deterministic Investigations rule families can replace that verifier/adjudicator impact, or whether a selective-adjudication design can keep most of the call savings while preserving the high Investigations score.

Recommended follow-up:

1. Freeze the same structured direct Investigations draft used by the no-verifier candidate and the same verifier-backed Investigations draft used by full v08.
2. Define deterministic Investigations rule families before implementation: performed-versus-planned suppression, modality/result extraction, normal/abnormal/unknown result cues, modality synonyms and EEG subtype handling, duplicate/result conflict handling, and benchmark-surface projection.
3. Ablate each rule family aggregate-only: result lens only, pending-test suppression only, result-cue extraction, dictionary/synonym expansion, deterministic-all, verifier-only, and verifier + deterministic arbitration.
4. Report Investigations headline F1, precision, recall, exact evidence rate, changed rows, action counts, and component ownership for each condition.
5. Test selective Investigations adjudication for cases deterministic rules cannot confidently resolve, especially planned-versus-completed ambiguity, modality-only mentions, missing result phrases, multiple tests with mixed results, and evidence that contains both historical and planned investigations.
6. Keep provenance explicit: deterministic result extraction or suppression is prediction-bearing `clinical_epilepsy` behavior; benchmark-compatible result rendering is `benchmark_format`.

Promotion guidance:

- Do not assume deterministic rules can replace the Investigations verifier/adjudicator until a same-draft aggregate ablation closes most of the `0.8563` to `0.9213` gap.
- Treat the current Investigations verifier/adjudicator stack as a high-impact component.
- The most plausible next architecture is `2-call + selective Investigations adjudicator`, where the adjudicator is invoked only for tests that deterministic rules mark as ambiguous or high risk.
