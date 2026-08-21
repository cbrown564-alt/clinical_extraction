# Rules for changing an ExECT scorer

Scoring, final formatting, and lexicon code determine what the project measures.
A change can move a reported number without changing extraction. Before such a
change is committed, state a hypothesis and replay dev140.

`scripts/check_scorer_edit_predeclaration.py` checks changed paths and a commit
or pull-request message. When protected code changes, the message must name a
`hypothesis_id` from `experiments/hypothesis_registry.jsonl` and mention a
dev140 replay, rescore, or rerun. Exit codes are 0 for pass, 1 for missing
evidence, and 2 for invalid use.

When the check fails:

1. add an `OPEN` hypothesis with a stop rule and intended dev140 replay;
2. run the replay and record whether the expected score moved;
3. cite the hypothesis and result in the commit or pull request;
4. update selected evidence only through a repeatable producer.

If no producer exists, keep the selected file unchanged. Refactors follow the
same rule: state the expected no-change result and verify it on dev140.

Related tests: `test_scorer_scope_invariants.py` and
`test_scorer_projection_consistency.py`.
