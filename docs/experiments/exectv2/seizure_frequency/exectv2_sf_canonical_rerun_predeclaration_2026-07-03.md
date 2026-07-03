# ExECTv2 SF canonical ledger re-run predeclaration

- Date: `2026-07-03`
- Status: frozen predeclaration before the SF ledger re-run
- Worktree at drafting: clean (A1 + A2 committed)
- Owner: ExECTv2 workstream
- Split/scope: dev140 (140 letters). NOT a holdout/full-200 run.
- Row-inspection boundary: dev140 — full row-level inspection is the point
  (this produces the adjudication substrate); no holdout/test interaction.

## Purpose

The SF gold case ledger (`experiments/gold_case_ledger_seizurefrequency.jsonl`,
66 rows) was built on a 2026-06-29 live LLM re-run of the SF-verify program
that reproduces the registered stored `.jsonl` only 99/140 (state_profile
0.7724 re-run vs 0.7483 registered). The re-run is on a *different prediction
basis* than the registered run — a pre-existing inconsistency surfaced by the
07-02 rescore-sweep doc. This predeclaration authorizes a deliberate re-run
that accepts the 0.7724 re-run as the fixed SF-ledger prediction basis going
forward, with explicit provenance distinguishing it from the registered
0.7483 number (whose row-level substrate cannot be reconstructed — the
original 06-28 completions were never cached locally).

## Why the 99/140 ceiling is irreducible

gpt-4.1-mini at temperature 0 is nondeterministic across separate API
sessions. The original 06-28 run's completions were never written to the
local DSPy cache, so re-invoking the same program against the same inputs
produces different (but cache-stable on repeat) completions. The 99/140
ceiling is structural, not a bug, seed, prompt-drift, or program-change issue
(confirmed by `docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`
§2). A faithful regeneration therefore means re-running and accepting a new
non-matching basis — there is no operation that reproduces 0.7483's substrate.

## Frozen contract

| Component | Value |
| --- | --- |
| Program | `SfVerifyExtractor` (generate + verify, two-stage) |
| Instructions | `experiments/exectv2_gepa_sf_verify_gpt41mini_20260628.instruction.txt` (=== generate === / === verify === blocks, unchanged) |
| Model | `openai/gpt-4.1-mini`, single model both stages |
| Temperature | 0.0 |
| max_tokens | 8000 |
| Cache | True (DSPy local cache; repeat runs are stable) |
| Split | dev140 (`gepa_data.load_dev_letters()`, n=140) |
| Call count | 2 calls × 140 letters = **~280 calls** (minus any cache hits) |
| Script | `experiments/exectv2_sf_canonical_row_analysis.py` (unchanged) |

## Outputs

- `experiments/_sf_canonical/_index.json` — per-letter gold/s1/s2 state sets
- `experiments/_sf_canonical/_summary.json` — aggregate stage-1 vs stage-2
  state_profile + per-state confusion + reproduction checks
- `experiments/_sf_canonical/<letter>.md` — per-letter adjudication substrate
- Regenerated `experiments/gold_case_ledger_seizurefrequency.jsonl` (66 rows
  on the new 0.7724 basis) via the existing Dx/SF backfill path
- Re-rendered `docs/canon/workstreams/SEIZURE_FREQUENCY_CANONICAL_LEDGER_CANON.md`
  with explicit provenance distinguishing the 0.7724 re-run basis (mechanism
  table) from the 0.7483 registered number (F1 ladder)

## What this is NOT

- Not a holdout or full-200 run (dev140 only).
- Not an attempt to reproduce 0.7483's substrate (impossible — completions
  gone). The registered 0.7483 number keeps its own disclosure and is not
  overwritten.
- Not a prompt/program tuning run (instructions unchanged from 06-28).

## Acceptance criterion

The re-run produces a self-consistent 0.7724-basis ledger with 0
unadjudicated rows, the reproduction check reports ~99/140 (confirming the
known ceiling), and the SF dossier carries explicit provenance for the
two-basis condition. The 0.7483 registered number is preserved with its
existing disclosure.
