# ExECTv2 SF LLM-Only Qwen 3.6:35B Plan

Date: 2026-06-15
Status: development plan plus initial `llm_only` prototype. Corrected on
2026-06-16 to separate the prior hybrid evidence-rendering attempt from the
active `llm_only` goal. Dev split only. This is not a full-200 or test
authorization.

Objective: build an ExECTv2 SeizureFrequency `llm_only` system using
`ollama_chat/qwen3.6:35b` that exceeds `0.700` strict per-item F1 on the
`exectv2_split_v1` dev140 surface, while preserving the Gan 2026 architecture
taxonomy and attribution discipline.

## 1. Architecture Taxonomy

Use the same architecture families as Gan 2026. ExECTv2 reports may call the
rules-only family `deterministic`, but the ownership rule is the same:

| Family | Prediction-bearing source | ExECTv2 implication |
| --- | --- | --- |
| `deterministic` / `rules_only` | deterministic rules produce clinical mentions and attributes | Current deterministic SF pipeline. |
| `llm_only` | the LLM produces every clinical mention or finding that can affect the score | Qwen must decide mention text, evidence, count/range/window/change/date, and duplicate mentions. |
| `hybrid` | deterministic and LLM components both contribute semantic behavior | Any run where deterministic rules extract, select, repair, or render clinical facts after an LLM step. |

The prior Qwen-selected-evidence replay must be labelled `hybrid`, not
`llm_only`. It asks Qwen to choose evidence, then runs the deterministic SF
extractor over that evidence. Because deterministic rules introduce anchors,
attributes, projection aliases, and semantic mentions, the final clinical facts
are primarily deterministic.

## 2. Allowed Determinism For This Goal

Allowed in `llm_only`:

- JSON extraction, schema validation, and parse diagnostics.
- Exact evidence substring checks and evidence-validity reporting.
- Format-only normalization of values the model already emitted, such as
  whitespace, case, quote stripping, `Last_Clinic` to `LastClinic`, named month
  to `MonthDate=3`, and word-number to the benchmark's numeric spelling.
- CUI projection from an LLM-emitted concept phrase through a finite
  phrase-to-CUI lexicon, reported as `benchmark_format`, because it normalizes
  the model's selected concept rather than selecting a clinical fact.
- Scoring projections from model-owned clinically meaningful fields into
  ExECTv2 attribute keys.

Not allowed in `llm_only`:

- Deterministic candidate generation.
- Deterministic candidate selection or fallback.
- Running deterministic anchor/rate/statement/frequency-section rules over the
  note or over model-selected evidence.
- Semantically changing repair, such as adding a missing count/window/date,
  changing the selected anchor, choosing a different event, splitting/merging
  mentions, or suppressing a model-emitted clinical mention based on a clinical
  rule.
- Projection aliases that create new clinically distinct mention surfaces or
  attributes not emitted by the model.

Any result that uses those disallowed operations belongs to a separate
`hybrid` workstream, even if the LLM is involved.

## 3. Candidate Shape

Build `exectv2_llm_only_sf_qwen36_clinical_findings_v0`.

Qwen emits a list of source-near clinical findings. Each finding is still
model-owned, but easier to project than the current free-form attribute dict:

```json
{
  "findings": [
    {
      "text": "focal seizures",
      "evidence": "In March she had 2 to 3 of her focal seizures",
      "clinical_kind": "frequency_rate",
      "count_low": "2",
      "count_high": "3",
      "period_low": null,
      "period_high": null,
      "period_unit": null,
      "time_relation": "during",
      "point_in_time": null,
      "day": null,
      "month": "March",
      "year": null,
      "frequency_change": null,
      "confidence": "high",
      "rationale": "The note states 2 to 3 focal seizures in March."
    }
  ]
}
```

The deterministic projection layer may map this to:

- `LowerNumberOfSeizures=2`, `UpperNumberOfSeizures=3`;
- `MonthDate=3`;
- `TimeSince_or_TimeOfEvent=During`;
- `CUI` and `CUIPhrase` from the model-emitted `text`.

It may not infer missing fields from the evidence if Qwen omitted them.

## 4. Clinically Meaningful Prompt Rules

Prompt rules should be transferable and stated clinically, not as benchmark
tricks:

