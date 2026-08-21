# Paper keep-set

Current owners for the final paper. Campaign reports and numbered
decisions are not current.

## Central argument

The proposed method translates clinic letters into structured clinical
facts in a designed form, with quoted source text. A model collects the
facts and evidence. Recorded rules then shape those facts into the
required form. Those mappings can be replayed on the same model output
without a new call.

The two public golds are the forms used for evaluation. They are not
the task. Gan's evaluation form is one current seizure-frequency state.
ExECT's is a complete four-family fact inventory. Written rules and a
model alone are baselines. Tables cite one model, Gemini 3.7 Flash, so
the story stays on the method. Grok, Luna, DeepSeek, Qwen, and Gemma
are companion rows. Later-stage LLM encode and LLM select calls are
Gemini only.

The paper claims visibility for the recorded object: the source span,
the later rule changes, and the submitted answer. It does not claim
access to a model's internal reasoning, or that a visible step is
clinically correct.

Headline table: four methods — Rules, LLM, LLM then rules, Rules
then LLM — against extract / encode / select. Gan LLM encode and
LLM select are promoted Gemini later-stage cells. ExECT later-stage
encode and select are still empty. LLM then rules is the three stops on
`gan_llm_with_rules` / `exect_llm_only`. Rules then LLM is the three
stops on `*_pre_post`. `gan_llm_only` is not a results column. Full ledger
is the only comparator when cited—not a headline method. See
[methods](methods.md).

| File | Job |
| --- | --- |
| [methods](methods.md) | Proposed method, baselines, roster, splits, scorers |
| [method × stage](../research/paper/five_rungs_of_rule_help_2026-08-20.md) | Plain-language four-method grid, with one Gan and one ExECT development example |
| [Gan rules and models](../research/paper/gan_rules_and_llms_across_stages_2026-08-21.md) | Gemini four-method reading: roles, order, encode/select lift |
| [rule catalogue](../research/paper/rule_catalogue_schema_format_post_2026-08-21.md) | Named extract / encode / select rules on both tasks |
| [claims](claims.md) | What the paper may say, and how strongly |
| [lineage](lineage.md) | How the living requests were reached and what kind of method change each revision made |
| [decisions](decisions/) | Current decisions |
| [source library](../research/paper/) | Writing sources |
| [paper experiments](../../paper_experiments/README.md) | Replayable cells |
| [scope](../plans/paper_final_repo_scope_2026-08-17.md) | Cut and allowed new runs |
| [decision history](../history/decisions.md) | Closed numbered series |
