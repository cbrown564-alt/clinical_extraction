<!-- GENERATED FILE. Do not edit by hand.
     Source: src/clinical_extraction/architecture/ (stage manifests +
     executed teaching cases). Regenerate with
     python scripts/build_architecture_docs.py -->

# Gan 2026 - LLM with rules

Method id: `gan2026_llm_with_rules`  
Role: **selected**  
Stages: 20  
Stages that may change clinical meaning: 11

## One sentence

> The model extracts the event history and chooses an answer; deterministic rules then check and sometimes correct that answer.

## Sixty seconds

One structured call returns two linked objects: an event ledger of source-near seizure-frequency facts, and a selection naming which event IDs won, the answer kind, the final label, evidence, confidence, and rationale. The model therefore makes the initial clinical selection - this is the single most misread fact about the method. Deterministic code then repairs JSON and schema, normalizes every event to a comparable rate, resolves an initial label from the model's chosen events, and runs ten named repair families in a fixed order. Each family can rewrite the final label, and each records a named event when it fires, so a changed answer is always attributable to one rule. The repaired label is checked for scorability and exact evidence, then projected to Purist and Pragmatic categories. Model owns the first answer; rules own every subsequent change to it.

## The five recall questions

| Question | Answer |
| --- | --- |
| What enters? | GanFrequencyRecord - see `gan.llm_with_rules.build_prompt` |
| Who first proposes the clinical answer? | the model proposes and selects (gan.llm_with_rules.model_call); ten deterministic repair families may change the answer afterwards |
| Which later stages may change clinical meaning? | `gan.llm_with_rules.repair.selected_evidence`, `gan.llm_with_rules.repair.monthly_diary`, `gan.llm_with_rules.repair.usual_interval`, `gan.llm_with_rules.repair.typical_over_ytd`, `gan.llm_with_rules.repair.breakthrough`, `gan.llm_with_rules.repair.non_epileptic`, `gan.llm_with_rules.repair.residual_jerk`, `gan.llm_with_rules.repair.post_change_burst`, `gan.llm_with_rules.repair.dated_sequence`, `gan.llm_with_rules.repair.elapsed_anchor` |
| What final representation is scored? | One Gan label string per letter, projected to a Purist and a Pragmatic category. |
| What evidence shows whether each component helped or harmed? | `docs/paper/decisions/gan-cleaned-request-is-the-cited-hybrid.md`, `docs/paper/methods.md`, `docs/paper/claims.md` |

## Stages

Read the `Effect` column first. `CLINICAL MEANING` marks every stage that can change the answer.

