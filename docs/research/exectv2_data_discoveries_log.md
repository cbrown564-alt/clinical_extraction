# ExECTv2 — Data & Schema Discoveries Log

Append-only log of **firm, evidence-backed discoveries** about the ExECTv2 data,
gold schema, annotation semantics, and scoring — the things that turned out to be
true once we measured, not what the plan assumed.

**Why this is separate from the architecture plans.** Each discovery constrains
*both* families: we encode it as a deterministic rule **and** we must reason
about it in the LLM runs (prompt instructions, output schema, few-shot choice,
error analysis). Keeping it here, architecture-neutral, stops the same fact being
re-derived per architecture and keeps rules ↔ LLM honest about the same ground
truth.

**Entry contract.** Each discovery is: a one-line claim that is *firm* (backed by
a count or a guideline clause, not a hunch), the evidence, the **rules
implication**, the **LLM implication**, and status. Stable IDs (`D#`); never
renumber. If a discovery is later falsified, mark it ~~struck~~ with why, don't
delete. Clause refs `L#` are line numbers in
`exectv2_annotation_guidelines_v9_extracted.md`; profile =
`exectv2_gold_schema_profile_2026-06-09.md`; SF audit =
`exectv2_sf_guideline_alignment_2026-06-10.md`.

Scope note: most entries so far are SeizureFrequency (the entity under active
work). Tag entries `[SF]`, `[all]`, or `[entity]` as they accrue.

---

## Scoring & schema semantics

### D1 — Match is an exact attribute-set; partial extraction scores zero `[all]`
**Discovery.** `score_entity` matches a mention only when its *entire* non-ignored
attribute set agrees (key and value) with gold — no partial credit. A mention with
the correct count but a missing `PointInTime` is a full miss, not a near-miss.
**Evidence.** `scoring.py:match_key` builds a sorted tuple of all attributes; the
empirically observed collapse of `no_ref` to 0.12 was driven by missing-attribute
misses, not wrong values.
**Rules implication.** A rule family must complete the *whole* gold bundle for a
mention to count; adding one attribute family at a time yields little until the
common bundles are fully covered. Prioritise by *bundle* frequency, not attribute
frequency.
**LLM implication.** The LLM must emit the full attribute bundle per mention; a
model that nails the count but omits temporal framing scores 0. Evaluate the LLM
with the same exact-set metric, and in error analysis attribute misses to the
*missing* key, not just wrong values. Consider an attribute-level (partial-credit)
diagnostic *alongside* the official exact-set score to see where it's close.
Status: **firm.**

