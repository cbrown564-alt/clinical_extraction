# Regenerating retained evidence

The retained evidence manifest owns selected artifact paths and hashes.
Its `architecture_freeze` object also owns the exact source commit and policy
fingerprints for new evidence.

## Recreate the verified environment

Use Python 3.11 explicitly. An unconstrained resolver may select a newer
interpreter even when the lock is otherwise unchanged.

```sh
uv sync --python 3.11 --frozen --extra dev
```

## Retrieve large selected artifacts

Five large ExECT replay files are content-addressed Git LFS objects. A normal
clone with Git LFS installed downloads them automatically. If a checkout
contains pointer files, retrieve the objects before validation:

```sh
git lfs pull
```

The JSON manifest records each LFS object ID, canonical content hash, and byte
size. Do not replace an object without updating all three values and replaying
the selected evidence.

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

Changing a frozen prompt, scorer, split, repair layer, model route, or component
graph requires a new freeze ID. The current freeze does not itself authorize a
model call; a live run also needs a predeclared question and exact runtime
condition.

## Paper

The maintained manuscript source is
`docs/research/paper_manuscript_2026-06-26.md`. The IEEE source remains under
`literature/IEEE/IEEE-conference-template-062824/`. The two sources are
synchronized to the retained manifest, and tests reject retired headline and
calibration values.

Build the IEEE PDF from that directory with two `pdflatex` passes, then inspect
every rendered page before treating the PDF as current.

