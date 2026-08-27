# ExECT prompt fundamentals

Date: 2026-08-16  
Status: **signed off**; mention-unit v2 `dev20` is an answer; `dev140` is a revise  
Owner campaign: [ExECT LLM representation and hybrid re-evaluation](exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)  
Glossary: [CONTEXT.md](../../CONTEXT.md)  
Not a new roadmap, status board, or research canon. This is the review the
existing campaign needed before another prompt rewrite.

## Why this exists

The latest mention-unit v2 draft asked the model to “extract what is
current for this patient.” That is the wrong task. Only **medications**
must be current. Gold already codes past seizure-frequency statements,
diagnoses, and completed investigations. We measured that, walked it
back, and then wrote it into the next prompt again.

The circle is not “we have not tried enough prompt versions.” It is that
each rewrite has been changing three things at once — the job, the
schema, and the current-versus-historical rule — while treating the last
failure as a reason to invent a new vocabulary. This document separates
what the history already decided from what is still a real experiment.

No live calls. Decision 0050 and `test60` are unchanged.

## Sign-off

Grilled 2026-08-16. Fork A stays. Mention-unit v2 on frozen `dev20` is
an **answer**:
[report](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md).
One knob was this language. Do not retune it for EA0009 or empty-gold
extras. The frozen-language `dev140` transfer is a **revise**:
[report](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_2026-08-16.md).

### Hard-question answers

1. **Gold wording without extras.** Split. On frozen `dev20`, v2 copies
   gold wording and extras did not rise. On `dev140`, wording still
   copies (131/187) and empty-gold extras rose versus v4 / trust-item.
   Empty-gold extras cannot be prompted away: the model cannot see gold.
   Cue 1 plus cue 5 is the bound.
2. **How much prompt.** Smallest payload: define the four clinical
   families, then say where each piece goes; eight-row form table on
   `llm` only; seven selection cues; no letter examples; no codebook.
   Not a new metaphor for mention.
3. **Unread second-unit SF.** Keep seven cues. Cue 5 already says every
   frequency statement. No eighth cue. Decision 0041 stays. A remaining
   EA0009 miss is a leftover, not a reason to grow this payload.
4. **Hybrid parse.** Landed encoder on that item’s `clinical_name` plus
   `evidence`. Trust-item is not the method. Do not retune the encoder
   in the same study that changes the prompt.
5. **Fork B.** Not now. Fork B is honest only if, after this study, the
   leftover is still “the model will not name Markup units unless we
   teach Markup.” Empty-gold extras and one unread second unit are not,
   by themselves, Fork B.
6. **“Current seizure experience.”** Do not write “current” on
   Diagnosis, SeizureFrequency, or Investigations. Cue 5 is the
   replacement: every frequency statement, including past ones; no
   seizure story that has no frequency. Prescription is the only
   current-only family.

### Locked model-facing language

- Keys: `clinical_family`, `clinical_name`, `evidence`. Adapter maps
  `clinical_name` → mention wording and `clinical_family` → the kind.
- **Clinical name** is the diagnosis type, the seizure words, the drug,
  or MRI / CT / EEG. Not the number, date, dose, or rest of the sentence.
- **Evidence** is the smallest supporting substring. Model-facing word:
  supporting sentence.
- Two prompts. Neither mentions a method. Neither says “return only.”
  Leftover words go in the number fields on `llm`, and in evidence on
  hybrid.
- Banned in the payload: mention, span, coding fields, current (except
  cue 7), gold, scorer, CUI, Markup, List 2 / 9 / 11, “named type not
  generic,” “this method,” “return only.”

The exact task text lives in the v2 protocol.

### Seven selection cues

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

## Already decided — do not re-open

These are not hypotheses. Re-testing them as if they were new is how we
went in a circle.

