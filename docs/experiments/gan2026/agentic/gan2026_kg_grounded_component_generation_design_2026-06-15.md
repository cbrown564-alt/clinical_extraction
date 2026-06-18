# Gan 2026 — Knowledge-Graph-Grounded Component Generation (design note)

Date: 2026-06-15
Status: design proposal (validation-only). Not a holdout authorization, not a
promoted candidate. Governs a new development branch, gated by the existing
25 -> 50 -> 250 validation ladder and the `gan2026_split_v1` lock.

Related:
- `` (Architecture 3:
  section/claim graph — the seed of this idea)
- ``
- `docs/design/gan2026_normalization_semantics.md`
- `PROJECT_STATUS.md` (the V12 fresh-evidence reasoner + consensus+fresh selector
  line, and the residual component-generation diagnosis)
- Existing code: `tasks/seizure_frequency/gan2026/state_graph/{graph,coverage}.py`,
  `experiments/boundary_state_graph_replay.py`,
  `experiments/claim_table_component_ablation.py`

---

## 1. Why this note, now

The recent literature consensus on making LLM pipelines more reliable converges
on three mechanisms, all of which the Gan line is currently approximating by
hand rather than by structure:

1. **Anchored extraction with provenance** — every emitted fact is tied to a
   precise source span; anchoring is the primary hallucination-reduction lever
   (AEVS / anchor-constrained frameworks).
2. **Ontology-constrained normalization** — facts are resolved into a controlled
   state vocabulary within a *fixed boundary*, so semantically distinct states
   cannot silently collapse (KARMA-style schema-guided extraction).
3. **Dual validation** — a fact is admitted only after passing both a structural
   shape check and a semantic check (SHACL-style + semantic).

The honest caveat from the same literature must be stated up front: injecting a
graph layer can **break cases the bare model already got right**, and
over-retrieval adds noise. A knowledge graph is therefore not a generalization
silver bullet. Its defensible value here is narrower and concrete, and it lines
up exactly with where this project is currently stuck.

### What the project is actually stuck on (from `PROJECT_STATUS.md`)

The honest diagnosis in the status doc is not a selection problem any more — it
is a **component-generation** problem:

- The consensus+fresh selector has been driven from v0.1 to v0.9 (validation
  `712/750` -> `733/750`), but every version is labelled *revise-only*,
  *validation-mined*, with weak `band_weekly` / `band_unknown` precision.
- The registered v0.9 residual audit puts the **selector-only oracle ceiling at
  `739/750` with current components**. Of the `17/750` residual errors, `6` have
  a correct unselected component, but **`11` have no correct deterministic,
  consensus, or fresh-evidence component available at all**.
- That no-correct residual is concentrated in exactly two failure shapes:
  **unknown-boundary over-inference** (inferring a rate or seizure-free duration
  from last-event-only / open-ended "since" / recent-rate evidence) and
  **cluster-burden misses**.
- The status "Now" board says it directly: *"pivot from selector micro-gates
  toward better component generation."*

So the binding constraint is not "which component do we pick" — it is "no
correct component exists to pick." That is precisely the gap an anchored,
ontology-constrained, dual-validated component generator is built to close. The
selector treadmill is a symptom of asking a chooser to fix a generation problem.

### And the val -> test gap

v0.6 + safety-v0.9 just failed the frozen `test450` holdout (`351/450`, below the
V0 baseline `364` and the `383` target). The family taxonomy localizes the
regression to the **weekly band**. A selector micro-gate cannot carry a
band-level policy across the val->test gap because the policy is encoded as a
pile of conditional string heuristics, not as an inspectable, ablatable
structural property. A typed state graph makes "what band is this, and why" a
first-class object with provenance — which is the only honest way to *predeclare*
a boundary-band policy and then test whether it survives.

---

## 2. What already exists (do not rebuild)

`state_graph/graph.py` already defines most of the substrate:

- `ClinicalFrequencyStateGraph` and `StateGraphNode` with `kind`,
  `semantic_kind` (`FrequencyLabelKind`), `monthly_frequency`, an
  `EvidenceSpan` (text + char offsets), `assertion_status`, `temporality`,
  `certainty`, `applies_to`, `rule_id`, and `graph_errors`.
- Two builders: `build_state_graph()` (deterministic oracle span harvester) and
  `build_state_graph_from_atomic_claims()` (LLM atomic claims, exact-evidence
  gated).
- `graph_invariance_signature()` — the fields expected to survive paraphrase
  (already a generalization-stability hook).
- `competing_hypothesis_node_ids` and `missing_variable_flags`.
- `coverage.py::oracle_coverage_summary()` — per-gold-kind representability.

**The graph is currently a diagnostic / oracle, not a prediction-bearing
component.** It harvests nodes and measures whether gold is representable; it
does not (a) carry typed edges, (b) enforce an admissible-state ontology, (c)
run dual validation before a node is admitted as a component, or (d) feed minted
components into the selector. This note is about promoting it across exactly
those four lines — nothing more exotic.

---

## 3. The proposal

**Promote `state_graph` from an oracle into an anchored, ontology-constrained,
dual-validated component generator that mints labelled candidates for the
no-correct-component residual, and expose the final label as an explicit,
ablatable graph query.** Keep the consensus+fresh selector as the chooser over
an enlarged, better-typed component pool.

