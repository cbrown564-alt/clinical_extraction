# Gan later-stage encode and select prompts

Date: 2026-08-21
Status: current
Owner: [paper methods](../methods.md)
Related: [Gemini is the cited model](gemini-is-the-cited-model.md)

## Decision

Later-stage `gan_llm_encode` and `gan_llm_select` are Gemini calls that
replace rule encode and rule select on a saved extract ledger. They do
not re-read the letter. After each call, only join and projection run.

Encode sees `event_id`, stated value, and quote. It writes one short
seizure-frequency label per event. The encode-cell answer is the extract
pick projected through those labels.

Select sees the labelled events plus the extract pick as a hint. It
keeps that pick unless a named ledger override applies. It may write a
new short label only when no single event is the answer. It cannot do
the note-derived hybrid families.

## Why

The LLM row must be attributable to the model at encode and at select.
A letter-in call would be a new extract. Running the nine hybrid
families after the call would score hybrid select as the LLM cell.
Keeping the note out is a deliberate narrowing: residual diary and
elapsed-window rates stay with hybrid select, not this prompt.

## Claim boundary

A prompt and ownership contract. Not a claim that the calls have been
run, or that this select matches hybrid select scores.
