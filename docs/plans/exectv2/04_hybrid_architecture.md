> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# Satellite 04 — Hybrid Architecture

Parent: [[00_overarching_implementation_plan]] · Phases 4 & 6
Status: **Phase 4 complete (2026-06-11) — see §7.** The candidate-assessment
hybrid is built, tested, and scored on dev for both models; the
`hybrid_structured_events` variant is held for Phase 6. Dev-split only until the
Phase 7 audit.

## Purpose

Build the hybrid ExECTv2 extractor — deterministic where representation,
arithmetic, and format belong; LLM where clinical judgment belongs. This is the
architecture that operationalizes the project's central lesson: representation
loss is mostly a normalization/projection problem, not a clinical-judgment
problem. It should be the strongest of the three on the hard entities (SF,
Patient History).

## 1. Shape (reset-native hybrid, ported)

Mirror Gan 2026's `hybrid` (`reset_clinical_assessment_pipeline`):

```
raw letter text
  → deterministic candidate extraction   (rule families → high-recall candidate mentions w/ evidence)
  → LLM clinical assessment              (select/judge among candidates; assign clinical interpretation)
  → deterministic Normalize              (shared epilepsy normalizer → attribute values)
  → Select/Render                        (emit PredictedMention set)
  → Verify / Route                       (evidence + plausibility gate; route the unresolved)
  → adapter → PredictedLetter
```

The LLM's job is **selection and assessment over a pre-extracted candidate set**,
not open-text parsing and not value formatting. Deterministic stages own
candidate recall, normalization, and format.

A second hybrid variant (optional, mirroring `hybrid_structured_events`):
**LLM extracts structured mentions from raw text → deterministic
normalize/render**, no candidate set, no routing. The gap between the two
variants measures LLM-task-design and routing cost — a clean ablation.

## 2. Candidate set (reuse the live-wiring lesson)

Gan 2026 learned to generate candidate sets **live per record** (deterministic
extraction ∪ LLM-extracted candidates), not from a static precomputed file
(plan §8a). Build ExECTv2's candidate stage live from the start:

- deterministic candidate extraction = the satellite-02 Extract stage run in
  high-recall mode (over-generate; the assessment stage prunes)
- optional LLM candidate extractor for recall the rules miss
- union into the candidate set the assessment LLM sees

This avoids the 250-row-scoped surface mistake; every dev letter gets a real
candidate set.

## 3. Clinical assessment stage

The LLM receives the candidate set (with evidence) and, per the closed output
contract:

- selects which candidates are real gold-worthy mentions
- assigns the clinical interpretation (current vs historical, seizure-free vs
  active, cluster vs intra-cluster rate)
- emits `uncertainty_flags` from the closed vocabulary and an
  `aggregation_policy` from its enum, each governed by an in-prompt decision
  table (Gan 2026 Phase 3 pre-conditions B & C)

Prompt language obeys ADR 0015; `PROMPT_VERSION` discipline applies.

## 4. Routing / verification

A lightweight verify stage checks evidence presence/substring and clinically
implausible combinations, and **routes** (does not silently fix) mentions it
cannot resolve. The routed-mention taxonomy is a first-class diagnostic
(satellite 07). No verifier-written labels (guardrail).

## 5. Deliverables & tests

- `hybrid/candidate_set.py` (live union), `hybrid/clinical_assessment.py`,
  reuse of shared normalizer + deterministic render, `hybrid/verify_route.py`
- The optional `hybrid_structured_events`-style variant
- Contract tests on candidate-set shape, assessment output, routing decisions
- Pilot + dev-split runs registered; per-entity dev F1 + routed-row taxonomy

## 6. Exit criteria

- **Phase 4**: hybrid scores SF on dev with live candidate sets, 0 unexplained
  failures; routed-row taxonomy produced; per-item/per-letter F1 reported.
- **Phase 6**: extended to all 9 entities; overall dev F1 reported per model;
  the two hybrid variants compared.

---

## 7. Phase 4 — Complete (2026-06-11)

