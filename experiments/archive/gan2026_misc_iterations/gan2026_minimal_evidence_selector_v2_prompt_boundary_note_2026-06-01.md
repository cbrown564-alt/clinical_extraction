# Gan 2026 Minimal Evidence Selector V2 Prompt Boundary Note

Date: 2026-06-01

This note records the prompt-boundary decision after reviewing the
`llm_only_minimal_evidence_selector_v1` validation25 iteration.

## Decision

The minimal evidence selector should not ask the model to internalise Gan
normalisation or scorer-facing formatting rules. The model's first task is only
to identify the clinically relevant current/recent seizure-frequency answer and
copy exact evidence.

The model now emits a shallow source-near schema:

```json
{
  "answer": {
    "state": "frequency",
    "answer_text": "source-near selected answer text",
    "evidence": "exact note substring",
    "confidence": "high",
    "reason": "optional brief reason"
  },
  "supporting_facts": []
}
```

It no longer emits `answer.final_label`.

## Rationale

The v1 prompt recovered validation25 score by adding a parser-ready
`answer.final_label`, but the prompt drifted toward benchmark-specific examples
and normalisation rules. That risks overfitting a small development slice and
wasting model bandwidth on transformations that deterministic code already
handles.

The intended separation is:

- LLM: clinical selection, current/recent relevance, source-near answer text,
  exact evidence.
- Deterministic post-processing: number-word conversion, unit singularisation,
  upper-bound conventions, quarter-to-3-month conversion, every/each interval
  formatting, cluster-label repair, scorer parsing, and Purist/Pragmatic
  scoring.

## Implementation

`gan2026_llm_only_minimal_evidence_selector_v2` removes prompt references to:

- `answer.final_label`
- "prediction-bearing" language
- internal derived fields such as `cluster_axis`, `boundary_state`,
  `selector_decision`, `temporality`, `assertion_status`, `section`,
  `semiology`, and `uncertainty`
- validation25-shaped normalisation examples

The clean scorer-facing layer now derives labels with
`repair_prediction_label_with_evidence(...)` from the model-selected evidence.
This lets existing deterministic rules tidy representations without changing
which evidence the model selected.

## Current Caveat

This shifts remaining representation failures into the deterministic repair
surface, where they belong. A focused follow-up is to audit selected-evidence
repair coverage for compact source phrases, rather than adding those rules back
to the prompt.

## Verification

Focused minimal-selector tests passed after the boundary change:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_gan2026_llm_only_minimal_evidence_selector.py
```

Result: `10 passed`.
