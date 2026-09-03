# Paper methods

Date: 2026-08-17
Revised: 2026-09-03 (methods reorganised by stage: Architecture and
the evidence record, Extract, Decide, Evaluation; the record is named
the evidence record and shown as a field table; Figure 2 redrawn as a
funnel with a fork into the two executors; policy table cut to two
columns; new one-row-two-implementations table)
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
does a decision applied to the evidence record improve on the
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
that reads the full letter and returns the evidence record: every
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

## C. Architecture and the evidence record

Paper subsections are B. Architecture and the Evidence Record,
C. Extract, D. Decide, E. Evaluation. The former "LLM Prompt Design",
"Rule Design" and "Pipeline Optimisation" subsections are folded in:
prompt design into Extract and Decide, rule design into Decide, and the
one load-bearing sentence of optimisation (interacting policies
motivated scoring after each stage) into Architecture; the development
controls moved to Evaluation.

The shared data structure is called the **evidence record** (not
"extraction record" or "candidate record"): it is named for what decide
consumes, and the evidence-obligation ablation stresses it.

**Figure 2** (`paper/draft/pipeline_architecture.tex`, compiled to
`pipeline_architecture.pdf`) follows one development letter through the
pipeline and is drawn to show three things: the letter narrows to a
record and the record to a label; one call produces the record; the
record forks to two executors that reconverge on one label. The four
prompt ingredients appear as tags on the extract call.

Funnel numbers reported in the Figure 2 caption, computed from the
cited Gemini 3.7 Flash `dev750` extraction cell
(`paper_experiments/gan/gan_llm_extract/gemini37flash/dev750/rows.jsonl`,
750 rows, all parsed): 2.16 events per letter (median 2; 216 letters
with one event, 292 with two, 242 with three or more; max 6); 22.1
quoted evidence words per letter (median 21); final label 3.9 words.
Letters are about 400 words. These are development mechanism
statistics for one model, not test results.

Figure 2 example: `dev750`, `source_row_index` 14187, cited Gemini 3.7
Flash cell. Letter: "She discontinued Valproate on 10 Jul. Shortly afterwards,
she experienced 2 to 3 seizures, one triggered by missed medication. She has
remained seizure-free since then." Record: e1 frequency rate, shortly after 10 Jul,
2 to 3 seizures; e2 seizure free, since mid-July, seizure-free since then;
provisional answer seizure free for a duration (e2). Decide: post-change burst
row applies, counting the burst rate over that interval = 2 to 3 per 1 month.
Rules (`post_change_burst`) and LLM call 2 both return 2 to 3 per 1 month, which
matches gold. Sources:
`paper_experiments/gan/rungs/gemini37flash/dev750/scored.jsonl`,
`paper_experiments/gan/gan_llm_extract/gemini37flash/dev750/rows.jsonl`,
`paper_experiments/gan/gan_llm_select_from_extract/gemini37flash/dev750/rows.jsonl`.
Figure 1 (the example letter with two highlighted candidates) is a
different development letter (`source_row_index` 5873) and is not a
decide-corrects-extract example.

**Table II, the evidence record**, lists the fields of the frozen
extract schema
([`gan_llm_extract_prompt_template.json`](../../../paper/supporting%20materials/gan_llm_extract_prompt_template.json))
with the Figure 2 event e1 as the example event and e2 as the provisional selection. Per event: `event_id`,
`kind` (six categories), `raw_value`, `evidence`, `time_window`,
`applies_to`, `temporality`, `assertion_status`, `notes`. Selection:
`selected_event_ids`, `final_label`, `final_kind`, `evidence`,
`rationale`, `confidence`. Note the honest reading of the contract:
events carry `raw_value` (instructed as source-near, in practice
usually written in an allowed form), and the canonical label is on the
selection only. The paper says "value" for events and "label" for the
answer. The second call returns the selection block and may not add
events or quotes.

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

## E. Extract

The paper frames extract as the larger task: whole letter in, record
out, most complex prompt; the model finds and quotes, normalises, and
chooses in one call. The extraction prompt has four ingredients, each
removed in turn in the ablations:

1. **Instructions** to find every seizure-frequency statement, represent
   it as an event in one of six categories, and propose a provisional
   answer.
