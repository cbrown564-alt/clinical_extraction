# ExECTv2 Phase 7 Frozen Audit — rules — SeizureFrequency

> **IMMUTABLE AUDIT RECORD.** Frozen full-200 read; no tuning, no row inspection, no repair beyond the standing semantically-neutral ladder. Any later change requires a *new* authorized audit, not an edit to this artifact (protocol §4.5).

- Generated: `2026-06-11`
- Authorization: full-200 read authorized by user 2026-06-11 (Phase 7)
- Locked code: git `ab0d8d5cb7aa`
- Surface: **all 200 letters** (`load_letters`, D16 gold) — the benchmark-comparable surface
- Architecture: `rules`
- Model: `(model-independent)`  ·  mode: `deterministic`  ·  prompt: `n/a (deterministic rules)`
- Entity: SeizureFrequency (benchmark's hardest cell; Table 1, Fonferko-Shadrach 2024). **This audits the SF cell, not the overall 0.87/0.90 headline** (9-entity scale-up is Phase 6, open).

## Headline vs published SF cell

Published SF: **0.66 per item / 0.68 per letter**. Headline match config = `sf_benchmark` (entity + phrase + guideline features + CUI; protocol §2).

- **Per-item F1 0.321** (95% CI 0.254–0.388) — below 0.66 (point 0.321)
- **Per-letter F1 0.539** (95% CI 0.451–0.618) — below 0.68 (point 0.539)

Verdict: does not clear the SF benchmark on both axes (CI-based).

## Scores under all three match configs (sensitivity)

| Config | per-item P | R | F1 | per-letter P | R | F1 | dev→audit per-item | dev→audit per-letter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `phrase_only` | 0.595 | 0.392 | 0.472 | 0.916 | 0.535 | 0.676 | 0.485 → 0.472 (-0.013) | 0.683 → 0.676 (-0.008) |
| `sf_semantic` | 0.405 | 0.266 | 0.321 | 0.887 | 0.387 | 0.539 | 0.362 → 0.321 (-0.041) | 0.575 → 0.539 (-0.036) |
| **`sf_benchmark`** | 0.405 | 0.266 | **0.321** | 0.887 | 0.387 | **0.539** | 0.362 → 0.321 (-0.041) | 0.575 → 0.539 (-0.036) |

## Gates & reliability trail (protocol §5)

- `schema_validity_rate`: 1.0
- `repair_rate`: 0.0
- `evidence_validity_rate`: 1.0
- `call_failures`: 0
- `parse_failures`: 0
- `n_mentions`: 173

## Provenance & reproduction

- Bootstrap: percentile CI over letters, 5000 resamples, seed 20260611.
- The dev→audit gap columns diff this frozen read against the locked dev read (rules: recomputed live; LLM/hybrid: the registered full-dev run) — the generalization check (protocol §3).
- Run once per architecture, after dev was locked; not iterated against.

