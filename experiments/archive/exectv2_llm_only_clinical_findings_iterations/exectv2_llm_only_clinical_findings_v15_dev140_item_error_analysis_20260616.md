# ExECTv2 LLM-Only v0.15 Dev140 Item Error Analysis

- Source JSONL: `experiments\exectv2_llm_only_clinical_findings_v15_hard_negative_live_dev140_qwen36_35b_20260616.jsonl`
- Pipeline family: `exectv2_llm_only_clinical_findings`
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.15`
- Model: `ollama_chat/qwen3.6:35b`
- Split: `dev`, 140 letters
- Machine-readable companion: `experiments\exectv2_llm_only_clinical_findings_v15_dev140_item_error_analysis_20260616.json`

## Headline

- Strict SF benchmark per-item F1: 0.304 (P=0.299, R=0.310, TP=58, FP=136, FN=129)
- Phrase-only per-item F1: 0.488 (P=0.479, R=0.497, TP=93, FP=101, FN=94)
- Interpretation: phrase discovery is insufficient, and many phrase-near predictions still lose strict credit because Qwen supplied the wrong frequency attributes.

## Slice Breakdown

| Rows | Strict F1 | Phrase F1 | Strict TP/FP/FN | Phrase TP/FP/FN |
|---|---:|---:|---:|---:|
| 1-25 | 0.724 | 0.759 | 21/6/10 | 22/5/9 |
| 26-50 | 0.326 | 0.581 | 14/31/27 | 25/20/16 |
| 51-75 | 0.241 | 0.517 | 7/23/21 | 15/15/13 |
| 76-100 | 0.079 | 0.289 | 3/38/32 | 11/30/24 |
| 101-125 | 0.200 | 0.367 | 6/24/24 | 11/19/19 |
| 126-140 | 0.326 | 0.419 | 7/14/15 | 9/12/13 |

## Failure Taxonomy

- `first_pass_format_coercion`: 120 letters
- `phrase_spurious`: 75 letters
- `phrase_omission`: 57 letters
- `strict_correct`: 43 letters
- `projection_warning`: 40 letters
- `attribute_mismatch`: 34 letters
- `surface_match_attribute_loss`: 34 letters
- `over_extraction_no_gold`: 17 letters
- `verification_parse_failure`: 6 letters
- `total_miss`: 1 letters

## Attribute Mismatches

- `TimeSince_or_TimeOfEvent`: 24 same-phrase conflicts
- `NumberOfSeizures`: 15 same-phrase conflicts
- `NumberOfTimePeriods`: 15 same-phrase conflicts
- `TimePeriod`: 15 same-phrase conflicts
- `PointInTime`: 7 same-phrase conflicts
- `FrequencyChange`: 5 same-phrase conflicts
- `LowerNumberOfSeizures`: 4 same-phrase conflicts
- `MonthDate`: 4 same-phrase conflicts
- `UpperNumberOfSeizures`: 3 same-phrase conflicts
- `YearDate`: 2 same-phrase conflicts
- `DayDate`: 2 same-phrase conflicts

## Worst Strict Items

| Row | Letter | Strict errors | Phrase errors | Strict TP/FP/FN | Phrase TP/FP/FN |
|---:|---|---:|---:|---:|---:|
| 131 | EA0186 | 6 | 6 | 0/3/3 | 0/3/3 |
| 110 | EA0161 | 6 | 4 | 0/2/4 | 1/1/3 |
| 97 | EA0143 | 6 | 4 | 0/4/2 | 1/3/1 |
| 125 | EA0180 | 5 | 5 | 0/2/3 | 0/2/3 |
| 84 | EA0126 | 5 | 5 | 0/3/2 | 0/3/2 |
| 78 | EA0119 | 5 | 5 | 0/1/4 | 0/1/4 |
| 116 | EA0168 | 5 | 3 | 0/2/3 | 1/1/2 |
| 92 | EA0136 | 5 | 3 | 0/2/3 | 1/1/2 |
| 70 | EA0108 | 5 | 3 | 0/2/3 | 1/1/2 |
| 68 | EA0106 | 5 | 3 | 0/2/3 | 1/1/2 |
| 60 | EA0087 | 5 | 3 | 0/2/3 | 1/1/2 |
| 57 | EA0082 | 5 | 3 | 0/2/3 | 1/1/2 |
| 134 | EA0190 | 4 | 4 | 1/2/2 | 1/2/2 |
| 126 | EA0181 | 4 | 4 | 0/2/2 | 0/2/2 |
| 117 | EA0169 | 4 | 4 | 0/2/2 | 0/2/2 |
| 108 | EA0158 | 4 | 4 | 0/2/2 | 0/2/2 |
| 103 | EA0152 | 4 | 4 | 0/2/2 | 0/2/2 |
| 85 | EA0127 | 4 | 4 | 0/2/2 | 0/2/2 |
| 82 | EA0124 | 4 | 4 | 0/2/2 | 0/2/2 |
| 81 | EA0123 | 4 | 4 | 0/1/3 | 0/1/3 |
| 42 | EA0057 | 4 | 4 | 0/2/2 | 0/2/2 |
| 41 | EA0056 | 4 | 4 | 1/2/2 | 1/2/2 |
| 37 | EA0049 | 4 | 4 | 2/0/4 | 2/0/4 |
| 34 | EA0045 | 4 | 4 | 0/4/0 | 0/4/0 |
| 138 | EA0198 | 4 | 2 | 0/2/2 | 1/1/1 |

## Principles For Next Step

- Treat dev140 as a distribution-shift test, not as a prompt-length problem: rows 1-25 looked viable, but rows 76-125 collapsed, so small-prefix gains are not trustworthy acceptance evidence.
- Optimize phrase discovery and attribute assignment separately. Phrase-only F1 0.488 versus strict F1 0.304 means both are failing, and the strict gap is dominated by right-or-near-right phrases losing clinical attributes.
- Do not add deterministic candidate selection, semantic normalization, or deterministic selection to hide this gap. Those belong to the hybrid workstream; the llm_only path can only use deterministic schema validation, exact-evidence checks, format projection, CUI projection, and score reporting.
- Shift Qwen's work from a long bag of rules to a smaller explicit clinical audit: enumerate all scored frequency facts, classify statement family, then fill attributes from that family. The model needs coverage discipline before surface wording discipline.
- Use item-level slices as gates. Any next change must improve hard rows and failure classes, not merely recover dev5/dev25. Require per-slice reporting and worst-case item review before a dev140 rerun is considered successful.
- Verifier passes must be conservative and evidence-bound. They helped remove hard negatives, but parse failures and revise actions can also introduce attribute drift; adds/revisions need their own audit counts.

## Item-By-Item Ledger

### 001 EA0002 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 3 -> '3'", "coerced_field_value: finding[1] 'count' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures` {CUI=C0751495; CUIPhrase=focal-seizures; LowerNumberOfSeizures=2; MonthDate=3; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=3}
  - `secondary-generalised-seizures` {CUI=C0270838; CUIPhrase=secondary-generalised-seizures; NumberOfSeizures=4; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; LowerNumberOfSeizures=2; MonthDate=3; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=3} | evidence: In March she had 2 to 3 of her focal seizures without change in awareness.
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; NumberOfSeizures=4; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since} | evidence: Since her last clinic appointment she has had four secondary generalised seizures.
- Error readout: no strict error.

### 002 EA0004 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'count' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since} | evidence: several seizures since the last clinic appointment
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: a few seizures per year though
- Error readout: no strict error.

### 003 EA0005 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=['format_projected: dropped_unanchored_background_rate_since', 'cui_projected: dropped_unanchored_background_rate_since']
- Gold:
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; MonthDate=7; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year}
- Predicted:
  - `Generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=Generalised tonic clonic seizure; MonthDate=7; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016} | evidence: Generalised tonic clonic seizure-last event July 2016.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: he has had roughly two seizures per year since then.
- Error readout: no strict error.

### 004 EA0006 - strict F1 0.667, phrase F1 0.667

- Counts: gold=3, predicted=3; strict TP/FP/FN=2/1/1; phrase TP/FP/FN=2/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `verification_parse_failure`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[0] 'year' 2014 -> '2014'", "coerced_field_value: finding[1] 'year' 2014 -> '2014'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=['coerced_python_literal_to_json'], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=2; TimeSince_or_TimeOfEvent=During; YearDate=2014}
  - `absence-like-seizures` {CUI=C0563606; CUIPhrase=absence-like-seizures; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2014}
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=2; TimeSince_or_TimeOfEvent=During; YearDate=2014}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=2; TimeSince_or_TimeOfEvent=During; YearDate=2014} | evidence: 2 generalised tonic clonic seizures 2014
  - `absence like seizures` {CUI=C0563606; CUIPhrase=absence like seizures; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2014} | evidence: absence like seizures 2014
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: he remains seizure free
- Phrase-level missing gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=2; TimeSince_or_TimeOfEvent=During; YearDate=2014}
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: he remains seizure free
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 005 EA0007 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 3 -> '3'", "coerced_field_value: finding[0] 'period_high' 4 -> '4'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'period_low' 3 -> '3'", "coerced_field_value: finding[1] 'period_high' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=3; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=4}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=3; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=4}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=3; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=4} | evidence: Seizure type and frequency: seizures every 3 to 4 weeks, possibly focal onset
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=3; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=4} | evidence: She has seizures every 3 to 4 weeks.
- Error readout: no strict error.

### 006 EA0008 - strict F1 0.500, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=1/1/1; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=1; NumberOfTimePeriods=3; TimePeriod=Week}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Increased}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=3; TimePeriod=Week} | evidence: focal seizures with altered awareness every 3 weeks
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased} | evidence: the seizures have returned
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Increased}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased} | evidence: the seizures have returned
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 007 EA0009 - strict F1 1.000, phrase F1 1.000

- Counts: gold=3, predicted=3; strict TP/FP/FN=3/0/0; phrase TP/FP/FN=3/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'year' 2017 -> '2017'", "coerced_field_value: finding[2] 'count_low' 6 -> '6'", "coerced_field_value: finding[2] 'count_high' 9 -> '9'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'", "coerced_field_value: finding[2] 'year' 2017 -> '2017'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4}
  - `cluster-of-seizures` {CUI=C3203523; CUIPhrase=cluster-of-seizures; MonthDate=8; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=6; MonthDate=8; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=9; YearDate=2017}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4} | evidence: Currently she get around 2-4 seizures per month.
  - `cluster of seizures` {CUI=C3203523; CUIPhrase=cluster of seizures; MonthDate=8; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017} | evidence: a cluster of seizures in August, 2017
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=6; MonthDate=8; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=9; YearDate=2017} | evidence: 6-9 seizures every week for 3 weeks
- Error readout: no strict error.

### 008 EA0010 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'remove': 1}, statuses={'history_context_only': 1}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'age_low' 13 -> '13'", "coerced_field_value: finding[0] 'age_high' 19 -> '19'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {AgeLower=13; AgeUnit=Year; AgeUpper=19; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; LowerNumberOfSeizures=3; UpperNumberOfSeizures=4} | evidence: around 3 or 4 focal to bilateral convulsive seizures
- Phrase-level missing gold:
  - `seizures` {AgeLower=13; AgeUnit=Year; AgeUpper=19; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; LowerNumberOfSeizures=3; UpperNumberOfSeizures=4} | evidence: around 3 or 4 focal to bilateral convulsive seizures
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 009 EA0011 - strict F1 0.571, phrase F1 0.571

- Counts: gold=5, predicted=2; strict TP/FP/FN=2/0/3; phrase TP/FP/FN=2/0/3
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'history_context_only': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'year' 2017 -> '2017'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; FrequencyChange=Infrequent}
  - `convulsive-seizure` {CUI=C0751494; CUIPhrase=convulsive-seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
- Predicted:
  - `Focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=Focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week} | evidence: Focal seizures with altered awareness approximately 1 per fortnight
  - `Focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=Focal to bilateral convulsive seizures; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017} | evidence: last event around Christmas 2017
- Phrase-level missing gold:
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
  - `convulsive-seizure` {CUI=C0751494; CUIPhrase=convulsive-seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
- Error readout: missed/renamed scored phrase(s).

### 010 EA0012 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 011 EA0014 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 012 EA0015 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 013 EA0016 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'diagnosis_without_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 014 EA0018 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 015 EA0019 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'revise': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=1; PointInTime=Last_Week; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; TimeSince_or_TimeOfEvent=During} | evidence: had a generalised tonic clonic seizure
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: He last had a seizure before this around a year ago.
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: He last had a seizure before this around a year ago.
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizure`: NumberOfSeizures: gold=1 vs pred=None; PointInTime: gold=Last_Week vs pred=None
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 016 EA0020 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'year' 2016 -> '2016'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'year' 2016 -> '2016'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016}
  - `absences` {CUI=C0563606; CUIPhrase=absences; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016} | evidence: has not had any further generalised tonic clonic seizures since August 2016
  - `absences` {CUI=C0563606; CUIPhrase=absences; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2016} | evidence: There have been no absences since November 2016
