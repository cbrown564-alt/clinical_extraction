# Hard-slice error modes across the six models

Date: 2026-08-06  
Status: development mechanism answer on retained no-call artifacts  
Paper-library role: cross-model technical record; start with [failures and limits](../paper/failures_and_limits_2026-08-10.md)

Protocol: [hard-slice error-mode protocol](six_model_hard_slice_error_modes_protocol_2026-08-06.md)  
Parent: [category-cut performance](six_model_category_cut_performance_2026-08-06.md)  
Artifact: [`experiments/six_model_hard_slice_error_modes_20260806.json`](../../experiments/six_model_hard_slice_error_modes_20260806.json)

## Plain answer

The floors are not mysterious low scores. They are a small set of repeated
failure shapes:

1. **Gan ordinary rates (`llm`):** models mostly either abstain to `unknown` or
   pick the wrong competing rate / quiet-interval reading. Hybrid rules rescue
   about **60–78%** of those wrongs—so the large llm-only **z** mass is largely
   repairable selection/format failure, not an unrecoverable comprehension wall.
2. **Gan clusters:** at the model boundary, incomplete cluster grammar dominates.
   After the llm-only format adapter, those collapses become `unknown` /
   no-reference. After full hybrid rules, incomplete grammar disappears and the
   residual is still **smooth-rate substitution or unknown**, almost always with
   exact evidence in hand (~98%).
3. **ExECT SeizureFrequency:** letter-exact errors are a mix of **empty-gold
   spurious SF**, missed state inventory, and substituted state sets. Rules cut
   empty-gold over-reads but do not clear the inventory problem. Active-rate is
   the main spurious extra state.

## Scope

| Slice | Surface | Denominator | Wrongness |
| --- | --- | --- | --- |
| Gan `ordinary_point_rate` | `llm` | 312 rows | Purist false |
| Gan `cluster_burden` | `llm` | 64 rows | Purist false |
| Gan `cluster_burden` | `llm_with_rules` | 64 rows | Purist false (v0.5 + floors patch) |
| ExECT SF | `llm` / `llm_with_rules` | 140 letters | SF unit-key multiset imperfect |

No note text. Holdout sealed. Regenerable via
`python scripts/build_six_model_hard_slice_error_modes.py`.

---

## Gan `ordinary_point_rate` (`llm`)

Accuracy band matches the category cut (~0.61–0.71). **73/312** rows are wrong
under all six models.

### Scored-label modes (pooled wrong row×model = 633)

| Mode | Count | Share |
| --- | ---: | ---: |
| `over_abstain_unknown` | 225 | 36% |
| `wrong_point_rate_selection` | 206 | 33% |
| `false_seizure_free` | 99 | 16% |
| other (no-reference, range/multiple, parse) | 103 | 16% |

Abstention + wrong-rate selection + false seizure-free are the story. Pragmatic
near-misses are real but limited (~18–27 wrongs per model).

### Model-boundary diagnostic

Raw model labels show **more** `unknown` (276) and some false cluster shapes
(28) that the llm-only format adapter later reshapes before Purist scoring.
Mode assignment in the tables above follows the **scored** label—the same
boundary the category-cut accuracy uses.

### Rules lift on this floor

Among llm Purist-wrongs, hybrid rescue rates:

| Model | llm acc | Rescue among wrongs |
| --- | ---: | ---: |
| DeepSeek | 0.66 | 0.60 |
| Gemma | 0.61 | 0.78 |
| Qwen | 0.64 | 0.72 |
| Luna | 0.66 | 0.73 |
| mini | 0.69 | 0.73 |
| Sol | 0.71 | 0.71 |

So ordinary-rate **z** without rules is mostly “wrong reading or abstention that
repair often fixes,” not a permanent six-model ceiling on that gold mass.

---

## Gan `cluster_burden`

### `llm` (shared **z**)

Consensus wrong in all six: **22/64**.

