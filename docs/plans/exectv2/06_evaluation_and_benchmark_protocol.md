> **Status: HISTORICAL** — design record only. See [`ACTIVE_ROADMAP.md`](../ACTIVE_ROADMAP.md) and [`recent_plan_rationalisation_2026-06-25.md`](../recent_plan_rationalisation_2026-06-25.md).

# Satellite 06 — Evaluation & Benchmark Protocol

Parent: [[00_overarching_implementation_plan]] · Phase 7 (+ governs all phases)
Status: **SF audit executed (2026-06-11, authorized) and first all-entity overall
audit executed for LLM-only (2026-06-12, authorized).** The frozen full-200 SF
audit has been run once per SF architecture (rules / llm_only / hybrid); no
single architecture clears the SF cell (0.66/0.68), best rules at 0.321/0.539.
The all-entity LLM-only audit is contract-clean but not competitive: semantic
overall F1 0.084 per-item / 0.232 per-letter; benchmark with-CUI 0.000/0.000.
Overall audits for hybrid and deterministic all-9 remain future gated work.

Current 2026-06-18 blocker note: the historical authorizations recorded here do
not authorize new full-200/test audits. New ExECTv2 full-200 work is blocked
until `docs/runbooks/gated_blockers_2026-06-18.md` is satisfied, including
benchmark-beating GPT-first dev evidence, explicit user authorization, a
predeclared aggregate readout, and a separate frozen protocol.

**Evidence validity metric (2026-06-27):** canonical definition in
[`docs/reference/evidence_groundedness_metric.md`](../../reference/evidence_groundedness_metric.md).

## Purpose

Define exactly how we score, what counts as "beating the benchmark", how splits
are used, and the authorized procedure for the benchmark-comparable audit. This
is the document a reviewer would check to trust the headline number.

## 1. The target

Published ExECTv2 (Fonferko-Shadrach 2024), validation of the rule-based pipeline
against the consensus gold standard, **with all features**:

- **Overall: F1 0.87 per item, 0.90 per letter.**
- Per-entity per-item F1 (gold): Birth History 0.97, Diagnosis 0.85, Epilepsy
  Cause 0.90, Investigations 0.95, Onset 0.96, Patient History 0.78, Prescription
  0.87, **Seizure Frequency 0.66**, When Diagnosed 0.91.
- **Seizure Frequency per letter 0.68** (the SF lowest; 260 gold annotations) —
  the specific SF bar we track in [[02_rules_based_architecture]].
- Human IAA overall 0.73 (SF 0.47) — context, not the target.

"Beat the benchmark" = exceed **overall** 0.87 per item / 0.90 per letter on the
**same surface the benchmark used (all 200 letters)**, with our gates active.
Per-entity wins (especially SF) are reported but the headline is overall.

## 2. Match policy (pin it, then report sensitivity)

