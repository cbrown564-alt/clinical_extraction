# Validation50 4800-Token Warning Forensics

- Source artifact: `experiments/gan2026_llm_only_typed_operations_reasoner_validation50_gpt41mini_v0_contractfix_max4800_2026-06-03.jsonl`
- Run: `llm_only_typed_operations_reasoner`, validation prefix 50, live `openai/gpt-4.1-mini`, `max_tokens=4800`.
- Terminal warnings observed before first 10-row checkpoint: two `LM response was truncated due to exceeding max_tokens=4800` messages; one also reported structured-output fallback to JSON mode.
- Limitation: DSPy warning logs did not include row ids, and failed raw completions are not persisted by the run artifact. The first 10 rows are therefore the warning window; row 103 is the only confirmed failed call in that window.

## First 10-Row Warning Window

```json
[
  {
    "call_error": null,
    "component_failures": {
      "scorer_format": "fail"
    },
    "graph_label": "4 per day",
    "ordinal": 1,
    "parse_errors": [],
    "raw_output_chars": 3090,
    "selected_evidence_valid": true,
    "source_row_index": 10,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {
      "evidence_exactness": "fail",
      "final_schema_rendering": "fail",
      "operation_extraction": "fail",
      "scorer_format": "fail"
    },
    "graph_label": "multiple per week",
    "ordinal": 2,
    "parse_errors": [
      "evidence: invalid operation evidence for ['op1']",
      "evidence: invalid selected evidence"
    ],
    "raw_output_chars": 2646,
    "selected_evidence_valid": false,
    "source_row_index": 40,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {
      "scorer_format": "fail"
    },
    "graph_label": "6 to 7 per year",
    "ordinal": 3,
    "parse_errors": [],
    "raw_output_chars": 3627,
    "selected_evidence_valid": true,
    "source_row_index": 79,
    "structured_record": true
  },
  {
    "call_error": "ValidationError: 5 validation errors for list[TypedOperationRecord]\n1.raw_phrase\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.temporality\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.assertion_status\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.certainty\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.operands\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing",
    "component_failures": {
      "final_schema_rendering": "fail",
      "operation_extraction": "fail",
      "operation_graph_projection": "fail",
      "operation_selection": "fail",
      "parse_schema": "fail",
      "scorer_format": "fail"
    },
    "graph_label": "no seizure frequency reference",
    "ordinal": 4,
    "parse_errors": [
      "not_run"
    ],
    "raw_output_chars": 0,
    "selected_evidence_valid": false,
    "source_row_index": 103,
    "structured_record": false
  },
  {
    "call_error": null,
    "component_failures": {},
    "graph_label": "17 per month",
    "ordinal": 5,
    "parse_errors": [],
    "raw_output_chars": 2634,
    "selected_evidence_valid": true,
    "source_row_index": 128,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {},
    "graph_label": "1 per 6 day",
    "ordinal": 6,
    "parse_errors": [],
    "raw_output_chars": 3392,
    "selected_evidence_valid": true,
    "source_row_index": 156,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {},
    "graph_label": "1 per 7 day",
    "ordinal": 7,
    "parse_errors": [],
    "raw_output_chars": 2607,
    "selected_evidence_valid": true,
    "source_row_index": 180,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {},
    "graph_label": "1 per 2 day",
    "ordinal": 8,
    "parse_errors": [],
    "raw_output_chars": 2644,
    "selected_evidence_valid": true,
    "source_row_index": 182,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {
      "scorer_format": "fail"
    },
    "graph_label": "1 per 7 to 9 day",
    "ordinal": 9,
    "parse_errors": [],
    "raw_output_chars": 3865,
    "selected_evidence_valid": true,
    "source_row_index": 187,
    "structured_record": true
  },
  {
    "call_error": null,
    "component_failures": {
      "scorer_format": "fail"
    },
    "graph_label": "1 per 4 week",
    "ordinal": 10,
    "parse_errors": [],
    "raw_output_chars": 5258,
    "selected_evidence_valid": true,
    "source_row_index": 190,
    "structured_record": true
  }
]
```

## Shared Task Instructions

```json
[
  "Extract source-near seizure-frequency operations from the note.",
  "Copy each evidence value as an exact substring from the note.",
  "Expose operands for event counts, windows, denominators, clusters, seizure freedom, anchors, semiology, and uncertainty.",
  "Select the operation set that best answers the requested policy while preserving clinical clarity.",
  "Keep frequency, seizure-free, unclear-frequency, no-reference, and unresolved-multiple states distinct.",
  "Return typed fields, not a string payload.",
  "Do not add any keys other than operations, selection, and final_answer.",
  "Do not copy note headers, patient identifiers, DOB fields, hospital numbers, NHS numbers, or letter boilerplate into typed output keys.",
  "Copy evidence using the exact visible characters from the note; do not emit escaped Unicode, HTML entities, backslash escapes, or control characters inside evidence strings.",
  "If final_answer.rendering_operands is present, include the same selected_evidence_id field required on operation operands."
]
```

## Shared Output Contract

```json
{
  "evidence_copy_rule": {
    "forbidden": [
      "\\u",
      "\\x",
      "HTML entities",
      "control characters",
      "normalized mathematical symbols"
    ],
    "required": "copy exact visible substrings from note_text"
  },
  "final_label_examples": [
    "4 per day",
    "1 per 7 to 9 day",
    "3 per 6 week",
    "multiple per month",
    "seizure free for 6 month",
    "unknown",
    "no seizure frequency reference"
  ],
  "forbidden_extra_keys": [
    "DOB",
    "Hospital No",
    "NHS No",
    "No",
    "clinic_date",
    "patient_name",
    "letter_text"
  ],
  "operation_kinds": [
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "last_event_only",
    "unknown_frequency",
    "no_reference"
  ],
  "operation_operand_fields": [
    "event_count_low",
    "event_count_high",
    "time_window_low",
    "time_window_high",
    "time_window_unit",
    "denominator_count",
    "denominator_unit",
    "cluster_size_low",
    "cluster_size_high",
    "seizure_free_duration_low",
    "seizure_free_duration_high",
    "seizure_free_duration_unit",
    "temporal_anchor",
    "semiology_grouping",
    "uncertainty_type",
    "selected_evidence_id"
  ],
  "pipeline_family": "llm_only_typed_operations_reasoner",
  "prompt_version": "gan2026_llm_only_typed_operations_reasoner_v0_contractfix",
  "rendering_operands_rule": "When final_answer.rendering_operands is non-null, it must include selected_evidence_id and that value must match a selected operation evidence_id.",
  "top_level_output_rule": "Do not add any keys other than operations, selection, and final_answer.",
  "top_level_outputs": [
    "operations",
    "selection",
    "final_answer"
  ],
  "trace_rule": "final_answer.selected_event_ids must equal selection.selected_operation_ids; selection.selected_evidence_id must name one selected operation evidence_id",
  "typed_output_schema_version": "typed_operations_v0"
}
```

## Row 40 End-to-End Trace

### Status

