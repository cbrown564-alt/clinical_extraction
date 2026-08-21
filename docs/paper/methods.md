# Paper methods

Date: 2026-08-17
Revised: 2026-08-21 (headline is four methods × three stages)
Status: current
Owner: this file

Two tasks. The proposed method translates clinic letters into structured
facts in a designed form, with quoted source text. The headline table is
four methods — **Rules**, **LLM**, **LLM then rules**, **Rules then
LLM** — against stages **extract**, **encode**, and **select**. It is
not five depths of one hybrid switch. Scores are not interchangeable
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
| What rules may then do | Override the pick from extracted events only, render the designed dialect, check that the quote is in the letter. Living hybrid select does not mine the letter for leftover dates, clinic-month diary assignment, residual jerk, or elapsed-window conversion. | Map families to dictionaries, drop unsupported states, check that each finding has a quote. Living hybrid select does not add leftover letter-scan findings after the call. |
| Submitted answer | One canonical frequency label | One de-duplicated fact inventory |
| How this paper scores it | Label mapped to a monthly Purist band | Four-family clinical fact F1 |

On Gan, **LLM then rules** is `gan_llm_with_rules`: extract, encode,
and select are the three stops on that raw. **Rules then LLM** is
`gan_llm_pre_post`: the same three stops on that other raw.
**LLM** is later-stage encode and select on the frozen
`gan_llm_with_rules` extract ledger. `gan_llm_only` is a third
prompt. It is not a results column.

On ExECT, **LLM then rules** is `exect_llm_only` replayed at
extract / encode / select. **Rules then LLM** is
`exect_llm_pre_post` (`exect_llm_with_rules` is the live alias)
replayed at those same stops. An unrepaired `*_pre_post` body is
the extract stop, not the select stop.

The paper records every submitted-answer version as a hop log. A
derived state graph is optional. A recorded hop is not a clinically
correct step.

The paper uses these change classes consistently (plain-language owner:
[five rungs](../research/paper/five_rungs_of_rule_help_2026-08-20.md)):

- **Extract:** collect facts and quotes. The model's written label or
  mentions. Parse is code.
- **Encode:** same facts, designed form (units, brand→generic, word
  numbers, codebook attach, Gan selected-evidence renderer, resolve a
  blank Gan label). Does not pick a different fact.
- **Select:** may change facts under recorded policy. Shared kinds on
  both tasks: **gate** (withhold or block), **drop** (remove a
  submitted fact), **rewrite** (change the meaning of a kept fact),
  **reselect** (change which extracted fact is current), **invent**
  (add a residual fact).
- **Score projection:** converts the submitted answer to the unit the
  benchmark scores. It can discard distinctions without changing the
  submitted answer.

A folded step is not described as visible unless a saved artifact
records it. A visible step is not described as clinically correct.

## Identities

The headline is four methods × three stages. Same names on both
tasks. Scores stay task-specific. The plain-language owner is
[five rungs of rule help](../research/paper/five_rungs_of_rule_help_2026-08-20.md).

| | Extract | Encode | Select |
| --- | --- | --- | --- |
| **Rules** | `gan_rules` / `exect_rules`. Same submitted answer in all three columns. No model. This rule set is not the encode/select stack on a model ledger. | same | same |
| **LLM** | Frozen extract ledger only (parsed `gan_llm_with_rules` / `exect_llm_only`). | Gan: Gemini later-stage `gan_llm_encode`. ExECT later-stage encode is still empty. | Gan: Gemini later-stage `gan_llm_select`. ExECT later-stage select is still empty. |
| **LLM then rules** | `gan_llm_with_rules` / `exect_llm_only` at extract (raw model label / flatten). | The same raw at rule encode. | The same raw at rule select. |
| **Rules then LLM** | `gan_llm_pre_post` / `exect_llm_pre_post` at extract. | The same raw at rule encode. | The same raw at rule select. |

`gan_llm_only` remains a live runner for existing cells. It is not a
results column. Do not use it as llm extract.

The living ExECT model methods are `exect_llm_only` and
`exect_llm_pre_post` (`exect_llm_with_rules` is the live alias of
pre-post). There is no Full-ledger method or comparison arm.

E5 and Compact are lineage labels, not living method names. See
[lineage](lineage.md).

## Roster

Gemini 3.7 Flash is the cited model, so the story stays on the
method. Companion rows, where their cells exist: Grok 4.6, GPT-5.6
Luna, DeepSeek V4 Flash 0731, Qwen 3.8 27B, Gemma 4 26B. GPT-5.6
Sol is historical. Later-stage LLM encode and LLM select calls
(`gan_llm_encode`, `gan_llm_select`, and the ExECT pair) are Gemini
only. See [Gemini is the cited model](decisions/gemini-is-the-cited-model.md).
Gan later-stage prompt contract:
[Gan later-stage encode and select prompts](decisions/gan-later-stage-encode-select-prompts.md).
ExECT later-stage prompt contract:
[ExECT later-stage encode and select prompts](decisions/exect-later-stage-encode-select-prompts.md).

Machine roster: [`paper_experiments/roster.json`](../../paper_experiments/roster.json).

## Cells

Replayable paper numbers live under `paper_experiments/`. Holdout
files keep only replay keys. A later Gan `test450` rung replay of
saved `gan_llm_with_rules` raw writes aggregate `comparison.json`
only. Do not inspect `test450` or `test60` rows.

Missing cells and the only allowed new runs are listed in
[the scope](../plans/paper_final_repo_scope_2026-08-17.md).
