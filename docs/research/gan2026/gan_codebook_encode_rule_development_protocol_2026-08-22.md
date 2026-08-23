# Gan codebook-extract encode-rule development protocol

Date: 2026-08-22
Status: completed
Owner: this file
Result:
[Gan codebook-extract encode-rule development](gan_codebook_encode_rule_development_2026-08-22.md)

## Question

On Gan `dev750`, what deterministic encode policy is justified after
`gan_llm_extract` has already attempted to write a Gan codebook
label?

The primary comparison is the current `llm_encode` replay against a candidate
that treats a parsed model label as the fact to encode rather than re-extracting
an answer from its selected evidence. The study asks which current rewrites are
format repairs, which are safe same-fact encodings, and which duplicate
extraction or selection.

## Why it matters

The selected-evidence renderer was built for a source-near model output. On the
codebook extract it changes 71 of 748 parsed labels, producing 22 Purist rescues
and five harms. All 71 changes are attributed to
`gan.render.selected_evidence`. The encode boundary must be reconsidered before
this ruleset is treated as the deterministic encode cell.

## Data and inspection policy

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 synthetic data |
| Split | `dev750` (`gan2026_split_v1` validation) |
| Row policy | Development inspection permitted |
| Locked split | Do not load or inspect `test450` |
| Saved extract | `experiments/paper/gan_llm_extract/gemini37flash/dev750/rows.jsonl` |
| Model | Gemini 3.7 Flash |
| Prompt/program | `gan_llm_extract` |
| Call mode | Saved-output deterministic replay; no model calls |
| Scorer | Gan Purist accuracy; secondary Pragmatic accuracy and scorable count |

The two extract parse failures remain incorrect in every arm. Raw synthetic
note text may appear only in the development diagnostic artifact, marked
`data_text_policy: synthetic_development_raw_text_diagnostic`.

## Fixed arms

1. **Extract identity**: parsed `selection.final_label`, with no encode rewrite.
2. **Format-only**: benchmark-compatible spelling and syntax repair that
   preserves the selected fact.
3. **Current rule encode**: `StructuredRepairConfig.for_mode("llm_encode")`.
4. **Candidate rule encode**: independently switchable rules supported by the
   row analysis.

Every arm uses the same saved raw output and source-row indices. Encode may not
change `selected_event_ids`, choose a different event, add a fact, or use
`test450`. A change in sentinel state, frequency category, denominator/window,
cluster meaning, or selected fact is recorded as semantic deterministic repair,
not format repair, even if it remains an experimental candidate.

## Required error analysis

The machine artifact must include all 750 rows and, for each parsed row:

- source-row index, gold label and categories;
- model label, format-only label, current-rule label, and candidate label;
- selected event ids, exact selected evidence, and evidence validity;
- parsed kind and Purist/Pragmatic result for each arm;
- current-rule before/after hops and rule-family attribution;
- mutually interpretable failure and change buckets;
- synthetic note text for this development diagnostic only.

The report must separately account for:

- current-rule rescues, harms, changed-but-category-neutral rows, and unchanged
  residual errors;
- already-parsed model labels versus unparsed labels;
- changes of sentinel state, frequency family, denominator/window, count,
  cluster structure, and format only;
- first-failure ownership: extract, encode, select/revision, or scorer/gold
  convention.

## Candidate and ablation policy

Start with the smallest policy implied by the mechanism:

- preserve an already parsed codebook label unless a named candidate rule has
  positive evidence for changing it;
- test strict format-only repair separately from evidence-derived semantic
  repair;
- give every candidate rule a stable id, focused tests, an isolated arm, and a
  leave-one-out result;
- audit every changed `dev750` row, including raw-correct to candidate-wrong
  regressions;
- reject score-positive rules that depend on row identity, gold labels, hidden
  split membership, or benchmark-specific phrase memorization without a
  defensible general rule.

No aggregate gain is sufficient by itself. The frozen candidate must report
wrong-to-correct and correct-to-wrong counts, predicted-kind changes,
selected-event-id changes, and each rule's isolated and leave-one-out effect.

## Artifacts

Write machine-readable development evidence under
`experiments/gan_codebook_encode_rule_development_20260822/`:

- `rows.jsonl`: all-row mechanism ledger;
- `changes.jsonl`: every candidate-changed row;
- `summary.json`: arm scores, buckets, ablations, and rule counts;
- `residuals.jsonl`: non-correct frozen-candidate rows with first-failure
  ownership where inspection supports it.

## Stop rule and claim boundary

Stop when all current-rule changes are classified, every accepted candidate
rule has been ablated and audited, and the remaining errors have been assigned
to a first component or explicitly marked unresolved. A negative result is
allowed: if no evidence-derived rewrite survives the encode boundary and
regression audit, freeze format-only or identity behavior as the encode answer.

The result is inspected development evidence on one saved Gemini raw
distribution. It is not holdout evidence, clinical validation, or permission
to update the locked five-cell grid. Any future holdout run requires a new
frozen protocol and must remain aggregate-only.