- Extract every distinct seizure-frequency statement, including header and
  narrative restatements when both are present.
- Preserve the seizure type as a short source phrase; put the full clause in
  evidence.
- Treat seizure-free as a current zero-event state only when the note asserts
  current absence of seizures.
- Treat last-event-only evidence as a dated event, not automatically a
  recurrent frequency.
- For count-plus-date statements, emit the count and calendar date rather than
  converting the year into a denominator.
- For `since last clinic` and medication-change statements, emit the clinical
  point in time explicitly.
- For ranges, preserve low and high values.
- For period gaps such as `every 3 to 4 weeks`, emit one event over a period
  range.
- Preserve repeated mentions and repeated gold-like statements; do not collapse
  duplicate clinical facts unless the text clearly refers to the same single
  statement.

These are `clinical_epilepsy` or `seizure_frequency` prompt policies. CUI
assignment and ExECTv2 key spelling remain `benchmark_format`.

## 5. Attribution Ladder

Every saved run must report these layers on the same raw Qwen output:

| Layer | Deterministic behavior | Purpose |
| --- | --- | --- |
| `raw_model_mentions` | parse only | What Qwen literally selected and filled. |
| `schema_valid_mentions` | schema validation, invalid field drop | Transport health. |
| `format_projected_mentions` | only value spelling and scorer-key projection from emitted fields | LLM-only scoring candidate. |
| `cui_projected_mentions` | phrase-to-CUI projection only | Benchmark with-CUI cell. |
| `hybrid_rendered_from_evidence` | deterministic extractor over selected evidence | Diagnostic only; always labelled `hybrid`. |

Threshold success can only be claimed from `format_projected_mentions` or
`cui_projected_mentions` if the projection did not add or choose clinical facts.
If only `hybrid_rendered_from_evidence` crosses `0.700`, the LLM-only goal is
not met.

## 6. Experiment Ladder

1. **Plan and tests.** Add contract tests proving the projection layer cannot add
   a count/window/date/anchor that Qwen did not emit, and that CUI projection is
   reported separately.
2. **Prompt-only smoke.** Ensure no internal architecture vocabulary leaks into
   the prompt, and the JSON schema is clear for Qwen.
3. **Live dev5.** Use `ollama_chat/qwen3.6:35b`, `api_base=http://localhost:11434`,
   temperature `0`, thinking disabled by the shared Ollama route. Stop on parse
   or evidence failures before scoring claims.
4. **Live dev25.** Promotion gate: no call failures, parse/schema failures below
   5 percent, evidence validity above 90 percent, and strict per-item F1 moving
   materially above the current raw Qwen semantic baseline.
5. **Hard-slice dev panel.** Include known hard families from the deterministic
   findings: date/count statements, frequency-section rows, period ranges,
   seizure-free/control statements, last-event/date statements, and repeated
   header plus narrative mentions.
6. **Live dev140.** Claim success only if `cui_projected_mentions` strict
   per-item F1 is `>0.700`, with the attribution ladder showing that score does
   not depend on semantic deterministic repair.

## 7. Stop Rules

- Stop and revise if Qwen continues to rewrite anchors into non-gold phrase
  surfaces and phrase-only F1 remains below deterministic by more than 10 points.
- Stop and revise if strict F1 improves only through semantic projection, new
  deterministic aliases, or deterministic evidence rendering.
- Stop expanding prompt examples if dev25 improvements come from memorizing
  dataset-specific phrase conventions rather than transferable clinical rules.
- Reclassify as `hybrid` immediately if deterministic code selects, repairs, or
  suppresses prediction-bearing clinical facts.

## 8. Expected Deliverables

- New ExECTv2 runner or config named with the `llm_only` family prefix.
- Unit tests for projection boundaries and architecture-family classification.
- Dev run artifacts with Qwen model metadata: tag, digest
  `07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522`,
  parameter size `36.0B`, quantization `Q4_K_M`, native Ollama chat route,
  `think=false`, temperature `0`, cache state, and row count.
- Report table comparing `deterministic`, prior raw `llm_only`, new `llm_only`,
  and the diagnostic `hybrid_rendered_from_evidence` workstream without
  conflating their claims.

