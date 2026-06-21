# ExECTv2 v09 Single-GPT Simplification Study

Date: 2026-06-21
Split: dev140 (first 140 dev rows) only — not a full-200, locked-test, or
benchmark claim.
Model-bearing source: GPT-4.1-mini single structured pass (prompt v0.9), plus
no-call deterministic assembly replay.
Scoring: assembly `headline_target` view, identical to the v08 report, so every
number below is directly comparable to v08's 0.9152.

## Goal

After v08 cleared all four key families above 0.900 with four focused producers
plus three arbitration layers, the renewed objective was **simplification**:

1. Move the v05 Diagnosis residual benchmark repair out of post-hoc lenses.
2. Reduce SF type/state false positives in the original LLM call, less determinism.
3. Achieve Investigations performance without a verifier — logic in the prompt.
4. Most importantly: build a **single GPT version that surpasses 0.9**, using
   only some deterministic repair plus standard dictionaries (drug-name mapping,
   dose-unit variants) translating the clinical facts.

The confirmed design: one single-pass GPT clinical engine
(`llm_only_key_entities_structured` v0.9) backed by one deterministic
standard-dictionary translation layer; the prompt owns clinical extraction and
selection, the dictionary owns convention translation.

## What was built (all tests green)

- `deterministic/standard_dictionary.py` — the single convention-translation
  layer: drug-name normalization (alias/brand → generic, validated against the
  whole benchmark lexicon), dose-unit and frequency canonicalizers (parity-tested
  against `all_entities`), the migrated v04/v05 diagnosis convention dictionary
  (alias repairs, residual rewrites/additions, noise drops), and the SF benchmark
  rewrite set. (`tests/test_exectv2_standard_dictionary.py`, 28 tests.)
- Prompt **v0.9** of the single GPT engine — new SF precision rules (safety-advice/
  conditional, bare seizure-free without anchor, anaphoric/composite anchors,
  one-mention-per-rate) and strengthened Investigations pending-test rules
  (verifier `will/arrange/await/appointment/...` cues + worked examples), so
  Investigations needs no separate verifier. No convention/CUIPhrase rewrite text
  in the prompt — that is the dictionary's job.
- `assembly/lenses.py` — three v09 dictionary lenses (`DiagnosisDictionaryLens`,
  `SeizureFrequencyDictionaryLens`, `PrescriptionDictionaryLens`) plus an
  Investigations pass-through, all calling `standard_dictionary`. The frozen v08
  lens chain is untouched. (`tests/test_exectv2_v09_dictionary_lenses.py`.)
- `runners/run_finding_assembly.py` — generic YAML-manifest assembly scorer
  printing `headline_target` overall + per-family for any manifest.

## Headline result: a single GPT pass does NOT clear 0.9

Every figure is dev140 `headline_target` (comparable to v08 0.9152).

| Config | Components | Overall | Dx | SF | Presc | Inv |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| GPT-only + dictionary (v09) | 4 GPT | 0.7552 | 0.761 | 0.680 | 0.751 | 0.855 |
| + deterministic prescription (v09b) | 3 GPT + 1 det | 0.7997 | 0.761 | 0.680 | 0.936 | 0.855 |
| Partial hybrid: presc+SF focused (v09h1) | 2 GPT + 2 focused | 0.8516 | 0.765 | 0.905 | 0.936 | 0.855 |
| Partial hybrid: presc+Dx focused (v09h2) | 2 GPT + 2 focused | 0.8553 | 0.908 | 0.680 | 0.936 | 0.855 |
| **Partial hybrid: presc+SF+Dx focused (v09 accepted)** | 1 GPT (Inv) + 3 focused | **0.9059** | 0.908 | 0.905 | 0.936 | 0.855 |
| v08 full multi-producer | 4 focused | 0.9152 | 0.908 | 0.905 | 0.936 | 0.913 |

The pure single-GPT + dictionary architecture reaches **0.755**, about 0.16 below
v08, and every family is down. This is the direct, evidenced answer to goal 4:
**no — a single well-built prompt plus standard dictionaries does not clear 0.9
at gpt-4.1-mini.** The v08 focused producers were doing substantial real work,
not incidental complexity.

## Where the single GPT pass falls short (real-scorer error ledger)

`experiments/exectv2_v09_dev140_error_ledger_20260621.md`:

