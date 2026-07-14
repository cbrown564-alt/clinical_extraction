# Regenerating retained evidence

The retained evidence manifest owns selected artifact paths and hashes.

## Verify selected files

```sh
source .venv/bin/activate
python scripts/check_retained_evidence_manifest.py
python scripts/verify_reference_evidence.py
```

The first command checks paths, hashes, byte sizes, registry metadata, and the
two-task by three-family matrix. The second replays or re-scores all six
reference cells without model calls.

## Regenerate a reference cell

Use the entry point, configuration, scorer, data contract, and tests listed in
that cell's `closure` object in
`docs/experiments/retained_evidence_manifest.json`. Do not infer a producer
from a historical filename.

Any changed selected artifact requires:

1. a documented reason and unchanged split boundary;
2. a regenerated hash and byte size;
3. matching registry metadata;
4. both verification commands; and
5. an update to the claims register if the result changes.

## Paper

The maintained manuscript source is
`docs/research/paper_manuscript_2026-06-26.md`. The IEEE source remains under
`literature/IEEE/IEEE-conference-template-062824/` and may lag until the final
evidence sync.