Bottom line: the path to an acceptable `llm_only` result is not to let
deterministic rules rescue Qwen-selected text. It is to make Qwen emit complete,
source-near clinical findings, then restrict deterministic code to transparent
scorer projection and CUI normalization over those already selected findings.

## 9. 2026-06-15 Prototype Status

Implemented `exectv2_llm_only_clinical_findings` as a new `llm_only` config:

- Runner: `run_llm_only_sf --config clinical_findings`.
- Prompt version: `exectv2_llm_only_sf_clinical_findings_v0.3`.
- Pipeline family: `exectv2_llm_only_clinical_findings`, mapped to
  `llm_only` in the ExECTv2 three-way report and audit runner.
- Attribution layers: raw model findings, format-projected mentions, and
  CUI-projected mentions.
- Tests pin prompt hygiene, evidence validation, no evidence-mining projection,
  CUI projection separation, dated-count projection, recurrence interval
  projection, last-event projection, and architecture-family classification.

Local Qwen route:

- Native Ollama chat smoke passed for `qwen3.6:35b` with `think=false`.
- DSPy/LiteLLM route passed through `ollama_chat/qwen3.6:35b`,
  `api_base=http://localhost:11434`, `temperature=0`, `--no-dspy-cache`.

Initial live dev results:

| Run | Prompt | Letters | Phrase per-item F1 | Strict per-item F1 | Notes |
| --- | --- | ---: | ---: | ---: | --- |
| `dev1` | v0.1 | 1 | 1.000 | 0.500 | Misread dated count as monthly rate. |
| `dev1` | v0.2 plus dated-count projection | 1 | 1.000 | 1.000 | Dated-count row fixed. |
| `dev5` | v0.2 plus dated-count projection | 5 | 0.632 | 0.316 | Low recall and interval/count misses. |
| `dev5` | v0.3 | 5 | 0.762 | 0.476 | Better section recall, still far below target. |
| `dev5` | v0.6 | 5 | 0.917 | 0.833 | Statement typing plus format projections cleared the tiny prefix. |
| `dev25` | v0.6 | 25 | 0.556 | 0.389 | Prefix gain did not generalize; many non-target false positives. |
| `dev10` | v0.8 | 10 | 0.769 | 0.718 | Age fields and negative clinical rules cleared the next small gate. |
| `dev25` | v0.8 | 25 | 0.625 | 0.531 | Better than v0.6 but still far below the >0.700 target. |
| `dev5` | v0.8 decision verifier | 5 | 0.900 | 0.900 | Qwen-owned edit pass removed/kept/revised findings without deterministic selection. |
| `dev10` | v0.8 decision verifier | 10 | 0.842 | 0.737 | Cleared target on dev10 with no parse or call failures. |
| `dev25` | v0.8 decision verifier | 25 | 0.710 | 0.581 | Improved phrase precision, still below target; verifier was too conservative. |

Current residuals are model-owned clinical omissions or choices, not acceptable
places for deterministic rescue in the `llm_only` workstream:

- Header facts such as `several seizures since the last clinic appointment`
  are found, but Qwen sometimes omits `time_relation=since` and
  `point_in_time=last clinic`.
- Vague counts still drift: Qwen may emit a range for `few seizures per year`
  instead of the single guideline count.
- Narrative generic `seizures` can be over-specialized to the diagnosis seizure
  type, producing a phrase/CUI mismatch.
- Section/prose duplicate facts are often collapsed into one prediction.
- Current `remains seizure free` without duration/date/anchor can appear as a
  false positive despite prompt guidance.

The v0.8 prototype added model-owned statement typing, source-role labels,
age-bound fields, current-zero-vs-non-target control distinction, and strictly
bounded format projections:

- equal count bounds collapse to a single count;
- equal/single-sided period bounds collapse to a single period count;
- `fortnight` is projected as two weeks;
- unanchored `since` on a generic background rate is dropped;
- model-emitted age bounds project to `AgeLower`, `AgeUpper`, and `AgeUnit`;
- model-emitted `current_control_no_duration` observations are preserved in
  raw output but excluded from scored predictions because Qwen explicitly marked
  them as non-target observations.

Residual v0.8 dev25 failure families:

- Target selection: Qwen still extracts non-target events such as single focal
  seizure diagnostic encounters, minor seizures, jerks, dissociative/blackout
  language, and loss-of-consciousness episodes in gold-empty rows.
