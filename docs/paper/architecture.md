# Architecture: extract, encode, select

Date: 2026-08-23
Status: current
Owner: this file

Two public golds. Three named stages. Five cells. Rules have authority.

```
letter
  -> extract   (rules, LLM, or both)   collect candidates / a first pick
  -> encode    (rules or LLM)          write the already-chosen fact in the designed form
  -> select    (rules or LLM)          may change the fact (gate, rewrite, reselect, invent)
  -> score     Purist (Gan) or 4-family micro F1 (ExECT)
```

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
| reselect | Choose a different already-extracted event |
| invent | Add a fact the extract did not propose |

The five cells are who runs extract / encode / select. See
[cells and runners](cells_and_runners.md). Implemented 2×3 runners
(`docs/architecture/`) explain live code paths. They are not the
headline table.

Gan gold: one current seizure-frequency label. ExECT gold: diagnosis,
frequency, prescriptions, investigations. Scores do not move between
tasks.
