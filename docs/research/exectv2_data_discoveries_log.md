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
**Rules implication.** The anchor+association model merges all nearby attributes
onto ONE anchor (`setdefault`). Per-statement segmentation **was implemented**
(split a numeric statement from a co-located FrequencyChange into two mentions)
**and measured net-negative on dev** (sf_semantic per-item 0.272→0.264,
per-letter 0.482→0.471) — the small upside (~11 candidate mentions) is outweighed
by split-induced FP, so it was reverted. The single-merged-statement default is
the better deterministic operating point on dev. The genuine multi-statement
gold (Ex1/Ex5) is rare (~11/187) and mostly entangled with the offset-drift
noise; it is **not** the dominant ceiling — phrase recall + the gold noise
ceiling (D12) are. See `exectv2_sf_error_analysis_2026-06-10.md` §2.11.
**LLM implication.** Still a natural *advantage* for the LLM (it can split by
clause without the FP cost the rules pay), but given how few gold mentions
actually require the split, expect a small effect; few-shot the Ex1/Ex5 cases but
don't over-weight them.
Status: **firm; per-statement net-negative for rules (measured 2026-06-10).**

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
Status: **firm.** **Caveat (2026-06-10):** the "label" being matched is gold
`text`, which is *itself* the drifted col5 covered span and is NOT reliable (D12);
the reliable clean label is `CUIPhrase` (col6). "Score on labels" only holds once
`text` is repaired to the canonical term — see D16.

### D12 — Gold `text` itself is partly corrupted by the same offset drift `[SF]`
**Discovery.** Some gold SF `text` values are truncated or over-captured because
the stored phrase was sliced by drifted offsets — e.g. `'convulsive seizur'`,
`'seizures e'`, `'ocal seizures with altered awarenes'`, and over-captured
`'2 generalised tonic clonic seizures in 2014'`, `'seizures since the last clinic
appointment'`.
**Evidence.** Row-level error list from `run_deterministic_sf`; contradicts D7
(text should be the seizure term only).
**Rules implication.** ~~A slice of phrase-exact recall is **un-winnable**.~~
**Quantified (2026-06-10, dev):** 37/187 = 19.8% of gold SF phrases are
offset-drift–corrupted (truncations + frequency-embedding over-captures); a
further 13/187 = 7.0% are singular/plural mismatches.
**LLM implication.** The LLM will (correctly) produce the clean seizure phrase and
be penalised against corrupt gold — so the *phrase* component of any score
understates true quality for both architectures.
Status: ~~firm; corrupt slice quantified.~~ **Partly falsified / superseded by D16
(2026-06-10).** The corruption is real but it is **not un-winnable**: the clean
canonical term was present in the gold all along as `CUIPhrase` (MarkupOutput
col6); only `text` (col5, the raw covered span) was corrupt. Repairing
`text:=CUIPhrase` recovers it — and *precision rises*, proving genuine repair, not
loosened matching. The earlier "keep exact match, report a ≈26.7% un-winnable
ceiling" scope decision was wrong; the ceiling was an artifact of matching against
the wrong column. Re-measured on dev: text≠CUIPhrase on **74/187 = 39.6%** of SF
mentions. See D16.

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
accepted miss, don't add rules to reproduce noise. The scorer now performs this
format-only canonicalization on both gold and predictions (2026-07-09); the
frozen corpus itself remains unchanged.
**LLM implication.** These cap achievable F1 a few tenths of a percent; don't
prompt-engineer toward them. Useful as a "ceiling" line in results.
Status: **firm.**

