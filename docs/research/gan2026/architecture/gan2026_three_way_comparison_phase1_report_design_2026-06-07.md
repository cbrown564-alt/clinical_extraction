# Gan 2026 Three-Way Comparison — Phase 1 Report Design

Date: 2026-06-07

Author: Claude

Status: design note for
[[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
Phase 1 (Section 3, "Comparison Protocol"). Scopes the report's data sources
and shape *before* spending API budget on the validation750 run. No
benchmark-comparable claim or holdout-facing protocol is authorized by this
note.

---

## 1. Why this note exists

Phase 0 closed with all six `PipelineArchitecture` configs wired into one
`Gan2026PipelineRunner`. Section 3 of the comparison plan asks for one report
covering, across all six:

- rendered / null / routed counts
- Purist-correct / Pragmatic-correct on rendered rows
- routed-row taxonomy (which families route, and why)
- evidence-trace and source-id validity rates

Before running anything, I mapped each architecture's `run_split()` output
shape (the surface the report would read from) and found a real asymmetry
that the report design has to account for rather than paper over — see
Section 2.

## 2. Finding: only one of six architectures has a routing stage, and its
##    `run_split` surface doesn't expose it

`run_split()` for **deterministic**, **deterministic_canonical_pipeline**, and
all three **`llm_only_*`** configs is a single-shot, no-verification path.
Each directly returns, per row, `comparison.{purist_correct,pragmatic_correct}`,
an evidence-trace boolean (`evidence_valid` or, for
`llm_only_canonical_pipeline`, the deliberately-distinct
`evidence_text_contained`), and an implicit rendered-vs-null signal
(`final_label != "unknown"`). None of these five has a "routed" concept —
there is no verification stage to route through.

`hybrid`'s `run_split()` (→
`llm_candidate_set_clinical_assessment_probe.run_split`) is an
**assessment-stage probe**: it reports `clinical_assessment_rows`,
`assessment_kind_counts`, schema-validation diagnostics, and the like. It does
**not** compute purist/pragmatic correctness, rendered/null counts, or
routing — those only exist once assessment rows are pushed through
`build_unified_pipeline_artifact` (`runner.py:471-555`), which chains
`projection_render -> score -> verification_route -> verification_decision`
and is `hybrid`'s *only* path to a final rendered/null/routed disposition and
a `purist_correct`/`routed_rows`/`action_counts` summary
(`runner.py:534-546`).

So a literal "run six `run_split`s, tabulate the same six columns" approach
cannot work: five architectures would populate the table directly, and
`hybrid` would have nothing in the rendered/null/purist/routed columns at all
— not because it scored worse, but because its lightweight probe surface
never produces those numbers.

**Resolution (confirmed with the user 2026-06-07):** routing is real and
specific to `hybrid` — it is not a missing feature in the other five, it is
the architectural difference the comparison exists to surface. The report
should:

1. Compare all six on the axes that are universally meaningful — rendered/null
   counts, Purist/Pragmatic-correct, evidence-trace validity, final-label
   distribution — in **one shared table**.
2. Carry a **separate hybrid-only appendix** for route-family taxonomy and
   routed-row counts, since no other architecture has an analogous surface to
   compare it against.

This does not, by itself, resolve *how `hybrid` gets numbers into the shared
table* — see Section 3.

## 3. Resolution detail: where `hybrid`'s shared-table numbers come from

Because `hybrid`'s `run_split` probe has no rendered/null/purist/routed
numbers, and the shared table needs *some* comparable number for `hybrid` in
each of those columns, `hybrid`'s row in the shared table must be populated
from `build_unified_pipeline_artifact` — i.e. its assessment rows replayed
through the same deterministic `projection_render -> score ->
verification_route -> verification_decision` chain the existing deep-replay
tooling already uses (`runner.py:494-507`). That artifact's `summary` already
carries `rendered_label_rows`, `null_rendered_label_rows`, `purist_correct`,
and `routed_rows` (`runner.py:534-546`) in the same vocabulary the comparison
needs.

Concretely, this means:

- **The hybrid-only routing appendix is not a second run** — it draws on the
  *same* deep-replay artifact that supplies `hybrid`'s shared-table numbers.
  One assembly, two presentations (shared-table row + routing appendix).
- **`hybrid` is the only architecture whose shared-table numbers come from a
  different code path than its raw `run_split`.** The report must say this
  plainly (in the metadata/provenance block, not buried in a footnote) —
  it is itself a finding about the architectures' shapes, not an
  inconsistency to hide. Suggested phrasing: *"hybrid's rendered/null/
  purist/routed numbers are produced by replaying its assessment rows through
  the deterministic projection/render/score/route/decision chain
  (`build_unified_pipeline_artifact`); the other five architectures produce
  these numbers directly from their single-shot `run_split` output. This
  asymmetry is the architectural fact under comparison, not a methodology
  artifact."*
- Pragmatic-correct is **not** present in `score_summary`/`route_summary`
  today (only `purist_correct` is, per `runner.py:542`) — the report-building
  code will need to either compute it from `score_rows` (if the per-row
  records carry gold + predicted frequencies, as the deterministic/llm-only
  paths' `comparison` dicts do) or explicitly mark that cell "not computed by
  the deep-replay chain" rather than silently leaving it blank. Confirm which
  before wiring the table — do not guess a number into that cell.

## 4. Shared comparison table — proposed columns

One row per architecture (six rows total):

| Column | Source per architecture (5 single-shot configs) | Source for `hybrid` |
| --- | --- | --- |
| Examples | `len(rows)` / `summary["examples"]` | `summary["input_assessment_rows"]` (deep-replay) |
| Rendered | count where `final_label != "unknown"` (derive; not all summaries carry this directly — confirm per-config before relying on a summary key) | `summary["rendered_label_rows"]` |
| Null | count where `final_label == "unknown"` | `summary["null_rendered_label_rows"]` |
| Routed | — (`N/A`, no routing stage) | `summary["routed_rows"]` |
| Purist-correct (of rendered) | `summary["purist_correct"]` / `summary["purist_accuracy"]` | `summary["purist_correct"]` (deep-replay `score_summary`) |
| Pragmatic-correct (of rendered) | `summary["pragmatic_correct"]` / `summary["pragmatic_accuracy"]` | TBD — confirm availability (Section 3); mark explicitly if not computed |
| Evidence-trace validity | `summary["evidence_valid"]` / rate, **except** `llm_only_canonical_pipeline` which reports `evidence_text_contained`/`evidence_text_containment_rate` (deliberately distinct — see plan Section 2, lines 119-124; do not conflate the two metrics in one column without footnoting which is which) | formal `CandidateSet` source-id validity rate, if the deep-replay chain exposes it (confirm in `score`/`route` stage metadata) |
| Final-label distribution | `Counter` over `final_label` (some summaries already carry `final_labels`; deterministic/canonical do not — derive if needed) | `Counter` over `decision_rows` final dispositions |

Footnote requirements for this table (must appear adjacent to it, not in an
appendix):
- which evidence-trace metric is being shown in each cell (substring-presence
  `evidence_valid`/`evidence_text_contained` vs. formal source-id validity) —
  these are *not* the same metric and the plan deliberately keeps them
  distinct (Section 2)
- that `hybrid`'s row is sourced from the deep-replay artifact, not its raw
  `run_split`

## 5. Hybrid-only routing appendix

Drawing on the same `build_unified_pipeline_artifact` replay used for
`hybrid`'s shared-table row:

- routed-row count and rate (of rendered rows, per `route_summary`)
- route-family taxonomy table: family name, row count, brief description —
  reuse the family inventory already named in
  `clinical_assessment_verification_route.py:80-176` (`seizure_free_conflict`,
  `selected_evidence_missing_exact_trace`, `selected_source_id_invalid`,
  `seizure_free_proxy_evidence_overreach`, `medication_cadence_ambiguity`,
  `cyclic_window_without_event_count`,
  `unresolved_cluster_cadence_with_per_cluster_burden`,
  `cluster_axis_ambiguity`, etc.)
- `action_counts` from `verification_decision` (affirm/reject/route
  dispositions), per `runner.py:545`

This section should explicitly note: *"no other architecture in this
comparison has a routing stage; this appendix exists to characterize what
`hybrid` does with the rows it doesn't render directly, not to provide a
column the other five could also fill."*

## 6. Report shape and reuse

Mirror the conventions already established by `reports/base.py` and
`artifact_analysis/reset_stage_component_ablation_v6.py`:

- **Claim-boundary line** at the top (validation-only, no holdout-facing
  claim, no live-model-call claim until the run actually happens) — same
  pattern as `reset_stage_component_ablation_v6.CLAIM_BOUNDARY`
- **Provenance/metadata block** via `reports.base.llm_model_metadata_lines`
  for each LLM-backed config (model, temperature, max_tokens, mode, git
  commit, JSONL artifact path, etc.) — the deterministic/canonical configs
  get the existing `write_deterministic_report`-style block instead
- **Shared comparison table** (Section 4) as the report's centerpiece —
  pipe-delimited Markdown, right-aligned numeric columns, footnotes inline
  beneath
- **Hybrid-only routing appendix** (Section 5) as its own `##` section,
  clearly separated and labeled as architecture-specific
- A short **"what this report does not claim"** section, explicitly stating:
  validation750-only, no `test450` read, no benchmark-comparable claim,
  evidence-trace metrics are not uniform across architectures (name which is
  which) — same disclaiming discipline as every other Gan 2026 artifact

Implementation should live alongside the existing report modules
(`gan2026/reports/`) as a new module (suggested name:
`three_way_comparison_report.py` or similar — confirm against `CONTEXT.md`'s
naming conventions before committing to it), taking six pre-computed
`(rows, metadata)` pairs (one per architecture; `hybrid`'s metadata being the
deep-replay `PipelineOutputArtifact.metadata`) and emitting the Markdown via
`reports.base.write_markdown_report`.

## 7. Recommended sequencing for the actual run

Before committing to the full validation750 surface (750 rows x 6 configs,
several of which are LLM calls):

1. **Pilot on a small slice first** (e.g. `validation25`/`validation50`,
   matching the existing matched-validation-slice convention seen in
   `experiments/gan2026_*_matched_validation25_comparison_*.md`) — this
   exercises the full six-architecture + deep-replay assembly path, confirms
   the shared-table columns populate as designed (especially the open
   `pragmatic_correct`/source-id-validity questions in Section 3), and
   produces a cheap, fast first read of the report shape end to end.
2. Resolve the two open data-availability questions from Section 3
   (pragmatic-correct and source-id validity for the deep-replay `hybrid`
   path) against the pilot's actual artifact shapes — adjust the table design
   if the data isn't where this note assumed.
3. Only then run the full validation750 surface and produce the Phase 1
   comparison report Section 3 calls for.

## 8. Open questions carried forward

1. Does `score_summary`/`route_summary` (or the underlying `score_rows`)
   carry a pragmatic-correct equivalent for the deep-replay `hybrid` path, or
   does the report need to compute it from `score_rows` directly, or mark the
   cell as not computed? (Section 3)
2. Does the deep-replay chain expose a formal `CandidateSet` source-id
   validity rate at the `score`/`route` stage that the report can cite for
   `hybrid`, distinct from the substring-presence metrics the other five
   report? (Section 4)
3. Confirm the new report module's name and location against `CONTEXT.md`'s
   established naming conventions before writing it (Section 6) — this is
   exactly the kind of naming call the plan's working agreement asks to be
   run through `/grill-with-docs` before locking in.

---

## 8a. Addendum (2026-06-08): `hybrid`'s validation750 surface is itself
##     scoped to ~250 rows — the report must disclose this too

Running the actual validation750 surface surfaced a second `hybrid`-specific
asymmetry beyond the deep-replay one this note already designs around (Section
3): `hybrid`'s `run_split` (`llm_candidate_set_clinical_assessment_probe.run_split`)
sources its `CandidateSet` input from a static, precomputed 250-row file
(`DEFAULT_CANDIDATE_SET_JSONL_PATH`) rather than computing one live per row, so
500/750 validation750 rows come back `candidate_set_missing`. See the parent
plan's Section 3 status update (2026-06-08) and the new Section 8a follow-up
entry — [[gan2026_three_way_architecture_comparison_and_cross_pollination_plan]]
— for the full analysis and the decision to track "wire live candidate-set
generation into `hybrid`" as a separate, deferred task rather than a Phase 1
blocker.

**Consequence for this report's design**: when populating the shared table
(Section 4), `hybrid`'s `Examples` cell and every other `hybrid` cell derived
from `build_unified_pipeline_artifact` must be computed over (and explicitly
labeled as) its available ~250-row subset — *not* the full 750-row surface the
other five architectures' rows cover. This is a second, independent reason
(stacked on top of the deep-replay-vs-run_split asymmetry already designed for)
that `hybrid`'s row needs its own disclosure footnote; do not let the two blur
together — name both explicitly:

1. `hybrid`'s numbers come from the deep-replay artifact, not raw `run_split`
   (Section 3 of this note).
2. `hybrid`'s numbers — deep-replay or otherwise — currently cover only the
   ~250 rows its static candidate-set file has entries for, not the full
   750-row surface the comparison nominally runs over.

---

## 9. Relationship to the parent plan

This note resolves the *data-source and shape* design questions Phase 1
(Section 3) raised once Phase 0 was complete. It does not authorize or
perform any run — Section 7's pilot-then-full sequencing is a recommendation
for when the user is ready to spend the API budget Phase 1 requires.
