# ExECTv2 Prescription rescue-scope candidate result

Date: 2026-07-15  
Decision: reject; do not disable Prescription residual additions

## Answer

Local frequency-cue precedence fixes the shared-evidence rescue-scope defect,
but it does not make unconditional removal of Prescription residual additions
safe. The candidate retained 37 of the comparator's 41 Prescription rescues
and produced 42 total rescues, but four comparator-correct rows became wrong.
The predeclared zero-regression gate therefore fails.

The default decision-0040 policy remains active. The local repair and residual
removal remain opt-in experiment behavior. No test60 row was assembled or
inspected, and no model was called.

## Fixed comparison

- Dataset and split: ExECTv2 dev140, with permitted row inspection.
- Inputs: saved GPT-4.1-mini, historical DeepSeek chat, and Qwen 3.6 35B repair
  v02 outputs.
- Comparator: current default decision-0040 model-led policy.
- Candidate: local selected-text frequency precedence plus removal of all
  deterministic Prescription residual additions.
- Fixed: every non-Prescription family, Prescription future/historical
  suppression, supported splitting and other normalization, gold, evidence
  checks, and scorers.
- Primary scorer: family-local `clinical_headline_unit_keys`.

## Gate result

| Gate | Result |
|---|---:|
| Prescription correct-to-wrong below 23 | pass: 17 |
| Prescription wrong-to-correct at least 36 | pass: 42 |
| Retain at least 36 of 41 comparator rescues | pass: 37 retained |
| Zero comparator-correct rows made wrong | **fail: 4** |
| Other families unchanged | pass: 0 changed rows |
| Exact evidence on every comparator-candidate change | pass: 18/18 |
| No new call, parse/schema, or fallback failure | pass |

Aggregate rescue counts cannot override the four direct regressions.

## Changed-row accounting

The candidate changed 18 model/family decisions, six for each saved model and
all in Prescription:

| Comparator direction | Candidate direction | Rows |
|---|---|---:|
| correct-to-wrong | unchanged | 6 |
| changed-still-wrong | wrong-to-correct | 4 |
| unchanged | wrong-to-correct | 1 |
| wrong-to-correct | unchanged | 4 |
| changed-still-wrong | unchanged | 2 |
| unchanged | changed-still-wrong | 1 |

The local rescue-scope repair contributes five new rescues and removes six
existing correct-to-wrong changes. Removing residual additions loses four
comparator rescues and creates the disqualifying regressions.

## Why the four residual rescues are not rescue-scope errors

- EA0096, DeepSeek and GPT-4.1-mini: the model emitted Topiramate 60 mg in the
  morning but omitted the paired 75 mg evening dose. Supported note-bound
  recovery supplied the second dose.
- EA0127, DeepSeek: the model omitted a current Lamotrigine 100 mg twice-daily
  regimen that exact note evidence supports.
- EA0150, Qwen: the model emitted only rescue Clobazam and omitted current
  Levetiracetam 1500 mg twice daily and Lamotrigine 200 mg twice daily from the
  same exact evidence span.

These are model candidate-generation omissions. Local frequency precedence
cannot recover facts that the model did not emit. The residual rules made the
first prediction-changing clinical decision on these facts, so the rescues are
deterministic-owned and the final rows are hybrid. Their value does not license
unbounded residual extraction, but it rules out unconditional removal.

## Scores

| Saved model | Comparator overall F1 | Candidate overall F1 | Comparator Prescription F1 | Candidate Prescription F1 |
|---|---:|---:|---:|---:|
| DeepSeek chat | 0.8747 | 0.8761 | 0.9268 | 0.9330 |
| GPT-4.1-mini | 0.8378 | 0.8389 | 0.8867 | 0.8922 |
| Qwen 3.6 35B repair v02 | 0.8565 | 0.8565 | 0.9481 | 0.9497 |

The aggregates are directionally positive, but the component regression gate
controls the decision.

## Architecture consequence

Do not remove Prescription residual additions as one undifferentiated group.
For the next candidate:

1. retain the currently demonstrated residual rescues with deterministic
   ownership;
2. keep local frequency-cue precedence as a separable repair candidate;
3. evaluate the explicit-current versus later-plan guard without changing
   candidate generation;
4. measure residual additions by rule and row so harmful additions can be
   removed without discarding demonstrated missing-regimen recovery.

## Artifacts

- Protocol: `docs/experiments/exectv2/reliability/exectv2_prescription_rescue_scope_candidate_protocol_2026-07-15.md`
- Machine-readable result: `experiments/exectv2_prescription_rescue_scope_candidate_dev140_20260715.json`
- Replay: `.venv\Scripts\python.exe scripts/check_exectv2_prescription_rescue_scope_candidate.py`

## Claim boundary

This is a development answer for three saved outputs on inspected dev140. It is
not holdout evidence, clinical validation, or evidence for the three unrun
models in the fixed roster.
