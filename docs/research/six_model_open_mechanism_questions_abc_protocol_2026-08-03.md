# Six-model open mechanism questions A–C protocol

Date: 2026-08-03  
Status: predeclared before attribution analysis  
Parent report:
[`six_model_comparison_report_2026-07-18.md`](six_model_comparison_report_2026-07-18.md)

## Primary questions

Answer the three open mechanism questions from the comparison report, in order:

| ID | Question |
| --- | --- |
| A | Why does ExECT rules lift fail to transfer from `dev140` to `test60`? |
| B | Why does GPT-4.1-mini suit Gan better than ExECT? |
| C | Which ExECT rules make Qwen competitive? |

One study answers all three because they share the same retained six-model
panel, the same development-only row policy, and the same ban on locked-holdout
row inspection. Each question still has its own stop rule and claim boundary.

## Why it matters

Finding 5 of the comparison report shows that ExECT’s large development-to-
holdout drop under LLM with rules is mostly rules lift that does not transfer.
Without family- and rule-class attribution, that finding cannot guide rule
retention, paper wording, or model selection. Mini’s mid-rank divergence and
Qwen’s larger holdout rules gain are the clearest task-shaped and rule-shaped
follow-ups.

## Data, split, and inspection permission

| Track | Split | Policy |
| --- | --- | --- |
| ExECTv2 | `dev140` | Row-level development analysis permitted |
| ExECTv2 | `test60` | Aggregate-only; no row inspection, quoting, or tuning |
| Gan 2026 | `dev750` (legacy id `validation750`) | Row-level development analysis permitted |
| Gan 2026 | `test450` | Aggregate-only; use locked totals for rank context only |

Replay mode: saved outputs and retained aggregates only. No new model calls,
prompt changes, gold changes, scorer changes, or rule edits are authorized.

## Candidates and fixed comparators

### Question A

- Candidate reading: rules lift by letter family on `dev140` versus aggregate
  family lift on `test60`.
- Fixed surfaces: ExECT LLM only (`raw_lane_score`) versus LLM with rules
  (`headline_target` / `clinical_headline`).
- Models: all six roster models in the July six-model ExECT panel. DeepSeek
  0731 holdout family LLM-only cells are absent; July DeepSeek family transfer
  is reported as July-panel evidence, not 0731-final.

### Question B

- Focal model: GPT-4.1-mini.
- Comparators: GPT-5.6 Sol and GPT-5.6 Luna (strong hosted models with nearly
  pure clinical-selection residuals on Gan).
- Gan evidence owner: matched v0.5 `dev750` panel and its first-failure owners.
  Do not silently mix historical v0.7 validation attribution with current-floor
  holdout scores.
- ExECT evidence owner: six-model `dev140` score ladders, pre-gate exact
  evidence, and SF state transitions.

### Question C

- Focal model: Qwen 3.6:35B.
- Comparator: GPT-5.6 Sol.
- Surfaces: family-level rules lift on both splits; `dev140` pre-gate quote
  repair/hard-drop; SF projection/suppression transitions; Diagnosis /
  Prescription changed-row category counts from retained aggregates.

## Component under study

Deterministic ExECT post-model rules and Gan deterministic reconstruction, with
model clinical selection and evidence selection as the residual owners. Rules
are safety/standardization floors, not a second extractor. Attribute
improvement to the first component that changes the answer.

## Scorer and metrics

| Question | Primary metric | Secondary |
| --- | --- | --- |
| A | Family F1 rules lift = final − LLM-only; transfer gap = test lift − dev lift | Overall lift gap; Investigations as near-zero control |
| B | Development mechanism contrast: Gan first-failure owners and deterministic rescue counts versus ExECT family F1 / pre-gate evidence / SF transitions | Locked aggregate ranks only as context |
| C | Qwen−Sol difference in family lift on `test60` and `dev140`; repair/drop counts; SF wrong→correct counts | Diagnosis/Prescription changed-row categories |

Scores remain two-decimal in narrative tables unless four-decimal source values
are needed for subtraction. Do not compare Gan Purist counts to ExECT F1 as if
they were the same scale.

## Minimal change

No pipeline change. Build one machine-readable attribution artifact from
retained JSON/JSONL and update the comparison report answers for A–C.

## Required analysis

1. Family-level rules lift on `dev140` and aggregate `test60` for all six
   models; identify which families lose transfer.
2. For Qwen versus Sol on `dev140`: SF state transitions, evidence
   repair/hard-drop classes, and aggregate changed-row categories by family.
3. For mini versus Sol/Luna: Gan matched v0.5 first-failure owners, model-
   boundary versus final Purist, deterministic wrong→correct / correct→wrong;
   ExECT LLM-only versus final family F1 and pre-gate evidence.
4. Representative permitted development examples only when needed to name the
   mechanism; no holdout rows.

## Artifact schema

Write
`experiments/six_model_open_mechanism_questions_abc_20260803.json` with:

- protocol path, date, commit or dirty-tree note, replay mode;
- per-model ExECT family lift table for both splits;
- Qwen-versus-Sol development mechanism block;
- mini cross-task mechanism block;
- stop-rule outcomes and claim boundaries for A–C;
- source artifact paths and hashes where available.

## Stop rules

| Outcome | When |
| --- | --- |
| Answer | Family-level transfer owners for A, task-shaped fit for B, and Qwen rule/family owners for C are identified from retained data |
| Negative | Evidence shows the open reading is wrong or uninformative |
| Revise | Retained instrumentation cannot separate families or rule classes needed for the claim |
| Reject | Would require holdout row inspection or new model calls outside scope |
| Blocked | Needed retained files missing or sealed |

Individual rule-ID transfer claims on `test60` are out of scope unless a
predeclared sealed aggregate ablation already exists. Development rule-class
findings may be stated as mechanisms inside families that lose transfer.

## Claim boundary if positive

- Diagnostic/development answer on named development distributions, with
  aggregate-only holdout family transfer for A and C.
- Not clinical validation, not published ExECT benchmark, not general model
  superiority, not proof that exact evidence is semantic support.
- Decision 0046 Sol ExECT method-row fills remain unchanged.