| Layer | Dominant modes (pooled wrongs) |
| --- | --- |
| Model boundary | `incomplete_cluster_grammar` 91, `collapse_to_unknown` 44, `dropped_to_smooth_rate` 34, `wrong_cluster_parameters` 32 |
| Scored llm_only | `collapse_to_unknown` 122, `dropped_to_smooth_rate` 34, `collapse_to_no_reference` 31, `wrong_cluster_parameters` 13 |

Models often *mention* clusters without emitting the required
`N cluster per …, M per cluster` grammar. The format adapter then collapses many
of those attempts into sentinels, which is what Purist sees.

### `llm_with_rules` (practical floor)

Consensus wrong in all six drops to **6/64**. Incomplete grammar is gone from
final labels. Remaining pooled wrongs:

| Mode | Count |
| --- | ---: |
| `collapse_to_unknown` | 57 |
| `dropped_to_smooth_rate` | 56 |
| `wrong_cluster_parameters` | 18 |
| other sentinels / false free | 12 |

Exact selected evidence among pooled hybrid wrongs: **140/143 (0.98)**. The
hybrid cluster floor is clinical selection / label construction with the quote
already found—not retrieval.

---

## ExECT SeizureFrequency (both surfaces)

Letter-exact rates (SF unit keys only; not the category-cut family F1):

| Model | llm exact | llm_with_rules exact |
| --- | ---: | ---: |
| DeepSeek | 0.64 | 0.71 |
| Sol / Luna | 0.61 | 0.63 |
| Qwen | 0.45 | 0.53 |
| mini | 0.41 | 0.50 |
| Gemma | 0.36 | 0.43 |

Consensus imperfect letters: **26** (`llm`), **23** (`llm_with_rules`).

### Pooled imperfect modes

| Mode | llm | llm_with_rules |
| --- | ---: | ---: |
| `empty_gold_spurious` | 115 | 85 |
| `substituted_or_mixed` | 104 | 91 |
| `missed_states_only` | 93 | 100 |
| `extra_states_only` | 76 | 66 |
| `missed_all_sf` | 19 | 19 |

Of 41 empty-gold-SF letters, spurious emission ranges from 9 (Sol) to 29 (Qwen)
on `llm`; rules reduce that band (Sol still 9; DeepSeek 15→8; Qwen 29→20) but
leave a stubborn empty-gold tax.

### State tokens among misses / extras (pooled)

| | llm missed | llm extra | hybrid missed | hybrid extra |
| --- | ---: | ---: | ---: | ---: |
| `unknown` | 97 | 76 | 97 | 68 |
| `active-rate` | 85 | **201** | 85 | **141** |
| `seizure-free` | 82 | 75 | 75 | 68 |

The distinctive precision pressure is **extra active-rate**. Rules shrink it;
they do not remove missed `unknown` / inventory under-fills.

---

## What this changes about “models perform similarly”

| Floor | Similarity means |
| --- | --- |
| Gan ordinary `llm` | Shared abstention + wrong-rate / false-free patterns; rules later erase most of it |
| Gan cluster | Shared failure to emit durable cluster grammar; hybrid residual is quote-backed smooth-rate or unknown |
| ExECT SF | Shared inventory / empty-gold / active-rate over-read problems on both surfaces |

This is compatible with
[why the error floor persists](why_the_error_floor_persists_2026-07-31.md):
evidence is usually present; the forced clinical choice and required label shape
are what break.

## Claim boundary

- Development hard-slice modes from retained artifacts; mode labels are analyst
  heuristics, not new gold.
- Gan `llm` modes use scored `decision_record.final_label`; model-boundary modes
  are diagnostic.
- ExECT letter-exactness is a mechanism lens; category-cut family F1 remains the
  competence metric.
- Not holdout competence; not Decision 0046 rewrite; DeepSeek Gan `llm` still
  pre-0731.

## Supersession

For full-bucket / full-family catalogs with summary + examples in one place,
read:

- [Gan category error catalog + ablation](../gan2026/category_error_catalog_2026-08-06.md)
- [ExECT family error catalog + ablation](../exectv2/family_error_catalog_2026-08-06.md)

This hard-slice note remains a short floor-focused precursor.
