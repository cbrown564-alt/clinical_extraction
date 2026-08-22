<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Gan 2026 - LLM only

Method id: `gan2026_llm_only`  
Role: **implemented runner (not a paper results column)**  
Stages: 8
Stages that may change clinical meaning: 2

## One sentence

> One model call reads the letter and returns the final Gan label directly; deterministic code then repairs, validates, and scores that answer.

## Sixty seconds

The prompt carries the Gan rule taxonomy, and the model returns a single decision object: final label, evidence, answer kind, selected seizure type, time window, confidence, and rationale. The model owns the clinical decision - no deterministic extractor proposes candidates. After the call, code repairs JSON dialect and schema shape, validates the decision against the schema, and then applies one selected-evidence label repair. That repair is not cosmetic: it can change the final label when the model's label disagrees with the evidence span it quoted. The repaired label is checked for scorability and evidence containment, then projected into the Purist and Pragmatic categories. The honest summary is that the model makes the clinical decision and exactly one deterministic stage can overrule its wording.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | GanFrequencyRecord - see `gan.llm.build_prompt` |
| Who first proposes the clinical answer? | the model (stage gan.llm.model_call), with one deterministic override at gan.llm.selected_evidence_repair |
| Which later stages may change clinical meaning? | `gan.llm.selected_evidence_repair` |
| What final representation is scored? | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| What evidence shows whether each component helped or harmed? | `docs/paper/methods.md`, `docs/paper/claims.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `gan.llm.build_prompt`<br>Build the decision prompt | rules | transport/schema only | Render the note text and the Gan rule taxonomy into the prompt input for one structured decision call. |
| 2 | `gan.llm.model_call`<br>Model decides the final label | model | CLINICAL MEANING | One structured call returns the final label, evidence, answer kind, selected seizure type, time window, confidence, and rationale. |
| 3 | `gan.llm.json_schema_repair`<br>Repair JSON dialect and payload shape | rules | transport/schema only | Recover the JSON object from the raw output, repair Python-literal dialect, fix a known rationale key typo, coerce rule-family fields, and drop unsupported keys. |
| 4 | `gan.llm.schema_validation`<br>Validate the decision schema | rules | gate | Validate the repaired payload against the canonical decision record; a failure ends the row with no prediction. |
| 5 | `gan.llm.selected_evidence_repair`<br>Evidence-based label repair | rules | CLINICAL MEANING | Compare the model's final label with the evidence span it quoted and rewrite the label when the evidence supports a different rate. |
| 6 | `gan.llm.scorable_label_check`<br>Check the label is scorable | rules | gate | Parse the repaired label into a frequency record; an unparseable label is recorded as unscorable. |
| 7 | `gan.llm.evidence_containment`<br>Check evidence is an exact substring | rules | gate | Require the model's quoted evidence to appear verbatim in the note text. |
| 8 | `gan.llm.score`<br>Project to Purist and Pragmatic scoring | scorer | benchmark projection | Map the predicted and gold monthly frequencies into the Purist and Pragmatic categories and compare. |

## Stage walkthrough

### 1. Build the decision prompt

`gan.llm.build_prompt` - rules-owned, transport/schema only, rule category `general`

Render the note text and the Gan rule taxonomy into the prompt input for one structured decision call.

|  | Type | Example |
| --- | --- | --- |
| In | GanFrequencyRecord | note text plus source row index |
| Out | prompt input JSON (str) | {"note_text": "...", "instructions": "..."} |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:build_prompt_input`)
- Test: [`tests/test_gan2026_llm_prompt_hygiene.py`](../../../tests/test_gan2026_llm_prompt_hygiene.py)
- Proven in a trace by: `prompt_input_json`, `prompt_version`
- Paper wording: A single prompt presents the note and the labelling taxonomy.

### 2. Model decides the final label

`gan.llm.model_call` - model-owned, CLINICAL MEANING

One structured call returns the final label, evidence, answer kind, selected seizure type, time window, confidence, and rationale.

|  | Type | Example |
| --- | --- | --- |
| In | prompt input JSON (str) | note text plus taxonomy instructions |
| Out | raw structured JSON (str) | {"final_label": "2 per month", "evidence": "about two seizures per month", ...} |

> This is the prediction boundary. row_trace.model_prediction.record retains the model's answer before any deterministic stage touches it.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:DspyCanonicalLlmExtractor`)
- Test: [`tests/test_gan2026_llm_pipeline.py`](../../../tests/test_gan2026_llm_pipeline.py)
- Proven in a trace by: `raw_output`, `row_trace.model_prediction.record`
- Paper wording: A single language-model call produces the final seizure-frequency label and its supporting evidence.

### 3. Repair JSON dialect and payload shape

`gan.llm.json_schema_repair` - rules-owned, transport/schema only, rule category `general`

Recover the JSON object from the raw output, repair Python-literal dialect, fix a known rationale key typo, coerce rule-family fields, and drop unsupported keys.

|  | Type | Example |
| --- | --- | --- |
| In | raw structured JSON (str) | output wrapped in prose, or using True/None instead of true/null |
| Out | payload dict | a dict matching the decision schema keys |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:parse_decision_json_with_trace`)
- Test: [`tests/test_gan2026_schema_repair.py`](../../../tests/test_gan2026_schema_repair.py)
- Proven in a trace by: `row_trace.format_repair.schema_payload_changed`, `row_trace.format_repair.events`
- Paper wording: Malformed model output is repaired at the transport and schema level only.

### 4. Validate the decision schema

`gan.llm.schema_validation` - rules-owned, gate, rule category `general`

Validate the repaired payload against the canonical decision record; a failure ends the row with no prediction.

|  | Type | Example |
| --- | --- | --- |
| In | payload dict | a dict missing the required final_label key |
| Out | CanonicalLlmDecisionRecord or a schema_validation_error | schema_validation_error: Field required |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:CanonicalLlmDecisionRecord`)
- Test: [`tests/test_gan2026_llm_pipeline.py`](../../../tests/test_gan2026_llm_pipeline.py)
- Proven in a trace by: `parse_errors`
- Paper wording: Decisions that do not validate against the schema are recorded as failures rather than scored.