Four concrete additions, each small and each mapping to one literature mechanism:

### 3.1 Typed edges (relations), not just node bags

Today the graph is a set of nodes plus a flat `competing_hypothesis_node_ids`
list. Add a minimal, closed set of typed edges between nodes:

- `SUPERSEDES` (a later/current statement overrides an earlier one) — directly
  encodes the recency / current-vs-historical decisions that the prompt prose
  and selector currently arbitrate.
- `REFINES` (cluster burden refines a cluster cadence; count+window refines a
  vague mention) — encodes the cluster-burden and denominator/window cases that
  the selector's v0.4 / v0.8 gates handle as string rules.
- `CONTRADICTS` (seizure-free assertion vs a positive current rate) — makes the
  boundary conflict explicit instead of implicit.

Edges are the literature's "relation extraction" step and the reason a graph
beats a claim table: the boundary-band and recency decisions become **edge
resolutions over typed nodes**, each carrying the provenance of both endpoints.

### 3.2 An admissible-state ontology (the "fixed boundary")

Encode the `FrequencyLabelKind` lattice as an explicit constraint object:
the legal states (`frequency`, `seizure_free`, `unknown`, `no_reference`,
`unresolved_multiple`) and the **admissible evidence -> state assignments and
admissible state transitions** under edge resolution. Two rules matter most,
because they are the project's two failure shapes:

- **No over-inference out of `unknown`.** Last-event-only, open-ended "since",
  vague-count, and relative-trend evidence may *only* anchor an `unknown` (or
  `no_reference`) node. They may not mint a `frequency` or `seizure_free` node.
  This is the unknown-boundary discipline that the selector currently enforces
  reactively (v0.3, v0.6, v0.7) — but as an ontology constraint it is a
  *generation-time* guard, so the bad component is never minted in the first
  place.
- **Cluster cadence is preserved, burden is refinable.** A cluster node's
  cadence is immutable under `REFINES`; only events-per-cluster may be refined.
  This is selector v0.4's cluster gate, lifted to the generator.

This is the ontology-grounding mechanism: a fixed boundary the generator may not
cross, which is exactly what stops the unknown-boundary over-inference that
dominates the no-correct residual.

### 3.3 Dual validation before admission

A node becomes an admitted component only if it passes:

- **Structural (shape) validation** — schema-valid `StateGraphNode`, exact
  evidence substring present in the note (`certainty="certain"` requires a
  located span), normalized label parses.
- **Semantic (transition) validation** — the node's evidence -> state assignment
  is admissible under 3.2, and any edge it participates in is a legal transition.

Nodes that fail semantic validation are retained but flagged
(`graph_errors`), never emitted as components. This is the SHACL-style dual gate
and it is also the attribution discipline the `research_drift_audit` keeps
asking for: an admitted component carries, by construction, its provenance span,
its rule_id, and the constraint it satisfied.

### 3.4 The final label as an explicit graph query

Replace "selector picks a string" for graph-sourced candidates with a named
`resolve_label(graph) -> (label, selected_node_ids, rationale)` query that:
resolves `SUPERSEDES`/`REFINES`/`CONTRADICTS` edges over current asserted nodes,
applies the admissible-state lattice, and returns the surviving node's label
plus the node IDs and edges it used. The query is a single, ablatable component
with its own row-change accounting — not logic smeared across prompt prose and
nine selector versions.

The consensus+fresh selector stays, but now it chooses among
{deterministic, consensus, fresh-evidence, **graph-query**} components. The graph
query's job is specifically to *mint a correct component for the `11/750` rows
where none currently exists*.

---

## 4. Claim type, repair boundary, and what stays out

Claim type: **`hybrid_llm_extractor`** for the graph-as-component-generator line.
The prediction-bearing components are (a) the LLM atomic-claim extractor feeding
`build_state_graph_from_atomic_claims`, and (b) the deterministic
`resolve_label` graph query. Both are named, isolated, and ablatable; neither is
hidden repair.

Allowed deterministic behaviour: schema/shape validation, exact-substring
evidence gating, the admissible-state ontology constraint, typed-edge resolution
in `resolve_label`, and scorer-compatible label grammar.

Disallowed (would convert this into unlabelled semantic repair): any
evidence-state reclassification *outside* the declared ontology, diary/calendar
arithmetic reconstruction, cluster reconstruction beyond `REFINES`, or a
post-hoc string override of the graph query's output. If the graph query needs
such repair to score, the branch is paused and reclassified — same stop rule as
the 2026-06-01 decision doc.

The existing **no-test-tuning guardrails are unchanged**: development is
validation-only on `gan2026_split_v1`; the locked `test450` remains
aggregate-only and is not touched by this branch without a separate frozen
protocol and explicit authorization.

---

## 5. Experiment ladder (validation-only)

All runs reuse the shared Gan CLI runner so split/cache/reuse/report metadata
stay comparable, and all are no-call replays where the required atomic-claim and
evidence artifacts already exist.

**Stage A — oracle uplift (no model spend).** Extend `oracle_coverage_summary`
to report representability *after* typed edges + ontology constraint are added,
broken out by family band (`band_daily`, `band_weekly`, `band_unknown`,
`band_zero`). Goal: show that the enriched graph *can represent a correct
component* for a meaningful share of the `11/750` no-correct residual. If it
cannot, stop — the mechanism is wrong and no run is justified.

