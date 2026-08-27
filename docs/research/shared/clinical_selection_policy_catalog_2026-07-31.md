# Clinical selection and scoring policy catalog

Date: 2026-07-31  
Status: development reference  
Paper-library role: internal policy reference; not part of the main reading path

Companion: [why the error floor persists](why_the_error_floor_persists_2026-07-31.md)

## Why this document exists

Most remaining disagreements are not “did the system see the sentence?” They
are “which reading counts as correct when the letter supports more than one?”
Those choices are policies. Some live in the gold annotations, some in the
instructions to the model, some in fixed code after the model answers, and
some in the scorer.

This catalog makes those policies explicit. It is for readers who need to
interpret a score, an error, or a residual without reverse-engineering the
pipeline.

It does **not** change gold, scorers, prompts, or rules. It names what the
retained system already does.

## How to read each entry

| Field | Meaning |
| --- | --- |
| **Policy** | The decision rule in plain English |
| **Implication** | What a reader should expect when this policy fires |
| **Where it lives** | Gold convention, model instructions, fixed repair code, scorer, or architecture choice |
| **Helps when** | A concrete case where following the policy matches gold / clinical intent |
| **Hurts when** | A concrete case where the same policy produces a wrong or contested score |
| **Status** | Active in the retained comparison, candidate-only, or archived |

Examples use retained development letters. They are illustrations of the rule,
not a prevalence estimate. Locked test rows were not inspected.

---

# Part A — Gan: one current seizure-frequency label

The Gan task forces a single winner label per letter. When a note contains
several true numbers, something must decide which one survives.

## A1. Typical recurring pattern beats year-to-date total

| | |
| --- | --- |
| **Policy** | If the letter states a usual or typical rate (for example monthly) and also a year-to-date count (“seven so far this year”), prefer the typical recurring rate. |
| **Implication** | Year-to-date diary arithmetic is not automatically “more objective.” The benchmark treats usual pattern as the current burden. |
| **Where it lives** | Gold convention; fixed repair code that overrides an explicit year-to-date selection; model instructions that say “prefer overall totals” can **oppose** this |
| **Helps when** | Letter 2748: gold `1 per month` from “typical pattern is a focal seizure monthly”; year-to-date “seven so far this year” is demoted. |
| **Hurts when** | Letters where the observation total over a named window is what gold wants, and a “usual interval” phrase wrongly wins (for example development regressions where a correct `7 per 6 month` became `1 per week`). |
| **Status** | Active in the finalized Gan repair ruleset |

## A2. Observational rate can win even when seizure status is uncertain

| | |
| --- | --- |
| **Policy** | If the letter gives a countable rate for current episodes, gold may code that rate even when the text says episodes are “under review,” “possible,” or not yet confirmed as seizures. |
| **Implication** | Clinical caution (“these may not be seizures”) is not the same as the scoring convention. Abstaining as `unknown` can be clinically reasonable and still score wrong. |
| **Where it lives** | Gold annotation convention; model instructions that tell the model to abstain on uncertain events push the opposite way |
| **Helps when** | Clinic letters that report phenomenology rates the service is tracking, even before full classification. |
| **Hurts when** | Letter 8419: gold `1 to 2 per week` from nocturnal episodes “under review”; the model answers `unknown` with the same span quoted. |
| **Status** | Active as frozen gold behavior; model-side caution remains a live conflict |

## A3. Ambiguous awareness episodes may be coded unknown, not a rate

| | |
| --- | --- |
| **Policy** | Some letters with countable “episodes of loss of awareness” or similar wording are coded `unknown` in gold rather than as a frequency. |
| **Implication** | Counting is not always enough. The benchmark sometimes withholds a rate when the events’ epileptic nature is soft. |
| **Where it lives** | Gold annotation convention (letter-by-letter; not a single published switch) |
| **Helps when** | Letters where coding a rate would overstate epileptic burden. |
| **Hurts when** | Letter 5491: gold `unknown`; model codes `2 per 6 week` from “two episodes … over the last six weeks.” Opposite of A2. |
| **Status** | Active; contributes to the hard residual band |

