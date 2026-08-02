# Luna prompt tuning under frozen LLM + rules

> **Follow-up (2026-07-31):** residual floors and narrow guards from this thread
> are absorbed into the **final Gan LLM-with-rules ruleset**. See
> [six-model comparison](six_model_comparison_report_2026-07-18.md) and
> [dated-count / guards](gan2026_luna_dated_count_competing_rate_report_2026-07-31.md).

Date: 2026-07-30  
Status: development and aggregate-only holdout panels complete

## Question

Can plain-language prompt changes still improve GPT-5.6 Luna on Gan 2026 when
the event schema, `hybrid_full_stack` repair, scorers, and splits stay frozen?

Most earlier prompt iteration used GPT-4.1-mini. This study compares Luna only
to itself.

## Design

Three prompt variants kept the same JSON schema and repair stack:

| ID | Prompt | Role |
| --- | --- | --- |
| A | `gan2026_hybrid_structured_events_v0.5` | Frozen control |
| B | `gan2026_hybrid_structured_events_v0.8_luna_rate` | Rate and aggregation guidance |
| C | `gan2026_hybrid_structured_events_v0.8_luna_current` | Current-state and boundary guidance |

Readouts were dual: **LLM-only** (model boundary) and **LLM with rules** (final
label after deterministic repair). Primary score: Gan Purist accuracy.

Splits:

- Development: `validation750` (`dev750`), row-level analysis permitted for
  drafting only.
- Holdout: `test450`, aggregate-only; no row inspection or tuning from test
  failures.

Owners:
[dev750 protocol](../experiments/gan2026/gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md),
[dev750 panel](../experiments/gan2026/gan2026_luna_prompt_variants_dev750_2026-07-30.md),
[test450 protocol](../experiments/gan2026/gan2026_luna_prompt_variants_test450_protocol_2026-07-30.md),
[test450 panel](../experiments/gan2026/gan2026_luna_prompt_variants_test450_2026-07-30.md).

## Results

### Development (`validation750`)

| Variant | LLM-only Purist | LLM+rules Purist | LLM+rules Pragmatic |
| --- | ---: | ---: | ---: |
| A | 411/750 | 646/750 | 671/750 |
| B | 422/750 (+11) | 656/750 (+10) | 675/750 |
| C | 414/750 (+3) | 666/750 (+20) | 680/750 |

On development, C leads the final score; B leads the raw model boundary.

### Holdout (`test450`, aggregate-only)

| Variant | LLM-only Purist | LLM+rules Purist | LLM+rules Pragmatic |
| --- | ---: | ---: | ---: |
| A | 222/450 | 363/450 | 376/450 |
| B | 235/450 (+13) | 374/450 (+11) | 386/450 |
| C | 224/450 (+2) | 373/450 (+10) | 384/450 |

On holdout, B leads both boundaries. C still beats A on final Purist, but by a
smaller margin than on development.

## Findings

1. **The frozen v0.5 prompt was not Luna’s ceiling.** Both instruction-only
   variants beat A on development and on sealed test450.
2. **Gains are not only rules absorbing model error.** LLM-only Purist rises
   for both variants, especially B (+11 development, +13 holdout).
3. **Development and holdout agree on direction, not rank.** C looked best on
   development final Purist; B looks best on holdout and on LLM-only in both
   splits.
4. **Effect size is modest but consistent:** about +10 to +20 Purist-correct
   rows under an unchanged repair stack. That supports a bounded claim that
   prompt tuning still matters inside LLM+rules, not that residual error is
   solved.

## Residual follow-up

A no-call row-level residual analysis on `validation750` found that only 48
rows remain Purist-wrong under all three prompts; 39 of those are already
rules-correct. The shared core is clinical selection, cluster/range label
projection, and seizure-free/unknown boundary conflict—not missing evidence.
Prompt variants rearrange the margins; they do not dissolve that core. The
later dated-count / competing-rate floors and final-ruleset replay absorb the
actionable stack fixes; see
[dated-count / guard report](gan2026_luna_dated_count_competing_rate_report_2026-07-31.md)
and
[six-model comparison](six_model_comparison_report_2026-07-18.md).

## Claim boundary

Luna-versus-Luna development and aggregate-only holdout evidence for the named
prompts, schema, and repair policy. This is not a six-model ranking, clinical
validation, published-benchmark claim, or authorization to replace the frozen
six-model v0.5 panel. Test450 rows remain sealed.