**Stage B — 25-row schema/evidence gate.** Build graphs from existing atomic
claims on 25 validation rows. Report: schema-valid node rate, exact-evidence
rate, ontology-rejection counts (and that rejected nodes are the over-inference
cases), and whether `resolve_label` produces interpretable, component-localized
output. No promotion; this is a viability gate.

**Stage C — 50-row component-contribution test.** On the first 50 validation
rows, measure the graph query purely as a *new component* fed to the v0.9
selector: how many of the previously no-correct rows now have a correct
component, raw-wrong -> final-correct improvements, and critically
**raw-correct -> final-wrong regressions** (the literature's "breaks cases the
model got right" risk — this is the number that kills the branch if it is
non-trivial).

**Stage D — 250-row promotion gate.** Only if Stage C shows net component uplift
with near-zero correct->wrong regression and the gains are explained by named
edge/ontology families (not opaque). Report per-band changed-label precision,
especially `band_weekly` and `band_unknown`, since those are the val->test
regression surface.

---

## 6. Stop conditions and promotion contract

- **Promote to the next ladder stage only if** the prior stage's gains localize
  to named edge types or ontology constraints, exact evidence is intact, and
  correct->wrong regressions are near zero.
- **Pause and reclassify** if `resolve_label` needs disallowed semantic repair
  to be interpretable, or if the graph query merely re-derives the existing
  deterministic component (no new correct components for the residual).
- **Reject** if Stage A oracle uplift over the no-correct residual is negligible,
  or if any stage shows the graph layer breaking band cases the bare components
  already handled (the explicit literature caveat).
- A high validation score triggers an **attribution audit before promotion**:
  per-component row-change accounting and per-band precision, per the
  architecture-space promotion contract.

## 7. Honest bottom line

This is not proposed as a generalization cure. It is proposed because the
project's own residual diagnosis is component starvation, and the most defensible
fix for "no correct component exists" is a generator that is *anchored*
(provenance by construction), *ontology-constrained* (cannot over-infer out of
the unknown boundary), and *dual-validated* (cannot admit an unsupported node) —
the three mechanisms the external consensus actually supports. It also converts
the boundary-band policy from selector string-heuristics into a typed,
ablatable structure, which is the only form in which a `band_weekly` policy can
be predeclared and honestly tested against the val->test gap. If Stage A does not
show oracle uplift over the no-correct residual, the idea is wrong and we spend
nothing further.

---

## 8. Implementation status (2026-06-15)

Status: **the predeclared edits are implemented and tested; the re-scoped Stage A
is clean (641/641, zero regressions); Stage B has now run in two passes (§8.4
below). The first pass replayed the stale 2026-06-02 atomic-claim graphs and the
C2 over-inference guard fired 0 times — but that was an artifact defect (the
conversion had dropped `raw_frequency`, minting every node `unknown`), not a guard
defect. The rebuilt pass re-converts the same v3 claim-table with `raw_frequency`
normalization; the graph now mints quantifying states (resolve final-kinds 13
frequency / 7 unresolved_multiple / 4 unknown / 1 no_reference, no longer uniformly
`unknown`) and the guard is exercised — it fired once, an
`over_inference_out_of_unknown:last_event_only` rejection of a `two episodes`
mention that parsed to a rate. Stage B is therefore a structural + interpretability
pass with the guard now demonstrably live. Stage C has now run (§8.5 below): on
the predeclared first-50 validation rows the v0.9 pool is already Purist-correct
on all 50, so the no-correct residual is not in this slice and Arm 1 has zero
targets; in Arm 2 an unconditional graph component only regresses (P1 −20, P3 −5,
both zero W→C), and only the independent-corroboration posture (P2) is
regression-safe — and exactly neutral. Stage C decision: `revise` — the graph may
enter the selector only under corroboration gating, and the component-starvation
uplift must be tested where the residual lives under a separate predeclared
protocol (not by slice-shopping within Stage C). Stage D has now run (§8.6 below):
the same P2-gated component at 250-row scale on a predeclared, residual-inclusive
slice (11 no-correct rows ∪ first 239 non-residual in source order, rebuilt from
the v4 claim-table — the only no-call source covering the residual). Arm 1 shows
the generator finally does its job: a Purist-correct competing component now exists
for `7/11` residual rows, localized to the ontology-guard families
(`unknown_over_quantified_rate` 5/5, `last_event_or_seizure_free_overinfer` 5/6).
P2 is regression-safe (C→W 0, `band_unknown` override precision 0.96), so the
predeclared gate returns `promote` — but only of the *generator*: P2 *recovers*
`0/7` of those residual rows at selection time (corroboration cannot fire where
every other component is wrong), so realized end-to-end uplift is nil (+1
incidental). Stage D decision: `promote` clears the validation ladder, **not** a
holdout authorization; the binding problem moves from component generation to a
corroboration-free selection trust rule.** The four
code lines exist and are tested. Stage A on the deterministic graph regressed as built
(−82 Purist, §8.2 below) — exactly the literature caveat in §1 and the Stage A
*reject* condition in §6 — but the regression was diagnostic, not fatal: it
surfaced contradiction **C2**, now resolved (ADR `0017`). With the guard scoped
to the uncurated graph path, the deterministic-graph Stage A is a near-neutral
no-op (`resolve_label − projection = 0`, no curated nodes rejected), so the
guard's real test moves to Stage B. The C1/C2/C4 edits below all landed on the
validation-only ladder; no holdout rows were touched.

