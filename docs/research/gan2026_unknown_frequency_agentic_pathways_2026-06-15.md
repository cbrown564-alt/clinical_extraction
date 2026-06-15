# Gan 2026 Unknown-Frequency and Agentic Selector Pathways

Date: 2026-06-15

Status: research handoff after validation-only iteration, including the
completed decisive live component-generation experiment and the rejected v0.7
live re-run (see results sections below). All model calls made so far were on
the validation split; no row-level holdout failures were inspected and scoring
policy is unchanged.

**Authorized next action (2026-06-15) — COMPLETED.** The user-authorized frozen
aggregate-only `test450` holdout of `fresh_evidence_reasoner` v0.6 + safety-v0.9
was run on 2026-06-15. Preflight passed `ok=true` after the two drifted hashes
(`fresh_evidence_reasoner.py`, its test) were recomputed to match the working
tree; the pinned command ran `450/450` rows with `0` call failures and `0`
parse/schema/label failures. **Final Purist `351/450` (`0.7800`)** — below the
`383/450` target and below the V0 baseline `364/450` (net Purist vs V0 `-14`),
final Pragmatic `362/450`, exact evidence substrings `423/450`,
`target_reached=false`. Per the stop rule this is final-evaluation evidence; no
row-level holdout content was inspected and any follow-up must restart as a
validation-only candidate. v0.4 (`379/450`) remains the best comparator;
v0.6/safety-v0.9 is now a measured-and-rejected holdout config. Artifacts:
`experiments/gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_6_safety_v0_9_2026-06-15.{jsonl,md}`.
This closes the v0.6 holdout question and is fresh evidence for the val→test gap
analysis (Insight 6): v0.6 trailed v0.4 on validation and trailed it harder on
test, with the fresh-evidence replacements going net-negative on the holdout.

## Objective

The immediate objective was to continue the agentic Gan 2026 seizure-frequency
line after the authorized V12 frozen aggregate-only `test450` audit missed the
target. The user stretch target is `>=0.900` Purist on `test450`
(`>=405/450`). The best completed frozen aggregate-only result remains V12
`fresh_evidence_reasoner` v0.4 at `379/450` Purist (`0.8422`), with no
row-level holdout tuning performed.

The newer work focused on a recurring weak spot: unknown-frequency cases where
the note contains seizure evidence but either the event count or the relevant
time window is unclear.

## Constraints

- Validation rows and synthetic/component-stress panels are valid development
  surfaces.
- Locked `test450` row-level failures, rationales, evidence, transitions, and
  selected events are not development surfaces.
- Any future holdout-facing run needs a new freeze packet and explicit user
  authorization.
- `unknown`, `no seizure frequency reference`, and `multiple per ...` may share
  Purist bucket behavior in some cases, but they are not clinically identical
  semantic decisions.
- Deterministic repairs must not be presented as LLM-owned clinical reasoning.

## Pathway 1: V12 Fresh-Evidence Reasoner

Rationale: V12 was designed to reduce deterministic overfit by letting a single
model own the final label from exact raw-note evidence, while saved GPT/Qwen/
DeepSeek structured-event traces serve only as scaffolding. Deterministic code
handles prompt assembly, schema/format repair, exact-substring evidence checks,
safety gates, rendering, and scoring.

Key findings:

- Validation750 v0.4 reached `682/750` Purist versus V0 `661/750`.
- The authorized aggregate-only `test450` audit reached `379/450`, below the
  original `383/450` threshold and below the stretch target.
- V12 had a smaller validation-to-test gap than deterministic and exact
  consensus paths, which supports the thesis that model-owned final reasoning
  generalizes better than validation-tuned deterministic switching.
- It still underperformed on unknown-frequency semantics, especially
  last-event-only and open-ended "since starting/beginning treatment" evidence.

Decision: keep V12 v0.4 as the best completed frozen holdout result and a
research comparator, but do not run another holdout without materially stronger
validation evidence.

