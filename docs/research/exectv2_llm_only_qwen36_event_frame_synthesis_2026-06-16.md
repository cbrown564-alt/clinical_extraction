# ExECTv2 LLM-Only Qwen Event-Frame Synthesis

Date: 2026-06-16

Status: development synthesis, not completion evidence. The `llm_only` target
remains unmet until the approach clears a meaningful promotion gate beyond small
prefix slices, and ultimately the full dev140 gate.

## Scope

This note records the Qwen 3.6:35b `llm_only` event-frame branch that followed
the v0.15 dev140 failure analysis:

- Dev140 failure ledger:
  `experiments/exectv2_llm_only_clinical_findings_v15_dev140_item_error_analysis_20260616.md`
- Machine-readable companion:
  `experiments/exectv2_llm_only_clinical_findings_v15_dev140_item_error_analysis_20260616.json`
- Active implementation:
  `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/llm_only_clinical_findings.py`
- Focused tests:
  `tests/test_exectv2_llm_only_clinical_findings.py`

The work is intentionally kept inside the Gan-style ontology:

- `llm_only`: Qwen owns prediction-bearing clinical facts, target/non-target
  status, statement family, phrase scope, counts, denominator, temporality, and
  final findings.
- Deterministic code is limited to JSON/schema compatibility, exact evidence
  substring checks, format projection from already emitted fields, finite CUI
  projection from the model-emitted phrase, reporting, and scoring.
- Deterministic candidate selection, semantic normalization, or deterministic
  final selection would move this into the `hybrid` workstream and is not used
  as success evidence here.

## Why The Branch Changed

v0.15 had a promising dev25 prefix result but collapsed on dev140:

| Run | Rows | Strict SF F1 | Phrase F1 | Parse | Verifier Parse | Evidence Validity |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| v0.15 hard-negative verifier | 140 | 0.3045 | 0.4882 | 0 | 4 | 0.9557 |

The item-level failure analysis showed that the problem was not primarily CUI
normalization. Phrase-only F1 was also poor, and same-phrase attribute conflicts
clustered around clinical event-frame attributes: `TimeSince_or_TimeOfEvent`,
`NumberOfSeizures`, `NumberOfTimePeriods`, `TimePeriod`, and `PointInTime`.

The immediate lesson was to stop adding a longer bag of examples and make Qwen
build an explicit clinical event frame before emitting ExECT mentions.

## Experiments Run

All live runs used:

- Model: `ollama_chat/qwen3.6:35b`
- API base: `http://localhost:11434`
- Temperature: `0`
- DSPy cache: disabled
- Thinking mode: disabled by the repo's Ollama/LiteLLM configuration

| Version / Artifact | Rows | What Changed | Strict SF F1 | Phrase F1 | Notes |
| --- | ---: | --- | ---: | ---: | --- |
| v0.16 family checklist | 25 | Boolean model-owned checklist before findings | 0.6154 | 0.7077 | Regressed from v0.15 dev25; rejected as a shape. |
| v0.17 event-frame dev1 | 1 | Replaced checklist with model-owned `event_frames` | 0.5000 | 0.5000 | Operational but over-copied `focal seizures without change in awareness` into phrase. |
| v0.18 event-frame dev1 | 1 | Added phrase-scope event-frame guidance | 1.0000 | 1.0000 | Recovered row EA0002. |
| v0.18 live dev5 | 5 | First event-frame dev5 smoke | 0.8421 | 0.8421 | Right clinical content was partly lost to schema parse failures. |
| v0.18 same-raw reparse dev5 | 5 | Reparsed saved raw output after schema tolerance | 0.9565 | 0.9565 | Diagnostic only; same raw outputs showed parser tolerance mattered. |
| v0.18 schema-tolerant live dev5 | 5 | Fresh live run with schema tolerance | 0.9565 | 0.9565 | No parse failures; one FP from bare `remains seizure free`. |
| v0.19 live dev5 | 5 | Added unanchored seizure-free boundary | 0.9524 | 0.9524 | Removed the FP; one FN from missing compact+narrative duplicate. |
| v0.19 live dev10 | 10 | Larger prefix smoke | 0.8780 | 0.8780 | No first-pass parse failures; evidence validity 1.0; verifier parse failures persisted on 3 rows. |
| v0.19 live dev25 partial | 2 | Interrupted dev25 run checkpoint | 1.0000 | 1.0000 | Partial 2-row artifact only; not promotion evidence. |

Primary artifacts:

- `experiments/exectv2_llm_only_clinical_findings_v19_event_frame_live_dev5_qwen36_35b_20260616.jsonl`
- `experiments/exectv2_llm_only_clinical_findings_v19_event_frame_live_dev5_qwen36_35b_20260616.md`
- `experiments/exectv2_llm_only_clinical_findings_v19_event_frame_live_dev10_qwen36_35b_20260616.jsonl`
- `experiments/exectv2_llm_only_clinical_findings_v19_event_frame_live_dev10_qwen36_35b_20260616.md`

Verification:

- `uv run python -m pytest tests\test_exectv2_llm_only_clinical_findings.py`
  passed `38/38`.
- `uv run ruff check src\clinical_extraction\tasks\epilepsy_phenotyping\exectv2\llm\llm_only_clinical_findings.py tests\test_exectv2_llm_only_clinical_findings.py`
  passed.

## Key Findings

### 1. Event Frames Are A Better LLM-Only Substrate Than Checklist Flags