- Phrase anchoring: Qwen still over-specializes generic `seizures` to diagnosis
  labels in some narrative rates, and it misses typo/variant anchors such as
  `generalised tonic chronic seizures`.
- Cluster decomposition: Qwen often emits the `seizures` rate in a cluster
  sentence but misses the separate `cluster of seizures` mention.
- Current control: Qwen inconsistently separates scored `no further seizures`
  from non-target vague `epilepsy under control` statements.
- Duplicate/parallel mentions improved on the first 10 rows but remain a
  likely recall risk.

Next llm_only escalation should therefore focus on Qwen-owned target selection,
not more deterministic projection:

1. Add a self-check field such as `frequency_statement_type` and require Qwen to
   classify `header_count_since_anchor`, `calendar_count`, `recurrence_interval`,
   `last_event_date`, `background_rate`, and `current_control_no_duration`
   before filling fields.
2. Require Qwen to emit one `source_role` per finding (`compact_section`,
   `narrative`, or `both`) and to duplicate findings when both section and
   narrative contain separately annotatable statements.
3. Add a model-only verification pass, still using Qwen 3.6:35B, that receives
   the note plus Qwen's raw findings and returns a final scored `findings` list
   after explicitly checking target status, generic-vs-specific anchor wording,
   cluster decomposition, current-zero eligibility, and duplicate compact/narrative
   mentions. This remains `llm_only` only if final selection is Qwen-owned and
   deterministic code performs no candidate selection or semantic repair.
4. Run dev10/dev25 only after the verification pass shows fewer false positives
   on gold-empty/non-target rows without lowering evidence validity.
5. Keep the prior Qwen-selected-evidence plus deterministic rendering result in
   the `hybrid` workstream only.

## 10. Decision Verifier Result

Implemented a second Qwen-owned pass over the first-pass Qwen findings:

- First pass emits `raw_extraction_findings`.
- Verification pass emits `decisions` over zero-based raw finding indexes:
  `keep`, `remove`, or `revise`, plus optional `findings_to_add`.
- Deterministic code only applies Qwen-authored decisions and preserves raw
  numeric/date fields unless Qwen explicitly revises them.
- Final scored layer is still `raw_model_findings`, now meaning the final
  Qwen-owned findings after the decision verifier.

This remains `llm_only` because final selection, removal, phrase correction, and
addition are model-owned. It is not the earlier hybrid evidence replay: no
deterministic extractor, candidate generator, or deterministic semantic selector
runs over the note or evidence.

Decision verifier observations:

- It fixed the first-row anchor regression after adding the clinical distinction
  between `with altered/impaired awareness` and `without change in awareness`.
- It improved dev25 phrase per-item F1 from `0.625` to `0.710`.
- Strict dev25 per-item F1 improved only from `0.531` to `0.581`, so this is
  progress but not success.
- It removed only one raw finding on dev25, despite many gold-empty false
  positives. The verifier is too conservative.

Current dev25 residual families after the decision verifier:

- Non-target false positives remain: `general and complex partial seizures`,
  single focal seizure encounter, minor seizures, loss-of-consciousness episodes,
  generic events, jerks.
- Phrase/CUI variants remain: `generalised tonic chronic seizures`,
  `event on 22 December`, and generic-vs-specific seizure wording.
- Cluster decomposition remains incomplete: the cluster mention and within-cluster
  seizure rate are not both reliably emitted.
- Some gold-empty rows correctly produce no findings, but letter-level precision
  is still dragged down by the remaining non-target rows.

This establishes the boundary for the next move. The verifier may make clinical
decisions only through explicit Qwen-authored `keep`, `remove`, `revise`, or
`add` actions. It is **not** acceptable for deterministic code to map a
diagnostic field such as `target_status=non_target_episode` into removal unless
Qwen also emitted the removal action. A status-only deterministic filter would
be a semantic selector and therefore a `hybrid` result.

Rejected next move for `llm_only`:

1. Make the verifier output a `target_status` for every raw finding
   (`target_epileptic_seizure_frequency`, `non_target_episode`, `history_context_only`,
   `diagnosis_without_frequency`, `future_risk_or_driving`, `uncertain_not_scored`)
   and have deterministic code require `remove` unless the status is target.
