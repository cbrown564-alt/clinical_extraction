# ExECTv2 gold, scorer, and interpretation assurance plan

Date: 2026-07-10  
Status: proposed — this is the mandatory gate before repository simplification
or new ExECTv2 research claims.  
Scope: ExECTv2's complete 200-letter corpus, its scorer, all projection and
reconciliation layers that affect reported metrics, and every cited ExECTv2
interpretation. Gan remains frozen; see [Split and evaluation boundary](#split-and-evaluation-boundary).

## Why this gate exists

The new all-corpus SeizureFrequency time-period audit was reassuring because it
bounded that specific defect class. It was also a warning: a correct prediction
could still be counted as a false positive/false negative because the gold or a
scoring transformation was wrong. The earlier pipeline-assumption audit found
the same broader problem through Prescription clause scope, Diagnosis hierarchy,
and benchmark-projection behavior.

This plan therefore does **not** ask only whether a prediction matches a stored
label. It asks, for every score-affecting fact:

1. Is the gold annotation internally valid and supported by the source letter?
2. Does the scorer represent the stated evaluation policy faithfully and
   symmetrically for gold and prediction?
3. Does every projection, lens, normalizer, and matcher preserve the intended
   clinical fact, or is it a declared semantic rule with evidence and an
   ablation?
4. Are the reported conclusions still true after all accepted corrections are
   replayed and disclosed?

The audit is assurance work, not a route for raising F1. A discovered defect may
be corrected only under the evidence and replay rules below; it may never be
converted into prompt, rule, model, or threshold tuning on the audited surface.

## What we know at entry

Known cases are leads, not a completeness claim:

| Item | Current finding | Required treatment in this plan |
| --- | --- | --- |
| EA0079 SF | `1 per month` is annotated as `1 per 2 years`; one genuine unsupported TimePeriod/NumberOfTimePeriods gold value. | Verify independently, retain as an open data issue, and quantify its score effect without editing the frozen corpus. |
| EA0169 SF | `TimePeriod=days` is a case/plural closed-vocabulary variant of `Day`, not a clinical error. | Verify the four-unit normalization is symmetric and format-only; replay all cited metrics after the repair. |
| EA0146 Rx | `DrugName=Perampanel` conflicts with span, CUI phrase, and CUI, which all identify brivaracetam. | Verify independently; evaluate only a transparent issue-policy, never silently overwrite gold. |
| SF point/range | Point and degenerate-range representations were shown to be equivalent for one scoring surface. | Prove equivalence is complete, symmetric, and does not collapse a clinically distinct interval. |
| Prior scorer audit | Scope, projection, and hierarchy defects were corrected; P6, SF-2, F2, P7, and SF-5 remain explicitly parked. | Re-open every parked item as an auditable disposition: safe, defect, semantic-policy choice, or unresolved. |

Existing assets to reuse rather than duplicate are the gold-issue ledger
(`experiments/gold_data_issues.jsonl`), shared mechanism ledger
(`experiments/exectv2_ledger/`), scorer edit gate, score/projection consistency
tests, scope-invariant tests, split manifests, and frozen run artifacts. The
audit must extend these shared assets; one-off local taxonomies and untracked
manual conclusions are not acceptable.

## Assurance standard

"Absolute security" must not be used loosely. The plan produces four separately
named assurance levels:

| Level | Meaning | What it takes |
| --- | --- | --- |
| A — mechanical integrity | Every corpus file, annotation, schema value, link, span, and scorer input is structurally valid. | Deterministic all-corpus checks, fixed manifests, and a reviewed exception ledger. |
| B — annotation support | Every score-bearing gold fact has a source-grounding verdict. | Blinded, independent review of every gold assertion and attribute; adjudicated disagreements. |
| C — measurement validity | The scorer and all reported views implement the declared policy without asymmetric or hidden semantic behavior. | Exhaustive rule inventory, metamorphic/property tests, reference implementations, and same-input replays. |
| D — clinical-semantic confidence | The gold assertions represent defensible clinical interpretation, not merely source-text agreement. | At least two independent qualified clinical adjudicators, blinded review packets, disagreement adjudication, and a predeclared policy for irreducible ambiguity. |

Levels A–C are achievable within the repository. Level D requires external
clinical authority. If it is not obtained, the final language must be
"mechanically and measurement-audited," not "clinically certain."

## Non-negotiable protocol

Before any substantive audit execution:

1. Freeze a read-only audit snapshot: source-text and `.ann` hashes, corpus
   loader version, split manifests, scorer commit, projection-rule inventory,
   and cited-run artifact hashes.
2. Give each audit run an ID and a predeclared question in
   `experiments/hypothesis_registry.jsonl`; record the audit code, inputs,
   reviewer version, and outputs in a manifest.
3. Review gold in source-text packets before exposing predictions, model names,
   F1, existing issue verdicts, or proposed code fixes. This prevents an error
   audit from becoming benchmark tailoring.
4. Preserve three immutable layers: original gold, audited canonical view, and
   optional corrected/reference view. Never overwrite source annotations.
5. Record every exception in the shared issue ledger with source evidence,
   category, reviewer IDs, resolution policy, score impact, and whether it is
   source, annotation, scorer, projection, or interpretation error.
6. A scorer or projection change requires the existing predeclaration gate,
   dev140 replay, exact same-input before/after comparison, tests, and an
   all-cited-runs re-score. A clinical semantic change additionally requires
   Level-D adjudication.

## Workstreams

### 0. Audit charter, inventory, and reproducibility baseline

Build a machine-readable inventory of every score-bearing object before judging
any of it:

- all 200 letters, source-text hashes, `.ann` hashes, annotation IDs, offsets,
  entities, attributes, CUI/CUI phrase, and split membership;
- every scorer entry point, metric/view, normalizer, matcher, deduplicator,
  hierarchy lookup, lens, projection, suppression, and repair; and
- every current reported run and the score/version it cites.

The inventory must state owner, portability category (`general`,
`clinical_epilepsy`, `seizure_frequency`, `gan2026_specific`, or
`benchmark_format` where applicable), prediction-bearing effect, and test
coverage. Any code that adds, removes, chooses, or changes a clinical fact is a
semantic deterministic rule, regardless of filename.

**Exit evidence:** one versioned audit manifest; reproducible corpus counts per
entity/attribute; no unclassified score-affecting code path.

### 1. Mechanical all-corpus gold integrity sweep (Level A)

Run deterministic checks over every annotation and fail closed on unclassified
exceptions:

- file pairing, unique letter IDs, encoding, line grammar, annotation IDs,
  relation/attribute targets, duplicate IDs, and orphan attributes;
- offset bounds, span-to-source alignment, corrected-spelling drift, and a
  source-near representation that makes any tolerated offset drift explicit;
- entity-specific required/forbidden attributes, types, numeric parsing,
  ranges, closed vocabularies, capitalization/plural variants, dates, units,
  CUI syntax, and cross-field consistency;
- duplicate, overlapping, contradictory, and mutually exclusive assertions in
  a letter; distinguish intended repeated assertions from accidental duplicate
  tags;
- split coverage, duplicate-letter relationships, leakage across dev/test,
  and corpus/count differences between direct loaders and scored inputs; and
- outlier reports: singleton values, unseen combinations, values with no text
  overlap, unusual counts/durations, and all annotation values that would be
  rewritten by canonicalization.

Every detector needs precision-oriented sampling of its own positives and a
negative-control check. A detector finding is not an error verdict until source
review; a clean detector is not a clean class until its stated recall limits are
documented.

**Entity-specific mechanical checks**

| Entity | Checks that must be exhaustive |
| --- | --- |
| Diagnosis | text/CUI/CUI phrase/category/certainty/negation agreement; hierarchy consistency; parent/child multiplicity; negated, historical, and differential assertions. |
| SeizureFrequency | count, point/range shape, period/unit, multiplier, zero versus seizure-free duration, cluster fields, current/historical state, semiology, and every time expression's textual support. |
| Prescription | span/CUI phrase/CUI/DrugName agreement; brand/generic equivalence; dose/unit/frequency validity; linked regimen duplicates; current, future, stopped, rescue, and weight-based contexts. |
| Investigations | modality, performed/result combinations, planned versus completed tests, negation, result evidence, same-modality duplicates, and modality/result cross-field consistency. |

**Exit evidence:** all corpus records classified as pass, intended convention,
format-only variant, suspected annotation defect, or loader defect; zero
unexplained structural exceptions.

### 2. Blinded source-to-gold semantic audit (Levels B and D)

Create reviewer packets from source text only: annotated span, sufficiently wide
context, letter date/section where relevant, and a stable fact ID. Do not show
the stored attributes initially. Each fact receives two independent reviews and
then an adjudication for disagreement.

The reviewer form must separately judge:

- whether the assertion is present, negated, historical, future, uncertain, or
  unsupported;
- whether each score-bearing attribute is entailed, merely plausible,
  ambiguous, contradicted, or absent;
- whether multiple facts were merged or one fact was duplicated; and
- the clinical interpretation needed to decide current status, temporality,
  seizure-free state, dose regimen, and investigation completion/result.

The audit must sample no subset: every gold assertion is reviewed. Automated
outlier/detector flags set review order and require enhanced context, but may
not narrow coverage. Report agreement before adjudication, disagreement reasons,
and class prevalence with confidence intervals. A single reviewer may complete
Level B; Level D requires two qualified clinical reviewers and an independent
adjudicator or adjudication panel.

**Exit evidence:** an immutable, per-fact review table; disagreement matrix;
adjudication rationale; and an issue ledger with no unresolved high-impact
source/annotation disagreement.

### 3. Scorer and matcher verification (Level C)

Treat the scorer as a measurement instrument, not as a convenience function.
For every entity and every score/view, build a trace table from raw annotation
to final TP/FP/FN/duplicate tag. Verify the following independently of the
production implementation:

- a minimal reference key builder and reference matching algorithm for each
  reported metric, exercised against exhaustive small synthetic cases;
- symmetry: equivalent gold and prediction representations canonicalize
  identically, and swapping identical inputs preserves counts;
- idempotence and locality: normalization is idempotent and unrelated note or
  sibling-fact context cannot change a fact's score unless policy explicitly
  says it may;
- monotonicity/cardinality: duplicate handling, hierarchy matching, and
  overlap matching cannot create extra credit or consume a better match;
- permutation invariance: score is stable under annotation/prediction order;
- projection parity: scorer membership and equivalent deterministic projection
  decisions agree on a shared fixture matrix; and
- null, empty, malformed, ambiguous, and adversarial boundary inputs have
  declared behavior rather than accidental fall-through.

Specific sceptical targets include `F2` greedy overlap matching, Diagnosis
hierarchy credit, Prescription future/weight scope, SF direction/state and
zero/seizure-free distinctions, point/range equivalence, all closed-vocabulary
normalizations, and Investigations modality/result suppression. Existing scope
and projection-consistency tests are starting evidence, not a substitute for
this complete matrix.

**Exit evidence:** every cited metric has a reference-test suite, a traceable
policy document, and successful all-corpus gold-self, metamorphic, permutation,
and differential tests. Gold-self F1=1.0 alone is explicitly insufficient.

### 4. Projection, repair, and attribution audit (Level C)

Enumerate every transformation from producer output to each reported view:
raw candidate → evidence validation → lens/reconciliation → normalization →
deduplication → benchmark/headline projection → scoring.

For each transformation, record input/output examples, rule category, evidence
dependency, whether it can change a selected clinical fact, and its effect on
the four families. Classify it as exactly one of:

1. format-only normalization;
2. validation/rejection;
3. deterministic semantic selection or repair; or
4. benchmark-only projection.

Anything in categories 2–4 must be visible in provenance and reported as a
component; it may not be described as an incidental normalizer. Use frozen raw
artifacts for same-input ablations so an attribution change cannot be confused
with a changed prompt/model output. Recheck the raw/post-lens/headline
decomposition after every accepted audit change.

**Exit evidence:** a complete transformation registry, same-raw-output ablation
for every semantic repair family, and per-family raw/post-lens/headline tables
that reproduce the cited scores.

### 5. Interpretation and claim audit

Audit the prose and figures as aggressively as code:

- map every headline number, ceiling, error-rate, and comparison in
  `PROJECT_STATUS.md`, manuscript drafts, reports, dashboards, and registries
  to a scorer version, split, artifact hash, and assurance level;
- distinguish strict benchmark, `clinical_headline`, raw, post-lens, and
  diagnostic metrics everywhere;
- re-evaluate gold-quality ceiling claims against the blinded audit, not only
  post-hoc model-disagreement ledgers;
- prohibit claims of generalisation, LLM-first behavior, or model improvement
  when deterministic semantic processing supplied the change; and
- create a change log showing every superseded metric and the reason it moved.

**Exit evidence:** a cited-claim ledger with no orphaned, stale, or
non-commensurable comparison; updated manuscript wording limited to the
achieved assurance level.

### 6. Correction policy, replay, and release decision

Do not mix the following three outcomes:

- **format-only canonicalization:** applies equally to gold and prediction,
  preserves selected clinical meaning, has a finite closed vocabulary, and is
  proven by fixtures and an all-corpus impact report;
- **annotation/reference defect:** original gold remains immutable; a versioned
  audited reference view and sensitivity report may be created only after
  independent review; and
- **semantic policy change:** requires a new metric/version, explicit rule
  category, same-raw ablation, and no retroactive claim that it was the old
  measure.

For every accepted change, run the scorer-edit predeclaration gate, dev140
same-artifact replay, full all-cited-run re-score, metric-delta table, ledger and
registry refresh, and documentation update. Full-200 work is aggregate-only
unless the special audit authorization below is active. Do not inspect model
errors while replaying.

**Exit evidence:** an audit release report containing original-versus-audited
scores, all accepted/rejected issues, remaining limitations, and a signed
decision: `assured`, `assured_with_known_limitations`, or `not_assured`.

## Split and evaluation boundary

The existing ExECTv2 rule blocks full-200/holdout row-level model-error
inspection. This plan must preserve that rule. A complete gold audit nevertheless
needs source-and-gold review across all 200 letters, so it requires a separate
predeclaration with these constraints:

- reviewers see source text and gold only, never predictions, scores, prompts,
  or model provenance;
- no audit finding can trigger model/rule/prompt/threshold changes on full-200;
- full-200 outputs are limited to aggregate score deltas from a frozen scorer
  and a versioned audited reference view; and
- any later model change begins a fresh dev140-only development cycle.

Without this authorization, the plan can certify only dev140 annotation support
and all-corpus mechanical/scorer behavior; it cannot claim complete ExECTv2
gold assurance. Gan `test450` remains outside row-level review. Only code- and
schema-level invariant checks that do not expose test cases are allowed. A
clinical review of Gan test gold would need its own independently governed,
post-evaluation protocol and cannot be used for further development.

## Required deliverables and completion gate

The audit is complete only when all of the following exist and are linked from
`PROJECT_STATUS.md`:

1. immutable corpus/scorer/run manifests and a complete score-affecting rule inventory;
2. mechanical all-corpus validation report and reviewed exception ledger;
3. blinded per-fact audit table, inter-reviewer agreement, and adjudication record;
4. scorer reference fixtures, property/differential tests, and an all-corpus trace report;
5. projection/transformation registry with same-raw ablations;
6. all-cited-runs re-score and disclosure table, or a documented reason a
   metric is withdrawn; and
7. an assurance release decision stating the achieved level and every unresolved limitation.

**Hard stop:** no repository inventory, simplification/deletion campaign, new
paper claim, or new ExECTv2 model/rule experiment begins until the release
decision is `assured` or `assured_with_known_limitations`. The latter is allowed
only when every limitation is bounded, visible in the claim ledger, and does not
invalidate a cited conclusion.

## Sequence after this plan

1. Approve the audit charter and the full-corpus gold-review authorization.
2. Execute workstreams 0–6 in order; workstreams 1–4 may have independent
   implementation tracks only after the common manifest and blinding protocol
   are frozen.
3. Publish the assurance release decision and update all affected claims.
4. Only then begin the repository **keep / merge / archive / delete** inventory,
   using the audited canonical pipeline, scorer, and artifacts as the protected
   core.

## References

- `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md`
- `docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md`
- `docs/runbooks/scorer_edit_predeclaration_gate.md`
- `docs/research/contribution_thesis.md`
- `docs/research/exectv2_data_discoveries_log.md`
- `experiments/gold_data_issues.jsonl`
