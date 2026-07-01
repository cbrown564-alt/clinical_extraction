# Documentation Archive

Last updated: 2026-07-01

**Status:** Policy placeholder — bulk archive moves are **deferred** per
[`docs/plans/repo_simplification_plan_2026-06-22.md`](../plans/repo_simplification_plan_2026-06-22.md)
(freeze-and-index before delete).

## Current approach (Wave 3)

Instead of moving files:

1. **Canon summaries** absorb narrative sprawl (see [`docs/canon/README.md`](../canon/README.md)).  
2. **Stub banners** on absorbed sources point to canons; full text stays in place.  
3. **Machine artifacts** (`experiments/*.jsonl`) are never archived — replay spine.  
4. **Frozen paths** in `final_artifact_index` are never moved or renamed.

## Future archive layout (when P2 cleanup runs)

```
docs/archive/
  plans/          # superseded dated plans (status: HISTORICAL)
  experiments/    # pilot ladders superseded by workstream canons
  research/       # iteration syntheses merged into canon
  ARCHIVE_INDEX.md
```

Procedure before any move:

1. Update [`docs/experiments/final_artifact_index_2026-06-22.md`](../experiments/final_artifact_index_2026-06-22.md) if paths are indexed.  
2. Leave stub redirect at old path OR update all internal links in same PR.  
3. Run `python3 scripts/check_doc_hygiene.py`.

## Already archived elsewhere

Superseded **experiment notes** (not docs/) live under
[`experiments/archive/`](../../experiments/archive/) — see
[`experiments/archive/ARCHIVE_INDEX.md`](../../experiments/archive/ARCHIVE_INDEX.md).
