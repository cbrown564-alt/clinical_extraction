# Qwen Protocol-Clean Attribution Readout

Date: 2026-06-23

Protocol: `docs/design/llm_repair_attribution_protocol_2026-06-22.md`

## Outcome

The direct Qwen compact route did not achieve the declared dev140 objective.
A smaller candidate-backed Qwen action-selection route was initially scored as
protocol-clean because the assembly added an explicit
`protocol_model_preserving_canonical` surface that preserves selected facts and
does not credit post-model residual additions. Under the revised
generation-and-selection protocol, this candidate-backed result is no longer an
LLM-attributed Qwen extraction pass because Qwen selected from upstream
candidate facts rather than generating the scored target facts itself.

The best recorded candidate-backed selector surface remains:

- `model_preserving_canonical` F1 `0.9155`
- precision `0.9141`
- recall `0.9169`
- TP `728`, FP `68`, FN `66`

## Direct Compact Dev25 Diagnostic

Candidate:
`exectv2_holistic_finding_assembly_v0924_qwencompact_schemarepair_dev25`

Artifacts:

- LLM rows: `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemarepair_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Assembly: `experiments/exectv2_holistic_finding_assembly_v0924_qwencompact_schemarepair_operand4_protocol_dev25_20260622.json`

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.8615 | 0.8438 | 0.8800 | 110 | 20 | 15 |
| schema_format | 0.8615 | 0.8438 | 0.8800 | 110 | 20 | 15 |
| model_preserving_canonical | 0.9055 | 0.9237 | 0.8880 | 111 | 9 | 14 |
| hybrid_full_stack | 0.9262 | 0.8947 | 0.9600 | 120 | 14 | 5 |

This table uses the earlier `dictionary_normalized` proxy for
`model_preserving_canonical`. Under the corrected source-preserving protocol
surface, the compact direct dev25 run tracks `raw_model`/`schema_format` and
does not by itself establish the final Qwen pass.

## Declared Dev140 Run

Candidate:
`exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_dev140`

Artifacts:

- LLM rows: `experiments/exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemaoperand_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Assembly: `experiments/exectv2_holistic_finding_assembly_v0924_qwencompact_schemaoperand_protocol_dev140_20260622.json`

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.6975 | 0.6840 | 0.7116 | 565 | 256 | 229 |
| schema_format | 0.6975 | 0.6840 | 0.7116 | 565 | 256 | 229 |
| model_preserving_canonical | 0.7821 | 0.8285 | 0.7406 | 588 | 119 | 206 |
| hybrid_full_stack | 0.8483 | 0.8251 | 0.8728 | 693 | 145 | 101 |

Per-family `model_preserving_canonical` dev140 F1:

- Diagnosis: 0.7637
- SeizureFrequency: 0.6813
- Prescription: 0.8721
- Investigations: 0.8155

## Transition Accounting

Dev140 parse/schema:

- Call failures: 0
- Blocking parse/schema failures after balanced JSON repair: 3
- Exact evidence rate after scoring: 1.0000 for all four lanes

Dev140 deterministic actions by protocol class:

- Allowed/model-preserving rewrites: Diagnosis convention rewrites 68; SeizureFrequency operand/convention rewrites 86.
- Disallowed rescue additions: Diagnosis 73, SeizureFrequency 63, Investigations 31, Prescription 11.
- Dropped model findings: Diagnosis 32, SeizureFrequency 30, Investigations 18, Prescription 13.

Approximate transition deltas on dev140:

- Clean to full-stack gain: +105 TP and -105 FN, with +26 FP.
- These gains are rescue-mediated and do not count toward the Qwen model-quality target.
- Raw to clean: +23 TP, -137 FP, -23 FN through schema/format/canonical rewrites and drops.

## Failed Alternative

The `full` prompt profile was tested on dev25 with `max_tokens=5000`:

- Artifact: `experiments/exectv2_llm_only_key_entities_structured_v0924_full_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok5000_20260622.jsonl`
- Result: 25 call failures and 25 parse failures.
- Cause: every response was truncated at `max_tokens=5000`; no scored mentions were recovered.

## Candidate-Backed Strict Action Iteration

Candidate-backed Qwen strict action adjudication was tested as a smaller
architecture. The model received candidate IDs and had to emit explicit
keep/reject actions; omitted IDs were rejected. A schema-format repair was added
for bare action lists and malformed rationale strings where the
`candidate_id`/`action`/`reason_code` triples were still explicit.