```json
{
  "call_error": null,
  "component_status": {
    "evidence_exactness": "fail",
    "final_schema_rendering": "fail",
    "operation_extraction": "fail",
    "operation_graph_projection": "ok",
    "operation_selection": "ok",
    "parse_schema": "ok",
    "scorer_format": "fail",
    "selected_operation_trace": "ok",
    "typed_operations_parse": "ok"
  },
  "ordinal_in_run": 2,
  "parse_errors": [
    "evidence: invalid operation evidence for ['op1']",
    "evidence: invalid selected evidence"
  ],
  "reference": {
    "gold_label": "4 per week",
    "gold_label_kind": "frequency",
    "gold_monthly_frequency": 17.380952380952383,
    "gold_normalized_label": "4 per week",
    "row_ok": true
  },
  "repair_changes": [
    {
      "from": "up to 4 seizures per week",
      "layer": "format_only",
      "to": "up to 4 per week"
    },
    {
      "from": "up to 4 seizures per week",
      "layer": "selected_evidence_arithmetic",
      "to": "multiple per week"
    },
    {
      "from": "up to 4 seizures per week",
      "layer": "typed_operation_graph_projection",
      "to": "multiple per week"
    }
  ],
  "score_layers": {
    "format_only": {
      "error": "Unparsable label (raw: 'up to 4 per week' / normalized: 'up to 4 per week')",
      "final_label": "up to 4 per week",
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema_plus_format_repair",
        "deterministic_semantic_repair": false,
        "repair_family": "format_preserving_label_repair",
        "repair_mode": "format_only",
        "scorer_facing": true,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "raw_llm": {
      "error": "Unparsable label (raw: 'up to 4 seizures per week' / normalized: 'up to 4 seizures per week')",
      "final_label": "up to 4 seizures per week",
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema",
        "deterministic_semantic_repair": false,
        "repair_family": "none",
        "repair_mode": "raw_llm",
        "scorer_facing": false,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "selected_evidence_arithmetic": {
      "final_label": "multiple per week",
      "gold_monthly_frequency": 17.380952380952383,
      "gold_pragmatic_category": "seizure_frequent",
      "gold_purist_category": "seizure_freq_more1week_less1day",
      "pragmatic_correct": false,
      "predicted_monthly_frequency": 1000.0,
      "predicted_pragmatic_category": "seizure_freq_unknown",
      "predicted_purist_category": "seizure_freq_unknown",
      "purist_correct": false,
      "repair_mode_metadata": {
        "attribution_source": "llm_selected_evidence_plus_arithmetic",
        "deterministic_semantic_repair": false,
        "repair_family": "selected_evidence_arithmetic_only",
        "repair_mode": "selected_evidence_arithmetic",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_selected_evidence_then_deterministic_arithmetic"
      },
      "scorable": true
    },
    "typed_operation_graph_projection": {
      "final_label": "multiple per week",
      "gold_monthly_frequency": 17.380952380952383,
      "gold_pragmatic_category": "seizure_frequent",
      "gold_purist_category": "seizure_freq_more1week_less1day",
      "pragmatic_correct": false,
      "predicted_monthly_frequency": 1000.0,
      "predicted_pragmatic_category": "seizure_freq_unknown",
      "predicted_purist_category": "seizure_freq_unknown",
      "purist_correct": false,
      "repair_mode_metadata": {
        "attribution_source": "llm_typed_operations_plus_deterministic_graph_projection",
        "deterministic_semantic_repair": true,
        "repair_family": "typed_operation_graph_projection",
        "repair_mode": "typed_operation_graph_projection",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_operation_selection_then_deterministic_graph_projection"
      },
      "scorable": true
    }
  }
}
```

### Model Input

```json
{
  "note_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 30 May 2016 \n\nDr Anita Kerr\nRiverside Medical Centre\n\n22 Riverside Walk, London, SE10 9AB\nDear Dr Anita Kerr\nMichael Carter, DOB: 21-11-1982, Hospital No: H837294 NHS No. 7845632190\nFlat 3, 14 Millstream Court, London, SE10 8PT \n\nI reviewed the above patient in the Neurology Clinic today. As you know he has generalised epilepsy. Since my last assessment he reports a variable pattern of episodes but overall a frequency of ≤ four seizures per week, typically brief generalised convulsions or absence episodes as described below. He has maintained good adherence to medication and has been keeping a diary which corroborates this frequency.\n\nHe describes two main event types: (1) abrupt loss of awareness with eyelid fluttering and brief behavioural arrest lasting 10–20 seconds, occurring in clusters on stressful days; and (2) generalised tonic–clonic seizures, usually from wakefulness, lasting around 60–90 seconds with post‑ictal fatigue and myalgia. There have been no focal warning symptoms, tongue biting is occasional, and injuries have been minor (one bruised shoulder last month). There is no clear menstrual or sleep‑deprivation trigger; however, he notes that missed meals and high caffeine intake may precipitate events. Family members have witnessed several episodes and confirm generalised onset without lateralising features.\n\nPast antiseizure medication side effects have been documented historically, including a pruritic rash with Lamotrigine (resolved on cessation) and gastrointestinal upset with Valproate (nausea and dyspepsia at higher doses). He is currently taking Levetiracetam 1 g b.d. and Clobazam 10 mg nocte. He reports mild irritability on Levetiracetam that is tolerable and denies current rash, visual disturbance, or significant gastrointestinal symptoms. No recent hospital admissions. He does not drive.\n\nExamination today was unremarkable with normal cognition, intact cranial nerves, and no focal neurological deficits. Weight and metabolic observations are stable. Previous EEG demonstrated generalised spike‑and‑wave discharges consistent with a generalised epilepsy syndrome; MRI brain (last year) was normal.\n\nPlan: We discussed ongoing self‑management and recording of events. Given the present pattern of ≤ four seizures per week and acceptable tolerability, he prefers to continue current therapy for now while we complete repeat EEG with hyperventilation and photic stimulation to re‑assess generalised activity. I have arranged this for the next available slot and requested medication levels and routine bloods (FBC, U&E, LFTs) to ensure no biochemical contributors. We also reviewed safety, seizure first aid, and avoidance of identified precipitants. He is aware of SUDEP information resources. Follow‑up is planned in 4 months, with earlier review if the frequency increases or new adverse effects occur.\n\nYours sincerely",
  "output_contract": {
    "evidence_copy_rule": {
      "forbidden": [
        "\\u",
        "\\x",
        "HTML entities",
        "control characters",
        "normalized mathematical symbols"
      ],
      "required": "copy exact visible substrings from note_text"
    },
    "final_label_examples": [
      "4 per day",
      "1 per 7 to 9 day",
      "3 per 6 week",
      "multiple per month",
      "seizure free for 6 month",
      "unknown",
      "no seizure frequency reference"
    ],
    "forbidden_extra_keys": [
      "DOB",
      "Hospital No",
      "NHS No",
      "No",
      "clinic_date",
      "patient_name",
      "letter_text"
    ],
    "operation_kinds": [
      "frequency_rate",
      "cluster_frequency",
      "seizure_free",
      "last_event_only",
      "unknown_frequency",
      "no_reference"
    ],
    "operation_operand_fields": [
      "event_count_low",
      "event_count_high",
      "time_window_low",
      "time_window_high",
      "time_window_unit",
      "denominator_count",
      "denominator_unit",
      "cluster_size_low",
      "cluster_size_high",
      "seizure_free_duration_low",
      "seizure_free_duration_high",
      "seizure_free_duration_unit",
      "temporal_anchor",
      "semiology_grouping",
      "uncertainty_type",
      "selected_evidence_id"
    ],
    "pipeline_family": "llm_only_typed_operations_reasoner",
    "prompt_version": "gan2026_llm_only_typed_operations_reasoner_v0_contractfix",
    "rendering_operands_rule": "When final_answer.rendering_operands is non-null, it must include selected_evidence_id and that value must match a selected operation evidence_id.",
    "top_level_output_rule": "Do not add any keys other than operations, selection, and final_answer.",
    "top_level_outputs": [
      "operations",
      "selection",
      "final_answer"
    ],
    "trace_rule": "final_answer.selected_event_ids must equal selection.selected_operation_ids; selection.selected_evidence_id must name one selected operation evidence_id",
    "typed_output_schema_version": "typed_operations_v0"
  },
  "task_instructions": [
    "Extract source-near seizure-frequency operations from the note.",
    "Copy each evidence value as an exact substring from the note.",
    "Expose operands for event counts, windows, denominators, clusters, seizure freedom, anchors, semiology, and uncertainty.",
    "Select the operation set that best answers the requested policy while preserving clinical clarity.",
    "Keep frequency, seizure-free, unclear-frequency, no-reference, and unresolved-multiple states distinct.",
    "Return typed fields, not a string payload.",
    "Do not add any keys other than operations, selection, and final_answer.",
    "Do not copy note headers, patient identifiers, DOB fields, hospital numbers, NHS numbers, or letter boilerplate into typed output keys.",
    "Copy evidence using the exact visible characters from the note; do not emit escaped Unicode, HTML entities, backslash escapes, or control characters inside evidence strings.",
    "If final_answer.rendering_operands is present, include the same selected_evidence_id field required on operation operands."
  ]
}
```

### Saved Raw Output

