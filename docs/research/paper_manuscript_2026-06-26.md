# Modular and Auditable Clinical Extraction from Epilepsy Letters

Updated: 2026-07-14
Status: synchronized working manuscript

This manuscript is governed by the
[paper claims register](../canon/10_paper_provenance.md) and the
[retained evidence manifest](../experiments/retained_evidence_manifest.md).
It intentionally omits closed candidates and claims whose supporting evidence
is not selected in the reduced repository.

## Abstract

Clinical extraction systems need more than a single aggregate score: their
model, deterministic rules, repairs, evidence, scorer, and evaluation boundary
must remain separately inspectable. We evaluate a modular architecture on two
epilepsy-letter tasks: current seizure-frequency labeling on the Gan 2026
synthetic benchmark and broad epilepsy phenotyping on ExECTv2. For each task we
retain rules-only, LLM-only, and hybrid reference cells with executable source
closure and no-call replay. On Gan validation750, the retained rules, LLM-only,
and structured-event hybrid cells obtain 697/750, 581/750, and 661/748 rendered
Purist-correct predictions, respectively. The frozen Gan holdout evidence is
364/450 Purist for the operational single-pass structured-event system and
379/450 for a more complex multi-trace ceiling comparator. On ExECT dev140,
the deterministic reference reaches 0.3548 strict per-item F1, the GEPA
LLM-only negative comparator reaches 0.7393 clinical-headline F1, and holistic
hybrid assembly reaches 0.9189 clinical-headline F1. A bounded same-core
full200 aggregate comparison spans 0.8197-0.8566 clinical-headline F1 across
Qwen 3.6 35B, GPT-4.1-mini, and DeepSeek chat. Saved-output ablations show
positive normalization contributions on both tasks (+0.0389 ExECT; +0.0293
Gan), while the evidence check is score-inert on those representative replays.
The contribution is therefore a reproducible, stage-owned comparison with
explicit claim boundaries, not a claim of independent clinical validation,
strict ExECT benchmark reproduction, or a completed six-model result.

## 1. Introduction

Epilepsy letters combine temporal reasoning, clinical terminology, medication
regimens, investigation findings, and ambiguous current-versus-historical
statements. Large language models can broaden extraction, but a model call can
also hide where a result came from. Deterministic systems are easier to inspect,
yet often fail on linguistic variation and long-range clinical selection.

We study these approaches as explicit architecture families rather than as one
opaque pipeline. The same project contains a deep single-label task and a broad
multi-entity task. This makes it possible to ask which stages transfer, which
results depend on task-specific scoring, and where evidence is insufficient for
a stronger claim.

The paper makes four bounded contributions:

1. a retained two-task by three-family comparison with exact replay closure;
2. explicit ownership of extraction, normalization, projection, repair,
   evidence validation, and scoring;
3. frozen aggregate evidence for the Gan operational-versus-ceiling trade-off
   and a three-model ExECT transfer study; and
4. reproducibility controls that pin prompts, scorers, splits, repair policies,
   runtime identifiers, dependencies, and artifact hashes.

## 2. Related work

ExECT demonstrated structured epilepsy extraction from unstructured clinic
letters and later work documented the corresponding annotation resource
[1,2]. Seizure-frequency extraction has also been studied with machine-reading
and pretrained-language-model approaches [3,4], while recent work has explored
fine-tuned LLMs and reproducible synthetic clinical letters [5,6]. Our focus is
complementary: we treat pipeline stages and evidence boundaries as part of the
scientific object, and compare rules-only, LLM-only, and hybrid forms without
collapsing their different scoring and repair mechanisms.

## 3. Methods

### 3.1 Tasks and split policy

Gan 2026 asks for one current seizure-frequency label per synthetic letter.
Validation750 is the row-inspectable development and replay surface. Test450 is
a locked holdout: only frozen aggregate results are retained, and row-level
holdout failures are not used for development.

ExECTv2 covers Diagnosis, SeizureFrequency, Prescription, and Investigations in
the primary comparison, with additional entities retained in the deterministic
all-nine reference. Dev140 is the row-inspectable development surface. Full200
combines dev140 with held-out test60 and is reported only as a
development-inclusive aggregate audit; it is not an independent holdout.

### 3.2 Architecture families

For each task, the retained manifest contains exactly one rules-only, LLM-only,
and hybrid cell.

- Rules-only cells use deterministic extraction, normalization, projection,
  validation, and rendering without model calls.