- Error readout: no strict error.

### 017 EA0021 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 4 -> '4'", "coerced_field_value: finding[0] 'count_high' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 018 EA0022 - strict F1 0.667, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=1/0/1; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures` {CUI=C0751495; CUIPhrase=focal-seizures; NumberOfSeizures=0; PointInTime=DrugChange}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Infrequent; PointInTime=DrugChange}
- Predicted:
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: the focal seizures are completely under control on the dose of lamotrigine 200 mg twice a day
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Infrequent; PointInTime=DrugChange}
- Error readout: missed/renamed scored phrase(s).

### 019 EA0023 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 7 -> '7'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 020 EA0024 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 021 EA0025 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=0/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 3 -> '3'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'generalised tonic chronic seizures'"]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=4}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Frequent}
- Predicted:
  - `generalised tonic chronic seizures` {LowerNumberOfSeizures=3; MonthDate=5; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=4} | evidence: approximately 3–4 generalised tonic chronic seizures per week from May to August
- Phrase-level missing gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=4}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Frequent}
- Phrase-level spurious predictions:
  - `generalised tonic chronic seizures` {LowerNumberOfSeizures=3; MonthDate=5; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=4} | evidence: approximately 3–4 generalised tonic chronic seizures per week from May to August
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 022 EA0026 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 15 -> '15'", "coerced_field_value: finding[0] 'period_count' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=15; NumberOfTimePeriods=4; TimePeriod=Month}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=15; NumberOfTimePeriods=4; TimePeriod=Month} | evidence: approximately 15 seizures over 4 months which all happen during sleep
- Error readout: no strict error.

### 023 EA0027 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 024 EA0028 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: has not had any further seizures
- Error readout: no strict error.

### 025 EA0030 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 026 EA0033 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 027 EA0034 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `focal to bilateral convulsive seizure` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizure; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2019} | evidence: focal to bilateral convulsive seizure 2019
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: she has not had any further seizures since increasing the levetiracetam
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizure` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizure; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2019} | evidence: focal to bilateral convulsive seizure 2019
- Same-phrase attribute conflicts:
  - `seizures`: TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 028 EA0035 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=0; NumberOfTimePeriods=4; TimePeriod=Year}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: generalised tonic clonic seizures, last seizure four years ago.
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: Previously she has been more than eight years seizure free.
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: Previously she has been more than eight years seizure free.
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizures`: NumberOfTimePeriods: gold=4 vs pred=None; TimePeriod: gold=Year vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 029 EA0038 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year}
- Predicted:
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; NumberOfSeizures=0} | evidence: She has had a recent generalised tonic chronic seizure at home.
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: Before the seizure she had been seizure free for 3 years.
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: Before the seizure she had been seizure free for 3 years.
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizure`: NumberOfSeizures: gold=1 vs pred=0; NumberOfTimePeriods: gold=1 vs pred=None; TimePeriod: gold=Year vs pred=None
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 030 EA0039 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=3, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=2
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'event'", "dropped_evidence_not_substring: text='event'"]
- Gold:
  - `convulsive-seizure` {CUI=C0751494; CUIPhrase=convulsive-seizure; NumberOfSeizures=1; NumberOfTimePeriods=5; TimePeriod=Year}
- Predicted:
  - `convulsive seizure` {CUI=C0751494; CUIPhrase=convulsive seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has had a convulsive seizure approximately every five years.
  - `event` {MonthDate=10; NumberOfSeizures=0; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: He recalls an event last month.
- Phrase-level spurious predictions:
  - `event` {MonthDate=10; NumberOfSeizures=0; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: He recalls an event last month.
- Same-phrase attribute conflicts:
  - `convulsive seizure`: NumberOfTimePeriods: gold=5 vs pred=1
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 031 EA0040 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'remove': 1, 'revise': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 3 -> '3'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange} | evidence: this has helped his seizures
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange} | evidence: this has helped his seizures
- Error readout: added non-matching phrase(s).

### 032 EA0043 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'diagnosis_without_frequency': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 4 -> '4'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'age_low' 15 -> '15'"], verification_parse=[], projection=['format_projected: dropped_unanchored_background_rate_since', 'cui_projected: dropped_unanchored_background_rate_since']
- Gold:
  - none
- Predicted:
  - `seizures` {AgeLower=15; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: They have happened roughly every year since the age of 15.
- Phrase-level spurious predictions:
  - `seizures` {AgeLower=15; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: They have happened roughly every year since the age of 15.
- Error readout: added non-matching phrase(s).

### 033 EA0044 - strict F1 0.667, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=1/0/1; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since} | evidence: has not had any further seizures since her last clinic appointment and since starting the lamotrigine
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Error readout: missed/renamed scored phrase(s).

### 034 EA0045 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=4; strict TP/FP/FN=0/4/0; phrase TP/FP/FN=0/4/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=4, verified=4, actions={'keep': 4}, statuses={'target_epileptic_seizure_frequency': 4}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[2] 'count' 0 -> '0'", "coerced_field_value: finding[3] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; MonthDate=6; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018} | evidence: He has had several episodes where he seemed to go into a day dream.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=6; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018} | evidence: He’s had three episodes whilst asleep where he's shook his arms and made unusual choking noises.
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; DayDate=31; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: His last episode was on 31st August 2018.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; DayDate=31; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: His last episode was on 31st August 2018.
- Phrase-level spurious predictions:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; MonthDate=6; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018} | evidence: He has had several episodes where he seemed to go into a day dream.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=6; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018} | evidence: He’s had three episodes whilst asleep where he's shook his arms and made unusual choking noises.
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; DayDate=31; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: His last episode was on 31st August 2018.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; DayDate=31; MonthDate=8; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: His last episode was on 31st August 2018.
- Error readout: added non-matching phrase(s).

### 035 EA0046 - strict F1 0.667, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=1/1/0; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; MonthDate=10; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2019}
- Predicted:
  - `Focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=Focal to bilateral convulsive seizures; MonthDate=10; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2019} | evidence: Focal to bilateral convulsive seizures, last event October 2019
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: He has not had any further events.
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: He has not had any further events.
- Error readout: added non-matching phrase(s).

### 036 EA0047 - strict F1 0.667, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=1/0/1; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-seizures` {CUI=C0234533; CUIPhrase=generalised-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `absences` {CUI=C0563606; CUIPhrase=absences; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Day}
- Predicted:
  - `generalised seizures` {CUI=C0234533; CUIPhrase=generalised seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: She gets generalised seizures once a week.
- Phrase-level missing gold:
  - `absences` {CUI=C0563606; CUIPhrase=absences; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Day}
- Error readout: missed/renamed scored phrase(s).

### 037 EA0049 - strict F1 0.500, phrase F1 0.500

- Counts: gold=6, predicted=2; strict TP/FP/FN=2/0/4; phrase TP/FP/FN=2/0/4
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=5, verified=2, actions={'keep': 2, 'remove': 3}, statuses={'non_target_episode': 3, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count_low' 1 -> '1'", "coerced_field_value: finding[1] 'count_high' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[2] 'count' 1 -> '1'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'", "coerced_field_value: finding[4] 'count' 1 -> '1'", "coerced_field_value: finding[4] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day}
  - `absence` {CUI=C0563606; CUIPhrase=absence; FrequencyChange=Infrequent}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Frequent}
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; FrequencyChange=Frequent}
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: generalised tonic clonic seizures 1 to 2 every month
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: He is having one to 2 generalised tonic clonic seizures every month.
- Phrase-level missing gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day}
  - `absence` {CUI=C0563606; CUIPhrase=absence; FrequencyChange=Infrequent}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Frequent}
- Error readout: missed/renamed scored phrase(s).

### 038 EA0050 - strict F1 0.333, phrase F1 0.667

