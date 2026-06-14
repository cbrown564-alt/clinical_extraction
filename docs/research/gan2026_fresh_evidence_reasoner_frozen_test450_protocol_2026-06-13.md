# Gan 2026 V12 Frozen Test450 Audit Protocol

Date: 2026-06-13

Status: frozen-protocol authorization packet. This document does not authorize
the `test450` run by itself. It records the exact candidate, command, permitted
readout, and stop rule to use if the user explicitly authorizes the audit.

## Objective

Run one aggregate-only locked `test450` audit for V12
`fresh_evidence_reasoner` v0.4 after explicit authorization.

Success criterion:

- Purist at least `383/450` (`0.8511`), exceeding `0.85`.
- No row-level test error inspection or tuning after the readout.
- No deterministic final-label fallback.

## Frozen Candidate

- Pipeline: `fresh_evidence_reasoner`
- Prompt version: `gan2026_fresh_evidence_reasoner_v0_4`
- Safety gate version: `gan2026_fresh_evidence_safety_gate_v0_3`
- Model: `openai/gpt-4.1`
- Temperature: CLI default `0.0`
- Max tokens: `2800`
- Split manifest: `gan2026_split_v1`
- Prediction-bearing behavior: the model may keep the original GPT
  structured-event final or replace it with a direct final label grounded in
  exact raw-note evidence.
- Test structured-event source substrate: V12 uses split-aware frozen defaults
  for `test450`, not the validation defaults:
  - GPT:
    `experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl`
  - Qwen:
    `experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl`
  - DeepSeek test450 structured-event artifact is unavailable and is not
    loaded. The prompt therefore exposes the DeepSeek agent as a missing source
    on `test`, while validation used the available DeepSeek validation
    structured-event source.
- Deterministic code role: prompt assembly, JSON/schema repair, format-only
  label repair, exact-substring evidence filtering, predeclared safety gates,
  rendering, and scoring.
- Fallback policy: original GPT structured-event LLM final only. Deterministic
  top labels are not shown to the model and are not used as final fallback.

## Freeze Evidence

Validation ladder passed before this protocol:

| Surface | V12 Purist | V0 Purist | Notes |
| --- | ---: | ---: | --- |
| validation25 | `25/25` | `25/25` | Contract smoke, no regressions |
| fixed hard50 | `42/50` | `39/50` | `3` wrong-to-correct, `0` correct-to-wrong |
| validation250 | `242/250` | `236/250` | `8` wrong-to-correct, `3` correct-to-wrong |
| validation750 | `682/750` | `661/750` | `42` wrong-to-correct, `22` correct-to-wrong |

Full validation750 artifact:

- JSONL:
  `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl`
- Report:
  `experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md`

Validation750 summary:

- Rows: `750`
- Prediction-bearing rows: `749`
- Model calls attempted: `750`
- Call failures: `0`
- Parse/schema/label failures: `0`
- Raw model Purist: `676/750`
- Format-only Purist: `676/750`
- Final Purist: `682/750`
- V0 Purist: `661/750`
- Final Pragmatic: `698/750`
- V0 Pragmatic: `679/750`
- Changed labels versus V0: `147`
- Changed-label precision versus V0: `0.2857`
- Exact evidence substrings: `703/750`
- Fresh-evidence replacement actions: `182`
- Evidence-gate fallbacks: `8`

## Current-State Hashes

Repository HEAD when this protocol was written:

```text
6f80af0e1e9974550f0abd322202d9c62496a000
```

The working tree contains uncommitted Gan 2026 experiment work. The following
SHA-256 hashes pin the frozen V12 code and validation artifact state:

```text
47a2a93db9641e582727a32c2230045341695b851183f9ae4029dade81a6c6ab  src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/fresh_evidence_reasoner.py
a191d9e4e364cd0d628a28c3788717dcca44081593c349cf1b92659dd1a7a8fd  src/clinical_extraction/tasks/seizure_frequency/gan2026/runner.py
ea509667aeb1e3485f0d8c6fc2456a709fa216ed3e5a91b55885b7a1cc70e598  src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/llm_pipeline_cli.py
4a317b2a56901510052aa77a78552909395f8931ec75a8564667ee65465ec4b0  src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/frozen_test_preflight.py
7aecd6a21886843d4d576421b8644f2a678e768c1b9b3c5ca74f03ce567b08e0  src/clinical_extraction/tasks/seizure_frequency/gan2026/cli/frozen_test_readout.py
7be9e3f53830ae034d0003f1de98c2f8e7e6819eb6c91a38ae9b48b02640417a  tests/test_gan2026_fresh_evidence_reasoner.py
3ea21277afc085ca997b963996da2874f297fd90672ad1b6405ff69a19c88d83  tests/test_gan2026_llm_pipeline_cli.py
bebaf896be847c854d22c90e1669f1a93ec3ed797215993c8be623c386aed355  tests/test_gan2026_frozen_test_preflight.py
821ded174c3f45d6524edaae78cd337a4469cb5b62fa55847c1c058db592f264  tests/test_gan2026_frozen_test_readout.py
d89634d8d376bec6e47e8a8dbe3dc37ac889807c7e91bf9dc0185c99bbdd3b2f  experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl
e4886614bc24354355a4a2d513c0f6ecce9fd1c23da1a705b4e226876dc55d58  experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.md
0c9bd96a49cfd22e57f2f9c421dbc78bf0e3a0f16233a67e09c853c174c2b40c  experiments/gan2026_test450_phase4_frozen_audit_hybrid_structured_events_gpt41mini_2026-06-09.jsonl
61ac7d12c9580188c3f5c467a41d55d4962cf7f81052e5617dd19868ef997f59  experiments/gan2026_agentic_structured_event_patch_recent_unresolved_burden_test450_qwen3635b_2026-06-13.jsonl
5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57  data/Gan (2026)/splits/gan2026_split_v1.json
```

