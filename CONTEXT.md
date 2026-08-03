# Clinical Extraction

Glossary for the two-task clinical extraction research system. Implementation detail lives elsewhere.

Paper-facing ExECT primary method-comparison boundary:
[decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md).

## Language

### Methods

**Active method**:
The public identity of a selected research method for a task: `rules`, `llm`, or `llm_with_rules`. Frontend grouping, badges, and selectors use this field only.
_Avoid_: `comparison_mode`; `llm_plus_rules`; `deterministic_only` as a second public vocabulary; `hybrid` or `llm_only` as the active identity

**Architecture stage ID**:
A stable attribution key for one pipeline stage inside a method manifest. For selected methods it uses the active-method token in the namespace (`gan.llm_with_rules.*`, `exect.llm_with_rules.*`, and the matching `rules` / `llm` forms), not a parallel `hybrid` namespace.
_Avoid_: `gan.hybrid.*` or `exect.hybrid.*` as the selected-method stage namespace; treating a stage ID as the public method name

**Selected ExECT hybrid**:
The current one-call, model-led ExECT LLM-with-rules method: the named model proposes Diagnosis, Seizure Frequency, Prescription, and Investigations findings, then family-specific deterministic transforms may change the scored answer under decision 0040 / 0041. Paper primary identity is governed by [decision 0046](docs/decisions/0046-exect-primary-method-comparison-boundary.md).
_Avoid_: v08, historical hybrid, holistic assembly, LLM with rules (unqualified when ExECT is meant)

**Historical ExECT hybrid control**:
The retained `v08` ExECT LLM-with-rules development control. It is reproducible evidence for an earlier ownership pattern, not the paper's primary ExECT hybrid. In the paper it appears only in a secondary results table with an explicit ownership caveat, never as the primary hybrid method row. It is not a supervisor-facing frontend ladder architecture.
_Avoid_: selected hybrid, final architecture, model-led comparison, primary method row; frontend component-ablation control column

**Supervisor-facing method demonstration**:
The frontend surfaces that teach or demonstrate the selected six-path system. They show only selected active methods and their teaching/replay evidence, not historical candidate ladders such as `v08` or `v09` partial-hybrid rows. The ExECT component-ablation ladder is not part of that demonstration until a selected-method ladder exists. The Gan component-ablation mock keeps the three-way comparison columns as selected `rules` / `llm` / `llm_with_rules` evidence (active-method labels), not as unnamed “diagnostic” or “Hybrid” columns.
_Avoid_: presenting closed candidates as the default control; mixing retained historical ablation columns into the primary demonstration; supervisor-facing “Hybrid …” method labels

**LLM with rules**:
A research method class in which a model proposes clinical content and deterministic code may later change clinical meaning. On ExECT, the selected instance is the Selected ExECT hybrid; on Gan, it is the event-ledger plus repair stack.
_Avoid_: using the phrase alone when the task-specific selected instance matters

### Documentation reading paths

**Supervisor path**:
The short README-led handoff route a supervisor follows without agent help: system story, frontend or six-path teaching case, canonical results, claim limits, and exact replay. It is intentionally small.
_Avoid_: treating the long evidence tables in `docs/NAVIGATION.md` as the supervisor path; packing historical Gan or ExECT reports into the handoff route

**Worker path**:
A short intentional route for ongoing research or engineering work, owned by `docs/THREAD_MAP.md` plus durable owner documents such as project status, active roadmap, regeneration triage, canon, design, and decisions.
_Avoid_: using worker paths as a dumping ground for every retained experiment report; equating “linked from NAVIGATION” with “active work”

**Documentation demotion**:
Keep a document or artifact on disk for named evidence, negative replay, or limitation context, but remove it from supervisor and worker indexes so it is no longer on an active reading path. Discovery after demotion is through the regeneration ledger, retained-evidence index, or the decision/report that owns the claim.
_Avoid_: creating a `docs/archive/` tree as the demotion mechanism; deleting solely because a path contains `archive`; conflating this with pytest deep-tier demotion

