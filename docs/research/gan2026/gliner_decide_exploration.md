# GLiNER2.5-Decide on the one-call seizure-frequency task: exploration report

Date: 2026-09-25. Status: exploratory, in progress. This is **not** a locked study
condition. The [protocol](one_shot_paper_protocol.md) still owns the study. This
report reuses the locked prompts' task, the [annotation guide](seizure_frequency_annotation_guide.md),
the dev750 reference and the lenient finding scorer read-only, and changes none of them.

## Question

Can a 340M encoder, [fastino/GLiNER2.5-Decide](https://huggingface.co/fastino/GLiNER2.5-Decide),
do the `minimal` and `expanded` one-call task in one forward pass? If it cannot
zero-shot, is it worth fine-tuning before, or alongside, DiffusionGemma?

## Model and setup

GLiNER2.5-Decide is `fastino/gliner2-large-v1` (DeBERTa-v3-large encoder,
Apache-2.0) tuned for "operational decision" classification over labels supplied
at call time. It is loaded with `gliner2` 2.0.0 (`AutoExtractor`). The checkpoint
keeps the GLiNER2 span, entity and structure heads, so one `extract()` call can
return, in a single pass:

- a classification;
- entity spans with offsets and confidences;
- lists of span-anchored structures with choice fields.

That is the closest encoder analogue of one call.

Setup steps and memory limits are in the [local GPU runbook](../../runbooks/gliner_local_gpu.md).
The points that matter:

- gliner2 needs `transformers<5`, which forces `huggingface-hub<1`. It is
  therefore installed separately, not as a project extra.
- Letters are long for this encoder. dev750 has a median of 515 DeBERTa tokens
  and a maximum of 1,070; 385 of 750 letters exceed 512 tokens. Full-context and
  chunked (384-word windows, 64 overlap) inference are run as separate conditions.
- On the 16 GB M1, running inference and a training smoke test together (with a
  VM) exhausted memory and caused a kernel panic. Runs now go one job at a time,
  on an RTX 3070 laptop (8 GB, bf16).

## Can the exact schema be replicated?

No. GLiNER2 selects labels and copies spans; it cannot write text or do
arithmetic. The table shows each locked contract element and its adaptation.

| Locked element | GLiNER2 equivalent | Consequence |
| --- | --- | --- |
| `answer.label` in the Gan grammar ("2 to 3 per month", "seizure free for 14 months") | One 10-way classification over the native **Purist bands**, with plain-language names and band descriptions | Scores the primary endpoint directly, but skips the label grammar. The model cannot add month counts or convert time, so arithmetic cases are learned as pattern → band. Pragmatic is derived from the predicted Purist band (a strict coarsening; tested). |
| `answer.evidence` quotation | One evidence entity span (`dtype=str`) | Always verbatim by construction. The primary view requires a span unless the band is unknown. Unknown merges Gan "unknown" and no-reference, so evidence cannot be required there. |
| Ten worked cases, instructions, ChatAdapter envelope | None; there is no prompt | Minimal and expanded differ only in the heads added to the same pass. |
| `findings[]` with nested quantity/duration unions | One `seizure_frequency_finding` structure. Value fields are spans (`evidence`, `event`, `quantity`, `per`, `window`, `seizures_per_cluster`, `restriction`); attributes are choice fields (`kind`, `phase`, `scope`, `counted_unit`, `status`, `level`) | Values go through a **format-only** normaliser (number words, ranges, bounds, written units; never unit conversion). Unreadable spans become `verbatim`, which the lenient scorer treats as not comparable. Attributes the model omits take the guide's stated defaults, and every default is counted. |
| `answer.claim_indices` | Not produced | A diagnostic link is derived from evidence overlap; it is never scored. |
| Strict first-response validity | Projection validates every finding against the locked `$defs/finding` schema | Findings with no in-note evidence, no kind or no required level are dropped and counted, never repaired. |

The code is kept in separable steps, following the repository rule:

- raw GLiNER output is saved unchanged (`runs/seizure_frequency/gliner/<run>/raw.jsonl`);
- `gliner/project.py` projects the answer and findings;
- `gliner/normalize.py` (`gliner_span_format_v1`) normalises value spans;
- scoring reuses `one_call/analysis.py` and `one_call/findings_score.py` unchanged.

## Which annotations are used

| Target | Source | Where |
| --- | --- | --- |
| Answer band (primary) | Original Gan `seizure_frequency_number`, mapped to Purist/Pragmatic | train300, dev750 |
| Answer evidence | Original Gan reference quotations, where verbatim in the note (217/300 train, 550/750 dev; no-reference rows teach an empty span) | Training target; overlap reported as a diagnostic |
| Findings | Locked dev750 reference (1,219 core + 131 supporting), owner-reviewed | Lenient score; expanded training target by dev750 cross-validation only |

No new annotation was created. test450 is never read; the runner refuses it.

## Evaluation design: what we intend to find out

All runs record dataset, split, row policy, model, schema hash, threshold,
context mode, projection and normaliser versions, packages and device.

1. **Zero-shot answer.** Purist agreement on all 750 dev letters for minimal-full
   and minimal-chunked. Comparators: the majority band (196/750, 26.1%) and the
   locked DeepSeek results (minimal 659/750, expanded 644/750; paired,
   descriptive only, since the task contract differs).
2. **Context.** Agreement split by letter length (≤384 vs >384 words), full vs chunked.
3. **Grounding.** Evidence span rate, and overlap with a verbatim Gan quotation.
4. **Inventory.** Lenient precision, core recall and all-reference recall, with
   attribute agreement among matched pairs and the projection drop/default tallies.
5. **One-pass interference.** Expanded minus minimal Purist, paired over letters,
   using the same bootstrap as the paper. This mirrors the paper's question: does
   asking for the inventory cost the answer? In GLiNER every task adds prompt
   tokens to the same encoder input, so interference is possible.
6. **Learnability (after fine-tuning).** The same measures for a model trained on
   train300 and evaluated on dev750.

**Pre-declared rule for "promising":** proceed to full fine-tuning if zero-shot
minimal beats the majority band, *or* if a small train300 LoRA run reaches
Purist ≥ 60% on dev750 with evidence on ≥ 70% of eligible letters. Otherwise
report GLiNER as unsuitable for the answer and consider it only as a span/evidence
component.

## Initial findings

These results are partial and must not be quoted as dev750 results.

The first zero-shot minimal, full-context run (MPS) completed 115 of 750 letters
before the machine crash. Those letters are the lowest source indices, not a
random sample: their gold mix has no seizure-free letters and a 42.6% majority band.

| Measure (115 letters) | GLiNER zero-shot | DeepSeek minimal, same letters |
| --- | --- | --- |
| Purist band correct | 16 (13.9%; 95% CI 8.7–21.4%) | 110 (95.7%) |
| Purist, evidence required | 4 (3.5%) | — |
| Pragmatic band correct | 43 (37.4%) | — |
| Evidence span returned (threshold 0.5) | 16% of letters | — |
| Span overlaps a Gan quotation | 18/104 (17%) | — |
| Median latency (M1 GPU) | 3.4 s per letter | 6.3 s |

Early observations:

- Zero-shot, the classifier does not read frequency; it falls **below the
  majority band**. Predictions cluster on "unknown" (47) and "daily or more"
  (32), mostly for letters whose gold is "more than weekly". Label choice looks
  driven by lexical cues, with no counting or window reasoning.
- Evidence spans are rarely confident enough to pass the 0.5 threshold. When a
  span is returned, it is often the right sentence.
- In a 5-letter expanded smoke test, adding the finding structure removed an
  evidence span that the smaller schema had returned on the same letter.
  Zero-shot choice fields were weak (a clear rate labelled `qualitative`), and
  every finding scored as a miss. This is only an anecdote, but it is the
  interference question in miniature.

On the pre-declared rule, zero-shot GLiNER is **not** promising for the answer.
The remaining question is whether it is learnable. That is cheap to answer with a
train300 LoRA run on the 3070, and it is the deciding experiment.

## Challenges and trade-offs

- **No arithmetic.** Many Gan answers need the note's counts combined or its
  window converted. A band classifier can only learn these as surface patterns.
  The alternative is a *compositional* hybrid: GLiNER extracts count and window
  spans, and deterministic code computes the label. That is a semantic rule, and
  it is the two-stage design the paper excludes. It would have to be reported as
  a hybrid, not as GLiNER.
- **Context.** Half the letters exceed 512 tokens. Full context relies on
  DeBERTa's relative positions beyond the training length. Chunking merges
  per-chunk decisions and can lose cross-chunk context (in the probe, the
  chunked answer was right and its span was lost).
- **Training-data scarcity and permissions.** train300 is the only split whose
  intended use covers "optimizer training". Treating fine-tuning as optimizer
  training needs your confirmation. Expanded targets exist only on dev750, so
  expanded fine-tuning means 5-fold cross-validation there (folds are built,
  stratified by band, seed 20260925). The guide says not to tune prompts to the
  finding score. Training on the reference is a different act, but it makes
  dev750 findings scores in-sample cross-validation results, not comparable to
  the zero-shot LLM runs. **This needs an owner decision before any expanded
  fine-tune.**
- **Evidence targets are incomplete.** 27% of letters have no verbatim Gan
  quotation. Those rows get no evidence target, rather than a false "no evidence" one.
- **Span alignment for values.** Reference values are normalised numbers, not
  spans. Training aligns them to the shortest phrase in the finding's evidence
  that the normaliser reads the same way: quantity 593/722 (82%), per 291/319
  (91%), window 142/163 (87%). The rest are omitted and counted.
- **Cost and latency.** GLiNER is local and free. After fine-tuning it could be
  run over every letter in minutes. That is the case for pursuing it even at
  lower accuracy, for example as an evidence locator or triage step.
- **Environment.** It needs a separate dependency set (transformers 4.x), and one
  machine crash showed that memory discipline matters on shared-memory Macs.

## Fine-tuning plan (machinery built)

Built and tested (`src/clinical_extraction/tasks/seizure_frequency/gan2026/gliner/`,
`scripts/benchmarks/gliner_decide.py`, `tests/test_gliner_decide.py`):

- Training JSONL for both targets (`build-data`). Every row passes gliner2's
  validator: train300 minimal, dev750 minimal, and dev750 expanded (1,350
  findings kept).
- Seeded, band-stratified dev750 folds (5 × 150).
- A `train` command wrapping `ExtractorTrainer`:
  - LoRA (r 16, α 32) or full fine-tuning;
  - device-aware settings (CUDA: batch 1 × 16 accumulation, bf16, gradient
    checkpointing; never fp16);
  - a training identity that records the exact training row IDs.
- Adapter or checkpoint inference through the same `infer`/`score` path, so
  zero-shot and fine-tuned runs are scored identically.

Phases:

1. **Zero-shot baselines** on the 3070: four runs (minimal/expanded × full/chunked).
2. **Minimal LoRA, train300 → dev750.** The deciding experiment. Then compare full
   fine-tuning and `--max-len 512` against chunked, if memory allows.
3. **Expanded, dev750 5-fold**, only after the owner decision above. Report
   interference (expanded minus minimal answer) within the same folds.
4. **DiffusionGemma parity.** The archived pilot
   (`archive/pre-lockdown-2026-09-24:scripts/benchmarks/diffusiongemma_single_label_pilot.py`)
   posed the same 10-way Purist choice with criteria. Use the same splits, the
   same targets (these JSONL files), and the same `score` projection, so the two
   models differ only in the model. GLiNER goes first because it is smaller and
   fits the 3070.

## Next steps

1. Run the four zero-shot baselines and the LoRA smoke test on the 3070 laptop (runbook order).
2. Train minimal LoRA on train300; score on dev750 against the pre-declared rule.
3. Owner decisions:
   - does train300 fine-tuning count as permitted optimizer training;
   - may dev750 reference findings be used as cross-validated training targets;
   - is a compositional (extract-then-compute) hybrid in scope at all.
4. Update this report with complete runs; replace the partial table.
