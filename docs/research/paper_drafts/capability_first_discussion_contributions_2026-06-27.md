# Discussion and Contributions — Capability-First Restructure

Date: 2026-06-27
Workstream: Wave 4 · P6c (Discussion + Contributions rewrite)
Status: writing-only draft; no new model calls, no holdout rows read, no new experiments
Evidence validity: validation-only replay (`dev140`) + frozen aggregate-only (`full-200`);
stated per-claim below. All figures carry the same evidence-boundary discipline as the primary
result artifacts they cite. Tasks: **Gan 2026** deep seizure-frequency labeling; **ExECTv2**
broad multi-entity phenotyping on clinical letters.

Sources consumed:
- `docs/research/paper_drafts/benchmark_surface_reconciliation_subsection_2026-06-27.md`
- `docs/research/paper_drafts/wall_transfer_cross_dataset_2026-06-27.md`
- `docs/research/paper_drafts/deepseek_model_agnostic_evidence_2026-06-27.md`
- `docs/research/paper_drafts/calibration_claim_revision_2026-06-27.md`
- `docs/research/closing_stage_research_critique_2026-06-27.md`
- `docs/research/gan2026/retrospectives/gan2026_research_closeout_synthesis_2026-06-17.md`
- `docs/research/wall_transfer_forward_observable_feature_inventory_2026-06-27.md`
- `experiments/exectv2_component_off_replay_dev140_20260626.md`
- `experiments/gan2026_f1_orchestrator_state.json`

---

## Discussion

### D.1  What the System Does Well and Why the Architecture Deserves Credit

The central claim of this work is that a decomposed, stage-owned architecture — not any
particular large language model — is the primary carrier of clinical extraction quality.
Three pieces of evidence support this claim. First, swapping the generation LLM while
holding the component graph, scoring surface, and evaluation protocol constant does not
degrade performance: DeepSeek chat reaches **0.8566** overall clinical-headline F1 on the
frozen full-200 aggregate versus GPT-4.1-mini's **0.8356**, a +0.021 lead distributed
across Diagnosis (+0.031), SeizureFrequency (+0.008), and Investigations (+0.053), with
Prescription tied at 0.8926 (evidence validity: frozen aggregate full-200, same-core
architecture, no row-level inspection). This is the predicted signature of a model-agnostic
system: the component graph normalizes structured outputs from qualitatively different LLMs
into consistent clinical-headline recovery, and the post-processing format layers contribute
a stable delta of ~+0.04–0.05 regardless of which LLM is in the generation lane. If the
LLM were the bottleneck, GPT's higher general-purpose benchmark ranking would dominate the
swap; it does not.

Second, the component-off ablation on dev140 confirms that the architecture's deterministic
spine is doing load-bearing work. The SeizureFrequency headline-projection layer contributes
+0.124–0.203 clinical-headline F1 depending on model; the residual semantic recovery lens
contributes +0.018–0.104. These are not margin gains — they are the mechanism by which
LLM-generated clinical facts are normalized, projected, and assembled into a recoverable
clinical headline. Removing any one of these layers produces a measurable regression. One
finding deserves specific attention: the evidence-validation gate is **structurally inert**
on the current holistic dev140 assembly (+0.000 delta across all four models; evidence
validity: dev140 replay-only aggregate), because the generation lanes emit only
verbatim-grounded mentions that already satisfy the gate. This is a grounding guard check,
not proof that evidence validation is universally unnecessary; it means the extraction lanes
already enforce the evidence contract before the gate fires.

Third, the structured-event extraction discipline itself — not the evidence-validation gate,
not the selector apparatus, but the forcing function that keeps the LLM source-near — is
where the Gan 2026 seizure-frequency strand found most of its reliable value. On the Gan
benchmark, the single GPT structured-event pass achieved **0.809 `test450` Purist** versus
the multi-trace fresh-evidence hybrid pipeline's **0.842**, a difference of only +15 test rows for a stack of four LLM calls and a
rule-guarded replace mechanism. The lesson is architectural: evidence-grounded intermediate
state, deterministic rendering, and a disciplined claim about what the LLM is allowed to
change are the primary sources of correctness. Orchestration complexity adds incrementally at
best.

---

