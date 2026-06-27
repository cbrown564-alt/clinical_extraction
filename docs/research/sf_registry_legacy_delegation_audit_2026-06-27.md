# SF Surface Registry — Legacy Delegation Audit

**Date:** 2026-06-27
**Task:** Wave 1 workstream I1 (closing campaign orchestration)
**Scope:** Read-only audit of `sf_surface_registry/` delegation depth
**Reference design:** `docs/plans/exectv2_sf_repair_stack_consolidation_design_2026-06-26.md`

---

## 1. Per rule-family verdict table

| Rule family | Catalog file | Rule count | Verdict | Orchestration | Behavior execution |
|-------------|--------------|------------|---------|---------------|-------------------|
| `convention_rewrite` | `catalog/convention_rewrite.yaml` | 41 | **Hybrid (catalog-orchestrated, partially legacy-delegated)** | `builders/registry.py` iterates `rules_for_phase(REWRITE)` | 36 discrete builders in `rewrite_builders.py` (~609 LOC); **5 operand-format rules delegate** to `_legacy_rewrite._sf_operand_format_rewrite`; regex constants from `_legacy_constants.py` |
| `convention_noise` | `catalog/convention_noise.yaml` | 13 | **Catalog-orchestrated; owns behavior** | `registry.apply_noise_builders` | 13 inline builders in `noise_builders.py`; regex constants imported from legacy; monolithic `_legacy_noise.is_sf_convention_noise` **not** on production path |
| `convention_residual` | `catalog/convention_residual.yaml` | 1 | **Catalog-indexed, legacy-executed** | Single catalog entry `residual_all_patterns` | `residual_builders.py` → `_legacy_residual.sf_residual_additions` (~905 LOC) |
| `extract` | `catalog/extract.yaml` | 47 | **Catalog-indexed metadata; legacy-executed** | `adapters/extraction.py` assembles `RuleSpec` lists from catalog order | `pattern` + `build` callbacks in `rules/{anchor,rate_builders,seizure_free,change,temporal}.py` via `*_EXTRACT_IMPLS` dicts |
| `projection_sf` | `catalog/projection_sf.yaml` | 31 | **Hybrid (catalog metadata + registry builders)** | `adapters/projection.py` hand-wires `_ProjectionAdapter` methods | Implementations in `builders/projection_{sf_state,cross_entity,evidence_repair}.py` (~1,163 LOC); constants/policy/shared still in `target_projection/`; **no `builder` field in YAML, no catalog loop** |
| `builders/registry.py` | — | — | **Owns orchestration** | Catalog-driven loops for rewrite/noise/residual | Dispatches to registered builder callables |
| `builders/rewrite_builders.py` | — | 41 registered | **Hybrid** | Registered per catalog `builder` name | Owns 36 branch predicates; delegates `operand_format_rewrite` |
| `builders/noise_builders.py` | — | 13 registered | **Owns behavior** | Registered per catalog `builder` name | Inline branch logic |
| `builders/residual_builders.py` | — | 1 registered | **Legacy-delegated** | Thin wrapper | `return legacy.sf_residual_additions(note_text)` |
| `builders/_legacy_*` | — | — | **Legacy reference / residual executor** | Re-exported via `_legacy_impl.py` | ~1,850 LOC total; used by shadow_diff + residual + operand_format |
| `builders/projection_*.py` | — | — | **Owns behavior (migrated Stack C)** | Called by projection adapter | Former `target_projection/{sf_state,cross_entity,evidence_repair}.py` logic; those modules **deleted** |

---

## 2. Evidence and delegation chains

### 2.1 Production call chain (convention — Stack B)

```
assembly/lenses/seizure_frequency.py
  → deterministic/standard_dictionary.py (re-exports conventions)
  → deterministic/conventions/__init__.py
  → sf_surface_registry/adapters/convention.py
      sf_convention_rewrite / is_sf_convention_noise / sf_residual_additions
  → sf_surface_registry/builders/registry.py
      apply_rewrite_builders / apply_noise_builders / collect_residual_candidates
  → catalog/*.yaml via catalog.rules_for_phase()
  → rewrite_builders.py | noise_builders.py | residual_builders.py
```