| Fact | Evidence | What it is not |
| --- | --- | --- |
| Only Prescription is current-only | v9: “We are only annotating current prescriptions for anti-seizure medications.” Plans without a stated dose are out. Past drugs are out. | “Extract what is current” for every family |
| SeizureFrequency includes dated counts, last-event, change, and seizure-free duration | v9 examples: 5 in May; last generalised seizure 5 years ago; last seizure September 2012; seizure-free 2 months; frequency improved since a drug. v19 historical guard recovered SF after v12 current-scope leftover damaged it (−0.2234 hybrid SF vs `v0.9.24` on `dev20`) | “Current epileptic frequency only.” v9’s phrase “current seizure experience” means a **frequency statement** about the patient’s seizures, including last-event and dated counts. The exclusion is past control **without** a frequency statement (“Tegretol controlled her seizures very well”) |
| Diagnosis includes named types that apply, including those in background or history | v9: concepts may sit in the heading, in background history, as past events, or in the opinion. Person trigger required. Generic “seizures / absences / jerks” are SeizureFrequency, not Diagnosis | “Diagnoses that apply now” as a current-only filter |
| Investigations are completed tests **with a result** | v9: EEG / CT / MRI plus normal/abnormal/unknown. No result → do not annotate. Pending tests are out. A past MRI with a result is in | “Current investigations” |
| Do not dump the annotator codebook into the prompt | `v0.9.24` is 84 rules, 49 examples, ~59k characters on EA0133. v10 cut it and SF collapsed because encoding left with the dump. v11–v16 put the tables in hybrid code and never recovered the selected stack | Pasting List 2, List 9, List 11, or the 49 letter examples back in |
| Do not ask for a clinical diary and hope rules recover coding | Inventory v2 hybrid 0.7117; v3 0.6667; v4 0.6175 vs control hybrid 0.9251 on the same `dev20`. v26/v27 cleaned the parse and still lost SF (0.7111 / 0.7059) | Another “ordinary-language event” schema with the same scorer |
| The two-method difference is real and must stay | `llm` fills family-specific fields. Hybrid emits wording + evidence only; named rules rewrite, project, and suppress. Decision 0040 / 0055 | Asking hybrid to re-read the letter, or asking `llm` to emit only a sentence |
| Empty family → emit nothing | Empty-gold extras are false positives. Mention-unit v1’s stop rule fired when empty-gold SF extras rose 2→6 | “List everything that might be relevant” |
| Decision 0055 already keeps historical seizure facts | “Current and planned prescriptions, current and **historical** seizure facts … remain separate items.” | Treating “current” as the inventory default |

The v10 residual analysis listed “current-scope policy (current regimen,
completed test, current epileptic frequency)” as one grammar the scorer
uses. That sentence is where the over-scope started. v12 tested it and
failed. v19 reversed the seizure half. Later Fork A copy still says
“events that apply now” and “current rates.” The mention-unit v2 task
repeated the same sentence in plainer words.

## Prompt history

Scores below are development only. `dev20` is the frozen 20-letter pool
unless marked `dev140`. Control hybrid on that pool sits around
**0.92**. Live default remains `exectv2_hybrid_key_family_event_ledger_v0.9.24`.

### 1. Selected stack — codebook in the prompt

`v0.9.24` grew from the 18 June v0.1 contract (12 structural rules, 3
examples) to 84 rules and 49 worked examples by 23 June. The original
task was: read the letter once; build a compact list of events for
medication, diagnosis, seizure frequency, and investigations. Family
guidance for SF named dated counts, ranges, clusters, seizure-free
duration, and change. It did **not** say “current only” for SF,
Diagnosis, or Investigations. Prescription later became current-only,
which matches v9.

The dump works as a score. It is not a method we can explain or edit
without a new model call. That is why the convention-migration campaign
exists.

### 2. Cut the dump (v10) — right deletion, wrong sufficiency bet

v10 kept the v0.1 topology and dropped the manual. Luna still found the
right sentences and wrote English into the fields (`several`, `two`,
`2-4`). Hybrid could not translate them. `dev20` hybrid **0.7265**
(−0.1946); SF **−0.4951** on both raw and hybrid.

The residual analysis was right that the missing piece is an **encoding
grammar**, not the 49 examples. It was wrong to fold “current epileptic
frequency” into that grammar as if it were the same kind of fact as
“current regimen.”

### 3. Move the codebook into hybrid (v11–v16)

