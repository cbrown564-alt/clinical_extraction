# How the cited methods were reached

Date: 2026-08-17
Revised: 2026-08-19 (method changes classified by semantic effect)
Status: current
Owner: this file

One page. No experiment links. Detail lives in git.

This history distinguishes changes by what they can alter:

| Change class | Meaning |
| --- | --- |
| Request or extraction change | Changes what evidence or candidate facts a model or rule method can produce |
| Representation change | Changes the event, state, fact, or attribute structure available to later stages |
| Task-decision change | Changes which current state wins or which facts enter the final inventory |
| Semantic deterministic change | Changes a clinical concept, state, attribute, multiplicity, evidence acceptance, or unknown status |
| Format-only change | Changes serialization without changing the represented answer |
| Scorer-only change | Changes how a submitted answer is projected or compared, not the submitted answer itself |

These classes matter because a prompt edit, a winner rule, a concept mapping,
and a JSON renderer are not interchangeable interventions.

## ExECT request history

Living names are on [methods](methods.md): ExECT rules, ExECT LLM
only, and ExECT LLM with rules. This page only records how the
living requests were reached.

ExECT LLM with rules is one structured call, then family-specific
deterministic repair. The long instruction book (Full ledger) still
scores well. It is long: a complete rule list, encoding schema, and
dozens of worked examples.

The living request is the same architecture written in ordinary
language. It keeps the scaffold, the seizure-frequency encoding
rules, and the scope rules. It drops the non-seizure-frequency
encoding rules and all worked examples. Those are request and
task-policy changes. The request writes authored-order JSON and does
not send `letter_id` or `prompt_version` to the model; those are
format and request-envelope changes unless they alter a generated
clinical fact.

A later dump used a different request shape (alphabetical JSON,
those fields present). That dump is not the living method. The
paper cites hybrid F1 for ExECT LLM with rules and raw F1 for
ExECT LLM only. Full ledger is the longer control when cited; it
is not a headline method or a peer column. Grok has no Full ledger
cell.

## Gan cleaned request

The Gan hybrid is one structured-events call, then a frozen deterministic
stack that chooses the current seizure-frequency label. The call defines the
candidate representation; the later stack contains task-decision, semantic,
and rendering changes. The
clinical contract is thirteen instructions plus event and selection
schemas.

An earlier request also sent three lab labels to the model: the
dataset and method name, a version string, and the row index. Those
labels do not teach extraction. The cleaned request keeps the
thirteen instructions and drops the three labels.

The paper method is the cleaned request. Cells from the enveloped
request are not that method. Do not relabel them.

## What was tried and is not cited

Shorter or longer Gan instruction add-ons that were not a shared
cross-model contract. ExECT study prompts from the mention-unit and
leftover-form campaigns. Example-zoo prunes that are not Compact. A
separate multi-model Gan architecture. GEPA as an ExECT LLM-only.
Those trails selected Compact and the cleaned Gan request. They are
not paper methods.
