# Project Status

Last updated: 2026-06-15

## Active Objective

Surpass `0.85` Purist accuracy on locked Gan 2026 `test450` with a frozen,
LLM-owned, evidence-grounded structured-event reasoning pipeline. Success
requires at least `383/450` Purist on one explicitly authorized aggregate-only
audit, with no deterministic final-label fallback and no tuning from test
row-level failures.

User stretch target: reach at least `405/450` (`>=0.900`) Purist on locked
`test450`. No current candidate is close enough for another holdout-facing run.

Latest completed frozen audit result: V12 `fresh_evidence_reasoner` v0.6 +
safety-v0.9, `openai/gpt-4.1`, reached `351/450` Purist (`0.7800`) on the
authorized 2026-06-15 aggregate-only `test450` audit, below the `383/450`
target and below the V0 baseline `364/450` (net Purist vs V0 `-14`). The best
completed frozen holdout remains V12 v0.4 at `379/450` Purist (`0.8422`), which
stays the comparator. The goal is not achieved.

## Recent Context

- Follow-on plan:
  `docs/research/gan2026_llm_reasoning_agentic_test085_experiment_plan_2026-06-13.md`.
  It requires validation hard slices, validation250, full validation only for a
  freeze decision, then one frozen aggregate-only `test450` audit after explicit
  authorization.
- V12 `fresh_evidence_reasoner` is registered on the shared Gan CLI. It uses
  saved structured-event traces only as scaffolding; the model may keep the
  original GPT structured-event final or replace it with a raw-evidence-grounded
  final label. Deterministic code is limited to prompt assembly, schema/format
  repair, exact-substring evidence filtering, predeclared safety gates,
  rendering, and scoring.
- V12 v0.4 passed the ladder without test row inspection: validation25 `25/25`,
  fixed hard50 `42/50` versus V0 `39/50`, validation250 `242/250` versus V0
  `236/250`, and validation750 `682/750` versus V0 `661/750`. Validation750 had
  `0` call failures, `0` parse/schema/label failures, `42` wrong-to-correct,
  `22` correct-to-wrong, `703/750` exact evidence substrings, and final
  Pragmatic `698/750`.
- Frozen audit packet:
  `docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md`.
  It pins the exact command, hashes, source substrate, aggregate-only readout,
  technical recovery policy, and stop rule. It is not authorization by itself.
- On 2026-06-14, the user explicitly authorized the one frozen V12 aggregate-only
  `test450` audit. The exact pinned command ran to completion with `450/450`
  rows, `0` call failures, and `0` parse/schema/label failures. The pinned
  aggregate-only readout helper reports final Purist `379/450` (`0.8422`),
  raw model Purist `372/450`, format-only Purist `372/450`, V0 Purist
  `364/450`, final Pragmatic `394/450`, exact evidence substrings `423/450`,
  and `target_reached=false`. No row-level holdout failures were inspected.
