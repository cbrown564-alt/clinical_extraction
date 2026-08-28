# Protocol: ExECT rules-only recall-first restructure

Date: 2026-08-27
Status: complete — Phases A–C accepted on dev140
([results](exect_rules_only_recall_first_restructure_2026-08-27.md));
Phase D replay executed, verdict development-only, cited rows unchanged
([replay](exect_rules_only_recall_first_test60_aggregate_2026-08-27.md))
Plan owner: recall-first rules restructure (chat plan, 2026-08-27)
Comparator: `run_letter` = `run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)`,
dev140 select stop **0.9167**, test60 select stop **0.8018** (promoted).
Baseline stage rungs: [stage rungs report](exect_rules_only_stage_rungs_2026-08-27.md)
(dev140 recognise/encode/select 0.9012 / 0.9150 / 0.9167).

## Primary question

Can standalone rules, restructured so that recognise is recall-first
(Diagnosis and SeizureFrequency recognise-stop recall >= 0.90 on
`dev140`), encode and select exist per family, and precision decisions
live in Select, reach a higher select-stop inventory F1 than the
promoted **0.9167** on `dev140` without any comparator-exact
regression — and does that transfer on one aggregate-only `test60`
replay?

## Fixed measurement frame

- Dataset: ExECTv2 `dev140` (140 letters, development, row inspection
  permitted). `test60` sealed until the final Phase D replay.
- Scorer: `clinical_inventory_unit_keys`, 4-family micro F1 and
  per-family P/R/F1, at the recognise, encode, and select stops.
- Zero model calls throughout.
- Comparator is frozen `ACCEPTED_THREE_STAGE_CONFIG` via `run_letter`.
- Changed-pair accounting: comparator-exact regressions, improved and
  worsened letter/family pairs, per the three-stage reconstruction
  measurement pattern.

## Phase structure and gates

### Phase A — taxonomy and plumbing (no score change permitted)

- Rule taxonomy audit doc classifying every deterministic rule as
  recognise / encode / select and by family.
- `ThreeStageConfig` gains per-family encoder and select-sequence
  configuration. Gate A1: default and accepted configs remain
  mention-identical to `run_letter` on all 140 letters.
- Score-neutral relocations: extract-internal precision drops become
  recognise emission switches paired with Select drops (SF rate-gate,
  Diagnosis non-diagnostic context, Investigations result requirement,
  Prescription plan filters — as feasibility allows). Gate A2: with
  emission plus paired drop enabled, the select stop is
  mention-identical to the comparator on all 140 letters; the
  recognise stop may change freely. Any relocation that cannot meet
  identity is recorded and parked, not forced.

### Phase B — recall-first recognise

Targets on `dev140` recognise stop (recall, exact inventory units):

| Family | Baseline R | Target R |
| --- | ---: | ---: |
| Diagnosis | 0.8298 | >= 0.90 |
| SeizureFrequency | 0.8667 | >= 0.90 |
| Prescription | 0.9709 | >= 0.9709 (no dev regression; external-coverage work) |
| Investigations | 0.9706 | >= 0.99 |

Levers (from the dev140 FN characterization of 2026-08-27): Diagnosis
specific-concept surfaces and nested ancestors as direct;
SF named-type / seizure-free / heading-state / rate-less candidates as
direct; Prescription external ASM dictionary, typo tolerance, dose
parse fixes; Investigations result-binding fixes. Recognise precision
is explicitly allowed to fall at this stop. Gate B: select stop still
mention-identical to comparator (all new direct classes carry paired
Select drops until Phase C), except where a Phase C rule has already
been accepted.

### Phase C — Select precision recovery

New or relaxed Select rules read the widened direct ledger: keep
supported SF states instead of dropping them, R1 local named-type
alignment, R3 multi-clause association, R2 SF typo lexicon at encode
(per the [gated SF rewrite protocol](exect_rules_only_sf_gated_rewrite_protocol_2026-08-27.md)),
Diagnosis keeps/drops for the generic-vs-specific confusion.

Gate C (candidate acceptance, per rule): isolated-positive and
leave-one-out-negative on `dev140`; candidate stack overall micro F1
>= **0.9167**; zero comparator-exact regressions; Phase B recall
targets maintained at the recognise stop.

### Phase D — freeze and one holdout replay

Freeze the accepted configuration as a new named config. Write a
separate predeclared aggregate-only `test60` protocol with family P/R
expectation bands informed only by dev evidence, then run one replay
(stage rungs included). Promotion of any cited number is recorded as
its own step. Roll the rules-base fingerprint fixture with evidence.

## Stop rules

- A relocation or recall lever that cannot meet its gate is recorded
  as a negative result and switched off; it does not block other
  levers.
- If Phase C cannot hold F1 >= 0.9167 with the recall targets met, the
  recall targets lose: report the best gated stack and the tension
  explicitly rather than shipping a recall-first stack that scores
  worse end-to-end.
- No `test60` loading, inspection, or tuning before Phase D.

## Artifacts

- `experiments/exect_rules_only_recall_first_20260827/` — per-phase
  machine-readable summaries (dev140).
- Dated reports in `docs/research/exectv2/` per phase completion.
- Final holdout artifact under its own Phase D protocol.

## Claim boundary

Development mechanism evidence until Phase D. The cited rows
(0.9167 / 0.8018) do not move before the Phase D replay completes and
an owner promotes the result.
