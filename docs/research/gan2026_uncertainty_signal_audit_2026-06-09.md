# Gan 2026 Uncertainty Signal Audit

Date: 2026-06-09

Author: Claude

Status: exploratory analysis — describes the current state of uncertainty/confidence
expression across all six architectures and what needs to change before Phase 3. No
architecture scores or holdout numbers are involved; all data is validation750 only.

Source script: `experiments/explore_uncertainty_signals.py`

Source data: `experiments/gan2026_three_way_comparison_validation750_*` JSONL files
(gpt-4.1-mini runs 2026-06-07/08, qwen3.6-35b runs 2026-06-08, deepseek-v4-flash runs
2026-06-08).

---

## 1. Inventory Of Uncertainty Signals Across Architectures

Ten distinct forms of uncertainty or confidence expression exist in the current codebase,
spread across five architectural layers. They do not share a common scale, vocabulary, or
ownership model.

| Signal | Layer | Type | Architectures |
| --- | --- | --- | --- |
| `certainty` (`certain`/`uncertain`) | Candidate extraction | 2-value enum | hybrid, `llm_only_structured_events` |
| `certainty_reason` (5 values) | Candidate extraction | enum, required when uncertain | hybrid, `llm_only_structured_events` |
| `assertion_status` (`asserted`/`negated`/`uncertain`/`conditional`) | Candidate extraction | 4-value enum | hybrid, `llm_only_structured_events` |
| `selection_mode` (`ambiguous`/`conflict`/`no_reliable_candidate`) | Selection | enum (3 of 5 values express uncertainty) | hybrid |
| `uncertainty_flags` (free text list) | Clinical assessment | unstructured | hybrid |
| `aggregation_policy` (8 values, 2 express uncertainty) | Clinical assessment | coded enum | hybrid |
| `normalization_issues` (free text list) | Clinical assessment | unstructured | hybrid |
| `uncertainty_flags` (tuple of strings) | Graph projection | unstructured, currently one value | `deterministic`, `deterministic_canonical_pipeline` |
| `route_families` (15 named values) | Verification route | enum | hybrid only |
| `confidence` (`low`/`medium`/`high`) | Final decision record | 3-value enum | `llm_only_direct_labeler`, `llm_only_canonical_pipeline` |
| `answer_kind` (`unknown`/`unresolved_multiple` as uncertainty outcomes) | Final decision record | enum | `llm_only_direct_labeler`, `llm_only_canonical_pipeline`, `llm_only_structured_events` |

The `llm_only_structured_events` and deterministic architectures have no scalar
confidence or uncertainty signal on the final decision record at all.

---

## 2. Confidence (low/medium/high) × Accuracy

Only `llm_only_direct_labeler` and `llm_only_canonical_pipeline` carry the `confidence`
field. Results across all three models:

| Architecture | Model | conf=high accuracy | conf=medium accuracy | conf=low accuracy |
| --- | --- | ---: | ---: | ---: |
| `llm_only_direct_labeler` | gpt-4.1-mini | 75.3% (n=749) | 0.0% (n=1) | — (n=0) |
| `llm_only_direct_labeler` | qwen3.6-35b | 73.3% (n=746) | 100.0% (n=2) | 100.0% (n=1) |
| `llm_only_direct_labeler` | deepseek-v4-flash | 78.4% (n=629) | 51.0% (n=102) | 68.4% (n=19) |
| `llm_only_canonical_pipeline` | gpt-4.1-mini | 77.5% (n=746) | 75.0% (n=4) | — (n=0) |
| `llm_only_canonical_pipeline` | qwen3.6-35b | 73.1% (n=739) | 100.0% (n=1) | 37.5% (n=8) |
| `llm_only_canonical_pipeline` | deepseek-v4-flash | 82.2% (n=556) | 50.8% (n=63) | 58.0% (n=131) |

**Key finding**: the `confidence` field is almost entirely degenerate for gpt-4.1-mini and
qwen. Both models assign `"high"` to 99%+ of rows — gpt-4.1-mini emits `"medium"` or
`"low"` on 1–5 rows out of 750; qwen on 3–9 rows out of 750. These counts are too small
to draw any conclusion from.

Deepseek is the only model that uses the field with a real distribution. When it does, the
signal is meaningful: medium and low rows are 25–30 percentage points below high rows.
The combined picture across all models and architectures (n=4,500 rows):

| confidence | correct | total | accuracy |
| --- | ---: | ---: | ---: |
| high | 3,179 | 4,165 | 76.3% |
| medium | 90 | 173 | 52.0% |
| low | 93 | 159 | 58.5% |

The aggregate gap is real (76% vs 52–58%), but it is entirely driven by deepseek.
gpt-4.1-mini and qwen do not contribute calibration information at all.

**Root cause**: the prompt defines `confidence` as a `Literal["low", "medium", "high"]`
field but gives no operational definition of what each level means. Without grounding,
instruction-following models collapse to the safest/most-positive answer.

---

## 3. answer_kind × Accuracy

