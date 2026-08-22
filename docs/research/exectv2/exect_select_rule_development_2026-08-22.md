# ExECT Select-rule development on dev140

Date: 2026-08-22  
Status: implemented and verified on development data; not promoted to holdout or paper results  
Protocol: [ExECT Select-rule development protocol](exect_select_rule_development_protocol_2026-08-22.md)  
Primary artifact: [`summary.json`](../../../experiments/exectv2_select_rule_development_20260822/summary.json)

## Answer

The deterministic ExECT Select stack had seven source-supported gaps after the
Encode boundary was corrected. The accepted rules raise exact clinical-fact
micro-F1 on the frozen Gemini `dev140` extract distribution from **0.8703 to
0.9001**. They change 28 letter/family key sets; all 28 improve, 22 become
exact, and no comparator-exact set regresses. All 36 rule actions retain exact
source evidence.

| Arm | Clinical fact F1 | Diagnosis | Investigations | Prescription | SeizureFrequency |
| --- | ---: | ---: | ---: | ---: | ---: |
| Deterministic Encode, before Select | 0.8529 | 0.7608 | 0.9513 | 0.9576 | 0.7862 |
| Current deterministic Select comparator | 0.8703 | 0.7944 | 0.9513 | 0.9424 | 0.8301 |
| Accepted deterministic Select stack | **0.9001** | **0.8674** | 0.9513 | **0.9600** | **0.8339** |

The accepted arm has 676 TP, 30 FP, and 120 FN: precision **0.9575**,
recall **0.8492**. It gets 91 Diagnosis, 129 Investigations, 128
Prescription, and 102 SeizureFrequency letter outputs exactly right.

These are exact multiset scores from `clinical_headline_unit_keys`, computed
per letter and family. The study used 140 saved development rows and made no
model calls. `test60` was not loaded or inspected.

## Accepted rules and independent evidence

Each candidate was run alone on top of the current comparator and then removed
from the combined candidate. Every accepted rule has a positive isolated
contribution, no comparator-exact regression, and a negative leave-one-out
effect when removed from the combined stack.

| Rule | Category / authority | Actions | Changed pairs | Isolated F1 | Target-family F1 | Exact rescues |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `selection.diagnosis_source_local_specificity` | clinical epilepsy / rewrite | 3 | 3 | 0.8744 | Diagnosis 0.8064 | 2 |
| `selection.diagnosis_explicit_heading_phenotype` | benchmark format / reselect | 1 | 1 | 0.8711 | Diagnosis 0.7968 | 1 |
| `selection.prescription_local_regimen_scope` | clinical epilepsy / rewrite | 2 | 1 | 0.8730 | Prescription 0.9524 | 1 |
| `selection.prescription_active_titration` | clinical epilepsy / reselect | 2 | 2 | 0.8719 | Prescription 0.9476 | 2 |
| `selection.prescription_exact_regimen_dedupe` | benchmark format / drop | 1 | 1 | 0.8709 | Prescription 0.9447 | 1 |
| `selection.sf_named_type_identity` | seizure frequency / rewrite | 1 | 1 | 0.8711 | SeizureFrequency 0.8339 | 1 |
| `selection.sf_to_diagnosis_explicit_type` | benchmark format / invent | 26 | 19 | 0.8899 | Diagnosis 0.8539 | 14 |
| All seven | mixed / named actions | 36 | 28 | **0.9001** | — | **22** |

The isolated scores are not additive. The cross-family rule consumes the
already-selected SeizureFrequency ledger after seizure-type identity has been
reconciled, while the Prescription rules can act on the same regimen in a
fixed order. The action ledger and leave-one-out arms expose those interactions
instead of crediting the whole gain to an unnamed post-processor.

## What each component solved

### 1. Keep Diagnosis specificity local to its source mention

Rule: `selection.diagnosis_source_local_specificity`

The existing Diagnosis selection logic sometimes broadened an encoded source
diagnosis or moved it onto a sibling branch. The new rule restores the source
concept only when the selected rewrite is demonstrably broader or conflated.
Observed corrections include:

- EA0123: `generalised epilepsy` returns to `epilepsy` for the local heading
  “longstanding epilepsy with generalised tonic clonic seizures”;
- EA0167: `symptomatic structural focal epilepsy` returns to the explicitly
  named `temporal lobe epilepsy`;
- EA0200: the generic `epilepsy` fact is not replaced by its sibling phrase
  merely because the same sentence later says “genetic generalised epilepsy.”

An explicit possible or probable generalised classification remains eligible
for the selected classification. The rule does not use a letter id, gold
label, or global row multiplicity.

### 2. Retain an explicit heading phenotype without reopening JME

Rule: `selection.diagnosis_explicit_heading_phenotype`

An absence phenotype explicitly emitted under a Diagnosis heading can be a
separate benchmark fact. The first candidate restored every such phenotype;
it rescued one row but regressed three Juvenile Myoclonic Epilepsy rows, where
the syndrome owns the phenotype under the existing convention. That candidate
was rejected. The accepted rule is silent whenever JME is present and fires
once, rescuing EA0161.