```json
{
  "final_answer": {
    "arithmetic_trace": "4 seizures/week * 4 weeks/month = 16 seizures/month",
    "combined_rationale": "The note provides a clear, current, and high-certainty frequency of up to 4 seizures per week, supported by patient diary and clinical assessment.",
    "final_rationale": "Selected the explicit current frequency statement with high certainty and no negation or uncertainty as the best clinical summary of seizure frequency.",
    "raw_clinical_summary": "Patient reports up to 4 seizures per week currently.",
    "raw_llm_final_kind": "frequency",
    "raw_llm_final_label": "up to 4 seizures per week",
    "raw_llm_monthly_frequency": 16.0,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 1.0,
      "denominator_unit": "week",
      "event_count_high": 4.0,
      "event_count_low": 0.0,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": null,
      "temporal_anchor": null,
      "time_window_high": 1.0,
      "time_window_low": 1.0,
      "time_window_unit": "week",
      "uncertainty_type": "none"
    },
    "selected_event_ids": [
      "op1"
    ],
    "selected_evidence": "overall a frequency of \u000264 seizures per week",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "overall a frequency of \u000264 seizures per week",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "up to 4 seizures per week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "week",
        "event_count_high": 4.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "week",
        "uncertainty_type": "none"
      },
      "operation_id": "op1",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u000264 seizures per week",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "frequency",
    "rationale": "The note explicitly states a current frequency of \u000264 seizures per week with high certainty and no negation or uncertainty, making this the clearest and most relevant frequency statement for clinical clarity.",
    "rejected_operation_ids": [],
    "selected_evidence": "overall a frequency of \u000264 seizures per week",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1"
    ],
    "selection_strategy": "current_highest_burden",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": []
  }
}
```

### Parsed Structured Record

```json
{
  "final_answer": {
    "arithmetic_trace": "4 seizures/week * 4 weeks/month = 16 seizures/month",
    "combined_rationale": "The note provides a clear, current, and high-certainty frequency of up to 4 seizures per week, supported by patient diary and clinical assessment.",
    "final_rationale": "Selected the explicit current frequency statement with high certainty and no negation or uncertainty as the best clinical summary of seizure frequency.",
    "raw_clinical_summary": "Patient reports up to 4 seizures per week currently.",
    "raw_llm_final_kind": "frequency",
    "raw_llm_final_label": "up to 4 seizures per week",
    "raw_llm_monthly_frequency": 16.0,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 1.0,
      "denominator_unit": "week",
      "event_count_high": 4.0,
      "event_count_low": 0.0,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": null,
      "temporal_anchor": null,
      "time_window_high": 1.0,
      "time_window_low": 1.0,
      "time_window_unit": "week",
      "uncertainty_type": "none"
    },
    "selected_event_ids": [
      "op1"
    ],
    "selected_evidence": "overall a frequency of \u000264 seizures per week",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "overall a frequency of \u000264 seizures per week",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "up to 4 seizures per week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "week",
        "event_count_high": 4.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "week",
        "uncertainty_type": "none"
      },
      "operation_id": "op1",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u000264 seizures per week",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "frequency",
    "rationale": "The note explicitly states a current frequency of \u000264 seizures per week with high certainty and no negation or uncertainty, making this the clearest and most relevant frequency statement for clinical clarity.",
    "rejected_operation_ids": [],
    "selected_evidence": "overall a frequency of \u000264 seizures per week",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1"
    ],
    "selection_strategy": "current_highest_burden",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": []
  }
}
```

### Evidence Summary

```json
{
  "event_evidence_invalid": [
    {
      "event_id": "op1",
      "evidence": "overall a frequency of \u000264 seizures per week"
    }
  ],
  "event_evidence_total": 1,
  "event_evidence_valid": 0,
  "selected_event_evidence_valid": true,
  "selected_evidence": "overall a frequency of \u000264 seizures per week",
  "selected_evidence_valid": false
}
```

### Typed Operation Graph Overlay

```json
{
  "competing_hypothesis_node_ids": [],
  "graph_builder": "llm_typed_operation_graph_overlay_v0",
  "missing_variable_flags": [
    "semiology_grouping",
    "temporal_anchor"
  ],
  "nodes": [
    {
      "applies_to": null,
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "overall a frequency of \u000264 seizures per week",
      "kind": "frequency_rate",
      "monthly_frequency": 1000.0,
      "node_id": "op:op1",
      "normalized_label": "multiple per week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "week",
        "event_count_high": 4.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "week",
        "uncertainty_type": "none"
      },
      "rule_id": "llm_typed_operation.1",
      "selected_evidence_id": "e1",
      "semantic_kind": "unresolved_multiple",
      "source_id": "op:op1",
      "temporality": "current"
    }
  ],
  "projection": {
    "evidence": "overall a frequency of \u000264 seizures per week",
    "final_kind": "unresolved_multiple",
    "final_label": "multiple per week",
    "monthly_frequency": 1000.0,
    "projection_policy": "gan2026_state_graph_projection_v0",
    "rationale": "Projected the graph from an unresolved multiple-frequency state node.",
    "selected_node_ids": [
      "op:op1"
    ],
    "uncertainty_flags": []
  }
}
```

## Row 79 End-to-End Trace

### Status

```json
{
  "call_error": null,
  "component_status": {
    "evidence_exactness": "ok",
    "final_schema_rendering": "ok",
    "operation_extraction": "ok",
    "operation_graph_projection": "ok",
    "operation_selection": "ok",
    "parse_schema": "ok",
    "scorer_format": "fail",
    "selected_operation_trace": "ok",
    "typed_operations_parse": "ok"
  },
  "ordinal_in_run": 3,
  "parse_errors": [],
  "reference": {
    "gold_label": "6 to 7 per year",
    "gold_label_kind": "frequency",
    "gold_monthly_frequency": 0.5416666666666666,
    "gold_normalized_label": "6 to 7 per year",
    "row_ok": true
  },
  "repair_changes": [
    {
      "from": "\u00026#8804; 6 to 7 seizures per year",
      "layer": "format_only",
      "to": "\u00026#8804; 6 to 7 per year"
    },
    {
      "from": "\u00026#8804; 6 to 7 seizures per year",
      "layer": "selected_evidence_arithmetic",
      "to": "6 to 7 per year"
    },
    {
      "from": "\u00026#8804; 6 to 7 seizures per year",
      "layer": "typed_operation_graph_projection",
      "to": "6 to 7 per year"
    }
  ],
  "score_layers": {
    "format_only": {
      "error": "Unparsable label (raw: '\\x026#8804; 6 to 7 per year' / normalized: '\\x026#8804; 6 to 7 per year')",
      "final_label": "\u00026#8804; 6 to 7 per year",
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema_plus_format_repair",
        "deterministic_semantic_repair": false,
        "repair_family": "format_preserving_label_repair",
        "repair_mode": "format_only",
        "scorer_facing": true,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "raw_llm": {
      "error": "Unparsable label (raw: '\\x026#8804; 6 to 7 seizures per year' / normalized: '\\x026#8804; 6 to 7 seizures per year')",
      "final_label": "\u00026#8804; 6 to 7 seizures per year",
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema",
        "deterministic_semantic_repair": false,
        "repair_family": "none",
        "repair_mode": "raw_llm",
        "scorer_facing": false,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "selected_evidence_arithmetic": {
      "final_label": "6 to 7 per year",
      "gold_monthly_frequency": 0.5416666666666666,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_more1per6mon_less1mon",
      "pragmatic_correct": true,
      "predicted_monthly_frequency": 0.5416666666666666,
      "predicted_pragmatic_category": "seizure_infrequent",
      "predicted_purist_category": "seizure_freq_more1per6mon_less1mon",
      "purist_correct": true,
      "repair_mode_metadata": {
        "attribution_source": "llm_selected_evidence_plus_arithmetic",
        "deterministic_semantic_repair": false,
        "repair_family": "selected_evidence_arithmetic_only",
        "repair_mode": "selected_evidence_arithmetic",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_selected_evidence_then_deterministic_arithmetic"
      },
      "scorable": true
    },
    "typed_operation_graph_projection": {
      "final_label": "6 to 7 per year",
      "gold_monthly_frequency": 0.5416666666666666,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_more1per6mon_less1mon",
      "pragmatic_correct": true,
      "predicted_monthly_frequency": 0.5416666666666666,
      "predicted_pragmatic_category": "seizure_infrequent",
      "predicted_purist_category": "seizure_freq_more1per6mon_less1mon",
      "purist_correct": true,
      "repair_mode_metadata": {
        "attribution_source": "llm_typed_operations_plus_deterministic_graph_projection",
        "deterministic_semantic_repair": true,
        "repair_family": "typed_operation_graph_projection",
        "repair_mode": "typed_operation_graph_projection",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_operation_selection_then_deterministic_graph_projection"
      },
      "scorable": true
    }
  }
}
```

### Model Input