- Counts: gold=4, predicted=2; strict TP/FP/FN=1/1/3; phrase TP/FP/FN=2/0/2
- Tags: `phrase_omission`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=6, verified=2, actions={'keep': 1, 'remove': 4, 'revise': 1}, statuses={'diagnosis_without_frequency': 2, 'non_target_episode': 2, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[2] 'count' 2 -> '2'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=1; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Infrequent}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=3; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since} | evidence: generalised tonic clonic seizures, 1 since previous appointment
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since} | evidence: his seizures have improved since reducing the lamotrigine
- Phrase-level missing gold:
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Infrequent}
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizures`: NumberOfSeizures: gold=1 vs pred=3
- Error readout: missed/renamed scored phrase(s), same phrase but wrong frequency attributes.

### 039 EA0052 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=[], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'attacks'"]
- Gold:
  - none
- Predicted:
  - `attacks` {NumberOfSeizures=4; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since} | evidence: Mr Richards has had 4 more attacks
- Phrase-level spurious predictions:
  - `attacks` {NumberOfSeizures=4; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since} | evidence: Mr Richards has had 4 more attacks
- Error readout: added non-matching phrase(s).

### 040 EA0054 - strict F1 0.800, phrase F1 0.800

- Counts: gold=5, predicted=5; strict TP/FP/FN=4/1/1; phrase TP/FP/FN=4/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=5, verified=5, actions={'keep': 5}, statuses={'target_epileptic_seizure_frequency': 5}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'year' 2014 -> '2014'", "coerced_field_value: finding[2] 'year' 2015 -> '2015'", "coerced_field_value: finding[3] 'count' 1 -> '1'", "coerced_field_value: finding[3] 'period_count' 1 -> '1'", "coerced_field_value: finding[4] 'count' 0 -> '0'", "coerced_field_value: finding[4] 'period_count' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; MonthDate=8; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2014}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; MonthDate=9; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2015}
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: 1 per week
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=8; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2014} | evidence: Focal to bilateral convulsive seizures August 2014 and September 2015
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=9; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2015} | evidence: Focal to bilateral convulsive seizures August 2014 and September 2015
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: These happen around once per week.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since} | evidence: He has not had one of his bigger focal to bilateral convulsive seizure for three years now.
- Phrase-level missing gold:
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=8; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2014} | evidence: Focal to bilateral convulsive seizures August 2014 and September 2015
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 041 EA0056 - strict F1 0.333, phrase F1 0.333

- Counts: gold=3, predicted=3; strict TP/FP/FN=1/2/2; phrase TP/FP/FN=1/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[2] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'day' 25 -> '25'", "coerced_field_value: finding[2] 'month' 12 -> '12'", "coerced_field_value: finding[2] 'year' 2009 -> '2009'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'partial motor seizures involving left arm twitching with retained awareness'"]
- Gold:
  - `partial-motor-seizures` {CUI=C0016399; CUIPhrase=partial-motor-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
  - `secondary-generalised-seizures` {CUI=C0270838; CUIPhrase=secondary-generalised-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year}
  - `secondary-generalized-seizures` {CUI=C0270838; CUIPhrase=secondary-generalized-seizures; DayDate=25; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2009}
- Predicted:
  - `partial motor seizures involving left arm twitching with retained awareness` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: He has partial motor seizures involving left arm twitching with retained awareness. He gets these every month.
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has also had secondary generalised seizures, they happen about every year, his last one was on Christmas day 2009.
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; DayDate=25; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2009} | evidence: his last one was on Christmas day 2009.
- Phrase-level missing gold:
  - `partial-motor-seizures` {CUI=C0016399; CUIPhrase=partial-motor-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
  - `secondary-generalized-seizures` {CUI=C0270838; CUIPhrase=secondary-generalized-seizures; DayDate=25; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2009}
- Phrase-level spurious predictions:
  - `partial motor seizures involving left arm twitching with retained awareness` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: He has partial motor seizures involving left arm twitching with retained awareness. He gets these every month.
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has also had secondary generalised seizures, they happen about every year, his last one was on Christmas day 2009.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 042 EA0057 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `verification_parse_failure`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'remove': 2}, statuses={'history_context_only': 2}, additions=2
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'period_count' 2 -> '2'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'day' 25 -> '25'", "coerced_field_value: finding[1] 'month' 12 -> '12'", "coerced_field_value: finding[1] 'year' 2009 -> '2009'"], verification_parse=['coerced_python_literal_to_json'], projection=["cui_projected: cui_not_mapped: 'dissociative seizures'", "format_projected: dropped_unmapped_frequency_change: 'continues'", "cui_projected: dropped_unmapped_frequency_change: 'continues'", "cui_projected: cui_not_mapped: 'dissociative seizures'"]
- Gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; DayDate=25; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2009}
- Predicted:
  - `dissociative seizures` {NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week} | evidence: Currently he his having dissociative seizures around twice every week.
  - `dissociative seizures` {} | evidence: He continues to get dissociative seizures which are brought on by stress.
- Phrase-level missing gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; DayDate=25; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2009}
- Phrase-level spurious predictions:
  - `dissociative seizures` {NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week} | evidence: Currently he his having dissociative seizures around twice every week.
  - `dissociative seizures` {} | evidence: He continues to get dissociative seizures which are brought on by stress.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 043 EA0059 - strict F1 0.800, phrase F1 0.800

- Counts: gold=3, predicted=2; strict TP/FP/FN=2/0/1; phrase TP/FP/FN=2/0/1
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'diagnosis_without_frequency': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015}
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Infrequent}
- Predicted:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: focal to bilateral convulsive seizures, last event 2015
  - `Focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=Focal seizures with altered awareness; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2017} | evidence: Focal seizures with altered awareness, last event 2017
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Infrequent}
- Error readout: missed/renamed scored phrase(s).

### 044 EA0061 - strict F1 0.000, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 2 -> '2'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'focal to bilateral seizures'"]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=10; TimePeriod=Year}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: focal seizures with altered awareness (unusual arm sensation), last event 3 years ago
  - `focal to bilateral seizures` {NumberOfSeizures=2; TimeSince_or_TimeOfEvent=Since} | evidence: focal to bilateral seizures 2 events in total, last event 10 years ago.
- Phrase-level missing gold:
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=10; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `focal to bilateral seizures` {NumberOfSeizures=2; TimeSince_or_TimeOfEvent=Since} | evidence: focal to bilateral seizures 2 events in total, last event 10 years ago.
- Same-phrase attribute conflicts:
  - `focal seizures with altered awareness`: NumberOfTimePeriods: gold=3 vs pred=None; TimePeriod: gold=Year vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 045 EA0062 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'remove': 2}, statuses={'non_target_episode': 2}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'count' 6 -> '6'", "coerced_field_value: finding[0] 'period_count' 2 -> '2'", "coerced_field_value: finding[1] 'count' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=6; NumberOfTimePeriods=2; TimePeriod=Year} | evidence: perhaps six in total.
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=6; NumberOfTimePeriods=2; TimePeriod=Year} | evidence: perhaps six in total.
- Error readout: added non-matching phrase(s).

### 046 EA0063 - strict F1 0.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=2/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Month}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since} | evidence: her seizures have stopped since reaching her current dose of lamotrigine
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: Her last seizure now was 5 months ago
- Same-phrase attribute conflicts:
  - `seizures`: FrequencyChange: gold=None vs pred=Decreased; NumberOfSeizures: gold=0 vs pred=None
  - `seizures`: NumberOfTimePeriods: gold=5 vs pred=None; TimePeriod: gold=Month vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: same phrase but wrong frequency attributes.

### 047 EA0067 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `secondary-generalised-seizures` {CUI=C0270838; CUIPhrase=secondary-generalised-seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month}
- Predicted:
  - `Secondary generalised seizures` {CUI=C0270838; CUIPhrase=Secondary generalised seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: Secondary generalised seizures, 2 per month in clusters
- Same-phrase attribute conflicts:
  - `secondary generalised seizures`: LowerNumberOfSeizures: gold=None vs pred=2; NumberOfSeizures: gold=2 vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 048 EA0068 - strict F1 0.667, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=1/0/1; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures` {CUI=C0751495; CUIPhrase=focal-seizures; FrequencyChange=Infrequent}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: has had no further seizures
- Phrase-level missing gold:
  - `focal-seizures` {CUI=C0751495; CUIPhrase=focal-seizures; FrequencyChange=Infrequent}
- Error readout: missed/renamed scored phrase(s).

### 049 EA0071 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'year' 2007 -> '2007'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'year' 2006 -> '2006'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2007} | evidence: she has a seizure last week
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2006} | evidence: Her last seizure before this was in 2006
- Phrase-level spurious predictions:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2007} | evidence: she has a seizure last week
- Same-phrase attribute conflicts:
  - `seizure`: NumberOfTimePeriods: gold=1 vs pred=None; TimePeriod: gold=Week vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=During; YearDate: gold=None vs pred=2007
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 050 EA0072 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `focal-motor-seizure` {CUI=C0016399; CUIPhrase=focal-motor-seizure; NumberOfSeizures=1; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `focal motor seizure` {CUI=C0016399; CUIPhrase=focal motor seizure; NumberOfSeizures=1} | evidence: Miss Trice has only had one focal motor seizure which is good for her.
- Same-phrase attribute conflicts:
  - `focal motor seizure`: PointInTime: gold=LastClinic vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 051 EA0073 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 052 EA0074 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1} | evidence: In June this year he had a collapse episode whilst in college. This occurred early in the morning and was witnessed. He felt non-specifically unwell and collapsed from his chair, and was noted to have jerking movement...
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1} | evidence: In June this year he had a collapse episode whilst in college. This occurred early in the morning and was witnessed. He felt non-specifically unwell and collapsed from his chair, and was noted to have jerking movement...
- Error readout: added non-matching phrase(s).

### 053 EA0075 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: she has had no further seizures
- Same-phrase attribute conflicts:
  - `seizures`: PointInTime: gold=DrugChange vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 054 EA0076 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 055 EA0078 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 056 EA0079 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=0/2/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'nocturnal generalised tonic clonic seizures'"]
- Gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Year}
- Predicted:
  - `nocturnal generalised tonic clonic seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: He has nocturnal generalised tonic clonic seizures which are associated with mild learnind difficulties.
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: he gets around 1 generlised tonic clonic seizure in his sleep per month.
- Phrase-level missing gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `nocturnal generalised tonic clonic seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: He has nocturnal generalised tonic clonic seizures which are associated with mild learnind difficulties.
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: he gets around 1 generlised tonic clonic seizure in his sleep per month.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 057 EA0082 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 3 -> '3'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `absences` {CUI=C0563606; CUIPhrase=absences; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Day; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=3}
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Frequent}
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Frequent; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Day; UpperNumberOfSeizures=3} | evidence: the absences continue fairly frequent, he probably gets 2-3 per day
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: His last generalised tonic clonic seizure was two years ago
- Phrase-level missing gold:
  - `absences` {CUI=C0563606; CUIPhrase=absences; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Day; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=3}
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizure` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: His last generalised tonic clonic seizure was two years ago
- Same-phrase attribute conflicts:
  - `absences`: FrequencyChange: gold=None vs pred=Frequent; TimeSince_or_TimeOfEvent: gold=During vs pred=None
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 058 EA0084 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since} | evidence: he has been seizure free since starting antiepileptic medication.
- Error readout: no strict error.

