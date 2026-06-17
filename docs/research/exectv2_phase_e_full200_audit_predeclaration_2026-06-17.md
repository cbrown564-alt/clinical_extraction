# ExECTv2 — GPT-First Phase E: Reliability Scorecard + Full-200 Audit — Predeclaration

Date: 2026-06-17
Driver: `runners/run_reliability_scorecard.py` (scorecard in
`reports/reliability_scorecard.py`); projection ablation
`reports/cui_projection_diagnostic.py`; hybrid `hybrid/all_entity_assessment.py`
Split: dev (140) for the scorecard · **test (200) holdout: NOT triggered** ·
Model: gpt-4.1-mini · Temperature 0.0
Plan: [[09_gpt_first_execution_plan]] Phase E

## Purpose

Phase E produces the compact reliability scorecard for the GPT-first hybrid and
states, against a predeclared rule, whether the dev evidence clears the promotion
gate that authorizes a frozen full-200 (test holdout) audit. It also fixes the
audit protocol *in advance*, so that if and when the gate is met the holdout read
is a single confirmatory, immutable run with no protocol drift.

## Predeclared promotion gate (decides whether the audit runs at all)

The audit is authorized **only if** the dev140 hybrid clears the published
benchmark-comparable freeze targets on the **benchmark (with-CUI)** headline:

- per-item F1 ≥ 0.87, **and**
- per-letter F1 ≥ 0.90,

with no severe regression in an already-strong entity and evidence/parse
reliability high (per the plan's promotion gates). The gate is read from the
scorecard's `promotion_gate` block (`reliability_scorecard.build_scorecard`).

## Gate read (2026-06-17, dev140, gpt-4.1-mini candidates v0.4)

| Candidate set | Benchmark per-item F1 | Benchmark per-letter F1 | Gate met? |
| --- | ---: | ---: | --- |
| GPT-only (9 focused passes) | 0.181 (CI [0.165, 0.198]) | 0.420 | **No** |
| GPT + deterministic rule augmentation | 0.312 (CI [0.294, 0.333]) | 0.658 | **No** |

**Verdict: the gate is NOT met.** Both configurations sit far below the 0.87 /
0.90 freeze targets (best benchmark per-item 0.312, per-letter 0.658). Per the
plan and the locked-holdout discipline, **the full-200 test audit is NOT
authorized and was NOT run.** Scorecards:
`experiments/exectv2_hybrid_all_entities_dev140_gpt41mini_20260617{,_ruleaug}_scorecard.{md,json}`.

The binding constraints, named for the next cycle:

1. **Over-emission / precision** (the first hybrid target). The combined GPT
   candidate precision is ~0.23 (semantic); the deterministic gate cannot prune
   well-formed-but-spurious or altitude-mismatched candidates without choosing
   clinical facts — that is the deferred GPT candidate-selection pass, to be added
   only when an ablation earns the extra stage.
2. **Benchmark projection coverage** (Phase D). Gold CUI density is 1.00; the
   lexicon covers 60% of predictions at 0.90 agreement, so the with-CUI headline
   is coverage-gated. Closing it is in-sample CUI lookup, a documented projection
   artifact — not a route to a real gate pass.

## Predeclared audit protocol (frozen now; executes only if the gate is later met)

When a future cycle clears the dev gate, the confirmatory holdout read is:

- **Data**: the full 200-letter corpus via the frozen test split; `dev` is never
  used to tune after the gate is locked. Run once, no peeking, no re-runs.
- **Architecture**: the exact `hybrid/all_entity_assessment.py` configuration that
  cleared the dev gate (candidate prompt version, `augment_rules` flag, gate
  settings) — hash-pinned in the registry before the run, in the spirit of the
  gan2026 single-model preflight ([[gan2026_single_model_preflight]]).
- **Readout**: aggregate-only — overall + per-entity per-item/per-letter F1 at
  phrase/semantic/benchmark, the source-near candidate diagnostic, the CUI
  projection ablation, routed taxonomy, and per-letter bootstrap CIs on the
  benchmark headline. Report the dev→audit gap explicitly.
- **Claim discipline**: the benchmark (with-CUI) headline is the only
  benchmark-comparable number; CUI projection credit is reported separately and
  never as LLM clinical reasoning. Model-transfer to Qwen 3.6:35B is a *separate*
  experiment, run only after the GPT audit is locked.

## What is not claimed

Until the gate is met the honest claim stays the **transfer claim** (Gan
established the architecture and reliability discipline; ExECTv2 tests whether it
scales to broad phenotyping). No benchmark-beating claim is made on dev evidence,
and no holdout number exists.