Decisions that govern the resume (all 2026-06-15, see `docs/decisions/` and
`docs/design/gan2026_rule_register.md`):

- **C1** — `0016-current-rate-supersedes-coexisting-current-seizure-free`: a
  *current* positive rate wins over a coexisting *current* seizure-free
  assertion; flag the seizure-free node `contradicted_by_current_rate`. `unknown`
  is reserved for conflicts not attributable to a current rate.
- **C2** — `0017-ontology-over-inference-guard-is-graph-path-only`: the
  over-inference guard runs **in parallel** — it constrains graph-minted
  components only and does **not** filter the legacy deterministic path. The fix
  for the no-correct residual is a *new clean competing `unknown` component* the
  selector can choose, not retroactive suppression of the deterministic over-read.
- **C3** documentation-only; **C4** a new builder guard (vague cluster-*count*
  null-route, honoring v6); **C5** abstention deferred — production stays
  single-label, no `outcome`/`allow_abstention` surface is built.
- Algorithm home: `docs/design/gan2026_resolve_label_spec.md`.

Note: the paths in §2/§5 of this note are stale. The code lives under
`src/clinical_extraction/tasks/seizure_frequency/gan2026/state_graph/`, and the
experiment scripts under top-level `experiments/`.

### 8.1 What is done

All four promotion lines from §3 are implemented as new modules in the
`state_graph` package, leaving the frozen `graph.py` model untouched (edges are
*derived*, not stored, so existing serialized artifacts are unchanged):

- **3.1 typed edges** — `state_graph/edges.py`: `GraphEdgeKind`
  (`SUPERSEDES`/`REFINES`/`CONTRADICTS`), a provenance-bearing `GraphEdge`, and
  `derive_edges(graph)`. SUPERSEDES (current over historical, same `applies_to`),
  REFINES (cluster burden over cadence-only via shared cadence period; explicit
  count+window over a vague unknown/unresolved node), CONTRADICTS (current
  positive rate vs current seizure-free, same target). Verified firing on
  hand-built atomic-claim graphs.
- **3.2 admissible-state ontology** — `state_graph/ontology.py`:
  `AdmissibleStateOntology`, `ADMISSIBLE_STATES`, `EvidenceShape`,
  `UNKNOWN_ONLY_SHAPES`, `classify_evidence_shape`, `is_admissible_assignment`
  (the no-over-inference-out-of-unknown guard, register §9.1/§7.7) and
  `is_admissible_transition` (cluster cadence immutable / burden refinable,
  §9.2).
- **3.3 dual validation** — `state_graph/validation.py`: `validate_node`
  (structural: no `graph_errors`, located span when `certainty="certain"`, label
  parses; semantic: admissible assignment) and `dual_validate_graph` returning
  admitted node/edge sets with per-failure provenance. Rejected nodes are
  retained-but-flagged, never silently dropped.
- **3.4 resolve_label** — `state_graph/resolve.py`: `GraphLabelResolution` +
  `resolve_label(graph)`. Drops superseded/refined targets and, for the final
  rank, **delegates to the existing tuned `project_graph_to_gan` over the
  edge-resolved, admitted node set** so it equals the baseline projection on rows
  where no new mechanism fired (isolating the delta).
- **Stage A coverage** — `state_graph/coverage.py`: `ontology_coverage_summary`
  + `OntologyCoverageSummary`/`BandCoverage`, reporting baseline vs
  admitted-only representability, projection-correct vs resolve-correct, broken
  out by `boundary_band`.
- **Tests** — `tests/test_gan2026_state_graph_ontology.py`, 16 passing (one per
  mechanism + the two failure shapes + Stage A coverage).
- **Stage A runner** — `experiments/build_gan2026_state_graph_ontology_oracle_uplift.py`,
  validation-only / no model spend, writes json+md and a run-registry entry. It
  ran clean on validation750.

### 8.2 Why Stage A regressed as built — diagnosis (this is C2, now resolved)

Stage A on the deterministic graph (validation750):

| Metric | Projection (baseline) | resolve_label |
|---|--:|--:|
| Purist correct | 641 | 559 |

`resolve_label - projection = -82`. By band the targeted residual improves
(`band_unknown` 122 -> **132, +10**) but the rate/zero bands regress hard:
`band_zero` -27, `band_submonthly` -21, `band_weekly` -26, `band_monthly` -16,
`band_daily` -2. That is precisely the literature caveat in §1 and the Stage A
*reject* condition in §6.

Root cause is isolated: delegating the rank to projection produced **byte-identical**
numbers, so the loss is **not** ranking logic — it is **Step 0 admission
rejecting curated deterministic nodes**. Of the rejected nodes, 40 are
`seizure_free` and 20 are `frequency`; the top rule_ids are
`seizure_free.generic_duration_or_since` (28), `seizure_free.since_date` (8),
`seizure_free.current_control_phrase` (4), plus `diary.*`/`cluster.*`/`rate.*`.
The shape detector flags evidence like *"Seizure-free since 27 March 2024"* and
*"no further events since"* as `open_ended_since`/`last_event_only` and so blocks
the `seizure_free` mint — even though gold is *"seizure free for N months"* and
the deterministic rule was right.

