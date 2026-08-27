# Six-model competence by gold task category

Date: 2026-08-06 (rules surface and ExECT within-family cuts extended 2026-08-08)
Status: development answer on retained / regenerated no-call artifacts  
Paper-library role: technical category record; start with the [Gan story](../paper/gan_story_2026-08-10.md) or [ExECT story](../paper/exect_story_2026-08-12.md)

Protocol: [category-cut protocol](six_model_category_cut_protocol_2026-08-06.md)  
Parent: [task-shape framework](task_shape_framework_2026-08-06.md)  
Artifact: [`experiments/six_model_category_cut_performance_20260806.json`](../../experiments/six_model_category_cut_performance_20260806.json)  
ExECT rules letter scores: pruned 2026-08-16
(`experiments/exectv2_rules_only_four_family_letter_scores_dev140_20260806.jsonl`;
recover from Git history). Living category-cut package remains this report's
JSON artifact below.

Readable development-row companions: [Gan representative examples](../gan2026/category_cut_representative_examples_2026-08-08.md) and [ExECT representative examples](../exectv2/category_cut_representative_examples_2026-08-08.md). The companion artifact is [`experiments/category_cut_representative_examples_20260808.json`](../../experiments/category_cut_representative_examples_20260808.json).

## Plain answer

Category competence is three-method, not two.

**Rules only (single deterministic system):** on Gan, almost every a_priori
bucket is already **high** (ordinary rates 0.96; clusters 0.89; free/range/no-
reference ≥ 0.97). Only `unknown_sentinel` is mid (0.79). On ExECT, rules own
Prescription (0.96), Diagnosis (0.86), and SeizureFrequency (0.83 primary;
0.85 under the category-cut helper) as **high**, while Investigations is a
hard **floor** (0.53).

**LLM only:** on Gan, the largest bucket—ordinary point rates—is a **shared
floor** (0.61–0.71). Only unresolved multiples meet strict **x**. Clusters are
strict **z**. On ExECT, complete prescriptions are common competence; normal
MRI is also strong. Single-seizure Diagnosis is the only sufficiently populated
strict floor, while qualitative SF change stays low across the roster.

**LLM with rules:** Gan’s hybrid easy mass appears for models that lack the
rules-only extractor (free/range/no-reference **x**); clusters stay the hybrid
practical floor. On ExECT, complete prescriptions remain strict **x** and
Diagnosis rules lift all three Diagnosis subtypes. SF remains mixed rather than
becoming common competence; hybrid post-LLM rules are not the same as the
independent rules-only method.

## How to read this

Six-model surfaces (`llm`, `llm_with_rules`):

| Lens | Rule (enough mass) |
| --- | --- |
| **x** | min ≥ 0.85 and spread ≤ 0.08 |
| **z** | max ≤ 0.75 |
| **y** | neither |

Single-system `rules` bands (same score thresholds; not multi-model agreement):

| Band | Rule |
| --- | --- |
| **high** | score ≥ 0.85 |
| **floor** | score ≤ 0.75 |
| **mid** | neither |

| Track | `rules` source | `llm` source | `llm_with_rules` source |
| --- | --- | --- | --- |
| Gan | retained three-way deterministic JSONL | validation `*--llm_only.jsonl` Purist | v0.5 attribution + floors patch |
| ExECT | regenerated four-family letter scores | `raw_lane_mentions` via clinical-headline helper | `predicted_mentions` (panel-matched) |

Gan panel reconstruction matches llm / hybrid. ExECT `llm_with_rules` matches
panel; ExECT `llm` and `rules` use the clinical-headline helper. ExECT rules
helper overall is **0.8196**; Decision 0046 `headline_target` remains
**0.8160** (SF is the main helper vs headline gap). Holdout rows were not
opened.

---

## Gan 2026 (`dev750` Purist)

### Overall

| Surface | Band / score |
| --- | --- |
| rules | **0.9293** (single system) |
| llm | ~0.68–0.79 (six models) |
| llm_with_rules | ~0.84–0.90 (six models) |

### Three-way a_priori buckets

