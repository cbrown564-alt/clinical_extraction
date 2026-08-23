# Three variables: stage ownership, model, and thinking

Date: 2026-08-23
Status: working results draft; not a cited table owner
Owners: [methods](../../paper/methods.md),
[claims](../../paper/claims.md),
[Gan five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md),
[ExECT cell 4](../exectv2/exect_rule_select_after_llm_encode_2026-08-22.md)
Related: [source-near extract and separate encode](gan_source_near_vs_bundled_encode_2026-08-23.md)

This is the cross-task results reading. It is not a replacement for
the Gemini five-cell owners. Holdout is aggregate-only. Do not inspect
`test450` or `test60` rows. DeepSeek Gan `test450` is still running.

## The question

Three variables were expected to move the headline score:

1. **Stage ownership** — who runs extract, encode, and select (rules,
   LLM, or both). Extra encode or select work can be a recorded rule
   replay or a later-stage model call.
2. **Model** — Gemini 3.7 Flash, Grok 4.6, GPT-5.6 Luna, DeepSeek V4
   Flash, on the same cell-3 extract (`gan_llm_extract` /
   `exect_llm_only`).
3. **Thinking effort** — Gemini only; low (living), medium, and high,
   on extract only.

The cited score is the select stop. Extract and encode are prior-stage
ablations. Thinking and the source-near Gan request are ablations, not
roster replacements.

## Answer

Thinking changes little once rules encode and select. Model choice
moves the score more than thinking, but only coarsely: Luna is behind;
Gemini, Grok, and DeepSeek (where scored) sit in a tight band. The
best mix is a model extract plus recorded post-processing. The exact
mix differs by task — Gan prefers LLM / rules / rules; ExECT prefers
LLM / LLM / rules — and both beat all-rules and all-model on holdout.
A later-stage model call can add a little more, at a second-call cost.
Rules do the same post-processing job at a better balance of score,
cost, and flexibility: the change is named, and the same raw can be
replayed under a new policy without another extract. Better models
extract better and stay ahead after rules. Rules close much of the
Luna gap; they do not erase it.

## 1. Stage ownership

Gemini 3.7 Flash, locked holdout, select stop. Gan is Purist. ExECT
is clinical-fact F1.

| Extract | Encode | Select | Gan `test450` | ExECT `test60` |
| --- | --- | --- | ---: | ---: |
| rules | rules | rules | 0.73 | 0.79 |
| both | rules | rules | 0.82 | 0.80 |
| LLM | rules | rules | **0.83** | 0.82 |
| LLM | LLM | rules | 0.82 | **0.82** |
| LLM | LLM | LLM | 0.79 | 0.80 |

Gan peak is cell 3 (LLM extract, `gan_rules_encode`, rule select).
ExECT peak is cell 4 (LLM extract, later-stage `exect_llm_encode`,
accepted Select). Both mixed rows beat standalone rules and the
all-model row. The two mixed rows are close; the paper still needs
both, because Gan encode on a codebook extract is not the same hop
as ExECT's later-stage letter-out encode.

Development reverses the all-rules comparison (Gan rules 0.89 vs
Gemini cell 3 0.86; ExECT rules 0.90 vs Gemini cell 3 0.88). The
holdout is the claim.

## 2. Thinking effort (Gemini only)

Same cell-3 extract, then rule encode and rule select. Medium and
high used a 2× output budget. Thinking was not run on later-stage
encode or select.

**Gan `test450` (Purist)**

| Thinking | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| Low (living) | **0.789** (355) | **0.800** (360) | **0.831** (374) |
| Medium | 0.776 (349) | 0.791 (356) | 0.813 (366) |
| High | 0.773 (348) | 0.784 (353) | 0.818 (368) |

**ExECT `test60` (F1)**

| Thinking | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| Low (living) | 0.797 | 0.810 | 0.816 |
| Medium | 0.795 | 0.811 | **0.823** |
| High | **0.801** | **0.819** | 0.820 |

High is the best ExECT extract. Medium is the best ExECT select. The
select band is 0.007. On Gan, low is best at every stop; select
spreads 8 letters. After the pragmatic map, Gan select is 381–383 /
450. Thinking is the weakest of the three variables, and it raises
tokens and latency.

## 3. Model (cell 3)

`gan_llm_extract` already writes the codebook form, so extract and
encode repeat. Select is `llm_select_after_codebook`. ExECT extract
is flatten; encode is same-fact format; select is rule select.

**Gan `test450` (Purist)**

| Model | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | **0.789** (355) | **0.789** (355) | 0.831 (374) |
| Grok 4.6 | 0.784 (353) | 0.784 (353) | **0.842** (379) |
| GPT-5.6 Luna | 0.693 (312) | 0.693 (312) | 0.778 (350) |
| DeepSeek V4 Flash | — | — | — |

DeepSeek Gan holdout is incomplete (73/450 as of this draft).

**ExECT `test60` (F1)**

| Model | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.797 | 0.810 | 0.816 |
| Grok 4.6 | 0.788 | 0.814 | 0.814 |
| GPT-5.6 Luna | 0.764 | 0.792 | 0.801 |
| DeepSeek V4 Flash | **0.803** | **0.824** | **0.821** |

**Gan `dev750` (Purist), same stack** — DeepSeek extract is on disk,
unpromoted.

| Model | Extract | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.781 (586) | 0.781 (586) | 0.865 (649) |
| Grok 4.6 | **0.784** (588) | **0.784** (588) | **0.867** (650) |
| GPT-5.6 Luna | 0.717 (538) | 0.717 (538) | 0.819 (614) |
| DeepSeek V4 Flash | 0.761 (571) | 0.761 (571) | 0.837 (628) |

Luna is the coarse miss. The other three are close after select.
Rules help Luna most (Gan holdout +38 letters, +0.084; ExECT +0.037)
and do not bring it level (Gan select still 0.064 behind Grok; ExECT
select 0.020 behind DeepSeek).

## Efficiency and flexibility

Later-stage LLM encode or select is a second call on every letter.
Thinking medium/high doubles the extract token budget. Rule encode
and select replay the saved extract. That is the cost case for
keeping cell 3 as the six-model row even where cell 4 is a hair
higher on ExECT.

Rules also name the change and can be edited. A new policy reprocesses
the same raw without another extract. The paper may say that. It may
not say a named step is clinically correct, or that a model's internal
reasoning is visible.

## What the paper may say

It may say the three variables were tested, and thinking moved the
least. It may say a model-plus-rules mix beats all-rules and
all-model on holdout, with the peak mix task-specific. It may say
rules are the better encode/select owner when score, cost, and
replay are taken together. It may say model quality shows up most at
extract, and that rules shrink but do not close the Luna gap.

It may not treat DeepSeek Gan holdout as scored. It may not promote
medium or high thinking over living low. It may not treat development
all-rules wins as the holdout result.

## Claim boundary

Working synthesis of already-run cells. Gemini five-cell totals stay
with their owners. Model stage scores are no-call replays of saved
`gan_llm_extract` / `exect_llm_only` raws. Luna and DeepSeek ExECT
`dev140` used the current extract / encode / select surfaces. Gan
Gemini extract replay can sit one letter above the locked identity
stop (354/450). Do not inspect holdout rows. Do not retune from these
bands.