| # | Stage | Owner | Effect | What it does |
| --- | --- | --- | --- | --- |
| 1 | `gan.llm_with_rules.build_prompt`<br>Build the structured-events prompt | rules | transport/schema only | Render the note text and the event-ledger schema into the prompt input for one structured call. |
| 2 | `gan.llm_with_rules.model_call`<br>Model extracts events and selects the answer | model | CLINICAL MEANING | One structured call returns an event ledger plus a selection naming selected_event_ids, final_kind, final_label, evidence, confidence, and rationale. |
| 3 | `gan.llm_with_rules.json_schema_repair`<br>Repair JSON dialect and payload shape | rules | transport/schema only | Recover the JSON object, repair Python-literal dialect, repair the selected-answer payload shape, quarantine events that fail event-level validation, and drop unsupported keys. |
| 4 | `gan.llm_with_rules.format_only_retry`<br>Format-only retry (local models) | rules | transport/schema only | For local ollama-served models whose first output was unparseable, ask for a format-only repair of the same content and re-enter the parse path; the retry is accepted only if it validates. |
| 5 | `gan.llm_with_rules.schema_validation`<br>Validate the extraction schema | rules | gate | Validate the repaired payload against the structured extraction record; a failure ends the row with no prediction. |
| 6 | `gan.llm_with_rules.normalize_events`<br>Normalize every event | rules | representation | Convert each model event's source phrase into a comparable normalized rate; this runs over the whole ledger, not only the selected events. |
| 7 | `gan.llm_with_rules.resolve_label`<br>Resolve the label from the model's selection | rules | representation | Read the model's selected_event_ids and final_kind and resolve the initial label from the corresponding normalized events. |
| 8 | `gan.llm_with_rules.repair.selected_evidence`<br>Repair 1 - evidence-based label repair | rules | CLINICAL MEANING | Compare the resolved label with the model's quoted evidence span and rewrite the label when the evidence supports a different rate. |
| 9 | `gan.llm_with_rules.repair.monthly_diary`<br>Repair 2 - monthly diary | rules | CLINICAL MEANING | Derive a label from a month-by-month diary in the ledger and override the current label unless the existing label is preserved by the diary guard. |
| 10 | `gan.llm_with_rules.repair.usual_interval`<br>Repair 3 - usual interval | rules | CLINICAL MEANING | Convert a stated usual interval between seizures into a rate label when the ledger supports it. |
| 11 | `gan.llm_with_rules.repair.typical_over_ytd`<br>Repair 4 - typical rate over year-to-date | rules | CLINICAL MEANING | When the ledger holds both a typical recurring rate and a year-to-date total, prefer the typical recurring rate. |
| 12 | `gan.llm_with_rules.repair.breakthrough`<br>Repair 5 - breakthrough seizures | rules | CLINICAL MEANING | Handle letters where the current burden is expressed as breakthrough seizures against an otherwise controlled background. |
| 13 | `gan.llm_with_rules.repair.non_epileptic`<br>Repair 6 - non-epileptic events | rules | CLINICAL MEANING | Prevent events the ledger marks as non-epileptic from supplying the seizure-frequency answer. |
| 14 | `gan.llm_with_rules.repair.residual_jerk`<br>Repair 7 - residual jerks | rules | CLINICAL MEANING | Decide whether residual myoclonic jerks count toward the current seizure-frequency answer. |
| 15 | `gan.llm_with_rules.repair.post_change_burst`<br>Repair 8 - post-change burst | rules | CLINICAL MEANING | Handle a burst of seizures that follows a named medication or lifestyle change, so a transient burst does not become the current rate. |
| 16 | `gan.llm_with_rules.repair.dated_sequence`<br>Repair 9 - dated sequence | rules | CLINICAL MEANING | Derive a rate from a sequence of individually dated seizures and the window they span. |
| 17 | `gan.llm_with_rules.repair.elapsed_anchor`<br>Repair 10 - elapsed since anchor | rules | CLINICAL MEANING | When the selected answer is seizure-free since a dated anchor, count months from that date to the clinic date. A last-event rate rewrite can still be computed and then withheld by the sustained seizure-free guard. |
| 18 | `gan.llm_with_rules.scorable_label_check`<br>Check the label is scorable | rules | gate | Parse the repaired label into a frequency record; an unparseable label is recorded as unscorable. |
| 19 | `gan.llm_with_rules.evidence_containment`<br>Check evidence is an exact substring | rules | gate | Require the model's quoted selection evidence to appear verbatim in the note text. |
| 20 | `gan.llm_with_rules.score`<br>Project to Purist and Pragmatic scoring | scorer | benchmark projection | Map the predicted and gold monthly frequencies into the Purist and Pragmatic categories and compare. |

## Stage walkthrough

### 1. Build the structured-events prompt

`gan.llm_with_rules.build_prompt` - rules-owned, transport/schema only, rule category `general`

Render the note text and the event-ledger schema into the prompt input for one structured call.

