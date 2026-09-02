# Protocol: Gan rules-only Phase E (find/encode split and Select relocation)

Date: 2026-08-30
Status: complete; gates E1–E4 held on `dev750` 2026-08-30
Report: [Phase E result](gan_rules_only_three_stage_phase_e_2026-08-30.md)
Successor: [Phase E2](gan_rules_only_three_stage_phase_e2_protocol_2026-08-30.md)
Owner: this file
Parent: [Phases A–C protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Brief: [reconstruction brief](gan_rules_only_three_stage_reconstruction_brief_2026-08-29.md)
Guardrail: `gan2026-scoring-guardrail`
Split: `dev750` only; `test450` sealed. Zero model calls.

## Primary question

Can the promoted three-stage rules program expose find, encode, and
Select as distinct measured outputs without changing the submitted
select label?

Two remaining fusions from Phase A are in scope:

1. Extract-time Select: `RuleSpec.exclude` and inline rate distractor
   / historical-lead-in skips never enter the ledger.
2. Find+encode fusion: builders write codebook labels at match time, so
   find and encode Purist stops are identical by construction.

Naming the anonymous inline producers is required so find-side
attribution is possible after (1).

## Why this matters

Phase D promoted measured stops **292 / 292 / 325** on `test450`. The
encode column is not an encode measurement: Phase A–C recorded a zero
encode delta because labels are already in designed form at find. Select
is cleaner than the Compact-era program but still cannot see excluded
spans. This phase is instrumentation plus same-fact encode extraction,
not a select lift.

## Stage-stop policy (decided now)

Select stop is unchanged: the submitted final label.

1. **Find stop:** the `find_tag` of the first wide-ledger candidate in
   document order, including Select-dropped entries. The tag is the
   pre-codebook payload: rate slots as `{count}/{unit}` (raw match
   tokens, optional `{count}/{denominator} {unit}`), seizure-free as
   `seizure_free`, unknown as `unknown`, no-reference as
   `no seizure frequency reference`, cluster as `cluster:{count}/{period}:{size}`
   when slots exist else the legacy custom label. Unparseable tags score
   wrong under Purist. This column is **not** commensurate with LLM find
   (those rows emit codebook-ish labels).
2. **Encode stop:** `repair_prediction_label` + parse of
   `encode_find_fact` on the same pick. Encode is the only writer of
   codebook phrasing (`N per unit`, seizure-free duration forms).
3. **Select stop:** competition over candidates that are not tagged
   Select drops (existing relocated drops plus the newly relocated
   extract-time drops).

Cited five-cell find/encode/select numbers stay **292 / 292 / 325**
until a later predeclared aggregate-only replay. This protocol does not
authorize `_gan_grid` rewiring.

## Comparator and gates

Comparator: living `run_record` for the default three-stage runner;
`run_record_three_stage(phase_c_candidate_config())` select label and
evidence for the promoted candidate.

- **E1 select identity:** default runner select label and evidence
  identical to `run_record` on every `dev750` record. Promoted-config
  select label and evidence identical to today's
  `phase_c_candidate_config()` runner on every `dev750` record.
- **E2 relocated drops:** every `RuleSpec.exclude` hit, every inline
  medication/dose distractor skip, and the inline historical-lead-in
  skip appear as ledger rows with a named `LedgerDropReason` and do not
  enter the competition pool.
- **E3 named producers:** no wide-ledger candidate from
  `extract_wide_candidates` may carry `rule_id="unknown"`.
- **E4 encode is not identity on rates:** at least one fixture exists
  where find_tag ≠ encode codebook form on the same pick (word-number
  rate → `N per unit`).

Stop if E1 fails. Do not read development stage counts from a
select-divergent run. Do not inspect `test450`.

## Minimal change

- Add `FindFact` + `encode_find_fact` / `find_tag`. Rate builders and
  inline rate emitters populate slots; seizure-free builders tag state
  only; encode writes codebook labels into `RawCandidate.label` for
  Select compatibility.
- `apply_rule` builds excluded matches and marks `deferred_drop`.
  `_extract_candidates` (living `run_record`) strips deferred rows
  before prune so the single-stop program does not change.
- Inline distractor / historical skips emit deferred rows the same way.
- Name every inline regex producer in rate and unknown extraction.

No scorer, sentinel, `label_forms`, or holdout change. No new Select
keep. The nine protected shorthand rows stay unfixed.

## Artifacts

`experiments/gan2026_rules_only_three_stage_phase_e_20260830/` —
`dev750` summary (select-identity gates, new find/encode Purist counts,
drop-reason counts, anonymous-producer count = 0) after E1 holds.
Narrative result follows the artifact.

## Claim boundary

Development instrumentation on `dev750`. Not a cited-row change. Not
holdout evidence. Find Purist is expected to fall because the find tag
is no longer a codebook label.