### D16 — The authoritative clean phrase is `CUIPhrase`; gold `text` is the raw covered span `[SF]`
**Column-order scope note (2026-06-17).** The invariant below is right and holds
for every entity — `CUIPhrase` is the clean canonical concept, gold `text` is the
raw offset-covered span — but the **col5/col6 positions are SeizureFrequency-
specific and must not be generalized**. Verified against the raw CSVs: for SF,
col5 = raw span → `text`, col6 = clean term → `CUIPhrase` (the wording below). For
the other seven markup files (BirthHistory, Diagnosis, EpilepsyCause, Investigations,
Onset, PatientHistory, WhenDiagnosed) the order is **flipped**: col5 = clean term →
`CUIPhrase`, col6 = raw span → `text` (e.g. `MakupBirthHist`
`…,C0583275,special-care-baby-unit,Special-care-baby-Unit,…` → `CUIPhrase`=col5,
`text`=col6). Prescription is a third layout: col5=`CUIPhrase`, col6=`DrugName`,
col10 (the full regimen markup span) → `text`. The JSON field mapping the code
reads (`text`=raw span, `CUIPhrase`=clean) is correct throughout; only the physical
column index varies by file (see the all-9 layered error analysis, Finding 1).

**Discovery.** The benchmark's per-entity `MarkupOutput_200_SyntheticEpilepsyLetters/*.csv`
carry **two** phrase columns: col5 = the raw covered span (drifted/corrupt), col6 =
the clean canonical term. The `Json/` builder put col5 → `text` and col6 →
`CUIPhrase` (for SeizureFrequency — column order varies per file, see scope note
above). So the clean phrase D12 called "un-winnable" was in the gold all along,
in a field scoring *ignores*. The published GATE system (F1 0.66 SF) cannot have
been scored on col5; it used col6/offset-overlap.
**Evidence.** `MarkupSeizureFrequency.csv` rows vs `Json/`: e.g. EA0008
col5 `focal-seizures-with-altered-awarenes` / col6 `…awareness` →
JSON `text` / `CUIPhrase` exactly. `CUIPhrase` coverage = 99–100% on all 9
entities (full corpus). SF dev: repairing `text:=CUIPhrase`, **extractor
unchanged**, sf_semantic per-item F1 0.272→**0.362**, per-letter 0.482→**0.575**,
phrase_only per-item 0.382→**0.485**; per-item **precision 0.484→0.615** (precision
*rising* ⇒ genuine repair, not a loosened matcher). Probe:
`experiments/_sf_gold_repair_probe.py`.
**Rules implication.** Score SF against `text:=CUIPhrase`. The remaining gap to
0.66/0.68 is now genuine modeling (recall), not gold noise. Re-pin
`test_dev_split_baseline_pinned`; strike the D12 "un-winnable ceiling" from plan 02
§3a and the SF error-analysis §4.
**LLM implication.** Score the LLM family against the *same* repaired gold or the
comparison is not apples-to-apples; the LLM was being penalised against a column
the benchmark never scored.
Status: **firm (SF, dev, measured 2026-06-10).** Generalization gated by D17.

### D17 — `text` vs `CUIPhrase` divergence is NOT uniform corruption across entities `[all]`
**Discovery.** The col5/col6 gap is a clean-up *only* for SF and Diagnosis. For
the structured entities col6 is an ontology normalization that changes meaning, so
`text:=CUIPhrase` is a per-entity decision, not a blanket repair.
**Evidence.** Full-corpus text≠CUIPhrase rate: SF 37%, Diagnosis 22% (mostly real
typo/over-capture fixes: `focal-seziures`→`focal-seizures`,
`generalised-tonic-chronic`→`…clonic`) **vs** Investigations **90%**, WhenDiagnosed
**82%**, Prescription **71%**. Samples:
- **Investigations** — col6 *encodes the finding*: `EEG`→`abnormal-eeg`,
  `MRI-`→`normal-mri`, `CT-scan`→`abnormal-ct`, inconsistently `EEG-normal`→`EEG`.
  `text:=CUIPhrase` would be **wrong** (extractor emits "EEG", gold becomes
  "abnormal-eeg").
- **Prescription** — col6 is the bare drug concept (`Lamotrigine-200mg-twice-a-day`
  →`lamotrigine`); defensible match basis (dose/freq live in attributes) but a
  semantic decision, and it mixes in real typo fixes (`zobisamide`→`zonisamide`).
- **WhenDiagnosed** — collapses to canonical `epilepsy`; mixes truncation fixes
  with over-capture stripping.
- A few col6 values are themselves bad (`Complex-partial-seizure`→`complex`,
  `cluster`→`seizure-cluster`), so col6 is far cleaner than col5 but not flawless.
