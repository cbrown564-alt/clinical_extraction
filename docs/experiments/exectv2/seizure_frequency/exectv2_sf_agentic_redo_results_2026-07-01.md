# ExECTv2 SeizureFrequency Agentic Redo — Results (2026-07-01)

Status: complete for the ExECTv2 SF pilot (Phase 3 of
`docs/plans/proud-bubbling-ocean.md`). Implements the predeclaration at
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_agentic_redo_predeclaration_2026-07-01.md`.
Raw data: `experiments/exectv2_sf_agentic_redo_hard_panel_results.jsonl`
(212 rows), report: `experiments/exectv2_sf_agentic_redo_hard_panel_results.md`.

## What this answers

Whether the Gan 2026 agentic-redo finding (decomposition and dynamic tool
selection substantially beat plain single-prompt extraction on a hard
panel, though neither cleared the strict promotion gate) transfers to
ExECTv2's SeizureFrequency family — the same clinical concept, in a
different corpus, schema, and scoring regime, and the primary/brief-aligned
task.

## New, safe tooling built (ExECTv2 had zero agentic infrastructure)

Two gold-free tools (a planned concept/CUI-lookup tool was rejected before
building anything: `deterministic/concept_normalizer.py`'s
`InSampleConceptNormalizer` is built directly from gold annotations, and
`UmlsConceptNormalizer` is unimplemented — wrapping either would have been
a real leak or simply broken):

- `check_evidence_in_letter` — wraps `core/evidence.py`'s
  `grade_evidence`/`evidence_is_substring`, bound per letter.
- `read_sf_boundary_guide` — re-exposes the v08 hybrid SF stage's existing
  clinical-decision prose (`llm_sf_state_adjudicator.py`'s six guide
  functions) as a queryable lookup, mirroring Gan's `read_boundary_guide`.

Architectures (all new): `single_agent_tools_react` (`dspy.ReAct` over the
existing single-pass SF signature); `multi_agent_d3_static` (three
specialists — `active_rate_fact_lister`, `seizure_free_hazard_lister`,
`cluster_or_change_lister` — targeting SF's two documented weak spots,
cluster-axis ambiguity and the direction-blind "changed" class, feeding a
resolver; specialist output schemas structurally cannot contain a
`mentions` field); `multi_agent_dynamic_orchestrator` (same specialists
wrapped as tools for a ReAct orchestrator). All mechanically clean: zero
call failures across two smoke tests (10 letters) and the full 212-pair
hard-panel run.

## A metric artifact, found and corrected before drawing conclusions

The hard panel (53 dev140 letters, reused from the SF canonical
row-adjudication's disagreement set) produced an implausible first read:
mean F1 of 0.12–0.15 for every condition, versus the production SF
headline of 0.9053. Diagnosis: **22 of the 53 panel letters have empty
gold SeizureFrequency annotations** (the adjudication doc's own "gold
annotated nothing" cases). Verified directly: `score_frequency_state`'s
`clinical_headline` F1 is **0.0 on an empty-gold letter regardless of the
prediction** — even a perfectly correct empty prediction scores 0.0, not
1.0. This mechanically ties all 4 conditions at a floor of 0.0 on 22/53
letters (41%), explaining both the low absolute numbers and why 46-49 of
53 per-letter comparisons were ties.

**Fix**: no new LLM calls needed — re-scored the already-collected 212
predictions restricted to the 31 non-empty-gold letters, where real
per-letter signal exists. This is a metric-mechanics correction applied
before looking at whether it changed which condition "wins," not a
post-hoc adjustment to the result — the same standard applied to the Gan
2026 temperature bug.

## Results (31 non-empty-gold letters, the gate basis)

| Condition | Mean F1 | vs single_greedy (W/L/T) |
| --- | ---: | --- |
| single_greedy | **0.2645** | — |
| single_agent_tools_react | 0.2151 | 3 / 4 / 24 |
| multi_agent_d3_static | 0.2151 | 2 / 3 / 26 |
| multi_agent_dynamic_orchestrator | 0.2065 | 1 / 4 / 26 |

`multi_agent_dynamic_orchestrator` vs `multi_agent_d3_static`: 1 win, 3
losses, 27 ties.

**Predeclared gates**: both FAIL — Angle 1 (react vs greedy): wins=3,
losses=4 (needed wins≥5, losses≤1). Angle 2 dynamism (orchestrator vs
static): wins=1, losses=3 (needed wins≥3, losses≤1). Zero true failures
(no-answer-produced) for any condition on any letter.

## The honest reading — a genuinely different pattern from Gan 2026

On Gan 2026's hard50, every new architecture beat `single_greedy` by a
wide accuracy margin (+8 to +26 points), even though none cleared the
strict gate. **On ExECTv2 SF, that pattern does not repeat.**
`single_greedy` is the best performer among the four tested here, and the
new architectures trend slightly negative (net −1 to −3 wins-minus-losses
each), not positive.

This should not be read as confident evidence that decomposition/tool-use
*hurts* on ExECTv2 SF — the sample (31 letters) is small, the margins are
thin (1-3 net losses on a 31-item panel is well within noise), and this
specific panel was built from a *different, more elaborate* pipeline's
disagreement cases (the two-stage GEPA-verify program, not
`single_greedy`), so all four architectures being weak on it is
unsurprising and not informative about their relative ranking on a fairer
panel. The defensible conclusion is **no detected advantage, and if
anything a mild negative trend, inconclusive at this sample size** — a
materially different result from Gan's clear (if gate-unproven) positive
signal, not a confirmation of it.

**Plausible reasons the pattern might genuinely differ by task** (not
tested here, flagged for any follow-up): ExECTv2 SF is a multi-mention,
richly-attributed extraction task (list of mentions, each with 10+
possible attributes) rather than Gan's single-label classification —
decomposing into evidence-only specialists may fragment attribute
construction across specialists in a way single-label tasks don't suffer
from, since the resolver has to reassemble full attribute sets from
partial specialist evidence rather than just picking among whole-answer
candidates.

## What this means for the user's original question

"How good can multi-agent get, and is dynamism load-bearing" — on Gan
2026, meaningfully better than single-prompt, with modest evidence
dynamism specifically helps. **On ExECTv2 SF, the same architecture family
does not show that advantage.** Taken together, this is evidence *against*
a universal "agentic decomposition helps clinical extraction" claim — it
is at best task-dependent, and this pilot's honest contribution is
demonstrating that dependence with real numbers rather than assuming
transfer.

## Not pursued in this pass

- Diagnosis/Prescription/Investigations families (this pilot was
  SF-only, per the plan's "start narrow" sequencing).
- A larger, fairer ExECTv2 SF hard panel not inherited from a different
  pipeline's error set (the 53-letter panel's provenance mismatch is a
  real limitation of this pilot, flagged above).
- Validation-scale confirmation (gated behind the failed gate, same as
  the Gan redo).

## Artifacts

- `experiments/exectv2_sf_agentic_redo_hard_panel.py` (driver)
- `experiments/exectv2_sf_agentic_redo_hard_panel_results.jsonl` (212 rows)
- `experiments/exectv2_sf_agentic_redo_hard_panel_results.md` (generated report)
- `experiments/exectv2_sf_react_single_agent_smoke.py`,
  `experiments/exectv2_sf_multi_agent_ceiling_smoke.py`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/agentic/`
  (`tools.py`, `react_single_agent.py`, `multi_agent_ceiling.py`)

## Guardrails respected

`test59`/`test450` never read or run. No holdout row-level inspection. No
gate threshold changed after seeing results (the empty-gold correction is
a metric-mechanics fix applied to where the panel carries signal, not a
threshold change).