The v0.16 checklist branch asked Qwen to produce note-level family flags such as
`has_current_rate`, `has_dated_count`, and `has_cluster`. That was model-owned,
but too lossy. It told the verifier that a family existed without forcing Qwen
to name the evidence, phrase, count, denominator, time relation, and target
status for each fact.

The event-frame branch makes Qwen emit a compact clinical frame:

- exact evidence
- seizure phrase
- target status
- statement family
- source role
- count/range
- denominator
- time relation
- anchor/date
- inclusion decision
- rationale

This directly targets the v0.15 dev140 error analysis, where strict failures
were mostly event-frame construction failures rather than CUI lookup failures.

### 2. The Event-Frame Branch Improved Prefix Performance, But Prefix Success Is Not Enough

v0.19 dev10 strict F1 reached `0.8780`, well above the `0.7` threshold on that
small slice. This is materially better than v0.15 dev140 and better than the
failed v0.16 dev25 branch.

However, v0.15 already taught that prefix performance can be misleading:
v0.15 dev25 was `0.724`, then dev140 collapsed to `0.3045`. Therefore v0.19
dev10 is useful mechanism evidence, not completion evidence.

The interrupted v0.19 dev25 run only completed 2 rows. That checkpoint is not a
valid promotion result.

### 3. Schema Tolerance Was Legitimate And Important

The v0.18 dev5 run had a low headline (`0.8421`) partly because Qwen produced
clinically useful output that failed schema validation:

- event-frame `statement_family` included audit-only names such as
  `family_history`;
- verifier `findings_to_add` sometimes contained event-frame-shaped objects
  rather than finding-shaped objects.

The parser was changed in format-only ways:

- event-frame `statement_family` became tolerant because event frames are audit
  substrate, not scored ExECT attributes;
- malformed `findings_to_add` entries missing `text` and `clinical_kind` are
  dropped instead of being converted into findings.

This is not deterministic semantic repair. It does not select a clinical fact or
turn an event frame into a scored mention. The same-raw-output reparse is marked
diagnostic for that reason.

### 4. CUI Projection Is Not The Active Limiter On The SF Branch

For the event-frame branch, phrase-only, semantic, and CUI-projected benchmark
scores are identical on the successful prefix runs. The finite SF CUI lookup is
doing its intended benchmark-format job. The remaining errors are phrase scope,
duplicate fact recall, and clinical statement-family boundaries.

### 5. The Remaining Errors Are Clinically Meaningful, Not Random

The v0.19 dev10 failures concentrated in a few interpretable families:

- Compact+narrative duplicate recall: Qwen kept a compact dated count but missed
  the repeated narrative count on EA0006.
- Returned-seizure phrase surface: Qwen emitted `seizures` for a
  `FrequencyChange=Increased` mention where the gold phrase was singular
  `seizure`.
- Focal-to-bilateral / convulsive last-event framing: Qwen missed some duplicate
  and variant last-event mentions on EA0011.
- Verifier schema fragility remains: dev10 had verifier parse failures on three
  rows, although first-pass parsing was clean and final scoring still used the
  first-pass findings.

These are exactly the kinds of families the next gate should inspect, rather
than only reading a scalar F1.

## Interpretation

The event-frame branch is the first `llm_only` shape in this sequence that looks
architecturally aligned with the dev140 error analysis:

- Qwen is forced to enumerate the clinical event unit before producing ExECT
  mentions.
- The event frame creates an inspectable distinction between coverage failure,
  target-selection failure, phrase-scope failure, attribute failure, and
  projection failure.
- Deterministic code remains non-semantic: it validates, projects, records, and
  scores, but does not choose candidates.

The main risk is that event frames may simply make Qwen more verbose on easy
prefix rows without solving the distribution shift that destroyed v0.15 dev140.
The dev10 result is encouraging, but not yet enough. The right next evidence is
a completed dev25 and then a dev140 gate with item-level slices.

## Distilled Insights

1. **Use event frames, not booleans.** A note-level checklist can say a family is
   present, but it cannot localize whether the miss was phrase, denominator,
   date, target status, or evidence.

2. **Keep attribution clean.** Schema tolerance is acceptable when it preserves
   Qwen's selected facts. Deterministic conversion from event frames to scored
   findings is not acceptable for this `llm_only` goal.

3. **Do not trust prefix wins.** v0.19 dev10 `0.8780` is promising, but v0.15
   already demonstrated that small-prefix success can collapse on dev140.

4. **Phrase and attribute failures should be reported separately.** Matching
   phrase-only and strict scores on v0.19 prefix runs means the immediate prefix
   misses are phrase/fact inventory issues, not hidden attribute/CUI issues.

5. **Verifier outputs need their own quality gate.** A verifier can remove
   false positives, but parse failures and malformed additions can silently
   change recall. The report should continue tracking verifier parse failures
   and malformed addition drops.

6. **Clinical boundaries should be expressed as transferable event-frame
   principles.** The useful additions were not row IDs or deterministic repairs;
   they were rules like: separate awareness context from seizure phrase, do not
   score bare unanchored `remains seizure free`, keep historical compact facts
   distinct from current control, and keep non-target episodes out of findings.

## Next Gate

The next run should not be another dev5/dev10 prompt tweak. It should be:

1. Finish v0.19 or successor on dev25 with per-row checkpoints.
2. Produce an item-level dev25 failure ledger, especially for duplicate facts,
   focal-to-bilateral variants, frequency-change phrase surface, and verifier
   parse failures.
3. Only if dev25 remains above `0.7` with interpretable errors, run dev140.
4. Treat success as unproven until dev140 strict `sf_benchmark` per-item F1
   exceeds `0.7` without deterministic candidate selection or semantic repair.

