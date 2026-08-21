# Hybrid rescue source provenance

Date: 2026-08-13

Status: development mechanism evidence; no model calls

Protocol: [docs/research/shared/hybrid_rescue_source_provenance_protocol_2026-08-13.md](hybrid_rescue_source_provenance_protocol_2026-08-13.md)
Artifact: [`experiments/hybrid_rescue_source_provenance_20260813.json`](../../experiments/hybrid_rescue_source_provenance_20260813.json)

## Plain answer

On Gan, 1,437 of 1,539 first-rescues (0.93) only re-render the model's
selected quote. The remaining 102 first-rescues compose or promote from
events the model already extracted. Zero first-rescues invent a rate from
letter text the model never quoted.

On ExECT, each family is classified on its own first-rescue hop.
Diagnosis still splits across quote reuse, inventory trim, and a small
unquoted-letter add class. Seizure frequency is almost all a render or
trim of a state the model already emitted. Prescription's ten first-
rescues all rewrite a drug the model named. Investigations has two
first-rescues, both inventory trims.

These are pooled six-model first-rescues on development splits, not
holdout component estimates. The [HTML exhibit](../artifacts/rescue_source_provenance_2026-08-13.html)
shows the family split, the `EA0007` two-model contrast, and one card per
source class.

## Source classes

- **`render_selected`** — Render the selected span: the first-changer rereads the model's chosen quote or already-selected event and only changes form or canonical wording.
- **`promote_relegated_model_answer`** — Promote a relegated model answer: another saved event or mention already carried the rescued label or concept.
- **`compose_from_captured_events`** — Compose from captured events: no single model event already held the rescued label, but the rule built it from events the model did extract (diary sums, dated sequences, elapsed anchors).
- **`use_model_quote_not_as_answer`** — Use a model quote the model did not treat as that answer: the supporting words appear in some model evidence or mention, but not as the rescued diagnosis or frequency answer.
- **`trim_inventory_to_exact`** — Trim the inventory to exact: family exactness is rescued by dropping extra keys, not by adding a new concept or regimen.
- **`add_from_unquoted_letter_span`** — Add from letter text the model never quoted: the supporting fragment is not in any saved model evidence or mention.

## Gan 2026 (`dev750`, Purist first-rescue)

Replayable first-rescues classified: **1539**.

| Source class | First-rescues | Share |
| --- | ---: | ---: |
| `render_selected` | 1437 | 0.93 |
| `promote_relegated_model_answer` | 13 | 0.01 |
| `compose_from_captured_events` | 89 | 0.06 |
| `use_model_quote_not_as_answer` | 0 | 0.00 |
| `trim_inventory_to_exact` | 0 | 0.00 |
| `add_from_unquoted_letter_span` | 0 | 0.00 |
| Total | 1539 | 1.00 |

By first-changer stage:

- `repair.dated_sequence`: `compose_from_captured_events` 6
- `repair.elapsed_anchor`: `compose_from_captured_events` 9
- `repair.monthly_diary`: `compose_from_captured_events` 62, `promote_relegated_model_answer` 4
- `repair.non_epileptic`: `compose_from_captured_events` 5, `promote_relegated_model_answer` 4
- `repair.post_change_burst`: `promote_relegated_model_answer` 1
- `repair.residual_jerk`: `compose_from_captured_events` 4
- `repair.selected_evidence`: `render_selected` 1437
- `repair.usual_interval`: `compose_from_captured_events` 3, `promote_relegated_model_answer` 4

### Examples

#### `render_selected`

- Row `10` / GPT-4.1-mini, `repair.selected_evidence`: `≤ 4 per day` → `4 per day` (gold `4 per day`). Selected evidence: 'the observed frequency is noted as ≤ four per day, with variable clustering, often in the late afternoon or evening'.
- Row `40` / GPT-4.1-mini, `repair.selected_evidence`: `≤ 4 per week` → `4 per week` (gold `4 per week`). Selected evidence: 'overall a frequency of ≤ four seizures per week'.

#### `promote_relegated_model_answer`

- Row `13858` / GPT-4.1-mini, `repair.non_epileptic`: `unknown` → `seizure free for multiple year` (gold `seizure free for multiple month`). Selected evidence: 'intermittent brief episodes of altered awareness and tingling sensations occurring over the past year'.
- Row `13889` / GPT-4.1-mini, `repair.non_epileptic`: `unknown` → `seizure free for multiple year` (gold `seizure free for multiple month`). Selected evidence: 'She reports that since adopting stricter sleep hygiene during travel and using a structured jet-lag plan, the events have been less intrusive day-to-day.'.

#### `compose_from_captured_events`

