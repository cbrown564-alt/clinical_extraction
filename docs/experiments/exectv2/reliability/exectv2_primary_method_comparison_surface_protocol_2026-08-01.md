# ExECTv2 primary method-comparison surface protocol (0046 evidence)

Date: 2026-08-01  
Status: complete; Phases A, B, and C finished 2026-08-01  
Governing decision:
[decision 0046](../../../decisions/0046-exect-primary-method-comparison-boundary.md)  
Parent:
[architecture index](../../../architecture/README.md)  
Glossary: [CONTEXT.md](../../../../CONTEXT.md)

## Primary question

What are the matched four-family `clinical_headline` numbers for the paper's
primary ExECT three-method comparison under decision 0046?

That comparison requires:

1. Sol LLM-only (`raw_lane_score`) and Sol hybrid (final) on `dev140` and
   `test60`;
2. the same stage pair for all six models on `test60` as a public aggregate
   panel;
3. rules-only four-family `clinical_headline` on `dev140` and aggregate-only
   `test60`.

This study materializes missing public artifacts. It does not change prompts,
family ownership, assembly policy, or scorers. It authorizes **no new model
calls**.

## Why this study

Decision 0046 demotes historical `v08` and GEPA from the primary method rows
and requires Sol-matched four-family `clinical_headline` peers. Sol hybrid and
`dev140` Sol LLM-only already exist in retained reports. Holdout LLM-only stage
scores exist only in sealed aggregates. Rules-only four-family
`clinical_headline` is not yet a selected public number on either split.

## Fixed conditions

- Dataset: ExECTv2; split manifest as used by the retained six-model panel.
- Scorer identity for primary cells: assembly `clinical_headline` /
  `headline_target` over Diagnosis, Seizure Frequency, Prescription, and
  Investigations.
- LLM-only identity: `raw_candidate` / `raw_lane_score` (not `source_scored`).
- Hybrid identity: final `headline_target` after selected deterministic family
  transforms under decision 0040 / 0041 and Diagnosis/Prescription
  `default` / `default` (decision 0045).
- Rules-only production: all-nine deterministic extractors may run;
  **restrict-and-rescore** — drop non-key entities before / for the peer score
  only. Do not invent a four-extractor-only method. Do not use
  `clinical_recovery_scorecard` overall as the Sol peer.
- Assembly policy: unchanged from the retained six-model panel.
- Cache / replay: no live model calls; A reads sealed aggregates only.

## Execution order (mandatory)

One protocol, three phases: **A → B → C**. Do not start B until A’s public
panel artifact is written. Do not start C until B’s `dev140` artifact is
written and checked.

### Phase A — public six-model `test60` stage panel

**Question.** What are aggregate `raw_lane_score` and final
`clinical_headline` for each of the six retained `test60` conditions?

**Row policy.** Aggregate-only. No test60 identifier, note, prediction,
evidence, error, or row slice may be printed, copied, or analyzed. Read only
sealed **aggregate** JSON (or already-sanitized local aggregates). Do not open
sealed row JSONL for this phase.

**Sources (hashes already recorded in
`experiments/hosted_holdout_panels_20260715.json` where applicable):**

| Slug | Aggregate source |
| --- | --- |
| `gpt41mini` | `scratch/holdout/exectv2_test60/gpt41mini/gpt41mini_aggregate.json` |
| `gpt56luna` | `scratch/holdout/exectv2_test60/gpt56luna/gpt56luna_aggregate.json` |
| `gpt56sol` | `scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol/gpt56sol_aggregate.json` |
| `deepseek_v4_flash` | `scratch/holdout/exectv2_test60/deepseek_v4_flash/deepseek_v4_flash_aggregate.json` |
| `qwen36_35b` | `scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b/qwen36_35b_aggregate.json` |
| `gemma4_26b` | `scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b/gemma4_26b_aggregate.json` |

**Required public artifact.**

- Directory: `experiments/exectv2_six_model_test60_stage_panel_20260801/`
- Machine panel: `panel_aggregate.json`
- Schema version: `exectv2.six_model_test60_stage_panel.v1`
- Per model: `raw_lane_score` overall F1 (and precision/recall if present),
  final `headline_target` / `clinical_headline` overall F1 (and
  precision/recall), optional four-family breakdowns if already present in the
  aggregate without row leakage, call/parse failure totals already public,
  source path + SHA-256 of the aggregate file read
- Claim boundary string on the artifact
- Short narrative:
  `docs/experiments/exectv2/reliability/exectv2_six_model_test60_stage_panel_2026-08-01.md`

**Stop rule (A).** Answer when all six models are in the public panel with
matching hashes for source aggregates. Reject if any step requires reading
sealed row JSONL. Revise once if a local sanitized aggregate uses a different
JSON shape but still exposes `raw_lane_score` and `headline_target` without row
fields.

### Phase B — rules-only four-family `clinical_headline` on `dev140`

**Question.** What is rules-only four-family `clinical_headline` F1 on
`dev140` under the Sol-matched `headline_target` surface?

**Row policy.** Development; row-level analysis permitted on `dev140` only.

**Method.**

1. Produce or reuse deterministic all-nine predictions for the manifest
   `dev140` letters (no model calls).
2. Restrict scored predictions to the four key families.
3. Score with the same assembly `headline_target` / `clinical_headline`
   machinery used for the six-model Sol hybrid cells.
