# Gan 2026 — `resolve_label` Graph Query Spec

Date: 2026-06-15
Status: design spec (validation-only). Implements line 3.4 of the KG design note
as the single, ablatable home for the selection-precedence and unknown-boundary
rules catalogued in the rule register. Not a holdout authorization. Governed by
the existing 25→50→250 validation ladder and the `gan2026_split_v1` lock.

Related:
- `docs/design/gan2026_rule_register.md` (the rules this query consolidates;
  contradictions C1–C5)
- ``
  §3.4 (the parent design)
- Code: `state_graph/{graph,edges,ontology,projection}.py`

## 1. Why this query exists

Today the final-state decision for graph-sourced candidates is made in
`projection.py::project_graph_to_gan` by a **flat priority over node kinds** that
does *no edge resolution*. The current-vs-historical and seizure-free-vs-frequency
precedence therefore lives in three incompatible places — the deterministic
`selection_score` integers, the projection node-ordering, and prompt prose —
which is the direct cause of register contradictions **C1** and **C2**.

`resolve_label` puts the **admission and typed-edge precedence** for graph
candidates into one named, provenance-bearing query. It does **not** replace the
projection's intra-kind ranking: as shipped, `resolve.py` deliberately
*delegates* the final intra-kind pick to `project_graph_to_gan` over the
edge-resolved, ontology-admitted node set, so the resolver is byte-equal to the
baseline projection on rows where no new mechanism fired and any Purist delta is
attributable to dual-validation / supersession / refinement alone. Absorbing the
ranking ladder into `resolve_label` is a tracked follow-up (see register
"resolve_label scope note"), not part of this spec.

```
resolve_label(graph) -> ResolvedLabel(
    final_label, final_kind, monthly_frequency,
    selected_node_ids, used_edge_ids, rationale, decision_trace,
    # outcome is always a label; "unknown" is the only soft option.
    # "abstain" is deferred (C5) and not a field on the shipped model.
)
```

It is a single ablatable component with its own row-change accounting for
admission and edge resolution, not logic smeared across `selection_score`,
`_select_projection_nodes`, and nine selector versions.

## 2. Inputs (all already exist)

- `graph.nodes : tuple[StateGraphNode]` — each carries `semantic_kind`,
  `monthly_frequency`, `evidence` (span), `assertion_status`, `temporality`,
  `applies_to`, `rule_id`, `graph_errors`.
- `edges = derive_edges(graph) : tuple[GraphEdge]` — `SUPERSEDES`, `REFINES`,
  `CONTRADICTS` (`state_graph/edges.py`).
- `ontology = AdmissibleStateOntology()` — `is_admissible_assignment`,
  `is_admissible_transition` (`state_graph/ontology.py`).

No new model call. No new schema field on the frozen graph model (edges are
derived).

## 3. Algorithm (deterministic, ordered)

### Step 0 — Admit
Drop any node whose `is_admissible_assignment` is `False` (records the rejection
reason in `decision_trace`). This is where register **§9.1 / §7** is enforced:
`UNKNOWN_ONLY_SHAPES` nodes that carry a `frequency`/`seizure_free` state are
**removed from contention**, not merely down-ranked. Resolves **C2** at
generation time *for the graph path* — the over-inferred component never reaches
selection.

### Step 1 — Apply `SUPERSEDES`
For every legal `SUPERSEDES` edge, mark the `target` (older) node dominated.
Dominated nodes cannot be selected but stay in the trace. This is the **principled
replacement** for the §5 priority integer that put `current_seizure_free` above
`frequency`: precedence is decided by *temporality of the specific competing
statements*, not by a global kind ranking.

### Step 2 — Apply `REFINES`
For every legal `REFINES` edge, replace the base (vaguer) node with the refiner
in the candidate set: cluster cadence + burden (§9.2), or explicit count+window
over a vague mention. Cadence stays immutable (`is_admissible_transition` already
rejects cadence-changing refinements).

### Step 3 — Resolve `CONTRADICTS` (the C1 decision, stated once)
A `CONTRADICTS` edge means a current positive rate and a current seizure-free
assertion coexist for the same `applies_to`. **Rule (proposed):**

- If exactly one side is `SUPERSEDES`-dominated, keep the survivor.
- Else **the current positive rate wins over the current seizure-free
  assertion**, and the seizure-free node is flagged
  `contradicted_by_current_rate`. Rationale: a positive current rate is direct
  evidence of ongoing seizures; a same-period "seizure-free" claim is then about
  a *subtype/scope* and must not zero out the rate.
