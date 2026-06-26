# ExECTv2 Phase 7 Frozen Audit — hybrid — SeizureFrequency

> **IMMUTABLE AUDIT RECORD.** Frozen full-200 read; no tuning, no row inspection, no repair beyond the standing semantically-neutral ladder. Any later change requires a *new* authorized audit, not an edit to this artifact (protocol §4.5).

- Generated: `2026-06-11`
- Authorization: full-200 read authorized by user 2026-06-11 (Phase 7)
- Locked code: git `ab0d8d5cb7aa`
- Surface: **all 200 letters** (`load_letters`, D16 gold) — the benchmark-comparable surface
- Architecture: `hybrid`
- Model: `openai/gpt-4.1-mini`  ·  mode: `live`  ·  prompt: `exectv2_hybrid_candidate_assessment_v0.2`
- Entity: SeizureFrequency (benchmark's hardest cell; Table 1, Fonferko-Shadrach 2024). **This audits the SF cell, not the overall 0.87/0.90 headline** (9-entity scale-up is Phase 6, open).

## Headline vs published SF cell

Published SF: **0.66 per item / 0.68 per letter**. Headline match config = `sf_benchmark` (entity + phrase + guideline features + CUI; protocol §2).

- **Per-item F1 0.246** (95% CI 0.192–0.301) — below 0.66 (point 0.246)
- **Per-letter F1 0.470** (95% CI 0.387–0.546) — below 0.68 (point 0.470)

Verdict: does not clear the SF benchmark on both axes (CI-based).

## Scores under all three match configs (sensitivity)

| Config | per-item P | R | F1 | per-letter P | R | F1 | dev→audit per-item | dev→audit per-letter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `phrase_only` | 0.487 | 0.627 | 0.548 | 0.767 | 0.789 | 0.778 | 0.585 → 0.548 (-0.037) | 0.781 → 0.778 (-0.003) |
| `sf_semantic` | 0.218 | 0.281 | 0.246 | 0.614 | 0.380 | 0.470 | 0.327 → 0.246 (-0.081) | 0.578 → 0.470 (-0.108) |
| **`sf_benchmark`** | 0.218 | 0.281 | **0.246** | 0.614 | 0.380 | **0.470** | 0.327 → 0.246 (-0.081) | 0.578 → 0.470 (-0.108) |

## Gates & reliability trail (protocol §5)

- `call_failures`: 0
- `parse_failures`: 0
- `n_candidates`: 888
- `n_mentions_raw`: 397
- `n_mentions_scored`: 339
- `n_routed`: 54
- `routed_taxonomy`: {'no_frequency_attributes': 11, 'bare_nonzero_count': 42, 'evidence_not_substring': 1}

## Provenance & reproduction

- Bootstrap: percentile CI over letters, 5000 resamples, seed 20260611.
- The dev→audit gap columns diff this frozen read against the locked dev read (rules: recomputed live; LLM/hybrid: the registered full-dev run) — the generalization check (protocol §3).
- Run once per architecture, after dev was locked; not iterated against.

