# Satellite 13 — De-duplicated Clinical-Fact LLM-Only Extraction (PRIMARY FOCUS)

Parent: [[00_overarching_implementation_plan]]
Status: **active — primary ExECTv2 research focus as of 2026-06-23; Phase 0, Phase 1, Phase 2, and Phase 3 complete; Phase 4 next.**
Dev-split only until a separately authorized Phase 7 audit.
Decision basis:
`docs/decisions/0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md`,
`docs/decisions/0033-deduplicated-clinical-fact-recovery-is-the-primary-llm-only-target.md`,
`docs/research/qwen_exectv2_llm_only_error_analysis_2026-06-23.md`,
`docs/experiments/exectv2/key_entities/exectv2_cross_model_closeout_2026-06-22.md`

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
| Attribution | model_preserving_canonical with no deterministic rescue | unchanged: still LLM-only; deterministic code only validates evidence, maps to the headline key, and scores |

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
- map the model's simplified fact into the scorer's headline-key fields
  (representation mapping of a model-selected fact — allowed);
- score on `clinical_headline`.

Deterministic code may **not** add a fact the model did not emit, choose a
seizure-frequency state the model omitted, expand ontology companions, or
de-duplicate in a way that rescues a missed concept. De-duplication is the
**model's** job in the prompt; the scorer's collapse only forgives, it does not
add.

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
  mapper performs representation mapping only and logs provenance per the
  attribution protocol.
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
Phase 4 fallback rung 1 (lean per-family LLM-only prompts) is now the active
next step.

### Phase 4 — Fallback rungs (only if single prompt plateaus < 0.900)
All still attribution-clean LLM-only. In order of preference:
1. lean **per-family** prompts (one call per family) — trades single-prompt
   elegance for focus on Dx/SF;
2. a two-call **generate-then-self-dedup** (model lists candidates, then selects a
   de-duplicated final set by id);
3. a small set of in-context worked examples demonstrating the de-dup policy for
   Diagnosis enumeration and SF state.
Exit: the first rung that clears `0.900`, or a documented finding that LLM-only
de-dup recovery plateaus below `0.900` with the gap localized.

### Phase 5 — Rollout to DeepSeek and Qwen
Run the winning configuration unchanged (model swap only) on
`deepseek/deepseek-chat` and `ollama_chat/qwen3.6:35b`. Report the three-model
de-dup comparison and per-family deltas; note any model-specific gap (expected:
SF state for Qwen, per the closeout).
Exit: dev140 de-dup `clinical_headline` for all three models, with a portability
read (which families transfer, which need model-specific prompting).

### Phase 6 — (Optional, separately authorized) audit and paper framing
If the dev result is strong and stable, predeclare a frozen full-200 /
holdout audit on the de-dup surface, framed explicitly as clinical-recovery.

## 7. Comparison Protocol

Every de-dup result is reported against the two kept rich-schema comparators on
**both** surfaces, so the contribution is unambiguous:

| Candidate | Architecture | strict benchmark | de-dup `clinical_headline` |
| --- | --- | ---: | ---: |
| clean_render (LLM-only, full schema) | 1 call, full schema | 0.334 / 0.339 | 0.713 / 0.725 |
| v08 (hybrid, full schema) | multi-component | ~0.374 | 0.9155 |
| **dedup_facts (this plan)** | 1 call, de-dup target | (diagnostic) | **target > 0.900** |

The claim is specifically: *an attribution-clean single-prompt LLM-only system,
designed to emit de-duplicated clinical facts, recovers the clinical-recovery
headline as well as the multi-component hybrid* — without deterministic fact
rescue.

## 8. Risks

| Risk | Mitigation |
| --- | --- |
| De-dup target read as a benchmark win | Claim language fixed to "clinical-recovery"; strict benchmark always shown alongside; not paper-comparable. |
| Single prompt plateaus below 0.900 | Phase 4 fallback rungs, all still LLM-only; a documented plateau is itself a valid result. |
| Headline definition drift | Phase 2 locks one canonical `clinical_headline` (Diagnosis = `concept_negation`); adapter must reproduce the 0.713/0.725 baseline before any new judgment. |
| Adapter silently rescues facts | Tests assert the scored fact set equals the model-emitted fact set (1:1), no additions; provenance logged. |
| Model de-dups too aggressively (recall loss) | Track recall separately; de-dup is "distinct facts," not "fewest facts." |
| Cleanup deletes useful path evidence | Archive, never delete; keep a one-line manifest of the two retained comparators. |

## 9. Claim Language

Allowed (after Phase 3/5):
> On dev140, an attribution-clean single-prompt LLM-only system targeting
> de-duplicated clinical facts reaches clinical-recovery (`clinical_headline`)
> F1 of X with GPT-4.1-mini (and Y/Z for DeepSeek/Qwen), versus 0.713 for the
> full-schema LLM-only baseline and 0.9155 for the full hybrid — without
> deterministic fact rescue.

Not allowed:
- "Benchmark cleared" or any comparison to the paper's 0.87/0.90 (different,
  strict target).
- "LLM-only" if the headline adapter adds, selects, or completes facts the model
  did not emit.
- Reporting de-dup `clinical_headline` without the strict benchmark beside it.

## 10. Completion Criteria

This plan is complete when:
- the rich-schema sprawl is reduced to the two named comparators (Phase 1);
- a single-prompt (or documented-minimal-fallback) LLM-only `single_call_dedup_facts`
  route exists, tested and attribution-clean (Phase 2);
- GPT-4.1-mini clears `0.900` de-dup `clinical_headline` on dev140, or a localized
  plateau is documented (Phases 3–4);
- the winning configuration is rolled out to DeepSeek and Qwen with a three-model
  de-dup comparison (Phase 5);
- every result is reported on both the de-dup and strict surfaces with fixed
  clinical-recovery claim language.
