# Gan 2026 Close-Off Report

Date: 2026-06-12

Status: synthesis and implementation plan. This report closes the current Gan
2026 development loop around the artifacts already produced. It does not
authorize new holdout use, row-level test inspection, or benchmark-facing claims
beyond the frozen aggregate reads already documented.

## Decision

The current promoted implementation direction is:

```text
hybrid_structured_events
```

This architecture is a hybrid, not a fully LLM-only pipeline: the model extracts
structured seizure-frequency events from raw note text, and the deterministic
Gan stack handles normalization, projection, rendering, and scoring. It is the
best close-off candidate because it combines high coverage, strong validation
accuracy, the best frozen `test450` aggregate result, and a comparatively simple
artifact contract.

The reset-native CandidateSet hybrid remains scientifically important because
it is the clearest auditable/verifier architecture, but it is not the operational
headline candidate for this close-off pass. Its accuracy on rendered rows is
competitive, but its null/routed surface is still too large.

## Evidence Summary

### GPT-4.1-mini Validation750

Source:
`experiments/gan2026_three_way_comparison_phase3_report_gpt41mini_validation750_2026-06-09.*`

| Architecture | Rendered | Purist of rendered | Pragmatic of rendered | Reading |
| --- | ---: | ---: | ---: | --- |
| `deterministic_canonical_pipeline` | 741/750 | 673/741 (0.908) | 681/741 (0.919) | High validation score after de-overfitting, but large holdout drop. |
| `hybrid` | 597/750 | 526/597 (0.881) | 545/597 (0.913) | Strong rendered accuracy, but too many null/routed rows. |
| `hybrid_structured_events` | 748/750 | 661/748 (0.884) | 679/748 (0.908) | Best LLM-using validation coverage and accuracy balance. |
| `llm_only_canonical_pipeline` | 750/750 | 582/750 (0.776) | 614/750 (0.819) | Useful comparator, not close to the hybrid candidates. |

### Frozen GPT-4.1-mini Test450

Source:
`experiments/gan2026_test450_phase4_comparison_report_gpt41mini_2026-06-10.*`

| Architecture | Rendered | Null | Routed | Purist of rendered | Pragmatic of rendered |
| --- | ---: | ---: | ---: | ---: | ---: |
| `deterministic_canonical_pipeline` | 450/450 | 0 | N/A | 329/450 (0.731) | 341/450 (0.758) |
| `hybrid` | 334/450 | 116 | 30 | 269/334 (0.805) | 281/334 (0.841) |
| `hybrid_structured_events` | 448/450 | 2 | N/A | 364/448 (0.812) | 381/448 (0.850) |
| `llm_only_canonical_pipeline` | 450/450 | 0 | N/A | 326/450 (0.724) | 346/450 (0.769) |

Reading: `hybrid_structured_events` leads the frozen aggregate audit on both
Purist and Pragmatic accuracy of rendered rows while keeping almost complete
coverage. This is the strongest current Gan 2026 result.

The deterministic pipeline's validation-to-test gap is the main generalization
warning: it leads validation after de-overfitting but drops below both hybrid
architectures on the locked aggregate audit. This supports the project thesis
that high validation performance from deterministic rules is incomplete evidence
without a holdout gap and rule-portability analysis.

### Cross-Model Validation

Source: ``

`hybrid_structured_events` is the strongest LLM-using architecture across all
three Phase 1 models:

| Model | `hybrid_structured_events` Purist of rendered | Main caveat |
| --- | ---: | --- |
| GPT-4.1-mini | 661/748 (0.884) | Best overall model/architecture pairing. |
| DeepSeek v4 flash | 609/742 (0.821) | Elevated seizure-free false positives. |
| Qwen 3.6 35B | 624/746 (0.836) | More conservative/unknown-prone than GPT. |

Follow-up prompt work on validation250 supports keeping the latest structured
events prompt:

- DeepSeek SE v0.6: +5/250 Purist-correct; seizure-free false positives halved.
- Qwen SE v0.6: +5/250 Purist-correct; unknown false positives nearly eliminated
  on that slice and seizure-free false positives reduced.

The Qwen CP v0.8 pass is a useful comparator improvement (+2/250), but not a
reason to replace `hybrid_structured_events` as the close-off candidate.

## Claim Boundaries

- Validation750 results are development evidence, not benchmark claims.
- The frozen `test450` audit is aggregate-only. No row-level holdout tuning is
  permitted from it.
- Evidence metrics are not uniform across architectures:
  - deterministic and structured-events runs report substring-style
    `evidence_valid`;
  - canonical LLM reports `evidence_text_contained`;
  - reset-native hybrid reports CandidateSet source-id validity from deep
    replay.
- `hybrid_structured_events` should be described as hybrid LLM extraction plus
  deterministic normalization/projection, not as fully LLM-only.
- The current close-off does not prove model independence. GPT-4.1-mini remains
  the best supported model for the promoted candidate.

## Implementation Plan To Finish

### P0 - Land The Close-Off State

1. Update `PROJECT_STATUS.md` so Gan close-off is the active objective again.
2. Add this report as the controlling Gan synthesis artifact.
3. Register this report in `experiments/registry.jsonl` as an analysis-only
   artifact.

### P1 - Optional Validation Confirmations

These are validation-only and should not block closing the current loop:

1. Run Qwen CP v0.8 validation750 if the project needs a cleaner read on whether
   `abstention_calibration` scales beyond validation250.
2. Run DeepSeek CP v0.7 / SE v0.6 validation750 only if the existing validation250
   improvement needs model-specific confirmation for a paper table.
3. Do not run another `test450` audit for these prompt versions unless a new
   frozen aggregate protocol is explicitly authorized.

### P2 - Paper-Facing Consolidation

1. Build or populate the Architecture Thesis Scorecard from existing artifacts:
   architecture, modularity/auditability signal, validation performance, frozen
   holdout performance, evidence trace caveats, and validation-to-test gap.
2. Produce a compact failure-mode table for the promoted candidate versus the
   deterministic and fully LLM comparators.
3. Preserve the deterministic de-overfitting result as a generalization lesson:
   removing Gan-specific rules intentionally reduced validation score but made
   the rule taxonomy more honest.

### P3 - Stop Rule

Gan 2026 is closed for this cycle when:

1. `PROJECT_STATUS.md` points to this report as the close-off control surface.
2. `hybrid_structured_events` is named as the promoted implementation direction.
3. Any additional validation750 model confirmations are either run or explicitly
   deferred.
4. ExECTv2 can resume with Gan treated as a completed foundation rather than an
   open experiment loop.