**Active documentation index**:
The short map of supervisor and worker paths. After Decision 0048 documentation cleanup, that role belongs to a thinned `docs/NAVIGATION.md` plus `docs/THREAD_MAP.md`, not to a long evidence catalog.
_Avoid_: treating a long NAVIGATION evidence table as the active index; adding a parallel status board or evidence register

**Demoted evidence discovery**:
Finding a demoted-but-kept report goes only through existing owners: paper claim status, the retained-evidence index, the regeneration ledger and retention-slice notes, or the decision/report that still cites it. A file with no such owner and no hard caller is a delete candidate, not an invisible keep.
_Avoid_: a new historical evidence catalog page; mirroring demoted NAVIGATION rows inside `REGENERATION.md`

**NAVIGATION evidence pointer block**:
The only evidence links that remain on the thinned active documentation index: retained-evidence manifest, paper claim status (`canon/10`), and the canonical six-model results report. Historical and focused experiment rows do not live on `NAVIGATION.md`.
_Avoid_: restoring long historical Gan/ExECT catalogs on NAVIGATION; parking active research threads on NAVIGATION instead of THREAD_MAP

**Documentation corpus triage pass**:
The Decision 0048 documentation wave that first drafts the thinned `PROJECT_STATUS` live view and thinned active documentation index, then inventories paths that lost a living-owner citation on that post-thin graph, keeps files with a hard caller or remaining living owner, deletes the rest, rebinds still-needed citations, lands the thinned docs and deletes together, keeps `CONTEXT.md` glossary-only, and records dispositions in the regeneration ledger and a retention-slice note. README currency and paper/canon provenance rewrites stay out unless a delete forces a rebind; leftover canon drift becomes a Next item after a consistency glance.
_Avoid_: unlink-only demotion that leaves invisible keeps; deleting against the pre-thin status citation graph; a second evidence catalog; porting NAVIGATION's Implementation table wholesale into THREAD_MAP; a separate documentation-cleanup decision when 0048 already owns the gate; preserving status chronology in a new log file; coupling index triage to manuscript editing

**Project status live view**:
The shape of `PROJECT_STATUS.md` after thinning: current outcome, a short fresh-evidence block for still-active claims, in progress, blocked or unvalidated, next, data and claim boundaries, and a short canonical-owners list. Fresh evidence covers the Decision 0048/0049 point, the selected six-model matrix owners, Decision 0046 primary fills, and open threads (DeepSeek unknown, handoff host/unaided review, semantic-support review). Canonical owners stay minimal: retained manifest, paper claim status, active roadmap, regeneration ledger, Decision 0048, comparison report, and open DeepSeek thread while it remains open.
_Avoid_: multi-date verification bullet histories; quarantined v0.7 catalogs on the status page; parking closed Luna/ruleset/reliability catalogs on the live panel; duplicating NAVIGATION's former evidence tables under Canonical owners

**Living owner citation**:
A keep-alive reference from a durable active surface: canon, decisions, retained-evidence manifest, regeneration ledger, project status, active roadmap, THREAD_MAP, README, thinned NAVIGATION, design or runbook owners, or a hard caller such as a test, check script, registry entry, or config. Peer links among demoted experiment or research reports do not count.
_Avoid_: transitive keep-alive through demoted-to-demoted links; treating any inbound `docs/` link as ownership

### Splits

**Gan development split**:
The 750-row Gan split that permits development review and replay. In prose and claims it is `dev750`. Retained filenames and live API machine `split` fields may keep the legacy identifier `validation750`.
_Avoid_: presenting `validation750` as the current prose split name; renaming retained artifact filenames for cosmetics

### Paper roles

**Primary method row**:
The result that stands for a method in the paper's main three-method comparison for a task.
_Avoid_: selected run (when meaning the paper table), headline score (when meaning role rather than number)

**Primary ExECT method-comparison score**:
Matched four-family clinical fact recovery used to compare ExECT rules-only, LLM-only, and the Selected ExECT hybrid as peers. Code and saved scores still use `clinical_headline` / `headline_target`.
_Avoid_: leading with “clinical headline” in prose; nine-entity published metrics as the three-method peer score; mixing entity counts across method rows