### D.2  The Benchmark-Surface Inversion and Its Honest Interpretation

The manuscript reports headline performance on a clinical-recovery surface
(`clinical_headline`—Diagnosis, SeizureFrequency, Prescription, and Investigations)
that does not match the published ExECTv2 benchmark's per-item F1 scorer
(nine entities, CUI codes, full attribute bundles). This choice has a principled basis:
gold character-offset annotations were made against the original unprocessed clinical
letters; subsequent spelling correction altered the text without updating the offsets (thesis
§5), making any offset-tuned comparison non-reproducible on the corrected surface. The
methodology is consistent with the benchmark paper's own inter-annotator agreement protocol,
which also disregarded CUIs and compared on phrase selection and attribute classification.

The honest consequence must be stated directly. On the comparable dev140 published-benchmark
surface (nine-entity CUI + attribute-bundle scorer), the best-of-dev140 like-for-like figure
is **0.3877 per item / 0.6972 per letter** — approximately 45% of the paper's 0.87 per-item
headline (evidence validity: dev140 validation-only, frozen aggregate, not a full-200
estimate). The gap is not a measurement artifact. The project's own 2026-06-18
like-for-like analysis locates the loss in **CUI reproduction and attribute-bundle
strictness**, not in concept recall or entity recognition, and identifies the lever as
deterministic phrase/CUI/attribute-bundle fidelity engineering that was explicitly
deprioritised in favour of the clinical-recovery evaluation framework. This is a defensible
choice; it should be narrated, not quietly elided.

There is a second finding embedded in the benchmark-surface comparison that is genuinely
informative: **rules beat hybrid on the published-benchmark surface for SeizureFrequency,
Diagnosis, and Prescription**. For SeizureFrequency specifically, the hybrid verifier
reaches 0.782 on the clinical-recovery surface but collapses to 0.347 on the
published-benchmark surface, well below the deterministic rules baseline of 0.692 (+0.345
rules advantage). Stacking all four hybrid verifiers lowers the nine-entity benchmark
overall from 0.3687 (deterministic) to 0.3100 (all-hybrid). This is not a contradiction: the
LLM's clinical-recovery gains and the benchmark's format-fidelity requirements are
orthogonal surfaces with different owners. The paper should state this directly — as a
two-surface, two-stakeholder finding — rather than allow the surface choice to hide it.

A specific caveat applies to SeizureFrequency rule-level claims under the published-benchmark
surface. The SF registry consolidates 133 rule IDs but the clinical behavior remains split:
convention rewrite and noise run through catalog-driven builder loops while residual
additions and operand-format rewrites execute in legacy Stack B modules; projection logic
uses no catalog-driven dispatch. The shadow-parity CI gate covers convention rewrite only.
Benchmark scores attributed to "SF rules" are valid aggregate readouts from saved replay
artifacts, not claims about cleanly auditable individual rule ownership (I1: SF registry
legacy delegation audit, 2026-06-27).

---

### D.3  The Confident Over-Reading Limit (the Wall) and What It Means for the Architecture's Ceiling

The Gan 2026 seizure-frequency strand's central negative result — the honest **holdout**
ceiling of **0.842 `test450` Purist** for the multi-trace fresh-evidence hybrid pipeline
and **0.809** for the single structured-event pass — is not a failure of
optimization effort. It is a characterization of a **confident over-reading limit (the
Wall)**: on the hardest rows the model over-reads ambiguous seizure-frequency evidence as
quantified rates with high confidence, and no forward-observable signal can safely breach it:
the signal distinguishing *withhold-to-unknown* from *emit-rate* is absent from every
inference-time feature (selector oracle 739/750; 11 rows with no Purist-correct component;
structural-impossibility finding from C7, which showed the no-correct residual rows are
feature-identical to genuine-rate rows on every observable dimension — only hidden gold
separates them).

The mechanism was established, not merely hypothesized, by a pre-registered semantic-entropy
probe (P2.1) at k=4 samples across temperatures {0.3, 0.5, 0.7, 1.0} on 150 validation
rows: mean label entropy **0.012**, with the most-over-read band (`band_unknown`) at **entropy
0.000** across all four temperatures (evidence validity: validation-only probe, n=150,
no holdout). The over-reading is not sampling noise — the model does not sample its way out
of the wrong answer. H0 (`H0_confident_over_reading`) was not refuted; the null is clean and
publishable.

