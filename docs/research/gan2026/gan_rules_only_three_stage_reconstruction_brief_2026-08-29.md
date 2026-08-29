# Reconstruct Gan rules-only for find / encode / select

Date: 2026-08-29
Status: follow-up brief; not a protocol and not a five-cell change
Owner: this file
For: the next session that rebuilds standalone Gan rules, not a rule patch
Related: [ExECT reconstruction brief](../exectv2/exect_rules_only_three_stage_reconstruction_brief_2026-08-27.md),
[ExECT recall-first restructure](../exectv2/exect_rules_only_recall_first_restructure_2026-08-27.md),
[five-cell grid](gan_five_cell_grid_2026-08-22.md),
[grid protocol](gan_five_cell_grid_protocol_2026-08-22.md),
[G5 remeasure & plateau closure](rules_only_campaign_g5_remeasure_2026-08-15.md),
[codebook-encode development](gan_codebook_encode_rule_development_2026-08-22.md),
[stage roles](../paper/gan_rules_and_llms_across_stages_2026-08-21.md),
[Gan is the dissertation paper](../../paper/decisions/gan-is-the-dissertation-paper.md)

## Why this exists

The dissertation five-cell table reports the Gan rules-only row as a
completely flat result: find **0.71**, encode **0.71**, select
**0.71** on locked `test450` (321/450, living gold), against cell 3
(LLM / rules / rules) at **0.83**. The flatness is **by
construction, not measurement**. `_gan_grid` in
`src/clinical_extraction/paper/five_cell.py` writes the one select
count into the extract and encode ablation slots, and
`replay_gan_rungs` scores only `final_value`. There is exactly one
scorable program stop today.

ExECT already ran this play. Its rules row was a Compact-era program
scored on a post-split measure; re-specifying it as three deliberate
stages (wide find ledger, same-fact encode, precision Select)
moved locked `test60` from **0.7725** to **0.8018** and gave the row
measured per-stage stops. The working hypothesis here is the same:
Gan rules-only interleaves encode and select decisions inside
extraction, so the published row understates what a staged rules
program can do, and the flat ablation column understates what the
paper's own modular-pipeline argument predicts.

That lift is not in hand. Do not write it as a paper sentence.
The cited rules number stays **0.71** until a predeclared
aggregate-only replay of a frozen candidate.

## What we already know

### 1. The seams exist, but they are not the three stages

`deterministic_canonical_stages.py` already names `extract_stage`,
`normalize_stage`, and `select_and_render_stage`, with typed
multi-candidate intermediates (`CandidateEvent` →
`NormalizedEvent` → `FinalSelection`). That is ahead of where ExECT
started. But the seams do not carry the locked stage meanings:

- **Encode is fused into find.** Rule builders write the
  codebook label at match time (`_build_rate_candidate` emits
  `"N per unit"` inside extract). `normalize_stage` is label repair
  (`repair_prediction_label`) plus parsing, not "write an
  already-selected fact into the designed form."
- **Select is fused into find.** `RuleSpec.exclude` predicates,
  medication-rate distractor suppression, and
  `prune_contained_frequency_fragments` (historical-rate drop,
  monthly-list fragment drop) all run during extract. A candidate the
  exclude predicate kills can never be rescued by competition. This
  is the exact failure the ExECT audit measured: Select replayed on
  a pre-narrowed ledger is a near no-op.
- The `select_and_render_stage` docstring already concedes that
  selection and formatting "do not expose a safe boundary" — the
  staging pass was renaming, deliberately not restructuring.

### 2. The true Select stage is small and heavily literal-tuned

`deterministic_selection.py` is a semantic priority ladder
(trigger-conditioned unknown 6 → current seizure-free 5 →
frequency / specific multiple 4 → generic multiple 3 → generic
seizure-free 2 → generic unknown 1 → no-reference 0) with
monthly-frequency tie-break, ablatable per reason via
`RuleGroup.TEMPORAL_SELECTION`. Its evidence cues
(`is_current_seizure_free_evidence`,
`is_specific_current_multiple_evidence`,
`frequency_summary_priority`) are long development-tuned literal
lists. Staging does not de-overfit those literals by itself, but it
makes each cue individually attributable and gate-able, which is the
precondition for de-overfitting them.

