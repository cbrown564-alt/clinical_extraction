# ExECT rules-only rule taxonomy audit

Date: 2026-08-27
Protocol: [recall-first restructure protocol](exect_rules_only_recall_first_restructure_protocol_2026-08-27.md), Phase A step 1.
Scope: every deterministic rule or switchable behavior in the four-family
rules-only program — the extractors under `deterministic/all_entities/`,
the SF pipeline stack (`pipeline.py`, `statement_parser.py`,
`frequency_section.py`, `sf_attribute_encoding.py`,
`sf_state_projection.py`, `sf_unknown_suppression.py`,
`sf_umbrella_clone.py`, `sf_last_event_duration.py`, `association.py`),
`select_rules.py`, and the encode stack entry
(`llm/pipelines/key_entities_structured.apply_format_stack`).

Classification: RECOGNISE finds candidate mentions in text; ENCODE
normalizes the surface or attributes of a fact without changing which
fact it is; SELECT keeps, drops, or rewrites candidates on context,
support, or duplication — a precision decision. A rule's role is its
actual behavior, not its file location.

## Headline findings

1. The promoted program has genuine per-family recognisers and a
   genuine ordered Select registry, but **most SELECT-role decisions
   still execute inside extraction**, invisible to the recognise-stop
   scores and not independently switchable. The largest offenders are
   listed in "Extract-internal SELECT" below.
2. Encode exists per family in mechanism but the accepted config runs
   it only for Diagnosis (`ENCODE_FORMAT_STACK`); SF encoding
   (`sf_attribute_encoding`, `lexicon`, `normalizer`) is hard-wired
   inside extraction, and Rx/Inv encode is hard-wired dose/unit/
   modality/result canonicalization inside their extractors.
3. The Select registry (15 rules in `select_rules.py`) is genuinely
   ordered, switchable, and now family-mapped (`RULE_FAMILY_BY_ID`),
   but the accepted set enables only five rules, three of them
   Diagnosis-side.

## Select registry (`select_rules.py`)

All 15 registry rules are SELECT-role, independently switchable, with
declared action kinds and portability. Family ownership as recorded in
`RULE_FAMILY_BY_ID`:

| Family | Rules |
| --- | --- |
| Diagnosis | source_local_specificity (rewrite), explicit_heading_phenotype (add), inventory_keep_source_diagnosis (add) |
| SeizureFrequency | sf_named_type_identity (rewrite), sf_recent_event_over_historical_free (add/drop), sf_supported_state_promotion (add), sf_rateless_anchor_drop (drop), sf_generic_duplicate_of_named_type_drop (drop), sf_seizure_free_positive_count_drop (drop) |
| Prescription | local_regimen_scope (rewrite), active_titration (add), exact_regimen_dedupe (drop) |
| Investigations | investigation_same_result_dedupe (drop) |
| cross_family | sf_to_diagnosis_explicit_type (add), inventory_weak_episode_drop (drop) |

Accepted 2026-08-27 set: the three RULES_ONLY Diagnosis rules plus
sf_seizure_free_positive_count_drop and inventory_weak_episode_drop.

Note the registry's "add" rules (`inventory_keep_source_diagnosis`,
`sf_supported_state_promotion`, `explicit_heading_phenotype`,
`active_titration`) are recoveries of candidates the extract stage
already found and dropped — evidence that recognise is not recall-first
today. Under the restructure these should become keep decisions over a
wider direct ledger rather than re-additions from source rows.

## Extract-internal SELECT (the relocation targets)

### SeizureFrequency (`pipeline.py` and stack)

| Behavior | Location | Status |
| --- | --- | --- |
| Rate-gate: anchors with no associated attribute are never emitted | `pipeline.py` default `keep_unassociated_anchors=False` | **Relocated 2026-08-27**: `RecogniseConfig.sf_keep_unassociated_anchors` emission switch paired with `selection.sf_rateless_anchor_drop`; Gate A2 identity 140/140, SF recognise recall 0.8667 -> 0.8909 |
| Association gate (same sentence, <=80 chars; orphan attributes discarded) | `association.py` | Hard-wired; orphan seizure-free attributes partially recoverable via `recognise.sf_seizure_free` producer |
| `_is_bare_nonzero_count` discard | `pipeline.py` | Hard-wired; guideline-grounded (L255), treated as a recognise contract, not relocated |
| `_should_keep_mention` precision filters (bare generic zero, bare "seizure free", statement-parser noise, alias FTB zero) | `pipeline.py` | Hard-wired SELECT inside extraction; relocation candidates, lower priority (corpus-tuned precision rules) |
| State drops (unlabelled/historical active rate, advice seizure-free), umbrella clone drop, unknown suppression | `sf_state_projection.py`, `sf_umbrella_clone.py`, `sf_unknown_suppression.py` | Hard-wired (projection-ablation gated); these run inside the SF extract stack |
| Overlap resolution (longest anchor, most-attribute extraction) | `overlap.py` | Treated as recognise mechanics, not relocated |