`answer_kind` is present on `llm_only_direct_labeler` and `llm_only_canonical_pipeline`
and carries a typed classification of the outcome. It does **not** function as a
low-confidence signal in the expected direction:

| answer_kind | gpt41mini direct_labeler | gpt41mini canonical | deepseek direct_labeler | deepseek canonical |
| --- | ---: | ---: | ---: | ---: |
| `frequency` | 74.1% (n=498) | 75.2% (n=496) | 77.9% (n=457) | 82.8% (n=372) |
| `seizure_free` | 71.9% (n=153) | 79.3% (n=135) | 65.6% (n=160) | 69.0% (n=155) |
| `unknown` | **89.2%** (n=65) | **84.7%** (n=85) | 70.0% (n=80) | 64.0% (n=186) |
| `no_reference` | 79.4% (n=34) | 85.3% (n=34) | 77.4% (n=53) | 83.3% (n=36) |

`"unknown"` rows have *higher* accuracy than `"frequency"` rows for gpt-4.1-mini. This is
expected and correct: when the model identifies a case as genuinely unknowable, the gold
label tends also to be `"unknown"` or a close cousin — so the model gets credit. This
means `answer_kind` should not be treated as a difficulty or uncertainty signal. It is a
classification of the *type* of answer, not its reliability.

`seizure_free` is the consistently lowest-accuracy kind (65–79%) across models and
architectures. This is where clinical extraction error concentrates, not where the model
expresses uncertainty. The model is *confident* on seizure-free rows but more often wrong.

---

## 4. llm_only_structured_events: Accuracy by Predicted Category

`llm_only_structured_events` has no confidence or `answer_kind` field. The closest
uncertainty proxy is the predicted scoring category (gpt-4.1-mini run):

| predicted_purist_category | correct | total | accuracy |
| --- | ---: | ---: | ---: |
| `seizure_freq_1ormore_daily` | 53 | 54 | 98.1% |
| `seizure_freq_more1week_less1day` | 139 | 144 | 96.5% |
| `currently_no_seizure` | 103 | 108 | 95.4% |
| `seizure_freq_more1mon_less1week` | 94 | 108 | 87.0% |
| `seizure_freq_unknown` | 154 | 186 | 82.8% |
| `seizure_freq_more1per6mon_less1mon` | 68 | 81 | 84.0% |
| `seizure_freq_1_per_mon` | 31 | 37 | 83.8% |
| `seizure_freq_1_per_week` | 11 | 12 | 91.7% |
| `seizure_freq_1_per_6mon` | 5 | 10 | 50.0% |
| `seizure_freq_1_per_yr` | 3 | 8 | 37.5% |

The low-frequency boundary categories (`1_per_6mon`, `1_per_yr`) have substantially lower
accuracy (37–50%), consistent across all three models. This is a difficulty signal rooted
in category granularity, not in the model's expressed uncertainty.

---

## 5. Hybrid: uncertainty_flags Distribution and Vocabulary

`uncertainty_flags` is a free-text `list[str]` on `ClinicalAssessment`. Usage rates
differ markedly by model:

| Model | Rows with any flag | Rate |
| --- | ---: | ---: |
| gpt-4.1-mini | 24 / 749 | 3.2% |
| deepseek-v4-flash | 123 / 750 | 16.4% |
| qwen3.6-35b | 19 / 250 | 7.6% |

The flag *vocabulary* is entirely uncontrolled. Deepseek emits 50+ distinct string values
across 123 rows, covering largely overlapping concepts under different phrasing:

- Vague quantity: `vague_frequency`, `vague_count`, `uncertain_count`, `unquantified`,
  `no_exact_count`, `no_concrete_frequency`, `imprecise number of events per burst`
- Uncertain temporality: `unclear_temporality`, `unclear_temporal_window`,
  `uncertain_timing`
- Event-type uncertainty: `uncertain_event_type`, `unclear_event_type`,
  `event_type_uncertain`, `uncertain_semiology`, `uncertain_etiology`
- Patient-report unreliability: `patient_unable_to_quantify`, `patient-reported`,
  `unwitnessed_events`, `no external accounts`

gpt-4.1-mini uses 9 distinct values; qwen uses 16. The concepts are not aligned. A
flag that deepseek marks as `vague_count` might appear as `approximate_wording` in
gpt-4.1-mini (if it appears at all) or be absorbed silently into a different
`aggregation_policy` value. These flags cannot be aggregated or compared across models.

Note: there is a *different* `uncertainty_flags` field on `GanGraphProjection` (the
deterministic graph projection layer), which currently emits only one value:
`"competing_frequency_hypotheses"`. It shares the field name with the clinical-assessment
`uncertainty_flags` but is a separate concept at a different layer.

---

## 6. Hybrid: aggregation_policy × Model Divergence

`aggregation_policy` is a closed enum (8 values), so cross-model comparison is
structurally possible. In practice, model usage diverges substantially:

