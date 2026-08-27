# Qwen rescue overfiring and generalization audit

Date: 2026-08-15
Status: complete; first remasure used July 18 v0.7 by source-selection
error. Audit code now requires matched v0.5 (Decision 0043). The
inexact-span family-rewrite split landed the same day.
Protocol: recovered from git history; this report is the answer.
Landing: [inexact-span family-rewrite](inexact_span_family_rewrite_2026-08-15.md)
Artifact: [`experiments/gan2026_qwen_rescue_overfiring_20260815.json`](../../experiments/gan2026_qwen_rescue_overfiring_20260815.json)
Rebuild: removed in the 2026-08-16 scripts prune; recover from git history (`scripts/audit_gan2026_qwen_rescue_overfiring.py`)

## Plain answer

Qwen 3.6:35B does **not** overfire the named repair stages relative to its
v0.7 peers. Evidence reconcile fires on 516 of 747 replayable Qwen cells
(0.69), below Sol (592/750) and only 1.09× the v0.7 peer median. Breakthrough
repair fires less on Qwen (2) than on Sol (9).

The distinctive Qwen crutch is **inexact selected evidence**, not stage
overfire. 165 of 747 Qwen cells (0.221) quote a span that is not an exact
source substring. Sol and Gemini are at 0. Requiring exact spans as a
study-local gate costs Qwen **−48 Purist** and mini −17; Sol and Gemini
move 0. Those 48 points are mostly paraphrase-to-same-family renders, not
clinical reselection.

A second, smaller Qwen signature is **family rewrite through evidence
reconcile**: 31 first-changers versus Sol 2 and Gemini 4. That is the
selection-masking path. A post-hoc, gold-free gate that blocks only
inexact-span family rewrites costs Qwen −7 on `dev750` and 0 on Sol and
Gemini.

The printed 675 → 364 (−0.091) comparison used July 18 **v0.7** `dev750`
raws against matched **v0.5** `test450`. That was a source-selection
error in the audit script, not a property of the selected comparison.
Decision 0043 requires v0.5 on both splits. The same-prompt historical
v0.5 panel is 660/750 → 364/450 (−0.071), matching Gemini's same-prompt
v0.5 drop (−0.070). Sol remains more resilient (−0.028 on that
reconstruction). After the family-rewrite landing, HEAD Qwen `test450`
is **361/450**. The six-model v0.5 `dev750` tree is not on this
checkout, so this report's stage tables stay the v0.7 diagnostic they
were measured on and must not be used as a v0.5 ranking.

Production rules are unchanged. The design below splits format render from
family rewrite. Landing it needs its own protocol and an aggregate-only
`test450` confirmation.

## What was replayed

Ordered no-call replay of saved `model_prediction.record` through HEAD
normalize / resolve / ten repair families. Zero model calls. Locked
`test450` rows were not opened.

| Model | Prompt | Replayable | Source |
| --- | --- | ---: | --- |
| Qwen 3.6:35B | v0.7 | 747/750 | July 18 hybrid jsonl |
| GPT-5.6 Sol | v0.7 | 750/750 | July 18 hybrid jsonl |
| GPT-5.6 Luna | v0.7 | 745/750 | July 18 hybrid jsonl |
| GPT-4.1-mini | v0.7 | 749/750 | July 18 hybrid jsonl |
| DeepSeek V4 Flash | v0.7 | 749/750 | July 18 hybrid jsonl |
| Gemma 4 26B | v0.7 | 742/750 | July 18 hybrid jsonl |
| Gemini 3.7 Flash | v0.5 | 750/750 | live current-stack cell |

This study's Qwen final is **673/747**. The published current-stack fill is
**675/750**. The three unreplayable rows are the fidelity gap; they are not
used in per-stage counts.

## Competence versus crutch

Purist at each band, replayable denominator.

| Model | Model final | After resolve | After evidence | Final | Dependence (final-correct, resolve-wrong) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.6:35B | 331 (0.443) | 355 (0.475) | 611 (0.818) | 673 (0.901) | 321/673 (0.477) |
| GPT-5.6 Sol | 268 (0.357) | 268 (0.357) | 606 (0.808) | 672 (0.896) | 405/672 (0.603) |
| Gemini 3.7 Flash | 449 (0.599) | 449 (0.599) | 617 (0.823) | 676 (0.901) | 235/676 (0.348) |
| GPT-4.1-mini | 333 (0.445) | 359 (0.479) | 607 (0.810) | 663 (0.885) | 305/663 (0.460) |

