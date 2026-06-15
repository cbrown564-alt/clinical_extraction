# ExECTv2 — Ontology-Grounded CUI Normalization (design note)

Date: 2026-06-15
Status: design proposal (dev-only). Secondary priority to the Gan 2026
knowledge-graph work; recorded now so it is ready when ExECTv2 resumes. Not a
holdout authorization. Governed by `docs/design/reliability_thesis.md` and the
Phase gates in `docs/plans/exectv2/00_overarching_implementation_plan.md`.

Related:
- `docs/plans/exectv2/00_overarching_implementation_plan.md` (the 0.87/0.90
  benchmark target; the with-CUI 0.000 cells)
- `docs/plans/exectv2/06_evaluation_and_benchmark_protocol.md` (match policy)
- Existing code: `tasks/epilepsy_phenotyping/exectv2/deterministic/lexicon.py`
  (`SF_CUI_LEXICON`, `assign_cui`), `.../deterministic/normalizer.py`,
  `.../contract/entities.py` (per-entity `closed_vocab`)
- Sibling note: `docs/research/gan2026_kg_grounded_component_generation_design_2026-06-15.md`

---

## 1. The problem this targets

The benchmark-comparable headline is **with-CUI** (the `sf_benchmark` /
benchmark match config keeps `CUI` in the match key). The Phase 7 audits show the
damage this does to any architecture that does not emit codes:

- **LLM-only all-9, frozen full-200 audit: benchmark with-CUI `0.000 / 0.000`.**
  It emits no CUI, so the with-CUI cell is *structurally* zero regardless of how
  good its phrases are (its semantic overall is `0.084 / 0.232`).
- SF cell with-CUI: rules `0.321 / 0.539`, hybrid `0.246 / 0.470`, **llm_only
  `0.000`** (emits no CUI).

The deterministic SF extractor is the *only* path that scores non-zero with-CUI,
and only because `lexicon.py` exists for that one entity. Every gold mention
across the corpus carries a CUI; the all-9 entity set needs codes on all nine
entities and on the LLM-only / hybrid paths, or the headline benchmark number is
capped far below 0.87/0.90 by construction.

This is a **normalization gap, not a reasoning gap** — which is exactly the case
where the external consensus on ontology-grounded LLM pipelines is strongest and
least speculative: resolve extracted surface phrases to a controlled vocabulary
within a fixed ontological boundary, as a deterministic, precision-first,
ablatable step that is *not* the LLM's job to hallucinate.

Current SF dev status after the 2026-06-15 deterministic iteration:

- Deterministic dev140 now reaches `sf_benchmark` per-item P/R/F1
  **0.667/0.749/0.705** (`140/70/47`) and phrase-only **0.714/0.802/0.756**
  (`150/60/37`). `sf_semantic == sf_benchmark`, so remaining SF misses are not
  primarily CUI-limited. The active deterministic strict per-item `>0.7`
  development target is now met on dev140.
- The local Qwen LLM-only dev25 pilot remains worse than deterministic on the
  comparable item surface: phrase-only F1 0.533, semantic F1 0.100, benchmark
  F1 0.000 because no CUI is emitted. Its errors are anchor rewrites and
  attribute/projection drift, not transport failures.
- The local Qwen hybrid dev5 pilot reaches only 0.480 on phrase/semantic/
  benchmark and over-keeps noisy evidence fragments. The useful design lesson is
  that an LLM should select evidence or candidate IDs, while deterministic code
  renders exact ExECTv2 phrases, attributes, and CUI.
- The rule families that closed the strict dev gap were statement-level
  extraction for dated/rate/control statements, projection-aware singular/plural
  aliases, typo-tolerant date normalization scoped to SF statements, and
  precision gates for generic `seizures`/`seizure-free` contexts. The next work
  is robustness/generalization, not CUI normalization. See
  `docs/research/exectv2_sf_item_error_analysis_2026-06-15.md` for item-level
  failure counts and representative examples.

---

## 2. What already exists (the pattern to generalize)

`deterministic/lexicon.py` is a working template for one entity:

- `SF_CUI_LEXICON`: 16 SeizureFrequency CUIs, each mapping to a tuple of observed
  normalized concept-phrase variants, keyed on the gold `CUIPhrase` (44 variants)
  rather than raw mention text — which is what makes it finite and
  near-collision-free.
- Deterministic collision resolution (`_COLLISION_RESOLUTION`) for the two
  truncation-artifact bare tokens.
- `assign_cui(phrase)`: normalizes with the same `scoring.normalize_phrase` the
  scorer uses, and **returns `None` rather than guessing** on an unknown phrase —
  precision-first, the right default.
