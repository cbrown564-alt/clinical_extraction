# Predecessor Lessons Packet

Date: 2026-06-27

Purpose: self-contained, drop-in guidance distilled from predecessor repos that are not part of this checkout (they live alongside it as sibling directories; see "Source Provenance And Re-Verification" below). This packet is private research/development guidance for the closing `clinical_extraction/` phase. It is not a benchmark result, a paper result table, or authorization to reopen locked evaluation surfaces.

## How To Use This Packet

Read this packet when deciding whether a proposed final-phase change is worth doing, how to frame a dissertation caveat, or whether an apparent new idea was already tried under another name.

The key rule is simple: predecessor evidence can guide hypotheses and guardrails; current `clinical_extraction/` protocols remain the source of truth for claims.

Each document is self-contained. It cites historical source paths as provenance, but it also includes the relevant dates, numbers, outcomes, and design implications so that a reader can understand the lesson without opening the old repos.

## Source Provenance And Re-Verification

The predecessor repos cited here are not part of this checkout, but they are present on the same machine as sibling directories of `clinical_extraction/`: `../dissertation/`, `../dissertation-experiments/`, `../dissertation-recursive/`, `../dspy-extraction/`, and `../dspy-extraction-cursor-pilot-artifacts/`. The historical paths in each record are relative to those roots. Every number in this packet is therefore auditable, not just assertable.

A spot-check on 2026-06-27 confirmed fidelity on three load-bearing claims:

- FM4 medication-tuple collapse `~0.60 -> 0.018` (`33x`) matches `dissertation-recursive/docs/53_multi_agent_phase_synthesis_gaps.md`.
- FM1 `h005` confidence `0.95` wrong vs `0.85` correct, verifier fired zero times at n=100, matches `dissertation/docs/run_logs/20260426T190914Z_h005_evidence_required_null_result.md`.
- A1 `FC11` evidence resolver quote presence `0.000 -> 0.981` with medication-name F1 `0.904` preserved matches `dissertation-recursive/docs/60_final_clarification_results_report.md`.

Before any claim in this packet is promoted into the manuscript, re-verify it against its cited source file, for example:

    grep -nEi "0\.018|33x" ../dissertation-recursive/docs/53_multi_agent_phase_synthesis_gaps.md

Predecessor numbers remain at evidence-authority level 4 (see below): they guide hypotheses and caveats, never current performance claims.

## Documents

1. `01_failure_modes_and_guardrails.md`
   - Past mistakes and negative results that should constrain final-phase work.
   - Best for answering: "Are we about to repeat a known failure mode?"
   - Its summary table carries a dated "Status in `clinical_extraction/`" column showing which guardrails are already enforced here versus still open.

2. `02_reusable_best_practices.md`
   - Practices that survived multiple repos and are worth keeping.
   - Best for answering: "How should we run or document a small authorized follow-up?"

3. `03_promising_unfinished_avenues.md`
   - Ideas that remain promising but require fresh protocols, validation-only surfaces, or explicit caveats before any implementation.
   - Best for answering: "What should go into backlog/future work rather than being silently forgotten?"
   - Includes a dated "Current Absorption Status" table marking which avenues are already partly built here (e.g. A9 companion views, A7 optimizer probe).

## Current Claim Boundary

The current `clinical_extraction/PROJECT_STATUS.md` states that ExECTv2 `clinical_headline` recovery is the headline surface, while strict benchmark/CUI results remain diagnostic. As of 2026-06-30 the user has explicitly authorized dev140-scoped development work that applies this packet's lessons to the current paper-ready evidence base (not just documentation/interpretation) — see `PROJECT_STATUS.md` "Done Recently" for the 2026-06-30 entry and `03_promising_unfinished_avenues.md`'s refreshed absorption table for what that authorization has already produced. Gan `test450` and ExECTv2 full-200/holdout row-level inspection remain blocked regardless; that boundary did not move.

Therefore:

- Use predecessor lessons to improve interpretation, documentation, future protocol design, AND to scope bounded dev140-only follow-up work, when explicitly authorized.
- Do not use predecessor metrics as current performance evidence.
- Do not tune from Gan locked-test or ExECTv2 full-200/holdout row-level failures — this remains absolute regardless of the development-authorization state.
- Any new experiment, authorized or not, still predeclares the scorer, split, inspection boundary, component ownership, and stop rule before running (BP1) — authorization widens what may be attempted, not the discipline each attempt is held to.

## Evidence Authority Order

When evidence conflicts, use this order:

1. Current `clinical_extraction/` frozen manifests, project status, protocols, and registered run artifacts.
2. Current aggregate reports explicitly cited by those manifests.
3. Current design docs governing attribution, split discipline, and scoring.
4. Historical predecessor docs summarized here.
5. Agent-generated drafts, SDK output, and mutation reports, only as leads.

## What This Packet Is Not

This packet does not:

- re-score historical runs;
- authorize new model calls;
- inspect protected holdout/full-200 row-level failures;
- claim that predecessor metrics are comparable to current metrics;
- replace `PROJECT_STATUS.md`, the frozen evidence manifest, or the manuscript provenance table.

It is a memory layer with evidence, not a new result source.
