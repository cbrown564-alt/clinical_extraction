# Documentation Map

The docs tree is organized by the job a document does, not by the order it was
written.

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
- `experiments/`: Human-readable lab-notebook material for individual runs,
  predeclarations, pilot iterations, readouts, and short experiment reports. An
  experiment doc should answer "what did this run do?"
- `literature/`: External papers and literature-review artifacts.

The repository-level `experiments/` directory remains the home for runnable
scripts, JSON/JSONL outputs, generated scorecards, and raw run artifacts. The
`docs/experiments/` directory is for curated narrative records that humans read.

