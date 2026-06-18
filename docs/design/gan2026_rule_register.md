# Gan 2026 — Aggregation / Selection / Unknown-Boundary Rule Register

Date: 2026-06-15
Status: consolidation reference. Development-split research note, not a holdout
result or benchmark claim. States each operative rule **once**, with provenance,
its code/doc home, and the open contradictions between layers. Companion to the
`resolve_label` spec that proposes a single home for the selection-precedence and
unknown-boundary rules.

Related:
- ``
  (the KG component-generation design this register feeds)
- `docs/design/gan2026_resolve_label_spec.md` (the unifying graph query)
- `docs/design/gan2026_normalization_semantics.md` (scoring collapse)
- ``
  (Yujian's clarified unknown policy)
- `` and
  `gan2026_clean_policy_attribution_note_2026-06-01.md` (clean policy boundary)
- ``
- ``,
  `gan2026_human_gold_audit_abstention_policy_report_2026-06-04.md`

## Purpose

The rules governing how the Gan line aggregates evidence, selects a final state,
and decides `unknown`/abstain are scattered across deterministic code, the
state-graph ontology, LLM/agentic gates, and ~10 policy docs. They were sourced
three ways and have drifted into mutual contradiction. This register pulls them
into one inspectable object so the KG line can absorb them deliberately instead
of inheriting the contradictions.

## Provenance legend

- **[A] author-sourced** — directly from Yujian Gan or his own scripts.
- **[I] inferred by implication** — reverse-engineered from gold-label
  consistency on the validation split.
- **[T] trial-and-error** — validation-mined gates, priorities, regexes.

---

## §1 — Numeric scoring collapse (aggregation → number)

Home: `gan2026/labels.py` (`map_purist`, `map_pragmatic`, `boundary_band`),
`gan2026/normalize.py` (`label_to_monthly_frequency`).
Doc: `gan2026_normalization_semantics.md`.

| # | Rule | Prov. |
|---|---|---|
| 1.1 | `unknown`, `no seizure frequency reference`, and unresolved/unknown-cluster cases all collapse to sentinel `1000.0` → Purist `SEIZURE_FREQ_UNKNOWN`. | **[A]** |
| 1.2 | Seizure-free → `0.0`; ordinary labels → yearly bounds → monthly midpoint. | **[A]** |
| 1.3 | **Cluster multiplication**: `N cluster per <p>, M per cluster` scores as `N·M per <p>`. This is the author's *evaluation-script* reading. | **[A]** |
| 1.4 | Purist = 12 bands; the six `BOUNDARY_BANDS` (`band_zero/unknown/submonthly/monthly/weekly/daily`) coarsen them and are the canonical CV fold set. | **[A]** thresholds, **[T]** banding |

Note on 1.3: the author's **CSV-prep parser does the opposite** (drops
`per cluster`, → `N per <p>`). The two author scripts disagree; the project chose
eval-script. See contradiction **C3**.

---

## §2 — Clean scorer-facing gold-normalization (label grammar only)

Home: `gan2026/contract/gold_policy.py`
(`CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES`).
Doc: `gan2026_gold_normalization_policy_question_2026-06-01.md`; **frozen** by
`gan2026_clean_policy_attribution_note_2026-06-01.md`.

These "preserve the selected clinical fact, only match Gan's surface convention":

| # | Family | Example | Prov. |
|---|---|---|---|
| 2.1 | `bimonthly` → `1 per 2 month` (contradictory explicit wording overrides) | 3/3 val hits consistent | **[I]** |
| 2.2 | cluster-name stripping when cadence-only (no within-cluster count) | `clusters every 4 weeks` → `1 per 4 week` | **[I]** |
| 2.3 | vague weekday cadence → `multiple per week` | `most weekdays` | **[I]** |
| 2.4 | vague quantity + explicit denominator → `multiple per <unit>` | `several per week` | **[I]** |
| 2.5 | period dialect / shorthand → Gan syntax | `q1-2d` → `1 per 1 to 2 day` | **[I]** |
| 2.6 | cluster syntax grammar normalization | — | **[I]** |
| 2.7 | single already-totaled count+window → `N per <window>` | `7 in past 3 months` → `7 per 3 month` | **[I]** |

The freeze is load-bearing: this layer is **not** a license to add families when a
row would score better. New families require a fresh direct-citation row-table
review.

---

## §3 — Named deterministic semantic modules (the "not clean" line)

