# Gan later-stage encode and select prompts

Date: 2026-08-21
Status: current
Owner: [paper methods](../methods.md)
Related: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

Later-stage `gan_llm_encode` and `gan_llm_select` are Gemini calls that
replace rule encode and rule select on a saved extract ledger. They do
not re-read the letter. After each call, only join and projection run.

Encode sees `event_id`, stated value, and quote. It writes one
seizure-frequency label per event from the shared label-form list.
The encode-cell answer is the extract pick projected through those labels.

Select sees the labelled events plus the extract pick as a hint. It
keeps that pick unless a named ledger override applies. It may write a
new label only when no single event is the answer, and that label must
use the same label-form list as encode. It cannot do the note-derived
hybrid families.

## Why

The LLM row must be attributable to the model at encode and at select.
A letter-in call would be a new extract. Running the nine hybrid
families after the call would score hybrid select as the LLM cell.
Keeping the note out is a deliberate narrowing. Living hybrid
select also stays on the extracted events: no leftover date mine,
no clinic-month diary assignment, no residual jerk, and no elapsed
window conversion.

## Claim boundary

A prompt and ownership contract. Gemini Gan later-stage cells are
promoted. This select is not hybrid select.
