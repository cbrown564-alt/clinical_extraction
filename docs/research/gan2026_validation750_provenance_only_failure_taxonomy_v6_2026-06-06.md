# Gan 2026 Validation750 Provenance-Only Failure Taxonomy V6

Date: 2026-06-06

Status: completed validation-development audit plus no-call replay. The note
starts from the original `220` provenance-only routed rows in
`experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl`
and closes with the replay result from
`experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`.

This note explains why rows land in the provenance-only route families
`selected_evidence_missing_exact_trace` and `selected_source_id_invalid`,
separates real trace failures from contract gaps, and maps each failure bucket
to the code path that likely created it.

This is not a benchmark claim and does not authorize locked-test inspection or
LLM-verifier promotion.

## Main Finding

The experiment confirmed that the extra carried `source_normalized_phrase`
should not be the provenance gate.

When provenance exactness is computed from the chosen primary candidates'
evidence spans and source ids, rather than from a separately carried normalized
summary phrase, the provenance-only surface collapses without changing any
rendered labels or scores.

High-level evidence:

- original routed rows: `276`
- replay routed rows: `82`
- original provenance-only rows: `220`
- replay provenance-only rows: `26`
- original `selected_evidence_missing_exact_trace`: `250`
- replay `selected_evidence_missing_exact_trace`: `0`
- original `selected_source_id_invalid`: `9`
- replay `selected_source_id_invalid`: `27`
- rendered rows unchanged: `580`
- scored rows unchanged: `580`
- Purist-correct scored rows unchanged: `488`

So the dominant prior failure mode was not "we do not know which candidate
won." It was "we required the wrong field to prove provenance."

## Completion Update

We completed the experiment by replaying the saved validation750
projection/render, score, and route chain after changing provenance exactness
to rely on the selected primary candidates' exact evidence/source trace instead
of `normalized_burden.source_normalized_phrase`.

Replay artifacts:

- `experiments/gan2026_clinical_assessment_projection_render_validation750_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`
- `experiments/gan2026_clinical_assessment_projection_score_validation750_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`
- `experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_candidate_trace_v1_2026-06-06.jsonl`

Before/after route summary:

| Surface | Original | Replay | Delta |
| --- | ---: | ---: | ---: |
| routed rows | `276` | `82` | `-194` |
| provenance-only rows | `220` | `26` | `-194` |
| `selected_evidence_missing_exact_trace` | `250` | `0` | `-250` |
| `selected_source_id_invalid` | `9` | `27` | `+18` |
| scored rows | `580` | `580` | `0` |
| Purist-correct scored rows | `488` | `488` | `0` |
| exact normalized-label matches | `418` | `418` | `0` |

Interpretation:

- `194 / 220` original provenance-only rows disappear immediately once exact
  provenance is tied to primary-candidate evidence instead of the extra summary
  phrase.
- the remaining provenance-only surface is no longer a phrase-rewrite taxonomy;
  it is almost entirely a real source-id instrumentation problem
  (`26` provenance-only rows plus `1` mixed row with
  `selected_source_id_invalid` and `mixed_window_or_vague_addition`)
- the increase from `9` to `27` `selected_source_id_invalid` rows is expected:
  rows that were previously masked by the stricter phrase gate now surface under
  the more honest remaining failure family

Decision:

- do not use `source_normalized_phrase` as the provenance-bearing exact-trace
  field
- keep provenance attached to exact selected candidate evidence spans and source
  ids
- treat `source_normalized_phrase` only as auxiliary normalization/reporting
  text while it remains useful elsewhere in the pipeline

## Audit Method

For every provenance-only routed row, we compared:

- the carried `source_normalized_phrase`
- the exact-trace phrases accepted by
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py`
- the selected source ids and expected source ids
- the row's assessment kind, aggregation policy, projection rule, rendered/null
  status, and score status

The exact-trace checker currently treats a row as exact only when the selected
phrase:

1. exactly equals a primary candidate `source_phrase`; or
2. exactly equals the primary candidate `evidence_span.text`; or
3. appears as a substring in the concatenated primary-candidate evidence text.

That means case-only rewrites, symbol normalization, clause trimming, burden
summaries, and model-written paraphrases all fail even when the primary
candidate and source ids remain clinically correct.

## Root Cause In Code

Two code paths together explain most of the surface:

1. `src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py`
   `_normalization_source_phrase(...)`

   Current behavior:
   if the draft already contains a non-empty `source_normalized_phrase`, keep
   it after cleaning.

   Effect:
   model-authored or repaired summary phrases survive into the final
   `ClinicalAssessment` even when an exact candidate phrase is available.

2. `src/clinical_extraction/tasks/seizure_frequency/gan2026/artifact_analysis/clinical_assessment_projection_render.py`
   `_selected_evidence_status_for_assessment(...)`

   Current behavior:
   exact trace is checked with exact string equality or exact substring
   containment.

   Effect:
   semantically faithful rewrites still fail the exact-trace contract.

The `9` `selected_source_id_invalid` rows are different. On this surface they
all come from carried source ids containing `unresolved`, so the source-id
format itself is the blocking issue.

## Top-Level Taxonomy

| Category | Rows | Rendered | Null | Scored | Main interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `semantic_rewrite_or_paraphrase` | 174 | 134 | 40 | 134 | Model or repair kept a burden summary that is clinically related to the winning candidate, but not an exact carried phrase |
| `selected_phrase_wraps_or_expands_exact_trace_phrase` | 20 | 19 | 1 | 19 | The exact candidate phrase is visibly inside the carried phrase, but the carried phrase adds extra context |
| `empty_selected_phrase` | 9 | 9 | 0 | 9 | Sentinel `unknown` / `no seizure frequency reference` rows with no carried evidence phrase |
| `unresolved_source_id_format` | 9 | 4 | 5 | 4 | Exact trace exists, but at least one carried source id is unresolved |
| `case_only_exact_phrase_match` | 6 | 4 | 2 | 4 | Exact phrase match under casefolding, but not byte-for-byte |
| `symbolic_normalization_rewrite` | 2 | 2 | 0 | 2 | Exact phrase except for symbol/word normalization such as adding `seizures` after `<= ... per day` |

## Category Detail

### 1. `semantic_rewrite_or_paraphrase`: 174 rows

Kind split:

- `frequency_rate`: `114`
- `seizure_free`: `30`
- `cluster_frequency`: `12`
- `unknown_frequency`: `11`
- `no_reference`: `7`

Other structure:

- rendered: `134`
- null: `40`
- scored: `134`
- single-primary rows: `170 / 174`

Interpretation:

This is the main bucket and the strongest evidence that the current surface is
mostly fixable plumbing debt.

The carried phrase usually preserves the same clinical burden, but in a cleaned
or compressed form that is no longer an exact trace. Typical patterns:

- add a generic event noun:
  `occurring multiple times in past week` ->
  `multiple seizures in past week`
- replace one lexical variant with another:
  `5 or 7 epileptic spasms this year` ->
  `5 to 7 epileptic spasms this year`
- compress a full sentence into a burden summary:
  `This week he has had 3 or 4 focal impaired awareness seizures, each lasting a few minutes...` ->
  `3 or 4 focal impaired awareness seizures this week`
- rewrite seizure-free statements into cleaner benchmark-facing phrasing:
  `He has had no further events since that date` ->
  `no seizures since 19-May-2024`
- rewrite no-reference or unknown rows into note-summary text rather than an
  exact note substring:
  `Invitation to school care-plan meeting (administrative coordination).` ->
  `No seizure frequency or burden information present`

Representative examples:

- row `278`: `occurring multiple times in past week` ->
  `multiple seizures in past week`
- row `1223`: `3 or 4 focal impaired awareness seizures, each lasting a few minutes` ->
  `3 or 4 focal impaired awareness seizures this week`
- row `2932`: `seizure-free since 29/09/2017` ->
  `seizure-free since 29/09/2017`
  but with Unicode/hyphen normalization and phrase cleaning
- row `11411`: note-level referral text ->
  `urgent referral for triage of generalised epilepsy`

Likely fix:

- stop using a free model summary as the provenance-bearing phrase when a
  single exact primary candidate exists
- preserve a separate exact selected-evidence field and keep
  `source_normalized_phrase` as a readable summary only

Rows:

`278, 1223, 1281, 1357, 1486, 1694, 1695, 1880, 2114, 2354, 2369, 2932, 2992, 3242, 3281, 3297, 3532, 3623, 3766, 3774, 3791, 3801, 3995, 4337, 4402, 4478, 4562, 4563, 4574, 4592, 4597, 4732, 4842, 5141, 5379, 5507, 5682, 5696, 5763, 5866, 5995, 6026, 6029, 6065, 6077, 6321, 6395, 6607, 6701, 7126, 7168, 7275, 7290, 7316, 7650, 8006, 8079, 8160, 8354, 8724, 8794, 8802, 8805, 8924, 9063, 9103, 9215, 9287, 9300, 9344, 9365, 9368, 9449, 9462, 9496, 10629, 11197, 11254, 11337, 11389, 11408, 11409, 11411, 11614, 11706, 11728, 11734, 11756, 11763, 12041, 12046, 12882, 13349, 13385, 13450, 13471, 13478, 13485, 13635, 13711, 13893, 14025, 14092, 14146, 14335, 14524, 14540, 14581, 14587, 14592, 14628, 14635, 14662, 14765, 14810, 14821, 14943, 14965, 15094, 15108, 15127, 15376, 15404, 15431, 15497, 15503, 15513, 15519, 15593, 15614, 15639, 15650, 15745, 15766, 15768, 15771, 15772, 15774, 15783, 15831, 15834, 15964, 15965, 15986, 15997, 16021, 16041, 16097, 16107, 16108, 16132, 16161, 16162, 16181, 16203, 16204, 16324, 16557, 16645, 16674, 16685, 16697, 16704, 16717, 16728, 16750, 16758, 16772, 16774, 16780, 16824, 16833, 16867, 16990`

### 2. `selected_phrase_wraps_or_expands_exact_trace_phrase`: 20 rows

Kind split:

- `cluster_frequency`: `8`
- `frequency_rate`: `6`
- `seizure_free`: `5`
- `unresolved_multiple`: `1`

Other structure:

- rendered: `19`
- null: `1`
- scored: `19`

Interpretation:

These are the cleanest low-risk fix candidates. The exact primary-candidate
phrase is already present inside the carried phrase. The trace fails only
because the carried phrase adds extra context before or after the exact phrase.

Representative examples:

- row `187`: `every seven to nine days` is wrapped as
  `events cluster every seven to nine days`
- row `6368`: `three witnessed convulsive episodes` is wrapped as
  `three witnessed convulsive episodes over the past six weeks`
- row `14973`: exact phrase appears inside a longer seizure-free summary

Likely fix:

- when the carried phrase contains an exact primary-candidate phrase, snap the
  provenance-bearing phrase back to that exact substring
- or explicitly store both `selected_evidence_exact_phrase` and the readable
  summary phrase

Rows:

`187, 1573, 3753, 4410, 6153, 6368, 7167, 9943, 10047, 10386, 11035, 11131, 11272, 12383, 14383, 14611, 14973, 15012, 16091, 16529`

### 3. `empty_selected_phrase`: 9 rows

Kind split:

- `unknown_frequency`: `2`
- `no_reference`: `7`

Other structure:

- rendered: `9`
- null: `0`
- scored: `9`

Interpretation:

These are sentinel rows. There is no carried evidence phrase at all, so the
exact-trace checker automatically marks them non-exact.

This is likely not the right policy for this row class. These rows are not
trying to prove an exact burden phrase. They are rendering `unknown` or
`no seizure frequency reference`.

Likely fix:

- exempt `unknown_due_to_absence` and `no_reference_boundary` sentinel rows
  from the exact selected-evidence route
- or use a `not_applicable` provenance state instead of forcing `exact_trace=false`

Rows:

`10618, 11405, 11463, 11632, 11640, 11658, 11681, 11804, 16714`

### 4. `unresolved_source_id_format`: 9 rows

Kind split:

- `seizure_free`: `4`
- `no_reference`: `2`
- `frequency_rate`: `1`
- `unknown_frequency`: `1`
- `cluster_frequency`: `1`

Other structure:

- rendered: `4`
- null: `5`
- scored: `4`

Interpretation:

This is the only bucket on the provenance-only surface that looks like a true
source-id plumbing failure rather than a phrase-carrying choice.

All `9` rows include at least one carried source id containing `unresolved`.
The exact phrase is already acceptable, but the span identifier was not fully
resolved upstream.

Likely fix:

- trace the unresolved-span source-id generator upstream and either resolve the
  span deterministically or downgrade these rows to an explicit
  `source_id_not_resolved` instrumentation bucket

Rows:

`5974, 6571, 7834, 11711, 11841, 13598, 13608, 15168, 15479`

### 5. `case_only_exact_phrase_match`: 6 rows

Kind split:

- `unknown_frequency`: `4`
- `frequency_rate`: `2`

Other structure:

- rendered: `4`
- null: `2`
- scored: `4`

Interpretation:

These are strict-string false positives. The carried phrase matches an exact
candidate phrase under casefolding, but not byte-for-byte.

Representative examples:

- `Sporadic drop attacks this year` ->
  `sporadic drop attacks this year`
- `Uncertain frequency` ->
  `uncertain frequency`

Likely fix:

- perform casefolded exact comparison before declaring trace failure
- build `expected_source_ids` from the canonicalized equality, not only
  case-sensitive equality

Rows:

`5490, 5491, 5504, 9888, 9912, 10268`

### 6. `symbolic_normalization_rewrite`: 2 rows

Kind split:

- `frequency_rate`: `2`

Interpretation:

These are low-risk normalization mismatches where the burden phrase is nearly
identical except for symbolic or noun insertion behavior.

Representative examples:

- row `10`: `<= four per day` ->
  `<= four seizures per day`
- row `79`: `<= 6 to 7 per year` ->
  `<= 6 to 7 seizures per year`

Likely fix:

- canonicalize simple event-noun insertion and comparator-symbol rewrites
- or snap the provenance-bearing phrase back to the exact candidate phrase

Rows:

`10, 79`

## What The Taxonomy Says About Fixability

The surface is highly fixable.

Evidence:

- `204 / 220` rows have exactly one primary candidate
- `172 / 220` are already rendered and scored, which means the clinical state
  is often stable enough for output even while provenance routing fires
- only `9 / 220` rows are true source-id-format failures

That means the obvious first fix is not a complex provenance model. It is
better stage discipline for which phrase is allowed to carry provenance.

## Recommended Fix Sequence

1. Separate exact-trace phrase from readable summary phrase.
   Keep a provenance-bearing field that must be copied from an exact primary
   candidate phrase or exact evidence span. Keep `source_normalized_phrase`
   free to remain human-readable if needed.

2. Add a snap-back rule for single-primary rows.
   When there is one winning primary candidate and the carried phrase is a
   paraphrase or expansion of that candidate, snap the provenance-bearing phrase
   back to the candidate phrase.

3. Exempt sentinel absence/no-reference rows from exact-trace routing.
   Their current route is a contract mismatch, not a meaningful audit signal.

4. Relax trivial exactness checks.
   Accept casefold-only matches and small symbol/noun normalization matches as
   exact.

5. Repair unresolved source ids upstream.
   This is the only small bucket that still looks like genuine source-id debt.

## Practical Next Experiment

This experiment is now complete.

The next deterministic follow-up is narrower:

1. inspect and repair the remaining `27` `selected_source_id_invalid` rows;
2. separate the `26` provenance-only unresolved-source rows from the single
   mixed clinical/provenance row;
3. keep the verifier target surface focused on the non-provenance `55` routed
   clinical/policy rows unless a later protocol explicitly broadens it.
