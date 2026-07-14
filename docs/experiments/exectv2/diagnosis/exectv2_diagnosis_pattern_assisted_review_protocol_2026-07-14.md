# ExECTv2 Diagnosis pattern-assisted review protocol

Date: 2026-07-14  
Status: complete intermediate diagnostic; the later final review resolved all 246 rows  
Track: ExECTv2 development evidence

## Question

How many of the 213 unreviewed Diagnosis disagreement rows repeat an observable
pattern found in the first 33 manual decisions, and how many can be labelled
conservatively before the remaining rows are reviewed manually?

The purpose is to reduce repetitive review. It is not to replace clinical
adjudication or calculate a corrected benchmark score.

## Fixed inputs and permissions

- Dataset and split: ExECTv2 `dev140`; row inspection is permitted.
- Test60 must not be read.
- Audit rows:
  `experiments/exectv2_diagnosis_interpretation_audit_dev140_20260714.jsonl`.
- Manual overlay:
  `C:/Users/cbrow/Downloads/exectv2-diagnosis-review-2026-07-14.json`.
- Fixed methods: rules only, the retained GEPA LLM-only comparator, and the
  retained v08 LLM-with-rules control.
- Calls: none. The study may only inspect the saved audit substrate and manual
  overlay.
- Primary scorer and gold remain unchanged.

The audit contains 246 rows. The supplied overlay contains 33 manual decisions,
so the unreviewed population is 213 rows. Manual decisions are immutable inputs
to this pass.

## Pattern labels learned from the 33 manual decisions

### Representation or evaluation patterns

1. The same diagnosis is rendered at different specificity, including
   generic versus specific seizure types, epilepsy versus a qualified epilepsy
   diagnosis, and singular versus plural seizure wording.
2. Gold multiplicity expects both a syndrome and its component concepts while
   a method emits a clinically consolidated representation.
3. A supported epilepsy or named seizure diagnosis is absent from gold because
   of an annotation convention or omission.
4. One semantic substitution appears as a paired missed and spurious row.

### Extraction-error patterns

1. A non-target condition, symptom, risk factor, cause, or generic event is
   promoted to an epileptic Diagnosis.
2. A negated mention is emitted as an affirmed diagnosis.
3. Lexical overgeneralisation creates a generic or broader diagnosis.
4. A separately asserted named seizure type is omitted.

The `absence-like` decision in EA0006 remains uncertain and is not a template
for automatic clinical resolution.

## Automatic assignment rules

Automatic labels must depend on observable fields and exact, review-derived
patterns. A row is left for manual review when rules conflict or when deciding
it requires clinical interpretation.

The pass may assign:

- `representation` when an opposite-direction row for the same method and
  letter has an overlapping non-empty CUI, or when the pair matches an explicit
  reviewed synonym, number, or parent/specific relation;
- `extraction_error` for an exact reviewed non-target concept family, a generic
  `seizures` output, or an affirmed method output whose only exact source
  occurrences are inside an observable negation span;
- `uncertain` only for the reviewed `absence-like` wording pattern.

Rules must not infer that every phrase appearing in a note is a correct
Diagnosis. They must not infer equivalence from embedding similarity, model
judgment, or an unreviewed ontology relation.

## Outputs and checks

The run will produce:

- a JSON overlay that preserves all 33 manual decisions and adds automatic
  decisions with a pattern identifier in the note;
- a JSON summary containing source hashes, per-pattern counts, method counts,
  conflicts, and the number left for manual review;
- a results section in this document.

Checks must establish that all keys exist in the fixed audit, no manual decision
changed, every automatic decision names one rule, conflicting rows remain
unreviewed, and counts reconcile to 246.

## Stop rule and claim boundary

Stop after producing and checking one no-call overlay. Keep a negative result if
the observable rules do not cover most remaining rows. The result is a
diagnostic convenience for this dev140 review. Automatic labels are hypotheses
for reviewer confirmation, not independent clinical adjudication, corrected
gold, test evidence, or a promoted scorer change.

