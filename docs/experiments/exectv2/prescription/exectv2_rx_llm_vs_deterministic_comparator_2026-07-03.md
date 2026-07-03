# LLM-vs-deterministic Prescription comparator — results

Date: 2026-07-03. Owner: ExECTv2 workstream.
Hypothesis: `rx_llm_vs_deterministic_comparator_2026-07-03`.
Predeclarations: dev140 (this doc) + `exectv2_rx_llm_vs_deterministic_full200_predeclaration_2026-07-03.md`.

## Setup

The best-possible LLM-tuned Prescription extractor: the canonical GEPA evolved Rx
instruction + probe #2 (current-vs-future dose) + probe #3 (AED-only) **with the
emit-if-unsure safety clause** that fixes the documented probe #3 over-drop (the
07-02 probe found the AED-only instruction made the model over-conservative,
dropping genuine AEDs like lamotrigine/carbamazepine that were on its own whitelist;
the fix is an explicit "do not drop a current-dose drug solely because you are
unsure if it is an AED" clause, not a tighter list). Run through the full v08
hybrid assembly with same-day baseline+treatment isolation (P7 audit method),
swapping only the Prescription producer.

Model: gpt-4.1-mini, temp 0, cache on. The LLM arm's evidence spans are grounded
to exact note substrings (the assembly's evidence-grounding invariant requires it).

## Results

### dev140

| Producer (Rx `clinical_headline`, v08 assembly) | F1 | P | R | TP/FP/FN |
| --- | ---: | ---: | ---: | --- |
| Deterministic pre-P7 (archived v08 manifest) | 0.9386 | 0.9502 | 0.9272 | 191/10/15 |
| **LLM-tuned (canonical + probe #2 + probe #3 + emit-if-unsure)** | **0.9526** | 0.9795 | 0.9272 | 191/4/15 |
| **Deterministic P7-fixed (production)** | **0.9615** | 0.9524 | 0.9709 | 200/10/6 |

### full-200 (aggregate-only, frozen protocol)

| Producer (Rx `clinical_headline`, v08 assembly) | F1 | P | R | TP/FP/FN | Overall |
| --- | ---: | ---: | ---: | --- | ---: |
| Deterministic pre-P7 (20260624 currentcode) | 0.9033 | 0.9312 | 0.8771 | 257/19/36 | 0.8616 |
| **Deterministic P7-fixed (production, cited)** | **0.9278** | 0.9343 | 0.9215 | 270/19/23 | **0.8680** |
| **LLM-tuned** | **0.9492** | 0.9748 | 0.9249 | 271/7/22 | **0.8730** |

## The finding: a split-dependent inversion

On **dev140**, the deterministic P7-fixed producer beats the LLM (+0.0089 Rx F1,
recall-driven: the P7 fix recovers multi-dose weight-context suppression the LLM
can't match). On **full-200**, the LLM-tuned extractor beats the deterministic
P7-fixed producer (+0.0214 Rx F1; overall +0.0050), improving BOTH precision
(FP 19→7, the AED-only gate fixing non-AED over-extraction the deterministic
lexicon doesn't fully handle on the broader test set) AND recall (TP 270→271).

The mechanism: the two approaches fix **different failure modes** that have
**different prevalence on dev vs test**.
- The deterministic P7 fix targets multi-dose weight-context over-suppression
  (recall) — concentrated in dev140 letters.
- The LLM AED-only gate targets non-AED comorbidity-drug over-extraction
  (precision) — more prevalent in the 60 test letters (cardiac/diabetes
  comorbidity meds in letters concluding non-epileptic causes).
- The deterministic producer IS AED-only by lexicon construction, but its lexicon
  over-captures on some full-200 letters in a way the LLM's contextual AED
  judgment avoids.

## Implication for the paper

This is a genuine, publishable finding that **complexifies the deterministic-lane
story**. The v08 architecture's deterministic Prescription lane is not strictly
dominant: it wins on the dev split (where its recall advantage dominates) but
loses on the full-200/test surface (where the LLM's contextual precision
advantage dominates). The honest paper framing: the deterministic lane is a
strong, cheap, attribution-clean baseline that is competitive with but not
strictly better than a tuned LLM on Prescription; the choice is a
cost/attribution/consistency tradeoff, not a clear win. The full-200 LLM
advantage (+0.0050 overall) is within the metric's run-to-run variance band and
should not be over-claimed.

This **partially revises** the 07-03 feasibility finding
(`exectv2_rx_headtohead_feasibility_finding_2026-07-03.md`), which compared the
LLM against the deterministic producer at the *isolated producer* level (0.9615
vs 0.9526 on dev140) and concluded the deterministic producer wins. That
conclusion holds for dev140 and for the isolated comparison, but does NOT
generalize to full-200 through the assembly, where the LLM's contextual
precision advantage on the broader test surface inverts the ordering.

## Provenance

- LLM artifacts: `experiments/exectv2_llm_rx_tuned_extractor_{dev140,full200}_20260703.jsonl`
- Baseline/treatment assemblies: `experiments/exectv2_v08_{dev140,full200}_rx_{deterministic_baseline,llm_tuned_treatment}_20260703.json{l,.json}`
- Reports: `docs/experiments/exectv2/prescription/exectv2_v08_{dev140,full200}_rx_{...}_2026-07-03.md`
- Script: `scripts/run_exectv2_v08_rx_llm_vs_deterministic.py`
- Call counts: dev140 ~140 calls (then cached), full200 ~60 fresh (140 cached).