2. Use deterministic target-status, candidate-source, or clinical-rule filters
   to suppress Qwen findings.

Acceptable revised move:

1. Keep `target_status` as an explanatory Qwen-owned field only.
2. Require the verifier prompt to make the action explicit: if Qwen believes a
   finding is non-target, it must emit `action=remove`; if it believes a compact
   section or narrative fact is missing, it must emit a full model-owned
   `findings_to_add` record.
3. Add hard negative and hard positive examples using transferable clinical
   categories: migraine frequency, blackout/loss-of-consciousness,
   dissociative/nonepileptic spells, single diagnostic seizure encounter,
   febrile childhood history, medication titration, driving-clearance windows,
   compact seizure-type frequency sections, current seizure-free statements
   coexisting with historical dated seizure counts, and duplicate section plus
   narrative mentions.
4. Keep using dev10 as a smoke gate, but require dev25 strict per-item F1 above
   `0.650` before spending a dev140 run.

## 11. Corrected Workstream Plan

The active goal is **not** to make the hybrid renderer better. It is to build a
Qwen-owned `llm_only` ExECTv2 SeizureFrequency system whose strict per-item F1
exceeds `0.700`. The deterministic SF findings remain valuable as a clinical
rule taxonomy and as a comparator, but not as a candidate source, selector, or
semantic repair layer for the `llm_only` claim.

### 11.1 Workstream labels

| Workstream | Allowed claim | Examples in scope |
| --- | --- | --- |
| `deterministic` / `rules_only` | Deterministic rules solve the clinical extraction problem. | Current ExECTv2 SF rule stack; dev140 strict per-item F1 `0.705`. |
| `llm_only` | Qwen owns the scored clinical finding inventory and all prediction-bearing attributes. | First-pass Qwen finding table, Qwen verifier/finalizer, deterministic JSON/schema/evidence checks, CUI projection from Qwen phrase, and scorer projection from Qwen fields. |
| `hybrid` | Qwen and deterministic rules both affect semantic output. | Qwen-selected evidence rendered by deterministic SF rules; deterministic candidate generation; deterministic target filters; deterministic selection among model findings; deterministic semantic normalizers. |

The current best Qwen `llm_only` result is the decision-verifier prototype,
`dev25` strict per-item F1 `0.581`. It is progress, not success. The earlier
Qwen-selected-evidence plus deterministic rendering line is a `hybrid`
diagnostic and cannot satisfy this goal even if it crosses `0.700`.

### 11.2 LLM-only boundary contract

The next implementation must preserve these boundaries:

- Qwen emits the clinical findings that can score: phrase, evidence,
  statement type, source role, count/range/window, date/age/change attributes,
  and whether each finding is target or non-target.
- Qwen's second pass may keep, remove, revise, or add findings. The action,
  revised phrase, revised attributes, and added records must be present in the
  model output.
- Deterministic code may parse JSON, validate schema, check evidence substrings,
  assign CUI from a Qwen phrase, normalize spelling of already emitted enum
  values, and project Qwen-owned fields into ExECTv2 scorer keys.
- Scoring projections over clinically meaningful model-owned findings are
  acceptable determinism. They are transport from Qwen's typed clinical record
  to benchmark fields, not a clinical decision.
- Deterministic code may not scan the note or evidence to discover missing
  facts, choose a candidate, suppress a finding for clinical reasons, change
  the seizure type, add a missing count/window/date/anchor, or split/merge
  mentions. Those are semantic operations and therefore `hybrid`.

### 11.3 Prompt and schema direction

Use the deterministic findings as a source of **transferable clinical rules**,
not as executable rescue logic. The next Qwen prompt should focus on these
model-owned decisions:

- Compact section recall: seizure-type frequency sections can contain multiple
  annotatable historical facts even when later prose says the patient is
  currently seizure free.
- Current versus historical coexistence: current zero/control statements do not
  erase dated prior seizure counts; Qwen must either emit both target findings
  or explicitly mark the current-control statement as non-scored.
- Target status as explanation, not code policy: Qwen must state why a finding
  is target or non-target and then make the corresponding action itself.