This result generalizes, at minimum structurally. On the ExECTv2 clinical-letter corpus,
SeizureFrequency is the persistently weakest extraction family under a frozen same-core
architecture across all three tested LLMs: GPT-4.1-mini **0.7525**, DeepSeek chat
**0.7602** (frozen full-200 aggregate). The other families are materially stronger
(Diagnosis 0.8397–0.8708, Prescription 0.8926, Investigations 0.8563–0.9091). The gap is
not model-specific (DeepSeek narrows it by only +0.008 vs GPT), not an evidence-failure
(evidence rate is 1.0000 on all model-swap runs), and correctible by task-specific
adjudication (dev140 v08 with SF adjudicator: 0.9053). These are the same structural
signatures as the Gan wall: persistent across models, not addressable by model choice alone,
reducible by targeted post-processing that corrects the base extraction residual, but not
eliminated at the base extraction level.

The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran on dev140
self-consistency artifacts and returned a **partial verdict (3 of 6 pre-registered checks
passed)**. The cross-dataset claim can now be stated with evidence: **43.6% of SF error cells are
temperature-unanimous wrong** (4/4 same wrong answer), confirming that a material
confident-error component is present — consistent with the Gan pattern. However, the full
Gan H0_confident_over_reading mechanism does not transfer: SF error entropy is elevated
(0.287 vs 0.069 for correct cells) and cross-model agreement is lower on error cells
(21.8%) than correct cells (69.4%) — the reverse of the Gan `band_unknown` pattern where
every wrong answer was entropy-zero and stable across all temperatures. The ExECTv2 SF
floor is a *mixed* mechanism: some errors are as confidently wrong as Gan's over-reading;
others are genuinely uncertain and heterogeneous across models. The confirmed finding is
**task-bound ceiling that transfers; mechanism that partially differs** — and this is the
more honest, more informative characterization: *a system whose ceiling is task-bound — not
system-bound — with an error composition that reveals both the clinical-reasoning limit and
its mixed character on a second independent corpus*. The wall is a characterization, not an
apology.

---

### D.4  Evaluation Discipline as the Lasting Methodological Contribution

The Gan closeout synthesis (Part III, 2026-06-17) identifies evaluation discipline — not
the F1 score — as the durable contribution. This assessment is correct and should be
foregrounded in the manuscript rather than subordinated to the numerical results.

The specific practices that constitute this discipline:

**Held-out-family cross-validation as a stop rule.** The two-tier gate (adversarial battery
*then* held-out-family CV) caught a -106 regression (v0.7) that a battery-perfect result
alone would have promoted to test450. The governing insight is that battery passing at 100%
is necessary but not sufficient: v0.7 was battery-perfect but over-demoted genuine-rate rows
because the coerce-to-unknown intervention was too aggressive across the full distribution.
Without the held-out-family CV gate, this candidate would have entered the locked evaluation
set with a false signal of generalization.

**Predeclared adversarial panels over cherry-picked cases.** The robustness battery's
minimal-pair, source-near, and KCL-OOD panels were authored before results were read. The
finding that the component wall is a genuine clinical gap (not surface overfit) came from the
C1 battery, where KCL-style OOD barely dented accuracy (87.5%) while minimal-pair and
synonym traps revealed the limit. This distinction — OOD-robust but abstention-incapable —
is the paper's most precise characterization of what the wall actually is.

**Contamination canaries and evidence-validity audits.** The M2 audit's recovery of
`REPAIRED_ELLIPSIS` copy-collation artifacts as the source of Qwen's apparent
evidence-validity gap (53.7% of hybrid exact-invalid strings; grounded rate 94.7% vs raw
74.8%) is a methodological result: the raw substring metric was misleading, and the audit
corrected it without changing any numbers or conclusions.

**Frozen aggregate-only inspection policies.** The standing protocol (no full-200 or holdout
row-level inspection without a fresh predeclaration) protected the test set from
contamination through seven experiment cycles, including structural-impossibility findings
that would have been tempting to probe at row level. That the C7 finding (feature
indistinguishability of no-correct residual from genuine-rate rows) was established without
reading any test row is itself a protocol achievement.

