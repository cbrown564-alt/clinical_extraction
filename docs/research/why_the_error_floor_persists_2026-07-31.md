# Why the error floor persists on Gan and ExECT

Date: 2026-07-31  
Status: development synthesis from retained artifacts  
Method: parallel audit of residual analyses, attribution panels, annotation
reviews, scoring code, and deterministic-rule studies. No new model calls. No
locked-test row inspection.

## Plain answer

The remaining errors are mostly **not** missing quotes, broken normalizers, or
forgotten prompt instructions. Across both tasks, the model usually finds the
right sentence. It then has to make a **forced clinical choice** that the note
does not uniquely determine: which rate is “current,” whether uncertain episodes
count as seizures, whether a quiet interval means seizure-free, which diagnosis
phrase is the official label, which drugs are “current.” The gold answer picks
one convention. Exact-match scoring demands that same pick.

Prompt wording moves a modest fringe. Deterministic repair rescues a large
mass of format and aggregation mistakes, and also creates a smaller set of
regressions. After both levers, a hard core remains that looks “easy” to a
human reader because the human tolerates ambiguity that the benchmark does not.

Rough ceilings under current gold and scorers (development evidence):

| Track | Rough best final score | What still fails |
| --- | --- | --- |
| Gan seizure-frequency label | ~85–90% exact category match | Competing rates, uncertainty boundaries, label-shape brittleness |
| ExECT four-family fact recovery | ~0.80–0.89 F1 on development; ~0.72–0.80 on locked test totals | Seizure-frequency state sets, diagnosis granularity, some drug-policy rule harm |

Those numbers are not a mysterious intelligence wall. They are the product of
**task definition + annotation convention + model selection**, with a thinner
layer of mechanical pipeline friction.

---

## What the two tasks actually ask

### Gan: one current frequency label per letter

The system must emit a single canonical frequency string, such as
`1 per month` or `3 cluster per month, multiple per cluster`. Scoring then
maps that string into a fine category band (the strict “Purist” score) or a
coarser frequent/infrequent band (the looser “Pragmatic” score).

A letter often contains several true numbers. The task still wants **one**
winner.

### ExECT: several facts from four letter sections

The system must recover facts about diagnosis, seizure frequency, medication,
and investigations. Seizure frequency is not one label: gold often expects a
**set** of states for different seizure types (active rate, seizure-free,
unknown). Diagnosis often expects a **specific inventory** of concept phrases,
not a clinically adequate paraphrase.

A casual reader can summarize a letter correctly and still fail the score.

---

## Claim 1: “The model can’t find the evidence” — mostly false

On the hardest Gan residual set for one strong model (48 letters wrong under
three different instruction wordings after repair), **all 48** still quote an
exact substring of the note. Among all final wrongs for that model, exact
quotes remain on roughly 95–98% of rows.

On ExECT development letters for the same model, roughly nine in ten wrong
letters still carry exact evidence.

So the residual is not a retrieval problem. The model finds text. It fails at
**which reading to commit to** and **how to render that reading into the
required structured form**.

---

## Claim 2: “Normalization and scoring are solved” — partly false

The scorers largely do what they are designed to do. That is not the same as
measuring the clinical question a human thinks they are answering.

### Fine bands punish near-misses that humans would accept

On Gan, about 3% of development rows are wrong under the strict category score
but right under the coarser clinical band. Inside the 48-letter hard core,
roughly a quarter are “close enough” under the coarse score for at least one
instruction wording.

Example (development letter): gold is `1 per month` because the note says the
typical pattern is a monthly seizure. The model instead codes
`7 per 10 month` from “seven … so far this year.” Both numbers are in the
letter. The coarse score accepts the year-to-date reading; the fine score does
not.

### Required label shape can turn a right fact into “unknown”

Example: the note says “two myoclonic clusters over the past three weeks.”
Gold wants a two-part cluster label:
`2 cluster per 3 week, multiple per cluster`.
The model says `2 clusters over 3 weeks` — clinically right, grammatically
off the dialect. Repair then collapses the answer to `unknown`.