Sol still receives the largest same-output stack lift. That matches the
2026-07-27 Qwen–Sol architecture interaction (pruned; recover from Git history):
the rules are not Qwen-tuned. Qwen's model-boundary score (0.443) is close
to mini and far below Gemini (0.599). The hybrid finals then converge.

Of Qwen's 321 representation rescues, only 39 are notes where Sol was
already correct at resolve. Most Qwen rescues are notes Sol also needed.

## Overfiring

No repair stage meets the predeclared flag (Qwen fire rate ≥ 1.5× v0.7
peer median and ≥ 10 Qwen fires).

| Stage | Qwen fires | Qwen rate | Peer median | Ratio | Flag |
| --- | ---: | ---: | ---: | ---: | --- |
| `repair.selected_evidence` | 516 | 0.691 | 0.636 | 1.09 | no |
| `repair.monthly_diary` | 45 | 0.060 | 0.068 | 0.89 | no |
| `repair.dated_sequence` | 14 | 0.019 | 0.013 | 1.41 | no |
| `repair.post_change_burst` | 8 | 0.011 | 0.003 | 4.01 | no (n<10) |
| `repair.breakthrough` | 2 | 0.003 | 0.007 | 0.40 | no |

`post_change_burst` is the same small compensation candidate already
flagged on 2026-08-11 (r=−0.739, n=21 pooled). It is not new and is below
the fire-count bar.

## Rescue class (first Purist-changing hop)

Unparsed `≤ N per T` and other source-near labels that evidence reconcile
canonicalizes are `render_unparsed`, not family rewrite.

| Model | render_unparsed | render_same_family | family_rewrite | clinical_reselect | elapsed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Qwen 3.6:35B | 277 | 208 | **31** | 20 | 4 |
| GPT-5.6 Sol | 454 | 136 | 2 | 5 | 0 |
| Gemini 3.7 Flash | 208 | 194 | 4 | 31 | 4 |
| GPT-4.1-mini | 270 | 212 | 36 | 25 | 1 |

The stage that fires is shared. The **use** of that stage to change
clinical family is Qwen/mini-heavy. Sol almost never needs it: Sol's mass
path is unparsed source-near labels rendered into the selected quote.

## Inexact evidence (the Qwen-specific crutch)

| Model | Inexact rows | Inexact and final-correct | Inexact and rescued from resolve |
| --- | ---: | ---: | ---: |
| Qwen 3.6:35B | **165 (0.221)** | 146 | 68 |
| GPT-4.1-mini | 56 (0.075) | 49 | 22 |
| Gemma 4 26B | 24 (0.032) | 24 | 1 |
| DeepSeek V4 Flash | 11 (0.015) | 8 | 2 |
| GPT-5.6 Luna | 6 (0.008) | 5 | 2 |
| GPT-5.6 Sol | 0 | 0 | 0 |
| Gemini 3.7 Flash | 0 | 0 | 0 |

Qwen paraphrases. Sol and Gemini copy. The quote-repair / span-reconstruction
stack then has something to do on Qwen that the stronger quoters never ask
for.

## Breakthrough / unknown

Breakthrough-marked notes (gold-free regex) are equally common across
models (~183). Qwen is not uniquely rescued there (158/183 final-correct
versus Sol 159 and Gemini 160).

On gold `unknown_sentinel` (100 notes, 99–100 replayable): Qwen 79 correct,
Sol 82, Gemini 83. Qwen false rate-or-free residuals: 21 versus Sol 18 and
Gemini 17. `repair.breakthrough` is not the Qwen problem; Qwen often
**selects the quiet-interval quote**, and later render or
`elapsed_anchor` locks it in.

Development examples (not holdout):

- Row `3534`: gold `unknown`. Qwen quotes seven months of better control
  with no rescue medication → `seizure free for 7 month`. Exact span.
  Selection failure, then same-family render.
- Row `6077`: gold `unknown`. Qwen quotes "no episodes in the preceding
  eight months" → `elapsed_anchor` emits `1 per 1 month`. Exact span.
  Quiet-interval compose, not quote-repair.