v11 put closed tables in code. Hybrid **0.8439** on `dev20` (−0.0772 vs
control). SF still −0.2161. v12 added the current-scope leftover:
hybrid **0.8646**, but SF **−0.2234** vs control. That is the
measurement of “make everything current.”

v13–v16 kept moving conventions into rules. v16 on `dev140` is the
best of that series: hybrid **0.8445** versus remasured `v0.9.24`
**0.8983** (−0.0538). Still unselected. Residual reading: leftover is
form-projection and empty-gold inventory, not unread letters.

### 4. Historical guard (v17–v21)

v17 changed request shape and added history sinks. v18 narrowed the
sinks. v19 added a present/ongoing guard for counted events so
historical frequency statements were not dropped. `dev20` hybrid
**0.9196** (control 0.9211); SF **0.8750**. `dev140` hybrid **0.8669**
versus v16 **0.8445**; SF 0.6667 → 0.7138. Preserve for the next
batch; not promoted.

v20 and v21 tried clause-head / seizure-free-anchor wording on top of
v19 and both regressed. Rejected.

v19 is the last prompt in this line that treated historical
SeizureFrequency as in-scope and almost matched the selected stack on
the frozen pool **without** putting the 49 examples back.

### 5. Cleaner parse of a still-wrong job (v22–v27)

v22 named-type ablation, v24–v25 CUI/multistate, v26–v27 clinical-family
contracts. v26: clean parse, hybrid **0.8610**, SF **0.7111**, 7/20
exact. v27: **0.8772**, SF **0.7059**, 8/20 exact. Evidence for
redesign, not a fill. A parser that accepts the payload is not the
same as a task the scorer measures.

### 6. Fork A inventory (v2–v4, trust-item, mention-unit)

The representation campaign kept `clinical_headline` and changed what
the model is asked to emit.

| Study | What we asked | Result on `dev20` unless noted | Verdict |
| --- | --- | --- | --- |
| Inventory v2 | Ordinary-language clinical diary | hybrid 0.7117 vs control 0.9251 | revise — changed the task, kept the scorer |
| Inventory v3 | One list of current coded events | hybrid 0.6667; model-only 0.7230 | revise |
| Inventory v4 | Same list; hybrid event-only | hybrid 0.6175; model-only 0.6909 | negative_result |
| v4 `dev140` damage catalog | No new calls; inspect projector | Projector ignored landed v9 tables | answer |
| trust-item remasure | Same v4 raws; projector-owned classes | `dev140` llm SF 0.5134 / hybrid 0.4430 vs control 0.8291; Investigations recover | answer — leftover is unread or generic events, not another table import |
| Mention-unit v1 | “Exact letter spans” + “coding fields”; SF allowlist missing `period_count` | llm 0.6234 / hybrid 0.6301; SF 0.1613 / 0.0357; empty-gold SF extras 2→6 | revise |
| Mention-unit v2 draft | Restore rate-form fields; still said “extract what is current” | not run | **rewritten** after this sign-off; no calls yet |

The instruction-job note was right that the winning job is “copy the
wording, fill the fields,” not “write a sentence.” It was wrong to call
those wordings “current mentions.”

## The circle, in one picture

```text
v0.1 task: list events in four families
        │
        ▼
v0.9.24: same job + whole codebook in the prompt     ← selected, not explainable
        │
        ▼
v10: drop the codebook                               ← SF collapses (encoding left)
        │
        ├── v11–v16: tables in hybrid                ← better, not recovered
        ├── v12: “current” on every family           ← SF damaged; measured
        └── v19: put historical SF back              ← almost recovered on dev20
                │
                ▼
        v26/v27: cleaner schema, still wrong job
                │
                ▼
        Fork A: diary → flatter events → mention wording
                │
                └── v2 draft: “extract what is current”   ← v12 again
```

Two false cuts keep coming back:

1. **If the codebook dump is bad, drop encoding too.** Encoding is the
   rate-form table and the closed values. The dump is List 2 / 9 / 11,
   the 49 letter examples, architecture scaffolding, and research
   metadata.
2. **If Prescription is current-only, everything is current-only.**
   v9, v12, and v19 already contradict that.

A third false cut appeared in Fork A: **if the model should not emit
gold field names, it should emit a paragraph.** The model still has to
name the unit the scorer counts. The paragraph is a different task.