### 3. The error mass maps onto the stage split

The G5 residual catalog (`dev750`, 2026-08-15 baseline; counts
predate the living-gold refresh, the partition is still the best
error map we have) found 69 imperfect rows in four modes:

| Mode | Rows | Stage reading |
| --- | ---: | --- |
| `g_unknown_over_resolved_to_free_or_rate` | 28 | Select competition: subtype negation over-claims freedom |
| `g_missed_rate_dropped_to_unknown` | 17 | Find recall: rate never reached the ledger (9 are protected benchmark shorthand) |
| `g_granularity_and_period_mismatch` | 15 | Encode/Select boundary: adjacent-rate binning and period choice |
| `g_other_misclassifications` | 9 | Mixed |

The development/holdout asymmetry is the ExECT shape again:
`dev750` **0.89** vs `test450` **0.71** on the living grid. A
development-tuned single-stop program is the common cause candidate.

### 4. Single-rule patches already hit their plateau — measured

Phases G1–G4 tried the patch route and closed at the fairness
plateau: Candidate A (`rate.nightly_seizures`) rescued 5 development
rows and **regressed holdout by 1** (killed under stop rules);
qualifier scoping rescued 13 `unknown` rows while harming 8 valid
seizure-free letters. That is direct evidence the remaining error
mass is architectural (competition and sequencing), not a missing
alias. The ExECT parallel: the 27 Aug alias patch proved direction on
the margin; the reconstruction delivered the lift.

### 5. The LLM rows prove encode and Select do real work on this task

On the cited grid, LLM find alone is **0.79**; codebook rule
encode takes it to **0.80**; rule select takes it to **0.83**. Those
stages fire because the model ledger is wide and the encode rules are
same-fact codebook rewrites
([codebook-encode development](gan_codebook_encode_rule_development_2026-08-22.md):
22 Purist rescues, no observed harms, semantic select kept separate).
Rules-only never gets that benefit because its ledger is already
narrowed and its labels already written when Select runs.

**Caution transferred from ExECT (measured there):** bolting the
existing encode/Select rules onto today's extractors regresses.
`gan_rules_encode` governs a *model* ledger; it does not
automatically transfer to a rules ledger. Resequence first, reuse
only where the ledger shape matches.

## What we need to know

Development on `dev750` only until a frozen candidate exists. Do not
inspect `test450` rows.

1. **What is the stop policy for a single-label task?** This is the
   design question ExECT never had. ExECT scores every stage stop
   directly because the task is a mention inventory. Gan submits one
   label per letter, so a recall-first find ledger has no Purist
   number until something picks. Options to predeclare, one of:
   - find stop = neutral pick (document order, or the priority
     ladder ablated to zero) — commensurate with the grid columns but
     partly arbitrary;
   - find stop = ledger-recall diagnostic (gold label present
     anywhere in the ledger) — honest about what find is for,
     but not commensurate with the LLM rows' Purist stops, which is a
     presentation decision for the paper table.
   Decide before measuring; do not choose after seeing numbers.

2. **What is the find ledger contract per rule family?** Which
   surfaces must remain visible to later stages: historical rates
   (tagged, not dropped), distractor-adjacent matches, monthly-list
   fragments, rate-less anchors, subtype-negation seizure-free
   phrases? What stays forbidden at find (medication-dose rates
   as frequency) versus deferred to Select? The nine benchmark
   shorthand rows (`TC *nine/mo`, `sz X2/d`) remain prohibited from
   hand-tuning by research safeguards regardless of stage.

3. **What is encode-only for a deterministic candidate?** Candidate
   split: builder labels become provisional find tags; encode
   becomes the codebook rendering (rate arithmetic to `"N per unit"`,
   seizure-free date math, sentinel forms) plus
   `repair_prediction_label` and `label_to_frequency_record`. Which
   current repairs are same-fact, and which silently reselect
   (granularity/period binning is the suspect: mode 3 above)? The
   `unknown`-on-parse-failure fallback must stay explicit, not become
   silent smoothing.