## Predeclared counterfactual arms

Gold-free predicates. Delta is Purist versus HEAD baseline.

| Arm | Qwen | Sol | Gemini | Mini |
| --- | ---: | ---: | ---: | ---: |
| `evidence_same_family_only` | −160 | −232 | −121 | −129 |
| `no_unknown_override` | −2 | −4 | −3 | −4 |
| `exact_span_only` | **−48** | 0 | 0 | −17 |

Blocking every family-changing evidence rewrite is not a landing
candidate: it is the architecture. Forbidding unknown-resolve overrides
is small and slightly harmful everywhere. Exact-span-only is the
Qwen-specific lever, and most of its −48 is useful paraphrase render.

## Post-hoc design probe (not predeclared)

Skip evidence reconcile only when the span is inexact **and** the derived
label would change an already-parsed kind.

| Model | Rescue | Harm | Net |
| --- | ---: | ---: | ---: |
| Qwen 3.6:35B | 1 | 8 | −7 |
| GPT-4.1-mini | 0 | 4 | −4 |
| GPT-5.6 Sol | 0 | 0 | 0 |
| Gemini 3.7 Flash | 0 | 0 | 0 |

This is the smallest model-agnostic gate that targets Qwen's family-rewrite
paraphrases without taking Sol's unparsed-render path. The eight Qwen
development harms are the suspected overfit set. Not landed.

## Generalization cliff (aggregate-only holdout)

Holdout numbers are copied from
[`experiments/current_stack/latest/fills.json`](../../experiments/current_stack/latest/fills.json)
and the living panel. No `test450` row was read.

| Comparison | Qwen | Gemini | Sol |
| --- | ---: | ---: | ---: |
| Printed hybrid (mixed prompt for Qwen/Sol) | 673–675/750 → 364/450 (**−0.091**) | 676/750 → 374/450 (−0.070) | 671–672/750 → 381/450 (−0.048) |
| Historical same-prompt v0.5 hybrid | 660/750 → 364/450 (**−0.071**) | 676/750 → 374/450 (−0.070) | 656/750 → 381/450 (−0.028) |
| LLM-only (panel aggregates) | 0.753 → 0.702 (−0.051) | 0.771 → 0.709 (−0.062) | 0.787 → 0.744 (−0.042) |

Gemini is the only current-stack pair that is v0.5 on both splits. Once
Qwen is reconstructed on v0.5, its drop matches Gemini's. Sol stays
flatter. GPT-4.1-mini is no longer in the selected hybrid holdout slot
(Decision 0052); this artifact therefore has no mini `test450` hybrid
fill.

The extra printed Qwen cliff is prompt-identity plus a real, smaller
same-prompt gap versus Sol. It is not evidence that Qwen uniquely
overfires `repair.selected_evidence`.

## Design: model-agnostic repair split

Keep the two jobs that the current `repair.selected_evidence` function
mixes:

1. **Format / quote render.** If the resolved label is unparsed, or the
   derived label has the same parsed `FrequencyLabelKind`, rewrite from
   the selected quote. Exact substring is preferred but not required.
   Encoding repair and paraphrase-to-same-family belong here.
2. **Family rewrite.** Changing unknown ↔ frequency ↔ seizure-free from
   the selected quote is a selection act. Require an exact source span
   and the existing license checks in
   `should_prefer_selected_evidence_label`. Inexact paraphrases must not
   change kind.

Later clinical families (`monthly_diary` … `elapsed_anchor`) stay as
selection arbitration over the event ledger. They should not be asked to
compensate for a missing exact quote.

Do **not** add a Qwen branch. Do **not** land `evidence_same_family_only`
or `exact_span_only`. The next implementable candidate is the post-hoc
inexact-family-rewrite block, as its own predeclared study, with
aggregate-only `test450` confirmation. Breakthrough blindness remains an
evidence-selection / prompt problem: the model quotes the quiet interval.

## Claim boundary

Development no-call mechanism audit on Gan `dev750`. Holdout figures are
published aggregates only. Not a paper performance claim. Not
authorization to change clinical meaning, prompts, deterministic rules,
or the scorer. Replayable Qwen 673/747 is not a replacement fill for
published 675/750.