- **Prescription (R=0.72).** The single pass misses many current-medication-list
  entries the deterministic all9 parser reliably catches (Clobazam 10mg,
  Perampanel 8mg, rescue Midazolam, Carbamazepine/Sodium-Valproate variants) and
  emits titration/wrong doses. Deterministic decisively wins (0.751 → 0.936).
- **Diagnosis.** 53 missed generic `epilepsy` Cert-5 mentions — a recall gap the
  convention dictionary does not address (it drops noise, never *adds* generic
  epilepsy). The dictionary still lifts the GPT producer from raw 0.591 to
  assembled 0.761, but the focused reconciler reaches 0.908.
- **SeizureFrequency.** Active-rate over-emission (gold 25 vs predicted 38) plus
  generic-seizure recall; the v0.9 precision rules helped but the v08 union +
  arbitration is a stronger recall+precision engine (0.680 → 0.905).
- **Investigations (0.855).** The closest family. The pending-test prompt rules
  fixed precision (0.916); recall (0.80) is the residual. This is the one family
  where dropping the verifier and using the prompt is nearly competitive.

## Accepted outcome: partial hybrid (best of both)

`configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml`
— **overall 0.9059**, the leanest configuration that still clears 0.9:

- Diagnosis: focused reconciler producer + v05 convention lens (0.908)
- SeizureFrequency: focused union-arbitration producer (0.905)
- Prescription: deterministic all9 repair producer (0.936)
- **Investigations: single GPT v0.9 pass, prompt-owned, no verifier (0.855)**

Versus v08 this **drops the entire Investigations verifier + pending-test
arbitration stack** and replaces it with one prompt-owned lane, at a cost of
−0.006 overall (0.9152 → 0.9059) and −0.058 on Investigations. The two- and
three-component tradeoff is explicit above: two focused components land at ~0.85;
clearing 0.9 requires keeping the three deterministic/focused families.

## How each goal is answered

1. **Diagnosis residual repair** is migrated into the `standard_dictionary`
   layer, not the prompt — honest, auditable, and it does lift the GPT producer
   (0.591 → 0.761). But it does not transfer enough to replace the reconciler,
   because the GPT producer's errors are recall (missing generic epilepsy), not
   the convention mismatches the dictionary was tuned for.
2. **SF type/state FPs** are reduced by the v0.9 prompt rules (evidence_valid SF
   0.516, headline 0.680), but a single pass cannot match the union+arbitration
   (0.905); the accepted hybrid keeps the focused SF producer.
3. **Investigations without a verifier works** — the v0.9 prompt reaches 0.855
   (precision 0.916), close enough to adopt as the one simplified lane.
4. **Single GPT > 0.9: not reachable** at gpt-4.1-mini with prompt + dictionary
   (0.755); the focused producers remain necessary for Diagnosis, SF, and
   Prescription.

## Residual risks / next steps

- dev140 only; no full-200 or holdout language. Dictionary entries remain labelled
  benchmark-format, not clinical generalization.
- The assembly gate still reports `do-not-promote` (its hardwired checks assume the
  v0.42 control and zero changed Prescription/Investigations rows); the renewed
  goal was the 0.900 family headlines, which only the partial hybrid satisfies.
- Investigations recall (0.80) is the partial hybrid's weakest point; a future
  prompt/dictionary recall pass could close the −0.006 gap to v08 without
  re-adding the verifier.
- A leaner 2-component hybrid at 0.9 would require targeted GPT-family recovery
  (Diagnosis generic-epilepsy recall, SF over-emission suppression); deferred.

## Canonical artifacts

- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140.yaml`
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09_dev140.yaml` (pure single-GPT)
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09b_leanhybrid_dev140.yaml`
- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v09h{1,2,3}_*_dev140.yaml` (ablation)
- `experiments/exectv2_llm_only_key_entities_structured_v09_dev140_gpt41mini_20260621.{jsonl,md}`
- `experiments/exectv2_holistic_finding_assembly_v09_partial_hybrid_dev140_20260621.{jsonl,json,md}`
- `experiments/exectv2_v09_dev140_error_ledger_20260621.{json,md}`
- `src/.../exectv2/deterministic/standard_dictionary.py`,
  `src/.../exectv2/runners/run_finding_assembly.py`