## Result

The pattern pass assigned 197 of the 213 previously unreviewed rows (92.5%).
The majority hypothesis is therefore supported on this dev140 review
population.

| Assigned label | Rows |
| --- | ---: |
| Representation or evaluation issue | 158 |
| Extraction error | 39 |
| Left for manual review | 16 |

Together with the 33 original manual decisions, the assisted overlay contains
230 decisions across the 246 audit rows.

The automatic rule counts overlap when one row has more than one observable
reason:

| Observable pattern | Rule matches |
| --- | ---: |
| Related prediction already expresses the missed clinical concept | 49 |
| Prediction is a related rendering of a gold concept | 44 |
| Reviewed synonym, number, or parent/specific pair | 36 |
| Supported concept appears omitted from gold | 25 |
| Opposite-direction rows share a CUI | 23 |
| No related prediction recovers the gold concept | 21 |
| Non-target condition, symptom, cause, or generic event | 16 |
| Reviewed negated-focal pattern | 1 |
| Unsupported spurious concept | 1 |

Automatic row memberships by method are 153 for LLM only, 63 for rules only,
and 56 for LLM with rules. These sum above 197 because a union review row may
belong to more than one method.

## Calibration against the 33 manual decisions

Before applying the broader rules to unreviewed rows, the pass replayed them on
the 33 manual decisions:

- 30 received the same label;
- 3 were deliberately left unclassified;
- none received a contradictory label.

The three unclassified calibration rows were EA0016 `spurious epilepsy`, EA0020
`spurious tonic clonic seizures`, and EA0028 `spurious epilepsy`. Their manual
decisions cannot be separated reliably by the observable rules used here.

## Rows left for manual review

The remaining 16 rows concentrate the expected difficult boundaries:

- myoclonic seizure versus myoclonic jerk or JME component meaning:
  EA0033, EA0043, EA0125, and EA0189;
- generic epilepsy or epileptic-seizure mentions with weak, family-history,
  non-epileptic, or non-assertive context: EA0073, EA0076, EA0100, EA0102,
  EA0104, EA0109, and EA0120;
- negated tonic-clonic wording: EA0114;
- family-history or uncertain absence wording: EA0189;
- probable non-epileptic psychogenic seizures: EA0198.

Use the exact review keys in the summary artifact for review. No automatic
label was assigned to these rows.

## Artifacts and reproducibility

- Assisted overlay:
  `experiments/exectv2_diagnosis_pattern_assisted_overlay_20260714.json`
- Machine-readable summary:
  `experiments/exectv2_diagnosis_pattern_assisted_summary_20260714.json`
- Implementation:
  `clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.diagnosis_pattern_assisted_review`
- Source audit SHA-256:
  `0c454b253d57cc572658eed62c232b7e5c688bfdfca68ebc1e8e87c332bee13f`
- Manual overlay SHA-256:
  `69ab1deaf6429005dd71cdbd28e021ffaf020be24f655cd7b3fef6f92d77becd`

The assisted overlay preserves the 33 supplied manual decisions byte-for-byte
at the decision-object level. Every automatic decision includes its rule name
in the note so it can be distinguished from manual review.

This remains a diagnostic development result. The 197 automatic labels are
pattern-based hypotheses for review management, not independent clinical
adjudication and not permission to alter gold or report a corrected F1.

## Follow-on review

The subsequent completed overlay reviewed the 16 remaining rows and confirmed
or revised the assisted decisions across the full 246-row union. The final
distribution is 173 representation/evaluation issues, 72 extraction errors,
and one uncertain row. The final overlay and mechanism ledger are recorded in
the [Diagnosis resolution protocol](exectv2_diagnosis_resolution_protocol_2026-07-14.md).
This section does not retroactively turn the 197 automatic labels into
independent clinical adjudication.
