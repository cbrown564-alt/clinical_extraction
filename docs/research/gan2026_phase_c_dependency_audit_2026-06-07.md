# Gan 2026 Phase C — Dependency Audit

Date: 2026-06-07

Author: Claude

Status: audit output — companion to
`gan2026_phase_a_file_catalog_2026-06-07.csv` and
`gan2026_canonical_runner_selection_2026-06-07.md`. Produces the
removal-readiness verdicts called for by
[[gan2026_repo_consolidation_and_cleanup_plan]] Section 5 (Phase C).
**Audit-only — no files modified, removed, or unwired.** Per the plan's
guardrails, this is a reviewable proposal; nothing is removed until it is
reviewed and Phase D (lineage documentation) completes.

---

## 1. Summary — Verdict Counts

41 files were directly audited (the 28 catalogued `superseded-candidate`
rows, plus the specific `needs-decision` files named in catalog summary
Section 5 items 1–7, including the 13 `hybrid_parallel_state_candidate_reasoner`
-referencing analyzers and the 2 `components/*` exception files). The 45
remaining `components/*` files are covered by one batch verdict (Section 4).

| Verdict | Count | Notes |
| --- | --- | --- |
| `safe-to-remove` | 0 | nothing is dependency-free *and* doc-clean *and* test-free in one step — everything needs at least one pre-step |
| `needs-test-removal-first` | 28 | every superseded-candidate `runner`/`component`/`report` has a mirrored test |
| `needs-doc-archival-first` | 31 | the 4 named hybrid lineages + most of their analyzer/component coupling are described as current/comparison-relevant in 2026-06-05 to 2026-06-07 docs and `PROJECT_STATUS.md` |
| `needs-registry-update-first` | 16 | CLI (`llm_pipeline_cli.py`) and/or observatory (`FAMILY_SHORT_LABELS`/frontend `traceAdapter`) entries must be unwired |
| `blocked — has live dependents` | **2** | `components/source_trace.py`, `components/suspicious_state_policy.py` — imported by **`suspicious_selected_state_routing.py`**, a `shared-keep` canonical-line analyzer |
| `needs-porting-then-removal` (compound) | 1 | `experiments/synthetic_hard_case_component_stress.py` — see Section 3.6 |

(Counts overlap — most files carry 2–3 verdicts simultaneously; see
per-lineage tables for the full combination per file.)

**Headline finding**: of the 7 open questions from the catalog summary
Section 5, **6 resolve cleanly toward removal** (with prep steps), and
**1 produces a real `blocked` finding** that the cleanup plan explicitly
calls a signal to revisit canonical assumptions (Section 5.1 below).
Critically, the `blocked` finding is **not** about the Phase B canonical
*runner* choice itself — `suspicious_selected_state_routing.py` is a
`hybrid-reset-current` analyzer, consistent with the canonical hybrid
selection — but it does mean two `components/*` modules currently
classified by lineage as "staged-v0 era" are actually load-bearing shared
infrastructure mis-filed by directory location.

---

## 2. Per-Lineage Audit

### 2.1 `staged_hybrid_assembly` (v0) — 2 files + exclusive analyzer coupling

| File | Import graph | CLI | Tests | Observatory/registry | Docs | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `hybrid/staged_hybrid_assembly.py` | imported only by `artifact_analysis/change_only_det_state_family_experiment.py` and `selected_state_union_replay.py` (both themselves `needs-decision`/v0-coupled, not kept) | not registered | `tests/test_gan2026_staged_hybrid_assembly.py` | no `pipeline_family` rows in `experiments/registry.jsonl`; not in `FAMILY_SHORT_LABELS` | mentioned only in the catalog/cleanup-plan docs (no 06-05-era "current" framing found) | `needs-test-removal-first` |