- A *historical* rate never contradicts a *current* seizure-free state (it is
  `SUPERSEDES`-dominated in Step 1).

This is the explicit answer to **C1** (accepted as
[[0016-current-rate-supersedes-coexisting-current-seizure-free]]): precedence is
`current frequency` > `current seizure-free` *only when they genuinely conflict
for the same target*; otherwise both can stand and Step 4 ranks them. It
reconciles the two engines by making the deciding variable *temporality +
target*, not a global integer.

> **Code debt:** `resolve.py::_surviving_contradiction` as shipped returns
> `"unknown"` on this edge instead of keeping the rate — it predates the C1
> decision. The fix (keep the rate node, flag the seizure-free node
> `contradicted_by_current_rate`, fall through to ranking) is predeclared in the
> register and rides the validation ladder; `unknown` is retained only for
> conflicts not attributable to a current rate.

### Step 4 — Rank survivors
Among admissible, non-dominated survivors, rank by a **single** ordering (the one
the register will cite as canonical), with ACD overrides preserved:

1. ACD-010 recent major-semiology relapse
2. ACD-008/009 explicit-summary / previous-month-active
3. current `frequency` (by `monthly_frequency`)
4. current `seizure_free`
5. `unresolved_multiple`
6. `unknown`
7. `no_reference`

Note this is the **projection** ordering (frequency > seizure_free), now safe
because Step 1–3 already removed the cases where the deterministic ladder's
inversion was actually doing work (historical rate vs current control).

### Step 5 — Outcome
- ≥1 survivor → `outcome="label"`, emit the top survivor's label.
- 0 survivors but admissible `unknown`/`no_reference` nodes existed → `outcome="unknown"`.
- Competing current `frequency` hypotheses with different labels and no resolving
  edge → `outcome="unknown"` with `uncertainty_flag=competing_frequency_hypotheses`
  (today's `_should_emit_competing_uncertainty`, retained).
- **Abstention (C5, deferred):** the production path **stays single-label**;
  `unknown` is the only soft option. The gated `outcome="abstain"` /
  `allow_abstention` hook is **not implemented** — `resolve.py` has no `outcome`
  field, by decision. Abstention is deferred until a coverage/over-abstention
  evaluation contract exists, at which point the `outcome` field, the flag, and
  its tests land together as one ablatable component. A never-exercised
  default-`False` branch is exactly what the attribution audits flag, so the
  decision surface is recorded in prose (register C5), not as dead code.

## 4. What this resolves vs leaves open

Resolves by construction:
- **C1** — one canonical precedence, decided by edge resolution (Steps 1–4).
- **C2** — over-inferred graph components are dropped at Step 0, not patched
  after rendering (the v0.10 deterministic-repair probe's `-8/-10` lesson).

Left as explicit, flagged decisions (not silently resolved):
- **C3** — cluster preservation/strip/multiply: `resolve_label` consumes
  whatever cluster label the node carries; the single rule must be stated in
  §1.3/§2.2/§4.3 of the register and enforced in the *builder*, not here.
- **C4** — vague cluster-count null-route: decide whether the graph builder
  honors the v6 decision before `resolve_label` ever sees such a node.
- **C5** — abstention: **deferred** (decision 2026-06-15). Production stays
  single-label; no `outcome`/`allow_abstention` surface is built until an
  evaluation contract exists. (Was "gated default-off outcome"; that dead branch
  is not implemented.)

## 5. Test + ablation contract

- One focused test per step (admit / supersedes / refines / contradicts / rank /
  outcome), reusing the supervisor-6 unknown panel and the paired source-near
  hard negatives as fixtures.
- `resolve_label` must be ablatable against the current
  `project_graph_to_gan` flat projection: report W→C / C→W and per-band
  changed-label precision (`band_weekly`, `band_unknown`) on validation only.
- Promotion follows the KG note's ladder: Stage A oracle uplift over the
  no-correct residual must be non-negligible before any live run; correct→wrong
  regressions must be near zero; gains must localize to named edges/ontology
  constraints, not opaque re-ranking.

## 6. Honest bottom line

`resolve_label` does not add new clinical knowledge; it relocates precedence and
unknown-boundary rules that already exist into one place where C1 and C2 stop
being possible by construction, and where C3–C5 become visible decisions rather
than buried inconsistencies. If Stage A shows no oracle uplift over the
no-correct residual, the query is not worth building — same stop rule as the
parent design note.