**Rules implication.** Apply `text:=CUIPhrase` to **SF + Diagnosis** now;
hold Investigations/Prescription/WhenDiagnosed/EpilepsyCause/Onset/BirthHistory/
PatientHistory for a per-entity review (decide whether the match phrase should be
surface span, col6 canonical, or a finding-aware key). Do **not** blanket-map.
**LLM implication.** Per-entity phrase target differs; the LLM prompt/eval must
match each entity's chosen phrase basis, not one rule for all nine.
Status: **firm (full corpus, 2026-06-10).** **RESOLVED (2026-06-12, Phase 6
LLM-only slice):** the per-entity phrase basis is decided as **repair
`text:=CUIPhrase` for {SeizureFrequency, Diagnosis} only** (CUIPhrase there is a clean
surface-phrase cleanup), and **keep the raw col5 span for the other seven**
(Investigations / Prescription / WhenDiagnosed / EpilepsyCause / Onset /
BirthHistory / PatientHistory). Rationale: for the structured entities col6 is a
*finding/concept normalization* (`EEG`→`abnormal-eeg`, `Lamotrigine-200mg…`→
`lamotrigine`, often a non-substring), so it is not a valid phrase-match target;
matching against it would score the LLM's surface phrase as wrong even when
correct. Cost: phrase recall on Investigations (90% col5≠col6), WhenDiagnosed
(82%), Prescription (71%) is understated against drifted col5 — a documented
ceiling, reported per-entity in the audit (a `text≠CUIPhrase` divergence note),
not silently absorbed. This is now encoded as
`contract/evaluation.py:EntityEvaluationPolicy.phrase_target`, with the loader
consuming that policy rather than carrying its own entity set. A future
finding-aware match key for Investigations
(score against the encoded finding, not the surface phrase) could lift those
cells but is out of scope for the LLM-only slice.

### D18 — Per-entity feature scope: Certainty/Negation apply to all entities except SeizureFrequency `[all]`
**Discovery.** The benchmark "with all features" match includes `Certainty` and
`Negation` for **every entity except SeizureFrequency**. SF is the sole carve-out
(D2). Investigations and Prescription never carry them at all.
**Evidence.** Guideline v9 L17 ("not allocating Certainty to Seizure Frequency"),
L19 ("Negation should be assigned to all concepts except Seizure Frequency"); the
gold profile shows Certainty/Negation populated on BirthHistory, Diagnosis,
EpilepsyCause, Onset, PatientHistory, WhenDiagnosed, absent on Investigations and
Prescription (not in their legal-attribute sets), and noise-only on SF.
**Rules implication.** The deterministic all-9 build must emit Certainty/Negation
for the six entities that take them; omitting them is a guaranteed exact-set miss
(D1).
**LLM implication.** The all-9 prompt must ask for Certainty/Negation on the six
in-scope entities and **must not** ask for them on SF (it will hallucinate
plausible values and tank the exact-set match). Per-entity feature scope, not one
schema for nine.
**Implementation.** Encoded in `contract/evaluation.py` and consumed by
`scoring.py:benchmark_ignore_for(entity)` / `semantic_ignore_for(entity)`
(2026-06-12; centralized 2026-06-17): SF ignores `{CUIPhrase, Certainty,
Negation}`; every other entity ignores only `{CUIPhrase}` under the benchmark
config (plus `{CUI}` under the semantic config). The evaluation policy is the
single source of truth the loader, scorer, and all-9 de-duplication read.
Status: **firm (guideline + profile, 2026-06-12).**

