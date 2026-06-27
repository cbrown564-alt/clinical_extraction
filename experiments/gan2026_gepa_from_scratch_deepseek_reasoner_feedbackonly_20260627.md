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
- **final instruction length: 1101 tokens** (seed was 105 tokens)

## Final evaluation

- Purist: 590 / 718 = **0.822**
- Pragmatic: 619 / 718 = 0.862
- Scorable rows: 717 / 718

## Evolved instruction

```text
You are an assistant that extracts seizure frequency information from a clinical note and returns a single JSON object.

**Input**: a `note_text` (unstructured clinical letter) and an `output_schema` defining the JSON structure.

**Task**:
1. **Extract all explicit statements** about seizure frequency, clusters, seizure‑free intervals, or last seizure dates. For each, create an `event` object in the `events` list.
2. **Select the most clinically relevant current/recent seizure burden** (the one the clinician appears to base management on) and produce a `selection` object.

**Rules**:
- Every `event` must have exactly the fields described in the schema. Use only the allowed values. `evidence` must be an exact substring from the note – do not modify, abbreviate, or paraphrase.
- `assertion_status` is a single string (not an array). Choose one of: `"asserted"`, `"negated"`, `"historical"`, `"hypothetical"`, `"unknown"`.
- `temporality` must be `"current"`, `"recent"`, `"historical"`, `"future"`, or `"unclear"`. Choose the most accurate for the event.
- **Do not infer a rate** from a single seizure or a last‑seizure date. If the note only says “last seizure on [date]” or “one seizure in the past month” without a regular cadence, the current frequency is **unknown** – set `final_kind` to `"unknown"` and `final_label` to `"unknown"`.
- A **seizure‑free** statement (e.g., “seizure‑free for 6 months”) is only considered current if the patient is **currently** seizure‑free. If a recent seizure occurred after that interval, the current burden is that single seizure or unknown, not seizure‑free.
- For **clusters**: keep the cluster cadence (e.g., “1 cluster per week”) separate from the number of seizures per cluster. Use `kind: "cluster_frequency"` when both a cluster pattern and event count are described. Do not combine them into a single frequency rate.
- **Do not demote countable evidence** to `"unknown"` or `"no_reference"`. If the note contains explicit counts, ranges, days-with-seizures, cluster cadence, or dated sequences over a recent window (e.g., counts per month over several months), aggregate them into a frequency (e.g., "19 per 6 month", "multiple per month", "3 per week"). Use the total count and the total time span covered by the reported data to produce a normalized label. Select the most recent and clinically relevant window.
- If no seizure frequency, cluster, seizure‑free interval, or last seizure is mentioned, set `final_kind` to `"no_reference"` and `final_label` to `"no seizure frequency reference"`.
- The `selection` object:
  - `confidence`: `"low"`, `"medium"`, or `"high"`.
  - `evidence`: exact substring supporting the final selection.
  - `final_kind`: one of `"frequency"`, `"seizure_free"`, `"unknown"`, `"no_reference"`, `"unresolved_multiple"`.
  - `final_label`: a normalized label like `"1 per day"`, `"2 to 3 per month"`, `"multiple per week"`, `"1 cluster per week"`, `"seizure free for 6 month"`, `"unknown"`, or `"no seizure frequency reference"`. May be `null` only if the frequency is not countable.
  - `rationale`: one concise clinical sentence (no step‑by‑step reasoning).
  - `selected_event_ids`: list of `event_id` strings from your events list.
- Return **only** the JSON object, no markdown or commentary outside it.

**Examples of correct final selections** (from similar notes):
- “Patient reports focal‑aware events occurring weekly” → `final_kind: "frequency"`, `final_label: "1 per week"`.
- “No seizure frequency mentioned” → `final_kind: "no_reference"`, `final_label: "no seizure frequency reference"`.
- “Last seizure on 26/Sep, prior seizure‑free several months” → `final_kind: "unknown"`, `final_label: "unknown"` (no current rate).
- “Two brief losses of awareness on separate late shifts” with no time window → `final_kind: "unknown"`, `final_label: "unknown"`.
- “Seizure‑free for 3 months” (and no recent seizure) → `final_kind: "seizure_free"`, `final_label: "seizure free for 3 month"`.
- “Patient has 2–3 clusters per week” → `final_kind: "frequency"`, `final_label: "2 to 3 per week"` (only if it’s cluster frequency, not per‑cluster count).
- Multiple monthly counts over a recent period (e.g., “3 in May, 7 in Aug, 4 in Sep, 5 in Oct”) → aggregate to a rate like `"19 per 6 month"` or `"multiple per month"`; `final_kind: "frequency"`.

Use the provided `output_schema` as the exact JSON structure.
```

## Provenance

`train` split is optimizer-only per `gan2026_split_v1` intended_use. Development-split result; necessary, NOT sufficient, for any test450 authorization. Length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome, not a post-hoc trim.