# Paper-final repository scope

Date: 2026-08-17
Status: accepted after grilling; keep-set lives in `docs/paper/`
Owner: [paper keep-set](../paper/README.md)

This repository's job is now to support the final paper. It is not a
continuing research campaign. Everyday dumps, closed prune trails,
superseded prompt versions, and contradictory numbered decisions are
debt. Git history keeps them. The working tree does not.

No new experiment runs except:

1. Missing cells on a primary paper method for one of the six living
   models.
2. Missing cells on a historical method the paper will cite as a
   direct comparison.
3. Luna `gan_llm_pre_post` on `dev750` (rung 5 development iterator).
   No Grok or holdout rung-5 in this cut.

Do not retune from holdout. Do not inspect `test60` or `test450`
rows. Do not invent numbers.

## What the paper is

Two tasks, five rungs of rule help, six models. Scores are not
interchangeable across tasks. This cut amends the 2026-08-17
three-method table. `gan_llm_only` remains a live runner identity.
It is not a results column.

| | Gan 2026 | ExECTv2 |
| --- | --- | --- |
| Question | One current seizure-frequency label | Complete diagnosis, frequency, prescription, and investigation inventory |
| Development | `dev750` | `dev140` |
| Locked test | `test450` (aggregate-only) | `test60` (aggregate-only) |
| Primary score | Purist accuracy | Four-family clinical fact F1 |

Living models, every time: Gemini 3.7 Flash (cited / method
identity), Grok 4.6, GPT-5.6 Luna, DeepSeek V4 Flash 0731, Qwen 3.8
27B, Gemma 4 26B. Later-stage LLM encode and LLM select calls are
Gemini only.

Historical aliases, not living: GPT-5.6 Sol, GPT-4.1-mini, DeepSeek
pre-0731, Qwen 3.6:35B, Compact dump (`v0.9.40`).

## Paper names

Frozen final methods get paper names. Lab version strings stay in one
lineage note and in git. They are not live identities.

Locked machine identities:

| Paper method | Identity | What it is today |
| --- | --- | --- |
| 1 `rules_only` | `gan_rules` / `exect_rules` | No model |
| 2 `llm_schema` | replay of `gan_llm_with_rules` / `exect_llm_only` | Schema only; shared raw with rungs 3–4 |
| 3 `llm_format` | same raw | Label-dialect or format stop; must not re-pick the fact |
| 4 `llm_post` | `gan_llm_with_rules` / replay `exect_llm_only` assembly | Full clinical post |
| 5 `llm_pre_post` | `gan_llm_pre_post` / `exect_llm_pre_post` | Candidates in the prompt, then the same post stack |

`gan_llm_only` is not a results column. Luna is the Gan pre-post
development iterator. Later-stage LLM encode / select calls are
Gemini only, on both tasks. Hybrid-call raw is not ExECT extract.

Locked historical comparator:

| Comparator | Identity | Role |
| --- | --- | --- |
| ExECT Full ledger | `exect_full_ledger` | Longer one-call control for specific comparisons; not a headline method or peer column of the five-rung table. Grok has no Full ledger cell |

Out of the manuscript: mention-encoder study prompts, Form recovery,
Compact dump, Gan `v0.6`/`v0.7`/`v0.8_*`, leftover-form knobs,
joint/`combined` assembly, ExECT GEPA, Gan multi-model as a separate
method story.
Today's Gan hybrid call (`v0.5`, with the envelope) is not the paper
method. Do not relabel those cells as `gan_llm_with_rules`.

The cleaned Gan request is a different call. Existing six-model
hybrid fills stay historical. They are not paper cells. Grok, Luna,
and Gemini `dev750` on the cleaned request are on disk. Grok cleaned
`test450` is on disk (375/450). DeepSeek, Qwen, and living Gemma on
`dev750`, and the other five models on aggregate-only `test450`,
remain allowed blanks.

## Allowed new runs

Known blanks on primary methods:

| Cell | Why it is allowed |
| --- | --- |
| Qwen 3.8 Compact `dev140`, then aggregate-only `test60` | Local living Compact is unfinished. Do not invent numbers. |
| Gan `gan_llm_with_rules` on the cleaned request: DeepSeek, Qwen, and living Gemma on `dev750`, then the remaining five models on aggregate-only `test450` | The paper method is the cleaned request. Grok cleaned `test450` (375/450) and Grok, Luna, Gemini `dev750` are on disk. Do not inspect holdout rows. Do not start new Sol live calls. |
| DeepSeek, Qwen 3.8, and living Gemma Gan LLM-only `dev750` and `test450` | `gan_llm_only` is a six-model paper table. Grok cells are on disk. |

Full ledger comparator cells that already exist do not need a new
run. A comparator that is not in the manuscript is not a blank.

## Target tree

`paper_experiments/` is the only place a paper number lives.
`experiments/` may exist locally as gitignored scratch for in-flight
runs. It is not a second evidence tree. Commit only stripped cells.

```
paper_experiments/
  README.md
  roster.json
  inventory.json
  gan/{gan_rules,gan_llm_only,gan_llm_with_rules}/{model}/{split}/
  exect/{exect_rules,exect_llm_only,exect_llm_pre_post}/{model}/{split}/
  comparators/exect_full_ledger/{model}/{split}/   # only if cited
```

Replay files keep only `letter_id` or `source_row_index`,
`prompt_version` (the paper name), and `raw_output`. Holdout is
aggregate-only.

Today's `gan2026_hybrid_structured_events_v0.5/` and
`gan2026_llm_only_canonical_pipeline_v0.8/` directories are the
selected methods under old names. Rename them. Do not keep both
names.

## Documents that remain

A short current set, written in paper language:

| File | Job |
| --- | --- |
| `README.md` | Public front door: two tasks, five rungs, held-out scores |
| `PROJECT_STATUS.md` | What is present, what is missing, what may be run |
| `docs/NAVIGATION.md` | Paper source library and current owners only |
| `docs/paper/methods.md` | Authoritative method names, roster, splits, scorers |
| `docs/paper/lineage.md` | One short history: how Compact and Gan hybrid were reached. No experiment links. |
| `docs/paper/claims.md` | What the paper may say, with strength. Sentence titles, not `C10`. |
| `docs/paper/decisions/` | Essential current decisions only, self-describing names |
| `docs/research/paper/` | Existing paper source library, retargeted to paper names |
| `docs/history/decisions.md` | Dense log of the numbered decision series. Pointers, not full copies. |

Current decisions (locked names):

- `exect-compact-is-the-cited-hybrid.md`
- `gan-cleaned-request-is-the-cited-hybrid.md`
- `six-model-roster.md`
- `holdout-is-aggregate-only.md`
- `pytest-is-the-research-validity-firewall.md`

Everything else in `docs/decisions/` (45 files) collapses into the
history log. `THREAD_MAP.md`, `ACTIVE_ROADMAP.md`, the 198 research
reports, and the leftover-form / prune / mention-unit campaign notes
leave the working tree. Recover from git if a reviewer asks how a
rule was found.

The paper source library stays because it is how the paper is
written. Retarget numbers and names. Do not keep Full-era headlines
as if they were current.

Canon files `01`–`11` either merge into `docs/paper/` or go to
history. Do not keep a second claim register.

## Code that remains

Live code implements the paper methods and, if cited, Full ledger.

Strip from the working tree:

- Gan prompt builders and switches for `v0.6`, `v0.7`, `v0.8_luna_*`,
  and `v0.8_deepseek_unknown`. Keep the cleaned request as
  `gan_llm_with_rules`. Keep a temporary alias from the old `final`
  string until paper cells are rewritten.
- ExECT prompt identities `v0.9.40`–`v0.9.44`, further-prune
  builders, naming grafts, and mention-unit / leftover-form study
  prompts
- Study runners and configs whose only job is a closed campaign
- Tests that exist only to pin a deleted identity

Keep a thin replay alias only where a paper cell's saved
`prompt_version` still uses an old string, until those files are
rewritten to the paper name. After the rewrite, delete the alias.

Do not preserve runnable links to experiments that will not be
re-run.

## Tests and safeguards that remain

- Always-on pytest as the research-validity firewall
- Holdout aggregate-only
- No tuning from locked test rows
- Component attribution on the living methods
- Paper-inventory tests: present vs missing cells, strip contract,
  paper names

Deep six-cell replay stays only for the paper methods.

## Sequence

Grilling is closed. Next:

1. Promote the keep-set into `docs/paper/` (methods, claims, five
   decisions, lineage page).
2. Fill allowed blanks (Luna Compact `test60`, Qwen Compact, cleaned
   Gan hybrid panel, Qwen Gan LLM-only).
3. Rename paper cells and live identities to paper names.
4. Delete historical prompt code, study runners, and research
   reports that are not in the keep-set.
5. Collapse numbered decisions into the history log.
6. Slim `PROJECT_STATUS.md` and `NAVIGATION.md` to the paper tree.

Steps 3–5 are one cut, not a drip of renames. Step 2 may run in
parallel once a blank has a runner.

## Inventory of debt (working-tree counts, 2026-08-17)

- 45 numbered decisions, several of which disagree about what the
  paper cites
- 198 research Markdown files (109 ExECT, 32 Gan, 35 shared)
- 11 canon files plus a separate paper source library
- 109 scripts, many campaign-specific
- Gan live code still selects among seven prompt versions
- ExECT live code still carries Full ledger, Compact, Compact dump,
  four further prunes, and mention-encoder identities
- `paper_experiments/` still uses `v0.5` / `v0.8` / `compact_ledger`
  directory names
- `PROJECT_STATUS.md` and `ACTIVE_ROADMAP.md` still narrate the
  leftover-form campaign as if it were current work

## Locked in grilling

1. **Method set (2026-08-17).** Six primary methods plus Full ledger
   as the only ExECT comparator—not a headline method or peer column.
   Do not present Full hybrid or Full raw as table peers. GEPA, Gan
   multi-model, mention-encoder study prompts, Compact dump, and extra
   Gan prompt variants are out.
2. **Gan hybrid payload (2026-08-17).** `gan_llm_with_rules` is the
   cleaned request, not today's enveloped `v0.5` call. That implies
   a new six-model Gan hybrid panel. Do not cite 381/450 as the
   paper hybrid until the cleaned holdout exists.
3. **Gan LLM-only panel (2026-08-17).** `gan_llm_only` is a six-model
   paper table. Qwen 3.8 `dev750` and `test450` are allowed blanks.
4. **Working-tree history (2026-08-17).** One lineage page. Keep the
   paper source library (stories, why hybrid, failures, cases,
   phrase-variant inventories, architecture exhibit). Cut campaign
   reports and the prune diary.
5. **Demo (2026-08-17).** Public frontend stays, restricted to paper
   methods. Historical paths leave the UI.
6. **Current decisions (2026-08-17).** Five files, self-describing
   names: Compact is the cited ExECT hybrid; the cleaned request is
   the cited Gan hybrid; six-model roster; holdout is aggregate-only;
   pytest is the research-validity firewall. Claim sentences live in
   `docs/paper/claims.md`. Numbered decisions collapse to the history
   log.
7. **Local scratch (2026-08-17).** `experiments/` may stay as
   gitignored scratch for in-flight runs. Only `paper_experiments/`
   is committed evidence.