**Key finding**: `staged_hybrid_assembly` is the cleanest of the four named
lineages — its only src-level dependents (`change_only_det_state_family_experiment`,
`selected_state_union_replay`) are themselves `needs-decision` analyzers whose
catalog notes already flag them as "superseded-lineage-coupled" (v0). Neither
is wired into CLI/observatory under any name. **This lineage is the
lowest-friction removal candidate** — its only blocker is its own test file
plus folding its contribution (the original "staged hybrid assembly rows"
pattern, h5/h9/h10 markers per the cleanup plan's example) into the Phase D
lineage doc.

### 2.2 `staged_assembly_v1` — 1 file

| File | Import graph | CLI | Tests | Observatory/registry | Docs | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `hybrid/staged_assembly_v1.py` | **zero** Python dependents anywhere in `src/` (grep returned no hits outside its own file/test) | not registered | `tests/test_gan2026_staged_assembly_v1.py` | no `pipeline_family` rows; not in `FAMILY_SHORT_LABELS` | **9** docs reference it, several from 2026-06-05 with active framing — `gan2026_hybrid_multi_component_staged_assembly_v1_frozen_holdout_protocol_2026-06-05.md`, `..._frozen_protocol_review_2026-06-05.md`, `..._gpt41mini_frozen_holdout_protocol_2026-06-05.md`, `..._qwen36_35b_ollama_frozen_holdout_protocol_2026-06-05.md`, `gan2026_validation_test_gap_staged_action_plan_2026-06-05.md`, `gan2026_final_assembly_findings_and_holdout_plan_2026-06-05.md`, `gan2026_component_architecture_reset_completed_tasks_2026-06-05.md`; `PROJECT_STATUS.md` line 691–693 references its frozen aggregate-only holdout protocol as still-relevant context | `needs-test-removal-first`, `needs-doc-archival-first` |

**Key finding**: `staged_assembly_v1` has **zero live code dependents** — the
cleanest import graph of the four — but is the **most heavily documented in
currency-framed language**. It cannot be removed until the substantial 2026-06-05
"frozen holdout protocol" documentation cluster is compressed into the Phase D
lineage doc (or explicitly marked historical). Code-wise it is ready the
moment its test is retired; doc-wise it needs the most Phase D prep of the
four lineages.

### 2.3 `hybrid_parallel_state_candidate_reasoner` — 1 file + 13 analyzer string-couplings

| File | Import graph | CLI | Tests | Observatory/registry | Docs | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `hybrid/hybrid_parallel_state_candidate_reasoner.py` | no Python module imports it; 13 `artifact_analysis/*` files reference it only via **string literals** (experiment-artifact filename prefixes / display labels) — see Section 3 for the full breakdown | **registered** at `cli/llm_pipeline_cli.py:243` (`GanLlmPipelineCliSpec` entry, full read/write/summarize wiring) | `tests/test_gan2026_hybrid_parallel_state_candidate_reasoner.py` | **registered** in `observatory/api.py` `FAMILY_SHORT_LABELS["hybrid_parallel_state_candidate_reasoner"] = "Parallel Hybrid"`; **referenced in the frontend** `frontend/lib/traceAdapter/index.ts:64`, `frontend/lib/types.ts:746`, and `frontend/lib/traceAdapter/__tests__/traceAdapter.test.ts` (lines 377/461/490); **but has zero `pipeline_family` rows in `experiments/registry.jsonl`** — the label/adapter entries are orphaned (no live registry data backs them) | **18** docs reference it; `PROJECT_STATUS.md` explicitly frames its validation750 run as an active **"comparison baseline"** (lines 167–168, 345–348, 367–369, 500–502, 513–515) | `needs-test-removal-first`, `needs-registry-update-first`, `needs-doc-archival-first` |

**Key finding — the registry/frontend wiring is dead-but-present**: the CLI
spec is fully live (it can still be invoked), but the observatory label and
the frontend `traceAdapter` switch-case reference a `pipeline_family` value
that **no longer appears in `experiments/registry.jsonl`** — i.e., the
adapter code path and label are vestigial (`_build_pipeline_families` only
ever surfaces families present in registry data, so this label is currently
unreachable in the UI). This is a `needs-registry-update-first` cleanup of
**dead** wiring, not a live coupling — but it must still be removed
explicitly (CLI spec, `FAMILY_SHORT_LABELS` entry, frontend `traceAdapter`
switch arm and its test cases) as part of this lineage's batch, because
`PROJECT_STATUS.md` still actively frames its run history as a comparison
baseline that the *new* reset-pipeline runs are being measured against.

### 2.4 `hybrid_rules_candidates_llm_adjudicator` + `hybrid_adjudicator_parser` + `reports/hybrid_adjudicator_report.py`

| File | Import graph | CLI | Tests | Observatory/registry | Docs | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `hybrid/hybrid_rules_candidates_llm_adjudicator.py` | imported by `artifact_analysis/architecture_component_ablation.py` (needs-decision/adjudicator-coupled), `experiments/saturated_surface_evaluation.py` (label-only, see 2.5), `experiments/synthetic_hard_case_component_stress.py` (real import — see 2.6), and its own `hybrid_adjudicator_parser` + `reports/hybrid_adjudicator_report.py` support modules | **registered** at `cli/llm_pipeline_cli.py:116` (full spec) | `tests/test_gan2026_hybrid_rules_candidates_llm_adjudicator.py` | **registered** in `FAMILY_SHORT_LABELS["hybrid_rules_candidates_llm_adjudicator"] = "Hybrid Adjudicator"`; **8 live `pipeline_family` rows** in `experiments/registry.jsonl` (this one has real registry data, unlike parallel-state) | 10 docs; `gan2026_extracted_candidate_schema_mapping_smoke_2026-06-05.md` frames it in active terms | `needs-test-removal-first`, `needs-registry-update-first`, `needs-doc-archival-first` |
| `hybrid/hybrid_adjudicator_parser.py` | imported **only** by `hybrid_rules_candidates_llm_adjudicator.py` — confirmed exclusive support module | not registered independently | covered transitively via the parent's test | n/a | n/a | `needs-test-removal-first` (same batch as parent) |
| `reports/hybrid_adjudicator_report.py` | imported **only** by `hybrid_rules_candidates_llm_adjudicator.py` — confirmed exclusive report writer (per catalog Section 5 item 6, already resolved) | n/a | covered transitively | n/a | n/a | `needs-test-removal-first` (same batch as parent) |

**Key finding**: this is the lineage with the most *real* registry data (8
live `pipeline_family` rows — unlike parallel-state's zero), so its
`needs-registry-update-first` step is a genuine unwiring of live observatory
display data, not dead-code cleanup. It is also the lineage with the most
exclusive-support-module structure already cleanly resolved (parser + report
writer both confirmed single-purpose). `architecture_component_ablation.py`
(the `artifact_analysis/` one, distinct from its `experiments/` compatibility
wrapper) imports the adjudicator directly and is itself adjudicator-coupled —
it should fold into the same removal batch (see Section 3.7).

### 2.5 `experiments/saturated_surface_evaluation.py` (catalog summary item 3a)

| Check | Finding |
| --- | --- |
| Import graph | **No Python import** of `hybrid_rules_candidates_llm_adjudicator` — only references it via **string artifact-label literals** (`"gan2026_hybrid_rules_candidates_llm_adjudicator_validation250_..."`, `"candidate": "hybrid_rules_candidates_llm_adjudicator_v0.2"`) used to load/parse saved run artifacts |
| Dependents | **Zero** — only its own mirrored test (`tests/test_gan2026_saturated_surface_evaluation.py`) references it |
| CLI/Observatory | not registered |
| Docs | no currency-framed mentions found beyond the catalog/cleanup-plan |

**Verdict: `safe-to-remove` modulo its test** → `needs-test-removal-first`
only. **Resolves catalog summary open question 3**: this file is exclusive
to the superseded adjudicator lineage (it evaluates *saved artifacts* from
that lineage's runs, not generic infrastructure) and has no independent
canonical-line value — it goes in the same batch as
`hybrid_rules_candidates_llm_adjudicator`.

### 2.6 `experiments/synthetic_hard_case_component_stress.py` (catalog summary item 3b) — the compound case

| Check | Finding |
| --- | --- |
| Import graph (outbound) | **Real Python import** at module level: `from ...hybrid import hybrid_rules_candidates_llm_adjudicator as hybrid_adjudicator` (line 23), plus `architecture_component_ablation as component_ablation` (line 13). Its `main()` (lines 221+) directly calls `hybrid_adjudicator.run_hybrid_rules_candidates_llm_adjudicator_split`, `.write_hybrid_rules_candidates_llm_adjudicator_jsonl`, `.write_hybrid_rules_candidates_llm_adjudicator_report` |
| Import graph (inbound) | **Imported by 3 `shared-keep` modules**: `artifact_analysis/boundary_state_graph_replay.py`, `experiments/boundary_state_graph_builder.py`, `experiments/state_graph_diagnostics.py` — all aliased as `hard_cases` |
| What the dependents actually use | **Only** the pure data-loading helpers defined at lines 70–103: `load_synthetic_hard_cases()`, `synthetic_records_from_cases()`, plus the constants `SYNTHETIC_SPLIT_NAME`, `SYNTHETIC_SPLIT_MANIFEST`, `DEFAULT_HARD_CASES_JSONL_PATH`. **None** of the 3 dependents call into `hybrid_adjudicator` or `component_ablation` — those are only exercised by `main()` (the adjudicator-pipeline CLI entry point, lines 221–310) |
| CLI/Observatory | not registered |
| Tests | `tests/test_gan2026_synthetic_hard_case_component_stress.py` — its two tests (`test_load_synthetic_hard_cases_as_scored_records`, `test_component_stress_result_summarizes_hybrid_conditions`) cover both the loader helpers and the adjudicator-coupled summarization path |

**Verdict: `needs-porting-then-removal`** (compound, not a clean
`safe-to-remove`/`blocked` binary). **Resolves catalog summary open question
3b**: this file is *not* cleanly exclusive to the superseded lineage — it has
a real, separable split:

- **Adjudicator-coupled half** (`main`, `build_component_stress_result`,
  `write_component_stress_report`, the `hybrid_adjudicator`/
  `component_ablation` calls) — exclusive to the superseded lineage,
  `safe-to-remove` in the same batch as the adjudicator.
- **Synthetic-hard-case loader half** (`load_synthetic_hard_cases`,
  `synthetic_records_from_cases`, `attach_hard_case_metadata`, the
  `SYNTHETIC_*` constants/paths) — **load-bearing for 3 `shared-keep`
  modules** that need it purely as a data-fixture loader, with no
  dependency on the adjudicator pipeline.

**Recommended pre-step**: port the loader half (≈35 lines, lines 70–133)
into a small shared module (e.g. `experiments/synthetic_hard_cases.py` or
fold into `experiments/artifact_io.py`), retarget the 3 dependents' `hard_cases.`
references at the new home, then the adjudicator-coupled remainder of this
file becomes `safe-to-remove` alongside the rest of the adjudicator lineage.
This is **not** a `blocked` finding against the Phase B canonical choice
(the dependents don't need the adjudicator pipeline at all — they need a
fixture loader that happens to currently live in a file that also contains
adjudicator code) — it is a **mechanical separation** the plan's "port the
dependency into the canonical line first" escape hatch (Section 5,
`blocked` verdict definition) anticipates.

### 2.7 `llm_only_*` non-canonical modules (8 src + 8 mirrored tests + 2 exclusive support)

| File | Import graph | CLI | Tests | Observatory/registry | Docs | Verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `llm_only_claim_table_selector.py` | imported by `claim_table_parser.py`, `reports/claim_table_report.py` (both exclusive support, confirmed single-purpose), `artifact_analysis/claim_table_component_ablation.py` (needs-decision, built for it), `artifact_analysis/evidence_selection_matrix.py` (string-label only — see Section 3) | **registered** (`cli/llm_pipeline_cli.py:106/198`) | `tests/test_gan2026_llm_only_claim_table_selector.py` | `FAMILY_SHORT_LABELS["llm_only_claim_table_selector"] = "Claim Table"`; **4 live `pipeline_family` rows** in registry | several docs | `needs-test-removal-first`, `needs-registry-update-first`, `needs-doc-archival-first` |
| `llm/claim_table_parser.py` | imported **only** by `llm_only_claim_table_selector.py` — confirmed exclusive | n/a | covered transitively | n/a | n/a | `needs-test-removal-first` (same batch) |
| `reports/claim_table_report.py` | imported **only** by `llm_only_claim_table_selector.py` — confirmed exclusive (catalog Section 5 item 6, resolved) | n/a | covered transitively | n/a | n/a | `needs-test-removal-first` (same batch) |
| `llm_only_minimal_evidence_selector.py` | zero non-test/non-CLI/non-observatory dependents | **registered** (`cli/llm_pipeline_cli.py:199`) | `tests/test_gan2026_llm_only_minimal_evidence_selector.py` | `FAMILY_SHORT_LABELS["llm_only_minimal_evidence_selector"] = "Minimal Evidence"`; **live registry rows** present (e.g., overnight 2026-06-01 validation250 run) | mentioned in cleanup/comparison plan docs | `needs-test-removal-first`, `needs-registry-update-first`, `needs-doc-archival-first` |
| `llm_only_rich_selected_state_reasoner.py` | imported only by `artifact_analysis/selected_state_union_replay.py` (`needs-decision`, v0-coupled) | **not registered** | `tests/test_gan2026_llm_only_rich_selected_state_reasoner.py` | not in `FAMILY_SHORT_LABELS`; 0 rows | — | `needs-test-removal-first` |
| `llm_only_simplified_selected_state_reasoner.py` | zero non-test/non-CLI dependents | **registered** (`cli/llm_pipeline_cli.py:209`) | `tests/test_gan2026_llm_only_simplified_selected_state_reasoner.py` | not in labels; 0 rows | — | `needs-test-removal-first`, `needs-registry-update-first` |
| `llm_only_sparse_operands_selected_state_reasoner.py` | zero non-test/non-CLI dependents | **registered** (`cli/llm_pipeline_cli.py:225`) | `tests/test_gan2026_llm_only_sparse_operands_selected_state_reasoner.py` | not in labels; 0 rows | — | `needs-test-removal-first`, `needs-registry-update-first` |
| `llm_only_typed_adapter_reasoner.py` | zero non-test/non-CLI dependents | **registered** (`cli/llm_pipeline_cli.py:286`) | `tests/test_gan2026_llm_only_typed_adapter_reasoner.py` | `FAMILY_SHORT_LABELS["llm_only_typed_adapter_reasoner"] = "Typed Adapter"`; 2 registry rows | — | `needs-test-removal-first`, `needs-registry-update-first` |
| `llm_only_typed_operations_reasoner.py` | zero non-test/non-CLI dependents | **registered** (`cli/llm_pipeline_cli.py:298`) | `tests/test_gan2026_llm_only_typed_operations_reasoner.py` | `FAMILY_SHORT_LABELS["llm_only_typed_operations_reasoner"] = "Typed Operations"`; 2 registry rows | — | `needs-test-removal-first`, `needs-registry-update-first` |
| `llm_only_structured_events_repair_ablation.py` | see Section 2.8 (item 7) | not registered | `tests/test_gan2026_llm_only_structured_events_repair_ambiguity.py`* | not in labels; 0 rows | mentioned in 2026-06-01 thermonuclear reviews + the canonical-runner-selection doc, no active-use framing | `needs-test-removal-first` |

\* file is `tests/test_gan2026_llm_only_structured_events_repair_ablation.py`.

**Key finding**: 6 of 8 `llm_only_*` candidates are CLI-registered (the
catalog summary's claim that the CLI is "shared-keep... but every
superseded-candidate's removal requires unwiring" is borne out exactly here —
this is the largest concentration of `needs-registry-update-first` verdicts
in the whole audit). None of the 8 has a `shared-keep` Python dependent —
their analyzer couplings (`claim_table_component_ablation`,
`selected_state_union_replay`) are themselves `needs-decision`/lineage-coupled,
not canonical. (Note: `direct_labeler_unrecalled_failure_slice_experiment`
and `fewshot_train_exemplar_candidate_experiment` were built around
`llm_only_direct_labeler`, which is now canonical, so they are retained for
the canonical line rather than being treated as superseded-candidates.)

### 2.8 `llm_only_structured_events_repair_ablation.py` — re-check (catalog summary item 7)

| Check | Finding |
| --- | --- |
| Forward import | imports `llm.llm_only_structured_events` (the **canonical** module) — a one-directional "ablates the canonical" coupling |
| Reverse import | the canonical `llm_only_structured_events.py` does **not** import the ablation module — confirmed no back-reference |
| Run history | **zero** `experiments/gan2026_llm_only_structured_events_repair_ablation_*` artifacts found (no mature run history, unlike its sibling `llm_only_structured_events` which has multiple validation250 runs) |
| CLI/Observatory | not registered anywhere |
| Docs | only mentioned in the 2026-06-01 thermonuclear-review docs (structural inventory, not active-use framing) and the canonical-selection/catalog docs produced *this week* as part of this very planning effort |

**Verdict: `needs-test-removal-first`**, confirming the selection decision's
own framing — **it is not the active ablation mechanism** (no run history,
no wiring, no current-use docs). Its methodology (the repair-family ablation
approach) belongs in the Phase D lineage doc; the file joins the same removal
batch as the other 8 `llm_only_*` candidates rather than surviving as
companion infrastructure for the canonical module.

---

## 3. The 13 `hybrid_parallel_state_candidate_reasoner`-Referencing Analyzers (catalog summary item 4)

This is the audit's most consequential check — the plan explicitly frames
"imports the runner's *code*" vs. "references its *output artifacts/labels*"
as the line between `blocked` and `needs-registry-update-first`.

**Finding: all 13 are loose string-literal couplings — zero Python imports.**

```
grep -n "^from\|^import" <each-of-13-files> | grep -i "hybrid\|parallel_state"
→ no matches in any of the 13 files
```

Every reference is one of:
- an **experiment-artifact filename prefix** string used to glob/locate saved
  `.jsonl`/`.json` run artifacts (e.g.
  `"gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"`),
  or
- a **prose/display label** (e.g. `hidden_family_atlas.py` lines 354/413:
  `"candidate_context": "hybrid_parallel_state_candidate_reasoner deterministic safety floor"`,
  `"- Comparator: current `hybrid_parallel_state_candidate_reasoner`..."`).

| File | Coupling type | CLI/Observatory wiring (own name) | Mirrored test |
| --- | --- | --- | --- |
| `candidate_discovery_matrix.py` | artifact-prefix string | none | `test_gan2026_candidate_discovery_matrix.py` |
| `change_only_det_state_family_experiment.py` | artifact-prefix string | none | **missing** — no `test_gan2026_change_only_det_state_family_experiment.py` found |
| `change_only_llm_selector_family_experiment.py` | artifact-prefix string | none | **missing** |
| `combined_change_only_switch_layer_experiment.py` | artifact-prefix string | none | **missing** |
| `evidence_selection_matrix.py` | artifact-prefix string | none | `test_gan2026_evidence_selection_matrix.py` |
| `h10_raw_identity_sidecar.py` | artifact-prefix string (×2) | none | `test_gan2026_h10_raw_identity_sidecar.py` |
| `h10_runtime_variance_audit.py` | artifact-prefix string (×2) | none | `test_gan2026_h10_runtime_variance_audit.py` |
| `hidden_family_atlas.py` | prose/display-label string (×2) | none | `test_gan2026_hidden_family_atlas.py` |
| `rq10_gold_scorer_ambiguity_audit.py` | artifact-prefix string | none | **missing** |
| `rq5_rendering_matrix.py` | artifact-prefix string | none | `test_gan2026_rq5_rendering_matrix.py` |
| `rq9_selective_action_router.py` | artifact-prefix string | none | `test_gan2026_rq9_selective_action_router.py` |
| `selective_safety_floor_gate_replay.py` | artifact-path string (full relative path) | none | `test_gan2026_selective_safety_floor_gate_replay.py` |
| `structured_projection_port_frozen_test_audit.py` | artifact-prefix string | none | `test_gan2026_structured_projection_port_frozen_test_audit.py` |

**This contradicts the catalog summary's framing** that "several are also
wired into `cli/llm_pipeline_cli.py` and/or `observatory/api.py`'s
`_PIPELINE_FAMILIES`" — a targeted re-check (grepping both the filenames
*and* every top-level `build_*`/`run_*` function name from each of the 13
files against `cli/llm_pipeline_cli.py` and `observatory/api.py`) found
**zero matches in either registry**. The CLI/observatory wiring that *does*
reference `hybrid_parallel_state_candidate_reasoner` (Section 2.3's
`FAMILY_SHORT_LABELS` entry, the CLI spec, and the frontend `traceAdapter`)
is wiring for the **runner itself**, not for any of these 13 analyzers.

**Resolution of catalog summary item 4**: this is **not** the
"blocked — has live dependents" scenario. It is a clean
`needs-registry-update-first`-adjacent situation, but the registry update
needed is for the *runner* (Section 2.3), not these analyzers. The analyzers
themselves are `needs-doc-archival-first` (their string literals point at
saved artifacts whose provenance/lineage should be summarized in the Phase D
doc) plus `needs-test-removal-first` for the 9 with mirrored tests. The 4
analyzers without dedicated test files
(`change_only_det_state_family_experiment`,
`change_only_llm_selector_family_experiment`,
`combined_change_only_switch_layer_experiment`,
`rq10_gold_scorer_ambiguity_audit`) carry **no** test-removal step — but that
absence is itself worth a note (possibly tested transitively via sibling
"family experiment" tests, or simply under-tested; worth a quick check before
removal so no coverage is silently lost, per the plan's Open Question 2).

**Verdict for all 13**: `needs-doc-archival-first` (+ `needs-test-removal-first`
for the 9 with mirrored tests). **None are `blocked`.** They can be
retargeted (re-pointed at canonical-runner artifact paths) *or* retired
alongside the parallel-state lineage — retiring alongside it is recommended
since their string literals are bespoke to that lineage's specific run
history (`validation750_gpt41mini_v0_*`, `test450_gpt41mini_v0_*`) and
retargeting would require fabricating equivalent provenance for the
canonical reset pipeline, which is better done as fresh analysis after
cleanup (per the plan's "select → clean → iterate" sequencing) than as a
mechanical find-replace now.

---

## 4. The `components/*` Group (47 files, catalog summary item 1)

**Confirmed**: the catalog's inferred lineage-attribution pattern holds.
Grepping every one of the 47 non-`__init__` files for cross-module imports
(`from ...components.<name> import` / `components import <name>`) outside
`components/` itself returns hits for **exactly two** files:

```
source_trace            <- artifact_analysis/selected_state_union_replay.py
                        <- artifact_analysis/suspicious_selected_state_routing.py
suspicious_state_policy <- artifact_analysis/suspicious_selected_state_routing.py
```

No other exceptions exist — every other components file (45 of 47, plus
`__init__.py` which is `shared-keep` infrastructure) is an island: imported
by nothing outside `components/`, consistent with the catalog's read that
they are "standalone validation/research scripts from the staged-assembly
eras." The `structured_*`/`boundary_*` naming families map to
`hybrid-staged-v1`; the `staged_decision_policy`/`trigger_*`/`selective_*`/
`change_only_*` families map to `hybrid-staged-v0`, exactly as the catalog
inferred from docstrings.

(Note: `validation_surface_inventory.py` and `staged_decision_policy.py`
contain string-literal mentions of `hybrid_parallel_state_candidate_reasoner`
and `suspicious_state_policy`/`source_trace`-shaped identifiers respectively —
all confirmed to be local function names, label strings, or docstring prose,
*not* cross-module imports, on direct inspection.)

### Batch verdict: **45 of 47 `components/*` files → `needs-test-removal-first` + `needs-doc-archival-first`**

These 45 are exclusive to the two staged-assembly eras (v0/v1 per the
filename-prefix split above), have mirrored tests
(`tests/test_gan2026_component_*.py`), and their lineage is now *confirmed*
(not just inferred) exclusive — they can be reclassified from
`needs-decision` to `superseded-candidate` and folded into the
`staged_hybrid_assembly` (v0-named files) / `staged_assembly_v1` (v1-named
files / `boundary_*`/`structured_*`) removal batches respectively.

### Exceptions — individual call-outs

#### `components/source_trace.py` — **`blocked — has live dependents`**

Imported directly by `artifact_analysis/suspicious_selected_state_routing.py`
(line 19), which is catalogued **`shared-keep`** /
**`hybrid-reset-current`** — i.e., a canonical-line analyzer in active use,
not a superseded one. Also imported by `selected_state_union_replay.py`
(`needs-decision`/v0-coupled — not itself a blocker).

#### `components/suspicious_state_policy.py` — **`blocked — has live dependents`**

Imported directly by `artifact_analysis/suspicious_selected_state_routing.py`
(line 22) — same `shared-keep` dependent as above, and **no other**
dependents.

**This is the audit's most important finding** (Section 5.1 expands on it):
two files whose *directory location and lineage tag* (`components/`,
`hybrid-staged-v0`) suggest they belong to a superseded era are in fact
imported, by name, into a live canonical-line (`hybrid-reset-current`)
analyzer that is itself marked `shared-keep`. The plan's guardrail says this
"means either the canonical choice... needs revisiting, or the dependency
needs to be ported into the canonical line first." Here it is unambiguously
the latter: `suspicious_selected_state_routing.py` is correctly classified as
`shared-keep` (it is wired into the live verification/routing cluster, part
of the canonical reset-pipeline analysis surface) — it is `source_trace.py`
and `suspicious_state_policy.py` that are **mis-classified by lineage tag**.
They should be reclassified `shared-infrastructure`/`shared-keep` (or moved
out of `components/` into a shared location reflecting their actual role),
**not** removed with the rest of `components/*`.

---

## 5. Findings Requiring Attention Before Phase D/E

### 5.1 The two `blocked` verdicts — `components/source_trace.py` and `components/suspicious_state_policy.py`

**This does not require revisiting the Phase B canonical *runner* choice**
(the dependent, `suspicious_selected_state_routing.py`, is itself
`hybrid-reset-current`/canonical-aligned — there is no secret dependency on a
*retired architecture's runner*). What it does require: **recognizing that
lineage-tag inference by directory/filename is not 100% reliable**, and that
these two files' `hybrid-staged-v0` tag in the Phase A catalog is wrong (or
at minimum incomplete — they may have originated in the v0 staged-assembly
work but have since been adopted as shared analysis primitives).

**Recommended resolution before Phase E removes the rest of `components/*`**:
reclassify these two files' `status` from `needs-decision` to `shared-keep`
(lineage `shared-infrastructure`) in the catalog, and — ideally as part of
the Phase F DRY-ification — relocate them out of `components/` (a directory
that will otherwise be entirely removed) into a shared home such as
`artifact_analysis/` alongside their sole consumer, or a new
`shared/` analysis-primitives module. Until relocated, **do not** include
them in the `components/*` removal batch.

### 5.2 The `synthetic_hard_case_component_stress.py` compound case (Section 2.6)

Not `blocked` in the strict sense — its 3 dependents need only its loader
helpers, which are mechanically separable from its adjudicator-coupled
`main()`. But it **must not** be removed as-is without first porting
`load_synthetic_hard_cases`/`synthetic_records_from_cases`/`SYNTHETIC_*`
constants (≈35 lines) to a shared home and retargeting
`boundary_state_graph_replay.py`, `boundary_state_graph_builder.py`, and
`state_graph_diagnostics.py`. Treat this as a **mandatory pre-step**, sequenced
*before* the `hybrid_rules_candidates_llm_adjudicator` removal batch (since
this file's removal is otherwise gated on that lineage's batch).

### 5.3 Vestigial observatory/frontend wiring for `hybrid_parallel_state_candidate_reasoner`

The `FAMILY_SHORT_LABELS` entry, CLI spec, and — notably — the **frontend**
`traceAdapter` switch-case and its dedicated test assertions
(`frontend/lib/traceAdapter/__tests__/traceAdapter.test.ts` lines 377/461/490)
all reference a `pipeline_family` value with **zero backing rows** in
`experiments/registry.jsonl`. This is dead UI-adapter code wired to a label
no run can currently produce. It still needs explicit unwiring (frontend
tests reference it by name and would need updating/removal too — this spans
the Python/TypeScript boundary, which is unusual for this audit and worth
flagging to whoever executes the removal batch, since it requires a
frontend-test-aware reviewer, not just a Python one).

### 5.4 Recommended removal-batch ordering

From least to most friction:

1. **`staged_hybrid_assembly` (v0)** — zero CLI/observatory wiring, only
   `needs-decision` (non-kept) analyzer dependents, modest doc footprint.
   Bundle with: its ~half of the 45 confirmed-exclusive `components/*` files
   (the `staged_decision_policy`/`trigger_*`/`selective_*`/`change_only_*`/
   `boundary_state_graph`-adjacent v0 set), `change_only_det_state_family_experiment`,
   `selected_state_union_replay`. **Lowest friction — go first.**

2. **`hybrid_rules_candidates_llm_adjudicator` + `hybrid_adjudicator_parser`
   + `reports/hybrid_adjudicator_report.py` + `experiments/saturated_surface_evaluation.py`
   + `architecture_component_ablation.py` (artifact_analysis variant)** —
   confirmed-exclusive support modules, but has **real** CLI + 8 live registry
   rows + `FAMILY_SHORT_LABELS` entry to unwire (genuine, not dead, wiring).
   **Pre-step required**: port `synthetic_hard_case_component_stress.py`'s
   loader half (Section 5.2) before this batch, since that file is otherwise
   coupled to this lineage's removal.

3. **The 8 `llm_only_*` modules + `claim_table_parser` + `reports/claim_table_report.py`
   + `llm_only_structured_events_repair_ablation`** — heaviest CLI-registry
   footprint (6 of 8 are CLI-registered; 3 carry `FAMILY_SHORT_LABELS`
   entries and live registry rows for `claim_table_selector`/`typed_adapter`/
   `typed_operations`). Bundle with `claim_table_component_ablation`.

4. **`staged_assembly_v1` + the v1-named `components/*` (`structured_*`,
   `boundary_*`)** — cleanest *code* dependency graph (zero Python
   dependents on the runner itself) but the **heaviest current-framed
   documentation** (9 docs, several from 2026-06-05 describing active
   "frozen holdout protocol" work, plus `PROJECT_STATUS.md`). **Needs the
   most Phase D prep** — do not start this batch until the lineage doc's
   v1 section is drafted and reviewed, even though the code removal itself
   would be mechanically the simplest of the four.

5. **`hybrid_parallel_state_candidate_reasoner` + the 13 string-coupled
   analyzers + `validation_surface_inventory.py` + the remaining
   `components/*` exceptions** — go **last**: it has the widest blast radius
   (CLI + observatory + frontend + 18 docs + `PROJECT_STATUS.md`'s active
   "comparison baseline" framing + 13 analyzer references whose string
   literals need archival decisions). The frontend `traceAdapter` coupling
   (Section 5.3) means this batch alone needs a reviewer who can verify
   TypeScript test changes, not just Python — budget extra review time.

Across all batches: relocate (don't remove) `components/source_trace.py`
and `components/suspicious_state_policy.py` *before* batch 5 reaches the
`components/*` cleanup, so the `suspicious_selected_state_routing.py`
import never breaks.

---

## 6. Resolution Summary — Catalog Summary Section 5 Open Questions

| # | Question | Resolution |
| --- | --- | --- |
| 1 | Are the 47 `components/*` files exclusive to staged-assembly eras? | **Yes for 45**; **`source_trace.py`/`suspicious_state_policy.py` are `blocked`** — live `shared-keep` dependent (`suspicious_selected_state_routing.py`); reclassify + relocate, don't remove |
| 2 | Are `llm_heavy_*` retired precursors or living comparators? | **Living comparators** — both CLI-registered with full specs, both in `FAMILY_SHORT_LABELS`, both have dedicated tests + mature run history + active doc references. Not superseded-candidates; no action needed |
| 3 | Are `saturated_surface_evaluation`/`synthetic_hard_case_component_stress` exclusive to the adjudicator lineage? | **`saturated_surface_evaluation`: yes, cleanly** (`safe-to-remove` + test). **`synthetic_hard_case_component_stress`: no — compound** (adjudicator-coupled half is exclusive; loader half is shared-keep-dependent; needs porting, not blocking) |
| 4 | Do the 13 `hybrid_parallel_state_candidate_reasoner`-referencing analyzers have live CLI/observatory wiring (the "blocked" scenario)? | **No** — re-check found **zero** CLI/observatory entries for any of the 13 under any name (filenames or function names). All 13 are loose string-literal artifact-path/label couplings, not code imports. **Not blocked** — `needs-doc-archival-first` + `needs-test-removal-first` (9 of 13) |
| 5 | `cli/llm_pipeline_cli.py`/`observatory/api.py` registry entries | **Confirmed shared-keep**, confirmed every superseded-candidate runner needs explicit unwiring; additionally found the `hybrid_parallel_state_candidate_reasoner` entries are **dead** (no backing registry rows) while `hybrid_rules_candidates_llm_adjudicator`/`llm_only_claim_table_selector`/`llm_only_typed_*` entries are **live** (have registry rows) |
| 6 | The two exclusive report writers | **Confirmed exclusive** — `reports/claim_table_report.py` imported only by `llm_only_claim_table_selector`; `reports/hybrid_adjudicator_report.py` imported only by `hybrid_rules_candidates_llm_adjudicator` |
| 7 | `llm_only_structured_events_repair_ablation.py` re-check | **Confirmed not the active ablation mechanism** — no run history, no CLI/observatory wiring, only mentioned in this week's planning docs and a 2026-06-01 structural inventory. One-directional import of the canonical module (no reverse dependency). Joins the standard `llm_only_*` removal batch |