A later mechanical floor rewrote many of these plural-cluster phrases into the
required form and recovered those rows. That proves an earlier slice of the
“irreducible” floor was pipeline brittleness, not clinical mystery. It also
shows why “scoring is fine” overstates things: the scorer only sees the final
string after repair.

### Different ExECT scores answer different questions

For the same outputs, published phrase matching, concept-identifier matching,
and the internal clinical-fact score can differ by large margins. Inside
seizure frequency alone, recovering the **state** (active / free / unknown)
can look strong while recovering the **exact rate magnitude** looks much
weaker. Collapsing these into one “accuracy” story hides where the floor
really is.

### A few gold fields are mechanically wrong

Retained issue records name three open field conflicts (wrong drug name versus
span, a literal null concept identifier, a time-period that contradicts the
quoted sentence). These should be cited individually. They do not explain a
corpus-wide error rate, but they do mean some scored “errors” are not model
mistakes.

**Verdict:** scoring/dialect/repair issues are a **meaningful minority** of the
remaining floor (roughly on the order of 15–30% of the hardest Gan core before
or around the July mechanical floors), not the main story after those floors.

---

## Claim 3: “We know the instructions, so the model should obey them” — false

Error analysis correctly named the hard themes: competing rates, seizure-free
boundaries, cluster structure, diagnosis specificity. The prompts already
encode those themes, and later wordings restated them in plainer language.

What happened:

- On Gan development, three instruction wordings moved final exact-match
  accuracy by roughly 20 letters out of 750. A shared hard core of **48**
  letters stayed wrong under all three. On **35** of those 48, all three
  wordings produced the **same final label**.
- On ExECT development, restating seizure-frequency boundaries recovered only
  a handful of letters. Overall score movement was tiny. The locked-test
  aggregate gains were similarly small.

Instructions can name a convention. They cannot make the model stably choose
that convention when the note supports another reading that is also
clinically plausible — especially when different instruction tweaks trade one
error type for another.

Example of an instruction conflict: telling the model to “prefer overall
period totals” helps some diary letters and hurts letters where gold prefers
the stated typical monthly pattern. Prompt tuning is not a free climb toward
gold; it rearranges the margins.

---

## Where the residual actually lives

### Gan: three stacked ceilings people conflate

1. **Model-only ceiling (~55% exact match for a strong model).** Before
   deterministic repair, hundreds of answers are wrong. The model quotes well
   and selects poorly among competing facts.
2. **Model-plus-rules ceiling (~86–90%).** Repair lifts most format,
   aggregation, and many rate-construction mistakes. Best post-floor
   development scores approach about 90%.
3. **Rules-only comparator (~93%).** A pure deterministic path with no model
   already gets about 697 of 750 development letters right. That caps absolute
   performance under current gold: even a perfect deferral-to-rules system
   would still miss about 7%.

The uncomfortable fact: every hybrid model in the six-model development panel
scores **below** the rules-only comparator on the same letters (by roughly
30–80 letters depending on model). Of 608 wrong finals in the frozen
attribution panel, about **87%** are first owned by model clinical selection,
not by scoring arithmetic.

Among the 48-letter prompt-shared hard core, **39** are already correct under
rules-only. Calling those “irreducible clinical hardness” is incomplete: the
clinical fact is recoverable without the model; the hybrid path fails to
deliver it because it over-trusts the model’s chosen reading.

### ExECT: error mass by letter section

For the best-dissected strong model under the active assembly policy:

| Letter section | Approx. wrong letters (of 140) | Who owns it |
| --- | ---: | --- |
| Seizure frequency | ~52 | Almost entirely the model’s state construction |
| Diagnosis | ~49 | Model specificity + representation conventions |
| Medications | ~24 | Often deterministic repair under the active policy |
| Investigations | ~15 | Model interpretation; rules barely touch |

