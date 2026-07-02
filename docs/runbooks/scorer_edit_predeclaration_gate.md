# Scorer-edit predeclaration gate

Repeatable procedure for the Phase-4 standing guardrail of the ExECTv2 pipeline
assumption audit (plan: `docs/plans/exectv2_pipeline_assumption_audit_plan_2026-07-02.md`).
Companion: `docs/research/exectv2_pipeline_assumption_audit_phase4_guardrail_2026-07-02.md`.

## Why this gate exists

The ExECTv2 **scoring, projection, and lexicon** layers are the measurement
instrument. A change to any of them retroactively moves numbers the manuscript,
dossiers, registry, and frontend snapshot cite. The project already requires — by
convention — that such a change be **predeclared as a hypothesis** and validated
with a **dev140 replay** before it ships. The seed defect
(`rx_future_medication_regex_scope_bug_2026-07-02`) reached the manuscript
precisely because that convention was not enforced at commit time. This gate makes
it structural.

## What the gate checks

`scripts/check_scorer_edit_predeclaration.py`: given a set of changed files and a
commit/PR message, if any changed path is **guarded**, the message must

1. reference a `hypothesis_id` that **exists** in
   `experiments/hypothesis_registry.jsonl`, and
2. mention a **dev140 replay** (a `dev140`/`dev-140`/`dev 140` token *and* a
   replay/re-score/re-run verb).

Otherwise it exits non-zero and prints what is missing.

**Guarded paths** (kept in lockstep with `_GUARD_RULES` in the script):

| Path signature | Layer |
| --- | --- |
| `exectv2/scoring/` | scored key builders (`prescription.py`, `seizure_frequency.py`, `investigations.py`, `match.py`, `normalize.py`) |
| `deterministic/conventions/` | projection convention layer |
| `deterministic/target_projection/` | benchmark target projection |
| `deterministic/sf_state_projection.py` | SF state projection |
| any `*_projection*.py` | generic projection-file convention |
| `contract/drug_lexicon.py` | drug canonicalization lexicon |

The script **never runs git**. The caller supplies the changed paths (positional
args or `--stdin`) and the message (`--message` or `--message-file`).

## Manual / local use

```bash
# Check staged files against the current commit message draft.
git diff --cached --name-only \
  | python scripts/check_scorer_edit_predeclaration.py --stdin --message-file .git/COMMIT_EDITMSG

# Or pass paths + message explicitly.
python scripts/check_scorer_edit_predeclaration.py \
  --message "Fix rx_future_medication_regex_scope_bug_2026-07-02 ...; dev140 replay 0.8766 -> 0.9073" \
  src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/scoring/prescription.py
```

Exit codes: `0` clean (no guarded files, or guarded + predeclared); `1` blocked;
`2` usage error (e.g. registry not found).

## Wiring as a git `commit-msg` hook

The gate needs the commit message, which is only available at the **commit-msg**
stage. Install a local hook (not tracked; each clone opts in):

```bash
cat > .git/hooks/commit-msg <<'SH'
#!/usr/bin/env sh
# $1 is the path to the commit message file.
git diff --cached --name-only \
  | python scripts/check_scorer_edit_predeclaration.py --stdin --message-file "$1"
SH
chmod +x .git/hooks/commit-msg
```

## Wiring in CI (PR-body check)

Add a step to a pull-request job that passes the PR body as the message and the PR
file list as stdin. Sketch for a GitHub Actions step (the repo CI lives in
`.github/workflows/ci.yml`; add under a `pull_request`-triggered job):

```yaml
      - name: Scorer-edit predeclaration gate
        if: github.event_name == 'pull_request'
        env:
          PR_BODY: ${{ github.event.pull_request.body }}
        run: |
          git fetch origin "${{ github.base_ref }}" --depth=1
          git diff --name-only "origin/${{ github.base_ref }}...HEAD" \
            | python scripts/check_scorer_edit_predeclaration.py --stdin --message "$PR_BODY"
```

### Why not a `.pre-commit-config.yaml` line?

The existing pre-commit hooks run at the **pre-commit** stage, which receives
staged *filenames* but not the commit message. This gate's value is the *message*
check, so a one-line addition to the existing `- repo: local` block would not have
the input it needs. The `commit-msg` git hook above (or the CI step) is the correct
seam. This is a deliberate documentation-over-hook choice per the Phase-4 plan.

## When the gate blocks you

- **Real measurement change:** predeclare it in `experiments/hypothesis_registry.jsonl`
  (add an OPEN entry with a `hypothesis_id`, statement, and kill criterion), run the
  dev140 replay, and cite both in the commit/PR message. Then regenerate the affected
  dossier via `experiments/exectv2_ledger/render_dossier.py` (never hand-edit) and
  update every citation of the moved number.
- **Pure refactor, no scored-number change:** the discipline still applies — say so
  explicitly and reference a `hypothesis_id` tracking that assertion plus a dev140
  *no-change* replay. A refactor that "cannot" move a number is exactly the case the
  seed defect masqueraded as.

## Related guardrails

- `tests/test_scorer_scope_invariants.py` — the clause-scope property tests (the
  seed defect encoded as a general invariant, per family).
- `tests/test_scorer_projection_consistency.py` — scorer <-> projection scope
  reconciliation test.
- `experiments/exectv2_ledger/mechanism.py` — the shared mechanism/verdict taxonomy
  future digs must extend (rather than adding a bespoke local script).