```json
{
  "note_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025\n\nDr A. Patel\nCity Gate Health Centre\n\n12 City Gate, London EC1A 4ZZ\nDear Dr A. Patel\nMr Daniel Hughes, DOB: 14-03-1986, Hospital No: H928374 NHS No. 8473926150\nFlat 3, 29 Fleet Street, London EC4Y 1AA \n\nDiagnoses/summary: Combined generalised and focal epilepsy type – patient reports features of both generalised seizures (brief absences and occasional generalised tonic–clonic events) and focal aware/aware-impaired episodes with temporal features. Seizure frequency currently reported as ≤ 6 to 7 per year, typically clustering around periods of jet lag and sleep loss related to frequent business travel across time zones. Appointments are often conducted by telephone due to travel schedule.\n\nMRI brain (2018): structurally normal; no definite epileptogenic lesion identified.\nEEG (2020, routine): generalised spike–wave activity with intermittent left temporal sharp waves; photic stimulation unremarkable.\n\nPrevious medication: Sodium valproate (weight gain, tremor), carbamazepine (dizziness, hyponatraemia), levetiracetam (mood irritability), clobazam PRN for travel-related clusters, lamotrigine (partial benefit), lacosamide (no clear benefit), topiramate (cognitive slowing), zonisamide (insomnia), perampanel (mood change).\n\nNot taken: brivaracetam, cenobamate, eslicarbazepine, rufinamide, vigabatrin, tiagabine, pregabalin, primidone.\n\nComorbidities: Migraine without aura (stress/sleep-loss related). No known cardiac disease. No history of status epilepticus.\n\nI reviewed Mr Daniel Hughes via a scheduled telephone clinic today, as he is currently travelling for work. He reports his seizure burden remains ≤ 6 to 7 per year, with a recognisable pattern: brief focal aware episodes with déjà vu and epigastric rising lasting under a minute, and rarer generalised tonic–clonic seizures typically following multiple long-haul flights. He describes occasional brief absences noted by colleagues during videoconferences. He keeps a diary correlating events with irregular sleep, overnight flights, and caffeine excess. No injuries. No hospital admissions since last review.\n\nCurrent medicines:\n- Lamotrigine 150 mg twice daily\n- Brivaracetam 100 mg twice daily (initiated abroad three months ago; self-reported better tolerability than levetiracetam)\n- Clobazam 10 mg at night PRN for travel weeks (1–3 nights around long-haul flights)\n- Riboflavin 200 mg daily for migraine prophylaxis (self-initiated)\n\nTravel and lifestyle context: Works across Europe, the US, and Asia with frequent time zone shifts. Uses airline pre-boarding to reduce stress, wears medical ID, and adheres to local driving restrictions when abroad. Reports good medication adherence using phone reminders, but missed two doses in the last quarter during a delayed connection. Sleep remains irregular on multi-sector trips.\n\nPlan:\n- Continue lamotrigine and brivaracetam at current doses given tolerability and seizure frequency of ≤ 6 to 7 per year. Reinforced adherence strategies during flight disruptions (carry-on blister packs, duplicate alarm prompts, and setting local-time conversion reminders).\n- Clobazam PRN limited to travel-associated high-risk periods; advised on sedation risk and avoidance of alcohol when used.\n- Agreed to trial structured sleep hygiene across time zones (patient-led): maintaining dark/light cues, limiting late caffeine, and scheduling short naps on arrival days based on local time; patient prefers non-pharmacological measures.\n- Safety: reiterated water precautions, working at height, and local regulations for driving post-seizure when abroad; patient confirms compliance.\n- Investigations: No immediate further imaging required. If breakthrough frequency increases or semiology changes, consider prolonged ambulatory EEG to characterise both generalised and focal events during travel periods.\n- Follow-up: Telephone review in 4 months or earlier if two or more events occur within a month. Patient will forward seizure diary screenshots monthly via secure portal.\n\nThank you for your ongoing care and for assisting with prescription continuity while he is overseas. Please contact me if any issues arise.\n\nYours sincerely",
  "output_contract": {
    "evidence_copy_rule": {
      "forbidden": [
        "\\u",
        "\\x",
        "HTML entities",
        "control characters",
        "normalized mathematical symbols"
      ],
      "required": "copy exact visible substrings from note_text"
    },
    "final_label_examples": [
      "4 per day",
      "1 per 7 to 9 day",
      "3 per 6 week",
      "multiple per month",
      "seizure free for 6 month",
      "unknown",
      "no seizure frequency reference"
    ],
    "forbidden_extra_keys": [
      "DOB",
      "Hospital No",
      "NHS No",
      "No",
      "clinic_date",
      "patient_name",
      "letter_text"
    ],
    "operation_kinds": [
      "frequency_rate",
      "cluster_frequency",
      "seizure_free",
      "last_event_only",
      "unknown_frequency",
      "no_reference"
    ],
    "operation_operand_fields": [
      "event_count_low",
      "event_count_high",
      "time_window_low",
      "time_window_high",
      "time_window_unit",
      "denominator_count",
      "denominator_unit",
      "cluster_size_low",
      "cluster_size_high",
      "seizure_free_duration_low",
      "seizure_free_duration_high",
      "seizure_free_duration_unit",
      "temporal_anchor",
      "semiology_grouping",
      "uncertainty_type",
      "selected_evidence_id"
    ],
    "pipeline_family": "llm_only_typed_operations_reasoner",
    "prompt_version": "gan2026_llm_only_typed_operations_reasoner_v0_contractfix",
    "rendering_operands_rule": "When final_answer.rendering_operands is non-null, it must include selected_evidence_id and that value must match a selected operation evidence_id.",
    "top_level_output_rule": "Do not add any keys other than operations, selection, and final_answer.",
    "top_level_outputs": [
      "operations",
      "selection",
      "final_answer"
    ],
    "trace_rule": "final_answer.selected_event_ids must equal selection.selected_operation_ids; selection.selected_evidence_id must name one selected operation evidence_id",
    "typed_output_schema_version": "typed_operations_v0"
  },
  "task_instructions": [
    "Extract source-near seizure-frequency operations from the note.",
    "Copy each evidence value as an exact substring from the note.",
    "Expose operands for event counts, windows, denominators, clusters, seizure freedom, anchors, semiology, and uncertainty.",
    "Select the operation set that best answers the requested policy while preserving clinical clarity.",
    "Keep frequency, seizure-free, unclear-frequency, no-reference, and unresolved-multiple states distinct.",
    "Return typed fields, not a string payload.",
    "Do not add any keys other than operations, selection, and final_answer.",
    "Do not copy note headers, patient identifiers, DOB fields, hospital numbers, NHS numbers, or letter boilerplate into typed output keys.",
    "Copy evidence using the exact visible characters from the note; do not emit escaped Unicode, HTML entities, backslash escapes, or control characters inside evidence strings.",
    "If final_answer.rendering_operands is present, include the same selected_evidence_id field required on operation operands."
  ]
}
```

### Saved Raw Output

```json
{
  "final_answer": {
    "arithmetic_trace": "6 to 7 seizures per year translates to approximately 0.5 to 0.58 seizures per month (6/12=0.5, 7/12~0.58).",
    "combined_rationale": "The note consistently reports a seizure frequency of \u00026#8804; 6 to 7 per year with high certainty and current temporality. No conflicting or negated statements found.",
    "final_rationale": "Selected the consistent current seizure frequency range of \u00026#8804; 6 to 7 per year as the best clinical summary of seizure frequency.",
    "raw_clinical_summary": "Patient reports seizure frequency of \u00026#8804; 6 to 7 per year, consistent across note.",
    "raw_llm_final_kind": "frequency",
    "raw_llm_final_label": "\u00026#8804; 6 to 7 seizures per year",
    "raw_llm_monthly_frequency": 0.58,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 1.0,
      "denominator_unit": "year",
      "event_count_high": 7.0,
      "event_count_low": 6.0,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": null,
      "temporal_anchor": null,
      "time_window_high": 1.0,
      "time_window_low": 1.0,
      "time_window_unit": "year",
      "uncertainty_type": "range"
    },
    "selected_event_ids": [
      "op1",
      "op2"
    ],
    "selected_evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "6 to 7 seizures per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "operation_id": "op1",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u00026#8804; 6 to 7 per year",
      "temporality": "current"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "He reports his seizure burden remains ≤ 6 to 7 per year",
      "evidence_id": "e2",
      "model_normalized_clinical_label": "6 to 7 seizures per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "operation_id": "op2",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u00026#8804; 6 to 7 per year",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "frequency",
    "rationale": "Both operations report the same current seizure frequency range of \u00026#8804; 6 to 7 per year, consistent and high certainty. Selecting both for clinical clarity and completeness.",
    "rejected_operation_ids": [],
    "selected_evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1",
      "op2"
    ],
    "selection_strategy": "clinical_clarity",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": [
      "range"
    ]
  }
}
```