Home: `gan2026/deterministic/rules/{cluster,seizure_free,rate,diary}.py`.
Doc: same as §2 (the boundary is drawn there).

These change epistemic status / compute new labels / select among facts and so
must stay ablatable with separate claim language: upper-bound→point estimate;
seizure-free final selection; **diary/calendar arithmetic**; unknown-vs-no-reference
classification; **cluster arithmetic/reconstruction**; last-event-only elapsed
interval. All **[T]/[I]**.

---

## §4 — Aggregation proper (cluster + diary)

Home: `gan2026/deterministic/rules/cluster.py` (~28 `RuleSpec`s), `rules/diary.py`.

| # | Rule | Prov. |
|---|---|---|
| 4.1 | A regex family emits cluster-syntax labels `N cluster per <p>, M per cluster`, inferring burden, cadence, and date-span denominators. | **[T]** |
| 4.2 | Vague cluster *size* defaults to `multiple per cluster`; vague cluster *count* may emit `multiple cluster per …`. | **[T]** |
| 4.3 | Cluster-syntax labels are kept verbatim (gold uses them) and only multiplied at scoring (→ §1.3). | **[I/A]** |

Note on 4.2: this **contradicts** the v6 decision to keep vague cluster-count
null-routed. See contradiction **C4**.

---

## §5 — Deterministic selection priority ladder

Home: `gan2026/deterministic/deterministic_selection.py` (`selection_score`);
names in `rules/temporal_selection.py`.

Effective `semantic_priority` ordering (lexicographic over
`(semantic, evidence, monthly_frequency)`, highest wins):

| Priority | Reason |
|--:|---|
| 6 | `trigger_conditioned_unknown` |
| 5 | `current_seizure_free` |
| 4 | `frequency` / `specific_current_multiple` |
| 3 | `generic_unresolved_multiple` |
| 2 | `generic_seizure_free` |
| 1 | `generic_unknown` |
| 0 | `no_reference` (fallback) |

**[T]** Key consequence: a current seizure-free assertion (5) and a trigger-only
unknown (6) **outrank a numeric frequency (4)**. "Current/trigger context
overrides a stale rate" is encoded as these integers. `is_current_seizure_free_evidence`
treats `"last seizure on …"` / `"no seizures since last visit"` as seizure-free —
the seed of contradiction **C2**.

---

## §6 — Agentic selection (consensus + fresh)

Home: `gan2026/agentic/consensus_fresh_agreement_selector.py`,
safety gate in `agentic/fresh_evidence_reasoner.py`.

| # | Rule | Prov. |
|---|---|---|
| 6.1 | Keep the deterministic floor unless V12 fresh-evidence reasoning *independently agrees* with exact multi-agent consensus on the same label. | **[T]** |
| 6.2 | Nine versions (v0.1→v0.9) of conservative micro-gates: cluster-cadence precision, boundary rescue, count-window support, parseable denominator refinement, semantic-equivalent unknown handling. | **[T]** |
| 6.3 | Safety gate v0.4→v0.9 blocks named overreach: nonselective unknown replacement, bare seizure-free, open-ended treatment-start denominators, historical-frequency→seizure-free, vague-`multiple` exactification, same-day cluster downgrade; plus scorer-neutral `no_reference`→`unknown`. | **[A] policy / [T] thresholds** |

Status: the selector line is a **converged honest null** — oracle ceiling
`739/750`; `11/750` rows have no correct component; bottleneck is now component
generation, not selection.

---

## §7 — Unknown / abstention boundary

The densest and most contradictory area.

| # | Rule | Home | Prov. |
|---|---|---|---|
| 7.1 | If seizure **count or period is unclear**, prefer `unknown` over an inferred rate. | `unknown_frequency_policy_audit` | **[A]** |
| 7.2 | A most-recent-seizure **date alone** is not a count over a window. | same | **[A]** |
| 7.3 | "Since starting/beginning medication or diet" is not a denominator unless the start/elapsed period is explicit. | same | **[A]** |
| 7.4 | Explicit count **+ usable follow-up period** *can* support a frequency. | same | **[A]** |
| 7.5 | Unclear seizure evidence is usually `unknown`, **not** `no_reference`. | same | **[A]** |
| 7.6 | ACD-003/004/005: vague-count-without-denominator, conditional-only-trigger, relative-only-trend → `unknown`. | `state_graph/graph.py` + projection | **[T]** |
| 7.7 | Ontology `UNKNOWN_ONLY_SHAPES` (last-event-only, open-ended-since, vague-count, conditional-only, relative-trend) may anchor **only** `unknown`/`no_reference`. | `state_graph/ontology.py` | **[A]** policy, **[T]** detectors |

