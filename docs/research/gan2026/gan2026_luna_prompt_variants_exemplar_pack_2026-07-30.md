# Luna Gan prompt-variant exemplar pack

Date: 2026-07-30
Status: drafting aid for the Luna A/B/C protocol; not a scored result

Protocol owner: [gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md](gan2026_luna_prompt_variants_dev750_protocol_2026-07-30.md)

Machine pack: [exemplar_pack.json](../../../experiments/gan2026_luna_prompt_variants_dev750_20260730/exemplar_pack.json) (SHA-256 `82eedfaf66a1a86a1390db2b779830b58652f367696a7021bf0be09eddd64a78`)

## Purpose

These 20 development rows are drawn from the frozen Luna v0.5 `validation750` residuals. They exist to ground prompt drafts for variants B and C. They are not a tuning set to overfit, not a benchmark score, and not an authorization to inspect `test450`.

## Selection rule

From Luna raw-wrong rows, prefer unrescued then prompt-addressable (rules-correct), diversify model_boundary_label within each clinical_subproblem.

## Slice targets

| Variant | Clinical subproblems | Exemplars |
| --- | --- | ---: |
| B rate and aggregation | `rate_denominator`, `cluster_or_diary_aggregation` | 8 |
| C current-state and boundaries | `seizure_free_boundary`, `temporal_selection`, `uncertainty_boundary`, `competing_event_selection` | 12 |

## Compact index

| Row | Slice | Variant | Gold | Luna raw | Luna final | Rules OK | Final OK |
| ---: | --- | --- | --- | --- | --- | --- | --- |
| 1030 | `rate_denominator` | B_rate_aggregation | `1 to 3 per month` | `1 or 3 per month` | `1 per month` | True | False |
| 1573 | `rate_denominator` | B_rate_aggregation | `11 per week` | `6 per week` | `6 per week` | True | False |
| 1866 | `rate_denominator` | B_rate_aggregation | `8 per 2 month` | `7 in 2 months` | `7 per 2 month` | True | False |
| 1880 | `rate_denominator` | B_rate_aggregation | `8 per 2 month` | `multiple per week` | `multiple per week` | True | False |
| 1165 | `cluster_or_diary_aggregation` | B_rate_aggregation | `5 to 7 per 3 week` | `seizure free for 6 weeks` | `seizure free for multiple year` | True | False |
| 1979 | `cluster_or_diary_aggregation` | B_rate_aggregation | `6 per 2 month` | `2 clusters per week` | `unknown` | True | False |
| 3261 | `cluster_or_diary_aggregation` | B_rate_aggregation | `2 cluster per month, 4 per cluster` | `2 clusters per month` | `2 cluster per month, multiple per cluster` | True | False |
| 4100 | `cluster_or_diary_aggregation` | B_rate_aggregation | `1 per 2 to 3 week` | `multiple per week` | `multiple per week` | True | False |
| 7859 | `seizure_free_boundary` | C_current_state_boundary | `unknown` | `seizure free for several weeks` | `seizure free for multiple year` | True | False |
| 9002 | `seizure_free_boundary` | C_current_state_boundary | `7 per year` | `seizure free for prolonged intervals` | `seizure free for multiple year` | True | False |
| 11282 | `seizure_free_boundary` | C_current_state_boundary | `unknown` | `seizure free since 05-Aug` | `seizure free for multiple year` | True | False |
| 7195 | `temporal_selection` | C_current_state_boundary | `unknown` | `1 per month` | `1 per month` | True | False |
| 14137 | `temporal_selection` | C_current_state_boundary | `unknown` | `3 to 4 seizures over 3 months` | `4 per 3 month` | True | False |
| 14628 | `temporal_selection` | C_current_state_boundary | `2 per 2 month` | `2 seizures in recent period` | `no seizure frequency reference` | True | False |
| 8144 | `uncertainty_boundary` | C_current_state_boundary | `seizure free for multiple month` | `unknown` | `unknown` | True | False |
| 15442 | `uncertainty_boundary` | C_current_state_boundary | `1 cluster per 4 day, 2 per cluster` | `null` | `unknown` | True | False |
| 15479 | `uncertainty_boundary` | C_current_state_boundary | `1 cluster per 4 to 5 day, 2 per cluster` | `multiple events in 1 day, typically 2 tonic seizures` | `unknown` | True | False |
| 5791 | `competing_event_selection` | C_current_state_boundary | `1 per month` | `2 in 3 months` | `no seizure frequency reference` | True | False |
| 7475 | `competing_event_selection` | C_current_state_boundary | `2 per 6 month` | `2 in 6 months` | `no seizure frequency reference` | True | False |
| 8160 | `competing_event_selection` | C_current_state_boundary | `seizure free for multiple month` | `approximately 1 every few weeks` | `no seizure frequency reference` | True | False |

## Row briefs for prompt drafting

Full note text is in the machine pack. Briefs below keep only the selected evidence quote and the selection rationale so the drafting pass can see the failure pattern without re-loading the artifact.

### Row 1030 (`rate_denominator` → B_rate_aggregation)

