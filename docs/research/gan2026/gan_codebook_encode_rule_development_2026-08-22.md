# Gan codebook-extract encode-rule development

Date: 2026-08-22
Status: development candidate frozen
Owner: this file
Protocol:
[Gan codebook-extract encode-rule development protocol](gan_codebook_encode_rule_development_protocol_2026-08-22.md)

## Answer

The existing Gan rule encode is the wrong default after
`gan_llm_extract`. It treats selected evidence as a new extraction
surface and rewrites a model label that has already attempted the Gan codebook.
On `dev750` it changes 71 labels: 22 Purist rescues, five Purist harms, 31 exact
label rescues, and 16 exact label harms.

The development candidate instead preserves the model's parsed label and runs
eight named gap repairs. It changes 27 labels, with 22 Purist rescues, five
Purist-correct stays that become exact-label correct, and no observed Purist or
exact-label harms. Purist accuracy is **0.8093** (607/750), compared with
**0.8027** (602/750) for the current rule encode and **0.7800** (585/750) for
identity. Exact normalized-label accuracy is **0.6907** (518/750), compared
with **0.6747** (506/750) and **0.6547** (491/750), respectively.

This freezes a development candidate, not a new holdout result. `test450` was
not loaded or inspected, and the locked five-cell grid is unchanged.

## Study boundary

- Dataset: Gan 2026 synthetic `dev750`, split manifest
  `gan2026_split_v1`.
- Source: saved Gemini 3.7 Flash
  `gan_llm_extract` raw output.
- Replay: deterministic only; zero model calls.
- Primary scorer: Gan Purist category accuracy.
- Diagnostics: Pragmatic accuracy, exact normalized-label accuracy, scorable
  count, changed-row direction, and first-failure ownership.
- Parsed rows: 748/750. The same two extract parse failures remain incorrect in
  every arm.
- Inspection: permitted development rows only. Raw synthetic text is confined
  to the machine diagnostic artifacts.

## Arm results

| Encode policy | Purist | Pragmatic | Exact label | Scorable |
| --- | ---: | ---: | ---: | ---: |
| Identity | 585/750 (0.7800) | 612/750 (0.8160) | 491/750 (0.6547) | 748 |
| Strict format helper | 585/750 (0.7800) | 612/750 (0.8160) | 491/750 (0.6547) | 748 |
| Current rule encode | 602/750 (0.8027) | 630/750 (0.8400) | 506/750 (0.6747) | 748 |
| Codebook-preserving candidate | **607/750 (0.8093)** | **631/750 (0.8413)** | **518/750 (0.6907)** | 748 |
| Full select diagnostic | 646/750 (0.8613) | 663/750 (0.8840) | 544/750 (0.7253) | 748 |

The full-select row is diagnostic. It changes semantic selection and therefore
is not an encode candidate.

The strict format helper changes 16 labels but produces no rescue: all 16
remain exact-label wrong, with 11 Purist-correct stays and five wrong stays.
It is therefore not evidence that format repair is needed on this saved
distribution.

## What fails in the current rule encode

The current selected-evidence renderer makes 71 changes:

- Purist: 22 rescues, five harms, 36 correct stays, eight wrong stays.
- Exact label: 31 rescues, 16 harms, 24 wrong stays.
- Shape: 25 count/window changes, 21 frequency-kind changes, nine cluster
  structure changes, and 16 same-kind form changes.
- Selection: no selected event ids change. The problem is semantic
  re-derivation after selection, not an unrecorded selection change.

The five Purist regressions expose four mechanisms:

1. **Unknown is overwritten by a plausible evidence reading.** Rows 5977 and
   6368 are gold/model `unknown`; the renderer invents `multiple per 6 week`
   and `3 per 6 week` from ambiguous mixed-event evidence.
2. **Cluster structure is discarded.** Row 9943 is already exactly
   `1 cluster per 4 to 5 week, multiple per cluster`; the renderer changes it
   to `1 per 4 to 5 week`.
3. **A complete diary is incompletely parsed.** Row 16203 is already exactly
   `9 per 3 month`; the renderer misses “a seizure to date” and writes
   `8 per 2 month`.
4. **Cluster days are collapsed to one cluster.** Row 17135 is already exactly
   `5 cluster per month, multiple per cluster`; the renderer writes
   `1 cluster per month, multiple per cluster`.

The 11 additional exact-label harms that remain Purist-correct include
denominator rescaling, count replacement, and cluster-size or interval
collapse. They may preserve a broad category, but they do not preserve the
model's already encoded fact.

The current rule encode still has real value: its 22 Purist and 31 exact-label
rescues show that identity alone leaves deterministic gaps. The answer is a
narrower boundary, not removal of all deterministic encode behavior.

## Frozen candidate rules

All eight rules are independently switchable, recorded by stable rule id, and
classified as semantic deterministic repair when they change a sentinel,
frequency, window, count, or cluster meaning.

- `monthly_diary`: 12 changes; seven Purist rescues and five Purist-correct
  stays; 12 exact-label rescues. It sums complete month sequences and explicit
  diary date series.
- `complete_cluster_cadence`: five changes; five Purist and exact-label
  rescues. It fills a missing cluster cadence only for a selected cluster
  event and an unknown-form model label.