This is exactly **register C2**: the ontology guard (§9.1/§7.7) blocks the same
mints the legacy deterministic seizure-free layer (`is_current_seizure_free_evidence`)
generates. The KG note assumed the guard's value would be net-positive; on the
*deterministic* graph it is net-negative because those nodes are curated, not
over-inferred. The guard's real target is the **LLM atomic-claim generator**
(§3.4 / §4), where uncurated over-inference actually occurs — but Stage A as
specified runs on the deterministic graph and cannot show that.

**Decision (C2, ADR `0017`):** the guard is **graph-path-only**. It does not
supersede or filter `is_current_seizure_free_evidence`; the deterministic
over-reads stay in the candidate pool untouched, and correctness comes from a
*new clean competing component*, not from suppression. This is the lesson the
v0.10 deterministic-repair probe paid for at `-8/-10` rows — reaching into the
deterministic path to suppress these over-reads broke cases it already got right
(the §1 caveat, made concrete). Concretely, this maps to §8.3 option 2 below:
Step-0 admission trusts curated deterministic `rule_id`s and applies the
over-inference guard only to uncurated (LLM-generated) nodes, which makes Stage A
on the *deterministic* graph a near-neutral no-op and pushes the real test of the
guard to Stage B (the LLM atomic-claim graph), where over-inference actually
occurs. The `−82` is therefore not a verdict on the mechanism; it is the artifact
of running a graph-generation guard over a curated path it was never meant to
police.

### 8.3 What is now done, and what remains

The register's two "Predeclared code changes" (C1, C4) plus the C2 scoping are
**implemented and tested** (`tests/test_gan2026_state_graph_ontology.py`, 18
passing); the re-scoped Stage A has been re-run. Items 1–4 are done; Stages
B/C/D (items 5–6) remain.

1. **Done — Step-0 guard scoped per ADR `0017` (C2).**
   `ontology.py::is_admissible_assignment` now applies the over-inference guard
   only to **uncurated (LLM-generated) nodes** (`is_uncurated_node`, keyed on the
   `llm-sg-` builder prefix); curated deterministic `rule_id`s are trusted. This
   is the chosen "parallel posture" — option 2 of the two candidates. The
   deterministic seizure-free over-reads stay in the pool; correctness must come
   from a new clean competing `unknown` component, not from filtering them out.
   On the deterministic graph the guard is now a no-op (no curated nodes
   rejected), so its real test moves to Stage B.

2. **Done — C1 fix applied to `resolve_label` (ADR `0016`).** The
   `_surviving_contradiction` `unknown` short-circuit is **removed**.
   `resolve_label` now, per `gan2026_resolve_label_spec.md` §3 Step 3, keeps the
   positive-rate node, flags the seizure-free node(s) `contradicted_by_current_rate`
   (recorded in `contradicted_node_ids` + `uncertainty_flags`), and falls through
   to ranking (projection yields rate-wins via `FREQUENCY > SEIZURE_FREE`).
   `unknown` survives only for conflicts not attributable to a current rate (none
   are derived today, since a CONTRADICTS edge is rate-attributable by
   construction).
   - Added the spec's `decision_trace` and `used_edge_ids` to
     `GraphLabelResolution` so admission / supersession / refinement /
     contradiction are inspectable. Bumped `resolver_id` →
     `gan2026_state_graph_resolve_label_v1` and `ontology_id` →
     `gan2026_admissible_state_ontology_v1` for attribution.
   - **Not added** (deliberately): the `outcome` field and a gated
     `allow_abstention` policy. Per register **C5** (deferred) and spec §3 Step 5,
     the production path stays single-label with `unknown` as the only soft
     option; a never-exercised default-`False` branch is what the attribution
     audits flag. The abstention surface lands only when a coverage/over-abstention
     evaluation contract exists.

3. **Done — C4 builder guard added.** `classify_evidence_shape` now matches a
   vague *count of clusters* (`_VAGUE_CLUSTER_COUNT_RE`, e.g. `"several clusters
   per month"`) and returns `VAGUE_COUNT` **before** the rate/denominator
   short-circuit — so the `per month` denominator no longer rescues it into
   `QUANTIFIED`. A vague cluster *size* (`"multiple per cluster"`) is a different
   axis and is unaffected; legacy `cluster.py` 4.2 is untouched on the
   deterministic path (parallel posture, consistent with C2). Enforcement of the
   null-route still flows through the uncurated-only guard from item 1.

4. **Done — Stage A re-run.** With the guard scoped to uncurated nodes, the
   deterministic-graph Stage A is now near-neutral: **`projection_correct = 641`,
   `resolve_correct = 641`, `resolve_minus_projection = 0`, zero correct→wrong
   regressions**, and `admitted_representable == baseline_representable` in every
   band (no curated nodes rejected). This clears the pre-decision `−82` regression
   that tripped the §6 *reject* condition. Per ADR `0017`, near-neutral on the
   deterministic graph is the expected pass — the *uplift* test is Stage B, where
   the guard actually fires on uncurated over-inference. Artifacts:
   `experiments/gan2026_state_graph_ontology_oracle_uplift_stage_a_2026-06-15.{json,md}`.