- Row `5995` / GPT-4.1-mini, `repair.monthly_diary`: `1 per month` → `3 per 8 month` (gold `1 per 3 months`). Selected evidence: 'August 1 generalised convulsion following two consecutive late doses during a weekend trip'.
- Row `14567` / GPT-4.1-mini, `repair.dated_sequence`: `2 per month` → `3 per 3 month` (gold `3 per 3 month`). Selected evidence: 'Her second and third seizure was in January 2018 back home in France'.

## ExECTv2 (`dev140`, per-family first-rescue)

Each family is classified on its own first rescue hop, not on which
family happened to rescue the letter first.

### Diagnosis

First-rescues classified: **174**.

| Source class | First-rescues | Share |
| --- | ---: | ---: |
| `render_selected` | 2 | 0.01 |
| `promote_relegated_model_answer` | 7 | 0.04 |
| `compose_from_captured_events` | 0 | 0.00 |
| `use_model_quote_not_as_answer` | 104 | 0.60 |
| `trim_inventory_to_exact` | 51 | 0.29 |
| `add_from_unquoted_letter_span` | 10 | 0.06 |
| Total | 174 | 1.00 |

By first-changer stage:

- `lens.diagnosis`: `add_from_unquoted_letter_span` 10, `promote_relegated_model_answer` 7, `render_selected` 2, `trim_inventory_to_exact` 51, `use_model_quote_not_as_answer` 104

#### Examples

##### `render_selected`

- `EA0085` / Gemma 4 26B, `lens.diagnosis`: `[]` → `["('Diagnosis', 'juvenile myoclonic epilepsy')"]`.
- `EA0166` / Gemma 4 26B, `lens.diagnosis`: `[]` → `["('Diagnosis', 'juvenile myoclonic epilepsy')"]`.

##### `promote_relegated_model_answer`

- `EA0132` / GPT-4.1-mini, `lens.diagnosis`: `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal seizure')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal seizure')", "('Diagnosis', 'focal to bilateral convulsive seizure')", "('Diagnosis', 'focal seizures with altered awareness')"]`.
- `EA0186` / GPT-5.6 Luna, `lens.diagnosis`: `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal to bilateral convulsive seizure')", "('Diagnosis', 'focal motor seizure')"]`.

##### `use_model_quote_not_as_answer`

- `EA0034` / GPT-4.1-mini, `lens.diagnosis`: `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal seizures left arm movement')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal seizure')", "('Diagnosis', 'focal to bilateral convulsive seizure')", "('Diagnosis', 'occipital lobe epilepsy')"]`.
- `EA0054` / GPT-4.1-mini, `lens.diagnosis`: `["('Diagnosis', 'symptomatic structural frontal lobe epilepsy')", "('Diagnosis', 'focal cortical dysplasia')", "('Diagnosis', 'focal seizures with altered awareness')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal seizures with altered awareness')", "('Diagnosis', 'focal to bilateral convulsive seizure')", "('Diagnosis', 'frontal lobe epilepsy')"]`.

##### `trim_inventory_to_exact`

- `EA0024` / GPT-4.1-mini, `lens.diagnosis`: `["('Diagnosis', 'unwitnessed blackouts')", "('Diagnosis', 'anxiety')"]` → `[]`.
- `EA0046` / GPT-4.1-mini, `lens.diagnosis`: `["('Diagnosis', 'symptomatic structural epilepsy')", "('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'focal to bilateral convulsive seizure')"]`.

##### `add_from_unquoted_letter_span`

- `EA0007` / GPT-5.6 Sol, `lens.diagnosis`: `["('Diagnosis', 'epilepsy')"]` → `["('Diagnosis', 'focal epilepsy')"]`.
- `EA0056` / GPT-5.6 Sol, `lens.diagnosis`: `["('Diagnosis', 'localisation related epilepsy secondary to previous cerebral abcess')", "('Diagnosis', 'epilepsy')", "('Diagnosis', 'partial motor seizure')", "('Diagnosis', 'secondary generalised seizure')"]` → `["('Diagnosis', 'focal epilepsy')", "('Diagnosis', 'partial motor seizure')", "('Diagnosis', 'secondary generalised seizure')"]`.

### SeizureFrequency

First-rescues classified: **347**.

| Source class | First-rescues | Share |
| --- | ---: | ---: |
| `render_selected` | 301 | 0.87 |
| `promote_relegated_model_answer` | 0 | 0.00 |
| `compose_from_captured_events` | 4 | 0.01 |
| `use_model_quote_not_as_answer` | 0 | 0.00 |
| `trim_inventory_to_exact` | 42 | 0.12 |
| `add_from_unquoted_letter_span` | 0 | 0.00 |
| Total | 347 | 1.00 |

By first-changer stage:

- `project_and_gate`: `render_selected` 300, `trim_inventory_to_exact` 3
- `sf_state_projection`: `compose_from_captured_events` 4, `render_selected` 1, `trim_inventory_to_exact` 34
- `sf_unknown_suppression`: `trim_inventory_to_exact` 5

#### Examples

##### `render_selected`

- `EA0002` / GPT-4.1-mini, `project_and_gate`: `["(('phrase', 'focal seizure'), 'active-rate')", "(('phrase', 'secondary generalised seizure'), 'active-rate')"]` → `["(('cui', 'C0751495'), 'active-rate')", "(('cui', 'C0270838'), 'active-rate')"]`.
- `EA0004` / GPT-4.1-mini, `project_and_gate`: `["(('phrase', 'seizure'), 'active-rate')"]` → `["(('cui', 'C0036572'), 'active-rate')"]`.

##### `compose_from_captured_events`

- `EA0137` / GPT-4.1-mini, `sf_state_projection`: `["(('cui', 'C0270838'), 'active-rate')", "(('cui', 'C0036572'), 'active-rate')"]` → `["(('cui', 'C0270838'), 'active-rate')", "(('cui', 'C0036572'), 'seizure-free')"]`.
- `EA0182` / GPT-5.6 Luna, `sf_state_projection`: `["(('cui', 'C0036572'), 'active-rate')"]` → `["(('cui', 'C0036572'), 'seizure-free')"]`.

##### `trim_inventory_to_exact`

- `EA0052` / GPT-4.1-mini, `sf_state_projection`: `["(('phrase', 'attack'), 'active-rate')"]` → `[]`.
- `EA0062` / GPT-4.1-mini, `sf_state_projection`: `["(('cui', 'C0036572'), 'active-rate')"]` → `[]`.

### Prescription

First-rescues classified: **10**.

| Source class | First-rescues | Share |
| --- | ---: | ---: |
| `render_selected` | 0 | 0.00 |
| `promote_relegated_model_answer` | 0 | 0.00 |
| `compose_from_captured_events` | 10 | 1.00 |
| `use_model_quote_not_as_answer` | 0 | 0.00 |
| `trim_inventory_to_exact` | 0 | 0.00 |
| `add_from_unquoted_letter_span` | 0 | 0.00 |
| Total | 10 | 1.00 |

By first-changer stage:

- `lens.prescription`: `compose_from_captured_events` 10

#### Examples

##### `compose_from_captured_events`

- `EA0038` / GPT-5.6 Sol, `lens.prescription`: `["('ordinary', 'carbamazepine', '400/400/200', 'mg', '3')", "('ordinary', 'zonisamide', '50', 'mg', '2')", "('ordinary', 'clobazam', '10', 'mg', '2')"]` → `["('ordinary', 'carbamazepine', '400', 'mg', '1')", "('ordinary', 'carbamazepine', '400', 'mg', '1')", "('ordinary', 'carbamazepine', '200', 'mg', '1')", "('ordinary', 'zonisamide', '50', 'mg', '2')", "('ordinary', 'clobazam', '10', 'mg', '2')"]`.
- `EA0152` / GPT-5.6 Sol, `lens.prescription`: `["('ordinary', 'carbamazepine', '400', 'mg', '2')", "('ordinary', 'clobazam', '10-20', 'mg', '2')"]` → `["('ordinary', 'carbamazepine', '400', 'mg', '2')", "('rescue', 'clobazam', 'as_required')"]`.

### Investigations

First-rescues classified: **2**.

| Source class | First-rescues | Share |
| --- | ---: | ---: |
| `render_selected` | 0 | 0.00 |
| `promote_relegated_model_answer` | 0 | 0.00 |
| `compose_from_captured_events` | 0 | 0.00 |
| `use_model_quote_not_as_answer` | 0 | 0.00 |
| `trim_inventory_to_exact` | 2 | 1.00 |
| `add_from_unquoted_letter_span` | 0 | 0.00 |
| Total | 2 | 1.00 |

By first-changer stage:

- `project_and_gate`: `trim_inventory_to_exact` 2

#### Examples

##### `trim_inventory_to_exact`

- `EA0002` / GPT-4.1-mini, `project_and_gate`: `["('MRI', 'Yes', None)", "('MRI', 'Yes', 'Abnormal')"]` → `["('MRI', 'Yes', 'Abnormal')"]`.
- `EA0015` / Gemma 4 26B, `project_and_gate`: `["('EEG', 'Yes', 'Unknown')"]` → `[]`.

## Claim boundary

- Development no-call replay of saved six-model ledgers.
- Classifies first-rescues only; later hops and harms are out of scope.
- Cue matching is conservative string support, not clinical entailment.
- Not holdout attribution, clinical validity, or a rewrite of stage ablation.
