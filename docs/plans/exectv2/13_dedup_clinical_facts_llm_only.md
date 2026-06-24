# Satellite 13 — De-duplicated Clinical-Fact LLM-Only Extraction (PRIMARY FOCUS)

Parent: [[00_overarching_implementation_plan]]
Status: **active — primary ExECTv2 research focus as of 2026-06-24; Phase 0, Phase 1, Phase 2, Phase 3, and Phase 4 complete; no Phase 5 model rollout promoted because no Phase 4 winner cleared the dev25 gate; post-Phase-4 direction is now explicit deterministic projection taxonomy/pilot work with separate score lines.**
Dev-split only until a separately authorized Phase 7 audit.
Decision basis:
`docs/decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md`,
`docs/decisions/0033-deduplicated-clinical-fact-recovery-is-the-primary-llm-only-target.md`,
`docs/research/qwen_exectv2_llm_only_error_analysis_2026-06-23.md`,
`docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`,
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_error_analysis_2026-06-24.md`,
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_decision_table_prompt_probe_2026-06-24.md`,
`CONTEXT.md` terms: [[Meaning-Preserving Benchmark Projection]],
[[Projection Boundary Violation]], [[Projection Attribution Tag]],
[[Projection-Aware Score Line]], [[Clinical-First Model Output]],
[[Benchmark-Mimicry Guardrail]], [[Deterministic Projection Eligibility]], and
[[Deterministic Projection Rule Taxonomy]].

## Purpose

Every ExECTv2 architecture built so far — LLM-only and hybrid — has tried to
emit the **full ExECTv2 annotation schema**: exact mention text, Certainty,
Negation, DiagCategory, seizure-frequency operands (counts, periods, dates,
states), and per-occurrence multiplicity. The strict benchmark surface that
scores that schema has a hard, model-independent ceiling:

| Route | Model | strict `model_preserving_canonical` F1 (dev140) |
| --- | --- | ---: |
| `single_call_clean_render_ids` (bare LLM-only) | Qwen-3.6 | 0.339 |
| `single_call_clean_render_ids` (bare LLM-only) | GPT-4.1-mini | 0.334 |
| `holistic_finding_assembly_v08` (full hybrid) | GPT-4.1-mini-family | ~0.374 (benchmark raw) |

The 2026-06-23 apples-to-apples control proved this is a property of the
**route/target**, not the model: a single bare call from GPT-4.1-mini and from
Qwen land within `0.005` of each other, and even the full hybrid's own
benchmark-surface score is ~0.37. The "`>0.900`" numbers in the cross-model
closeout are the **`clinical_headline`** (clinical-recovery) surface, which
de-duplicates findings and scores at concept/component level — a different,
legitimate, and (per decision 0027) the *designated headline* target.

The key untested observation: **no system has been designed to emit the
de-duplicated clinical facts directly.** When the existing full-schema LLM-only
output is merely *scored* on the de-dup surface, it nearly doubles (0.33 →
~0.72) for free. This plan makes the de-duplicated clinical-fact surface the
**primary target** and a lean single-prompt LLM-only system the **primary
architecture**, with the goal of clearing `0.900` clinical-recovery F1 with
GPT-4.1-mini and then rolling out to DeepSeek and Qwen.

## 1. Reframing The Workstream

| Axis | Old framing | New primary framing (this plan) |
| --- | --- | --- |
| Primary scored surface | strict benchmark / `model_preserving_canonical` (all attributes, exact text, multiplicity) | **`clinical_headline`** — de-duplicated, concept/component-level clinical facts |
| Primary architecture | rich-schema producers (LLM-only and hybrid) reproducing the full annotation | **single-prompt LLM-only** emitting only de-duplicated clinical facts |
| Rich-schema runs (certainty/negation/operands/multiplicity) | the main pursuit | **comparison points only** — keep 1–2 best dev140 comparators, archive the rest (Phase 1 cleanup) |
| Attribution | model_preserving_canonical with no deterministic rescue | LLM-only remains model-selected facts only; deterministic code may perform tagged meaning-preserving benchmark projection, while hybrid rescue/verifier filtering are separate score lines |