### 059 EA0085 - strict F1 0.667, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=1/1/0; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[0] 'age_low' 17 -> '17'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'year' 2020 -> '2020'"], verification_parse=[], projection=['format_projected: dropped_unanchored_background_rate_since', 'cui_projected: dropped_unanchored_background_rate_since']
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2020}
- Predicted:
  - `seizures` {AgeLower=17; AgeUnit=Year; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has had on average one seizure a year since the age of 17
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2020} | evidence: but a total of 3 in 2020
- Phrase-level spurious predictions:
  - `seizures` {AgeLower=17; AgeUnit=Year; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has had on average one seizure a year since the age of 17
- Error readout: added non-matching phrase(s).

### 060 EA0087 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 4 -> '4'", "coerced_field_value: finding[1] 'period_count' 3 -> '3'", "coerced_field_value: finding[2] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'period_count' 5 -> '5'"], verification_parse=[], projection=[]
- Gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; FrequencyChange=Increased}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=4; NumberOfTimePeriods=3; TimePeriod=Week}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=4; NumberOfTimePeriods=3; TimePeriod=Week; TimeSince_or_TimeOfEvent=During} | evidence: She has had four in the last three weeks
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Week} | evidence: has had up to five weeks seizure free
- Phrase-level missing gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; FrequencyChange=Increased}
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Week} | evidence: has had up to five weeks seizure free
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizures`: TimeSince_or_TimeOfEvent: gold=None vs pred=During
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 061 EA0088 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=["format_projected: dropped_unmapped_point_in_time: 'before Christmas'", "cui_projected: dropped_unmapped_point_in_time: 'before Christmas'"]
- Gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: He has been seizure free since before Christmas.
- Same-phrase attribute conflicts:
  - `seizure free`: MonthDate: gold=12 vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 062 EA0092 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `complex partial seizures` {CUI=C0149958; CUIPhrase=complex partial seizures; NumberOfSeizures=1} | evidence: a further cluster of complex partial seizures
- Phrase-level spurious predictions:
  - `complex partial seizures` {CUI=C0149958; CUIPhrase=complex partial seizures; NumberOfSeizures=1} | evidence: a further cluster of complex partial seizures
- Error readout: added non-matching phrase(s).

### 063 EA0093 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'month' 12 -> '12'", "coerced_field_value: finding[0] 'year' 2015 -> '2015'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=12; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: has had no seizures since Christmas 2015
- Error readout: no strict error.

### 064 EA0096 - strict F1 0.000, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `attribute_mismatch`, `surface_match_attribute_loss`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day; TimeSince_or_TimeOfEvent=During}
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Frequent}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; FrequencyChange=Increased} | evidence: On Sunday and Monday, he was having generalised tonic clonic seizures in the night
- Phrase-level missing gold:
  - `absences` {CUI=C0563606; CUIPhrase=absences; FrequencyChange=Frequent}
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizures`: FrequencyChange: gold=None vs pred=Increased; NumberOfSeizures: gold=1 vs pred=None; NumberOfTimePeriods: gold=1 vs pred=None; TimePeriod: gold=Day vs pred=None; TimeSince_or_TimeOfEvent: gold=During vs pred=None
- Error readout: missed/renamed scored phrase(s), same phrase but wrong frequency attributes.

### 065 EA0100 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=0, actions={'remove': 2}, statuses={'diagnosis_without_frequency': 1, 'history_context_only': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 066 EA0102 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Year}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Year} | evidence: She has been seizure free for more than five years.
- Error readout: no strict error.

### 067 EA0104 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=2; strict TP/FP/FN=0/2/0; phrase TP/FP/FN=0/2/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `verification_parse_failure`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=0, actions={}, statuses={}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 3 -> '3'", "coerced_field_value: finding[1] 'age_low' 30 -> '30'", "coerced_field_value: finding[1] 'age_high' 39 -> '39'"], verification_parse=["schema_validation_error: Input should be 'frequency_rate', 'seizure_free', 'frequency_change', 'dated_count', 'last_event', 'cluster_frequency' or 'other_frequency'"], projection=["cui_projected: cui_not_mapped: 'smaller versions of the attacks'"]
- Gold:
  - none
- Predicted:
  - `smaller versions of the attacks` {NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: The smaller versions of the attacks can happen several times per week.
  - `seizure free` {AgeLower=30; AgeUnit=Year; AgeUpper=39; CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year} | evidence: The best period of seizure freedom that she has had is probably around three years of seizure freedom which she had in her early 30s.
- Phrase-level spurious predictions:
  - `smaller versions of the attacks` {NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: The smaller versions of the attacks can happen several times per week.
  - `seizure free` {AgeLower=30; AgeUnit=Year; AgeUpper=39; CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year} | evidence: The best period of seizure freedom that she has had is probably around three years of seizure freedom which she had in her early 30s.
- Error readout: added non-matching phrase(s).

### 068 EA0106 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 2 -> '2'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'focal motor seizures (left hand and arm movement)'"]
- Gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
- Predicted:
  - `focal motor seizures (left hand and arm movement)` {NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week} | evidence: focal motor seizures (left hand and arm movement) every 2 weeks
  - `Focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=Focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: Focal to bilateral convulsive seizures last event 2 years ago
- Phrase-level missing gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
- Phrase-level spurious predictions:
  - `focal motor seizures (left hand and arm movement)` {NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Week} | evidence: focal motor seizures (left hand and arm movement) every 2 weeks
- Same-phrase attribute conflicts:
  - `focal to bilateral convulsive seizures`: NumberOfTimePeriods: gold=2 vs pred=None; TimePeriod: gold=Year vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 069 EA0107 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizures; MonthDate=10; NumberOfSeizures=4; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=4} | evidence: Since last October she had 4 generalised tonic clonic seizures
- Same-phrase attribute conflicts:
  - `generalised tonic clonic seizures`: MonthDate: gold=10 vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 070 EA0108 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 3 -> '3'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'focal motor seizures with secondary generalised tonic clonic seizures'"]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=12; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased}
- Predicted:
  - `focal motor seizures with secondary generalised tonic clonic seizures` {LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: Currently his seizures occur 2 to 3 times per month.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: in his last episode, two weeks ago
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=12; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
- Phrase-level spurious predictions:
  - `focal motor seizures with secondary generalised tonic clonic seizures` {LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: Currently his seizures occur 2 to 3 times per month.
- Same-phrase attribute conflicts:
  - `seizures`: LowerNumberOfSeizures: gold=2 vs pred=None; NumberOfSeizures: gold=None vs pred=0; NumberOfTimePeriods: gold=1 vs pred=None; TimePeriod: gold=Month vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since; UpperNumberOfSeizures: gold=3 vs pred=None
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 071 EA0109 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 3 -> '3'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='focal seizures'"]
- Gold:
  - none
- Predicted:
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; FrequencyChange=Increased} | evidence: The episodes were rare in the past but have become more frequent in the last year
- Phrase-level spurious predictions:
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; FrequencyChange=Increased} | evidence: The episodes were rare in the past but have become more frequent in the last year
- Error readout: added non-matching phrase(s).

### 072 EA0110 - strict F1 0.500, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=1/1/1; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[2] 'count_low' 3 -> '3'", "coerced_field_value: finding[2] 'count_high' 5 -> '5'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
  - `seizure-cluster` {CUI=C3203523; CUIPhrase=seizure-cluster; NumberOfSeizures=1; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: Current frequency of the seizures is once or twice a month
  - `cluster of seizures` {CUI=C3203523; CUIPhrase=cluster of seizures; MonthDate=last month; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During} | evidence: last month there was a cluster of 3 in a single day
- Phrase-level missing gold:
  - `seizure-cluster` {CUI=C3203523; CUIPhrase=seizure-cluster; NumberOfSeizures=1; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
- Phrase-level spurious predictions:
  - `cluster of seizures` {CUI=C3203523; CUIPhrase=cluster of seizures; MonthDate=last month; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During} | evidence: last month there was a cluster of 3 in a single day
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 073 EA0111 - strict F1 0.667, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=1/0/1; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='tonic clonic seizures'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased} | evidence: there has been an increase in her seizures.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased}
- Error readout: missed/renamed scored phrase(s).

### 074 EA0113 - strict F1 0.500, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=1/1/1; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[0] 'age_low' 16 -> '16'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'year' 2018 -> '2018'"], verification_parse=[], projection=['format_projected: dropped_unanchored_background_rate_since', 'cui_projected: dropped_unanchored_background_rate_since']
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018}
- Predicted:
  - `seizures` {AgeLower=16; AgeUnit=Year; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has had on average one seizure a year since the age of 16
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2018} | evidence: but a total of 3 in 2018
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `seizures` {AgeLower=16; AgeUnit=Year; CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: He has had on average one seizure a year since the age of 16
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 075 EA0114 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'focal impaired awareness seizures'"]
- Gold:
  - none
- Predicted:
  - `focal impaired awareness seizures` {NumberOfSeizures=2} | evidence: a couple of focal impaired awareness seizures
- Phrase-level spurious predictions:
  - `focal impaired awareness seizures` {NumberOfSeizures=2} | evidence: a couple of focal impaired awareness seizures
- Error readout: added non-matching phrase(s).

### 076 EA0116 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=3; strict TP/FP/FN=0/3/0; phrase TP/FP/FN=0/3/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 2, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'year' 2017 -> '2017'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=2} | evidence: She has had a few episodes from sleep.
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017} | evidence: The first occurred in May 2017.
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; PointInTime=Last_Week; TimeSince_or_TimeOfEvent=Since} | evidence: The most recent episode occurred last week and was similar in nature.
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=2} | evidence: She has had a few episodes from sleep.
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017} | evidence: The first occurred in May 2017.
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; PointInTime=Last_Week; TimeSince_or_TimeOfEvent=Since} | evidence: The most recent episode occurred last week and was similar in nature.
- Error readout: added non-matching phrase(s).

### 077 EA0117 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=0; strict TP/FP/FN=0/0/1; phrase TP/FP/FN=0/0/1
- Tags: `total_miss`, `phrase_omission`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'remove': 1, 'revise': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='focal impaired awareness seizures and dissociative seizures'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
- Predicted:
  - none
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
- Error readout: missed/renamed scored phrase(s).

### 078 EA0119 - strict F1 0.000, phrase F1 0.000

- Counts: gold=4, predicted=1; strict TP/FP/FN=0/1/4; phrase TP/FP/FN=0/1/4
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'target_epileptic_seizure_frequency': 1, 'uncertain_not_scored': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: '1 seizure per week to 1 seizure every month'"]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
- Predicted:
  - `1 seizure per week to 1 seizure every month` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: Seizure type and frequency: 1 seizure per week to 1 seizure every month
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
- Phrase-level spurious predictions:
  - `1 seizure per week to 1 seizure every month` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: Seizure type and frequency: 1 seizure per week to 1 seizure every month
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 079 EA0120 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: He has not had any further seizures since his last appointment.
- Same-phrase attribute conflicts:
  - `seizures`: PointInTime: gold=LastClinic vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 080 EA0121 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=0/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=3, verified=1, actions={'keep': 1, 'remove': 2}, statuses={'target_epileptic_seizure_frequency': 1, 'uncertain_not_scored': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[2] 'count_low' 2 -> '2'", "coerced_field_value: finding[2] 'count_high' 3 -> '3'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; LowerNumberOfSeizures=0; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
- Predicted:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: The focal to bilateral convulsive seizures occur less often, perhaps up to 2 or 3 times per month.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Frequent}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; LowerNumberOfSeizures=0; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: The focal to bilateral convulsive seizures occur less often, perhaps up to 2 or 3 times per month.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 081 EA0123 - strict F1 0.000, phrase F1 0.000

- Counts: gold=3, predicted=1; strict TP/FP/FN=0/1/3; phrase TP/FP/FN=0/1/3
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'period_low' 2 -> '2'", "coerced_field_value: finding[1] 'period_high' 3 -> '3'", "coerced_field_value: finding[2] 'period_count' 4 -> '4'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='generalised tonic clonic seizures'", "dropped_evidence_not_substring: text='generalised tonic clonic seizures'"]
- Gold:
  - `generalized-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalized-tonic-clonic-seizures; FrequencyChange=Infrequent}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; LowerNumberOfTimePeriods=2; NumberOfSeizures=1; TimePeriod=Year; UpperNumberOfTimePeriods=3}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Decreased}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=4; TimePeriod=Year} | evidence: Her longest period without seizures has been 4 years.