5. **Done — Stage B run in two passes (guard now exercised).** Full reading in
   §8.4. The first pass replayed the stale 2026-06-02 atomic-claim graphs: the
   structural + interpretability sub-gates passed but the guard fired 0 times,
   because that conversion had dropped `raw_frequency` and minted every node
   `unknown`. The rebuilt pass re-converts the *same* v3 claim-table with
   `raw_frequency` normalization (`state_graph/claim_table.py`, scorer-facing
   grammar only — no diary/window arithmetic): the graph now mints quantifying
   states (resolve final-kinds 13 frequency / 7 unresolved_multiple / 4 unknown /
   1 no_reference) and the guard is **exercised**, firing once on an
   `over_inference_out_of_unknown:last_event_only` mint (a `two episodes` mention
   parsed to `2 per month`). Both sub-gates still pass (80/80 schema-valid + exact
   evidence; 25/25 component-localized). Stage C is now twofold: (a) does the
   selector pick the clean graph `unknown` over the deterministic over-read on the
   `band_unknown` residual (ADR `0017`, C2 per-row), and (b) do the newly-minted
   quantifying graph components add correct candidates without correct→wrong
   regression.

   **Stage C done (§8.5); Stage D done (§8.6).** Stage C fed the graph query as
   a fourth component to the v0.9 selector on the first-50 rows and returned
   `revise`. Stage D re-ran the same P2-gated wiring at 250-row scale on a
   predeclared slice that *does* contain all 11/750 no-correct residual rows. The
   generator clears the ladder on component availability (Arm 1: a correct
   component now exists for **7/11** residual rows, concentrated in the
   ontology-guard families), and the safe posture is regression-free (P2 C→W 0).
   But the safe posture **recovers 0/7** of those residual rows at selection time
   — corroboration cannot fire where every other component is wrong — so the
   realized end-to-end uplift is nil (+1 net, on an incidental non-residual row).
   The binding problem has therefore moved from *component generation* to
   *selection*: a corroboration-free trust rule for the graph's clean `unknown`
   that avoids P3's regressions. **No holdout is authorized.**

6. **C3** is documentation-only (cluster syntax preserved iff a within-cluster
   count exists; scoring multiplies count·burden — one rule, two enforcement homes
   that must agree). **C5** stays deferred. Both require no further code here.

### 8.4 Stage B — atomic-claim viability gate (2026-06-15)

Stage B is the gold-free, no-model-spend viability gate of §5. The summariser is
`state_graph/coverage.py::atomic_claim_viability_summary` (gold-free; tests in
`tests/test_gan2026_state_graph_ontology.py`, now 23 passing). It ran in two
passes: a diagnostic replay of the stale 2026-06-02 graphs, then a rebuilt pass
that normalizes `raw_frequency` so the guard is actually exercised.

#### 8.4.1 First pass (diagnostic) — guard unexercised

Replayed the saved validation25 atomic-claim graphs
(`…llm_atomic_claim_rows_validation25_2026-06-02.jsonl`, from the gpt-4.1-mini
section claim-table v3). Runner:
`experiments/build_gan2026_state_graph_ontology_stage_b_viability.py`; artifacts
`experiments/gan2026_state_graph_ontology_stage_b_viability_2026-06-15.{json,md}`.

| Sub-gate | Metric | Reading |
|---|--:|---|
| Structural (shape) | schema-valid 79/80; exact-evidence 79/80 | pass — the lone reject is `atomic_claim_evidence_not_exact` |
| Semantic (ontology) | over-inference rejections **0/80** | **unexercised** |
| Interpretability | 25/25 decision-traced; 25/25 component-localized | pass |
| Final label | `unknown` 25/25 | the graph minted only `unknown` |

The guard fired 0 times because the 2026-06-02 conversion **dropped each claim's
`raw_frequency`**, so the builder minted every node `semantic_kind ∈ {unknown,
no_reference}` — even the 16 nodes whose *evidence shape* is `quantified`. With no
quantifying state minted, the guard (keyed on `FREQUENCY`/`SEIZURE_FREE` out of an
unknown-only shape) had nothing to police. This is an artifact defect, not a guard
defect: the conversion threw away the information the guard exists to check.

#### 8.4.2 Rebuilt pass — `raw_frequency` normalized, guard exercised

Re-converts the *same* v3 claim-table, but maps each claim's `raw_frequency`
through the project scorer-facing grammar (`state_graph/claim_table.py::
atomic_claims_from_structured_record`, plain `repair_prediction_label` — the
allowed source-near→Gan conversion of §4, **no** diary/window arithmetic), then
rebuilds via the frozen `build_state_graph_from_atomic_claims`. The node *kind*
still comes from the claim type, so a `last_event_only` shape survives even when
its raw frequency parses to a rate — which is exactly what the guard must catch.
Runner: `experiments/build_gan2026_state_graph_ontology_stage_b_rebuild.py`;
artifacts `…_stage_b_rebuild_2026-06-15.{json,md}` plus the rebuilt-graphs replay
artifact `…_stage_b_rebuild_2026-06-15_graphs.jsonl`.

