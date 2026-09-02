# Paper methods

Date: 2026-08-17
Revised: 2026-09-02 (Gan only; two decision executors on one shared
extract; paper stages are extract and decide)
Status: current; matches `paper/draft/FES.tex` Section III
Owner: this file
Scope: [Gan is the dissertation paper](../decisions/gan-is-the-dissertation-paper.md),
[paper-story simplification](../decisions/paper-story-simplification.md)

Paper stage names are **extract** and **decide**. The implementation
names three stages (`find`, `encode`, `select`). The cited extraction
prompt already writes the gold label form, so `find` and `encode` are
bundled into one call and reported as extract; `select` is reported as
decide. Implementation names appear below only where they identify an
existing artifact. LLM calls are called LLM calls, not agents.

## Research questions

**Primary question.** Can a prompted LLM
call and a decision policy extract a patient's current
seizure-frequency pattern from epilepsy clinic letters as accurately as
the fine-tuned LLM previously reported on the same synthetic corpus
(Gan et al., 2026)?

**Secondary question.** Does extract then decide add value:
does a decision applied to the extraction record improve on the
provisional answer; does it matter whether
rules or a second LLM call apply the policy; and which
ingredients of the extraction prompt does the result depend on?

The two-executor comparison (section D) answers the first part of the
secondary question. Three extraction-prompt ablations answer the last
part. The six-model comparison, the Gemini low/high thinking contrast,
and the Gemini temperature 0 versus 1 ablation show how far the result
depends on the model and its sampling settings. Saved outputs, quoted
evidence, and replayed decision stages are the experimental controls
that make the comparisons paired; they are not a separate research
question.

## A. Study design

The study treats the route from a clinic letter to one submitted
seizure-frequency label as two stages. **Extract** is one LLM call
that reads the full letter and returns a structured record of every
candidate seizure-frequency event, each with an exact quoted evidence
span, a category, and a label in one of the gold standard's canonical
forms, together with a provisional answer chosen from those
candidates. **Decide** receives that record and a fixed decision
policy, never the letter, and returns the final label with the event
or events that support it.

The decision is performed in two ways on the same record.
In **Hybrid**, rules apply the policy. In **LLM-only**, a
second LLM call applies the same policy written as instructions with
worked examples. The extraction call, its output, and the policy are
shared, so a difference between the two executors is attributable to
the decision stage alone. The provisional answer is what a one-prompt
system would submit; scoring it gives the one-prompt baseline that
both executors are measured against.

The study evaluates agreement with the task's reference labels on
synthetic letters. It does not evaluate clinical correctness,
real-letter performance, workflow fit, privacy compliance, or
deployment readiness. Locked test results are reported only as
aggregate totals; development data are used to examine mechanisms and
limitations.

## B. Dataset, gold form, and split policy

| Characteristic | Gan 2026 |
| --- | --- |
| Source material | Public synthetic epilepsy clinic letters (Gan et al., 2026), modelled on King's College London letters |
| Full resource | 15,099 letters; 1,200 used here |
| Task output | One current seizure-frequency label per letter, with one supporting quote |
| Development split (`dev750`) | 750 letters |
| Locked test split (`test450`) | 450 letters, stratified by Pragmatic category |
| Scoring unit | One label per letter; micro-F1 equals per-letter accuracy |

The letters are about 400 words each. Preprocessing was minimal:
quotes, new lines, tabs, the ≤ sign and nulls were cleaned, and letters
were ingested whole with no tokenisation, section-splitting, or
truncation. The 1,200-letter sample was split 750 / 450 stratified by
the four Pragmatic categories (frequent, infrequent, unknown, seizure
free). The `dev750` distribution is 51% / 17% / 17% / 15%; `test450`
is 50% / 18% / 17% / 15%.

The gold standard's quote is a loose comparator for evidence, not gold
for spans: it may be exact, paraphrased, abbreviated, ellipsized, or
missing. Evidence quality is therefore measured in the paper as
exact-substring adherence of the selected event's quote, and a
development-first directional study of semantic sufficiency is
specified before any further held-out replay
([protocol](../../research/gan2026/gan_directional_evidence_adjudication_dev750_protocol_2026-09-02.md)).

## C. What each stage receives and returns

| | Extract | Decide |
| --- | --- | --- |
| Input | Full letter | Candidate record and decision policy; not the letter |
| Output | Candidate record: events, each with quoted span, category, canonical label; provisional answer | Final label and its supporting event(s) |
| Performed by | LLM call 1 | Hybrid: rules. LLM-only: LLM call 2 |

The pipeline is a fixed sequence of calls and functions. No LLM call
uses tools, chooses the next step, or invokes another model; each call
is a prompt with a fixed input and a schema-validated JSON output. The
letter is the only free-text input; every later step reads the record.

## D. Decision executors

| Executor | LLM calls | Extract | Decide | Cited `test450` Purist |
| --- | ---: | --- | --- | ---: |
| Hybrid | 1 | LLM call 1 (`gan_llm_extract`) | Recorded rules (`gan_rules_encode`, then `llm_select_after_codebook`) | 0.86 (387) |
| LLM-only | 2 | Same call, same record | LLM call 2 (`gan_llm_select_from_extract`, policy-example prompt) | 0.85 (383) |