- Phrase-level missing gold:
  - `generalized-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalized-tonic-clonic-seizures; FrequencyChange=Infrequent}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; LowerNumberOfTimePeriods=2; NumberOfSeizures=1; TimePeriod=Year; UpperNumberOfTimePeriods=3}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Decreased}
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; NumberOfTimePeriods=4; TimePeriod=Year} | evidence: Her longest period without seizures has been 4 years.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 082 EA0124 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'absence events'"]
- Gold:
  - `absence` {CUI=C0563606; CUIPhrase=absence; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: the last occurred three years ago
  - `absence events` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: These currently happen around once a week
- Phrase-level missing gold:
  - `absence` {CUI=C0563606; CUIPhrase=absence; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: the last occurred three years ago
  - `absence events` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: These currently happen around once a week
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 083 EA0125 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Increased}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures} | evidence: increasing seizures
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Increased}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures} | evidence: increasing seizures
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 084 EA0126 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=3; strict TP/FP/FN=0/3/2; phrase TP/FP/FN=0/3/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=3, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 4 -> '4'", "coerced_field_value: finding[0] 'count_high' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'drop attacks'"]
- Gold:
  - `frontal-lobe-seizure` {CUI=C0085541; CUIPhrase=frontal-lobe-seizure; LowerNumberOfSeizures=4; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=5}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year}
- Predicted:
  - `Focal frontal lobe seizures` {CUI=C0085541; CUIPhrase=Focal frontal lobe seizures; LowerNumberOfSeizures=4; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=5} | evidence: These currently occur around 4-5 times a month.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: these haven't happened for several years now.
  - `drop attacks` {NumberOfSeizures=0} | evidence: they haven't happened in adulthood.
- Phrase-level missing gold:
  - `frontal-lobe-seizure` {CUI=C0085541; CUIPhrase=frontal-lobe-seizure; LowerNumberOfSeizures=4; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=5}
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `Focal frontal lobe seizures` {CUI=C0085541; CUIPhrase=Focal frontal lobe seizures; LowerNumberOfSeizures=4; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=5} | evidence: These currently occur around 4-5 times a month.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: these haven't happened for several years now.
  - `drop attacks` {NumberOfSeizures=0} | evidence: they haven't happened in adulthood.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 085 EA0127 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'seizures free'"]
- Gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; NumberOfSeizures=0; PointInTime=LastClinic}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=2; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2005}
- Predicted:
  - `seizures free` {NumberOfSeizures=0} | evidence: he remains seizures free
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: His last seizure was in February 2005
- Phrase-level missing gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; NumberOfSeizures=0; PointInTime=LastClinic}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=2; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2005}
- Phrase-level spurious predictions:
  - `seizures free` {NumberOfSeizures=0} | evidence: he remains seizures free
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: His last seizure was in February 2005
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 086 EA0128 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=0/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'period_count' 7 -> '7'"], verification_parse=[], projection=[]
- Gold:
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Same}
  - `generalized-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalized-tonic-clonic-seizures; NumberOfSeizures=0; NumberOfTimePeriods=7; TimePeriod=Year}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; NumberOfTimePeriods=7; TimePeriod=Year} | evidence: having been seven years without any tonic clonic
- Phrase-level missing gold:
  - `myoclonic-jerks` {CUI=C0027066; CUIPhrase=myoclonic-jerks; FrequencyChange=Same}
  - `generalized-tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=generalized-tonic-clonic-seizures; NumberOfSeizures=0; NumberOfTimePeriods=7; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=0; NumberOfTimePeriods=7; TimePeriod=Year} | evidence: having been seven years without any tonic clonic
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 087 EA0129 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week; UpperNumberOfSeizures=2} | evidence: He was having seizures with a frequency of one to two per week at the onset.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; PointInTime=DrugChange; TimePeriod=Week} | evidence: During the time that he has been on lamotrigine he has continued to have seizures around once per week.
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week; UpperNumberOfSeizures=2} | evidence: He was having seizures with a frequency of one to two per week at the onset.
- Same-phrase attribute conflicts:
  - `seizures`: LowerNumberOfSeizures: gold=None vs pred=1; NumberOfSeizures: gold=1 vs pred=None; UpperNumberOfSeizures: gold=None vs pred=2
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 088 EA0131 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased; PointInTime=Last_Year; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; FrequencyChange=Frequent} | evidence: quite a number of generalised tonic clonic seizures
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased} | evidence: seizures have been worse in the last year
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; FrequencyChange=Frequent} | evidence: quite a number of generalised tonic clonic seizures
- Same-phrase attribute conflicts:
  - `seizures`: PointInTime: gold=Last_Year vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 089 EA0132 - strict F1 0.667, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=1/1/0; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'period_low' 1 -> '1'", "coerced_field_value: finding[1] 'period_high' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month}
- Predicted:
  - `Focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=Focal seizures with altered awareness; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: Focal seizures with altered awareness, several per month
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: They are happening weekly.
- Phrase-level spurious predictions:
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: They are happening weekly.
- Error readout: added non-matching phrase(s).

### 090 EA0133 - strict F1 0.400, phrase F1 0.400

- Counts: gold=2, predicted=3; strict TP/FP/FN=1/2/1; phrase TP/FP/FN=1/2/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=4, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=2
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 3 -> '3'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'year' 2015 -> '2015'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'Focal motor seizures, (left arm jerks)'", "dropped_evidence_not_substring: text='focal seizures'", "cui_projected: cui_not_mapped: 'convulsive epileptic seizure'"]
- Gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
  - `focal-to-bilateral-convulsive-seizures` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015}
