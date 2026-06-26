# Gan 2026 Section-Claim-Table V3 250-Row Failure Review

Date: 2026-06-01

Surface: first 250 rows of `gan2026_split_v1` validation.

Artifacts reviewed:

- `experiments/gan2026_section_claim_table_validation250_gpt41mini_v3_2026-06-01.md`
- `experiments/gan2026_section_claim_table_validation250_gpt41mini_v3_2026-06-01.jsonl`

This is validation development analysis only. It is not a holdout or benchmark
result.

## Decision

Revise section-claim-table rather than promote or reject it.

The 250-row diagnostic shows useful intermediate traces, 0 call failures, and
high exact-evidence rates, but clean Purist is only 218/250. The failure pattern
is concentrated enough to justify one narrow v4 attempt: keep the architecture,
but change the prompt/schema contract around cluster label preservation, additive
count arithmetic, unsupported enum values, and no-reference versus seizure-free
boundaries. Do not expand clean scorer-facing policy for these rows.

The next run should be a new v4 25/50-row validation ladder. Do not run another
250-row diagnostic or any holdout evaluation until v4 passes the small-surface
gate.

## Summary

- Clean Purist misses: 32 / 250.
- Clean Pragmatic misses: 26 / 250.
- Unscorable schema/format rows: 2 / 250.
- Evidence exactness remains mostly local: 760/771 claim evidence substrings and
  246/250 selected final evidence substrings were exact.
- Downstream repair changed 19 rows, but it did not resolve the core semantic
  miss families below.

## Failure Families

| Family | Rows | Count | Interpretation |
| --- | --- | ---: | --- |
| Cluster burden under-selection or flattening | 1317, 1706, 3224, 3242, 3261, 3262 | 6 | The claim table often detects cluster structure but the final label collapses it to ordinary frequency, per-day burden, or a vague multiple-per-month label. |
| Additive counted-window arithmetic | 1773, 1794, 1866, 1880, 1922, 1980 | 6 | The selected evidence contains multiple counted seizure types in one window, but final labels omit one component, soften an exact total, or produce a broad range. |
| Unknown/no-reference/seizure-free boundary | 2166, 3137, 3371, 3532, 3534, 4771, 5092, 5110, 5406, 5476, 5491, 5507 | 12 | The model still confuses unquantified seizure evidence, negated current seizures, rescue-medication proxies, conditional events, and true no-reference notes. |
| Perimenstrual/window-only overconversion | 3468, 3469, 3482 | 3 | Window-limited seizure statements without event counts are converted into ordinary rates, but the gold surface treats them as unknown. |
| Upper-bound or compact notation mismatch | 3623, 3643, 4092, 5534 | 4 | The model fails to preserve exact benchmark label form for maximum weekly burden, compact `q...wk` notation, or isolated very-infrequent events. |
| Schema enum failure | 3468, 4480 | 2 | The model emitted `claim_type: historical`, which is outside the claim schema. Row 4480 appears label-correct but unscorable solely because an unselected historical claim broke validation. |

Rows can belong to more than one family; row 3468 is both a schema failure and a
perimenstrual/window-only overconversion. The family counts above are for review,
not mutually exclusive score accounting.

## Row Review