Because decide works from the saved record, both executors were
replayed on the same extraction output without a new model call.

Other configurations were built and measured and remain repository
evidence, not paper rows: rules throughout (0.72), rule-extracted
candidates added to the model's record before rule decide (0.82), the
same extract without the deterministic label rewrite (0.85), a
separate LLM label-rewriting call before decide, and a one-call prompt
that applies the policy inside the extraction call. They are
summarised in the supporting materials with their scope
([results](results.md) section B and D).

## E. Extraction prompt

The extraction prompt has four ingredients, each removed in turn in
the ablations:

1. **Instructions** to identify relevant seizure-frequency events and
   to propose a provisional answer under the decision policy.
2. **Examples** of how events should be represented.
3. **Allowed labels**: a closed list of the canonical label forms used
   by the gold standard.
4. **Evidence obligation**: schema fields for the evidence span of
   every event, with the instruction that each span must be an exact
   quote from the letter. The ablation removes the fields and the
   instruction together as one package; it does not test the quote
   instruction alone.

Each event is assigned one of six categories (frequency rate, cluster
frequency, seizure free, last event only, unknown frequency, no
reference). The decision policy is stated once and applied twice:
provisionally by the model inside the extraction call, and finally at
decide. The frozen template, without `note_text`, is
[`gan_llm_extract_prompt_template.json`](../../../paper/supporting%20materials/gan_llm_extract_prompt_template.json).
It is not the source-near variant (`gan_llm_extract_raw`) and not the
second-call decide prompt.

## F. Decision policy and rules

| When | Do |
| --- | --- |
| Several current seizure types are present | Choose the highest current or recent frequency |
| The letter gives an overall current count and a breakdown by type | Choose the overall count |
| A seizure-free statement sits with other current seizure-like events | Keep seizure-free separate from unknown or last-event statements |

In Hybrid, rules first rewrite any label the model left in a
non-canonical form (at most 0.01 on `test450`: 355 → 360 before the
decision rules), then apply the policy. Each rule is a named function
that reads the record, never the letter. Rule authority is recorded by
type: **gate** (block a provisional answer the policy forbids),
**reselect** (choose a different already-extracted event), and
**rewrite** (derive a new label from the extracted events, such as a
diary total). No decision rule scans the letter for a new candidate.
The named families are in the [rule catalogue](../rule_catalogue.md).
In LLM-only, the second call states the same policy as instructions
with worked examples and receives only the record.

## G. Development controls and reproducibility

All prompts, schemas, rules, and configuration choices were developed
on `dev750`. Development material was used to identify failure modes,
refine the record, and specify the decision policy. `test450` was
reserved for aggregate-only evaluation: individual test letters and
their outputs were not inspected, and a held-out defect starts a new
development candidate rather than a holdout repair.

Each run retains the model's record, its evidence, the rule
transformations, and the final answer. Where a comparison changes only
the decision stage, that stage is replayed from the saved record
rather than generated by a new call. Replayable cells live in
`paper_experiments/`. The supporting materials hold the full prompts,
schemas, rule definitions, model settings, and replay artefacts.

## H. Evaluation protocol

The primary metric is Purist micro-F1 on `test450`, following Gan et
al. (2026): the submitted label is mapped to a monthly-frequency band
while keeping the seizure-free and uncertainty outcomes. Pragmatic
micro-F1 is the coarser companion (frequent, infrequent, unknown,
seizure free). Each letter has one gold label and one prediction, so
micro-F1 equals the share of letters answered correctly; accuracy is
not printed as a second headline.

Results are compared with the Synthetic (1,166) evaluation reported by
Gan et al. (2026), a different held-out sample of the same corpus with
identical metric definitions. That comparison is bounded: it is not a
paired test and not a state-of-the-art claim. Paired exact McNemar
tests are used only where both arms are scored on the same `test450`
letters (Hybrid versus LLM-only; temperature; thinking) and report
discordant counts only.

The primary model is Gemini 3.7 Flash at temperature 0 with low
thinking effort. It is the only model used for the second decision
call, the prompt ablations, and the temperature and thinking
ablations. Six models were evaluated as the extraction call in Hybrid
(Gemini 3.7 Flash, Grok 4.6, DeepSeek V4 Flash, GPT-5.6 Luna, and two
local models, Qwen 3.8 27B and Gemma 4 26B). For the six-model table
the paper also reports contract adherence: exact-substring evidence
for the selected event, non-semantic format repairs, and unparsed
records. The two local models show that the design can run
on a single laptop GPU under the same synthetic task; they do not show
real-letter performance or deployment readiness.

## Supporting implementation material

The implementation map from paper stages to live runners is in
[cells and runners](../cells_and_runners.md) and
[architecture](../architecture.md); both use implementation names.
The rule catalogue, model roster, prompt decisions, and experiment
scope remain in the linked paper documentation. They support
reproducibility and audit, but are not part of the main Methods
narrative.