### D2 — Certainty, Negation, CUIPhrase are out of scope for SeizureFrequency `[SF]`
**Discovery.** SF mentions do not take `Certainty` or `Negation`; the gold rows
that carry them are annotation noise.
**Evidence.** Guideline L17 ("We are not allocating Certainty to Seizure
Frequency…"), L19 ("Negation should be assigned to all concepts except Seizure
Frequency…"); profile shows 1 `Certainty` + 1 `Negation` SF mention total.
**Rules implication.** Don't emit them; score SF with `SF_BENCHMARK`/`SF_SEMANTIC`
which ignore `{CUIPhrase, Certainty, Negation}`. The old `full_features` config
was measuring against the wrong target.
**LLM implication.** Do **not** ask the model for certainty/negation on SF (it will
hallucinate plausible values and tank exact-set match). The benchmark-comparable
LLM score must use the same ignore set. Per-entity feature scope differs — the
prompt/schema must be entity-specific, not one schema for all nine.
Status: **firm.**

### D3 — `CUI` is the only reference attribute in scope for SF, and nothing emits it yet `[SF]`
**Discovery.** Every SF mention carries a `CUI` (16 distinct); it is in scope for
the benchmark match. No deterministic rule produces it, so `sf_benchmark` is
structurally 0.000.
**Evidence.** Profile (CUI on 187/187); `sf_benchmark` F1 = 0.000.
**Rules implication.** A finite phrase→CUI lexicon (16 values) is the *only* lever
on the headline metric — independent of all recall work.
**LLM implication.** The LLM likely can't reliably produce UMLS CUIs free-hand;
the realistic path is the LLM emits the seizure-term phrase and a shared phrase→CUI
lookup assigns the CUI for *both* architectures. Treat CUI assignment as a shared
post-step, not a per-architecture task.
Status: **firm.**

---

## Annotation semantics (what counts as a mention / value)

### D4 — A count with no time frame is not an SF mention (except 0) `[SF]`
**Discovery.** A bare nonzero `NumberOfSeizures` (no period/date/change/PIT) is
never a valid SF mention; `NumberOfSeizures=0` alone *is* valid (seizure-free with
no stated period).
**Evidence.** Gold: **0** mentions with only a nonzero `NumberOfSeizures`; **3**
with only `NumberOfSeizures=0`. Guideline L255 (don't annotate events without a
frequency statement); L53 ("0 with no time period or point in time").
**Rules implication.** Filter emitted mentions whose only attribute is a nonzero
count (implemented in `pipeline._is_bare_nonzero_count`). This single filter cut
~80 FP.
**LLM implication.** Instruct the model: a frequency statement needs a time frame
(period, date, point-in-time, or change direction); a standalone count in
history/diagnosis prose is **not** SF. This is the SF-vs-PatientHistory/Diagnosis
boundary the model will most often get wrong.
Status: **firm.**

### D5 — Implied count: plural "seizures" ⇒ 2, singular ⇒ 1 when unquantified `[SF]`
**Discovery.** When a frequency statement names "seizures" (plural) with no number,
gold assigns `NumberOfSeizures=2`; singular "a seizure" implies 1.
**Evidence.** Guideline L989 (explicit default). List 11 word-numbers.
**Rules implication.** `pipeline._apply_implied_count` fills it when no count/
change present.
**LLM implication.** Few-shot this default explicitly; models otherwise leave the
count empty (→ exact-set miss) or invent a number. A non-obvious annotation
convention the model cannot guess.
Status: **firm.**

### D6 — SF anchors are seizure / specific-seizure / absence / myoclonic-jerk only `[SF]`
**Discovery.** "Events, episodes, spells, attacks, auras" and generic
convulsions/spasms are **not** SF mentions; only seizures (incl. specific types),
absences, and myoclonic jerks are.
**Evidence.** Guideline L227. Removing slang from the anchor vocab cut FP (115→104).
**Rules implication.** SF-specific anchor term set (`_SF_ANCHOR_TERMS`), distinct
from the shared `SEIZURE_TERMS`.
**LLM implication.** Negative instruction + the slang list; the model will
otherwise label "episodes"/"events" as SF because they're semantically seizures.
Status: **firm.**

### D7 — SF `text` is the seizure-term phrase only; frequency lives entirely in attributes `[SF]`
**Discovery.** The annotated SF span is the seizure-type noun phrase
("seizures", "generalised tonic clonic seizures"); counts/periods/dates/change are
encoded *only* as attributes, never in `text`.
**Evidence.** Every guideline SF example (L233–L249); the anchor+association model
relies on it.
**Rules implication.** Anchor extracts the noun phrase; attribute rules fill the
rest. Confirmed correct by the examples.
**LLM implication.** Output schema must separate `text` (seizure phrase) from the
attribute bundle; a model that puts "3 per month" in `text` mismatches. Don't let
the model echo frequency words into the phrase field.
Status: **firm.**

### D8 — One mention per *frequency statement*, not per seizure phrase `[SF]`
**Discovery.** One sentence / one seizure phrase can yield multiple SF mentions
when multiple time frames are present.
**Evidence.** Guideline Ex1 "5 seizures in May, but none since" → 2 mentions;
Ex5 "since last being seen, she had two seizures in March" → 2 mentions (L233,
L243).
**Rules implication.** The current anchor+association model merges all nearby
attributes onto ONE anchor (`setdefault`) and structurally cannot emit these —
this is the dominant remaining precision/recall ceiling. Needs per-statement
segmentation.
**LLM implication.** This is a natural *advantage* for the LLM (it can split by
clause), but it must be explicitly instructed and few-shot'd, or it will emit one
merged mention like the rules do. A concrete place to expect LLM > rules.
Status: **firm.**

### D9 — `TimeSince_or_TimeOfEvent` only with a date or point-in-time `[SF]`
**Discovery.** `TimeSince` (Since/During) is set only when a date or named
point-in-time is present — NOT for a bare "N period ago".
**Evidence.** Guideline L231; Ex3 "last seizure 5 years ago" → period only, no
TimeSince.
**Rules implication.** Gate TimeSince on date/PIT presence (temporal rules do;
`last_seizure_ago` emits none).
**LLM implication.** Subtle conditional the model will over-apply; instruct + show
the Ex3 counter-example.
Status: **firm.**

### D10 — During vs Since is semantic, not lexical `[SF]`
**Discovery.** "in \<date\>" with a positive count ⇒ `During`; the same "in
\<date\>" under a "last seizure" / "none since" framing ⇒ `Since` (it marks no
events *since* that date).
**Evidence.** Guideline Ex1 (During) vs Ex6/L247 ("last seizure in September 2012"
⇒ Since despite the surface "in").
**Rules implication.** The zero-generating "last seizure was \<date\>" rule sets
Since and wins overlap resolution over the plain date rule.
**LLM implication.** Requires reading the polarity of the surrounding clause —
favourable to the LLM, but a known trap; include both framings in few-shot.
Status: **firm.**