## Pathway 2: Unknown-Frequency Policy Hardening

Rationale: Yujian clarified that when either seizure count or relevant period is
unclear, `unknown` is usually safer than inferring a frequency. The six
supervisor-discussed validation examples made the policy concrete:

- Last seizure date alone does not define one seizure in a period.
- "No seizures since the last event" does not by itself create a seizure-free
  duration label.
- Open-ended "since beginning medication/diet" is not a denominator unless the
  period is explicit.
- Explicit count plus a usable follow-up period can support a frequency label.

What was tried:

- Prompt v0.6 added explicit unknown-frequency policy.
- Safety gates through v0.9 blocked several known overreach patterns:
  nonselective unknown replacements, bare seizure-free outputs,
  open-ended treatment-start denominators, historical-frequency-to-seizure-free
  replacement, vague multiple exactification, and same-day cluster downgrades.
- A scorer-neutral semantic repair converts `no seizure frequency reference` to
  `unknown` when the model's own evidence shows seizure activity with unclear
  count/window.

Key findings:

- Supervisor6 improved from V0 `4/6` to `5/6`.
- Trigger25 improved from V0 `21/25` to `22/25`.
- Full unknown-boundary trigger panel improved from V0 `105/123` to `109/123`,
  with `0` final correct-to-wrong regressions.
- Validation250 improved from `238/250` under an earlier safety gate to
  `240/250`, but still trailed the v0.4 validation250 comparator at `242/250`.

Decision: the policy is clinically right and useful, but the v0.6/safety-v0.9
line is diagnostic, not holdout-facing.

## Pathway 3: Consensus plus Fresh Agreement Selector

Rationale: Exact structured-event consensus had validation signal but poor
changed-label precision. The selector hypothesis was to keep the deterministic
floor unless exact structured-event consensus and V12 fresh-evidence
independently agreed on the same replacement.

Progression:

- v0.1 reached `712/750`, but changed-label precision was too weak.
- v0.2/v0.3 added conservative boundary filters.
- v0.4 preserved cluster cadence and improved precision.
- v0.5 added a fresh-evidence boundary rescue for deterministic seizure-free/
  no-reference overreach, reaching `728/750`.
- v0.6 added fresh-boundary-profile guards after a synthetic panel exposed
  label-only rescue regressions.
- v0.7 added explicit count-window support for deterministic unknown origins.
- v0.8 accepted a narrow parseable denominator/window refinement.
- v0.9 added normalized-equivalent disagreement and specific-rate-to-unknown
  uncertainty handling.

Key findings:

- v0.9 is the selector-family validation front-runner: `733/750` Purist,
  `36` wrong-to-correct, `0` correct-to-wrong, changed-label precision `0.7347`.
- Synthetic stress checks passed for the targeted v0.9 mechanics.
- The selector-only oracle ceiling with current deterministic/consensus/fresh
  components is only `739/750`, because `11/750` selected validation errors
  have no correct available component.

Decision: stop adding selector micro-gates for now. The selector improved
validation substantially, but the remaining headroom is component generation,
not selection.

## Pathway 4: Residual Component-Generation Audit

Rationale: Before inventing another selector gate, quantify whether remaining
errors are selection failures or missing-correct-component failures.

Key findings:

- v0.9 selected wrong on `17/750`.
- `6` of those had a correct unselected component.
- `11` had no correct deterministic, consensus, or fresh-evidence component.
- The no-correct residual was dominated by unknown-boundary over-inference from
  last-event/seizure-free/recent-rate evidence, plus cluster-burden failures.
- Current components cap the selector at `739/750`, far below a validation
  signal strong enough to justify a `>=0.900` holdout target.

Decision: component generation must improve before another credible
holdout-facing design exists.

## Pathway 5: Deterministic Last-Event-to-Unknown Repair Probe

