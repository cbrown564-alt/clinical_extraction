# Gan 2026 Qwen36 35B Validation250 Three-Pipeline Research Report

Date: 2026-06-02

This is validation-split development analysis on `gan2026_split_v1`. It is not
a held-out benchmark result.

## Compared Artifacts

- Structured-events:
  `experiments/gan2026_llm_only_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`
- Structured-events error analysis:
  `experiments/gan2026_llm_only_structured_events_validation250_qwen36_35b_max5000_overnight_2026-06-01_error_analysis.md`
- Minimal evidence selector:
  `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`
- Minimal evidence selector error analysis:
  `experiments/gan2026_llm_only_minimal_evidence_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01_error_analysis.md`
- Claim-table selector:
  `experiments/gan2026_llm_only_claim_table_selector_validation250_qwen36_35b_max5000_overnight_2026-06-01.jsonl`

All three runs used `ollama_chat/qwen3.6:35b`, `temperature=0.0`,
`max_tokens=5000`, `think=false`, live mode, and no DSPy cache reuse.

## Executive Read

The three Qwen runs answer a useful design question: Qwen does not need the
schema to be collapsed to a minimal source-near answer. It needs robust
non-semantic schema/dialect repair and tighter output-shape constraints.

The structured-events run is the strongest direction. As scored, it reaches
152 / 250 Purist and 155 / 250 Pragmatic, but that score is dominated by 83
Python-literal JSON dialect failures. The existing error analysis shows that
an oracle format-only pass can salvage all 83 parser-blocked outputs, and 79 of
those 83 become Purist-correct. That implies an approximate content-level
Purist score of 231 / 250, or 0.924, after format repair.

The minimal evidence selector is contract-stable and evidence-stable, but it is
too weak as a prediction boundary. It gets 249 / 250 minimal records with
249 / 250 exact answer evidence, but the source-near answer text needs massive
downstream interpretation. Frozen clean scorer-facing repair reaches 193 / 250
Purist, far below the structured-events oracle-salvage estimate.

The claim-table selector v5 is not viable for Qwen in its current form. It ran
all 250 rows but produced 0 / 250 schema-valid claim-table records and 0 / 250
score at all layers. This is not a call failure. It is a systematic output
contract failure: most raw outputs are Python-dict-like and often contain the
right clinical concepts, but the model drifts across alternate field names,
nested shapes, and selector forms. Even an oracle `ast.literal_eval` to JSON
conversion makes only 9 / 250 rows pass the current v5 parser.

## Score And Contract Summary

| Pipeline | Contract records | Parse/schema failures | Best scored Purist | Best scored Pragmatic | Main interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| Structured-events v0.5 | 167 / 250 | 83 blocking invalid JSON rows | 152 / 250 as scored | 155 / 250 as scored | Strong content, weak strict JSON compliance |
| Structured-events v0.5 with oracle format salvage | 250 / 250 | 0 after oracle dialect conversion | 231 / 250 estimated | not recomputed in this report | Best evidence of Qwen clinical capability |
| Minimal evidence selector v2 | 249 / 250 | 1 | 193 / 250 clean | 194 / 250 clean | Stable contract, weak prediction boundary |
| Claim-table selector v5 | 0 / 250 | 250 | 0 / 250 | 0 / 250 | Schema/shape collapse |
| Claim-table v5 with oracle Python-literal conversion | 9 / 250 | 241 still schema-invalid | 9 / 250 clean | 9 / 250 clean | Dialect repair alone is insufficient |

## Evidence Behavior

| Pipeline | Exact evidence result | Interpretation |
| --- | ---: | --- |
| Structured-events as scored | 151 / 250 selected evidence exact | Suppressed by parse failures |
| Structured-events with oracle format salvage | 223 / 250 selected evidence exact | Strong evidence content when dialect is accepted |
| Minimal evidence selector | 249 / 250 answer evidence exact; 482 / 485 supporting facts exact | Excellent evidence copying |
| Claim-table selector as scored | 0 / 250 final evidence exact; 0 / 0 claim evidence | No schema-valid records |
| Claim-table after oracle Python-literal conversion | 9 schema-valid rows; 10 / 10 claim evidence exact inside those rows | Some content exists, but shape drift prevents audit |

