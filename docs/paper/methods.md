# Paper methods

Date: 2026-08-17
Revised: 2026-08-21 (five cells: two producers + encode/revise; not five depths)
Status: current
Owner: this file

Two tasks. The proposed method translates clinic letters into structured
facts in a designed form, with quoted source text. The five reported
cells are two producers, one replay stack (schema / encode / revise),
and one optional prompt treatment — not five depths of one hybrid
switch. Scores are not interchangeable across tasks.

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

The paper uses these change classes consistently (plain-language owner:
[five rungs](../research/paper/five_rungs_of_rule_help_2026-08-20.md)):

- **Dialect:** same-fact writing (units, brand→generic, word numbers).
- **Encode:** codebook / designed form / Gan selected-evidence renderer;
  does not pick a different fact. ExECT format-replay includes CUI attach.
- **Revise (semantic):** may change facts under recorded policy — gate,
  rewrite, reselect, invent (overwrite is one kind, not the definition).
- **Score projection:** converts the submitted answer to the unit the
  benchmark scores. It can discard distinctions without changing the
  submitted answer.

A folded step is not described as visible unless a saved artifact
records it. A visible step is not described as clinically correct.

## Identities

Headline columns are the five reported cells. Same names on both tasks.
Scores stay task-specific. The plain-language owner, with one
development letter on each task, is
[five rungs of rule help](../research/paper/five_rungs_of_rule_help_2026-08-20.md).

| Rung | Identity | Gan | ExECT |
| --- | --- | --- | --- |
| 1 `rules_only` | `gan_rules` / `exect_rules` | Other producer; no model; different rule set | Other producer; no model; different rule set |
| 2 `llm_schema` | replay `gan_llm_with_rules` `raw_model` / replay `exect_llm_only` `source_scored` | Parsed ledger; already writes a label (`_normalize_event` / `_resolve_final_label` leak) | Parsed mentions. Score raw clinical-fact keys |
| 3 `llm_encode` | replay `llm_encode` / `format_only` stop | Encode: selected-evidence renderer into evaluation form; must not switch the selected event | Encode: same-fact writing including `project_cuis` on encode-replay; not concept rewrite |
| 4 `llm_revise` | `gan_llm_with_rules` `llm_revise` / `exect_llm_only` full assembly | Revise: full clinical revise may change facts | Revise: family transforms, gates, producer checks |
| 5 `llm_pre_post` | `gan_llm_pre_post` / `exect_llm_pre_post` | Other request: candidates in the prompt, then the same post stack | Living hybrid request. Cite hybrid F1. Do not score that raw as rung 2 |

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
