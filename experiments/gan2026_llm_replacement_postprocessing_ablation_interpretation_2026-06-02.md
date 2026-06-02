# Gan 2026 LLM-Replacement Post-Processing Ablation Interpretation

Date: 2026-06-02

This note summarizes the first no-call replacement-ablation replay for future
LLM-heavy v2 planning. It is a validation-only development interpretation, not a
benchmark or holdout claim.

## Source Artifacts

- Design:
  `experiments/gan2026_llm_replacement_postprocessing_ablation_design_2026-06-02.md`
- Replay report:
  `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.md`
- Replay rows:
  `experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_2026-06-02.jsonl`
- Source saved outputs:
  `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`

## Main Finding

The strongest score movement in LLM-heavy v1 comes from deterministic
selected-evidence arithmetic, not from format-only repair.

| Layer | Purist | Pragmatic | Changed from raw | Raw wrong -> correct | Raw correct -> wrong |
| --- | ---: | ---: | ---: | ---: | ---: |
| Raw model label | 188/250 | 195/250 | 0 | 0 | 0 |
| Format-only repair | 188/250 | 195/250 | 7 | 0 | 0 |
| Selected-evidence arithmetic | 219/250 | 225/250 | 57 | 32 | 1 |
| Benchmark-aligned adapter | 204/250 | 213/250 | 28 | 16 | 0 |
| Full stack | 204/250 | 213/250 | 28 | 16 | 0 |

Evidence and trace caveats remain unchanged across these no-call conditions:
selected evidence was exact on 230/250 rows, event/node evidence was valid on
236/250 rows, and selected-event trace mismatches remained 9/250.

## Representative Examples

- Format-only repair: row 1363 changed `3 per 1 day` to `3 per day`, preserving
  the same clinical meaning and correctness.
- Cluster rendering: row 190 changed `1 per 4 week cluster` to `1 per 4 week`,
  matching the gold label from correctly selected evidence about clusters every
  four weeks.
- Bimonthly semantics: rows such as 959, 960, and 987 show raw `2 per month` or
  `1 to 2 per month` repaired to `1 per 2 month` from bimonthly evidence.
- Cluster burden preservation: row 3224 changed a flattened label,
  `6 to 7 per 1 day per month`, into `1 cluster per month, 6 to 7 per cluster`.
- Arithmetic regression: row 2748 changed raw-correct `1 per month` to
  `7 per year` because the selected evidence contained both a year-to-date count
  and a current monthly pattern.

## Interpretation

Format-only repair appears safe but low-value for score. It fixes surface
grammar without changing Purist or Pragmatic performance.

Selected-evidence arithmetic is prediction-bearing. It often shows that the LLM
selected useful evidence but did not render the final Gan-compatible label
correctly. Because it changes Purist category 36 times and Pragmatic category 32
times, it must be treated as a deterministic post-processing component rather
than scorer normalization.

Benchmark alignment is also prediction-bearing but less powerful than
selected-evidence arithmetic on this artifact. It explains 16 raw-wrong to
correct changes, but the full-stack result remains below the arithmetic-only
diagnostic layer.

## Decision For Next Work

Do not start broad `llm_heavy_clinical_frequency_reasoner_v2` prompt work from
aggregate validation250 scores. The next useful step is a validation25
replacement smoke focused specifically on making arithmetic/rendering LLM-owned:

- the model should emit a parser-ready final label and enough structured
  operands to audit its arithmetic;
- deterministic code should validate evidence, schema, and arithmetic
  consistency, not silently replace the model's selected label;
- stop rules should fail the smoke for selected-event trace mismatches,
  non-exact selected evidence, or hidden deterministic semantic repair.

The promotion question for v2 is therefore not "can the score improve?" It is:
can the LLM own the clinical arithmetic/rendering decisions that v1 currently
delegates to deterministic post-processing?