2. **Examples** of how events should be represented.
3. **Allowed labels**: a closed list of the canonical label forms used
   by the gold standard, with writing rules (digits, flattened bounds,
   night counts as day counts).
4. **Evidence obligation**: the `evidence` fields for every event and
   the selection, with the instruction that each must be an exact
   quote. The ablation removes the fields and the instruction together
   as one package; it does not test the quote instruction alone.

Each event is assigned one of six categories (frequency rate, cluster
frequency, seizure free, last event only, unknown frequency, no
reference). The extraction prompt states the first two rows of the
decision policy table (overall count over breakdown; not seizure-free
while events continue), so the model applies them when it proposes the
provisional answer; the paper says so in the Extract text and marks the
two rows with an asterisk in Table III. The remaining eight rows are
the work of decide. The frozen template, without `note_text`, is
[`gan_llm_extract_prompt_template.json`](../../../paper/supporting%20materials/gan_llm_extract_prompt_template.json).
It is not the source-near variant (`gan_llm_extract_raw`) and not the
second-call decide prompt.

## F. Decide: policy and two implementations

**Table III, decision policy**, is now two columns (the record
contains; final answer), ten rows in two groups; the
provisional-to-final example column was cut and the worked examples are
in the supporting materials. Rows and Hybrid rule families:

| Group | The record contains | Final answer | Hybrid rule family |
| --- | --- | --- | --- |
| Choose a different event | An overall count and a breakdown by seizure type | The overall count | extract prompt; restated in call 2 |
| Choose a different event | A seizure-free statement while other seizure-like events continue | The continuing events | extract prompt; restated in call 2 |
| Choose a different event | A brief daily spell, or unknown, and the usual gap between seizures | The usual gap | `usual_interval` |
| Choose a different event | A year-to-date total and a typical rate | The typical rate | `typical_over_ytd` |
| Write a new label | Counts for named months (Figure 2) | Total over those months | `monthly_diary` |
| Write a new label | Seizures on separate dates or months | Count over that span | `dated_sequence` |
| Write a new label | A recent count after a stated seizure-free interval | Count over that interval | `breakthrough` |
| Write a new label | A burst after a treatment change, then a quiet period | Burst count over the quiet period | `post_change_burst` |
| Write a new label | A dated last seizure and a quiet period since of under six months | Count over the time since | `last_event_well_since` |
| Write a new label | Current attacks that are not epileptic | Seizure free for multiple years | `non_epileptic` |

On `dev750` the rules that changed an answer were `monthly_diary` (47),
`last_event_well_since` (10), `dated_sequence` (10),
`post_change_burst` (7), `breakthrough` (3) and `non_epileptic` (1)
(`paper_experiments/gan/rungs/gemini37flash/dev750/hops.jsonl`).

**Table IV, one policy row, two implementations**, shows the
month-count row as (left) pseudocode of the Hybrid rule including its
guards and (right) the instruction and worked example given to LLM
call 2. Sources: `monthly_diary_label_from_events` in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_structured_monthly_diary.py`
(sum counts over two or more named months; span is first to last month
inclusive) and `_should_preserve_label_from_monthly_diary` in
`hybrid_structured_events.py` (never replace a per-day or per-week
rate, or seizure free for four months or more or any years); the
"Month counts" case in
`src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/prompt_llm_select.py`
(`CASES`), whose example is 3 in March + 6 in May → 9 per 3 month. The
paper states the executors differ in how guards are expressed, how a
pattern is recognised, and in determinism.

In Hybrid, rules first rewrite any label the model left in a
non-canonical form (at most 0.01 on `test450`: 355 → 360 before the
decision rules), then apply the policy. Each rule is a named function
that reads the record, never the letter, and has guards that stop it
firing. The repository's finer authority vocabulary (gate, reselect,
rewrite) stays in the [rule catalogue](../rule_catalogue.md) and the
supporting materials. No decision rule scans the letter for a new
candidate. In LLM-only, the second call receives the record with the
provisional answer marked as the first choice, one instruction with one
worked example per row, and may write a new label only when no single
event is the answer; it never adds events or quotes.

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
