# Documentation Map

The docs tree is organized by the job a document does, not by the order it was
written.

**Start here:** [`NAVIGATION.md`](NAVIGATION.md) — tiered routing to the control
plane, design docs, paper material, and long tail.

**Active work:** [`plans/ACTIVE_ROADMAP.md`](plans/ACTIVE_ROADMAP.md).  
**Reading by thread:** [`THREAD_MAP.md`](THREAD_MAP.md).  
**Canon summaries (Wave 2):** [`research/PAPER_CANON.md`](research/PAPER_CANON.md), [`research/exectv2_evaluation_canon.md`](research/exectv2_evaluation_canon.md), [`research/gan2026/GAN2026_RESEARCH_CANON.md`](research/gan2026/GAN2026_RESEARCH_CANON.md), [`experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md`](experiments/exectv2/CLOSEOUT_EVIDENCE_CANON.md), [`research/exectv2_gepa_canon.md`](research/exectv2_gepa_canon.md).  
**Lifecycle rules:** [`runbooks/documentation_lifecycle.md`](runbooks/documentation_lifecycle.md).

## Stable Design

- `design/`: Durable architecture notes, data contracts, evaluation protocols,
  model strategy, and reusable design constraints.
- `decisions/`: Architecture decision records. Use this for choices that should
  stay discoverable after the implementation details move on.
- `plans/`: Forward implementation plans and milestone breakdowns.
- `runbooks/`: Repeatable operational procedures.

## Research And Experiments

- `research/`: Thesis, synthesis, paper-facing interpretation, major error
  analysis, and durable data/gold-scoring notes. A research doc should answer
  "what did we learn?" or "what claim does this support?"
- `research/error_analysis/`: Row-level case files and adjudication substrates
  for error-analysis workstreams (for example evidence-recall consolidation).
- `research/maintenance/`: Rolling archives such as monthly PROJECT_STATUS
  digests.
- `experiments/`: Human-readable lab-notebook material for individual runs,
  predeclarations, pilot iterations, readouts, and short experiment reports. An
  experiment doc should answer "what did this run do?"
- `literature/`: External papers and literature-review artifacts.

The repository-level `experiments/` directory remains the home for runnable
scripts, JSON/JSONL outputs, generated scorecards, and raw run artifacts. The
`docs/experiments/` directory is for curated narrative records that humans read.

New narrative markdown belongs in `docs/experiments/` unless it is a
registry-linked scorecard or error ledger that must co-locate with JSON/JSONL
under `experiments/`. See the two-tree rule in `NAVIGATION.md`.