This is consistent with decision 0027 ("clinical-recovery is the ExECTv2
headline; projection is an artifact layer"). It does **not** abandon the strict
benchmark — that remains the paper-comparable number for a future audit — but it
demotes strict-schema *iteration* to a comparison baseline and makes
de-duplicated clinical recovery the thing we actively optimize.

## 2. What We Are Measuring (and Attribution Rules)

The target is the existing **`clinical_headline`** scorer
(`scoring.py`: Diagnosis = `concept_negation`, and `clinical_headline` for
SeizureFrequency, Prescription, Investigations — the same definitions the v08
report uses for its `0.9155` headline). The unit per family:

| Family | Headline unit (what must be recovered, de-duplicated) | Explicitly NOT scored |
| --- | --- | --- |
| Diagnosis | distinct concept + affirmed/negated | Certainty, DiagCategory, exact gold text, duplicate rows |
| SeizureFrequency | one entry per distinct seizure-type + coarse state (active-rate / seizure-free / changed / unknown) | exact counts, periods, dates, multiplicity |
| Prescription | distinct current regimen: drug name + dose + frequency | section-prefixed gold text, rescue/plan nuance beyond current |
| Investigations | distinct modality + performed + result | dates, exact gold text, duplicate modality rows |

**Attribution remains clean (still an LLM-only claim).** Per
`docs/design/llm_repair_attribution_protocol_2026-06-22.md`, the model must
generate and select every scored fact. Deterministic code may only:

- validate that each fact's evidence is an exact source substring;
- perform [[Meaning-Preserving Benchmark Projection]]: map a model-selected
  clinical fact into scorer/headline fields without changing concept identity,
  assertion, temporality, frequency state, negation, or prescription status;
- emit [[Projection Attribution Tag]] values for any deterministic rule that
  changes the scored representation;
- score on `clinical_headline`.

Deterministic code may **not** add a fact the model did not emit, choose a
seizure-frequency state the model omitted, expand ontology companions, or
de-duplicate in a way that rescues a missed concept. These are [[Projection
Boundary Violation]] cases and must be reported only as hybrid rescue or
verifier-filtered score lines, never blended into the LLM-only headline.
De-duplication is the **model's** job in the prompt; the scorer's collapse only
forgives, it does not add.

Reporting now follows [[Projection-Aware Score Line]] discipline:

1. **LLM-only clinical recovery + meaning-preserving projection** — model
   selected every clinical fact; deterministic code only rendered benchmark
   convention.
2. **Hybrid rescue** — deterministic rules or candidates added facts, selected
   missing states, or completed clinically meaningful attributes.
3. **Verifier-filtered** — unsupported model predictions were rejected before
   scoring by a named verifier/guard layer.

## 3. Baseline and Target

Measured dev140 (computed 2026-06-23, Diagnosis headline = `concept_negation`):

| Surface | GPT-4.1-mini | Qwen-3.6 | v08 hybrid (reference) |
| --- | ---: | ---: | ---: |
| strict benchmark | 0.334 | 0.339 | ~0.374 |
| **de-dup `clinical_headline` overall** | **0.713** | **0.725** | **0.9155** |
| └ Diagnosis | 0.653 | 0.673 | 0.909 |
| └ SeizureFrequency | 0.551 | 0.512 | 0.905 |
| └ Prescription | 0.846 | 0.839 | 0.936 |
| └ Investigations | 0.863 | 0.919 | 0.913 |

**Control to beat:** GPT-4.1-mini `0.713` (full-schema output scored on the
de-dup surface). **Target:** `> 0.900` clinical-recovery F1 with a purpose-built
simplified single prompt. **Where the gap lives:** Diagnosis (~0.65) and
SeizureFrequency (~0.55); Prescription and Investigations are already near
target. The two families that must improve are exactly the two the rich-schema
prompt over-constrains and the hybrid closes with focused components.

Hypothesis for why a lean prompt should beat 0.713: the current prompt carries
~80 schema rules; de-dup headline precision is only ~0.70 (≈245 within-letter
false positives from attribute/multiplicity over-emission). Dropping the
attribute burden should cut over-emission (precision) and free model capacity
for Diagnosis enumeration and SF state (recall) — the two gap families.

## 4. Simplified Schema Design

One JSON object, no markdown, evidence-grounded, de-duplicated by the model:

```json
{
  "clinical_facts": [
    {"family": "diagnosis",
     "concept": "<short clinical concept exactly as a source span allows>",
     "negation": "affirmed | negated",
     "evidence": "<exact substring of the letter>"},

    {"family": "seizure_frequency",
     "seizure_type": "<named seizure type, or 'seizures' if generic>",
     "state": "active_rate | seizure_free | changed | unknown",
     "evidence": "<exact substring of the letter>"},

    {"family": "prescription",
     "drug": "<current drug name>",
     "dose": "<number>", "dose_unit": "mg",
     "frequency": "<times per day, e.g. 1, 2, 3>",
     "evidence": "<exact substring of the letter>"},

    {"family": "investigation",
     "modality": "MRI | CT | EEG | telemetry",
     "result": "normal | abnormal | unknown",
     "evidence": "<exact substring of the letter>"}
  ]
}
```

Design rules baked into the prompt:

- **De-duplicate at the source.** Emit each distinct clinical fact once. Do not
  repeat a diagnosis, seizure-type state, drug regimen, or investigation that you
  have already listed.
- **Clinical-first model output.** The model selects source-supported clinical
  facts and attributes; deterministic code owns benchmark rendering and
  projection eligibility.
- **Benchmark-mimicry guardrail.** Do not imitate ExECT phrase boundaries,
  ontology surfaces, or guideline defaults when they conflict with clinical
  meaning. Benchmark quirks belong to tagged deterministic projection.
- **No strict-schema fields.** No Certainty, no DiagCategory, no counts/periods/
  dates, no section labels, no exact gold-string mimicry.
- **Distinct seizure types, not events.** One seizure_frequency entry per distinct
  seizure type with its coarse state; do not enumerate each dated occurrence.
- **Current medications only**, as drug + dose + frequency.
- **Completed investigations only**, as modality + result.
- Everything must be source-grounded by an exact evidence substring.

## 5. Implementation Sketch

- **New route:** add `single_call_dedup_facts` to
  `llm/llm_only_key_entities_generation_selection.py` and its runner
  `runners/run_llm_only_key_entities_generation_selection.py` (the existing
  resume/checkpoint harness is reused).
- **Headline adapter:** a deterministic, attribution-clean mapper from a
  `clinical_fact` into the minimal `PredictedMention`/`ClinicalFinding` fields the
  `clinical_headline` keys read (Diagnosis concept+Negation; SF seizure-type+state
  token; Rx DrugName/DrugDose/Frequency; Inv modality+Performed+Result). The
  mapper performs [[Meaning-Preserving Benchmark Projection]] only and logs
  [[Projection Attribution Tag]] values per the attribution protocol.
- **Projection eligibility layer (post-Phase-4 direction):** deterministic code,
  not the model, decides whether a selected fact is eligible for projection.
  Every rule must be classified by the [[Deterministic Projection Rule Taxonomy]]
  before it affects scored output: LLM-only-compatible projection, hybrid
  rescue, or verifier rejection.
- **Primary reported surface:** `clinical_headline` overall (micro-averaged) plus
  the four per-family headline F1s, evidence validity, and call/parse-failure
  counts. Strict benchmark is reported as a secondary diagnostic only.
- **Standardize the headline definition (deliverable):** lock one canonical
  `clinical_headline` overall (Diagnosis = `concept_negation`, matching v08 and
  decision 0027) so the runner's report, the assembly views, and this route all
  agree. Resolve the current discrepancy where the LLM-only runner's
  "Key Clinical-Recovery Headlines" Diagnosis cell differs from `concept_negation`.
- **Tests:** `tests/test_exectv2_dedup_facts_route.py` — schema parse, evidence
  gate, headline-adapter mapping, attribution-clean (no fact added vs raw model
  output), de-dup is model-side not scorer-rescued.

## 6. Phased Plan

### Phase 0 — Plan and guardrail (complete 2026-06-23)
Deliverables: this plan; an ADR
`docs/decisions/0033-deduplicated-clinical-fact-recovery-is-the-primary-llm-only-target.md`.
Exit: the de-dup clinical-recovery surface and single-prompt LLM-only route are
named as primary; claim language fixed (clinical-recovery, **not**
paper-comparable benchmark).

Completion note: ADR 0033 now fixes the primary LLM-only target, attribution
boundary, strict-surface diagnostic requirement, and Phase 1 cleanup handoff.

### Phase 1 — Cleanup (rich-schema runs become comparators) — complete 2026-06-23
Keep **two** rich-schema comparators at dev140 scale:
1. **LLM-only rich-schema:** `single_call_clean_render_ids` dev140 (GPT-4.1-mini
   and Qwen) — the bare-model strict number (0.334/0.339) and its de-dup view
   (0.713/0.725).
2. **Hybrid rich-schema:** `holistic_finding_assembly_v08` dev140 — strict ~0.37,
   headline 0.9155.

Archive (do not delete) the many superseded iterations: the dev1/dev2/dev5
generation-selection ladder variants, `single_call_{inventory,mentions,mention_ids,render_ids,typed_mentions,per_entity*}`,
the `qwen_pool_*` adjudication variants, and the DeepSeek/Qwen v0.9.x
diagnostic rows beyond the one kept comparator each. Move their experiment
artifacts under an `experiments/_archive/exectv2_richschema_iterations/` index
with a one-line manifest pointing at the two kept comparators.
Exit: a single comparison table (rich-schema LLM-only, rich-schema hybrid,
de-dup target) is the only live scoreboard; the iteration sprawl is indexed and
out of the active path.

Completion note: superseded rich-schema iteration outputs were moved under
`experiments/_archive/exectv2_richschema_iterations/` with a manifest. The
active scoreboard is now
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase1_active_scoreboard_2026-06-23.md`,
which keeps only the `single_call_clean_render_ids` GPT-4.1-mini/Qwen dev140
comparators, the `holistic_finding_assembly_v08` dev140 hybrid control, and the
Phase 2 `single_call_dedup_facts` target row.

### Phase 2 — Build the simplified schema, route, adapter (no new performance claim) — complete 2026-06-23
Deliverables: the `single_call_dedup_facts` route, headline adapter, runner
wiring, tests; a prompt-only smoke on dev1; a no-call replay that maps the
*existing* clean_render output through the new adapter and reproduces the
`0.713`/`0.725` de-dup baseline (proves the adapter and scoring are correct
before any new prompt is judged).
Exit: adapter reproduces the baseline; tests green; attribution-clean verified.

Completion note: `single_call_dedup_facts` now has a direct simplified
`clinical_facts` prompt, parser, representation-only headline adapter, runner
wiring, prompt-only smoke coverage, and tests in
`tests/test_exectv2_dedup_facts_route.py`. The runner/report surface now locks
canonical `clinical_headline` overall to Diagnosis `concept_negation`. No-call
clean-render replays through the adapter exactly reproduce the fixed canonical
source baselines:

- GPT-4.1-mini:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_replay_clean_render_ids_dev140_gpt41mini_20260623.{jsonl,md}`,
  overall `0.7114`, Diagnosis `0.6527`, SeizureFrequency `0.5507`,
  Prescription `0.8462`, Investigations `0.8627`.
- Qwen-3.6:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_replay_clean_render_ids_dev140_qwen36_20260623.{jsonl,md}`,
  overall `0.7215`, Diagnosis `0.6726`, SeizureFrequency `0.5118`,
  Prescription `0.8386`, Investigations `0.9189`.

These are adapter/scoring replays only, not new performance claims. The slight
difference from the rounded planning shorthand (`0.713`/`0.725`) comes from
locking the canonical Diagnosis component to `concept_negation` and recomputing
the overall micro score from the saved source rows.

### Phase 3 — GPT-4.1-mini single-prompt iteration to >0.900 — complete 2026-06-23 (localized plateau)
Iterate the simplified prompt on dev (smoke on dev25, confirm on dev140). Each
cycle: run → score `clinical_headline` → row-level error analysis on **Diagnosis
and SeizureFrequency** (the gap families) → one principled prompt change →
re-run. Track precision (over-emission) and recall (enumeration/state) separately.
Exit: `clinical_headline` overall `> 0.900` on dev140 with GPT-4.1-mini, 0
call/blocking-schema failures, evidence validity ≥ `0.96`, and per-family
headline F1 with Diagnosis and SeizureFrequency each materially above their
`0.65`/`0.55` baselines.

Completion note: five single-prompt GPT-4.1-mini iterations were run on dev25,
then the best gate-clean candidate (`v0.5`) was confirmed on dev140. The
single-prompt route did **not** clear the `>0.900` target; dev140 canonical
`clinical_headline` was `0.710` overall with evidence validity `0.9613`, 0
call failures, and 0 parse/schema failures. The plateau is localized to
Diagnosis (`0.672`) and SeizureFrequency (`0.558`), while Prescription (`0.814`)
and Investigations (`0.832`) remain stronger but not enough to offset the gap.
See
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase3_single_prompt_plateau_2026-06-23.md`.
Phase 4 fallback rung 1 (lean per-family LLM-only prompts) was evaluated next
and is documented below.

### Phase 4 — Fallback rungs (only if single prompt plateaus < 0.900) — complete 2026-06-24 (fallback plateau)
All still attribution-clean LLM-only. In order of preference:
1. lean **per-family** prompts (one call per family) — trades single-prompt
   elegance for focus on Dx/SF;
2. a two-call **generate-then-self-dedup** (model lists candidates, then selects a
   de-duplicated final set by id);
3. a small set of in-context worked examples demonstrating the de-dup policy for
   Diagnosis enumeration and SF state.
Exit: the first rung that clears `0.900`, or a documented finding that LLM-only
de-dup recovery plateaus below `0.900` with the gap localized.

Completion note: Phase 4 added and tested
`single_call_dedup_facts_per_family`, a four-call attribution-clean fallback
route that gates each prompt to one model-emitted fact family and then reuses
the Phase 2 one-to-one adapter. Two GPT-4.1-mini dev25 gates were run:

- compact per-family:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_dev25_gpt41mini_20260624.{jsonl,md}`,
  canonical `clinical_headline` `0.796`, Diagnosis `0.698`,
  SeizureFrequency `0.690`, Prescription `0.873`, Investigations `0.976`,
  evidence validity `0.9609`, 0 call/parse/schema failures.
- full-example per-family:
  `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_full_examples_dev25_gpt41mini_20260624.{jsonl,md}`,
  canonical `clinical_headline` `0.782`, Diagnosis `0.701`,
  SeizureFrequency `0.593`, Prescription `0.900`, Investigations `0.952`,
  evidence validity `0.9562`, 0 call/parse/schema failures.

Neither Phase 4 fallback beat the Phase 3 dev25 gate (`0.800`) or approached
the `>0.900` target, so no dev140 confirmation or Phase 5 model rollout was
promoted. The plateau remains localized to Diagnosis and SeizureFrequency. See
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_fallback_plateau_2026-06-24.md`.

Prompt-guideline probe note: after the Phase 4 plateau, a targeted
decision-table prompt profile was tested because several errors appeared
prompt-addressable. The best mixed profile (`decision_table_sf_inv`) improved
dev25 to `0.828` and dev140 overall to `0.729`, but did not improve dev140
SeizureFrequency or approach `>0.900`. This confirms that clearer instructions
help local behavior but do not solve the prediction-bearing ontology/state
boundary. See
`docs/experiments/exectv2/key_entities/exectv2_dedup_phase4_decision_table_prompt_probe_2026-06-24.md`.

### Phase 5 — Deterministic projection taxonomy and Prescription pilot — next, not started
This phase is **not** a continuation of the LLM-only prompt ladder and does not
resurrect the `>0.900` LLM-only target by hidden repair. It formalizes the
post-Phase-4 finding that deterministic rules can help map clinical meaning onto
benchmark conventions only when their ownership is explicit.

Deliverables:

1. A small [[Deterministic Projection Rule Taxonomy]] with allowed
   meaning-preserving categories and disallowed/separate hybrid categories.
2. A Prescription-first projection pilot, because Prescription has the clearest
   convention mappings: brand/generic equivalence, frequency abbreviation
   rendering, exact dose/unit normalization, route synonym rendering,
   guideline-defaulted rescue/PRN frequency, and duplicate regimen collapse
   within the same headline unit.
3. Rule-level [[Projection Attribution Tag]] output for every deterministic
   mapping that changes the scored representation.
4. Separate [[Projection-Aware Score Line]] reporting:
   LLM-only + meaning-preserving projection; hybrid rescue; verifier-filtered.
5. Tests proving that the LLM-only score line does not add missed medications,
   infer current/past status the model omitted, drop hallucinated medications,
   infer missing dose/frequency from clinical practice, or convert vague ASM
   therapy into specific drugs.

Exit: a Prescription pilot report showing per-rule counts, score deltas by
score line, and examples of accepted projection versus boundary violations. The
phase succeeds if it clarifies attribution and benchmark-convention effects,
even if it does not materially raise overall `clinical_headline`.

### Phase 6 — Rollout to DeepSeek and Qwen — parked
Only run a model swap if a future GPT-4.1-mini configuration or projection-aware
score line has a clearly stated transfer question. The original model rollout
was not promoted because no Phase 4 LLM-only fallback cleared the dev25 gate.

If reactivated, run the selected configuration unchanged on
`deepseek/deepseek-chat` and `ollama_chat/qwen3.6:35b`. Report the three-model
de-dup comparison and per-family deltas; note any model-specific gap (expected:
SF state for Qwen, per the closeout). Projection-aware reporting must keep
LLM-only, hybrid rescue, and verifier-filtered score lines separate.

### Phase 7 — (Optional, separately authorized) audit and paper framing
If the dev result is strong and stable, predeclare a frozen full-200 /
holdout audit on the de-dup surface, framed explicitly as clinical-recovery.

## 7. Comparison Protocol

Every de-dup result is reported against the two kept rich-schema comparators on
**both** surfaces, so the contribution is unambiguous:

| Candidate | Architecture | strict benchmark | de-dup `clinical_headline` |
| --- | --- | ---: | ---: |
| clean_render (LLM-only, full schema) | 1 call, full schema | 0.334 / 0.339 | 0.713 / 0.725 |
| v08 (hybrid, full schema) | multi-component | ~0.374 | 0.9155 |
| dedup_facts v0.5 | 1 call, de-dup target | diagnostic | 0.710 dev140 |
| dedup_facts_per_family compact | 4 calls, de-dup target | diagnostic | 0.796 dev25 gate |
| decision_table_sf_inv | 4 calls, mixed prompt profile | diagnostic | 0.729 dev140 |
| Projection-aware Prescription pilot | deterministic projection over model-selected facts | diagnostic | separate LLM-only / hybrid / verifier-filtered lines |

The current claim is specifically: *direct attribution-clean LLM-only prompting
for de-duplicated clinical facts plateaued below the v08 hybrid, with the
remaining gap localized to prediction-bearing Diagnosis and SeizureFrequency
decisions.* The next research question is whether tagged
[[Meaning-Preserving Benchmark Projection]] can quantify benchmark-convention
effects without changing the LLM-only clinical-recovery attribution.

## 8. Risks

| Risk | Mitigation |
| --- | --- |
| De-dup target read as a benchmark win | Claim language fixed to "clinical-recovery"; strict benchmark always shown alongside; not paper-comparable. |
| Single prompt plateaus below 0.900 | Phase 4 fallback rungs, all still LLM-only; a documented plateau is itself a valid result. |
| Headline definition drift | Phase 2 locks one canonical `clinical_headline` (Diagnosis = `concept_negation`); adapter must reproduce the 0.713/0.725 baseline before any new judgment. |
| Adapter silently rescues facts | Tests assert the scored fact set equals the model-emitted fact set (1:1), no additions; provenance logged. |
| Projection pilot silently becomes hybrid rescue | Every rule must have a [[Projection Attribution Tag]] and a [[Deterministic Projection Rule Taxonomy]] category; hybrid rescue and verifier-filtered outputs get separate score lines. |
| Prescription projection overstates general progress | Report per-family score deltas and rule counts; do not infer Diagnosis/SF recovery from Prescription convention mapping. |
| Model de-dups too aggressively (recall loss) | Track recall separately; de-dup is "distinct facts," not "fewest facts." |
| Cleanup deletes useful path evidence | Archive, never delete; keep a one-line manifest of the two retained comparators. |

## 9. Claim Language

Allowed now:
> On dev140, direct attribution-clean LLM-only prompting for de-duplicated
> clinical facts plateaued at `0.710`–`0.729` overall clinical-recovery F1,
> below the v08 hybrid `0.9155`, with the residual concentrated in
> prediction-bearing Diagnosis and SeizureFrequency decisions.

Allowed for Phase 5:
> A projection-aware Prescription pilot reports LLM-only clinical recovery plus
> tagged meaning-preserving benchmark projection separately from hybrid rescue
> and verifier-filtered score lines.

Not allowed:
- "Benchmark cleared" or any comparison to the paper's 0.87/0.90 (different,
  strict target).
- "LLM-only" if the headline adapter adds, selects, or completes facts the model
  did not emit.
- Blending hybrid rescue or verifier rejection into the LLM-only score line.
- Reporting de-dup `clinical_headline` without the strict benchmark beside it.

## 10. Completion Criteria

This plan is complete when:
- the rich-schema sprawl is reduced to the two named comparators (Phase 1);
- a single-prompt (or documented-minimal-fallback) LLM-only `single_call_dedup_facts`
  route exists, tested and attribution-clean (Phase 2);
- GPT-4.1-mini clears `0.900` de-dup `clinical_headline` on dev140, or a localized
  plateau is documented (Phases 3–4);
- the post-plateau deterministic projection taxonomy and Prescription pilot are
  either completed with projection-aware score lines or explicitly deferred
  (Phase 5);
- any future DeepSeek/Qwen rollout is tied to a stated transfer question rather
  than treated as a required continuation (Phase 6);
- every result is reported on both the de-dup and strict surfaces with fixed
  clinical-recovery claim language.