The reset-native candidate-assessment hybrid is built, gated, test-covered, and
scored on the full dev split for two models. It is **the strongest SeizureFrequency
system in the workstream on the per-letter axes** and ties the deterministic
extractor on attribute-aware per-letter F1 while far exceeding it on phrase recall
— exactly the outcome the central hybrid lesson predicts (representation/format is
deterministic; clinical judgment is the LLM's).

### 7.1 Deliverables shipped

- `hybrid/candidate_set.py` — live, high-recall candidate set per record
  (deterministic anchors ∪ optional LLM candidates). High recall = it keeps the
  bare seizure-type anchors the deterministic pipeline *drops* (no nearby
  frequency), handing the keep/drop judgment to the LLM. ~4.6 candidates/letter
  (639 over 140 dev letters).
- `hybrid/clinical_assessment.py` — the LLM **selects and judges** over the
  candidate set (keep/route each, finalize attributes, emit `uncertainty_flags`
  from a closed vocab + an `aggregation_policy` from its enum) → deterministic
  **normalize** (shared epilepsy normalizer: number-word/unit/month
  canonicalization) + CUI-lexicon **render** → attribute repair (neutral).
- `hybrid/verify_route.py` — evidence-substring + plausibility gate that **routes**
  (never silently fixes) unresolved mentions into a first-class taxonomy.
- `runners/run_hybrid_sf.py` (with `--resume`); `tests/test_exectv2_hybrid_sf.py`
  (21 tests: candidate set, parse incl. lenient repair, normalize, render,
  routing, resume integration, prompt hygiene). Full suite green.

### 7.2 Results (full dev, 140 letters, D16-repaired gold)

| Run | phrase_only per-item / per-letter | sf_semantic ≡ sf_benchmark per-item / per-letter |
|-----|-----------------------------------|--------------------------------------------------|
| gpt-4.1-mini **v0.1** | 0.577 / 0.787 | 0.233 / 0.476 |
| gpt-4.1-mini **v0.2** | **0.585 / 0.781** | **0.327 / 0.578** |
| qwen3.6:35b **v0.2** | 0.498 / 0.730 | 0.228 / 0.451 |

Comparators (dev, same gold): deterministic `sf_benchmark` 0.362 / 0.575,
`phrase_only` 0.382 / 0.604; LLM-only best (gpt per_entity) `phrase_only`
0.486 / 0.698, `sf_semantic` 0.135 / 0.264; published SF benchmark **0.66 / 0.68**.

**Findings:**

- **Hybrid gpt-4.1-mini is the best per-letter SF system built.** `phrase_only`
  per-letter **0.781** is the highest of any architecture and the only one to
  clear the SF benchmark target (0.68); it beats LLM-only (0.698) and the
  deterministic baseline (0.604).
- **Attribute-aware per-letter ties the rules and beats everything else.**
  `sf_benchmark` per-letter **0.578** ≈ deterministic 0.575 but with far higher
  phrase recall, and ≫ LLM-only 0.264. The hybrid recovers the LLM-only's
  catastrophic attribute loss by routing formatting through the deterministic
  normalizer — the central lesson, demonstrated.
- **Per-item attributes still favour the rules** (hybrid 0.327 vs deterministic
  0.362). The hybrid keeps more mentions than gold annotates (288 kept vs 187
  gold), so FP proliferation costs per-item precision — the LLM-only's failure
  mode, dampened but not gone. This is the clearest cross-pollination target for
  Phase 5 (tighten the keep decision / candidate precision).
- **gpt-4.1-mini > qwen3.6:35b on hybrid**, mirroring LLM-only. qwen hybrid
  (0.498 / 0.730 phrase) still beats its own LLM-only (0.642) and the rules
  per-letter — the hybrid scaffold lifts the weaker model too.

### 7.3 Prompt optimization (v0.1 → v0.2)

The v0.1 pilot/dev error diff showed the residual gap was attribute *encoding*,
not phrase selection. Four generalizable, source-backed prompt rules were added
(not phrase-list overfitting): period-gap encoding (`one every 3 weeks` →
`NumberOfSeizures=1` + `NumberOfTimePeriods=3`, not `NumberOfTimePeriods=1`);
date-anchored counts (a count tied to a calendar date is a dated event, no
spurious recurring period); seizure-free with no stated duration → bare
`NumberOfSeizures=0`; and "respect the deterministic draft unless contradicted".
Result on gpt-4.1-mini: `sf_semantic` per-item **0.233 → 0.327 (+40%)**, per-letter
**0.476 → 0.578 (+21%)**, with `phrase_only` held flat — the move was plausible
and explicable, not a blind score chase.

### 7.4 Routing taxonomy (first-class diagnostic)

The verify/route stage is doing real work, not rubber-stamping. gpt v0.2: 37
routed — `bare_nonzero_count` 29, `no_frequency_attributes` 7,
`evidence_not_substring` 1. qwen v0.2: 45 routed — `no_frequency_attributes` 25,
`bare_nonzero_count` 13, `empty_evidence` 5, `evidence_not_substring` 2. The
dominant reason (a count with no time frame) is exactly the guideline-L255
non-frequency case; routing it rather than scoring it is what protects per-letter
precision. No verifier-written labels (guardrail held).

### 7.5 Reliability findings (cross-model gate hardening)

- **qwen Python-dict output.** The larger hybrid prompt exposed qwen3.6 emitting
  Python-literal output (single-quoted keys, `True`/`False`) — strict JSON
  rejected 100% of a first qwen run. Fixed with a semantically-neutral
  `ast.literal_eval` fallback in the parse gate plus tolerant optional-field
  defaults; qwen then ran at 0 call failures / 1 parse failure (a lone
  `max_tokens` truncation). The gate repairs representation, never a clinical fact.
- **Resume.** A power-off interrupted the qwen dev run at 50/140. Resume
  (`core/run_resume.py`, now a foundational runner requirement — satellite 05 §5a)
  finished it from the checkpoint with `n_resumed=50`, no work re-spent.

### 7.6 Exit criteria — met

Phase 4 hybrid scores SF on dev with **live** candidate sets, **0 unexplained
failures**, a routed-row taxonomy, and per-item/per-letter F1 reported per model.
Runs registered (`exectv2_hybrid_dev140_{gpt41mini,qwen3635b}_20260611`). The
optional `hybrid_structured_events` variant and the all-9-entity scale-up are
Phase 6; the three-way SF comparison + cross-pollination (the per-item precision
target above) is Phase 5.
