# Three variables: stage ownership, model, and thinking

Date: 2026-08-23
Revised: 2026-08-29 (Gan rules row 0.72 after three-stage Phase D)
Status: working results draft; not a cited table owner
Owners: [methods](../../paper/methods.md),
[claims](../../paper/claims.md),
[Gan five-cell grid](../gan2026/gan_five_cell_grid_2026-08-22.md),
[ExECT cell 4](../exectv2/exect_rule_select_after_llm_encode_2026-08-22.md)
Related: [source-near find and separate encode](gan_source_near_vs_bundled_encode_2026-08-23.md),
[find then Select vs find-and-select](exect_extract_vs_extract_and_select_2026-08-25.md),
[Grok temperature 0](../gan2026/gan_grok46_temperature_0_2026-08-28.md),
[Gemini temperature 1](../gan2026/gan_gemini37flash_temperature_1_2026-08-28.md)

This is the cross-task results reading. It is not a replacement for
the Gemini five-cell owners. Holdout is aggregate-only. Do not inspect
`test450` or `test60` rows.

## The question

Three variables were expected to move the cited select stop:

1. **Stage ownership** — who runs find, encode, and select (rules,
   LLM, or both). Extra encode or select work can be a recorded rule
   replay or a later-stage model call.
2. **Model** — the six living roster models, on the same cell-3
   find (`gan_llm_extract` / `exect_llm_extract`).
3. **Thinking effort** — Gemini only; low (living), medium, and high,
   on find only.

The cited score is the select stop. Find and encode are prior-stage
ablations. Thinking, temperature 0 versus 1, and the source-near Gan
request are ablations, not roster replacements.

## Answer

Thinking and temperature both move the select stop less than stage
ownership. Temperature signs are mixed across model and split; they
do not justify a living setting other than 0, and they do not predict
a Luna gain or loss if that provider allowed 0. Model choice
moves the score more than those request settings, but only coarsely:
on ExECT inventory holdout Gemini leads, then Grok / DeepSeek / Luna,
then Qwen / Gemma. The best mix is a model find
plus recorded post-processing. On holdout both peaks are LLM / rules /
rules (Gan 0.86; ExECT 0.87 / 0.8674). ExECT cell 4 (later-stage
encode) is 0.86 and does not raise the stop. Both beat all-rules and
all-model on holdout. Rules do the same
post-processing job at a better balance of score, cost, and
flexibility: the change is named, and the same raw can be replayed
under a new policy without another find. Better models find
better and stay ahead after rules. Rules close much of the Luna gap;
they do not erase it.

## 1. Stage ownership

Gemini 3.7 Flash, locked holdout, select stop. Gan is Purist. ExECT
is 4-family micro F1 (`clinical_inventory_unit_keys`).

| Find | Encode | Select | Gan `test450` | ExECT `test60` |
| --- | --- | --- | ---: | ---: |
| rules | rules | rules | 0.72 | 0.77 |
| both | rules | rules | 0.82 | 0.86 |
| LLM | rules | rules | **0.83** | **0.87** |
| LLM | LLM | rules | 0.82 | 0.86 |
| LLM | LLM | LLM | 0.79 | 0.85 |

Gan peak is cell 3 (LLM find, `gan_rules_encode`, rule select).
ExECT peak is cell 3 (find, then rule select). Cell 4
(later-stage encode, then the same Select) is 0.86 and does not
raise the holdout stop. All five ExECT rows use 4-family micro F1.
The paper still needs both mixed
rows, because Gan encode on a codebook find is not the same hop
as ExECT's later-stage letter-out encode.

Development reverses the all-rules comparison on the previous
Compact/headline scorer (Gan rules 0.92 vs Gemini cell 3 0.86;
ExECT rules 0.90 vs Gemini cell 3 0.88). The holdout is the claim.

## 2. Thinking effort (Gemini only)

Same cell-3 find, then rule encode and rule select. Medium and
high used a 2× output budget. Thinking was not run on later-stage
encode or select. The inferential contrast is living low versus
high at the cell-3 select stop; medium is a point estimate. Owner:
[paired `test450` tests](../gan2026/gan_paired_significance_test450_2026-08-29.md).