Seizure frequency barely moves when deterministic projection runs
(54 → 52 wrong letters in the residual map). Medications can look strong at
headline F1 while the active repair policy **turns some correct model drug
lists into wrong finals** (about 13 → 24 wrong letters for that model). A more
complex joint repair policy recovers many of those drug and diagnosis rows
(+0.01 to +0.02 overall F1) but was demoted because the gain did not justify
the complexity for the retained comparison. That means part of the ExECT
“floor” under the active policy is a **chosen policy tradeoff**, not an
unknown model limit.

---

## Failure modes with examples a non-specialist can follow

### 1. Two true rates; gold picks one

**Note contains:** “typical pattern is a focal seizure monthly” and “only
seven … so far this year.”

**Gold:** monthly pattern.  
**Model:** year-to-date total.  
**Why it feels unfair:** both readings are in the letter. A clinician could
defend either depending on the question asked (“usual pattern” vs “burden this
year”). Exact-match scoring cannot.

### 2. Uncertain episodes vs coded rates

**Note contains:** “persisting nocturnal episodes under review,” with informal
weekly cues.

**Gold:** `1 to 2 per week`.  
**Model:** `unknown`, because the episodes are not confirmed seizures.  
**Why it matters:** the model is clinically cautious. Gold encodes the
observational rate anyway. This is a **policy disagreement**, not a missed
sentence.

The reverse also happens: gold codes `unknown` for ambiguous awareness
episodes, while the model turns “two episodes … over six weeks” into
`2 per 6 week`.

### 3. Seizure-free vs historical counts

**Note contains:** a clear “seizure-free since [date]” statement and older
counts from months earlier.

**Model (raw):** correctly chooses seizure-free.  
**After repair (pre-floor):** historical counts overwrite the correct answer.  
**Why it matters:** some “model errors” in final scores were actually
deterministic overwrites. Floors fixed the clearest shared cases and then
introduced smaller new regressions elsewhere — the classic rules-vs-rules
tradeoff.

### 4. Cluster structure vs smooth rate

**Note contains:** clusters on several evenings per fortnight, roughly five
spells per cluster.

**Gold:** a two-part answer (how often clusters occur × how many per cluster).  
**Model:** collapses to something like `multiple per week`.  
**Why it matters:** the clinical burden was noticed; the required structure was
not assembled.

### 5. ExECT multi-state profiles

**Note contains:** ongoing seizures every two weeks for one type, and a
different type last seen years ago, with incomplete current detail for a third.

**Gold:** active-rate + seizure-free + sometimes an explicit **unknown** slot.  
**Model:** a plausible subset (active + free), dropping unknown or merging
types.  
**Why a skimming human “succeeds”:** humans summarize. The benchmark wants the
full annotated state set.

### 6. Diagnosis: paraphrase that is clinically right, inventory-wrong

**Header-like text:** genetic generalised epilepsy — epilepsy with generalised
tonic clonic seizures alone.

**Gold:** includes the full syndrome phrase.  
**Model:** emits broader `epilepsy` plus related terms, with an exact quote of
the same line.  
**Internal review split:** missing the specific syndrome can be tagged as a
representation issue; adding an unsupported broad `epilepsy` can be tagged as a
true extraction error. Same letter, mixed verdict.

### 7. Medications: current vs taper language

**Note:** “Current … lamotrigine 75mg bd (to reduce and stop as detailed
below).”

**Model:** correctly keeps current lamotrigine.  
**Active repair:** may drop it because taper language appears.  
**A stricter joint repair:** restores it.  
**Why it matters:** this class of residual is assembly policy, not missing
prompt text.

### 8. Empty gold with a defensible extraction

**Note mentions:** EEG confirmation of epileptic activity, or “has not had any
… seizures.”

**Gold:** no investigation or frequency annotation.  
**Model:** extracts EEG performed or seizure-free.  
**Score:** wrong.  
**Why it matters:** empty gold means “not annotated,” not “clinically false.”
These inflate apparent error if treated as ordinary model mistakes.

