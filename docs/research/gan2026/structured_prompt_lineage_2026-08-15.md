# Gan structured-prompt lineage

Date: 2026-08-15
Status: development review complete; `v0.5` remains the selected live prompt
Trigger: ExECT structured-prompt bloat/v10 note (pruned; recover from Git history); living owner [Decision 0053](../../decisions/0053-gan-structured-events-final-prompt.md)
Selected prompt: `gan2026_hybrid_structured_events_v0.5` under
[Decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md)
Successor payload: `gan2026_hybrid_structured_events_final` under
[Decision 0053](../../decisions/0053-gan-structured-events-final-prompt.md)
(envelope hygiene; not selected until a matched panel exists)

## Plain answer

The selected Gan one-call prompt,
`gan2026_hybrid_structured_events_v0.5`, is not a GEPA program and is
not an ExECT-style annotation manual. It is a 13-instruction
events-plus-selection contract that shipped on 1 June 2026, lost one
architecture-jargon line on 3 June (Decision 0015), and then froze.
The live development contract hash on the 7 June `dev750` GPT-4.1-mini
cell still matches HEAD.

Later versions are named, model-specific add-ons on that same schema:

| Version | Extra instructions | Why it exists |
| :--- | ---: | :--- |
| `v0.6` | +1 | DeepSeek Chat seizure-free precedence |
| `v0.7` | +9 vs `v0.5` | DeepSeek Reasoner countable-fact conservation |
| `v0.8_luna_rate` / `_current` | +6 / +7 | Luna-only rate and current-state studies |
| `v0.8_deepseek_unknown` | +6 | DeepSeek unknown-competence candidate (negative) |

Decision 0043 already returned the hosted comparison to `v0.5` because
`v0.6` / `v0.7` are not a shared instruction. This write-up is the
lineage that decision did not write. It does not change a selected
score, land a prompt, or authorize holdout calls.

There is no recommended Gan `v10`. The selected prompt is already the
short shared contract. Decision 0053 adds
`gan2026_hybrid_structured_events_final`: the same 13 instructions
with the `task` / `prompt_version` / `source_row_index` envelope
removed. That payload is implemented. Luna `dev20` found no large
drop. Luna `dev750` is queued:
[Luna `dev750` report](structured_prompt_final_luna_dev750_2026-08-15.md).
It is not the selected comparison identity yet.

## Why this exists

The ExECT sibling found that the published EA0133 payload is 59,213
characters: 84 rules and 49 worked examples grown in five days of
ordinary commits. Appendix A of the
[six-model walkthrough](../paper/six_model_single_letter_walkthrough_2026-08-15.md)
would otherwise present that LLM condition as an annotation manual.

Gan needed the same question asked of its selected prompt. Decision
0043 already said `v0.5` is the shortest shared structured-events
prompt and quarantined `v0.6` / `v0.7`. That is a comparison-boundary
decision, not a commit-by-commit contract-versus-bloat list.

The walkthrough's Gan letter (row 13190, `dev750`) is easier to read
once the prompt size is on the page: the shared `v0.5` payload on that
letter is **5,076 characters** (13 instructions, 1,893-character
note). The July 18 six-model raw tree used `v0.7` on the same letter
(**7,841 characters**, 22 instructions). Models still diverge. They
are not being asked to follow a 59k-character manual.

## Other prompts are different objects

| Object | Schema | When | Role |
| :--- | :--- | :--- | :--- |
| Structured events (`event_selector_v0.5` → `hybrid_structured_events_v0.5`) | `events` + `selection` | 1–3 June; frozen 7 June | Selected `llm_with_rules` one-call prompt |
| Structured events `v0.6` / `v0.7` | same | 10 June / 24 June | DeepSeek-specific policy; selectable for replay only |
| Structured events `v0.8_*` | same | 31 July / 1 Aug | Named Luna / DeepSeek development candidates |
| Canonical pipeline `gan2026_llm_only_canonical_pipeline_v0.8` | direct label + guidance | selected `llm` method | Different method. Teaching-case payload ~13k characters |
| Candidate-set hybrid assessment (`hybrid` v5, 9 June) | CandidateSet roles | Phase 3 architecture study | Different architecture. The four FM-6 / FM-2a / FM-2b / FM-5b instructions and worked examples live here, not on the structured-events prompt |

Do not describe `v0.5` as GEPA-optimized. Do not describe the 9 June
"hybrid v5" commit as a change to this prompt: that commit renamed
`llm_only_structured_events` → `hybrid_structured_events` and added
instructions to the **candidate-set** assessment prompt.

The selected `llm` method uses the canonical-pipeline prompt, not
these structured-events versions. A `v0.8` string on that method is
not a `v0.8` structured-events variant.

