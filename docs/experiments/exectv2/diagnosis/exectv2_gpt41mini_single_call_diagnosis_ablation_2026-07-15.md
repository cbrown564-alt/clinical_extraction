# ExECTv2 GPT-4.1-mini single-call Diagnosis ablation

Date: 2026-07-15  
Status: dev140 no-call development result; gate failed, later selected by policy

## Answer

The retained structured event-ledger output should not replace the Diagnosis decomposer in its current form. It fails the predeclared Diagnosis F1 boundary and produces materially more letter-level regressions than rescues.

## Aggregate result

| Layer | Two-call Diagnosis F1 | Single-call Diagnosis F1 | Delta |
| --- | ---: | ---: | ---: |
| Raw candidate | 0.7702 | 0.7063 | -0.0639 |
| Evidence valid | 0.8727 | 0.8542 | -0.0185 |
| Clinical headline | 0.8727 | 0.8542 | -0.0185 |

Overall four-family F1 delta: `-0.0072`.

## Letter-level directions

- Wrong to correct: `3`
- Correct to wrong: `11`
- Changed but still wrong: `14`
- Unchanged correct: `77`
- Unchanged wrong: `35`

## Mechanism

- Missing-only regressions: `5`
- Extra-only regressions: `4`
- Replacement or mixed regressions: `2`
- Candidate exact-evidence letter rate: `1.0000`

Regressions include missed named Diagnosis concepts, extra non-target concepts, and mixed granularity replacements. Exact evidence was present, so the main failure is clinical selection rather than grounding.

The reviewed tags overlap representation and gold-label concerns, but the regressions also include previously identified extraction errors, missed named diagnoses, and non-target Diagnosis concepts. The fixed-score loss therefore cannot be attributed only to gold interpretation.

## Experimental decision

**reject** — The predeclared F1 or evidence-validity rejection boundary failed.

The predeclared experimental gate rejected the candidate. This result remains
negative evidence and is not rewritten as a gate pass.

## Subsequent architecture decision

[Decision 0041](../../../decisions/0041-single-call-exect-model-comparison.md)
selects the single structured call for the final six-model development
comparison. The accepted tradeoff is `-0.0185` Diagnosis F1 and `-0.0072`
overall F1 in this replay, in exchange for removing one model pass per letter.
This is a resource-policy choice; it does not establish measured cost or
latency savings and does not erase the 11 observed regressions.

## Split-control finding

The working-tree six-model runner selected `load_letters()[:140]`; only 94 IDs matched the manifest dev140 split. Affected active runs were stopped, their partial artifacts are not evidence, and the runner now selects manifest rows and rejects contaminated resume artifacts.

## Boundary

Development answer for retained GPT-4.1-mini ExECTv2 dev140 output under the fixed scorer and selected deterministic policy. No test60 row was assembled or inspected. This is not clinical validation, a published-benchmark result, or evidence for other models.

## Reproduction

- Protocol: `docs/experiments/exectv2/diagnosis/exectv2_gpt41mini_single_call_diagnosis_ablation_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_gpt41mini_single_call_diagnosis_ablation_dev140_20260715.json`
- Candidate assembly: `configs/exectv2/diagnosis_ablation/gpt41mini_single_call_dev140.json`
- Command: `.venv\Scripts\python.exe removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/check_exectv2_gpt41mini_single_call_diagnosis_ablation.py`)`
