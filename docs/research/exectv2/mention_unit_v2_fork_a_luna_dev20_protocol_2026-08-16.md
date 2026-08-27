# ExECT mention-unit v2 — GPT-5.6 Luna protocol

Date: 2026-08-16  
Status: complete; frozen `dev20` live run is an **answer**  
Result: [mention-unit v2](mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)  
Plan: [ExECT LLM representation and hybrid re-evaluation](../../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)  
Review: [prompt fundamentals](../../plans/exect_prompt_fundamentals_2026-08-16.md) (signed off)  
Decision: [0055](../../decisions/0055-exect-semantic-inventory-and-method-contracts.md)  
Prior result: [mention-unit v1 (mention-unit v1 pruned; recover from Git history)  
Leftover owner: [trust-item remasure](prompt_variant_slots_2026-08-16.md)  
Design note: [what we ask the model to do](prompt_variant_slots_2026-08-16.md)  
Glossary: [CONTEXT.md](../../../CONTEXT.md)

Fork A stays. Decision 0050 and `test60` are unchanged. This file
replaces the paused draft that said “extract what is current.”

## Primary question

On the same 20 development letters, if we use the signed-off
clinical-name prompts — `llm` leftover words go in the number fields;
hybrid leftover words stay in evidence; the landed encoder reads
`clinical_name` plus `evidence` — does gold SeizureFrequency wording
appear as `clinical_name`, and do extras on letters with no gold
SeizureFrequency stay down?

One knob: this language. Scope is corrected. Rate-form fields are
restored on `llm`. “Mention,” “span,” and “coding fields” are out.

v1 asked for “exact letter spans” and “coding fields.” The model still
put the sentence in `text`, and the schema had no place for “every 3
weeks” (`count=1`, `period_count=3`, `period=week`). Empty-gold
SeizureFrequency extras also rose. This study uses the signed-off
prompts. It does not dump List 2, List 9, List 11, or the 49
`v0.9.24` letter examples, and it does not retune the landed encoder.

Headline F1 is context. A score rise that still leaves gold wording
inside a sentence is not an answer. A gold unit is copied when
`clinical_name` matches the gold wording or the hyphen-normalized gold
phrase. A sentence that merely contains that wording is not a hit.

## Data and row policy

- Dataset: ExECTv2 (2025), split manifest
  `data/ExECTv2 (2025)/splits/exectv2_split_v2.json`.
- Same frozen `dev20` as v1: EA0002, EA0004, EA0005, EA0006, EA0007,
  EA0008, EA0009, EA0010, EA0011, EA0012, EA0015, EA0016, EA0047,
  EA0074, EA0093, EA0120, EA0131, EA0133, EA0154, EA0158.
- Development rows may be inspected. `test60` remains aggregate-only
  and is not authorized.
- Do not run `dev140` until this `dev20` is clean under the stop rules
  below. A later `dev140` needs its own protocol. Promote nothing.

## Candidate and fixed comparators

- Candidate: `exectv2_mention_unit_v2` `llm` and matched `llm_with_rules`.
- Fixed mention-unit v1: saved v1 raws on these letters. No new v1 calls.
- Fixed control: saved GPT-5.6 Luna current-stack `v0.9.24` output,
  replayed through the unchanged control projection. Decision 0050 is
  unchanged.
- Fixed default v4: saved `exectv2_semantic_inventory_v4` fork-A `dev20`
  raws, rematerialized with the unchanged default projector.
- Fixed trust-item: those same v4 raws rematerialized with the saved
  `trust_item` policy. No new v4 calls. Trust-item is a comparator, not
  the hybrid method.
- One independent model call per method per row. Same model,
  temperature, output budget, and provider route.

## Model and generation

- Model: `openai/gpt-5.6-luna`.
- Temperature: 1.0.
- Maximum output tokens: 2400.
- Cache: disabled for fresh candidate calls.

## Method contracts

One list of rows. Each row has `clinical_family`, `clinical_name`, and
`evidence`. Both `clinical_name` and `evidence` are copied from the
letter, not paraphrased. `clinical_name` is mention wording: the
diagnosis type, the seizure words, the drug, or MRI / CT / EEG.
Leftover words — the number, date, dose, or result — do not live in
`clinical_name`.

| Clinical family | `clinical_name` is | `llm` also fills | Hybrid derives or rewrites |
| --- | --- | --- | --- |
| Diagnosis | Named epilepsy or seizure type | certainty, negation | Heading split, closed-table rewrite, noise drop |
| SeizureFrequency | Seizure, absence, or myoclonic-jerk words | count, lower_count, upper_count, period_count, lower_period, upper_period, period, state, change, since_or_during, point_in_time, month, year | Landed `sf_attribute_encoding` on `clinical_name` + `evidence`; uncoded-phenomenology suppression |
| Prescription | Drug or compact regimen | dose, unit, schedule, status | Planned-only and non-epilepsy suppression |
| Investigations | MRI, CT, or EEG | result, status | Pending-test suppression |

Shared rules:

- Empty clinical family: skip it. Rows on a letter with no gold units
  in that family are false positives.
- One row is one unit. A fact that belongs to two clinical families is
  two rows. They may share evidence.
- `llm` fields are family-specific. Do not list unused keys.
- Hybrid rules may read that row’s `clinical_name` and its `evidence`.
  They may not search the rest of the letter or grow rows from unused
  wording. Letter-level residual addition is out.
- Decision 0040 stays in force for rewrite, project, and suppress.
  Extractor substitution is not allowed.
- This study does not retune the landed encoder. Leftover words in
  hybrid evidence are expected.
- No codebook, no research metadata, and no “named type not generic”
  in the model-facing payload. Closed v9 tables stay in hybrid rewrite.
  Do not dump List 2, List 9, or List 11.

The scored object remains the ExECT mention set. The adapter maps
`clinical_name` → mention wording and `clinical_family` → the kind.
Internal `PredictedMention.entity` still means the kind. The model
never sees that.

## Model-facing wording

Two prompts. Neither mentions a method. Neither says “return only.”
Do not use mention, span, coding fields, or bare “family” in anything
the model sees.

**System line (both)**

> List each diagnosis, seizure-frequency statement, current medicine, and completed test with a result. Return the requested JSON exactly.

**Shared opening (both)**

> Read the letter once. Return one list that follows the schema. Each row has a clinical family, a clinical name, and evidence.
>
> The list has four clinical families:
>
> - Diagnosis: a named epilepsy or seizure type the letter applies to this patient, including in history.
> - SeizureFrequency: a frequency statement — a rate, dated count, last event, change, or seizure-free duration — including past ones.
> - Prescription: a current anti-seizure medicine.
> - Investigations: a completed MRI, CT, or EEG with a result.
>
> In clinical name, write the diagnosis type, the seizure words, the drug, or MRI / CT / EEG.

**`llm` continues**

> If the letter says “2 to 3 focal seizures a week”, the clinical name is focal seizures. The “2 to 3” and the “week” go in the number fields, not in clinical name.
> In evidence, copy the shortest part of the letter that supports that row.
> If there is a rate, a date, or seizure freedom, use the form table.

**Hybrid continues**

> If the letter says “2 to 3 focal seizures a week”, the clinical name is focal seizures. The “2 to 3” and the “week” stay in evidence, not in clinical name.
> In evidence, copy the shortest part of the letter that supports that row, including the number, date, dose, or result.

**Shared closer (both)**

> If a clinical family has nothing, skip it. If the same type is both a diagnosis and a frequency statement, write two rows. They may share evidence.

### Form table (`llm` payload only)

One-liner above the table: “If there is a rate, a date, or seizure
freedom, use this table.” Abstract rows. No patient names, no letter
IDs, no gold restatements.

| When the letter says | Fill |
| --- | --- |
| A single count over a time unit, including every 3 weeks | `count`, `period_count`, `period` — every 3 weeks is 1 / 3 / week |
| A count range | `lower_count`, `upper_count`, plus the same time or date fields |
| A time-unit range | `count`, `lower_period`, `upper_period`, `period` |
| A count in a stated month or year | `count` (or the range), date fields, `since_or_during=during`. Do not invent `period=month` unless the letter says per month |
| No further / none / not had any since a date | `count=0`, `since_or_during=since`, date fields |
| Seizure-free for a duration, or last event a stated time ago | `count=0`, `period_count`, `period` |
| A count since last clinic or a drug change | `count`, `since_or_during=since`, `point_in_time` |
| Returned, worse, improved, frequent, or infrequent, with no count | `change` only |

Closed values, lowercase: `period` day / week / month / year;
`since_or_during` since / during; `change` decreased / frequent /
increased / infrequent / same. Approximate count words only: couple 2,
few 2, several 3. The adapter maps these to gold names. Do not paste
the rest of List 11.

### Selection cues (both)

1. Copy the clinical name from the letter. If a clinical family has
   nothing to list, skip it.
2. Bare absences or myoclonic jerks are not a diagnosis. Named absence
   seizures or myoclonic seizures are.
3. Do not list epilepsy from driving, counselling, or a general
   discussion unless the letter attaches it to this patient.
4. A named type with a count of 0 is still a diagnosis, and also a
   seizure-frequency row with count 0. That is two rows. They may share
   evidence.
5. List every frequency statement, including past ones: a rate, a dated
   count, a last event, a change, or a seizure-free duration. The
   clinical name may be seizures, a named type, absences, or myoclonic
   jerks. Do not use events, episodes, or slang. Do not list a seizure
   story that has no frequency.
6. List a completed MRI, CT, or EEG only when the letter states a
   result. Do not guess the EEG type.
7. Current anti-seizure medicines only. Rescue may lack a dose. If the
   letter says the same dose and does not state the dose, leave the
   drug out.

No eighth cue for second-unit recall.

The rendered payload must not contain: mention, span, coding fields,
current (except cue 7 and the system line’s “current medicine”), gold,
scorer, benchmark, frozen, control, CUI, Markup, UMLS, List 2, List 9,
List 11, “named type not generic,” “this method,” or “return only.”

## Scoring

Primary decision metric: whether gold mention wording appears as
`clinical_name` on development rows. Compare that coverage to
mention-unit v1, default v4, and trust-item on the same letters.

Secondary: four-family `clinical_headline` (context only), semantic F1,
family F1, extras versus misses, empty-gold extras, non-target mentions,
hybrid growth from unused letter text, rule-trace attribution, and
changed-row mechanism classes on development rows only.

## Minimal implementation change

Version a new research-lane prompt to `exectv2_mention_unit_v2`. Keep
the hybrid rewrite path on the landed encoder. Widen the `llm`
SeizureFrequency allowlist to the fields in the contract table; the
adapter already maps `period_count`, `lower_period`, `upper_period`,
`change`, `point_in_time`, `month`, and `year`. Parse `clinical_name`
and `clinical_family`; do not ask the model for `text` or `family`.
Change the task, schema keys, field descriptions, and selection cues
to the wording above. Do not change gold, the selected stack, the
default prompt, or the v4 / `trust_item` projectors.

## Required checks and stop rules

Before live calls:

- contract tests pass, including a rendered-prompt check that “span,”
  “mention,” “coding fields,” “this method,” and “return only” are
  absent; that “current” does not appear on Diagnosis,
  SeizureFrequency, or Investigations guidance; that `clinical_name`
  and `clinical_family` are present; that `llm` has `period_count` and
  the form table; and that hybrid leftover words are taught as
  evidence;
- rendered prompts stay free of research metadata, unused attribute
  keys, List 2 / List 9 / List 11, and “named type not generic”;
- a prompt-only smoke writes `model_calls`: 0.

After `dev20`, treat the study as `revise` if any of these hold:

- empty-gold SeizureFrequency extras rise versus mention-unit v1,
  default v4, or trust-item on the same letters;
- ECG or other non-target investigations appear;
- hybrid grows mentions from unused letter text.

A mechanically clean `dev20` that still leaves gold wording uncopied,
or still puts that wording inside a sentence, is a valid
`negative_result`. Headline movement alone does not promote.

Do not repair a miss by inspecting `test60`. Leave these leftovers
untouched until this study answers: bundled drugs (n=3),
intervening-word counts (“one recent … seizure”), and the one EA0015
EEG Unknown extra. EA0009 `cluster-of-seizures` may stay unread; do
not retune the prompt for that one letter.

Stop with `answer`, `negative_result`, `revise`, `reject`, or
`blocked_by_instrumentation`.

## Artifact contract

Study directory:
`experiments/exectv2_mention_unit_v2_luna_dev20_20260816/`.

Write `comparison.json`, `rows.jsonl`, and an emission census. One JSON
object per development row with source row ID, prompt hash, raw model
output, parsed items, evidence checks, semantic view, rule trace,
scorer view, gold-wording emission, and comparator keys. `test60`
artifacts, if later authorized, remain aggregate-only.

## Claim boundary

A `dev20` result can support a development-method decision. It is not
clinical validation, holdout evidence, or a Decision 0050 change.
Contract tests and the prompt-only smoke passed before the live calls.