Rationale: The residual audit made an apparently simple repair tempting: rewrite
fresh-evidence last-event/seizure-free over-inferences to `unknown`, then let
the existing selector use the repaired component.

Key findings:

| Repair | Selected Purist | Delta vs v0.9 | Selected C->W | Decision |
| --- | ---: | ---: | ---: | --- |
| Seizure-free last-event to unknown | `725/750` | `-8` | `11` | reject |
| Last-event plus unclear-count markers to unknown | `733/750` | `0` | `0` | no gain |
| Any last-event seizure-free/frequency to unknown | `723/750` | `-10` | `14` | reject |

Decision: reject broad deterministic profile-string repair. It recovers some
unknown-boundary cases but damages true seizure-free rows. This confirmed that
the ambiguity decision needs to be made before final-label rendering, not
patched afterward.

## Pathway 6: Model-Owned Ambiguity Classification

Rationale: The supervisor guidance is not a pure string rule. The model needs to
explicitly decide whether count and window are usable before rendering the final
label.

Implemented contract:

- `fresh_evidence_reasoner` now accepts optional
  `ambiguity_classification`.
- Prompt/schema support asks for the ambiguity class before `final_label`.
- Safety gate can permit selective `unknown` replacements for:
  `unknown_count_or_window`, `last_event_only_unknown`, and
  `cluster_axis_incomplete`.
- The old last-event-only heuristic remains as a fallback, but the intended
  path is model-owned classification.

Supervisor-seeded panel:

| Row | Supervisor label | Expected component | Ambiguity class |
| ---: | --- | --- | --- |
| 11272 | `unknown` | `unknown` | `last_event_only_unknown` |
| 14454 | `2 per 2 month` | `2 per 2 month` | `explicit_count_window` |
| 14029 | `unknown` | `unknown` | `unknown_count_or_window` |
| 13267 | `2 per 5 month` | `2 per 5 month` | `explicit_count_window` |
| 14137 | `unknown` | `unknown` | `unknown_count_or_window` |
| 11337 | `unknown` | `unknown` | `unknown_count_or_window` |

Result: parser/safety-gate contract passes `6/6`.

Important caveat: because the reasoner and tests changed, the historical
v0.6/safety-v0.9 frozen preflight now correctly fails on hash drift. This is
expected and protective. There is no current holdout launch packet.

## Distilled Insights

These are the load-bearing conclusions from the six pathways above, stated as
causes rather than events. Each is what should actually change the next cycle.

### 1. Selection is saturated; the binding constraint is now the component pool

The selector ladder `v0.1 -> v0.10` moved validation750 from `712` to `733`, but
the selector-only oracle over the current deterministic/consensus/fresh
components is only `739/750`. Any perfect selector — one that always picks the
correct available component — beats the current front-runner by at most `+6`
rows, and each new gate now buys fractions of a row while trading churn. The
question "which component do we pick?" is effectively answered. The unanswered
question is "why is no component correct?" Continuing to engineer selection is
optimizing against a ceiling we have already nearly reached.

### 2. The components fail in *correlated*, not independent, ways on the residual

This is the deepest finding and it explains the low ceiling. Selection and
consensus only help when the sources disagree and at least one is right. On the
`11/750` no-correct rows, the deterministic rules path, exact three-agent
consensus, and V12 fresh evidence make the **same** over-inference: they read a
last-event date, a "no seizures since" clause, or a historical rate as a current
frequency or seizure-free duration. Three nominally independent sources share one
over-reading prior, so their independence collapses precisely on the rows that
matter. No amount of selecting among identically-wrong components recovers them —
which is why the oracle ceiling sits only `6` rows above the front-runner.

### 3. The residual is small, clinical, and concentrated — not diffuse noise