### D19 — Overall F1 is micro-averaged across entity cells; the LLM-only family cannot clear the with-CUI bar by construction `[all]`
**Discovery.** The project headline ("beat overall 0.87 per item / 0.90 per
letter with all features") aggregates across all nine entities. Two facts shape
how the LLM-only slice reports it: (a) overall per-item = micro-average over every
mention of every entity, overall per-letter = micro-average over every
(letter, entity) presence cell — the aggregation chosen for `score_overall`
(`sum_prf1` over the per-entity PRF1s); (b) the LLM emits **no CUI** (D3), so the
with-CUI `benchmark` overall collapses toward 0 on every entity, exactly as the
SF-cell audit showed.
**Evidence.** SF-cell Phase 7 audit: llm_only headline (with CUI) 0.000 while
`sf_semantic` 0.122/0.246 (protocol 06 §8). Full all-entity LLM-only audit
(2026-06-12): semantic overall F1 `0.084` per-item / `0.232` per-letter, while
with-CUI benchmark overall is `0.000` / `0.000`; phrase-only is `0.147` /
`0.362`, confirming nontrivial extraction is erased by the CUI-strict headline.
**Rules/LLM implication.** Report the LLM-only overall under **both** configs,
lead with the CUI-dropped `semantic` overall (its real attribute-level quality),
and state plainly that the literal with-CUI 0.87 bar needs the **shared
phrase→CUI lexicon extended to all 9 entities** (a shared post-step, SF's lives in
`deterministic/lexicon.py`) — a documented gating item, not an LLM-only defect.
The dev→audit gap and per-entity breakdown carry the generalization story
regardless of the CUI headline.
Status: **firm (decided and audited 2026-06-12); aggregation landed in
`score_overall`, gold-vs-gold overall/per-entity behavior is pinned in tests,
and the first all-entity LLM-only full-200 audit confirms the reporting caveat.**

### D20 — The headline collapses same-unit redundant duplicates but preserves distinct-offset duplicates `[all]`
**Discovery.** A letter can carry two-or-more raw gold mentions that reduce to the
*same* headline scoring unit, differing only in a headline-demoted attribute —
a **Redundant-Convention Duplicate** the clinical-recovery headline de-duplicates
and does **not** require the model to reproduce. These are distinct from
**Distinct-Assertion Duplicates** (the same concept at distinct offsets, P5 /
all-9 Finding 3), which the headline **preserves** because the published
offset-based benchmark counts each.
**Evidence.** EA0044 SeizureFrequency carries two `seizures` mentions at the
**same offset 395–403**, both `NumberOfSeizures=0` (seizure-free), differing only
in `PointInTime` (`LastClinic` vs `DrugChange`). `scoring._frequency_state_keys`
keys SF on `(seizure_type, state)` then `dict.fromkeys`-dedups → one unit. Corpus
headline gold vs. raw-mention gold: SF 187→168 (collapse + current-state
suppression); **Investigations 136→136 (no collapse** — distinct-offset EEG
duplicates preserved, e.g. EA0044 EEG at offsets 226 and 770); Diagnosis 405→297;
Prescription 206→193.
**Rules implication.** The redundant-vs-distinct split is per-family: SF collapses
on `(seizure_type, state)`, Diagnosis on the [[Concept Recovery Unit]], Prescription
on the regimen tuple; Investigations never collapses. Keep this keying in
`scoring.py` (one home); do not re-derive it per surface.
**LLM implication.** The model is correct to emit one mention per headline scoring
unit; emitting the redundant `PointInTime` twin earns no headline credit and is not
penalised. Do not few-shot the redundant twin as a target.
**Frontend implication.** A per-letter exploration surface (the Example Explorer)
must report match status and family counts against the headline scoring unit, not
the raw mention multiset — the two disagree exactly on duplicate-bearing letters,
which is why the explorer's `G/P` drill-down contradicted the `headline_target`
chips above it. Redundant-Convention Duplicates are badged "removed from headline
scoring - deduplicated"; Distinct-Assertion Duplicates are badged "distinct
assertion — counted". Tagging is computed in `frontend_review.py` reusing the
scorer keys (single source of truth), not re-implemented in TypeScript.
Status: **firm (EA0044 + dev140 corpus counts, 2026-06-22).**

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

_Next candidate discoveries to confirm: ~~per-entity feature-scope table~~
(DONE — D18); the SF-vs-Diagnosis vs SF-vs-PatientHistory boundary rules (L131);
whether the `Seizure type and frequency:` header reliably bounds SF context; the
SF-vs-PatientHistory/Diagnosis count boundary at the all-9 scale (the LLM must
keep a standalone history count out of SF — D4 — without dropping it from
PatientHistory)._
