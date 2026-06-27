# Evidence Validity Audit — Phase 0 Before Picture

Date: 2026-06-27  ·  Model calls: 0 (replay-only)

Read-only taxonomy audit over saved artifacts. Current validity uses the existing raw substring metric (`evidence_valid` / `evidence_text_contained` at row level for gan2026; mention-level `evidence_valid` for ExECTv2). Grounded rate applies the existing repair cascade from `core/evidence.py` without changing any call site.

## Headline

- **Qwen hybrid (validation750 surfaced row):** exact 74.8% → grounded 94.7%; 53.7% of exact-invalid strings are recoverable `REPAIRED_*`.
- **Qwen LLM-only (validation750 surfaced row):** exact 76.5% → grounded 90.9%; 61.4% of exact-invalid strings are recoverable `REPAIRED_*`.

The Qwen gap is overwhelmingly recoverable formatting (`REPAIRED_*`, especially artifact normalisation for `≤` copy quirks), not absent evidence — the current metric penalises grounded copy fidelity.

## gan2026

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07`

- Model: GPT-4.1-mini
- Pipeline: `hybrid_structured_events` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`
- Audited 750 rows · 2247 evidence strings
- Current exact-valid rate (row): 92.1%
- Grounded rate (all extracted strings): 97.1%
- Exact-only string rate: 94.8%