**Primary ExECT hybrid method-row fill**:
The Selected ExECT hybrid result for GPT-5.6 Sol on the primary ExECT method-comparison score. The six-model panel remains model-comparison evidence; Sol is the paper's method-identity number for ExECT LLM with rules.
_Avoid_: GPT-4.1-mini as the ExECT hybrid method identity; v08; best-of-six without naming Sol

**Primary ExECT LLM-only method-row fill**:
GPT-5.6 Sol's `raw_candidate` / `raw_lane_score` from the same one-call four-family pipeline — the earliest scored model boundary before deterministic clinical changes. On `dev140` this is clinical fact F1 `0.8097` (reported as `0.81`). On `test60`, the public six-model stage panel records Sol `raw_lane_score` F1 `0.7771` (final LLM-with-rules `0.8047`). Owner: [stage panel](experiments/exectv2_six_model_test60_stage_panel_20260801/panel_aggregate.json). The primary method table still cites Sol only.
_Avoid_: GEPA as the Sol hybrid's LLM-only peer; `source_scored` as the LLM-only method identity; citing the Gan LLM-only `test450` panel as ExECT evidence; citing sealed-only test60 LLM-only numbers in the manuscript; Sol-only holdout stage panel when six-model finals already exist

**Gan six-model LLM-only test450 panel**:
The retained aggregate-only Gan LLM-only holdout panel at `experiments/gan2026_six_model_llm_only_test450_20260801/panel_aggregate.json` (`gan2026_llm_only_canonical_pipeline_v0.8`, all six models). Separate from ExECT stage scores.
_Avoid_: ExECT test60 LLM-only; ExECT model-boundary

**Primary ExECT three-method split policy**:
The primary ExECT method table includes both `dev140` and `test60` once every method cell has an aggregate-safe source. Sol LLM-only / hybrid already have sealed stage aggregates on `test60`. Rules-only four-family clinical fact recovery is authorized on `test60` as aggregate-only scoring (no row inspection) and is materialized.
_Avoid_: publishing test60 method cells without an aggregate source; inspecting sealed test60 rows; treating the Gan LLM-only `test450` panel as satisfying an ExECT test cell

**GEPA ExECT LLM-only comparator**:
The retained GEPA-optimized GPT-4.1-mini four-family program (`0.7393` clinical fact F1). Historical / negative architecture evidence, not the primary peer of the Selected ExECT hybrid.
_Avoid_: primary ExECT LLM-only method-row fill; Sol LLM only

**Secondary ExECT published-metric reference**:
The nine-entity paper-derived phrase / CUI / all-features rules-only replay. It answers the published-metric question, not the primary three-method comparison.
_Avoid_: primary method row, three-method peer

**Primary ExECT rules-only method-row fill**:
Four-family Sol-matched clinical fact recovery (`clinical_headline` / `headline_target`) applied to rules-only deterministic predictions restricted to Diagnosis, Seizure Frequency, Prescription, and Investigations. The all-nine extractors may still run; non-key entities are excluded from this peer score only. On `dev140` the materialized overall F1 is **0.8160**. On aggregate-only `test60` it is **0.7154**.
_Avoid_: all-nine strict micro F1 as the three-method peer; Diagnosis-only clinical recovery as the four-family peer; published-metric all-features as the three-method peer; `clinical_recovery_scorecard` overall as the Sol peer; four-extractor-only as a different rules-only method

**0046 rules-only scoring rule**:
B/C use restrict-and-rescore through the same assembly `headline_target` score as Sol, not the older multi-entity clinical-recovery scorecard.

### Verification

Suite policy owner: [Decision 0049](docs/decisions/0049-pytest-research-validity-firewall.md).