## A4. Highest current burden across seizure types

| | |
| --- | --- |
| **Policy** | When several current seizure types appear, select the highest current overall burden, not only the most dramatic subtype. Prefer an overall count when the note gives one. |
| **Implication** | A mild but frequent type can beat a rare severe type. A multi-type total should beat a single-type phrase when both are current. |
| **Where it lives** | Model instructions; gold often agrees but not always when one type’s phrase is vivid |
| **Helps when** | Letters with an explicit overall current count plus a subtype breakdown — overall wins. |
| **Hurts when** | Letter 1880: gold `8 per 2 month`; model locks onto “several times per week” for one semiology and loses the aggregate. |
| **Status** | Active instruction; residual multi-semiology conflicts remain open |

## A5. Seizure-free must not erase ongoing other seizure types

| | |
| --- | --- |
| **Policy** | “No tonic-clonic seizures since review” does not make the letter seizure-free if auras, jerks, or clusters are still occurring. |
| **Implication** | Type-specific freedom is not global freedom. |
| **Where it lives** | Model instructions; deterministic seizure-free distractor filters |
| **Helps when** | Driving or lifestyle text mentions a seizure-free interval while weekly focal seizures continue. |
| **Hurts when** | Over-application turns a true quiet letter into a residual rate, or under-application lets a dated quiet interval become false seizure-free when gold wants `unknown`. |
| **Status** | Active |

## A6. Sustained remission beats older historical counts

| | |
| --- | --- |
| **Policy** | A clear current “seizure-free since [date]” statement should win over older diary counts from earlier months in the same letter. |
| **Implication** | Historical burden is context, not the current label, once remission is established. |
| **Where it lives** | Model instructions; fixed repair guards that preserve seizure-free against diary overwrite |
| **Helps when** | Letter 2932: raw answer correctly kept `seizure free since 29/09/2017`; after the guard, repair no longer replaces it with February/March historical totals. |
| **Hurts when** | Before the guard, repair did exactly that overwrite. Short quiet intervals can still be coded seizure-free when gold wants `unknown`. |
| **Status** | Active finalized repair guard; short-quiet vs unknown boundary still contested |

## A7. Short quiet intervals are not automatically seizure-free

| | |
| --- | --- |
| **Policy** | Days or weeks without seizures, when overall current burden is unclear, should often become `unknown` rather than `seizure free`. |
| **Implication** | Remission is a high bar. Brief quiet spells after recent activity do not clear the ledger. |
| **Where it lives** | Model instructions (especially boundary-focused wordings); gold sometimes still codes seizure-free or a rate |
| **Helps when** | Cuts false long remission claims after a short gap. |
| **Hurts when** | Overshoot: a letter with an ongoing daily rate is answered as long seizure-free because a quiet-since clause was over-weighted. |
| **Status** | Active as guidance; not a perfect match to gold on every letter |

## A8. Dated windowed counts are rates, not “no frequency mentioned”

| | |
| --- | --- |
| **Policy** | Phrases like “two events in three months,” or two named calendar months with events, are countable rates (`2 per 3 month`), not `no seizure frequency reference`. |
| **Implication** | Absence of a smooth “per week” average is not absence of frequency evidence. |
| **Where it lives** | Model instructions; fixed dated-sequence and “N in M months” repair |
| **Helps when** | Letters 14587 and 14628: gold windowed rates; repair recovers them from demotion to no-reference. |
| **Hurts when** | Letters where gold is `unknown` but incidental dated mentions get projected into a rate. |
| **Status** | Active finalized repair |

## A9. Diary month lists can aggregate — with narrow exceptions

