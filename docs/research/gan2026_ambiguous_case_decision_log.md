# Gan 2026 Ambiguous Case Decision Log

Purpose: keep a running, durable record of ambiguous seizure-frequency
representation cases and the project's interpretation decisions. These cases
come back repeatedly in RQ1/RQ2/RQ4 work, so decisions here should be treated as
stable policy unless explicitly superseded by a later decision record.

Related policy:
`docs/research/gan2026_llm_component_interpretation_policy_and_controlled_experiments_2026-06-03.md`

## How To Use This Log

For each recurring ambiguous case, record:

- the clinical phrase or representation;
- whether it is a valid clinical fact;
- whether it is projection-compatible with a Gan label;
- which component should receive credit or own the remaining failure;
- the transparent projection policy when a benchmark label is required;
- examples or row ids when available;
- open questions that need controlled experiments.

Do not use this log to tune the LLM away from faithful clinical language. Use it
to make projection, uncertainty, and first-failure ownership consistent.

## Decisions

### ACD-001. `multiple times per week`

Status: firm decision.

Decision: `multiple times per week` is a correct clinical representation of
`multiple per week`.

Interpretation:

- The phrase preserves the clinical fact.
- It is projection-compatible with the Gan label `multiple per week`.
- It should not be counted as an LLM candidate-generation or evidence-selection
  failure merely because it is not already in benchmark label syntax.

Component ownership:

- Candidate generation receives representation credit when evidence supports an
  active current burden.
- Projection/rendering owns the conversion from `multiple times per week` to
  `multiple per week`.

Projection policy:

- Project to `multiple per week` when the selected evidence supports current
  recurring seizure burden within a week.
- Preserve the source phrase in evidence or raw frequency fields for audit.

Open questions:

- Catalogue equivalent projection-compatible variants, including `several per
  week`, `several focal seizures per week`, `many times per week`, and
  `frequent weekly events`.

### ACD-002. `multiple per shift`

Status: firm decision with projection policy to catalogue.

Decision: `multiple per shift` is a valid clinical fact. It is ambiguous because
`shift` is not a calendar denominator, but the ambiguity belongs to the clinical
fact and should be represented transparently.

Interpretation:

- The phrase should not be counted as an LLM failure when it faithfully reflects
  the source.
- It should be classified as denominator-ambiguous or uncertainty-bearing.
- The system should preserve the original phrase and evidence rather than force
  the LLM to emit a benchmark label directly.

Component ownership:

- Candidate/evidence components receive credit for preserving the faithful fact
  and evidence.
- Projection policy owns any conversion into a Gan-compatible calendar label.

Projection policy:

- Conservative projection to `multiple per week` is reasonable when the note
  context supports recurring shifts and no better calendar denominator is
  stated.
- Mark the projection as policy-mediated and denominator-ambiguous.
- If shift frequency or schedule context is absent and the benchmark answer
  cannot be responsibly inferred, preserve the fact and allow an uncertainty or
  abstention path depending on the experiment protocol.

Open questions:

- Catalogue shift/work/school/activity-window variants and decide when they
  project to weekly burden versus remain denominator-ambiguous.
- Test this case in isolated projection experiments with fixed evidence and
  fixed candidate facts.

## Catalogue Backlog

Add recurring cases here before or during the frozen component-projection panel:

- projection-compatible phrases for weekly/monthly categories;
- vague-but-current burden phrases such as `frequent`, `many`, `several`, and
  `occasional`;
- shift, workday, school-day, sleep-window, and activity-window denominators;
- cluster cadence versus per-cluster burden;
- seizure-free statements with later breakthrough events;
- no definite seizure events versus no seizure frequency reference;
- current-month no-event snippets in patients with broader active burden;
- diary/log aggregations with partial months, mixed zero/nonzero months, or
  percent-change phrasing;
- competing semiologies with same-window additive counts;
- historical high burden versus current lower burden or seizure freedom;
- unknown boundary cases where seizure-like events are present but not
  decisively epileptic or countable.