## Keep — fundamental components

These stay unless a later decision explicitly replaces them.

1. **Scored object.** The official comparison is the ExECT coded
   inventory under `clinical_headline`. Fork A stays. Fork B (score a
   clinical diary instead) is a different campaign and is still
   uninstrumented.
2. **Two-method difference.** Both lanes name the same units from the
   letter. `llm` fills family-specific fields. Hybrid emits wording +
   evidence only; named rules rewrite, project, and suppress. Hybrid
   may not search the letter for new units. `llm` may not inherit
   hybrid transforms silently.
3. **Exact letter text.** `clinical_name` and `evidence` are substrings
   of the letter, not paraphrases. `clinical_name` is mention wording.
4. **Family scope.**
   - Diagnosis: named epilepsy and seizure types the letter applies to
     the patient, including historical named types gold codes. No
     generic “seizures.”
   - SeizureFrequency: every frequency statement gold codes — current
     rates, dated counts, last-event as zero, seizure-free duration,
     change, ranges, intervals. Generic `seizures`, absences, and
     myoclonic jerks are allowed here. Past control without a
     frequency statement is out.
   - Prescription: **current** ASMs only. Dose required except rescue.
     Missing frequency defaults stay in hybrid (Decision 0021 / 0024).
   - Investigations: completed EEG / CT / MRI **with a result**.
     Pending tests out.
5. **Rate-form table and closed values.** The selected / v26 form list
   is the encoding grammar v10 deleted: point rate including “every 3
   weeks” = 1 / 3 / Week; count range; period range; dated count;
   seizure-free since a date; seizure-free duration; count since a
   point; frequency change. Closed values: TimePeriod Day / Week /
   Month / Year; Since / During; FrequencyChange; PointInTime. The
   `llm` schema must have a place for `period_count` (and the other
   mapped fields). Mention-unit v1 did not.
6. **v9 closed tables in hybrid rewrite.** List 9, List 11, last-event
   → 0, heading split, pending-test drop, prescription defaults. Do
   not retype them into the prompt. Do not replace them with a toy
   projector (v4 damage catalog).
7. **Empty family → nothing.**
8. **Boundaries.** No `test60` inspection. No Decision 0050 change. No
   gold at prompt-build time. One call per method per row. Luna
   `dev20` before any `dev140`. Use `.venv`.

## Vary — experimental components

Change **one** of these per study. Record which one. Do not rename the
schema in the same study that changes scope or examples.

| Knob | Why it is still open | What we already know |
| --- | --- | --- |
| How much of the rate-form table sits in the prompt vs hybrid | v10 proved the model will not invent the grammar. v11–v16 proved hybrid can hold the tables and still lose if the model does not emit the form. v1 omitted `period_count` and could not write “every 3 weeks” | **v2 lock:** eight abstract form rows on `llm` only. Do not omit `period_count`. |
| How we ask for wording-not-sentence | v1 said “exact letter span” and got clauses. “Mention” is our jargon. “Coding fields” is ours too | **v2 lock:** `clinical_name` / `clinical_family`. One concrete leftover-word sentence per prompt. |
| Selection-cue count and wording | Guideline placement said at most seven sentences that decide *what to list* | **v2 lock:** the seven cues in the sign-off. Cue 7 is the only “current.” No eighth second-unit cue. |
| Whether `llm` fills attributes or only wording | Decision 0055 wants `llm` to own semantic parse. Instruction-job note wants `llm` to fill the scored fields | **v2 lock:** family-specific plain rate-form / dose / result / certainty fields. Adapter maps to gold names. |
| Schema envelope | Ledger-with-mentions (`v0.9.24`), clinical-family events (v26), inventory `{family, event, evidence, attributes}` (v4), mention-unit `{family, text, evidence}` (v1) | **v2 lock:** `{clinical_family, clinical_name, evidence}` plus `llm` fields. Later studies may isolate envelope again. |
| Tiny form examples vs none | The 49 letter examples leak gold (EA0004 ≈ example 09). Zero examples left Luna writing `several` | **v2 lock:** the eight-row form table is not a letter example. Couple / few / several only. |
| Hybrid parse depth on the hybrid lane | trust-item showed Investigations/Rx can finish from the event string; SF cannot unless a number sits next to “seizures,” and `suppress_uncoded_sf` deletes Absences/Jerks | **v2 lock:** landed encoder on `clinical_name` + `evidence`. Trust-item is not the method. |

