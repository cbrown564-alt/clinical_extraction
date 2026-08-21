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
model alone are baselines. Tables cite one model, Grok 4.6, so the
story stays on the method. Gemini is in the same band where cells exist.

The paper claims visibility for the recorded object: the source span,
the later rule changes, and the submitted answer. It does not claim
access to a model's internal reasoning, or that a visible step is
clinically correct.

Headline table: five rungs of rule help on both tasks. `gan_llm_only`
is not a results column. ExECT rungs 2–4 replay `exect_llm_only`;
rung 5 is living `exect_llm_pre_post` (hybrid F1). Full ledger is
the only comparator when cited—not a headline method. See
[methods](methods.md).

| File | Job |
| --- | --- |
| [methods](methods.md) | Proposed method, baselines, roster, splits, scorers |
| [five rungs](../research/paper/five_rungs_of_rule_help_2026-08-20.md) | Plain-language rungs, with one Gan and one ExECT development example |
| [rule catalogue](../research/paper/rule_catalogue_schema_format_post_2026-08-21.md) | Named schema / format / post rules on both tasks |
| [claims](claims.md) | What the paper may say, and how strongly |
| [lineage](lineage.md) | How the living requests were reached and what kind of method change each revision made |
| [decisions](decisions/) | Five current decisions |
| [source library](../research/paper/) | Writing sources |
| [paper experiments](../../paper_experiments/README.md) | Replayable cells |
| [scope](../plans/paper_final_repo_scope_2026-08-17.md) | Cut and allowed new runs |
| [decision history](../history/decisions.md) | Closed numbered series |