### Parsed Structured Record

```json
{
  "final_answer": {
    "arithmetic_trace": "6 to 7 seizures per year translates to approximately 0.5 to 0.58 seizures per month (6/12=0.5, 7/12~0.58).",
    "combined_rationale": "The note consistently reports a seizure frequency of \u00026#8804; 6 to 7 per year with high certainty and current temporality. No conflicting or negated statements found.",
    "final_rationale": "Selected the consistent current seizure frequency range of \u00026#8804; 6 to 7 per year as the best clinical summary of seizure frequency.",
    "raw_clinical_summary": "Patient reports seizure frequency of \u00026#8804; 6 to 7 per year, consistent across note.",
    "raw_llm_final_kind": "frequency",
    "raw_llm_final_label": "\u00026#8804; 6 to 7 seizures per year",
    "raw_llm_monthly_frequency": 0.58,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 1.0,
      "denominator_unit": "year",
      "event_count_high": 7.0,
      "event_count_low": 6.0,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": null,
      "temporal_anchor": null,
      "time_window_high": 1.0,
      "time_window_low": 1.0,
      "time_window_unit": "year",
      "uncertainty_type": "range"
    },
    "selected_event_ids": [
      "op1",
      "op2"
    ],
    "selected_evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "6 to 7 seizures per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "operation_id": "op1",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u00026#8804; 6 to 7 per year",
      "temporality": "current"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "He reports his seizure burden remains ≤ 6 to 7 per year",
      "evidence_id": "e2",
      "model_normalized_clinical_label": "6 to 7 seizures per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "operation_id": "op2",
      "operation_kind": "frequency_rate",
      "raw_phrase": "\u00026#8804; 6 to 7 per year",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "frequency",
    "rationale": "Both operations report the same current seizure frequency range of \u00026#8804; 6 to 7 per year, consistent and high certainty. Selecting both for clinical clarity and completeness.",
    "rejected_operation_ids": [],
    "selected_evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1",
      "op2"
    ],
    "selection_strategy": "clinical_clarity",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": [
      "range"
    ]
  }
}
```

### Evidence Summary

```json
{
  "event_evidence_invalid": [],
  "event_evidence_total": 2,
  "event_evidence_valid": 2,
  "selected_event_evidence_valid": true,
  "selected_evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
  "selected_evidence_valid": true
}
```

### Typed Operation Graph Overlay

```json
{
  "competing_hypothesis_node_ids": [
    "op:op1",
    "op:op2"
  ],
  "graph_builder": "llm_typed_operation_graph_overlay_v0",
  "missing_variable_flags": [
    "semiology_grouping",
    "temporal_anchor"
  ],
  "nodes": [
    {
      "applies_to": null,
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
      "kind": "frequency_rate",
      "monthly_frequency": 0.5416666666666666,
      "node_id": "op:op1",
      "normalized_label": "6 to 7 per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "rule_id": "llm_typed_operation.1",
      "selected_evidence_id": "e1",
      "semantic_kind": "frequency",
      "source_id": "op:op1",
      "temporality": "current"
    },
    {
      "applies_to": null,
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "He reports his seizure burden remains ≤ 6 to 7 per year",
      "kind": "frequency_rate",
      "monthly_frequency": 0.5416666666666666,
      "node_id": "op:op2",
      "normalized_label": "6 to 7 per year",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 1.0,
        "denominator_unit": "year",
        "event_count_high": 7.0,
        "event_count_low": 6.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": null,
        "temporal_anchor": null,
        "time_window_high": 1.0,
        "time_window_low": 1.0,
        "time_window_unit": "year",
        "uncertainty_type": "range"
      },
      "rule_id": "llm_typed_operation.2",
      "selected_evidence_id": "e2",
      "semantic_kind": "frequency",
      "source_id": "op:op2",
      "temporality": "current"
    }
  ],
  "projection": {
    "evidence": "Seizure frequency currently reported as ≤ 6 to 7 per year",
    "final_kind": "frequency",
    "final_label": "6 to 7 per year",
    "monthly_frequency": 0.5416666666666666,
    "projection_policy": "gan2026_state_graph_projection_v0",
    "rationale": "Projected the graph by selecting the highest current frequency node.",
    "selected_node_ids": [
      "op:op1"
    ],
    "uncertainty_flags": []
  }
}
```

## Row 103 End-to-End Trace

### Status

```json
{
  "call_error": "ValidationError: 5 validation errors for list[TypedOperationRecord]\n1.raw_phrase\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.temporality\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.assertion_status\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.certainty\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing\n1.operands\n  Field required [type=missing, input_value={'operation_id': 'op2', '...the current pattern is'}, input_type=dict]\n    For further information visit https://errors.pydantic.dev/2.12/v/missing",
  "component_status": {
    "evidence_exactness": "ok",
    "final_schema_rendering": "fail",
    "operation_extraction": "fail",
    "operation_graph_projection": "fail",
    "operation_selection": "fail",
    "parse_schema": "fail",
    "scorer_format": "fail",
    "selected_operation_trace": "ok",
    "typed_operations_parse": "ok"
  },
  "ordinal_in_run": 4,
  "parse_errors": [
    "not_run"
  ],
  "reference": {
    "gold_label": "2 to 4 per year",
    "gold_label_kind": "frequency",
    "gold_monthly_frequency": 0.25,
    "gold_normalized_label": "2 to 4 per year",
    "row_ok": true
  },
  "repair_changes": [
    {
      "from": "None",
      "layer": "typed_operation_graph_projection",
      "to": "no seizure frequency reference"
    }
  ],
  "score_layers": {
    "format_only": {
      "error": "missing_final_label",
      "final_label": null,
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema_plus_format_repair",
        "deterministic_semantic_repair": false,
        "repair_family": "format_preserving_label_repair",
        "repair_mode": "format_only",
        "scorer_facing": true,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "raw_llm": {
      "error": "missing_final_label",
      "final_label": null,
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema",
        "deterministic_semantic_repair": false,
        "repair_family": "none",
        "repair_mode": "raw_llm",
        "scorer_facing": false,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "selected_evidence_arithmetic": {
      "error": "missing_final_label",
      "final_label": null,
      "repair_mode_metadata": {
        "attribution_source": "llm_selected_evidence_plus_arithmetic",
        "deterministic_semantic_repair": false,
        "repair_family": "selected_evidence_arithmetic_only",
        "repair_mode": "selected_evidence_arithmetic",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_selected_evidence_then_deterministic_arithmetic"
      },
      "scorable": false
    },
    "typed_operation_graph_projection": {
      "final_label": "no seizure frequency reference",
      "gold_monthly_frequency": 0.25,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_more1per6mon_less1mon",
      "pragmatic_correct": false,
      "predicted_monthly_frequency": 1000.0,
      "predicted_pragmatic_category": "seizure_freq_unknown",
      "predicted_purist_category": "seizure_freq_unknown",
      "purist_correct": false,
      "repair_mode_metadata": {
        "attribution_source": "llm_typed_operations_plus_deterministic_graph_projection",
        "deterministic_semantic_repair": true,
        "repair_family": "typed_operation_graph_projection",
        "repair_mode": "typed_operation_graph_projection",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_operation_selection_then_deterministic_graph_projection"
      },
      "scorable": true
    }
  }
}
```

### Model Input

