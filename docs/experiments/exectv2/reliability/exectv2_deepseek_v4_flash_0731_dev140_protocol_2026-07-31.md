# ExECTv2 DeepSeek V4-Flash-0731 dev140 re-run protocol

Date: 2026-07-31  
Status: complete  
Report: [0731 re-run report](exectv2_deepseek_v4_flash_0731_dev140_2026-07-31.md)  
Diff artifact: `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715_current_rules.json`  
Comparator: no-call current-rules replay of the retained 2026-07-15 DeepSeek
structured outputs
(`experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json`)  
Authorization: user requested a no-cache re-run of ExECT `dev140` on the updated
DeepSeek `deepseek-v4-flash` API surface, then a ruleset-matched baseline replay.

## Primary question

Does the 2026-07-31 DeepSeek-V4-Flash API update (`DeepSeek-V4-Flash-0731`, same
model id `deepseek-v4-flash`) change ExECTv2 `dev140` clinical_headline
performance, and on which letters and families, relative to the retained
2026-07-15 DeepSeek panel condition?

## Why this study

DeepSeek announced that `deepseek-v4-flash` now serves the post-trained
0731 public-beta API with the same architecture and calling method. The
retained six-model panel used that id on 2026-07-15 under thinking-enabled
defaults. A same-config, cache-disabled re-run is the only way to measure
whether the provider update moves development extraction answers.

## Fixed conditions

- Dataset / split: ExECTv2 `dev140` (140 letters); row-level inspection permitted.
- Locked split: `test60` is out of scope for this study. No sealed holdout
  inspection, no test60 re-run unless separately authorized.
- Model: `deepseek/deepseek-v4-flash` via `https://api.deepseek.com`.
- Runtime: official DeepSeek route; temperature `0`; structured max tokens
  `64000` (see operational amendment below); DSPy cache disabled; no resume
  from prior checkpoints.
- Architecture: decision 0040 model-led families + decision 0041 single call.
- Prompt: `exectv2_hybrid_key_family_event_ledger_v0.9.24` (frozen six-model
  prompt; no prompt edit).
- Repair: Diagnosis/Prescription `default` / `default` (decision 0045).
- Scorer: internal `clinical_headline` primary; evidence-valid, raw, and
  family F1 secondary.
- Comparator: frozen 2026-07-15 DeepSeek structured outputs replayed through
  the current SF adapters and assembly
  (`exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140`).
- Candidate id:
  `exectv2_deepseek_v4_flash_0731_update_dev140`.

## Minimal change

Only the provider-served model weights behind the same API id change. Code,
prompt, lenses, scorers, split, and assembly contract stay fixed. Outputs use
new dated paths so the frozen 2026-07-15 panel is not overwritten.

## Operational amendment (pre-completion)

A first live attempt with the retained comparator budget (`max_tokens=16000`)
produced repeated DSPy truncation warnings and a parse failure within the
first five letters. Reasoning tokens count inside the completion budget on
DeepSeek V4 thinking mode, so the 0731 revision exhausted the old ceiling
before emitting complete JSON. The structured max was raised to `64000` for
this study only; thinking remains API-default enabled. Partial artifacts from
the truncated attempt were discarded before the clean re-run.

## Required readouts

1. Aggregate `clinical_headline` overall and by Diagnosis, SeizureFrequency,
   Prescription, Investigations, versus the 2026-07-15 comparator.
2. Call / parse / schema failure counts.
3. Letter-level changed-row analysis on `dev140`:
   - letters whose predicted mention sets change under clinical_headline;
   - direction when scorer-defined correctness changes (rescue / regression /
     both-wrong or both-correct reshuffle);
   - family attribution of changes.
4. Representative permitted examples for rescues and regressions.

## Stop rule and claim boundary

Answer whether the 0731 update improves, harms, or is near-neutral on this
exact ExECTv2 development stack. This is development evidence for a provider
model revision under a frozen pipeline. It is not holdout transfer, published
ExECT benchmark reproduction, clinical validation, or automatic replacement of
the retained six-model panel cell unless a later promotion decision says so.

## Artifacts

| Kind | Path |
| --- | --- |
| Config | `configs/exectv2/six_model_comparison/deepseek_v4_flash_0731_dev140.json` |
| Run JSON | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.json` |
| Run JSONL | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl` |
| Diff artifact | `experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731_vs_20260715_current_rules.json` |
| Ruleset-matched baseline | `experiments/exectv2_deepseek_v4_flash_20260715_model_current_rules_dev140_20260731.json` |
| Report | `docs/experiments/exectv2/reliability/exectv2_deepseek_v4_flash_0731_dev140_2026-07-31.md` |
