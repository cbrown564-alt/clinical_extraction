# Audit — the `multiple` count sentinel across projects (item 6)

Date: 2026-07-06. Owner: ExECTv2 + Gan2026 workstreams.
Status: **Complete.** Zero LLM calls.
Provenance: item 6 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.
Driver: `scripts/run_gan_multiple_sentinel_audit.py`.

## TL;DR (the framing-changing finding)

The cross-project divergence on the word `multiple` is **not** the 2-vs-3
distinction the plan emphasized. It is the **unknown-vs-counted** distinction.
This repo resolves bare `multiple per <period>` to the **unknown** bin
(monthly 1000.0, `FrequencyLabelKind.UNRESOLVED_MULTIPLE`) and resolves
cluster-format `multiple cluster per <period>` with a **period-dependent**
cluster count {week→2, month→8, year→18, day→2} plus a fixed-2 per-cluster
size. **Both predecessors** (dissertation-recursive = 2.0, dissertation-
experiments/dspy = 3.0) instead assign a real count to every `multiple` label,
including bare `multiple per <period>`.

Measured sensitivity on Gan **validation750** (predictions held fixed; only the
gold resolution changes):

| Gold scheme | Purist acc | Pragmatic acc | Purist Δ vs ours | Pragmatic Δ vs ours | bin-crossers |
| --- | ---: | ---: | ---: | ---: | ---: |
| **Ours (dynamic, bare-multiple→unknown)** | **0.7600** | **0.8240** | — | — | 0 |
| Fixed-2 (dissertation-recursive) | 0.7080 | 0.7760 | −0.0520 | −0.0480 | 46 |
| Fixed-3 (dissertation-experiments / Gan §2.6.1) | 0.7053 | 0.7760 | −0.0547 | −0.0480 | 49 |

The **2-vs-3 distinction moves ~0.3pp Purist and 0pp Pragmatic.** The
**unknown-vs-counted distinction moves ~5pp Purist / ~4.8pp Pragmatic.** Of the
46 fixed-2 bin-crossers, **41 are bare `multiple per <period>` rows** (the
unknown-vs-counted axis); only **3 are cluster-format rows** (the period-
dependent axis); 2 are other cluster shapes. The cluster-count period-
dependence the plan flagged as "a third scheme" is real but is the **minor**
axis; the dominant effect is that we treat bare `multiple per <period>` as
unscoreable-unknown while both predecessors count it.

> The negative deltas do **not** mean our model is better. They mean our
> predictions were generated and scored under *our* convention (bare
> `multiple` → unknown), so model and gold agree on "unknown" for those rows.
> Under a predecessor convention the gold gains a real count while the (held-
> fixed) prediction stays unknown, turning previously-correct rows into errors.
> The number that matters is the **convention difference**, not who scores
> higher under it.

## The code path traced end-to-end

There is exactly **one** count-resolution path in this codebase:
`src/clinical_extraction/tasks/shared/epilepsy/normalization.py`.

- `label_to_frequency_record(label)` (`:38`) — the only entry point that
  resolves a raw Gan label into scored monthly frequency.
  - If the label contains `cluster`, dispatches to `_expand_cluster_label`
    (`:179`).
  - Otherwise, `parse_label_bounds` (`:70`) — and here bare `multiple per
    <period>` returns `FrequencyLabelKind.UNRESOLVED_MULTIPLE` (sentinel
    monthly 1000.0). Confirmed by the audit: dynamic resolution reproduces the
    stored gold monthly on **750/750** validation rows.
- `_expand_cluster_label(label)` (`:179-205`) — line 180 maps
  `multiple per cluster → 2 per cluster` (fixed-2 per-cluster size), then calls
  `_replace_multiple_cluster_count`, then multiplies cluster-count ×
  per-cluster-count.
- `_replace_multiple_cluster_count(label)` (`:208-217`) — the period-dependent
  cluster-count values are **inlined literals** (no constant):
  - `week` → `2 cluster per`
  - `month` → `8 cluster per`
  - `year` → `18 cluster per`
  - `day` → `2 cluster per`

**No second code path resolves `multiple` to a count for scoring.** Confirmed
by whole-`src/` grep. Other `multiple` mentions exist but do not affect Gan
scoring: the ExECTv2 extraction normalizer (`deterministic/normalizer.py:18`,
`"multiple": "2"`) is a separate task (word→digit for the epilepsy-letters
task, not the Gan scorer); agentic/structured-event code branches on the
literal `"multiple"` for label-shape logic, not count resolution.