### Diagnosis (`diagnosis.py`)

| Behavior | Location | Status |
| --- | --- | --- |
| Longest-match overlap skip (`occupied`) — nested ancestor concepts never emit directly | match loop | Recall gap; `nested_ancestor_diagnosis_candidates` producer exists (deferred class), to be emitted as direct in Phase B |
| Service-context / family-history-of exclusion (D1) | `_is_nondiagnostic_service_context` flag | Accepted ON at recognise; excluded occurrences re-emittable via `nondiagnostic_context_diagnosis_candidates` producer — Phase B direct emission with paired Select drop |
| Onset-statement drop, cause/secondary-to drop | `_is_diagnosis_phrase_inside_*` | Hard-wired (cause drop inverted by accepted `secondary_to_retention`) |
| Negation/family/admin/uncertain context exclusion | `_is_excluded_diagnosis_context` | Only on the resolution-candidate path; baseline path unaffected |

### Prescription (`prescription.py`)

Hard-wired SELECT inside extraction: incomplete-regimen gate,
future/titration/initiation left-context filters, weight-based dose
skip, planned dose-phrase trim, parenthetical-alias skip, PRN-no-dose
path. Relocation parked: these filters are entangled with dose parsing
(the filter decides which dose span belongs to the regimen), so
emit-then-drop cannot reproduce the identical mention set cheaply.
Recorded as a negative relocation result under the protocol's stop
rule; Phase B addresses Rx via dictionary coverage instead.

### Investigations (`investigations.py`)

Hard-wired SELECT inside extraction: planned-test drop,
emit-only-with-result, negated-finding-to-Normal precedence,
result-window binding. The mentions-without-result drop is the
Investigations relocation candidate (emit result-less modality
mentions, drop at Select); result binding itself is recognise
mechanics.

## Encode inventory

| Family | Encoders | Where | Switchable? |
| --- | --- | --- | --- |
| Diagnosis | concept resolve, `attach_benchmark_concept`, format target, Certainty/Negation defaults | extractor; plus `ENCODE_FORMAT_STACK` at the encode stage | format stack per family via `ThreeStageConfig.family_encoders` |
| SeizureFrequency | CUI lexicon, `sf_attribute_encoding` cascade (word-number, range split, interval completer, last-event zero, during window, ...), normalizer count/unit/month maps, projection alias texts | inside SF extract stack | hard-wired |
| Prescription | dose/unit canonicalization, frequency codes, drug alias resolve + CUI | extractor | hard-wired |
| Investigations | modality canonicalization, result classify, EEG type | extractor | hard-wired |

The `family_encoders` registry (2026-08-27) makes per-family encode
sequences configurable; `encode.format_stack` is the first registered
encoder, and the SF typo lexicon (gated rewrite R2) is the first
planned SF-specific encoder.

## Recognise inventory (per family)

- Diagnosis: 72-surface alternation (recall-first extras plus 67
  benchmark surfaces), probable-focal and focal-onset alias regexes,
  residual additions (dev-only flag), nested-ancestor and
  nondiagnostic-context deferred producers.
- SeizureFrequency: ablatable anchor/rate/seizure-free/change/temporal
  rule registry, frequency-section parser, statement parser (~20
  letter-wide emitters plus same-sentence and pronoun carry-forward),
  deferred producers for named-type, heading-state, and orphan
  seizure-free candidates, and (new) rate-less anchor emission.
- Prescription: ~54 match strings (38 benchmark surface forms + 35
  brand/typo aliases resolving to 23 canonical entries), dose/frequency
  parsing.
- Investigations: modality pattern (EEG/VEEG/MRI/CT variants) plus
  result binding.

## Consequences adopted by the restructure

1. Relocations proceed emission-switch + paired-Select-drop, one at a
   time, each gated by select-stop identity (Gate A2). Completed: SF
   rate-gate. Queued: Diagnosis nondiagnostic-context and nested
   ancestors as direct classes, Investigations result-less mentions.
   Parked with reasons: Prescription plan filters, SF
   `_should_keep_mention` cluster.
2. Recognise-stop recall becomes an honest recall-first number as
   relocations land; precision at that stop is expected to fall and is
   not repaired at recognise.
3. Phase C converts the drop-by-default pairing into per-class
   conditional keeps inside the Select stage, replacing the
   "promotion/add" pattern.