**Gan `test450` (Purist)**

| Thinking | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Low (living) | **0.789** (355) | **0.800** (360) | **0.831** (374) |
| Medium | 0.776 (349) | 0.791 (356) | 0.813 (366) |
| High | 0.773 (348) | 0.784 (353) | 0.818 (368) |

**ExECT `test60` (Compact/headline F1).** Not the cited inventory cell 3.

| Thinking | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Low (living) | 0.797 | 0.810 | 0.816 |
| Medium | 0.795 | 0.811 | **0.823** |
| High | **0.801** | **0.819** | 0.820 |

High is the best ExECT find. Medium is the best ExECT select. The
select band is 0.007. On Gan, low is best at every stop; select
spreads 8 letters. After the pragmatic map, Gan select is 381–383 /
450. Thinking is the weakest of the three variables, and it raises
tokens and latency.

## 2b. Temperature (Gemini and Grok)

Same Gan cell-3 find, then codebook rule encode and rule select.
Gemini living is temperature 0; the temperature-1 row is a non-promoted
ablation. Grok living is now temperature 0; the temperature-1 row is
the earlier cited Grok cell. Luna stays at 1 because the provider
rejects 0. Select is a no-call `llm_select_after_codebook` replay.

**Gan Purist, temperature 0 versus 1**

| Model | Split | Stop | Temp. 0 | Temp. 1 | Δ (1 − 0) |
| --- | --- | --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | `test450` | Find | 0.789 (355) | 0.778 (350) | −5 |
| Gemini 3.7 Flash | `test450` | Select | 0.831 (374) | 0.824 (371) | −3 |
| Gemini 3.7 Flash | `dev750` | Find | 0.781 (586) | 0.788 (591) | +5 |
| Gemini 3.7 Flash | `dev750` | Select | 0.865 (649) | 0.867 (650) | +1 |
| Grok 4.6 | `test450` | Find | 0.789 (355) | 0.784 (353) | −2 |
| Grok 4.6 | `test450` | Select | 0.838 (377) | 0.842 (379) | +2 |

Gemini select at temperature 0 is the living codebook replay
(374/450). Table 1 still cites 373/450. Grok `dev750` temperature 1
is omitted: those codebook extract raws were overwritten.

The signs flip by model. Holdout select prefers Gemini at 0 and Grok
at 1 by two or three letters. Development select is flat for Gemini.
The holdout select band is smaller than thinking’s 8. Stage ownership on the same Gemini holdout is 0.72
rules versus 0.83 cell 3 (48 letters). Temperature is mixed and
small beside that three-stage allocation. Living temperature 0 for
every model that accepts it is the right default. Luna was not run
at 0; the mixed Gemini/Grok pattern does not predict that Luna
would rise or fall if the provider allowed it.

## 3. Model (cell 3)

Gan find is `gan_llm_extract`. Encode and select are codebook
rule replays on that raw (`gan_rules_encode` /
`llm_select_after_codebook`). ExECT find is flatten; encode is
same-fact format; select is rule select.

**Gan `test450` (Purist).** Sources:
`paper_experiments/gan/rungs/{slug}/test450/comparison.json` on
promoted `gan_llm_extract`. Grok temperature is 0.

| Model | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | **0.789** (355) | 0.800 (360) | 0.831 (374) |
| Grok 4.6 | **0.789** (355) | **0.811** (365) | **0.838** (377) |
| GPT-5.6 Luna | 0.693 (312) | 0.738 (332) | 0.778 (350) |
| DeepSeek V4 Flash | 0.742 (334) | 0.758 (341) | 0.796 (358) |
| Qwen 3.8 27B | 0.700 (315) | 0.731 (329) | 0.753 (339) |
| Gemma 4 26B | 0.664 (299) | 0.682 (307) | 0.718 (323) |

Gemini’s cited five-cell select is 0.86 (387/450), the living
codebook roster replay on the same stack.

