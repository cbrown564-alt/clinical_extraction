# ExECT later-stage encode and select prompts

Date: 2026-08-21
Revised: 2026-08-23 (Gemini-only later stages; cited score is 4-family micro F1)
Status: current
Owner: [paper methods](../methods.md)
Related: [Gemini is the cited model](gemini-is-the-cited-model.md),
[six-model roster](six-model-roster.md),
[Gan later-stage encode and select prompts](gan-later-stage-encode-select-prompts.md)

## Decision

Later-stage `exect_llm_encode` and `exect_llm_select` are Gemini
calls that replace rule encode and rule select on a saved
`exect_llm_extract` mention list. They do not re-read the letter.

Encode sees `mention_id`, family, clinical name, supporting
sentence, details, and the closed name list for every family
(diagnosis phrases, 16 seizure-type heads, generic medicines,
MRI/CT/EEG) plus closed detail values. It writes one
`standard_name` and details per find mention. It does not add,
drop, or split rows, and it does not write CUIs. After the call,
code joins by `mention_id` and maps plain keys to gold keys. It may
attach CUI from `standard_name` as decoration. Hybrid format and
select do not run.

Select sees the encoded rows (`mention_id`, family, `standard_name`,
details, supporting sentence). It does not see the encode name list
again. The given `standard_name` is the short-name style to keep on
merge or when also listing a fact in the other family. It may drop,
relabel `standard_name`, rewrite details from words already on that
row, merge onto another `mention_id`, or also list a kept fact in
diagnosis or seizure frequency by copying that row's quote and
standard name. It returns one row per input `mention_id`. It may
not invent a new quote or a name the kept row did not carry. After
the call, only join runs. Encode join writes `standard_name`;
scoring uses that name.

The SeizureFrequency type key is the canonical seizure-type phrase
(16 lexicon heads), not CUI. Gold folds `CUIPhrase` when present.
The encode list drops CUI-lookup leftovers (bare `focal` /
`generalised`, `no further seizures`) and lists generic `seizures`
last. Rules-only CUI attach stays an exact phrase lookup after the
longest-span anchor; it does not assign by subset of the word
`seizures`.

Hybrid select follows the same invent ban. Letter-scan Diagnosis /
SF / Rx / Inv tables are rules find and pre-post high-priority
suggested evidence. The model keep/rejects them. Rules do not union
them in after a hybrid call.

## Why

The LLM row must be attributable to the model at encode and at
select. A letter-in call is a second find. Running hybrid invent
after the call would score hybrid select as the LLM cell. CUI is a
one-to-one tag, not a model job. Standard name is the designed-form
name; clinical name stays find wording.

## Claim boundary

A prompt and ownership contract. These calls are Gemini-only
ablations on a saved `exect_llm_extract` find raw. They are not the
six-model row and are not authorised on Grok, Luna, DeepSeek, Qwen,
or Gemma. Clinical-fact SF type now keys the folded seizure-type
phrase. CUI stay on the mention as secondary attributes and still
feed the published with-CUI diagnostic. Gemini later-stage
`exect_llm_encode` and `exect_llm_select` have been run and
promoted; cite the 4-family micro F1 (`clinical_inventory_unit_keys`)
cells, not Compact/headline F1 or `clinical_headline_unit_keys`.
Living hybrid select no longer unions residual letter-scan
findings after the call. Pre-post still shows those cues as
suggested evidence.