**Key files:**
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_surface_registry/adapters/convention.py`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_surface_registry/builders/registry.py`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/sf_surface_registry/catalog/convention_*.yaml`

### 2.2 `convention_rewrite` — hybrid delegation

**Catalog owns:** rule IDs, phase tags, builder name mapping, iteration order.

**Registry owns:** per-branch builder functions (duplicated from legacy monolith).

**Legacy still executes:**
- `operand_format_rewrite` → `legacy._sf_operand_format_rewrite(...)` in `_legacy_rewrite.py` (covers catalog rules: `collapse_equal_*`, `drop_per_month_spurious_month_date`, `rewrite_exact_*_operand_format`, etc.)
- Shared regex constants via `_legacy_constants.py` (partially sourced from `patterns.yaml`)

**Parity gate:** `parity/shadow_diff.py` compares `_legacy_impl.sf_convention_rewrite` (monolithic) vs `apply_rewrite_adapter` (catalog loop). CI: `test_shadow_diff_zero_mismatches_on_all_standard_dictionary_cases`.

### 2.3 `convention_noise` — catalog-orchestrated, inline builders

All 13 `noise_branch_*` builders implement logic directly in `noise_builders.py`. Regex constants (`_SF_VAGUE_EPISODE_RE`, `_SF_CONTEXTUAL_RATE_NOISE_RE`, etc.) are imported from `_legacy_impl` / `_legacy_constants.py`.

Monolithic `_legacy_noise.is_sf_convention_noise` remains for reference; production uses the catalog loop only.

### 2.4 `convention_residual` — full legacy delegation

```python
# residual_builders.py
@register_builder("residual_all_patterns")
def residual_all_patterns(note_text: str) -> list[ResidualCandidate]:
    return legacy.sf_residual_additions(note_text)