|  | Type | Example |
| --- | --- | --- |
| In | GanFrequencyRecord | note text plus source row index |
| Out | prompt input JSON (str) | {"note_text": "...", "schema": {...}} |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:build_prompt_input`)
- Test: [`tests/test_gan2026_llm_prompt_hygiene.py`](../../../tests/test_gan2026_llm_prompt_hygiene.py)
- Proven in a trace by: `prompt_input_json`, `prompt_version`
- Paper wording: A single prompt requests a structured event ledger and an explicit selection.

### 2. Model extracts events and selects the answer

`gan.llm_with_rules.model_call` - model-owned, CLINICAL MEANING

One structured call returns an event ledger plus a selection naming selected_event_ids, final_kind, final_label, evidence, confidence, and rationale.

|  | Type | Example |
| --- | --- | --- |
| In | prompt input JSON (str) | note text plus the event-ledger schema |
| Out | raw structured JSON (str) | {"events": [{"event_id": "evt_1", ...}], "selection": {"selected_event_ids": ["evt_1"], "final_label": "2 per month"}} |

> The model, not a deterministic selector, makes the initial event selection. Finding 5 of the 2026-07-30 review reported a teaching fixture that attributed this to a deterministic component.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:DspyStructuredExtractor`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `raw_output`, `row_trace.model_prediction.record`
- Paper wording: A single language-model call produces a structured event ledger and an explicit selection of the current event.

### 3. Repair JSON dialect and payload shape

`gan.llm_with_rules.json_schema_repair` - rules-owned, transport/schema only, rule category `general`

Recover the JSON object, repair Python-literal dialect, repair the selected-answer payload shape, quarantine events that fail event-level validation, and drop unsupported keys.

|  | Type | Example |
| --- | --- | --- |
| In | raw structured JSON (str) | output using True/None, or an events list containing one malformed entry |
| Out | payload dict plus repair notes | a dict matching the structured extraction schema |

> Event quarantine removes entries that cannot validate. It is transport-level by contract, but it does reduce the ledger the model's selection can point at; quarantine notes are retained in parse_errors.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/schema_repair.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair:repair_structured_extraction_payload`)
- Test: [`tests/test_gan2026_schema_repair.py`](../../../tests/test_gan2026_schema_repair.py)
- Proven in a trace by: `row_trace.format_repair.schema_payload_changed`, `row_trace.format_repair.events`
- Paper wording: Malformed model output is repaired at the transport and schema level only.

### 4. Format-only retry (local models)

`gan.llm_with_rules.format_only_retry` - rules-owned, transport/schema only, rule category `general`

For local ollama-served models whose first output was unparseable, ask for a format-only repair of the same content and re-enter the parse path; the retry is accepted only if it validates.

|  | Type | Example |
| --- | --- | --- |
| In | malformed raw output plus the target schema | truncated JSON from a local model |
| Out | repaired JSON (str) or a rejection note | format_retry_rejected: schema_validation |

> Conditional. Fires only in live mode for models whose name starts with ollama_chat/.

- Code: [`src/clinical_extraction/core/local_structured_output.py`](../../../src/clinical_extraction/core/local_structured_output.py) (`clinical_extraction.core.local_structured_output:validate_format_retry`)
- Test: [`tests/test_exectv2_local_format_retry.py`](../../../tests/test_exectv2_local_format_retry.py)
- Proven in a trace by: `format_retry_output`, `format_retry_notes`
- Paper wording: Local-model outputs that fail to parse receive one format-only repair attempt, accepted only when it validates.

### 5. Validate the extraction schema

`gan.llm_with_rules.schema_validation` - rules-owned, gate, rule category `general`

Validate the repaired payload against the structured extraction record; a failure ends the row with no prediction.

|  | Type | Example |
| --- | --- | --- |
| In | payload dict | a payload whose selection lacks final_label |
| Out | StructuredExtractionRecord or a schema_validation_error | schema_validation_error: Field required |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:StructuredExtractionRecord`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `parse_errors`
- Paper wording: Extractions that do not validate against the schema are recorded as failures rather than scored.

### 6. Normalize every event

`gan.llm_with_rules.normalize_events` - rules-owned, representation, rule category `seizure_frequency`

Convert each model event's source phrase into a comparable normalized rate; this runs over the whole ledger, not only the selected events.

|  | Type | Example |
| --- | --- | --- |
| In | list[StructuredEventRecord] | event 'about two seizures per month' |
| Out | list[NormalizedEventRecord] | normalized label '2 per month', monthly_frequency 2.0 |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:_normalize_event`)
- Test: [`tests/test_gan2026_normalize_governance.py`](../../../tests/test_gan2026_normalize_governance.py)
- Proven in a trace by: `normalized_events`, `row_trace.deterministic_selection.normalized_events_field`
- Paper wording: Model-produced events are normalized to a common rate representation.