The remaining gap is not formatting and not spread thinly across the label space.
The no-correct residual is dominated by a single clinical phenomenon — unknown-
boundary over-inference (last-event / seizure-free and quantified-rate
over-reading) — with a small cluster-burden tail. The target is therefore narrow
enough to attack directly: make the components stop over-reading ambiguous
boundary evidence, and represent the cluster axis. These are two component-
generation problems, not twenty selector problems, and they should not be
conflated.

### 4. The ambiguity decision must precede label rendering — it cannot be repaired after

The v0.10 probe settled this quantitatively: deterministic last-event-to-unknown
rewrites net `-8` to `-10` because "last-event-only ambiguity" and "true
seizure-free duration" are indistinguishable at the rendered-label / profile-
string layer yet clinically opposite. The only discriminating signal — whether
the count and window are actually defined — lives in the raw note and is lost
once a label is chosen. The `ambiguity_classification` contract is therefore not
a refinement; it is the **only** layer at which the decision is recoverable. Any
future component-generation work that defers the ambiguity call past rendering
will reproduce the v0.10 loss.

### 5. Purist scoring is partially blind on exactly the axis we are now targeting

`multiple per month` and `unknown` share the Purist unknown bucket
(`1000.0`/month), so row `14029`'s clinically over-specific output scored
*correct*. Purist both understates the unknown-boundary problem and can
over-credit a "fix" that merely re-buckets an over-specific label. Optimizing
validation Purist on the ambiguity slice is optimizing a metric that is silent on
the failure mode. The next cycle needs a semantic / over-specificity view
alongside Purist or it will mistake re-bucketing for reasoning.

### 6. The val->test gap is still binding, and oracle-validation does not imply the target

V12 has the smallest gap (`-6.7pp`) *because* the model owns the final call, but
the gap comes from distribution shift in which component is right — and the
residual rows are exactly where that shift bites. So `0.985` validation oracle is
not `0.900` test: a perfect selector at the `739/750` ceiling is still a
validation number, and selection cannot move a test row whose only correct answer
was never generated. The lever that moves test is component generation on the
shift-fragile clinical families, not selection.

### 7. The gating infrastructure works; the line has converged on an honest null

The held-out-family CV gate refused the `708` consensus winner; the precision-
gated selector reverted `+11 -> +6`. Overfit is now caught by construction. That
is why ten selector versions all ended "revise, not freeze" with zero promotions
— not for lack of mechanism but because the component pool has no answer on the
hard rows. This is a genuine negative result, not an incomplete one: the selector
line is done. The next bet must be a *different* bet (live generation), and it
should be allowed to fail the same gates rather than be tuned around them.

## Decisive Experiment Result (2026-06-15, completed)

The single decisive experiment has been run. Live `v0.6` + safety-`v0.9`
ambiguity-aware fresh-evidence generation (`openai/gpt-4.1`, the intended frozen
config) was executed over the predeclared 22-row validation hard slice: the
`11` no-correct residual rows, the `6` recoverable rows, and the supervisor
panel. This is the first time the ambiguity contract was run live rather than
checked as a static parser/safety-gate contract. The fresh output was scored
against gold for component availability only; no locked test rows were read.

Artifacts:

- `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.{jsonl,md}`
- `experiments/gan2026_ambiguity_live_component_generation_audit_2026-06-15.{json,md}`
- `experiments/gan2026_residual_ambiguity_slice_indices_2026-06-15.txt` (frozen slice)
- `experiments/build_gan2026_ambiguity_live_component_generation_audit.py`

Headline:

| Metric | Result |
| --- | ---: |
| No-correct rows newly correct (live fresh) | `3/11` |
| Selector oracle ceiling | `739/750 -> 741/750` (`+2` net) |
| Recoverable fresh component preserved | `5/6` (regressed `14821`) |
| Supervisor panel, **live** | `5/6` (static contract was `6/6`) |

What the result actually shows:

1. **The ceiling moved for the first time.** Deterministic post-hoc repair
   netted `-8` to `-10` (Pathway 5); model-owned ambiguity generation netted a
   positive ceiling lift. The `3` fixes (`5534`, `6571`, `11272`) are exactly
   the last-event-only over-inferences the contract targets — all three
   collapsed correctly to `unknown` with `last_event_only_unknown`. This
   validates the model-owned direction over the deterministic one (Insight 4)
   and is the first evidence that the *component pool*, not just the selector,
   can improve (Insight 1).

2. **The lift is small and not free.** Net `+2`, not `+3`, because regeneration
   broke `14821` — a correct `1 per month` collapsed to `unknown`. The same
   contract that fixes last-event rows also over-applies `unknown`.

3. **Live generation fails the precision case that the static contract passed.**
   The supervisor panel was `6/6` as a parser/safety-gate contract but `5/6`
   live: row `13267` (`2 per 5 month`, an explicit count-window frequency)
   collapsed to `unknown`. This is the critical finding — the weak point is the
   model's *ambiguity-class decision at generation time*, not the gate that acts
   on it. The static panel masked this because it fed the class in; live, the
   model picks `unknown_count_or_window` for a row that has a usable window.

4. **The class field is internally incoherent with the rendered label.** On
   `14454`, `14137`, and `11337` the emitted `ambiguity_classification` does not
   match the (correct) final label. The contract is being satisfied by the gate
   and the label logic, not by a reliable class signal — so the class cannot yet
   be trusted as a feature.

5. **Cluster burden is untouched.** Both cluster rows (`9937`, `9943`)
   collapsed to `unknown` instead of producing a cluster-burden label. As
   predicted (Insight 3), this is a separate generation problem the
   unknown-frequency contract does nothing for.

Decision: **revise, not freeze.** The path is real — model-owned ambiguity
generation is the first lever to move the ceiling — but a `+2` validation-slice
lift with a new over-application regression and a live precision failure on
`13267` is nowhere near a holdout candidate. The bottleneck has moved one step:
from "no correct component exists" to "the ambiguity-class decision is not
precise enough to fix the hard rows without eroding legitimate frequencies."

## v0.7 Live Re-Run Result (2026-06-15, completed — revise)

The v0.7 demotion-precision prompt revision was run live (`openai/gpt-4.1`,
safety-`v0.9`, max_tokens `2800`) over the same predeclared 22-row validation
hard slice, with explicit user authorization. It **failed every success
condition** and was reverted.

| Metric | v0.6 (decisive) | v0.7 (this run) |
| --- | ---: | ---: |
| No-correct rows newly correct | `3/11` | `1/11` |
| Selector oracle ceiling | `741/750` | `739/750` |
| Supervisor panel (live), label correct | `5/6` | `2/6` |
| Recoverable fresh preserved | `5/6` | `5/6` |
| Target `13267` (`2 per 5 month`) | wrong | still wrong |
| Target `14821` (`1 per month`) | wrong | still wrong |

What the result shows:

1. **The tightening over-corrected in the opposite direction.** v0.7 pushed
   three gold-`unknown` rows (`6571`, `11272`, `11337`) *out* of `unknown` into
   over-specific seizure-free / frequency labels — the exact over-inference the
   unknown policy exists to suppress — and collapsed a correct `2 per 2 month`
   (`14454`) to `unknown`. "Treat unknown as the exception" traded the
   over-application problem for an over-specification problem.

2. **It did not fix the two target rows.** `13267` and `14821` — the explicit
   count-window and recurring-rate rows the revision was written for — stayed
   wrong. The instruction the model needed was not the binding constraint at
   generation time.

3. **The net effect is a regression, not a wash.** The oracle ceiling fell from
   v0.6's `741` back to the prior `739`, erasing the only ceiling gain the line
   had produced, and the live supervisor panel dropped from `5/6` to `2/6`.