- Generic phrase anchoring: preserve `seizures` when the source says generic
  seizures; use a specific seizure type only when the source phrase supports it.
- Last-event discipline: last-event evidence is a dated event unless the note
  gives an explicit recurrent rate or seizure-free duration.
- Duplicate/parallel facts: compact section and narrative restatement may both
  be annotatable; Qwen must not collapse them solely because they are clinically
  related.
- Non-target hard negatives: blackout, loss of consciousness, dissociative or
  nonepileptic spells, migraine frequency, driving-clearance windows, diagnostic
  history without frequency, febrile childhood history, and medication-change
  context should not become seizure-frequency findings unless the note states
  target epileptic seizure frequency.

### 11.4 Implementation steps

1. **Boundary tests first.** Add or preserve tests proving status fields do not
   deterministically remove findings, projection does not mine evidence for
   missing attributes, CUI assignment is phrase-only, and Qwen-authored verifier
   actions are the only way findings are added/removed/revised.
2. **Artifact relabeling.** Ensure reports and metadata distinguish
   `llm_only`, `deterministic`/`rules_only`, and `hybrid`. Any selected-evidence
   plus deterministic-rendering result should be named and reported only as
   `hybrid`.
3. **Qwen finalizer.** Prefer a full final-findings rewrite or explicit
   action-overlay from Qwen over deterministic post-hoc filters. Save both raw
   first-pass and final Qwen findings for attribution.
4. **Clinically meaningful prompt revision.** Add the compact-section/current
   control coexistence rule, non-target hard negatives, generic phrase anchoring,
   last-event discipline, and duplicate/parallel fact policy as prompt guidance.
   Keep examples generic rather than letter-ID-specific.
5. **Dev ladder.** Run live Qwen with `ollama_chat/qwen3.6:35b`, `think=false`,
   temperature `0`, and cache disabled for fresh comparisons:
   `dev5` for parse/evidence smoke, `dev10` for small-signal F1, `dev25` for
   promotion, and `dev140` only after `dev25` strict per-item F1 is credibly
   above `0.650` and false positives are falling without recall collapse.
6. **Promotion gate.** Claim the goal only if the `llm_only` scored layer, with
   deterministic behavior limited to the allowed envelope above, exceeds
   strict per-item F1 `0.700`. A `hybrid` layer crossing `0.700` is useful but
   does not satisfy this goal.
7. **Failure writeup.** If Qwen stalls below target, record the residual model
   failure families and keep hybrid candidate-selection/renderer work in a
   separate document rather than diluting the `llm_only` claim.

### 11.5 Reporting table to maintain

Every comparison report should keep these rows separate:

| Row | Family | Scored? | Interpretation |
| --- | --- | --- | --- |
| Deterministic SF rules | `deterministic` / `rules_only` | yes | Transparent rule comparator. |
| Qwen raw first pass | `llm_only` | diagnostic | Shows model extraction before verification. |
| Qwen verified/final findings | `llm_only` | yes | Only candidate eligible for this goal. |
| Qwen-selected evidence plus deterministic renderer | `hybrid` | diagnostic or separate scored row | Useful separate workstream, not an `llm_only` success. |
| Deterministic target filter over Qwen findings | `hybrid` | separate only | Semantic deterministic selector; excluded from this goal. |

## 12. 2026-06-16 Qwen-Only Iteration Results

After correcting the workstream boundary, the implementation stayed within the
`llm_only` envelope:

- Qwen first pass emits source-near findings.
- Qwen verifier emits explicit `keep`, `remove`, `revise`, and
  `findings_to_add` decisions.
- Deterministic code parses JSON, checks evidence substrings, assigns CUI from
  Qwen phrases, and projects Qwen-owned fields to ExECTv2 scorer keys.
- No deterministic candidate generation, deterministic target filtering, or
  deterministic semantic repair was added.

Implemented changes:

- Prompt v0.9: calibrated the verifier that historical dated seizure counts,
  dated occurrences, and last-event dates are target ExECTv2 SF facts; current
  control does not erase compact-section historical facts.
- Parser compatibility: added a bounded `ast.literal_eval` fallback for
  Python-literal quote drift in model outputs. This is format-only parsing; the
  Pydantic schema still validates the same model-authored decisions.