Proposed but **UNIMPLEMENTED in the prediction path** **[I]**: the rich
abstention / human-review contract (coverage, over-abstention, nine review
reasons) from `human_gold_audit_abstention_policy_report` and the
`ambiguity_ownership_protocol`. Production projection forces a single label, so
`unknown` is doing double duty as a genuine state *and* a de-facto abstention.
See contradiction **C5**.

---

## §8 — Projection policy (ACD-003 … ACD-010)

Home: `gan2026/state_graph/projection.py`.
Doc: `gan2026_acd_projection_policy_predeclaration_2026-06-04.md`. All **[T]**.

ACD-006 diary summing; ACD-007 non-epileptic triage → seizure-free; **ACD-008**
explicit current summary rate > derived long-period average; **ACD-009**
previous-month active burden > current-month-to-date zero (unless a longer
seizure-free state is explicit); **ACD-010** recent major-semiology relapse >
interictal rates. Projection priority integers: ACD-009/008 = 8, ACD-010 = 9,
then FREQUENCY = 4 > SEIZURE_FREE = 3 > UNRESOLVED_MULTIPLE = 2 > UNKNOWN = 1.

---

## §9 — State-graph ontology + typed edges (the new substrate)

Home: `gan2026/state_graph/ontology.py`, `edges.py`.

| # | Rule | Prov. |
|---|---|---|
| 9.1 | `UNKNOWN_ONLY_SHAPES` cannot mint `frequency`/`seizure_free` (generation-time encoding of §7). | **[A]** |
| 9.2 | Cluster cadence immutable under `REFINES`; only events-per-cluster refinable. | **[A]** |
| 9.3 | `SUPERSEDES` (current > historical), `REFINES` (burden / count-window over vague), `CONTRADICTS` (positive rate vs current seizure-free). | **[T]** design |

---

## Contradictions C1–C5 (surfaced by this register; all resolved 2026-06-15)

**C1 — Frequency-vs-seizure-free precedence is inverted between the two
selection engines.** `deterministic_selection.py` ranks `current_seizure_free`
(5) **above** `frequency` (4). `state_graph/projection.py::_select_projection_nodes`
selects current-frequency nodes **first**, seizure-free only if none exist. Same
decision, opposite answer.

→ **RESOLVED (2026-06-15, [[0016-current-rate-supersedes-coexisting-current-seizure-free]]):**
a *current* positive rate wins over a coexisting *current* seizure-free
assertion when no `SUPERSEDES` edge breaks the tie; the seizure-free node is
flagged `contradicted_by_current_rate`. A *historical* rate never contradicts a
current seizure-free state (it is `SUPERSEDES`-dominated first). `unknown` is
reserved for conflicts that cannot be attributed to a current rate. This matches
`projection.py` (which already does rate-wins) and isolates the legacy
`deterministic_selection.py` inversion as the outlier to retire. **Code debt:**
`resolve.py::_surviving_contradiction` still returns `unknown` on this edge — see
"Predeclared code changes" below.

**C2 — Author unknown policy vs deterministic seizure-free layer.**
`is_current_seizure_free_evidence` treats `"last seizure on …"` and
`"no seizures since last visit"` as seizure-free — exactly the last-event-only /
open-ended-since shapes §7.2/§7.3 say must be `unknown`. The ontology (§9.1)
sides with the author and blocks these mints; the legacy deterministic path still
generates them and feeds the selector. This is the documented `11/750`
no-correct residual (three "independent" sources making the same over-read).

