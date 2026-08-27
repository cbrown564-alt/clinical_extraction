# Model-compensating rule audit (both tasks)

Date: 2026-08-11
Status: complete, no-call development audit; one flagged candidate's follow-on
removal study also complete (KILLED, rule kept, compensation holdout-confirmed)
Protocol: recovered from git history; this report is the answer.

## Plain answer

**Revised 2026-08-11 (same day, second pass).** The first pass of this audit
only checked for literal sign reversal (does the rule help one model and hurt
another) and found almost nothing beyond the already-known Prescription case.
That check was too narrow: a rule can be uniform-sign across every model —
never actually hurting a strong model — and still be doing most of its work
compensating for one weak model, which carries the same "value decays as
models improve" risk the Prescription finding raised. Re-run as a
**magnitude-correlation** check (does the size of the benefit correlate with
how weak the model already is, using each model's independent LLM-only
competence as the yardstick), calibrated against the known-confirmed
Prescription rule (r=-0.646) as a reference point:

**`Diagnosis:diagnosis_residual_additions` is a genuine compensating rule**
— r=-0.932 (micro-F1) on n=213 changed cells, a *stronger* compensation
signature than the confirmed Prescription case, on more than double the cell
count. Gemma 4 26B (the weakest model on this task) gains 0.1201 F1 from the
rule; GPT-5.6 Sol and DeepSeek V4 Flash (the two strongest) gain only 0.0504
and 0.0490 — roughly 2.4x less. This was invisible to the sign-only pass
because all 6 models are uniform-negative-sign (nobody is hurt), which the
first pass read as "convention, keep." **Unlike the Prescription case,
though, a follow-on removal study (below) found this compensation is real
and durable — it replicates on `test59` holdout, not dev-set memorization —
so, unlike Prescription, the rule stays.**

Two Gan repair stages show the same pattern at smaller scale:
`repair.post_change_burst` (r=-0.739, n=21) and `repair.dated_sequence`
(r=-0.625, n=60) — both comparable in correlation strength to the confirmed
case, but on far fewer cells, so lower priority and noisier.

The literal sign-reversal check from the first pass still stands as reported
below: only the already-known Prescription pair reverses sign outright, plus
one noise-scale Gan case (`repair.non_epileptic`).

A byproduct of this audit found and fixed a real internal contradiction in
the Gan 08-10 report (see below) — it had claimed the opposite sign for
`repair.breakthrough` from its own data table.

## Method

Two passes, both no-call, over the same three 2026-08-10 decompositions.

**Pass 1 (sign reversal, original protocol):** collate per-model deltas,
classify each rule's sign pattern, flag reversals, judge noise-scale vs.
genuine compensation by magnitude and firing count.

**Pass 2 (magnitude correlation, added after user review):** sign-only
checking misses a rule that helps every model (never reverses) but helps
weak models much more than strong ones — the same decaying-value risk in a
form that doesn't cross zero. For each rule with per-model data, computed
Pearson's r between each model's independent task-level LLM-only competence
(from `six_model_comparison_report_2026-07-18.md`'s matched LLM-only tables:
Gan `test450` — Sol/DeepSeek 0.74, mini 0.73, Luna 0.71, Qwen 0.70, Gemma
0.68; ExECT `test60` — DeepSeek/Sol 0.78, Luna 0.76, Qwen/mini 0.73, Gemma
0.69) and that rule's per-model benefit magnitude (accuracy/F1 cost if the
rule is removed). A negative r means weaker models get more benefit — the
compensation signature. Calibrated against the one rule already known and
holdout-confirmed to be compensating, `is_prescription_convention_noise`
(r=-0.646, n=84), as the reference threshold: candidates at or beyond that
strength, on comparable or larger n, are the ones worth escalating.

Caveat: r is computed over only 6 points (one per model) per rule, so it is
directional evidence, not a significance-tested result — it is a triage
signal for which rules deserve a predeclared removal study, not a
substitute for one.

## Results by source

### 1. Gan repair stages (`gan2026_rule_decomposition_and_mechanism_audit_20260810.json`, dev750, 6 models)