### 7. Resolve the label from the model's selection

`gan.llm_with_rules.resolve_label` - rules-owned, representation, rule category `seizure_frequency`

Read the model's selected_event_ids and final_kind and resolve the initial label from the corresponding normalized events.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus normalized events | selected_event_ids ['evt_1'], final_kind 'frequency_rate' |
| Out | resolved label (str) or None | '2 per month' |

> Representation, not selection: this stage renders the model's choice, it does not re-choose. If no selected event normalizes to a Gan label the row is recorded unscorable. row_trace.deterministic_selection retains both the model's own final_label and the resolved label so the two can be compared.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:_resolve_final_label`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_selection.selected_event_ids`, `row_trace.deterministic_selection.model_final_label`, `row_trace.deterministic_selection.resolved_label`
- Paper wording: The model's selection is resolved into a label using the normalized form of the events it selected.

### 8. Repair 1 - evidence-based label repair

`gan.llm_with_rules.repair.selected_evidence` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Compare the resolved label with the model's quoted evidence span and rewrite the label when the evidence supports a different rate.

|  | Type | Example |
| --- | --- | --- |
| In | resolved label plus selection evidence plus note text | label '2 per month' with evidence 'two seizures in the past fortnight' |
| Out | repaired label (str) | '2 per 2 week' |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/normalize.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.normalize:repair_prediction_label_with_evidence`)
- Test: [`tests/test_gan2026_selected_evidence_derivation.py`](../../../tests/test_gan2026_selected_evidence_derivation.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair reconciles the label with the evidence span the model selected.

### 9. Repair 2 - monthly diary

`gan.llm_with_rules.repair.monthly_diary` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Derive a label from a month-by-month diary in the ledger and override the current label unless the existing label is preserved by the diary guard.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label plus note text | ledger listing 3, 2, and 4 seizures in three named months |
| Out | repaired label (str) | '3 per month' |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_monthly_diary.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_monthly_diary.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_monthly_diary:monthly_diary_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair converts month-by-month diary entries into a single rate.

### 10. Repair 3 - usual interval

`gan.llm_with_rules.repair.usual_interval` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Convert a stated usual interval between seizures into a rate label when the ledger supports it.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label | 'he usually goes about six weeks between seizures' |
| Out | repaired label (str) | '1 per 6 week' |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:usual_interval_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair converts a stated usual interval into a rate.

### 11. Repair 4 - typical rate over year-to-date

`gan.llm_with_rules.repair.typical_over_ytd` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

When the ledger holds both a typical recurring rate and a year-to-date total, prefer the typical recurring rate.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label | 'typical pattern is a focal seizure monthly' alongside 'seven so far this year' |
| Out | repaired label (str) | '1 per month' |

> Policy A1 in docs/research/shared/clinical_selection_policy_catalog_2026-07-31.md. Unlike its neighbours this repair is not gated by a repair_config flag; it runs whenever its precondition holds.

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:typical_recurring_rate_over_ytd_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair prefers a stated typical recurring rate over a year-to-date total.

### 12. Repair 5 - breakthrough seizures

`gan.llm_with_rules.repair.breakthrough` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Handle letters where the current burden is expressed as breakthrough seizures against an otherwise controlled background.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label | 'seizure free apart from two breakthrough seizures this year' |
| Out | repaired label (str) | '2 per year' |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:breakthrough_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair resolves breakthrough-seizure phrasing against a controlled background.

### 13. Repair 6 - non-epileptic events

`gan.llm_with_rules.repair.non_epileptic` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Prevent events the ledger marks as non-epileptic from supplying the seizure-frequency answer.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label | ledger holding both epileptic seizures and dissociative episodes |
| Out | repaired label (str) | the epileptic rate, not the combined rate |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:non_epileptic_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair excludes events recorded as non-epileptic from the frequency answer.

### 14. Repair 7 - residual jerks

`gan.llm_with_rules.repair.residual_jerk` - rules-owned, CLINICAL MEANING, rule category `clinical_epilepsy`

Decide whether residual myoclonic jerks count toward the current seizure-frequency answer.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label plus note text | 'no generalised seizures but occasional morning jerks' |
| Out | repaired label (str) | the label the residual-jerk policy selects |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:residual_jerk_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair applies the residual-jerk policy to the frequency answer.

### 15. Repair 8 - post-change burst

`gan.llm_with_rules.repair.post_change_burst` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Handle a burst of seizures that follows a named medication or lifestyle change, so a transient burst does not become the current rate.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label plus note text | 'after the dose reduction he had four seizures in a week, none since' |
| Out | repaired label (str) | the settled post-burst rate |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:post_change_burst_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair separates a post-change seizure burst from the settled current rate.

### 16. Repair 9 - dated sequence

`gan.llm_with_rules.repair.dated_sequence` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

Derive a rate from a sequence of individually dated seizures and the window they span.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label plus note text | 'seizures on 3 January, 19 February and 28 March' |
| Out | repaired label (str) | '3 per 3 month' |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:dated_sequence_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair converts a dated seizure sequence into a rate over its observed window.

### 17. Repair 10 - elapsed since anchor

`gan.llm_with_rules.repair.elapsed_anchor` - rules-owned, CLINICAL MEANING, rule category `seizure_frequency`

When the selected answer is seizure-free since a dated anchor, count months from that date to the clinic date. A last-event rate rewrite can still be computed and then withheld by the sustained seizure-free guard.

|  | Type | Example |
| --- | --- | --- |
| In | StructuredExtractionRecord plus current label plus note text | 'Seizure-free since 27 March 2024' in a letter dated 29 September 2024 |
| Out | repaired label (str) | seizure free for 6 month |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_repair_families.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:elapsed_since_anchor_label_from_events`)
- Test: [`tests/test_gan2026_hybrid_structured_events_contract.py`](../../../tests/test_gan2026_hybrid_structured_events_contract.py)
- Proven in a trace by: `row_trace.deterministic_semantic.events`
- Paper wording: A deterministic repair converts a seizure-free since-date into a month duration against the clinic date.