Decision: **revise, do not freeze.** No freeze packet was created. v0.6 remains
the best completed configuration. The lesson reinforces Insight 4: the
ambiguity-class decision is made at generation time from the raw note, and a
prompt instruction that *names* the rule does not reliably move that decision —
it can swing the model from one boundary error to its mirror image. A future
v0.8 must change the *evidence the model conditions on* (e.g. a structured
count/window extraction step the class decision reads from) rather than adding
more boundary prose, and must be evaluated against the live supervisor panel and
the semantic scorer, not the static contract.

## Instrumentation Built (2026-06-15, completed)

The three supporting-instrumentation items below were built as deterministic,
validation-only audits. None makes a model call, reads a locked test row, or
changes the scorer. They are the prerequisites the live run is gated behind.

### 1. Component diversity audit (Insight 2, quantified)

`experiments/build_gan2026_residual_component_diversity_audit.py` normalizes the
deterministic, consensus, and fresh-v0.4 labels on each v0.9 selected-wrong row
to their Purist buckets and measures how many distinct buckets the three
produce.

Result: of the `11` no-correct residual rows, `7` (`0.636`) have all three
components collapsed into a *single* Purist bucket — they are not just wrong but
*identically* wrong. `4` are split across buckets. This confirms Insight 2
quantitatively: the dominant residual mode is correlated, single-bucket
over-reading, so a second generation pass that shares the over-reading prior
buys nothing on the correlated majority. The `4` split rows are the more
tractable target for a second pass; the `7` correlated rows need *different
evidence*, not another vote.

### 2. Semantic / over-specificity scorer (Insight 5, instrumented)

`experiments/build_gan2026_ambiguity_slice_semantic_scorer.py` scores the 22-row
live slice on the clinical decision kind (taken from the Purist bucket, not the
surface form) and flags two things Purist is blind to: over-specific
re-bucketing (a concrete frequency that lands in the unknown bucket for a gold
`unknown`) and class/label incoherence.

Result on this slice: Purist `12/22` equals semantic `12/22` — no re-bucketing
illusion fires, because the model collapsed to genuine `unknown` rather than to
over-specific phrases like `multiple per month`. The scorer is now in place for
the live run, where regeneration is far more likely to trip it. It does confirm
the Insight-4 finding directly: class/label incoherence fires on `14454` and
`14137`, so `ambiguity_classification` cannot yet be trusted as a selector
feature. (Note: the scorer treats `1 per multiple month` as an unknown-bucket
call, so demoting it to plain `unknown` on `5534` is correctly scored as the
safe call, not a miss.)

### 3. Source-near contrast panel (step 3.3, built)

`experiments/build_gan2026_source_near_contrast_panel.py` encodes the supervisor
distinctions as three paired hard negatives sharing surface cues but requiring
opposite calls: last-event-only vs last-event-plus-duration; open-ended
since-treatment count vs explicit count-plus-window; cluster cadence with vs
without events-per-cluster.

Result: the gate preserves both directions of all three pairs (`6/6`). This is a
clean predeclared hard-negative set for the next live run, but — per the `13267`
lesson — passing it *statically* is necessary, not sufficient: the live run must
reproduce these distinctions from raw evidence without the class fed in.

## Recommended Next Steps

The decisive experiment and the three supporting instrumentation pieces are
done. The remaining steps require live model calls (spend) and explicit user
authorization; they are gated, not yet run.

### v0.6 + safety-v0.9 test450 frozen holdout — COMPLETED 2026-06-15

**Done.** Result recorded above ("Authorized next action … COMPLETED"): final
Purist `351/450`, below target and below V0 baseline; rejected. The runbook that
was executed is retained below for provenance. The user authorized
(2026-06-15) a new frozen aggregate-only `test450` holdout of
`fresh_evidence_reasoner` v0.6 + safety-v0.9 in its current reverted form. v0.6
has only ever been evaluated on validation; the only measured holdout is v0.4 at
`379/450`. Run it in this order:

1. **Restore/refresh the freeze packet.** The preflight already pins the target
   config (`EXPECTED_PROMPT_VERSION = v0_6`, `EXPECTED_SAFETY_GATE_VERSION =
   v0_9`, `EXPECTED_MODEL = openai/gpt-4.1`, `EXPECTED_MAX_TOKENS = 2800`,
   `EXPECTED_TARGET_PURIST = 383/450`, manifest `gan2026_split_v1`, 450 rows).
   The protocol doc
   `docs/research/gan2026_fresh_evidence_reasoner_frozen_test450_protocol_2026-06-13.md`
   holds predeclared SHA-256 hashes. Because `fresh_evidence_reasoner.py` and its
   test were edited and then reverted this session, **recompute and update the
   predeclared hashes** for the frozen file set so they match the current v0.6
   working tree, and set the dated output artifact paths
   (`..._test450_live_gpt41_v0_6_safety_v0_9_<run-date>.{jsonl,md}`) to the
   actual run date (the preflight's `DEFAULT_TEST_*` paths currently read
   `2026-06-15`).
2. **Run the preflight and require `ok=True`.**
   `uv run python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight --json`
   It must pass with no hash drift, no pre-existing test outputs, and all
   version/model/max-tokens/manifest/row-count/target checks matched. Do not
   proceed on any failure.
3. **Run the locked aggregate-only holdout** — full 450 rows, no `--limit`, no
   `--source-row-indices` (test runs must cover the whole split):
   `uv run gan2026-llm-experiment --pipeline fresh_evidence_reasoner --split test --model openai/gpt-4.1 --max-tokens 2800 --temperature 0.0 --mode live --confirm-test-audit --resume-existing --jsonl <dated v0_6 test450 jsonl> --markdown <dated md>`.
   This is 450 live `gpt-4.1` calls; resumable per the resumability requirement.
4. **Aggregate-only readout.** Report Purist/Pragmatic rates only and register
   the run (`split=test`). **Do not inspect row-level holdout failures,
   rationales, evidence, transitions, or selected events** (Constraints). Compare
   the aggregate to v0.4's `379/450`.

Honest expectation: v0.6 trails v0.4 on validation (`240/250` vs `242/250` on
val250), so it is *unlikely* to beat `379` on test. The run is authorized to
obtain the measurement and close the v0.6 holdout question, not because
validation predicts a win. Whatever the result, keep v0.4 as the comparator and
record v0.6's test number as a fixed fact for the val→test gap analysis
(Insight 6).

### Sharpen the ambiguity-class decision (the new bottleneck)

The live run proved the ceiling can move but exposed where it stalls: the
model's generation-time choice between `explicit_count_window` and the
`unknown_*` classes is not precise enough. It correctly demotes last-event-only
rows but also collapses a legitimate `2 per 5 month` (`13267`) and a correct
`1 per month` (`14821`) to `unknown`. The next prompt revision must tighten that
boundary — require a positively identified count **and** window before any
`unknown` demotion of a frequency original — and be re-tested *live* on the
supervisor panel, because the static `6/6` contract did not catch the live
`13267` failure. Until the class field agrees with the rendered label on the
panel, do not treat `ambiguity_classification` as a selector feature.

**Prompt revision v0.7 drafted, live-tested, and rejected.** The v0.7 attempt
added three demotion-precision instructions (treat `unknown` as the exception,
classify `explicit_count_window` when a count and window are both present
including a remission interval, and reserve `last_event_only_unknown` for genuine
single-event evidence) plus an inline requirement to name the count and period.
It passed the static panels `6/6`, but the authorized live re-run (below) shows
it **over-corrected and regressed**. The code was reverted to v0.6, which remains
the best completed configuration; the v0.7 attempt is preserved only in
artifacts. See "v0.7 Live Re-Run Result" below.

### Attack cluster-burden generation separately