Scoring is label-based (offsets drift). The benchmark-comparable headline is
entity + `normalize_phrase` + **all features** (the paper's "with all features"),
via `MatchConfig(include_attributes=True)`. Three decisions make "all features"
concrete; all are pinned in `exectv2/scoring.py` and exercised by the report
builders:

- **`CUIPhrase` ignored** — it mirrors the annotated phrase, so it is redundant
  with the phrase key (`DEFAULT_IGNORE_ATTRIBUTES`).
- **CUI kept in the headline.** The deterministic family emits CUI from the
  phrase via `deterministic/lexicon.py`, so for SF today CUI is a deterministic
  function of the phrase and the with-CUI / without-CUI scores coincide. We keep
  CUI in the headline (`SF_BENCHMARK`) as the literal "with all features" reading,
  and report the CUI-excluded variant (`SF_SEMANTIC`) as a sensitivity row so any
  future divergence — e.g. an LLM family emitting a different CUI for the same
  phrase — is visible rather than hidden. (This pins the choice the earlier draft
  left the other way; it is score-neutral for the deterministic family today and
  is the user-confirmed headline.)
- **Certainty and Negation excluded for SeizureFrequency.** Guideline v9
  (L17/L19) does not allocate Certainty to SF and excludes SF from Negation; gold
  SF mentions carrying those attributes are annotation noise (SF
  guideline-alignment audit). `SF_BENCHMARK` therefore ignores
  `{CUIPhrase, Certainty, Negation}` and keeps CUI + the semantic attributes. For
  the other entities in Phase 6, each per-entity ignored-attribute set is read
  from that entity's guideline section, not inherited from SF.
- Per-item = every mention (multiset, per-letter, micro-averaged). Per-letter =
  ≥1 correct mention. Both implemented in `scoring.py` (`score_entity`).

The three pinned SF configs **are** the sensitivity table, already rendered
side-by-side by the three-way report:

| Config | Match key | Role |
| --- | --- | --- |
| `phrase_only` (`PHRASE_ONLY`) | entity + phrase | lower bound: phrase recall, no attributes |
| `sf_semantic` (`SF_SEMANTIC`) | + guideline attributes, **CUI dropped** | CUI-excluded sensitivity variant |
| `sf_benchmark` (`SF_BENCHMARK`) | + guideline attributes + **CUI** | **headline** (benchmark-comparable) |

Reporting all three pre-empts the "you picked the lenient policy" criticism: the
headline is the strict, with-CUI cell, shown next to the lenient phrase-only
cell. Phase 6 generalizes the same three-tier shape per entity
(`phrase_only` / `<entity>_semantic` / `<entity>_benchmark`).

**Phase 6 per-entity policy (landed 2026-06-12).** The per-entity ignored-set is
now in code: `scoring.py:benchmark_config_for(entity)` /
`semantic_config_for(entity)`. Each entity ignores `{CUIPhrase}` under the
benchmark config (plus `{CUI}` under semantic); **SeizureFrequency additionally
ignores `{Certainty, Negation}`** as the sole guideline carve-out (D2/D18,
L17/L19). These builders are the single source of truth the all-9 scorer and
runners read — no per-entity ignore-set is hand-transcribed.

**Overall aggregation (Phase 6).** "Overall" F1 = micro-average across entity
cells: per-item sums tp/fp/fn over every mention of every entity; per-letter sums
over every (letter, entity) presence cell (`score_overall` via `sum_prf1` over the
per-entity PRF1s). The per-entity breakdown is reported alongside so a single weak
cell (SF, PatientHistory) is visible, not buried in the micro-average. The
benchmark reports an overall point estimate; we add the breakdown and a bootstrap
CI at audit.

**LLM-only with-CUI caveat (D19).** The LLM-only family emits no CUI, so its
`benchmark` (with-CUI) overall collapses toward 0 on every entity by construction.
Its real quality is the `semantic` (CUI-dropped) overall; both are reported,
leading with semantic. The literal with-CUI 0.87 bar requires the shared
phrase→CUI lexicon extended to all 9 entities — a shared post-step (SF's is
`deterministic/lexicon.py`), flagged as the gating item, not built in the
LLM-only slice.

## 3. Split usage

- **`dev`**: all development, iteration, ablation, prompt tuning. Unlimited reads.
- **`test`**: held out; a single confirmatory read per architecture once dev is
  locked. Authorized.
- **Full-200 frozen audit**: the benchmark-comparable headline. The benchmark
  scored on all 200, so this is the only directly comparable number. Run **once
  per architecture**, after dev is locked, **no tuning against it**, authorized.

The `dev` vs full-200 gap is itself reported (the validation-to-test-gap
discipline from Gan 2026) as evidence of generalization vs overfitting.

## 4. Authorized audit procedure (Phase 7)

Identical in spirit to the Gan 2026 frozen-aggregate audit:

1. Lock all rules/prompts/configs for the architecture under audit; record
   versions.
2. Obtain explicit user authorization for the holdout/full-200 read.
3. Run the locked pipeline over the frozen surface, no row inspection, no
   re-tuning, no repair beyond the standing semantically-neutral ladder.
4. Produce the aggregate report (overall + per-entity per-item/per-letter F1,
   gates, sensitivity table, dev→audit gap).
5. Register the audit run; it is immutable. Any later change requires a new
   authorized audit, not an edit.

## 5. What we report alongside the score

The reliability claim is the score **plus** the gates and trails:

- schema-validity rate, repair rate
- evidence-validity rate (per architecture)
- uncertainty calibration summary
- routed-row taxonomy (hybrid)
- the three-way comparison and the dev→audit gap

A score without these is a benchmark result; with these it is a reliability
result, which is the paper's contribution.

## 6. Statistical care

- Report per-item F1 with a bootstrap CI over letters (the benchmark reports
  point estimates; we add CIs to make the comparison honest).
- For the headline "beat" claim, state the margin and whether the CI clears
  0.87/0.90, not just the point estimate.

## 7. Deliverables & exit criteria

- ~~This protocol, pinned match policy, and split manifest in place~~ — **DONE**:
  policy pinned in `scoring.py` (the three SF configs), split manifest
  `exectv2_split_v1.json` + `load_letters_for_split` (satellite 05 §8).
- ~~Sensitivity + dev→audit-gap reporting wired into the report builders~~ —
  **DONE**: the three-way report renders `phrase_only` / `sf_semantic` /
  `sf_benchmark` side-by-side; the Phase 7 audit runner
  (`runners/run_phase7_audit.py`) adds the bootstrap CI over letters and the
  dev→audit gap columns (see §8).
- ~~Exit (Phase 7): authorized full-200 audit for each SF architecture~~ —
  **DONE for the SF cell** (2026-06-11): rules / llm_only / hybrid each audited
  once over the frozen full-200, registered immutably, with CIs + gap + gates.
  No architecture clears 0.66/0.68 (§8).
- **DONE for the LLM-only all-entity overall slice** (2026-06-12): the all-9
  single-pass LLM-only extractor was audited once over the frozen full-200
  surface with bootstrap CI, dev→audit gap, gates, and per-entity table (§8).
  It does not clear the 0.87/0.90 target.

## 8. Implementation status (2026-06-11)

What of this protocol is already enforced in code, and what waits for the
authorized audit. The split between "policy, now" and "audit, later" is
deliberate: everything that can be pinned and tested on `dev` is, so the Phase 7
read is purely a frozen execution with nothing left to decide.

**Match policy (§2) — DONE and tested.** The three SF configs live in
`exectv2/scoring.py` (`PHRASE_ONLY`, `SF_SEMANTIC`, `SF_BENCHMARK`) with the
`CUIPhrase` / `Certainty` / `Negation` / `CUI` decisions encoded as their
`ignore_attributes` sets and justified in inline comments against guideline v9.
`score_entity` emits per-item and per-letter PRF1 under any config. Covered by
`tests/test_exectv2_scoring.py` (gold-vs-gold = 1.0 under every config).

**Sensitivity table (§2, §5) — DONE for SF.** `reports/three_way_comparison.py`
renders the three configs as adjacent columns for every architecture, against the
published 0.66/0.68 SF cell. The headline column is `sf_benchmark`; the report
header labels it "keeps CUI" so the policy is legible on the artifact itself. The
builder is entity-parameterized for the Phase 6 all-9 table.

**Split usage (§3) — enforced.** Development reads go through `dev` (140 letters)
via `load_letters_for_split`; `load_letters` (full 200) is reserved for the
frozen audit. `test` (60) is untouched. The dev→full-200 and dev→test gaps are
**not yet computable** — only `dev` has been read — so the gap line in §3/§5/§7 is
a Phase 7 deliverable, not a present number.

**Statistical care (§6) — DONE.** `runners/run_phase7_audit.py` computes a
percentile bootstrap CI over letters (5000 resamples, seeded) for the headline
per-item and per-letter F1, and states for each axis whether the CI lower bound
clears the target. CIs are produced only at the audit, not on dev numbers.

**Audit procedure (§4) — EXECUTED for the SF cell (2026-06-11, authorized).**
Locked at git `ab0d8d5c` (zero uncommitted source/test diffs). `run_phase7_audit`
runs the locked pipeline over the full 200-letter corpus (`load_letters`, D16
gold), scores all three configs through the single `score_entity` path,
bootstraps the CI, diffs the dev read for the gap, records the gates, writes an
immutable `experiments/exectv2_audit_*` report, and registers the run
(`decision=historical`, `split=full200_audit`). Run once per architecture, no
tuning against it.

**Result — SF cell, full 200, gpt-4.1-mini for the LLM families (headline =
`sf_benchmark`, with CUI; published target 0.66/0.68):**

| Architecture | phrase_only (item/letter) | sf_semantic | **sf_benchmark (headline)** | headline CI (per-item) | dev→audit (headline item/letter) |
| --- | --- | --- | --- | --- | --- |
| rules | 0.472 / 0.676 | 0.321 / 0.539 | **0.321 / 0.539** | 0.254–0.388 | −0.041 / −0.036 |
| llm_only (per_entity) | 0.463 / 0.677 | 0.122 / 0.246 | **0.000 / 0.000** | 0.000–0.000 | 0.000 / 0.000 |
| hybrid (candidate+assess) | 0.548 / 0.778 | 0.246 / 0.470 | **0.246 / 0.470** | 0.192–0.301 | −0.081 / −0.108 |

Readings:

- **No architecture clears the SF cell** (0.66/0.68) on the with-CUI headline;
  the best is **rules at 0.321/0.539**. This matches the dev story and the known
  SF exact-text noise ceiling (≈26.7% un-winnable; plan 00 §3a).
- **dev→audit gaps are small and negative** for rules and llm_only (full-200 is
  marginally harder than dev — healthy generalization, no overfit). Hybrid's gap
  is larger (−0.081/−0.108): its phrase recall held (phrase_only −0.037/−0.003)
  but its **attribute assignment generalized less well** off dev.
- **llm_only's headline is 0.000 by construction** — it emits no `CUI`, so under
  the user-pinned with-CUI headline nothing matches; its real quality is
  `sf_semantic` 0.122/0.246 and `phrase_only` 0.463/0.677. This is the exact
  CUI-divergence §2 was written to surface (the audit report carries the note),
  realized rather than hypothetical — a finding, not a defect.
- 0 call/parse failures on all live runs; hybrid routed 54/397 with the standing
  taxonomy. Full gates in each `experiments/exectv2_audit_*` report.

**All-entity LLM-only overall audit — DONE (2026-06-12, authorized).**
`runners/run_phase7_audit_overall.py` ran the all-9 LLM-only extractor over
`load_letters()` and scored `score_overall` under semantic (CUI dropped),
benchmark (with CUI), and phrase-only configs. It writes
`experiments/exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.*`
and registers
`exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612`.

Result — full 200, gpt-4.1-mini, all nine entities:

| Config | per-item F1 | 95% CI | per-letter F1 | 95% CI | dev→audit |
| --- | ---: | ---: | ---: | ---: | --- |
| semantic (CUI dropped) | **0.084** | 0.071-0.099 | **0.232** | 0.201-0.263 | 0.087→0.084 / 0.236→0.232 |
| benchmark (with CUI) | **0.000** | 0.000-0.000 | **0.000** | 0.000-0.000 | 0.000→0.000 / 0.000→0.000 |
| phrase_only | 0.147 | — | 0.362 | — | 0.143→0.147 / 0.346→0.362 |

Gate health: `0` call failures, `0` parse/schema failures, `1391/1492`
evidence-valid mentions (`0.9323`). Per-entity semantic item F1 remains far
below the published cells: Diagnosis `0.169`, Investigations `0.324`,
EpilepsyCause `0.032`, PatientHistory `0.011`, SeizureFrequency `0.004`, and
BirthHistory/Onset/WhenDiagnosed `0.000`.

Reading: the LLM-only all-entity single-pass path is structurally reliable but
not competitive. It over-emits broad phrases and misses exact benchmark
phrase/attribute bundles. The benchmark with-CUI score is structurally zero
because the LLM-only slice emits no CUI; semantic is the meaningful quality read
for this architecture.

**Open items:**

1. The `test` split (60) remains untouched; a single confirmatory `test` read is
   available under §3 but was not needed for this SF-cell audit (the full-200 is
   the benchmark-comparable surface). It stays reserved.
2. The **overall all-entity audits for hybrid and deterministic** remain gated on
   building those all-9 architectures. Keep the immutable SF-cell audit runner
   untouched; use sibling/parameterized paths for future overall audits.