```json
{
  "note_text": "King's College Hospital \n\nDepartment of Neurosciences \n\nClinic Date: 13 September 2021 \n\nDr A. Reynolds\nConsultant Neurologist  \nKing's College Hospital  \nDepartment of Neurosciences, King's College Hospital, London SE5 9RS  \n\nDear Dr A. Reynolds\nConsultant Neurologist,  \n\nSarah Thompson, DOB: 14-03-1986, Hospital No: KCH728415 NHS No. 9075634218  \n12 Willow Crescent, London, SE15 2AB\n\nThank you for asking me to review your patient. I am pleased to report a sustained improvement in their overall stability and day‑to‑day functioning. The patient describes a calmer routine over recent months, with structured rest periods and regular time away from usual stressors. Travel and time set aside for relaxation were noted by the patient to improve general wellbeing; this is recorded here neutrally as part of the history.\n\nBy way of comparison, prior to this period the seizures were occurring every 1 or 2 weeks. Over the past year, however, the patient and family report that events have become markedly infrequent, such that the current pattern is ≤ two or four per year. This has translated into fewer unscheduled contacts and quicker return to baseline after brief episodes of disorientation. There have been no injuries, no hospital attendances, and no changes in speech, focal weakness, or memory beyond a short-lived post-event tiredness lasting minutes to an hour at most.\n\nMedication has remained unchanged, with good adherence reported. Sleep hygiene and pacing strategies have been continued. There is no recent intercurrent illness, no alcohol or substance use, and no clear precipitating factors identified. The patient keeps a simple diary, which aligns with the impression above. Examination in clinic today was unremarkable with stable observations, normal gait, and no lateralising neurological signs.\n\nOn balance, the clinical picture is of gradual improvement with a materially reduced event burden to ≤ two or four per year, compared with the earlier pattern of seizures every 1 or 2 weeks. I have advised continuation of the current approach and to maintain a consistent routine. The patient will continue to document any events and will let us know if there is any change in frequency, severity, or recovery pattern.\n\nI will plan routine follow‑up in six months, with earlier review if needed. Please do not hesitate to contact me if there are any concerns or if further information would be helpful.\n\nYours sincerely",
  "output_contract": {
    "evidence_copy_rule": {
      "forbidden": [
        "\\u",
        "\\x",
        "HTML entities",
        "control characters",
        "normalized mathematical symbols"
      ],
      "required": "copy exact visible substrings from note_text"
    },
    "final_label_examples": [
      "4 per day",
      "1 per 7 to 9 day",
      "3 per 6 week",
      "multiple per month",
      "seizure free for 6 month",
      "unknown",
      "no seizure frequency reference"
    ],
    "forbidden_extra_keys": [
      "DOB",
      "Hospital No",
      "NHS No",
      "No",
      "clinic_date",
      "patient_name",
      "letter_text"
    ],
    "operation_kinds": [
      "frequency_rate",
      "cluster_frequency",
      "seizure_free",
      "last_event_only",
      "unknown_frequency",
      "no_reference"
    ],
    "operation_operand_fields": [
      "event_count_low",
      "event_count_high",
      "time_window_low",
      "time_window_high",
      "time_window_unit",
      "denominator_count",
      "denominator_unit",
      "cluster_size_low",
      "cluster_size_high",
      "seizure_free_duration_low",
      "seizure_free_duration_high",
      "seizure_free_duration_unit",
      "temporal_anchor",
      "semiology_grouping",
      "uncertainty_type",
      "selected_evidence_id"
    ],
    "pipeline_family": "llm_only_typed_operations_reasoner",
    "prompt_version": "gan2026_llm_only_typed_operations_reasoner_v0_contractfix",
    "rendering_operands_rule": "When final_answer.rendering_operands is non-null, it must include selected_evidence_id and that value must match a selected operation evidence_id.",
    "top_level_output_rule": "Do not add any keys other than operations, selection, and final_answer.",
    "top_level_outputs": [
      "operations",
      "selection",
      "final_answer"
    ],
    "trace_rule": "final_answer.selected_event_ids must equal selection.selected_operation_ids; selection.selected_evidence_id must name one selected operation evidence_id",
    "typed_output_schema_version": "typed_operations_v0"
  },
  "task_instructions": [
    "Extract source-near seizure-frequency operations from the note.",
    "Copy each evidence value as an exact substring from the note.",
    "Expose operands for event counts, windows, denominators, clusters, seizure freedom, anchors, semiology, and uncertainty.",
    "Select the operation set that best answers the requested policy while preserving clinical clarity.",
    "Keep frequency, seizure-free, unclear-frequency, no-reference, and unresolved-multiple states distinct.",
    "Return typed fields, not a string payload.",
    "Do not add any keys other than operations, selection, and final_answer.",
    "Do not copy note headers, patient identifiers, DOB fields, hospital numbers, NHS numbers, or letter boilerplate into typed output keys.",
    "Copy evidence using the exact visible characters from the note; do not emit escaped Unicode, HTML entities, backslash escapes, or control characters inside evidence strings.",
    "If final_answer.rendering_operands is present, include the same selected_evidence_id field required on operation operands."
  ]
}
```

### Saved Raw Output

```text
No raw_output was persisted. The call raised before a TypedOperationsExtractionRecord could be saved.
```

### Parsed Structured Record

```text
No structured_record persisted.
```

### Evidence Summary

```json
{
  "event_evidence_invalid": [],
  "event_evidence_total": 0,
  "event_evidence_valid": 0,
  "selected_event_evidence_valid": false,
  "selected_evidence": null,
  "selected_evidence_valid": false
}
```

### Typed Operation Graph Overlay

```json
{
  "competing_hypothesis_node_ids": [],
  "graph_builder": "llm_typed_operation_graph_overlay_v0",
  "missing_variable_flags": [
    "no_typed_operations"
  ],
  "nodes": [],
  "projection": {
    "evidence": "",
    "final_kind": "no_reference",
    "final_label": "no seizure frequency reference",
    "monthly_frequency": 1000.0,
    "projection_policy": "gan2026_state_graph_projection_v0",
    "rationale": "Projected no-reference because the graph has no usable frequency nodes.",
    "selected_node_ids": [],
    "uncertainty_flags": []
  }
}
```

## Row 190 End-to-End Trace

### Status

```json
{
  "call_error": null,
  "component_status": {
    "evidence_exactness": "ok",
    "final_schema_rendering": "ok",
    "operation_extraction": "ok",
    "operation_graph_projection": "ok",
    "operation_selection": "ok",
    "parse_schema": "ok",
    "scorer_format": "fail",
    "selected_operation_trace": "ok",
    "typed_operations_parse": "ok"
  },
  "ordinal_in_run": 10,
  "parse_errors": [],
  "reference": {
    "gold_label": "1 per 4 week",
    "gold_label_kind": "frequency",
    "gold_monthly_frequency": 1.086309523809524,
    "gold_normalized_label": "1 per 4 week",
    "row_ok": true
  },
  "repair_changes": [
    {
      "from": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
      "layer": "format_only",
      "to": "seizure free for multiple year"
    },
    {
      "from": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
      "layer": "selected_evidence_arithmetic",
      "to": "1 per 4 week"
    },
    {
      "from": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
      "layer": "typed_operation_graph_projection",
      "to": "1 per 4 week"
    }
  ],
  "score_layers": {
    "format_only": {
      "final_label": "seizure free for multiple year",
      "gold_monthly_frequency": 1.086309523809524,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_1_per_mon",
      "pragmatic_correct": false,
      "predicted_monthly_frequency": 0.0,
      "predicted_pragmatic_category": "currently_no_seizure",
      "predicted_purist_category": "currently_no_seizure",
      "purist_correct": false,
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema_plus_format_repair",
        "deterministic_semantic_repair": false,
        "repair_family": "format_preserving_label_repair",
        "repair_mode": "format_only",
        "scorer_facing": true,
        "semantic_selection_owner": "llm"
      },
      "scorable": true
    },
    "raw_llm": {
      "error": "Unparsable cluster label: 'clusters of absence seizures every 4 weeks; last tonic–clonic seizure may 2025; seizure free since then'",
      "final_label": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
      "repair_mode_metadata": {
        "attribution_source": "raw_llm_scoring_schema",
        "deterministic_semantic_repair": false,
        "repair_family": "none",
        "repair_mode": "raw_llm",
        "scorer_facing": false,
        "semantic_selection_owner": "llm"
      },
      "scorable": false
    },
    "selected_evidence_arithmetic": {
      "final_label": "1 per 4 week",
      "gold_monthly_frequency": 1.086309523809524,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_1_per_mon",
      "pragmatic_correct": true,
      "predicted_monthly_frequency": 1.086309523809524,
      "predicted_pragmatic_category": "seizure_infrequent",
      "predicted_purist_category": "seizure_freq_1_per_mon",
      "purist_correct": true,
      "repair_mode_metadata": {
        "attribution_source": "llm_selected_evidence_plus_arithmetic",
        "deterministic_semantic_repair": false,
        "repair_family": "selected_evidence_arithmetic_only",
        "repair_mode": "selected_evidence_arithmetic",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_selected_evidence_then_deterministic_arithmetic"
      },
      "scorable": true
    },
    "typed_operation_graph_projection": {
      "final_label": "1 per 4 week",
      "gold_monthly_frequency": 1.086309523809524,
      "gold_pragmatic_category": "seizure_infrequent",
      "gold_purist_category": "seizure_freq_1_per_mon",
      "pragmatic_correct": true,
      "predicted_monthly_frequency": 1.086309523809524,
      "predicted_pragmatic_category": "seizure_infrequent",
      "predicted_purist_category": "seizure_freq_1_per_mon",
      "purist_correct": true,
      "repair_mode_metadata": {
        "attribution_source": "llm_typed_operations_plus_deterministic_graph_projection",
        "deterministic_semantic_repair": true,
        "repair_family": "typed_operation_graph_projection",
        "repair_mode": "typed_operation_graph_projection",
        "scorer_facing": true,
        "semantic_selection_owner": "llm_operation_selection_then_deterministic_graph_projection"
      },
      "scorable": true
    }
  }
}
```