- Prompt v0.10: added transferable clinical guidance for previous-event context,
  episode duration versus denominator, cluster decomposition, infrequent
  current wording versus old diagnosis-year counts, and focal seizures without
  awareness-change context.
- Prompt v0.11: tightened Qwen-owned target selection for vague diagnosis-level
  control, diagnostic episode descriptions, minor/nonspecific events, and
  no-further-seizures source wording; added explicit guidance that specific
  seizure-type control after medication increase should be scored as
  `current_zero_no_duration` with `point_in_time=medication change`.

Focused tests:

- `uv run python -m pytest tests\test_exectv2_llm_only_clinical_findings.py`
  -> `32 passed`.
- `uv run ruff check src\clinical_extraction\tasks\epilepsy_phenotyping\exectv2\llm\llm_only_clinical_findings.py tests\test_exectv2_llm_only_clinical_findings.py`
  -> all checks passed.

Live Qwen 3.6:35B results (`ollama_chat/qwen3.6:35b`,
`api_base=http://localhost:11434`, temperature `0`, `think=false`, cache
disabled):

| Run | Strict `sf_benchmark` per-item F1 | Phrase-only per-item F1 | Notes |
| --- | ---: | ---: | --- |
| v0.9 dev5 | 0.818 | 0.818 | Historical compact-section verifier regression fixed, but one verifier parse failure remained. |
| v0.9 dev10 | 0.683 | 0.780 | Below target; parser quote drift and attribute misses. |
| v0.9 saved-output parser replay dev10 | 0.700 | 0.780 | Same raw Qwen outputs; parser fallback removed verifier parse failure. Diagnostic tie only, not success. |
| v0.10 dev5 | 0.952 | 0.952 | Strong tiny-prefix result after previous-event/cluster/duration guidance. |
| v0.10 dev10 | 0.780 | 0.780 | Cleared dev10. |
| v0.10 dev25 | 0.603 | 0.635 | Failed promotion; precision collapsed on gold-empty/non-target rows. |
| v0.11 dev5 | 0.909 | 0.909 | Stricter non-target guidance preserved tiny-prefix performance. |
| v0.11 dev10 | 0.829 | 0.829 | Best dev10 result so far. |
| v0.11 dev25 | 0.677 | 0.710 | Improved over v0.10 but still below strict `>0.700`; goal not met. |

Current best strict `llm_only` score on the meaningful promotion slice is
v0.11 dev25 `sf_benchmark` per-item F1 `0.677` (`P=0.677`, `R=0.677`, `21/10/10`).
Phrase-only v0.11 dev25 reaches `0.710`, showing Qwen's phrase inventory is now
near the threshold, but strict attributes and target selection still fall short.

Residual v0.11 dev25 families:

- Duplicate compact-section facts: Qwen keeps the compact GTC/absence facts but
  does not duplicate gold's repeated GTC mention.
- Non-target false positives: vague ongoing seizures without a count/date,
  minor/nonspecific seizure-like episodes, and suspected diagnostic episodes
  still sometimes survive Qwen verification.
- Generic-vs-specific anchoring: Qwen still over-specializes generic
  `seizures` to diagnosis-level seizure types on rows such as `15 seizures over
  4 months`.
- Current zero wording: `has not had any further seizures` sometimes becomes
  `seizure free`, causing phrase/CUI mismatch.
- Point-in-time/date attributes: recent single events can miss `Last_Week` or
  mis-handle last-event/free-duration distinction.
- Frequency-change recall: Qwen still misses some `FrequencyChange=Increased`,
  `Frequent`, or `Infrequent` rows, especially when intertwined with narrative
  history or medication-change context.

Next aligned move:

1. Keep v0.11 as the current front-runner but do not claim success.
2. Build a Qwen-owned final-findings rewrite variant, rather than an action
   overlay, so the verifier can correct numeric/date/period fields without
   deterministic repair.
3. Add a dev25 hard-slice prompt panel around the residual families above:
   generic count-over-window, no-further-seizures wording, suspected episode
   diagnostic descriptions, minor/nonspecific events, medication-change control,
   and frequency-change-only mentions.
4. Use saved-output analysis only for parser/format attribution. Any semantic
   improvement must come from a fresh Qwen-owned final output or be labelled
   `hybrid`.