| Sub-gate | Metric | Reading |
|---|--:|---|
| Structural (shape) | schema-valid 80/80; exact-evidence 80/80 | pass |
| Semantic (ontology) | over-inference rejections **1/80** (`…:last_event_only`) | **exercised** — the guard fires on a genuine over-read |
| Interpretability | 25/25 decision-traced; 25/25 component-localized; 0 defaulted | pass |
| Final label | frequency 13 / unresolved_multiple 7 / unknown 4 / no_reference 1 | the graph now contributes quantified candidates, not only `unknown` |

The single firing is the textbook case: row 278's claim *"including two episodes
witnessed by a friend"* (claim type `last_event_only`, `raw_frequency` `"two
episodes"`) normalizes to `2 per month` [`frequency`], and the guard rejects the
uncurated mint as `over_inference_out_of_unknown:last_event_only`. The node is
retained with provenance, never silently dropped, and the row falls through to its
other admitted components. Only one firing, because the normalizer routes vague
quantities (`rare`, `occasional`, `≤ four per day`) to `unresolved_multiple` /
`no_reference` rather than a bare `FREQUENCY`, so those never reach the guard —
itself an upstream form of unknown-boundary discipline.

**What this means for the ladder.** The rebuilt graph is no longer a pure
`unknown`-minter: it supplies both (a) clean competing `unknown` components for the
`band_unknown` over-inference residual (the ADR `0017` C2 target) and (b) genuine
quantified components for the rate bands, with the guard demonstrably blocking the
one uncurated over-read it should. Stage C therefore has both arms to test against
the v0.9 selector: does the selector prefer the graph `unknown` over the
deterministic over-read on `band_unknown`, and do the quantified graph components
add correct candidates with near-zero correct→wrong regression (the §6 stop
condition)? Stage B is a pass; the guard's rejection arm is now live and audited.

### 8.5 Stage C — 50-row component-contribution test (2026-06-15)

Stage C feeds the `resolve_label` graph query as a fourth component to the frozen
v0.9 consensus+fresh selector, on the predeclared first-50 validation rows. It is
a no-call replay: the graph is rebuilt deterministically from the validation50 v3
section claim-table (the strict superset of the Stage B validation25 source,
`raw_frequency` normalized, no diary/window arithmetic); the
deterministic/consensus/fresh components and the v0.9 selected baseline come from
the saved v0.9 validation750 replay. Runner:
`experiments/build_gan2026_state_graph_ontology_stage_c_component_contribution.py`;
artifacts `…_stage_c_component_contribution_2026-06-15.{json,md}` plus the
rebuilt-graphs and per-row accounting JSONL. Decision: **`revise`**.

**Headline.** v0.9 selected Purist is **50/50** on this slice; the graph component
standalone is 30/50 (kinds: 28 frequency / 9 unknown / 7 unresolved_multiple / 6
no_reference).

**Arm 1 — component-pool coverage.** The existing pool ({deterministic, consensus,
fresh}) is already Purist-correct on **all 50** rows, so there are **0 no-correct
targets** in the first-50 slice and the graph mints a correct component for 0 of
them. The `11/750` no-correct residual simply does not live in the first 50 rows
(it includes none of the `band_unknown` over-reads here — all 6 `band_unknown`
rows are already correct, and the graph independently resolves all 6 to a correct
`unknown`). This is a slice fact, not a verdict on the mechanism: the
component-starvation benefit — the entire reason for the generator — cannot be
demonstrated where the residual is absent, and honoring the predeclared slice
forbids shopping for the rows where it is present.

**Arm 2 — selection contribution.** With the graph added as a fourth candidate,
final labels scored against the v0.9 selected baseline (C→W is the §6 kill metric):

| Posture | Overrides | Final Purist | W→C | C→W | Net | C→W bands |
|---|--:|--:|--:|--:|--:|---|
| `P1_unilateral` (override on any disagreement) | 28 | 30/50 | 0 | 20 | −20 | weekly 10, monthly 6, submonthly 3, daily 1 |
| `P2_corroborated` (override only if consensus/fresh agree) | 5 | 50/50 | 0 | 0 | 0 | — |
| `P3_unknown_only` (override only on graph `unknown`) | 8 | 45/50 | 0 | 5 | −5 | weekly 3, monthly 2 |

An *unconditional* graph component only regresses (P1 −20, P3 −5; both zero W→C) —
the §1 literature caveat and the v0.10 deterministic-repair `−8/−10` lesson made
concrete a second time, now from the graph side. The P3 regressions are the
mirror image of the C2 story: the atomic-claim graph over-routes 5 real-rate rows
(weekly/monthly) to `unknown` (a claim-extraction recall gap, not a guard
firing), so an unknown-routing override zeroes out rows v0.9 got right. Only the
**independent-corroboration posture (P2)** is regression-safe — and on this solved
slice it is exactly neutral (0 W→C, 0 C→W), because the graph never contradicts a
consensus/fresh-corroborated label.

**Reading against §6.** Stage C does not clear the promotion bar: there is no net
component uplift to show here (no headroom), an unconditional component breaks
band cases the pool already handled (the explicit *reject* trigger), and the only
safe integration — corroboration gating — adds nothing on this slice. The honest
decision is `revise`, not `reject`: the mechanism is not falsified (it is
regression-safe under P2 and correct on all 6 true-`unknown` rows), but its raison
d'être is untested because the predeclared 50-row slice contains none of the
no-correct residual. Stage D must therefore wire the same P2-gated graph component
at 250-row scale on a slice that actually contains the `11/750` residual, under
its own predeclared protocol, and is the only place the component-starvation claim
can be honestly tested.