| Bucket | n | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- | --- |
| `ordinary_point_rate` | 312 | 0.96 (**high**) | 0.61–0.71 (**z**) | 0.82–0.89 (**y**) |
| `cluster_burden` | 64 | 0.89 (**high**) | 0.31–0.59 (**z**) | 0.52–0.77 (**y**) |
| `seizure_free` | 112 | 0.97 (**high**) | 0.78–0.95 (**y**) | 0.95–1.00 (**x**) |
| `range_rate` | 92 | 0.98 (**high**) | 0.75–0.85 (**y**) | 0.89–0.96 (**x**) |
| `no_reference_sentinel` | 27 | 1.00 (**high**) | 0.04–1.00 (**y**) | 0.96–1.00 (**x**) |
| `unresolved_multiple` | 43 | 0.86 (**high**) | 0.93–1.00 (**x**) | 0.93–1.00 (**x**) |
| `unknown_sentinel` | 100 | 0.79 (**mid**) | 0.81–0.89 (**y**) | 0.77–0.87 (**y**) |

Rules-only already owns the mass that hybrid later makes look like common
model competence. Hybrid still fails to make clusters common across models
(best 0.77) even though rules-only clusters are **high**.

### llm only — x / y / z

**x:** `unresolved_multiple` only.  
**y:** unknown, range, seizure-free, no-reference.  
**z:** `ordinary_point_rate`, `cluster_burden`.

Without the model lane’s post-processing, the **largest gold mass is a shared
floor**.

### llm_with_rules — x / y / z

**x:** `seizure_free`, `range_rate`, `no_reference_sentinel`, `unresolved_multiple`  
**y:** `ordinary_point_rate`, `unknown_sentinel`, `cluster_burden`  
**practical z:** `cluster_burden` (no strict z; best only 0.77)

---

## ExECTv2 (`dev140` four-family clinical fact F1)

### Overall

| Surface | Band / score |
| --- | --- |
| rules (helper) | **0.8196** (Decision 0046 headline 0.8160) |
| llm (helper on raw lane) | ~0.74–0.85 |
| llm_with_rules | ~0.80–0.90 |

### Family roll-up (secondary)

| Family | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | --- | --- | --- |
| Prescription | 0.96 (**high**) | 0.85–0.95 (**y**) | 0.87–0.94 (**x**) |
| Diagnosis | 0.86 (**high**) | 0.69–0.77 (**y**) | 0.84–0.89 (**y**) |
| SeizureFrequency | 0.83 (**high**)* | 0.59–0.79 (**y**) | 0.62–0.83 (**y**) |
| Investigations | 0.53 (**floor**) | 0.80–0.95 (**y**) | 0.80–0.95 (**y**) |

\* The displayed family value is the Decision 0046 `headline_target` fill;
the category-cut helper used for letter-bucket parity reports 0.8503.

Rules-only already owns Prescription and strong Diagnosis/SF on development.
Investigations is model-carried: rules are the floor; llm / hybrid stay mid-to-
high. Hybrid SF remains a practical floor across models even though rules-only
SF is **high**—do not conflate independent rules-only with post-LLM family
rules. This roll-up is no longer the primary category analysis.

### Primary within-family subtype cuts

Gold subtype selects the development letters; the unchanged scorer evaluates
only the named family on those letters. Subtypes can overlap when a letter has
several facts. `n` is the number of letters carrying the gold subtype. A dash
means `n < 10`, so no band or x/y/z lens is assigned.

#### Diagnosis

| Gold subtype | n | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- | --- |
| `epilepsy` | 118 | 0.89 (**high**) | 0.64–0.77 (**y**) | 0.82–0.89 (**y**) |
| `multiple_seizures` | 94 | 0.88 (**high**) | 0.62–0.77 (**y**) | 0.81–0.90 (**y**) |
| `single_seizure` | 16 | 0.81 (**mid**) | 0.55–0.75 (**z**) | 0.74–0.82 (**y**) |

The family roll-up hid the clearest Diagnosis result: single-seizure concepts
are a shared LLM-only floor. Diagnosis rules lift every subtype, but the rare
single-seizure slice remains weaker than epilepsy and multiple-seizure facts.

#### SeizureFrequency

| Gold subtype | n | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- | --- |
| `seizure_free` | 46 | 0.84 (**mid**) | 0.60–0.85 (**y**) | 0.63–0.87 (**y**) |
| `numeric_cadence_rate` | 51 | 0.87 (**high**) | 0.69–0.83 (**y**) | 0.70–0.84 (**y**) |
| `count_in_named_window` | 19 | 0.90 (**high**) | 0.61–0.92 (**y**) | 0.63–0.92 (**y**) |
| `qualitative_frequency_change` | 27 | 0.86 (**high**) | 0.67–0.76 (**y**) | 0.67–0.77 (**y**) |

