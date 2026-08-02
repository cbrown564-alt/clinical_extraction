<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Gan 2026 - Rules only

Method id: `gan2026_rules_only`  
Role: **selected**  
Stages: 5  
Stages that may change clinical meaning: 2

## One sentence

> Deterministic rules find every seizure-frequency statement in the letter, normalize them, pick one as the current answer, and render it as a Gan label.

## Sixty seconds

No model is involved. Pattern rules read the letter and emit candidate seizure-frequency events, each carrying its own evidence span. A normalization stage converts the free text of each candidate into a comparable monthly rate. A selection stage then applies the Gan clinical policy - prefer a current, typical, overall burden - to choose one winning event, and renders it as a Gan label string. An evidence-and-trace check confirms the rendered answer is still supported by the span the rule matched. Finally the single label is projected into the Purist and Pragmatic scoring categories. Every clinical choice in this method belongs to a named rule group, so any error can be attributed to a rule rather than to a model.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | note text (str) plus source row index - see `gan.rules.extract` |
| Who first proposes the clinical answer? | deterministic rules (stage gan.rules.select_and_render) |
| Which later stages may change clinical meaning? | `gan.rules.select_and_render` |
| What final representation is scored? | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| What evidence shows whether each component helped or harmed? | `docs/canon/06_gan_clinical_policy.md`, `docs/research/clinical_selection_policy_catalog_2026-07-31.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `gan.rules.extract`<br>Extract candidate events | rules | CLINICAL MEANING | Run the seizure-frequency pattern rules over the note text and emit every candidate event with its evidence span, temporality, and certainty. |
| 2 | `gan.rules.normalize`<br>Normalize candidate events | rules | representation | Convert each candidate's source phrase into a comparable normalized rate and label form without choosing between candidates. |
| 3 | `gan.rules.select_and_render`<br>Select the current event and render the label | rules | CLINICAL MEANING | Apply the Gan clinical selection policy to choose one event as the current answer, then render it as a Gan label string with rationale and evidence. |
| 4 | `gan.rules.evidence_trace_check`<br>Check evidence and clinical trace | rules | gate | Confirm the rendered answer is still supported by the matched span and build the clinical assessment trace; record which ablation switches were disabled. |
| 5 | `gan.rules.score`<br>Project to Purist and Pragmatic scoring | scorer | benchmark projection | Map the predicted and gold monthly frequencies into the Purist and Pragmatic categories and compare. |

## Stage walkthrough

### 1. Extract candidate events

`gan.rules.extract` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Run the seizure-frequency pattern rules over the note text and emit every candidate event with its evidence span, temporality, and certainty.

|  | Type | Example |
| --- | --- | --- |
| In | note text (str) plus source row index | "He reports about two seizures per month, though he had seven so far this year." |
| Out | tuple[list[ExtractedCandidate], CandidateSet, list[CandidateEvent]] | two candidate events: 'about two seizures per month' (rate, current) and 'seven so far this year' (count, year-to-date) |

> This is where clinical content originates in the rules-only method: a phrase the rules do not match cannot be selected later.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:extract_stage`)
- Test: [`tests/test_gan2026_deterministic_canonical_pipeline.py`](../../../tests/test_gan2026_deterministic_canonical_pipeline.py)
- Proven in a trace by: `diagnostics.candidate_events`
- Paper wording: Deterministic pattern rules extract candidate seizure-frequency events with source-anchored evidence spans.

### 2. Normalize candidate events

`gan.rules.normalize` - rules-owned, representation, rule category `seizure_frequency`

Convert each candidate's source phrase into a comparable normalized rate and label form without choosing between candidates.

|  | Type | Example |
| --- | --- | --- |
| In | list[CandidateEvent] plus the raw candidates | 'about two seizures per month' |
| Out | list[NormalizedEvent] | normalized rate 2 per month, monthly_frequency 2.0 |

