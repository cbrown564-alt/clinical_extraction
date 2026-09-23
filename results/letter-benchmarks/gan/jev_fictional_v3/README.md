# Jev classification and verification pilot v3

Completed 2026-09-22 (Europe/London) on 16 fictional letters: eight development and eight reserved.
The split preceded question implementation; inputs, scoring and references were
frozen before either comparison. Reserved predictions were inspected only after
development, with no intervening question or key changes. This is not a clinical
holdout or clinical validation.

**Decision: do not expand this Jev candidate to dev750.** The narrower task still
shows recurring classification failures. Verification trades a task-specific error
flag for substantial unnecessary review and accepts one clearly wrong seeded claim.
The evidence does not justify another broad run or adding Jev to the paper method.

## Standalone classification

| Measure | Jev development | DeepSeek development | Jev reserved | DeepSeek reserved |
| --- | ---: | ---: | ---: | ---: |
| Correct decisions | 91/100 | 100/100 | 84/100 | 99/100 |
| Exact candidate-task answers | 5/8 | 8/8 | 2/8 | 7/8 |
| Correct coverage judgments | 8/8 | 8/8 | 8/8 | 8/8 |
| Current finding TP / FP / FN | 7 / 3 / 2 | 8 / 0 / 1 | 8 / 2 / 2 | 9 / 0 / 1 |

The common task classifies role, kind and outer/inner field applicability for
source-derived candidates, plus candidate-list coverage. It does not extract
numerical values or discover arbitrary findings. Exact candidate-task correctness
can coexist with an omitted finding when the model correctly reports missing
coverage; omitted source findings remain in recall denominators. Both splits
contain one intentionally omitted current finding.

Jev's failures include treating confirmed non-epileptic attacks as current seizures,
assigning a sibling's events to the patient inventory, treating unresolved
contradictory accounts as current facts, and calling a recent observed count
historical. It also mishandles context-only sentences and prospective thresholds.
These challenge the earlier v2 success on easier role labels. Results across v2
and v3 have different tasks and denominators and must not be pooled.

## Verification and the hybrid

| Measure | Development | Reserved |
| --- | ---: | ---: |
| Actual correct DeepSeek proposals accepted | 17/23 | 17/22 |
| Actual correct proposals deferred | 6/23 | 5/22 |
| Actual wrong proposals accepted | No wrong proposals | 0/1 |
| Seeded wrong proposals accepted | 0/24 | 1/24 |
| Seeded correct proposals deferred | 1/8 | 1/8 |
| Hybrid retained current finding TP / FP / FN | 7 / 0 / 2 | 9 / 0 / 1 |

The hybrid adds a Jev clinical call after DeepSeek. Accept releases a candidate
unchanged; reject/uncertain/missing defers it to review. There is no field masking,
reclassification or repair. It accepted 34 of 46 actual proposals, deferred all
12 others, and unnecessarily deferred 11 of the 45 reference-correct proposals.
All observed deferrals in this run were explicit reject verdicts. Across both
splits, current finding recall after automatic release fell from 17/19 for DeepSeek
to 16/19 for the hybrid. No human review outcomes are simulated.

The seeded false acceptance was `r_cluster.s0`: a source explicitly describes
4 grouped seizure days per month with 9 seizures in 24 hours on each such day.
Jev accepted a proposal marking the inner-count field **not applicable**, despite
that explicit within-group quantity. This error is independent of the disputed
future-threshold reference described below. Seeded challenges contain one correct
and three single-field corruptions per letter, with hidden labels and shuffled
proposal order. They are a controlled stress test, not an estimate of real error
prevalence. The [verification decisions](verification_decisions.json) preserve
every proposal, reference and verdict.

## Reference sensitivity

DeepSeek V4 Pro independently labelled all 48 source sentences without author
keys or evaluation predictions. It agreed on 191/192 fields. The disagreement was
`r_cluster.s2.inner_applicable`, a hypothetical cluster-day threshold without a
stated cluster size. Codex retained yes before evaluation because the written
rule defines field applicability by grouped structure, even when the value is
unstated. The original review and adjudication are preserved.

DeepSeek Flash's sole mismatch is this same field, and Jev rejected that tuple.
That is an error under the frozen operational definition, not a demonstrated
incorrect clinical quantity. A **post-hoc reference sensitivity check** treating the
reviewer's no as correct would make DeepSeek 200/200 and all 12 hybrid deferrals
unnecessary. The main reference and scores remain unchanged. Consequently, the
single actual error caught is weak evidence for benefit; the seeded false acceptance
and recurring classification failures still support the no-expansion decision.

## Time, cost and execution

- Jev classification: mean 0.768 seconds per letter; peak-rate cost estimate US$0.004017.
- DeepSeek classification: mean 6.141 seconds; US$0.052007.
- Jev verification: additional mean 0.596 seconds; US$0.001161.
- Hybrid: sum of mean request times approximately 6.737 seconds; classification plus verification US$0.053168.
- Challenge verification: US$0.001542; source review: US$0.033896.
- Total for 65 calls: **US$0.092623** peak-rate upper estimate, below the US$2 cap and US$0.797639 reservation.

These are measured-token estimates at published peak rates, not invoices. Latencies
are single observations, include network/provider time and do not establish general
throughput. Models were Jev 1.13.0 and the DeepSeek Flash alias, with DeepSeek V4 Pro
for reference review. An immutable DeepSeek backend checkpoint is not claimed.

Every network call returned successfully; no retries or repairs occurred. A local
startup accounting-file race occurred before the first standalone Jev call; runs
were subsequently serialised without changing the freeze. Run one pilot command
at a time. No dev750, locked-test or patient data was used in this pilot.

## Evidence and replay

- [Frozen settings and hashes](freeze.json), [original split](split_lock.json).
- [Source review](review.json), [adjudication](adjudication.json).
- [Machine report](report.json), [decision and sensitivity](decision.json).
- [Verifier proposals and verdicts](verification_decisions.json), [checks](verification.json).

Raw requests/responses, returned versions, usage and timing are local under
`runs/jev_fictional_v3/`. Literal numeric candidates are stored separately without
semantic binding. Native Gan answers, complete numerical finding records and
clinical utility are not evaluated. Both the author and model reviewer can share
reference bias; no clinician reference panel has validated these fixtures.

```sh
.venv/bin/python -m scripts.benchmarks.jev_verifier_pilot report > /tmp/jev-v3-report.json
cmp /tmp/jev-v3-report.json results/letter-benchmarks/gan/jev_fictional_v3/report.json
```

Offline report replay was byte-identical. Frozen inputs and v2 artifacts are
unchanged. 836 always-on tests, Ruff, mypy (422 files), offline scoring controls,
source isolation and documentation hygiene passed. Main-paper work remains with
its existing owners: adjudicating the remaining v0.7 source ambiguities and completing R7
schema-failure/rich-simple disagreement analysis.
