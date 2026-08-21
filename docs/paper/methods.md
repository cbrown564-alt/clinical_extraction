# Paper methods

Date: 2026-08-17
Revised: 2026-08-20 (five rungs of rule help; `gan_llm_only` is not a results column)
Status: current
Owner: this file

Two tasks. The proposed method translates clinic letters into structured
facts in a designed form, with quoted source text. Rule help is a
depth axis, not an on/off hybrid switch. Scores are not interchangeable
across tasks.

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Question | One current seizure-frequency label | Complete diagnosis, frequency, prescription, and investigation inventory |
| Development | `dev750` | `dev140` |
| Locked test | `test450` (aggregate-only) | `test60` (aggregate-only) |
| Primary score | Purist accuracy | Four-family clinical fact F1 |

Clinical fact F1 is the project's research metric for ExECT. It is
not the published ExECT benchmark.

## The proposed method

The method translates a clinic letter into structured clinical facts in
a designed form, with quoted source text. One model call returns a
structured ledger. Recorded rules then shape that ledger into the
required form. Saved model output can be replayed through those rules
without a new call.

This paper evaluates two designed forms using public golds. Other forms
are a design property, not a third evaluated task.

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Letter | One clinic letter | One clinic letter |
| What the model collects | Frequency events with source text, and a first pick of the current state | Four-family facts with source text |
| What rules may then do | Override the pick, render the designed dialect, check that the quote is in the letter | Map families to dictionaries, drop unsupported states, check that each finding has a quote |
| Submitted answer | One canonical frequency label | One de-duplicated fact inventory |
| How this paper scores it | Label mapped to a monthly Purist band | Four-family clinical fact F1 |

On Gan the living request for rungs 2–4 is `gan_llm_with_rules`:
the model extracts events and makes a first pick. Rules may later
render or switch that pick. Rungs 2–4 share one saved `raw_output`.
Rung 5 is a new Gan request that also puts those deterministic
candidates in the prompt. `gan_llm_only` is a different prompt. It is
not a results column.

On ExECT, rungs 2–4 replay `exect_llm_only` `raw_output`. Rung 5 is
the living `exect_llm_pre_post` request, which already suggests
candidates before generation. `exect_llm_with_rules` is the live
alias for that request. An unrepaired hybrid answer is not
rung 2.

The paper records every submitted-answer version as a hop log. A
derived state graph is optional. A recorded hop is not a clinically
correct step.

The paper uses these change classes consistently:

- **Format change:** changes serialization without changing the represented
  clinical fact.
- **Semantic change:** changes the selected event or state, concept, attribute,
  multiplicity, evidence acceptance, or unknown status.
- **Score projection:** converts the submitted answer to the unit the
  benchmark scores. It can discard distinctions without changing the
  submitted answer.

A folded step is not described as visible unless a saved artifact
records it. A visible step is not described as clinically correct.

## Identities

Headline columns are the five rungs. Same names on both tasks.
Scores stay task-specific. The plain-language owner, with one
development letter on each task, is
[five rungs of rule help](../research/paper/five_rungs_of_rule_help_2026-08-20.md).

| Rung | Identity | Gan | ExECT |
| --- | --- | --- | --- |
| 1 `rules_only` | `gan_rules` / `exect_rules` | No model | No model |
| 2 `llm_schema` | replay `gan_llm_with_rules` `raw_model` / replay `exect_llm_only` `source_scored` | JSON and schema only. Score the model's own label | Parsed mentions. Score raw clinical-fact keys |
| 3 `llm_format` | replay `selected_evidence_derivation` / `format_only` stop | Label-dialect render. Must not switch the selected event | Serialization stop before dictionary rewrite |
| 4 `llm_post` | `gan_llm_with_rules` `hybrid_full_stack` / `exect_llm_only` full assembly | Full clinical post stack | Family transforms and producer checks |
| 5 `llm_pre_post` | `gan_llm_pre_post` / `exect_llm_pre_post` | New request: suggested candidates in the prompt, then the same post stack | Living hybrid request. Cite hybrid F1 |

`gan_llm_only` remains a live runner for existing cells. It is not a
results column. Do not use it as rung 2 or 3.

The living ExECT model methods are `exect_llm_only` and
`exect_llm_pre_post` (`exect_llm_with_rules` is the live alias of
pre-post). There is no Full-ledger method or comparison arm.

E5 and Compact are lineage labels, not living method names. See
[lineage](lineage.md).

## Roster

Grok 4.6 is the cited model, so the story stays on the method.
Companion rows, where their cells exist: GPT-5.6 Luna, Gemini
3.7 Flash, DeepSeek V4 Flash 0731, Qwen 3.8 27B, Gemma 4 26B.
GPT-5.6 Sol is historical. Gemini is in the same band as Grok
where both cells exist.

Machine roster: [`paper_experiments/roster.json`](../../paper_experiments/roster.json).

## Cells

Replayable paper numbers live under `paper_experiments/`. Holdout
files keep only replay keys. A later Gan `test450` rung replay of
saved `gan_llm_with_rules` raw writes aggregate `comparison.json`
only. Do not inspect `test450` or `test60` rows.

Missing cells and the only allowed new runs are listed in
[the scope](../plans/paper_final_repo_scope_2026-08-17.md).
