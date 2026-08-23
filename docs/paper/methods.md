# Paper methods

Date: 2026-08-17
Revised: 2026-08-22 (cell 3 is the six-model row; other extracts are ablations)
Status: current
Owner: this file

Two tasks. The proposed method translates clinic letters into structured
facts in a designed form, with quoted source text. The Gan headline
table is five role rows: each of **extract**, **encode**, and
**select** is **rules**, **LLM**, or **both**. The cited score is the
select stop. Extract and encode stops are prior-stage ablations.
ExECT uses the same five role rows. Neither table is five depths of
one hybrid switch. Scores are not interchangeable across tasks.

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

On Gan, **LLM** extract is `gan_llm_extract`. **both**
extract is `gan_llm_and_rules_extract`. LLM encode means that
extract already wrote the codebook form. LLM-then-rules encode is
`gan_rules_encode`. **LLM** select is
`gan_llm_select_from_extract`. `gan_llm_extract_raw` is the
source-near ablation. `gan_llm_only` is a third prompt. It is not
a results column.

On ExECT, **LLM** extract is `exect_llm_only`. **both** extract is
`exect_llm_pre_post` (`exect_llm_with_rules` is the live alias).
LLM encode is later-stage `exect_llm_encode`. LLM / LLM / rules is
accepted Select on that encode ledger. **LLM** select is later-stage
`exect_llm_select`. An unrepaired `*_pre_post` body is the extract
stop, not the select stop.

The paper records every submitted-answer version as a hop log. A
derived state graph is optional. A recorded hop is not a clinically
correct step.

The paper uses these change classes consistently (plain-language owner:
[five cells](../paper/method_x_stage.md)):

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

Stage boundaries are defined by the replayed rule sets on frozen model
output, not by the live producer's call order. The live producer
interleaves encode and select work where data dependencies require it;
every stage-boundary claim in this paper is scored at a replay stop.

A folded step is not described as visible unless a saved artifact
records it. A visible step is not described as clinically correct.

## Identities

Both tasks are five role rows. Scores stay task-specific. The
plain-language owner is
[five cells of rule help](../paper/method_x_stage.md).

| Extract | Encode | Select | Gan | ExECT |
| --- | --- | --- | --- | --- |
| rules | rules | rules | `gan_rules` | `exect_rules` |
| both | rules | rules | `gan_llm_and_rules_extract`, then rule encode and select | `exect_llm_pre_post`, then rule encode and select |
| LLM | rules | rules | `gan_llm_extract`, then `gan_rules_encode` and rule select | `exect_llm_only`, then rule encode and select |
| LLM | LLM | rules | Same extract; select families only | Same extract; later-stage encode, then accepted Select |
| LLM | LLM | LLM | `gan_llm_select_from_extract` | later-stage `exect_llm_select` |

`gan_llm_only` remains a live runner for existing cells. It is not a
results column. Do not use it as llm extract.

`exect_llm_with_rules` is the live alias of `exect_llm_pre_post`.
E5 and Compact are lineage labels, not method names. See
[lineage](lineage.md).

## Roster and ablations

Gemini 3.7 Flash is the cited model. Headline tables are Gemini
five-cell grids. The cited score is the select stop.

**Six-model comparison (both tasks):** only cell 3 — LLM extract,
rules encode, rules select. Gan extract is
`gan_llm_extract`. ExECT extract is `exect_llm_only`.
Rule encode and rule select replay on that raw. This row is the
roster comparison because the model does one extract and the rules
are fixed. It is not the peak ExECT row (that is LLM encode then
rule select). Companion models: Grok 4.6, GPT-5.6 Luna, DeepSeek V4
Flash 0731, Qwen 3.8 27B, Gemma 4 26B. Sol is historical.

**Thinking ablation (Gemini only):** the same cell 3, at low, medium,
and high thinking. Thinking can change extract only. Do not run a
thinking grid on later-stage encode or select.

**Source-near Gan ablation (Gemini):** `gan_llm_extract_raw` extract
keeps letter wording and scores lower. Rule encode and rule select
recover most of the score. This shows the method can trade source
wording against form alignment. It is not a claim that the softer
extract preserves clinical reasoning. It is not a results column.

**Stage ablations:** extract and encode stops on the cited rows.
Later-stage LLM encode and LLM select stay Gemini only.

Do not present leftover living extracts (`gan_llm_only`, source-near
`gan_llm_extract_raw` as a headline, ExECT producer raw F1) as
primary results.

See [Gemini is the cited model](decisions/gemini-is-the-cited-model.md)
and [six-model roster](decisions/six-model-roster.md).
Gan later-stage prompt contract:
[Gan later-stage encode and select prompts](decisions/gan-later-stage-encode-select-prompts.md).
ExECT later-stage prompt contract:
[ExECT later-stage encode and select prompts](decisions/exect-later-stage-encode-select-prompts.md).

Machine roster: [`paper_experiments/roster.json`](../../paper_experiments/roster.json).

## Cells

Replayable paper numbers live under `paper_experiments/`. Holdout
files keep only replay keys. A later Gan `test450` rung replay of
saved `gan_llm_extract_raw` raw writes aggregate `comparison.json`
only. Do not inspect `test450` or `test60` rows.

Missing cells and the only allowed new runs are listed in
[the scope](../plans/paper_final_repo_scope_2026-08-17.md).