---

## How much of the floor is annotation / task definition?

Enough that exact-match scores systematically understate clinical agreement —
and not so much that models are “done.”

### ExECT diagnosis review (246 concept disagreements on development)

| Review decision | Rows | Share |
| --- | ---: | ---: |
| Representation / evaluation issue | 173 | ~70% |
| Extraction error | 72 | ~29% |
| Uncertain | 1 | <1% |

Sensitivity views that forgive representation rows raise diagnosis agreement
dramatically (hybrid diagnosis can move from ~0.90 toward ~0.98 in the
conservative reinterpretation). Those are **reinterpretations of saved
outputs**, not corrected benchmarks, and most triage decisions were
pattern-assisted rather than independent clinician adjudication.

A blind re-review of borderline cases agreed only about **60%** of the time
(κ ≈ 0.40). Soft boundaries are real; project judgments are not highly
reproducible on close calls.

### ExECT seizure-frequency historical review (53 disagreements)

About **72%** were annotation mismatch, redundancy, or ambiguity; about
**28%** were genuine model error. An internal “clinically defensible” view
rose from ~62% exact agreement to ~89% — historical sensitivity evidence, not
validation.

### Gan hard core

Of 48 persistent wrongs: exact evidence on all; rules-only already correct on
39; only 9 jointly hard for both model and rules. The dominant themes are
competing formulations, uncertainty boundaries, and structure choice — exactly
where two careful readers can disagree.

**Do not conclude** that remaining error is mostly annotation noise. Real
extraction errors remain (negation-as-diagnosis, wrong event choice, omitted
rates, investigations graded Unknown instead of Abnormal). **Do conclude** that
a large explainable share of the apparent ceiling is the gap between
human-tolerant reading and a strict, convention-bound structured contract.

---

## Why deterministic rules cannot close the rest

Rules are essential and nearly exhausted as a safe lever.

On Gan development across six models, repair produced about **1,607**
wrong-to-correct transitions and only **29** correct-to-wrong transitions in
the frozen panel — huge help, rare direct harm. But on **514** model-rows the
independent rules path is correct while the hybrid final is wrong, usually
because the model locked onto the wrong event and repair could not (or would
not) override that selection. Later mechanical floors recovered more
format/dated-count/competing-rate cases and also created new regressions on
other letters. Further rule tuning was closed after cross-model harm appeared.

On ExECT, seizure-frequency projection is comparatively safe and still leaves
a large model-owned remainder. Diagnosis and medication rules both rescue and
regress. Every bounded candidate that tried to eliminate regressions while
keeping rescues failed a predeclared gate. The joint policy that reduces those
regressions was demoted for complexity versus a ~1–2 point F1 gain.

```
Note with several true facts
        │
        ▼
Model picks one reading + quote     ← dominates residual
        │
        ▼
Deterministic repair / projection   ← rescues format; can overwrite
        │
        ▼
Exact-match against gold convention ← punishes alternate defensible readings
```

More rules can patch grammar. They cannot safely re-decide clinical selection
on every letter without hurting other letters.

---

## Why the tasks “don’t seem that hard”

Because everyday clinical reading and the benchmark are different jobs.

| Everyday reading | What the score demands |
| --- | --- |
| “About monthly” | One exact canonical string and fine category band |
| “Pretty much seizure-free lately” | Seizure-free vs unknown vs residual rate, with dating rules |
| “Has genetic generalised epilepsy” | Exact concept inventory, including compound syndrome phrases |
| “On lamotrigine, planning to stop” | Current vs planned vs rescue ontology |
| “EEG confirmed epilepsy” | Whether investigations were annotated at all; result ternary |
| One summary per letter | Multiple concurrent frequency states per seizure type |

Humans succeed by compressing ambiguity. The evaluation succeeds by matching a
specific annotated reading.

---

## What else to consider (beyond more prompt tuning)