| | |
| --- | --- |
| **Policy** | Multi-month diary lines can be summed into `total per span months`, except when the current answer is a protected seizure-free statement or an already-parsable day/week rate. |
| **Implication** | Diary arithmetic is allowed, but not allowed to destroy a clear remission or a clear short-interval rate. |
| **Where it lives** | Fixed repair code (narrow guard after broader diary overwrite hurt holdout totals) |
| **Helps when** | Sparse month-by-month seizure-day logs that need a single current label. |
| **Hurts when** | Broad diary overwrite previously turned correct fortnight rates or seizure-free answers into wrong aggregates; some edge cases remain. |
| **Status** | Active finalized narrow guard |

## A10. Cluster burden needs two parts: how often clusters occur, and how many per cluster

| | |
| --- | --- |
| **Policy** | Cluster answers must use the benchmark’s two-part grammar, for example `2 cluster per 3 week, multiple per cluster`. A bare “2 clusters over 3 weeks” is not enough. |
| **Implication** | Clinically right cluster facts can score as `unknown` until rewritten into the dialect. |
| **Where it lives** | Gold / allowed-label convention; fixed projection that rewrites plural “clusters over/in …” forms; model instructions to keep both sides |
| **Helps when** | Letters 5837 and 10097: clinically clear clusters become scorable after projection. |
| **Hurts when** | Before projection, those same answers collapsed to `unknown`. Singleton “1 cluster per period” without a per-cluster side still becomes `unknown` by design. |
| **Status** | Active finalized projection + singleton guard |

## A11. “One or three” means a range, not the low endpoint

| | |
| --- | --- |
| **Policy** | Countable `N or M per period` is treated as `N to M per period`. |
| **Implication** | Endpoint collapse is a repair bug, not a clinical choice. |
| **Where it lives** | Fixed repair / selected-evidence parsing |
| **Helps when** | Letter 1030: gold `1 to 3 per month` recovered from `1 or 3 per month`. |
| **Hurts when** | Pre-fix collapse to `1 per month` scored a near-correct raw answer wrong. |
| **Status** | Active finalized |

## A12. Trigger-only patterns (sleep deprivation, perimenstrual-only) → unknown

| | |
| --- | --- |
| **Policy** | If seizures are described as occurring only under a specific trigger, without a usable baseline rate, prefer `unknown` (or no frequency reference) rather than inventing a regular rate. |
| **Implication** | Catamenial or sleep-only patterns are not converted into a smooth monthly average unless gold supplies one. |
| **Where it lives** | Deterministic rules path; gold often agrees; menstrual “per cycle” counts are outside the label dialect |
| **Helps when** | “Seizures only when perimenstrual” with no baseline count. |
| **Hurts when** | Letter-class cases where gold still codes a monthly range (for example from “3 to 6 per cycle” language that the dialect cannot parse). |
| **Status** | Active; per-cycle dialect gap remains open |

## A13. Exact fine category match is the primary score; coarse bands are secondary

| | |
| --- | --- |
| **Policy** | Primary Gan accuracy requires the exact fine frequency category. A secondary “Pragmatic” score only asks infrequent vs frequent. |
| **Implication** | Near-misses that a clinician would accept can still fail the primary number. |
| **Where it lives** | Scorer |
| **Helps when** | Distinguishes true band errors from coarse clinical agreement. |
| **Hurts when** | Letter 2748-class: year-to-date vs monthly can be coarse-correct and fine-wrong, so the headline looks like a full miss. |
| **Status** | Active |

## A14. Architecture: the model chooses the reading; repair rewrites the label

| | |
| --- | --- |
| **Policy** | After the model selects events and a final label, fixed code may rewrite that label from the already-selected evidence, but it does not freely re-pick a different clinical reading the way the independent rules-only path can. |
| **Implication** | If the model commits to the wrong competing rate, repair often cannot reach the answer that rules-only would have produced. Hybrid scores can sit below the rules-only comparator for that reason. |
| **Where it lives** | Architecture |
| **Helps when** | Component attribution stays honest: most residual wrongs are selection failures with exact quotes. |
| **Hurts when** | About 514 model-rows in the six-model development panel are rules-correct but hybrid-wrong; 39 of 48 prompt-shared hard wrongs are already rules-correct. |
| **Status** | Active |

---

