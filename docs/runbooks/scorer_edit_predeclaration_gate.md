# Scorer-Edit Predeclaration Gate

Scoring, projection, and lexicon code is part of the measurement instrument. A
change can move reported numbers even when extraction output is unchanged. The
gate requires a declared hypothesis and a `dev140` replay before such a change
is committed.

## What The Gate Checks

`scripts/check_scorer_edit_predeclaration.py` accepts changed paths and a commit
or pull-request message. If a guarded path changed, the message must:

1. name a `hypothesis_id` present in
   `experiments/hypothesis_registry.jsonl`; and
2. mention a `dev140` replay, re-score, or rerun.

The guarded paths are defined by `_GUARD_RULES` in the script and cover ExECT
scoring, deterministic conventions and projections, projection-named Python
files, and the drug lexicon. The script does not call Git.

## Local Use

```sh
git diff --cached --name-only \
  | python scripts/check_scorer_edit_predeclaration.py \
      --stdin --message-file .git/COMMIT_EDITMSG
```

Or pass the inputs explicitly:

```sh
python scripts/check_scorer_edit_predeclaration.py \
  --message "<hypothesis_id>; dev140 replay <result>" \
  src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py
```

Exit codes are `0` for clean, `1` for blocked, and `2` for invalid use.

## Commit-Message Hook

Install this optional local hook in each clone:

```sh
cat > .git/hooks/commit-msg <<'SH'
#!/usr/bin/env sh
git diff --cached --name-only \
  | python scripts/check_scorer_edit_predeclaration.py \
      --stdin --message-file "$1"
SH
chmod +x .git/hooks/commit-msg
```

## When The Gate Blocks

- Add an `OPEN` row with a hypothesis, kill criterion, and intended `dev140`
  replay to `experiments/hypothesis_registry.jsonl`.
- Run the replay and record whether the expected score moved.
- Cite the hypothesis and replay result in the commit or pull-request message.
- Update selected evidence only through a declared, repeatable producer. If no
  current producer exists, keep the retained artifact frozen rather than
  hand-editing it.

Pure refactors follow the same rule: declare the expected no-change result and
verify it on `dev140`.

## Related Checks

- `tests/test_scorer_scope_invariants.py`
- `tests/test_scorer_projection_consistency.py`
- `docs/design/deterministic_projection_rule_taxonomy.md`
- `docs/experiments/retained_evidence_manifest.json`
