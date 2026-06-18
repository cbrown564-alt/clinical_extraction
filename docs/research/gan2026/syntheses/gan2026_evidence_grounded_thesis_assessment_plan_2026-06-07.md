# Gan 2026 Evidence-Grounded Architecture Thesis Assessment Plan

Date: 2026-06-07

Author: Claude

Status: planning document — defines how to make the project's central
research thesis falsifiable and measurable. No benchmark-comparable claim is
authorized by this document; it defines the *measurement contract*, not a
result.

---

## 1. The Thesis, Stated Precisely

The project's working thesis, as expressed by the user, is:

> A transparent, auditable, evidence-grounded system — built through
> modularity, task decomposition, and explicit evidence trails — is not just
> easier to debug and configure. That same structure is *what makes it*
> more accurate, more generalizable, and more scalable than an opaque,
> monolithic alternative.

This is a **comparative, falsifiable claim**, not a design preference. To
treat it as a real research finding rather than a narrative we have grown
attached to, it needs:

1. operational definitions for every term (transparency, auditability,
   evidence-groundedness, modularity, task decomposition, accuracy,
   generalizability, scalability);
2. a comparison surface where the claim could, in principle, fail;
3. a predeclared scoring rubric, written down *before* the comparison runs,
   exactly mirroring the project's existing predeclaration discipline for
   verifier experiments (`gan2026_validation750_first_verifier_report_predeclaration_v6_2026-06-06.md`
   is the model to follow).

---

## 2. Operationalizing Each Term

Each term below is defined as something *measurable from existing or
near-existing artifacts* — this assessment should consume signal the project
already produces, not invent a new measurement apparatus from scratch.

### 2.1 Structural axes (the "how it's built" side)

| Term | Operational definition | Where the signal already lives |
| --- | --- | --- |
| **Modularity / task decomposition** | Count of independently named, independently ablatable stages/components in the pipeline; whether each can be disabled without breaking the chain (an ablation switch exists and is exercised) | reset-stage component inventory, ablation switch coverage in `llm_candidate_set_clinical_assessment_probe.py`, `reset_stage_component_ablation_v6.py` |
| **Evidence-groundedness** | % of rendered rows whose final value can be traced to a specific source span / candidate / selected fact, with no unexplained "gap" between source and output | exact-trace and source-id validity checks already computed by the null-reduction slice analyzer and the candidate-trace provenance audits |
| **Auditability / transparency** | "Trace sufficiency": can a reviewer, given only the row's trace fields (selected evidence, named rule/family, route reason), explain *why* the system produced this output without reading model internals? Score as a 3-point rubric (full / partial / none) over a sampled row set | route/decision artifacts already carry named families and rule ownership; this needs a predeclared rubric and a sampling protocol, not new instrumentation |

### 2.2 Outcome axes (the "does it work" side)

| Term | Operational definition | Where the signal already lives |
| --- | --- | --- |
| **Accuracy** | Purist-correct / Pragmatic-correct rate on rendered rows, on validation750 | existing scoring artifacts |
| **Generalizability** | The validation-to-`test450` gap: does performance and null/route structure hold up on the locked holdout, or does it collapse? This is the *exact* metric the project has already been protecting via the frozen-aggregate-audit discipline | `gan2026_test450_hn1_frozen_aggregate_audit_2026-06-07.md` and its protocol |
| **Scalability** | Proxy metrics for "how cheaply can this system absorb a new clinical family or a new benchmark task": (a) blast radius of a typical change (files/tests touched to add or fix one family); (b) whether a new family can be added as a *named, ablatable, additive* component without rewriting existing ones; (c) time/iteration cost observed empirically across the HN1-HN5 program | the HN1-HN5 implementation history itself is the empirical record — each promoted family is a data point on "cost to add one general-purpose unit of capability" |

**Important framing note**: "scalability" here does not mean runtime
performance. It means *organizational* scalability — can the system grow in
clinical scope without each addition becoming more expensive than the last.
That is the scalability claim actually embedded in the user's thesis, and it
is the one the modularity/decomposition argument is meant to support.

---

## 3. The Comparison Surface