- LLM-only cells concentrate clinical extraction in one model program. The
  ExECT GEPA cell is retained as a negative development comparator, not as the
  production control.
- Hybrid cells keep model-owned clinical extraction distinct from
  deterministic selection, normalization, evidence checks, and scoring. Gan
  uses one structured-event pass; ExECT uses manifest-driven finding assembly
  with family-specific lenses.

### 3.3 Scoring surfaces

Gan uses Purist and Pragmatic label scoring. Purist is the primary strict label
surface. ExECT's primary research-control surface is de-duplicated
`clinical_headline` recovery across four families. Phrase, CUI, evidence-valid,
and full-attribute companions are reported separately. `clinical_headline` is
not presented as reproduction of the published strict ExECT benchmark.

### 3.4 Repair and attribution

Raw model selection, JSON/format repair, source-exact evidence repair,
deterministic semantic repair, projection, and final scoring are separate
stages. Model-specific transport or output-shape adapters do not become model
quality evidence. Semantic repairs retain a named deterministic owner and must
be ablated or otherwise tested before supporting a causal interpretation.

### 3.5 Architecture freeze and reproducibility

Freeze `reduced_reference_architecture_20260714` pins the implementation at
commit `465621341c6af59f2fc028be7bf5f9e325739c50`. Manifest v3 fingerprints the
dependency declaration and lock, prompt contracts, scorers, split manifests,
repair policies, model policy, split runbook, and CI workflow. A semantic
prompt, scorer, split, repair, runtime-route, or component-graph change requires
a new freeze and complete replay. The freeze does not itself authorize model
calls.

## 4. Results

### 4.1 Retained two-task architecture comparison

Table 1 is the minimum retained scientific comparison. Scores are not compared
across tasks because the datasets, outputs, and scorers differ.

**Table 1. Retained reference cells.**

| Task | Family | Split | Retained result | Role and boundary |
| --- | --- | --- | ---: | --- |
| ExECTv2 | Rules only | dev140 | strict item F1 0.3548 | Incomplete deterministic development reference |
| ExECTv2 | LLM only | dev140 | headline F1 0.7393 | GEPA negative development comparator |
| ExECTv2 | Hybrid | dev140 | headline F1 0.9189 | Current development performance control |
| Gan 2026 | Rules only | validation750 | 697/750 Purist | Deterministic development comparator |
| Gan 2026 | LLM only | validation750 | 581/750 Purist | Single-pass development comparator |
| Gan 2026 | Hybrid | validation750 | 661/748 rendered Purist | Single-pass structured-event comparator |

All six cells replay from current code and retained outputs without model calls.
The ExECT hybrid replay also returns evidence-valid F1 0.8913. Its current
benchmark/CUI companion is 0.4791 versus 0.4729 in the retained run artifact;
this companion-scorer drift is open and does not affect the reproduced 0.9189
headline result.

### 4.2 Gan frozen holdout evidence

**Table 2. Gan operational and ceiling evidence on locked test450.**

| System | Purist | Role | Boundary |
| --- | ---: | --- | --- |
| Single-pass structured-event system | 364/450 (0.809) | Operational close-off result | Frozen aggregate only |
| V12 multi-trace reviewer | 379/450 (0.842) | High-complexity ceiling comparator | Saved aggregate; source candidate removed |

The 15-row quality difference does not yet support an efficiency conclusion.
A matched table of calls, tokens, cost, latency, hardware, and cache policy
remains open.

### 4.3 ExECT same-core model evidence

The retained model-transfer package holds the two-call no-SF-adjudicator
component graph fixed while changing the runtime model. Table 3 is a full200
development-inclusive aggregate read; no test60 row-level analysis is used.

**Table 3. ExECT same-core full200 aggregate `clinical_headline`.**

| Model condition | Overall | Diagnosis | SF | Prescription | Investigations | Call / parse failures |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeepSeek chat | 0.8566 | 0.8708 | 0.7602 | 0.8926 | 0.9091 | 0 / 1 |
| GPT-4.1-mini | 0.8356 | 0.8397 | 0.7525 | 0.8926 | 0.8563 | 0 / 0 |
| Qwen 3.6 35B repair v02 | 0.8197 | 0.8307 | 0.7020 | 0.8926 | 0.8503 | 0 / 0 |

These runs support a bounded same-core transfer statement. They are not a
strict same-prompt panel: the retained GPT condition used temperature 0.3, and
Qwen used a compact prompt and output-contract repair. The requested six-model
comparison remains incomplete, with three missing runtime conditions requiring
predeclaration.

