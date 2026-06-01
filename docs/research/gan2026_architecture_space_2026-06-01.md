# Gan 2026 Architecture Space

Date: 2026-06-01

Related retrospective:
`experiments/gan2026_llm_structured_decision_retrospective_2026-06-01.md`

This note deliberately widens the candidate architecture space for Gan 2026
seizure-frequency extraction. It is a response to the narrow optimization loop
identified in the LLM-structured decision retrospective: once the project began
improving local validation performance through increasingly capable post-LLM
repair logic, the main design question collapsed into "how do we improve this
pipeline?" rather than "what decomposition should this task have?"

The purpose here is not to choose a final architecture. The purpose is to keep
several distinct hypotheses alive long enough to test them cleanly.

## Design Pressure To Avoid

The recent failure mode was not only that deterministic post-processing became
too strong. The deeper failure was architectural tunnel vision. There are many
valid ways to decompose seizure-frequency extraction:

- extract all candidate facts, then select
- propose candidate labels, then adjudicate
- build a clinical state representation, then query it
- split reasoning across specialized model roles
- make deterministic rule discovery itself the experimental object

Those decompositions imply different claims, ablations, costs, and risks. A
pipeline that performs well after hidden semantic repair is less useful than a
pipeline whose prediction-bearing components are explicit and testable.

Future experiments should therefore pass two gates:

1. The architecture gate: the prediction-bearing component is named, isolated,
   ablatable, and assigned a claim type before metrics are interpreted.
2. The metric gate: Gan validation performance improves under the documented
   split protocol.

A high score should trigger an attribution audit before it triggers promotion.
The previous repair-heavy structured run showed that a pipeline can hit the
numeric target while failing the intended architecture claim.

## Evaluation Criteria

Candidate architectures should be compared on more than Purist or Pragmatic
accuracy. At minimum, each promoted architecture should report:

- raw component output before downstream repair
- format-only repair output
- full-stack output, if any downstream stack exists
- rows changed by each component
- raw-wrong to final-correct changes
- raw-correct to final-wrong regressions
- evidence substring validity
- exact normalized-label match where meaningful
- semantic-kind transitions, such as `frequency` to `unknown`
- deterministic rule categories used: `general`, `clinical_epilepsy`,
  `seizure_frequency`, `gan2026_specific`, and `benchmark_format`

These criteria preserve the project thesis that deterministic rules and LLM
reasoning are both controlled variables, not incidental implementation detail.

## Promotion Contract

Before a candidate moves from one validation ladder stage to the next, its
experiment artifact should declare:

- claim type: `llm_first`, `hybrid_llm_extractor`, `hybrid_llm_adjudicator`,
  `deterministic_first`, or `diagnostic_probe`
- prediction-bearing component and the exact downstream components allowed to
  change its output
- comparator: raw structured model selection, deterministic V1 frozen output,
  prior promoted candidate, or another named baseline
- repair policy: raw only, strict format-preserving repair, named semantic
  module, or full stack
- row-change accounting: rows changed by each downstream component, raw-wrong to
  final-correct changes, and raw-correct to final-wrong regressions
- evidence policy: exact substring requirement, tolerated missing evidence, and
  any manual review protocol
- model and runtime metadata, including cache or no-call replay status
- split surface and prefix size, following the 25/50/250 validation ladder
- stop condition: what result would promote, revise, pause, or reject the
  architecture before the next larger run

The 25-row stage should primarily test schema validity, evidence validity, call
stability, and whether failures are interpretable. The 50-row stage should
decide whether the architecture has a distinctive advantage over its comparator
on a named failure family. The 250-row stage should be reserved for candidates
whose 50-row result has already defined the decision the larger slice will make.

Full 750-row validation should remain rare and should require a written reason
that 250 rows are insufficient. Locked test rows remain unavailable for
architecture selection or row-level failure inspection.

## Architecture 1: LLM Event Extractor, Deterministic Selector

### Decomposition

1. An LLM extracts all seizure-frequency-relevant events from the note as
   source-near clinical facts.
2. Deterministic normalization converts each event into comparable bounds,
   semantic kind, evidence, and Gan-compatible label candidates.
3. A deterministic selector chooses the final Gan label using explicit clinical
   policy.

### Research Hypothesis

The LLM is better used as a broad, evidence-grounded fact extractor than as the
final decision maker. Deterministic selection can then be accepted as the
prediction-bearing component, rather than hidden inside post-processing repair.

This architecture turns the retrospective's attribution problem into a cleaner
claim: model-mediated event discovery plus transparent deterministic clinical
selection.

Claim type: `hybrid_llm_extractor`. This is not a clean LLM-first architecture,
because the deterministic selector is explicitly prediction-bearing.

### Why It Is Worth Testing

This is likely the cleanest hybrid architecture if the project wants strong
transparency and ablation discipline. It also fits the existing package
boundaries: event extraction, normalization, selection, evidence validation, and
scoring are already conceptually separate.

### Risks