- Gold: `1 to 3 per month`
- Luna raw: `1 or 3 per month`
- Luna final: `1 per month`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `one or three seizures last month`
- Selection kind: `unresolved_multiple`
- Selection rationale: `Recent seizure frequency is reported as either one or three seizures in the last month, with uncertainty about which brief episodes represent definite seizures; therefore the frequency remains unresolved rather than countable as a single rate.`
- Note length: 3314 characters (full text in machine pack)

### Row 1573 (`rate_denominator` → B_rate_aggregation)

- Gold: `11 per week`
- Luna raw: `6 per week`
- Luna final: `6 per week`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `six focal non-motors in last week`
- Selection kind: `frequency`
- Selection rationale: `Among the separately reported current/recent semiologies, focal non-motor events have the highest stated frequency.`
- Note length: 3374 characters (full text in machine pack)

### Row 1866 (`rate_denominator` → B_rate_aggregation)

- Gold: `8 per 2 month`
- Luna raw: `7 in 2 months`
- Luna final: `7 per 2 month`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `seven absence seizures in the past two months`
- Selection kind: `frequency`
- Selection rationale: `Recent seizure frequency is documented for multiple semiologies; the absence seizures represent the highest stated burden.`
- Note length: 2014 characters (full text in machine pack)

### Row 1880 (`rate_denominator` → B_rate_aggregation)

- Gold: `8 per 2 month`
- Luna raw: `multiple per week`
- Luna final: `multiple per week`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `occurring several times per week`
- Selection kind: `frequency`
- Selection rationale: `The highest current seizure burden is the focal onset events occurring several times per week; other recent seizure types are also documented but at lower or less frequent rates.`
- Note length: 3113 characters (full text in machine pack)

### Row 1165 (`cluster_or_diary_aggregation` → B_rate_aggregation)

- Gold: `5 to 7 per 3 week`
- Luna raw: `seizure free for 6 weeks`
- Luna final: `seizure free for multiple year`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `given six seizure-free weeks following the travel-related cluster`
- Selection kind: `seizure_free`
- Selection rationale: `The recent cluster is followed by six weeks without further episodes, so the current seizure status is seizure-free.`
- Note length: 3708 characters (full text in machine pack)

### Row 1979 (`cluster_or_diary_aggregation` → B_rate_aggregation)

- Gold: `6 per 2 month`
- Luna raw: `2 clusters per week`
- Luna final: `unknown`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `smartwatch data suggests nocturnal movement clusters twice weekly`
- Selection kind: `frequency`
- Selection rationale: `The highest current or recent reported event burden is the smartwatch-suggested nocturnal movement clusters occurring twice weekly, exceeding the separately reported focal seizures and automatisms occurring three times each over two months.`
- Note length: 4210 characters (full text in machine pack)

### Row 3261 (`cluster_or_diary_aggregation` → B_rate_aggregation)

- Gold: `2 cluster per month, 4 per cluster`
- Luna raw: `2 clusters per month`
- Luna final: `2 cluster per month, multiple per cluster`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `She reports two clusters this month`
- Selection kind: `frequency`
- Selection rationale: `The note gives a current overall cluster frequency with a breakdown of approximately four absences per cluster; the overall current frequency is selected.`
- Note length: 2592 characters (full text in machine pack)

### Row 4100 (`cluster_or_diary_aggregation` → B_rate_aggregation)

- Gold: `1 per 2 to 3 week`
- Luna raw: `multiple per week`
- Luna final: `multiple per week`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `clusters of brief warning sensations (described as a rising internal feeling and metallic taste) on some days`
- Selection kind: `frequency`
- Selection rationale: `The warning-sensation clusters are described as occurring on some days, representing the highest current seizure-like event burden compared with the less frequent disruptive events occurring every 2–3 weeks.`
- Note length: 3226 characters (full text in machine pack)

### Row 7859 (`seizure_free_boundary` → C_current_state_boundary)

- Gold: `unknown`
- Luna raw: `seizure free for several weeks`
- Luna final: `seizure free for multiple year`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `he has not noted any further turns for several weeks, including during recent late shifts`
- Selection kind: `seizure_free`
- Selection rationale: `The note reports no further seizure-like turns for several weeks. The two recent prodromal sensations did not progress to collapse or witnessed convulsion and therefore do not override the seizure-free selection.`
- Note length: 3923 characters (full text in machine pack)

### Row 9002 (`seizure_free_boundary` → C_current_state_boundary)

- Gold: `7 per year`
- Luna raw: `seizure free for prolonged intervals`
- Luna final: `seizure free for multiple year`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `prolonged intervals entirely free of events`
- Selection kind: `seizure_free`
- Selection rationale: `The note describes prolonged recent intervals without events and a trajectory toward durable remission. The seven seizures were recorded in 2024 and are historical rather than a current seizure burden.`
- Note length: 2276 characters (full text in machine pack)

### Row 11282 (`seizure_free_boundary` → C_current_state_boundary)

