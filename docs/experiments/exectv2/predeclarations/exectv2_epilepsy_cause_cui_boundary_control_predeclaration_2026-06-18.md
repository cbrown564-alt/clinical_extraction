# ExECTv2 EpilepsyCause CUI Boundary-Control Predeclaration

- Date: `2026-06-18`
- Surface: ExECTv2 `dev` only
- Status: predeclared diagnostic plan; no mapping promotion authorized
- Source artifact: `experiments/exectv2_cui_missing_mapping_ledger_dev140_20260618.csv`

## Purpose

EpilepsyCause residual CUI mappings must remain diagnostic-only until a targeted
dev-only boundary-control audit shows that a candidate variant is a safe
benchmark-format projection. This protects the distinction between selected
clinical cause mentions and deterministic CUI attachment.

## Current Residual Candidates

The current dev140 missing-mapping ledger leaves these EpilepsyCause forms as
`review_needed_long_tail`:

| Concept | Mentions | Candidate CUI | Decision |
| --- | ---: | --- | --- |
| `erinatal insult` | 1 | `C0005604` | diagnostic only |
| `traumatic brain injury 2005` | 1 | `C0876926` | diagnostic only |
| `easle` | 1 | `C0025007` | diagnostic only |
| `hypoxia during a difficult birth.` | 1 | `C0559478` | diagnostic only |
| `neurocysticercosis.` | 1 | `C0338437` | diagnostic only |

## Boundary-Control Evidence Required

Before any residual variant can be promoted into
`benchmark_projection.epilepsy_cause_concept`, the audit must be run and written
up on dev only:

1. Confirm the mapping is a one-to-one benchmark-format projection after the
   EpilepsyCause mention has already been selected.
2. Show the variant does not broaden clinical-cause selection, repair entity
   assignment, or add a new EpilepsyCause mention.
3. Include boundary controls for typo, punctuation, date-suffix, historical
   context, and PatientHistory/BirthHistory overlap risk.
4. Report semantic CUI-free and CUI-projected scores separately, with the delta
   attributed only to deterministic benchmark-format projection.
5. Keep all outputs labeled `dev_only_boundary_control_diagnostic`.

## Prohibited Uses

- Do not inspect ExECTv2 holdout or Gan `test450` row-level failures.
- Do not run full-200 or test-facing audits for this decision.
- Do not treat a one-row dev residual as production ontology truth.
- Do not promote EpilepsyCause variants because the target CUI is obvious from
  the ledger alone.

## Promotion Gate

Promotion is allowed only in a later change if the dev-only report shows:

- zero boundary-control regressions on the predeclared controls;
- unchanged CUI-free clinical recovery;
- a CUI-projected-only gain confined to already-selected EpilepsyCause mentions;
- tests pinning both the promoted variant and the still-blocked residual forms.

Until then, these variants stay diagnostic-only.
