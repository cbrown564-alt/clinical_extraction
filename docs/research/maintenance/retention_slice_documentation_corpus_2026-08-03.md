# Decision 0048 retention slice: documentation corpus triage

Date: 2026-08-03  
Status: **indexes thinned**; **6 orphan docs deleted**; peer-satellite cull deferred  
Decision: [0048](../../decisions/0048-comprehension-and-handoff-refactor.md)  
Glossary: [CONTEXT.md](../../../CONTEXT.md) (Documentation reading paths)

## What landed

1. Thinned [`docs/NAVIGATION.md`](../../NAVIGATION.md) to supervisor handoff,
   current work, pipeline doors, and the three-link evidence pointer block.
2. Expanded [`docs/THREAD_MAP.md`](../../THREAD_MAP.md) “Change the
   implementation” with durable design/decision doors only.
3. Reshaped [`PROJECT_STATUS.md`](../../../PROJECT_STATUS.md) to the live
   control panel (no verification archaeology / evidence catalog).
4. Kept `CONTEXT.md` glossary-only (removed false 0046 backlog header).
5. Rebound Decision 0046 Phase A/B/C report links and Decision 0047 parity
   summary onto those decisions as living owners.

## Deleted

| Path | Reason |
| --- | --- |
| `docs/experiments/exectv2/rules_base_parity_264237bd.md` | No living owner, config, script, or test citation; superseded by 0047 parity package |
| `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_score_guide_2026-07-14.md` | Lost active-index citation; no hard caller |
| `docs/experiments/exectv2/diagnosis/exectv2_diagnosis_pattern_assisted_review_protocol_2026-07-14.md` | Lost active-index citation; no path hard caller |
| `docs/experiments/exectv2/reliability/exectv2_gemma4_context_probe_dev140_protocol_2026-07-17.md` | No protocol-path caller; configs cite experiment IDs only |
| `docs/experiments/gan2026/gan2026_deepseek_v4_flash_0731_holdout_rerun_protocol_2026-07-31.md` | Stub with no living owner or hard caller |
| `docs/experiments/gan2026/gan2026_local_val750_qwen_gemma_protocol_2026-07-18.md` | No living owner, config, or script citation |

None appear in `retained_evidence_manifest.json`. Recovery: Git history.

## Kept (not deleted this slice)

- Protocols and reports with check-script, run-script, or config `protocol`
  path fields (including rejected-policy negative replay).
- Research satellites still linked from the canonical six-model comparison
  report or other retained research synthesis pages. Deleting those would
  require editing the comparison report; deferred rather than creating broken
  links inside a living-cited document.

## Deferred

- Peer-satellite cull among `docs/research/*` and focused experiment reports
  that are only reachable from other demoted/research pages.
- Manuscript provenance wording pass (separate from index triage).

## Follow-on completed outside this slice

- README currency pass (2026-08-03): decluttered glance layer; Gan Purist and
  ExECT `clinical_headline` primary results shown as peers in `README.md` and
  `PROJECT_STATUS.md` Current outcome.

## Checks

- Retained-evidence manifest check after this slice.
- No inbound references to the six deleted paths remained in `docs/`,
  `scripts/`, `tests/`, `configs/`, or `src/` at delete time.
