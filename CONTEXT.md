# Clinical Extraction

Glossary for the two-task clinical extraction research system. Implementation detail lives elsewhere.

Paper-facing ExECT primary method-comparison boundary:
[decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md).

**0046 evidence backlog** (authorized, not yet done):
Protocol:
[exectv2_primary_method_comparison_surface_protocol_2026-08-01.md](docs/experiments/exectv2/reliability/exectv2_primary_method_comparison_surface_protocol_2026-08-01.md).
Execution order **A → B → C**:
- **A** — Public six-model ExECT `test60` stage panel (`raw_lane_score` vs final). **Complete** — [panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json); Sol raw `0.7771` / final `0.8047`.
- **B** — Four-family rules-only `clinical_headline` on `dev140`. **Complete** — F1 **0.8160**; [artifact](experiments/exectv2_rules_only_four_family_clinical_headline_dev140_20260801.json).
- **C** — Aggregate-only four-family rules-only `clinical_headline` on `test60`. **Complete** — F1 **0.7154**; [artifact](experiments/exectv2_rules_only_four_family_clinical_headline_test60_20260801.json).

## Language

### Methods

**Active method**:
The public identity of a selected research method for a task: `rules`, `llm`, or `llm_with_rules`. Frontend grouping, badges, and selectors use this field only.
_Avoid_: `comparison_mode`; `llm_plus_rules`; `deterministic_only` as a second public vocabulary; `hybrid` or `llm_only` as the active identity

**Architecture stage ID**:
A stable attribution key for one pipeline stage inside a method manifest. For selected methods it uses the active-method token in the namespace (`gan.llm_with_rules.*`, `exect.llm_with_rules.*`, and the matching `rules` / `llm` forms), not a parallel `hybrid` namespace.
_Avoid_: `gan.hybrid.*` or `exect.hybrid.*` as the selected-method stage namespace; treating a stage ID as the public method name

**Selected ExECT hybrid**:
The current one-call, model-led ExECT LLM-with-rules method: the named model proposes Diagnosis, Seizure Frequency, Prescription, and Investigations findings, then family-specific deterministic transforms may change the scored answer under decision 0040 / 0041. Paper primary identity is governed by [decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md).
_Avoid_: v08, historical hybrid, holistic assembly, LLM with rules (unqualified when ExECT is meant)

**Historical ExECT hybrid control**:
The retained `v08` ExECT LLM-with-rules development control. It is reproducible evidence for an earlier ownership pattern, not the paper's primary ExECT hybrid. In the paper it appears only in a secondary results table with an explicit ownership caveat, never as the primary hybrid method row. It is not a supervisor-facing frontend ladder architecture.
_Avoid_: selected hybrid, final architecture, model-led comparison, primary method row; frontend component-ablation control column

**Supervisor-facing method demonstration**:
The frontend surfaces that teach or demonstrate the selected six-path system. They show only selected active methods and their teaching/replay evidence, not historical candidate ladders such as `v08` or `v09` partial-hybrid rows. The ExECT component-ablation ladder is not part of that demonstration until a selected-method ladder exists. The Gan component-ablation mock keeps the three-way comparison columns as selected `rules` / `llm` / `llm_with_rules` evidence (active-method labels), not as unnamed “diagnostic” or “Hybrid” columns.
_Avoid_: presenting closed candidates as the default control; mixing retained historical ablation columns into the primary demonstration; supervisor-facing “Hybrid …” method labels

**LLM with rules**:
A research method class in which a model proposes clinical content and deterministic code may later change clinical meaning. On ExECT, the selected instance is the Selected ExECT hybrid; on Gan, it is the event-ledger plus repair stack.
_Avoid_: using the phrase alone when the task-specific selected instance matters

### Splits

**Gan development split**:
The 750-row Gan split that permits development review and replay. In prose and claims it is `dev750`. Retained filenames and live API machine `split` fields may keep the legacy identifier `validation750`.
_Avoid_: presenting `validation750` as the current prose split name; renaming retained artifact filenames for cosmetics