### 4.4 Cross-task component evidence

**Table 4. Saved-output component ablation.**

| Component | ExECT dev140 delta | Gan validation750 delta | Interpretation |
| --- | ---: | ---: | --- |
| Normalization / standard dictionary | +0.0389 | +0.0293 | Positive on both representative replays |
| Evidence validation | 0.0000 | 0.0000 | Score-inert on these replays; safety behavior tested directly |

The zero score delta does not show that evidence validation is unnecessary. A
filter may be essential on malformed or hallucinated outputs even when all
selected reference predictions already satisfy it. Rejection and repair tests,
not aggregate F1 alone, carry that part of the evidence.

### 4.5 Reliability and evidence state

**Table 5. Retained reliability evidence and limits.**

| Subject | Retained result | Boundary |
| --- | --- | --- |
| ExECT evidence | Hybrid dev140 minimum exact evidence rate 1.0000 | Development reference |
| ExECT internal calibration | Brier 0.2225; base-rate Brier 0.2340; ECE 0.0587 | Full200 aggregate scoring-rule result |
| Gan grounding | Architecture-specific validation grounding packages retained | Metrics are not uniform across families |
| Fresh-checkout reproducibility | 1,153 tests, Ruff, mypy, manifest hashes, split barriers, and six-cell replay pass on Python 3.11 | Engineering verification, not clinical validation |

Model-reported confidence remains unused, and no low-burden review-routing
policy is promoted. The manifest does not retain evidence for a cross-task
Wall-transfer claim.

## 5. Discussion

The strongest result is structural rather than universal. The reduced system
can reproduce six architecture cells while keeping component ownership and
evaluation boundaries explicit. Hybrid assembly is substantially stronger than
the retained ExECT rules-only and LLM-only development references on
`clinical_headline`, but the three cells do not share a strict published
benchmark surface. The deterministic paper-comparable engineering remains open.

The model-transfer result shows that the component graph runs with three
qualitatively different runtime models. DeepSeek leads the retained full200
aggregate, while Qwen trails most clearly on SeizureFrequency. Because runtime
conditions are asymmetric and the panel is only three of six, this is evidence
of bounded portability rather than a universal model-agnostic claim.

The cross-task ablation suggests that normalization is useful in both tasks.
The evidence gate's zero F1 delta illustrates why clinical pipeline evidence
cannot be reduced to aggregate score changes: rejection, provenance, and repair
behavior need direct contract tests.

## 6. Limitations

- Gan test450 is frozen aggregate evidence and cannot support row-level tuning.
- ExECT full200 includes dev140 and is not an independent holdout.
- `clinical_headline` is a clinical-recovery surface, not the published strict
  benchmark.
- The ExECT benchmark/CUI companion has small current-code replay drift that
  remains open.
- The model panel is three of six and uses asymmetric runtime conditions.
- Model-reported confidence and low-burden review routing are not validated.
- Annotation-quality findings are internally adjudicated; unqualified clinical
  validity would require independent domain review.
- The current evidence does not support an ExECT Wall-transfer claim.

## 7. Conclusion

A small, frozen, stage-owned clinical extraction system can preserve both
performance evidence and the provenance needed to interpret it. The retained
results support a two-task rules/LLM/hybrid comparison, a bounded Gan
operational-versus-ceiling result, and a three-model ExECT same-core study. They
do not yet support strict ExECT benchmark reproduction, a six-model conclusion,
or independent clinical validation. Those boundaries are part of the result,
not footnotes to it.

## References

1. Fonferko-Shadrach B, et al. Using natural language processing to extract
   structured epilepsy data from unstructured clinic letters: development and
   validation of the ExECT system. *BMJ Open*. 2019;9:e023232.
2. Fonferko-Shadrach B, et al. Annotation of epilepsy clinic letters for natural
   language processing. *Journal of Biomedical Semantics*. 2024;15:17.
3. Xie K, et al. Extracting seizure frequency from epilepsy clinic notes: a
   machine reading approach. *JAMIA*. 2022;29:873-881.
4. Abeysinghe R, et al. Leveraging pretrained language models for seizure
   frequency extraction from epilepsy evaluation reports. *npj Digital
   Medicine*. 2025.
5. Holgate B, et al. Fine-tuning LLMs to extract epilepsy seizure frequency data
   from health records. *BioNLP*. 2025:44-55.
6. Gan Y, et al. Reproducible synthetic clinical letters for seizure frequency
   information extraction. arXiv:2603.11407. 2026.