| Stage | Cells changed | Sign pattern | r(competence, help) | Verdict |
| --- | ---: | --- | ---: | --- |
| `repair.selected_evidence` | 2520 | uniform negative (all 6) | +0.273 | foundational, keep (see note) |
| `repair.monthly_diary` | 312 | uniform negative (all 6) | -0.066 | convention, keep |
| `repair.usual_interval` | 33 | uniform negative (all 6) | +0.197 | convention, keep |
| `repair.typical_over_ytd` | 2 | ≤0 on firing models | +0.107 | too small to classify |
| `repair.breakthrough` | 22 | uniform negative (all 6) | -0.603 | small-magnitude, noise (see below) |
| `repair.non_epileptic` | 11 | **reversed**: deepseek_v4_flash +0.0013, other 5 ≤0 | +0.183 | flagged as sign-reversal, closed as noise (see below) |
| `repair.residual_jerk` | 25 | uniform negative (all 6) | +0.212 | convention, keep |
| `repair.post_change_burst` | 21 | uniform negative/flat (all 6) | **-0.739** | **secondary compensation candidate, see below** |
| `repair.dated_sequence` | 60 | uniform negative (all 6) | **-0.625** | **secondary compensation candidate, see below** |
| `repair.elapsed_anchor` | 63 | uniform negative (all 6) | -0.067 | convention, keep |