### Model Input

```json
{
  "note_text": "KINGS NEUROSCIENCES CENTRE\n\n\nClinic Date: 02 October 2025 \n\nDr Wang\nSaffron Park Hospital\n\nSaffron Park, London, E14 7JL\nDear Dr Wang\nAlex Carter, DOB: 14-05-2006, Hospital No: P903772 NHS No. 7712390045\nFlat 3, 12 Kingsbridge Lane, London, E14 6PA \n\nI reviewed the above patient in the Adult Neurology Clinic today following transition from paediatric services. A parent attended and contributed helpful collateral history. He has a confirmed diagnosis of generalised epilepsy.\n\nThis is our first adult clinic review post-transition. From the joint handover summary and today’s history, his typical episodes comprise brief staring spells with eyelid flutter and occasional myoclonic jerks shortly after waking. Generalised tonic–clonic seizures have been infrequent. At present he reports clusters of brief absence episodes every 4 weeks, usually over 1–2 days, often precipitated by reduced sleep and academic stress. His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.\n\nHe is taking Sodium Valproate 500 mg b.d. and Levetiracetam (Keppra) 1 g b.d. with good adherence. He describes mild morning lethargy and intermittent low mood around examination periods, which he and his parent feel are manageable. No rashes, visual disturbance, or focal neurological symptoms were reported. There is no history of focal onset phenomena. He is not driving.\n\nOn examination today he was alert and oriented with normal speech and language. Cranial nerves were intact, tone and power were normal in all limbs, reflexes were symmetric, and coordination and gait were normal. There were no neurocutaneous stigmata.\n\nPaediatric EEGs have shown generalised spike–wave discharges, most recently in 2024. MRI brain (2023) was normal. We will arrange an updated EEG to reassess background and interictal activity in the adult service and to support ongoing management planning. Given his current pattern of absence clusters every 4 weeks without recent convulsions, I have not altered medication today. We discussed adherence, regular sleep, and stress management as practical measures that may help reduce breakthrough events. He and his parent were given information on our transition nurse specialist and epilepsy advisor should they wish to discuss education or lifestyle issues further.\n\nI have asked him to keep a simple seizure diary, noting any absence clusters and possible triggers, particularly sleep loss. We will review him in 6 months, or sooner if events increase in frequency, if he experiences any adverse effects, or if a generalised tonic–clonic seizure recurs.\n\nYours sincerely",
  "output_contract": {
    "evidence_copy_rule": {
      "forbidden": [
        "\\u",
        "\\x",
        "HTML entities",
        "control characters",
        "normalized mathematical symbols"
      ],
      "required": "copy exact visible substrings from note_text"
    },
    "final_label_examples": [
      "4 per day",
      "1 per 7 to 9 day",
      "3 per 6 week",
      "multiple per month",
      "seizure free for 6 month",
      "unknown",
      "no seizure frequency reference"
    ],
    "forbidden_extra_keys": [
      "DOB",
      "Hospital No",
      "NHS No",
      "No",
      "clinic_date",
      "patient_name",
      "letter_text"
    ],
    "operation_kinds": [
      "frequency_rate",
      "cluster_frequency",
      "seizure_free",
      "last_event_only",
      "unknown_frequency",
      "no_reference"
    ],
    "operation_operand_fields": [
      "event_count_low",
      "event_count_high",
      "time_window_low",
      "time_window_high",
      "time_window_unit",
      "denominator_count",
      "denominator_unit",
      "cluster_size_low",
      "cluster_size_high",
      "seizure_free_duration_low",
      "seizure_free_duration_high",
      "seizure_free_duration_unit",
      "temporal_anchor",
      "semiology_grouping",
      "uncertainty_type",
      "selected_evidence_id"
    ],
    "pipeline_family": "llm_only_typed_operations_reasoner",
    "prompt_version": "gan2026_llm_only_typed_operations_reasoner_v0_contractfix",
    "rendering_operands_rule": "When final_answer.rendering_operands is non-null, it must include selected_evidence_id and that value must match a selected operation evidence_id.",
    "top_level_output_rule": "Do not add any keys other than operations, selection, and final_answer.",
    "top_level_outputs": [
      "operations",
      "selection",
      "final_answer"
    ],
    "trace_rule": "final_answer.selected_event_ids must equal selection.selected_operation_ids; selection.selected_evidence_id must name one selected operation evidence_id",
    "typed_output_schema_version": "typed_operations_v0"
  },
  "task_instructions": [
    "Extract source-near seizure-frequency operations from the note.",
    "Copy each evidence value as an exact substring from the note.",
    "Expose operands for event counts, windows, denominators, clusters, seizure freedom, anchors, semiology, and uncertainty.",
    "Select the operation set that best answers the requested policy while preserving clinical clarity.",
    "Keep frequency, seizure-free, unclear-frequency, no-reference, and unresolved-multiple states distinct.",
    "Return typed fields, not a string payload.",
    "Do not add any keys other than operations, selection, and final_answer.",
    "Do not copy note headers, patient identifiers, DOB fields, hospital numbers, NHS numbers, or letter boilerplate into typed output keys.",
    "Copy evidence using the exact visible characters from the note; do not emit escaped Unicode, HTML entities, backslash escapes, or control characters inside evidence strings.",
    "If final_answer.rendering_operands is present, include the same selected_evidence_id field required on operation operands."
  ]
}
```

### Saved Raw Output

```json
{
  "final_answer": {
    "arithmetic_trace": "",
    "combined_rationale": "The note documents multiple seizure frequency states: current cluster frequency of absence seizures and seizure-free state for tonic–clonic seizures since May 2025. To preserve clinical clarity, all relevant operations are selected.",
    "final_rationale": "Multiple seizure frequency states coexist: clusters of absence seizures every 4 weeks and seizure freedom from tonic–clonic seizures since May 2025. This combined interpretation best reflects the clinical picture.",
    "raw_clinical_summary": "Patient has clusters of brief absence episodes every 4 weeks lasting 1-2 days, last generalised tonic–clonic seizure in May 2025, and no tonic–clonic seizures since then.",
    "raw_llm_final_kind": "unresolved_multiple",
    "raw_llm_final_label": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
    "raw_llm_monthly_frequency": null,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 4.0,
      "denominator_unit": "week",
      "event_count_high": null,
      "event_count_low": null,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": "absence episodes",
      "temporal_anchor": null,
      "time_window_high": 2.0,
      "time_window_low": 1.0,
      "time_window_unit": "day",
      "uncertainty_type": "none"
    },
    "selected_event_ids": [
      "op1",
      "op2",
      "op3"
    ],
    "selected_evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "absence clusters every 4 weeks over 1-2 days",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 4.0,
        "denominator_unit": "week",
        "event_count_high": null,
        "event_count_low": null,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": "absence episodes",
        "temporal_anchor": null,
        "time_window_high": 2.0,
        "time_window_low": 1.0,
        "time_window_unit": "day",
        "uncertainty_type": "none"
      },
      "operation_id": "op1",
      "operation_kind": "cluster_frequency",
      "raw_phrase": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
      "temporality": "current"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.",
      "evidence_id": "e2",
      "model_normalized_clinical_label": "last generalised tonic–clonic seizure May 2025",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 1.0,
        "event_count_low": 1.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "operation_id": "op2",
      "operation_kind": "last_event_only",
      "raw_phrase": "last generalised tonic–clonic seizure was in May 2025",
      "temporality": "historical"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "there have been none since",
      "evidence_id": "e3",
      "model_normalized_clinical_label": "seizure free since May 2025",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 0.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e3",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "operation_id": "op3",
      "operation_kind": "seizure_free",
      "raw_phrase": "there have been none since",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "unresolved_multiple",
    "rationale": "The note describes current clusters of absence episodes every 4 weeks over 1-2 days, a last generalised tonic–clonic seizure in May 2025, and no seizures since then. These represent multiple distinct seizure frequency states: cluster frequency for absence seizures and seizure-free state for tonic–clonic seizures. Selecting all three operations preserves clinical clarity and best represents the patient's seizure frequency status.",
    "rejected_operation_ids": [],
    "selected_evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1",
      "op2",
      "op3"
    ],
    "selection_strategy": "clinical_clarity",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": []
  }
}
```