## What grew

Counts below are from `git show` of `llm_structured.py` (1 June), then
`llm_only_structured_events.py`, then
[`hybrid_structured_events.py`](../../../src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/hybrid_structured_events.py).
Instruction counts are the `instructions` list length after version
gates. Character counts are `json.dumps` of the builder payload with
an empty note (schema + instructions only).

| Date | Commit | Version | Instr. | Payload (no note) | Added |
| :--- | :--- | :--- | ---: | ---: | :--- |
| 1 Jun | `7d893672` | `gan2026_llm_structured_event_selector_v0.5` | **14** | — | Task, event/selection schemas, 14 instructions including one “do not use deterministic candidates” line |
| 3 Jun | `6406deaf` | same body, Decision 0015 hygiene | **13** | — | Dropped the architecture line; `benchmark` / `Gan-compatible` → `normalized` / `answer` |
| 9 Jun | `f4d1c2e0` | `gan2026_hybrid_structured_events_v0.5` | 13 | — | Rename only |
| 7 Jun | live cell | **`v0.5` frozen** | 13 | 3,161 | 7 June `dev750` GPT-4.1-mini contract hash still matches HEAD |
| 10 Jun | `3ed082ae` | `v0.6` | 14 | 3,797 | One seizure-free-versus-recent-frequency precedence rule (DeepSeek Chat `validation250`) |
| 24 Jun | `6bdce5fe` | `v0.7` (then the default) | **22** | 5,926 | Eight countable-fact / cluster / remission-boundary rules (DeepSeek Reasoner) |
| 16–27 Jul | Decision 0043 / `6c6df72c` / `085be7c5` | **`v0.5` selected again** | 13 | 3,161 | `v0.5` restored as selectable, then as the default. No instruction edit |
| 31 Jul | `04498ef2` | `v0.8_luna_rate` / `_current` | 19 / 20 | 4,586 / 4,735 | Luna-only forks from `v0.5`, not from `v0.7` |
| 1 Aug | `f1497939` | `v0.8_deepseek_unknown` | 19 | 4,489 | DeepSeek unknown-boundary fork from `v0.5` |

June 1 `v01`–`v05` JSONL names are repair-pipeline iterations on this
same prompt, not earlier instruction versions. There is no structured-events
`v0.1`–`v0.4` prompt body.

`v0.6` (`3ed082ae`) is authored as Conor Brown with a Claude trailer
and a targeted DeepSeek `validation250` rationale. `v0.7`
(`6bdce5fe`) has an empty body. The `v0.8` Luna block landed with a
Cursor trailer. This is ordinary agent/human patching, not GEPA
reflection. The difference from ExECT is timing: the patches were
**versioned beside** the frozen contract instead of being written into
it.

## The v0.5 contract (what stays selected)

Reconstructed from HEAD `build_prompt_input(..., prompt_version=v0.5)`,
which matches the 7 June `dev750` sidecar. Task text still says
“LLM-only structured-events”; that is a leftover name, not a
component-ownership brief.

**Task.** Read the clinical note. Extract source-near seizure-frequency
facts as slim events, then select one current burden.

**Thirteen instructions.**

1. Read the full note and extract source-near seizure-frequency facts.
2. Events are slim clinical facts. `raw_value` holds the stated rate,
   duration, last-event statement, or unknown / no-reference cue.
3. `kind` is one of `frequency_rate`, `cluster_frequency`,
   `seizure_free`, `last_event_only`, `unknown_frequency`,
   `no_reference`.
4. Use one `no_reference` event only when the note has no usable
   seizure-frequency evidence. If seizures are discussed but frequency
   is unclear, use `unknown_frequency`.
5. Keep seizure-free statements separate from unknown or last-event-only
   statements. Do not select seizure-free if other current seizure-like
   events remain active.
6. When several current seizure types are present, select the highest
   current or recent burden across semiologies.
7. If the note gives an overall current count plus a subtype breakdown,
   select the overall count.
8. `final_label` may be a normalized label such as `1 per day`,
   `2 to 3 per month`, `multiple per week`, `1 cluster per week`,
   `seizure free for 6 month`, `unknown`, or
   `no seizure frequency reference`.
9. Prefer the source expression in `raw_value` and a concise
   normalized label in `final_label`.
10. If a last event is dated and the patient has been well or
    seizure-free since, still extract that dated last-event fact.
11. If a count such as 3 or 4 jerks occurred since a dated last
    tonic-clonic seizure, keep the count and the dated anchor.
12. Every `evidence` value must be an exact note substring when
    possible.
13. Return exactly one JSON object. No markdown.

The closed `event_schema` and `selection_schema` travel with every
version. There is no `architecture` block, no candidate ledger, and no
worked-example list.