# Part B — ExECT: facts from four letter sections

ExECT does not force one frequency label. It recovers sets of facts. Opacity
comes from which states, concepts, and regimens are required, and from which
assembly policy is active.

## B1. Active comparison uses thin assembly; richer joint repair is archived

| | |
| --- | --- |
| **Policy** | The retained six-model comparison uses the simpler Diagnosis/Prescription assembly. A richer “joint” repair that reduces many drug and diagnosis regressions exists only as archived replay evidence. |
| **Implication** | Some medication wrongs under the active score are policy debt, not unknown model limits. Enabling joint repair raises overall development F1 by about 0.01–0.02 without changing model rank order. |
| **Where it lives** | Architecture decision |
| **Helps when** | Keeps the published panel simple and hash-stable. |
| **Hurts when** | For one strong model, default assembly moved medication letter wrongs from 13 to 24; joint repair brought them back near 10. |
| **Status** | Default assembly active; joint archived |

## B2. Seizure frequency is a set of states, not one summary

| | |
| --- | --- |
| **Policy** | A letter can require several concurrent facts: active rate for one seizure type, seizure-free for another, and sometimes an explicit unknown when a named type has no usable current frame. |
| **Implication** | Emitting the “main” clinical story can still fail if a required secondary state is missing. |
| **Where it lives** | Gold convention; model instructions; primary internal score keys facts by seizure-type identity plus state |
| **Helps when** | Letters that truly carry different burdens by type. |
| **Hurts when** | Model emits a plausible active-rate + seizure-free pair and drops a required unknown, or merges types. This is the dominant ExECT residual theme. |
| **Status** | Active |

## B3. “Last event / none since …” means seizure-free, not an active rate

| | |
| --- | --- |
| **Policy** | “Last seizure in October 2019” or “no seizures since dose increase” maps to seizure-free with a temporal anchor, not to a recurring yearly rate. |
| **Implication** | Historical dating is remission evidence unless another current count is attached. |
| **Where it lives** | Gold guideline; model instructions; fixed projection that rewrites last-event active-rates to seizure-free |
| **Helps when** | Suppresses “one event years ago” treated as ongoing burden. |
| **Hurts when** | Gold occasionally keeps a historical dated count as active; projection can fight that letter. |
| **Status** | Active |

## B4. “Well controlled” is not bare seizure-free

| | |
| --- | --- |
| **Policy** | Qualitative control language such as “well controlled” maps in gold toward an infrequent / frequency-change reading, not an automatic seizure-free state. Model instructions also reject bare “well controlled” without type and time frame. |
| **Implication** | Control language is a change/quality signal, not always remission. |
| **Where it lives** | Gold guideline; model instructions; fixed recovery of qualitative-change mentions |
| **Helps when** | “Remains well controlled on medication” after a regimen change — credit change/infrequent rather than inventing zero seizures. |
| **Hurts when** | Letters like “completely under control” where gold expects both change and seizure-free, while the model emits only seizure-free — or the reverse. |
| **Status** | Active |

## B5. Empty gold means “not annotated,” not “clinically false”

| | |
| --- | --- |
| **Policy** | If a section has no gold facts, extracting a defensible fact from the letter is not proof the model hallucinated. Empty-gold cases are diagnostic and must not drive prompt success criteria. |
| **Implication** | Apparent false positives on empty sections can be annotation omissions. |
| **Where it lives** | Experiment / claim boundary; gold practice |
| **Helps when** | Prevents tuning the system to under-extract on letters that simply were not annotated. |
| **Hurts when** | Development panels still score those extractions as wrong, so headline error looks larger than clinical falsehood. Examples include EEG mentioned in narrative with empty Investigations gold, or stated rates with empty Seizure Frequency gold. |
| **Status** | Active as interpretation rule |

## B6. Diagnosis often requires split concept inventory, not one paraphrase