- `explicit_cluster_interval`: three changes; three Purist and exact-label
  rescues. It prefers the explicit spacing of clusters over a secondary daily
  phrase.
- `vague_periodic_cadence`: two changes; two Purist and exact-label rescues for
  bounded weekly wording.
- `year_to_date_window`: two changes; two Purist and exact-label rescues using
  the note date to encode the elapsed window.
- `hourly_rate`: one Purist and exact-label rescue from an explicit hourly
  rate.
- `single_last_period`: one Purist and exact-label rescue from an explicit
  single event in the last named period.
- `drop_unknown_wrapper`: one Purist and exact-label rescue where the evidence
  derivation independently confirms the embedded `1 per day`.

Every isolated rule improves both Purist and exact-label counts over identity.
Removing any one rule from the full candidate loses exactly its listed
contribution. There are no overlapping changed rows in this replay.

The candidate never changes selected event ids. Its 27 changes consist of 18
frequency-kind changes and nine count/window changes; none is misclassified as
format-only.

## Boundary slices

Across the 748 parsed rows, identity / current encode / candidate Purist-correct
counts by partitioning frequency band are:

- currently zero: 104 / 105 / 104 of 112;
- unknown: 110 / 108 / 110 of 126;
- submonthly: 44 / 45 / 45 of 90;
- monthly: 86 / 91 / 93 of 133;
- weekly-to-subdaily: 174 / 182 / 184 of 206;
- daily: 67 / 71 / 71 of 81.

The candidate does not regress identity in any partitioning band. Its advantage
over the current renderer comes from restoring two unknown rows and adding two
rescues in each of the monthly and weekly bands, while declining the current
renderer's select-like seizure-free rewrite in the zero band. On overlapping
qualitative slices, cluster-burden correctness is 250 / 261 / 263 of 322 and
seizure-free-duration correctness is 77 / 79 / 80 of 115.

## Candidate versus current encode

For Purist scoring, both encoders are correct on 599 rows, the candidate alone
is correct on eight, the current encode alone is correct on three, and neither
is correct on 140. The candidate-only rows are:

- the five current Purist regressions;
- one complete monthly diary the current parser misses (row 16107);
- two explicit cluster intervals that the current renderer incorrectly
  reduces to a secondary daily rate (rows 16590 and 16618).

The three current-only rows are not evidence for broad encode re-derivation:

- row 190 requires dropping source cluster meaning to match a Gan gold
  projection;
- row 10481 has an explicit model cluster size where gold keeps only
  `multiple per cluster`;
- row 13889 requires revising selection from `unknown` to seizure-free.

Those are scorer/gold or select responsibilities, not safe encode repairs.

For exact-label scoring, both encoders are correct on 497 rows, the candidate
alone on 21, and the current encode alone on nine. The candidate's net
advantage is 12 exact labels.

## Residual ownership

The frozen candidate leaves 143 Purist-incorrect rows:

- 45 are repaired by the existing semantic select stack (`select_revision`);
- 35 contain a normalized event candidate in the gold category but the model
  selected another answer (`selection`);
- 59 have no normalized selected-event candidate that demonstrates a safe
  encode repair (`extract_or_unresolved`);
- two are extract parse failures;
- two reflect inspected scorer/gold projection conventions.

This ownership split explains the gap between candidate encode (0.8093) and the
full-select diagnostic (0.8613). Moving those select rescues into encode would
recreate the boundary violation this study was designed to remove.

## Transfer limits

The rules were designed and audited on the same permitted `dev750`
distribution. Zero observed regression is not out-of-sample evidence. Six of
the eight rules trigger on three or fewer rows, and this study does not test a
second model's codebook extract or a separate paraphrase stress set. The
candidate is therefore a validation-tuned hybrid development artifact, not a
general encode policy or a benchmark improvement.

The 59 `extract_or_unresolved` rows are deliberately not converted into new
rules without a demonstrated safe encode mechanism. Some may be extract
failures; others may need a new select rule or a scorer-policy decision.

## Recommendation

1. Keep `llm_encode` as the historical source-near renderer for experiments
   that actually provide source-near values.
2. Use `gan_rules_encode` as the frozen development candidate after
   `gan_llm_extract`.
3. Define codebook encode as identity plus the eight named gap repairs; do not
   run broad selected-evidence re-derivation.
4. Keep select/revision separate. Do not promote full-select behavior into
   encode to gain score.
5. Do not update paper claims or the locked five-cell grid from this
   development result. Any holdout evaluation must freeze this implementation
   first and report aggregate-only results under a new protocol.

## Reproduction and artifacts

Run from the repository environment:

```bash
source .venv/bin/activate
python scripts/analyze_gan_codebook_encode_rules_dev750.py
```

Artifacts:

- `experiments/gan_codebook_encode_rule_development_20260822/summary.json`
- `experiments/gan_codebook_encode_rule_development_20260822/rows.jsonl`
- `experiments/gan_codebook_encode_rule_development_20260822/changes.jsonl`
- `experiments/gan_codebook_encode_rule_development_20260822/residuals.jsonl`

`summary.json` records the source-output SHA-256, implementation SHA-256
values, package versions, scorer, split, row policy, replay mode, rule
ablations, regression lists, and the claim boundary.