4. Retain overall and per-family F1, plus a statement that five non-key
   entities were excluded from this peer score only.

**Required public artifact.**

- `experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json`
- Narrative:
  `docs/experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-15.md`
- Schema version: `exectv2.rules_only_four_family_clinical_headline.dev140.v1`

**Stop rule (B).** Answer when the machine artifact recomputes from code +
`dev140` without model calls and reports overall + four family F1. Reject if
the scorer silently includes non-key entities or uses
`clinical_recovery_scorecard` overall. Revise once if the assembly scorer needs
a thin adapter to accept rules-only `PredictedLetter` inputs without changing
match semantics.

### Phase C — rules-only four-family `clinical_headline` on `test60`

**Question.** What is rules-only four-family `clinical_headline` F1 on locked
`test60` under the same surface as B?

**Row policy.** Aggregate-only. The deterministic runner may read test note
text to extract and score, as the frozen six-model runner does, but **no**
test60 identifier, note, prediction, evidence, error, or row slice may leave
the sealed/ignored workspace into public docs or `experiments/` artifacts.
Public outputs are aggregates only.

**Method.** Same restrict-and-rescore rule as B. Prefer writing sealed per-run
outputs under
`scratch/holdout/exectv2_rules_only_four_family_test60_20260801/` and a public
aggregate JSON under `experiments/` that contains only totals.

**Required public artifact.**

- `experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json`
- Narrative:
  `docs/experiments/exectv2/reliability/exectv2_rules_only_four_family_clinical_headline_test60_2026-08-15.md`
- Schema version: `exectv2.rules_only_four_family_clinical_headline.test60.v1`

**Stop rule (C).** Answer when the public aggregate exists with overall + four
family F1 and an explicit aggregate-only claim boundary. Reject if any public
file contains letter IDs or row predictions. Blocked if instrumentation cannot
score `test60` without emitting row-level public artifacts — fix the writer,
do not relax the row policy.

## Primary table fills after completion

| Method | `dev140` | `test60` |
| --- | --- | --- |
| Rules only | Phase B overall F1 | Phase C overall F1 |
| LLM only (Sol) | retained `raw_lane_score` `0.8097` | Phase A Sol `raw_lane_score` |
| LLM with rules (Sol) | retained final `0.8920` | Phase A Sol final / hosted panel `0.8047` |

Six-model stage numbers from Phase A support the model panel; the primary
method table cites **Sol** only for LLM-only and hybrid.

## Out of scope

- New model calls, prompt edits, repair-policy changes, or scorer semantic
  changes
- Promoting `v08` or GEPA into primary method rows
- Nine-entity published-metric replay as a three-method peer
- Canon/manuscript edits (follow-on after artifacts exist)
- Phase 5 orchestrator refactoring

## Claim boundary

Development and aggregate holdout **measurement packaging** for decision 0046.
Positive completion supplies the missing primary-method cells. It does not
establish clinical validation, published ExECT benchmark reproduction, or
general model superiority. Hosted-versus-local route differences remain
disclosed for the six-model stage panel.

## Phase A result (2026-08-01)

Public panel written:

- [panel_aggregate.json](../../../experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json)
- [stage panel report](exectv2_six_model_test60_stage_panel_2026-08-01.md)
- Builder: `scripts/build_exectv2_six_model_test60_stage_panel.py`

Sol `test60`: LLM only (`raw_lane_score`) `0.7771`; hybrid final `0.8047`.
Hosted aggregate SHA-256 values matched the holdout panel record. Local Qwen
and Gemma sanitized aggregates drifted in bytes/hash but retained the same
public final `clinical_headline` F1; the stage panel records both hashes.

## Phase B result (2026-08-01)

- [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json)
- [report](exectv2_rules_only_four_family_clinical_headline_dev140_2026-08-15.md)
- Builder: removed in the 2026-08-16 scripts prune; living remasure is `scripts/build_exectv2_rules_only_four_family_clinical_headline_20260815.py` (recover the 2026-08-01 builder from git history if needed)
- Overall four-family `clinical_headline` F1: **0.8160**
  (Diagnosis 0.8599, SeizureFrequency 0.8323, Prescription 0.9615,
  Investigations 0.5325)

## Phase C result (2026-08-01)

- Public aggregate:
  [JSON](../../../experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json)
- [report](exectv2_rules_only_four_family_clinical_headline_test60_2026-08-15.md)
- Builder: removed in the 2026-08-16 scripts prune; living remasure is `scripts/build_exectv2_rules_only_four_family_clinical_headline_20260815.py` (recover the 2026-08-01 builder from git history if needed)
- Overall four-family `clinical_headline` F1: **0.7154**
  (Diagnosis 0.8550, SeizureFrequency 0.5797, Prescription 0.8395,
  Investigations 0.4037)
- Sealed predictions under
  `scratch/holdout/exectv2_rules_only_four_family_test60_20260801/` (ignored;
  not for row inspection)

## Completed primary fills

| Method | `dev140` | `test60` |
| --- | ---: | ---: |
| Rules only (four-family) | 0.8160 | 0.7154 |
| LLM only (Sol `raw_lane_score`) | 0.8097 | 0.7771 |
| LLM with rules (Sol final) | 0.8920 | 0.8047 |

## Next action

Update canon and manuscript method rows to decision 0046 using these
artifacts. Phase 5 / finding 1 remains a separate open branch.