The selector could become another saturated rule stack if not constrained. It
must therefore be categorized, tested, and ablated by rule family.

The event-recall metric is also non-trivial because Gan labels do not provide
gold event annotations. Any event-recall claim needs either manual annotation, a
narrow "gold-answer-supporting evidence was extracted" proxy, or a separately
audited review protocol.

### First Experiments

- Run the LLM event extractor on 25/50/250 validation rows.
- Score schema validity, exact evidence validity, and gold-answer-supporting
  event coverage separately from final-label correctness.
- Compare selector variants: minimal current-event selector, temporal selector,
  seizure-free-aware selector, and full selector.
- Report rows where event extraction was correct but deterministic selection
  failed.
- Require selector variants to declare rule categories and produce row-change
  counts against the same extracted event set.

## Architecture 2: Deterministic Candidate Generator, LLM Adjudicator

### Decomposition

1. Deterministic extraction proposes multiple candidate events and labels with
   evidence spans.
2. An LLM adjudicator chooses among candidates, rejects unsupported candidates,
   or emits `unknown` / `no seizure frequency reference`.
3. Deterministic code validates and formats the chosen answer without changing
   clinical interpretation.

### Research Hypothesis

The deterministic system is useful as a high-recall retrieval layer, while the
LLM is most useful for semantic adjudication: current versus historical,
seizure-free versus unknown, highest current frequency, semiology conflict, and
cluster interpretation.

This architecture weakens a strict LLM-first claim, but it may strengthen the
broader claim that seizure-frequency extraction benefits from auditable hybrid
division of labor.

Claim type: `hybrid_llm_adjudicator`. The deterministic generator is allowed to
shape the search space, while the LLM adjudicator is the prediction-bearing
semantic selector.

### Why It Is Worth Testing

Many known failures are selection failures, not simple extraction failures. The
current deterministic V1 ablations already show that temporal selection and
seizure-free/no-event interpretation are major performance drivers. An LLM
adjudicator could be pointed exactly at those ambiguous cases.

### Risks

The LLM may simply rubber-stamp deterministic candidates. Candidate ordering,
prompt wording, and inclusion of deterministic scores could bias the result.
Candidate recall is a hard precondition: if the correct answer is not present in
the candidate set, adjudicator accuracy cannot be interpreted as a reasoning
failure.

### First Experiments

- Present unordered candidate sets with evidence but without gold labels or
  deterministic confidence scores.
- Shuffle candidate order across runs or use a fixed non-score-derived order.
- Compare deterministic top candidate, LLM note-only output, and LLM
  adjudicated candidate output.
- Focus the first slice on rows where deterministic ablations changed the
  prediction.
- Track whether the LLM improves selection or merely preserves the original
  deterministic error.
- Report candidate-set recall using a documented proxy before scoring the
  adjudicator as a selector.

## Architecture 3: Section And Claim Graph Pipeline

### Decomposition

1. Segment the clinical letter into meaningful zones: history, interval history,
   diary/log summaries, medication changes, plan, impression, and other
   note-specific sections.
2. Extract atomic seizure-frequency claims from each zone.
3. Build a graph or table of claims with temporality, assertion status,
   semiology, frequency, anchor date, certainty, and evidence.
4. Query the resulting clinical state representation to produce the final Gan
   label.

### Research Hypothesis

The task is not best modeled as direct label extraction. It is better modeled as
clinical state construction followed by a benchmark-specific query.

This architecture separates "what facts are present in the note?" from "which
fact answers the Gan question?" more strongly than the current structured
extractor does.

### Why It Is Worth Testing

The retrospective shows repeated trouble around recency, competing windows,
multiple semiologies, seizure-free statements, current non-epileptic events, and
date anchors. A graph-shaped intermediate representation could make those
conflicts visible instead of forcing them into final-label repair.

### Risks

The representation may become too complex for rapid iteration. The graph could
also create new schema-validity problems unless the first version is deliberately
small.

The first implementation should therefore be a flat claim table, not a true
graph. A graph should only follow if the table exposes relationship failures
that cannot be represented as columns.

### First Experiments

- Start with a deliberately small flat claim table before implementing a true
  graph.
- Use deterministic or LLM sectioning as a controlled variant.
- Score claim-table completeness and final-query accuracy separately.
- Inspect whether failures arise from segmentation, claim extraction, temporal
  anchoring, or final querying.
- Treat the final Gan query as a named component with its own ablation, because
  that query is where benchmark-specific selection policy can hide.

## Architecture 4: Multi-Role LLM Debate With Frozen Tools

### Decomposition

1. An extractor role lists candidate seizure-frequency facts with evidence.
2. A skeptic role challenges unsupported, historical, or irrelevant facts.
3. A temporal role focuses only on currentness, anchor windows, and recency.
4. A final selector role chooses the answer from the surviving facts.
5. Deterministic code performs schema validation, evidence checks, arithmetic,
   and accepted-label formatting.

### Research Hypothesis