> Normalization is representation-only by contract: it must not drop or reorder candidates. tests/test_gan2026_normalize_governance.py is the governing constraint.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:normalize_stage`)
- Test: [`tests/test_gan2026_normalize_governance.py`](../../../tests/test_gan2026_normalize_governance.py)
- Proven in a trace by: `diagnostics.normalized_events`
- Paper wording: Candidate events are normalized to a common rate representation before selection.

### 3. Select the current event and render the label

`gan.rules.select_and_render` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Apply the Gan clinical selection policy to choose one event as the current answer, then render it as a Gan label string with rationale and evidence.

|  | Type | Example |
| --- | --- | --- |
| In | list[CandidateEvent] plus list[NormalizedEvent] | two normalized events: 2 per month (typical, current) and 7 per year (year-to-date) |
| Out | FinalSelection (selected_event_ids, final_label, evidence, rationale) | final_label '2 per month', evidence 'about two seizures per month' |

> This stage owns the prediction. The competing-rate policies catalogued in docs/research/clinical_selection_policy_catalog_2026-07-31.md fire here.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:select_and_render_stage`)
- Test: [`tests/test_gan2026_pipeline_v1_selection.py`](../../../tests/test_gan2026_pipeline_v1_selection.py)
- Proven in a trace by: `diagnostics.final_selection`
- Paper wording: A deterministic selection policy chooses one current event and renders the final label.

### 4. Check evidence and clinical trace

`gan.rules.evidence_trace_check` - rules-owned, gate, rule category `general`

Confirm the rendered answer is still supported by the matched span and build the clinical assessment trace; record which ablation switches were disabled.

|  | Type | Example |
| --- | --- | --- |
| In | note text, FinalSelection, CandidateSet, selected index | final_label '2 per month' with evidence 'about two seizures per month' |
| Out | tuple[bool, ClinicalAssessment \| None] | evidence_valid True |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/deterministic_canonical_stages.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:evidence_trace_check_stage`)
- Test: [`tests/test_gan2026_clinical_assessment_contract.py`](../../../tests/test_gan2026_clinical_assessment_contract.py)
- Proven in a trace by: `diagnostics.evidence_valid`, `diagnostics.clinical_assessment`
- Paper wording: Each selected answer is checked against its source span before scoring.

### 5. Project to Purist and Pragmatic scoring

`gan.rules.score` - scorer-owned, benchmark projection

Map the predicted and gold monthly frequencies into the Purist and Pragmatic categories and compare.

|  | Type | Example |
| --- | --- | --- |
| In | predicted label and gold monthly frequency | predicted 2.0 per month, gold 2.0 per month |
| Out | per-row category comparison and aggregate metrics | purist_correct True, pragmatic_correct True |

> Two letters with different clinical answers can score identically if both land in the same category. The scorer, not the pipeline, decides that.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/evaluate.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.evaluate:evaluate_frequency_records`)
- Test: [`tests/test_gan2026_evaluate.py`](../../../tests/test_gan2026_evaluate.py)
- Proven in a trace by: `comparison.purist_correct`, `comparison.pragmatic_correct`
- Paper wording: Predictions are scored under the Purist and Pragmatic category projections.

## Code map

Entry point: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/rules.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/rules.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.rules:run_record`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `gan.rules.extract` | `clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:extract_stage` | `tests/test_gan2026_deterministic_canonical_pipeline.py` |
| `gan.rules.normalize` | `clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:normalize_stage` | `tests/test_gan2026_normalize_governance.py` |
| `gan.rules.select_and_render` | `clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:select_and_render_stage` | `tests/test_gan2026_pipeline_v1_selection.py` |
| `gan.rules.evidence_trace_check` | `clinical_extraction.tasks.seizure_frequency.gan2026.deterministic_canonical_stages:evidence_trace_check_stage` | `tests/test_gan2026_clinical_assessment_contract.py` |
| `gan.rules.score` | `clinical_extraction.tasks.seizure_frequency.gan2026.evaluate:evaluate_frequency_records` | `tests/test_gan2026_evaluate.py` |

## Not this method

These paths exist and are easy to mistake for the selected method. They are named here so they cannot be read as it.

| Path | Role | Why it is not the selected method |
| --- | --- | --- |
| `src/clinical_extraction/tasks/seizure_frequency/gan2026/runners/split.py` | research entry point | Runs run_item over a split and aggregates; adds no clinical stage. |
| `src/clinical_extraction/tasks/seizure_frequency/gan2026/runners/config.py` | experiment control | Disables named rule groups to attribute results; not part of the selected configuration. |

## Executable trace

See the [Gan 2026 teaching case](../teaching_cases/gan2026.md), which runs this method over one letter and records what every stage above actually did.