1. **Treat selection as the product problem.** The dominant residual is choosing
   among competing supported facts. Architecture that can compare candidates
   (or defer to a rules path when the model is uncertain) matters more than
   another paragraph of instructions.
2. **Report multiple score layers honestly.** Fine exact match, coarse clinical
   band, set-based state recovery, and representation-sensitive diagnosis views
   answer different questions. The “ceiling” depends on which question you ask.
3. **Make competing-rate and uncertainty policy explicit.** If gold prefers
   typical pattern over year-to-date totals, or observational rates over
   diagnostic caution, that is benchmark policy. Document it as such rather
   than treating model caution as stupidity. See the
   [policy catalog](clinical_selection_policy_catalog_2026-07-31.md).
4. **Accept that empty or multi-annotated gold needs separate accounting.**
   Empty-gold extractions and multiplicity conventions should not drive prompt
   success criteria as if they were ordinary false facts.
5. **Use human review for the hard band, not more auto-rules.** Competing-rate,
   seizure-free boundary, and diagnosis-granularity letters are exactly where
   internal agreement is weakest. A review queue beats another brittle guard.
6. **Consider changing the question for some use cases.** “List supported
   burden states with evidence” or “selectively abstain when seizure status is
   unconfirmed” may be more clinically useful than forcing one Purist winner.
7. **Keep mechanical floors, stop expecting them to finish the job.**
   Format-tolerant projection was real progress. Safe remaining mechanical
   gains look small and regression-prone.
8. **Independent clinical adjudication before “clinically equivalent” claims.**
   Project triage shows many disagreements are representation-shaped; it does
   not validate those alternatives as clinical truth.

---

## Bottom line

The threshold feels low because three different stories were collapsed into one
number:

1. **The model is a weak stable selector** among several true facts in one
   letter (~55% alone on Gan; large seizure-frequency remainder on ExECT).
2. **Deterministic repair and label dialect** create a second story —
   historically a bigger mechanical floor than it looked, now mostly patched,
   with residual over/under-correction.
3. **Gold and scoring encode conventions** that notes do not uniquely
   determine, so exact-match accuracy saturates below human “that’s basically
   right.”

Prompt optimization can still win small, real gains on the margins. It will
not dissolve the hard core, because the hard core is largely
**disagreement-under-ambiguity**, not missing instructions. The useful next
moves are clearer task/policy definition, multi-layer evaluation, selection
architecture, and human review of the ambiguous band — not another round of
hoping the model will finally internalize every convention the project has
discovered.

## Claim boundary

Development mechanism synthesis from retained Gan and ExECT artifacts. Not
holdout row analysis, not clinical validation, not a claim that sensitivity
views replace primary scores, and not permission to reopen closed rule-tuning
without a predeclared study.

## Evidence owners

- [Gan Luna residual analysis](gan2026_luna_prompt_variants_residual_analysis_2026-07-31.md)
- [Gan projection / anti-regression floors](gan2026_luna_projection_antiregression_floor_report_2026-07-31.md)
- [Gan dated-count / competing-rate floors](gan2026_luna_dated_count_competing_rate_report_2026-07-31.md)
- [ExECT Luna residual map](../experiments/exectv2/reliability/exectv2_luna_single_call_dev140_residual_map_2026-07-31.md)
- [ExECT annotation-evidence synthesis](../experiments/exectv2/reliability/exectv2_annotation_evidence_synthesis_2026-07-15.md)
- [Scoring canon](../canon/04_scoring.md)
- [Six-model comparison](six_model_comparison_report_2026-07-18.md)
- [Decision 0045 (default vs joint ExECT policy)](../decisions/0045-exect-default-policy-not-joint-combined.md)
- Machine artifacts under
  `experiments/gan2026_luna_prompt_variants_dev750_20260730/`,
  `experiments/gan2026_matched_v05_dev750_attribution_20260727.json`,
  `experiments/gan2026_six_model_current_floors_replay_20260731/`,
  and `experiments/exectv2_luna_single_call_dev140_residual_map_20260731/`