Dev25 passed the older non-rescue surface, but under the revised
generation-and-selection protocol this remains candidate-backed selector
evidence rather than Qwen extraction evidence:

- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev25`
- Assembly: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev25_20260623.json`

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.9450 | 0.9231 | 0.9680 | 121 | 10 | 4 |
| schema_format | 0.9450 | 0.9231 | 0.9680 | 121 | 10 | 4 |
| model_preserving_canonical | 0.9450 | 0.9231 | 0.9680 | 121 | 10 | 4 |
| hybrid_full_stack | 0.9535 | 0.9248 | 0.9840 | 123 | 10 | 2 |

The same strict-action architecture missed the older dev140 non-rescue gate by
a narrow margin after the protocol surface correction:

- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_strict_actions_dev140`
- Assembly: `experiments/exectv2_holistic_finding_assembly_v05_qwen_strict_actions_protocol_dev140_20260623.json`

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.8977 | 0.9117 | 0.8841 | 702 | 67 | 92 |
| schema_format | 0.8977 | 0.9117 | 0.8841 | 702 | 67 | 92 |
| model_preserving_canonical | 0.8977 | 0.9117 | 0.8841 | 702 | 67 | 92 |
| hybrid_full_stack | 0.9020 | 0.8960 | 0.9081 | 721 | 83 | 73 |

Per-family strict-action dev140 `model_preserving_canonical` F1:

- Diagnosis: 0.8795
- SeizureFrequency: 0.9053
- Prescription: 0.9247
- Investigations: 0.8880

The strict-action run shows that explicit keep/reject enumeration is close on
the older selector surface but still short of the `>0.900` non-rescue gate; it
also does not satisfy the revised model-origin requirement.

## Default-Keep Action Contract Diagnostic

A no-call default-keep replay was scored using the same Qwen action responses
and the prompt-declared action contract: candidate facts are kept unless Qwen
explicitly rejects them. This is a candidate-backed Qwen selection architecture,
not direct free-form Qwen extraction. Under the revised protocol, it is a hybrid
selector diagnostic because the primary surface preserves copied candidate facts
rather than facts generated by Qwen in this experiment condition.

- Candidate: `exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_dev140`
- Assembly: `experiments/exectv2_holistic_finding_assembly_v05_qwen_relaxed_actions_protocol_dev140_20260623.json`

| Surface | Overall F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| raw_model | 0.9155 | 0.9141 | 0.9169 | 728 | 68 | 66 |
| schema_format | 0.9155 | 0.9141 | 0.9169 | 728 | 68 | 66 |
| model_preserving_canonical | 0.9155 | 0.9141 | 0.9169 | 728 | 68 | 66 |
| hybrid_full_stack | 0.9091 | 0.8978 | 0.9207 | 731 | 83 | 63 |

Per-family default-keep dev140 `model_preserving_canonical` F1:

- Diagnosis: 0.9090
- SeizureFrequency: 0.9053
- Prescription: 0.9357
- Investigations: 0.9132

This clears the older non-rescue surface for the candidate-backed Qwen
action-selection route, but it does not clear the revised LLM-attributed Qwen
gate because the scored facts come from candidate bundles and are kept by
default unless Qwen emits a verified reject.

## Protocol Surface Correction

Earlier tables in this report used the assembly `dictionary_normalized` surface
as a proxy for `model_preserving_canonical`. That proxy is conservative but not
identical to the repair-attribution protocol: it runs final entity lenses and
can drop model-selected overcalls, while the protocol requires those overcalls
to remain visible as model false positives. The assembly now materializes
`protocol_model_preserving_canonical`, which preserves the source-scored
model-selected fact inventory and excludes post-model residual additions from
the primary score.

## Interpretation

The direct compact Qwen route did not generalize, but the candidate-backed Qwen
action-selection route exposed a strong hybrid candidate-selector path. Under
the revised protocol, the default-keep result should be described as
candidate-backed hybrid adjudication, not Qwen extraction and not a
promotion-relevant Qwen model-quality pass. The stricter explicit-action
ablation remains useful as selector evidence, but the next qualifying Qwen
experiment must have Qwen generate the scored facts and then select among those
model-generated facts.