| Grade | Count |
|---|---:|
| `EXACT` | 2130 |
| `REPAIRED_CASE` | 38 |
| `REPAIRED_ELLIPSIS` | 14 |
| `ABSENT` | 63 |
| `EMPTY` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 117
- Recoverable `REPAIRED_*`: 52 (44.4% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 65

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Since his last review here in March 2025, the charts and his account suggest a fluctuating pattern with brief episodes …"
  - "On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering, often in the la…"
  - "variable clustering, often in the late afternoon or evening"
  - "overall a frequency of ≤ four seizures per week"
  - "brief behavioural arrest lasting 10–20 seconds, occurring in clusters on stressful days"
- `REPAIRED_CASE`:
  - "he and his partner report that the seizures occur every four months"
  - "The shorter episodes often occur towards the end of longer, hotter shifts and tend to cluster on consecutive days when …"
  - "No tongue biting or urinary incontinence reported in recent episodes"
  - "Previously she experienced clusters of focal impaired-awareness seizures interspersed with quiescent periods"
  - "a rescue buccal midazolam plan remains in place for any prolonged event lasting more than 5 minutes, although this has …"
- `REPAIRED_ELLIPSIS`:
  - "five focal onset seizures ... in last month"
  - "he reports two absence seizures ... in last week"
  - "he reports ... three petit mal in last week"
  - "She reports one drop attacks ... in the past two months"
  - "Over the past six months he describes ... five epileptic spasms"
- `ABSENT`:
  - "He has been largely stable for the past 18 months on sodium valproate."
  - "six drop attacks in the past two months"
  - "three drop attacks in the past three months"
  - "two drop attacks in the past three months"
  - ""six or eight petit mal over the past month""
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08`

- Model: DeepSeek
- Pipeline: `hybrid_structured_events` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_deepseek_2026-06-08.jsonl`
- Audited 750 rows · 2176 evidence strings
- Current exact-valid rate (row): 95.7%
- Grounded rate (all extracted strings): 98.2%
- Exact-only string rate: 97.8%

| Grade | Count |
|---|---:|
| `EXACT` | 2128 |
| `REPAIRED_CASE` | 8 |
| `REPAIRED_ELLIPSIS` | 1 |
| `ABSENT` | 31 |
| `EMPTY` | 8 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 48
- Recoverable `REPAIRED_*`: 9 (18.8% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 39

**Samples (up to 5 per grade)**

- `EXACT`:
  - "≤ four per day"
  - "variable clustering"
  - "overall a frequency of ≤ four seizures per week"
  - "lasting 10–20 seconds"
  - "occurring in clusters on stressful days"
- `REPAIRED_CASE`:
  - "He has used on five occasions over the past three months"
  - "no clear triggers identified"
  - "He has remained generally well with intermittent sensory auras and brief events without clear loss of awareness"
  - "no clear loss of awareness was reported, and there have been no injuries"
  - "Two brief morning absences at work"
- `REPAIRED_ELLIPSIS`:
  - "brief morning myoclonic jerks several times per week, and three generalised tonic–clonic seizures in the past six month…"
- `ABSENT`:
  - "no daytime triggers identified"
  - "the previous seizure occurred during a flight's descent"
  - "she can go many months without an event, describing her pattern as "yearly seizures," with some years having one event …"
  - "four focal sensory and five focal non-motors in last month, giving a total of nine events per month"
  - "no seizure frequency reference"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08`

- Model: Qwen
- Pipeline: `hybrid_structured_events` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_qwen3635b_2026-06-08.jsonl`
- Audited 750 rows · 2125 evidence strings
- Current exact-valid rate (row): 74.8%
- Grounded rate (all extracted strings): 94.7%
- Exact-only string rate: 88.6%

| Grade | Count |
|---|---:|
| `EXACT` | 1883 |
| `REPAIRED_CASE` | 5 |
| `REPAIRED_ELLIPSIS` | 125 |
| `ABSENT` | 108 |
| `EMPTY` | 4 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 242
- Recoverable `REPAIRED_*`: 130 (53.7% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 112

**Samples (up to 5 per grade)**

- `EXACT`:
  - "the observed frequency is noted as ≤ four per day"
  - "variable clustering, often in the late afternoon or evening"
  - "the observed frequency is noted as ≤ four per day, with variable clustering"
  - "overall a frequency of ≤ four seizures per week"
  - "occurring in clusters on stressful days"
- `REPAIRED_CASE`:
  - "over the past three months, he and his partner report clusters of events with variable frequency: on steadier stretches…"
  - "there are no current red flags (no nocturnal injuries, tongue biting, incontinence, or postictal confusion)"
  - "there have been no episodes suggestive of auras, blackouts, or nocturnal events according to her and her partner’s obse…"
  - "she reports a recent shift in her seizure pattern over the past three months, characterised by clusters arising after n…"
  - "she could not quantify the total number of events and feels they are occurring more often at work compared to home"
- `REPAIRED_ELLIPSIS`:
  - "ongoing events occurring roughly weekly ... The occupational health summaries corroborate a weekly frequency over the p…"
  - "Currently reporting monthly seizures... pattern of monthly seizures only"
  - "This patient reports bimonthly seizures... The last two seizures were approximately eight and sixteen weeks ago, aligni…"
  - "they believe there were 3 or 5 seizures last month. Two were typical brief focal aware episodes... and one to three eve…"
  - "one tonic-clonic ... in last week"
- `ABSENT`:
  - "Over the same interval, there have been two nocturnal generalised tonic-clonic seizures"
  - "events tend to cluster every seven to nine days. Over the same interval, there have been two nocturnal generalised toni…"
  - "there have been none since [May 2025]"
  - "patient has self-reported seizure frequency averaging 1 per eight months. Over the past 16 months he has experienced tw…"
  - "describing her pattern as “yearly seizures,” with some years having one event and others none. She has returned to full…"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07`

- Model: GPT-4.1-mini
- Pipeline: `llm_only_canonical_pipeline` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl`
- Audited 750 rows · 750 evidence strings
- Current exact-valid rate (row): 93.3%
- Grounded rate (all extracted strings): 95.5%
- Exact-only string rate: 93.3%

| Grade | Count |
|---|---:|
| `EXACT` | 700 |
| `REPAIRED_CASE` | 11 |
| `REPAIRED_WHITESPACE` | 2 |
| `REPAIRED_ELLIPSIS` | 3 |
| `ABSENT` | 24 |
| `EMPTY` | 10 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 50
- Recoverable `REPAIRED_*`: 16 (32.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 34

**Samples (up to 5 per grade)**

- `EXACT`:
  - "On the accommodation logs, the observed frequency is noted as ≤ four per day"
  - "Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week"
  - "Seizure frequency currently reported as ≤ 6 to 7 per year"
  - "Over the past year, however, the patient and family report that events have become markedly infrequent, such that the c…"
  - "He reports a current seizure frequency of 17 per month"
- `REPAIRED_CASE`:
  - "at present, his typical pattern is a focal seizure monthly"
  - "He was unable to quantify a clear pattern or monthly rate. He specifically described “Sporadic drop attacks this year,”…"
  - "He is now Seizure-free after dose escalation of ASM. Specifically, a gradual increase in his current regimen over the p…"
  - "He describes occasional brief morning myoclonic jerks when sleep-deprived, with rare episodes of transient unresponsive…"
  - "ongoing seizures with variable semiology; prior non-diagnostic EEGs; MRI brain (2006) reported no clear structural corr…"
- `REPAIRED_WHITESPACE`:
  - "The generalised tonic–clonic seizures have been infrequent over the past year and, according to the patient and his par…"
  - "She reports occasional brief staring spells with loss of awareness and immediate recovery, sometimes with a subtle eyel…"
- `REPAIRED_ELLIPSIS`:
  - "Quarterly clusters with one convulsions per episode. Specifically, approximately every three months he experiences a br…"
  - "She experienced her first seizure in October 2017 while on holiday in Spain. ... Her second and third seizure was in Ja…"
  - "He may go four days without seizures, but when they happen he often has them in batches, with three occurring within 24…"
- `ABSENT`:
  - "she states that she can go many months without an event, describing her pattern as “yearly seizures”"
  - "Over the last three months, he has recorded “21 to 28 epileptic spasms in three months”"
  - "Several episodes per week, predominantly brief staring episodes with behavioural arrest consistent with absences, and t…"
  - "Last cluster was in early June 2025 during a documented delay in dispensing (ï¿½ two days without evening tablets). Sin…"
  - "Alex has not described any definite events for over a year. He notes occasional brief moments of "head-fog" under stres…"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08`

- Model: DeepSeek
- Pipeline: `llm_only_canonical_pipeline` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_deepseek_2026-06-08.jsonl`
- Audited 750 rows · 750 evidence strings
- Current exact-valid rate (row): 92.5%
- Grounded rate (all extracted strings): 95.6%
- Exact-only string rate: 92.5%

| Grade | Count |
|---|---:|
| `EXACT` | 694 |
| `REPAIRED_CASE` | 6 |
| `REPAIRED_WHITESPACE` | 2 |
| `REPAIRED_ELLIPSIS` | 15 |
| `ABSENT` | 24 |
| `EMPTY` | 9 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 56
- Recoverable `REPAIRED_*`: 23 (41.1% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 33

**Samples (up to 5 per grade)**

- `EXACT`:
  - "≤ four per day"
  - "overall a frequency of ≤ four seizures per week"
  - "≤ 6 to 7 per year"
  - "the current pattern is ≤ two or four per year"
  - "He reports a current seizure frequency of 17 per month"
- `REPAIRED_CASE`:
  - "He was unable to quantify a clear pattern or monthly rate"
  - "The partner (when present) has previously heard brief groaning and heavy breathing once or twice a week"
  - "he did not have seizures for over 6 months, but then reported two generalised tonic-clonic seizures two Fridays ago"
  - "He has not needed to deploy it to date"
  - "his last episode was recorded on 17/May and he has remained well since"
- `REPAIRED_WHITESPACE`:
  - "The diary shows infrequent events predominantly aligned with days of delayed or missed antiseizure medication (ASM) dos…"
  - "He reports two distinct seizure patterns: - Generalised: brief morning myoclonic jerks several times per week, and thre…"
- `REPAIRED_ELLIPSIS`:
  - "He describes daily events despite treatment trials in primary care. ... He keeps a diary and notes TC one/d over the pa…"
  - "noise-triggered focal seizures occur about once every 3–4 weeks... Intervening background focal auras without loss of a…"
  - "no witnessed episodes suggestive of a typical event... remaining free of his usual attacks over this interval... has no…"
  - "Alex has not described any definite events for over a year. ... His seizure diary shows no recorded events since June l…"
  - "Seizure cessation following initiation of last ASM. ... the last marked event predating the start of levetiracetam."
- `ABSENT`:
  - "Over the past month she reports "six or eight petit mal over the past month""
  - "Over the past year there have been two brief generalised tonic–clonic seizures... A seizure diary kept over the last th…"
  - "He reports no episodes suggestive of seizures since his last review and confirms there have been no witnessed events, n…"
  - "he reports no definite seizures and no witnessed collapses. His wearable device and home seizure-detection app record n…"
  - "Prior cluster pattern resolved since 11 Aug 2023. No events witnessed by colleagues... She has not required any emergen…"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08`

- Model: Qwen
- Pipeline: `llm_only_canonical_pipeline` · split `validation` · source `registry_surface_as_architecture`
- Artifact: `experiments/gan2026_three_way_comparison_validation750_llm_only_canonical_pipeline_qwen3635b_2026-06-08.jsonl`
- Audited 750 rows · 750 evidence strings
- Current exact-valid rate (row): 76.5%
- Grounded rate (all extracted strings): 90.9%
- Exact-only string rate: 76.5%

| Grade | Count |
|---|---:|
| `EXACT` | 574 |
| `REPAIRED_CASE` | 1 |
| `REPAIRED_WHITESPACE` | 1 |
| `REPAIRED_ELLIPSIS` | 106 |
| `ABSENT` | 66 |
| `EMPTY` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 176
- Recoverable `REPAIRED_*`: 108 (61.4% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 68

**Samples (up to 5 per grade)**

- `EXACT`:
  - "the observed frequency is noted as ≤ four per day, with variable clustering, often in the late afternoon or evening"
  - "overall a frequency of ≤ four seizures per week"
  - "seizure frequency of ≤ 6 to 7 per year"
  - "the current pattern is ≤ two or four per year"
  - "He reports a current seizure frequency of 17 per month"
- `REPAIRED_CASE`:
  - "The pattern this year has been as follows: Seizures in 2017-2017: May: 8 days with seizures June: 1 days with seizures …"
- `REPAIRED_WHITESPACE`:
  - "episodes tend to cluster on days with poor sleep or higher stress. From the app logs and her account: When clusters occ…"
- `REPAIRED_ELLIPSIS`:
  - "events tend to cluster every seven to nine days... Over the same interval, there have been two nocturnal generalised to…"
  - "He reports events occur daily... Alex logged similar events on his phone diary daily over the past four weeks."
  - "This patient reports bimonthly seizures... The last two seizures were approximately eight and sixteen weeks ago, aligni…"
  - "the patient reports several focal seizures last week ... There has also been one episode with a witnessed fall"
  - "focal onset events ... occurring several times per week"
- `ABSENT`:
  - "He describes episodes that remain variably stereotyped. He notes that over the course of most calendar cycles he will h…"
  - "Over the last three months, he has recorded “21 to 28 epileptic spasms in three months”"
  - "The patient reported 1 tonic-clonic seizures yesterday... He is otherwise well, working full-time, and prefers to avoid…"
  - "She has had occasional tonic-clonic over last year... She describes ongoing focal aware and focal impaired-awareness ep…"
  - "Over the past month she reports "six or eight petit mal over the past month""
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12`

- Model: openai/gpt-4.1-mini
- Pipeline: `agentic_boundary_audit_prompt_v2` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl`
- Audited 12 rows · 12 evidence strings
- Current exact-valid rate (row): 83.3%
- Grounded rate (all extracted strings): 83.3%
- Exact-only string rate: 83.3%

| Grade | Count |
|---|---:|
| `EXACT` | 10 |
| `ABSENT` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 2
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 2

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Over the past six weeks he describes three witnessed convulsive episodes and several brief staring events with loss of …"
  - "Morning clusters one - two×/month; ~four events over 90 min"
  - "a very infrequent, short event a fortnight ago"
  - "She reports infrequent generalised seizures provoked by patterned or flickering visual stimuli (e.g. rapid screen refre…"
  - "continues to experience brief absence from time to time"
- `ABSENT`:
  - "brief pause-and-stare episodes with subtle mouth movements” occur predominantly in clusters within the 3 days prior to …"
  - "brief bursts occurring roughly once a month, typically soon after waking; consistent pattern over the last three months…"

### `gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12`

- Model: none
- Pipeline: `agentic_boundary_guide_rescue_replay` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_agentic_hard50_boundary_guide_rescue_replay_2026-06-12.jsonl`
- Audited 50 rows · 50 evidence strings
- Current exact-valid rate (row): 0.0%
- Grounded rate (all extracted strings): 0.0%
- Exact-only string rate: 0.0%

| Grade | Count |
|---|---:|
| `EMPTY` | 50 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 50
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 50

**Samples (up to 5 per grade)**

- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13`

- Model: panel: deterministic_rules_tool + gpt-4.1-mini + qwen3-235b-a22b + deepseek
- Pipeline: `agentic_structured_event_consensus` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl`
- Audited 750 rows · 750 evidence strings
- Current exact-valid rate (row): 0.0%
- Grounded rate (all extracted strings): 0.0%
- Exact-only string rate: 0.0%

| Grade | Count |
|---|---:|
| `EMPTY` | 750 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 750
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 750

**Samples (up to 5 per grade)**

- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12`

- Model: none; saved ollama_chat/qwen3.6:35b structured-events outputs only
- Pipeline: `agentic_structured_event_patch` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_validation750_qwen3635b_2026-06-12.jsonl`
- Audited 750 rows · 2052 evidence strings
- Current exact-valid rate (row): 77.5%
- Grounded rate (all extracted strings): 95.2%
- Exact-only string rate: 89.6%

| Grade | Count |
|---|---:|
| `EXACT` | 1838 |
| `REPAIRED_CASE` | 4 |
| `REPAIRED_ELLIPSIS` | 111 |
| `ABSENT` | 95 |
| `EMPTY` | 4 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 214
- Recoverable `REPAIRED_*`: 115 (53.7% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 99

**Samples (up to 5 per grade)**

- `EXACT`:
  - "the observed frequency is noted as ≤ four per day, with variable clustering"
  - "brief episodes most days"
  - "overall a frequency of ≤ four seizures per week"
  - "occurring in clusters on stressful days"
  - "overall a frequency of ≤ four seizures per week, typically brief generalised convulsions or absence episodes as describ…"
- `REPAIRED_CASE`:
  - "over the past three months, he and his partner report clusters of events with variable frequency: on steadier stretches…"
  - "No history of myoclonic jerks or absences since remission began"
  - "there have been no episodes suggestive of auras, blackouts, or nocturnal events according to her and her partner’s obse…"
  - "within these burst periods the number of episodes varies and has not been reliably logged"
- `REPAIRED_ELLIPSIS`:
  - "following a recent event that occurred during air travel... The witnessed episode in-flight featured loss of responsive…"
  - "Over the last four weeks he has experienced many convulsions in past month... These events clustered after eastbound fl…"
  - "ongoing events occurring roughly weekly ... occupational health summaries corroborate a weekly frequency over the past …"
  - "This patient reports bimonthly seizures... The last two seizures were approximately eight and sixteen weeks ago, aligni…"
  - "they believe there were 3 or 5 seizures last month. ... There has been an apparent increase in generalised events over …"
- `ABSENT`:
  - "Over the past year, however, the patient and family report that events have become markedly infrequent, such that the c…"
  - "Over the same interval, there have been two nocturnal generalised tonic-clonic seizures"
  - "events tend to cluster every seven to nine days. Over the same interval, there have been two nocturnal generalised toni…"
  - "there have been none since [May 2025]"
  - "Over the past five months on the present regimen, events have reduced to ≤ once per month, typically brief focal impair…"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13`

- Model: openai/gpt-4.1
- Pipeline: `fresh_evidence_reasoner` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`
- Audited 750 rows · 1647 evidence strings
- Current exact-valid rate (row): 93.7%
- Grounded rate (all extracted strings): 96.7%
- Exact-only string rate: 95.0%

| Grade | Count |
|---|---:|
| `EXACT` | 1565 |
| `REPAIRED_CASE` | 23 |
| `REPAIRED_WHITESPACE` | 1 |
| `REPAIRED_ELLIPSIS` | 3 |
| `ABSENT` | 55 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 82
- Recoverable `REPAIRED_*`: 27 (32.9% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 55

**Samples (up to 5 per grade)**

- `EXACT`:
  - "the observed frequency is noted as ≤ four per day, with variable clustering, often in the late afternoon or evening"
  - "On the accommodation logs, the observed frequency is noted as ≤ four per day, with variable clustering, often in the la…"
  - "overall a frequency of ≤ four seizures per week"
  - "he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week, typically brief generali…"
  - "Seizure frequency currently reported as ≤ 6 to 7 per year"
- `REPAIRED_CASE`:
  - "he and his partner report that the seizures occur every four months"
  - "over the last eight weeks, they report a stable pattern of focal aware sensory episodes with occasional progression to …"
  - "deterioration from previous stability; seizures every other day over the last six weeks"
  - "he reports improved sleep regularity and reduced overtime on night shifts. He has had No events for twelve months, with…"
  - "They report intermittent brief losses of awareness with occasional sudden startle and post-event fatigue"
- `REPAIRED_WHITESPACE`:
  - "Plan: - Practical advice provided on maintaining charged medical devices: carry a compact power bank, use low-power mod…"
- `REPAIRED_ELLIPSIS`:
  - "There is no current antiseizure therapy in place; he self-discontinued medication over three years ago ... and there ha…"
  - "He described a long history of intermittent episodes that have varied over the years. The current concerns relate to br…"
  - "He had a cluster of three seizures in Aug ... In Sep he had six nocturnal seizures, and in Oct a single tonic seizure w…"
- `ABSENT`:
  - "he has been keeping a diary which corroborates this frequency"
  - "she prefers to defer routine daily antiseizure medication for now, given her current pattern of approximately twice per…"
  - "He has been largely stable for the past 18 months on sodium valproate."
  - ""six or eight petit mal over the past month""
  - ""myoclonic every other day"; "occasional clusters during periods of intense study""

### `gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15`

- Model: none
- Pipeline: `hybrid_clinical_frequency_state_graph` · split `validation` · source `registry_promote`
- Artifact: `experiments/gan2026_state_graph_ontology_stage_d_promotion_gate_2026-06-15_rows.jsonl`
- Audited 250 rows · 250 evidence strings
- Current exact-valid rate (row): 0.0%
- Grounded rate (all extracted strings): 0.0%
- Exact-only string rate: 0.0%

| Grade | Count |
|---|---:|
| `EMPTY` | 250 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 250
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 250

**Samples (up to 5 per grade)**

- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

## ExECTv2

### `exectv2_holistic_finding_assembly_v08_dev140`

- Model: GPT-4.1-mini-family lanes
- Pipeline: `rich_schema_reliability` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl`
- Audited 140 rows · 913 evidence strings
- Current exact-valid rate (mention): 100.0%
- Grounded rate (all extracted strings): 99.7%
- Exact-only string rate: 99.5%

| Grade | Count |
|---|---:|
| `EXACT` | 908 |
| `REPAIRED_CASE` | 1 |
| `REPAIRED_WHITESPACE` | 1 |
| `EMPTY` | 3 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 5
- Recoverable `REPAIRED_*`: 2 (40.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 3

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "focal seizures"
  - "secondary generalised seizures"
- `REPAIRED_CASE`:
  - "focal epilepsy"
- `REPAIRED_WHITESPACE`:
  - "Diagnosis: Focal epilepsy"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140`

- Model: GPT-4.1-mini-family lanes
- Pipeline: `rich_schema_reliability` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/_archive/exectv2_richschema_iterations/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.jsonl`
- Audited 140 rows · 894 evidence strings
- Current exact-valid rate (mention): 100.0%
- Grounded rate (all extracted strings): 99.6%
- Exact-only string rate: 99.3%

| Grade | Count |
|---|---:|
| `EXACT` | 888 |
| `REPAIRED_CASE` | 1 |
| `REPAIRED_WHITESPACE` | 1 |
| `EMPTY` | 4 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 6
- Recoverable `REPAIRED_*`: 2 (33.3% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 4

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "focal seizures"
  - "secondary generalised seizures"
- `REPAIRED_CASE`:
  - "focal epilepsy"
- `REPAIRED_WHITESPACE`:
  - "Diagnosis: Focal epilepsy"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140`

- Model: DeepSeek chat
- Pipeline: `rich_schema_reliability` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/_archive/exectv2_richschema_iterations/exectv2_holistic_finding_assembly_v0916_deepseek_reparse_dev140_20260622.jsonl`
- Audited 140 rows · 843 evidence strings
- Current exact-valid rate (mention): 100.0%
- Grounded rate (all extracted strings): 99.8%
- Exact-only string rate: 99.8%

| Grade | Count |
|---|---:|
| `EXACT` | 841 |
| `EMPTY` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 2
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 2

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "Current antiepileptic medication: carbamazepine 400 mg twice a day"
  - "Topiramate 100 mg BD"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140`

- Model: Qwen 3.6 35B
- Pipeline: `rich_schema_reliability` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/_archive/exectv2_richschema_iterations/exectv2_holistic_finding_assembly_v0922_qwencompact_residualrepair_dev140_20260622.jsonl`
- Audited 140 rows · 881 evidence strings
- Current exact-valid rate (mention): 100.0%
- Grounded rate (all extracted strings): 99.9%
- Exact-only string rate: 99.9%

| Grade | Count |
|---|---:|
| `EXACT` | 880 |
| `EMPTY` | 1 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 1
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 1

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "secondary generalised seizures"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "She also gets the same sensations before one of her have bigger convulsive seizures."
- `EMPTY`:
  - "<no evidence strings extracted>"

### `decision_table_sf_inv_gpt41mini_dev140`

- Model: GPT-4.1-mini
- Pipeline: `active_llm_only` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev140_gpt41mini_20260624.jsonl`
- Audited 140 rows · 656 evidence strings
- Current exact-valid rate (mention): 0.0%
- Grounded rate (all extracted strings): 99.7%
- Exact-only string rate: 99.7%

| Grade | Count |
|---|---:|
| `EXACT` | 654 |
| `EMPTY` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 2
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 2

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "carbamazepine 400 mg twice a day"
  - "Topiramate 100 mg BD"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `decision_table_sf_inv_deepseek_chat_dev140`

- Model: DeepSeek chat
- Pipeline: `active_llm_only` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_deepseek_chat_20260624.jsonl`
- Audited 140 rows · 780 evidence strings
- Current exact-valid rate (mention): 0.0%
- Grounded rate (all extracted strings): 99.7%
- Exact-only string rate: 99.7%

| Grade | Count |
|---|---:|
| `EXACT` | 778 |
| `EMPTY` | 2 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 2
- Recoverable `REPAIRED_*`: 0 (0.0% of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 2

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "carbamazepine 400 mg twice a day"
  - "Topiramate 100 mg BD"
- `EMPTY`:
  - "<no evidence strings extracted>"
  - "<no evidence strings extracted>"

### `decision_table_sf_inv_qwen36_side11435_dev140`

- Model: Qwen 3.6 35B
- Pipeline: `active_llm_only` · split `dev140` · source `exectv2_reliability_catalog`
- Artifact: `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_qwen36_side11435_20260624.jsonl`
- Audited 140 rows · 746 evidence strings
- Current exact-valid rate (mention): 0.0%
- Grounded rate (all extracted strings): 100.0%
- Exact-only string rate: 100.0%

| Grade | Count |
|---|---:|
| `EXACT` | 746 |

**Exact-invalid split** (strings failing raw substring today):

- Exact-invalid strings: 0
- Recoverable `REPAIRED_*`: 0 (n/a of exact-invalid)
- Genuine `ABSENT`/`EMPTY`: 0

**Samples (up to 5 per grade)**

- `EXACT`:
  - "Diagnosis: focal epilepsy-Probable temporal"
  - "In March she had 2 to 3 of her focal seizures without change in awareness."
  - "Since her last clinic appointment she has had four secondary generalised seizures."
  - "carbamazepine"
  - "Topiramate 100 mg BD"


---

Generated by `experiments/build_evidence_validity_audit.py` (Phase 0). Phase 1 will promote `grade_evidence` into `core/evidence.py`; Phases 2–4 replace call sites and replay the unified metric.
