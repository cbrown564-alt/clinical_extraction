# Find then Select vs find-and-select in one call

Date: 2026-08-25
Status: working ablation draft; not a results column
Owners: [find-and-select vs find](../exectv2/exect_one_call_select_vs_rule_select_2026-08-25.md),
[ExECT inventory grid](../exectv2/exect_both_extract_on_inventory_protocol_2026-08-23.md)
Related: [three variables](three_variables_rules_model_thinking_2026-08-23.md),
[source-near find vs bundled encode](gan_source_near_vs_bundled_encode_2026-08-23.md)

This is the ExECT select-ownership ablation. It is not the five-cell
grid and not a roster result. Holdout is aggregate-only. Do not
inspect `test60` rows.

## The question

Two ExECT choices sit next to cell 3:

1. **What the find writes.** `exect_llm_extract` asks the model
   for the four-family inventory. It does not ask the model to drop
   findings that Select would later refuse.
2. **Who selects, and in how many calls.** Select can stay with
   recorded inventory rules after that find, or the model can
   find and filter in one call (`exect_llm_extract_and_select`),
   then optionally take the same Select stack.

The paper cites find plus inventory Select. The one-call filter
stays an ablation.

## Answer

Inventory Select after `exect_llm_extract` is the better stack.
On Gemini `dev140` the select-stop gap is tiny (**0.8877** vs
**0.8864**). The one-call request is the better find-stop there
(**0.8384** vs **0.8273**) because it already drops some false
positives. After the same Select, find still has higher
Diagnosis recall and much higher SeizureFrequency recall.

On locked `test60` the same find plus Select wins at both
stops (find **0.8491 → 0.8674**; one-call **0.8170 → 0.8435**).
The holdout gap is mostly SeizureFrequency (select-stop **0.8082**
vs **0.6818**; recall **0.7973** vs **0.6081**). Both stacks use
one model call. Bundling Select into the request does not replace
the recorded filter.

## 1. Find-stop vs select-stop

Gemini 3.7 Flash, `clinical_inventory_unit_keys`, 4-family micro
F1. Find-stop is the model payload. Select-stop is inventory
Select on that payload.

| Stack | `dev140` find | `dev140` select | `test60` find | `test60` select |
| --- | ---: | ---: | ---: | ---: |
| LLM recognises, rules select | 0.8273 | **0.8877** | **0.8491** | **0.8674** |
| LLM recognises and selects (1 call), rules select | **0.8384** | 0.8864 | 0.8170 | 0.8435 |

The one-call request can look like a win before Select. After
Select, find is ahead on both splits. The development margin
is 0.0013. The locked margin is 0.0239. That is not a cited
five-cell replacement.

## 2. Where the remaining gap sits

Gemini 3.7 Flash, select-stop family F1.

| Split | Stack | Overall | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `dev140` | find, rules select | **0.8877** | **0.8413** | **0.8338** | 0.9604 | **0.9591** |
| `dev140` | find-and-select, rules select | 0.8864 | 0.8381 | 0.8307 | **0.9659** | 0.9438 |
| `test60` | find, rules select | **0.8674** | 0.8432 | **0.8082** | **0.9286** | 0.9247 |
| `test60` | find-and-select, rules select | 0.8435 | **0.8500** | 0.6818 | 0.9036 | **0.9462** |

On development, find keeps Diagnosis recall **0.8298** vs
**0.8024** and SeizureFrequency recall **0.8667** vs **0.7879**.
The one-call SeizureFrequency misses are often seizure-free or
unspecified-rate states that the payload still refuses unless
attributes are filled. That reading is development only.

On `test60`, SeizureFrequency recall is **0.7973** vs **0.6081**.
No holdout letters or row errors were opened.

The one-call payload still keeps generic and specific stated
diagnoses, heading named types, and hedge-implied place or type.
Non-epileptic, future-medication, and pending-test filters stay.
Those filters do not make the model the better Select owner.

## What the paper may say

It may say asking the model to find and select in one call does
not beat find plus inventory Select. It may say the one-call
request can raise the find-stop on development by dropping some
false positives, and that the same Select then puts find back
ahead. It may say the locked gap is larger and sits in
SeizureFrequency. It may say both stacks are one model call, so
the reason to keep Select in rules is score and a recorded filter,
not an extra prompt.

It may not treat `exect_llm_extract_and_select` as cell 3. It may
not cite the read-only aliases `exect_llm_extract_filtered` or
`exect_llm_only` as a results column. It may not inspect `test60`
rows. It may not retune the one-call SeizureFrequency rules from
holdout misses.

## Claim boundary

Synthesis of the Gemini inventory find cell and the live
find-and-select ablation. Mechanism on `dev140` may name
letters; holdout may not. Companion models were not restaged.
See [three variables](three_variables_rules_model_thinking_2026-08-23.md)
for the roster reading, and
[source-near find vs bundled encode](gan_source_near_vs_bundled_encode_2026-08-23.md)
for the Gan analog: bundling a later stage into find.