The natural experiment already exists, and
[[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
produces exactly the surface this assessment needs:

| Architecture | Expected structural profile | Expected outcome profile (to be tested, not assumed) |
| --- | --- | --- |
| Fully deterministic | high transparency/auditability (every decision is a named rule), but possibly low modularity in practice (rules often encode multiple concerns at once) | known signs of overfitting -> likely the *largest* validation-to-test gap |
| Fully LLM | low auditability/evidence-groundedness (reasoning is not inspectable; trace is whatever the prompt asks the model to emit, not structurally guaranteed) | accuracy and generalizability currently **unknown** — this is precisely the gap this thesis assessment should close |
| Hybrid (reset-native) | explicitly designed for high modularity, evidence-groundedness, and auditability (named stages, ablation switches, trace contracts) | the thesis predicts this architecture should show the best combination of accuracy *and* the smallest validation-to-test gap |

This table is written as **predictions to be tested**, not findings. The
entire point of running the comparison is that the hybrid architecture could,
in principle, turn out to be *more* accurate but *not* more generalizable (or
vice versa) — which would falsify or qualify the thesis as stated, and that
result would be just as valuable to record as confirmation.

---

## 4. Organizing The Scattered Evidence Around The Thesis

The codebase survey found that evidence relevant to this thesis already
exists, but is scattered across roughly:

- ~12 overlapping component/ablation analyzers
- ~10 boundary/seizure-free diagnostic analyzers
- multiple validation-test-gap and provenance-validity checks
- the reset-stage component inventory and ablation surface

Rather than building a new bespoke analysis (which would just add a 77th
artifact-analysis file to the pile), this plan's deliverable is **one
canonical "Architecture Thesis Scorecard"** that:

1. is a pure aggregator over existing artifacts — no new clinical logic, no
   new model calls, in the same spirit as `reset_clinical_assessment_pipeline`'s
   "compose, don't reimplement" discipline;
2. has a frozen schema: one row per architecture, one column per
   operationalized axis from Section 2, with a link to the supporting
   artifact(s) for every cell;
3. is explicitly predeclared (its schema and scoring rubric written down and
   reviewed) *before* it is run over real comparison data, so the scorecard
   cannot be quietly reshaped to fit whatever the data shows.

This scorecard becomes the natural, reusable home for "is our thesis true"
going forward — instead of a one-off research note that ages out, it is a
living comparison artifact that can be re-run whenever the three architectures
change materially.

---

## 5. Phasing

| Phase | Work | Gate |
| --- | --- | --- |
| 0 | Freeze the operational definitions and scoring rubric from Section 2 as a standalone predeclaration document (mirrors the verifier predeclaration pattern) | review only — must happen *before* Phase 2 produces any data |
| 1 | Inventory existing analyzers/artifacts and map each to a thesis axis (a cataloging exercise that doubles as input to [[gan2026_repo_consolidation_and_cleanup_plan]] Phase A) | none |
| 2 | Build the Architecture Thesis Scorecard as a pure aggregator; populate it with whatever comparison data already exists (even partial) as a structural smoke test | none — validation-only |
| 3 | Run the scorecard over the full three-way validation750 comparison from [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]] Phase 1; publish a frozen synthesis read | none — validation-only |
| 4 | Extend the scorecard to the frozen `test450` aggregate audit once that comparison phase is authorized; publish the generalizability column with real numbers | **requires the same explicit authorization gate as the comparison plan's Phase 4** |
| 5 | Write the thesis verdict: confirmed / confirmed-with-qualification / falsified-in-part, with the scorecard as primary evidence | none — synthesis only |

---

## 6. Guardrails

- **Predeclare before measuring.** The single biggest risk to this workstream
  is post-hoc rationalization — defining "auditability" in whatever way makes
  the hybrid pipeline look best after the fact. Phase 0's predeclaration
  document is the safeguard, and it should be written and reviewed before any
  comparison numbers exist.
- **Reuse, don't rebuild.** Every signal in Section 2's "where the signal
  already lives" column should be consumed from its existing source. If a
  needed signal does not yet exist, that is itself a finding (a gap in the
  project's own evidence-groundedness), and should be named as such rather
  than quietly patched over with a new one-off script.
- **Report disconfirming results as prominently as confirming ones.** If the
  fully-LLM architecture turns out to be more accurate *and* more
  generalizable than the hybrid (a real possibility, since it is currently
  unmeasured), that is the most important possible output of this workstream
  — it would mean the thesis needs revision, and that should be stated
  plainly, not buried.
- Inherit every guardrail from
  [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
  regarding `test450`: this plan touches the locked holdout only through that
  plan's authorized, frozen-aggregate Phase 4.

---

## 7. Open Questions

1. Is "trace sufficiency" (Section 2.1) better measured by a human-rater
   rubric over a sampled row set, or can parts of it be made fully mechanical
   (e.g., "every rendered value has a non-null exact-trace field")? A hybrid
   of both is likely correct — mechanical checks for the floor, human rating
   for the ceiling — but the split needs to be predeclared.
2. Should "scalability" be assessed only retrospectively (mining the HN1-HN5
   implementation history for cost data), or does it warrant a small forward
   experiment — e.g., timing how long it takes to port one new family into
   each of the three architectures under controlled conditions?
3. How should the scorecard handle the fact that the three architectures are
   not at the same maturity level (the hybrid has had far more iteration than
   the fully-LLM line)? A naive comparison risks penalizing the less-mature
   architecture for immaturity rather than for any structural property. The
   predeclaration in Phase 0 should explicitly name this confound and decide
   how — or whether — to control for it.

---

## 8. Relationship To The Other Two Workstreams

- This plan is **downstream** of
  [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]: it
  cannot produce real numbers until that plan's Phase 1 comparison exists.
- This plan's Phase 1 cataloging of scattered thesis-relevant analyzers
  **feeds directly into** [[gan2026_repo_consolidation_and_cleanup_plan]]
  Phase A — the same survey work serves both "what supports our thesis" and
  "what should we keep."
- The Architecture Thesis Scorecard, once built, should become one of the
  **kept, canonical** artifacts that survives the cleanup in
  [[gan2026_repo_consolidation_and_cleanup_plan]] — it is exactly the kind of
  consolidated, DRY, principle-organized artifact that workstream is meant to
  produce more of.
