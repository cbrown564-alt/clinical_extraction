# One-call seizure-frequency study protocol

Owner: Conor Brown. Locked 2026-09-24. This document owns the study question,
conditions, endpoints, execution settings and run record. The
[annotation guide](seizure_frequency_annotation_guide.md) owns the finding
definition and reference. The [roadmap](../../plans/ACTIVE_ROADMAP.md) owns
priorities; the [paper outline](../../../publications/jamia-one-shot/README.md)
owns the manuscript.

## Question

Can one clinical inference call return the established single seizure-frequency
answer with the same accuracy as an answer-only request, while also returning a
richer, inspectable inventory of the seizure-frequency statements behind it?

The native answer is the claim that must hold. The inventory is secondary and
descriptive: its boundaries (repeated events, labels, measurement wording) are
naturally less crisp than a single label, so it is scored leniently and never
used to tune prompts.

## Conditions

Exactly two conditions. Both use the same task, the original ten worked
selection cases, label forms, instructions, ChatAdapter envelope and note. Only
the output schema and its population instructions differ.

| Condition | Returns | Source |
| --- | --- | --- |
| `minimal` | `answer.label`, `answer.evidence` | The r4 answer-only request, byte-identical (sha256 `902bf3e2…99a4`). |
| `expanded` | The same answer plus `claim_indices` and every seizure-frequency finding under the annotation guide | Same request with the locked [expanded schema](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/one_call/expanded.schema.json). |

Code: `src/clinical_extraction/tasks/seizure_frequency/gan2026/one_call/`
(`prompts.py`, `parse.py`, `findings_score.py`, `analysis.py`). Rendered
no-call requests: `results/letter-benchmarks/gan/one_call/rendered/`.
`tests/test_one_call.py` protects prompt identity, condition parity, strict
parsing and the finding score. Change a prompt, the schema or the scorer only
by an owner decision recorded here; do not create numbered revisions.

## Data

| Source | Role | Conditions of use |
| --- | --- | --- |
| Gan synthetic dev750 | Development and the paired comparison; all 750 rows including `row_ok=False`. | Previously exposed; development evidence only. |
| Gan synthetic test450 | One frozen evaluation of both conditions. | Aggregate-only. Needs the source-only re-annotation under the guide and a recorded freeze first. Never inspect predictions or failures. |
| Real Gan 300 | Primary real-letter answer agreement. | Pending written permission, exposure and eligibility metadata. Sealed. |

The [holdout policy](../../benchmarks/holdout-is-aggregate-only.md) applies.

## Endpoints

| Endpoint | Definition |
| --- | --- |
| **Primary: answer agreement** | Native Purist correct / all scheduled letters, per condition. The whole response must be usable; any failure counts as wrong. Pragmatic companion. Wilson 95% intervals. |
| **Primary contrast** | Expanded minus minimal, paired over letters: difference, wins/losses/ties and a paired percentile bootstrap 95% interval (seed 20260913, 10,000 replicates). Descriptive; no non-inferiority claim. |
| Declared-answer view | Same, judging only the declared answer even when the findings are invalid. Secondary. |
| Contract reliability | Failure categories (no response, truncation, envelope, syntax, schema, target label, missing evidence), exact-quotation rate, cost and latency. |
| **Findings (descriptive)** | Lenient precision, core recall and all-reference recall against the dev750 reference, with attribute agreement among matched pairs. Rule in the guide and `findings_score.py`. |

## Execution

DeepSeek `deepseek-flash` (documented V4.1 Flash), thinking enabled at low
effort, temperature 0 submitted, 24,000 output tokens, 600-second timeout,
concurrency 12. One first attempt per letter and condition; condition order
alternates between letters. No retry, format repair or semantic repair.
Deterministic code only parses, validates and scores.

```bash
.venv/bin/python -m scripts.benchmarks.one_call prepare
.venv/bin/python -m scripts.benchmarks.one_call run      # paid; needs authorisation
.venv/bin/python -m scripts.benchmarks.one_call score    # offline replay
```

Raw requests, responses and attempt ledgers stay local under
`runs/seizure_frequency/one_call/dev750/`; the aggregate goes to
`results/letter-benchmarks/gan/one_call/dev750/score.json`.

**Budget.** The study cap is US$100. Earlier runs charged US$69.1461255
(conservative). The runner reserves worst-case cost before calling: the paired
dev750 run reserves US$55.42, a bound of US$124.57, so it will refuse to start
until the cap is raised or the conditions are run separately. Expected actual
charge is about US$10 (R11 cost US$7.67 for 750 expanded calls).

## Run record

No run of the locked `expanded` prompt has been made yet.

History before the lockdown, for context only. All rows are dev750 answer
agreement on DeepSeek V4.1 Flash unless stated; they used different prompts
and schemas and are not results of the locked conditions.

| Run | Purist | Note |
| --- | --- | --- |
| v1 rich / simple (test450, thinking off) | 342 / 334 of 450 | First one-call comparison, 13 Sep. |
| r4 minimal | 658/750 | Mixed view with 14 timeout reruns; reproduced by the new parser. |
| r5 rich | 658/750 | Paired difference with r4: 0.00 (−1.73 to +1.60). |
| r6 original one-call prompt | about 599/750 | First attempt. |
| R7, R8 full inventory | 650, 638/750 | R8 lost answers to 31 schema-invalid records. |
| R9, R11 compact | 652, 651/750 | Declared-answer view; reproduced by the new parser. |

Replaying the archived R9 and R11 findings through the lenient scorer against
the locked reference gives precision 0.78 and 0.87, and core recall 0.82 and
0.81. The strict whole-claim scores of the same outputs were about 0.35 F1.
This replay is diagnostic only.

Everything removed at the lockdown is recoverable: Git tag
`archive/pre-lockdown-2026-09-24` holds the tracked code, prompts, guides,
scorers and results; `~/code/archives/clinical-extraction-runs-2026-09-24.tar.gz`
holds the local `runs/` directory, including raw responses and ledgers.

## Out of scope

Paper-pipeline replication, Jev, optimiser search, hybrid or two-call methods,
longitudinal work and further annotation-policy iteration. The dissertation's
two-stage results remain context only. The Holgate whole-prompt comparator stays
contingent on receiving the original prompt and its use conditions; it is not a
third locked condition.