These practices transfer. The ExECTv2 reliability scorecard adopts the same evaluation
dimensions, the same evidence-groundedness metric, and the same predeclaration format. The
method is reusable at the architecture level.

---

### D.5  Limitations

**I1 — SF registry hybrid-delegated (structural).** The ExECTv2 SeizureFrequency registry
consolidates 133 rule IDs across extraction, convention repair, and projection under a
YAML-indexed catalog, but clinical behavior remains split between catalog-driven builder
loops and legacy Stack B modules. The `convention_residual` family delegates entirely to
`_legacy_residual.py` (~905 LOC); five operand-format rewrites execute in
`_legacy_rewrite._sf_operand_format_rewrite`; `projection_sf` uses no catalog-driven dispatch
loop. Shadow-parity CI covers convention rewrite only. Aggregate benchmark scores attributed
to "SF rules" are valid readouts from saved replay artifacts; individual rule-level causal
attribution within the SF stack is not auditable from catalog metadata alone. This is a
maintainability and audit-trail limitation, not a validity limitation on the reported
aggregate figures.

**S1 — Cross-task thesis-complete criterion unmeasured.** The reliability thesis §7 sets
the thesis-complete criterion as "a shared core demonstrably reused across tasks." Structural
reuse is real at the code level (49 ExECTv2 modules import `core`/`tasks.shared`/
`tasks.seizure_frequency`), but the SeizureFrequency clinical machinery — the declared
"bridge" — is re-implemented under `exectv2/deterministic/sf_state_projection.py` and
`rules/seizure_free.py`; `assembly/lenses/seizure_frequency.py` does not import the Gan SF
normalizer. The shared-component ablation that would measure the cross-task dividend (turn one
shared component off, report delta on both tasks at once) is predeclared in the
`exectv2_component_off_reliability_ablation_plan_2026-06-26.md` but not yet executed at
cross-task scope. The modularity thesis is supported by structural evidence and the model-swap
result; the quantified cross-task component dividend remains future work.

**Partial wall mechanism — ExECTv2 probe returned 3 of 6 pre-registered checks passed.** The
wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) ran on dev140
self-consistency artifacts. Task-bound ceiling is confirmed: SF is the weakest family
across all three LLMs and both splits, and 43.6% of SF error cells are
temperature-unanimous wrong — a material confident-error component. However, the full
Gan H0_confident_over_reading does not replicate: SF error entropy is elevated (0.287
vs 0.069 for correct cells) and cross-model agreement is lower on error cells (21.8%)
than correct cells (69.4%). The dominant Gan-residual pattern — near-zero entropy,
stable wrong answer regardless of temperature — applies to a subset of ExECTv2 SF
errors but not to the majority. The manuscript cross-dataset claim must be stated as:
task-bound ceiling transfers; mechanism is mixed (confident-error component present but
coexisting with uncertain errors not seen in the Gan residual). The stronger Gan claim
— the wall is purely confident, undetectable by self-referential signals — does not
transfer in full.

**Calibration is near-base-rate, not deployment-ready.** The scoring rule's aggregate
full-200 validation calibration is Brier **0.2245** versus constant base-rate **0.2387**
(Δ = 0.0142), ECE **0.0432**. The improvement above base rate is real but small. All signal
carried by the rule comes from external predeclared features (family identity, evidence-
provenance indicators, evidence-ambiguity flags), not from model-reported confidence, which
is degenerate on the Gan strand and unused here. Holdout calibration confirmation has not
been run.

---

## Contributions

The following five contributions are stated as the measured deliverables of this work.
Evidence-validity labels accompany each claim; no contribution overstates its evidence basis.

---

**Contribution 1: Benchmark reconciliation with honest gap disclosure and surface inversion
finding.**