| | |
| --- | --- |
| **Policy** | Compound phrases are frequently annotated as multiple atomic concepts (for example refractory epilepsy + focal epilepsy). The model should emit the annotated inventory, not only a clinically adequate summary. |
| **Implication** | “It got the diagnosis” is not enough for the score. |
| **Where it lives** | Gold guideline; model instructions; scorer that matches concept identity (with limited parent/child forgiveness) |
| **Helps when** | “Partial seizures with secondary generalisation” correctly yields both concepts. |
| **Hurts when** | Header names a specific syndrome; model emits broader related terms from the same exact quote and misses the compound syndrome string. |
| **Status** | Active |

## B7. Do not invent generic “epilepsy” from a specific subtype alone

| | |
| --- | --- |
| **Policy** | Prefer the most specific syndrome or type. Add generic `epilepsy` only when the source uses it as a diagnosis, not merely because a subtype implies epilepsy. |
| **Implication** | Specificity beats ontology completion. |
| **Where it lives** | Model instructions; fixed companion-addition disabled |
| **Helps when** | “Symptomatic structural focal epilepsy” alone — no extra generic epilepsy row. |
| **Hurts when** | Gold expects both a specific syndrome and a broader epilepsy tag; the model’s specific-only set fails. |
| **Status** | Active |

## B8. Fixed diagnosis residual additions can rescue or over-add

| | |
| --- | --- |
| **Policy** | After the model answers, fixed code may add diagnosis concepts from source-bound patterns when the concept is missing. Under archived joint repair, additions are skipped if they look redundant with what the model already has (token containment only, not synonym-aware). |
| **Implication** | Default assembly can add useful missing concepts and can also add near-duplicate broader terms. |
| **Where it lives** | Fixed assembly code (default active; redundancy guard archived with joint policy) |
| **Helps when** | Recovers heading diagnoses or phenotypes the model skipped. |
| **Hurts when** | Adds a broader phrase when the model already has a synonymous specific phrase (documented synonym regression pattern). |
| **Status** | Residual additions active; synonym-aware guard not active |

## B9. Current medication beats planned taper language — in principle

| | |
| --- | --- |
| **Policy** | Drugs the patient is taking now are Prescription facts. Future starts, stop plans, and “if further seizures” contingencies are not, unless a separate current statement supports them. Rescue/as-required drugs are a separate lane from ordinary scheduled regimens. |
| **Implication** | “Current lamotrigine, planning to reduce and stop” should keep current lamotrigine. |
| **Where it lives** | Model instructions; scorer future-cue scoping; stronger preserve-current guards only in archived joint assembly |
| **Helps when** | Titration targets without a current dose are excluded; split morning/night unequal doses become separate ordinary rows. |
| **Hurts when** | Under active default assembly, taper language can cause a correct current drug to be dropped. Joint repair restores many of those rows. |
| **Status** | Instruction and scorer active; model-preserving drug guard archived with joint policy |

## B10. Investigations require a result story; planned tests do not count

| | |
| --- | --- |
| **Policy** | Completed tests with result or explicit unknown-result status score. Planned, requested, or awaiting tests should not. |
| **Implication** | Mentioning “MRI arranged” is not an Investigations win. |
| **Where it lives** | Gold guideline; model instructions; fixed noise drops |
| **Helps when** | “EEG showed left temporal discharges” → completed abnormal. |
| **Hurts when** | Model grades result `Unknown` despite text supporting Abnormal, or extracts a defensible EEG when gold left Investigations empty (see B5). |
| **Status** | Active |

## B11. Which seizure-frequency score you quote changes the story

| | |
| --- | --- |
| **Policy** | The internal clinical-fact score keys seizure frequency by seizure-type identity plus a simplified state. A companion “state profile” score asks only which burden states the letter describes, ignoring type identity. A further companion checks whether active-rate magnitudes match. |
| **Implication** | You can look strong on “which states exist” and weak on “exact type + rate,” or the reverse. These must not be collapsed into one accuracy claim. |
| **Where it lives** | Scorer design |
| **Helps when** | Separates representation tax from missed burden. |
| **Hurts when** | Reporting only one number makes ExECT look either harder or easier than the clinical question being asked. |
| **Status** | Active |

