# Reliability Thesis

Status: durable design doc. This is the project-level statement of what the
paper argues and why the codebase is shaped the way it is. It sits above the
task-specific framing in `docs/research/contribution_thesis.md` (which is
Gan-2026/seizure-frequency-centric) and the package shape in
`docs/design/architecture.md`. When those documents and this one disagree about
scope, this one defines the destination and they define the current task.

## 1. The Claim

Clinicians need clinical-extraction AI they can trust. Trust is not a property
of a single benchmark score; it is a property of a system whose behavior is
**reliable** (it generalizes beyond the surface it was tuned on, and it knows
when it is wrong) and **transparent** (every prediction carries an inspectable
trail, and every component can be ablated and error-analyzed).

The paper's central claim is that a **modular, auditable clinical-extraction
architecture** delivers both, and that we can demonstrate this — not assert it —
by holding the architecture fixed while varying two things that usually confound
reliability claims in this literature:

1. **The task and dataset.** We apply the same architecture to two distinct
   tasks in the epilepsy-letter domain:
   - **Deep single-concept extraction** — seizure frequency from Gan 2026
     letters. The hardest single epilepsy indicator: it requires clinical
     reasoning (which fact is the patient's current burden), temporal reasoning
     (current vs. historical, windows, since-dates), and concept normalization
     (count/range × period → a comparable rate).
   - **Broad multi-concept phenotyping** — the full ExECTv2 entity set
     (Fonferko-Shadrach 2024): nine entity types with attributes and UMLS CUIs,
     scored per-item and per-letter.
2. **The architecture family.** For each task we build three canonical
   architectures over the same shared core: **rules-based**, **LLM-only**, and
   **hybrid**. Holding the task fixed and varying the family isolates what the
   LLM adds; holding the family fixed and varying the task isolates what
   generalizes.

A system that beats the published benchmark on *both* tasks, with *all three*
architecture families, using *one* modular codebase, is the concrete artifact
that makes the reliability claim credible.

## 2. Why These Two Datasets

The two datasets are deliberately complementary, and the relationship between
them is the spine of the reliability argument.

| | Gan 2026 (task 1) | ExECTv2 (task 2) |
| --- | --- | --- |
| Scope | one concept, deep | nine concepts, broad |
| Unit of prediction | one normalized label per letter | many entity mentions per letter, with attributes + CUI |
| Scoring | label accuracy (purist/pragmatic) | per-item and per-letter F1 |
| Hard part | clinical + temporal reasoning, normalization | breadth, attribute structure, recall across templates |
| Published bar | — | overall F1 **0.87 per item / 0.90 per letter** (rule-based GATE pipeline); human IAA 0.73 |

Crucially, **Seizure Frequency is the bridge between the two tasks**. It is the
deep target of task 1, and it is simultaneously ExECTv2's *weakest* entity
(0.66 per item, 0.47 human IAA) — precisely because it resists rule-based
extraction for the same reasons that made it task 1's central challenge. This is
why ExECTv2 work begins with Seizure Frequency: it is the most direct test of
whether the capability built for task 1 transfers to a new dataset, a new
annotation schema, and a new scoring regime. If the modular investment is real,
it shows up first and most clearly here.

The ExECTv2 annotation schema independently corroborates that the task-1
normalization model was the right abstraction: its SeizureFrequency attributes
encode count, ranges (`Lower/UpperNumberOfSeizures`), rate denominators
(`TimePeriod`, `NumberOfTimePeriods`), temporal anchors
(`PointInTime`/`Month`/`Year`/`DayDate`, `TimeSince_or_TimeOfEvent`), and
`FrequencyChange` — the same count/range × period × temporal-anchor structure
the Gan 2026 normalizer already produces. And `NumberOfSeizures = 0` (92 of 263
mentions) is a seizure-free assertion: the lowest-accuracy answer kind from task
1, reusable here.

## 3. The Two Pillars Of The Claim

### 3.1 Reliability

Reliability has three observable, reportable components:

- **Generalization, demonstrated by transfer.** The same architecture and the
  same shared core clear the bar on two tasks. Within task 1 we already separate
  *generalizable* from *validation-tuned* behavior (the Phase 2 de-overfitting
  work, which deliberately accepted a validation-score regression to remove
  GAN-dataset-specific notation that would not transfer). Task 2 is the external
  check on that discipline.
- **Robustness through automated gates.** Every prediction passes through two
  deterministic gates that other papers in this space do not run:
  **schema validation** (the structured output conforms to the task's data
  contract) and **evidence verification** (the cited evidence is an exact source
  substring). These convert "the model said so" into "the model said so, the
  output is well-formed, and the support is present in the note." Schema-validity
  rate, repair rate, and evidence-validity rate are first-class reported metrics,
  not implementation details.
- **Calibrated uncertainty.** The system expresses uncertainty in a way that is
  grounded, closed-vocabulary, and cross-model comparable (the Phase 3
  uncertainty-signal harmonization), so that "I am not sure" is a usable signal
  rather than noise.

### 3.2 Transparency

Transparency is what lets a clinician (or reviewer) audit a decision instead of
trusting it blind. It operates at two levels:

- **Per-prediction:** extracted events, evidence spans, assertion/negation,
  temporality, normalized values, and a final rationale — stored, not discarded.
- **Per-corpus:** rigorous error analysis, clinically-meaningful failure-mode
  taxonomies, and ablations that show which component (and which rule category)
  helps or hurts. Because the architecture is modular and every component is
  named, stage-owned, and ablatable, the error analysis can attribute each
  failure to a component rather than to "the model."

This directly attacks the black-box problem: the rules-based architecture is
inspectable by construction, the LLM-only architecture is bounded by the schema
and evidence gates, and the hybrid architecture makes explicit which component
extracts candidates, which selects the clinical fact, and which only normalizes
or formats.

## 4. Why Three Architectures Per Task

The three families are not redundant; each answers a different question, and the
*comparison* is the contribution (see
`docs/research/gan2026_three_way_architecture_comparison_and_cross_pollination_plan_2026-06-07.md`
for the task-1 instantiation):

- **Rules-based** is the portability and reproducibility baseline, and the
  honest measure of what is achievable with no model at all. It is also the
  reference the published ExECTv2 benchmark itself is (a rule-based GATE
  pipeline), so beating it with rules is a like-for-like win.
- **LLM-only** is the upper bound on what unaided model reasoning contributes,
  bounded only by the schema and evidence gates.
- **Hybrid** tests the thesis that representation/normalization is best owned by
  deterministic stages while clinical judgment is best owned by the model — the
  separation of concerns that task 1 proved out.

Running all three on both tasks lets us state, with evidence, *what the LLM
adds*, *what generalizes*, and *what only fit the local benchmark* — the three
questions reliability claims usually leave unanswered.

## 5. What This Demands Of The Codebase

The thesis is only credible if it is delivered by *one* modular architecture,
not three copies of a pipeline. Task 1 was built by rapid experimentation, which
created real capability but also code duplication. Task 2 is where we collect the
modular dividend the original design promised.

Operating rules for ExECTv2 work:

- **Build on `core`; extend `core` rather than copy.** Task-neutral primitives
  (pipeline protocols, result containers, evidence/validation types, and now
  generic precision/recall/F1 scoring arithmetic) live in `core`. When task-1
  code would otherwise be duplicated, the reusable part is lifted into `core` (or
  a shared epilepsy layer); the task-specific part stays under `tasks/`.
- **Reuse the proven machinery.** The artifact/registry/report tooling, the
  three-way comparison report shape, and the run-registry validation are reuse
  candidates, not things to reinvent per task.
- **Keep the rule taxonomy.** `general` / `clinical_epilepsy` /
  task-specific / dataset-specific / `benchmark_format` (see
  `architecture.md`). The de-overfitting discipline from task 1 is the same
  standard task 2 rules are held to.
- **Score on labels, not gold offsets.** ExECTv2's gold character spans drift
  against the corrected-spelling letters (spelling was fixed after annotation
  without updating offsets), so matching is done on entity + normalized phrase +
  attributes, never on raw spans. This mirrors the benchmark paper's own
  methodology (CUIs disregarded in inter-annotator agreement; comparison on
  phrase selection/classification and attributes).

## 6. Paper-Relevant Outputs (Both Tasks)

The implementation should produce artifacts that become paper tables and
figures, for each task and each architecture family:

- per-item and per-letter F1 against the published benchmark (ExECTv2);
  purist/pragmatic label accuracy (Gan 2026)
- three-way architecture comparison (rules / LLM-only / hybrid)
- component and rule-category ablation tables
- error taxonomy with counts and examples, attributed to components
- evidence-validity rate, schema-validity rate, repair rate
- uncertainty calibration summary
- worked examples of successful and failed clinical/temporal reasoning

## 7. Success Criteria

- **Minimum:** beat the ExECTv2 per-item/per-letter F1 benchmark with at least
  one architecture, using the shared modular core, with the schema and evidence
  gates active.
- **Target:** beat it with all three canonical architectures, with a clean
  three-way comparison and component/rule ablations.
- **Thesis-complete:** the above on both tasks, with a shared core demonstrably
  reused across them, plus the transparency artifacts (per-prediction trails,
  corpus error analysis, calibrated uncertainty) that distinguish this work from
  the black-box norm in clinical extraction.