## What later versions add, and why they are not the comparison prompt

| Add-on | Why it is accretion |
| :--- | :--- |
| `v0.6` overlapping-window seizure-free precedence | Written after DeepSeek Chat validation failures. Useful for that condition; not a shared task statement ([Decision 0043](../../decisions/0043-gan-hosted-comparison-uses-v05-prompt.md)). |
| `v0.7` countable-fact check, dated-count conservation, cluster-axis split, “no seizures since review” vs active auras, silent-reasoning line | Written after DeepSeek Reasoner validation failures. Eight extra instructions, including gold-shaped examples (`two seizures in February`, `four morning jerks since 03/2015`). |
| `v0.8_luna_rate` | Range preservation, clinic/diary totals, cluster both-axes. Luna-versus-Luna study; not a six-model default. |
| `v0.8_luna_current` | Short-quiet-spell → unknown, yearly rate over long quiet stretches, questionable-event abstention. Same study. |
| `v0.8_deepseek_unknown` | Quiet-spell / vague-language → unknown. Piloted on the gold UNK slice; **stopped as negative** ([unknown-competence thread](deepseek_unknown_competence_thread_2026-07-31.md)). |

Decision 0043 records an aggregate prompt-interaction diagnostic:
`v0.7` improved Qwen relative to `v0.5` on locked `test450` while
reducing the other five models. That is not a recommended prompt and
not a row-level mechanism claim. This review did not reopen those
holdout rows.

The Luna `v0.8` variants did beat frozen `v0.5` for Luna on `dev750`
and, aggregate-only, on `test450`
([Luna prompt variants](luna_prompt_variants_report_2026-07-30.md)).
That still does not replace the shared six-model prompt.

## Residual policy already inside v0.5

`v0.5` is short. It is not schema-only. Instructions 5–11 are
clinical selection and extraction policy that shipped on day 1, not
later failure patches:

- active events block seizure-free (5)
- highest-burden-across-semiologies (6)
- overall count over subtype (7)
- gold-shaped example labels (8)
- dated last-event extraction even when selection is seizure-free (10)
- keep a since-anchor count in the event list (11)

The [gold phrase-variant brief](../paper/gan_gold_phrase_variants_2026-08-13.md)
argues that normalisation and render rules do not belong in the
prompt. Instruction 8 already lists seven gold-dialect strings. That
is a small leak, not a 333-label inventory.

A later paper-purity study could name a thinner contract (schema,
kind taxonomy, `no_reference` vs `unknown`, exact evidence, one JSON)
and test it on development rows. That would be a new candidate, not a
restore, and it is **not** queued here. ExECT needed that cut because
the live prompt *is* the pile. Gan's live prompt is not.

## Live development check (already measured)

No `test450` rows were opened.

The 7 June GPT-4.1-mini `dev750` sidecar
([`experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl`](../../../experiments/gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl))
is 750/750 `gan2026_hybrid_structured_events_v0.5`. The
instruction/schema contract SHA-256 is
`810c007ae8aa944316c6f427d4e3ef3b8a688cc071da66d80e149dbc7f8ead1b`.
HEAD `build_prompt_input` for `v0.5` hashes to the same value. The
13 Aug companion replay
`experiments/gan2026_six_model_current_stack_dev750_replay_20260813/gpt41mini_v05_june07/`
carries the same contract.

On walkthrough row **13190** (`dev750`, already published):

| Prompt | Instructions | Payload characters |
| :--- | ---: | ---: |
| `v0.5` (selected) | 13 | 5,076 |
| `v0.7` (July 18 six-model raw tree) | 22 | 7,841 |
| ExECT `v0.9.24` on EA0133 | 84 rules + 49 examples | 59,213 |

Across that 7 June `v0.5` cell, full payloads (note included) run
3,963–8,636 characters (median 5,874). The July 18 `v0.7` six-model
replay of the same notes runs 6,728–11,401 (median 8,639).

The teaching-case letter is 3,462 characters under
`gan.llm_with_rules.build_prompt` and 13,054 under `gan.llm.build_prompt`
([Gan teaching case](../../architecture/teaching_cases/gan2026.md)).
That gap is method-prompt identity, not `v0.5` vs `v0.7`.

## Claim boundary

- Development provenance only. `test450` was not inspected.
- `v0.5` remains the selected six-model / current-stack
  `llm_with_rules` prompt. Decision 0043 / 0050 fills are unchanged.
- No Gan prompt is landed, renamed, or recommended as a new default.
- Luna `v0.8` and DeepSeek `v0.8` stay named diagnostic candidates.
- A thinner schema-only prompt would need a predeclared development
  study. It is not authorized by this review.
