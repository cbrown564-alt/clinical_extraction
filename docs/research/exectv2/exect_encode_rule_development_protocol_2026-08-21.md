# ExECT encode-rule development protocol

Date: 2026-08-21
Status: completed 2026-08-22
Owner: this file

## Question

On ExECTv2 `dev140`, which same-fact rewrites made by the saved Gemini
`exect_llm_encode` call are missing from the deterministic encode stack, and can
general deterministic rules recover those rewrites without adding, dropping,
merging, or clinically reselecting mentions?

The study matters because both arms start from the saved
`exect_llm_only/gemini37flash/dev140` mention list. At protocol time, the
current deterministic encode replay was read as 0.8011 clinical-fact F1 and the
saved Gemini encode as 0.8545. The audit found that those readings came from
different scorers. The permissive result scorer was subsequently retired. The
completed study and all current result paths use the exact per-letter,
per-family `clinical_headline_unit_keys` scorer; the result report gives the
aligned comparison.

## Data and inspection policy

| Item | Value |
| --- | --- |
| Dataset | ExECTv2 |
| Split | `dev140` (`exectv2_split_v2` development partition) |
| Row policy | Development row inspection permitted |
| Locked split | `test60`; do not inspect or tune on its rows |
| Saved extract source | `paper_experiments/exect/exect_llm_only/gemini37flash/dev140/structured.jsonl` |
| LLM encode diagnostic | `experiments/paper/exect_llm_encode/gemini37flash/dev140/rows.jsonl` |
| Model | `gemini/gemini-3.7-flash` |
| Prompt/program | `exect_llm_encode`, schema `paper.exect_llm_encode.v1` |
| Call mode | Saved-output inspection and deterministic replay; no new model calls |
| Starting commit | `0dcb68aa0d2b066a9fa5f626a89986897643bc3c` with unrelated untracked files present |

## Candidate and comparator

The fixed comparator is the current `apply_format_stack` result on the saved
extract mentions. It performs evidence copy/whitespace repair, removes model
CUIs, repairs legal attributes, formats each family, and calls `project_cuis`.

The candidate may extend only same-fact encode behavior. Allowed changes are:

- map an extracted name or alias to the existing closed ExECT name list;
- normalize an already-extracted dose, unit, schedule, count, period, date,
  result, status, or category from the mention text, attributes, or exact
  evidence on that row;
- attach the corresponding codebook identifier after the name is canonical;
- remove an attribute that is not supported by that mention's own text or
  evidence when removal does not change the selected clinical fact.

The candidate must preserve mention count, mention identity, family, and exact
evidence. A rule that adds, drops, splits, merges, retargets, or changes the
clinical assertion is selection/revision and is out of scope for this study.

## Score and audits

Primary score: four-family clinical-fact micro-F1 from
`clinical_headline_unit_keys`. Secondary scores: family F1, true/false
positive and false-negative counts, per-letter family exactness, and the number
of comparator-correct letter/family pairs damaged by the candidate.

The LLM output is diagnostic, not the candidate. Row inspection starts with
mention-level cases where LLM encode changes a comparator key toward gold, then
checks all gold misses that still have the essential name and operands in the
extract mention or its exact evidence. Every proposed rule must be checked
against every dev140 row it changes, including cases where the current rule
encoding or raw extraction is already correct.

Required ablations:

1. current deterministic encode;
2. each new named rule family alone;
3. the cumulative candidate;
4. saved Gemini encode on the same raw mentions as a diagnostic ceiling, not an
   ablation of deterministic code.

## Machine-readable artifact

Write the development artifact under
`experiments/exectv2_encode_rule_development_20260821/` before the narrative
report. Preserve one record per letter, family, mention, and changed component
decision where possible, with:

- letter id, family, mention id, exact evidence, and evidence-validity status;
- extract, comparator, Gemini-encode, candidate, and gold scorer keys;
- rule id and before/after mention payload;
- comparator and candidate match counts;
- wrong-to-correct, correct-to-wrong, and first-failure owner;
- whether all required operands were already present in the extract row;
- dataset, split, scorer, prompt/program, model, replay state, and commit.

