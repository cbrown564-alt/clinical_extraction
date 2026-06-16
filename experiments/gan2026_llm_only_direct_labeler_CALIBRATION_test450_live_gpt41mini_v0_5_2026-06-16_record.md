# Gan 2026 F1 — CALIBRATION test450 record (NOT a certified promotion)

Date: 2026-06-16
Owner: gan2026-freeze-warden
Decision class: **CALIBRATION measurement** (user-authorised). This is **not** a
robustness-certified promotion and **not** a 0.90 attempt.

## What this is, in one line

The first-ever frozen `test450` Purist number for the **llm_only direct labeler
prompt v0.5** on **`openai/gpt-4.1-mini`**, run once to calibrate the true
validation->test gap on mini. Every prior Gan 2026 holdout (incl. the 379/450
V12 champion) used full `openai/gpt-4.1`, never mini, so the val->test gap on
mini was previously unmeasured.

## Candidate selection and rationale

Chosen candidate: **`llm_only_direct_labeler`, prompt version
`gan2026_llm_only_direct_labeler_v0.5`**, `openai/gpt-4.1-mini`, temperature 0.

Why this candidate (per the F1 protocol's calibration instructions):

1. **Cleanly freezable on mini tonight.** It is single-model: there is no
   3-source (GPT/Qwn/DeepSeek) panel, so the V12 source-symmetry hard gate in
   `frozen_test_preflight.py` is structurally inapplicable. The pipeline is
   registered in the CLI registry (`runner.get_cli_specs()`), has no entry in
   `FROZEN_TEST_PIPELINE_LAUNCH_SPECS`, and so the test-split model-lock that
   pins `fresh_evidence_reasoner` to full `gpt-4.1` does **not** apply — mini can
   be passed explicitly and the test-split integrity gates still fire.
2. **Known mini validation reference exists.** `validation750` = **575/750
   (0.7667)** Purist on `gpt-4.1-mini`, prompt v0.5
   (`gan2026_llm_only_direct_labeler_v05_validation750_gpt41mini_2026-06-09.md`).
   This is the reference needed to compute the gap honestly without fabricating
   a number.
3. **No defensible mini reference exists for the stronger hybrid/V12 family.**
   The 733-739 validation / 379 test numbers for that family are on full
   `gpt-4.1`, not mini. The protocol forbids fabricating a mini validation
   number, so the clean default candidate is used.

This candidate is **not** robustness-certified. It explicitly failed Cycle 1's
robustness battery (Panel A 2/6 both-correct, Panel B 5/7), so it would be
**refused** under the normal certification bar. It is run here only because the
user explicitly authorised a calibration measurement and delegated the freeze
judgment for that purpose.

## Preflight (test-split integrity, not V12 source-symmetry)

The V12 `frozen_test_preflight.py` is wired specifically to
`fresh_evidence_reasoner` + full `gpt-4.1` + the 3-source panel + a hashed
protocol doc; it is the wrong instrument for a single-model mini candidate and
its source-symmetry gate does not apply here. The applicable test-split
integrity checks were verified directly and all passed:

- Split manifest `gan2026_split_v1`; `test` split count = **450**.
- `source_row_indices` length 450, **all 450 unique**.
- `load_records_for_split('test')` returns 450 records, 450 unique ids.
- Active module prompt version = `gan2026_llm_only_direct_labeler_v0.5` (frozen
  baseline default; v0.6/v0.7 not selected).
- No pre-existing test450 output artifact at the target paths before launch.
- Post-run JSONL: 450 rows, 450 unique `source_row_index`, every row
  `split == "test"`, 0 call failures, 0 parse/schema/label failures.

## Run (executed exactly once, live)

Command (via the single CLI harness; test-split policy gates enforced:
`--confirm-test-audit`, `--escalation-reason`, full split, `--progress-every 0`,
`--mode live`, `--temperature 0.0`):

```
uv run python -m clinical_extraction.tasks.seizure_frequency.gan2026.cli.llm_pipeline_cli \
  --pipeline llm_only_direct_labeler --split test --mode live \
  --model openai/gpt-4.1-mini --temperature 0.0 --max-tokens 900 \
  --progress-every 0 --confirm-test-audit \
  --escalation-reason "<calibration reason>" \
  --jsonl experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.jsonl \
  --markdown experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.md
```

No tuning on test, no re-run to pick a better number, no inspection of
individual test row failures to revise anything.

## Result (verbatim)

- **test450 Purist (final): 325 / 450 = 0.7222**  (micro-F1 = accuracy)
- test450 Pragmatic: 354 / 450 = 0.7867
- Decision records: 450/450; call failures: 0; parse/validation failures: 0;
  exact evidence substrings: 422/450.
- Verified independently from the JSONL `comparison.purist_correct` flags:
  325/450, matching the report exactly.

## Validation reference and the val->test gap

- **validation750 reference (mini, v0.5): 575 / 750 = 0.7667** Purist.
- **test450 (mini, v0.5): 325 / 450 = 0.7222** Purist.
- **val->test gap = 0.7667 - 0.7222 = +0.0444 (+4.44 percentage points).**
- In row terms: validation-implied test rate would be 575/750 * 450 = 345.0
  rows; observed test = 325, i.e. **-20 rows** vs the val-implied count.

Interpretation: on `gpt-4.1-mini`, this single-model llm_only labeler loses ~4.4
points moving from the saturated validation surface to the locked test450
holdout — a modest, plausibly-real distribution/holdout penalty, consistent with
the protocol's expectation that calibration test numbers land ~0.75-0.85. This
gap is now the first measured mini val->test anchor; it is **not** evidence of
robustness and does not change the certification status of any candidate.

## Status

- robustness_certified: **false** (failed Cycle 1 battery; not certified).
- This artifact is a calibration measurement only. The orchestrator may fold the
  measured gap into the scoreboard; the Freeze Warden does not itself promote
  this candidate or alter champion status.

## Artifacts

- experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.jsonl
- experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16.md
- experiments/gan2026_llm_only_direct_labeler_CALIBRATION_test450_live_gpt41mini_v0_5_2026-06-16_record.md (this file)
- Validation reference: experiments/gan2026_llm_only_direct_labeler_v05_validation750_gpt41mini_2026-06-09.md