- Post-audit synthesis:
  `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
  records the architecture rationale, pipeline diagrams, validation/test
  performance, and major explored journeys for hybrid structured events,
  agentic/consensus variants, and V12 `fresh_evidence_reasoner`.
- The missing DeepSeek structured-events `test450` source artifact has now been
  filled. On 2026-06-14, the user authorized a live DeepSeek SE v0.6 full
  `test450` source-coverage run, producing
  `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.jsonl`
  and `.md`. Aggregate health: `446/450` structured records, `0` call failures,
  `4` parse/schema/label issues, `440/450` exact evidence substrings, Purist
  `354/450`, Pragmatic `368/450`. This corrects the source-coverage gap for
  future frozen aggregate-only consensus/scaffolding audits; it is not a new
  promoted candidate and no row-level holdout failure analysis was performed.
- On 2026-06-15, the user authorized a fresh frozen aggregate-only `test450`
  holdout of V12 `fresh_evidence_reasoner` v0.6 + safety-v0.9 in its current
  (reverted) form — v0.6 had never been run on `test450`. The protocol hashes
  for `fresh_evidence_reasoner.py` and its test were recomputed/updated to match
  the current working tree (the ambiguity-classification additions), the
  preflight then reported `"ok": true`, and the exact pinned command ran to
  completion with `450/450` rows, `0` call failures, and `0` parse/schema/label
  failures. The pinned aggregate-only readout helper reports final Purist
  `351/450` (`0.7800`), raw model Purist `349/450`, format-only Purist
  `349/450`, V0 Purist `364/450`, final Pragmatic `362/450`, exact evidence
  substrings `423/450`, net Purist gain vs V0 `-14`, and `target_reached=false`.
  No row-level holdout failures were inspected. Per the stop rule this is final-
  evaluation evidence; any follow-up must start as a new validation-only
  candidate. v0.6/safety-v0.9 is now a measured-and-rejected holdout config; v0.4
  remains the best comparator.
- Yujian's unknown-frequency guidance is now captured in
  `docs/research/gan2026_unknown_frequency_policy_audit_2026-06-15.md`.
  The six discussed examples are all validation rows. V12 v0.4 scored `76/92`
  on gold-normalized validation unknown rows versus V0 `79/92`, and over-inferred
  rates/seizure-free labels from last-event-only or open-ended "since" evidence.
  Prompt v0.6 plus safety gate v0.9 now explicitly treats last-event-only and
  unclear-window "since" evidence as unknown while preserving explicit
  count-plus-window cases. Validation hard-slice signal is positive:
  supervisor6 `5/6` versus V0 `4/6`, trigger25 `22/25` versus V0 `21/25`, and
  the full unknown-boundary trigger panel `109/123` versus V0 `105/123`, with
  `0` final correct-to-wrong regressions on those slices. Safety v0.9 no-call
  replay removes the two v0.7 validation250 correct-to-wrong regressions,
  improving broad validation250 from `238/250` to `240/250` versus V0 `236/250`,
  and converts 5 no-reference fallbacks to semantically correct `unknown`
  without changing Purist counts. This still trails the earlier v0.4
  validation250 result of `242/250`. Therefore v0.6/safety-v0.9 is
  diagnostic/revise evidence, not a promoted holdout candidate.
- The next component-generation support for this issue is now in place:
  `fresh_evidence_reasoner` accepts an optional model-owned
  `ambiguity_classification` before final-label rendering. The safety gate can
  now allow selective `unknown` replacements when that field marks
  `unknown_count_or_window`, `last_event_only_unknown`, or
  `cluster_axis_incomplete`, instead of relying only on brittle profile-string
  heuristics. A supervisor-seeded ambiguity panel passes `6/6`, covering rows
  `11272`, `14454`, `14029`, `13267`, `14137`, and `11337`. This is
  validation infrastructure, not a holdout candidate.
- A materially different validation-only selector has been tested:
  `consensus_fresh_agreement_selector` keeps the deterministic baseline unless
  exact structured-event consensus proposes a different label and V12
  fresh-evidence independently emits that same label. The no-call validation750
  replay reaches `712/750` Purist versus deterministic `697/750`, consensus
  `708/750`, and V12 v0.4 `682/750`. This is the best validation aggregate seen
  in the current selector family, but it is still a revise signal rather than a
  freeze candidate: changed-label precision is only `0.2385`, and outside
  `band_daily` the band precision remains low (`0.125`-`0.3077`) despite
  non-negative net gains.
- Selector v0.2 tested a conservative non-boundary precision gate over the same
  saved validation artifacts: keep the v0.1 V12-agreed consensus switch only if
  the deterministic origin is not `no seizure frequency reference` and the
  agreed replacement is not `unknown` or `seizure_free`. It reaches `710/750`
  Purist with fewer changes (`58` vs `109`) and better changed-label precision
  (`0.3621` vs `0.2385`), with every 125-row validation block non-negative.
  This is useful movement but still revise-only: submonthly/monthly/weekly
  precision remains below the promotion bar.
- Selector v0.3 adds the unknown-frequency discipline directly to the selector:
  do not switch out of deterministic `unknown` or no-reference origins, and do
  not accept agreed replacements that are `unknown`, `seizure_free`, or
  parser-ambiguous `other` labels. On the same validation750 replay it restores
  the v0.1 aggregate (`712/750`) while cutting changed labels to `28` and
  raising changed-label precision to `0.6071` (`17` W->C / `2` C->W). It is
  still revise-only because `band_weekly` precision remains weak (`0.3333`).
- Selector v0.4 adds cluster-cadence preservation: if the deterministic label
  contains a cluster cadence, consensus/V12 agreement may refine the
  events-per-cluster burden but may not demote the answer to a plain rate or
  change the cluster cadence. On the same validation750 replay it reaches
  `714/750`, with only `26` changed labels, `17` W->C, `0` C->W, and
  changed-label precision `0.6538`. It is the selector-family front-runner, but
  still validation-only and not a holdout authorization.
- A validation-only v0.4 hard-slice audit supports the cluster-cadence gate:
  the two v0.3 switches suppressed by v0.4 were exactly the two v0.3
  correct-to-wrong regressions (`1` cluster demotion and `1` cluster-cadence
  change), while v0.4 keeps all `17` W->C changes. All six 125-row validation
  blocks have non-negative net changed-label impact. This is supportive but not
  sufficient for holdout; the next evidence should be a predeclared synthetic or
  adversarial robustness panel.
- A predeclared synthetic component-stress panel now covers v0.4's cluster
  cadence, denominator/window, unknown-boundary, seizure-free, multi-semiology,
  and agreement-control mechanics. v0.4 matches its expected action on `20/20`
  cases, improves synthetic Purist from deterministic `13/20` to selected
  `18/20`, blocks `9` unsafe agreed switches, and has `0` selected
  correct-to-wrong transitions. It also exposes two known conservative
  false-negatives: explicit count-plus-window cases that start from
  deterministic `unknown`.
- A follow-up validation-only unknown-origin relaxation probe rejects the
  tempting label-only v0.5 rule. On the saved v0.4 validation750 replay, only
  `4` switches were blocked by deterministic `unknown` origin; accepting them
  all would produce `0` W->C and `2` C->W regressions, net `-2`, both in
  `band_unknown`. Therefore keep v0.4 unless a future selector adds a narrow
  evidence feature for explicit count plus usable follow-up period.
- Selector v0.5 moved the validation front-runner forward. It keeps all v0.4
  consensus+fresh safeguards, then adds a narrow V12 fresh-evidence boundary
  rescue for deterministic seizure-free/no-reference overreach:
  deterministic `seizure_free` may switch only to fresh `unknown` or
  `no seizure frequency reference`, and deterministic
  `no seizure frequency reference` may switch only to fresh `seizure_free`. On
  saved validation750 it reaches `728/750` Purist, with `40` changed labels,
  `31` W->C, `0` C->W, and changed-label precision `0.775`. The `14` actions
  added over v0.4 are all W->C on validation (`11` in `band_unknown`, `3` in
  `band_zero`). This is strong validation-only evidence, not a holdout
  authorization.
- A predeclared synthetic/adversarial v0.5 boundary-rescue panel exposed the
  rule's main weakness: label-only fresh boundary rescue can erase valid
  seizure-free duration or turn true no-reference text into seizure-free. v0.5
  scored selected `8/12`, with `5` W->C and `3` C->W on the synthetic panel.
  Selector v0.6 adds a gold-free fresh-boundary-profile guard. It preserves the
  v0.5 validation750 replay exactly (`728/750`, `31` W->C, `0` C->W,
  changed-label precision `0.775`) and improves the synthetic panel to
  `11/12`, with `5` W->C, `0` C->W, and changed-label precision `1.0`. The
  remaining synthetic miss is the supervisor-approved explicit count plus
  usable follow-up period case that starts from deterministic `unknown`; it
  needs a separate evidence feature before any relaxation.
- Selector v0.7 adds that narrow evidence feature for deterministic `unknown`
  origins. It accepts only consensus+fresh-agreed specific labels when the fresh
  boundary profile explicitly contains both a seizure count and a usable
  follow-up/observation window, and blocks last-event-only, open-ended
  treatment-start, vague-count, unsupported replacement, and disagreement
  profiles. On saved validation750 it is unchanged from v0.6 (`728/750`,
  `31` W->C, `0` C->W, precision `0.775`) because no saved validation
  unknown-origin row qualifies. On a predeclared synthetic count-window stress
  panel it reaches selected `10/12`, with `5` W->C, `0` C->W, precision `1.0`,
  and desired actions `12/12`. This is useful mechanism coverage, but not a new
  holdout-facing promotion signal.
- Selector v0.8 adds a narrow parseable denominator/window refinement for
  consensus+fresh labels previously blocked as parser-ambiguous `other`. It
  accepts only profiles with denominator/window support or explicit current
  count/window support, while blocking boundary origins, last-event-only,
  seizure-free interval, highest-semiology, disagreement, and parser-incompatible
  replacements. On saved validation750 it reaches `731/750`, with `34` W->C,
  `0` C->W, and changed-label precision `0.7234`. The v0.8 synthetic
  parseable-refinement stress panel passes desired actions `11/11`, with `3`
  W->C and `0` C->W. It is the selector-family validation front-runner, but it
  is still revise-only: the gain is small, validation-mined, and far short of a
  holdout-facing `>=0.900` signal.
- Selector v0.9 adds two tiny residual gates on top of v0.8: normalized-equivalent
  consensus/fresh disagreement, and specific-rate-to-unknown uncertainty when
  both model sources agree on `unknown` and the fresh profile explicitly says
  the evidence is unquantified. On saved validation750 it reaches `733/750`,
  with `36` W->C, `0` C->W, and changed-label precision `0.7347`. The v0.9
  synthetic stress panel passes desired actions `7/7`, with `2` W->C and `0`
  C->W. This is useful residual cleanup, but still revise-only: the post-v0.9
  residual has `17` selected errors, `11` of which have no correct available
  deterministic/consensus/fresh component.
- Verification status before authorization: focused frozen-gate/registry tests pass
- Verification status: the current focused check passes `81/81`
  (`fresh_evidence_reasoner`, frozen preflight tests, run registry tests, and
  consensus+fresh selector tests); the run registry validates `147` entries;
  targeted Ruff is clean for the touched reasoner, tests, ambiguity-panel
  builder, and v0.9/v0.10 audit builders. The full pytest suite was not rerun
  after the ambiguity-classification patch; the last pre-patch full-suite signal
  was `1422/1422`. Full-repo Ruff still reports unrelated pre-existing lint debt
  in older scratch/ExECTv2 files, so targeted Ruff is the current clean signal
  for this work. The pinned V12 `test450` output/resume artifacts are still
  absent.
- Post-run first readout is also pinned:
  `python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_readout --json`
  reads only the pinned aggregate-only Markdown report, rejects alternate report
  paths, row-level sections, and unpinned JSONL-artifact markers, and reports
  whether final Purist reached `383/450`, with raw/format-only/final
  Purist/Pragmatic aggregate attribution counts, without opening the JSONL.
- The shared Gan LLM CLI requires `--confirm-test-audit` for `--split test`,
  requires live mode with temperature `0.0`, rejects partial test subsets,
  overwrites, source-artifact override flags (`--structured-event-jsonl`,
  `--candidate-set-jsonl`), prompt-only test mode, `--api-base`, and
  `--disable-dspy-cache`; for V12 it also rejects model/token drift from
  `openai/gpt-4.1` and `2800`, plus JSONL/Markdown output-path drift from the
  pinned frozen audit artifacts. It permits `--resume-existing` only for
  documented technical recovery with an existing JSONL.
- Source-symmetric exact three-agent consensus was checked aggregate-only after
  the DeepSeek source artifact became available: `366/450` Purist, only one row
  above the prior constrained two-agent `365/450`. No row-level holdout failures
  were inspected or tuned.
  Earlier V1, V3, V4, V7, V8, V9, V10, and V11 branches are rejected for
  escalation except as historical comparison artifacts.

## Guardrails

- Gan split `gan2026_split_v1` is locked: 300 train, 750 validation, 450 holdout.
- Validation is development evidence. Locked `test450` is aggregate-only; no
  row-level holdout tuning or error inspection is authorized.
- New holdout-facing Gan work requires explicit frozen-protocol authorization.
- Keep evidence metrics architecture-specific: `evidence_valid`,
  `evidence_text_contained`, exact raw-note substring checks, and CandidateSet
  source-id validity are different.
- Do not claim multi-agent value without matched-budget single-agent evidence.
  V12 is a single-model fresh-evidence candidate.

## Active Priorities

1. Treat V12 safety-gate v0.4 as a hardened comparator, not a threshold path:
   validation replay is only `683/750` and completed V12 holdout evidence is
   `379/450`.
2. Preserve the no-test-tuning boundary: do not inspect row-level holdout
   failures, rationales, evidence, selected events, or transitions.
3. Treat prompt v0.6/safety-v0.9 as a validation diagnostic. It captures useful
   unknown-frequency policy, but broad validation250 did not preserve the v0.4
   margin. Do not spend another frozen holdout without a much stronger
   validation signal.
4. Treat the consensus+fresh agreement selector as evidence that the candidate
   pool has headroom (`733/750` selected with v0.9, oracle still much higher).
   v0.9 is the selector-family development front-runner because it preserves the
   v0.8 validation-positive gates and adds two residual rescues with no
   saved-validation regressions. It is still not a holdout candidate because the
   gain is small, validation-mined, and far from the `405/450` stretch target.
   The v0.9 residual leaves `17/750` selected validation errors; only `6` have
   a correct unselected component, while `11` have no correct deterministic,
   consensus, or fresh-evidence output available. The next meaningful step
   should pivot from selector micro-gates toward better component generation.
   The registered v0.9 residual component-generation audit quantifies the
   selector-only oracle ceiling at `739/750` with current components, and shows
   the no-correct residual is dominated by unknown-boundary over-inference from
   last-event/seizure-free/recent-rate evidence plus cluster-burden misses.
   A follow-up v0.10 component-repair probe rejects broad deterministic
   last-event-to-unknown rewrites: the broad variants regress selected Purist to
   `725/750` or `723/750`, and the narrow unclear-count variant is neutral at
   `733/750` with no selected-label gain. The replacement direction is now a
   model-owned ambiguity-classification contract, with the supervisor panel
   passing `6/6`; the next evidence must be a validation-only live/prompt replay
   showing this field improves component generation without sacrificing valid
   seizure-free and explicit count-window cases.

## Work Board

### Now

- Move beyond v0.9 selector micro-gates. The remaining selector-only candidates
  are now mostly fresh-only overrides without consensus support; they should not
  be promoted without a new predeclared hard-negative panel and a stronger
  generalization story. Prefer component-generation work for the `11/750`
  residual rows where no available component is correct, starting with
  unknown-boundary generation that does not infer frequency or seizure-free
  duration from last-event-only evidence. Do not use broad deterministic
  profile-string repair for this; v0.10 shows it damages true seizure-free rows.
  Use the new `ambiguity_classification` contract and the `6/6` supervisor panel
  as the first hard-negative gate.

### Next

- Populate the Architecture Thesis Scorecard from existing Gan artifacts.
- If selector work continues, predeclare the next feature before implementation
  and test it against validation plus source-near synthetic hard negatives,
  especially denominator/window and current-frequency profiles.
- Run a validation-only ambiguity-classification component-generation attempt:
  prompt or replay must emit the explicit ambiguity class before rendering the
  final label, pass the supervisor ambiguity panel, and then demonstrate lift on
  predeclared validation hard slices before any broad validation replay.

### Blocked

- Any Gan holdout-facing rerun, row-level test analysis, or post-test tuning is
  blocked without explicit authorization and a frozen-protocol note.
- V1, V3, V4, V7, V8, V9, V10, V11, and historical E3/E4 live designs are
  blocked from escalation except as comparison artifacts.

### Backlog

- Optional: summarize V12 report profile dumps in future Markdown reports.
- Optional: add an Architecture Thesis Scorecard entry contrasting V12
  single-model fresh-evidence reasoning with saved-output consensus.

### Done Recently

- 2026-06-13: Added, tested, registered, and froze V12
  `fresh_evidence_reasoner`; completed validation25, hard50, family-slice,
  validation250, and validation750 gates without test row inspection.
- 2026-06-14: Ran the explicitly authorized V12 frozen aggregate-only `test450`
  audit and pinned readout. Result missed the goal: final Purist `379/450`
  (`target_reached=false`), final Pragmatic `394/450`, with `0` call failures
  and `0` parse/schema/label failures. No row-level holdout analysis was done.
- 2026-06-14: Added a detailed research synthesis covering hybrid structured
  events, early agentic/matched-budget variants, structured-event consensus,
  V1-V11 agentic variants, and V12 `fresh_evidence_reasoner`, with Mermaid
  pipeline diagrams and aggregate validation/test performance tables.
- 2026-06-14: Generated the missing DeepSeek SE v0.6 `test450` structured-event
  artifact as an aggregate-only source-coverage run: Purist `354/450`,
  Pragmatic `368/450`, `446/450` structured records, `0` call failures, and
  `440/450` exact evidence substrings.
- 2026-06-15: Completed the next-phase brief steps 3 and 4. V12 safety-gate
  v0.4 rejects validation-negative `unknown` replacements and replays to
  `683/750` Purist; preflight now hard-gates GPT/Qwen/DeepSeek test source
  symmetry and pins a fresh future audit output path. Source-symmetric
  three-agent consensus remains weak at `366/450` Purist.
- 2026-06-15: Added Yujian's unknown-frequency annotation guidance as V12
  prompt v0.6 plus safety gate v0.9 policy and a validation-only audit note.
  Supervisor6 improved from V0 `4/6` to `5/6`; trigger25 improved from V0
  `21/25` to `22/25`; the full trigger panel improved from V0 `105/123` to
  `109/123` with `0` final regressions. Safety v0.9 no-call replay improved
  validation250 to `240/250`, beating V0 `236/250`, and repaired 5
  no-reference fallbacks to `unknown`; it still trails the v0.4 comparator
  `242/250`, so this line is not promoted to holdout.
- 2026-06-15: Added and registered the validation-only
  `consensus_fresh_agreement_selector`. It reaches `712/750` Purist by accepting
  exact consensus switches only when V12 v0.4 agrees, but changed-label
  precision is too low (`0.2385`) for holdout-facing freeze.
- 2026-06-15: Added v0.2 of the consensus+fresh selector. It suppresses
  no-reference-origin switches and unknown/seizure-free replacements, reaching
  `710/750` with changed-label precision `0.3621`; still revise-only.
- 2026-06-15: Added v0.3 of the consensus+fresh selector. It suppresses
  deterministic `unknown` origins and ambiguous `other` replacements, restoring
  `712/750` with only `28` changed labels and `0.6071` changed-label precision;
  still revise-only due to weak weekly-band precision.
- 2026-06-15: Added v0.4 of the consensus+fresh selector. It preserves
  deterministic cluster cadence unless consensus/V12 only refine cluster
  burden, reaching `714/750` with `17` W->C, `0` C->W, and `0.6538`
  changed-label precision; still validation-only.
- 2026-06-15: Added a v0.4 hard-slice audit. It confirms the two v0.3 switches
  suppressed by v0.4 were both regressions and that v0.4 keeps all `17` fixes,
  but it remains saved-validation evidence rather than a holdout-facing freeze.
- 2026-06-15: Added and registered the v0.4 synthetic component-stress panel.
  v0.4 matches expected actions on `20/20` source-near synthetic cases, reaches
  selected `18/20` versus deterministic `13/20`, blocks `9` unsafe switches,
  and exposes `2` explicit count-window false-negatives from the conservative
  unknown-origin gate.
- 2026-06-15: Added and registered a validation-only unknown-origin relaxation
  probe. Accepting all v0.4 switches blocked solely by deterministic `unknown`
  origin would be net `-2` on validation (`0` W->C, `2` C->W), so a label-only
  v0.5 relaxation is rejected.
- 2026-06-15: Added selector v0.5. It preserves v0.4 and adds a fresh-evidence
  boundary rescue for deterministic seizure-free/no-reference overreach. Saved
  validation750 improves to `728/750` with `31` W->C, `0` C->W, and `0.775`
  changed-label precision.
- 2026-06-15: Added a v0.5 boundary-rescue audit. The `14` actions added over
  v0.4 are all W->C, with `0` C->W: `11` deterministic seizure-free to
  fresh uncertain-boundary rescues in `band_unknown`, and `3` deterministic
  no-reference to fresh seizure-free rescues in `band_zero`.
- 2026-06-15: Added and registered a v0.5 boundary-rescue synthetic stress
  panel and selector v0.6. The v0.5 panel exposed `3` synthetic C->W hard
  negatives from label-only boundary rescue. v0.6 adds a fresh-boundary-profile
  guard, preserves validation750 `728/750`, and improves the synthetic panel to
  `11/12` with `0` C->W. It remains revise-only.
- 2026-06-15: Added selector v0.7 and registered the unknown count-window
  synthetic stress panel. v0.7 preserves validation750 `728/750`, accepts no
  extra saved-validation unknown-origin actions, and passes the synthetic
  count-window mechanism panel with selected `10/12`, `5` W->C, `0` C->W,
  precision `1.0`, and desired actions `12/12`. It remains revise-only because
  the new feature is validation-neutral.
- 2026-06-15: Added and registered the v0.7 residual headroom audit. v0.7 leaves
  `22/750` selected validation errors; `11` have no correct deterministic,
  consensus, or fresh-evidence component available, while `11` have a correct
  unselected component (`6` consensus+fresh and `5` fresh-only). A broad
  parseable-`other` relaxation is rejected as validation-negative: `27`
  candidate actions, `4` W->C, `5` C->W, net `-1`.
- 2026-06-15: Added selector v0.8 and registered its validation replay plus
  parseable-refinement synthetic stress panel. v0.8 accepts a narrow subset of
  parseable `other` replacements with denominator/window or explicit current
  count/window profiles, reaching validation750 `731/750` with `34` W->C,
  `0` C->W, and changed-label precision `0.7234`. The synthetic stress panel
  matches desired actions `11/11`, with `3` W->C and `0` C->W. It remains
  revise-only and not holdout-facing.
- 2026-06-15: Added selector v0.9 and registered its validation replay plus
  semantic-equivalence/unknown-uncertainty synthetic stress panel. v0.9 reaches
  validation750 `733/750` with `36` W->C, `0` C->W, and changed-label precision
  `0.7347`. The synthetic stress panel matches desired actions `7/7`, with `2`
  W->C and `0` C->W. It remains revise-only; remaining headroom increasingly
  requires better component generation.
- 2026-06-15: Added and registered the v0.9 residual component-generation
  audit. The residual leaves `17` selected validation errors: `6` still have a
  correct unselected component, but `11` have no correct deterministic,
  consensus, or fresh-evidence output. The selector-only oracle ceiling with
  current components is therefore `739/750`, and the no-correct residual is
  concentrated in unknown-boundary over-inference and cluster-burden failures.
- 2026-06-15: Added and registered the v0.10 component-repair probe. Three
  deterministic last-event-to-unknown fresh-component rewrites were tested over
  saved v0.9 validation rows. Broad seizure-free and any-last-event rewrites
  are validation-negative (`725/750` and `723/750` selected Purist), while the
  narrower unclear-count rewrite is selected-neutral (`733/750`) and provides no
  usable component-generation gain. Reject this repair family.
- 2026-06-15: Added model-owned ambiguity classification to
  `fresh_evidence_reasoner` and registered the supervisor-seeded
  unknown-frequency ambiguity panel. The panel passes `6/6` across the six
  discussed validation rows and contrasts last-event-only ambiguity, open-ended
  medication/diet windows, single provoked breakthrough events, and explicit
  count-plus-window cases. It is validation infrastructure, not a holdout
  candidate.
- 2026-06-13: Built Stage 0 validation-only family hard-slice manifests and V0
  pure structured-event comparator report, then rejected prior agentic branches
  and the `365/450` structured-event consensus holdout result as insufficient.

## Core Artifacts

- `docs/research/gan2026_llm_reasoning_agentic_test085_experiment_plan_2026-06-13.md`
- `docs/research/gan2026_hybrid_structured_events_agentic_consensus_fresh_evidence_analysis_2026-06-14.md`
- `docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md`
- `docs/research/gan2026_unknown_frequency_policy_audit_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_live_gpt41_v0_6_safety_v0_7_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_live_gpt41_v0_6_safety_v0_7_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_unknown_policy_trigger_full_validation_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_validation250_nocall_replay_v0_6_safety_v0_9_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_2_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_3_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_hard_slice_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_synthetic_component_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_4_unknown_origin_relaxation_probe_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_5_boundary_rescue_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_6_boundary_rescue_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_unknown_count_window_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_7_residual_headroom_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_8_parseable_refinement_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.md`
- `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`
- `experiments/gan2026_fresh_evidence_reasoner_hard50_live_gpt41_v0_4_2026-06-13.md`
- `experiments/gan2026_v06_test450_hybrid_structured_events_deepseek_2026-06-14.md`
- `experiments/gan2026_llm_reasoning_stage0_v0_comparators_2026-06-13.md`
- `experiments/RUN_INDEX.md`
