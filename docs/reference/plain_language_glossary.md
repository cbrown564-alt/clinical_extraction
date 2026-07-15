# Naming guide

Last updated: 2026-07-15

Use the plain name in prose and commands. Give an internal identifier once only
when linking to saved evidence or code that still uses it.

## Pipeline methods

| Plain name | Saved or internal identifiers | Meaning |
| --- | --- | --- |
| Rules only | `rules_only`, `deterministic_canonical_pipeline` | Deterministic rules determine the clinical facts |
| LLM only | `llm_only`, `llm_only_canonical_pipeline` | The model determines the clinical facts; code validates or formats them |
| LLM with rules | `hybrid`, `hybrid_structured_events` | The model and deterministic code can both affect clinical meaning |

Current Gan commands use `rules`, `llm`, and `llm_with_rules`.

## Saved result identifiers

| Identifier | Plain description | Use the identifier when… |
| --- | --- | --- |
| `V12` | Gan multi-model comparison, 379/450 Purist on locked test450 | Linking to its saved aggregate report |
| `v0_reference` | Gan single-pass event extractor, 364/450 Purist on locked test450 | Joining saved runs or citing its lineage |
| `v08` | Historical ExECT LLM-with-rules development control, 0.9189 clinical fact F1 on dev140; not the final decision-0040 architecture | Replaying its selected files or discussing its exact version |
| `GEPA` | Optimizer used for the selected ExECT LLM-only negative comparison | Describing the optimization method |

Do not use a version code as if it explains the method.

## Scores

| Code or term | Plain description | Important limit |
| --- | --- | --- |
| `clinical_headline` | De-duplicated clinical fact recovery across the main ExECT entities | Internal research score, not the published strict benchmark |
| `state_profile` | Combined seizure-frequency state score | Used for seizure-frequency development only |
| Purist | Strict Gan label accuracy | Primary Gan holdout score |
| Pragmatic | Gan accuracy with specified label equivalences | Secondary score; do not replace Purist in holdout claims |
| Phrase/CUI/full attributes | Published ExECT representation metrics | Required for a published-benchmark comparison |
| Evidence groundedness | Share of cited evidence found in the note after neutral text repair | Measures citation presence, not clinical correctness |

## Data splits

| Code | Plain description | Row policy |
| --- | --- | --- |
| `validation750` | Gan development split, 750 letters | Row review allowed |
| `test450` | Gan locked holdout, 450 letters | Saved aggregates only |
| `dev140` | ExECT development split, 140 letters | Row review allowed |
| `full200` | All 200 ExECT letters | Includes development rows; test60 row review remains barred |

## Terms to use carefully

| Avoid as a default | Prefer | Keep only when… |
| --- | --- | --- |
| architecture family | method | Comparing rules-only, LLM-only, and LLM-with-rules as research categories |
| surface | score, output format, data split, or view | Retain only in fixed code fields that cannot be renamed safely |
| cell | run or selected result | Referring to a literal table cell |
| spine | pipeline or processing steps | Retired from current prose; the file is now `02_pipeline_steps.md` |
| gate | check, restriction, or approval | A named decision truly depends on pass/fail evidence |
| contract | schema or software interface | Do not use it for a general rule or requirement |
| frozen | fixed, locked, or saved | `--frozen` command flags and exact saved identifiers |
| bounded | limited to the named data and method | A mathematical bound is meant |
| canonical | current, selected, or authoritative | A code identifier or filename still contains it |
| artifact | file, output, report, or saved evidence | A build system uses “artifact” as an exact technical term |
| provenance | source and change history | A formal provenance record is being discussed |

## Domain and technical terms retained deliberately

Keep Purist, Pragmatic, CUI, F1, Brier score, ECE, calibration, normalization,
deterministic, LLM, schema, evidence span, holdout, and inter-annotator agreement.
They name established technical or clinical concepts and are more precise than
ordinary substitutes.
