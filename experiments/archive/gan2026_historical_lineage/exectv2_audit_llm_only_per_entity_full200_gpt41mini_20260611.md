# ExECTv2 Phase 7 Frozen Audit — llm_only / per_entity — SeizureFrequency

> **IMMUTABLE AUDIT RECORD.** Frozen full-200 read; no tuning, no row inspection, no repair beyond the standing semantically-neutral ladder. Any later change requires a *new* authorized audit, not an edit to this artifact (protocol §4.5).

- Generated: `2026-06-11`
- Authorization: full-200 read authorized by user 2026-06-11 (Phase 7)
- Locked code: git `ab0d8d5cb7aa`
- Surface: **all 200 letters** (`load_letters`, D16 gold) — the benchmark-comparable surface
- Architecture: `llm_only` / `per_entity`
- Model: `openai/gpt-4.1-mini`  ·  mode: `live`  ·  prompt: `exectv2_llm_only_per_entity_v0.2`
- Entity: SeizureFrequency (benchmark's hardest cell; Table 1, Fonferko-Shadrach 2024). **This audits the SF cell, not the overall 0.87/0.90 headline** (9-entity scale-up is Phase 6, open).

## Headline vs published SF cell

Published SF: **0.66 per item / 0.68 per letter**. Headline match config = `sf_benchmark` (entity + phrase + guideline features + CUI; protocol §2).

- **Per-item F1 0.000** (95% CI 0.000–0.000) — below 0.66 (point 0.000)
- **Per-letter F1 0.000** (95% CI 0.000–0.000) — below 0.68 (point 0.000)

Verdict: does not clear the SF benchmark on both axes (CI-based).

## Scores under all three match configs (sensitivity)

| Config | per-item P | R | F1 | per-letter P | R | F1 | dev→audit per-item | dev→audit per-letter |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `phrase_only` | 0.478 | 0.449 | 0.463 | 0.717 | 0.641 | 0.677 | 0.486 → 0.463 (-0.023) | 0.698 → 0.677 (-0.021) |
| `sf_semantic` | 0.126 | 0.118 | 0.122 | 0.410 | 0.176 | 0.246 | 0.135 → 0.122 (-0.013) | 0.264 → 0.246 (-0.018) |
| **`sf_benchmark`** | 0.000 | 0.000 | **0.000** | 0.000 | 0.000 | **0.000** | 0.000 → 0.000 (+0.000) | 0.000 → 0.000 (+0.000) |

## CUI note (why the headline is 0.000)

This architecture does **not emit the `CUI` attribute**. The headline `sf_benchmark` config keeps CUI (protocol §2, user-pinned), so no prediction can match the gold CUI and the headline collapses to 0.000 even though phrase and semantic-attribute extraction are non-trivial (`sf_semantic` keeps 31 per-item matches; `phrase_only` keeps 118). Read `sf_semantic` (CUI dropped) as this architecture's attribute-level quality. This is the exact CUI-divergence §2 made the headline policy guard against — surfaced, not hidden.

## Gates & reliability trail (protocol §5)

- `call_failures`: 0
- `parse_failures`: 0
- `n_mentions_raw`: 255
- `n_mentions_scored`: 247

## Provenance & reproduction

- Bootstrap: percentile CI over letters, 5000 resamples, seed 20260611.
- The dev→audit gap columns diff this frozen read against the locked dev read (rules: recomputed live; LLM/hybrid: the registered full-dev run) — the generalization check (protocol §3).
- Run once per architecture, after dev was locked; not iterated against.