## Exact Authorized Command

Run this only after explicit user authorization for the frozen V12 aggregate
`test450` audit.

The shared Gan LLM CLI enforces a launch guard for locked holdout runs:
`--split test` requires `--confirm-test-audit`, requires an escalation reason,
rejects `--limit`, `--source-row-indices`, `--source-row-index-file`, and
`--overwrite-existing`, `--structured-event-jsonl`, and `--candidate-set-jsonl`,
and only permits `--resume-existing` when an existing JSONL artifact is present
and the escalation reason describes technical recovery. Test runs must use
`--mode live`, `--temperature 0.0`, and `--progress-every 0`. Prompt-only test
runs, nonzero-temperature test runs, `--api-base`, and `--disable-dspy-cache`
are rejected. For the V12 `fresh_evidence_reasoner` test audit, the CLI also
requires `--model openai/gpt-4.1`, `--max-tokens 2800`, the pinned JSONL output
path, and the pinned Markdown output path. For the V12 `test` split, the
Markdown report writer omits row-level tables and emits only aggregate sections
for the first readout; the CLI stdout summary also omits aggregate profile and
final-label distribution buckets, including during documented technical-recovery
resume.

Before launch, run the deterministic preflight:

```powershell
.\.venv\Scripts\python.exe -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_preflight --json
```

Do not launch the audit unless the preflight reports `"ok": true`. The preflight
checks frozen hashes, the exact launch command and singleton launch options,
split-manifest count, absence of prior V12 `test` outputs or stale
`.resume-part` outputs, source-artifact hashes and locked-row coverage for the
frozen GPT and Qwen test substrates, explicit DeepSeek test-source
unavailability, a synthetic prompt-input hygiene check that fails if row ids,
gold labels, split metadata, raw-record fields, or deterministic-top tokens enter
the model prompt, and a synthetic aggregate-only output-contract check that fails
if V12 `test` Markdown or stdout summaries expose row-level details, profile
buckets, or final-label distributions. The synthetic V12 `test` Markdown must
also be parseable by the pinned aggregate-only readout helper before launch.

```powershell
.\.venv\Scripts\python.exe -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli `
  --pipeline fresh_evidence_reasoner `
  --split test `
  --mode live `
  --model openai/gpt-4.1 `
  --max-tokens 2800 `
  --confirm-test-audit `
  --jsonl experiments\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl `
  --markdown experiments\gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.md `
  --progress-every 0 `
  --escalation-reason "User-authorized frozen aggregate-only test450 audit of V12 v0.4 fresh_evidence_reasoner; candidate prompt, safety gates, model ID, scorer, split manifest, and inspection policy frozen before first readout."
```

Do not pass `--limit`. Do not pass `--source-row-indices` or
`--source-row-index-file`. Do not pass `--overwrite-existing`; the CLI rejects
it for locked-test runs. Do not pass `--structured-event-jsonl` or
`--candidate-set-jsonl`; the frozen split-aware V12 defaults pin the source
substrate. Do not pass `--temperature`; the frozen audit uses the CLI default
`0.0`. Do not pass `--api-base` or `--disable-dspy-cache`. Do not change the
frozen `--model openai/gpt-4.1`, `--max-tokens 2800`, `--jsonl`, or
`--markdown` settings. Do not use `--mode prompt-only`. Do not pass
`--resume-existing` for the initial audit.

After the run succeeds, read only the aggregate Markdown with:

```powershell
.\.venv\Scripts\python.exe -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.frozen_test_readout --json
```

This helper rejects reports containing row-level sections and emits only the
permitted aggregate fields, including whether final Purist reached `383/450`,
raw/format-only/final Purist and Pragmatic counts, and aggregate Pragmatic
counts as a sidecar. It rejects alternate Markdown paths and reports that do not
point back to the pinned frozen JSONL artifact. Do not open the JSONL to compute
the first readout.

## Permitted First Readout

Allowed:

- Aggregate Purist and Pragmatic counts/rates.
- Call failure count.
- Parse/schema/label failure count.
- Prediction-bearing row count.
- Evidence exact-substring count.
- Action counts and fallback counts.
- Omission marker for withheld aggregate profile and final-label distributions.
- Aggregate comparison to validation V0 and prior aggregate baselines.

Not allowed before starting a new validation-only development cycle:

- Inspecting individual `test450` rows.
- Reading test row-level failures, rationales, evidence, selected events, or
  row-level transitions.
- Changing prompts, safety gates, normalization, label repair, model ID, token
  budget, source artifacts, or scorer based on the test result.
- Running a second tuned `test450` audit from the result.

## Technical-Failure Policy

If the process fails before producing any aggregate result, rerun the exact same
frozen command or resume the same artifact only as technical recovery. Do not use
test row-level content to decide how to recover.

If a partial JSONL exists after a technical failure, only inspect row count and
aggregate completion metadata needed for recovery. If the partial artifact has
fewer than `450` rows, resume with the same frozen configuration using
`--resume-existing` and an escalation reason that explicitly describes technical
recovery, not a new experimental condition.

If a complete JSONL exists but report writing fails, regenerate only the report
from the same rows or rerun with `--resume-existing` to combine the same frozen
rows, without row-level analysis.

## Stop Rule

After the first valid aggregate readout:

- If final Purist is at least `383/450`, record goal success with conservative
  claim language and update `PROJECT_STATUS.md`, `experiments/registry.jsonl`,
  and `experiments/RUN_INDEX.md`.
- If final Purist is below `383/450`, record the failure as final-evaluation
  evidence. Any follow-up must start as a new validation-only candidate.