4. **What is the Select sequence?** An explicit order over: dedupe,
   fragment containment, historical drop (`has_historical_lead_in`),
   distractor drop, subtype-negation scope check (mode 1), then the
   priority-ladder competition. Each rule switchable, with
   leave-one-out and row-level no-harm gates against the frozen
   comparator, mirroring the codebook-encode acceptance shape
   (rescues counted, zero observed exact-label harms).

5. **Where is the holdout hole if we may not read letters?**
   Predeclare mode-level expectations on a frozen `dev750` candidate,
   then one aggregate-only `test450` replay. Prior signal: holdout
   killed a development-positive rate rule (G1), so the predicted
   risk is find widening that leaks distractors past an
   under-specified Select. A development-only mode-1 win will not by
   itself close 0.71 vs 0.83.

6. **Two rule programs, one vocabulary.** After reconstruction, do
   rules-only find / encode / select share authority names with
   `gan_rules_encode` and the select rules on the LLM rows, or stay a
   separate namespace with a mapping? The paper currently treats
   standalone rules as a different program; a rebuild should decide
   whether that remains a feature or a debt.

7. **What must not change.** Scorer stays Purist micro-F1 on living
   gold. Sentinel distinctions (numeric rate, `unknown`,
   `no seizure frequency reference`, seizure-free) are preserved.
   No `label_forms` retune. No holdout tuning; no `test450` row
   inspection. The cited five-cell rules number stays **0.71** and
   the dissertation table is untouched until a predeclared
   aggregate-only replay. All select-precedence, sentinel, repair,
   and binning changes are semantic rules under the Gan scoring
   guardrail. Claim language: "development result" during iteration,
   "final holdout result" only for the frozen candidate's single
   replay.

## What the early signs point at

**Architecture, not a missing alias list.** G1–G4 measured the patch
ceiling. The remaining modes are competition (28 rows) and recall
(17 rows) — Select-shaped and find-shaped respectively — and
both stages are currently entangled inside extract.

**Mode 1 is the Select target.** Subtype negation over-claiming
seizure freedom is a scope decision between competing readings —
exactly what the locked taxonomy assigns to Select. The measured
13-rescue / 8-harm trade-off from qualifier scoping is what happens
when that decision is made inside find-stage code with no competitor
visible; a Select that can see both the negation and the rest of the
ledger can gate on support instead.

**Mode 2 is the find target, with the ExECT SF warning.** Wider
rate recognition must not become "emit every anchor": ExECT's
rate-less emit-all cost 0.10 F1. Widen narrowly (narrative rate
expressions), tag provisional candidates, and let Select drop
unsupported ones. The protected shorthand rows stay unfixed.

**The dissertation stakes cut both ways.** A successful
reconstruction narrows the rules-vs-cell-3 gap and adds a real
find/encode/select gradient to the rules row — which
*strengthens* the paper's modularity argument (stages matter even
within one method) while weakening any sentence that leans on 0.71
as evidence that rules are inherently poor. Draft claim text to
survive either outcome before the replay, not after.

**Development near-parity is not the story.** Rules already sit at
0.89 on `dev750`. Any rebuild that only chases development rescues
is another G1–G4; the deliverable is the holdout number and the
measured stage gradient.

## What the next session should do first

1. Read this brief, the [G5 remeasure](rules_only_campaign_g5_remeasure_2026-08-15.md),
   the [ExECT brief](../exectv2/exect_rules_only_three_stage_reconstruction_brief_2026-08-27.md)
   and [restructure result](../exectv2/exect_rules_only_recall_first_restructure_2026-08-27.md),
   and the scoring-guardrail required context — not the retired Gate
   B numbers (329/450 was older gold; living is 321/450).
2. Decide and record the stage-stop policy (question 1) before any
   measurement.
3. Write a reconstruction protocol with three independently stoppable
   programs (tagged find ledger, encode registry, Select
   sequence), Purist scoring, row-level no-harm gates against the
   frozen comparator, no `test450` inspection.
4. Instrument the rules-only find ledger (pre-encode,
   pre-prune) so later stages have something to read — today's
   `extract_stage` output is post-exclude and post-prune, which is
   the missing object.
5. Start with mode 1 (subtype-negation Select scope) and mode 2
   (narrative-rate find), in that order; treat the priority
   ladder as the Select seed, not the finished sequence.

Do not promote a new holdout number from that session unless the
protocol froze the candidate first.
