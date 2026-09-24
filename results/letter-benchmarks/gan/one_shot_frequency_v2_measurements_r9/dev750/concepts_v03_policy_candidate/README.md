# R9 scored-term policy candidate after source review

This is a saved-response **Gan 2026 synthetic dev750** comparison, not a new
model run or paper endpoint. All 750 rows, including `row_ok=False`, and all
1,219 frozen compact v0.3 reference claims remain. It uses the unchanged R9
DeepSeek V4.1 Flash first responses, no format or semantic repair, the v3
window convention, and `finding_compact_concepts_v03` with
`compact_scored_terms_v03`. Invalid responses contribute reference misses.
No test450 rows were inspected. Reproduce with
`.venv/bin/python scripts/benchmarks/score_compact_concepts_v03.py` in a fresh
output directory. `score.json` records model, prompt, split, row, replay,
repair, source and code hashes; local per-letter pairs and the scored reference
are under `runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/`.

The [focused source and output checks](../../../../../../runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/source_review_cases.jsonl)
cover the final nine policy examples, including the prior owner edit reasons.
The [earlier 39-case audit](../concepts_v02_source_audit/README.md) covers the
initial lexical, population and trigger distinctions. These are selected
mechanism cases, not a prevalence sample.

## Policy outcome

The conditional qualitative cases have a narrow rule. A stated level that is
explicitly limited by **only**, a contrastive **when**, or **if** keeps that
condition: uncommon spells *when meals are regular* (6321), progression to
convulsion *if the cluster is prolonged* (10996), and a perimenstrual-only or
specifically premenstrual cluster pattern (3468, 7168). The owner-edited v0.3
reference already names the restrictions in 6321 and 10996. Non-exclusive
associations such as occasional clustering on workdays after missed breakfast
(2023) or during restricted sleep offshore (4592) remain evidence context.

The 19 combined reference populations with an unmapped descriptive component
retain their literal combined label and scope. R9 emits no combined-scope
claim for 18 of them; for 17189 it emits the same combined wording. The main
error in this group is therefore omitted or narrowed population, not a need
for a large spelling dictionary. The owner-reviewed reference explicitly
keeps ordinary seizures distinct from `prolonged or status episodes` (17146)
and keeps `clusters requiring attendance` within the combined absence (17189).

The owner-reviewed 5092 claim is an absence of **observed clinical** seizures,
not an unrestricted absence; v3 scores the observation limit. Source 6077 has
an eight-month `day-to-day` absence alongside a recent flight event. The
owner's v0.3 adjudication explicitly retained that claim **provisionally**
with `past_or_unclear` phase and said the source cannot settle its relation to
the flight. The scorer keeps its literal restriction and does not turn it into
global current freedom. This one source ambiguity remains visible; it is not
resolved by a scorer alias or model prompt.

| Same saved R9 responses | Matches | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| Frozen literal v2 | 202 | 15.43% | 16.57% | 15.98% |
| Window-corrected v3 | 282 | 21.54% | 23.13% | 22.31% |
| Scored-term v2 | 445 | 34.00% | 36.51% | 35.21% |
| Scored-term v3 | 445 | 34.00% | 36.51% | 35.21% |

The v3 policy changes restriction agreement in one source-aligned pair (5092)
and changes no whole-claim matches. Source-aligned pairs remain 1,062. The
review queue still flags 266 claims: 194 nonempty literal restrictions with
no scored code, 73 named labels outside the finite type dictionary, and 19
combined populations with a literal fallback; categories overlap. These are
expected review markers, **not** 266 known errors. A scan of the remaining
literal restrictions found no further explicit `only`, `outside`, or `if`
population limits. Selected `when`/`during` examples were source-reviewed;
the unreviewed remainder stays available in the local queue.

The scored-term dictionary is a development candidate. Align the next prompt's
diary arithmetic rule before testing it on a small dev slice. This replay
remains separate from the frozen v0.3 paper score.

## Diary arithmetic correction

The earlier 39-case audit called source 15992 a model aggregation error. That
attribution was wrong. Its reference count of seven is the owner-approved sum
of four December and three January awake events; seven is not stated in the
note. R9's frozen prompt explicitly says `Do not infer arithmetic`, and R9
returned the two source counts. The mismatch is between prompt and reference
policy, so this miss cannot fairly be charged to the model alone.

The [eight selected source checks](../../../../../../runs/one_shot_frequency_v2_measurements_r9/dev750/concepts_v03_policy_candidate/diary_arithmetic_review.jsonl)
show the same pattern for 4402, 4410, 5995, 6065, 15965, 15982, 15992 and
16041: the owner reference has a derived diary total and the saved R9 output
has source components without that total. These are selected examples, not a
prevalence estimate. The frozen score above remains a diagnostic score under
this documented policy mismatch. A future prompt must allow a single total
when disjoint, same-unit diary components can be added without overlap, while
retaining the prohibition on guessed dates, units, denominators and ambiguous
cluster arithmetic. The source-stated components remain available as evidence;
subtype progressions must not be counted again.