## B12. Architecture: one model call owns all four families

| | |
| --- | --- |
| **Policy** | Each letter gets one structured four-family model call. A separate diagnosis-only pass was rejected for cost despite a small diagnosis score loss. |
| **Implication** | Diagnosis specificity errors partly reflect resource architecture, not only instruction quality. |
| **Where it lives** | Architecture decision |
| **Helps when** | Keeps comparison cost and protocol uniform across models. |
| **Hurts when** | Dedicated diagnosis decomposition was slightly stronger on development diagnosis F1. |
| **Status** | Active |

---

# Part C — Cross-cutting interpretation rules

## C1. Exact quoted evidence ≠ clinically correct answer

| | |
| --- | --- |
| **Policy** | Evidence validity only checks that the cited text is an exact contiguous substring of the letter. |
| **Implication** | High exact-evidence rates among wrong answers are expected. They mean the system found text, not that it chose gold’s reading. |
| **Where it lives** | Evidence metric |
| **Helps when** | Separates quotation failure from selection failure. |
| **Hurts when** | Readers treat “exact evidence” as proof the answer is clinically supported. |
| **Status** | Active |

## C2. Representation disagreement is tracked separately from extraction error

| | |
| --- | --- |
| **Policy** | Internal ExECT diagnosis review classifies many disagreements as representation/evaluation issues rather than extraction errors. Sensitivity views may forgive representation rows; they do not replace the primary score. |
| **Implication** | A large share of diagnosis disagreement is “how to write the fact,” not “missed the disease.” |
| **Where it lives** | Review protocol and scoring overlays |
| **Helps when** | Avoids calling every concept mismatch a clinical failure. |
| **Hurts when** | Project triage is not independent clinician validation; borderline calls re-agree only modestly (~60%, κ ≈ 0.40). |
| **Status** | Active as interpretation overlay |

## C3. Further Gan rule tuning is closed without a new study

| | |
| --- | --- |
| **Policy** | The July 2026 Gan repair package (projection, anti-regression, dated counts, competing-rate preference, narrow guards) is the finalized comparison ruleset. |
| **Implication** | New row-specific guards need a predeclared study. The residual is treated as mostly selection/annotation, not missing format rules. |
| **Where it lives** | Research process decision |
| **Helps when** | Stops rules-versus-rules churn that already produced cross-model regressions. |
| **Hurts when** | A few remaining mechanical edges stay unfixed by policy. |
| **Status** | Finalized |

---

# Quick map: where policies live

| Kind of decision | Mostly lives in | Examples |
| --- | --- | --- |
| Which rate is “current” | Gold + model instructions + repair | A1, A4, A8, A9 |
| Uncertain episodes vs rate | Gold (often rate) vs model caution | A2, A3 |
| Seizure-free vs historical activity | Instructions + repair guards + ExECT projection | A5–A7, B3 |
| Required label / concept shape | Gold dialect + projection / inventory rules | A10, A11, B6, B7 |
| Drug current vs planned | Instructions + assembly policy | B9, B1 |
| Empty sections | Annotation practice + claim boundary | B5 |
| What the headline number means | Scorer | A13, B11, C1 |

---

# Using this catalog

1. When a wrong answer has an exact quote, ask which policy above forced the
   fork — do not assume the model “missed the note.”
2. When comparing systems, name the assembly policy (ExECT default vs joint)
   and the score layer (fine vs coarse; clinical-fact vs state profile).
3. When proposing a prompt or rule change, state which catalog entry it
   alters, who benefits, and who is harmed — using the help/hurt pattern
   above.
4. When writing paper claims, treat gold conventions (A1–A3, B2, B4–B6) as
   benchmark policy, not as proof that alternate readings are clinically
   invalid.

## Claim boundary

Development reference synthesized from retained prompts, repair code, scorers,
annotation guidelines, residual analyses, and decision records. Not a change
to any policy, not holdout inspection, and not clinical validation of gold.
