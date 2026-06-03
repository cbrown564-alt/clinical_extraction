# Gan 2026 LLM-Heavy Decision 0007 Validation25 Contract Triage

- Date: 2026-06-03
- Artifact triaged: `experiments/gan2026_llm_heavy_evidence_selection_with_deterministic_adapters_validation25_gpt41mini_v0_2026-06-03.jsonl`
- Pipeline: `llm_heavy_evidence_selection_with_deterministic_adapters`
- Surface: validation25 under `gan2026_split_v1`
- Mode: saved-output row review; no hosted calls
- Scorer/split policy: unchanged
- Decision: revise contract before another run

## Summary

The v0 Decision 0007 run produced 25/25 typed records with no adapter parse
failures, but failed the promotion gate because selected evidence exactness was
19/25, selected operand completeness was 22/25, and raw parser-facing labels
were 0/25 scorable. The mechanical adapter reached 19/25 Purist, so the current
artifact is useful as a diagnostic of clinical selection and operand exposure,
not a promotable LLM-heavy result.

## Failure Slices

### Exact-Evidence Failures

Rows: `10`, `40`, `79`, `103`, `409`, `446`.

These are mostly copy-contract failures around special characters rather than
wrong clinical facts. The model selected the correct clause family but emitted
escaped/control/entity forms where the note contains the literal `<=`-style
Unicode glyph. The next prompt should explicitly require exact source copying,
including Unicode inequality symbols, and should forbid HTML entities, control
character encodings, and normalized mathematical symbols inside evidence fields.

Rows `10` and `446` are also adapted-label misses because the selected
frequency operands expose only `occurrences_high` for phrases like at most four
per day / twice per week. The v1 contract should require a concrete lower bound
when the model's selected clinical answer is scorer-facing exact frequency, or a
separate inequality flag when it is intentionally selecting an upper-bound fact.

### Missing Or Inconsistent Operands

Row: `128`.

The selected fact is typed as `cluster_frequency`, but the evidence and emitted
frequency operands describe the actual scorer-facing fact: `17 per month`.
Cluster operands are empty, so the adapter has no complete cluster cadence to
render. This is a contract inconsistency, not a scorer problem.

The v1 contract should require:

- `clinical_kind=frequency` for total seizure burden such as `17 per month`,
  even when the note mentions clustering.
- `clinical_kind=cluster_frequency` only when the answer itself is a cluster
  cadence, such as one cluster per four weeks.
- Consistency between `clinical_kind` and the non-null operand family used for
  rendering.

### Wrong Selected Clinical Fact Or Operand

Rows: `187`, `190`, `280`.

Rows `187` and `190` select clinically relevant cluster cadence but render a
cluster syntax label, while the gold normalization expects the cadence as a
frequency label. This is a cluster-axis ambiguity: the model should expose both
cluster cadence and final scorer-facing axis, and the adapter should render only
the selected final answer axis.

Row `280` identifies the right current day window but emits a numeric lower
bound of 2 instead of the vague count `multiple`, yielding `2 per 1 day` rather
than `multiple per day`. The v1 contract should instruct that words such as
`multiple`, `many`, and `several` populate `vague_count` unless an exact count is
explicitly stated.

### Raw Parser-Label Grammar

All 25 raw parser-facing labels are unscorable because they use underscored
diagnostic tags such as `frequency_1_per_7_days`, `frequency`, or
`cluster_frequency` instead of parser-ready Gan labels.

The v1 contract should give a closed grammar for `raw_model_parser_label`:

- exact frequency: `N per D unit` or `N to M per D to E unit`
- vague frequency: `multiple per unit`
- seizure-free: `seizure free for D unit`
- sentinel: `unknown` or `no seizure frequency reference`
- no prefixes, underscores, plural units, prose modifiers, or cluster tags
  unless cluster syntax is explicitly being tested as a side-car

## Proposed V1 Contract Change

Make a prompt/schema-only revision before another live run:

1. Rename the prompt version and typed schema to v1.
2. Add a raw parser-label grammar block to `task_instructions` and
   `output_contract`.
3. Add exact evidence copy rules that preserve Unicode and forbid escaped
   entities/control encodings in evidence fields.
4. Add clinical-kind/operand consistency rules for frequency versus cluster
   frequency.
5. Add explicit vague-count guidance for `multiple`, `many`, and `several`.
6. Keep the mechanical adapter, scorer, split manifest, and Decision 0007 gate
   unchanged for the next validation25 smoke.

## Interpretation

This triage supports a targeted v1 contract revision. Do not promote v0 or run
validation50 from this artifact. The next validation25 run should be interpreted
primarily by raw parser-label scorable count, selected-evidence exactness,
operand completeness, and the same six adapted-miss rows.