| Row | Gold | V3 clean label | Family | Notes |
| ---: | --- | --- | --- | --- |
| 1317 | `unknown, multiple per cluster` | `1 per day` | Cluster burden | Model recognizes a one-day cluster but turns an event-burden statement into ordinary daily frequency. |
| 1706 | `multiple cluster per month, multiple per cluster` | `multiple per month` | Cluster burden | Cluster cadence and per-cluster burden are flattened to ordinary frequency. |
| 1773 | `11 per 3 month` | `multiple per month` | Additive arithmetic | Evidence contains two drop attacks plus nine convulsions; final label softens the exact total. |
| 1794 | `8 per 2 month` | `6 per 2 month` | Additive arithmetic | Evidence contains six drop attacks plus two absence seizures; final label omits the absences. |
| 1866 | `8 per 2 month` | `1 to 4 per month` | Additive arithmetic | Evidence contains one drop attack plus seven absence seizures; final label converts poorly rather than preserving the two-month total. |
| 1880 | `8 per 2 month` | `7 per 2 month` | Additive arithmetic | Evidence contains one drop attack plus seven convulsions; final label omits one event. |
| 1922 | `7 per 3 month` | `2 to 3 per 3 month` | Additive arithmetic | Evidence contains two drop attacks plus five convulsions; final label drops the second component. |
| 1980 | `6 per 3 month` | `3 per 3 month` | Additive arithmetic | Evidence contains three focal onset seizures plus three spasms; final label omits the spasms. |
| 2166 | `unknown` | unscorable `frequent petit mal recently` | Boundary / format | The model preserves source-near vague frequency in the final label instead of emitting `unknown`. |
| 3137 | `seizure free for multiple month` | `no seizure frequency reference` | Boundary | Negated definite seizures are treated as no-reference rather than seizure-free. |
| 3224 | `1 cluster per month, 6 to 7 per cluster` | `6 to 7 per day` | Cluster burden | The model sees monthly clusters but normalizes per-cluster burden as a per-day ordinary rate. |
| 3242 | `2 cluster per month, 5 per cluster` | `multiple per month` | Cluster burden | Explicit cluster count and per-cluster burden are not preserved in final label. |
| 3261 | `2 cluster per month, 4 per cluster` | `multiple per month` | Cluster burden | Explicit cluster count and per-cluster burden are softened. |
| 3262 | `2 cluster per month, 5 per cluster` | `2 per month` | Cluster burden | Final label keeps cluster cadence but loses events per cluster. |
| 3371 | `unknown` | `seizure free for multiple year` | Boundary | Conditional seizure occurrence with an outside-window seizure-free statement is over-read as overall seizure freedom. |
| 3468 | `unknown` | unscorable | Schema / window-only | Unsupported `claim_type: historical`; the selected perimenstrual-only window is also overconverted to `1 per 1 week`. |
| 3469 | `unknown` | `1 per 6 day` | Window-only | Perimenstrual-only occurrence without count is converted into ordinary frequency. |
| 3482 | `unknown` | `1 per 6 day` | Window-only | Same perimenstrual/window-only overconversion pattern. |
| 3532 | `unknown` | `2 per 3 week` | Boundary | A recent isolated count and relative increase are converted to a rate despite no stable current frequency. |
| 3534 | `unknown` | `seizure free for 6 month` | Boundary | Rescue medication not used is treated as seizure freedom. |
| 3623 | `7 per week` | `multiple per week` | Upper-bound notation | The prompt needs to preserve explicit maximum burden when the benchmark gold uses the maximum. |
| 3643 | `7 per week` | `multiple per week` | Upper-bound notation | Same maximum weekly burden issue. |
| 4092 | `1 per 2 to 3 week` | `2 to 3 per week` | Compact notation | `qtwo - threewk` is interpreted as two to three per week rather than every two to three weeks. |
| 4480 | `3 to 5 per week` | unscorable | Schema enum | Label would likely be correct after non-semantic schema repair; an unselected historical claim broke validation. |
| 4771 | `unknown` | `2 per 6 week` | Boundary | The model chooses a specific secondary-generalization count despite broader unquantified cluster/run context. |
| 5092 | `seizure free for multiple month` | `no seizure frequency reference` | Boundary | No clinical seizures since referral is a seizure-free claim, not no-reference. |
| 5110 | `seizure free for multiple month` | `no seizure frequency reference` | Boundary | Negated witnessed or self-recognized seizures are converted to no-reference. |
| 5406 | `seizure free for multiple month` | `no seizure frequency reference` | Boundary | Non-epileptic-like episodes with no definite epileptic events should map to seizure-free in this surface. |
| 5476 | `unknown` | `1 per month` | Boundary | Rescue-medication use frequency is treated as seizure-frequency cadence. |
| 5491 | `unknown` | `2 per 6 week` | Boundary | A partial recent count is selected despite broader vague/uncertain current frequency evidence. |
| 5507 | `unknown` | `3 per 4 month` | Boundary | Collapse/fall counts without definite seizure-frequency framing are overcounted. |
| 5534 | `1 per multiple month` | `1 per 2 week` | Upper-bound notation | A single event a fortnight ago is selected as a two-week rate instead of very infrequent multi-month cadence. |

## V4 Scope

Recommended v4 changes:

- Add prompt language requiring cluster labels to preserve both cluster cadence
  and per-cluster burden when both are explicit.
- Add prompt language requiring additive arithmetic across seizure semiologies
  in the same selected current window, with the total preserved in final_label.
- Forbid `claim_type: historical` explicitly; historical is a temporality or
  assertion status, not a claim type. A no-call parser repair for unselected
  `claim_type: historical` can be tested separately, but it must be recorded as
  schema repair rather than semantic repair.
- Add boundary examples distinguishing no-reference, seizure-free, unknown, and
  rescue-medication proxy statements.
- Add a compact-notation instruction for `q2-3wk`-style labels and an
  upper-bound instruction for benchmark rows where the explicit maximum is the
  intended label.

Not recommended:

- Do not expand clean scorer-facing normalization for these families; that would
  hide semantic selection failures inside benchmark-facing policy.
- Do not run section-claim-table beyond 250 rows or evaluate holdout from v3.
- Do not turn the review rows into deterministic post-hoc semantic repair unless
  the repair is named, ablated, and claimed as a hybrid module.

## Gate

The next candidate should be named `gan2026_section_claim_table_v4` and restart
at 25 validation rows. Promotion to 50 rows requires no schema failures, no
cluster-label collapse on reviewed cluster examples, and no new clean-policy
expansion. Promotion back to 250 rows requires the 50-row review to show that the
change fixed a failure family rather than merely moving errors around.
