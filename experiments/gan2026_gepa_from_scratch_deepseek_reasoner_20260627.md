# GEPA from-scratch — gan2026_gepa_from_scratch_deepseek_reasoner_20260627

Date: 2026-06-27

DSPy-native GEPA run. The optimizable surface is the signature instruction; the deterministic schema-repair/normalize/purist stack is reused unchanged. Trained on the frozen `train` split (optimizer-only); evaluated on `validation` (development surface, NOT test450).

## Models

- Task model: `deepseek/deepseek-reasoner` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 287, valset 200)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 1200 tok (alpha 0.1)
- **final instruction length: 547 tokens** (seed was 105 tokens)

## Final evaluation

- Purist: 598 / 718 = **0.833**
- Pragmatic: 621 / 718 = 0.865
- Scorable rows: 717 / 718

## Evolved instruction

```text
You are an assistant that extracts seizure frequency information from clinical notes. Given a note_text and an output_schema, produce exactly one JSON object matching the schema. No markdown or commentary outside the JSON.

Rules for the `events` list:
- Each distinct seizure-frequency fact (stated frequency, cluster pattern, seizure-free interval, last event date, or explicit unknown frequency) is one event.
- For each event:
  - `assertion_status`: one of "asserted", "negated", "historical", "hypothetical", "unknown".
  - `temporality`: one of "current", "recent", "historical", "future", "unclear".
  - `evidence`: exact substring from note_text (including punctuation).
  - `raw_value`: near‑verbatim expression from the note (or null).
  - `kind`: one of "frequency_rate", "cluster_frequency", "seizure_free", "last_event_only", "unknown_frequency", "no_reference".
  - `applies_to`: seizure type or clinical target if specified, otherwise null.
  - `time_window`: source‑near temporal window (e.g., "past two months") or null.
  - `notes`: optional short note or null.

Rules for the `selection` object (single most clinically relevant seizure burden):
- `selected_event_ids`: list of one or more event_ids that together describe the burden.
- `final_kind`: one of "frequency", "seizure_free", "unknown", "no_reference", "unresolved_multiple".
- `final_label`: normalized string (e.g., "3 per week", "seizure free for 6 months", "unknown"); never null.
- `confidence`: "low", "medium", or "high".
- `evidence`: exact substring supporting the final label.
- `rationale`: one concise clinical sentence (not step‑by‑step).

Selection priorities:
1. Prefer explicit recent frequency (e.g., "3 per week") over generic seizure‑free when both appear. Only select "seizure_free" if sustained freedom with no recent countable seizures.
2. If multiple distinct seizure types/frequencies jointly represent current burden, use `final_kind: "unresolved_multiple"` and include all relevant event_ids.
3. Normalize numbers to digits; use standard phrasing ("seizure free since <date>" or "seizure free for <duration>").

Ensure all strings are properly escaped. Output only the JSON object.
```

## Provenance

`train` split is optimizer-only per `gan2026_split_v1` intended_use. Development-split result; necessary, NOT sufficient, for any test450 authorization. Length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome, not a post-hoc trim.