The unknown-frequency contract does nothing for the cluster rows (`9937`,
`9943`), which collapsed to `unknown` instead of a cluster-burden label. This is
a distinct component-generation problem (Insight 3) and needs its own prompt
path and hard-negative contrasts, not a fold into the unknown-boundary work.

### Supporting instrumentation (DONE — see "Instrumentation Built" above)

All three instrumentation items are now built, run, and registered. They are
deterministic and validation-only, and they are prerequisites the live run is
gated behind.

1. **Report component diversity, not just availability.** *Built.* `7/11`
   no-correct rows are correlated single-bucket failures; `4/11` are split. A
   same-prior second pass buys nothing on the correlated majority.

2. **Add a semantic / over-specificity scorer to the ambiguity slice.** *Built.*
   On this slice Purist `12` equals semantic `12` (no re-bucketing illusion);
   the scorer is in place to keep the live run honest, and it confirms Insight-4
   class/label incoherence on `14454`/`14137`.

3. **Build the paired source-near contrast panel.** *Built.* The gate preserves
   both directions of all three pairs (`6/6`); static passing is necessary, not
   sufficient, for the live run.

### Freeze what is finished

4. **Freeze the selector at v0.9 (and V12 v0.4) as fixed comparators.** Do not
   add selector gates. Per Insights 1 and 7 the line has converged; new gates
   trade churn for fractions of a row against a ceiling we have reached.

5. **Re-freeze for holdout only when the oracle ceiling itself moves.** A future
   holdout request requires, in order: the component oracle ceiling lifts above
   `739/750` on a held-out-family CV (not just aggregate validation); supervisor
   ambiguity panel and source-near hard-negative pass; semantic-scorer
   confirmation that the gain is clinical, not re-bucketing; panel/source
   symmetry across splits; updated frozen protocol hashes and aggregate-only
   readout; explicit user authorization.

## Durable Artifacts

- `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_7_safety_v0_9_2026-06-15.{jsonl,md}` (v0.7 live re-run — rejected)
- `experiments/build_gan2026_ambiguity_live_component_generation_audit_v0_7.py` and `experiments/gan2026_ambiguity_live_component_generation_audit_v0_7_2026-06-15.{json,md}` (v0.7 ceiling/supervisor audit)
- `experiments/build_gan2026_ambiguity_slice_semantic_scorer_v0_7.py` and `experiments/gan2026_ambiguity_slice_semantic_scorer_v0_7_2026-06-15.{json,md}`
- `experiments/build_gan2026_residual_component_diversity_audit.py` and `experiments/gan2026_residual_component_diversity_audit_2026-06-15.{json,md}` (Insight 2 quantified)
- `experiments/build_gan2026_ambiguity_slice_semantic_scorer.py` and `experiments/gan2026_ambiguity_slice_semantic_scorer_2026-06-15.{json,md}` (Insight 5 / over-specificity overlay)
- `experiments/build_gan2026_source_near_contrast_panel.py` and `experiments/gan2026_source_near_contrast_panel_2026-06-15.{json,md}` (paired hard negatives)
- `experiments/gan2026_ambiguity_live_component_generation_audit_2026-06-15.{json,md}` (decisive result)
- `experiments/gan2026_fresh_evidence_reasoner_residual_slice_live_gpt41_v0_6_safety_v0_9_2026-06-15.{jsonl,md}`
- `experiments/gan2026_residual_ambiguity_slice_indices_2026-06-15.txt`
- `experiments/build_gan2026_ambiguity_live_component_generation_audit.py`
- `docs/research/gan2026_unknown_frequency_policy_audit_2026-06-15.md`
- `docs/research/gan2026_agentic_next_phase_brief_2026-06-14.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.md`
- `experiments/gan2026_unknown_frequency_ambiguity_panel_2026-06-15.md`
- `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py`
- `tests/test_gan2026_fresh_evidence_reasoner.py`