| aggregation_policy | gpt-4.1-mini | deepseek | qwen (250-row) |
| --- | ---: | ---: | ---: |
| `single_fact` | 60.2% | 47.3% | 80.8% |
| `primary_with_context` | 29.8% | 10.9% | 14.0% |
| `unknown_due_to_ambiguity` | **0.1%** | **13.1%** | 2.0% |
| `seizure_free_state` | 1.5% | **19.1%** | 0.4% |
| `additive_same_window` | 4.7% | 4.1% | 1.6% |
| `no_reference_boundary` | 2.5% | 3.5% | 0 |
| `unknown_due_to_absence` | 0.8% | 0.7% | 1.2% |
| `cluster_axis` | 0.4% | 1.3% | 0 |

Deepseek uses `unknown_due_to_ambiguity` on 13.1% of rows; gpt-4.1-mini on 0.1%.
Deepseek uses `seizure_free_state` on 19.1% of rows; gpt-4.1-mini on 1.5%. These are
not reflecting true differences in the data — the same 750 rows are being assessed by
both models. The field is coded correctly in the schema but the prompt provides no
guidance on when each value applies, so models interpret it differently.

---

## 7. normalization_issues Density

`normalization_issues` is a free-text `list[str]` on `ClinicalAssessment`. It is populated
on a large fraction of rows and not currently analyzed for accuracy correlation:

| Model | Rows with any normalization_issues | Rate |
| --- | ---: | ---: |
| gpt-4.1-mini | 313 / 749 | 41.8% |
| deepseek-v4-flash | 314 / 750 | 41.9% |
| qwen3.6-35b | 59 / 250 | 23.6% |

The high rate (>40%) for gpt-4.1-mini and deepseek suggests this field is being used
broadly as a general comment field rather than to flag specific normalization failures.
It is not currently used for routing or scoring decisions and so has no measurable accuracy
correlation in the current pipeline.

---

## 8. Summary: What Has Signal, What Doesn't

| Signal | Has accuracy correlation? | Notes |
| --- | --- | --- |
| `confidence` (low/medium/high) | **Only for deepseek** | gpt-4.1-mini and qwen collapse to "high"; 25–30pp gap for deepseek |
| `answer_kind = "unknown"` | **No** — higher accuracy, not lower | Model correctly identifies genuinely unknowable cases |
| `answer_kind = "seizure_free"` | **Yes** — lower accuracy | Consistently the hardest kind, but model doesn't express doubt |
| `uncertainty_flags` (hybrid) | Unmeasured (no per-row scores without deep-replay) | Vocabulary is uncontrolled; cannot aggregate across models |
| `aggregation_policy` (hybrid) | Unmeasured | Coded field, but model-specific interpretation; unreliable cross-model |
| `normalization_issues` (hybrid) | Unmeasured | Density too high (>40%) to be a useful flag; likely used as general notes |
| `route_families` (hybrid only) | Indirect — routed rows withheld from scoring | 15 named families; the most structured uncertainty expression in the codebase |
| Predicted category granularity (`structured_events`) | **Yes** — fine-grained categories (1/yr, 1/6mon) have 37–50% accuracy | Not a model-expressed signal; reflects inherent task difficulty at category boundaries |

---

## 9. Implications for Phase 3

Three concrete fixes before Phase 3's prompt-refinement pass (see also the Phase 3
additions in the three-way comparison plan, Section 5):

**Fix 1 — Ground the `confidence` field operationally.** Define each level in the prompt
in plain clinical language: what *observable feature of this note* makes the answer
high/medium/low confidence? Without this, instruction-following models default to high.
Candidate definitions grounded in the existing `VerificationRouteFamily` taxonomy:
- `"low"`: competing current facts that the rules above did not resolve, or the frequency
  can only be described as a vague range with no window
- `"medium"`: one fact is clearly dominant but ambiguity exists (e.g. conditional trigger,
  vague count with a clear window, or relative-only trend)
- `"high"`: one unambiguous current fact, no competing claims, evidence is a direct quote

**Fix 2 — Replace `uncertainty_flags` (hybrid) with a closed vocabulary.** The current
free-text list produces 50+ synonymous values per model with no cross-model comparability.
The `VerificationRouteFamily` enum (15 named families: `cluster_axis_ambiguity`,
`seizure_free_conflict`, `conditional_only_trigger`, `multiple_current_primary_facts`,
etc.) already names the clinically meaningful uncertainty types. The prompt for the
clinical assessment stage should offer this list and ask the model to select from it
rather than improvise free text.

**Fix 3 — Add usage guidance for `aggregation_policy` to the hybrid prompt.** The 8-value
enum is right in design but models interpret it wildly differently (gpt-4.1-mini uses
`unknown_due_to_ambiguity` 130× less than deepseek). A short decision table in the
prompt (similar in spirit to the `guidance_for_tricky_cases` block in
`llm_only_canonical_pipeline`) would make the field comparable across models.

These three fixes do not require schema changes — only prompt changes — and each is
independently ablatable (change one, re-run, compare).
