# ExECTv2 Prescription lens per-rule decomposition

Date: 2026-08-10
Status: development leave-one-out decomposition; **default changed** (v09 -> v10)

Supersedes the decision boundary of: [Prescription lens on/off counterfactual](prescription_lens_counterfactual_2026-08-06.md)
Companion: [ExECT hybrid stage ablation](hybrid_stage_ablation_2026-08-06.md)

> **Status update 2026-08-10 — holdout CONFIRMED, and this page understates the
> result.** The [test59 holdout confirmation](prescription_lens_v10_holdout_confirmation_2026-08-10.md)
> measures the same removal at **+0.0881 exactness and +0.0462 Prescription F1**,
> roughly five times the development effect recorded below, improving five of
> six models. The claim boundary at the foot of this page ("no worse, and
> materially simpler", not "better") was correct on `dev140` alone and is now
> superseded: v10 is simpler **and** better. The asymmetry is itself evidence
> for the dev-fitting this page flags — the removed rules were tuned against
> `dev140`, so `dev140` was their best case.

## Plain answer

The Prescription lens was never one rule. Decomposed, it is **four rules that
help and two that hurt**. Removing the two harmful rules is simultaneously a
**simplification** and an **improvement on both metrics** — which the earlier
all-or-nothing counterfactual could not see.

| Arm | Prescription micro F1 | Letter exactness |
| --- | ---: | ---: |
| lens fully off | 0.9152 | 0.8301 |
| v09 lens (previous default) | 0.9175 | 0.8108 |
| **v10 lens (new default)** | **0.9182** | **0.8337** |

v10 beats both the previous default and full removal on both measures. Mean
four-family clinical-headline F1 moves 0.8587 -> 0.8594.

## Why the 2026-08-06 counterfactual could not conclude

That study compared the whole lens against a thin identity lens and reported a
`mixed_metric_split`: exactness favoured off, F1 favoured on, so no default
rewrite. Two things were missing.

**The on/off contrast is inside noise.** Re-running the same ordered no-call
replay with per-cell output: micro-F1 delta on-minus-off `+0.0023`, letter-cluster
bootstrap 95% CI `[-0.022, +0.028]`, P(delta<=0) = 0.44. Exactness McNemar
b=44 / c=60, exact binomial p = 0.14. Neither metric separates the arms. The
lens changes only 119 of 830 cells.

**The split was an aggregation artifact.** Good and bad rules were being summed.

## Leave-one-out decomposition

Same replay, 830 letter x model cells, six models, one arm per sub-rule.

| Sub-rule | Cells changed | Delta F1 if removed | Verdict |
| --- | ---: | ---: | --- |
| `split_daily_dose_regimen` | 5 | **-0.0079** | Keep. 15 correct keys, **0 spurious** |
| `normalize_drug_name` | 9 | -0.0034 | Keep |
| `normalize_dose_unit` / `normalize_dose_value` | 1 | -0.0008 | Keep |
| `prescription_convention_attribute_repairs` | 14 | -0.0006 | Keep |
| `prescription_residual_additions` | 34 | **+0.0003** | **Remove** |
| `is_prescription_convention_noise` | 84 | **+0.0012** | **Remove** |

### Why the noise drop was removed

It is the most active rule in the lens and it trades recall for precision at a
loss: it deleted **46 gold-supported regimens** to remove **53 spurious** ones
(with it: P 0.9337 / R 0.9019; without: P 0.8977 / R 0.9392).

The failure is systematic, not marginal. `EA0008`:

> `Current anti-epileptic medication: lamotrigine 75mg bd (to reduce and stop as detailed below)`

`_PLANNED_OR_HISTORICAL_PRESCRIPTION_EVIDENCE` matches `to reduce and stop`, so
an **explicitly current** medication was deleted because a future taper appeared
in the same parenthesis. This is the letter the 08-06 report used as its
headline lens-off rescue example.

It is also **model-compensating rather than corrective** — it patches weaker
models emitting planned regimens, and over-fires on models that already suppress
them:

| Model | with noise drop | without |
| --- | ---: | ---: |
| GPT-5.6 Luna | 0.9250 | **0.9492** |
| DeepSeek V4 Flash | 0.9353 | **0.9538** |
| GPT-5.6 Sol | 0.9432 | **0.9540** |
| Qwen 3.6 35B | **0.9249** | 0.8934 |
| GPT-4.1-mini | **0.8672** | 0.8592 |
| Gemma 4 26B | **0.9086** | 0.9021 |

A rule whose sign depends on the model is not a convention translation. Its
value decays as models improve.

### Why the residual additions were removed

Net negative: **18 correct additions against 22 spurious**. It was also gated on
`_PRESCRIPTION_RESIDUAL_TARGET_KEYS`, a hard-coded frozenset of **15 exact
(drug, dose, unit, frequency) tuples harvested from dev140** — so dev140 is its
best case and it is still precision-negative there. It cannot be expected to
transfer.

**The rule still exists** in `deterministic/conventions/prescription.py` because
`llm/pipelines/key_entities_structured/prompt_content.py` uses it to build
candidate hints for the prompt. Only the assembly-side use was removed. Changing
the prompt-side use would invalidate every retained sidecar.

## What the alternative fix would have been

The lens shipped with an unused guard (`is_bounded_explicit_current_prescription`)
that fixes exactly the `EA0008` deletion, reachable only via
`prescription_policy_variant="combined"` — disabled by
[Decision 0045](../../decisions/0045-exect-default-policy-not-joint-combined.md) on
complexity grounds. Measured, Rx-only, Dx/SF/Inv fixed:

| Rx policy | P | R | F1 | Exactness | Four-family F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `default` (v09) | 0.9337 | 0.9019 | 0.9175 | 0.8108 | 0.8587 |
| `current_guard_only` | 0.9339 | 0.9392 | 0.9365 | 0.8590 | 0.8639 |
| `combined` | 0.9570 | 0.9376 | 0.9472 | 0.8855 | 0.8664 |

Guarding scores higher than deleting. **It was not chosen**: it re-adds the
complexity 0045 rejected, and both guard sets are dev140-derived, so the higher
number carries more overfitting risk than it does confidence. Deleting two rules
is the simpler system, and it improves both metrics. This table is recorded so
the trade is explicit rather than lost.

## Claim boundary

Development decomposition on ExECT `dev140`, six retained structured sidecars,
ordered no-call replay. **No holdout evidence.** The removal is a
simplification-motivated default change whose measured F1 gain (`+0.0008`) is
well inside the noise band established above; the exactness gain (`+0.0229`,
McNemar 54/35, p = 0.056) is the stronger signal. Selecting these two rules for
removal on dev140 carries the same in-sample risk this document criticises in
`_PRESCRIPTION_RESIDUAL_TARGET_KEYS`; the honest claim is **"no worse, and
materially simpler"**, not "better".

Confirming on test59 was the outstanding step and is now **done and CONFIRMED**:
[holdout confirmation](prescription_lens_v10_holdout_confirmation_2026-08-10.md).
On the holdout the removal is worth `+0.0881` exactness and `+0.0462`
Prescription F1, so the cautious wording above understates it.

## Reproduction

Leave-one-out arms are produced by patching the named `standard_dictionary`
functions around `replay_letter_arm` in
`removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/build_exectv2_prescription_lens_counterfactual.py`)`; policy arms by
substituting `prescription_policy_variant` in the `LensPolicy` it constructs.
No model calls.