---

## Data quality & vocab drift

### D11 — Gold offsets are unreliable; score on labels, not spans `[all]`
**Discovery.** Spelling was corrected in the letters *after* annotation without
updating character offsets, so gold `start/end` drift against `note_text`.
**Evidence.** Established Phase 0 (user-confirmed); `data.py` docstring; gold-vs-
gold label match = 1.0 while offsets disagree.
**Rules implication.** Match and evidence-check on normalized labels, never
offsets.
**LLM implication.** Don't ask the model for character offsets and don't score
them; evidence-substring checks must be offset-free (verbatim-substring, not
index-based).
Status: **firm.**

### D12 — Gold `text` itself is partly corrupted by the same offset drift `[SF]`
**Discovery.** Some gold SF `text` values are truncated or over-captured because
the stored phrase was sliced by drifted offsets — e.g. `'convulsive seizur'`,
`'seizures e'`, `'ocal seizures with altered awarenes'`, and over-captured
`'2 generalised tonic clonic seizures in 2014'`, `'seizures since the last clinic
appointment'`.
**Evidence.** Row-level error list from `run_deterministic_sf`; contradicts D7
(text should be the seizure term only).
**Rules implication.** A slice of phrase-exact recall is **un-winnable**. Consider
scoring SF phrase match on a normalized seizure-term key rather than the raw gold
string; quantify the corrupt slice as a noise ceiling.
**LLM implication.** The LLM will (correctly) produce the clean seizure phrase and
be penalised against corrupt gold — so the *phrase* component of any score
understates true quality for both architectures. Report a corrupt-gold-adjusted
number, and don't tune prompts to reproduce corruption.
Status: **firm; needs the corrupt slice quantified.**

### D13 — Closed vocabularies drift: gold extends the guideline's enumerations `[SF]`
**Discovery.** Gold uses `PointInTime` values `Last_Month`, `Last_Week` that the
guideline's List 4 / Appendix never enumerate (they list only `Last_Year`,
decades, named events).
**Evidence.** Profile (PointInTime values) vs guideline L935/L1011.
**Rules implication.** Closed-vocab validation must accept gold-observed values,
not just guideline-listed ones (the registry already widens some).
**LLM implication.** Give the model the *gold-observed* value set, not the
guideline list, or correct-but-unlisted predictions get marked invalid.
Status: **firm.**

### D14 — Known annotation-noise rows (accept, don't fit) `[SF]`
**Discovery.** A handful of gold rows violate the schema: `TimePeriod="days"`
(plural of Day), stray `DiagCategory="MultipleSeizures"` on SF (×2), `CUIPhrase`
case/format variants.
**Evidence.** Profile "Annotation noise summary"; SF audit §5.
**Rules implication.** Normalize where safe (`days`→`Day`); otherwise leave as an
accepted miss, don't add rules to reproduce noise.
**LLM implication.** These cap achievable F1 a few tenths of a percent; don't
prompt-engineer toward them. Useful as a "ceiling" line in results.
Status: **firm.**

---

## Distributional facts (shape the work, not strictly schema)

### D15 — 41% of SF mentions carry a temporal attribute; a few bundles dominate `[SF]`
**Discovery.** 76/187 dev SF mentions carry ≥1 of PointInTime/date/TimeSince. The
dominant gold semantic bundles are `(count, period)` 58, `(FrequencyChange)` 26,
`(count, PointInTime, Since)` 25, `(range, period)` 17, `(count, MonthDate,
YearDate, Since)` 13, `(count, YearDate, Since)` 11.
**Evidence.** Dev-split bundle analysis 2026-06-10.
**Rules implication.** Cover the top ~6 bundles fully (exact-set, D1) before
breadth; that's where the F1 is.
**LLM implication.** Use these bundles to choose few-shot examples (cover the head
of the distribution) and to weight error analysis. The long tail of rare bundles
is where neither architecture will pay off quickly.
Status: **firm (dev split).**

---

_Next candidate discoveries to confirm: per-entity feature-scope table (which of
Certainty/Negation/CUI apply to each of the 9 entities); the SF-vs-Diagnosis vs
SF-vs-PatientHistory boundary rules (L131); whether the `Seizure type and
frequency:` header reliably bounds SF context._