- Predicted:
  - `Focal motor seizures, (left arm jerks)` {LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: Focal motor seizures, (left arm jerks) 2-3 per month
  - `Focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=Focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: Focal to bilateral convulsive seizures, last event 2015
  - `convulsive epileptic seizure` {NumberOfSeizures=0} | evidence: he had a convulsive epileptic seizure for the first time
- Phrase-level missing gold:
  - `focal-motor-seizures` {CUI=C0016399; CUIPhrase=focal-motor-seizures; LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3}
- Phrase-level spurious predictions:
  - `Focal motor seizures, (left arm jerks)` {LowerNumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=3} | evidence: Focal motor seizures, (left arm jerks) 2-3 per month
  - `convulsive epileptic seizure` {NumberOfSeizures=0} | evidence: he had a convulsive epileptic seizure for the first time
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 091 EA0135 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count_low' 6 -> '6'", "coerced_field_value: finding[1] 'count_high' 9 -> '9'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='seizures'"]
- Gold:
  - `cluster-of-seizures` {CUI=C3203523; CUIPhrase=cluster-of-seizures; NumberOfSeizures=1; NumberOfTimePeriods=6; TimePeriod=Month; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `cluster of seizures` {CUI=C3203523; CUIPhrase=cluster of seizures} | evidence: Mr Francis had a cluster of seizures over the weekend
- Same-phrase attribute conflicts:
  - `cluster of seizures`: NumberOfSeizures: gold=1 vs pred=None; NumberOfTimePeriods: gold=6 vs pred=None; TimePeriod: gold=Month vs pred=None; TimeSince_or_TimeOfEvent: gold=During vs pred=None
- Error readout: same phrase but wrong frequency attributes.

### 092 EA0136 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1, 'revise': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'count' 2 -> '2'", "coerced_field_value: finding[2] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Same}
  - `generalised-convulsions` {CUI=C0234533; CUIPhrase=generalised-convulsions; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
  - `generalised-seizure` {CUI=C0234533; CUIPhrase=generalised-seizure; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Year}
- Predicted:
  - `generalised convulsions` {CUI=C0234533; CUIPhrase=generalised convulsions; NumberOfSeizures=0; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since} | evidence: He has not had any generalised convulsions now for several years.
  - `generalised seizures` {CUI=C0234533; CUIPhrase=generalised seizures; NumberOfSeizures=0; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since} | evidence: They have not happen now for at least 5 years.
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Same}
  - `generalised-seizure` {CUI=C0234533; CUIPhrase=generalised-seizure; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `generalised seizures` {CUI=C0234533; CUIPhrase=generalised seizures; NumberOfSeizures=0; TimePeriod=Year; TimeSince_or_TimeOfEvent=Since} | evidence: They have not happen now for at least 5 years.
- Same-phrase attribute conflicts:
  - `generalised convulsions`: NumberOfTimePeriods: gold=3 vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 093 EA0137 - strict F1 0.500, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=1/1/1; phrase TP/FP/FN=2/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=2, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["format_projected: dropped_unmapped_point_in_time: 'about 2 months ago'", "cui_projected: dropped_unmapped_point_in_time: 'about 2 months ago'"]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; NumberOfTimePeriods=2; TimePeriod=Month}
  - `secondary-generalised-seizures` {CUI=C0270838; CUIPhrase=secondary-generalised-seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year}
- Predicted:
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: She continues to have around 2 secondary generalised seizures per year.
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=During} | evidence: Her seizure was about 2 months ago.
- Same-phrase attribute conflicts:
  - `seizure`: NumberOfTimePeriods: gold=2 vs pred=None; TimePeriod: gold=Month vs pred=None; TimeSince_or_TimeOfEvent: gold=None vs pred=During
- Error readout: same phrase but wrong frequency attributes.

### 094 EA0139 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=0/2/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`
- Verifier: raw=1, verified=2, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=1
- Warnings: parse=[], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'an episode in September'"]
- Gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=2; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures} | evidence: he has had further generalised tonic clonic seizures since I last saw him, an episode in September was severe and was associated with a head injury.
  - `an episode in September` {MonthDate=9; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: an episode in September was severe and was associated with a head injury.
- Phrase-level missing gold:
  - `generalised` {CUI=C0494475; CUIPhrase=generalised; NumberOfSeizures=2; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures} | evidence: he has had further generalised tonic clonic seizures since I last saw him, an episode in September was severe and was associated with a head injury.
  - `an episode in September` {MonthDate=9; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: an episode in September was severe and was associated with a head injury.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 095 EA0141 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=2, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'"], verification_parse=[], projection=["dropped_evidence_not_substring: text='seizure'"]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3} | evidence: at least three seizures he has epilepsy
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=3} | evidence: at least three seizures he has epilepsy
- Error readout: added non-matching phrase(s).

### 096 EA0142 - strict F1 0.000, phrase F1 0.667

- Counts: gold=1, predicted=2; strict TP/FP/FN=0/2/1; phrase TP/FP/FN=1/1/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'day' 6 -> '6'"], verification_parse=[], projection=["format_projected: dropped_unmapped_time_relation: 'until'", "cui_projected: dropped_unmapped_time_relation: 'until'", "format_projected: dropped_unmapped_point_in_time: 'Feburary 6th'", "cui_projected: dropped_unmapped_point_in_time: 'Feburary 6th'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; DayDate=6; MonthDate=2; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=2; MonthDate=2; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4} | evidence: Up until February this year he was having around 3 seizures per month.
  - `seizure freedom` {CUI=C1299590; CUIPhrase=seizure freedom; DayDate=6; MonthDate=2; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: since Feburary 6th he has not had any more seizures. This is a long period of seizure freedom for him
- Phrase-level spurious predictions:
  - `seizure freedom` {CUI=C1299590; CUIPhrase=seizure freedom; DayDate=6; MonthDate=2; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: since Feburary 6th he has not had any more seizures. This is a long period of seizure freedom for him
- Same-phrase attribute conflicts:
  - `seizures`: DayDate: gold=6 vs pred=None; LowerNumberOfSeizures: gold=None vs pred=2; NumberOfSeizures: gold=0 vs pred=None; NumberOfTimePeriods: gold=None vs pred=1; TimePeriod: gold=None vs pred=Month; TimeSince_or_TimeOfEvent: gold=Since vs pred=None; UpperNumberOfSeizures: gold=None vs pred=4
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 097 EA0143 - strict F1 0.000, phrase F1 0.333

- Counts: gold=2, predicted=4; strict TP/FP/FN=0/4/2; phrase TP/FP/FN=1/3/1
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=4, verified=4, actions={'keep': 4}, statuses={'target_epileptic_seizure_frequency': 4}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'count' 1 -> '1'", "coerced_field_value: finding[2] 'age_low' 22 -> '22'", "coerced_field_value: finding[2] 'age_high' 22 -> '22'", "coerced_field_value: finding[3] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=0; NumberOfTimePeriods=5; TimePeriod=Year}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: These events, which are focal seizures with altered awareness, used to happen weekly but her last event was more than five years ago.
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: but her last event was more than five years ago.
  - `secondarily generalised seizures` {AgeLower=22; AgeUnit=Year; AgeUpper=22; CUI=C0270838; CUIPhrase=secondarily generalised seizures; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During} | evidence: She has only every had one secondarily generalised seizures which happend when she was 22, the morning after a night out.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: She has not had any seizure as a result of this.
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: These events, which are focal seizures with altered awareness, used to happen weekly but her last event was more than five years ago.
  - `secondarily generalised seizures` {AgeLower=22; AgeUnit=Year; AgeUpper=22; CUI=C0270838; CUIPhrase=secondarily generalised seizures; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During} | evidence: She has only every had one secondarily generalised seizures which happend when she was 22, the morning after a night out.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: She has not had any seizure as a result of this.
- Same-phrase attribute conflicts:
  - `focal seizures with altered awareness`: NumberOfSeizures: gold=0 vs pred=1; NumberOfTimePeriods: gold=5 vs pred=1; TimePeriod: gold=Year vs pred=Week
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 098 EA0146 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 6 -> '6'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'grand mal episodes'"]
- Gold:
  - none
- Predicted:
  - `grand mal episodes` {NumberOfSeizures=6; NumberOfTimePeriods=1; TimePeriod=Year; TimeSince_or_TimeOfEvent=During} | evidence: He has had around 6 of these during the last year.
- Phrase-level spurious predictions:
  - `grand mal episodes` {NumberOfSeizures=6; NumberOfTimePeriods=1; TimePeriod=Year; TimeSince_or_TimeOfEvent=During} | evidence: He has had around 6 of these during the last year.
- Error readout: added non-matching phrase(s).

### 099 EA0148 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2} | evidence: he has had 2 seizures
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2} | evidence: he has had 2 seizures
- Error readout: added non-matching phrase(s).

