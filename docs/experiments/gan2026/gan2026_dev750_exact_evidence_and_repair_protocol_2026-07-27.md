# Gan 2026 dev750 exact-evidence and repair-provenance protocol

Date: 2026-07-27  
Status: frozen before new saved-output analysis

## Primary question

What does the Gan 2026 exact-evidence measure mean, why does Qwen 3.6:35B have
substantially fewer exact-evidence answers than GPT-5.6 Sol, what happens to
Qwen predictions when exact evidence is absent, and what do deterministic
repair notes record?

## Data and inspection policy

- Dataset: Gan 2026.
- Split: `dev750` (`validation750` in retained artifact identifiers).
- Manifest: `gan2026_split_v1`.
- Row policy: development row-level inspection is permitted.
- Primary models: `ollama_chat/qwen3.6:35b` and `openai/gpt-5.6-sol`.
- Context panel: all six retained `llm_with_rules` development runs.
- Method: `llm_with_rules` event-ledger pipeline; `llm_only` is used only where
  it clarifies whether a behavior is prompt- or representation-dependent.
- Calls: none; saved-output analysis only.
- Exclusion: no `test450` row may be opened or used for mechanism analysis.

## Inputs

- `experiments/gan2026_six_model_validation_20260718/*--llm_with_rules.jsonl`
- `experiments/gan2026_six_model_post_panel_attribution_20260720.json`
- evidence-validation implementation and tests in
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/` and `tests/`
- retained run reports and comparison summaries that define repair counts

## Definitions to verify

The report must derive the implemented definition of exact selected evidence
from code and traces. It must keep these concepts separate:

- non-empty evidence;
- exact source substring after the implemented normalization, if any;
- evidence attached to the model's selected answer;
- evidence attached to any extracted event;
- clinically decisive evidence;
- correct final label; and
- valid source identifier.

The report must derive the meaning and counting unit of repair notes from code
and saved artifacts. It must distinguish format-only repair, semantic
deterministic repair, final-label rendering/canonicalization, parse/schema
repair, and fallback or safety-floor decisions.

## Required analyses

- Exact-evidence rate for all six models on the same 750 development rows.
- For Qwen and Sol, every non-exact-evidence row classified by the first failed
  condition: empty/missing evidence, paraphrase or extra text, punctuation or
  whitespace mismatch, multiple-span synthesis, source-text mutation,
  wrong selected span, or another observed mechanism.
- Correctness and score-layer outcomes with and without exact evidence.
- Final-answer ownership on non-exact rows: preserved model choice,
  format-only deterministic rendering, prediction-bearing deterministic
  semantic change, fallback/safety floor, or unresolved failure.
- Whether deterministic code chooses the answer on most Qwen non-exact rows.
- Evidence-valid and evidence-invalid wrong-to-correct and correct-to-wrong
  transitions.
- Repair-note totals by event type and by number of affected rows, including
  zero-event rows and rows with multiple notes.
- Relationship between repair notes, exact evidence, and correctness; repair
  notes must not be interpreted as errors without row-level support.
- Representative row examples for every observed failure mechanism, using only
  permitted development rows.

## Machine artifact

One row represents one model-by-source-row evidence decision. Preserve model,
source row id, gold and predicted labels, raw and final correctness, selected
evidence, exact-match result, failure mechanism, deterministic events, final
answer owner, and whether fixed code changed the prediction-bearing clinical
decision.

## Stop rule and claim boundary

Stop if the six retained files do not each contain the same 750 unique manifest
rows, if exact-evidence status cannot be reproduced from the stored source note
and selected evidence, or if repair-event counts cannot be reconciled with the
retained reports. Otherwise report a development evidence/provenance answer.
Exact substring evidence is not clinical semantic validation. The study cannot
use or explain locked `test450` rows and cannot transfer development mechanisms
to the test evidence without a frozen audit.
