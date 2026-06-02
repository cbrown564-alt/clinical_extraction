# 0007: LLM-Heavy Owns Clinical Selection, Deterministic Code Owns Mechanical Adapters

Date: 2026-06-02

## Decision

For Gan 2026 `llm_heavy` runs, "LLM-heavy" means the model owns the
prediction-bearing clinical selection, not every parser-ready or
benchmark-facing surface detail.

The model should select:

- the relevant clinical fact;
- the source evidence;
- the temporal state and current-versus-historical interpretation;
- the competing-event or competing-seizure-type choice;
- the operands needed for arithmetic, interval, duration, or cluster rendering.

Deterministic code should intentionally own mechanical and benchmark-facing work
that frees model capacity for clinical interpretation:

- parser-ready Gan label formatting;
- unit grammar, plural handling, and allowed-label syntax;
- arithmetic from model-selected operands;
- total-window rendering such as `3 events over 6 weeks` to `3 per 6 week`;
- seizure-free duration calculation from model-selected seizure-free or
  last-event evidence;
- cluster syntax rendering from model-selected cluster operands;
- stable Gan conventions such as bare `bimonthly` or `biweekly` mappings;
- schema/alias repair that does not change the selected clinical fact,
  semantic kind, or selected evidence.

This decision supersedes the narrow part of decision 0006 that required
`llm_heavy_clinical_frequency_reasoner_v2` to prove model-owned parser-ready
selected-evidence arithmetic/rendering before deterministic arithmetic could be
used in the primary score layer. Decision 0006 remains useful as a historical
diagnostic smoke and attribution warning, but the promoted architecture should
not force the model to memorize mechanical Gan syntax when deterministic code
can apply it more transparently.

## Boundaries

Deterministic code may compute or render from model-selected evidence and still
be part of an LLM-heavy primary score layer.

Deterministic code must not silently choose a different clinical fact in an
LLM-heavy primary score layer. If deterministic code selects among competing
clinical facts, competing graph nodes, seizure types, temporal states, or
candidate events, the run is hybrid.

Named hybrid implementations may allow deterministic clinical selection. That
is an acceptable architecture, but reports must call it hybrid rather than
LLM-heavy.

Synthetic or Gan-template-specific diary/log aggregation remains research-only
until portability is demonstrated outside Gan-style notes. These rules may be
used in `rules_only` comparators, hard slices, and ablations, but they should
not become default LLM-heavy primary adapters merely because they improve Gan
validation rows.

## Context

The Workstream B rule-ownership audit showed that many deterministic components
were being judged as attribution risks because the raw model did not emit the
exact final Gan label. User clarification changed the intended architecture:
the project should not maximize model burden. It should allocate each decision
to the component that can make it most transparently and reproducibly.

The earlier LLM-heavy and typed-adapter smokes showed a recurring pattern:
models can often select useful evidence but lose points on parser grammar,
arithmetic rendering, cluster syntax, or arbitrary benchmark conventions.
Forcing those conventions into the prompt risks spending context and attention
on mechanical details instead of the harder clinical task: selecting the right
current seizure-frequency fact from messy source text.

Decision 0005 already separated arbitrary benchmark-format conventions from
clinical reasoning. This decision extends that separation into the definition
of an LLM-heavy run: deterministic benchmark adapters are not a compromise if
they only compute from, or render, the model-selected clinical fact.

## Ownership Rules

Use these categories in reports and run metadata:

- `LLM-heavy`: the model selected the clinical fact, evidence, temporal state,
  and operands; deterministic code may render the final Gan-compatible label.
- `LLM-owned clinical selection`: the raw model output identifies the selected
  clinical fact and evidence that the deterministic adapter uses.
- `deterministic adapter`: deterministic code maps an already selected fact to
  parser-compatible syntax, benchmark convention, arithmetic result, or duration
  rendering.
- `hybrid`: deterministic and model components both contribute semantic
  selection, candidate choice, graph projection, or competing-fact arbitration.
- `research-only comparison`: deterministic logic is useful on Gan-style
  patterns but lacks enough portability evidence for default LLM-heavy scoring.

## Examples

LLM-heavy with deterministic adapter:

- Model selects evidence: "bimonthly focal seizures."
- Deterministic adapter maps Gan convention: `1 per 2 month`.
- Claim language: LLM-heavy clinical selection with deterministic benchmark
  adapter.

LLM-heavy with deterministic arithmetic:

- Model selects evidence and operands: "three events over the past six weeks."
- Deterministic adapter renders: `3 per 6 week`.
- Claim language: LLM-heavy clinical selection with deterministic arithmetic
  adapter.

LLM-heavy with deterministic seizure-free duration:

- Model selects current last-event evidence and clinic date.
- Deterministic adapter computes the month duration and renders the Gan label.
- Claim language: LLM-heavy clinical selection with deterministic duration
  adapter.

Hybrid, not LLM-heavy:

- Model extracts several candidate nodes.
- Deterministic projection chooses among current frequency, historical
  frequency, seizure-free state, and unknown state.
- Claim language: hybrid graph projection or hybrid clinical selection.

Research-only until portability:

- Deterministic code recognizes a Gan-style synthetic monthly diary template
  and aggregates sparse month counts.
- Claim language: research-only or rules-only comparator unless portability is
  shown outside Gan-style notes.

## Consequences

- Future LLM-heavy prompts should prioritize source evidence, clinical
  selection, temporal interpretation, and operand exposure over memorizing Gan
  grammar.
- Scoring reports should include enough trace data to prove that deterministic
  adapters computed from model-selected facts rather than replacing them.
- Attribution reports should distinguish wrong selected fact from right fact
  with deterministic rendering.
- Component ablations should still report raw model labels, deterministic
  adapter layers, and hybrid projection layers separately.
- Decision 0006-style parser-ready rendering smokes may still be run as
  diagnostics, but failing one does not by itself reject deterministic adapters
  as primary LLM-heavy components.
- Workstream B's rule-ownership matrix is the active policy source for deciding
  whether a rule is a deterministic adapter, model instruction, hybrid side-car,
  or research-only comparison.

## Required Reporting

Any LLM-heavy run using deterministic adapters must report:

- the raw model-selected evidence and selected operands;
- whether selected evidence is exact/source-near;
- the deterministic adapter families used;
- rows where adapters changed the parser-facing final label;
- rows where deterministic code would have selected a different clinical fact,
  if such diagnostics are available;
- raw, adapter, and hybrid/projection score layers when those layers exist.

Do not describe a result as LLM-heavy if deterministic code made the clinical
selection that determined the final answer.