This is recorded as benchmark-format reselection, not as new clinical
inference.

### 3. Keep rescue cadence on the named medicine

Rule: `selection.prescription_local_regimen_scope`

In a shared sentence, an as-required rescue cue for one medicine could spread
to scheduled sibling regimens. The rule restores cadence from each encoded
medicine phrase. In EA0150, levetiracetam and lamotrigine remain twice daily
while clobazam alone remains as required.

The operand is the emitted regimen ledger. The rule does not infer a cadence
that is absent from the selected medicine's source fact.

### 4. Keep the current starting regimen of an active titration

Rule: `selection.prescription_active_titration`

The comparator could suppress an entire titration even when the sentence
states a current starting dose. The accepted rule reselects only that initial
current regimen. It does not select a target dose, and it remains silent for a
true future request to prescribe, start, commence, or initiate treatment. It
rescues EA0092 and EA0116 without reopening planned-treatment rows.

### 5. Remove only an exact historical regimen duplicate

Rule: `selection.prescription_exact_regimen_dedupe`

EA0075 contains a historical initiation assertion and a current assertion of
the same exact regimen. The rule drops the historical duplicate. It requires
the same drug, dose, unit, and cadence and preserves unequal regimens. It also
preserves identical current assertions, because the exact scorer retains
benchmark multiplicity.

### 6. Preserve the selected seizure type within a shared evidence group

Rule: `selection.sf_named_type_identity`

When several named seizure types share evidence and state attributes, one row
could be reassigned to a sibling type. The rule reconciles the entire
evidence/state group rather than choosing one convenient row. It rescues
EA0006. Explicit refinements such as `typical absences` and focal seizures
with altered awareness remain permitted, including when the CUI becomes more
specific.

### 7. Expose an already-selected named SF fact in Diagnosis

Rule: `selection.sf_to_diagnosis_explicit_type`

The scorer expects an explicitly named seizure type in both its frequency and
Diagnosis views in some rows. The rule projects an already-selected, named
SeizureFrequency fact into Diagnosis with the same evidence and concept id. It
never scans unused note text and ignores generic `seizure` rows. It also
deduplicates embedded focal/partial motor aliases already present in
Diagnosis.

This rule accounts for 26 of 36 actions and 19 of 28 improved pairs, so its
contribution is reported separately. Its authority is `invent` in the
Diagnosis view, but its portability category is benchmark format: the
clinical fact was already selected by the upstream SF lane.

## Changed-row audit

The combined candidate has:

- 28 changed letter/family pairs, all with a lower FP+FN error count;
- 22 wrong-to-exact rescues;
- zero correct-to-wrong changes;
- zero comparator-exact regressions;
- 36 recorded rule actions, all with exact evidence.

The exact-rescue list and before/after key multisets are in
[`family_changes.jsonl`](../../../experiments/exectv2_select_rule_development_20260822/family_changes.jsonl).
Mention-level rule ids, action classes, evidence, and attributes are in
[`rule_actions.jsonl`](../../../experiments/exectv2_select_rule_development_20260822/rule_actions.jsonl).

## Saved Gemini Select diagnostic

The saved later-stage Gemini program is a diagnostic comparator, not an
ablation of the deterministic rules.

| Same-input arm | Clinical fact F1 |
| --- | ---: |
| Saved Gemini Encode | 0.8176 |
| Saved Gemini Select | 0.8213 |
| Current deterministic Select on saved Gemini Encode | 0.8484 |
| Accepted deterministic Select on saved Gemini Encode | **0.8765** |

The saved model Select program provides a small positive aggregate change from
its own Encode input. The deterministic candidate produces the larger result
on those same encoded mentions, but this remains one inspected development
distribution and is not evidence of clinical superiority.

## No-call transfer audit

After freezing the rules on Gemini, the candidate was replayed on every saved
`dev140` raw-output distribution available to the audit. Aggregate F1 improves
on all nine. Across the 128 changed letter/family pairs, 127 improve and one
is score-neutral; none worsens and no comparator-exact pair regresses.

| Saved raw distribution | Comparator | Candidate | Changed-pair direction |
| --- | ---: | ---: | --- |
| LLM-only DeepSeek | 0.8875 | 0.8968 | 8 better |
| LLM-only Gemini | 0.8703 | 0.9001 | 28 better |
| LLM-only GPT-5.6 Luna | 0.8636 | 0.8765 | 12 better |
| LLM-only Grok | 0.8884 | 0.9001 | 11 better |
| LLM-pre-post DeepSeek | 0.8769 | 0.8843 | 8 better |
| LLM-pre-post Gemini | 0.8822 | 0.8965 | 14 better |
| LLM-pre-post Gemma | 0.7288 | 0.7601 | 26 better |
| LLM-pre-post GPT-5.6 Luna | 0.8754 | 0.8902 | 14 better |
| LLM-pre-post Grok | 0.8909 | 0.8988 | 6 better, 1 same |