## Cross-project divergence (confirmed against sibling repos)

| Project | Bare `multiple per <period>` | Cluster `multiple cluster per <period>` | Source |
| --- | --- | --- | --- |
| **This repo** | **unknown (1000.0)** | period-dependent {2,8,18,2} × fixed-2 per-cluster | `normalization.py:70,179-217` |
| dissertation-recursive | **2.0** (counted) | 2.0 (fixed) | `../dissertation-recursive/src/gan_frequency.py:66` — `"MULTIPLE_VALUE=2.0 kept for Gan comparability; minimal-repo parser uses 3.0"` |
| dissertation-experiments | **3.0** (counted) | 3.0 (fixed) | `../dissertation-experiments/src/clinical_extraction/normalizers/seizure_frequency.py:21,36` — `"The keyword 'multiple' maps to 3 seizures (Gan et al. Section 2.6.1)"; _MULTIPLE = 3.0` |
| dspy | 3.0 (per the §2.6.1 convention shared with dissertation-experiments) | 3.0 | follows dissertation-experiments; the plan's primary citation |

In-repo corroboration of the 2.0 guideline value:
`docs/research/exectv2_sf_guideline_alignment_2026-06-10.md:53` documents the
annotation guideline mapping `multiple=2, several=3` (List 11 L867–L885).

## The mover rows on validation750

- **135** rows mention `multiple`; **72** mention `cluster`; **28** mention
  both; **5** use `multiple cluster per <period>` (the period-dependent cluster-
  count axis).
- The **41 bare-`multiple per <period>` bin-crossers** dominate the sensitivity.
  Representative: `multiple per week` (gold unknown→8.69 monthly under fixed-2);
  `multiple per day` (unknown→60.83); `multiple per month` (unknown→2.03).
- The **3-4 cluster-format bin-crossers** are the period-dependent axis.
  Representative: `multiple cluster per month, multiple per cluster` — ours
  resolves to **16.22** monthly (8 clusters × 2 per-cluster); fixed-2 resolves
  to **4.06** (2 × 2); fixed-3 to **6.08** (2 clusters × 3). These cross the
  Purist `more1week_less1day` ↔ `1_per_week` boundary.

## Recommended disclosure language

Any cross-paper comparison of our Gan numbers to dspy's reported 90.3% monthly
(or to either predecessor's) must carry this disclosure:

> Our scorer resolves bare `multiple per <period>` labels to the **unknown**
> bin (unscoreable), following the `FrequencyLabelKind.UNRESOLVED_MULTIPLE`
> sentinel; both dissertation-recursive (MULTIPLE_VALUE=2.0) and
> dissertation-experiments (Gan §2.6.1, `_MULTIPLE=3.0`) instead resolve
> `multiple` to a real count. On validation750, holding predictions fixed, this
> convention difference moves Purist accuracy by ~5pp and Pragmatic accuracy by
> ~4.8pp; the 2.0-vs-3.0 distinction within the counted family moves <0.3pp
> Purist and 0pp Pragmatic. Our cluster-format resolution is additionally
> period-dependent ({2,8,18,2} by week/month/year/day), a third scheme neither
> predecessor uses, but it affects only 5 validation rows. Absolute Gan
> accuracy figures are **not directly comparable** across these conventions
> without stating the resolution rule; the 2-vs-3 axis is negligible next to
> the unknown-vs-counted axis.

## Implications for items 2 and 3 (the experiments this audit gates)

This audit's outcome bounds the item-2/item-3 framing in one specific way: the
"cross-family test" those experiments run is about **our own** measured SF-
direction capacity-vs-execution gap (B2 −0.0775 etc.), **not** about matching
dspy's absolute 90.3% monthly rate. The 90.3% number and our Gan numbers are
not on the same scoring convention; citing dspy's rate as a direct comparator
for our gap would inherit this confound. The item-2 predeclaration should state
the cross-family claim in terms of our own within-architecture deltas, and cite
dspy G32 only as the *architectural principle* (closed-option generation) being
transferred, not as a comparable accuracy target.

## Cost / split discipline

Zero LLM calls. Re-scoring of a frozen validation750 prediction artifact
(`experiments/gan2026_8c_canonical_pipeline_v03_validation750_gpt41mini_2026-06-09.jsonl`)
against three gold-resolution variants. **No test450 row inspection** —
test450 remains frozen; this audit uses validation750 only, which is the
development surface.