- Gold: `unknown`
- Luna raw: `seizure free since 05-Aug`
- Luna final: `seizure free for multiple year`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `with none since`
- Selection kind: `seizure_free`
- Selection rationale: `The note reports a last seizure on 05-Aug followed by no further seizures, indicating current seizure freedom.`
- Note length: 779 characters (full text in machine pack)

### Row 7195 (`temporal_selection` → C_current_state_boundary)

- Gold: `unknown`
- Luna raw: `1 per month`
- Luna final: `1 per month`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `Since that period, frequency has settled back to baseline with only one possible brief event last month.`
- Selection kind: `frequency`
- Selection rationale: `The most recent countable overall seizure-like event burden is one possible brief event last month. The two episodes around childbirth are historical, and absence of convulsive events does not establish freedom from all seizure types.`
- Note length: 3459 characters (full text in machine pack)

### Row 14137 (`temporal_selection` → C_current_state_boundary)

- Gold: `unknown`
- Luna raw: `3 to 4 seizures over 3 months`
- Luna final: `4 per 3 month`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `since beginning Clobazam he has had 3 - 4 generalised tonic-clonic seizures`
- Selection kind: `frequency`
- Selection rationale: `The note reports a recent overall count of 3–4 generalised tonic-clonic seizures since starting Clobazam, representing the current seizure burden; the dated last event is retained separately.`
- Note length: 3066 characters (full text in machine pack)

### Row 14628 (`temporal_selection` → C_current_state_boundary)

- Gold: `2 per 2 month`
- Luna raw: `2 seizures in recent period`
- Luna final: `no seizure frequency reference`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `Two unprovoked seizures under evaluation`
- Selection kind: `frequency`
- Selection rationale: `The note documents an overall count of two recent unprovoked seizures, with the individual events occurring in April and June 2015.`
- Note length: 3252 characters (full text in machine pack)

### Row 8144 (`uncertainty_boundary` → C_current_state_boundary)

- Gold: `seizure free for multiple month`
- Luna raw: `unknown`
- Luna final: `unknown`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `She notes occasional brief déjà vu sensations without progression`
- Selection kind: `unknown`
- Selection rationale: `Although she has had no disabling seizures, current brief déjà vu sensations remain active and their frequency is described only as occasional, without a countable rate.`
- Note length: 1924 characters (full text in machine pack)

### Row 15442 (`uncertainty_boundary` → C_current_state_boundary)

- Gold: `1 cluster per 4 day, 2 per cluster`
- Luna raw: `None`
- Luna final: `unknown`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `followed by a day with multiple events, typically two tonic seizures`
- Selection kind: `frequency`
- Selection rationale: `The note describes active current seizures with intermittent cluster days; the highest current burden is multiple events, typically two tonic seizures on a cluster day. The pattern is not stated as a directly countable regular rate.`
- Note length: 3020 characters (full text in machine pack)

### Row 15479 (`uncertainty_boundary` → C_current_state_boundary)

- Gold: `1 cluster per 4 to 5 day, 2 per cluster`
- Luna raw: `multiple events in 1 day, typically 2 tonic seizures`
- Luna final: `unknown`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `a day with multiple events, typically two tonic seizures`
- Selection kind: `frequency`
- Selection rationale: `The note describes ongoing current seizures with recurrent clustering; the active multiple-event day represents the highest current seizure burden, so the seizure-free interval is not selected.`
- Note length: 3141 characters (full text in machine pack)

### Row 5791 (`competing_event_selection` → C_current_state_boundary)

- Gold: `1 per month`
- Luna raw: `2 in 3 months`
- Luna final: `no seizure frequency reference`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `Over the past three months they report two brief myoclonic jerks on awakening`
- Selection kind: `frequency`
- Selection rationale: `The myoclonic jerks are the more frequent current seizure type, occurring twice over the recent three-month period; a separate recent generalised tonic–clonic event is also documented.`
- Note length: 2851 characters (full text in machine pack)

### Row 7475 (`competing_event_selection` → C_current_state_boundary)

- Gold: `2 per 6 month`
- Luna raw: `2 in 6 months`
- Luna final: `no seizure frequency reference`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `two definite generalised tonic–clonic seizures in the last six months`
- Selection kind: `frequency`
- Selection rationale: `The note documents a definite recent count of two generalised tonic–clonic seizures in six months, despite uncertainty about overall frequency from incomplete diary recording.`
- Note length: 3543 characters (full text in machine pack)

### Row 8160 (`competing_event_selection` → C_current_state_boundary)

- Gold: `seizure free for multiple month`
- Luna raw: `approximately 1 every few weeks`
- Luna final: `no seizure frequency reference`
- Rules control correct: `True`
- First failure owner: `llm_clinical_selection`
- Evidence grade: `EXACT`
- Selected evidence: `occurring perhaps once every few weeks`
- Selection kind: `frequency`
- Selection rationale: `The patient reports ongoing brief lapses at approximately once every few weeks; these current seizure-like events take precedence over seizure-free statements about convulsions or clear seizures.`
- Note length: 2192 characters (full text in machine pack)

## Claim boundary

Development diagnostic exemplars for Luna prompt drafting only. Not a scoring result, not holdout evidence, and not for locked test450 inspection.