```

Catalog explicitly records `source_stack: sf_surface_registry/builders/_legacy_impl.py`. All ~50+ residual pattern loops live in `_legacy_residual.py` (~905 LOC).

### 2.5 `extract` — metadata catalog, Stack A execution

**Catalog owns:** `rule_id`, `rule_set`, `order`, `group`, `portability`, `description`, `examples`, `provenance`, `exclude`, `builder` name (string reference).

**Stack A owns:** `ExtractRuleImpl.pattern` and `.build` in:
- `rules/anchor.py` → `ANCHOR_EXTRACT_IMPLS`
- `rules/rate_builders.py` → `RATE_EXTRACT_IMPLS`
- `rules/seizure_free.py`, `change.py`, `temporal.py`

**Assembly:** `adapters/extraction.py` `_build_rule_spec()` joins catalog entry + impl dict.

**Consumers:** `deterministic/pipeline.py`, `statement_parser.py`, `frequency_section.py` import `RATE_RULES` etc. from the extract adapter.

**CI:** `test_extract_adapter_rule_count_matches_catalog`, `test_extract_adapter_examples_match_catalog_metadata`.

### 2.6 `projection_sf` — catalog metadata + migrated builders

**Catalog owns:** 31 rule IDs, `phases: [project|evidence_repair]`, `quarantine_family` on 9 families, stale `source_stack` pointers (e.g. `target_projection/sf_state.py` — **module deleted**).

**Registry builders own:** SF projection/repair logic in:
- `builders/projection_sf_state.py` (~349 LOC)
- `builders/projection_cross_entity.py` (~486 LOC)
- `builders/projection_evidence_repair.py` (~328 LOC)

**Still external to catalog:**
- `target_projection/constants.py`, `policy.py`, `shared.py`, `types.py`, `investigations.py`
- `target_projection/__init__.py` lazy-re-exports builder symbols (PEP 562) for backward compatibility
- `target_projection/policy.py` derives `QUARANTINED_TARGET_PROJECTION_FAMILIES` from `catalog.quarantined_projection_families()` ✅

**Orchestration:** `adapters/projection.py` `_ProjectionAdapter` manually wires methods — **not** a `rules_for_phase(PROJECT)` loop. Some rules in catalog (`split_*`, `normalized_*`) still live in `llm/llm_target_indicators_single_call.py` per `source_stack` metadata.

**Consumer:** `llm/pipelines/target_indicators_single_call/projection.py` → `adapters.projection.apply_all`.

### 2.7 Legacy module inventory

| Module | LOC (approx) | Role |
|--------|-------------|------|
| `_legacy_impl.py` | 29 | Re-export barrel |
| `_legacy_rewrite.py` | 391 | Monolithic rewrite + operand-format (parity reference) |
| `_legacy_noise.py` | 108 | Monolithic noise (not production path) |
| `_legacy_residual.py` | 925 | **Production residual executor** |
| `_legacy_constants.py` | 397 | Regex constants (partially from `patterns.yaml`) |

**Removed:** `deterministic/conventions/seizure_frequency.py`, `target_projection/{sf_state,cross_entity,evidence_repair}.py`.

---

## 3. Honest paper claim (exact sentence)

> ExECTv2 consolidates SeizureFrequency surface rules into a single YAML-indexed registry (133 rule IDs across extraction, convention repair, and projection) with shared regex patterns and phase adapters, but clinical behavior is still split: convention rewrite and noise run through catalog-driven builder loops while residual additions and operand-format rewrites execute in legacy Stack B modules, extraction regex and builders remain in `rules/`, and projection logic—though relocated under registry builders—is orchestrated by hand-written adapters rather than catalog-driven dispatch.

---

## 4. What would need to change to promote catalog to own behavior

### `convention_rewrite`
- Inline `_sf_operand_format_rewrite` into `rewrite_builders.py` (or split into 5 catalog-backed operand builders with declarative predicates).
- Move remaining `_legacy_constants.py` regex into `patterns.yaml` / catalog `pattern_id` references.
- Delete `_legacy_rewrite.py`; retain shadow_diff against archived golden outputs, not live monolith.

### `convention_noise`
- Migrate noise regex constants fully to `patterns.yaml`.
- Add shadow parity harness for noise (currently rewrite-only).
- Delete `_legacy_noise.py`.

### `convention_residual`
- Decompose `_legacy_residual.py` into per-pattern catalog entries + registered builders (or codegen from a residual pattern table).
- Replace single `residual_all_patterns` stub with N catalog rules matching residual families.
- Largest remaining legacy-delegation gap (~905 LOC).

### `extract`
- Move `ExtractRuleImpl` pattern/build functions into registry `builders/extract_*.py` (or codegen from catalog).
- Optionally embed regex via `pattern_id` → `patterns.yaml` instead of inline `re.compile` in `rules/`.
- Keep `extract.yaml` as single source for metadata **and** builder binding.

### `projection_sf`
- Add `builder` fields to `projection_sf.yaml` mapping rule_id → registry function.
- Implement `apply_projection_builders()` catalog loop (mirror convention `registry.py`).
- Route `_ProjectionAdapter` through catalog dispatch; migrate LLM-local `split_*` rules into builders.
- Refresh stale `source_stack` metadata; collapse `target_projection/` to policy/constants only.

### `builders/*` (cross-cutting)
- Delete `_legacy_impl.py` barrel and all `_legacy_*.py` after parity gates pass per family.
- Update README claim from "canonical owner" to accurate split, or complete migration first.
- Extend CI beyond rewrite shadow_diff: noise, residual, projection rule-attribution parity.

---

## 5. Test / CI evidence

| Gate | File | What it proves |
|------|------|----------------|
| Unique rule IDs | `test_catalog_rule_ids_are_unique` | Catalog integrity |
| Rewrite shadow parity | `test_shadow_diff_*` | Registry adapter == monolithic legacy rewrite |
| Extract metadata parity | `test_extract_adapter_*` | Catalog metadata matches assembled RuleSpecs |
| Shared patterns | `test_shared_patterns_match_standard_dictionary_fixtures` | Phase-1 pattern canonicalization |
| LOC gates | `test_registry_package_line_count_gate` | Registry package bounded |

**Not gated:** noise parity vs legacy, residual decomposition, projection catalog-driven dispatch.

---

## 6. README / design doc drift

- `sf_surface_registry/README.md` states registry is "**canonical owner**" and Phase 2 convention adapter "delegates to legacy" — partially stale: rewrite/noise use catalog loops; residual and operand-format still legacy.
- Design doc Phase 5 claims "legacy paths are thin facades" — `_legacy_residual.py` (~905 LOC) and duplicated rewrite builders (~609 LOC) contradict this.
- `catalog/projection_sf.yaml` `source_stack` values reference deleted modules.

---

*Audit performed read-only on 2026-06-27. No holdout reads. No git operations.*