**ExECT `test60` (4-family inventory micro F1).** Cited cell-3 roster:
`exect_llm_extract` then rule encode / select. Find is the raw
stop; select is the hybrid stop. Sources:
`paper_experiments/exect/exect_llm_extract/{slug}/test60/comparison.json`.

| Model | Find | Select |
| --- | ---: | ---: |
| Gemini 3.7 Flash | **0.8491** | **0.8674** |
| Grok 4.6 | 0.7874 | 0.8146 |
| DeepSeek V4 Flash | 0.7830 | 0.8099 |
| GPT-5.6 Luna | 0.7650 | 0.7983 |
| Qwen 3.8 27B | 0.7260 | 0.7644 |
| Gemma 4 26B | 0.7198 | 0.7573 |

The Compact/headline ExECT model swap (`exect_llm_only` rung replay)
is retired for the roster table. It remains only as a labelled
secondary surface where an older draft still needs it.

**Gan `dev750` (Purist), same stack.** Sources:
`paper_experiments/gan/rungs/{slug}/dev750/comparison.json`.

| Model | Find | Encode | Select |
| --- | ---: | ---: | ---: |
| Gemini 3.7 Flash | 0.781 (586) | 0.811 (608) | 0.875 (656) |
| Grok 4.6 | 0.780 (585) | **0.815** (611) | **0.888** (666) |
| GPT-5.6 Luna | 0.717 (538) | 0.765 (574) | 0.825 (619) |
| DeepSeek V4 Flash | 0.727 (545) | 0.773 (580) | 0.831 (623) |
| Qwen 3.8 27B | 0.673 (505) | 0.708 (531) | 0.769 (577) |
| Gemma 4 26B | 0.668 (501) | 0.699 (524) | 0.756 (567) |

Luna is the coarse miss on Gan holdout find. After select on
`test450`, Gemini leads (**0.860**), then Grok **0.853**, DeepSeek
**0.820**, Luna **0.789**, Qwen **0.762**, and Gemma **0.724**. Rules
raise every model over its find stop and help Luna most
(+43 letters) without bringing Luna or the local models level
with Gemini or Grok. On the cited ExECT inventory roster, Gemini leads after
select (**0.8674**); Grok **0.8146**, DeepSeek **0.8099**, and Luna
**0.7983** form the next band; Qwen and Gemma trail (**0.7644** /
**0.7573**).

## Efficiency and flexibility

Later-stage LLM encode or select is a second call on every letter.
Thinking medium/high doubles the find token budget. Rule encode
and select replay the saved find. That is the cost case for
keeping cell 3 as the six-model row. On this inventory find
cell 3 is also the Gemini peak.

Rules also name the change and can be edited. A new policy reprocesses
the same raw without another find. The paper may say that. It may
not say a named step is clinically correct, or that a model's internal
reasoning is visible.

## What the paper may say

It may say the three variables were tested, and that thinking and
temperature moved less than stage ownership. It may say temperature
0 versus 1 is mixed and that living 0 is the appropriate default.
It may not predict a Luna change at temperature 0. It may say a
model-plus-rules mix beats all-rules and
all-model on holdout, with both holdout peaks at LLM / rules / rules.
It may say rules are the better encode/select owner when score, cost, and
replay are taken together. It may say model quality shows up most at
find, and that rules shrink but do not close the Luna / local-model
gaps on either task.

It may not promote medium or high thinking over living low. It may
not treat development all-rules wins as the holdout result. It may
not treat DeepSeek Gan holdout as matching Grok or Gemini.

## Claim boundary

Working synthesis of already-run cells. Gemini five-cell totals stay
with their owners. The ExECT stage-ownership table and the six-model
ExECT cell-3 roster use 4-family micro F1. The Gemini thinking ExECT
band above remains a Compact/headline secondary surface
(`exect_llm_only`). Gan model stage scores are no-call replays of
saved `gan_llm_extract` raws. The temperature table is a diagnostic
ablation (Gemini 1 not promoted; Grok 0 is living). Do not inspect
holdout rows. Do not retune from these bands.
