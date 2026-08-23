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

Headline tables: five role rows (rules, LLM, or both at extract /
encode / select). The cited score is the select stop. The six-model
row is cell 3 (LLM extract, rules encode, rules select) on both
tasks. Gemini thinking and the source-near Gan extract are
ablations. Gan LLM extract is the codebook extract; ExECT LLM
encode is a second later-stage call. See
[methods](methods.md),
[Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md),
and
[ExECT cell 4](../research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md).
`gan_llm_only` is not a results column. Full ledger is the only
comparator when cited—not a headline method.

| File | Job |
| --- | --- |
| [methods](methods.md) | Proposed method, baselines, roster, splits, scorers |
| [method × stage](method_x_stage.md) | Plain-language method × stage grid, with one Gan and one ExECT development example |
| [Gan rules and models](../research/paper/gan_rules_and_llms_across_stages_2026-08-21.md) | Gemini Gan reading: roles, order, encode/select lift |
| [Gan five-cell grid](../research/gan2026/gan_five_cell_grid_2026-08-22.md) | Cited Gemini frequency five-cell totals |
| [ExECT cell 4](../research/exectv2/exect_rule_select_after_llm_encode_2026-08-22.md) | Cited Gemini inventory LLM / LLM / rules stop |
| [rule catalogue](rule_catalogue.md) | Named extract / encode / select rules on both tasks |
| [claims](claims.md) | What the paper may say, and how strongly |
| [lineage](lineage.md) | How the living requests were reached and what kind of method change each revision made |
| [decisions](decisions/) | Current decisions |
| [source library](../research/paper/) | Writing sources |
| [paper experiments](../../paper_experiments/README.md) | Replayable cells |
| [cells and runners](cells_and_runners.md) | Live runner names mapped onto the five cells |
| [architecture](architecture.md) | Extract / encode / select and rule authority |
| [decision history](../history/decisions.md) | Closed numbered series |
