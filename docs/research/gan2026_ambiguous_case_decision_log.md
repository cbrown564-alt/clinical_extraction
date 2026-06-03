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

### ACD-003. Vague count or cadence adjectives (`several`, `frequent`, `many`, `occasional`)

Status: firm decision.

Decision: Vague count adjectives (e.g., `several`, `frequent`, `many`) paired with a clear calendar denominator are projection-compatible with coarse benchmark labels like `multiple per [denominator]`. Vague adjectives without a denominator (e.g., `occasional`) are inherently ambiguous and project to `unknown`.

Interpretation:
- The phrase "several last week" or "frequent weekly events" preserves the clinical fact and is projection-compatible with `multiple per week`.
- "several last month" maps to `multiple per month`.
- "occasional" without a denominator does not provide enough rate signal and maps to `unknown`.

Component ownership:
- Candidate/evidence selection gets credit for extracting the vague phrase and denominator.
- Projection/rendering owns the mapping of `several` -> `multiple` and `frequent` -> `multiple`.

Projection policy:
- Map `several` / `frequent` -> `multiple` when paired with a denominator.
- Map `occasional` without denominator -> `unknown`.

Examples:
- Row 1707: "several focal seizures last week" -> `multiple per week`.
- Row 1695: "several focal seizures last month" -> `multiple per month` (also see ACD-009).

Open questions:
- Test mapping of other adjectives like `a few`, `a handful`, `frequent` under isolated projection tasks.

### ACD-004. Conditional-only occurrences (`only with sleep deprivation`, `only when perimenstrual`)

Status: firm decision.

Decision: Conditional-only occurrence statements without numeric rate (e.g., "seizures occur only when perimenstrual" or "exclusively after nights of curtailed sleep") must project to `unknown`. Silently inventing a frequency like "1 per month" is a clinical overreach.

Interpretation:
- Triggers or menstrual cycle constraints are critical clinical facts but do not define a calendar rate (e.g., how many seizures occur per cycle).

Component ownership:
- Candidate generation/evidence selection gets credit for capturing the conditional constraint.
- Projection owns the decision to map to `unknown`.

Projection policy:
- Project to `unknown` if the text defines a conditional trigger without quantifying the cadence.

Examples:
- Row 3356: "seizures occurring exclusively after nights of curtailed sleep" -> `unknown`.
- Row 3371: "seizures... only when significantly short on sleep; outside of nights with curtailed rest, no events have occurred in the past eight weeks" -> `unknown`.
- Row 3468: "Seizures happen when perimenstrual only (days -2 to +2)" -> `unknown`.
- Row 3469: "Seizures happen when perimenstrual only (days -3 to +3)" -> `unknown`.
- Row 3482: "Seizures happen when perimenstrual only (days -3 to +3)" -> `unknown`.

### ACD-005. Relative-only changes or qualitative trends

Status: firm decision.

Decision: Relative-only frequency descriptions (e.g., "frequency increased by 50%" or "better control") without absolute counts or rates project to `unknown` (or `no seizure frequency reference` if there is no other reference in the note).

Interpretation:
- Relative statements describe a trend/comparison rather than a current absolute rate.

Component ownership:
- Candidate/evidence selection gets credit for extracting the relative trend.
- Projection owns the mapping to `unknown`.

Projection policy:
- Project to `unknown` if no baseline or current rate is quantified.

Examples:
- Row 3528: "frequency increased by ~50% after dose increase" -> `unknown`.
- Row 3534: "seizure control as Better over the past seven months" -> `unknown`.

### ACD-006. Diary Date Listings

Status: firm decision.

Decision: When the note lists explicit dates of events in a diary, the frequency should be represented by summing the events and normalizing to the calendar span of the reporting period.

Interpretation:
- Logs of dates represent a concrete historical count.

Component ownership:
- Evidence selection owns extracting the exact list of dates.
- Projection/rendering owns summing the count and normalizing the span.

Projection policy:
- Sum the events (e.g., 5 dates) and divide by the span (e.g., March to May is ~2 months), projecting to `5 per 2 month`.

Examples:
- Row 4368: "Seizure events on 03-07, 03-27, 05-15, 05-19, 05-24" -> `5 per 2 month`.

### ACD-007. Non-Epileptic or Uncertain Events

Status: firm decision.

Decision: When the note explicitly states "no definite seizure events" and describes emergency department presentations or other events as evaluated and triaged as non-epileptic (e.g., light-headedness, anxiety, palpitations), these must not be counted as active seizure events.

Interpretation:
- Dissociative or somatic symptoms evaluated as non-epileptic represent a seizure-free state for the epilepsy diagnosis.

