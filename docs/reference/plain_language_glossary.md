# Plain-language glossary

Paper methods are five cells: who runs extract, encode, and select (rules, LLM, or both). `rules` / `llm` / `llm_with_rules` are live runner families, not the headline table. `hybrid_full_stack` is a load alias for rule select.

# Naming guide

Last updated: 2026-08-03

Use the plain name in prose and commands. Give an internal identifier once only
when linking to saved evidence or code that still uses it.

## Pipeline methods

| Plain name | Active identity | Saved or internal identifiers | Meaning |
| --- | --- | --- | --- |
| Rules only | `rules` | `rules_only`, `deterministic_canonical_pipeline` | Deterministic rules determine the clinical facts |
| LLM only | `llm` | `llm_only`, `llm_only_canonical_pipeline` | The model determines the clinical facts; code validates or formats them |
| LLM with rules | `llm_with_rules` | `hybrid`, `hybrid_structured_events`, `hybrid_full_stack` (retained row, filename, and ruleset ids) | The model and deterministic code can both affect clinical meaning |

Do not use `hybrid` as the supervisor-facing method name. Keep it when citing a
saved identity that still contains the word.

## Saved result identifiers

| Identifier | Plain description | Use the identifier when… |
| --- | --- | --- |
| `V12` | Gan multi-model comparison, 0.84 Purist on locked test450 | Linking to its saved aggregate report |
| `v0_reference` | Gan single-pass event extractor, 0.81 Purist on locked test450 | Joining saved runs or citing its lineage |
| `v08` | Historical ExECT LLM-with-rules development control, 0.9202 clinical fact F1 on dev140 (superseded value 0.9189, pre the disclosed Diagnosis subsumption-guard fix, commit 41165adc, 2026-08-11); not the final decision-0040 architecture | Replaying its selected files or discussing its exact version |
| `GEPA` | Optimizer used for the selected ExECT LLM-only negative comparison | Describing the optimization method |

Do not use a version code as if it explains the method.

## Scores

| Plain name | Code or saved term | Important limit |
| --- | --- | --- |
| 4-family micro F1 | `clinical_inventory_unit_keys` | Paper-cited ExECT primary metric |
| Clinical fact recovery / clinical fact F1 | `clinical_headline`, `headline_target` | Historical Compact/headline view id and internal research score; not the paper-cited primary |
| Seizure-frequency state profile | `state_profile` | Used for seizure-frequency development only |
| Purist | Purist | Strict Gan label accuracy; primary Gan holdout score |
| Pragmatic | Pragmatic | Gan accuracy with specified label equivalences; secondary score |
| Phrase / CUI / full attributes | published-metric views | Required for a published-benchmark comparison |
| Evidence groundedness | evidence groundedness | Measures citation presence, not clinical correctness |

## Data splits

| Plain name | Code | Row policy |
| --- | --- | --- |
| Gan development split | `dev750` in prose; retained filenames and API `split` may say `validation750` | Row review allowed |
| Gan locked holdout | `test450` | Saved aggregates only |
| ExECT development split | `dev140` | Row review allowed |
| ExECT locked holdout | `test60` | Aggregate-only |
| All ExECT letters | `full200` | Includes development rows; test60 row review remains barred |

## Terms to use carefully

| Avoid as a default | Prefer | Keep only when… |
| --- | --- | --- |
| clinical headline / `clinical_headline` as the prose measure name | clinical fact recovery or clinical fact F1 | Linking to code, JSON keys, filenames, or replay fields |
| hybrid as the active method name | LLM with rules / `llm_with_rules` | Citing a retained filename, ruleset id, or historical stage namespace |
| architecture family | method | Comparing rules-only, LLM-only, and LLM-with-rules as research categories |
| surface | score, output format, data split, or view | Fixed code fields that cannot be renamed safely |
| cell | run or selected result | Referring to a literal table cell |
| spine | pipeline or processing steps | Retired from current prose; the file is now `02_pipeline_steps.md` |
| gate | check, restriction, or approval | A named decision truly depends on pass/fail evidence |
| contract | schema or software interface | Do not use it for a general rule or requirement |
| frozen | fixed, locked, or saved | `--frozen` command flags and exact saved identifiers |
| bounded | limited to the named data and method | A mathematical bound is meant |
| canonical | current, selected, or authoritative | A code identifier or filename still contains it |
| artifact | file, output, report, or saved evidence | A build system uses “artifact” as an exact technical term |
| provenance | source and change history | A formal provenance record is being discussed |
| reliability scorecard (as a live frontend page) | Decision 0044 shared reliability report and machine package | Citing the retained shared scorecard artifact |

## Domain and technical terms retained deliberately

Keep Purist, Pragmatic, CUI, F1, Brier score, ECE, calibration, normalization,
deterministic, LLM, schema, evidence span, holdout, and inter-annotator agreement.
They name established technical or clinical concepts and are more precise than
ordinary substitutes.
