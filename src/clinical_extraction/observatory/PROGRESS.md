# Observatory Backend — Progress Log

**Last updated:** 2026-06-07

## Current Active Surface

The Observatory keeps historical run records queryable through `/registry`, but
the active `/pipeline-families` surface now filters deleted runner families out
of dropdowns and replay-oriented UI paths.

Canonical families are always listed, even before they have registry-backed
artifacts:

| Family | Label | Notes |
| --- | --- | --- |
| `rules_only` | Deterministic V1 | Executable via `/run/note` and `/run/ablation`. |
| `llm_only_direct_labeler` | LLM Direct Labeler | Canonical one-shot fully LLM runner. |
| `hybrid_structured_events` | LLM Structured Events | Canonical structured fully LLM runner. |
| `reset_clinical_assessment_pipeline` | Reset Clinical Assessment | Canonical hybrid/reset runner. |

Retained historical/comparator families may still appear when backed by registry
rows, including `llm_structured_events`,
`llm_heavy_clinical_frequency_reasoner`,
`llm_heavy_evidence_selection_with_deterministic_adapters`,
`hybrid_clinical_frequency_state_graph`, `llm_first_direct_extractor`,
`dspy_final_selection_adjudicator`, and
`llm_replacement_postprocessing_ablation`.

Unreviewed registry family strings are also filtered out of
`/pipeline-families`; they remain available only through `/registry` until a
future explicit retention decision promotes them.

Deleted runner families are preserved only in historical registry data and old
research artifacts. They are intentionally filtered out of active selectors and
are not replay-supported by the frontend dispatcher.

## Frontend Replay Adapters

The replay adapter dispatcher supports only active/canonical or retained
comparator artifact shapes:

| File | Families handled |
| --- | --- |
| `deterministic.ts` | `rules_only` live deterministic traces |
| `decisionRecord.ts` | direct decision-record families |
| `events.ts` | structured-event and LLM-heavy event families |
| `selectedFact.ts` | selected-fact with deterministic adapters |
| `stateGraph.ts` | clinical frequency state graph |
| `ablation.ts` | replacement post-processing ablation |

The frontend has a small retired-family deny-list in `lib/pipelineFamilies.ts`
so historical rows do not repopulate active run selection.

## Known Issues / Next Steps

1. Frontend lint has pre-existing React/ESLint failures unrelated to the
   consolidation cleanup; TypeScript and Jest checks pass.
2. Historical registry rows remain intentionally queryable. If a future UI needs
   a historical archive mode, add an explicit archive toggle instead of mixing
   retired families back into the active workbench.

## Backend Restart Command

```powershell
.venv\Scripts\python.exe -m uvicorn clinical_extraction.observatory.api:app --reload --port 8000
```
