# ExECTv2 Key-Entity Structured Prompt v0.2 Pilot

Date: 2026-06-18  
Split: dev25 only  
Pipeline: `exectv2_llm_only_key_entities_structured`  
Model: `openai/gpt-4.1-mini`

## Decision

v0.2 is a useful iteration, not a promoted candidate. It confirms that the single
structured schema can respond to error-analysis-led prompt changes: semantic item
F1 improved from `0.206` to `0.272`, benchmark item F1 from `0.158` to `0.220`,
and evidence validity from `0.9539` to `0.9760`, with `0` call failures and `0`
parse failures in both pilots.

It remains far below the key-family target of F1 >0.8. The next iteration should
not promote to dev140 yet; it should split the v0.2 tradeoff by tightening
SeizureFrequency rendering further while undoing the Prescription text-altitude
regression.

## v0.1 -> v0.2 Comparison

| Layer | v0.1 item F1 | v0.2 item F1 | Delta |
| --- | ---: | ---: | ---: |
| source-near | 0.722 | 0.680 | -0.042 |
| phrase-only | 0.385 | 0.408 | +0.023 |
| semantic | 0.206 | 0.272 | +0.066 |
| benchmark | 0.158 | 0.220 | +0.062 |

| Entity | v0.1 semantic F1 | v0.2 semantic F1 | Read |
| --- | ---: | ---: | --- |
| Prescription | 0.264 | 0.172 | Regressed; full-regimen text guidance overcorrected. |
| Diagnosis | 0.204 | 0.283 | Improved; assertion defaults and atomic seizure-type guidance helped. |
| SeizureFrequency | 0.070 | 0.210 | Improved; range/date/last-clinic rules helped but still weak. |
| Investigations | 0.267 | 0.522 | Improved; EEG_Type restraint and shorter modality text helped. |

## Error-Analysis Read

The v0.1 dominant failure was not schema reliability. It was rendering:
source-near F1 was already much higher than semantic F1, and SeizureFrequency
attribute agreement was only `4/19`. The v0.2 prompt therefore added explicit
clinical rendering rules:

- ranges use `LowerNumberOfSeizures` / `UpperNumberOfSeizures`;
- dated counts keep `MonthDate` / `YearDate` and `During` rather than a guessed
  recurring `TimePeriod`;
- `since last clinic` maps to `TimeSince_or_TimeOfEvent=Since` and
  `PointInTime=LastClinic`;
- last-event and seizure-free statements use `NumberOfSeizures=0` plus the stated
  temporal anchor;
- every Diagnosis mention carries `Certainty` and `Negation`;
- plain EEG does not default to `EEG_Type=Standard`;
- model-supplied `CUI` / `CUIPhrase` is stripped before the shared projection
  step, preserving clean benchmark-format attribution.

The strongest gains came exactly where those rules targeted: SF semantic item F1
`0.070 -> 0.210`, Investigations `0.267 -> 0.522`, and Diagnosis `0.204 ->
0.283`. The main regression came from medication text altitude: asking for compact
full regimen spans lowered Prescription semantic item F1 `0.264 -> 0.172`.

## Next Iteration

Do not spend dev140 yet. Build v0.3 on the same dev25 surface:

1. Keep the SF and investigation v0.2 rules.
2. Rework Prescription rendering as a two-policy instruction: bare drug name for
   clinical identity, compact regimen span only when the annotation-style line is
   unambiguous. If this remains unstable, compare against the existing
   Prescription component scorer rather than forcing benchmark phrase altitude
   into the LLM prompt.
3. Add a small hard-case panel from the dev25 observed errors for SF dates,
   ranges, vague counts, and last-event statements before the next live run.
4. Promote to dev140 only after dev25 semantic F1 improves without entity-level
   collapse.
