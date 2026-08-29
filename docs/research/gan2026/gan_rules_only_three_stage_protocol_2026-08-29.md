# Protocol: Gan rules-only three-stage reconstruction (Phases A–C)

Date: 2026-08-29
Status: predeclared before implementation; Phase A executes first
Owner: this file
Brief: [reconstruction brief](gan_rules_only_three_stage_reconstruction_brief_2026-08-29.md)
Mirrors: [ExECT restructure protocol](../exectv2/exect_rules_only_recall_first_restructure_protocol_2026-08-27.md)
Guardrail: `gan2026-scoring-guardrail` (scorer, sentinels, and Purist/Pragmatic
mapping are untouched throughout)

## Primary question

Can the Gan rules-only program be re-specified as three independently
stoppable stages — tagged find ledger, encode, Select sequence —
score-neutrally to the living `run_record`, and once instrumented, how
much of the residual development error is Select headroom (candidates
present but losing competition) versus find recall (gold never in
the ledger)? This partition decides where Phases B–C spend effort.

## Data, rows, scorer

- Dataset/split: Gan 2026 `gan2026_split_v1` validation (`dev750`,
  750 records via `load_records_for_split`). `test450` is sealed for
  all of Phases A–C; the aggregate-only Phase D replay is owned by
  [phase_d_protocol](gan_rules_only_three_stage_phase_d_protocol_2026-08-29.md).
- Row policy: `development_review_permitted` on `dev750` only.
- Scorer: Purist accuracy (primary) and Pragmatic (secondary) via the
  existing `score_label` / `map_purist` / `map_pragmatic`. No scorer,
  label-form, parse-bound, or sentinel change in any phase. The nine
  benchmark shorthand rows remain prohibited from hand-tuning.
- Comparator: living `run_record(architecture="rules")` — the promoted
  five-cell rules row (`dev750` select 0.89 on the living grid;
  `test450` 321/450 = 0.71, not replayed here).
- Zero model calls in all phases.

## Stage-stop policy (decided now, before any measurement)

The select stop is the submitted final label, unchanged. Because Gan
submits one label per record, the earlier stops need a declared pick:

1. **Find stop (Purist-commensurate):** the raw builder label of
   the first ledger candidate in document order (evidence-span start;
   unlocatable spans last; tie-break = ledger emission order). The pick
   is over the **wide pre-drop ledger**: select-stage drops (duplicate,
   fragment, historical) are Select work and do not narrow the
   find stop. Rule-`exclude` suppressions never compete (they are
   span records with no built candidate). Unparseable raw labels score
   as unscorable (wrong), not smoothed. Rationale: "find without
   selection" reads the first frequency-relevant statement; document
   order is the least tuned neutral policy available.
   *(Amended 2026-08-29 before any measurement: an earlier sentence had
   dropped records not competing, which contradicts the stage boundary
   that assigns drops to Select. No numbers had been produced.)*
2. **Encode stop (Purist-commensurate):** the normalized label
   (`repair_prediction_label` + `label_to_frequency_record`) of the
   same document-order-first pick. Find→encode isolates encode on
   a fixed pick; encode→select isolates selection.
3. **Oracle ceiling (diagnostic, not a grid column):** fraction of
   records where any surviving (post-drop) ledger candidate's
   normalized label is Purist-correct. `oracle − select` = Select
   headroom; `1 − oracle` = find/encode recall gap. A second
   wide-ledger oracle (including dropped candidates) is recorded to
   show whether the relocated drops discard any Purist-correct
   candidate.

These are recorded per phase. The five-cell grid and dissertation
table are not changed by this protocol; wiring stage stops into
`_gan_grid` happens only if Phase D's predeclared verdict is
`promotion_accepted`.

## Phase A — score-neutral instrumentation (this session)

Minimal change: a three-stage runner in the gan2026 orchestration
package that produces (a) a tagged find ledger containing every
raw candidate **pre-dedupe and pre-prune**, plus span-level records of
rule-`exclude` suppressions (recorded, never built or competed); (b)
an encode pass over the ledger; (c) a Select sequence whose first
rules are the relocated drops — duplicate drop, contained-fragment
drop, historical-rate drop — each tagged with its reason, followed by
the existing priority-ladder competition. No rule pattern, builder,
exclude predicate, prune condition, repair, or selection cue changes.

Gates (all must hold on 750/750 `dev750` records):

- **A1 identity:** final label AND selected evidence identical to the
  comparator `run_record` on every record.
- **A2 relocation identity:** with the relocated drops enabled (they
  are the default), the surviving competition pool is set-identical to
  the comparator's post-prune candidate list on every record.

Outputs: stage stops and oracle ceiling under the declared policy;
drop-reason and exclusion counts; per-mode residual partition
(Select-headroom vs recall-gap) for the 69-row error mass.

Stop rule: if A1 cannot be met without a semantic change, Phase A
reports "blocked by instrumentation" with the first divergent record
class and stops; no stage numbers are read from a non-identical run.

## Phase B — recall-first find (separate session)

Widen the ledger with tagged provisional candidates (narrative rate
expressions from `g_missed_rate_dropped_to_unknown`, excluding the
nine protected shorthand rows), keeping the select stop
mention-identical until Phase C decides keeps. Gate B: find
oracle ceiling rises with zero select-stop label changes.

## Phase C — Select precision recovery (separate session)

Explicit ordered Select sequence: tagged drops, subtype-negation scope
gate (mode `g_unknown_over_resolved_to_free_or_rate`), then
competition. Every new rule switchable; acceptance requires
isolated-positive, leave-one-out-negative, and **zero**
comparator-correct row regressions on `dev750`. Trials that harm
comparator-correct rows are rejected (the measured G1–G4 and ExECT
lesson: do not bolt rules onto a mismatched ledger).

## Artifacts

`experiments/gan2026_rules_only_three_stage_20260829/` — one JSON per
arm: date, dirty-tree note, config, gate results, stage stops
(Purist + Pragmatic), oracle ceiling, drop/exclusion counters, and
per-record rows (`source_row_index`, stage labels, gate booleans) for
development inspection. Narrative results doc follows the artifact.

## Claim boundary

Phases A–C are development instrumentation on `dev750` only. Phase D
owns the holdout aggregate and, after `promotion_accepted`, the cited
rules row (325/450) and measured stage stops.