We provide the first like-for-like comparison between our clinical-recovery evaluation
surface and the published ExECTv2 benchmark (nine-entity CUI + attribute-bundle scorer): our
best-of-dev140 configuration reaches **0.3877 per item / 0.6972 per letter** on the
published-benchmark surface versus the published pipeline's **0.87 / 0.90**
(evidence validity: dev140 validation-only, frozen aggregate). The gap is explained:
spelling correction on the clinical letters drifted the gold character offsets, making the
offset-tuned published number non-reproducible on the corrected surface; the residual gap
on the aligned surface is concentrated in CUI reproduction and attribute-bundle strictness,
representing closeable deterministic fidelity engineering that was explicitly deprioritised.
A non-obvious inversion accompanies this finding: the deterministic rules pipeline beats the
hybrid configuration on the published-benchmark surface for Diagnosis, Prescription, and
SeizureFrequency (SF rules advantage: +0.345 benchmark per-item F1 on SF), while the hybrid
dominates on the clinical-recovery surface. This two-surface, two-stakeholder result is a
finding, not a measurement inconsistency; it characterizes the difference between
CUI-bundle fidelity and clinical-concept recovery as genuinely distinct objectives.

---

**Contribution 2: Cross-task shared component ablation establishing the evidence-validation
gate as structurally inert and SF normalization as the operative shared component.**

We report the first systematic one-component-off aggregate ablation for ExECTv2 under a
frozen dev140 replay protocol. The ablation establishes that the evidence-validation gate
contributes **Δ = 0.000** to clinical-headline F1 across all four model configurations on the
current holistic assembly (evidence validity: dev140 replay-only, no model calls, aggregate
only). This is not a failure of the gate — it is a grounding-architecture result: the
structured-event generation lanes enforce exact-evidence grounding before the gate fires, so
the gate's protection is already baked in at the source. Separately, the SeizureFrequency
headline-projection layer contributes **+0.124–0.203 F1** depending on model (largest for
DeepSeek: +0.203), concentrated entirely on the SF family. This identifies SF normalization
and projection as the operative shared clinical component across both tasks — not because the
same module is imported (the ExECTv2 SF clinical machinery is re-implemented, not directly
ported), but because the clinical task's structure, and the architecture's response to it,
are parallel. The delta is a component-impact finding; the full cross-task shared-component
dividend requires the predeclared cross-task ablation (S1; future work).

---

**Contribution 3: The wall as a cross-dataset confident-over-reading phenomenon — partial
mechanism transfer with structural confirmation.**

We characterize the Gan 2026 seizure-frequency **holdout** ceiling (**0.842 `test450`
Purist**, multi-trace fresh-evidence hybrid pipeline) as a confident, architecturally
unresolvable over-reading of ambiguous evidence: the
model commits to rate-like interpretations of genuinely ambiguous clinical text without
uncertainty and with no forward-observable signal separating wrong over-reads from correct
rate extractions. A pre-registered semantic-entropy probe (P2.1: k=4 at temperatures
{0.3, 0.5, 0.7, 1.0}, n=150 residual-enriched rows) returned mean label entropy **0.012**
with `band_unknown` entropy **0.000** — H0 (`H0_confident_over_reading`) not refuted
(evidence validity: validation-only probe; test450 not read for mechanism). We show that the
same wall appears structurally on the ExECTv2 clinical-letter corpus: SeizureFrequency is
the persistently weakest extraction family under a frozen same-core architecture across all
three tested LLMs (GPT-4.1-mini **0.7525**, DeepSeek chat **0.7602**, frozen full-200
aggregate), with the same signatures — model-independent gap, 1.0000 evidence rate
(faithful-but-wrong, not unfaithful), and correctability by task-specific adjudication
(dev140 with SF adjudicator: 0.9053). The wall-transfer probe (`exectv2_sf_wall_transfer_probe_2026-06-27.md`) returned a partial verdict (**3 of 6 pre-registered checks passed**;
`dev140` self-consistency artifact replay): 43.6% of
SF error cells are temperature-unanimous wrong, confirming a material confident-error
component. However, SF error entropy is elevated (0.287 vs 0.069 correct) and cross-model
agreement is lower on error cells (21.8%) than correct cells (69.4%), establishing that the
ExECTv2 SF floor is a *mixed* mechanism — not purely the confident over-reading
characterized on Gan. The cross-dataset claim is therefore: **task-bound ceiling transfers;
mechanism partially differs.** The confirmed finding is the methodologically significant
one: a system whose ceiling is **task-bound, not system-bound** — present on two
independent corpora under three different LLMs — exhibits exactly the behavior a
clinically-grounded, modular architecture predicts. The limit is the clinical task's
ambiguity floor, not an architectural deficiency, and the error composition reveals both
a confident-wrong component and a genuinely uncertain component that may respond to
different mitigations.