`repair.selected_evidence`'s r=+0.273 is not a compensation signal in the
risky sense despite the huge 0.21 span in per-model help: it is the
foundational evidence-reconcile stage (removing it costs every model
0.21-0.42 Purist, by far the largest effect in the table) — every model
needs it, the variance looks like it tracks something else (evidence
availability per model's outputs), not competence, and the correlation sign
is positive (stronger models benefit slightly *more*, the opposite of
compensation). Flagged here only to show it was checked, not because it is a
candidate.

**`repair.post_change_burst` (n=21, r=-0.739) and `repair.dated_sequence`
(n=60, r=-0.625) are secondary candidates.** Both show a compensation
correlation stronger than the confirmed Prescription reference (-0.646), but
on much smaller cell counts (21 and 60 vs 84), so the correlation is noisier
and the absolute stakes (Purist points recoverable) are smaller — Qwen/Gemma
gain roughly 0.01 Purist from `post_change_burst`, Sol/mini/DeepSeek gain
near-zero to 0.001; a similar ~0.008-0.014 spread on `dated_sequence`. Not
escalated to a removal study in this pass (see Recommendations) but flagged
for the next Gan decomposition refresh to re-check with a larger dev
sample or the retained holdout ledger.

**`repair.non_epileptic` flagged, not actioned.** 11 changed cells out of
4,482 — the smallest non-trivial firing count in the table. The reversal is
one model (deepseek_v4_flash, +0.0013, i.e. 1 cell's worth of Purist points
on a ~450-note-equivalent denominator) against four negative and one flat.
This was already bundled into the
[minor rules pruning test450 holdout confirmation](../gan2026/minor_rules_pruning_test450_confirmation_2026-08-10.md)
(alongside `typical_over_ytd`, which does not reverse), which came back net
-0.0004, DeepSeek unchanged (0.0000 delta) — i.e. the one model whose
development sign favored removal showed **no effect** on holdout. That is
consistent with the reversal being noise (11 cells is too few to resolve a
1-cell-scale model effect), not a real compensation pattern. **No further
study recommended** — the effect size is below what any predeclared holdout
could resolve.

**Report bug found and fixed.** The 08-10 report's own "Audit Findings"
narrative (item 3) claimed removing `repair.breakthrough` "IMPROVES Purist
accuracy (+0.0022)... REMOVE" — the opposite of its own table two sections
above (`-0.0020`, uniform negative sign, "KEEP"). The narrative had conflated
this report's whole-`dev750` result with the *unknown-gold-only* subset
result from a same-day sibling study
([`unknown_sentinel_clinical_harm_2026-08-06.md`](../gan2026/unknown_sentinel_clinical_harm_2026-08-06.md),
10 harm cells there — a different, narrower population). The whole-ledger
question was already asked and answered directly by
[`unknown_breakthrough_loo_2026-08-06.md`](../gan2026/unknown_breakthrough_loo_2026-08-06.md):
removing it costs the full ledger 0.881→0.874, decision
`necessity_confirmed_with_global_cost`, not removed. The same narrative item
6 also claimed four rules had "0 cell changes" when the table two sections
above shows 2/11/25/21 changed cells respectively. Both are narrative-only
errors — the underlying JSON artifact and table were correct throughout, and
no landed decision was made on the wrong claim (the actual minor-rules
holdout confirmation correctly targeted `typical_over_ytd` +
`non_epileptic`, not `breakthrough`). Fixed in place in the source report
with an inline correction; `PROJECT_STATUS.md`'s propagated claim is
corrected in the same edit as this audit.

### 2. ExECT family-lens rules (`exectv2_family_lens_rule_decomposition_20260810.json`, dev140, 6 models)

13 rules audited (7 Diagnosis, 5 SeizureFrequency, 3 Investigations — note
SF lists 5 including the two `sf_unknown_suppression.*` sub-keys). Only 3
fire non-trivially on dev140: `diagnosis_alias_rewrites` (138 cells),
`diagnosis_noise_drop` (162 cells), `diagnosis_residual_additions` (213
cells) — all three **uniform negative sign across all 6 models**, no
literal reversal. The remaining 10 rules are zero-fire for every model
(`diagnosis_heading_recovery`, `diagnosis_residual_rewrites`,
`diagnosis_attribute_repairs`, `diagnosis_generic_epilepsy_companion`, all
SF rules, all Investigations rules) — already tracked as dead-code-removal
candidates in the source decomposition, pending prompt-consumer audit
per its own `selection_rule`, not a model-compensation question.

**Magnitude-correlation pass 2 changes the read on one of these three:**

| Rule | Cells | r(competence, help on F1) | Verdict |
| --- | ---: | ---: | --- |
| `diagnosis_alias_rewrites` | 138 | +0.488 | helps stronger models somewhat more — not compensating |
| `diagnosis_noise_drop` | 162 | +0.019 | flat, no competence relationship |
| `diagnosis_residual_additions` | 213 | **-0.932** | **strongest compensation signature found in this entire audit, escalate** |

**`Diagnosis:diagnosis_residual_additions` — headline finding, escalate to a
predeclared removal study.** Per-model micro-F1 benefit (help if the rule
stays): Gemma 4 26B **0.1201**, GPT-4.1-mini 0.0712, Qwen 3.6 35B 0.0661,
GPT-5.6 Luna 0.0570, GPT-5.6 Sol 0.0504, DeepSeek V4 Flash 0.0490. Gemma —
the weakest model on this task (0.69 LLM-only vs. 0.78 for Sol/DeepSeek) —
gets 2.4x the benefit of the two strongest models, and the gradient runs
cleanly down the competence ranking for every model except a Qwen/mini
crossover. r=-0.932 on 213 changed cells is both a stronger correlation and
a larger sample than the already-confirmed `is_prescription_convention_noise`
(r=-0.646, n=84) that motivated this whole audit. This rule was previously
reviewed only in aggregate by the family-lens decomposition (pruned; recover from Git history)
(net-helpful pooled, kept) and by the [Diagnosis canonical row-adjudication](project_predecessor_lessons_application.md)
(85.2% of *all* Diagnosis disagreements are gold-multiplicity artifacts, not
this rule specifically) — neither checked per-model skew. It has **not**
been through a leave-one-out holdout test in isolation.

**Mechanism check (2026-08-11):** reading the source
(`diagnosis.py:546-569`, `RESIDUAL_SOURCE_CONCEPT_PATTERNS`) before writing
the removal protocol found the rule is **53 hard-coded regex patterns
matching literal `dev140` note phrasing** (e.g.
`Diagnosis:\s*focal onset epilepsy \(occipital\)` -> `"occipital lobe
epilepsy"`) -- the same shape as the already-removed Prescription
`_PRESCRIPTION_RESIDUAL_TARGET_KEYS` frozenset, and dev-derived by its own
docstring. This reframes the removal study: the live question is not only
"does removal help" (dev140 already shows removal costs every model 0.05-0.12
F1, so blanket removal is very likely to fail the standing selection rule
in-sample) but whether the measured benefit, and its Gemma-heavy skew,
**transfers to held-out notes at all** -- if the patterns rarely fire outside
the dev140 letters they were written against, the "compensation" is
dev-memorization, not a durable weak-model correction, independent of
whatever the removal-arm accuracy delta says.

**Study run, result (2026-08-11):**
[result](../exectv2/diagnosis_residual_additions_compensation_removal_2026-08-11.md).
The memorization hypothesis was **refuted**: the pattern set fires on 67.8%
of `test59` letters vs. 70.7% on `dev140` (comparable rates, computed the
same way -- raw per-letter firing, not the post-dedup "changed cells"
figure). The compensation pattern itself **replicates on holdout**: removing
the rule costs Gemma 4 26B (weakest model) -0.0523 F1 and -0.0351 exactness
on `test59` -- far more than any other model, and the only model where
removal hurts exact-match too. **Verdict: KILLED (rule kept)** -- this is a
real, durable weak-model compensation effect, not dev140 overfitting. A
separate, narrower "remove 4 zero-help broadening patterns" candidate
(already identified by a pre-existing 2026-08-10 mechanism audit this study
found and reused) remains open and untested on holdout, but is orthogonal to
the compensation question -- it targets pure harm, not the skew.

### 3. Prescription sub-rules (`prescription_lens_rule_decomposition_2026-08-10.md`, dev140, 6 models)

Per-model tables exist only for the two flagged rules (the source report did
not produce per-model deltas for the other four). Confirmed sign-reversed:

| Rule | Cells | Sign pattern | Status |
| --- | ---: | --- | --- |
| `is_prescription_convention_noise` | 84 | **reversed**: helps Luna/DeepSeek/Sol (removing them costs 0.02-0.03), hurts Qwen/GPT-4.1-mini/Gemma (removing them gains 0.006-0.032) | **already removed** in v10, holdout-confirmed +0.0881 exactness / +0.0462 F1, 5/6 models improved |
| `prescription_residual_additions` | 34 | aggregate net-positive-if-removed (+0.0003); no per-model breakdown in source, removed alongside the above on the strength of its own precision-negative (18 help / 22 spurious) evidence, not a sign-reversal finding specifically | **already removed** in v10 |
| `split_daily_dose_regimen`, `normalize_drug_name`, `normalize_dose_unit`/`normalize_dose_value`, `prescription_convention_attribute_repairs` | 5/9/1/14 | aggregate-only, all uniform negative (delta-if-removed negative in every case) | no per-model data to test reversal; aggregate gives no reason to suspect one — **not flagged**, would need a fresh per-model rerun to fully clear |

The v10 holdout `by_model` artifact (combined effect of removing both
flagged rules together) confirms the development sign for 5/6 models and
shows GPT-4.1-mini essentially flat (0.8144→0.8114 Prescription F1, a small
residual cost) — consistent with GPT-4.1-mini being the one model the
removed rules were compensating for. This closes the loop on the rule that
originally motivated this audit.

## Synthesis

Literal sign reversal turns out to be too narrow a test: on that check alone,
model-compensation looked like a Prescription-specific mechanism, with
almost nothing else in the rule base implicated. The magnitude-correlation
pass overturns that reading. Compensation does not require a rule to ever
hurt a strong model — a rule that helps every model, but helps the weakest
one 2-2.5x more than the strongest, has the identical decaying-value profile,
and `Diagnosis:diagnosis_residual_additions` fits that profile more strongly
(r=-0.932, n=213) than the confirmed Prescription case did (r=-0.646, n=84).
Two Gan repair stages (`post_change_burst`, `dated_sequence`) show a weaker
version of the same pattern. So the honest synthesis is: model-compensation
is not confined to Prescription — it recurs wherever a rule's design lets one
weak model draw disproportionately on it — but only one instance in this
audit (`diagnosis_residual_additions`) clears the bar the Prescription case
set for "worth a dedicated removal study," and it has not yet been through
that study. The H-inflation gradient (Dx 93.5% > SF 61-83% > Rx 52.2% > Inv
26-30%, [[project_predecessor_lessons_application]]) is a different axis —
gold-multiplicity artifact share, not per-model skew — and does not settle
this question either way for `diagnosis_residual_additions` specifically.

**Not covered by this audit** (would need fresh per-model reruns to fully
clear): the four unflagged Prescription sub-rules only have aggregate deltas
in the source report; no per-model artifact was produced for them at
decomposition time.

## Recommendations

1. **`Diagnosis:diagnosis_residual_additions` — study complete, KILLED
   (rule kept).** [Result](../exectv2/diagnosis_residual_additions_compensation_removal_2026-08-11.md):
   the memorization hypothesis was refuted (firing rate transfers,
   67.8% vs 70.7%) and the compensation pattern replicates on `test59`
   holdout (Gemma loses -0.0523 F1 / -0.0351 exactness on removal, far more
   than any other model). No rule change; the compensation is real and
   durable, not dev140 overfitting.
2. `repair.post_change_burst` and `repair.dated_sequence` (Gan) are noted as
   secondary, smaller-n candidates for the next Gan decomposition refresh;
   not escalated now given the small absolute stakes (~0.01 Purist) and
   noisier n=21/60 samples.
3. `repair.non_epileptic`'s literal sign reversal is closed as noise-scale
   (already holdout-tested, no effect); no further study.
4. If a future decomposition pass touches Prescription again, produce a
   per-model artifact for the four currently aggregate-only sub-rules so this
   audit's coverage gap can close.
5. The `repair.breakthrough` narrative bug is fixed; no rule change follows
   from it (the underlying decision — keep `repair.breakthrough` — was
   already correct).

## Claim boundary

No-call development audit over retained artifacts, plus one completed
follow-on predeclared removal study
([`diagnosis_residual_additions`](../exectv2/diagnosis_residual_additions_compensation_removal_2026-08-11.md),
result: KILLED, rule kept — a genuine, holdout-confirmed weak-model
compensation effect, not dev-set memorization). Corrects a narrative-only
documentation bug in the Gan 08-10 report. No rule, prompt, or scored
production artifact changed as a result of this audit or its follow-on
study; the standing default is unchanged and reconfirmed.
