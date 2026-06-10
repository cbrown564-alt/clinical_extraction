# ExECTv2 SeizureFrequency — Guideline Alignment Audit (2026-06-10)

Maps every deterministic SeizureFrequency rule/normalization decision 1:1 to the
ExECT v2.1 annotation guidelines (`ExECT V2 .1- What and How of
annotating_v9.docx`, v9 2023-09-09), and logs every place where (a) our rules
diverge from the guideline, (b) gold diverges from the guideline, or (c) the
guideline is under-specified. Clause references are line numbers in the
extracted text `exectv2_annotation_guidelines_v9_extracted.md`.

This is the SF slice of the broader guideline-alignment workstream (plan 02 §3a
gap 7). The same template extends to the other eight entities.

## 0. Headline implications

1. **Certainty and Negation are out of scope for SF** (clause L17, L19: "We are
   not allocating Certainty to Seizure Frequency…"; "Negation should be assigned
   to all concepts except Seizure Frequency…"). Therefore the benchmark-
   comparable SF match must **exclude `Certainty` and `Negation`** (plus the
   redundant `CUIPhrase`). The single gold SF mentions carrying `Certainty`/
   `Negation` (gold_schema_profile) are **annotation noise, not signal**, and our
   `full_features` config (which requires them) is scoring against the wrong
   target. Action: add a guideline-aligned scoring config
   `sf_benchmark = ignore {CUIPhrase, Certainty, Negation}` keeping `CUI` +
   semantics. This is the config our benchmark comparison should use (the SF bar
   is 0.66 per item / 0.68 per letter, Table 1 Fonferko-Shadrach 2024).

2. **The biggest recall miss is a single mandated default we don't implement:**
   bare plural "seizures" with no quantifier ⇒ `NumberOfSeizures = 2`
   (clause L989). This rescues the most common gold phrase (bare `seizures`),
   which our pipeline currently drops for "no nearby attribute."

3. **The biggest precision miss is also guideline-explicit:** SF anchors are
   *only* seizures / specific seizures / absences / myoclonic jerks; "events,
   episodes, or other slang" must not be annotated (clause L227). Our anchor
   terms include `episodes|events|spells|attacks|auras` → direct FP source.

## 1. Anchor phrases (what is an SF mention)

| Decision | Guideline | Status |
|---|---|---|
| Anchor = seizure-type noun phrase, frequency in attributes | All SF examples L233–L249; Appendix L977+ | **Aligned** |
| Anchor terms include `episodes/events/spells/attacks/auras` | L227 forbids slang; only seizures, specific seizures, absences, myoclonic jerks | **DIVERGENT (our rule)** — restrict SF anchor vocab to {seizure(s), <specific type> seizure(s), absence(s), myoclonic jerk(s)}; drop slang. Note `SEIZURE_TERMS` is shared, so SF needs its own narrower term set, not the general one. |
| Drop anchors with no nearby frequency attribute | L255 "Annotating … without a statement of frequency" is a listed common mistake → drop is correct in principle | **Aligned in principle**, but currently over-drops because the default-count and change/temporal rules below are missing. |
| `seizure-free` as its own anchor | L235–L237 annotate seizure-free as `NumberOfSeizures=0` | **Aligned** |
| Generic seizures vs Diagnosis/PatientHistory boundary | L131: generic seizures with a *person trigger* ("her seizures") → annotate; bare "seizure frequency is…" → ignore; exception after diagnosis triggers like "seizure type and frequency" | **Partially covered** — we have no person-trigger gate; potential FP/precision lever, currently not modeled. Under-specified edge but mostly explicit. |

## 2. Count / rate attributes

| Decision | Guideline | Status |
|---|---|---|
| `N per/each/every period` → NumberOfSeizures=N, NoTP=1 | Appendix L979–L993 | **Aligned** |
| ranges → Lower/UpperNumberOfSeizures | L991–L993; L983–L985 for period ranges | **Aligned** |
| word numbers via `normalize_count` | List 11 L867–L885: single=1, once=1, none=0, a couple=2, a few=2, a number=2, multiple=2, several=3 | **DIVERGENT (confirmed)** — `normalize_count` passes `a couple`/`a number`/`none` through unchanged (invalid as counts) and maps `few`/`several`/`multiple`→the literal string `'multiple'`. Required: a couple/a few/a number/multiple→2, several→3, none→0, single/once→1. |
| **bare plural "seizures" ⇒ NumberOfSeizures=2** | **L989** explicit default | **MISSING (high impact)** — new rule. Singular "a seizure" ⇒ implied 1 (under-specified but implied). |
| "under control"/"well controlled" ⇒ FrequencyChange=Infrequent | List 11 L877–L879 | **MISSING** — new mapping. |
| "completely under control" ⇒ NumberOfSeizures=0 | List 11 L875 | Our `complete seizure control` control-phrase ≈ aligned; widen to "completely under control". |
| medication-dose exclusion ("75 mg twice a day") | not in guideline but correct (Prescription frequency, L973) | **Aligned (defensible)** |

## 3. Temporal attributes (the missing family)

Appendix L1003–L1011 defines for SF: `DayDate` 1–31, `MonthDate` 1–12,
`YearDate` 4-digit, `TimeSince_or_TimeOfEvent ∈ {Since, During}`, `PointInTime`
∈ {This_Year, Last_Year, LastClinic, DrugChange, From_Birth, Surgery,
DischargeDate, LastChristmas, Birthday, Easter, 1960s…2010s}. None are currently
emitted.

| Pattern | Guideline | Rule status |
|---|---|---|
| date "in May" / "in September 2012" → MonthDate/YearDate; month name → number | Ex1 L233, Ex6 L245–L247; Appendix numeric | **MISSING** — normalize month name→1..12. |
| "since the last clinic" → TimeSince=Since + PointInTime=LastClinic | Ex5 L243 | **MISSING** |
| "since starting lamotrigine" → TimeSince=Since + PointInTime=DrugChange + FrequencyChange | Ex4 L239 | **MISSING** — PointInTime=DrugChange from drug-change trigger. |
| **"last seizure was in <date>" ⇒ NumberOfSeizures=0 + Since + date** | L249 "Last seizure in /time period = 0 seizures Since"; Ex6 L245 | **MISSING (high impact)** — a count=0 generator distinct from "seizure-free". |
| `TimeSince` only when a **date or point in time** is present | L231, Ex3 L237 ("5 years ago" → NO TimeSince) | **DIVERGENT (our rule)** — `count_in_last_period` emits `TimeSince=Since` for "in the last 3 months" (a time *period*, not a date/point-in-time) → over-emission. Gate TimeSince on date/PointInTime presence. |
| "in May … but none since" → **During** for the counted month, **Since** for the zero | Ex1 L233; L247 rationale | **MISSING** — During vs Since disambiguation. |

## 4. FrequencyChange

| Decision | Guideline | Status |
|---|---|---|
| Decreased/Increased/Same/Infrequent/Frequent closed vocab | Appendix L987 | **Aligned** |
| "improved" ⇒ Decreased; "worsened" ⇒ Increased | Ex4 L239 ("improved"→Decreased) | **Aligned** |
| under/well controlled ⇒ Infrequent | List 11 L877–L879 | **MISSING** (see §2) |

## 5. Gold-vs-guideline divergences (noise / un-winnable)

These are gold defects to **document, not fit** (transparency artifact):

1. **SF `Certainty`/`Negation` mentions** — violate L17/L19; treat as noise,
   exclude from the SF match (see §0.1).
2. **Stray `DiagCategory="MultipleSeizures"` on SF** (gold_schema_profile) —
   belongs to Diagnosis; noise.
3. **`TimePeriod="days"`** — plural form of `Day`; normalize.
4. **Offset-drift–corrupted gold `text`** — e.g. `'convulsive seizur'`,
   `'seizures e'`, `'ocal seizures with altered awarenes'`, and over-captured
   `'2 generalised tonic clonic seizures in 2014'`, `'seizures since the last
   clinic appointment'`. The guideline says SF text is the *seizure term only*
   (all examples), so these gold phrases are corrupt. A slice of phrase recall is
   **un-winnable on exact phrase text**. Recommend: quantify this slice, and
   consider scoring SF phrase match on a normalized seizure-term key rather than
   the raw (drifted) gold string. Consistent with "score on labels not offsets."
5. **`PointInTime` values `Last_Month`, `Last_Week`** appear in gold but are
   **not in the guideline's PointInTime vocab** (L935/L1011 list only
   `Last_Year`, decades, named events). Guideline under-specifies; gold extends
   it. Accept the gold values; flag the guideline gap.