### Paper roles

**Primary method row**:
The result that stands for a method in the paper's main three-method comparison for a task.
_Avoid_: selected run (when meaning the paper table), headline score (when meaning role rather than number)

**Primary ExECT method-comparison surface**:
Matched four-family `clinical_headline` scoring used to compare ExECT rules-only, LLM-only, and the Selected ExECT hybrid as peers.
_Avoid_: nine-entity published metrics as the three-method peer score; mixing entity counts across method rows

**Primary ExECT hybrid method-row fill**:
The Selected ExECT hybrid result for GPT-5.6 Sol on the primary ExECT method-comparison surface. The six-model panel remains model-comparison evidence; Sol is the paper's method-identity number for ExECT LLM with rules.
_Avoid_: GPT-4.1-mini as the ExECT hybrid method identity; v08; best-of-six without naming Sol

**Primary ExECT LLM-only method-row fill**:
GPT-5.6 Sol's `raw_candidate` / `raw_lane_score` from the same one-call four-family pipeline — the earliest scored model boundary before deterministic clinical changes. On `dev140` this is clinical-headline F1 `0.8097` (reported as `0.81`). On `test60`, the public six-model stage panel records Sol `raw_lane_score` F1 `0.7771` (final hybrid `0.8047`). Owner: [stage panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json). The primary method table still cites Sol only.
_Avoid_: GEPA as the Sol hybrid's LLM-only peer; `source_scored` as the LLM-only method identity; citing the Gan LLM-only `test450` panel as ExECT evidence; citing sealed-only test60 LLM-only numbers in the manuscript; Sol-only holdout stage panel when six-model finals already exist

**Gan six-model LLM-only test450 panel**:
The retained aggregate-only Gan LLM-only holdout panel at `experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json` (`gan2026_llm_only_canonical_pipeline_v0.8`, all six models). Separate from ExECT stage scores.
_Avoid_: ExECT test60 LLM-only; ExECT model-boundary

**Primary ExECT three-method split policy**:
The primary ExECT method table includes both `dev140` and `test60` once every method cell has an aggregate-safe source. Sol LLM-only / hybrid already have sealed stage aggregates on `test60`. Rules-only four-family `clinical_headline` is authorized on `test60` as aggregate-only scoring (no row inspection) and is not yet materialized.
_Avoid_: publishing test60 method cells without an aggregate source; inspecting sealed test60 rows; treating the Gan LLM-only `test450` panel as satisfying an ExECT test cell

**GEPA ExECT LLM-only comparator**:
The retained GEPA-optimized GPT-4.1-mini four-family program (`0.7393` clinical fact F1). Historical / negative architecture evidence, not the primary peer of the Selected ExECT hybrid.
_Avoid_: primary ExECT LLM-only method-row fill; Sol LLM only

**Secondary ExECT published-metric reference**:
The nine-entity paper-derived phrase / CUI / all-features rules-only replay. It answers the published-metric question, not the primary three-method comparison.
_Avoid_: primary method row, three-method peer

**Primary ExECT rules-only method-row fill**:
Four-family Sol-matched `clinical_headline` / `headline_target` applied to rules-only deterministic predictions restricted to Diagnosis, Seizure Frequency, Prescription, and Investigations. The all-nine extractors may still run; non-key entities are excluded from this peer score only. On `dev140` the materialized overall F1 is **0.8160**. On aggregate-only `test60` it is **0.7154**.
_Avoid_: all-nine strict micro F1 as the three-method peer; Diagnosis-only clinical recovery as the four-family peer; published-metric all-features as the three-method peer; `clinical_recovery_scorecard` overall as the Sol peer; four-extractor-only as a different rules-only method

**0046 rules-only scoring rule**:
B/C use restrict-and-rescore through the same assembly `headline_target` surface as Sol, not the older multi-entity clinical-recovery scorecard.