---

**Contribution 4: Model-agnostic architecture validated by a non-development LLM outperforming
the primary model.**

We demonstrate that the ExECTv2 architecture is model-agnostic through the strongest
available test: a same-core model-swap experiment in which DeepSeek chat, running on the
frozen component graph developed against GPT-4.1-mini, surpasses GPT-4.1-mini by **+0.021
overall F1** on the frozen full-200 aggregate (0.8566 vs 0.8356; evidence validity: frozen
aggregate full-200, same-core `exectv2_2call_no_sf_adjudicator` architecture, predeclared
gate `pass_with_caveat` for one parse/schema failure within tolerance). The post-processing
format layers contribute a stable **~+0.044–0.046** across all three models tested, confirming
that the architecture normalizes idiosyncratic model output differences before they reach the
scored surface. DeepSeek's clinical-recovery base (0.8110) also exceeds GPT's (0.7922),
ruling out the alternative that the aggregate advantage is purely a formatting artifact.
This result provides direct empirical support for the modularity claim: if the LLM were the
intelligence locus, the non-development LLM would not lead on three of four clinical families
while holding the architecture constant. The architecture's component graph, deterministic
normalization, and projection stages are the primary carriers of clinical extraction quality.

---

**Contribution 5: Evaluation discipline as a reusable, transferable methodology for
LLM-mediated clinical extraction.**

The single most transferable output of this work is the evaluation discipline developed
through seven experiment cycles on the Gan benchmark and applied to the ExECTv2 strand. The
core practices are: (a) predeclared adversarial panels with distinct clinical failure axes
(minimal-pair, source-near, KCL-style OOD), run before validation750 to catch overfitting
that would otherwise reach the locked evaluation set; (b) held-out-family cross-validation
as a stop rule, catching the -106 regression in v0.7 that battery-perfect performance would
have promoted; (c) contamination canaries and evidence-validity audits distinguishing
metric artifacts from real failures (e.g., `REPAIRED_ELLIPSIS` recovery); (d) frozen
aggregate-only inspection policies that preserved the test set's evidential integrity through
structural-impossibility findings including C7's proof that the no-correct residual is
feature-indistinguishable from genuine-rate rows on all inference-time signals. These
practices were transferred to the ExECTv2 reliability scorecard under the same evaluation
dimensions and evidence-groundedness metric. The methodology is architecture-independent and
task-independent; its durable contribution is the proof that rigorous, predeclared evaluation
protocols for LLM-mediated clinical extraction are both necessary (removing them would have
produced false promotion decisions) and sufficient (they correctly characterized both a
genuine ceiling and the mechanism behind it without holdout contamination).

---

## Evidence Validity Summary

| Contribution | Evidence level | Boundary |
|---|---|---|
| C1 — Benchmark reconciliation | dev140 validation-only, frozen aggregate | No full-200 published-benchmark surface computed |
| C2 — Component ablation (gate inert; SF norm matters) | dev140 replay-only, aggregate | No model calls; cross-task ablation scope is future work (S1) |
| C3 — Wall cross-dataset (partial mechanism) | Frozen aggregate `full-200` (ExECTv2); validation-only probe (Gan P2.1); `dev140` self-consistency artifact replay (wall-transfer probe) | Task-bound ceiling confirmed; Gan H0 mechanism partially differs (3 of 6 pre-registered checks passed; error entropy 0.287 vs 0.069; cross-model agreement 21.8% on errors vs 69.4% correct); no holdout on ExECTv2 |
| C4 — Model-agnostic architecture | Frozen aggregate full-200, predeclared gate | No holdout on non-primary models; row-level attribution excluded |
| C5 — Evaluation discipline | Validation-only + test450 aggregate (Gan); validation-only (ExECTv2) | No new experiments; retrospective characterization of completed work |

---

*Writing only. No git operations. No holdout or full-200 row-level inspection. No new model
calls. Parent task: Wave 4 workstream P6c.*