Some errors are reasoning-compression failures. A single prompt may be asked to
extract, normalize, select, temporally reason, and format at once. Specialized
roles may produce better decisions by making disagreement explicit before the
final label.

### Why It Is Worth Testing

This is bold enough to reveal whether decomposition helps at all before more
careful engineering. It may also produce useful row-level rationales even if it
is too expensive for the final system.

Claim type: `diagnostic_probe` until proven otherwise. This should not be a
near-term production candidate unless it demonstrates a specific advantage over
a single-role selector on a named failure family.

### Risks

It is more expensive, more variable, and harder to reproduce than a simple
pipeline. It could also produce persuasive but unsupported rationales. Evidence
validation and fixed role contracts are therefore mandatory.

Its outputs should be interpreted as diagnostic evidence about decomposition,
not as paper-facing performance evidence, until variance and reproducibility are
measured.

### First Experiments

- Run only 25 or 50 validation rows at first.
- Use the same extracted candidate set for single-selector and multi-role
  selector comparisons.
- Require every role to cite evidence substrings.
- Report changed rows by whether debate improved, preserved, or worsened the
  final answer.

## Architecture 5: Program-Synthesized Rule Families From Error Taxonomy

### Decomposition

1. Run a frozen baseline or small LLM/hybrid candidate.
2. Generate row-level failure taxonomies from validation artifacts.
3. Use LLM assistance or program synthesis to propose candidate deterministic
   rule families.
4. Accept rules only if they are categorized, tested, ablatable, and reviewed for
   portability.
5. Report rule-family contribution and regression counts.

### Research Hypothesis

Rule discovery can be a disciplined research process rather than an implicit
repair chase. The question becomes: which deterministic clinical rules are
portable, which are Gan-specific, and how much does each family contribute?

This architecture treats deterministic rules as a first-class scientific object,
not as hidden glue around an LLM.

Claim type: `deterministic_first` or `diagnostic_probe`, depending on whether
the accepted rule families produce final predictions or only inform analysis.

### Why It Is Worth Testing

The project already learned useful things from deterministic ablations. This
architecture makes that activity explicit and could produce a strong paper table
about rule category utility and brittleness.

### Risks

This can overfit validation quickly if proposed rules are accepted because they
improve local score. The acceptance process must require portability labels,
negative tests, regression counts, and ablation evidence.

Rules proposed from validation failures should be reviewed as failure-family
rules, not row-specific patches. Any Gan-specific or benchmark-format rule must
remain labeled as such even when it improves score.

### First Experiments

- Freeze a baseline before proposing new rules.
- Create one rule proposal per failure family, not one rule per row.
- Require each proposed rule to declare its portability category.
- Compare accepted rules on 25/50/250 validation slices before any full
  validation run.

## Cross-Architecture Experiment Matrix

The next research phase should avoid choosing one architecture too early. A
minimal matrix could look like:

| Architecture | 25-row goal | 50-row goal | 250-row promotion gate |
| --- | --- | --- | --- |
| LLM extractor + deterministic selector | schema validity, evidence validity, and gold-answer-supporting event coverage | selector error taxonomy on fixed extracted events | promote only if selector-family ablations explain gains and regressions |
| Deterministic candidates + LLM adjudicator | candidate prompt feasibility and candidate-set recall proxy | changed-row improvement rate over deterministic top candidate | promote only if shuffled/unscored adjudication improves named selection failures |
| Section/claim graph | flat claim-table viability | temporal/conflict failure analysis with query errors separated | promote only if table/query ablations localize errors and reduce hidden repair |
| Multi-role LLM debate | reasoning transcript quality and evidence support | single vs multi-role comparison on the same candidate facts | keep diagnostic unless a named failure family improves enough to justify cost |
| Program-synthesized rules | rule proposal discipline | portability, negative-test, and regression review | promote only as named rule-family ablations, not as silent repair |

The matrix is intentionally uneven. Some architectures are plausible production
candidates. Others are diagnostic probes. The point is to prevent the next phase
from collapsing into another local optimization path.

## Recommended Near-Term Branches

The two strongest near-term candidates are:

1. LLM event extractor with deterministic selector.
2. Section and claim graph pipeline.

The first offers a clean, honest hybrid system with strong ablation discipline.
The second most aggressively reframes the task and may reveal that the current
schemas are still too final-label-shaped.

Before either branch becomes the main development path, the current cleaned
attribution condition should be completed or explicitly suspended: raw
structured model selection plus strict format-preserving repair only. Otherwise
this architecture-space reset could avoid, rather than resolve, the open
question about how much of the previous gain belonged to model reasoning.

The program-synthesized rule-family architecture should run as a discipline
layer alongside either of those candidates. It can prevent future deterministic
improvements from becoming invisible semantic repair.

## Bottom Line

The next stage should not ask only how to improve the current structured LLM
pipeline. It should ask which task decomposition makes seizure-frequency
extraction most inspectable, portable, and scientifically credible.

The current repair-heavy structured pipeline remains a useful warning and a
source of artifacts. It should not be the gravitational center of the research
program.