**Always-on test tier**:
The default Python test obligation that protects research validity: split barriers, scoring and claim contracts, locked-row policy, and selected-method behavior whose silent change would falsify a paper-facing claim. Plain `pytest` and CI run this tier only (`-m "not deep"`). The exit band for this simplification is about 200–300 collected always-on tests; about 100–150 is an aspirational floor if governing owners stay honest after thinning.
_Avoid_: full-repo behavioral coverage; treating every unit edge as always-on; “the suite” as an undifferentiated 1,500-test blob; requiring deep markers for the default gate; treating ~500 remaining tests as “dramatic” enough

**Always-on admission**:
A test enters the always-on tier only if a silent failure could falsify a paper-facing claim, split barrier, locked-row policy, or selected-method clinical meaning, or if a living canon page, decision, or method card still names it as the governing contract for that obligation.
_Avoid_: admitting every method-card stage pin; one-test-per-module coverage; retaining TDD edge tables by default

**Deep test tier**:
Optional, rarely run coverage beyond the always-on tier — a short allowlist of dense mechanism tables that still help debug living selected-method behavior, not a junk drawer for everything demoted. Deep is selected explicitly (for example `pytest -m deep`); it is capped at about five files or about 100 tests, and growth past that cap is resolved by deletion or by folding into a thinner always-on contract, not by expanding demotion.
_Avoid_: always-on; default CI gate; retaining deep cases merely because they once drove TDD; demoting bulk instead of deleting it; unbounded `@pytest.mark.deep` growth

**Non-admitted test disposition**:
Tests that fail always-on admission are deleted by default. Demotion into the deep tier is allowed only for a short allowlist of dense tables that still earn occasional debugging of living selected-method mechanisms. Retired-candidate and redundant TDD edge coverage is deleted; evidence for closed work stays in artifacts and docs, not pytest.
_Avoid_: demoting everything that fails admission; relocating bulk without deletion; keeping closed-candidate behavior alive only as tests

**Governing test owner**:
The single always-on pytest contract (or small vertical-slice file) that a living canon page, decision, or method card names for one obligation. Owner links are updated in the same change that deletes or demotes a test; demoted deep tests are not owners. Breadcrumb “Test:” pins for every pipeline stage are removed rather than rebound one-for-one.
_Avoid_: stale owner links after a cull; citing deep-tier files as owners; keeping one test citation per stage as documentation completeness

**Fat-file thinning**:
Dense parametrized tables are reduced by keeping a few exemplars only for living selected-method mechanisms, deleting whole files or branches that pin retired or redundant mechanisms, and demoting a dense table only when it still earns deep-tier debugging under the deep cap.
_Avoid_: demoting entire fat files to shrink the default gate; keeping one exemplar per historical TDD episode; deleting living SF/normalize boundaries with no exemplar or governing contract left

**Test write policy**:
A new pytest case may land only if it passes always-on admission or fits the deep-tier cap for living-mechanism debugging. New always-on coverage should replace or narrow an existing case when it pins the same obligation rather than stacking another edge beside it. The lasting form is an exemplar or governing contract, not an encyclopedia.
_Avoid_: unbounded “add a regression case”; growing always-on by accretion; using a hard count ceiling alone without replace-or-narrow discipline

**Pytest-first test simplification**:
The suite-reduction campaign applies first to the Python pytest base. Frontend Jest is left alone unless a file clearly pins a retired surface, with a light Jest pass only later if needed. Landing is wave-by-risk: policy and default-gate mechanics first; then obvious deletes; then fat-table thinning with exemplars and owner rebinds; then a scoreboard check against the always-on exit band.
_Avoid_: treating the ~73 Jest tests as the same bulk problem as pytest; blocking the pytest cull on a full frontend retiering; one unreviewable mega-delete; opportunistic-only culling that never reaches the exit band

**Wave 2 delete class**:
Near-automatic deletion for pytest that pins a non-selected surface or is redundant once a governing always-on contract or vertical slice already owns the obligation. Filename heuristics alone do not authorize deletion when the behavior still runs in a selected active method.
_Avoid_: deleting every `*candidate*` file by name; debating every obvious retired encyclopedia as if it were selected-method coverage; keeping duplicate parity/panel wrappers after one owner remains
