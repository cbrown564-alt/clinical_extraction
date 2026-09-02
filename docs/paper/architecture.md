# Architecture: find, encode, select

Date: 2026-08-23
Status: current
Owner: this file

Two public golds. Three named stages. Five cells. Rules have authority.

These are **implementation** names. The dissertation paper reports two
stages, **extract** (find plus the bundled codebook encode in one LLM
call) and **decide** (select), and compares two decision executors on
one shared extract
([paper-story simplification](decisions/paper-story-simplification.md)).
Use the implementation names below only to identify artifacts.

The first stage is **find**, not extract. The overall job is
information extraction; this stage is the named-entity-recognition
step that collects candidates. Live runner names and envelope keys
still say `extract`.

```
letter
  -> find (rules, LLM, or both)   collect candidates / a first pick
  -> encode    (rules or LLM)          write the already-chosen fact in the designed form
  -> select    (rules or LLM)          may change the fact (gate, rewrite, reselect, invent)
  -> score     Purist micro-F1 (Gan) or 4-family micro F1 (ExECT)
```

On Gan, living rules find is source-near (`gan_llm_extract_raw`
dialect): found tokens, not codebook spelling. `gan_llm_extract`
already writes codebook form, so it is bundled find-and-encode.
Cell 3 shares encode between that request and `gan_rules_encode`.
Owner: [rules find dialects](../research/gan2026/gan_rules_find_llm_dialects_2026-08-31.md).

Encode does not reselect. A quoted span is not proof the right statement
was chosen. Select is the leftover that may change the fact.

Rule authority (catalogue index, not a second pipeline):

| Authority | May do |
| --- | --- |
| parse | Recover a typed object |
| dialect | Same fact, different spelling or unit |
| encode | Write the designed form / codebook |
| gate | Block or keep a fact |
| rewrite | Change the submitted concept |
| reselect | Choose a different already-found event |
| invent | Add a fact the find stage did not propose |

The five cells are who runs find / encode / select. See
[cells and runners](cells_and_runners.md). Implemented 2×3 runners
(`docs/architecture/`) explain live code paths. They are not the
headline table.

Gan gold: one current seizure-frequency label. ExECT gold: diagnosis,
frequency, prescriptions, investigations. Scores do not move between
tasks.