### 5. Evidence-based label repair

`gan.llm.selected_evidence_repair` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Compare the model's final label with the evidence span it quoted and rewrite the label when the evidence supports a different rate.

|  | Type | Example |
| --- | --- | --- |
| In | model final_label plus model evidence | final_label '2 per month' with evidence 'two seizures in the past fortnight' |
| Out | repaired label (str) | '2 per 2 week' |

> The method is called LLM-only because the model owns the decision, but this stage is a clinical-meaning stage, not formatting. The row trace labels its rule_category 'benchmark_format', which understates it; the manifest is the authority. Reported in finding 4 of the 2026-07-30 review.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.normalize:repair_prediction_label_with_evidence`)
- Test: [`tests/test_gan2026_benchmark_prediction_repair_policy.py`](../../../tests/test_gan2026_benchmark_prediction_repair_policy.py)
- Proven in a trace by: `row_trace.deterministic_adapter.before_label`, `row_trace.deterministic_adapter.after_label`, `row_trace.deterministic_adapter.events`
- Paper wording: A single deterministic repair reconciles the model's label with the evidence span it selected; this repair can change the final clinical answer.

### 6. Check the label is scorable

`gan.llm.scorable_label_check` - rules-owned, gate, rule category `benchmark_format`

Parse the repaired label into a frequency record; an unparseable label is recorded as unscorable.

|  | Type | Example |
| --- | --- | --- |
| In | repaired label (str) | 'roughly a few a month' |
| Out | GanFrequencyRecord or an unscorable_final_label error | unscorable_final_label: unrecognized label |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/label_parser.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/label_parser.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser:label_to_frequency_record`)
- Test: [`tests/test_gan2026_labels.py`](../../../tests/test_gan2026_labels.py)
- Proven in a trace by: `parse_errors`
- Paper wording: Labels that cannot be parsed into the benchmark representation are recorded as unscorable.

### 7. Check evidence is an exact substring

`gan.llm.evidence_containment` - rules-owned, gate, rule category `general`

Require the model's quoted evidence to appear verbatim in the note text.

|  | Type | Example |
| --- | --- | --- |
| In | note text plus model evidence | evidence 'two seizures per month' against the note text |
| Out | bool | evidence_valid True |

- Code: [`src/clinical_extraction/core/evidence.py`](../../../src/clinical_extraction/core/evidence.py) (`clinical_extraction.core.evidence:evidence_is_substring`)
- Test: [`tests/test_core_evidence.py`](../../../tests/test_core_evidence.py)
- Proven in a trace by: `evidence_valid`, `row_trace.evidence_validation.exact_substring`
- Paper wording: Evidence is required to be an exact substring of the source note.

### 8. Project to Purist and Pragmatic scoring

`gan.llm.score` - scorer-owned, benchmark projection

Map the predicted and gold monthly frequencies into the Purist and Pragmatic categories and compare.

|  | Type | Example |
| --- | --- | --- |
| In | repaired label plus gold monthly frequency | predicted 2.0 per month, gold 2.0 per month |
| Out | per-row category comparison | purist_correct True, pragmatic_correct True |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/labels.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.labels:map_purist`)
- Test: [`tests/test_gan2026_labels.py`](../../../tests/test_gan2026_labels.py)
- Proven in a trace by: `comparison.purist_correct`, `comparison.pragmatic_correct`, `row_trace.scoring`
- Paper wording: Predictions are scored under the Purist and Pragmatic category projections.

## Code map

Entry point: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/llm.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/llm.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm:run_record`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `gan.llm.build_prompt` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:build_prompt_input` | `tests/test_gan2026_llm_prompt_hygiene.py` |
| `gan.llm.model_call` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:DspyCanonicalLlmExtractor` | `tests/test_gan2026_llm_pipeline.py` |
| `gan.llm.json_schema_repair` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:parse_decision_json_with_trace` | `tests/test_gan2026_schema_repair.py` |
| `gan.llm.schema_validation` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm:CanonicalLlmDecisionRecord` | `tests/test_gan2026_llm_pipeline.py` |
| `gan.llm.selected_evidence_repair` | `clinical_extraction.tasks.seizure_frequency.gan2026.normalize:repair_prediction_label_with_evidence` | `tests/test_gan2026_benchmark_prediction_repair_policy.py` |
| `gan.llm.scorable_label_check` | `clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser:label_to_frequency_record` | `tests/test_gan2026_labels.py` |
| `gan.llm.evidence_containment` | `clinical_extraction.core.evidence:evidence_is_substring` | `tests/test_core_evidence.py` |
| `gan.llm.score` | `clinical_extraction.tasks.seizure_frequency.gan2026.labels:map_purist` | `tests/test_gan2026_labels.py` |

## Not this method

These paths exist and are easy to mistake for this runner. They are named here so they cannot be read as it.

| Path | Role | Why it is not this runner |
| --- | --- | --- |
| `src/clinical_extraction/tasks/seizure_frequency/gan2026/runners/llm_only_canonical.py` | research entry point | CLI wrapper over run_split; adds no clinical stage. |

## Executable trace

See the [Gan 2026 teaching letters](../teaching_cases/gan2026.md), which run this method over the paper flagship letters and record what every stage above actually did.