### 18. Check the label is scorable

`gan.llm_with_rules.scorable_label_check` - rules-owned, gate, rule category `benchmark_format`

Parse the repaired label into a frequency record; an unparseable label is recorded as unscorable.

|  | Type | Example |
| --- | --- | --- |
| In | repaired label (str) | 'a few a month' |
| Out | GanFrequencyRecord or an unscorable_final_label error | unscorable_final_label: unrecognized label |

- Code: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/label_parser.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/contract/label_parser.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser:label_to_frequency_record`)
- Test: [`tests/test_gan2026_labels.py`](../../../tests/test_gan2026_labels.py)
- Proven in a trace by: `parse_errors`
- Paper wording: Labels that cannot be parsed into the benchmark representation are recorded as unscorable.

### 19. Check evidence is an exact substring

`gan.llm_with_rules.evidence_containment` - rules-owned, gate, rule category `general`

Require the model's quoted selection evidence to appear verbatim in the note text.

|  | Type | Example |
| --- | --- | --- |
| In | note text plus selection evidence | evidence 'about two seizures per month' against the note text |
| Out | bool | evidence_valid True |

> The evidence checked is the model's selection evidence, which the repair families do not rewrite. A repaired label can therefore carry evidence that motivated the model's original answer.

- Code: [`src/clinical_extraction/core/evidence.py`](../../../src/clinical_extraction/core/evidence.py) (`clinical_extraction.core.evidence:evidence_is_substring`)
- Test: [`tests/test_core_evidence.py`](../../../tests/test_core_evidence.py)
- Proven in a trace by: `evidence_valid`, `row_trace.evidence_validation.exact_substring`
- Paper wording: Evidence is required to be an exact substring of the source note.

### 20. Project to Purist and Pragmatic scoring

`gan.llm_with_rules.score` - scorer-owned, benchmark projection

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

Entry point: [`src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/llm_with_rules.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/orchestration/llm_with_rules.py) (`clinical_extraction.tasks.seizure_frequency.gan2026.orchestration.llm_with_rules:run_record`)