- Portability tag already declared: `benchmark_format` (a finite ontology lookup
  shaped to the benchmark's annotation conventions, not a general clinical rule).

`contract/entities.py` already encodes the *other* half of the ontology — the
per-entity `closed_vocab` domains (e.g. `FrequencyChange`, `EEG_Type`,
`PrematureBirth`, `DiagCategory`). These are small enumerated controlled
vocabularies the gate already validates against. The CUI lexicon is the missing
companion: the concept-phrase -> code map.

---

## 3. The proposal

**Generalize the finite, gold-grounded phrase -> CUI lexicon pattern from
SeizureFrequency to all nine entities, and wire CUI assignment as a single
deterministic post-extraction normalization step shared by all three
architectures (deterministic, LLM-only, hybrid).**

Three parts:

### 3.1 A per-entity CUI lexicon module

Mirror `SF_CUI_LEXICON` for each entity that carries CUIs in gold. Build each
from a one-shot profile of the 200-letter gold `CUIPhrase` distribution (the same
method that produced the SF lexicon and the entity registry). Keep the structure
identical: CUI -> tuple of normalized `CUIPhrase` variants, explicit
`_COLLISION_RESOLUTION` per entity, `assign_cui(entity, phrase)` returning `None`
on unknown. Tag every lexicon `benchmark_format` and document its gold-coverage
and collision count in the module docstring, exactly as SF does.

### 3.2 A shared, architecture-agnostic normalization pass

A single `normalize_cuis(prediction)` step that, after any architecture emits
phrases, assigns the CUI for each mention's concept phrase deterministically.
This is the literature's "entity normalization to controlled vocabulary"
mechanism, and making it a shared post-step is what fixes the LLM-only `0.000`:
the model is freed from inventing codes (which it does badly), and the code
assignment becomes a reproducible, ablatable lookup. The LLM/hybrid paths keep
owning *phrase* extraction; the lexicon owns *normalization*.

### 3.3 Keep it precision-first and ablatable

- Unknown phrase -> no CUI (never guess), preserving the lexicon's precision, as
  `assign_cui` already does.
- The with-CUI vs phrase-only split stays an explicit, reported ablation
  (`MatchConfig`), so the lexicon's exact contribution is measured, never blended
  into a single number.
- Report per-entity CUI coverage (share of emitted mentions that received a code)
  alongside the with-CUI score, so a low with-CUI cell is attributable to either
  missing phrases (extraction) or missing lexicon entries (normalization).

---

## 4. Discipline, claim type, and honest caveats

Claim type: **deterministic normalization layer**, portability tag
`benchmark_format`. It is prediction-bearing only for the CUI attribute; it does
not touch phrase extraction or any reasoning component.

**Honest caveat 1 — this is benchmark-format grounding, not true UMLS/SNOMED
grounding.** The ambitious version in the literature links phrases to a full
external ontology (UMLS/SNOMED CT) with synonym resolution. The finite gold-CUI
lexicon is deliberately the *first* step: it is precision-first, fully
reproducible, and honestly tagged `benchmark_format`. A later branch could back
it with a real terminology service, but that is not needed to unblock the
`0.000` cell and would add an external dependency and a new error surface.

**Honest caveat 2 — overfitting risk.** A lexicon mined from the 200-letter gold
can memorize that corpus. Mitigations, all already part of the project's
discipline: build lexicons from the **dev split only**, report coverage and
collisions per entity, keep the `benchmark_format` tag visible in every result,
and treat the full-200 with-CUI number as a frozen, authorized audit produced
once — never iterated against. A lexicon entry justified only by a single
dev-split mention should be flagged low-confidence in the module, as the SF bare
tokens already are.

---

## 5. Experiment ladder (dev-only)

Reuse the existing ExECTv2 runner, registry, and `three_way_comparison` report.

1. **SF re-confirm (no new lexicon):** wire the shared `normalize_cuis` pass into
   the LLM-only and hybrid SF paths using the *existing* `SF_CUI_LEXICON`. Show
   LLM-only SF with-CUI moving off `0.000` on dev. This validates the wiring
   before any new lexicon is built — cheapest possible proof.
2. **One new entity:** build the lexicon for the next-highest-CUI-density entity
   (likely Diagnosis or Investigations), report dev with-CUI uplift and coverage,
   and confirm the gate still validates gold-as-prediction at `1.0`.
3. **Remaining entities:** roll out per entity, each with its own coverage and
   collision report. Stop adding an entity's lexicon if its dev coverage gain is
   negligible.
4. **Frozen full-200 with-CUI audit:** only after dev is locked and only with
   explicit authorization, per Phase 7 — produced once, frozen.

## 6. Stop conditions

- **Reject the wiring** if step 1 does not move LLM-only SF with-CUI off `0.000`
  on dev (then the gap is extraction, not normalization, and this note is moot).
- **Stop expanding** to an entity whose lexicon adds negligible dev with-CUI
  coverage — breadth for its own sake is not the goal.
- **Pause** if a lexicon cannot be kept near-collision-free on `CUIPhrase` keys;
  a noisy lexicon that guesses would forfeit the precision-first property that
  makes this defensible.

## 7. Bottom line

The with-CUI cells are zero for the LLM-only path by construction, and the fix is
the least speculative application of the knowledge-graph consensus available to
this project: a finite, precision-first, dev-built, `benchmark_format`-tagged
phrase -> code normalization layer, generalized from the SeizureFrequency lexicon
that already works, and shared across all three architectures so the model never
has to hallucinate codes. It is sequenced after the Gan 2026 component-generation
work but is small, self-contained, and unblocks a benchmark cell that no amount
of phrase-level reasoning can move on its own.

## 8. Deterministic SF follow-through (2026-06-15)

The immediate deterministic-rule iteration confirms an important boundary for
this note: **CUI is not the active cap on the current deterministic
SeizureFrequency score.** The SF phrase -> CUI lexicon already makes
`sf_semantic == sf_benchmark` for deterministic rules. A quick canonical-text
simulation using the CUI lexicon lowered F1, because the benchmark still matches
the annotated phrase surface rather than CUI alone. Therefore the next
deterministic gains have to come from phrase/attribute extraction rules, not from
rewiring CUI assignment.

Implemented rule families, all deterministic and guideline-shaped:

- period-range frequency: `every 3 to 4 weeks` -> `NumberOfSeizures=1`,
  `LowerNumberOfTimePeriods=3`, `UpperNumberOfTimePeriods=4`, `TimePeriod=Week`;
- period-gap frequency: `every five years` / `every year` ->
  `NumberOfSeizures=1` with the corresponding `NumberOfTimePeriods` and
  `TimePeriod`;
- fortnight frequency: `1 per fortnight` -> `NumberOfSeizures=1`,
  `NumberOfTimePeriods=2`, `TimePeriod=Week`;
- header continuation rates: a seizure-type line followed by `1 per week` on
  the next line;
- range-of-type counts: `2 to 3 of her focal seizures` ->
  `LowerNumberOfSeizures=2`, `UpperNumberOfSeizures=3`;
- bare header years: `2 generalised tonic clonic seizures 2014` and
  `absence like seizures 2014` -> dated `During` events;
- bare header month-years: `focal to bilateral convulsive seizures August 2014`
  -> dated `During` events;
- article count events: `a generalised tonic clonic seizure last week` ->
  `NumberOfSeizures=1`;
- standalone point-in-time triggers: `last week` / `last month` / `last year`
  in seizure context -> `TimeSince_or_TimeOfEvent=During`;
- last-event/list temporal variants: `last event October 2019`,
  `last one was on Christmas day 2009`, and `last event 3 years ago`;
- zero/control statements: `has not had any further seizures` and
  `focal seizures are completely under control`;
- statement-level dated/rate composition: `in August, 2017 ... 6-9 seizures
  every week`, `3-4 ... seizures per week from May to August`, and `On Sunday
  and Monday ... generalised tonic clonic seizures`;
- typo-tolerant date statements: `Feburary 6th`, `Novemebr 2015`, and
  seizure-free spelling drift (`seizrue free`) only inside SF statements;
- projection precision filters for bare generic zero mentions, statement-parser
  exact-count artifacts, and over-broad seizure-free aliases;
- follow-up point-in-time trigger: `since my previous phone call` ->
  `PointInTime=LastClinic`, `TimeSince_or_TimeOfEvent=Since`;
- dose-increase drug-change triggers: `since increasing levetiracetam` ->
  `PointInTime=DrugChange`, `TimeSince_or_TimeOfEvent=Since`.

Development result on `exectv2_split_v1` dev140, deterministic rules:

| Config | Per-item F1 | Per-letter F1 | Reading |
| --- | ---: | ---: | --- |
| `phrase_only` | **0.756** | **0.942** | Crosses `>0.7` on the active per-item axis and remains high per-letter. |
| `sf_semantic` | **0.705** | **0.925** | Crosses `>0.7` on strict semantic attributes; equal to benchmark because deterministic CUI is emitted. |
| `sf_benchmark` | **0.705** | **0.925** | Active deterministic strict per-item target is met on dev140. |

Interpretation: this is a **validation development result**, not a new frozen
full-200 audit. It completes the active dev140 deterministic strict per-item
`>0.7` target. The remaining misses still concentrate in exact guideline
attributes, especially `PointInTime`, `TimeSince_or_TimeOfEvent`, and
change/rate splits. The ontology-grounded CUI normalization design remains
valuable for LLM-only and future all-entity paths where CUI is structurally
absent, but deterministic SF's next need is robustness and held-out validation
rather than more CUI normalization.

LLM fallback status from the same iteration:

- OpenAI-backed hybrid pilot with `openai/gpt-4.1` did not execute clinically:
  every call failed with API quota exhaustion, so the resulting zero score is an
  infrastructure failure rather than model evidence.
- Local Ollama `ollama_chat/qwen3.6:35b` hybrid candidate-assessment pilot was
  technically healthy but clinically weak on the 5-letter slice
  (`sf_benchmark` per-item F1 0.48 before deterministic anchor rendering, 0.56
  when existing raw outputs are re-rendered through deterministic candidate
  anchors).
- Local Ollama LLM-only single-pass pilot on the same 5-letter slice reached
  `phrase_only` per-item F1 0.737, but strict `sf_benchmark` was 0.0 before
  adding deterministic CUI/attribute normalization. This suggests the useful
  LLM role may be phrase selection, while exact attributes should remain
  deterministic or verifier-owned.
