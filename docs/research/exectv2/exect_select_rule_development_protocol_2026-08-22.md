# ExECT Select-rule development protocol

Date: 2026-08-22  
Status: completed on development data; holdout remains sealed

## Primary question

Which additions or corrections to the deterministic ExECT Select rules recover
source-supported clinical facts on the frozen Gemini `dev140` extract
distribution without damaging a letter/family result that the current Select
stack gets exactly right?

This matters because Select is the semantic stage: it may gate, drop, merge,
split, rewrite, reselect, or add a fact, but every decision must remain
attributable to a named rule and exact source evidence. The completed Encode
study classified 104 residual error units as Select/revision work. This study
tests those opportunities rather than allowing them to leak back into
same-fact formatting.

## Data and inspection policy

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` (`exectv2_split_v2` development partition) |
| Row policy | Development row inspection permitted |
| Locked split | `test60`; do not load, inspect, or tune on its rows |
| Saved extract source | `experiments/paper/exect_llm_encode/gemini37flash/dev140/rows.jsonl`, field `extract_mentions` |
| Saved LLM Select source | `experiments/paper/exect_llm_select/gemini37flash/dev140/rows.jsonl` |
| Model | `gemini/gemini-3.7-flash` |
| Model programs | diagnostic `exect_llm_encode` and `exect_llm_select`, schema `paper.exect_llm_select.v1` |
| Call mode | Saved-output inspection and deterministic replay; no new model calls |
| Starting commit | `0dcb68aa0d2b066a9fa5f626a89986897643bc3c`, with the in-progress Encode study and unrelated user changes present |

## Candidate, comparator, and score layers

The primary comparator is the current deterministic Select stack applied after
the accepted deterministic Encode rules to the saved Gemini extract mentions.
The candidate may add only independently switchable Select rules.

The primary score ladder is:

1. saved model extract mentions;
2. accepted deterministic Encode output;
3. current deterministic Select comparator;
4. deterministic Select candidate;
5. exact clinical-fact scorer.

Two diagnostic ladders are required:

- saved Gemini Encode → saved Gemini Select, to identify model-positive and
  model-negative selection decisions;
- saved Gemini Encode → current/candidate deterministic Select, so model and
  rule selection can be compared from identical encoded mentions.

The saved Gemini Select output is diagnostic and is not an ablation of the
deterministic candidate.

## Component and rule boundary

Select owns semantic decisions over facts already present in an extracted row
or explicit source evidence. Allowed rule effects are:

- gate or drop a non-fact, unsupported, pending, historical, planned, or
  duplicate mention;
- merge or split mentions when exact evidence shows the same or distinct
  clinical facts;
- rewrite or reselect the clinical concept when the source explicitly supports
  the target and the change is not merely a closed-name rendering;
- add a fact from an exact, bounded source pattern when the rule records
  invention ownership and its portability category;
- resolve competing temporal, family, event, or regimen ownership.

Every rule must declare one of `general`, `clinical_epilepsy`,
`seizure_frequency`, or `benchmark_format`. Benchmark-format rules must not be
described as clinical reasoning. Rules may not use gold labels, letter ids, or
development-row multiplicity as inputs.

Encode remains fixed during the primary experiment. Same-fact spelling,
standard-name rendering, CUI attachment, and operand formatting are out of
scope unless a failing Select test proves that the clinical decision itself
changes.

## Scorer and audits

Primary score: four-family clinical-fact micro-F1 from exact multiset
`clinical_headline_unit_keys`, evaluated per letter and family. Secondary
measures are family F1, TP/FP/FN, exact letter/family count, changed-row error
direction, comparator-exact regressions, and exact-evidence validity.

Required row-level analyses:

- every current Select change from deterministic Encode;
- every candidate change from the current comparator;
- every saved Gemini Select change from its saved Encode input;
- wrong-to-correct, correct-to-wrong, and partially improved or harmed cases;
- the first component that changes the scorer key;
- remaining errors classified as Extract, Encode, Select, scorer/gold
  convention, or unresolved.

## Required ablations and hard checks

1. deterministic Encode with no Select;
2. current deterministic Select;
3. each new named Select rule alone on top of the current comparator;
4. the cumulative Select candidate;
5. the candidate with each accepted rule removed;
6. saved Gemini Select on saved Gemini Encode;
7. current and candidate deterministic Select on saved Gemini Encode;
8. no-call replay of the frozen candidate across every available saved
   `dev140` raw-output distribution after rule development is complete.

Every accepted rule must have a focused failing pytest first and at least one
raw-correct or near-neighbour regression case. Broad rules require inspection
of every changed development row.

## Machine-readable artifacts

Write artifacts under
`experiments/exectv2_select_rule_development_20260822/` before the narrative
result. Preserve one record per meaningful letter/family decision, including:

- dataset, split, row policy, letter id, family, scorer, model, program, and
  replay state;
- exact source evidence and evidence-validity status;
- extract, deterministic Encode, comparator Select, candidate Select, Gemini
  Encode, Gemini Select, and gold keys;
- rule ids, action class, portability, before/after mention payloads, and first
  changing component;
- TP/FP/FN deltas, exact rescue/regression flags, required-operand status,
  parse/call/fallback events, and residual owner.

The summary must include the git commit and dirty-tree note, dependency
versions, input paths and counts, exact scorer identity, rule ablations,
changed-row precision, evidence accounting, comparator-correct regressions,
family and hidden-decision breakdowns, and transfer replay results.

## Stop rule and claim boundary

Stop when all current and saved-Gemini Select changes and all candidate-changed
rows are classified, the candidate is independently ablatable, remaining
errors are assigned to an owner, and no further source-supported portable
Select rule is justified by the permitted rows. A rule is rejected when its
gain depends on gold labels, row ids, batch multiplicity, unsupported source
inference, or unacceptable comparator-correct damage.

A positive result is a development answer for the named saved `dev140`
distributions and exact ExECT clinical-fact scorer. Cross-model no-call replay
may support a bounded transfer hypothesis. It is not holdout evidence,
clinical validation, or permission to inspect or update `test60`.

## Completion record

The study accepted seven rules and rejected one. The combined candidate moves
the current deterministic Select comparator from 0.8703 to 0.9001 exact
clinical-fact F1. All 28 changed letter/family pairs improve, 22 become exact,
and no comparator-exact pair regresses. No-call transfer improves the aggregate
score on all nine saved development distributions. The result and limitations
are reported in
[ExECT Select-rule development on dev140](exect_select_rule_development_2026-08-22.md).