| Stage | Implementation | Governing test |
| --- | --- | --- |
| `gan.llm_with_rules.build_prompt` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:build_prompt_input` | `tests/test_gan2026_llm_prompt_hygiene.py` |
| `gan.llm_with_rules.model_call` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:DspyStructuredExtractor` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.json_schema_repair` | `clinical_extraction.tasks.seizure_frequency.gan2026.contract.schema_repair:repair_structured_extraction_payload` | `tests/test_gan2026_schema_repair.py` |
| `gan.llm_with_rules.format_only_retry` | `clinical_extraction.core.local_structured_output:validate_format_retry` | `tests/test_exectv2_local_format_retry.py` |
| `gan.llm_with_rules.schema_validation` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:StructuredExtractionRecord` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.normalize_events` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:_normalize_event` | `tests/test_gan2026_normalize_governance.py` |
| `gan.llm_with_rules.resolve_label` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events:_resolve_final_label` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.selected_evidence` | `clinical_extraction.tasks.seizure_frequency.gan2026.normalize:repair_prediction_label_with_evidence` | `tests/test_gan2026_selected_evidence_derivation.py` |
| `gan.llm_with_rules.repair.monthly_diary` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_monthly_diary:monthly_diary_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.usual_interval` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:usual_interval_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.typical_over_ytd` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:typical_recurring_rate_over_ytd_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.breakthrough` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:breakthrough_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.non_epileptic` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:non_epileptic_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.residual_jerk` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:residual_jerk_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.post_change_burst` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:post_change_burst_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.dated_sequence` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:dated_sequence_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.repair.elapsed_anchor` | `clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_structured_repair_families:elapsed_since_anchor_label_from_events` | `tests/test_gan2026_hybrid_structured_events_contract.py` |
| `gan.llm_with_rules.scorable_label_check` | `clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser:label_to_frequency_record` | `tests/test_gan2026_labels.py` |
| `gan.llm_with_rules.evidence_containment` | `clinical_extraction.core.evidence:evidence_is_substring` | `tests/test_core_evidence.py` |
| `gan.llm_with_rules.score` | `clinical_extraction.tasks.seizure_frequency.gan2026.labels:map_purist` | `tests/test_gan2026_labels.py` |

## Not this method

These paths exist and are easy to mistake for the selected method. They are named here so they cannot be read as it.

| Path | Role | Why it is not the selected method |
| --- | --- | --- |
| `src/clinical_extraction/tasks/seizure_frequency/gan2026/runners/hybrid_structured_events.py` | research entry point | CLI wrapper over run_split; adds no clinical stage. |
| `src/clinical_extraction/tasks/seizure_frequency/gan2026/experiments/repair_modes.py` | experiment control | Named repair modes switch repair families on and off for ablation. The selected comparison uses hybrid_full_stack. |
| `src/clinical_extraction/paper/cli.py` | replay path | python -m clinical_extraction.paper run --method gan_llm_with_rules --model <slug> --split <dev750\|test450> |

## Executable trace

See the [Gan 2026 teaching letters](../teaching_cases/gan2026.md), which run this method over the paper flagship letters and record what every stage above actually did.
