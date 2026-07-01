# Documentation Archive

Last updated: 2026-07-01

**Status:** Active — Wave 4 moved stubbed iteration narratives here with redirect
stubs at original paths.

## Policy

1. **Canon summaries** absorb narrative sprawl (see [`docs/canon/README.md`](../canon/README.md)).  
2. **Redirect stubs** at original paths point to archive + canon; frozen paths never move.  
3. **Machine artifacts** (`experiments/*.jsonl`) are never archived — replay spine.  
4. **Frozen paths** in `final_artifact_index` are never moved or renamed.

Procedure before any future move:

1. Update [`docs/experiments/final_artifact_index_2026-06-22.md`](../experiments/final_artifact_index_2026-06-22.md) if paths are indexed.  
2. Leave redirect stub at old path OR update all internal links in same PR.  
3. Run `python3 scripts/check_doc_hygiene.py`.

---

## Layout (Wave 4)

```
docs/archive/
  experiments/
    gan2026/
      validation750/     # 31 files — VALIDATION750_CANON absorbs
      rq_series/         # 31 files — COMPONENT_MECHANICS_CANON absorbs
    exectv2/
      key_entities/      # 13 files — v01–v07 holistic + EAs (v08 frozen in place)
  ARCHIVE_INDEX.md
```

---

## Already archived elsewhere

Superseded **experiment notes** (not docs/) live under
[`experiments/archive/`](../../experiments/archive/) — see
[`experiments/archive/ARCHIVE_INDEX.md`](../../experiments/archive/ARCHIVE_INDEX.md).

Superseded **plans** remain in `docs/plans/` with HISTORICAL status banners until
P2 repo simplification runs.