The minimal evidence selector wins on raw evidence-substring compliance, but
that is not enough for this benchmark. The task needs a model boundary that
captures clinical structure and a parser-ready or reliably repairable final
answer. Structured-events is the better compromise.

## Runtime Proxy

No explicit timing metadata was present for these historical runs, so these are
filesystem timestamp proxies, not guaranteed wall-clock measurements.

| Pipeline | Timestamp span | Approx duration | Approx seconds/row |
| --- | ---: | ---: | ---: |
| Structured-events | 2026-06-02 00:14:40 to 05:43:58 | 5h 29m 18s | 79.0 |
| Minimal evidence selector | 2026-06-02 05:49:49 to 08:05:59 | 2h 16m 10s | 32.7 |
| Claim-table selector | 2026-06-02 08:53:55 to 23:29:18 | 14h 35m 23s | 210.1 |

The claim-table run is both the slowest and the least usable. That matters:
even if future repair recovered more rows, the current v5 surface is expensive
for Qwen and unstable.

Future CLI runs now record explicit `run_started_at_utc`,
`run_finished_at_utc`, `elapsed_seconds`, `rows_per_second`, and
`seconds_per_row`, so this proxy should not be needed again.

## Structured-Events Findings

The structured-events artifact is the key result. The as-scored report shows:

- Structured records: 167 / 250.
- Parse/schema/label issues: 83.
- Exact selection evidence substrings: 151 / 250.
- Purist score: 152 / 250.
- Pragmatic score: 155 / 250.

The dedicated error analysis reframes those numbers:

- All 83 parser-blocked rows are Python-literal style objects with
  single-quoted keys or strings.
- 55 of those 83 also contain Python `None`.
- An oracle format-only conversion salvages 83 / 83 rows to structured records.
- 79 / 83 parser-blocked rows become Purist-correct after salvage.
- Structured rows only score 152 / 167, or 0.910 Purist.
- Estimated content-level score after oracle format repair is 231 / 250, or
  0.924 Purist.

This is the strongest evidence that Qwen's clinical extraction content is good
enough to keep a meaningful structured schema. The failure is mostly
serialization dialect, not reasoning.

The remaining content-level structured-events errors are specific and tractable:

- Temporal precedence between recent burden and later no-event windows.
- Seizure-free duration versus sparse frequency repair.
- Count/window arithmetic in event lists and recent-window counts.
- Unknown/no-reference/unresolved-multiple policy boundaries.
- Idioms such as `fortnight` and source-near range phrases.

These are real clinical/normalization problems, but they are a much smaller
set than the raw 98 as-scored errors suggest.

## Minimal Evidence Findings

The minimal evidence selector did exactly what it was designed to do: it made
Qwen produce a simple, mostly valid, evidence-grounded object.

Strengths:

- Minimal records: 249 / 250.
- Invalid JSON failures: 0.
- Schema failures: 1.
- Exact answer evidence: 249 / 250.
- Exact supporting-fact evidence: 482 / 485.

Weaknesses:

- Raw source-near answer score: 12 / 250 Purist.
- Strict-format score: 56 / 250 Purist.
- Frozen clean scorer-facing score: 193 / 250 Purist.
- Rows changed by downstream repair layers: 240.
- 37 rows are scorer-correct semantic-boundary mismatches.

The residual clean errors are dominated by representation-boundary failures:

- 32 seizure-free gold rows collapse to `no seizure frequency reference`.
- 11 counted-window rows remain non-parser-ready.
- Additional errors involve vague/abbreviated surfaces, cadence surfaces, and
  clean-repair fallback to unknown.

Interpretation: the minimal contract is useful as a JSON/evidence transfer
smoke, but it pushes too much benchmark-specific normalization out of the model
boundary. It is simpler than Qwen needs and weaker than the structured-events
schema once dialect repair is admitted.

## Claim-Table Findings

The claim-table selector v5 is the negative control in this comparison.

As scored:

- Structured claim-table records: 0 / 250.
- Parse/schema/label issues: 250.
- Exact selected final evidence substrings: 0 / 250.
- Raw, strict-format, and clean scorer-facing scores: 0 / 250.

Raw-output inspection shows three distinct problems:

1. JSON dialect failure.

Most rows are Python-dict-like rather than strict JSON. An oracle
`ast.literal_eval` parses 237 / 250 raw outputs.