## Hard questions

Answer these in writing before the next live protocol. A protocol that
does not name which question it is for is another circle.

1. **Can the model emit gold wording without extras?** Mention-unit v1
   said no on this pool: gold type wording stayed inside a sentence,
   and empty-gold SF extras rose. If v2 (once corrected) still cannot,
   the leftover is selection, not schema vocabulary. That is a
   different study than “restore `period_count`.”
2. **How much prompt is enough without `v0.9.24` bloat?** We have two
   poles: 84 rules + 49 examples (selected), and seven selection
   sentences + no form table (v1). v19 sat in between and nearly
   matched on `dev20`. The open question is the smallest payload that
   keeps the rate-form table, family scope above, and no letter
   examples. It is not “write a new metaphor for mention.”
3. **Is unread second-unit SF a prompt problem or a one-call limit?**
   EA0009 (cluster-of-seizures unread), EA0016 (dated focal gold left
   uncoded while an extra generic rate is emitted). If the model
   consistently lists one rate and drops the second, more field
   instructions will not find it. That may need a harder selection
   cue, a second pass (out of Decision 0041), or a claim that one-call
   `llm` cannot match hybrid+codebook on multi-unit letters.
4. **Do we still believe hybrid should parse a short wording string?**
   trust-item: hybrid helps 18 `dev140` letters and damages 73, mostly
   because count is empty unless a digit sits next to “seizures.” If
   we keep that projector, we are not testing Decision 0055. If we
   restore the landed SF encoder on mention wording + evidence, we are
   testing the mention-unit job. Say which.
5. **When is Fork B the honest next campaign?** If we keep
   `clinical_headline` and the model cannot name Markup units without
   being taught Markup, the comparison is “how close can a short
   prompt get to a codebook prompt,” not “does a semantic inventory
   help.” Fork B (score the inventory, not the codebook) is the
   alternative. It needs its own scorer and must not be smuggled into
   Fork A as a prompt tweak.
6. **What does “current seizure experience” mean in a model-facing
   sentence?** v9 uses it. We over-read it as current-only. The
   accurate instruction is: extract every seizure-frequency
   **statement** (count, rate, last-event, change, seizure-free
   duration), including past ones; do not extract seizure stories that
   have no frequency. Write that. Do not write “current.”

## What this means for mention-unit v2

This review is signed off. Questions 2, 4, 5, and 6 were answered
before the live run. Question 1 is an **answer** on frozen `dev20`
and a **revise** on `dev140`: gold wording still appears as
`clinical_name` (131/187 exact on `llm`); empty-gold extras rose.
Question 3 stays deferred: EA0009 `cluster-of-seizures` is still
unread; do not add an eighth cue.

## Out of scope

- Changing gold, the selected stack, or Decision 0050.
- Inspecting `test60`.
- Running `dev140` or live Luna calls from this document.
- A new status board or a second representation campaign.
- Transferring any of this to Gan 2026.

## Sources

- v9 extract: [annotation_guidelines_v9_extracted.md](../research/exectv2/annotation_guidelines_v9_extracted.md)
- Guideline vs prompt / zoo drafts (v10–v27): pruned; recover from Git history. Living owners: [Decision 0054](../decisions/0054-model-request-order-and-metadata-are-explicit.md), [prompt variant slots](../research/exectv2/prompt_variant_slots_2026-08-16.md).
- Fork A: [campaign](exect_llm_representation_and_hybrid_revaluation_2026-08-16.md),
  [Decision 0055](../decisions/0055-exect-semantic-inventory-and-method-contracts.md),
  [instruction job](../research/exectv2/prompt_variant_slots_2026-08-16.md),
  [trust-item](../research/exectv2/prompt_variant_slots_2026-08-16.md),
  (mention-unit v1 pruned; recover from Git history),
  [mention-unit v2 protocol](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md)
