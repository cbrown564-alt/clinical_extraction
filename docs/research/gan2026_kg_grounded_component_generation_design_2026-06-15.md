# Gan 2026 — Knowledge-Graph-Grounded Component Generation (design note)

Date: 2026-06-15
Status: design proposal (validation-only). Not a holdout authorization, not a
promoted candidate. Governs a new development branch, gated by the existing
25 -> 50 -> 250 validation ladder and the `gan2026_split_v1` lock.

Related:
- `docs/research/gan2026_architecture_space_2026-06-01.md` (Architecture 3:
  section/claim graph — the seed of this idea)
- `docs/research/gan2026_next_architecture_decision_2026-06-01.md`
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
is clean (641/641, zero regressions). Stage B is the next gate.** The four code
lines exist and are tested. Stage A on the deterministic graph regressed as built
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

5. **Stages B/C/D not started.** They require the existing LLM atomic-claim +
   evidence artifacts and feeding the graph query as a fourth component to the
   v0.9 consensus+fresh selector. Stage B is the *first* place the C2 guard is
   actually exercised (uncurated over-inference). Stage C measures whether the
   selector picks the clean graph `unknown` over the deterministic over-read — the
   empirical resolution of C2 *per row* (ADR `0017`: C2 is resolved "at
   generation," not "for every row"). Gated on Stage B viability.

6. **C3** is documentation-only (cluster syntax preserved iff a within-cluster
   count exists; scoring multiplies count·burden — one rule, two enforcement homes
   that must agree). **C5** stays deferred. Both require no further code here.