2. Shape drift beyond dialect.

After converting those 237 Python literals to JSON, only 9 / 250 rows satisfy
the current v5 claim-table parser. The rest are still schema-invalid.

3. Field-name and nesting drift.

Observed top-level patterns include:

| Shape pattern after Python-literal parse | Count |
| --- | ---: |
| `claims` plus `final_query` | 211 |
| `claims` without a recognized final query | 21 |
| `claim_table` without a recognized final query | 4 |
| other top-level shape | 1 |

Common drift fields include `claim_text`, `evidence_substring`,
`cluster_axis_state`, `final_selector`, `final_selection`, and selector strings
where the schema expects a final-query object. The model is not simply
returning the right schema with single quotes. It is improvising adjacent
schemas.

An oracle Python-literal conversion gives:

- 237 / 250 raw outputs parseable as Python literals.
- 9 / 250 schema-valid records after conversion.
- 9 / 250 clean Purist and Pragmatic correct.
- 10 / 10 claim evidence exact among the small schema-valid subset.

Interpretation: claim-table v5 is too large or too unconstrained for Qwen in
this provider path. Its raw content may contain useful clinical facts, but the
shape is not stable enough to score or audit.

## Cross-Pipeline Interpretation

The comparison supports a narrower conclusion than "simplify the schema":

1. Qwen can handle clinically meaningful structured extraction.

The structured-events salvage analysis is the best evidence: once Python-dict
serialization is repaired, almost all parser-blocked rows become usable, and
most are correct.

2. Qwen fails hard when the schema has too many adjacent degrees of freedom.

Claim-table v5 asks for a richer table, several taxonomy fields, and a final
selector. Qwen often returns plausible nearby structures, but not the exact
contract. That is a schema adherence failure, not proof that all structured
schemas are too complex.

3. Minimal evidence is overly conservative.

It prevents most schema failures, but it gives up the model-side structure
needed for parser-ready final labels and benchmark policy states. The result is
stable evidence with weaker scoring.

4. Deterministic repair should target non-semantic dialect and shape errors
first.

The highest-leverage repair is not more clinical inference. It is accepting
Python-literal JSON dialect and applying conservative key/shape aliases where
the intended structured-events schema is otherwise clear.

5. Repair precedence needs safety checks.

Structured-events is promising, but several residual errors are caused or
worsened by deterministic repair overriding a plausible selected label. Repair
should prefer format normalization over semantic replacement unless the
replacement has stronger evidence and preserves kind/window compatibility.

## Recommendation

Promote `llm_only_structured_events` as the Qwen candidate architecture for the
next validation ladder, with explicit schema-repair work before another live
250-row run.

Recommended next changes:

1. Add Python-literal dialect repair to the structured-events parser.

Use `ast.literal_eval` only as an explicit fallback after strict JSON parse
fails, record a `json_dialect_repair` note, and preserve the raw output.

2. Keep the structured-events schema, but harden prompt output instructions.

The prompt should explicitly ban Python literals, single-quoted keys, `None`,
`True`, and `False`; require JSON `null`, `true`, and `false`; and possibly
include a small negative example.

3. Add schema-repair ablation metrics.

Report raw strict JSON score, dialect-repaired score, and semantic-repair score
separately. This will prevent format recovery from being confused with clinical
improvement.

4. Tighten repair precedence.

Do not let dated-sequence, elapsed-anchor, or selected-evidence derivation
override a parser-ready selected final label unless semantic kind, evidence,
and window checks agree.

5. Deprioritize claim-table v5 for Qwen.

Do not spend the next iteration trying to rescue the full claim table. It is
slow and produced broad shape drift. If claim tables remain scientifically
interesting, revisit them later with a smaller schema or constrained decoding,
after structured-events is fully evaluated.

6. Use minimal evidence only as a transfer smoke.

Minimal evidence remains useful for verifying local-model JSON/evidence
behavior, but it should not be the main scoring architecture because it gives
away too much normalization at the model boundary.

## Bottom Line

The best current interpretation is:

Qwen36 35B has enough clinical extraction capability for the structured-events
schema. The main blocker is non-semantic output serialization and limited schema
repair, not excessive schema complexity. The next milestone should be a
structured-events schema-repair replay and then a fresh validation250 run with
timing and repair-layer metrics recorded.