### Parsed Structured Record

```json
{
  "final_answer": {
    "arithmetic_trace": "",
    "combined_rationale": "The note documents multiple seizure frequency states: current cluster frequency of absence seizures and seizure-free state for tonic–clonic seizures since May 2025. To preserve clinical clarity, all relevant operations are selected.",
    "final_rationale": "Multiple seizure frequency states coexist: clusters of absence seizures every 4 weeks and seizure freedom from tonic–clonic seizures since May 2025. This combined interpretation best reflects the clinical picture.",
    "raw_clinical_summary": "Patient has clusters of brief absence episodes every 4 weeks lasting 1-2 days, last generalised tonic–clonic seizure in May 2025, and no tonic–clonic seizures since then.",
    "raw_llm_final_kind": "unresolved_multiple",
    "raw_llm_final_label": "Clusters of absence seizures every 4 weeks; last tonic–clonic seizure May 2025; seizure free since then",
    "raw_llm_monthly_frequency": null,
    "rendering_operands": {
      "cluster_size_high": null,
      "cluster_size_low": null,
      "denominator_count": 4.0,
      "denominator_unit": "week",
      "event_count_high": null,
      "event_count_low": null,
      "seizure_free_duration_high": null,
      "seizure_free_duration_low": null,
      "seizure_free_duration_unit": null,
      "selected_evidence_id": "e1",
      "semiology_grouping": "absence episodes",
      "temporal_anchor": null,
      "time_window_high": 2.0,
      "time_window_low": 1.0,
      "time_window_unit": "day",
      "uncertainty_type": "none"
    },
    "selected_event_ids": [
      "op1",
      "op2",
      "op3"
    ],
    "selected_evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
    "supporting_event_ids": []
  },
  "operations": [
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
      "evidence_id": "e1",
      "model_normalized_clinical_label": "absence clusters every 4 weeks over 1-2 days",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 4.0,
        "denominator_unit": "week",
        "event_count_high": null,
        "event_count_low": null,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": "absence episodes",
        "temporal_anchor": null,
        "time_window_high": 2.0,
        "time_window_low": 1.0,
        "time_window_unit": "day",
        "uncertainty_type": "none"
      },
      "operation_id": "op1",
      "operation_kind": "cluster_frequency",
      "raw_phrase": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
      "temporality": "current"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.",
      "evidence_id": "e2",
      "model_normalized_clinical_label": "last generalised tonic–clonic seizure May 2025",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 1.0,
        "event_count_low": 1.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "operation_id": "op2",
      "operation_kind": "last_event_only",
      "raw_phrase": "last generalised tonic–clonic seizure was in May 2025",
      "temporality": "historical"
    },
    {
      "assertion_status": "asserted",
      "certainty": "high",
      "clinical_note": "",
      "evidence": "there have been none since",
      "evidence_id": "e3",
      "model_normalized_clinical_label": "seizure free since May 2025",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 0.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e3",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "operation_id": "op3",
      "operation_kind": "seizure_free",
      "raw_phrase": "there have been none since",
      "temporality": "current"
    }
  ],
  "selection": {
    "final_clinical_state": "unresolved_multiple",
    "rationale": "The note describes current clusters of absence episodes every 4 weeks over 1-2 days, a last generalised tonic–clonic seizure in May 2025, and no seizures since then. These represent multiple distinct seizure frequency states: cluster frequency for absence seizures and seizure-free state for tonic–clonic seizures. Selecting all three operations preserves clinical clarity and best represents the patient's seizure frequency status.",
    "rejected_operation_ids": [],
    "selected_evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
    "selected_evidence_id": "e1",
    "selected_operation_ids": [
      "op1",
      "op2",
      "op3"
    ],
    "selection_strategy": "clinical_clarity",
    "target_policy": "clinical_clarity",
    "uncertainty_flags": []
  }
}
```

### Evidence Summary

```json
{
  "event_evidence_invalid": [],
  "event_evidence_total": 3,
  "event_evidence_valid": 3,
  "selected_event_evidence_valid": true,
  "selected_evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
  "selected_evidence_valid": true
}
```

### Typed Operation Graph Overlay

```json
{
  "competing_hypothesis_node_ids": [
    "op:op1",
    "op:op2",
    "op:op3"
  ],
  "graph_builder": "llm_typed_operation_graph_overlay_v0",
  "missing_variable_flags": [
    "cluster_size",
    "event_count",
    "seizure_free_duration",
    "temporal_anchor"
  ],
  "nodes": [
    {
      "applies_to": "absence episodes",
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
      "kind": "cluster_frequency",
      "monthly_frequency": 1.086309523809524,
      "node_id": "op:op1",
      "normalized_label": "1 per 4 week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": 4.0,
        "denominator_unit": "week",
        "event_count_high": null,
        "event_count_low": null,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e1",
        "semiology_grouping": "absence episodes",
        "temporal_anchor": null,
        "time_window_high": 2.0,
        "time_window_low": 1.0,
        "time_window_unit": "day",
        "uncertainty_type": "none"
      },
      "rule_id": "llm_typed_operation.1",
      "selected_evidence_id": "e1",
      "semantic_kind": "frequency",
      "source_id": "op:op1",
      "temporality": "current"
    },
    {
      "applies_to": "generalised tonic–clonic seizure",
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "His last generalised tonic–clonic seizure was in May 2025 after a night of sleep deprivation, and there have been none since.",
      "kind": "last_event_only",
      "monthly_frequency": 1.086309523809524,
      "node_id": "op:op2",
      "normalized_label": "1 per 4 week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 1.0,
        "event_count_low": 1.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e2",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "rule_id": "llm_typed_operation.2",
      "selected_evidence_id": "e2",
      "semantic_kind": "frequency",
      "source_id": "op:op2",
      "temporality": "historical"
    },
    {
      "applies_to": "generalised tonic–clonic seizure",
      "assertion_status": "asserted",
      "certainty": "high",
      "evidence": "there have been none since",
      "kind": "seizure_free",
      "monthly_frequency": 1.086309523809524,
      "node_id": "op:op3",
      "normalized_label": "1 per 4 week",
      "operands": {
        "cluster_size_high": null,
        "cluster_size_low": null,
        "denominator_count": null,
        "denominator_unit": null,
        "event_count_high": 0.0,
        "event_count_low": 0.0,
        "seizure_free_duration_high": null,
        "seizure_free_duration_low": null,
        "seizure_free_duration_unit": null,
        "selected_evidence_id": "e3",
        "semiology_grouping": "generalised tonic–clonic seizure",
        "temporal_anchor": "May 2025",
        "time_window_high": null,
        "time_window_low": null,
        "time_window_unit": null,
        "uncertainty_type": "none"
      },
      "rule_id": "llm_typed_operation.3",
      "selected_evidence_id": "e3",
      "semantic_kind": "frequency",
      "source_id": "op:op3",
      "temporality": "current"
    }
  ],
  "projection": {
    "evidence": "clusters of brief absence episodes every 4 weeks, usually over 1–2 days",
    "final_kind": "frequency",
    "final_label": "1 per 4 week",
    "monthly_frequency": 1.086309523809524,
    "projection_policy": "gan2026_state_graph_projection_v0",
    "rationale": "Projected the graph by selecting the highest current frequency node.",
    "selected_node_ids": [
      "op:op1"
    ],
    "uncertainty_flags": []
  }
}
```