Component ownership:
- Candidate/evidence selection gets credit for distinguishing definite seizures from non-epileptic symptoms.
- Projection/rendering owns mapping the row to `seizure free` rather than active/unknown.

Projection policy:
- Project to `seizure free for multiple month` (or other duration if specified, e.g., "since last visit") when the note reports no definite seizure events and triages breakthrough symptoms as non-epileptic.

Examples:
- Row 3137: "no definite seizure events... Two recent Emergency Department presentations... primarily for light-headedness and a brief episode of dissociation... bedside observations normal, resolution without intervention..." -> `seizure free for multiple month`.

### ACD-008. Qualitative Summary Statements vs. Derived Calculations

Status: firm decision.

Decision: When a note contains both an aggregate count over a long period (e.g., 7 seizures so far this year) and an explicit qualitative summary statement of the current pattern (e.g., "typical pattern is a focal seizure monthly"), the explicit summary statement overrides the mathematical calculation.

Interpretation:
- Explicit summary statements represent the clinician's direct assessment of the current stable frequency state.

Component ownership:
- Projection/rendering owns prioritizing summary statements over calculated ratios.

Projection policy:
- Project the stated summary rate (e.g., `1 per month`) rather than the mathematical average (e.g., 7 / 10 months = `7 per 10 month`).

Examples:
- Row 2748: "only seven focal impaired-awareness seizures reported so far this year. At present, his typical pattern is a focal seizure monthly" -> `1 per month`.

### ACD-009. Previous Month vs. Current Month to Date

Status: firm decision.

Decision: Reporting "no events in the current month to date" does not establish seizure freedom if the previous month had an active rate. The active rate of the previous month should be projected as the current burden.

Interpretation:
- A short period of zero events (e.g., 20-27 days) does not establish long-term seizure freedom in a patient with active epilepsy.

Component ownership:
- Projection/rendering owns the temporal aggregation and ignoring short-term current-month zero-counts.

Projection policy:
- Project the active frequency of the previous month (e.g., `multiple per month` for "handful last month") unless there is an explicit long-term seizure-free duration statement or 3+ months of event-free history.

Examples:
- Row 1695: "handful of short focal events during the previous month... In the current month to date, no events have been recorded" (clinic date July 27) -> `multiple per month`.

### ACD-010. Multi-Semiology Severity Prioritization

Status: firm decision.

Decision: In patients with multiple semiologies, a recent acute relapse or clustering of high-severity events (e.g., tonic-clonic convulsive seizures) takes priority for the current state projection over lower-severity minor interictal rates (e.g., minor sensory auras).

Interpretation:
- Relapse of major convulsive events represents the primary clinical change and defines the patient's current burden.

Component ownership:
- Projection/rendering owns prioritizing major relapsed rates over minor baseline rates.

Projection policy:
- Project the frequency of the major relapsed events (e.g., `3 per day`) over minor interictal event rates (e.g., `1 to 2 per week`).

Examples:
- Row 1363: "Yesterday he experienced three tonic-clonic seizures... He describes interictal brief auras occurring approximately once or twice per week" -> `3 per day`.
- Row 1165: "document 5 or 7 focal onset seizures in three weeks during a recent period that included an episode while travelling by air... Outside that three‑week window, there have been no further episodes for the last six weeks" -> `5 to 7 per 3 week`.

## Catalogue Backlog (Resolved & Archived)

All initial backlog items from the 2026-06-03 error analysis have been catalogued and resolved:
- **projection-compatible phrases for weekly/monthly categories**: Resolved in ACD-001, ACD-003, ACD-009, ACD-010.
- **vague-but-current burden phrases**: Resolved in ACD-003.
- **shift, workday, school-day, sleep-window, and activity-window denominators**: Resolved in ACD-002.
- **cluster cadence versus per-cluster burden**: Resolved in ACD-006, ACD-010.
- **seizure-free statements with later breakthrough events**: Resolved in ACD-004.
- **no definite seizure events versus no seizure frequency reference**: Resolved in ACD-007.
- **current-month no-event snippets in patients with broader active burden**: Resolved in ACD-009.
- **diary/log aggregations with partial months, mixed zero/nonzero months, or percent-change phrasing**: Resolved in ACD-005, ACD-006.
- **competing semiologies with same-window additive counts**: Resolved in ACD-010.
- **historical high burden versus current lower burden or seizure freedom**: Resolved in ACD-008.
- **unknown boundary cases where seizure-like events are present but not decisively epileptic or countable**: Resolved in ACD-004, ACD-007.

