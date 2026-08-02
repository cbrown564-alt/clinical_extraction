# Decision 0048 retention slice: orphan / superseded docs

Date: 2026-08-02  
Status: **deleted** (5 files); **kept for negative-replay** (4 rejected-policy docs)  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md) broader corpus triage  
Inventory: [docs research orphans explore](../../../PROJECT_STATUS.md)

## Deleted

| Path | Reason |
| --- | --- |
| `docs/research/contribution_thesis.md` | Zero inbound links; framing owned by README + `docs/canon/README.md` |
| `docs/research/from_structured_output_to_clinical_interpretation.md` | Zero inbound links; superseded by canonical six-model comparison report |
| `docs/research/maintenance/repository_surgery_assessment_2026-07-14.md` | Declared non-owner; competed with PROJECT_STATUS / ACTIVE_ROADMAP |
| `docs/experiments/exectv2/reliability/exectv2_six_model_gpt41mini_dev140_2026-07-15.md` | Pre–0041 two-call report; manifest keeps `*_single_call_*` variant |
| `docs/experiments/exectv2/reliability/exectv2_six_model_gpt56luna_dev140_2026-07-15.md` | Same for Luna |

None appear in `retained_evidence_manifest.json`. Recovery: Git history.

## Kept (judgment): rejected-policy docs

These were proposed for delete but **must remain** while check scripts require the
predeclared protocol path:

- `exectv2_model_preserving_policy_candidate_{,protocol_}2026-07-15.md`
- `exectv2_prescription_rescue_scope_candidate_{,protocol_}2026-07-15.md`

`scripts/check_exectv2_model_preserving_policy_candidate.py` (and the rescue
sibling) fail if `PROTOCOL_PATH` is missing. They support negative / rejected
candidate reproduction (Decision 0048 keep criterion 5). Deleting them needs a
coordinated script + machine-artifact retarget, not a docs-only slice.

## Hygiene in this slice

Fixed five broken `docs/REGENERATION.md` links that used
`../research/maintenance/...` (resolves outside `docs/`) to
`research/maintenance/...`.

## Out of scope

Borderline diagnosis review docs with test/CLI coupling; broader
`experiments/` binary/JSON triage (separate inventory).