The summary must include all candidate-changed letter/family pairs, exact
evidence accounting, deterministic-correct regression count, and results by
family and rule id.

## Test and iteration policy

Write a small failing test before each rule family. Prefer hand-built mentions
that pin the same-fact boundary. Add a raw-correct regression case for every
broad alias or evidence parser. Iterate on `dev140`; this is development, so
the resulting score is not independent evidence. Do not run new model calls.

## Stop rule and claim boundary

Stop when at least three material, independently ablatable encode-rule families
have been tested and either accepted or rejected, all changed dev140 rows have
been audited, and remaining LLM gains have been classified as encodeable,
missing extraction operands, or semantic selection.

A positive result is a development answer for the frozen Gemini
`exect_llm_only` raw distribution and the ExECT clinical-fact scorer. It may
support a transfer hypothesis for the same-fact rules. It is not holdout
evidence, clinical validation, or permission to report a new `test60` result.

## Initial completion (superseded by the extension)

Four independently stoppable rule families were accepted in the first pass. On the exact rung
scorer, the deterministic encode result increased from 0.8019 to 0.8469 and
the saved Gemini encode scored 0.8210 on the same extract rows. All candidate
key changes were non-worsening by false-positive-plus-false-negative count; 15
letter/family pairs became exact and none became non-exact. See the
[development result](exect_encode_rule_development_2026-08-22.md) and its
machine-readable artifacts. `test60` was not loaded or inspected.

## Exhaustive extension: 2026-08-22

The first completion answered the saved-Gemini delta question but did not
classify every residual error. The study is therefore reopened for one bounded
extension with this primary question:

> Of the candidate's remaining 164 false-negative and 66 false-positive exact
> clinical-fact units on Gemini `dev140`, which still have the necessary fact
> and operands in the extracted mention or its exact evidence and can be fixed
> by a general same-fact encode rule?

The comparator, candidate boundary, exact scorer, model-call policy, and split
policy above remain fixed. The extension adds these required artifacts and
checks:

1. one residual record for every non-exact letter/family pair, including the
   full missing and excess key multisets, extract/candidate mentions, exact
   evidence status, and first-failure classification;
2. an accounted total in which every remaining FP and FN unit is assigned to
   encode, extract, select/revision, scorer/gold convention, or unresolved;
3. focused failing tests before any additional rule;
4. an audit of every row changed by an accepted rule, including partial harms
   where the comparator was already non-exact;
5. after the rule set is frozen on Gemini, no-call transfer replays on every
   available saved `exect_llm_only` `dev140` model distribution, with no tuning
   from `test60` and no overwrite of promoted paper artifacts;
6. a strict post-change review of rule ownership, hidden semantic changes,
   evidence validity, reproducibility, and maintainability.

The extension stops only when all residual units are classified, no further
safe encode rule is supported by the permitted rows, all accepted rules remain
independently stoppable, and cross-model development behavior is recorded. A
positive transfer result remains development evidence, not holdout validation.

## Final completion

The extension accepted seven independently switchable rules across Diagnosis,
Prescription, SeizureFrequency, and Investigations. Exact clinical-fact F1 on
the frozen Gemini raw mentions increased from 0.8000 to 0.8570; saved Gemini
LLM encode scored 0.8176 on the same rows. Of 49 changed letter/family key
sets, 42 improved and seven were neutral; none worsened, and no
comparator-exact set regressed.

The frozen rules improved all nine available saved dev140 raw distributions
with no changed family classified worse. The residual ledger accounts for all
214 remaining exact error units: 60 extraction, 104 selection/revision, and 50
scorer/gold-convention units, with zero safe encode and zero unresolved units.
The strict review removed a rescue-prescription exception that depended on
row-level rescue multiplicity rather than the fact itself. `test60` was not
loaded or inspected. See the [development result](exect_encode_rule_development_2026-08-22.md)
and machine-readable artifacts.