### 8.6 Stage D — 250-row promotion gate on the residual (2026-06-15)

Stage D is the §5 promotion gate, run exactly as §8.5 mandated: the **same
P2-gated** `resolve_label` graph component, at 250-row scale, on a **predeclared
slice that actually contains all 11/750 no-correct residual rows**. Runner:
`experiments/build_gan2026_state_graph_ontology_stage_d_promotion_gate.py`;
artifacts `…_stage_d_promotion_gate_2026-06-15.{json,md}` plus the rebuilt-graphs
and per-row accounting JSONL. Decision: **`promote` (clears the validation ladder
only — not a holdout authorization)**.

**Predeclared protocol (fixed before the run, no slice-shopping).**

- *Slice.* The 250-row slice = the **11 no-correct residual rows** (from the
  frozen v0.9 residual component-generation audit) ∪ the **first 239 non-residual
  validation rows in `source_row_index` order**. One deterministic, reproducible
  rule: residual-inclusive by construction, 250-row scale, chosen by source order
  (not by outcome).
- *Claim extractor.* Graphs are rebuilt from the **validation750 v4** section
  claim-table — the *only* no-call source that covers the residual, because the v3
  table the earlier ladder used was never run past the first 250 validation rows
  (10 of the 11 residual rows are unreachable under v3 without new model calls).
  The v3→v4 change is a **declared confound**, held constant across the whole
  slice; a v3↔v4 cross-check on the one overlap residual row (5534) resolves to
  the **same Purist class** (`unknown` both ways), so the extractor swap does not,
  on the one row we can check, change the graph's verdict.
- *Component & posture.* Identical ontology/edge/`resolve_label` query; **P2
  (corroborated)** is the promotion-decision posture (the only Stage C survivor);
  P1/P3 are reported as effect bounds.

**Arm 1 — component availability (the component-starvation fix).** The graph now
mints a Purist-correct competing component for **7/11** predeclared residual rows
(`5534, 6321, 6368, 6571, 11254, 11272, 14025`). The coverage localizes exactly to
the ontology guard's two target families — `unknown_over_quantified_rate` **5/5**
and `last_event_or_seizure_free_overinfer_unknown` **5/6** — and is **0/2** on
`cluster_burden_component_failure` and **0/1** on the
`highest_semiology_or_denominator_conflict` row, which the guard was never built to
address. This is the first direct evidence that the anchored, ontology-constrained
generator does what the whole branch was proposed to do: produce a correct
component where none existed.

**Arm 2 — selection contribution (P2, the promotion posture).**

| Posture | Overrides | Final Purist | W→C | C→W | Net | C→W bands |
|---|--:|--:|--:|--:|--:|---|
| `P1_unilateral` | 188 | 99/250 | 8 | 147 | −139 | daily 14, monthly 35, submonthly 11, weekly 50, zero 37 |
| `P2_corroborated` (promotion) | 28 | 239/250 | 1 | **0** | +1 | — |
| `P3_unknown_only` | 90 | 174/250 | 7 | 71 | −64 | daily 5, monthly 15, submonthly 5, weekly 23, zero 23 |

P2 is regression-safe — **0 C→W**, no `band_weekly`/`band_unknown` regression — and
its changed-label precision is **26/27 = 0.96 on `band_unknown`** (the one
`band_monthly` override is a wrong→wrong, not a regression). The unconditional
postures confirm the §1 caveat a third time: P1 −139, P3 −64, both driven by the
atomic-claim extractor over-routing real-rate rows to `unknown`/`no_reference`.

**The decisive honesty number: 0/7 realized.** Of the 7 residual rows for which the
graph mints a correct component, P2 **recovers 0** at selection time. The single
net +1 is an *incidental non-residual* corroborated override. This is structural,
not bad luck: corroboration requires an independent component to agree, and the
no-correct residual is *defined* by every other component being wrong — so the one
posture that is safe is exactly the one that cannot harvest the residual. Arm 1
(availability) and Arm 2 (realized) therefore diverge completely on the rows that
matter.

**Reading against §6.** The predeclared gate returns `promote` because, for the P2
posture, §6's literal criteria hold: gains localize to the named ontology
constraint, exact evidence is intact (dual validation), correct→wrong is zero, and
new correct components exist for the residual (not a mere re-derivation of the
deterministic component → not the §6 *pause* trigger). What `promote` means here is
narrow and must not be overstated: **the component *generator* clears the
validation ladder; the end-to-end *selection* benefit under the safe posture is
nil (0/7 residual recovered, +1 incidental).** The binding constraint has moved
from component generation (now demonstrably addressable) to **selection**: the open
problem is a corroboration-free trust rule that admits the graph's clean,
dual-validated `unknown` on the no-correct residual *without* re-introducing P3's
71 `C→W` regressions. **Holdout remains unauthorized.** `test450` stays locked; any
holdout protocol is separate, frozen, and explicitly authorized (§4), and must
first weigh whether a realized selection uplift this thin justifies the spend — on
today's evidence it does not, and the next work is the selector trust rule, not a
holdout run.