6. **Guideline internal inconsistency**: Ex1 L233 writes `MonthDate = May` and
   `MonthDate = 5` in the same example; Appendix says numeric 1–12. Canonical =
   numeric.

## 6. Per-statement (multi-mention) requirement

L233 (Ex1) and L241–L243 (Ex5) mandate **multiple SF mentions from one
sentence / one seizure phrase** when multiple time framings are present
("5 seizures in May, but none since" → two; "since last being seen, she had two
seizures in March" → two). Our anchor+association model merges all nearby
attributes onto **one** anchor (`setdefault`), so it structurally cannot emit
these. Confirms plan 02 §3a gap 3: move from one-mention-per-phrase to
one-mention-per-frequency-statement.

## 7. Prioritized rule changes (feeds the temporal-family + CUI work)

Status after the 2026-06-10 batches. Dev per-item F1: phrase 0.313→0.332→**0.356**,
semantic 0.123→0.132→**0.156**; per-letter F1: phrase 0.526→**0.575**, semantic
0.238→**0.313**. Pinned in `test_dev_split_baseline_pinned`.

1. **Scoring** — **DONE**. `SF_BENCHMARK` (ignore CUIPhrase/Certainty/Negation,
   keep CUI) + `SF_SEMANTIC` (also drop CUI) in `scoring.py`; runner + pins use
   them.
2. **Default count** — **DONE**. `_apply_implied_count` in `pipeline.py`: plural
   ⇒ 2, singular ⇒ 1, only when no count/FrequencyChange present. Low yield *so
   far* — gated behind §3 temporal (most bare anchors still drop for no
   attribute); payoff lands with the temporal family.
3. **Anchor precision** — **DONE**. `_SF_ANCHOR_TERMS` in `rules/anchor.py`
   (seizure/absence/jerk only); removed episodes/events/spells/attacks/auras
   from SF anchoring. FP −11.
4. **Temporal family** — **DONE** (`rules/temporal.py`). PIT-since
   (LastClinic/DrugChange/Surgery/Last_*), dates (DMY/MY/M/Y with month-name→num
   and During-vs-Since by preposition), "last seizure was <date> ⇒ 0 Since", and
   "last seizure N <period> ago ⇒ 0, no TimeSince". Plus a bare seizure-count
   rule (`rate.bare_count`), an SF-context gate (date/PIT only fire within ~45
   chars of a seizure noun), and a bare-nonzero-count emit filter (a count with
   no time frame is not an SF mention per L255; gold has 0 such). Net: per-item
   recall 0.118→0.150, per-letter F1 +0.06–0.08. Remaining ceiling is precision
   (SF-vs-Diagnosis and per-statement, items 6/§6).
5. **Word-number mappings** — **PARTIAL**. `normalize_count` now: few/couple/
   multiple/number→2, several→3, none→0 (List 11). Still TODO: "under control"/
   "well controlled" ⇒ FrequencyChange=Infrequent (control-phrase rule).
6. **Per-statement emission** (architectural; larger). **DONE — net-negative,
   reverted.** Splitting a numeric statement from a co-located FrequencyChange
   was measured net-negative on dev (per-item 0.272→0.264) and reverted; the
   single-merged-statement default wins. See D8 and the error-analysis artifact.
7. **CUI lexicon**: SF seizure-term → CUI (16 distinct) for the headline metric.
   **DONE** (`deterministic/lexicon.py`); `sf_benchmark` == `sf_semantic`.

Phase 2 completion batch (2026-06-10) additionally landed: awareness-suffix fix,
range "times"/noun handling, count_in_last_period TimeSince drop (§3), Christmas
⇒ December, "after"/drug-stop point-in-time + date filler + flexible seizure-free
duration, medication-dose/adverbial/non-clinical gates, and the same-sentence
bounded-gap association rule. sf_semantic per-item 0.156→0.272. Still TODO (item
5): "under/well controlled" ⇒ FrequencyChange=Infrequent.

## Method / regeneration

Extract: `uv run python` over the docx zip → `word/document.xml` (see
`exectv2_annotation_guidelines_v9_extracted.md`). Profile cross-check:
`docs/research/exectv2_gold_schema_profile_2026-06-09.md`.