The useful SF distinction is not “letter has SF.” Active numeric cadence is
steadier; named-window counts separate models most; seizure-free remains
surprisingly variable; qualitative change is low across models and gains
little from the family rules. This is the ExECT analogue of Gan's rate /
seizure-free / sentinel distinctions.

#### Prescription

| Gold subtype | n | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- | --- |
| `complete_regimen` | 113 | 0.97 (**high**) | 0.88–0.96 (**x**) | 0.87–0.95 (**x**) |
| `rescue_as_required` | 5 | 0.97 (—) | 0.71–0.94 (—) | 0.76–0.94 (—) |

Complete regimens, not Prescription as an undifferentiated family, are the
large shared-competence mass. Rescue prescriptions are too sparse for a lens.

#### Investigations

| Gold subtype | n | rules (band) | llm min–max (lens) | llm_with_rules min–max (lens) |
| --- | ---: | --- | --- | --- |
| `mri_normal` | 37 | 0.79 (**mid**) | 0.86–0.95 (**y**) | 0.86–0.95 (**y**) |
| `mri_abnormal` | 23 | 0.30 (**floor**) | 0.79–0.96 (**y**) | 0.79–0.96 (**y**) |
| `eeg_abnormal` | 39 | 0.59 (**floor**) | 0.81–0.96 (**y**) | 0.81–0.96 (**y**) |
| `eeg_normal` | 14 | 0.79 (**mid**) | 0.87–0.96 (**y**) | 0.87–0.96 (**y**) |
| CT and unknown-result subtypes | 1–8 | reported in artifact; no lens | reported | reported |

The rules-only Investigations floor is specifically abnormal MRI and abnormal
EEG recovery, not a uniform inability to extract investigations. The model and
hybrid surfaces are identical because the selected family rules are a no-op.

### Secondary whole-letter composition

The artifact retains `multi_mention_with_sf` and the other whole-letter
buckets for workload and interaction analysis. They no longer determine ExECT
x/y/z conclusions or representative-example coverage because they combine
unrelated family problems.

---

## Do models “perform similarly”?

| Surface | Similar overall? | What the category cut shows |
| --- | --- | --- |
| Gan rules | n/a (one system) | Mass competence already present without a model |
| Gan llm | Yes, compressed low band | Similarity is **shared weakness** on ordinary rates + clusters |
| Gan llm_with_rules | Yes, higher band | Similarity is **shared strength** on free/range/sentinel mass; clusters still break multi-model agreement |
| ExECT rules | n/a (one system) | Owns Rx/Dx/SF; Investigations floor |
| ExECT llm | Moderately | No strict x; Diagnosis and SF pull everyone down |
| ExECT llm_with_rules | Yes, higher band | Prescription carries ease; SF still separates |

## Holdout (aggregate only)

Sibling study:
[sealed holdout category aggregates](six_model_holdout_category_aggregates_2026-08-06.md).
ExECT `test60` family lenses are answered from the public stage panel; Gan
a_priori and ExECT letter-bucket holdout scores are unlocked via machine-only
sealed scoring in
[holdout category aggregates](six_model_holdout_category_aggregates_2026-08-06.md).
The report also includes the rules-only family column from the Decision 0046
aggregate. Gold mix share shifts stay small.

## Claim boundary

- Development category competence on **rules**, **llm**, and **llm_with_rules**.
- Rules bands are single-system; x/y/z remain six-model only.
- Regenerable via
  `python scripts/build_exectv2_rules_only_four_family_letter_scores_dev140.py`
  then `python scripts/build_six_model_category_cut_performance.py`.
- ExECT rules helper F1 is not a rewrite of Decision 0046 `0.8160`.
- DeepSeek Gan `llm` `dev750` remains pre-0731.
- Not a Decision 0046 method-fill rewrite.

## Next

0. Done: real development-letter companions for every mutually exclusive Gan
   bucket and every observed ExECT within-family subtype — [Gan](../gan2026/category_cut_representative_examples_2026-08-08.md),
   [ExECT](../exectv2/category_cut_representative_examples_2026-08-08.md).
1. Done: full error catalogs with examples —
   [Gan](../gan2026/category_error_catalog_2026-08-06.md),
   [ExECT](../exectv2/family_error_catalog_2026-08-06.md).
2. Done: hybrid stage ablations + cross-task packaging —
   [synthesis](cross_task_hybrid_mechanism_synthesis_2026-08-06.md).
3. Done: [sealed holdout category aggregates](six_model_holdout_category_aggregates_2026-08-06.md)
   (family lenses + rules column + unlocked Gan a_priori / ExECT letter-bucket holdout scores).