Eight sources parse all 140 rows. The saved Gemma source has four pre-existing
parse failures; comparator and candidate receive the same empty mentions for
those rows. Its within-source delta is comparable, but its absolute score is
not directly comparable to the cleanly parsed sources.

Transfer inspection also fixed portability defects before the freeze: heading
recovery became JME-aware; titration recovery excluded prescribe/start requests
and target doses; exact-regimen dedupe stopped collapsing current multiplicity;
SF identity became group-wide while permitting explicit refinements; and the
cross-family projection learned the embedded focal/partial motor alias.

Machine results are in
[`transfer_summary.json`](../../../experiments/exectv2_select_rule_development_20260822/transfer_summary.json)
and
[`transfer_changes.jsonl`](../../../experiments/exectv2_select_rule_development_20260822/transfer_changes.jsonl).

## Rejected candidate

`selection.sf_recent_event_over_historical_free` replaced a historical
seizure-free sibling with an explicitly recent event. The change was
clinically plausible and retained exact evidence, but its only changed
letter/family pair was neutral under the declared exact scorer. It was not
accepted into the selected stack. This avoids promoting an unmeasured semantic
preference merely because it reads well in one row.

## Residual ownership and stopping boundary

The accepted candidate leaves 110 non-exact letter/family pairs. Their first
failure is upstream of Select in every case:

| First failure at the Encode boundary | Error units |
| --- | ---: |
| Required key absent at Encode | 120 |
| Excess key already present at Encode and preserved | 30 |
| Added or rewritten first by the accepted Select rules | **0** |

This is a first-failure attribution, not a claim that downstream rules could
never compensate for upstream errors. It establishes the stop for this study:
no further rule was justified from the permitted rows without note scanning,
gold-conditioned operands, unsupported inference, or a separate upstream
extract/encode change. The row-level ledger is
[`residual_family_errors.jsonl`](../../../experiments/exectv2_select_rule_development_20260822/residual_family_errors.jsonl).

## Runtime attribution

The seven accepted rules are an explicit post-lens stage in the selected
`exectv2_llm_pre_post` architecture. Runtime rows retain:

- `post_lens_mentions`, the stage input;
- `select_rule_actions`, including the rule id and before/after fact;
- `policy.select_rule_ids`, the exact selected or archived ablation policy.

An explicit non-selected rule set requires `archived_replay=True`. This keeps
the current comparator and every single-rule or leave-one-out arm replayable
without making an archived policy the default.

## Claim boundary

This is inspected development evidence from saved `dev140` outputs. The
cross-model audit tests whether the frozen rules behave similarly on other
saved development distributions; it is not an independent split, holdout
generalization, or clinical validation. The result has not replaced the
promoted paper rung artifacts. `test60` remains sealed.

The accepted rules are replay stops for the cited table. On saved
`exect_llm_only` raw they define cell 3 rule select after rule encode
(the six-model roster row, not the peak). On saved later-stage encode
they define cell 4 rule select (Gemini only). ExECT uses the same five
role rows as Gan; the cited score is the select stop. `exect_llm_with_rules`
is the live alias of `exect_llm_pre_post` (both extract); it is not a
second headline method. A living producer raw F1 is not LLM extract.

## Post-study portability correction

After the study freeze, the accepted Diagnosis and SF rules were rewritten so
they state a hierarchy instead of the rescue phrases that first justified
them. Scores above remain the frozen study reading; this section is a
mechanism correction, not a new scored arm.

- `selection.diagnosis_specificity_hierarchy` now treats laterality as an
  epilepsy classification (`possible/probable generalised`, `generalised
  epilepsy`), not as the adjective in generalised tonic clonic seizures. A
  `namely` / `i.e.` clause cannot overwrite the source concept. A named lobe
  wins over a same-branch etiology form, and the structural-epilepsy prefix
  no longer strips the lobe.
- `selection.diagnosis_source_local_specificity` restores a source fact only
  when the later rewrite is broader, an etiology sibling of a named lobe, or
  a laterality child the hierarchy does not authorize. The
  `longstanding…GTC` and `namely genetic generalised` regexes are gone.
- `selection.diagnosis_explicit_heading_phenotype` uses a syndrome-owns-
  phenotype table. JME still owns absence and myoclonus; temporal lobe
  epilepsy does not. Heading myoclonus can be retained when no owning
  syndrome is present.
- `selection.sf_named_type_identity` permits parent/child refinements
  (absences ⊂ typical absence; focal seizures ⊂ focal seizures with altered
  awareness) instead of two CUI pairs plus an exact surface.
- `selection.sf_to_diagnosis_explicit_type` states always-project versus
  heading-only CUIs, and projects named absence refinements as
  `absence seizures`.
- `selection.prescription_active_titration` treats `prescribe` / `start` /
  `commence` / `initiate` as the planned-treatment class. Letter openers are
  test examples, not the rule.

