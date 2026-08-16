# SF Surface Registry — Public API & Migration Guide

**Task:** ExECTv2 P1-1 (thermo-nuclear audit)  
**Design:** `docs/plans/exectv2_sf_repair_stack_consolidation_design_2026-06-26.md`

The registry is the **canonical owner** of shared SeizureFrequency (SF) clinical
surface definitions. Three legacy stacks remain for one release cycle behind
deprecation shims; new code should import from here.

## Public API

| Module | Purpose |
|--------|---------|
| `sf_surface_registry` | Query API: `SurfacePhase`, `SurfaceRule`, `rules_for_phase`, `validate_unique_rule_ids` |
| `sf_surface_registry.patterns` | Compiled regex + token fragments from `patterns.yaml` |
| `sf_surface_registry.adapters.convention` | Stack B facade: `apply_rewrite`, `is_sf_convention_noise`, `sf_residual_additions` |
| `sf_surface_registry.adapters.projection` | Stack C facade (SF subset; delegates to `target_projection` until Phase 3) |
| `sf_surface_registry.adapters.extraction` | Stack A facade: `RATE_RULES`, `ANCHOR_RULES`, `rule_by_id` from `catalog/extract.yaml` |
| `sf_surface_registry.parity.shadow_diff` | Shadow parity harness (Stack B rewrite vs registry adapter) |

### Preferred imports (2026-06-26)

```python
# Shared patterns (Phase 1 — canonical)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.patterns import (
    EVERY_N_TO_M_PERIODS,
    NO_FURTHER_SINCE,
)

# Convention repair (Phase 2 pending — adapter delegates to legacy)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry.adapters.convention import (
    apply_rewrite,
    sf_residual_additions,
)

# Catalog query
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.sf_surface_registry import (
    SurfacePhase,
    rules_for_phase,
)
```

### Removed legacy import paths

Shims were removed after Observatory / replay confirmed no external imports.
Use the registry adapters directly:

| Former path | Use instead |
|-------------|-------------|
| `conventions.seizure_frequency` | `sf_surface_registry.adapters.convention` |
| `standard_dictionary.sf_*` (SF only) | `sf_surface_registry.adapters.convention` |
| `target_projection` (SF projection) | `sf_surface_registry.adapters.projection` |
| `rules.*` named rule re-exports | `sf_surface_registry.adapters.extraction` |
| Inline duplicate regex in stacks A/B/C | `sf_surface_registry.patterns` |

## Migration status

| Phase | Scope | Status |
|-------|-------|--------|
| 0 | Parity harness, rule index, catalog stubs | ✅ Complete |
| 1 | `patterns.yaml` shared by Stacks A/B/C | ✅ Complete |
| 2 | Convention rewrite → catalog + adapter loop | ✅ Complete |
| 3 | Projection catalog; policy from registry | ✅ Complete |
| 4 | Extraction RuleSpec metadata → catalog | ✅ Complete |
| 5 | Shim removal, approval gate docs | ✅ Complete |

## Regenerating the rule index

The checked-in rule index enumerates all `rule_id` values across the three
stacks for duplicate-ID CI gates and catalog scaffolding.

```bash
python scripts/generate_sf_surface_rule_index.py
```

**Outputs:**

- `docs/plans/sf_surface_rule_index.yaml` — 135 unique rule IDs (47 extract + 41 convention + 47 projection)
- `sf_surface_registry/catalog/convention_rewrite.yaml` — Stack B rewrite stubs

Run after adding or renaming any `rule_id` in `rules/`, `conventions/seizure_frequency.py`, or `target_projection/`.

## CI gates

Living SF extra-AR exemplars: `tests/test_sf_extra_ar_exemplars.py`.
State/ownership projection exemplars: `tests/test_exectv2_sf_state_projection.py`.

## Quarantine model

Projection families default **off** via `target_projection.policy`. Phase 3
will move `quarantine_family` metadata into `catalog/projection_sf.yaml` and
derive `QUARANTINED_TARGET_PROJECTION_FAMILIES` from the registry. Until then,
quarantine sets remain in `target_projection/constants.py` with shared patterns
sourced from `patterns.yaml`.

## Follow-ups after Phases 2–4

1. **Phase 2:** Flip adapter to own rewrite loop; shrink `conventions/seizure_frequency.py` to <500 LOC facade re-exporting from adapter.
2. **Phase 3:** Route `llm_target_indicators_single_call.py` through `adapters.projection.apply_all()`; derive quarantine from catalog.
3. **Phase 4:** Generate `RATE_RULES` etc. from `catalog/extract.yaml`.
4. **Post-migration:** Remove deprecation shims; delete legacy implementation modules after one release cycle.