→ **RESOLVED (2026-06-15, [[0017-ontology-over-inference-guard-is-graph-path-only]]):**
the ontology guard runs **in parallel** — it constrains graph-minted components
only; `is_current_seizure_free_evidence` and the deterministic over-reads are
left in the pool untouched. The fix is a new clean competing `unknown` component
for the selector to choose, not retroactive suppression (the v0.10
deterministic-repair probe's `-8/-10` lesson). C2 is resolved *at generation*;
whether it resolves a given *row* is an empirical Stage C outcome.

**C3 — Three coexisting cluster conventions.** Eval-script multiplies (§1.3),
CSV-prep drops, and `cluster_name_stripping` (§2.2) strips when no burden.

→ **RESOLVED (2026-06-15, documentation-only):** the single rule is *cluster
syntax is preserved iff a within-cluster count exists; otherwise strip to
cadence; scoring multiplies count·burden.* Within our code the two operative
conventions already agree (both key off burden presence); they are enforced in
**two homes that must stay in agreement** — label *shape* (preserve-vs-strip) in
the builder/normalizer (§2.2), and *multiplication* (count·burden) in
`labels.py` scoring (§1.3). CSV-prep's "drop" is the **author's external script,
which the project deliberately does not follow** — provenance, not a live
internal fork. No code change; §1.3/§2.2/§4.3 cite this statement as canonical.

**C4 — Vague cluster-count: rendered vs deliberately null-routed.**
`gan2026_validation750_vague_cluster_count_cadence_decision_v6` keeps
`several/multiple clusters` null-routed; `cluster.py` (4.2) still emits
`multiple cluster per month, multiple per cluster`. Different lineages (V1 rules
vs reset).

→ **RESOLVED (2026-06-15):** the **graph builder honors v6** — a vague *count of
clusters* routes to `unknown`/`unresolved_multiple` even when a cadence
denominator is present; vague cluster *size* (events per cluster) still yields
`multiple per cluster`. **This needs a new guard:** `ontology.py`'s evidence-shape
classifier short-circuits `"several clusters per month"` to `QUANTIFIED` (the
`per month` denominator hits `_DENOMINATOR_RE` *before* the `VAGUE_COUNT`
branch), so today the ontology silently admits the v6-forbidden node. The guard
must distinguish a vague count *of clusters* from a vague count *of events*.
Legacy `cluster.py` 4.2 is left untouched on the deterministic path (parallel
posture, consistent with C2). See "Predeclared code changes" below.

**C5 — Abstention is heavily specified and entirely inactive.** Two protocols
define a coverage/over-abstention contract; the prediction path always renders a
label.

→ **RESOLVED (2026-06-15, deferred):** the production path **stays
always-label** with `unknown` as the only soft option. Abstention is **deferred**
until a coverage/over-abstention evaluation contract (from the two protocols)
actually exists — at which point the `outcome`/`allow_abstention` surface, its
flag, and its tests are added together as one ablatable component. The decision
surface lives in this prose, **not** as a default-`False` dead branch in
`resolve.py` (the attribution audits flag never-exercised branches). The spec's
gated-abstain hook is removed accordingly.

## Predeclared code changes (ride the validation ladder)

Two resolutions above imply label-changing code edits. Neither is patched
silently; both are predeclared here and must ride the 25→50→250 ladder in
[[gan2026_kg_grounded_component_generation_design_2026-06-15]] §5 with
correct→wrong accounting:

1. **C1 fix** — `resolve.py::_surviving_contradiction` must stop returning
   `unknown` on a current-rate-vs-current-seizure-free edge: keep the rate node,
   flag the seizure-free node `contradicted_by_current_rate`, fall through to
   ranking. `unknown` survives only for non-rate-attributable conflicts.
2. **C4 guard** — add an `ontology.py`/builder guard so a vague *count of
   clusters* is not rescued into a frequency node by a cadence denominator
   (the `QUANTIFIED` short-circuit). Honors the v6 null-route; leaves cluster
   *size* refinement intact.

**`resolve_label` scope note:** the spec's "replaces the flat projection"
framing is retired. As shipped, `resolve.py` owns **admission + typed-edge
resolution** and **delegates intra-kind ranking** to `project_graph_to_gan`
(deliberate, for byte-equal-to-baseline attribution). The intra-kind priority
integers in §5/§8 therefore remain the canonical ranking statement, *cited by*
`resolve_label`, not superseded by it. Absorbing the ranking ladder into
`resolve_label` is a tracked follow-up, gated on Stage A/B proving the new
mechanisms carry their weight.

## How to use this register

When the KG line absorbs a rule, cite the `§x.y` id here so there is one
canonical statement. Contradictions C1–C5 are now resolved (C1/C2 by edge
resolution and the ADRs above; C3 documentation-only; C4 by the predeclared
graph-builder guard; C5 deferred). `gan2026_resolve_label_spec.md` carries the
algorithm; this register carries the canonical rule statements and their homes.