### 100 EA0149 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 4 -> '4'", "coerced_field_value: finding[0] 'count_high' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 101 EA0150 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count_low' 1 -> '1'", "coerced_field_value: finding[1] 'count_high' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `secondary-generalised-seizures` {CUI=C0270838; CUIPhrase=secondary-generalised-seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=2}
  - `complex-partial-seizures` {CUI=C0149958; CUIPhrase=complex-partial-seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
- Predicted:
  - `complex partial seizures` {CUI=C0149958; CUIPhrase=complex partial seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: The complex partial seizures are now happening once a month
  - `secondary generalised seizures` {CUI=C0270838; CUIPhrase=secondary generalised seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=2} | evidence: he has around 1-2 secondary generalised seizures per year
- Error readout: no strict error.

### 102 EA0151 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'target_epileptic_seizure_frequency': 1, 'uncertain_not_scored': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 5 -> '5'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'cluster of 5 seizures'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=5; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `cluster of 5 seizures` {NumberOfSeizures=5} | evidence: Last month, Joan had a cluster of 5 seizures within two days.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=5; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
- Phrase-level spurious predictions:
  - `cluster of 5 seizures` {NumberOfSeizures=5} | evidence: Last month, Joan had a cluster of 5 seizures within two days.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 103 EA0152 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=[], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'Complex partial seizures (deja-vu, automatism)'"]
- Gold:
  - `secondary-generalised-seizure` {CUI=C0270838; CUIPhrase=secondary-generalised-seizure; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=4}
  - `complex-partial-seizure` {CUI=C0149958; CUIPhrase=complex-partial-seizure; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
- Predicted:
  - `Complex partial seizures (deja-vu, automatism)` {LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: Complex partial seizures (deja-vu, automatism) 1-2 per month
  - `Secondary generalised seizures` {CUI=C0270838; CUIPhrase=Secondary generalised seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=4} | evidence: Secondary generalised seizures 3-4 per year
- Phrase-level missing gold:
  - `secondary-generalised-seizure` {CUI=C0270838; CUIPhrase=secondary-generalised-seizure; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=4}
  - `complex-partial-seizure` {CUI=C0149958; CUIPhrase=complex-partial-seizure; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
- Phrase-level spurious predictions:
  - `Complex partial seizures (deja-vu, automatism)` {LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: Complex partial seizures (deja-vu, automatism) 1-2 per month
  - `Secondary generalised seizures` {CUI=C0270838; CUIPhrase=Secondary generalised seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=4} | evidence: Secondary generalised seizures 3-4 per year
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 104 EA0153 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: They happen about 1-2 per month and are always the same.
- Phrase-level spurious predictions:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: They happen about 1-2 per month and are always the same.
- Error readout: added non-matching phrase(s).

### 105 EA0154 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 4 -> '4'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=4; TimePeriod=Week}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=4; TimePeriod=Week} | evidence: the seizure frequency is roughly every 4 weeks at present
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=4; TimePeriod=Week}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=4; TimePeriod=Week} | evidence: the seizure frequency is roughly every 4 weeks at present
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 106 EA0156 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; MonthDate=7; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; MonthDate=7; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: She has remained seizure free since the beginning of July.
- Error readout: no strict error.

### 107 EA0157 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `verification_parse_failure`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={}, statuses={}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 3 -> '3'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=["invalid_json: Expecting ',' delimiter"], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week; UpperNumberOfSeizures=4}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week; UpperNumberOfSeizures=4} | evidence: she is having between 3 and 4 per week
- Error readout: no strict error.

### 108 EA0158 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 1, 'remove': 1, 'revise': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 3 -> '3'", "coerced_field_value: finding[0] 'count_high' 4 -> '4'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Week}
  - `generalised-seizure` {CUI=C0234533; CUIPhrase=generalised-seizure; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4}
- Predicted:
  - `generalised seizures` {CUI=C0234533; CUIPhrase=generalised seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4} | evidence: She gets around 3-4 generalised seizures per month, usually when asleep.
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: Jennifer also gets focal seizures with altered awareness probably several times per week.
- Phrase-level missing gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Week}
  - `generalised-seizure` {CUI=C0234533; CUIPhrase=generalised-seizure; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4}
- Phrase-level spurious predictions:
  - `generalised seizures` {CUI=C0234533; CUIPhrase=generalised seizures; LowerNumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=4} | evidence: She gets around 3-4 generalised seizures per month, usually when asleep.
  - `focal seizures` {CUI=C0751495; CUIPhrase=focal seizures; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: Jennifer also gets focal seizures with altered awareness probably several times per week.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 109 EA0160 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 110 EA0161 - strict F1 0.000, phrase F1 0.333

- Counts: gold=4, predicted=2; strict TP/FP/FN=0/2/4; phrase TP/FP/FN=1/1/3
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'target_epileptic_seizure_frequency': 2, 'uncertain_not_scored': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_low' 2 -> '2'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'absence seizures'"]
- Gold:
  - `tonic-clonic-seizures` {CUI=C0494475; CUIPhrase=tonic-clonic-seizures; FrequencyChange=Frequent; NumberOfTimePeriods=2; TimePeriod=Year}
  - `absences` {CUI=C0563606; CUIPhrase=absences; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
  - `tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=tonic-clonic-seizure; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Month}
- Predicted:
  - `absence seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: The absences continue to happen maybe every week
  - `tonic clonic seizures` {CUI=C0494475; CUIPhrase=tonic clonic seizures; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Month} | evidence: She has had relatively frequent tonic clonic seizures in the last few years, perhaps every two months or so.
- Phrase-level missing gold:
  - `absences` {CUI=C0563606; CUIPhrase=absences; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
  - `tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=tonic-clonic-seizure; NumberOfSeizures=1; NumberOfTimePeriods=2; TimePeriod=Month}
- Phrase-level spurious predictions:
  - `absence seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: The absences continue to happen maybe every week
- Same-phrase attribute conflicts:
  - `tonic clonic seizures`: FrequencyChange: gold=Frequent vs pred=None; NumberOfSeizures: gold=None vs pred=1; TimePeriod: gold=Year vs pred=Month
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 111 EA0162 - strict F1 0.000, phrase F1 0.500

- Counts: gold=1, predicted=3; strict TP/FP/FN=0/3/1; phrase TP/FP/FN=1/2/0
- Tags: `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'", "coerced_field_value: finding[0] 'year' 2006 -> '2006'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'year' 2006 -> '2006'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=12; NumberOfSeizures=3; TimePeriod=Day; TimeSince_or_TimeOfEvent=During; YearDate=2006} | evidence: he did have a cluster of three seizures in a 24-hr period in Devember
  - `generalised tonic-clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic-clonic seizures; MonthDate=12; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2006} | evidence: These were generalised tonic-clonic seizures.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0} | evidence: he has not had any more seizures
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=12; NumberOfSeizures=3; TimePeriod=Day; TimeSince_or_TimeOfEvent=During; YearDate=2006} | evidence: he did have a cluster of three seizures in a 24-hr period in Devember
  - `generalised tonic-clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic-clonic seizures; MonthDate=12; NumberOfSeizures=3; TimeSince_or_TimeOfEvent=During; YearDate=2006} | evidence: These were generalised tonic-clonic seizures.
- Same-phrase attribute conflicts:
  - `seizures`: MonthDate: gold=None vs pred=12; NumberOfSeizures: gold=0 vs pred=3; PointInTime: gold=LastClinic vs pred=None; TimePeriod: gold=None vs pred=Day; TimeSince_or_TimeOfEvent: gold=Since vs pred=During; YearDate: gold=None vs pred=2006
- Error readout: added non-matching phrase(s), same phrase but wrong frequency attributes.

### 112 EA0163 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'period_count' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Week}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Week} | evidence: He hasn't had any seizures now for around three weeks which is good news.
- Error readout: no strict error.

### 113 EA0164 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 114 EA0166 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 115 EA0167 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=5; PointInTime=Last_Year; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=5; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: he has had around 5 seizures in the last year
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=5; PointInTime=Last_Year; TimeSince_or_TimeOfEvent=During}
- Phrase-level spurious predictions:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=5; NumberOfTimePeriods=1; TimePeriod=Year} | evidence: he has had around 5 seizures in the last year
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 116 EA0168 - strict F1 0.000, phrase F1 0.400

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=1/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `seizure-free` {CUI=C1299590; CUIPhrase=seizure-free; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=11; NumberOfSeizures=0; YearDate=2015}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: he remains seizrue free which is good news.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: His last seizure was Novemebr 2015.
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=11; NumberOfSeizures=0; YearDate=2015}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: His last seizure was Novemebr 2015.
- Same-phrase attribute conflicts:
  - `seizure free`: PointInTime: gold=LastClinic vs pred=None; TimeSince_or_TimeOfEvent: gold=Since vs pred=None
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 117 EA0169 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `verification_parse_failure`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=0, actions={}, statuses={}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count_low' 10 -> '10'", "coerced_field_value: finding[1] 'count_high' 15 -> '15'"], verification_parse=["invalid_json: Expecting ',' delimiter"], projection=["cui_projected: cui_not_mapped: 'focal dyscognitive seizures'", "cui_projected: cui_not_mapped: 'these seizures'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=10; NumberOfTimePeriods=2; TimePeriod=days; UpperNumberOfSeizures=15}
  - `dyscognitive-seizures` {CUI=C0270834; CUIPhrase=dyscognitive-seizures; FrequencyChange=Frequent}
- Predicted:
  - `focal dyscognitive seizures` {FrequencyChange=Frequent} | evidence: She gets frequent focal dyscognitive seizures in clusters.
  - `these seizures` {LowerNumberOfSeizures=10; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=15} | evidence: Last week she had around 10-15 of these seizures over 2 days.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=10; NumberOfTimePeriods=2; TimePeriod=days; UpperNumberOfSeizures=15}
  - `dyscognitive-seizures` {CUI=C0270834; CUIPhrase=dyscognitive-seizures; FrequencyChange=Frequent}
- Phrase-level spurious predictions:
  - `focal dyscognitive seizures` {FrequencyChange=Frequent} | evidence: She gets frequent focal dyscognitive seizures in clusters.
  - `these seizures` {LowerNumberOfSeizures=10; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=15} | evidence: Last week she had around 10-15 of these seizures over 2 days.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 118 EA0171 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'diagnosis_without_frequency': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: he has not had any further episdoes
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=DrugChange} | evidence: he has not had any further episdoes
- Error readout: added non-matching phrase(s).

### 119 EA0172 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=1; strict TP/FP/FN=0/1/0; phrase TP/FP/FN=0/1/0
- Tags: `over_extraction_no_gold`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'nocturnal seizures'"]
- Gold:
  - none
- Predicted:
  - `nocturnal seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day} | evidence: He tells me that they are happening most days and happen during the night.
- Phrase-level spurious predictions:
  - `nocturnal seizures` {NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day} | evidence: He tells me that they are happening most days and happen during the night.
- Error readout: added non-matching phrase(s).

### 120 EA0173 - strict F1 0.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=1/0/0
- Tags: `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'day' 15 -> '15'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; DayDate=15; MonthDate=4; NumberOfSeizures=0}
- Predicted:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; DayDate=15; MonthDate=4; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: her last seizure was on the 15th April in her home
- Same-phrase attribute conflicts:
  - `seizure`: TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: same phrase but wrong frequency attributes.

### 121 EA0175 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 1 -> '1'", "coerced_field_value: finding[0] 'period_high' 2 -> '2'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=1; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=2}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfTimePeriods=1; NumberOfSeizures=1; TimePeriod=Week; UpperNumberOfTimePeriods=2} | evidence: Her seizures are happening every 1-2 weeks.
- Error readout: no strict error.

### 122 EA0176 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; FrequencyChange=Same; NumberOfSeizures=0}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: she remains seizure free
- Phrase-level missing gold:
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; FrequencyChange=Same; NumberOfSeizures=0}
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: she remains seizure free
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 123 EA0178 - strict F1 0.000, phrase F1 0.667

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=1/0/1
- Tags: `phrase_omission`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 5 -> '5'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=5; TimePeriod=Month}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Decreased; PointInTime=DrugChange; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=5; TimePeriod=Month; TimeSince_or_TimeOfEvent=Since} | evidence: Hannah thinks that she has had 2 seizures in the last five months which is good for her.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=5; TimePeriod=Month}
- Same-phrase attribute conflicts:
  - `seizures`: TimeSince_or_TimeOfEvent: gold=None vs pred=Since
- Error readout: missed/renamed scored phrase(s), same phrase but wrong frequency attributes.

### 124 EA0179 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 125 EA0180 - strict F1 0.000, phrase F1 0.000

- Counts: gold=3, predicted=2; strict TP/FP/FN=0/2/3; phrase TP/FP/FN=0/2/3
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'year' 2015 -> '2015'"], verification_parse=[], projection=[]
- Gold:
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; FrequencyChange=Same; NumberOfSeizures=0}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015}
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; NumberOfSeizures=0}
- Predicted:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: he remains seizure free
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: His last seizure was Novemebr 2015
- Phrase-level missing gold:
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; FrequencyChange=Same; NumberOfSeizures=0}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015}
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; NumberOfSeizures=0}
- Phrase-level spurious predictions:
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0} | evidence: he remains seizure free
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; MonthDate=11; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2015} | evidence: His last seizure was Novemebr 2015
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 126 EA0181 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=0/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `verification_parse_failure`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=0, actions={}, statuses={}, additions=0
- Warnings: parse=["coerced_field_value: finding[1] 'count_low' 10 -> '10'", "coerced_field_value: finding[1] 'count_high' 15 -> '15'"], verification_parse=['schema_validation_error: Input should be a valid integer'], projection=["cui_projected: cui_not_mapped: 'focal dyscognitive seizures'", "cui_projected: cui_not_mapped: 'these seizures'"]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=10; NumberOfTimePeriods=2; TimePeriod=Day; UpperNumberOfSeizures=15}
  - `dyscognitive-seizures` {CUI=C0270834; CUIPhrase=dyscognitive-seizures; FrequencyChange=Frequent}
- Predicted:
  - `focal dyscognitive seizures` {FrequencyChange=Frequent} | evidence: She gets frequent focal dyscognitive seizures in clusters.
  - `these seizures` {LowerNumberOfSeizures=10; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=15} | evidence: Last week she had around 10-15 of these seizures over 2 days.
- Phrase-level missing gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=10; NumberOfTimePeriods=2; TimePeriod=Day; UpperNumberOfSeizures=15}
  - `dyscognitive-seizures` {CUI=C0270834; CUIPhrase=dyscognitive-seizures; FrequencyChange=Frequent}
- Phrase-level spurious predictions:
  - `focal dyscognitive seizures` {FrequencyChange=Frequent} | evidence: She gets frequent focal dyscognitive seizures in clusters.
  - `these seizures` {LowerNumberOfSeizures=10; TimeSince_or_TimeOfEvent=During; UpperNumberOfSeizures=15} | evidence: Last week she had around 10-15 of these seizures over 2 days.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 127 EA0182 - strict F1 0.000, phrase F1 0.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=0/1/1; phrase TP/FP/FN=0/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=1, verified=1, actions={'keep': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_low' 3 -> '3'", "coerced_field_value: finding[0] 'period_high' 3 -> '3'"], verification_parse=[], projection=["cui_projected: cui_not_mapped: 'single seizure'"]
- Gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Week}
- Predicted:
  - `single seizure` {NumberOfSeizures=1; NumberOfTimePeriods=3; PointInTime=LastClinic; TimePeriod=Week; TimeSince_or_TimeOfEvent=Since} | evidence: She reports having a single seizure some 3 weeks ago.
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Week}
- Phrase-level spurious predictions:
  - `single seizure` {NumberOfSeizures=1; NumberOfTimePeriods=3; PointInTime=LastClinic; TimePeriod=Week; TimeSince_or_TimeOfEvent=Since} | evidence: She reports having a single seizure some 3 weeks ago.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 128 EA0183 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 4 -> '4'", "coerced_field_value: finding[0] 'count_high' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 129 EA0184 - strict F1 0.000, phrase F1 0.000

- Counts: gold=2, predicted=1; strict TP/FP/FN=0/1/2; phrase TP/FP/FN=0/1/2
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'non_target_episode': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=3; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `typical-absences` {CUI=C4316903; CUIPhrase=typical-absences; FrequencyChange=Same; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=3} | evidence: three generalised tonic clonic seizures
- Phrase-level missing gold:
  - `generalised-tonic-clonic-seizure` {CUI=C0494475; CUIPhrase=generalised-tonic-clonic-seizure; NumberOfSeizures=3; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
  - `typical-absences` {CUI=C4316903; CUIPhrase=typical-absences; FrequencyChange=Same; PointInTime=LastClinic; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `generalised tonic clonic seizures` {CUI=C0494475; CUIPhrase=generalised tonic clonic seizures; NumberOfSeizures=3} | evidence: three generalised tonic clonic seizures
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 130 EA0185 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'non_target_episode': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 4 -> '4'", "coerced_field_value: finding[0] 'count_high' 5 -> '5'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 131 EA0186 - strict F1 0.000, phrase F1 0.000

- Counts: gold=3, predicted=3; strict TP/FP/FN=0/3/3; phrase TP/FP/FN=0/3/3
- Tags: `phrase_omission`, `phrase_spurious`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'count' 1 -> '1'"], verification_parse=[], projection=["format_projected: dropped_unmapped_point_in_time: '10 months ago'", "cui_projected: dropped_unmapped_point_in_time: '10 months ago'"]
- Gold:
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
  - `focal` {CUI=C0016399; CUIPhrase=focal; NumberOfSeizures=0; NumberOfTimePeriods=10; TimePeriod=Month}
- Predicted:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=Since} | evidence: I think therefore that this was a focal to bilateral convulsive seizures.
  - `focal motor seizures` {CUI=C0016399; CUIPhrase=focal motor seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: The last event was probably 10 months ago.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017} | evidence: He has had one previous focal to bilateral convulsive seizure at the time of diagnosis of his epilepsy in May 2017.
- Phrase-level missing gold:
  - `focal-to-bilateral-convulsive-seizure` {CUI=C0877017; CUIPhrase=focal-to-bilateral-convulsive-seizure; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=During}
  - `focal` {CUI=C0016399; CUIPhrase=focal; NumberOfSeizures=0; NumberOfTimePeriods=10; TimePeriod=Month}
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; PointInTime=Last_Month; TimeSince_or_TimeOfEvent=Since} | evidence: I think therefore that this was a focal to bilateral convulsive seizures.
  - `focal motor seizures` {CUI=C0016399; CUIPhrase=focal motor seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: The last event was probably 10 months ago.
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; MonthDate=5; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During; YearDate=2017} | evidence: He has had one previous focal to bilateral convulsive seizure at the time of diagnosis of his epilepsy in May 2017.
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 132 EA0188 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 1 -> '1'", "coerced_field_value: finding[1] 'period_low' 1 -> '1'", "coerced_field_value: finding[1] 'period_high' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `secondary-generalised-seizure` {CUI=C0270838; CUIPhrase=secondary-generalised-seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day}
- Predicted:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Day} | evidence: Currently she is getting around 1 seizure per day.
  - `secondary generalised seizure` {CUI=C0270838; CUIPhrase=secondary generalised seizure; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: About once a month she will have a secondary generalised seizure which start like her normal seizure but then will progress to involve loss of consciousness with limb shaking.
- Error readout: no strict error.

### 133 EA0189 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=0, verified=0, actions={}, statuses={}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

### 134 EA0190 - strict F1 0.333, phrase F1 0.333

- Counts: gold=3, predicted=3; strict TP/FP/FN=1/2/2; phrase TP/FP/FN=1/2/2
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=3, verified=3, actions={'keep': 3}, statuses={'target_epileptic_seizure_frequency': 3}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'", "coerced_field_value: finding[2] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `focal-seizures-with-altered-awareness` {CUI=C0270834; CUIPhrase=focal-seizures-with-altered-awareness; Certainty=5; Negation=Affirmed; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018}
  - `focal` {CUI=C0877017; CUIPhrase=focal; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018}
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `focal seizures with altered awareness` {CUI=C0270834; CUIPhrase=focal seizures with altered awareness; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: focal seizures with altered awareness (deja-vu), last event 2018
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: focal to bilateral convulsive seizures, last event 2018
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; PointInTime=Surgery} | evidence: he remains seizure free after his surgery
- Phrase-level missing gold:
  - `focal` {CUI=C0877017; CUIPhrase=focal; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018}
  - `seizure` {CUI=C1299590; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `focal to bilateral convulsive seizures` {CUI=C0877017; CUIPhrase=focal to bilateral convulsive seizures; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since; YearDate=2018} | evidence: focal to bilateral convulsive seizures, last event 2018
  - `seizure free` {CUI=C1299590; CUIPhrase=seizure free; NumberOfSeizures=0; PointInTime=Surgery} | evidence: he remains seizure free after his surgery
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 135 EA0191 - strict F1 0.500, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=1/1/1; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 2}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[1] 'count' 0 -> '0'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since} | evidence: No events since surgery
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since} | evidence: Gillian has had no further seizures since her surgery
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; PointInTime=Surgery; TimeSince_or_TimeOfEvent=Since} | evidence: No events since surgery
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s).

### 136 EA0195 - strict F1 0.000, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `first_pass_format_coercion`
- Verifier: raw=1, verified=2, actions={'revise': 1}, statuses={'target_epileptic_seizure_frequency': 1}, additions=1
- Warnings: parse=["coerced_field_value: finding[0] 'count' 0 -> '0'", "coerced_field_value: finding[0] 'period_count' 3 -> '3'"], verification_parse=[], projection=[]
- Gold:
  - `seizure-freedom` {CUI=C1299590; CUIPhrase=seizure-freedom; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; DayDate=2; MonthDate=11; NumberOfSeizures=1; TimeSince_or_TimeOfEvent=During}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year} | evidence: remained seizure free for three years
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; DayDate=2nd november; NumberOfSeizures=0; TimeSince_or_TimeOfEvent=Since} | evidence: had another seizure whilst he was asleep on the 2nd November
- Phrase-level missing gold:
  - `seizure-freedom` {CUI=C1299590; CUIPhrase=seizure-freedom; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=0; NumberOfTimePeriods=3; TimePeriod=Year} | evidence: remained seizure free for three years
- Same-phrase attribute conflicts:
  - `seizure`: DayDate: gold=2 vs pred=2nd november; MonthDate: gold=11 vs pred=None; NumberOfSeizures: gold=1 vs pred=0; TimeSince_or_TimeOfEvent: gold=During vs pred=Since
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 137 EA0197 - strict F1 1.000, phrase F1 1.000

- Counts: gold=2, predicted=2; strict TP/FP/FN=2/0/0; phrase TP/FP/FN=2/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=3, verified=2, actions={'keep': 2, 'remove': 1}, statuses={'target_epileptic_seizure_frequency': 2, 'uncertain_not_scored': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 1 -> '1'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count_low' 1 -> '1'", "coerced_field_value: finding[1] 'count_high' 2 -> '2'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=2}
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Year; UpperNumberOfSeizures=2} | evidence: His baseline has been around one or two seizures per year.
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; LowerNumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month; UpperNumberOfSeizures=2} | evidence: he is having one or two seizures per month.
- Error readout: no strict error.

### 138 EA0198 - strict F1 0.000, phrase F1 0.500

- Counts: gold=2, predicted=2; strict TP/FP/FN=0/2/2; phrase TP/FP/FN=1/1/1
- Tags: `phrase_omission`, `phrase_spurious`, `attribute_mismatch`, `surface_match_attribute_loss`, `projection_warning`, `first_pass_format_coercion`
- Verifier: raw=2, verified=2, actions={'keep': 1, 'revise': 1}, statuses={'target_epileptic_seizure_frequency': 2}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count' 1 -> '1'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=['format_projected: dropped_unanchored_background_rate_since', 'cui_projected: dropped_unanchored_background_rate_since']
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased}
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: She has been having around one seizure per month
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; FrequencyChange=Increased; MonthDate=4; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week} | evidence: since April she has been having several per week
- Phrase-level missing gold:
  - `seizure` {CUI=C0036572; CUIPhrase=seizure; NumberOfSeizures=3; NumberOfTimePeriods=1; TimePeriod=Week}
- Phrase-level spurious predictions:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=1; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: She has been having around one seizure per month
- Same-phrase attribute conflicts:
  - `seizures`: FrequencyChange: gold=Increased vs pred=None; NumberOfSeizures: gold=None vs pred=1; NumberOfTimePeriods: gold=None vs pred=1; TimePeriod: gold=None vs pred=Month
- Error readout: missed/renamed scored phrase(s), added non-matching phrase(s), same phrase but wrong frequency attributes.

### 139 EA0199 - strict F1 1.000, phrase F1 1.000

- Counts: gold=1, predicted=1; strict TP/FP/FN=1/0/0; phrase TP/FP/FN=1/0/0
- Tags: `strict_correct`, `first_pass_format_coercion`
- Verifier: raw=2, verified=1, actions={'keep': 1, 'remove': 1}, statuses={'history_context_only': 1, 'target_epileptic_seizure_frequency': 1}, additions=0
- Warnings: parse=["coerced_field_value: finding[0] 'count_low' 2 -> '2'", "coerced_field_value: finding[0] 'count_high' 2 -> '2'", "coerced_field_value: finding[0] 'period_count' 1 -> '1'", "coerced_field_value: finding[1] 'count' 3 -> '3'", "coerced_field_value: finding[1] 'period_count' 1 -> '1'"], verification_parse=[], projection=[]
- Gold:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month}
- Predicted:
  - `seizures` {CUI=C0036572; CUIPhrase=seizures; NumberOfSeizures=2; NumberOfTimePeriods=1; TimePeriod=Month} | evidence: around 2 seizures per month at the moment
- Error readout: no strict error.

### 140 EA0200 - strict F1 0.000, phrase F1 0.000

- Counts: gold=0, predicted=0; strict TP/FP/FN=0/0/0; phrase TP/FP/FN=0/0/0
- Tags: `strict_correct`
- Verifier: raw=1, verified=0, actions={'remove': 1}, statuses={'diagnosis_without_frequency': 1}, additions=0
- Gold:
  - none
- Predicted:
  - none
- Error readout: no strict error.

